"""
Fix My Money — realistic AI presenter, v2 (InfiniteTalk), 2026-11-25.

Why v2: the owner felt the OmniAvatar clip still "looks AI" and the mouth gives it away.
InfiniteTalk (MeiGen, Apache-2.0, built on Wan2.1-I2V-14B) is the open model with the best
lip-sync in recent comparisons, and it animates head, face and shoulders together with the
speech instead of mostly the mouth. We run it without speed-up LoRAs (40 steps, audio CFG 4,
text CFG 5, the authors' recommended settings) because those LoRAs cost identity and detail.

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

app = modal.App("fmm-avatar-infinitetalk")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1", "libgl1", "libglib2.0-0")
    .pip_install("torch==2.4.1", "torchvision==0.19.1", "torchaudio==2.4.1",
                 index_url="https://download.pytorch.org/whl/cu121")
    .pip_install("xformers==0.0.28.post1")  # PyPI build matches torch 2.4.1 / cu121
    .pip_install("ninja", "psutil", "packaging", "wheel", "misaki[en]", "librosa", "soundfile",
                 "huggingface_hub[cli]==0.30.2", "hf_transfer")
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
    print(f"weights downloaded in {time.time() - t:.0f}s", flush=True)
    return ckpt


@app.function(image=image, gpu="H100", timeout=45 * 60, memory=98304)
def render(image_bytes: bytes, audio_bytes: bytes, size: str = "infinitetalk-480",
           steps: int = 40, prompt: str = PROMPT) -> bytes:
    import glob
    import time
    # GPU-side import check before the ~6 min download (wan/xfuser need CUDA at import time)
    sh("cd /root/it && python -c 'import wan, xfuser; print(\"imports ok\")'")
    ckpt = download(size)
    os.makedirs("/tmp/in", exist_ok=True)
    os.makedirs("/tmp/out", exist_ok=True)
    Path("/tmp/in/presenter.png").write_bytes(image_bytes)
    Path("/tmp/in/voice.mp3").write_bytes(audio_bytes)
    sh("ffmpeg -y -loglevel error -i /tmp/in/voice.mp3 -ac 1 -ar 16000 /tmp/in/voice.wav")
    Path("/tmp/in/job.json").write_text(json.dumps({
        "prompt": prompt, "cond_video": "/tmp/in/presenter.png",
        "cond_audio": {"person1": "/tmp/in/voice.wav"}}))
    os.chdir("/root/it")
    t = time.time()
    sh(f"python generate_infinitetalk.py --ckpt_dir {ckpt} --wav2vec_dir {W}/chinese-wav2vec2-base "
       f"--infinitetalk_dir {W}/InfiniteTalk/single/infinitetalk.safetensors --input_json /tmp/in/job.json "
       f"--size {size} --sample_steps {steps} --mode streaming --motion_frame 9 "
       f"--sample_text_guide_scale 5 --sample_audio_guide_scale 4 --save_file /tmp/out/fmm")
    print(f"rendered in {time.time() - t:.0f}s", flush=True)
    vids = sorted(glob.glob("/tmp/out/fmm*.mp4"))
    return Path(vids[-1]).read_bytes()


@app.local_entrypoint()
def main(image: str, audio: str, out: str, size: str = "infinitetalk-480", steps: int = 40):
    data = render.remote(Path(image).read_bytes(), Path(audio).read_bytes(), size, steps)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(data)
    print(f"saved {out} ({len(data) / 1e6:.1f} MB)")
