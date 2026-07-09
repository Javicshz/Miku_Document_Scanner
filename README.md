# Miku Document Scanner

This is a document scanner originally made by following the PyImageSearch tutorial:
[Build a Kick-Ass Mobile Document Scanner in Just 5 Minutes](https://pyimagesearch.com/2014/09/01/build-kick-ass-mobile-document-scanner-just-5-minutes/).

I later adapted it to include extra features like OCR, searchable PDF output, multiple image support and a simple Hatsune Miku themed GUI. The Miku design is mostly just for fun but the scanner still works like a normal document scanner.

## Files

The main files in this repo are:

- `scanner_core.py` - Contains the main scanner logic. It reads an image, resizes it, finds the document outline, applies the perspective transform and turns it into a clean scanned page.
- `ocr_pdf.py` - Runs OCR with Tesseract and combines one or more scanned pages into a single searchable PDF.
- `gui_app.py` - Opens a small graphical user interface so the app can be used without running everything manually from the command line.
- `pyimagesearch/transform.py` - Handles the four-point perspective transform used to straighten the document.
- `requirements.txt` - Lists the Python dependencies needed to run the project.
- `assets/` - Stores the GUI images, bundled font and background music used by the app.

The repo also includes two images used while testing the app. I included them for user testing.

## Setup

### Step 1

Clone this repo to your local computer.

### Step 2

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Mac or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate.bat
```

### Step 3

Install the required packages inside the virtual environment:

```bash
pip install -r requirements.txt
```

To confirm everything installed, run:

```bash
pip list
```

### Step 4

Run the GUI app:

```bash
python gui_app.py
```

## Workflow

The app starts by letting the user select one or more image files. Each image is sent through the scanner, where the document outline is detected and transformed so it looks like a flat scanned page. After that, the scanned page is cleaned up into a high contrast black and white image. Tesseract OCR is then used to read the text and create searchable PDF pages. If multiple images are selected, the app combines them into one final PDF.

The GUI also has a fixed-size Miku themed window, pixel-style buttons, falling leek animation and quiet background music.

## Dependencies

The main dependencies used in this project are:

- `opencv-python` - Used for image processing, edge detection, contours and perspective correction.
- `imutils` - Helps simplify OpenCV resizing and contour handling.
- `scikit-image` - Used for local thresholding to make the final scan look cleaner.
- `numpy` - Used for array and point calculations during the image transform.
- `pytesseract` - Connects Python to Tesseract OCR so the PDF can include searchable text.
- `pypdf` - Combines the OCR-generated PDF pages into one final PDF file.
- `pillow`, `imageio` and `tifffile` - Help with image reading and image format support.
- `lxml`, `pikepdf`, `img2pdf`, `networkx`, `scipy`, `packaging`, `lazy-loader` and `wheel` - Supporting packages installed with the image/PDF processing tools.

Tesseract OCR also needs to be installed on the computer separately because `pytesseract` is only the Python wrapper for it.

## Asset Credits and Notices

- Background music: downloaded from DOVA-SYNDROME at [https://dova-s.jp/bgm/detail/23620](https://dova-s.jp/bgm/detail/23620). Use of the music should follow the license and usage rules listed on DOVA-SYNDROME.
- Hatsune Miku character image: Hatsune Miku, © Crypton Future Media, Inc. 2007, licensed under [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/). Based on the creator guidelines from [Piapro / Crypton Future Media](https://piapro.net/intl/en_for_creators.html). This license is for noncommercial use.
- VT323 font: bundled under the SIL Open Font License. See `assets/fonts/VT323/OFL.txt`.
