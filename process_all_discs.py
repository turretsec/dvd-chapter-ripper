#!/usr/bin/env python3
"""
process_all_discs.py

The "just run this" version of split_chapters.py. No command-line
arguments needed.

Scans your archive's disc-backups folder (see config.py) for MKV files,
and for each one that hasn't been split into chapters yet, splits it
automatically. Safe to run over and over. It only processes discs that
are new since the last run.

This script assumes it lives next to split_chapters.py and config.py, at:
  <archive-root>/_tools/dvd-chapter-splitter/process_all_discs.py

The archive root is auto-detected as two folders up from this file's
location, so nothing needs to be typed in. If you keep this repo
somewhere else, edit ARCHIVE_ROOT below to point at your archive folder
directly.

Typical workflow:
  1. MakeMKV -> back up a disc as <disc-id>.mkv into your backups folder
  2. Run this script (or double-click Run_Ripper.bat on Windows)
  3. It finds any new disc backups and splits them into chapters,
     skipping anything already done
  4. Watch the new clips and log them in your media index/spreadsheet
"""

import sys
from pathlib import Path

from config import BACKUPS_SUBDIR, RIPS_SUBDIR
from split_chapters import split_chapters as split_one_disc

SCRIPT_DIR = Path(__file__).resolve().parent
ARCHIVE_ROOT = SCRIPT_DIR.parent.parent  # .../_tools/dvd-chapter-splitter -> _tools -> archive root
BACKUPS_DIR = ARCHIVE_ROOT / BACKUPS_SUBDIR
RIPS_DIR = ARCHIVE_ROOT / RIPS_SUBDIR


def already_processed(disc_id: str) -> bool:
    out_dir = RIPS_DIR / disc_id
    return out_dir.exists() and any(out_dir.glob(f"{disc_id}_Ch*.mp4"))


def main():
    if not BACKUPS_DIR.exists():
        print(f"Can't find backups folder: {BACKUPS_DIR}")
        print("Check ARCHIVE_ROOT / config.py match your actual folder layout.")
        input("Press Enter to close...")
        sys.exit(1)

    mkv_files = sorted(BACKUPS_DIR.glob("*.mkv"))
    if not mkv_files:
        print(f"No .mkv files found in {BACKUPS_DIR}")
        input("Press Enter to close...")
        return

    print(f"Archive root: {ARCHIVE_ROOT}")
    print(f"Found {len(mkv_files)} disc backup(s) in {BACKUPS_DIR}\n")

    new_count = 0
    skip_count = 0

    for mkv_path in mkv_files:
        disc_id = mkv_path.stem  # filename without .mkv, e.g. 1234567-0000001

        if already_processed(disc_id):
            print(f"[already done] {disc_id}")
            skip_count += 1
            continue

        print(f"[processing]   {disc_id}")
        out_dir = RIPS_DIR / disc_id
        try:
            split_one_disc(mkv_path, disc_id, out_dir, reencode=False, overwrite=False)
        except SystemExit:
            # split_chapters() exits early if e.g. no chapters were found in
            # this file - catch that here so one bad disc doesn't stop the
            # whole batch from running.
            print(f"  -> skipped {disc_id}, see message above")
            continue
        new_count += 1

    print(f"\nDone. Processed {new_count} new disc(s), skipped {skip_count} already-done disc(s).")
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
