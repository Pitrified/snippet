import logging
from math import sqrt
from math import log
from math import floor
from math import ceil

from PIL import Image
from PIL import ImageTk

from observable import Observable
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import line_curve_point
from cursive_writer.utils.geometric_utils import translate_point_dir
from cursive_writer.utils.geometric_utils import dist2D
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.spline_point import SplinePoint


class Model:
    def __init__(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        # full path of the current image
        self.pf_input_image = Observable()
        # ImageTk that holds the cropped picture
        self.crop_input_image = Observable()

        # current mouse position in the image coordinate
        self.curr_mouse_pos = Observable()

        # canvas width
        self._widget_wid = -1
        self._widget_hei = -1

        # how to react to a mouse movement
        self.state = Observable("free")

        # font measurement: save the SPoint with normalized x,y on
        # descent-base-mean-ascent send the position scaled for display
        # info on all font measurement lines
        # in VIEWING coordinates
        self.fm_lines_view = Observable()
        # in ABSOLUTE coordinates
        self.fm_lines_abs = Observable()

        # proportion between the line
        self.prop_mean_ascent = 0.7
        self.prop_desc_base = 0.6

        # info on the line from clicked point to current
        self.free_line = Observable()
        # info on where you clicked the canvas
        self.click_left_start_pos = Observable()

        # all the SplinePoint generated, dict {spid: SP(x, y, od, id), ... }
        self.all_SP = Observable({})
        # id of the NEXT spid to assign
        self.next_spid = 0
        # visible SP, in view coord
        self.visible_SP = Observable({})
        # how to actually build the spline path, as list of lists [[0,1,2], [4,6,7,8]]
        self.active_SP = Observable([[]])
        # id of the selected SP
        self.selected_spid_SP = Observable(None)
        # indexes of the current selected SP, where to put the next one in the path
        self.selected_indexes = [0, -1]
        # id of the SP under the mouse
        self.hovered_SP = -1
        # the index of the selected header, only active when no points are in
        # that glyph or you want to insert a SP at the beginning of a glyph
        self.selected_header_SP = Observable(0)
        # id of the spline header hovered
        self.hovered_header_SP = -1

    ### OPERATIONS ON CANVAS ###

    def set_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.set_pf_input_image")
        logg.info(f"{fmt_cn('Setting', 'start')} pf_input_image '{pf_input_image}'")

        self.pf_input_image.set(pf_input_image)

        # create the new image cropper
        self._image_cropper = ImageCropper(self.pf_input_image.get())
        # NOTE if a new image is loaded, noone redraws it but a configure event

    def do_canvas_resize(self, widget_wid, widget_hei):
        logg = logging.getLogger(f"c.{__class__.__name__}.do_canvas_resize")
        logg.info(f"{fmt_cn('New', 'start')} canvas is {widget_wid}x{widget_hei}")

        self._widget_wid = widget_wid
        self._widget_hei = widget_hei

        # compute the new image
        self._image_cropper.reset_image(self._widget_wid, self._widget_hei)

        self.redraw_canvas()

    def save_click_canvas(self, click_type, mouse_x, mouse_y):
        """Save the pos clicked on the canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.save_click_canvas")

        # mouse pos relative to image corner
        # do this for all click_type and states
        self.start_img_x = mouse_x - self._image_cropper.widget_shift_x
        self.start_img_y = mouse_y - self._image_cropper.widget_shift_y
        logg.info(
            f"{fmt_cn('Clicked', 'start')}: pos in image {self.start_img_x}x{self.start_img_y}"
        )

        current_state = self.state.get()
        logg.debug(f"Clicked current_state: {current_state}")

        # handle left click
        if click_type == "left_click":
            # was free
            if current_state == "free":
                self.state.set("free_clicked_left")
                self.click_left_start_pos.set((self.start_img_x, self.start_img_y))

            # was ready to set BM
            elif current_state == "setting_base_mean":
                self.state.set("setting_base_mean_clicked")

        # handle right click
        elif click_type == "right_click":
            # regardless of state, start moving the image
            # this resets a state like setting_base_mean
            self.state.set("free_clicked_right")
            # save the old mouse pos
            self.old_img_x = self.start_img_x
            self.old_img_y = self.start_img_y

        # handle scroll up
        elif click_type == "scroll_up":
            self.zoom_image("in", self.start_img_x, self.start_img_y)

        # handle scroll down
        elif click_type == "scroll_down":
            self.zoom_image("out", self.start_img_x, self.start_img_y)

        # very weird things
        else:
            logg.error(f"{fmt_cn('Unrecognized', 'error')} click_type {click_type}")

    def move_canvas_mouse(self, move_type, mouse_x, mouse_y):
        """React to mouse movement on Canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_canvas_mouse")
        logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('move_canvas_mouse', 'start')}")

        # save the current pos in the image
        img_mouse_x = mouse_x - self._image_cropper.widget_shift_x
        img_mouse_y = mouse_y - self._image_cropper.widget_shift_y
        self.curr_mouse_pos.set((img_mouse_x, img_mouse_y))

        current_state = self.state.get()
        logg.debug(f"Moved current_state: {current_state}")

        # mouse moved over the canvas
        if move_type == "move_free":
            # nothing specific to this case
            pass

        # moved the mouse while left button clicked
        elif move_type == "move_left_clicked":
            # draw the tangent for the SPoint
            if current_state == "free_clicked_left":
                line_point = line_curve_point(
                    img_mouse_x, img_mouse_y, self.start_img_x, self.start_img_y
                )
                self.free_line.set(line_point)

            # setting BM
            elif current_state == "setting_base_mean_clicked":
                # compute and save the font measurement info:
                # get the new abs lines with current mouse pos
                self.build_fm_lines_abs("base_mean")
                # update the fm_lines_view with the current abs/mov/zoom
                self.recompute_fm_lines_view()

        # moved the mouse while right button clicked
        elif move_type == "move_right_clicked":
            if current_state == "free_clicked_right":
                self.move_image(img_mouse_x, img_mouse_y)

        # very weird things
        else:
            logg.error(f"{fmt_cn('Unrecognized', 'error')} move_type {move_type}")

    def release_click_canvas(self, click_type, mouse_x, mouse_y):
        """The mouse has been released: depending on self.state
            - adjust baseline
            - create new point
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.release_click_canvas")

        # mouse pos relative to image corner
        self.end_img_x = mouse_x - self._image_cropper.widget_shift_x
        self.end_img_y = mouse_y - self._image_cropper.widget_shift_y
        logg.info(
            f"{fmt_cn('Released', 'start')} - pos in image {self.end_img_x}x{self.end_img_y}"
        )

        current_state = self.state.get()
        logg.debug(f"Released current_state: {current_state}")

        # handle left click
        if click_type == "left_click":
            # was clicked left, add the spline point
            if current_state == "free_clicked_left":
                self.add_spline_point()
                self.state.set("free")
                self.free_line.set(None)
                self.click_left_start_pos.set(None)

            # was clicked SBM: set the font measurements
            elif current_state == "setting_base_mean_clicked":
                # compute and save the font measurement info:
                # get the new abs lines with current mouse pos
                self.build_fm_lines_abs("base_mean")
                # update the fm_lines_view with the current abs/mov/zoom
                self.recompute_fm_lines_view()

                # after you release the mouse, go back to free state
                self.state.set("free")

        # handle right click
        elif click_type == "right_click":
            if current_state == "free_clicked_right":
                # move the image
                self.move_image(self.end_img_x, self.end_img_y)
                # go back to free state
                self.state.set("free")

        # very weird things
        else:
            logg.error(f"{fmt_cn('Unrecognized', 'error')} click_type {click_type}")

    def zoom_image(self, direction, img_x, img_y):
        """Zoom the image

        img_x, img_y are relative to the image corner in the widget
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('zoom_image', 'start')} {direction}")

        # compute the new image
        self._image_cropper.zoom_image(direction, img_x, img_y)

        self.redraw_canvas()

    def move_image(self, new_x, new_y):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_image")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('move_image', 'start')}")

        delta_x = self.old_img_x - new_x
        delta_y = self.old_img_y - new_y

        self.old_img_x = new_x
        self.old_img_y = new_y

        self._image_cropper.move_image(delta_x, delta_y)
        self.redraw_canvas()

    def update_image_obs(self):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_image_obs")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('update_image_obs', 'start')}")
        # update the image in the observable, with info on where to put it
        data = {
            "image_res": self._image_cropper.image_res,
            "widget_shift_x": self._image_cropper.widget_shift_x,
            "widget_shift_y": self._image_cropper.widget_shift_y,
            "resized_wid": self._image_cropper.resized_dim[0],
            "resized_hei": self._image_cropper.resized_dim[1],
        }
        self.crop_input_image.set(data)

    def clicked_btn_set_base_mean(self):
        """Clicked the button of base mean
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_mean")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('click_btn_set_base_mean', 'start')}")

        current_state = self.state.get()

        # if it was already in SBM, go back to free
        if current_state == "setting_base_mean":
            self.state.set("free")

        # else go to state SBM
        else:
            self.state.set("setting_base_mean")

    def clicked_btn_set_base_ascent(self):
        """TODO: what is clicked_btn_set_base_ascent doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_ascent")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('clicked_btn_set_base_ascent', 'start')}")

    def clicked_sh_btn_new_spline(self):
        """TODO: what is clicked_sh_btn_new_spline doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_new_spline")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('clicked_sh_btn_new_spline', 'a2')}")

        path = self.active_SP.get()

        sel_idxs = self.selected_indexes
        current_glyph = path[sel_idxs[0]]

        logg.debug(f"sel_idxs: {sel_idxs}")
        logg.debug(f"path[{sel_idxs[0]}]: {current_glyph}")

        # the current_glyph is empty, do nothing
        if len(current_glyph) == 0:
            logg.info(f"Current glyph is {fmt_cn('empty', 'warn')}")
            return

        split_left = current_glyph[: sel_idxs[1] + 1]
        split_right = current_glyph[sel_idxs[1] + 1 :]
        logg.debug(f"split_left: {split_left} split_right: {split_right}")

        path[sel_idxs[0]] = split_left
        path.insert(sel_idxs[0] + 1, split_right)
        logg.debug(f"path: {path}")
        self.active_SP.set(path)

        # cursor at the end of current_glyph: point to NEXT list
        if len(current_glyph) == sel_idxs[1] + 1:
            logg.debug(f"Pointing at the end of the line")
            #  self.selected_indexes = [sel_idxs[0] + 1, -1]
            self.sp_header_btn1_pressed(sel_idxs[0] + 1)

        logg.debug(f"self.selected_indexes: {self.selected_indexes}")

    def redraw_canvas(self):
        """
        """
        self.update_image_obs()
        self.recompute_fm_lines_view()
        self.compute_visible_spline_points()

    ### FONT MEASUREMENTS ###

    def build_fm_lines_abs(self, input_type):
        """Build the font measurement line

        Given the current values of mouse pos and the start_pos, compute the
        new fm_lines_abs
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_fm_lines_abs")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('build_fm_lines_abs', 'start')} type {input_type}")

        # mouse position in the image, scaled for viewing
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

        # these are in VIEWING coord
        fm_lines_view = {
            "vert_point": self.vert_point,
            "base_point": self.base_point,
            "mean_point": self.mean_point,
            "ascent_point": self.ascent_point,
            "descent_point": self.descent_point,
        }
        # rescale them to ABSOLUTE
        fm_lines_abs = self.rescale_fm_lines_to_abs(fm_lines_view)
        # save them
        self.fm_lines_abs.set(fm_lines_abs)

    def recompute_fm_lines_view(self):
        """Updats the value in fm_lines_view to match the current abs/mov/zoom
        """
        curr_abs_lines = self.fm_lines_abs.get()
        if not curr_abs_lines is None:
            new_view_lines = self.rescale_fm_lines_to_view(curr_abs_lines)
            self.fm_lines_view.set(new_view_lines)

    def rescale_fm_lines_to_abs(self, fm_lines_view):
        """Rescale the points from VIEWING coord to ABSOLUTE img coord

        Returns a new dict of points
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.rescale_fm_lines_to_abs")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('rescale_fm_lines_to_abs', 'start')}")

        abs_lines = {}
        for line_name in fm_lines_view:
            abs_point = self.rescale_point(fm_lines_view[line_name], "view2abs")
            abs_lines[line_name] = abs_point
        return abs_lines

    def rescale_fm_lines_to_view(self, fm_lines_abs):
        """Rescale the points from ABSOLUTE img coord to VIEWING coord
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.rescale_fm_lines_to_view")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('rescale_fm_lines_to_view', 'start')}")

        view_lines = {}
        for line_name in fm_lines_abs:
            view_point = self.rescale_point(fm_lines_abs[line_name], "abs2view")
            view_lines[line_name] = view_point
        return view_lines

    def rescale_point(self, point, direction):
        """Rescale a point in the specified direction
            * view2abs
            * abs2view

        Returns a new OrientedPoint
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.rescale_point")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('rescale_point', 'start')}")

        # current zoom value
        zoom = self._image_cropper.zoom
        logg.trace(f"zoom: {zoom}")

        # position of the cropped region inside the zoomed image
        mov_x = self._image_cropper._mov_x
        mov_y = self._image_cropper._mov_y
        logg.trace(f"mov_x: {mov_x} mov_y: {mov_y}")

        if direction == "view2abs":
            # position in the image, scaled for viewing
            view_x = point.x
            view_y = point.y
            logg.trace(f"view_x: {view_x} view_y: {view_y}")

            # compute position in zoomed image
            zoom_x = mov_x + view_x
            zoom_y = mov_y + view_y
            logg.trace(f"zoom_x: {zoom_x} zoom_y: {zoom_y}")

            # rescale from zoomed to absolute
            abs_x = zoom_x / zoom
            abs_y = zoom_y / zoom
            logg.trace(f"abs_x: {abs_x} abs_y: {abs_y}")

            # create a new point
            return OrientedPoint(abs_x, abs_y, point.ori_deg)

        elif direction == "abs2view":
            # position in the image, in absolute coord
            abs_x = point.x
            abs_y = point.y

            # rescale from absolute to zoomed
            zoom_x = abs_x * zoom
            zoom_y = abs_y * zoom

            # compute position in the visible image
            view_x = zoom_x - mov_x
            view_y = zoom_y - mov_y

            # create a new point
            return OrientedPoint(view_x, view_y, point.ori_deg)

    ### SPLINE ###

    def add_spline_point(self):
        """Add the new SplinePoint
            
            - to the dict active_SP
            - update the selected_spid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.add_spline_point")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('add_spline_point', 'start')}")

        if (
            self.start_img_x < 0
            or self.start_img_y < 0
            or self.start_img_x > self._image_cropper.zoom_wid
            or self.start_img_y > self._image_cropper.zoom_hei
        ):
            logg.warn(f"Point {fmt_cn('outside', 'warn')} image")
            return

        # mouse position in the image, scaled for viewing
        view_x, view_y = self.curr_mouse_pos.get()

        view_op = line_curve_point(self.start_img_x, self.start_img_y, view_x, view_y)

        # MAYBE add button to flip this behaviour
        # flip this to draw spline orientation in the other direction
        view_op.set_ori_deg(view_op.ori_deg + 180)

        # RESCALE the point from view to absolute coordinates
        abs_op = self.rescale_point(view_op, "view2abs")

        # create the SplinePoint
        new_sp = SplinePoint(abs_op.x, abs_op.y, abs_op.ori_deg, self.next_spid)

        # save the point
        all_SP = self.all_SP.get()
        all_SP[new_sp.spid] = new_sp
        self.all_SP.set(all_SP)

        # put the point in the active ones
        path = self.active_SP.get()
        path[self.selected_indexes[0]].insert(self.selected_indexes[1] + 1, new_sp.spid)
        self.selected_indexes[1] += 1
        self.active_SP.set(path)

        # update the id of the selected SP
        self.selected_spid_SP.set(new_sp.spid)

        # prepare for the next spid
        self.next_spid += 1
        logg.debug(f"There are now {self.next_spid} SplinePoint")

        # reset the header
        self.selected_header_SP.set(None)

        self.compute_visible_spline_points()

    def compute_visible_spline_points(self):
        """
        """
        logg = logging.getLogger(
            f"c.{__class__.__name__}.compute_visible_spline_points"
        )
        logg.trace(f"Start {fmt_cn('compute_visible_spline_points', 'start')}")

        # region showed in the view, in abs image coordinate
        region = self._image_cropper.region

        all_SP = self.all_SP.get()
        visible_SP = {}
        selected_spid_SP = self.selected_spid_SP.get()

        #  for spid, curr_sp in all_SP.items():
        for hid, glyph in enumerate(self.active_SP.get()):
            for spid in glyph:
                curr_sp = all_SP[spid]

                # check that the point is in the region cropped
                if (
                    region[0] < curr_sp.x < region[2]
                    and region[1] < curr_sp.y < region[3]
                ):
                    view_op = self.rescale_point(curr_sp, "abs2view")

                    # assign a type to the point
                    if spid == selected_spid_SP:
                        arrow_type = "selected"
                    elif spid == self.hovered_SP or hid == self.hovered_header_SP:
                        arrow_type = "active"
                    else:
                        arrow_type = "standard"
                    visible_SP[spid] = [view_op, arrow_type]

        self.visible_SP.set(visible_SP)

    def find_spid_in_active_SP(self, spid):
        """Find the indexes of the given spid in the path
        """
        # whole letter
        path = self.active_SP.get()
        # get each glyph
        for i, glyph in enumerate(path):
            # get each point
            for j, sp in enumerate(glyph):
                if sp == spid:
                    return [i, j]
        return [0, -1]
        # MAYBE return [len(path) - 1, len(path[-1]) - 1] to point at the last element

    def sp_frame_entered(self, spid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_entered', 'start')}")

        # save the id of the point that the mouse is hovering
        self.hovered_SP = spid

        self.compute_visible_spline_points()

    def sp_frame_left(self, spid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_left', 'start')}")

        # reset the id
        self.hovered_SP = -1

        self.compute_visible_spline_points()

    def sp_frame_btn1_pressed(self, spid):
        """React to mouse button 1 pressed on the FrameSPoint with id spid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_btn1_pressed")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('sp_frame_btn1_pressed', 'start')} {spid}")

        self.selected_indexes = self.find_spid_in_active_SP(spid)
        logg.trace(f"selected_indexes: {self.selected_indexes}")

        logg.trace(f"self.active_SP.get(): {self.active_SP.get()}")

        # highlight point
        self.selected_spid_SP.set(spid)

        # remove highlight from header
        self.selected_header_SP.set(None)

        # recompute colors
        self.compute_visible_spline_points()

    def sp_header_entered(self, hid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_entered")
        logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_entered', 'a2')}")

        # save the id of the point that the mouse is hovering
        self.hovered_header_SP = hid

        self.compute_visible_spline_points()

    def sp_header_left(self, hid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_left', 'start')}")

        # reset the id
        self.hovered_header_SP = -1

        self.compute_visible_spline_points()

    def sp_header_btn1_pressed(self, hid):
        """React to mouse button 1 pressed on the header with id hid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_btn1_pressed")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('sp_header_btn1_pressed', 'start')} {hid}")

        # remove highlight from point
        self.selected_spid_SP.set(None)

        # tell the view to highlight this header
        self.selected_header_SP.set(hid)

        # set the indexes to point before the first point in the clicked glyph
        self.selected_indexes = [hid, -1]

        # redraw the visible points: now no one will be highlighted
        self.compute_visible_spline_points()


class ImageCropper:
    def __init__(self, photo_name_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

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
        logg.trace(f"widget_wid: {widget_wid} widget_hei: {widget_hei}")

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
        logg.trace(f"Linear zoom: {zoom}")

        # dimension of the virtual zoomed image
        zoom_wid = ceil(self._image_wid * zoom)
        zoom_hei = ceil(self._image_hei * zoom)

        # the zoomed photo fits inside the widget
        if zoom_wid <= self.widget_wid and zoom_hei <= self.widget_hei:
            logg.trace(f"The zoomed photo fits {fmt_cn('inside', 'a1')} the widget")
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            # take the entire image
            region = [0, 0, self._image_wid, self._image_hei]
            # center the photo in the widget
            self.widget_shift_x = (self.widget_wid - zoom_wid) // 2
            self.widget_shift_y = (self.widget_hei - zoom_hei) // 2

        # the zoomed photo is wider than the widget
        elif zoom_wid > self.widget_wid and zoom_hei <= self.widget_hei:
            logg.trace(f"The zoomed photo is {fmt_cn('wider', 'a1')} than the widget")
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
            logg.trace(f"The zoomed photo is {fmt_cn('taller', 'a1')} than the widget")
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
            logg.trace(f"The zoomed photo is {fmt_cn('bigger', 'a1')} than the widget")
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

        logg.trace(
            f"self._image_wid {self._image_wid} self._image_hei {self._image_hei}"
        )
        logg.trace(f"zoom_wid {zoom_wid} zoom_hei {zoom_hei}")
        logg.trace(f"resized_dim {resized_dim} region {region}")
        logg.trace(
            f"widget_shift_x {self.widget_shift_x} widget_shift_y {self.widget_shift_y}"
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
        """Change zoom level, keep (rel_x, rel_y) still
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        #  logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Zooming', 'start')} image {direction}")

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
        logg.trace(f"old_zoom {old_zoom} new_zoom {new_zoom}")
        recap = f"image ({self._image_wid}, {self._image_hei})"
        recap += f" old_zoom ({old_zoom_wid}, {old_zoom_hei})"
        recap += f" new_zoom ({new_zoom_wid}, {new_zoom_hei})"
        logg.trace(recap)

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
        logg.trace(recap)
        recap = f"mov_x/old_zoom {self._mov_x / old_zoom}"
        recap += f" mov_x/new_zoom {self._mov_x / new_zoom}"
        recap += f" rel_x/old_zoom {rel_x / old_zoom}"
        recap += f" rel_x/new_zoom {rel_x / new_zoom}"
        logg.trace(recap)
        recap = f"(mov_x+rel_x)*new_z/old_z {(self._mov_x+rel_x)*new_zoom/old_zoom}"
        recap += f" (mov_y+rel_y)*new_z/old_z {(self._mov_y+rel_y)*new_zoom/old_zoom}"
        logg.trace(recap)

        # source of hell was that the formula *is* right, but sometimes to keep
        # a point fixed you need *negative* mov_x, implemented by moving the
        # Label around; this will not happen, and mov can be set to 0.
        # the same happens on the other side, the region should go out of the image
        new_mov_x = (self._mov_x + rel_x) * new_zoom / old_zoom - rel_x
        new_mov_y = (self._mov_y + rel_y) * new_zoom / old_zoom - rel_y

        if new_zoom_wid < self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.trace(f'new_zoom photo {fmt_cn("smaller", "a1")} than frame')
            self._mov_x = 0
            self._mov_y = 0
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.trace(f'new_zoom photo {fmt_cn("wider", "a1")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = 0
        elif new_zoom_wid < self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.trace(f'new_zoom photo {fmt_cn("taller", "a1")} than frame')
            self._mov_x = 0
            self._mov_y = new_mov_y
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.trace(f'new_zoom photo {fmt_cn("larger", "a1")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = new_mov_y

        self._validate_mov()

        recap = f"mov_x {self._mov_x} mov_y {self._mov_y}"
        logg.trace(recap)

        self.update_crop()

    def move_image(self, delta_x, delta_y):
        """Move image of specified delta
        """
        self._mov_x += delta_x
        self._mov_y += delta_y
        self._validate_mov()
        self.update_crop()

    def _validate_mov(self):
        """Check that mov is reasonable for the current widget/image/zoom
        """
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
        """region (left, top, right, bottom) must fit inside the image
        """
        logg = logging.getLogger(f"c.{__class__.__name__}._validate_region")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('_validate_region', 'start')}")

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
