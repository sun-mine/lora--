# -*- coding: utf-8 -*-
"""Qwen2.5-3B LoRA 微调：让模型先输出「思考」，再输出「答案」。

用法：
    /home/shipl/llm/bin/python code/finetune.py            # 全量训练
    /home/shipl/llm/bin/python code/finetune.py --smoke    # 小样本冒烟测试
"""

import argparse
import glob
import json
import os
import random
import re

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "model", "qwen2.5")
DATA_DIR = os.path.join(ROOT, "database")
OUT_DIR = os.path.join(ROOT, "output", "lora-qwen2.5-cot")

SYSTEM_PROMPT = "你是一个善于分步思考的助手。请先写出思考过程，再给出最终答案。"


# ---------------- 数据读取：6 个来源统一成 (问题, 思考, 答案) ----------------

def _read_jsonl(path):
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _read_json_list(path):
    """读取 JSON 数组；个别文件被截断，尽量抢救出其中完整的对象。"""
    text = open(path, encoding="utf-8-sig").read()
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    items, start = [], text.find("[")
    start = text.find("{", start) if start != -1 else -1
    while start != -1:
        try:
            obj, end = decoder.raw_decode(text, start)
            items.append(obj)
            start = text.find("{", end)
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
    return items


def load_m3():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/M3/**/*.jsonl", recursive=True):
        for x in _read_jsonl(path):
            rows.append((x.get("question"), x.get("thinking"), x.get("answer")))
    return rows


def load_deepseek():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/deepseek/**/*.jsonl", recursive=True):
        for x in _read_jsonl(path):
            rows.append((x.get("question"), x.get("cot"), x.get("answer")))
    return rows


def load_k27():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/k2.7/**/*.jsonl", recursive=True):
        for x in _read_jsonl(path):
            rows.append((x.get("problem"), x.get("reasoning"), x.get("answer")))
    return rows


def load_qwen():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/qwen/**/*.json", recursive=True):
        for x in _read_json_list(path):
            rows.append((x.get("instruction"), x.get("thinking"), x.get("output")))
    return rows


def _split_doubao(text):
    """Doubao 的思考过程和答案合并在 output 里，按常见分隔标记切开。"""
    for pattern in (r"\n##\s*代码实现", r"\n##\s*答案", r"\n```"):
        m = re.search(pattern, text)
        if m:
            return text[:m.start()], text[m.start():].lstrip("\n")
    m = re.search(r"(所以最终答案|最终答案是|答案是|因此，答案)", text)
    if m:
        return text[:m.start()], text[m.start():]
    return "", text


def load_doubao():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/doubao/**/*.json", recursive=True):
        for x in _read_json_list(path):
            question = (x.get("instruction") or "").strip()
            if x.get("input"):
                question += "\n" + x["input"].strip()
            thinking, answer = _split_doubao(x.get("output") or "")
            rows.append((question, thinking, answer))
    return rows


def load_glm():
    rows = []
    for path in glob.glob(f"{DATA_DIR}/glm/**/*.txt", recursive=True):
        text = open(path, encoding="utf-8-sig").read()
        for block in re.split(r"\n(?=【题目\d+】)", text):
            m = re.match(r"【题目\d+】\s*(.*?)\s*思考：(.*?)答案：(.*)", block, re.S)
            if m:
                rows.append((m.group(1), m.group(2), m.group(3)))
    return rows


# ---------------- 构造训练集 ----------------

def build_dataset(tok, max_length, limit=None):
    pairs = (
        load_m3()
        + load_deepseek()
        + load_k27()
        + load_qwen()
        + load_doubao()
        + load_glm()
    )
    print(f"原始样本 {len(pairs)} 条")

    seen = set()
    samples = []
    for q, t, a in pairs:
        if not all(isinstance(v, str) for v in (q, t, a)):
            continue
        q, t, a = q.strip(), t.strip(), a.strip()
        if len(t) < 20 or len(a) < 10:  # 思考过短或答案为空，丢掉
            continue
        key = re.sub(r"\s+", "", q)  # 跨源去重
        if not key or key in seen:
            continue
        seen.add(key)
        samples.append((q, t, a))

    random.Random(42).shuffle(samples)

    rows, dropped_long = [], 0
    for q, t, a in samples:
        prompt = tok.apply_chat_template(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": q},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        completion = f"思考：\n{t}\n\n答案：\n{a}{tok.eos_token}"
        if len(tok(prompt + completion).input_ids) > max_length:
            dropped_long += 1
            continue
        rows.append({"prompt": prompt, "completion": completion})

    print(f"清洗后 {len(rows)} 条（去重/过滤 {len(pairs) - len(samples)} 条，超长丢弃 {dropped_long} 条）")
    if limit:
        rows = rows[:limit]

    n_val = max(1, int(len(rows) * 0.03))
    return Dataset.from_list(rows[n_val:]), Dataset.from_list(rows[:n_val])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="只取少量样本、跑几步验证流程")
    parser.add_argument("--max_length", type=int, default=4096)
    parser.add_argument("--epochs", type=float, default=5)
    parser.add_argument("--resume", action="store_true", help="从 output 目录最新的 checkpoint 继续训练")
    args = parser.parse_args()

    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    train_ds, val_ds = build_dataset(tok, args.max_length, limit=200 if args.smoke else None)
    print(f"训练集 {len(train_ds)} 条，验证集 {len(val_ds)} 条")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR, dtype=torch.bfloat16, device_map={"": 0}
    )
    model.config.use_cache = False

    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )

    cfg = SFTConfig(
        output_dir=OUT_DIR,
        max_length=args.max_length,
        completion_only_loss=True,       # 只对「思考+答案」算 loss
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8 if args.smoke else 16,
        num_train_epochs=args.epochs,
        max_steps=5 if args.smoke else -1,
        learning_rate=1e-4,
        lr_scheduler_type="cosine",
        warmup_steps=1 if args.smoke else 16,
        logging_steps=1 if args.smoke else 10,
        eval_strategy="no" if args.smoke else "steps",
        eval_steps=100,
        save_steps=100,
        save_total_limit=2,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to="none",
        dataloader_num_workers=2,
    )

    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        peft_config=lora,
        processing_class=tok,
    )
    resume_from = None
    if args.resume:
        ckpts = glob.glob(os.path.join(OUT_DIR, "checkpoint-*"))
        if ckpts:
            resume_from = max(ckpts, key=lambda p: int(p.rsplit("-", 1)[1]))
            print(f"从 {resume_from} 继续训练")
        else:
            print("没有找到 checkpoint，从头开始训练")

    trainer.train(resume_from_checkpoint=resume_from)
    trainer.save_model(OUT_DIR)
    tok.save_pretrained(OUT_DIR)
    print(f"LoRA 权重已保存到 {OUT_DIR}")


if __name__ == "__main__":
    main()
