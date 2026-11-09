#!/usr/bin/env python3
"""Construit une vidéo de pitch/soutenance à partir d’un PPTX et d’une narration."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def ffprobe_duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", str(path)]).stdout.strip()
    return float(out)


def probe_video(path: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=codec_name,width,height,duration",
               "-show_entries", "format=duration", "-of", "json", str(path)]).stdout
    return json.loads(out)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    return [p.strip() for p in parts if p.strip()]


def srt_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_srt(narration: str, slides: list[Path], total: float, out: Path) -> None:
    sentences = split_sentences(narration)
    if not sentences:
        out.write_text("", encoding="utf-8")
        return
    per = total / len(slides)
    lines = []
    idx = 1
    for si in range(len(slides)):
        chunk = sentences[si::len(slides)] or [sentences[min(si, len(sentences) - 1)]]
        start = si * per
        step = per / max(1, len(chunk))
        for j, text in enumerate(chunk):
            a = start + j * step
            b = a + step * 0.92
            lines += [str(idx), f"{srt_timestamp(a)} --> {srt_timestamp(b)}", text, ""]
            idx += 1
    out.write_text("\n".join(lines), encoding="utf-8")


def build(deck: Path, narration_path: Path, out: Path, audio: Path | None = None,
          full: bool = False, burn: bool = False) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="greenit-video-"))
    try:
        pdf = deck.with_suffix(".pdf")
        if not pdf.exists():
            run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(deck.parent), str(deck)])
        prefix = tmp / "slide"
        run(["pdftoppm", "-png", "-r", "150", str(pdf), str(prefix)])
        slides = sorted(tmp.glob("slide-*.png"))
        if not slides:
            raise RuntimeError("Aucune image de slide générée")
        narration = narration_path.read_text(encoding="utf-8")
        if audio:
            total = ffprobe_duration(audio)
        else:
            total = max(60.0, min(90.0, len(slides) * 5.0))
        per = total / len(slides)
        concat = tmp / "concat.txt"
        with concat.open("w", encoding="utf-8") as f:
            for slide in slides:
                f.write(f"file '{slide.as_posix()}'\n")
                f.write(f"duration {per:.3f}\n")
            f.write(f"file '{slides[-1].as_posix()}'\n")
        video_only = tmp / "video.mp4"
        vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
               "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "23",
               "-r", "30", "-pix_fmt", "yuv420p", "-t", f"{total:.3f}", str(video_only)]
        run(cmd)
        srt = out.with_suffix(".srt")
        make_srt(narration, slides, total, srt)
        final = tmp / "final.mp4"
        if audio:
            cmd = ["ffmpeg", "-y", "-i", str(video_only), "-i", str(audio),
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(final)]
        else:
            cmd = ["ffmpeg", "-y", "-i", str(video_only), "-c:v", "copy", "-an", str(final)]
        run(cmd)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(final, out)
        info = probe_video(out)
        dur = float(info.get("format", {}).get("duration", 0))
        stream = (info.get("streams") or [{}])[0]
        report = {"video": str(out), "duration_s": round(dur, 2), "width": stream.get("width"),
                  "height": stream.get("height"), "codec": stream.get("codec_name"),
                  "slides": len(slides), "srt": str(srt), "audio": bool(audio)}
        out.with_name("video-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not (60 <= dur <= 90):
            print(f"AVERTISSEMENT : durée {dur:.1f}s hors plage 60–90s", file=sys.stderr)
        return report
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", type=Path, required=True)
    ap.add_argument("--narration", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--burn-subtitles", action="store_true")
    args = ap.parse_args()
    r = build(args.deck, args.narration, args.out, args.audio, args.full, args.burn_subtitles)
    print(f"OK vidéo {r['video']} ({r['duration_s']}s, {r['width']}x{r['height']}, {r['codec']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
