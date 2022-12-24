"""Select the center of the image and make it fit the width/height requirements."""

from loguru import logger as lg
from PIL import Image, ImageFilter


def blur_and_fit(img_orig: Image.Image, width_req: int, height_req: int) -> Image.Image:
    """Select the center of the image and make it fit the width/height requirements."""
    width_orig = img_orig.width
    height_orig = img_orig.height
    width_ratio = width_req / width_orig
    height_ratio = height_req / height_orig
    lg.debug(f"{width_ratio=:.2f} {height_ratio=:.2f}")

    # original is smaller than required
    if width_ratio > 1 and height_ratio > 1:
        if width_ratio > height_ratio:
            lg.debug(f"case 1")
            ratio = height_ratio
        else:
            lg.debug(f"case 2")
            ratio = width_ratio

    # original is bigger than required
    elif width_ratio < 1 and height_ratio < 1:
        if width_ratio > height_ratio:
            lg.debug(f"case 3")
            ratio = height_ratio
        else:
            lg.debug(f"case 4")
            ratio = width_ratio

    # original is taller than required
    elif width_ratio > 1 and height_ratio < 1:
        ratio = height_ratio
        lg.debug(f"case 5")

    # original is wider than required
    elif width_ratio < 1 and height_ratio > 1:
        lg.debug(f"case 6")
        ratio = width_ratio

    # original is identical to required
    else:
        return img_orig

    lg.debug(f"{ratio=:.2f}")
    width_fin = ratio * width_orig
    height_fin = ratio * height_orig
    lg.debug(f"{width_orig=:7.2f} {height_orig=:7.2f}")
    lg.debug(f"{width_fin =:7.2f} {height_fin =:7.2f}")

    return img_orig


def main() -> None:
    """Test the chopping func."""
    imgs = {
        "img1": Image.new(mode="RGB", size=(800, 800)),
        "img2": Image.new(mode="RGB", size=(1800, 400)),
        "img3": Image.new(mode="RGB", size=(2100, 2000)),
        "img4": Image.new(mode="RGB", size=(4000, 1100)),
        "img5": Image.new(mode="RGB", size=(1000, 1100)),
        "img6": Image.new(mode="RGB", size=(2100, 500)),
        "img7": Image.new(mode="RGB", size=(2000, 1000)),
    }

    width_req = 2000
    height_req = 1000
    lg.debug(f"{width_req =:7.2f} {height_req =:7.2f}")
    for img_name, img in imgs.items():
        lg.debug(f"{img_name}")
        blur_and_fit(img, width_req, height_req)


if __name__ == "__main__":
    main()
