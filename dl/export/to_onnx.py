"""Optional ONNX export of the two stateless sub-graphs (encoder, human head) + onnxruntime parity check.
The Vercel runtime uses the NumPy bundle (to_numpy.py); ONNX is for other deployments."""

from pathlib import Path

import numpy as np
import torch


class _Encoder(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, x):
        return self.m.encode(x)


def export(model, out_dir: str | Path, table, tol: float = 1e-5) -> dict:
    import onnxruntime as ort

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    model.eval()
    x = torch.from_numpy(table.x[:4])
    path = out / "encoder.onnx"
    torch.onnx.export(_Encoder(model), (x,), str(path), input_names=["x_seq"], output_names=["e", "u"],
                      dynamic_axes={"x_seq": {0: "batch"}, "e": {0: "batch"}, "u": {0: "batch"}}, dynamo=True)  # the legacy tracer gave wrong outputs (err 0.2)
    sess = ort.InferenceSession(str(path))
    xb = table.x[:16]
    e_o, u_o = sess.run(None, {"x_seq": xb})
    with torch.no_grad():
        e_t, u_t = model.encode(torch.from_numpy(xb))
    err = float(max(np.abs(e_o - e_t.numpy()).max(), np.abs(u_o - u_t.numpy()).max()))
    return {"path": str(path), "max_abs_err": err, "ok": err <= tol}
