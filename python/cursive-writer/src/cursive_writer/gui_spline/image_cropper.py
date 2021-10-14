import logging
import math

from PIL import Image  # type: ignore
from PIL import ImageTk  # type: ignore

from cursive_writer.utils.color_utils import fmt_cn


class ImageCropper:
    """Class to crop a region from an image, saved in image_res

    Various coordinate systems:
        - abs: the real pixel pos in the image, also called img (_image_wid)
        - mov: how much the cropped region is moving inside the image
        - view: the cursor position relative to the visible corner of the image
        - zoom = mov + view: the position relative to the zoomed image corner
        - widget_shift: how much the cropped image must be moved in the widget
            to keep it centered when the zoomed image is smaller than the widget
    """

    def __init__(self, photo_name_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        # load the image
        self._photo_name_full = photo_name_full
        if self._photo_name_full.exists():
            self._image = Image.open(self._photo_name_full)
            self._image_wid, self._image_hei = self._image.size
        else:
            self.create_blank_image()

        # setup parameters for resizing
        self.upscaling_mode = Image.NEAREST
        self.downscaling_mode = Image.LANCZOS

        # zoom saved in log scale, actual zoom: zoom_base**zoom_level
        self._zoom_base = math.sqrt(2)
        self._zoom_level = None

        # shift of the image inside the canvas to keep it centered
        self.widget_shift_x = 0
        self.widget_shift_y = 0

        # dimension of the canvas
        self.widget_wid = -1
        self.widget_hei = -1

        # position of the region you crop inside the image
        self._mov_x = 0
        self._mov_y = 0

    def create_blank_image(self):
        """TODO: what is create_blank_image doing?"""
        logg = logging.getLogger(f"c.{__class__.__name__}.create_blank_image")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('create_blank_image', 'a2')}")

        self._image_wid = 1000
        self._image_hei = 1000
        image_size = (self._image_wid, self._image_hei)
        blank_color = (73, 109, 137)
        self._image = Image.new("RGB", image_size, color=blank_color)

    def reset_image(self, widget_wid=-1, widget_hei=-1):
        """Resets zoom level and position of the image

        Save the current widget dimensions if changed.

        Find zoom_level so that the image fits in the widget:
        _image_wid * ( zoom_base ** zoom_level ) = widget_wid
        and analogously for hei
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.reset_image")
        #  logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Resetting')} image")
        logg.log(5, f"widget_wid: {widget_wid} widget_hei: {widget_hei}")

        if widget_wid != -1:
            self.widget_wid = widget_wid
            self.widget_hei = widget_hei

        #  if self._image_wid < self.widget_wid and self._image_hei < self.widget_hei:
        if False:
            # the original photo is smaller than the widget
            self._zoom_level = 0
        else:
            ratio = min(
                self.widget_wid / self._image_wid, self.widget_hei / self._image_hei
            )
            self._zoom_level = math.log(ratio, self._zoom_base)

        self._mov_x = 0
        self._mov_y = 0
        self.update_crop()

    def update_crop(self):
        """Update the cropped region with the current parameters

        Image.resize takes as args
        - the output dimension (wid, hei)
        - the region to crop from (left, top, right, bottom)

        The Label fills the frame, and the image is centered in the Label,
        there is no need for x_pos and place
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_crop")
        #  logg.setLevel("TRACE")
        logg.log(5, f"{fmt_cn('Updating')} crop zoom {self._zoom_level:.4f}")

        # zoom in linear scale
        zoom = self._zoom_base ** self._zoom_level
        logg.log(5, f"Linear zoom: {zoom}")

        # dimension of the virtual zoomed image
        zoom_wid = math.ceil(self._image_wid * zoom)
        zoom_hei = math.ceil(self._image_hei * zoom)

        # the zoomed photo fits inside the widget
        if zoom_wid <= self.widget_wid and zoom_hei <= self.widget_hei:
            logg.log(5, f"The zoomed photo fits {fmt_cn('inside', 'a1')} the widget")
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            # take the entire image
            region = [0, 0, self._image_wid, self._image_hei]
            # center the photo in the widget
            self.widget_shift_x = (self.widget_wid - zoom_wid) // 2
            self.widget_shift_y = (self.widget_hei - zoom_hei) // 2

        # the zoomed photo is wider than the widget
        elif zoom_wid > self.widget_wid and zoom_hei <= self.widget_hei:
            logg.log(5, f"The zoomed photo is {fmt_cn('wider', 'a1')} than the widget")
            # target dimension as wide as the widget
            resized_dim = (self.widget_wid, zoom_hei)
            # from top to bottom, only keep a vertical stripe
            region = [
                self._mov_x / zoom,
                0,
                (self._mov_x + self.widget_wid) / zoom,
                self._image_hei,
            ]
            # center the photo in the widget
            self.widget_shift_x = 0
            self.widget_shift_y = (self.widget_hei - zoom_hei) // 2

        # the zoomed photo is taller than the widget
        elif zoom_wid <= self.widget_wid and zoom_hei > self.widget_hei:
            logg.log(5, f"The zoomed photo is {fmt_cn('taller', 'a1')} than the widget")
            resized_dim = (zoom_wid, self.widget_hei)
            region = [
                0,
                self._mov_y / zoom,
                self._image_wid,
                (self._mov_y + self.widget_hei) / zoom,
            ]
            # center the photo in the widget
            self.widget_shift_x = (self.widget_wid - zoom_wid) // 2
            self.widget_shift_y = 0

        # the zoomed photo is bigger than the widget
        elif zoom_wid > self.widget_wid and zoom_hei > self.widget_hei:
            logg.log(5, f"The zoomed photo is {fmt_cn('bigger', 'a1')} than the widget")
            resized_dim = (self.widget_wid, self.widget_hei)
            region = [
                self._mov_x / zoom,
                self._mov_y / zoom,
                (self._mov_x + self.widget_wid) / zoom,
                (self._mov_y + self.widget_hei) / zoom,
            ]
            # center the photo in the widget
            self.widget_shift_x = 0
            self.widget_shift_y = 0

        self._validate_region(region)

        logg.log(
            5, f"self._image_wid {self._image_wid} self._image_hei {self._image_hei}"
        )
        logg.log(5, f"zoom_wid {zoom_wid} zoom_hei {zoom_hei}")
        logg.log(5, f"resized_dim {resized_dim} region {region}")
        logg.log(
            5,
            f"widget_shift_x {self.widget_shift_x} widget_shift_y {self.widget_shift_y}",
        )
        # save the positions
        self.resized_dim = resized_dim
        self.zoom = zoom
        self.zoom_wid = zoom_wid
        self.zoom_hei = zoom_hei
        self.region = region

        # decide what method to use when resizing
        if zoom > 1:
            resampling_mode = self.upscaling_mode
        else:
            resampling_mode = self.downscaling_mode

        # apply resize
        image_res = self._image.resize(resized_dim, resampling_mode, region)
        # convert the photo for tkinter
        image_res = ImageTk.PhotoImage(image_res)
        # save it as attribute of the object, not garbage collected
        self.image_res = image_res

    def zoom_image(self, direction, rel_x=-1, rel_y=-1):
        """Change zoom level, keep (rel_x, rel_y) still"""
        logg = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        #  logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Zooming')} image {direction}")

        old_zoom = self._zoom_base ** self._zoom_level
        old_zoom_wid = self._image_wid * old_zoom
        old_zoom_hei = self._image_hei * old_zoom

        if direction == "in":
            self._zoom_level += 1
        elif direction == "out":
            self._zoom_level -= 1
        elif direction == "reset":
            self.reset_image()
            return 0
        else:
            logg.error(f"Unrecognized zooming direction {direction}")
            return 1

        new_zoom = self._zoom_base ** self._zoom_level
        new_zoom_wid = self._image_wid * new_zoom
        new_zoom_hei = self._image_hei * new_zoom
        logg.log(5, f"old_zoom {old_zoom} new_zoom {new_zoom}")
        recap = f"image ({self._image_wid}, {self._image_hei})"
        recap += f" old_zoom ({old_zoom_wid}, {old_zoom_hei})"
        recap += f" new_zoom ({new_zoom_wid}, {new_zoom_hei})"
        logg.log(5, recap)

        # find the center of the photo on the screen if not set
        if rel_x == -1 or rel_y == -1:
            if old_zoom_wid < self.widget_wid and old_zoom_hei < self.widget_hei:
                rel_x = old_zoom_wid / 2
                rel_y = old_zoom_hei / 2
            elif old_zoom_wid >= self.widget_wid and old_zoom_hei < self.widget_hei:
                rel_x = self.widget_wid / 2
                rel_y = old_zoom_hei / 2
            elif old_zoom_wid < self.widget_wid and old_zoom_hei >= self.widget_hei:
                rel_x = old_zoom_wid / 2
                rel_y = self.widget_hei / 2
            elif old_zoom_wid >= self.widget_wid and old_zoom_hei >= self.widget_hei:
                rel_x = self.widget_wid / 2
                rel_y = self.widget_hei / 2
        recap = f"rel_x {rel_x} rel_y {rel_y}"
        recap += f" widget ({self.widget_wid}, {self.widget_hei})"
        logg.log(5, recap)
        recap = f"mov_x/old_zoom {self._mov_x / old_zoom}"
        recap += f" mov_x/new_zoom {self._mov_x / new_zoom}"
        recap += f" rel_x/old_zoom {rel_x / old_zoom}"
        recap += f" rel_x/new_zoom {rel_x / new_zoom}"
        logg.log(5, recap)
        recap = f"(mov_x+rel_x)*new_z/old_z {(self._mov_x+rel_x)*new_zoom/old_zoom}"
        recap += f" (mov_y+rel_y)*new_z/old_z {(self._mov_y+rel_y)*new_zoom/old_zoom}"
        logg.log(5, recap)

        # source of hell was that the formula *is* right, but sometimes to keep
        # a point fixed you need *negative* mov_x, implemented by moving the
        # Label around; this will not happen, and mov can be set to 0.
        # the same happens on the other side, the region should go out of the image
        new_mov_x = (self._mov_x + rel_x) * new_zoom / old_zoom - rel_x
        new_mov_y = (self._mov_y + rel_y) * new_zoom / old_zoom - rel_y

        if new_zoom_wid < self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.log(5, f'new_zoom photo {fmt_cn("smaller", "a1")} than frame')
            self._mov_x = 0
            self._mov_y = 0
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.log(5, f'new_zoom photo {fmt_cn("wider", "a1")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = 0
        elif new_zoom_wid < self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.log(5, f'new_zoom photo {fmt_cn("taller", "a1")} than frame')
            self._mov_x = 0
            self._mov_y = new_mov_y
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.log(5, f'new_zoom photo {fmt_cn("larger", "a1")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = new_mov_y

        self._validate_mov()

        recap = f"mov_x {self._mov_x} mov_y {self._mov_y}"
        logg.log(5, recap)

        self.update_crop()

    def move_image(self, delta_x, delta_y):
        """Move image of specified delta"""
        self._mov_x += delta_x
        self._mov_y += delta_y
        self._validate_mov()
        self.update_crop()

    def _validate_mov(self):
        """Check that mov is reasonable for the current widget/image/zoom"""
        zoom = self._zoom_base ** self._zoom_level
        zoom_wid = self._image_wid * zoom
        zoom_hei = self._image_hei * zoom

        # in any case they can't be negative
        if self._mov_x < 0:
            self._mov_x = 0
        if self._mov_y < 0:
            self._mov_y = 0

        # the zoomed photo fits inside the widget
        if zoom_wid < self.widget_wid and zoom_hei < self.widget_hei:
            self._mov_x = 0
            self._mov_y = 0
        # the zoomed photo is wider than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei < self.widget_hei:
            if self._mov_x + self.widget_wid > zoom_wid:
                self._mov_x = zoom_wid - self.widget_wid
            self._mov_y = 0
        # the zoomed photo is taller than the widget
        elif zoom_wid < self.widget_wid and zoom_hei >= self.widget_hei:
            self._mov_x = 0
            if self._mov_y + self.widget_hei > zoom_hei:
                self._mov_y = zoom_hei - self.widget_hei
        # the zoomed photo is bigger than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei >= self.widget_hei:
            if self._mov_x + self.widget_wid > zoom_wid:
                self._mov_x = zoom_wid - self.widget_wid
            if self._mov_y + self.widget_hei > zoom_hei:
                self._mov_y = zoom_hei - self.widget_hei

    def _validate_region(self, region):
        """region (left, top, right, bottom) must fit inside the image"""
        logg = logging.getLogger(f"c.{__class__.__name__}._validate_region")
        #  logg.setLevel("TRACE")
        logg.log(5, f"Start {fmt_cn('_validate_region')}")

        # left
        if region[0] < 0:
            logg.warn(f"region[0] {region[0]} is less than 0")
            region[0] = 0
        # top
        if region[1] < 0:
            logg.warn(f"region[1] {region[1]} is less than 0")
            region[1] = 0
        # right
        if region[2] > self._image_wid:
            logg.warn(f"region[2] {region[2]} is more than img_wid {self._image_wid}")
            region[2] = self._image_wid
        # bottom
        if region[3] > self._image_hei:
            logg.warn(f"region[3] {region[3]} is more than img_hei {self._image_hei}")
            region[3] = self._image_hei
