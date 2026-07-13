# dvd-chapter-splitter

Splits chapter-marked DVD rips (MKV) into individual video files, one per
chapter.

This small project was created because I needed to rip about 100 *iMemories* DVDs. So, it's geared towards the workflow I used.

## How it works

1. [**MakeMKV**](https://www.makemkv.com/) rips the DVD title (not Backup
mode! A normal title rip preserves the chapter markers in a way
`ffprobe` can read).
2. `split_chapters.py` reads those chapter markers with `ffprobe` and cuts
the file into one `.mp4` per chapter with `ffmpeg`.
3. `process_all_discs.py` is a no-arguments wrapper that scans a folder of
disc backups and processes anything new, skipping discs already split. This is
 for if you're working through a big stack of old discs over time.

## Requirements

* Python 3.9+
* [`ffmpeg`/`ffprobe`](https://ffmpeg.org/) on your PATH
* [MakeMKV](https://www.makemkv.com/) for the initial disc rip
    * Not run by this tool. You rip the disk by yourself. These scripts are for post-processing/workflow.

No external Python packages are required (see `requirements.txt`).

## Folder layout

This tool expects (and `process_all_discs.py` will create) a layout like:

```
MyArchive/
├── 01_Videos/
│   ├── 01_Disc_Backups/       <- put your ripped .mkv files here
│   │   └── <disc-id>.mkv
│   └── 02_Chapter_Rips/       <- split chapters land here
│       └── <disc-id>/
│           ├── <disc-id>_Ch01.mp4
│           └── <disc-id>_Ch02.mp4
└── _tools/
    └── dvd-chapter-splitter/  <- this repo, cloned/copied in here
```

Folder names are configurable in `config.py` if your layout differs.

`<disc-id>` can be anything you like - a sequential label (`DVD01`), or
(recommended, if your discs have one) the barcode/serial number already
printed on the disc, so there's no separate numbering scheme to keep in
sync with the physical stack.

## Setup (Windows, from scratch)

### 1. Install Python
1. Open the **Microsoft Store**, search for **"Python install manager"**, and install it (or run `winget install 9NQ7512CXL7T` in a terminal).
2. Open a new Command Prompt and install the latest Python 3:
```
   py install 3.13
```
3. Verify it worked:
```
   py --version
```

### 2. Install ffmpeg (required by the script)
```
winget install ffmpeg
```
Close and reopen Command Prompt, then verify:
```
ffmpeg -version
ffprobe -version
```

### 3. Install MakeMKV (for ripping the discs themselves)
> This is separate from the script and is what actually reads the DVD and produces the `.mkv` file.
Download and install from https://www.makemkv.com/download/

### 4. Get the repo onto the archive drive
Unzip or clone it into a `_tools` folder inside your archive, e.g.:
```
C:\MyArchive\_tools\dvd-chapter-splitter\
```
so that `split_chapters.py`, `config.py`, etc. all end up in that folder.

### 5. Set up the virtual environment
```
cd C:\MyArchive\_tools\dvd-chapter-splitter
py -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
```
No packages need installing beyond that. The project is stdlib-only (see `requirements.txt`).

### 6. Test it
```
.venv\Scripts\python.exe process_all_discs.py
```
With no discs backed up yet, it should print "No .mkv files found" (or that it can't find the archive folder if you haven't created it or configured `config.json`) and exit cleanly. That confirms Python, the venv, and folder detection are all working.

### 7. Day-to-day use
1. Rip a disc with MakeMKV -> save the `.mkv` as `<disc-id>.mkv` into `01_Videos\01_Disc_Backups\`
2. Double-click `Run_Ripper.bat`
3. Watch the new clips and log them in your media index

Only steps 1-5 are one-time setup -- after that it's rip -> double-click -> review, repeated per disc.

## Usage

### One disc at a time

```bash
python3 split_chapters.py \\
  --input "/path/to/1234567-0000001.mkv" \\
  --disc-id "1234567-0000001" \\
  --archive-root "/path/to/MyArchive"
```

Options:

* `--reencode` - re-encode for frame-accurate cuts instead of the default
fast `-c copy` (which can bleed \~1-2 seconds from the previous chapter,
since cuts snap to the nearest keyframe)
* `--overwrite` - overwrite chapter files that already exist

### Batch mode (recommended)

Drop this repo into `<archive-root>/_tools/dvd-chapter-splitter/`, set up a
virtual environment there (`python -m venv .venv`), then either:

```bash
python3 process\_all\_discs.py
```

or, on Windows, just double-click `Run\_Ripper.bat`.

It scans `01_Disc_Backups/` for any `.mkv` file, splits anything it hasn't
already processed, and tells you what it did. Re-run it any time after
backing up more discs. Already processed discs are skipped automatically.

## Notes

* This tool doesn't touch your original discs, and doesn't decrypt or rip
discs itself; that's MakeMKV's job. It only operates on the `.mkv` file
MakeMKV produces.
* Keep your MakeMKV disc backups around even after splitting. They're
your fallback if a chapter needs to be re-cut differently later.

## License

MIT - see [LICENSE](LICENSE).
