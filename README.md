# Qwen2.5-3B LoRA 思考链微调

用 LoRA SFT 让 Qwen2.5-3B 学会「先输出思考过程，再输出答案」。

- 基座：Qwen2.5-3B（bf16）
- 数据：6 个来源、3 个领域（C++ / HTML / 数学）的中文 CoT，共 2993 条，清洗后 2485 条
- 训练：单卡 RTX 4090 24GB，2 epoch / 302 步 / 约 27 分钟
- 结果：train_loss 0.804，hold-out eval_loss 0.809，token 准确率 79%
- 产物：约 30M 可训练参数的 LoRA adapter（115MB）

## 目录结构

```
├── code/
│   ├── finetune.py        # 数据清洗 + LoRA 训练（单文件）
│   ├── chat.py            # 对话脚本
│   └── chat01.py          # 基座模型最小示例
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
```

已验证版本：torch 2.6.0+cu124、transformers 5.23.0、peft 0.21.3、trl 1.18.0。

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

## 查看成果展示

直接用浏览器打开 `lora-showcase.html`，或在 GitHub 仓库 Settings → Pages 中选择 `main` / `/ (root)`，通过 Pages 地址访问。
展示页包含指标、数据分布、loss 曲线和 4 组微调前后真实输出对比，字体与图表均已本地化，可离线打开。

## 说明与限制

- 这次微调改变的是**输出格式与风格**，不代表模型推理能力有实质提升。
- 约 3k 数据只能覆盖简单推理，复杂多步问题仍需要更多高质量数据或强化学习。
- Qwen2.5 没有独立的思考通道，思考内容对用户可见。
- 数据集遵循 Apache License 2.0，详见 `database/README.md`。
