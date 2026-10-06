"""
Fix My Money — reel audio: a calm music bed, and optional AI narration.

Music: a soft electric-piano-and-pad bed, 72 bpm, with no drums. Chords are crossfaded
so nothing re-attacks on a scene change. It sits well under the voice and dips further
(ducks) whenever someone is speaking.

Narration: Kokoro-82M (Apache-2.0 weights, runs on CPU) through kokoro-onnx. Each scene
can carry a `vo` line; the reel's scene timing stretches to fit the spoken line, so text
on screen and voice stay together.

Setup (once per machine/run):  python3 engine/audio.py --setup
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import wave

import numpy as np

SR = 24000                     # Kokoro's native rate; ffmpeg upsamples to 44.1k AAC
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("FMM_TTS_DIR", os.path.join(HERE, "tts"))
MODEL = os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx")
VOICES = os.path.join(MODEL_DIR, "voices-v1.0.bin")
RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

DEFAULT_VOICE = "af_heart"
DEFAULT_SPEED = 1.05


# ------------------------------------------------------------------ setup
def setup() -> None:
    """Install the TTS runtime and fetch the model (~120 MB) if missing."""
    try:
        import kokoro_onnx  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "kokoro-onnx", "soundfile",
                        "--break-system-packages"], check=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    for path in (MODEL, VOICES):
        if not os.path.exists(path):
            subprocess.run(["curl", "-sSL", "-o", path, f"{RELEASE}/{os.path.basename(path)}"], check=True)
    print("tts ready:", MODEL_DIR)


# ------------------------------------------------------------------ narration
_K = None


def _kokoro():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        _K = Kokoro(MODEL, VOICES)
    return _K


def _sarvam(text: str, speaker: str, pace: float, language: str) -> tuple[np.ndarray, int]:
    """Sarvam Bulbul v3: natural Indian voices, Hindi-English code-mixing. Key from env only."""
    import base64, io, json as _json, urllib.request
    body = _json.dumps({"text": text, "target_language_code": language, "speaker": speaker,
                        "model": "bulbul:v3", "pace": pace, "speech_sample_rate": SR,
                        "output_audio_codec": "wav"}).encode()
    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", data=body, method="POST",
                                 headers={"api-subscription-key": os.environ["SARVAM_API_KEY"].strip(),
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        wav_bytes = base64.b64decode(_json.loads(resp.read())["audios"][0])
    with wave.open(io.BytesIO(wav_bytes)) as w:
        sr = w.getframerate()
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        if w.getnchannels() == 2:
            raw = raw.reshape(-1, 2).mean(axis=1)
    return raw.astype(np.float32) / 32768.0, sr


def speak(text: str, voice: str = DEFAULT_VOICE, speed: float = DEFAULT_SPEED,
          language: str = "hi-IN") -> np.ndarray:
    """Narrate one line. Returns mono float32 at SR.

    voice "sarvam:<speaker>" uses Sarvam (needs SARVAM_API_KEY in the environment);
    anything else is a local Kokoro voice.
    """
    if voice.startswith("sarvam:"):
        samples, sr = _sarvam(text, voice.split(":", 1)[1], speed, language)
    else:
        lang = "hi" if voice[:2] in ("hf", "hm") and not text.isascii() else (
            "en-gb" if voice.startswith("b") else "en-us")
        samples, sr = _kokoro().create(spoken(text) if text.isascii() else text, voice=voice, speed=speed, lang=lang)
    samples = np.asarray(samples, dtype=np.float32)
    if sr != SR:  # never expected, but keep timing honest if it happens
        idx = np.linspace(0, len(samples) - 1, int(len(samples) * SR / sr))
        samples = np.interp(idx, np.arange(len(samples)), samples).astype(np.float32)
    # trim leading/trailing silence so scenes don't open with dead air
    loud = np.where(np.abs(samples) > 0.01)[0]
    if len(loud):
        samples = samples[max(0, loud[0] - int(0.03 * SR)): loud[-1] + int(0.08 * SR)]
    return samples


def spoken(text: str) -> str:
    """Make on-screen shorthand pronounceable."""
    rep = {"₹": "rupees ", "%": " percent", "×": " times", "~": "about ", "&": " and ",
           "SIP": "S.I.P.", "EMI": "E.M.I.", "PPF": "P.P.F.", "NSC": "N.S.C.", "RBI": "R.B.I.",
           "NPS": "N.P.S.", "UPI": "U.P.I.", "cr ": "crore ", "L ": "lakh "}
    for a, b in rep.items():
        text = text.replace(a, b)
    return " ".join(text.replace("**", "").replace("[[", "").replace("]]", "").split())


# ------------------------------------------------------------------ music bed
# Am9 – Fmaj7 – C(add9) – G6, voiced low and close. Frequencies in Hz.
CHORDS = [
    [110.00, 164.81, 196.00, 246.94, 261.63],
    [87.31, 130.81, 174.61, 220.00, 329.63],
    [130.81, 196.00, 246.94, 293.66, 329.63],
    [98.00, 146.83, 196.00, 246.94, 329.63],
]
BPM = 72


def _lowpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, len(x), 4096):  # chunked so it stays fast without scipy
        seg = x[i:i + 4096]
        out = np.empty_like(seg)
        for j, v in enumerate(seg):
            acc = (1 - a) * v + a * acc
            out[j] = acc
        y[i:i + 4096] = out
    return y


def music(seconds: float) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n) / SR
    bar = 4 * 60 / BPM                     # one chord per bar (~3.33 s)
    pad = np.zeros(n)
    xf = 1.4                               # crossfade between chords
    for ci in range(int(math.ceil(seconds / bar)) + 1):
        a = int(max(0, (ci * bar - xf / 2)) * SR)
        b = min(n, int((ci * bar + bar + xf / 2) * SR))
        if a >= n:
            break
        tt = t[a:b] - ci * bar + xf / 2
        span = bar + xf
        env = np.clip(tt / xf, 0, 1) * np.clip((span - tt) / xf, 0, 1)
        env = np.sin(env * math.pi / 2) ** 2           # equal-power, no clicks
        for f in CHORDS[ci % 4]:
            for det in (-0.12, 0.12):                  # gentle chorus, not wobble
                ph = 2 * np.pi * (f + det) * tt
                pad[a:b] += env * (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph))
    pad = _lowpass(pad, 900.0)

    # soft electric-piano arpeggio: one note per beat, quiet, fast decay
    keys = np.zeros(n)
    beat = 60 / BPM
    for k in range(int(seconds / beat)):
        chord = CHORDS[int(k * beat // bar) % 4]
        f = chord[[2, 3, 4, 3][k % 4]] * 2
        s0 = int(k * beat * SR)
        s1 = min(n, s0 + int(1.6 * SR))
        tt = t[s0:s1] - k * beat
        env = np.minimum(1, tt / 0.012) * np.exp(-tt * 2.6)
        keys[s0:s1] += env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 6))
    keys = _lowpass(keys, 2200.0)

    mix = pad / (np.max(np.abs(pad)) + 1e-9) * 0.55 + keys / (np.max(np.abs(keys)) + 1e-9) * 0.30
    fade = np.clip(np.minimum(t / 1.2, (seconds - t) / 1.8), 0, 1)
    return (mix * fade).astype(np.float32)


# ------------------------------------------------------------------ mix + write
def _db(x):
    return 10 ** (x / 20)


def mix(seconds: float, voice_track: np.ndarray | None) -> np.ndarray:
    """Music alone sits at about -22 dBFS; under speech it ducks to about -34 dBFS."""
    bed = music(seconds)
    bed = bed / (np.sqrt(np.mean(bed ** 2)) + 1e-9) * _db(-22)
    if voice_track is None:
        out = bed
    else:
        v = np.zeros(len(bed), dtype=np.float32)
        v[: min(len(v), len(voice_track))] = voice_track[: len(v)]
        # envelope follower on the voice -> smooth gain for the music
        win = int(0.25 * SR)
        energy = np.convolve(np.abs(v), np.ones(win) / win, mode="same")
        speaking = np.clip(energy / 0.02, 0, 1)
        gain = 1 - (1 - _db(-12)) * speaking
        rms = np.sqrt(np.mean(v[v != 0] ** 2)) if np.any(v) else 1
        v = v / (rms + 1e-9) * _db(-16)
        out = bed * gain + v
    peak = np.max(np.abs(out))
    if peak > 0.95:
        out = out / peak * 0.95
    return out


def write_wav(path: str, x: np.ndarray) -> None:
    data = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup()
    elif "--music-demo" in sys.argv:
        write_wav(sys.argv[-1], mix(16.0, None))
