#!/usr/bin/env bash
# Fix My Money — make a generated presenter clip read like real phone footage (free, runs on the
# GitHub runner with ffmpeg). 2026-11-25.
#   polish_video.sh <in.mp4> <out.mp4>
# What it does, and why:
#   * upscale to 1080x1920 with lanczos + light unsharp  -> no soft, "plastic" low-res look
#   * very slow, tiny handheld drift (a few px)          -> a perfectly locked frame reads as synthetic
#   * fine temporal grain + mild contrast/saturation     -> real sensors have noise; AI frames are too clean
#   * 30 fps, H.264 high quality, AAC audio kept as is
set -euo pipefail
in="$1"; out="$2"
ffmpeg -y -loglevel error -i "$in" -filter_complex "
[0:v]fps=30,
scale=1160:2062:force_original_aspect_ratio=increase:flags=lanczos,
crop=1080:1920:x='(iw-1080)/2+7*sin(t*0.55)+3*sin(t*1.7)':y='(ih-1920)/2+6*sin(t*0.43+1.3)+2*sin(t*1.3)',
unsharp=5:5:0.45:5:5:0.0,
eq=contrast=1.03:saturation=0.94:gamma=1.01,
noise=c0s=5:c0f=t+u:c1s=2:c1f=t+u:c2s=2:c2f=t+u,
format=yuv420p[v]" -map "[v]" -map 0:a? -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 192k -movflags +faststart "$out"
