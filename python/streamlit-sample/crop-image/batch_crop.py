"""Crop a bunch of images."""

from pathlib import Path
from typing import Optional, Tuple

import streamlit as st
from loguru import logger as lg
from PIL import Image
from streamlit_cropper import st_cropper

from folder_select import folder_selector

# INPUT_FOL = Path(".").absolute().expanduser() / "input"
# OUTPUT_FOL = Path(".").absolute().expanduser() / "output"

IMG_EXT = [".png", ".jpg", ".jpeg"]
ASPECT_LIST = [None, (16, 9), (9, 16), (4, 3), (3, 4), (1, 1)]
# MAX_WIDTH = 100
MAX_FILE_SIZE = 1024 * 2

if "pic_id" not in st.session_state:
    st.session_state["pic_id"] = 0
if "is_saving" not in st.session_state:
    st.session_state["is_saving"] = False


def get_file_name(path: Path):
    """Func to get the file name from a Path."""
    return path.name


def fmt_aspect_ratio(aspect_ratio: Optional[Tuple[int, int]]):
    """Format an aspect ratio as a string."""
    if aspect_ratio is None:
        return "Free"
    return f"{aspect_ratio[0]}:{aspect_ratio[1]}"


def save_img(img: Image.Image, max_file_size: int, img_path: Path):
    """Save an image smaller than file_size, with the highest quality possible."""
    lg.debug("Saving...")

    # convert the image to RGB to save as JPEG
    # https://stackoverflow.com/a/48248432/20222481
    img = img.convert("RGB")

    high_qt = 100
    low_qt = 60

    i = 0

    while high_qt - low_qt > 1:
        # try saving with mid qt
        mid_qt = (high_qt + low_qt) // 2
        lg.debug(f"{high_qt} {low_qt} {mid_qt}")
        img.save(img_path, optimize=True, quality=mid_qt, format="jpeg")
        lg.debug(f"{img_path.stat().st_size}")

        # if it's too big, set it as high_qt
        # if it's too small, set it as low_qt
        saved_size = img_path.stat().st_size
        if saved_size > max_file_size:
            high_qt = mid_qt
        else:
            low_qt = mid_qt

        i += 1
        if i > 20:
            break

    lg.debug(f"final {high_qt} {low_qt}")


def main():
    """Crop a bunch of images, then save them compressed."""
    # st.title("Crop images")

    # # upload the first file to select the folder
    # file_start = st.sidebar.file_uploader("Select an image in the folder", type=IMG_EXT)
    # print(file_start)

    input_fol = folder_selector()

    # setup the folders
    # if not input_fol.exists():
    #     st.warning(f"Folder {input_fol} does not exist.")
    #     return

    if input_fol is None:
        st.write("Please select a folder.")
        return

    output_fol = input_fol / "output"
    if not output_fol.exists():
        lg.debug(f"creating {output_fol}")
        output_fol.mkdir(parents=True)

    # get the input images
    image_in_paths = [
        file_path for file_path in input_fol.iterdir() if file_path.suffix in IMG_EXT
    ]
    lg.debug(f"found {len(image_in_paths)} images")

    # create the select box
    if st.session_state["is_saving"]:
        # if it was saving, then go to the next one
        # update the id of the next pic to fix
        # FIXME if there are enough pics
        lg.debug("Was saving: changing pic_id")
        if st.session_state["pic_id"] + 1 < len(image_in_paths):
            st.session_state["pic_id"] += 1
            lg.debug(f"          : {st.session_state['pic_id']}")
        image_in_path: Path = st.sidebar.selectbox(
            "Pick one",
            image_in_paths,
            format_func=get_file_name,
            index=st.session_state["pic_id"],
        )
        # now it is not saving anymore
        st.session_state["is_saving"] = False
    else:
        # if it was not saving, leave the widget as it was
        image_in_path: Path = st.sidebar.selectbox(
            "Pick one",
            image_in_paths,
            format_func=get_file_name,
        )
        # but if the rerun was because of the selectbox
        # we have to update the current pic_id
        st.session_state["pic_id"] = image_in_paths.index(image_in_path)
    # lg.debug(f"{type(image_in_path)=}")

    max_width_str = st.sidebar.text_input("Max width", "2000")
    max_width = int(max_width_str)
    # FIXME clearly has to be validated

    # optionally force a specific aspect ratio
    # aspect_ratio = st.sidebar.radio(
    aspect_ratio = st.sidebar.selectbox(
        "Aspect ratio", ASPECT_LIST, format_func=fmt_aspect_ratio
    )

    # open and crop the image
    img_orig = Image.open(image_in_path)
    img_crop: Image.Image = st_cropper(
        img_orig,
        aspect_ratio=aspect_ratio,
    )
    st.text(f"got {img_crop.width}x{img_crop.height}")
    st.image(img_crop)

    # resize the image, thinner than max width
    if img_crop.width > max_width:
        ratio_w = max_width / img_crop.width
        size = (max_width, int(ratio_w * img_crop.height))
        lg.debug(f"reducing to {size}")
        img_small = img_crop.resize(size, resample=Image.Resampling.LANCZOS)
    else:
        img_small = img_crop.copy()
    st.text(f"got {img_small.width}x{img_small.height}")
    st.image(img_small)

    # find the out path
    img_name = image_in_path.name
    img_out_path = output_fol / img_name
    img_out_path = img_out_path.with_suffix(".jpeg")
    if img_out_path.exists():
        st.write(f"Will overwrite {Path.joinpath(Path('.'),*img_out_path.parts[-3:])}")

    # create the save button
    save_btn = st.button("Save")
    if save_btn:
        # save the image so that's smaller than max size
        # save_img(img_small, MAX_FILE_SIZE, img_out_path)
        st.session_state["is_saving"] = True
        lg.debug("Saving now")
    else:
        st.session_state["is_saving"] = False
        lg.debug("Not saving")
    
    # just a button to trigger a rerun
    st.button("Again")


if __name__ == "__main__":
    main()
