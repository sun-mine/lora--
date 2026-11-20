# Qwen2.5-3B LoRA 思考链微调 + AWQ 量化

用 LoRA SFT 让 Qwen2.5-3B 学会「先输出思考过程，再输出答案」，再用 AWQ 把合并后的模型压到 4-bit。

- 基座：Qwen2.5-3B（bf16）
- 数据：6 个来源、3 个领域（C++ / HTML / 数学）的中文 CoT，共 2993 条，清洗后 2485 条
- 训练：单卡 RTX 4090 24GB，2 epoch / 302 步 / 约 27 分钟
- 结果：train_loss 0.804，hold-out eval_loss 0.809，token 准确率 79%
- 产物：约 30M 可训练参数的 LoRA adapter（115MB）
- 量化：AWQ W4A16（group_size 128），合并模型从 6.2GB 压到 2.08GB，加载仅占 2.06GB 显存

## 目录结构

```
├── code/
│   ├── finetune.py        # 数据清洗 + LoRA 训练（单文件）
│   ├── quant_awq.py       # LoRA 合并 + AWQ 4-bit 量化
│   ├── chat.py            # 对话脚本
│   └── chat01.py          # 基座模型最小示例
├── AWQ_Qhua/              # 量化产物（本地生成，不入库）
├── database/              # 6 个来源的 CoT 数据
│   ├── M3/                # JSONL：question / thinking / answer
│   ├── deepseek/          # JSONL：question / cot / answer
│   ├── glm/               # TXT：【题目N】/ 思考：/ 答案：
│   ├── k2.7/              # JSONL：problem / reasoning / answer
│   ├── qwen/              # JSON：instruction / thinking / output
│   ├── doubao/            # JSON：instruction / input / output
│   └── README.md          # 数据集说明
├── lora-showcase.html     # 微调成果展示页
├── assets/charts.js       # 展示页图表
├── _shared/               # 字体与 ECharts（离线可用）
└── index.html             # 展示页入口跳转
```

## 环境

```bash
pip install torch transformers peft trl datasets accelerate
pip install autoawq   # 量化需要
```

已验证版本：torch 2.6.0+cu124、transformers 5.23.0、peft 0.21.3、trl 1.18.0、autoawq 0.2.9。

## 准备模型

模型体积约 6GB，不包含在本仓库中。从 HuggingFace 或 ModelScope 下载 Qwen2.5-3B，放到：

```
model/qwen2.5/
├── config.json
├── tokenizer.json
└── model-00001-of-00002.safetensors ...
```

## 训练

```bash
# 全量训练
python code/finetune.py

# 冒烟测试：200 条样本、5 步，确认流程可跑
python code/finetune.py --smoke

# 自定义轮数与最大长度
python code/finetune.py --epochs 3 --max_length 4096
```

训练脚本会完成：

1. 读取 6 个来源，统一成 `(问题, 思考, 答案)`
2. 跨源去重、过滤过短思考与空答案、丢弃超长样本
3. 用 ChatML 模板构造 `prompt` / `completion`，只对 completion 计算 loss
4. LoRA 训练并保存 adapter 到 `output/lora-qwen2.5-cot`

关键超参：

| 配置 | 值 |
| --- | --- |
| LoRA r / alpha / dropout | 16 / 32 / 0.05 |
| 目标模块 | q/k/v/o + gate/up/down |
| max_length | 4096 |
| batch × 梯度累积 | 1 × 16 |
| 学习率 | 1e-4，cosine，warmup 16 步 |
| epochs | 2 |
| 精度 | bf16 + gradient checkpointing |

显存占用约 8.7GB；如果显存更小，可降低 `--max_length` 或把 `gradient_accumulation_steps` 调大。

## 数据格式

训练时统一的 assistant 输出为：

```
思考：
<推理过程>

答案：
<最终答案>
```

各来源字段映射见 `code/finetune.py` 中的 `load_*` 函数。Doubao 的思考和答案混在同一字段，脚本按「## 代码实现」「```」「所以最终答案」等标记切分，切分不可靠的样本会被丢弃。

## 推理

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

model_dir = "model/qwen2.5"
adapter_dir = "output/lora-qwen2.5-cot"

tok = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForCausalLM.from_pretrained(
    model_dir, dtype=torch.bfloat16, device_map={"": 0}
)
model = PeftModel.from_pretrained(model, adapter_dir)

messages = [
    {"role": "system", "content": "你是一个善于分步思考的助手。请先写出思考过程，再给出最终答案。"},
    {"role": "user", "content": "一个长方形的长是 8 厘米，宽是 5 厘米，周长和面积是多少？"},
]
inputs = tok.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
inputs = tok(inputs, return_tensors="pt").to(model.device)

out = model.generate(**inputs, max_new_tokens=512, do_sample=True,
                     temperature=0.7, top_p=0.9,
                     pad_token_id=tok.eos_token_id)
print(tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

输出会以 `思考：` 开头，`答案：` 之后是最终结果。

## 量化（AWQ 4-bit）

LoRA adapter 本身不能直接量化，脚本会先在显存里把 adapter 合并回基座，再对完整模型做 AWQ W4A16 量化，不产生 6GB 的中间文件。

```bash
# 默认：128 条校准样本、序列长度 512、4-bit
python code/quant_awq.py

# 显存紧张时减少校准量
python code/quant_awq.py --calib_samples 64 --calib_seq_len 256

# INT8
python code/quant_awq.py --w_bit 8
```

| 项目 | 配置 |
| --- | --- |
| 量化方法 | AWQ（激活感知，需真实样本校准） |
| 位宽 / 分组 | 4-bit / group_size 128 |
| zero_point / kernel | true / GEMM |
| 校准数据 | 128 条训练集 CoT 样本，seq_len 512 |
| 量化范围 | 每层 q/k/v/o + gate/up/down 共 7 个线性层 |
| 保持原精度 | `lm_head`、`embed_tokens` |

体积与显存：

| 形态 | 磁盘体积 | 加载显存 |
| --- | --- | --- |
| LoRA adapter（单独） | 115MB | 需配合 6.2GB 基座 |
| 合并后 bf16 | 6.17GB | ≈ 6.2GB |
| AWQ 4-bit | 2.08GB | 2.06GB |

加载量化模型：

```python
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_quantized("AWQ_Qhua", fuse_layers=False)
```

验证输出（量化后，贪心解码）：

```
思考：
第一步，理清题意，求 3² + 4² 的值；第二步，计算并验证；第三步，得出结果。

计算：3² = 9，4² = 16，9 + 16 = 25。验证：25 = 5²，结果正确。

答案：
25
```

量化后「思考 / 答案」结构保持完整，数值计算无退化。

## 查看成果展示

直接用浏览器打开 `lora-showcase.html`，或在 GitHub 仓库 Settings → Pages 中选择 `main` / `/ (root)`，通过 Pages 地址访问。
展示页包含指标、数据分布、loss 曲线、4 组微调前后真实输出对比，以及量化产物的体积与配置，字体与图表均已本地化，可离线打开。

## 说明与限制

- 这次微调改变的是**输出格式与风格**，不代表模型推理能力有实质提升。
- 约 3k 数据只能覆盖简单推理，复杂多步问题仍需要更多高质量数据或强化学习。
- Qwen2.5 没有独立的思考通道，思考内容对用户可见。
- AWQ 是校准式量化，效果依赖校准分布：这里用训练集同分布的 CoT 样本，换到别的任务上建议重新采样校准数据。
- 用 transformers 原生 `from_pretrained` 加载 AWQ 模型需要额外的 `gptqmodel`；本仓库用 AutoAWQ 或 vLLM 加载。
- 数据集遵循 Apache License 2.0，详见 `database/README.md`。
