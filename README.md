# Digital Image Forensics

A Python project for examining JPEG images with several traditional digital
image forensics techniques. Use the command-line utility or the Streamlit web
interface to inspect image metadata and view side-by-side analysis results.

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

The CLI displays analysis images in a Matplotlib window. The web interface
renders those maps in the browser. Analysis maps and EXIF reports are not
exported as files.

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
  - Streamlit (web interface)

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

## Web interface

Run the browser interface locally from the project directory:

```bash
python -m streamlit run streamlit_app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Select an
analysis method, upload a JPEG, set optional parameters where shown, and click
**Analyze image**.

The web interface accepts JPEG files up to 20 MB and 8 megapixels. CFA
demosaicing analysis is restricted to images of 1 megapixel or less because
that algorithm uses substantially more memory. Uploaded images are handled
using temporary files and are removed after the analysis request; deployment
platforms may apply their own logging, cache, or data-retention policies.

## Deployment on Streamlit Community Cloud

The Python CLI cannot run as a GitHub Pages site: GitHub Pages hosts static
content and does not execute Python applications. The Streamlit interface in
[`streamlit_app.py`](./streamlit_app.py) can be hosted on Streamlit Community
Cloud using this GitHub repository:

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with
   GitHub and authorize access to this repository.
2. Choose **Create app** and select `RohitKhobare/Digital_Image_Forensics-`,
   branch `main`, and main file path `streamlit_app.py`.
3. Deploy the app. Streamlit installs the dependencies from
   [`requirement.txt`](./requirement.txt) and provides the public app URL.

The hosted app URL is not included here yet; it must be created from an
authorized Streamlit Community Cloud account. If deployment fails, check the
app's build and runtime logs in Streamlit Cloud.

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
| `streamlit_app.py` | Streamlit browser UI for uploading JPEGs and running the forensic analyses. |
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
- The web interface imposes upload and image-dimension limits to control
  memory use; CFA analysis has a lower pixel limit.
- There is no automated test suite included in the project.
