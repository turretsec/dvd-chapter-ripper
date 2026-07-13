"""
config.py

Folder layout used by split_chapters.py and process_all_discs.py, relative
to your archive root. Adjust these if your setup uses different folder
names. Nothing else in the scripts needs to change.
"""

from pathlib import Path

# Where full MakeMKV disc backups live, relative to the archive root
BACKUPS_SUBDIR = Path("01_Videos") / "01_Disc_Backups"

# Where split chapter clips get written, relative to the archive root
RIPS_SUBDIR = Path("01_Videos") / "02_Chapter_Rips"
