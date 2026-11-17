import json

with open('cpp_cot_3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")
print("Checking all entries have required fields...")
ok = True
for i, entry in enumerate(data):
    if 'instruction' not in entry or 'input' not in entry or 'output' not in entry:
        print(f"Entry {i} missing fields!")
        ok = False
    if entry['input'] != '':
        print(f"Entry {i} input is not empty")
    if not entry['instruction'] or not entry['output']:
        print(f"Entry {i} has empty instruction or output")
        ok = False

print("Checking for duplicate instructions...")
instructions = [e['instruction'] for e in data]
unique = set(instructions)
if len(unique) != len(instructions):
    print("Warning: duplicate instructions found!")
    from collections import Counter
    for instr, count in Counter(instructions).items():
        if count > 1:
            print(f"  Duplicate: {instr[:50]}...")
else:
    print("No duplicates found.")

print(f"\nTopics covered:")
topics = {
    '文件操作': 0,
    '多线程/并发': 0,
    '网络编程': 0,
    '设计模式': 0,
    'C++特性': 0,
    '算法': 0,
}
keywords = {
    '文件操作': ['文件', '日志', 'INI', 'CSV', '目录', '文件锁', '内存映射', '文件复制'],
    '多线程/并发': ['线程', '线程池', '锁', '生产者', '消费者', 'mutex', 'future', 'promise', '信号量', '并行'],
    '网络编程': ['TCP', 'UDP', 'HTTP', 'socket', 'select', 'IO多路复用', '广播', '聊天室'],
    '设计模式': ['单例', '工厂', '策略', '观察者', '装饰器', '适配器', '命令', '责任链', '状态', '中介者', '访问者', '模板方法', '备忘录', '对象池'],
    'C++特性': ['RAII', 'constexpr', '内存序', '可变参数', '移动语义', '类型擦除', 'variant', '智能指针', 'shared_ptr', 'memory_order'],
    '算法': ['滑动窗口', '动态规划', '时间轮', '正则', 'JSON'],
}
for entry in data:
    instr = entry['instruction']
    for topic, kws in keywords.items():
        if any(kw in instr for kw in kws):
            topics[topic] += 1

for t, c in topics.items():
    print(f"  {t}: {c}题")

if ok:
    print("\nJSON validation PASSED!")
else:
    print("\nJSON validation FAILED!")

print(f"\nSample entry #{1}:")
print(f"Instruction: {data[0]['instruction']}")
print(f"Output length: {len(data[0]['output'])} chars")
