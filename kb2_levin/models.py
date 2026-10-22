"""
models.py
FT-Transformer, ResNet, MLP (chuyển thể từ RTDL / repo gốc) và TabTransformer.
Mọi mô hình có: features(x_num, x_cat) -> biểu diễn; self.head -> logits.
Nhờ vậy có thể thay head (linear / MLP 2x200) và đóng băng feature extractor.
"""
import math
from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class CatEmbedding(nn.Module):
    def __init__(self, cardinalities: List[int], d: int):
        super().__init__()
        self.register_buffer("offsets", torch.tensor([0] + cardinalities[:-1]).cumsum(0))
        self.emb = nn.Embedding(sum(cardinalities), d)
        nn.init.kaiming_uniform_(self.emb.weight, a=math.sqrt(5))

    def forward(self, x_cat):              # -> (B, n_cat, d)
        return self.emb(x_cat + self.offsets[None])


class TabularModel(nn.Module):
    head: nn.Module

    def features(self, x_num, x_cat):
        raise NotImplementedError

    def forward(self, x_num, x_cat=None):
        return self.head(self.features(x_num, x_cat))


# ============================================================================ MLP
class MLP(TabularModel):
    def __init__(self, n_num, cards, d_out, d_layers, dropout, d_embedding):
        super().__init__()
        d_in = n_num
        self.cat = None
        if cards:
            self.cat = CatEmbedding(cards, d_embedding)
            d_in += len(cards) * d_embedding
        self.layers = nn.ModuleList([nn.Linear(d_layers[i - 1] if i else d_in, d) for i, d in enumerate(d_layers)])
        self.dropout = dropout
        self.head = nn.Linear(d_layers[-1] if d_layers else d_in, d_out)

    def features(self, x_num, x_cat):
        x = [x_num]
        if self.cat is not None and x_cat is not None:
            x.append(self.cat(x_cat).flatten(1))
        x = torch.cat(x, dim=-1)
        for layer in self.layers:
            x = F.dropout(F.relu(layer(x)), self.dropout, self.training)
        return x


# ============================================================================ ResNet
class ResNet(TabularModel):
    def __init__(self, n_num, cards, d_out, d, d_hidden_factor, n_layers, hidden_dropout,
                 residual_dropout, d_embedding):
        super().__init__()
        d_in = n_num
        self.cat = None
        if cards:
            self.cat = CatEmbedding(cards, d_embedding)
            d_in += len(cards) * d_embedding
        d_hidden = int(d * d_hidden_factor)
        self.first_layer = nn.Linear(d_in, d)
        self.layers = nn.ModuleList([nn.ModuleDict({
            "norm": nn.BatchNorm1d(d), "linear0": nn.Linear(d, d_hidden), "linear1": nn.Linear(d_hidden, d)})
            for _ in range(n_layers)])
        self.last_norm = nn.BatchNorm1d(d)
        self.hidden_dropout, self.residual_dropout = hidden_dropout, residual_dropout
        self.head = nn.Linear(d, d_out)

    def features(self, x_num, x_cat):
        x = [x_num]
        if self.cat is not None and x_cat is not None:
            x.append(self.cat(x_cat).flatten(1))
        x = self.first_layer(torch.cat(x, dim=-1))
        for layer in self.layers:
            z = F.relu(layer["linear0"](layer["norm"](x)))
            z = F.dropout(z, self.hidden_dropout, self.training)
            z = F.dropout(layer["linear1"](z), self.residual_dropout, self.training)
            x = x + z
        return F.relu(self.last_norm(x))


# ============================================================================ FT-Transformer
def reglu(x):
    a, b = x.chunk(2, dim=-1)
    return a * F.relu(b)


class FTTokenizer(nn.Module):
    def __init__(self, n_num, cards, d_token):
        super().__init__()
        self.cat = CatEmbedding(cards, d_token) if cards else None
        n_bias = n_num + (len(cards) if cards else 0)
        self.weight = nn.Parameter(torch.empty(n_num + 1, d_token))   # +1 cho [CLS]
        self.bias = nn.Parameter(torch.empty(n_bias, d_token))
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.bias, a=math.sqrt(5))

    def forward(self, x_num, x_cat):
        x_num = torch.cat([torch.ones(len(x_num), 1, device=x_num.device), x_num], dim=1)
        x = self.weight[None] * x_num[:, :, None]
        if self.cat is not None and x_cat is not None:
            x = torch.cat([x, self.cat(x_cat)], dim=1)
        bias = torch.cat([torch.zeros(1, self.bias.shape[1], device=x.device), self.bias])
        return x + bias[None]


class MHA(nn.Module):
    def __init__(self, d, n_heads, dropout):
        super().__init__()
        self.W_q, self.W_k, self.W_v = nn.Linear(d, d), nn.Linear(d, d), nn.Linear(d, d)
        self.W_out = nn.Linear(d, d) if n_heads > 1 else None
        for m in [self.W_q, self.W_k, self.W_v]:
            nn.init.zeros_(m.bias)
        if self.W_out is not None:
            nn.init.zeros_(self.W_out.bias)
        self.n_heads, self.dropout = n_heads, nn.Dropout(dropout) if dropout else None

    def _split(self, x):
        b, t, d = x.shape
        return x.reshape(b, t, self.n_heads, d // self.n_heads).transpose(1, 2)

    def forward(self, x_q, x_kv):
        q, k, v = self._split(self.W_q(x_q)), self._split(self.W_k(x_kv)), self._split(self.W_v(x_kv))
        att = F.softmax(q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1]), dim=-1)
        if self.dropout is not None:
            att = self.dropout(att)
        x = (att @ v).transpose(1, 2).reshape(x_q.shape[0], x_q.shape[1], -1)
        return self.W_out(x) if self.W_out is not None else x


class FTTransformer(TabularModel):
    def __init__(self, n_num, cards, d_out, d_token, n_layers, n_heads, d_ffn_factor,
                 attention_dropout, ffn_dropout, residual_dropout):
        super().__init__()
        self.tokenizer = FTTokenizer(n_num, cards, d_token)
        d_hidden = int(d_token * d_ffn_factor)
        self.layers = nn.ModuleList()
        for i in range(n_layers):
            layer = nn.ModuleDict({"attention": MHA(d_token, n_heads, attention_dropout),
                                   "linear0": nn.Linear(d_token, d_hidden * 2),   # ReGLU
                                   "linear1": nn.Linear(d_hidden, d_token),
                                   "norm1": nn.LayerNorm(d_token)})
            if i:   # prenormalization: lớp đầu không có norm0
                layer["norm0"] = nn.LayerNorm(d_token)
            self.layers.append(layer)
        self.last_norm = nn.LayerNorm(d_token)
        self.ffn_dropout, self.residual_dropout = ffn_dropout, residual_dropout
        self.head = nn.Linear(d_token, d_out)

    def features(self, x_num, x_cat):
        x = self.tokenizer(x_num, x_cat)
        for i, layer in enumerate(self.layers):
            last = i + 1 == len(self.layers)
            r = layer["norm0"](x) if "norm0" in layer else x
            r = layer["attention"](r[:, :1] if last else r, r)   # lớp cuối chỉ cần [CLS]
            if last:
                x = x[:, :1]
            x = x + F.dropout(r, self.residual_dropout, self.training)
            r = reglu(layer["linear0"](layer["norm1"](x)))
            r = layer["linear1"](F.dropout(r, self.ffn_dropout, self.training))
            x = x + F.dropout(r, self.residual_dropout, self.training)
        return F.relu(self.last_norm(x[:, 0]))


# ============================================================================ TabTransformer
class TTBlock(nn.Module):
    def __init__(self, d, n_heads, attn_dropout, ff_dropout):
        super().__init__()
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, n_heads, dropout=attn_dropout, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Dropout(ff_dropout), nn.Linear(4 * d, d))

    def forward(self, x):
        h = self.n1(x)
        x = x + self.attn(h, h, h, need_weights=False)[0]
        return x + self.ff(self.n2(x))


class TabTransformer(TabularModel):
    """Transformer cho đặc trưng phân loại + LayerNorm cho đặc trưng số, nối lại rồi qua MLP."""

    def __init__(self, n_num, cards, d_out, d_embedding, n_layers, n_heads, attention_dropout, ff_dropout):
        super().__init__()
        self.cat = None
        n_cat = len(cards) if cards else 0
        if n_cat:
            self.cat = CatEmbedding(cards, d_embedding)
            self.blocks = nn.ModuleList([TTBlock(d_embedding, n_heads, attention_dropout, ff_dropout)
                                         for _ in range(n_layers)])
        self.num_norm = nn.LayerNorm(n_num)
        d_in = n_num + n_cat * d_embedding
        self.mlp = nn.Sequential(nn.Linear(d_in, 4 * d_in), nn.ReLU(), nn.Linear(4 * d_in, 2 * d_in), nn.ReLU())
        self.head = nn.Linear(2 * d_in, d_out)

    def features(self, x_num, x_cat):
        parts = [self.num_norm(x_num)]
        if self.cat is not None and x_cat is not None:
            h = self.cat(x_cat)
            for b in self.blocks:
                h = b(h)
            parts.append(h.flatten(1))
        return self.mlp(torch.cat(parts, dim=-1))


# ============================================================================ factory
def build_model(name: str, n_num: int, cards: Optional[List[int]], d_out: int, hp: dict) -> TabularModel:
    if name == "mlp":
        return MLP(n_num, cards, d_out, list(hp["d_layers"]), hp["dropout"], hp["d_embedding"])
    if name == "resnet":
        return ResNet(n_num, cards, d_out, hp["d"], hp["d_hidden_factor"], hp["n_layers"],
                      hp["hidden_dropout"], hp["residual_dropout"], hp["d_embedding"])
    if name == "ft_transformer":
        return FTTransformer(n_num, cards, d_out, hp["d_token"], hp["n_layers"], hp.get("n_heads", 8),
                             hp["d_ffn_factor"], hp["attention_dropout"], hp["ffn_dropout"],
                             hp["residual_dropout"])
    if name == "tab_transformer":
        d = int(math.ceil(hp["d_embedding"] / hp["n_heads"]) * hp["n_heads"])   # chia hết cho số head
        return TabTransformer(n_num, cards, d_out, d, hp["n_layers"], hp["n_heads"],
                              hp["attention_dropout"], hp["ff_dropout"])
    raise ValueError(name)


def replace_head(model: TabularModel, d_out: int, mlp_head: bool, hidden: int = 200):
    """Khởi tạo lại head: linear hoặc MLP 2 lớp x 200 neuron (giống load_transfer_model_from_checkpoint)."""
    d_in = model.head.in_features if isinstance(model.head, nn.Linear) else model.head[0].in_features
    model.head = (nn.Sequential(nn.Linear(d_in, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(),
                                nn.Linear(hidden, d_out)) if mlp_head else nn.Linear(d_in, d_out))
    return model


def freeze_feature_extractor(model: TabularModel):
    for n, p in model.named_parameters():
        p.requires_grad = n.startswith("head.")
    model._frozen = True
    return model
