import json
import os

path = r'f:\数据集\M3\cpp\cot_02_algo.jsonl'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
valid = 0
entries = []
for l in lines:
    l = l.strip()
    if not l:
        continue
    try:
        obj = json.loads(l)
        valid += 1
        entries.append(obj)
    except Exception as e:
        print(f'Invalid: {e}')

print(f'Valid JSON lines: {valid}')

# Difficulty distribution
from collections import Counter
diffs = Counter(e['difficulty'] for e in entries)
print(f'Difficulty distribution: {dict(diffs)}')

# Verify ID range
ids = [e['id'] for e in entries]
print(f'ID range: {min(ids)} - {max(ids)}')
expected = [f'cpp_algo_{i:03d}' for i in range(1, 51)]
missing = set(expected) - set(ids)
print(f'Missing IDs: {sorted(missing) if missing else "none"}')
print(f'Extra IDs: {sorted(set(ids) - set(expected))}')

# Category analysis
import re
def classify(q):
    keywords = {
        '二分': '二分查找',
        '滑动窗口': '滑动窗口',
        '双指针': '双指针',
        '链表': '链表',
        '二叉树': '二叉树',
        '动态规划': '动态规划',
        '回溯': '回溯',
        '贪心': '贪心',
        '排序': '排序',
        'BFS': 'BFS',
        'DFS': 'DFS',
        '拓扑': '拓扑排序',
        '并查集': '并查集',
        'Dijkstra': '图算法',
        'KMP': '字符串匹配',
        '背包': '动态规划',
        '编辑距离': '动态规划',
        'LCA': '二叉树',
        '岛屿': 'BFS/DFS',
        '颜色分类': '排序',
        'Kadane': '动态规划',
        '单调队列': '滑动窗口',
        '中心扩展': '字符串',
        '荷兰': '排序',
        'Floyd': '链表/图',
        '优先队列': '堆/优先队列',
        '栈': '栈',
        '队列': 'BFS',
        '回文': '字符串',
        '矩阵': '二维DP',
    }
    for k, v in keywords.items():
        if k in q:
            return v
    return '其他'

# Get questions from a sample
cat_counter = Counter()
for e in entries:
    # Combine question + thinking + answer for classification
    text = e['question'] + e['thinking'] + e['answer']
    cats = set()
    for k, v in {
        '二分': '二分查找', '旋转': '二分查找', '搜索插入': '二分查找',
        '滑动窗口': '滑动窗口', '覆盖子串': '滑动窗口',
        '接雨水': '双指针', '三数之和': '双指针', '移动零': '双指针',
        '链表': '链表', 'LCA': '二叉树', '二叉树': '二叉树', '前序': '二叉树', '中序': '二叉树', '层序': '二叉树', '最大深度': '二叉树',
        '动态规划': '动态规划', '背包': '动态规划', 'Kadane': '动态规划', '编辑距离': '动态规划', '路径': '动态规划',
        '回溯': '回溯', '括号生成': '回溯', '全排列': '回溯', '子集': '回溯', '岛屿': '回溯/DFS', '单词搜索': '回溯/DFS',
        '排序': '排序', '颜色分类': '排序',
        'BFS': 'BFS', 'DFS': 'DFS', '课程表': '拓扑排序', 'Kahn': '拓扑排序',
        'Dijkstra': '图算法', 'KMP': '字符串匹配', 'K 排序': '链表', '合并': '链表/堆',
        '中心扩展': '字符串', '回文': '字符串', '异位': '字符串', '唯一': '字符串', '有效括号': '栈/字符串', '最长有效': '栈',
        '栈': '栈', '最小栈': '栈',
        '贪心': '贪心', '荷兰': '排序', '打家劫': '动态规划/贪心',
        '单调队列': '滑动窗口',
    }.items():
        if k in text:
            cats.add(v)
    if not cats:
        cats = {'其他'}
    for c in cats:
        cat_counter[c] += 1

print(f'\nAlgorithm category (by keywords, may overlap):')
for c, n in sorted(cat_counter.items(), key=lambda x: -x[1]):
    print(f'  {c}: {n}')

# File size
print(f'\nFile size: {os.path.getsize(path)} bytes')
