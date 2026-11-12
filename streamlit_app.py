import contextlib
import io
import os
import tempfile
import threading

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image, UnidentifiedImageError

import foreimg


MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_IMAGE_PIXELS = 8_000_000
MAX_CFA_PIXELS = 1_000_000
ANALYSIS_LOCK = threading.Lock()

ANALYSES = {
    "EXIF metadata": "exif",
    "JPEG Ghost": "jpeg_ghost",
    "Multiple JPEG Ghost": "jpeg_ghost_multiple",
    "Noise inconsistencies": "noise",
    "Median-filter noise residue": "median_noise",
    "Error Level Analysis": "ela",
    "CFA demosaicing artifacts": "cfa",
}

st.set_page_config(page_title="Digital Image Forensics", page_icon="🔎")
st.title("Digital Image Forensics")
st.write(
    "Inspect JPEG metadata and explore traditional image-forensics analysis "
    "maps. Results are indicators only, not proof of manipulation."
)
st.warning(
    "Images are analyzed in memory or temporary files for this session and are "
    "not retained by this app. Avoid uploading sensitive images to a hosted "
    "service unless you are comfortable with that service's privacy practices."
)

analysis_name = st.selectbox("Analysis method", list(ANALYSES))
uploaded_file = st.file_uploader(
    "Choose a JPEG image", type=("jpg", "jpeg"), accept_multiple_files=False
)

quality = None
block_size = None
if analysis_name in ("JPEG Ghost", "Error Level Analysis"):
    default_quality = 60 if analysis_name == "JPEG Ghost" else 90
    quality = st.slider("JPEG re-save quality", 1, 100, default_quality)
if analysis_name in ("Noise inconsistencies", "Median-filter noise residue"):
    if analysis_name == "Noise inconsistencies":
        block_size = st.select_slider("Block size", options=(4, 8, 16), value=8)
    else:
        block_size = st.select_slider(
            "Median-filter kernel size", options=(3, 5, 7, 9), value=3
        )

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        st.error("The uploaded file exceeds the 20 MB limit.")
        st.stop()

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            if image.format != "JPEG":
                st.error("The uploaded file is not a valid JPEG image.")
                st.stop()
            image_width, image_height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError):
        st.error("The uploaded file is not a readable JPEG image.")
        st.stop()

    if image_width < 16 or image_height < 16:
        st.error("Images must be at least 16 pixels wide and 16 pixels tall.")
        st.stop()

    pixel_count = image_width * image_height
    if pixel_count > MAX_IMAGE_PIXELS:
        st.error("Images must be 8 megapixels or smaller.")
        st.stop()
    if ANALYSES[analysis_name] == "cfa" and pixel_count > MAX_CFA_PIXELS:
        st.error(
            "CFA analysis is memory-intensive. For this hosted app, use an "
            "image of 1 megapixel or smaller."
        )
        st.stop()

    st.image(image_bytes, caption=uploaded_file.name, width="stretch")
    if st.button("Analyze image", type="primary"):
        with tempfile.TemporaryDirectory() as work_dir:
            image_path = os.path.join(work_dir, "uploaded.jpg")
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            st.subheader(analysis_name)
            output = io.StringIO()
            figure = None
            with ANALYSIS_LOCK:
                plt.close("all")
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(
                    output
                ):
                    method = ANALYSES[analysis_name]
                    if method == "exif":
                        foreimg.exif_check(image_path)
                    elif method == "jpeg_ghost":
                        figure = foreimg.jpeg_ghost(
                            image_path, quality, show_plot=False
                        )
                    elif method == "jpeg_ghost_multiple":
                        figure = foreimg.jpeg_ghost_multiple(
                            image_path, show_plot=False
                        )
                    elif method == "noise":
                        figure = foreimg.noise_inconsistencies(
                            image_path, block_size, show_plot=False
                        )
                    elif method == "median_noise":
                        figure = foreimg.median_noise_inconsistencies(
                            image_path, block_size, show_plot=False
                        )
                    elif method == "ela":
                        figure = foreimg.ela(
                            image_path, quality, None, show_plot=False
                        )
                    else:
                        figure = foreimg.cfa_tamper_detection(
                            image_path, show_plot=False
                        )

                if figure is not None:
                    st.pyplot(figure)
                    plt.close(figure)
                result_text = output.getvalue().strip()
                if result_text:
                    st.text(result_text)
                if method == "exif" and "EXIF data has been stripped" in result_text:
                    st.info(
                        "This image has no readable EXIF metadata; other "
                        "analysis methods may still be available."
                    )

st.caption(
    "For educational and exploratory use. Findings should be reviewed by a "
    "qualified examiner and corroborated with other evidence."
)
