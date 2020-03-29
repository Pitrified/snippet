import logging
from math import sqrt
from math import log
from math import floor
from math import ceil

from PIL import Image
from PIL import ImageTk

from observable import Observable
from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import line_curve_point
from cursive_writer.utils.geometric_utils import translate_point_dir
from cursive_writer.utils.geometric_utils import dist2D
from cursive_writer.utils.oriented_point import OrientedPoint


class Model:
    def __init__(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

        # full path of the current image
        self.pf_input_image = Observable()
        # ImageTk that holds the cropped picture
        self.crop_input_image = Observable()

        # current mouse position
        self.curr_mouse_pos = Observable()

        # canvas width
        self._widget_wid = -1
        self._widget_hei = -1

        # how to react to a mouse movement
        self.state = Observable("free")

        # font measurement: save the SPoint with normalized x,y on
        # descent-base-mean-ascent send the position scaled for display
        # info on all font measurement lines
        self.fm_lines = Observable()
        # proportion between the line
        self.prop_mean_ascent = 0.7
        self.prop_desc_base = 0.6

        # info on the line from clicked point to current
        self.free_line = Observable()
        # info on where you clicked the canvas
        self.click_start_pos = Observable()

    def set_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.set_pf_input_image")
        logg.info(f"{fmt_cn('Setting', 'start')} pf_input_image '{pf_input_image}'")

        self.pf_input_image.set(pf_input_image)

        self._image_cropper = ImageCropper(self.pf_input_image.get())

    def do_canvas_resize(self, widget_wid, widget_hei):
        logg = logging.getLogger(f"c.{__class__.__name__}.do_canvas_resize")
        logg.info(f"{fmt_cn('New', 'start')} canvas is {widget_wid}x{widget_hei}")

        self._widget_wid = widget_wid
        self._widget_hei = widget_hei

        # compute the new image
        self._image_cropper.reset_image(self._widget_wid, self._widget_hei)

        # update the image in the observable, with info on where to put it
        data = {
            "image_res": self._image_cropper.image_res,
            "widget_shift_x": self._image_cropper.widget_shift_x,
            "widget_shift_y": self._image_cropper.widget_shift_y,
            "resized_wid": self._image_cropper.resized_dim[0],
            "resized_hei": self._image_cropper.resized_dim[1],
        }
        self.crop_input_image.set(data)

        # TODO update also lines drawn

    def save_click_canvas(self, mouse_x, mouse_y):
        """Save the pos clicked on the canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.save_click_canvas")

        # mouse pos relative to image corner
        self.start_img_x = mouse_x - self._image_cropper.widget_shift_x
        self.start_img_y = mouse_y - self._image_cropper.widget_shift_y
        logg.info(
            f"{fmt_cn('Clicked', 'start')} - pos in image {self.start_img_x}x{self.start_img_y}"
        )

        current_state = self.state.get()
        logg.debug(f"Clicked current_state: {current_state}")
        if current_state == "free":
            self.state.set("free_clicked")
            self.click_start_pos.set((self.start_img_x, self.start_img_y))
        elif current_state == "setting_base_mean":
            self.state.set("setting_base_mean_clicked")

    def move_canvas_mouse(self, mouse_x, mouse_y):
        """React to mouse movement on Canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_canvas_mouse")
        logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} move_canvas_mouse")

        # save the current pos in the image
        img_mouse_x = mouse_x - self._image_cropper.widget_shift_x
        img_mouse_y = mouse_y - self._image_cropper.widget_shift_y
        self.curr_mouse_pos.set((img_mouse_x, img_mouse_y))

        current_state = self.state.get()
        logg.debug(f"Moved current_state: {current_state}")
        if current_state == "free":
            pass
        elif current_state == "free_clicked":
            line_point = line_curve_point(
                img_mouse_x, img_mouse_y, self.start_img_x, self.start_img_y
            )
            self.free_line.set(line_point)
        elif current_state == "setting_base_mean":
            pass
        elif current_state == "setting_base_mean_clicked":
            fm_lines = self.build_fm_lines("base_mean")
            self.fm_lines.set(fm_lines)

    def release_click_canvas(self, mouse_x, mouse_y):
        logg = logging.getLogger(f"c.{__class__.__name__}.release_click_canvas")

        # mouse pos relative to image corner
        self.end_img_x = mouse_x - self._image_cropper.widget_shift_x
        self.end_img_y = mouse_y - self._image_cropper.widget_shift_y
        logg.info(
            f"{fmt_cn('Released', 'start')} - pos in image {self.end_img_x}x{self.end_img_y}"
        )

        # TODO depending on self.state
        # - adjust baseline
        # - create new point

        current_state = self.state.get()
        logg.debug(f"Released current_state: {current_state}")
        if current_state == "free_clicked":
            # MAYBE add the spline point
            self.state.set("free")
            self.free_line.set(None)
            self.click_start_pos.set(None)
        elif current_state == "setting_base_mean_clicked":
            # compute and save the font measurement info
            fm_lines = self.build_fm_lines("base_mean")
            self.fm_lines.set(fm_lines)
            # after you release the mouse, go back to free state
            self.state.set("free")
        else:
            logg.error(f"Unrecognized current_state released: {current_state}")

    def click_set_base_mean(self):
        """Clicked the button or base mean
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.click_set_base_mean")
        #  logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} click_set_base_mean")

        self.state.set("setting_base_mean")

    def build_fm_lines(self, input_type):
        """Build the font measurement line
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_fm_lines")
        #  logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} build_fm_lines type {input_type}")

        curr_pos_x, curr_pos_y = self.curr_mouse_pos.get()

        if input_type == "base_mean":
            self.vert_point = line_curve_point(
                self.start_img_x, self.start_img_y, curr_pos_x, curr_pos_y
            )
            self.base_point = OrientedPoint(
                self.start_img_x, self.start_img_y, self.vert_point.ori_deg + 90
            )
            self.mean_point = OrientedPoint(
                curr_pos_x, curr_pos_y, self.vert_point.ori_deg + 90
            )

            dist_base_mean = dist2D(self.base_point, self.mean_point)

            dist_base_ascent = dist_base_mean * (1 + self.prop_mean_ascent)
            self.ascent_point = translate_point_dir(
                self.base_point, self.vert_point.ori_deg, dist_base_ascent
            )
            dist_desc_base = dist_base_mean * self.prop_desc_base
            self.descent_point = translate_point_dir(
                self.base_point, self.vert_point.ori_deg, -dist_desc_base
            )

        fm_lines = {
            "vert_point": self.vert_point,
            "base_point": self.base_point,
            "mean_point": self.mean_point,
            "ascent_point": self.ascent_point,
            "descent_point": self.descent_point,
        }
        return fm_lines


class ImageCropper:
    def __init__(self, photo_name_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

        # load the image
        self._photo_name_full = photo_name_full
        self._image = Image.open(self._photo_name_full)
        self._image_wid, self._image_hei = self._image.size

        # setup parameters for resizing
        self.upscaling_mode = Image.NEAREST
        self.downscaling_mode = Image.LANCZOS

        # zoom saved in log scale, actual zoom: zoom_base**zoom_level
        self._zoom_base = sqrt(2)
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

    def reset_image(self, widget_wid=-1, widget_hei=-1):
        """Resets zoom level and position of the image

        Save the current widget dimensions if changed.

        Find zoom_level so that the image fits in the widget:
        _image_wid * ( zoom_base ** zoom_level ) = widget_wid
        and analogously for hei
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.reset_image")
        logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Resetting', 'start')} image")
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
            self._zoom_level = log(ratio, self._zoom_base)

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
        logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Updating', 'start')} crop zoom {self._zoom_level:.4f}")

        # zoom in linear scale
        zoom = self._zoom_base ** self._zoom_level

        # dimension of the virtual zoomed image
        zoom_wid = ceil(self._image_wid * zoom)
        zoom_hei = ceil(self._image_hei * zoom)

        # the zoomed photo fits inside the widget
        if zoom_wid < self.widget_wid and zoom_hei < self.widget_hei:
            logg.trace(f"The zoomed photo fits {fmt_cn('inside', 'a1')} the widget")
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            # take the entire image
            region = (0, 0, self._image_wid, self._image_hei)
            # center the photo in the widget
            self.widget_shift_x = (self.widget_wid - zoom_wid) // 2
            self.widget_shift_y = (self.widget_hei - zoom_hei) // 2

        # the zoomed photo is wider than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei < self.widget_hei:
            logg.trace(f"The zoomed photo is {fmt_cn('wider', 'a1')} than the widget")
            # target dimension as wide as the widget
            resized_dim = (self.widget_wid, zoom_hei)
            # from top to bottom, only keep a vertical stripe
            region = (
                self._mov_x / zoom,
                0,
                (self._mov_x + self.widget_wid) / zoom,
                self._image_hei,
            )
            # center the photo in the widget
            self.widget_shift_x = 0
            self.widget_shift_y = (self.widget_hei - zoom_hei) // 2

        # the zoomed photo is taller than the widget
        elif zoom_wid < self.widget_wid and zoom_hei >= self.widget_hei:
            logg.trace(f"The zoomed photo is {fmt_cn('taller', 'a1')} than the widget")
            resized_dim = (zoom_wid, self.widget_hei)
            region = (
                0,
                self._mov_y / zoom,
                self._image_wid,
                (self._mov_y + self.widget_hei) / zoom,
            )
            # center the photo in the widget
            self.widget_shift_x = (self.widget_wid - zoom_wid) // 2
            self.widget_shift_y = 0

        # the zoomed photo is bigger than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei >= self.widget_hei:
            logg.trace(f"The zoomed photo is {fmt_cn('bigger', 'a1')} than the widget")
            resized_dim = (self.widget_wid, self.widget_hei)
            region = (
                self._mov_x / zoom,
                self._mov_y / zoom,
                (self._mov_x + self.widget_wid) / zoom,
                (self._mov_y + self.widget_hei) / zoom,
            )
            # center the photo in the widget
            self.widget_shift_x = 0
            self.widget_shift_y = 0

        logg.trace(f"resized_dim {resized_dim} region {region}")
        logg.trace(
            f"widget_shift_x {self.widget_shift_x} widget_shift_y {self.widget_shift_y}"
        )
        self.resized_dim = resized_dim

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
