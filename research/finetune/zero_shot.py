import warnings; warnings.filterwarnings("ignore")
import torch, common
d = torch.device("mps")
S = common.load_sessions()
print(len(S), "sessions")
tr, va, te = common.split_users({e["user"] for e in S})
print("train/val/test people:", len(tr), len(va), len(te))
m = common.build_model(d)
for k, r in common.evaluate(m, S, te, d, ks=(2, 3, 4)).items(): print("zero-shot k=%d" % k, r)
