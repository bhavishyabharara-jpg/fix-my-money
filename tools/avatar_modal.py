"""
Fix My Money — realistic AI presenter on Modal (free monthly credit), 2026-11-22.

Runs the open-source OmniAvatar-14B pipeline exactly as the public Hugging Face demo
(alexnasa/OmniAvatar, which the owner approved) does, but on our own Modal GPU so there is
no 5-second cap and no queue. Called from GitHub Actions (.github/workflows/avatar.yml).

    modal run tools/avatar_modal.py --image <png> --audio <mp3> --out <mp4> [--steps 4]

Cost guards (owner rule: never a rupee on the card):
  * Modal workspace: spend limit $0 and usage limit $29 (< the $30/month free credit), so Modal stops
    every job before any charge is possible.
  * No persistent Volume: Modal bills Volume storage even after the spend limit stops workloads, so the
    weights are downloaded into the run's own temporary disk and disappear when the run ends.
  * One GPU function, hard timeout of 25 minutes.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import modal

SPACE = "https://huggingface.co/spaces/alexnasa/OmniAvatar"
MODELS = "/models"
PROMPT = ("A realistic video of a friendly Indian man explaining money to the camera, speaking and "
          "moving his head and eyes naturally, sometimes looking at the camera, subtle hand movement, "
          "steady camera, bright home office.")

app = modal.App("fmm-avatar")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1")
    .pip_install("torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0")
    .run_commands(
        f"git clone --depth 1 {SPACE} /root/space",
        # the Space's own requirements, minus the CUDA-only extras that we install separately
        "grep -v -E '^(torchvision|torchaudio|onnxruntime-gpu|ffmpeg|#)' /root/space/requirements.txt > /tmp/req.txt",
        "pip install -r /tmp/req.txt",
        "pip install spaces soundfile gradio==5.36.2 huggingface_hub hf_transfer",
        # prebuilt flash-attn for torch 2.8 / cu12 / py3.11; if it is unavailable the pipeline uses torch attention
        "pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/"
        "flash_attn-2.8.3+cu12torch2.8cxx11abiTRUE-cp311-cp311-linux_x86_64.whl || true",
        # the Space pins numpy 1.26; newest pyarrow/datasets need numpy 2 -> numpy-1 compatible versions
        "pip install 'pyarrow<18' 'datasets<4'",
        # fail fast at (cheap, CPU) build time instead of after GPU minutes
        "python -c 'import numpy, pyarrow, datasets, f5_tts.api; print(numpy.__version__, pyarrow.__version__)'",
    )
    .env({"HF_HOME": f"{MODELS}/hf", "HF_HUB_ENABLE_HF_TRANSFER": "1", "PROCESSED_RESULTS": "/tmp/results"})
)


def _prep_dirs():
    os.makedirs(f"{MODELS}/pretrained_models", exist_ok=True)
    link = Path("/root/space/pretrained_models")
    if not link.exists():
        link.symlink_to(f"{MODELS}/pretrained_models")
    os.chdir("/root/space")


def download():
    """Fetch the weights into this container's temporary disk (no Volume = no storage bill)."""
    import time
    from huggingface_hub import hf_hub_download, snapshot_download
    t = time.time()
    _prep_dirs()
    snapshot_download(repo_id="Wan-AI/Wan2.1-T2V-14B", local_dir="./pretrained_models/Wan2.1-T2V-14B",
                      allow_patterns=["*.safetensors", "*.json", "*.pth", "google/*"])
    snapshot_download(repo_id="facebook/wav2vec2-base-960h", local_dir="./pretrained_models/wav2vec2-base-960h")
    snapshot_download(repo_id="OmniAvatar/OmniAvatar-14B", local_dir="./pretrained_models/OmniAvatar-14B")
    hf_hub_download("alexnasa/F5_checkpoint", "model_10000.pt")
    hf_hub_download("alexnasa/F5_checkpoint", "vocab.txt")
    print(f"weights downloaded in {time.time() - t:.0f}s", flush=True)


@app.function(image=image, gpu="H100", timeout=1500, memory=65536)
def render(image_bytes: bytes, audio_bytes: bytes, steps: int = 4, prompt: str = PROMPT) -> bytes:
    import sys
    import time
    download()
    sys.path.insert(0, "/root/space")
    # the Space runs `pip install ...` at import time; everything is already in the image
    real = subprocess.check_call
    subprocess.check_call = lambda cmd, *a, **k: 0 if "pip install" in str(cmd) else real(cmd, *a, **k)
    t0 = time.time()
    import app as space  # loads models (from the volume) onto the GPU; builds but does not launch the UI
    subprocess.check_call = real
    print(f"models loaded in {time.time() - t0:.0f}s")
    os.makedirs("/tmp/in", exist_ok=True)
    img, aud = "/tmp/in/presenter.png", "/tmp/in/voice.mp3"
    Path(img).write_bytes(image_bytes)
    Path(aud).write_bytes(audio_bytes)
    t1 = time.time()
    out = space.infer(img, aud, prompt, [[720, 400]], steps, "fmm")   # 9:16, no 5 s trim
    print(f"rendered in {time.time() - t1:.0f}s")
    return Path(out).read_bytes()


@app.local_entrypoint()
def main(image: str, audio: str, out: str, steps: int = 4, prompt: str = PROMPT):
    data = render.remote(Path(image).read_bytes(), Path(audio).read_bytes(), steps, prompt)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(data)
    print(f"saved {out} ({len(data) / 1e6:.1f} MB)")
