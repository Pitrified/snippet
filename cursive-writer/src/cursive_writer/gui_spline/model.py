import logging
import numpy as np
from math import cos
from math import sin
from pathlib import Path

from tkinter import filedialog

from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import apply_affine_transform
from cursive_writer.utils.geometric_utils import compute_affine_transform
from cursive_writer.utils.geometric_utils import dist2D
from cursive_writer.utils.geometric_utils import line_curve_point
from cursive_writer.utils.geometric_utils import translate_point_dir
from cursive_writer.utils.image_cropper import ImageCropper
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.spline_point import SplinePoint
from cursive_writer.utils.utils import enumerate_double_list
from cursive_writer.utils.utils import iterate_double_list
from cursive_writer.utils.utils import find_free_index
from cursive_writer.utils.observable import Observable
from cursive_writer.utils.spline_segment_holder import SplineSegmentHolder


class Model:
    def __init__(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        # full path of the current image
        self.pf_input_image = Observable()
        # Path to the folder to save the spline in
        self.path_out_folder = None

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
        # list of lists with segment points
        self.visible_segment_SP = Observable()

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
                self.build_fm_lines_abs("base_mean")
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
            - adjust baseline
            - create new point
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
                self.build_fm_lines_abs("base_mean")
                # update the fm_lines_view with the current abs/mov/zoom
                self.recompute_fm_lines_view()

                # after you release the mouse, go back to free state
                self.state.set("free")

        # handle right click
        elif click_type == "right_click":
            if current_state == "free_clicked_right":
                # move the image
                self.move_image(self.end_view_x, self.end_view_y)
                # go back to free state
                self.state.set("free")

        # very weird things
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} click_type {click_type}")

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

        # the selected is not the first
        if sel_idxs[0] > 0:
            # the previous is emptry
            if len(path[sel_idxs[0] - 1]) == 0:
                logg.info(f"Previous glyph is {fmt_cn('empty', 'warn')}")
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

        if self.selected_indexes[1] == -1:
            logg.warn(f"{fmt_cn('Cannot', 'warn')} move a glyph")
            return

        all_SP = self.all_SP.get()
        sel_pt = all_SP[self.selected_spid_SP.get()]

        shift = 0.1
        very_shift = 1
        rot = 0.1
        very_rot = 1

        if adjust_type == "vl":
            sel_pt.translate(-very_shift, 0)
        elif adjust_type == "l":
            sel_pt.translate(-shift, 0)
        elif adjust_type == "r":
            sel_pt.translate(shift, 0)
        elif adjust_type == "vr":
            sel_pt.translate(very_shift, 0)
        elif adjust_type == "vb":
            sel_pt.translate(0, very_shift)
        elif adjust_type == "b":
            sel_pt.translate(0, shift)
        elif adjust_type == "u":
            sel_pt.translate(0, -shift)
        elif adjust_type == "vu":
            sel_pt.translate(0, -very_shift)
        elif adjust_type == "va":
            sel_pt.rotate(-very_rot)
        elif adjust_type == "a":
            sel_pt.rotate(-rot)
        elif adjust_type == "o":
            sel_pt.rotate(rot)
        elif adjust_type == "vo":
            sel_pt.rotate(very_rot)

        all_SP[self.selected_spid_SP.get()] = sel_pt

        self.all_SP.set(all_SP)

        # update the segment holder
        self.spline_segment_holder.update_data(all_SP, self.path_SP.get())
        # update the visible segments
        self.compute_visible_segment_points()

        self.compute_visible_spline_points()

    def clicked_fs_btn_save_spline(self, glyph_root_name):
        """Save the spline points to file
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_save_spline")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fs_btn_save_spline', 'a2')}")

        if self.path_out_folder is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the output folder before saving")
            return

        if glyph_root_name == "":
            logg.warn(f"{fmt_cn('Set', 'alert')} the glyph root name before saving")
            return

        fm_lines_abs = self.fm_lines_abs.get()
        if fm_lines_abs is None:
            logg.warn(f"{fmt_cn('Set', 'alert')} the font measurements before saving")
            return

        if not self.path_out_folder.exists():
            self.path_out_folder.mkdir(parents=True)

        letter_name_fmt = f"{glyph_root_name}_{{:03d}}.txt"
        glyph_name_fmt = f"{glyph_root_name}_{{:03d}}_{{:03d}}.txt"
        logg.debug(f"letter_name_fmt {letter_name_fmt} glyph_name_fmt {glyph_name_fmt}")

        # get the first free file index glyph_root_name_NNN.txt
        file_index = find_free_index(self.path_out_folder, letter_name_fmt)

        # full path to the letter recap file
        letter_name = self.path_out_folder / letter_name_fmt.format(file_index)
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
            full_glyph_name = self.path_out_folder / glyph_name

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
                fm_pt = OrientedPoint(fm_x, fm_y, fm_ori_deg)
                gly_line = f"{fm_pt.x}\t{fm_pt.y}\t{fm_pt.ori_deg}\n"
                str_glyph += gly_line
            full_glyph_name.write_text(str_glyph)

        letter_name.write_text(all_glyphs)

    def clicked_fs_btn_set_save_path(self):
        """Set the output folder to save the spline into
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_set_save_path")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_fs_btn_set_save_path', 'a2')}")

        str_out_folder = filedialog.askdirectory()

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        if len(str_out_folder) == 0:
            logg.info(f"Selection of output_folder cancelled")
            return

        path_out_folder = Path(str_out_folder)
        logg.debug(f"path_out_folder: {path_out_folder}")

        self.path_out_folder = path_out_folder

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

    def build_fm_lines_abs(self, input_type):
        """Build the font measurement line

        Given the current values of mouse pos and the start_pos, compute the
        new fm_lines_abs
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_fm_lines_abs")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('build_fm_lines_abs')} type {input_type}")

        if input_type == "base_mean":
            vert_pt_view = line_curve_point(
                self.start_view_x, self.start_view_y, self.move_view_x, self.move_view_y
            )
            base_pt_view = OrientedPoint(
                self.start_view_x, self.start_view_y, vert_pt_view.ori_deg + 90
            )
            mean_pt_view = OrientedPoint(
                self.move_view_x, self.move_view_y, vert_pt_view.ori_deg + 90
            )

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

    def recompute_fm_lines_view(self):
        """Updats the value in fm_lines_view to match the current abs/mov/zoom
        """
        curr_abs_lines = self.fm_lines_abs.get()
        if not curr_abs_lines is None:
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
        logg.trace(f"Start {fmt_cn('compute_visible_segment_points', 'a2')}")

        full_path = list(iterate_double_list(self.path_SP.get()))

        if len(full_path) == 0 or len(full_path) == 1:
            self.visible_segment_SP.set([])
            return

        # region showed in the view, in abs image coordinate
        region = self._image_cropper.region
        all_SP = self.all_SP.get()

        # list of lists, each containing
        visible_points = []

        spid0 = full_path[0]
        for spid1 in full_path[1:]:
            pair = (spid0, spid1)
            logg.trace(f"Processing pair: {pair}")

            abs_p0 = all_SP[spid0]
            abs_p1 = all_SP[spid1]
            # check that at least one of the end of the segment is in view
            if (
                region[0] < abs_p0.x < region[2] and region[1] < abs_p0.y < region[3]
            ) or (
                region[0] < abs_p1.x < region[2] and region[1] < abs_p1.y < region[3]
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
