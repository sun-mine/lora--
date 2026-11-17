---
license: Apache License 2.0
language:
  - zh
  - en
tags:
  - CoT
  - Agents
---
数据集文件元信息以及数据文件，请浏览“数据集文件”页面获取。

您可以通过如下GIT Clone命令，或者ModelScope SDK来下载数据集

#### 下载方法 
:modelscope-code[]{type="sdk"}
:modelscope-code[]{type="git"}

## 概述

本数据集合集合计约 **3,050 条** 高质量中文 Chain-of-Thought (CoT) 思考链数据，涵盖 C++ 编程、HTML/CSS/JavaScript 网页设计、数学三大领域，由 **6 个不同模型/来源** 生成，适用于大语言模型指令微调 (SFT)、推理能力训练、多源数据对比研究等场景。

## 目录结构

```
F:\数据集\
├── README.md                  # 本文件
├── M3/                        # M3 模型生成 (500条)
│   ├── cpp/                   #   C++编程 (150条, jsonl)
│   ├── html/                  #   HTML设计 (150条, jsonl)
│   └── math/                  #   数学题   (200条, jsonl)
├── deepseek/                  # DeepSeek 模型生成 (500条)
│   ├── cpp_cot/               #   C++编程 (150条, jsonl)
│   ├── html_cot/              #   HTML设计 (150条, jsonl)
│   └── math_cot/              #   数学题   (200条, jsonl)
├── glm/                       # GLM 模型生成 (500条)
│   ├── cpp题目/               #   C++编程 (150条, txt)
│   ├── html设计/              #   HTML设计 (150条, txt)
│   └── 数学题/                #   数学题   (200条, txt)
├── k2.7/                      # K2.7 模型生成 (500条)
│   ├── cpp/                   #   C++编程 (150条, jsonl)
│   ├── html/                  #   HTML设计 (150条, jsonl)
│   └── math/                  #   数学题   (200条, jsonl)
├── qwen/                      # Qwen 模型生成 (~551条)
│   ├── cpp/                   #   C++编程 (192条, json)
│   ├── html/                  #   HTML设计 (151条, json)
│   └── math/                  #   数学题   (208条, json)
└── doubao/                    # Doubao 模型生成 (500条)
    └── cot_data/
        ├── cpp/               #   C++编程 (150条, json)
        ├── html/              #   HTML设计 (150条, json)
        └── math/              #   数学题   (200条, json)
```

## 统计总览

| 来源 | 模型 | C++ | HTML | 数学 | 总计 | 格式 |
|------|------|-----|------|------|------|------|
| M3 | M3 | 150 | 150 | 200 | 500 | JSONL |
| deepseek | DeepSeek | 150 | 150 | 200 | 500 | JSONL |
| glm | GLM | 150 | 150 | 200 | 500 | TXT |
| k2.7 | K2.7 | 150 | 150 | 200 | 500 | JSONL |
| qwen | Qwen | 192 | 151 | 208 | ~551 | JSON |
| doubao | Doubao | 150 | 150 | 200 | 500 | JSON |
| **总计** | | **~942** | **~901** | **~1,208** | **~3,051** | |

## 各来源数据格式

### 1. M3 (JSONL)

每行一条 JSON，字段含 **id**、**category**、**difficulty**、**question**、**thinking**、**answer**。自带难度标注和分类标签。

**C++** (3文件 x 50条)：基础与STL → 算法与数据结构 → 面向对象与设计模式
**HTML** (3文件 x 50条)：布局与结构 → CSS样式与动画 → 响应式与交互
**数学** (4文件 x 50条)：代数与方程 → 几何与图形 → 概率与统计 → 应用题与综合

```json
{"id": "cpp_basic_001", "category": "C++基础与STL", "difficulty": "easy", "question": "...", "thinking": "1. 首先...", "answer": "..."}
```

### 2. DeepSeek (JSONL)

每行一条 JSON，字段含 **id**、**question**、**cot**、**answer**。思考过程较详细，带有问题分析和方法对比。

```json
{"id": "cpp_1_001", "question": "指针和引用有什么区别？", "cot": "首先，我需要理清...", "answer": "..."}
```

### 3. GLM (TXT)

纯文本格式，以 `【题目N】` 标记，包含 `思考：` 和 `答案：` 段落。风格口语化，像真人答题。

```
【题目1】请解释C++中int和long的区别
思考：第一步，分析两者的基本定义...第二步，对比系统差异...第三步，得出结论...
答案：int和long都是C++中的整型数据类型...
```

### 4. K2.7 (JSONL)

每行一条 JSON，字段含 **problem**、**reasoning**、**answer**。

```json
{"problem": "设计一个三栏圣杯布局...", "reasoning": "首先分析页面结构...", "answer": "..."}
```

### 5. Qwen (JSON)

标准 JSON 数组，字段含 **instruction**、**thinking**、**output**。思考过程与代码分离，结构清晰。

```json
[{"instruction": "请解释单链表的反转算法...", "thinking": "首先...", "output": "..."}]
```

### 6. Doubao (JSON)

标准 JSON 数组，字段含 **instruction**、**input**、**output**。思考过程与答案合并于 output 字段中。

```json
[{"instruction": "输出Hello World。", "input": "", "output": "让我一步步思考...\n\n```cpp\n..."}]
```

## 格式对比

| 特性 | M3 | DeepSeek | GLM | K2.7 | Qwen | Doubao |
|------|-----|----------|-----|------|------|--------|
| 文件格式 | JSONL | JSONL | TXT | JSONL | JSON | JSON |
| 难度标注 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 分类标签 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 思考字段 | thinking | cot | 内嵌 | reasoning | thinking | output内 |
| 答案字段 | answer | answer | 内嵌 | answer | output | output内 |
| 唯一ID | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

## 数据特点

1. **多源多样性**：6 个不同模型生成，可对比不同模型在 CoT 推理上的风格差异
2. **三领域覆盖**：C++ 编程、HTML 网页设计、数学，难度从入门到进阶
3. **真实思考过程**：每条数据都包含类似人类的分步推理，非直接给出答案
4. **格式多样**：JSON、JSONL、TXT 三种格式，满足不同训练框架需求
5. **中文优化**：全部中文，天然适合中文 LLM 训练

## 适用场景

- 大语言模型 (LLM) 监督微调 (SFT)
- 多源数据对比训练研究
- 代码生成与数学推理能力训练
- 中文编程助手 / 教育答疑系统训练

## 加载示例

### JSONL 格式 (M3 / DeepSeek / K2.7)

```python
import json

data = []
with open('M3/cpp/cot_01_basic.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))
print(f"加载 {len(data)} 条数据")
```

### JSON 格式 (Qwen / Doubao)

```python
import json

with open('qwen/cpp/cpp_cot_1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"加载 {len(data)} 条数据")
```

### TXT 格式 (GLM)

```python
import re

with open('glm/cpp题目/cpp_agent_1.txt', 'r', encoding='utf-8') as f:
    content = f.read()
problems = re.split(r'\n(?=【题目\d+】)', content)
print(f"共 {len(problems)} 道题")
```

### 统一转换为 SFT 格式

```python
def to_sft_format(item, source):
    if source == 'M3':
        return {'instruction': item['question'], 'input': '',
                'output': item['thinking'] + '\n\n' + item['answer']}
    elif source == 'deepseek':
        return {'instruction': item['question'], 'input': '',
                'output': item['cot'] + '\n\n' + item['answer']}
    elif source == 'k2.7':
        return {'instruction': item['problem'], 'input': '',
                'output': item['reasoning'] + '\n\n' + item['answer']}
    elif source == 'qwen':
        return {'instruction': item['instruction'], 'input': '',
                'output': item['thinking'] + '\n\n' + item['output']}
    elif source == 'doubao':
        return item  # 已经是标准格式
```
