"""Innate4LayerNet: the 4-layer model of docs/research/four-layer-dl-architecture.md.

L1 Gaussian Range Encoding (G=20) + multi-scale masked Conv1D (k=1,3,5) + LayerNorm, jitter U[0.98,1.02] in training.
L2 BiGRU + masked multi-head self-attention + attentive statistics pooling -> e_q (64, L2-norm), u_q (32).
L3 time- and attempt-aware set matching + drift guard (hybrid anchor mu_0 + time-decayed prototype mu_decay).
L4 dual-stream calibration head: s_human (u_q + f_tab + h_burst) and s_owner (v_match + k + dt); tau(k, dt) is fitted by eval/calibrate.py.

Every op has a NumPy twin in backend/app/scoring/dl_adapter.py (the Vercel runtime); keep them identical (export/verify_parity.py).
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from app.scoring.dl_adapter import (ANCHOR_M, BURST_IDX, E_DIM, F_NAMES, G, L_MAX, N_CONT, N_HEADS, N_BURST, N_CTX, RANGES, U_DIM)

D_GRU = 48  # per direction
D = 2 * D_GRU


class Innate4LayerNet(nn.Module):
    def __init__(self, n_tab: int = len(F_NAMES)):
        super().__init__()
        lo, hi = torch.tensor(RANGES, dtype=torch.float32).T
        self.register_buffer("lo", lo)
        self.register_buffer("hi", hi)
        # ---- layer 1 ----
        self.conv1, self.conv3, self.conv5 = (nn.Conv1d(N_CONT * G, 32, k, padding=k // 2) for k in (1, 3, 5))
        self.proj, self.ln1 = nn.Linear(96, 64), nn.LayerNorm(64)
        # ---- layer 2 ----
        self.gru_f, self.gru_b = nn.GRUCell(64, D_GRU), nn.GRUCell(64, D_GRU)
        self.wq, self.wk, self.wv, self.wo = (nn.Linear(D, D) for _ in range(4))
        self.ln2 = nn.LayerNorm(D)
        self.att1, self.att2 = nn.Linear(D, D_GRU), nn.Linear(D_GRU, 1)
        self.e_head, self.u_head = nn.Linear(2 * D, E_DIM), nn.Linear(2 * D, U_DIM)
        self.drop = nn.Dropout(0.1)
        # ---- layer 3 ----
        self.att_c = nn.Parameter(torch.tensor([1.0, 0.0]))  # temperature of cosine attention: softplus(c0 + c1*log(1+k))
        self.att_t = nn.Parameter(torch.tensor([-0.3]))  # time-decay weight on log(1+dt_hours)
        # ---- layer 4 ----
        self.own1, self.own2 = nn.Linear(10, 16), nn.Linear(16, 1)
        self.hum1, self.hum2 = nn.Linear(U_DIM + n_tab + N_BURST, 32), nn.Linear(32, 1)

    # layers 1-2
    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        pooled = self.pooled(x)
        return F.normalize(self.e_head(pooled), dim=-1, eps=1e-8), self.u_head(pooled)

    def pooled(self, x: torch.Tensor) -> torch.Tensor:
        """Attentive statistics (B, 2*D) shared by e_head and u_head."""
        m = x[..., 9]
        if self.training:  # BehavePassDB-style timing jitter, one factor per sample, on the time channels only
            x = torch.cat([x[..., :6] * torch.empty(x.shape[0], 1, 1, device=x.device).uniform_(0.98, 1.02), x[..., 6:]], -1)
        sig = ((self.hi - self.lo) / G)[:, None]
        centers = self.lo[:, None] + (self.hi - self.lo)[:, None] * (torch.arange(G, device=x.device) + 0.5) / G
        gre = torch.exp(-0.5 * ((x[..., :N_CONT, None] - centers) / sig) ** 2).flatten(2) * m[..., None]
        ct = gre.transpose(1, 2)
        h = F.relu(torch.cat([c(ct) for c in (self.conv1, self.conv3, self.conv5)], 1).transpose(1, 2)) * m[..., None]
        h = self.ln1(self.proj(h)) * m[..., None]
        B, L, _ = h.shape
        outs = []
        for cell, rev in ((self.gru_f, False), (self.gru_b, True)):
            s, o = h.new_zeros(B, D_GRU), [None] * L
            for t in (range(L - 1, -1, -1) if rev else range(L)):
                new, mt = cell(h[:, t], s), m[:, t, None]
                s = mt * new + (1 - mt) * s
                o[t] = s * mt
            outs.append(torch.stack(o, 1))
        h = self.drop(torch.cat(outs, -1))
        hd = D // N_HEADS
        q, k, v = (w(h).view(B, L, N_HEADS, hd).transpose(1, 2) for w in (self.wq, self.wk, self.wv))
        s = q @ k.transpose(-1, -2) / math.sqrt(hd) + torch.where(m[:, None, None, :] > 0, 0.0, -1e9)
        h = self.ln2(h + self.wo((s.softmax(-1) @ v).transpose(1, 2).reshape(B, L, D))) * m[..., None]
        al = (self.att2(torch.tanh(self.att1(h)))[..., 0] + torch.where(m > 0, 0.0, -1e9)).softmax(-1)
        mu = (al[..., None] * h).sum(1)
        sd = torch.sqrt(((al[..., None] * h * h).sum(1) - mu * mu).clamp_min(0) + 1e-6)
        return torch.cat([mu, sd], -1)

    # layer 3
    def match(self, e_q, gal_e, gal_dt_h, gal_mask) -> torch.Tensor:
        eps = 1e-8
        k = gal_mask.sum(1)
        first = (gal_mask.cumsum(1) <= ANCHOR_M).float() * gal_mask
        mu0 = F.normalize((gal_e * first[..., None]).sum(1) / first.sum(1, keepdim=True).clamp_min(1), dim=-1, eps=eps)
        cos = (gal_e * e_q[:, None]).sum(-1)
        temp = F.softplus(self.att_c[0] + self.att_c[1] * torch.log1p(k))
        logit = torch.where(gal_mask > 0, temp[:, None] * cos + self.att_t[0] * torch.log1p(gal_dt_h.clamp_min(0)), torch.full_like(cos, -1e9))
        mud = F.normalize((logit.softmax(1)[..., None] * gal_e).sum(1), dim=-1, eps=eps)
        n = k.clamp_min(1)
        cm = (cos * gal_mask).sum(1) / n
        std = torch.sqrt((((cos - cm[:, None]) * gal_mask) ** 2).sum(1) / n + 1e-8)
        dv, qv = mud - mu0, e_q - mu0
        drift_cos = (dv * qv).sum(-1) / (dv.norm(dim=-1) * qv.norm(dim=-1) + eps)
        return torch.stack([(e_q * mu0).sum(-1), (e_q * mud).sum(-1), torch.where(gal_mask > 0, cos, torch.full_like(cos, -9)).max(1).values, cm,
                            torch.where(gal_mask > 0, cos, torch.full_like(cos, 9)).min(1).values, std, drift_cos, dv.norm(dim=-1)], -1)

    # layer 4
    def owner_logit(self, v, k, dt_last_h) -> torch.Tensor:
        z = torch.cat([v, torch.log1p(k)[:, None], torch.log1p(dt_last_h.clamp_min(0))[:, None]], -1)
        return self.own2(F.relu(self.own1(z)))[..., 0]

    def human_logit(self, u, f_tab, h_ctx) -> torch.Tensor:
        return self.hum2(F.relu(self.hum1(torch.cat([u, f_tab, h_ctx[:, list(BURST_IDX)]], -1))))[..., 0]

    def forward(self, x, f_tab, h_ctx, gal_x=None, gal_dt_h=None, gal_mask=None):
        """Full pass for one batch of queries; gal_* (B,K,...) is the enrolment gallery (optional)."""
        e, u = self.encode(x)
        out = {"e": e, "u": u, "human_logit": self.human_logit(u, f_tab, h_ctx)}
        if gal_x is not None:
            B, K = gal_x.shape[:2]
            ge = self.encode(gal_x.flatten(0, 1))[0].view(B, K, -1)
            v = self.match(e, ge, gal_dt_h, gal_mask)
            out["owner_logit"] = self.owner_logit(v, gal_mask.sum(1), (gal_dt_h + (1 - gal_mask) * 1e9).min(1).values)
        return out
