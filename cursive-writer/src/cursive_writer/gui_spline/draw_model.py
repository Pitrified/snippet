import logging
import math

from cursive_writer.gui_spline.image_cropper import ImageCropper
from cursive_writer.gui_spline.observable import Observable
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import apply_affine_transform
from cursive_writer.utils.geometric_utils import compute_affine_transform
from cursive_writer.utils.geometric_utils import dist2D
from cursive_writer.utils.geometric_utils import line_curve_point
from cursive_writer.utils.geometric_utils import translate_point_dir
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.spline_point import SplinePoint
from cursive_writer.utils.spline_segment_holder import SplineSegmentHolder
from cursive_writer.utils.utils import enumerate_double_list
from cursive_writer.utils.utils import find_free_index
from cursive_writer.utils.utils import iterate_double_list
from cursive_writer.utils.utils import load_glyph
from cursive_writer.utils.utils import load_spline


class Model:
    def __init__(self, thickness):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        self.thickness = thickness

        # Path of the current image
        self.pf_input_image = Observable()
        # Path to the folder to save the spline in
        self.data_dir = Observable()

        # ImageTk that holds the cropped picture
        self.crop_input_image = Observable()

        # current mouse position in the image coordinate
        self.curr_mouse_pos_info = Observable()

        # canvas width
        self._widget_wid = -1
        self._widget_hei = -1

        # how to react to a mouse movement
        self.state = Observable("free")

        ### FONT MEASUREMENT ###

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
        # we want that to be the normalized height
        self.normalized_dist_base_mean = 1000

        # how much the points are translated when adjusting
        self.setup_adjust_dict()

        # info on the line from clicked point to current
        self.free_line = Observable()
        # info on where you clicked the canvas
        self.click_left_start_pos = Observable()

        self.abs2fm = None
        self.fm2abs = None

        ### SPLINE POINTS ###

        # all the SplinePoint generated, dict {spid: SP(x, y, od, id), ... }
        self.all_SP = Observable({})
        # id of the NEXT spid to assign
        self.next_spid = 0
        # visible SP, in view coord
        self.visible_SP = Observable({})
        # how to actually build the spline path, as list of lists [[0,1,2], [4,6,7,8]]
        self.path_SP = Observable([[]])
        # id of the selected SP
        self.selected_spid_SP = Observable(None)
        # indexes of the current selected SP in the path, or [n, -1] for header n
        self.selected_indexes = [0, -1]
        # id of the SP under the mouse
        self.hovered_SP = -1
        # the index of the selected header, only active when no points are in
        # that glyph or you want to insert a SP at the beginning of a glyph
        self.selected_header_SP = Observable(0)
        # id of the spline header hovered
        self.hovered_header_SP = -1

        self.spline_segment_holder = SplineSegmentHolder()
        self.spline_thick_holder = SplineSegmentHolder(thickness=self.thickness)
        # list of lists with segment points
        self.visible_segment_SP = Observable()
        # TODO what structure does this have
        self.thick_segment_points = Observable()

    def setup_adjust_dict(self):
        """TODO: what is setup_adjust_dict doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.setup_adjust_dict")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('setup_adjust_dict')}")

        self.shift = 0.1
        self.very_shift = 1
        self.rot = 0.1
        self.very_rot = 1

        self.adjust_shift = {}
        self.adjust_shift["vl"] = (-self.very_shift, 0)
        self.adjust_shift["l"] = (-self.shift, 0)
        self.adjust_shift["r"] = (self.shift, 0)
        self.adjust_shift["vr"] = (self.very_shift, 0)
        self.adjust_shift["vb"] = (0, self.very_shift)
        self.adjust_shift["b"] = (0, self.shift)
        self.adjust_shift["u"] = (0, -self.shift)
        self.adjust_shift["vu"] = (0, -self.very_shift)

        self.adjust_rot = {}
        self.adjust_rot["va"] = -self.very_rot
        self.adjust_rot["a"] = -self.rot
        self.adjust_rot["o"] = self.rot
        self.adjust_rot["vo"] = self.very_rot

    ### OPERATIONS ON CANVAS ###

    def set_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.set_pf_input_image")
        logg.info(f"{fmt_cn('Setting')} pf_input_image '{pf_input_image}'")

        self.pf_input_image.set(pf_input_image)

        # create the new image cropper
        self._image_cropper = ImageCropper(self.pf_input_image.get())
        # NOTE if a new image is loaded, noone redraws it but a configure event

    def do_canvas_resize(self, widget_wid, widget_hei):
        logg = logging.getLogger(f"c.{__class__.__name__}.do_canvas_resize")
        logg.info(f"{fmt_cn('New')} canvas is {widget_wid}x{widget_hei}")

        self._widget_wid = widget_wid
        self._widget_hei = widget_hei

        # compute the new image
        self._image_cropper.reset_image(self._widget_wid, self._widget_hei)

        self.redraw_canvas()

    def save_click_canvas(self, click_type, canvas_x, canvas_y):
        """Save the pos clicked on the canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.save_click_canvas")

        # mouse pos relative to image corner
        # do this for all click_type and states
        self.start_view_x = canvas_x - self._image_cropper.widget_shift_x
        self.start_view_y = canvas_y - self._image_cropper.widget_shift_y

        current_state = self.state.get()

        recap = f"{fmt_cn('Clicked')} mouse on canvas"
        recap += f" - start_view_pos {self.start_view_x}x{self.start_view_y}"
        recap += f" - current_state: {current_state}"
        logg.info(recap)

        # handle left click
        if click_type == "left_click":
            # was free
            if current_state == "free":
                self.state.set("free_clicked_left")
                self.click_left_start_pos.set((self.start_view_x, self.start_view_y))

            # was ready to set BM
            elif current_state == "setting_base_mean":
                self.state.set("setting_base_mean_clicked")

        # handle right click
        elif click_type == "right_click":
            # regardless of state, start moving the image
            # this resets a state like setting_base_mean
            self.state.set("free_clicked_right")
            # save the old mouse pos
            self.old_move_view_x = self.start_view_x
            self.old_move_view_y = self.start_view_y

        # handle scroll up
        elif click_type == "scroll_up":
            self.zoom_image("in", self.start_view_x, self.start_view_y)

        # handle scroll down
        elif click_type == "scroll_down":
            self.zoom_image("out", self.start_view_x, self.start_view_y)

        # very weird things
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} click_type {click_type}")

    def move_canvas_mouse(self, move_type, canvas_x, canvas_y):
        """React to mouse movement on Canvas
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_canvas_mouse")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('move_canvas_mouse')}")

        # save the current pos in the image
        self.move_view_x = canvas_x - self._image_cropper.widget_shift_x
        self.move_view_y = canvas_y - self._image_cropper.widget_shift_y

        # compute and update mouse pos info to send and show
        self.update_mouse_pos_info(canvas_x, canvas_y)

        current_state = self.state.get()
        logg.trace(f"Moved current_state: {current_state}")

        # mouse moved over the canvas
        if move_type == "move_free":
            # nothing specific to this case
            pass

        # moved the mouse while left button clicked
        elif move_type == "move_left_clicked":
            # draw the tangent for the SPoint
            if current_state == "free_clicked_left":
                line_point = line_curve_point(
                    self.start_view_x,
                    self.start_view_y,
                    self.move_view_x,
                    self.move_view_y,
                )
                self.free_line.set(line_point)

            # setting BM
            elif current_state == "setting_base_mean_clicked":
                # compute and save the font measurement info:
                # get the new abs lines with current mouse pos
                self.build_fm_lines_abs(
                    "base_mean",
                    self.start_view_x,
                    self.start_view_y,
                    self.move_view_x,
                    self.move_view_y,
                )
                # update the fm_lines_view with the current abs/mov/zoom
                self.recompute_fm_lines_view()

        # moved the mouse while right button clicked
        elif move_type == "move_right_clicked":
            if current_state == "free_clicked_right":
                self.move_image(self.move_view_x, self.move_view_y)

        # very weird things
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} move_type {move_type}")

    def release_click_canvas(self, click_type, canvas_x, canvas_y):
        """The mouse has been released: depending on self.state
            - create new point
            - set baseline
            - adjust baseline
            - move glyph
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.release_click_canvas")

        # mouse pos relative to image corner
        self.end_view_x = canvas_x - self._image_cropper.widget_shift_x
        self.end_view_y = canvas_y - self._image_cropper.widget_shift_y

        current_state = self.state.get()

        logg.info(f"{fmt_cn('Released')} view_pos {self.end_view_x}x{self.end_view_y}")

        recap = f"{fmt_cn('Released')} mouse on canvas"
        recap += f" - end_view_pos {self.end_view_x}x{self.end_view_y}"
        recap += f" - current_state: {current_state}"
        logg.info(recap)

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
                self.build_fm_lines_abs(
                    "base_mean",
                    self.start_view_x,
                    self.start_view_y,
                    self.end_view_x,
                    self.end_view_y,
                )
                # update the fm_lines_view with the current abs/mov/zoom
                self.recompute_fm_lines_view()
                # update the thick_segment_points now that FM are available
                self.update_thick_segments()
                # after you release the mouse, go back to free state
                self.state.set("free")

            # was adjusting base or mean
            elif current_state in ["adjusting_base", "adjusting_mean"]:
                # update the FM lines using the clicked point as base or mean
                self.adjust_fm_lines("mouse_release")
                # after you release the mouse, *do not* go back to free state

            # was moving glyph
            elif current_state == "moving_glyph":
                # move the glyph using the selected point and the released pos
                self.move_glyph("mouse_release")
                # after you release the mouse, go back to free state
                self.state.set("free")

        # handle right click
        elif click_type == "right_click":
            if current_state == "free_clicked_right":
                # move the image
                self.move_image(self.end_view_x, self.end_view_y)
                # go back to free state
                self.state.set("free")
                # draw the changes
                self.redraw_canvas()

        # very weird things
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} click_type {click_type}")
            return

    def zoom_image(self, direction, view_x, view_y):
        """Zoom the image

        view_x, view_y are relative to the image corner that you see in the widget
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        #  logg.setLevel("INFO")
        logg.info(f"Start {fmt_cn('zoom_image')} {direction}")

        # compute the new image
        self._image_cropper.zoom_image(direction, view_x, view_y)

        self.redraw_canvas()

    def move_image(self, new_move_view_x, new_move_view_y):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_image")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('move_image')}")

        delta_x = self.old_move_view_x - new_move_view_x
        delta_y = self.old_move_view_y - new_move_view_y

        self.old_move_view_x = new_move_view_x
        self.old_move_view_y = new_move_view_y

        self._image_cropper.move_image(delta_x, delta_y)
        self.redraw_canvas()

    def update_image_obs(self):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_image_obs")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('update_image_obs')}")
        # update the image in the observable, with info on where to put it
        data = {
            "image_res": self._image_cropper.image_res,
            "widget_shift_x": self._image_cropper.widget_shift_x,
            "widget_shift_y": self._image_cropper.widget_shift_y,
            "resized_wid": self._image_cropper.resized_dim[0],
            "resized_hei": self._image_cropper.resized_dim[1],
        }
        self.crop_input_image.set(data)

    def clicked_btn_set_fm(self, fm_set_type):
        """Clicked one of the button of font measurement set
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_fm")
        #  logg.setLevel("INFO")
        logg.info(f"Start {fmt_cn('click_btn_set_fm')} - {fm_set_type}")

        current_state = self.state.get()

        if fm_set_type == "bm":
            # if it was already in SBM, go back to free
            if current_state == "setting_base_mean":
                self.state.set("free")

            # else go to state SBM
            else:
                self.state.set("setting_base_mean")

        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} fm_set_type {fm_set_type}")

    def clicked_btn_adjust_fm(self, fm_adjust_type):
        """Clicked one of the button of font measurement set
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_fm")
        #  logg.setLevel("INFO")
        logg.info(f"Start {fmt_cn('click_btn_set_fm')} - {fm_adjust_type}")

        fm_lines_abs = self.fm_lines_abs.get()
        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the FM lines before adjusting them")
            self.state.set("free")
            return

        current_state = self.state.get()

        if fm_adjust_type == "base":
            # if it was already in AB, go back to free
            if current_state == "adjusting_base":
                self.state.set("free")
            else:
                self.state.set("adjusting_base")

        elif fm_adjust_type == "mean":
            # if it was already in AM, go back to free
            if current_state == "adjusting_mean":
                self.state.set("free")
            else:
                self.state.set("adjusting_mean")

        else:
            logg.warn(
                f"{fmt_cn('Unrecognized', 'alert')} fm_adjust_type {fm_adjust_type}"
            )

    def clicked_btn_set_base_ascent(self):
        """TODO: change state to setting_base_ascent
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_ascent")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_btn_set_base_ascent')}")

    def clicked_sh_btn_new_spline(self):
        """Start working on a new glyph

        Either you are at the end of the current_glyph, so you create a new one
        and start building that, or you are in the middle of the current, so
        you split that in two and keep working on the end of the first chunk
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_new_spline")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_sh_btn_new_spline')}")

        path = self.path_SP.get()
        sel_idxs = self.selected_indexes
        current_glyph = path[sel_idxs[0]]
        logg.debug(f"sel_idxs: {sel_idxs}")
        logg.debug(f"path[{sel_idxs[0]}]: {current_glyph}")

        # the current_glyph is empty, do nothing
        if len(current_glyph) == 0:
            logg.info(f"Current glyph is {fmt_cn('empty', 'warn')}")
            return

        # the selected glyph is not the first
        if sel_idxs[0] > 0:
            # the previous glyph is emptry
            if len(path[sel_idxs[0] - 1]) == 0:
                logg.info(f"Previous glyph is {fmt_cn('empty', 'warn')}")
                return

        # the selected glyph is not the last
        if sel_idxs[0] < len(path) - 1:
            # the selected point is the last in the glyph
            if len(path[sel_idxs[0]]) - 1 == sel_idxs[1]:
                # the next glyph is empty
                if len(path[sel_idxs[0] + 1]) == 0:
                    logg.info(f"Next glyph is {fmt_cn('empty', 'warn')}")
                    return

        split_left = current_glyph[: sel_idxs[1] + 1]
        split_right = current_glyph[sel_idxs[1] + 1 :]
        logg.debug(f"split_left: {split_left} split_right: {split_right}")

        path[sel_idxs[0]] = split_left
        path.insert(sel_idxs[0] + 1, split_right)
        logg.debug(f"path: {path}")
        self.path_SP.set(path)

        # update the segment holder
        self.spline_segment_holder.update_data(self.all_SP.get(), path)
        # update the visible segments
        self.compute_visible_segment_points()

        self.update_thick_segments()

        # cursor at the end of current_glyph: point to NEXT list
        if len(current_glyph) == sel_idxs[1] + 1:
            logg.debug(f"Pointing at the end of the line")
            #  self.selected_indexes = [sel_idxs[0] + 1, -1]
            self.sp_header_btn1_pressed(sel_idxs[0] + 1)

        logg.debug(f"self.selected_indexes: {self.selected_indexes}")

    def clicked_sh_btn_delete_SP(self):
        """Delete a spline point or a header

        The point is straightforward, just remove it from the list
        For the header, if it is the first, do nothing, else merge with the previous
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_delete_SP")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_sh_btn_delete_SP')}")

        path = self.path_SP.get()
        glyph_idx, point_idx = self.selected_indexes

        logg.debug(f"path: {path}")
        logg.debug(f"glyph_idx, point_idx: {glyph_idx} {point_idx}")

        # delete header
        if point_idx == -1:
            if glyph_idx == 0:
                logg.info(f"Cannot remove the {fmt_cn('first', 'warn')} glyph")
                return

            # update the selected_indexes before popping
            new_glyph_idx = glyph_idx - 1
            new_point_idx = len(path[new_glyph_idx]) - 1
            logg.debug(f"new_glyph_idx, new_point_idx: {new_glyph_idx} {new_point_idx}")

            # pop the selected glyph from the path
            popped_glyph = path.pop(glyph_idx)
            logg.debug(f"path after pop: {path} popped_glyph: {popped_glyph}")

            # insert it by extending the previous glyph
            path[glyph_idx - 1].extend(popped_glyph)
            logg.debug(f"path after extend: {path}")

        # delete point
        else:
            # find spid of point to remove
            spid_pop = path[glyph_idx][point_idx]

            # remove it from the path
            path[glyph_idx].remove(spid_pop)
            logg.debug(f"path after remove: {path} spid_pop: {spid_pop}")

            # update the selected_indexes
            new_glyph_idx = glyph_idx
            new_point_idx = point_idx - 1
            logg.debug(f"new_glyph_idx, new_point_idx: {new_glyph_idx} {new_point_idx}")

        # update the path
        self.path_SP.set(path)

        # update the cursor
        self.selected_indexes = [new_glyph_idx, new_point_idx]

        # update the segment holder
        self.spline_segment_holder.update_data(self.all_SP.get(), path)
        # update the visible segments
        self.compute_visible_segment_points()

        self.update_thick_segments()

        # update the selected label
        # now pointing to a header
        if new_point_idx == -1:
            self.selected_spid_SP.set(None)
            self.selected_header_SP.set(new_glyph_idx)

        # now pointing at a point
        else:
            self.selected_spid_SP.set(path[new_glyph_idx][new_point_idx])
            self.selected_header_SP.set(None)

        # technically not needer if a header has been deleted, but it does not hurt
        self.compute_visible_spline_points()

    def clicked_btn_adjust(self, adjust_type):
        """Adjust the position/orientation of the selected point
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_adjust")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_btn_adjust')}")

        if self.state.get() in ["adjusting_base", "adjusting_mean"]:
            self.adjust_fm_lines("adjust_btn", adjust_type)
            return

        if self.selected_indexes[1] == -1:
            glyph_idx = self.selected_indexes[0]
            logg.debug(f"{fmt_cn('Moving', 'a1')} glyph {glyph_idx}")

            if adjust_type in self.adjust_shift:
                self.translate_glyph(glyph_idx, *self.adjust_shift[adjust_type])
            else:
                logg.warn(f"{fmt_cn('Cannot', 'warn')} rotate a glyph")
                return

        # translate the current active point
        else:
            all_SP = self.all_SP.get()
            sel_pt = all_SP[self.selected_spid_SP.get()]

            if adjust_type in self.adjust_shift:
                sel_pt.translate(*self.adjust_shift[adjust_type])
            elif adjust_type in self.adjust_rot:
                sel_pt.rotate(self.adjust_rot[adjust_type])
            else:
                logg.warn(f"{fmt_cn('Unrecognized', 'warn')} adjust_type {adjust_type}")
                return

            # update the point
            all_SP[self.selected_spid_SP.get()] = sel_pt
            self.all_SP.set(all_SP)

        # update the visible spline points
        self.compute_visible_spline_points()
        # update the segment holder
        self.spline_segment_holder.update_data(self.all_SP.get(), self.path_SP.get())
        # update the visible segments
        self.compute_visible_segment_points()
        # update the thick spline
        self.update_thick_segments()

    def clicked_btn_move_glyph(self):
        """TODO: what is clicked_btn_move_glyph doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_move_glyph")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_btn_move_glyph')}")

        all_SP = self.all_SP.get()
        selected_spid_SP = self.selected_spid_SP.get()
        if selected_spid_SP not in all_SP:
            logg.warn(f"{fmt_cn('No glyph', 'alert')} to move")
            self.state.set("free")
            return

        if self.state.get() == "moving_glyph":
            self.state.set("free")
        else:
            self.state.set("moving_glyph")

    def clicked_fs_btn_save_spline(self, glyph_root_name):
        """Save the spline points to file
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_save_spline")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fs_btn_save_spline')}")

        data_dir = self.data_dir.get()

        if data_dir is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the output folder before saving")
            return

        if glyph_root_name == "":
            logg.warn(f"{fmt_cn('Set', 'alert')} the glyph root name before saving")
            return

        fm_lines_abs = self.fm_lines_abs.get()
        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the font measurements before saving")
            return

        if not data_dir.exists():
            data_dir.mkdir(parents=True)

        letter_name_fmt = f"{glyph_root_name}_{{:03d}}.txt"
        glyph_name_fmt = f"{glyph_root_name}_{{:03d}}_{{:03d}}.txt"
        logg.debug(f"letter_name_fmt {letter_name_fmt} glyph_name_fmt {glyph_name_fmt}")

        # get the first free file index glyph_root_name_NNN.txt
        file_index = find_free_index(data_dir, letter_name_fmt)

        # full path to the letter recap file
        letter_name = data_dir / letter_name_fmt.format(file_index)
        logg.debug(f"letter_name: {letter_name}")

        path = self.path_SP.get()
        all_SP = self.all_SP.get()
        base_point_abs = fm_lines_abs["base_point"]
        logg.debug(f"base_point_abs: {base_point_abs}")

        # save which glyph make this letter
        all_glyphs = ""

        # go through all the glyphs
        for glyph_index in range(len(path)):
            # build the name of the glyph file
            glyph_name = glyph_name_fmt.format(file_index, glyph_index)
            # build the glyph full file name
            full_glyph_name = data_dir / glyph_name

            # build the line for the main file
            path_line = f"{glyph_name}\t0\t0\n"
            all_glyphs += path_line

            # build the glyph point recap
            str_glyph = ""
            for spid in path[glyph_index]:
                abs_pt = all_SP[spid]
                # find the coord of the point in fm frame
                fm_x, fm_y = apply_affine_transform(self.abs2fm, abs_pt.x, abs_pt.y)
                fm_ori_deg = -abs_pt.ori_deg + base_point_abs.ori_deg
                # create the OrientedPoint to normalize the angle
                fm_op = OrientedPoint(fm_x, fm_y, fm_ori_deg)
                gly_line = f"{fm_op.x}\t{fm_op.y}\t{fm_op.ori_deg}\n"
                str_glyph += gly_line
            full_glyph_name.write_text(str_glyph)

        letter_name.write_text(all_glyphs)

    def clicked_fs_btn_set_save_path(self, data_dir):
        """Set the output folder to save the spline into
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_set_save_path")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fs_btn_set_save_path')} {data_dir}")

        self.data_dir.set(data_dir)

    def clicked_fl_btn_load_glyph(self, path_input_glyph):
        """TODO: what is clicked_fl_btn_load_glyph doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fl_btn_load_glyph")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fl_btn_load_glyph')}")

        fm_lines_abs = self.fm_lines_abs.get()
        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the font measurements before loading")
            return
        base_point_abs = fm_lines_abs["base_point"]

        fm_ops = load_glyph(path_input_glyph, dx=0, dy=0)
        logg.trace(f"fm_ops: {fm_ops}")

        # start new glyph
        self.clicked_sh_btn_new_spline()

        for fm_op in fm_ops:
            abs_x, abs_y = apply_affine_transform(self.fm2abs, fm_op.x, fm_op.y)
            abs_ori_deg = -fm_op.ori_deg + base_point_abs.ori_deg
            abs_op = OrientedPoint(abs_x, abs_y, abs_ori_deg)
            self.add_spline_abs_point(abs_op)

    def clicked_fl_btn_load_spline(self, path_input_spline):
        """TODO: what is clicked_fl_btn_load_spline doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fl_btn_load_spline")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fl_btn_load_spline')}")

        fm_lines_abs = self.fm_lines_abs.get()
        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the font measurements before loading")
            return
        base_point_abs = fm_lines_abs["base_point"]

        data_dir = self.data_dir.get()

        fm_ops = load_spline(path_input_spline, data_dir, dx=0, dy=0)
        logg.trace(f"fm_ops: {fm_ops}")

        # iterate each glyph seq of points
        for glyph_ops in fm_ops:

            # start new glyph
            self.clicked_sh_btn_new_spline()

            for fm_op in glyph_ops:
                abs_x, abs_y = apply_affine_transform(self.fm2abs, fm_op.x, fm_op.y)
                abs_ori_deg = -fm_op.ori_deg + base_point_abs.ori_deg
                abs_op = OrientedPoint(abs_x, abs_y, abs_ori_deg)
                self.add_spline_abs_point(abs_op)

    def redraw_canvas(self):
        """
        """
        self.update_image_obs()
        self.recompute_fm_lines_view()
        self.compute_visible_spline_points()
        self.compute_visible_segment_points()

    def update_mouse_pos_info(self, canvas_x, canvas_y):
        """Compute relevant mouse coord and pack them

        canvas_pos is the position inside the widget
        """
        # position of the cropped region inside the zoomed image
        #  mov_x = self._image_cropper._mov_x
        #  mov_y = self._image_cropper._mov_y

        # position inside the cropped region
        view_x = canvas_x - self._image_cropper.widget_shift_x
        view_y = canvas_y - self._image_cropper.widget_shift_y

        view_op = OrientedPoint(view_x, view_y, 0)
        abs_op = self.rescale_point(view_op, "view2abs")

        if self.abs2fm is None:
            fm_x, fm_y = 0, 0
            fm2_x, fm2_y = 0, 0
        else:
            fm_x, fm_y = apply_affine_transform(self.abs2fm, abs_op.x, abs_op.y)
            fm2_x, fm2_y = apply_affine_transform(self.fm2abs, abs_op.x, abs_op.y)

        curr_mouse_pos_info = {
            "view": (view_x, view_y),
            "abs": (abs_op.x, abs_op.y),
            "canvas": (canvas_x, canvas_y),
            "fm": (fm_x, fm_y),
        }
        self.curr_mouse_pos_info.set(curr_mouse_pos_info)

    ### FONT MEASUREMENTS ###

    def build_fm_lines_abs(self, input_type, start_vx, start_vy, end_vx, end_vy):
        """Build the font measurement line

        Given the current values of mouse pos and the start_pos, compute the
        new fm_lines_abs
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_fm_lines_abs")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('build_fm_lines_abs')} type {input_type}")

        if math.isclose(start_vx, end_vx) and math.isclose(start_vy, end_vy):
            recap = f"{fmt_cn('Coincident', 'alert')} points"
            recap += f" ({start_vx}, {start_vy}) ({end_vx}, {end_vy})"
            logg.warn(recap)
            return

        if input_type == "base_mean":
            vert_pt_view = line_curve_point(start_vx, start_vy, end_vx, end_vy)
            base_pt_view = OrientedPoint(start_vx, start_vy, vert_pt_view.ori_deg + 90)
            mean_pt_view = OrientedPoint(end_vx, end_vy, vert_pt_view.ori_deg + 90)

            logg.trace(f"base_point: {base_pt_view} vert_point: {vert_pt_view}")

            dist_base_mean = dist2D(base_pt_view, mean_pt_view)

            dist_base_ascent = dist_base_mean * (1 + self.prop_mean_ascent)
            ascent_pt_view = translate_point_dir(
                base_pt_view, vert_pt_view.ori_deg, dist_base_ascent
            )
            dist_desc_base = dist_base_mean * self.prop_desc_base
            descent_pt_view = translate_point_dir(
                base_pt_view, vert_pt_view.ori_deg, -dist_desc_base
            )

        # these are in VIEWING coord
        fm_lines_view = {
            "vert_point": vert_pt_view,
            "base_point": base_pt_view,
            "mean_point": mean_pt_view,
            "ascent_point": ascent_pt_view,
            "descent_point": descent_pt_view,
        }
        # rescale them to ABSOLUTE
        fm_lines_abs = self.rescale_fm_lines_to_abs(fm_lines_view)
        # save them
        self.fm_lines_abs.set(fm_lines_abs)

        # compute the affine transform fm-abs
        base_pt_abs = fm_lines_abs["base_point"]
        mean_pt_abs = fm_lines_abs["mean_point"]
        # distance from base to mean point in abs units
        dist_base_mean = dist2D(base_pt_abs, mean_pt_abs)
        # the length of the fm basis vectors in abs coord
        basis_length = dist_base_mean / self.normalized_dist_base_mean

        self.fm2abs, self.abs2fm = compute_affine_transform(base_pt_abs, basis_length)

    def adjust_fm_lines(self, source, adjust_type=None):
        """TODO: what is adjust_fm_lines doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.adjust_fm_lines")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('adjust_fm_lines')} {source}")

        fm_lines_abs = self.fm_lines_abs.get()

        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the FM lines before adjusting them")
            return

        base_pt_abs = fm_lines_abs["base_point"]
        mean_pt_abs = fm_lines_abs["mean_point"]

        current_state = self.state.get()

        # use the mouse release pos to set the FM
        if source == "mouse_release":
            if current_state == "adjusting_base":
                # get the mean point in view coord
                mean_view_op = self.rescale_point(mean_pt_abs, "abs2view")
                # the base point is the released one
                self.build_fm_lines_abs(
                    "base_mean",
                    self.end_view_x,
                    self.end_view_y,
                    mean_view_op.x,
                    mean_view_op.y,
                )
            elif current_state == "adjusting_mean":
                # get the base point in view coord
                base_view_op = self.rescale_point(base_pt_abs, "abs2view")
                # the mean point is the released one
                self.build_fm_lines_abs(
                    "base_mean",
                    base_view_op.x,
                    base_view_op.y,
                    self.end_view_x,
                    self.end_view_y,
                )

            else:
                logg.warn(f"{fmt_cn('Unrecognized', 'alert')} state {current_state}")
                return

        elif source == "adjust_btn":
            # check that we are shifting
            if adjust_type in self.adjust_shift:
                dx, dy = self.adjust_shift[adjust_type]
            else:
                logg.warn(f"{fmt_cn('Cannot', 'warn')} rotate a FM")
                return

            if current_state == "adjusting_base":
                new_base_abs_op = OrientedPoint(
                    base_pt_abs.x + dx, base_pt_abs.y + dy, 0
                )
                new_base_view_op = self.rescale_point(new_base_abs_op, "abs2view")
                mean_view_op = self.rescale_point(mean_pt_abs, "abs2view")
                self.build_fm_lines_abs(
                    "base_mean",
                    new_base_view_op.x,
                    new_base_view_op.y,
                    mean_view_op.x,
                    mean_view_op.y,
                )
            elif current_state == "adjusting_mean":
                base_view_op = self.rescale_point(base_pt_abs, "abs2view")
                new_mean_abs_op = OrientedPoint(
                    mean_pt_abs.x + dx, mean_pt_abs.y + dy, 0
                )
                new_mean_view_op = self.rescale_point(new_mean_abs_op, "abs2view")
                self.build_fm_lines_abs(
                    "base_mean",
                    base_view_op.x,
                    base_view_op.y,
                    new_mean_view_op.x,
                    new_mean_view_op.y,
                )

            else:
                logg.warn(f"{fmt_cn('Unrecognized', 'alert')} state {current_state}")
                return

        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} source {source}")
            return

        # update the fm_lines_view with the current abs/mov/zoom
        self.recompute_fm_lines_view()
        # update the thick_segment_points now that FM are available
        self.update_thick_segments()

    def recompute_fm_lines_view(self):
        """Updates the value in fm_lines_view to match the current abs/mov/zoom
        """
        curr_abs_lines = self.fm_lines_abs.get()
        if curr_abs_lines is not None:
            new_view_lines = self.rescale_fm_lines_to_view(curr_abs_lines)
            self.fm_lines_view.set(new_view_lines)

    def rescale_fm_lines_to_abs(self, fm_lines_view):
        """Rescale the fm points from VIEWING coord to ABSOLUTE img coord

        Returns a new dict of points
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.rescale_fm_lines_to_abs")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('rescale_fm_lines_to_abs')}")

        abs_lines = {}
        for line_name in fm_lines_view:
            abs_point = self.rescale_point(fm_lines_view[line_name], "view2abs")
            abs_lines[line_name] = abs_point
        return abs_lines

    def rescale_fm_lines_to_view(self, fm_lines_abs):
        """Rescale the fm points from ABSOLUTE img coord to VIEWING coord
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.rescale_fm_lines_to_view")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('rescale_fm_lines_to_view')}")

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
        logg.trace(f"Start {fmt_cn('rescale_point')}")

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

            - to the dict path_SP
            - update the selected_spid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.add_spline_point")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('add_spline_point')}")

        if (
            self.start_view_x < 0
            or self.start_view_y < 0
            or self.start_view_x > self._image_cropper.zoom_wid
            or self.start_view_y > self._image_cropper.zoom_hei
        ):
            logg.info(f"Point {fmt_cn('outside', 'warn')} image, ignored")
            return

        view_op = line_curve_point(
            self.start_view_x, self.start_view_y, self.move_view_x, self.move_view_y
        )

        # MAYBE add button to flip this behaviour
        # flip this to draw spline orientation in the other direction
        view_op.set_ori_deg(view_op.ori_deg + 180)

        # RESCALE the point from view to absolute coordinates
        abs_op = self.rescale_point(view_op, "view2abs")

        # add the point in path/all_SP
        self.add_spline_abs_point(abs_op)

    def add_spline_abs_point(self, abs_op):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.add_spline_abs_point")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('add_spline_abs_point')}")

        # create the SplinePoint
        new_sp = SplinePoint(abs_op.x, abs_op.y, abs_op.ori_deg, self.next_spid)
        logg.debug(f"id(new_sp): {id(new_sp)}")

        # save the point
        all_SP = self.all_SP.get()
        all_SP[new_sp.spid] = new_sp
        self.all_SP.set(all_SP)

        # put the point in the active ones
        path = self.path_SP.get()
        path[self.selected_indexes[0]].insert(self.selected_indexes[1] + 1, new_sp.spid)
        self.selected_indexes[1] += 1
        self.path_SP.set(path)

        # update the segment holder
        self.spline_segment_holder.update_data(all_SP, path)
        # update the visible segments
        self.compute_visible_segment_points()

        # update the thick_segment_points
        self.update_thick_segments()

        # update the id of the selected SP
        self.selected_spid_SP.set(new_sp.spid)

        # prepare for the next spid
        self.next_spid += 1
        logg.info(f"There are now {self.next_spid} SplinePoint")

        # reset the header
        self.selected_header_SP.set(None)

        self.compute_visible_spline_points()

    def compute_visible_spline_points(self):
        """Transform the points in view coord and send the visible one
        """
        logg = logging.getLogger(
            f"c.{__class__.__name__}.compute_visible_spline_points"
        )
        logg.trace(f"Start {fmt_cn('compute_visible_spline_points')}")

        # region showed in the view, in abs image coordinate
        region = self._image_cropper.region

        all_SP = self.all_SP.get()
        visible_SP = {}
        selected_spid_SP = self.selected_spid_SP.get()

        # for hid, glyph in enumerate(self.path_SP.get()):
        #     for spid in glyph:
        for hid, _, spid in enumerate_double_list(self.path_SP.get()):
            curr_sp = all_SP[spid]

            # check that the point is in the region cropped
            if region[0] < curr_sp.x < region[2] and region[1] < curr_sp.y < region[3]:
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

    def find_spid_in_path_SP(self, spid):
        """Find the indexes of the given spid in the path
        """
        for i, j, sp in enumerate_double_list(self.path_SP.get()):
            if sp == spid:
                return [i, j]
        return [0, -1]

    def compute_visible_segment_points(self):
        """Transform the segment points in view coord and send the visible one
        """
        logg = logging.getLogger(
            f"c.{__class__.__name__}.compute_visible_segment_points"
        )
        # logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('compute_visible_segment_points')}")

        full_path = list(iterate_double_list(self.path_SP.get()))

        if len(full_path) == 0 or len(full_path) == 1:
            self.visible_segment_SP.set([])
            return

        # region showed in the view, in abs image coordinate
        region = self._image_cropper.region
        all_SP = self.all_SP.get()

        # list of lists, each containing
        visible_points = []

        path = self.path_SP.get()

        for glyph in path:
            if len(glyph) <= 1:
                logg.trace(f"Skip this glyph")
                continue

            spid0 = glyph[0]
            for spid1 in glyph[1:]:
                pair = (spid0, spid1)
                logg.trace(f"Processing pair: {pair}")

                abs_p0 = all_SP[spid0]
                abs_p1 = all_SP[spid1]
                # check that at least one of the end of the segment is in view
                if (
                    region[0] < abs_p0.x < region[2]
                    and region[1] < abs_p0.y < region[3]
                ) or (
                    region[0] < abs_p1.x < region[2]
                    and region[1] < abs_p1.y < region[3]
                ):
                    # extract the points to draw the segment
                    seg_pts = self.spline_segment_holder.segments[pair]

                    # points of this segment visible
                    svp = []

                    for x, y in seg_pts:
                        # create a OrientedPoint to rescale to view
                        abs_op = OrientedPoint(x, y, 0)
                        view_op = self.rescale_point(abs_op, "abs2view")
                        svp.append(view_op)

                    visible_points.append(svp)

                # get ready for next iteration
                spid0 = spid1

        self.visible_segment_SP.set(visible_points)

    def update_thick_segments(self):
        """TODO: what is update_thick_segments doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_thick_segments")
        # logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('update_thick_segments')}")

        if self.abs2fm is None:
            return

        full_path = list(iterate_double_list(self.path_SP.get()))
        if len(full_path) == 0 or len(full_path) == 1:
            self.thick_segment_points.set([[], []])
            return

        all_fm = {}
        all_SP = self.all_SP.get()
        path = self.path_SP.get()
        fm_lines_abs = self.fm_lines_abs.get()
        base_point_abs = fm_lines_abs["base_point"]

        for spid in full_path:
            abs_pt = all_SP[spid]
            # find the coord of the point in fm frame
            fm_x, fm_y = apply_affine_transform(self.abs2fm, abs_pt.x, abs_pt.y)
            fm_ori_deg = -abs_pt.ori_deg + base_point_abs.ori_deg
            # create the OrientedPoint to normalize the angle
            fm_op = OrientedPoint(fm_x, fm_y, fm_ori_deg)
            all_fm[spid] = fm_op

        logg.trace(f"all_fm: {all_fm}")
        logg.trace(f"path: {path}")

        # TODO fix compute_thick_spline
        # TODO when drawing FM lines, call this
        self.spline_thick_holder.update_data(all_fm, path)

        # in the dict self.spline_thick_holder.segments[pair] = [(x0, y0), (x1, y1), ...]

        all_fm_x = []
        all_fm_y = []

        for glyph in path:
            if len(glyph) <= 1:
                logg.trace(f"Skip this glyph")
                continue

            spid0 = glyph[0]
            for spid1 in glyph[1:]:
                pair = (spid0, spid1)
                segment_points = self.spline_thick_holder.segments[pair]

                for fm_op in segment_points:
                    all_fm_x.append(fm_op[0])
                    all_fm_y.append(fm_op[1])

                spid0 = spid1

        self.thick_segment_points.set((all_fm_x, all_fm_y))

    def sp_frame_entered(self, spid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_entered')}")

        # save the id of the point that the mouse is hovering
        self.hovered_SP = spid

        self.compute_visible_spline_points()

    def sp_frame_left(self, spid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_left')}")

        # reset the id
        self.hovered_SP = -1

        self.compute_visible_spline_points()

    def sp_frame_btn1_pressed(self, spid):
        """React to mouse button 1 pressed on the FrameSPoint with id spid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_btn1_pressed")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('sp_frame_btn1_pressed')} {spid}")

        # if the state is moving glyph, start the movement and reset the state
        if self.state.get() == "moving_glyph":
            self.move_glyph("clicked_point", spid)
            self.state.set("free")
            return

        # else, set this point as selected and update the model

        self.selected_indexes = self.find_spid_in_path_SP(spid)
        logg.debug(f"selected_indexes: {self.selected_indexes}")

        logg.debug(f"self.path_SP.get(): {self.path_SP.get()}")

        # highlight point
        self.selected_spid_SP.set(spid)

        # remove highlight from header
        self.selected_header_SP.set(None)

        # recompute colors
        self.compute_visible_spline_points()

    def sp_header_entered(self, hid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_entered')}")

        # save the id of the point that the mouse is hovering
        self.hovered_header_SP = hid

        self.compute_visible_spline_points()

    def sp_header_left(self, hid):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_left')}")

        # reset the id
        self.hovered_header_SP = -1

        self.compute_visible_spline_points()

    def sp_header_btn1_pressed(self, hid):
        """React to mouse button 1 pressed on the header with id hid
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_btn1_pressed")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('sp_header_btn1_pressed')} {hid}")

        # remove highlight from point
        self.selected_spid_SP.set(None)

        # tell the view to highlight this header
        self.selected_header_SP.set(hid)

        # set the indexes to point before the first point in the clicked glyph
        self.selected_indexes = [hid, -1]
        logg.debug(f"self.selected_indexes: {self.selected_indexes}")

        # redraw the visible points: now no one will be highlighted
        self.compute_visible_spline_points()

    def translate_glyph(self, glyph_idx, dx, dy):
        """Translate all the points in a glyph
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.translate_glyph")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('translate_glyph')}")
        logg.debug(f"glyph_idx: {glyph_idx} dx: {dx} dy: {dy}")

        all_SP = self.all_SP.get()
        for spid in self.path_SP.get()[glyph_idx]:
            all_SP[spid].translate(dx, dy)
        self.all_SP.set(all_SP)

    def move_glyph(self, source, clicked_spid=None):
        """TODO: what is move_glyph doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.move_glyph")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('move_glyph')} {source}")

        all_SP = self.all_SP.get()
        selected_spid_SP = self.selected_spid_SP.get()
        sel_idxs = self.selected_indexes

        # check that the current selected_spid_SP is valid
        if selected_spid_SP not in all_SP:
            logg.warn(f"{fmt_cn('No glyph', 'alert')} to move")
            return

        # get the current selected point
        curr_abs_sp = all_SP[selected_spid_SP]

        # move the currently selected point to where the mouse was released
        if source == "mouse_release":
            # the released point is in view coordinate
            release_view_op = OrientedPoint(self.end_view_x, self.end_view_y, 0)
            # convert it to abs
            release_abs_op = self.rescale_point(release_view_op, "view2abs")
            # and compute the delta in abs coord to shift the glyph
            dx_abs = release_abs_op.x - curr_abs_sp.x
            dy_abs = release_abs_op.y - curr_abs_sp.y
            self.translate_glyph(sel_idxs[0], dx_abs, dy_abs)

        # move the currently selected point to the clicked point position
        elif source == "clicked_point":
            clicked_abs_sp = all_SP[clicked_spid]
            dx_abs = clicked_abs_sp.x - curr_abs_sp.x
            dy_abs = clicked_abs_sp.y - curr_abs_sp.y
            self.translate_glyph(sel_idxs[0], dx_abs, dy_abs)

        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} source {source}")
            return

        # update the visible spline points
        self.compute_visible_spline_points()
        # update the segment holder
        self.spline_segment_holder.update_data(self.all_SP.get(), self.path_SP.get())
        # update the visible segments
        self.compute_visible_segment_points()
        # update the thick spline
        self.update_thick_segments()
