# Digital Image Forensics

A Python command-line utility for examining JPEG images with several traditional
digital image forensics techniques. It prints image metadata or displays
side-by-side visual analysis results to help an investigator identify areas
that may warrant closer inspection.

> **Important:** These techniques are indicators, not proof that an image is
> authentic or manipulated. Results can be affected by image content,
> compression, resizing, and other processing. Interpret them alongside other
> evidence.

## Features

The program is implemented in [`foreimg.py`](./foreimg.py) and supports:

| Technique | CLI option | What it reports |
| --- | --- | --- |
| EXIF metadata inspection | `-e`, `--exif` (also the default) | Prints available EXIF tags and checks software/edit dates, camera information, GPS, author, and copyright fields. |
| JPEG Ghost | `-g`, `--jpegghost` | Re-saves at one JPEG quality and displays a difference map beside the source image. |
| Multiple JPEG Ghost | `-gm`, `--jpegghostm` | Displays maps from repeated JPEG re-saves at a range of qualities. |
| Noise inconsistencies | `-n1`, `--noise1` | Displays a noise estimate derived from wavelet detail coefficients. |
| Median-filter noise residue | `-n2`, `--noise2` | Displays the difference between the source and a median-filtered image. |
| Error Level Analysis (ELA) | `-el`, `--ela` | Displays the difference between the source and a JPEG re-saved at a selected quality. |
| Demosaicing/CFA artifacts | `-cf`, `--cfa` | Displays a block-based analysis map based on candidate color filter array patterns. |

Analysis images are shown in a Matplotlib window; they are not saved as result
files. JPEG Ghost and ELA temporarily create a re-saved JPEG in the current
working directory and remove it after the plot window is closed.

## Requirements

- Python 3
- The packages listed in [`requirement.txt`](./requirement.txt):
  - OpenCV (`opencv-python`)
  - Pillow
  - ExifRead
  - SciPy
  - PyWavelets
  - NumPy
  - progressbar2
  - Matplotlib

The program accepts files with `.jpg` or `.jpeg` extensions. A working
graphical display is needed for the analysis modes that show plots.

## Setup

From the project directory, create and activate a virtual environment, then
install the dependencies:

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirement.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirement.txt
```

The repository also includes `install_packet.sh`, a Bash script that installs
the packages from `requirement.txt` with `pip`.

## Usage

Run commands from the project directory. The positional argument is the JPEG
image path:

```bash
python foreimg.py <image.jpg> [options]
```

If no analysis option is supplied, the program inspects EXIF metadata. The
explicit EXIF option is:

```bash
python foreimg.py -e exif1.jpg
```

Examples for the other analyses:

```bash
python foreimg.py -g demo.jpg
python foreimg.py -gm demo.jpg
python foreimg.py -n1 demo.jpg
python foreimg.py -n2 demo.jpg
python foreimg.py -el demo.jpg
python foreimg.py -cf demo.jpg
```

Get the command-line help directly from the program:

```bash
python foreimg.py -h
```

### Options

| Option | Applies to | Default | Description |
| --- | --- | --- | --- |
| `-e`, `--exif` | EXIF | Default mode when no mode is selected | Inspect and print available EXIF metadata. |
| `-g`, `--jpegghost` | JPEG Ghost | JPEG quality `60` | Compare the input with a JPEG re-saved at the chosen quality. |
| `-gm`, `--jpegghostm` | Multiple JPEG Ghost | Starts at quality `60`, increasing by `2` for 19 re-saves | Display multiple quality comparisons. |
| `-n1`, `--noise1` | Noise inconsistencies | Block size `8` | Analyze wavelet detail coefficients in blocks. |
| `-n2`, `--noise2` | Median-filter residue | Median-filter kernel size `3` | Analyze the difference after median filtering. |
| `-el`, `--ela` | ELA | JPEG quality `90`; block-size argument defaults to `8` but is not used by the current ELA calculation | Compare the source with a JPEG re-save. |
| `-cf`, `--cfa` | CFA artifacts | Internal block size `16` | Analyze demosaicing-related patterns. |
| `-q`, `--quality <integer>` | JPEG Ghost or ELA | `60` for `-g`; `90` for `-el` | Set the quality used for the JPEG re-save. |
| `-s`, `--blocksize <integer>` | `-n1`, `-n2`, or `-el` | `8` for `-n1` and `-el`; `3` for `-n2` | Set the method's block/kernel size where used. |

For example:

```bash
python foreimg.py -g -q 50 demo.jpg
python foreimg.py -n1 -s 7 demo.jpg
python foreimg.py -n2 -s 7 demo.jpg
python foreimg.py -el -q 90 demo.jpg
```

The script selects one analysis mode at a time. If multiple mode flags are
provided, the first matching mode in its command-line dispatch order is used.
The program does not validate that quality values or kernel sizes are within a
method-specific valid range.

## Project files

| File | Purpose |
| --- | --- |
| `foreimg.py` | Command-line entry point and implementations of metadata, JPEG Ghost, noise, ELA, and CFA analyses. |
| `requirement.txt` | Python dependency list used by pip. |
| `install_packet.sh` | Bash dependency installation helper. |
| `exif1.jpg`, `exif2.jpg`, `exif3.jpg` | Sample JPEGs for EXIF inspection. |
| `demo.jpg`, `demo2.jpg`, `demo3.jpg`, `demo4.jpg` | Sample JPEGs for forensic analysis modes. |
| `Rohit.jpg` | Additional JPEG image included with the project. |

## Limitations

- This is a traditional, exploratory analysis tool, not an automated
  authenticity verdict or a substitute for forensic examination.
- Output is visual or printed metadata; the current CLI does not export reports
  or analysis maps.
- Input is limited by the program to JPEG filename extensions.
- There is no automated test suite included in the project.
