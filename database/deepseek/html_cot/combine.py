import json
import os

# Collect all data from part files
all_data = []

# Read gen_all.py (entries 1-10)
import importlib.util
def load_data_from_file(filepath):
    spec = importlib.util.spec_from_file_location("module", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.data

all_data.extend(load_data_from_file("gen_all.py"))
all_data.extend(load_data_from_file("gen_part2.py"))
all_data.extend(load_data_from_file("gen_part3.py"))
all_data.extend(load_data_from_file("gen_part4.py"))
all_data.extend(load_data_from_file("gen_part5.py"))
all_data.extend(load_data_from_file("gen_part6.py"))
all_data.extend(load_data_from_file("gen_part7.py"))
all_data.extend(load_data_from_file("gen_part8.py"))
all_data.extend(load_data_from_file("gen_part9.py"))
all_data.extend(load_data_from_file("gen_part10.py"))

print(f"Total entries collected: {len(all_data)}")

# Verify unique IDs
ids = [d['id'] for d in all_data]
if len(ids) != len(set(ids)):
    print("WARNING: Duplicate IDs found!")
    from collections import Counter
    for k, v in Counter(ids).items():
        if v > 1:
            print(f"  {k}: {v} times")

# Check cot length
for d in all_data:
    cot_len = len(d['cot'])
    if cot_len < 300:
        print(f"WARNING: {d['id']} cot length is {cot_len} chars (< 300)")

# Write JSONL
output_path = "html_cot_3.jsonl"
with open(output_path, 'w', encoding='utf-8') as f:
    for entry in all_data:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"Written to {output_path}")
print(f"File size: {os.path.getsize(output_path)} bytes")

# Verify JSONL
with open(output_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f"Lines in file: {len(lines)}")
for i, line in enumerate(lines):
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"ERROR at line {i+1}: {e}")
        print(f"  Line preview: {line[:100]}")