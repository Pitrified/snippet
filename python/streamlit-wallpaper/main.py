"""Fit an image to a wallpaper."""

from loguru import logger as lg
from typing import Optional, Tuple
from PIL import Image, ImageFilter
import streamlit as st

from blur_and_fit import blur_and_fit

ASPECT_LIST = [None, (16, 9), (9, 16), (4, 3), (3, 4), (1, 1)]
IMG_EXT = [".png", ".jpg", ".jpeg"]


def fmt_aspect_ratio(aspect_ratio: Optional[Tuple[int, int]]) -> str:
    """Format an aspect ratio as a string."""
    if aspect_ratio is None:
        return "Free"
    return f"{aspect_ratio[0]}:{aspect_ratio[1]}"


def main() -> None:
    """Fit an image to a wallpaper."""
    # sidebar
    aspect_ratio = st.sidebar.selectbox(
        "Aspect ratio", ASPECT_LIST, format_func=fmt_aspect_ratio
    )
    lg.debug(f"{aspect_ratio=}")
    sc1, sc2 = st.sidebar.columns(2)
    with sc1:
        width_st = sc1.text_input("Width:", value="2000")
    with sc2:
        height_st = sc2.text_input("Height:", value="1000")

    lg.debug(f"{width_st=} {height_st=}")
    width_req = int(width_st)
    height_req = int(height_st)

    # main col
    st.title("Wallpaperize")

    img_file = st.file_uploader("Upload an image:", type=IMG_EXT)
    if img_file is None:
        st.stop()

    # st.write(f"{type(img_file)}")

    # get the original file
    img_pil = Image.open(img_file)
    lg.debug(f"{img_pil.width=} {img_pil.height=}")
    st.image(img_pil)

    # chop the center piece and make it larger
    img_chop = blur_and_fit(img_pil, width_req, height_req)

    # blur it
    img_blur = img_pil.filter(ImageFilter.BLUR)
    st.image(img_blur)

    # paste the original in the center


if __name__ == "__main__":
    main()
