#!/usr/bin/env python3
"""
split_chapters.py

Splits a chapter-marked MKV (ripped from a DVD title via MakeMKV) into
individual chapter clips.

This exists because many disc-based digitization services (iMemories and
similar) deliver VHS/tape transfers as a DVD where each "chapter" is a
separate clip -- but with no embedded metadata about what's actually in
each one. This script gets you from "one DVD with N chapters" to "N
individual video files," so you can review, caption, and archive each
clip on its own.

Discs are identified by whatever ID you give them (a serial/barcode number
works well if your discs have one, since it's already unique and printed
on the disc).

Expected workflow:
  1. MakeMKV "Backup" of the disc, saved under your archive's disc-backups
     folder (see config.py), e.g. 01_Videos/01_Disc_Backups/<disc-id>.mkv
  2. MakeMKV rip of the movie/title (normal rip, not backup mode) -> a
     single .mkv file with the DVD's chapter markers preserved
  3. This script splits that .mkv into one file per chapter

Usage:
  python3 split_chapters.py --input "1234567-0000001.mkv" \
      --disc-id "1234567-0000001" --archive-root "/path/to/MyFamilyArchive"

Output (folder names come from config.py):
  <archive-root>/01_Videos/02_Chapter_Rips/1234567-0000001/1234567-0000001_Ch01.mp4
  <archive-root>/01_Videos/02_Chapter_Rips/1234567-0000001/1234567-0000001_Ch02.mp4
  ...

Notes:
  - Uses "-c copy" (no re-encoding) by default: fast and lossless, but cuts
    snap to the nearest keyframe, so you may get ~1-2 seconds of bleed from
    the previous chapter at the start of a clip.
  - Pass --reencode for frame-accurate cuts (much slower across many discs).
  - Safe to re-run: skips chapters whose output file already exists, unless
    --overwrite is passed.

Requires: ffmpeg and ffprobe on PATH.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from config import RIPS_SUBDIR


def get_chapters(input_path: Path):
    """Return a list of chapter dicts (start_time, end_time, ...) via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_chapters",
        str(input_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffprobe failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    chapters = data.get("chapters", [])
    if not chapters:
        print(
            "No chapters found in this file. Make sure this is the ripped "
            "TITLE (not the raw disc backup) -- rip the title normally in "
            "MakeMKV (not Backup mode) so chapter markers are preserved in "
            "a way ffprobe can read.",
            file=sys.stderr,
        )
        sys.exit(1)
    return chapters


def split_chapters(input_path: Path, disc_id: str, out_dir: Path,
                    reencode: bool, overwrite: bool):
    chapters = get_chapters(input_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(chapters)} chapters in {input_path.name}")

    for i, chapter in enumerate(chapters, start=1):
        start = chapter["start_time"]
        end = chapter["end_time"]
        out_name = f"{disc_id}_Ch{i:02d}.mp4"
        out_path = out_dir / out_name

        if out_path.exists() and not overwrite:
            print(f"  [skip] {out_name} already exists")
            continue

        cmd = ["ffmpeg", "-y", "-i", str(input_path), "-ss", start, "-to", end]
        if reencode:
            cmd += ["-c:v", "libx264", "-c:a", "aac", "-crf", "18"]
        else:
            cmd += ["-c", "copy"]
        cmd.append(str(out_path))

        print(f"  [rip ] {out_name}  ({start} -> {end})")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ffmpeg failed on chapter {i}: {result.stderr[-500:]}",
                  file=sys.stderr)

    print(f"\nDone. Chapters written to: {out_dir}")
    print("Next: watch each clip and log it in your media index/spreadsheet.")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", required=True, type=Path,
                         help="Path to the ripped MKV title (with chapter markers)")
    parser.add_argument("--disc-id", required=True,
                         help="Identifier for this disc, e.g. a serial/barcode "
                              "number (used in output filenames/folder)")
    parser.add_argument("--archive-root", required=True, type=Path,
                         help="Path to your archive root folder")
    parser.add_argument("--reencode", action="store_true",
                         help="Re-encode for frame-accurate cuts (slower, no keyframe bleed)")
    parser.add_argument("--overwrite", action="store_true",
                         help="Overwrite chapter files that already exist")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    out_dir = args.archive_root / RIPS_SUBDIR / args.disc_id
    split_chapters(args.input, args.disc_id, out_dir, args.reencode, args.overwrite)


if __name__ == "__main__":
    main()
