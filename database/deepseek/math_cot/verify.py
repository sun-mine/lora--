import json

path = r"f:\数据集\deepseek\math_cot\math_cot_3.jsonl"
lines = []
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            lines.append(line)

print(f"总行数: {len(lines)}")

errors = []
for i, line in enumerate(lines):
    try:
        obj = json.loads(line)
        for field in ["id", "question", "cot", "answer"]:
            if field not in obj:
                errors.append(f"第{i+1}行缺少字段: {field}")
        oid = obj.get("id", "")
        if not oid.startswith("math_3_"):
            errors.append(f"第{i+1}行id格式错误: {oid}")
        cot_len = len(obj.get("cot", ""))
        if cot_len < 300:
            errors.append(f"第{i+1}行cot长度不足: {cot_len}字")
    except json.JSONDecodeError as e:
        errors.append(f"第{i+1}行JSON解析失败: {e}")

if errors:
    print("发现错误:")
    for e in errors:
        print(f"  {e}")
else:
    print("所有50条数据格式验证通过！")

cot_lengths = [len(json.loads(line)["cot"]) for line in lines]
print(f"COT长度范围: {min(cot_lengths)} ~ {max(cot_lengths)} 字符")
print(f"COT平均长度: {sum(cot_lengths)/len(cot_lengths):.0f} 字符")

ids = [json.loads(line)["id"] for line in lines]
print(f"ID范围: {ids[0]} ~ {ids[-1]}")
print(f"ID唯一性: {len(set(ids)) == len(ids)}")