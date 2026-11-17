import os
import glob
import json
import math
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# ============================================================
# 0. 配置
# ============================================================
DATA_DIR = "database"          # ★ 改成你的数据根目录（下面会拼 DATA_DIR/M3/**/*.jsonl）
CKPT_PATH = "mini_gpt.pt"

BLOCK_SIZE = 128
BATCH_SIZE = 32
MAX_STEPS = 5000
EVAL_INTERVAL = 100
LR = 3e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 模型配置（小模型，单卡可训）
D_MODEL = 256
N_HEADS = 8
N_LAYERS = 4
DROPOUT = 0.1

torch.manual_seed(42)

# ============================================================
# 1. 数据读取与清洗（复用你之前的逻辑）
# ============================================================
def _read_jsonl(path):
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_text_corpus(data_dir):
    """读取 M3 下所有 jsonl，清洗去重，拼成训练文本列表"""
    texts = []
    seen = set()
    pattern = f"{data_dir}/M3/**/*.jsonl"
    files = glob.glob(pattern, recursive=True)
    print(f"找到 {len(files)} 个 jsonl 文件")
    for path in files:
        for x in _read_jsonl(path):
            q, t, a = x.get("question"), x.get("thinking"), x.get("answer")
            # 类型检查
            if not all(isinstance(v, str) for v in (q, t, a)):
                continue
            q, t, a = q.strip(), t.strip(), a.strip()
            # 质量过滤
            if len(t) < 20 or len(a) < 10:
                continue
            # 跨源去重
            key = re.sub(r"\s+", "", q)
            if not key or key in seen:
                continue
            seen.add(key)
            texts.append(f"问题：{q}\n思考：{t}\n答案：{a}\n\n")
    return texts


# ============================================================
# 2. 字符级词表
# ============================================================
def build_vocab(texts):
    corpus = "".join(texts)
    chars = sorted(set(corpus))
    stoi = {c: i for i, c in enumerate(chars)}
    itos = {i: c for c, i in stoi.items()}
    return corpus, stoi, itos


# ============================================================
# 3. Dataset
# ============================================================
class CharDataset(Dataset):
    def __init__(self, ids, block_size):
        self.ids = ids
        self.block_size = block_size

    def __len__(self):
        return max(0, len(self.ids) - self.block_size)

    def __getitem__(self, i):
        x = self.ids[i : i + self.block_size]
        y = self.ids[i + 1 : i + 1 + self.block_size]
        return x, y


# ============================================================
# 4. 模型组件
# ============================================================
def scaled_dot_product_attention(q, k, v, mask=None):
    d_k = q.size(-1)
    scores = q @ k.transpose(-2, -1) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    attn = F.softmax(scores, dim=-1)
    return attn @ v, attn


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.proj = nn.Linear(d_model, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=-1)

        def split(t):
            return t.view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        q, k, v = split(q), split(k), split(v)
        out, _ = scaled_dot_product_attention(q, k, v, mask)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.dropout(self.proj(out))


class SwiGLU(nn.Module):
    def __init__(self, d_model, hidden_mult=4, dropout=0.1):
        super().__init__()
        hidden = int(d_model * hidden_mult * 2 / 3)
        self.gate = nn.Linear(d_model, hidden, bias=False)
        self.up = nn.Linear(d_model, hidden, bias=False)
        self.down = nn.Linear(hidden, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.down(F.silu(self.gate(x)) * self.up(x)))


class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d_model))

    def forward(self, x):
        norm = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return norm * self.weight


class Block(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        self.norm1 = RMSNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads, dropout)
        self.norm2 = RMSNorm(d_model)
        self.ffn = SwiGLU(d_model, dropout=dropout)

    def forward(self, x, mask=None):
        x = x + self.attn(self.norm1(x), mask)
        x = x + self.ffn(self.norm2(x))
        return x


class LearnedPosEmb(nn.Module):
    def __init__(self, max_len, d_model):
        super().__init__()
        self.emb = nn.Embedding(max_len, d_model)

    def forward(self, x):
        T = x.size(1)
        return x + self.emb(torch.arange(T, device=x.device))[None]


class GPT(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=8, n_layers=4,
                 max_len=128, dropout=0.1):
        super().__init__()
        self.max_len = max_len
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = LearnedPosEmb(max_len, d_model)
        self.blocks = nn.ModuleList(
            [Block(d_model, n_heads, dropout) for _ in range(n_layers)]
        )
        self.norm_f = RMSNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        # 权重共享
        self.lm_head.weight = self.tok_emb.weight
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx):
        B, T = idx.shape
        assert T <= self.max_len, f"序列长度 {T} 超过 max_len {self.max_len}"
        x = self.pos_emb(self.tok_emb(idx))
        mask = torch.tril(torch.ones(T, T, device=idx.device))[None, None, :, :].bool()
        for blk in self.blocks:
            x = blk(x, mask)
        x = self.norm_f(x)
        return self.lm_head(x)  # (B, T, vocab)


# ============================================================
# 5. 训练
# ============================================================
@torch.no_grad()
def evaluate(model, loader, vocab_size):
    model.eval()
    total, cnt = 0.0, 0
    for x, y in loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
        total += loss.item()
        cnt += 1
    model.train()
    return total / max(1, cnt)


def train(model, train_ds, val_ds, vocab_size):
    model.to(DEVICE)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=0)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)

    step = 0
    model.train()
    while step < MAX_STEPS:
        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            logits = model(x)
            loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            step += 1
            if step % 50 == 0:
                print(f"step {step:5d} | train loss {loss.item():.4f}")
            if step % EVAL_INTERVAL == 0:
                vl = evaluate(model, val_loader, vocab_size)
                print(f"  >> val loss {vl:.4f}")
            if step >= MAX_STEPS:
                break
    return model


# ============================================================
# 6. 生成
# ============================================================
@torch.no_grad()
def generate_text(model, prompt, stoi, itos, max_new_tokens=120, temperature=0.8):
    model.eval()
    idx = [stoi.get(c, 0) for c in prompt]
    idx = torch.tensor([idx], device=DEVICE)
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -model.max_len:]
        logits = model(idx_cond)[:, -1, :] / max(temperature, 1e-6)
        probs = F.softmax(logits, dim=-1)
        next_tok = torch.multinomial(probs, 1)
        idx = torch.cat([idx, next_tok], dim=1)
    return "".join(itos[i] for i in idx[0].tolist())


# ============================================================
# 7. 主流程
# ============================================================
def main():
    # 数据
    texts = load_text_corpus(DATA_DIR)
    if not texts:
        raise RuntimeError("没有读到数据，请检查 DATA_DIR 路径是否正确")
    print(f"样本数: {len(texts)}")

    corpus, stoi, itos = build_vocab(texts)
    vocab_size = len(stoi)
    print(f"字符种类(vocab): {vocab_size}, 语料总字符: {len(corpus)}")

    # 编码 + 划分
    data_ids = torch.tensor([stoi[c] for c in corpus], dtype=torch.long)
    n = int(0.97 * len(data_ids))
    train_ids, val_ids = data_ids[:n], data_ids[n:]

    train_ds = CharDataset(train_ids, BLOCK_SIZE)
    val_ds = CharDataset(val_ids, BLOCK_SIZE)
    print(f"train 块数: {len(train_ds)}, val 块数: {len(val_ds)}")
    if len(train_ds) == 0:
        raise RuntimeError("数据太少，不够一个 block_size，请增大数据或减小 BLOCK_SIZE")

    # 模型
    model = GPT(vocab_size=vocab_size, d_model=D_MODEL, n_heads=N_HEADS,
                n_layers=N_LAYERS, max_len=BLOCK_SIZE, dropout=DROPOUT)
    print(f"参数量: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")

    # 训练
    model = train(model, train_ds, val_ds, vocab_size)

    # 生成示例
    print("\n===== 生成示例 =====")
    for p in ["问题：什么是机器学习？\n思考：", "问题：如何学习编程？\n思考："]:
        print(generate_text(model, p, stoi, itos, max_new_tokens=100))

    # 保存
    torch.save({
        "model": model.state_dict(),
        "stoi": stoi,
        "itos": itos,
        "config": dict(vocab_size=vocab_size, d_model=D_MODEL, n_heads=N_HEADS,
                       n_layers=N_LAYERS, max_len=BLOCK_SIZE, dropout=DROPOUT),
    }, CKPT_PATH)
    print(f"\n模型已保存到 {CKPT_PATH}")


if __name__ == "__main__":
    main()