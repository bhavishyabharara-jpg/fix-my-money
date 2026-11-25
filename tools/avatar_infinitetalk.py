"""
Fix My Money — realistic AI presenter, v2 (InfiniteTalk), 2026-11-25.

Why v2: the owner felt the OmniAvatar clip still "looks AI" and the mouth gives it away.
InfiniteTalk (MeiGen, Apache-2.0, built on Wan2.1-I2V-14B) is the open model with the best
lip-sync in recent comparisons, and it animates head, face and shoulders together with the
speech instead of mostly the mouth. Default is the lightx2v speed-up LoRA (6 steps, one guidance pass):
the full 40-step setting needs ~1 GPU-hour (~$4) per 13 s clip, too much for the free $30/month.

    modal run tools/avatar_infinitetalk.py --image <png> --audio <mp3> --out <mp4> [--size infinitetalk-480]

Cost guards (owner rule: never a rupee on the card):
  * Modal workspace: spend limit $0 and usage limit $29 (< the $30/month free credit).
  * No persistent Volume (storage is billed even after the spend limit) — weights are downloaded
    into the run's temporary disk and vanish with it.
  * One GPU function with a hard 45-minute timeout.
  * A build-time import check, so dependency problems fail on cheap CPU, not on the GPU.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import modal

REPO = "https://github.com/MeiGen-AI/InfiniteTalk"
W = "/weights"
PROMPT = ("A real, candid smartphone video of an Indian man in his early thirties talking to the camera "
          "about money in his living room. He speaks calmly and naturally like a friend explaining "
          "something, with small natural head movements, normal blinking, relaxed face, only a slight "
          "smile at times, subtle hand gestures near the bottom of the frame. Natural window daylight, "
          "realistic skin texture, steady phone camera, medium close-up.")

LORA = "Wan21_T2V_14B_lightx2v_cfg_step_distill_lora_rank32.safetensors"

app = modal.App("fmm-avatar-infinitetalk")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1", "libgl1", "libglib2.0-0")
    .pip_install("torch==2.4.1", "torchvision==0.19.1", "torchaudio==2.4.1",
                 index_url="https://download.pytorch.org/whl/cu121")
    .pip_install("xformers==0.0.28.post1")  # PyPI build matches torch 2.4.1 / cu121
    .pip_install("ninja", "psutil", "packaging", "wheel", "misaki[en]", "librosa", "soundfile",
                 "huggingface_hub[cli]==0.30.2", "hf_transfer", "hf_xet")
    .add_local_file(str(Path(__file__).parent / "infinitetalk_constraints.txt"), "/root/constraints.txt", copy=True)
    .run_commands(
        # prebuilt flash-attn for torch 2.4 / cu12 / py3.11 (no compile)
        "pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/"
        "flash_attn-2.7.4.post1+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl",
        f"git clone --depth 1 {REPO} /root/it",
        # unused import that no longer exists on Python 3.11+ (Modal's minimum)
        "sed -i 's/^from inspect import ArgSpec$/# &/' /root/it/wan/multitalk.py",
        # InfiniteTalk's requirements are unpinned and 2026 releases need torch>=2.6. Install with the
        # exact package set verified to import cleanly (tools/infinitetalk_constraints.txt), no gradio UI.
        "grep -v -i '^gradio' /root/it/requirements.txt > /tmp/req.txt",
        "pip install -r /tmp/req.txt -c /root/constraints.txt --extra-index-url https://download.pytorch.org/whl/cu121",
        # keep the CUDA wheels above (requirements may try to move torch)
        "pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 "
        "--index-url https://download.pytorch.org/whl/cu121",
        # fail fast at (cheap, CPU) build time
        "cd /root/it && python -c 'import torch, xformers, flash_attn, librosa, transformers, diffusers, decord; "
        "print(torch.__version__, transformers.__version__, diffusers.__version__)'",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": f"{W}/hf"})
)


def sh(cmd: str) -> None:
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


def download(size: str) -> str:
    import time
    from huggingface_hub import hf_hub_download, snapshot_download
    t = time.time()
    base = "Wan-AI/Wan2.1-I2V-14B-720P" if size.endswith("720") else "Wan-AI/Wan2.1-I2V-14B-480P"
    ckpt = f"{W}/{base.split('/')[1]}"
    snapshot_download(base, local_dir=ckpt, allow_patterns=["*.safetensors", "*.json", "*.pth", "google/*", "xlm-roberta-large/*"])
    snapshot_download("TencentGameMate/chinese-wav2vec2-base", local_dir=f"{W}/chinese-wav2vec2-base")
    hf_hub_download("TencentGameMate/chinese-wav2vec2-base", "model.safetensors", revision="refs/pr/1",
                    local_dir=f"{W}/chinese-wav2vec2-base")
    hf_hub_download("MeiGen-AI/InfiniteTalk", "single/infinitetalk.safetensors", local_dir=f"{W}/InfiniteTalk")
    # lightx2v step-distill LoRA (the speed-up InfiniteTalk's README recommends): 4-8 steps, 1 guidance pass
    hf_hub_download("Kijai/WanVideo_comfy", LORA, local_dir=f"{W}/lora")
    print(f"weights downloaded in {time.time() - t:.0f}s", flush=True)
    return ckpt


def _infer(tag: str, image_bytes: bytes, audio_bytes: bytes, ckpt: str, size: str, fast: bool, steps: int,
           prompt: str) -> bytes:
    import glob
    import time
    d = f"/tmp/in/{tag}"
    os.makedirs(d, exist_ok=True)
    os.makedirs("/tmp/out", exist_ok=True)
    Path(f"{d}/presenter.png").write_bytes(image_bytes)
    Path(f"{d}/voice.in").write_bytes(audio_bytes)
    sh(f"ffmpeg -y -loglevel error -i {d}/voice.in -ac 1 -ar 16000 {d}/voice.wav")
    Path(f"{d}/job.json").write_text(json.dumps({
        "prompt": prompt, "cond_video": f"{d}/presenter.png", "cond_audio": {"person1": f"{d}/voice.wav"}}))
    os.chdir("/root/it")
    if fast:
        tune = (f"--lora_dir {W}/lora/{LORA} --lora_scale 1.0 --sample_steps {steps or 6} --sample_shift 2 "
                f"--sample_text_guide_scale 1.0 --sample_audio_guide_scale 2.0")
    else:
        tune = f"--sample_steps {steps or 40} --sample_text_guide_scale 5 --sample_audio_guide_scale 4"
    t = time.time()
    # the whole model fits in the H100's 80 GB: no CPU offload between steps; hard 20-min cap per clip
    sh(f"timeout 1200 python generate_infinitetalk.py --ckpt_dir {ckpt} --wav2vec_dir {W}/chinese-wav2vec2-base "
       f"--infinitetalk_dir {W}/InfiniteTalk/single/infinitetalk.safetensors --input_json {d}/job.json "
       f"--size {size} --mode streaming --motion_frame 9 --offload_model False {tune} --save_file /tmp/out/{tag}")
    print(f"{tag}: rendered in {time.time() - t:.0f}s", flush=True)
    return Path(sorted(glob.glob(f"/tmp/out/{tag}*.mp4"))[-1]).read_bytes()


def _prepare(size: str) -> str:
    # GPU-side import check before the download (wan/xfuser need CUDA at import time)
    sh("cd /root/it && python -c 'import wan, xfuser; print(\"imports ok\")'")
    # a stalled download once burned 35 GPU-minutes: hard cap it (normal: ~4-7 min)
    import signal

    def _stuck(*_):
        raise TimeoutError("model download took over 12 minutes - stopping to save credit")
    signal.signal(signal.SIGALRM, _stuck)
    signal.alarm(12 * 60)
    ckpt = download(size)
    signal.alarm(0)
    return ckpt


@app.function(image=image, gpu="H100", timeout=45 * 60, memory=98304)
def render(image_bytes: bytes, audio_bytes: bytes, size: str = "infinitetalk-480",
           fast: bool = True, steps: int = 0, prompt: str = PROMPT) -> bytes:
    """One clip. fast=True: lightx2v LoRA, 6 steps, one guidance pass (~$1.6 for 13 s incl. download).
    fast=False: full 40-step, text+audio CFG (~$4 for 13 s on an H100 - too costly for daily use)."""
    return _infer("fmm", image_bytes, audio_bytes, _prepare(size), size, fast, steps, prompt)


@app.function(image=image, gpu="H100", timeout=80 * 60, memory=98304)
def render_many(jobs: list, size: str = "infinitetalk-480", fast: bool = True, steps: int = 0,
                prompt: str = PROMPT) -> list:
    """Several clips for one model download (the daily reels, batched). Returns bytes or None per job."""
    ckpt = _prepare(size)
    out = []
    for i, (image_bytes, audio_bytes) in enumerate(jobs):
        try:
            out.append(_infer(f"job{i}", image_bytes, audio_bytes, ckpt, size, fast, steps, prompt))
        except Exception as exc:  # one bad clip must not cost the others
            print(f"job{i}: FAILED {type(exc).__name__}: {exc}", flush=True)
            out.append(None)
    return out


@app.local_entrypoint()
def main(image: str = "", audio: str = "", out: str = "", size: str = "infinitetalk-480", fast: bool = True,
         steps: int = 0, manifest: str = ""):
    if manifest:  # [{"image": ..., "audio": ..., "out": ...}, ...]
        items = json.loads(Path(manifest).read_text())
        res = render_many.remote([(Path(it["image"]).read_bytes(), Path(it["audio"]).read_bytes()) for it in items],
                                 size, fast, steps)
        for it, data in zip(items, res):
            if data:
                Path(it["out"]).parent.mkdir(parents=True, exist_ok=True)
                Path(it["out"]).write_bytes(data)
                print(f"saved {it['out']} ({len(data) / 1e6:.1f} MB)")
            else:
                print(f"no clip for {it['out']}")
        return
    data = render.remote(Path(image).read_bytes(), Path(audio).read_bytes(), size, fast, steps)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(data)
    print(f"saved {out} ({len(data) / 1e6:.1f} MB)")
