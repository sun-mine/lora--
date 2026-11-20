# -*- coding: utf-8 -*-
"""Qwen2.5-3B + CoT LoRA 合并后做 AWQ 4-bit 量化，产物输出到 AWQ_Qhua。

流程：加载基座 -> 合并 LoRA -> 用训练数据做校准 -> AWQ W4A16(GEMM) -> 保存

用法：
    /home/shipl/llm/bin/python code/quant_awq.py
    /home/shipl/llm/bin/python code/quant_awq.py --calib_samples 32 --calib_seq_len 256
"""

import argparse
import os
import random
import re
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finetune as ft  # 复用同一套数据清洗逻辑

from awq.models.qwen2 import Qwen2AWQForCausalLM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(ROOT, "model", "qwen2.5")
LORA_DIR = os.path.join(ROOT, "output", "lora-qwen2.5-cot")
OUT_DIR = os.path.join(ROOT, "AWQ_Qhua")


def build_calib_texts(tok, n_samples, seed=42):
    """从 6 个数据源抽出与训练分布一致的 (问题, 思考, 答案) 作为校准集"""
    pairs = (
        ft.load_m3()
        + ft.load_deepseek()
        + ft.load_k27()
        + ft.load_qwen()
        + ft.load_doubao()
        + ft.load_glm()
    )

    seen, rows = set(), []
    for q, t, a in pairs:
        if not all(isinstance(v, str) for v in (q, t, a)):
            continue
        q, t, a = q.strip(), t.strip(), a.strip()
        if len(t) < 20 or len(a) < 10:
            continue
        key = re.sub(r"\s+", "", q)
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append((q, t, a))

    random.Random(seed).shuffle(rows)

    samples = []
    for q, t, a in rows[:n_samples]:
        prompt = tok.apply_chat_template(
            [
                {"role": "system", "content": ft.SYSTEM_PROMPT},
                {"role": "user", "content": q},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        samples.append(f"{prompt}思考：\n{t}\n\n答案：\n{a}{tok.eos_token or ''}")
    return samples


def load_merged_model():
    """基座 + LoRA 合并成完整模型（只在显存里做，不落盘 6GB 中间文件）"""
    from peft import PeftModel

    print(f"加载基座: {BASE_DIR}")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_DIR, dtype=torch.bfloat16, device_map={"": 0}
    )
    print(f"合并 LoRA: {LORA_DIR}")
    model = PeftModel.from_pretrained(model, LORA_DIR)
    model = model.merge_and_unload()
    model.eval()
    # 校准阶段每个 decoder layer 都按同一份 kwargs 反复前向，KV cache 会跨 batch 累积出错
    model.config.use_cache = False
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib_samples", type=int, default=128, help="校准样本条数")
    parser.add_argument("--calib_seq_len", type=int, default=512, help="校准序列长度")
    parser.add_argument("--w_bit", type=int, default=4, choices=[4, 8])
    parser.add_argument("--group_size", type=int, default=128)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("AWQ 校准需要 GPU")

    tok = AutoTokenizer.from_pretrained(LORA_DIR)
    calib = build_calib_texts(tok, args.calib_samples)
    print(f"校准样本: {len(calib)} 条")

    model = load_merged_model()
    print(f"参数量: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B")

    # 只量化 decoder layer 内的线性层，lm_head / embed_tokens 自动保持原精度
    awq_model = Qwen2AWQForCausalLM(model, "qwen2", False, model.config, None, None)

    print("开始 AWQ 量化（含激活统计 + scale 搜索 + 权重打包）...")
    awq_model.quantize(
        tok,
        quant_config={
            "w_bit": args.w_bit,
            "q_group_size": args.group_size,
            "zero_point": True,
            "version": "GEMM",
        },
        calib_data=calib,
        max_calib_samples=len(calib),
        max_calib_seq_len=args.calib_seq_len,
        duo_scaling=True,
        apply_clip=True,
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    awq_model.save_quantized(OUT_DIR)
    tok.save_pretrained(OUT_DIR)

    size = sum(
        os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT_DIR) for f in fs
    )
    print(f"AWQ 量化完成 -> {OUT_DIR}（{size / 1e9:.2f} GB）")


if __name__ == "__main__":
    main()
