#!/usr/bin/env python3
"""
Fix My Money — realistic AI presenter on Kaggle's free GPUs (no card anywhere), 2026-11-23.

Runs in GitHub Actions. For one request it:
  1. writes a private Kaggle "script" kernel (GPU + internet on) that downloads the open-source
     OmniAvatar code and weights, fetches our presenter photo and Sarvam voice from the public
     repo, renders the talking-presenter video and saves it to /kaggle/working/avatar.mp4;
  2. pushes it with the Kaggle CLI, waits for it to finish, downloads the outputs.

    python tools/kaggle_avatar.py avatar/requests/<name>.json avatar/out/<name>.mp4

Request JSON: {"image": "<repo path>", "audio": "<repo path>", "model": "1.3B"|"14B", "steps": 25}
Needs env KAGGLE_USERNAME and KAGGLE_KEY (repo secrets). Never posts anything.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAW = "https://raw.githubusercontent.com/bhavishyabharara-jpg/fix-my-money/main/"
PROMPT = ("A realistic video of a friendly Indian man explaining money to the camera, speaking and moving "
          "his head and eyes naturally, subtle hand movement, steady camera, bright home office.")

KERNEL = r'''
import glob, os, shutil, subprocess, time, urllib.request
IMAGE_URL = "__IMAGE__"
AUDIO_URL = "__AUDIO__"
MODEL = "__MODEL__"          # "1.3B" or "14B"
STEPS = __STEPS__
PROMPT = "__PROMPT__"
OUT = "/kaggle/working"
t0 = time.time()

def sh(cmd, check=True):
    print("$", cmd, flush=True)
    r = subprocess.run(cmd, shell=True)
    if check and r.returncode:
        raise SystemExit(f"failed ({r.returncode}): {cmd}")
    return r.returncode

sh("nvidia-smi")
sh("git clone --depth 1 https://github.com/Omni-Avatar/OmniAvatar /tmp/OA")
os.chdir("/tmp/OA")
# use Kaggle's preinstalled torch; install everything else the repo needs
sh("grep -v -i -E '^(torch|torchvision|torchaudio|flash)' requirements.txt > /tmp/req.txt || true")
sh("pip install -q -r /tmp/req.txt", check=False)
sh("pip install -q 'huggingface_hub[cli]' hf_transfer librosa", check=False)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
base = "Wan-AI/Wan2.1-T2V-14B" if MODEL == "14B" else "Wan-AI/Wan2.1-T2V-1.3B"
sh(f"huggingface-cli download {base} --local-dir pretrained_models/{base.split('/')[1]}")
sh(f"huggingface-cli download OmniAvatar/OmniAvatar-{MODEL} --local-dir pretrained_models/OmniAvatar-{MODEL}")
sh("huggingface-cli download facebook/wav2vec2-base-960h --local-dir pretrained_models/wav2vec2-base-960h")
print(f"setup done in {time.time() - t0:.0f}s", flush=True)

os.makedirs("/tmp/in", exist_ok=True)
urllib.request.urlretrieve(IMAGE_URL, "/tmp/in/presenter.png")
urllib.request.urlretrieve(AUDIO_URL, "/tmp/in/voice.mp3")
sh("ffmpeg -y -loglevel error -i /tmp/in/voice.mp3 -ac 1 -ar 16000 /tmp/in/voice.wav")
open("/tmp/in/input.txt", "w").write(f"{PROMPT}@@/tmp/in/presenter.png@@/tmp/in/voice.wav\n")

cfg = "configs/inference.yaml" if MODEL == "14B" else "configs/inference_1.3B.yaml"
hp = f"num_steps={STEPS},guidance_scale=4.5,overlap_frame=13"
if MODEL == "14B":
    hp += ",num_persistent_param_in_dit=0"   # offload to fit a 16 GB T4 (slow, but time is free)
t1 = time.time()
# T4 has no native bf16: try fp16 first, then the config default
rc = sh(f"torchrun --standalone --nproc_per_node=1 scripts/inference.py --config {cfg} "
        f"--input_file /tmp/in/input.txt --hp={hp},dtype=fp16", check=False)
if rc:
    rc = sh(f"torchrun --standalone --nproc_per_node=1 scripts/inference.py --config {cfg} "
            f"--input_file /tmp/in/input.txt --hp={hp}", check=False)
print(f"inference exit {rc} in {time.time() - t1:.0f}s", flush=True)
vids = sorted(glob.glob("/tmp/OA/**/*.mp4", recursive=True), key=os.path.getmtime)
vids = [v for v in vids if "examples" not in v]
print("videos:", vids, flush=True)
if vids:
    shutil.copy(vids[-1], f"{OUT}/avatar.mp4")
print(f"total {time.time() - t0:.0f}s", flush=True)
'''


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    # the kaggle CLI imports `six` but does not always install it
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "six"], check=False)
    # newer Kaggle CLIs read the token from KAGGLE_API_TOKEN; the repo secret is KAGGLE_KEY
    if os.environ.get("KAGGLE_KEY") and not os.environ.get("KAGGLE_API_TOKEN"):
        os.environ["KAGGLE_API_TOKEN"] = os.environ["KAGGLE_KEY"]
    req_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    req = json.loads(req_path.read_text())
    user = os.environ["KAGGLE_USERNAME"]
    slug = "fmm-avatar"
    code = (KERNEL.replace("__IMAGE__", RAW + req["image"]).replace("__AUDIO__", RAW + req["audio"])
            .replace("__MODEL__", req.get("model", "1.3B")).replace("__STEPS__", str(int(req.get("steps", 25))))
            .replace("__PROMPT__", req.get("prompt", PROMPT).replace('"', "'")))
    work = Path(tempfile.mkdtemp())
    (work / "run.py").write_text(code)
    (work / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{user}/{slug}", "title": slug, "code_file": "run.py", "language": "python",
        "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
        "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": [],
    }))
    r = run(["kaggle", "kernels", "push", "-p", str(work)])
    print(r.stdout, r.stderr)
    if r.returncode:
        return 1
    t0 = time.time()
    status = ""
    while time.time() - t0 < 5.5 * 3600:
        time.sleep(60)
        s = run(["kaggle", "kernels", "status", f"{user}/{slug}"]).stdout.lower()
        status = s.strip()
        print(f"{(time.time() - t0) / 60:.0f} min: {status}", flush=True)
        if any(k in s for k in ("complete", "error", "cancel")):
            break
    dl = Path(tempfile.mkdtemp())
    r = run(["kaggle", "kernels", "output", f"{user}/{slug}", "-p", str(dl)])
    print(r.stdout[-500:], r.stderr[-500:])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for log in dl.glob("*.log"):
        shutil.copy(log, out_path.with_suffix(".kaggle.log"))
    vid = dl / "avatar.mp4"
    if vid.exists():
        shutil.copy(vid, out_path)
        print(f"saved {out_path} ({vid.stat().st_size / 1e6:.1f} MB) after {(time.time() - t0) / 60:.0f} min")
        return 0
    print("no video produced; see the .kaggle.log")
    return 1


if __name__ == "__main__":
    sys.exit(main())
