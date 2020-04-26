import logging
import numpy as np
import math

from copy import deepcopy
from timeit import default_timer as timer

from cursive_writer.spliner.spliner import compute_aligned_cubic_segment
from cursive_writer.spliner.spliner import compute_aligned_glyph
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils.geometric_utils import slope2deg
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.geometric_utils import translate_spline_sequence


def find_lower_tangent(l_x_as, l_y_as, r_x_as, r_y_as, r_yp_as):
    """Finds a line tangent to both curves

    The curvature of the right curve is automatically extrapolated

    l_x_as: x aligned sample of left curve
    l_y_as: y values of left curve
    r_x_as: x aligned sample of right curve
    r_y_as: y values of right curve
    r_yp_as: first derivative values of right curve

    Returns:
    l_xid: index, in l_x_as, of the contact point
    r_xid: index, in r_x_as, of the contact point
    l_tang_y_as: sample of the tangent on l_x_as
    tangent_time: time elapsed to check tangents
    """
    # logg = logging.getLogger(f"c.{__name__}.find_lower_tangent")
    # logg.debug(f"Start find_lower_tangent")

    # compute the second derivative
    r_ypp = r_yp_as[1:] - r_yp_as[:-1]
    mean_r_ypp = np.mean(r_ypp)

    # logg.debug(f"r_yp_as: {r_yp_as}")
    # logg.debug(f"r_ypp: {r_ypp}")

    if mean_r_ypp >= 0:
        # logg.debug(f"ypp positive")
        range_xid = range(r_x_as.shape[0])
    else:
        # logg.debug(f"ypp negative")
        range_xid = range(r_x_as.shape[0])[::-1]

    tangent_start = timer()
    for xid in range_xid:
        # point tangent to the *right* segment
        tang_op = OrientedPoint(r_x_as[xid], r_y_as[xid], slope2deg(r_yp_as[xid]))
        tang_coeff = tang_op.to_ab_line()

        # sample it on the *left* segment sample
        l_tang_y_as = poly_model(l_x_as, tang_coeff, flip_coeff=True)
        # ax.plot(l_x_as, l_tang_y_as, color="b", ls="-", marker="")
        # ax.plot(l_x_as, l_tang_y_as, color="b", ls="", marker=".")

        # find if the left segment has some points lower than the tangent
        lower = l_y_as < l_tang_y_as
        # logg.debug(f"lower: {lower} {np.sum(lower)}")
        if np.sum(lower) == 0:
            # logg.debug(f"Breaking at xid: {xid}")
            break

    tangent_end = timer()
    tangent_time = tangent_end - tangent_start
    # logg.debug(f"Time to find tangent: {tangent_end - tangent_start:.6f}")

    # find distance from left segment to tangent
    dist_left_tangent = l_y_as - l_tang_y_as
    min_dist_left_tangent = np.min(dist_left_tangent)
    argmin_dist_left_tangent = np.argmin(dist_left_tangent)
    recap = f"min_dist_left_tangent: {min_dist_left_tangent:.6f}"
    recap += " argmin_dist_left_tangent: {argmin_dist_left_tangent}"
    # logg.debug(recap)

    if min_dist_left_tangent < 0:
        # logg.debug(f"Tangent not found")
        return -1, -1, None, tangent_time

    l_xid = argmin_dist_left_tangent
    r_xid = xid

    return l_xid, r_xid, l_tang_y_as, tangent_time


def find_best_shift(l_x_as, l_y_as, l_yp_as, r_x_orig_as, r_y_as, r_yp_as, x_stride):
    """Finds the best shift to align two curves

    l_x_as: x aligned sample of left curve
    l_y_as: y values of left curve
    l_yp_as: first derivative values of left curve
    r_x_orig_as: x aligned sample of right curve
    r_y_as: y values of right curve
    r_yp_as: first derivative values of right curve
    x_stride: stride of the alignement

    Returns:
    best_shift: the best shift to apply to the right curve
    best_r_x_as: the best x aligned sample of the right curve
    best_l_tang_y_as: sample of the best tangent on l_x_as
    l_id_s_x: if of the last x to keep in the left curve
    r_id_s_x: if of the last x to keep in the right curve
    l_p_ext: the left extended contact point
    r_p_ext: the right extended contact point
    ext_x_as: aligned x sample of the connecting segment
    ext_y_as: y values of the connecting segment
    """
    logg = logging.getLogger(f"c.{__name__}.find_best_shift")
    # logg.debug(f"Start find_best_shift")

    shift_start = timer()

    # find how much the right segment can shift
    shift_11 = l_x_as[-1] - r_x_orig_as[-1] - (l_x_as[-1] - l_x_as[0]) / 2
    shift_10 = l_x_as[-1] - r_x_orig_as[0]
    # align the shift on the stride grid: now if you sum the shift to l_x_as
    # the points are still aligned.
    shift_a_11 = math.floor(shift_11 / x_stride) * x_stride
    shift_a_10 = math.ceil(shift_10 / x_stride) * x_stride
    shift_range = np.arange(shift_a_11, shift_a_10 + x_stride / 2, x_stride)
    # recap = f"shift_11: {shift_11} shift_10: {shift_10}"
    # recap += f" shift_a_11: {shift_a_11} shift_a_10: {shift_a_10}"
    # logg.debug(recap)

    best_dist_x_touch = float("inf")
    best_shift = None
    best_r_x_as = None
    best_l_tang_y_as = None

    tangent_times = []

    for shift in shift_range:
        r_x_as = r_x_orig_as + shift
        # logg.debug(f"\nNew shift r_x_as[0]: {r_x_as[0]} r_x_as[-1]: {r_x_as[-1]}")

        # ax.plot(r_x_as, r_y_as, color="y", ls="-", marker="")
        # ax.plot(r_x_as, r_y_as, color="y", ls="", marker=".")

        # find the indexes where the tangent touches the curves
        l_xid, r_xid, l_tang_y_as, tangent_time = find_lower_tangent(
            l_x_as, l_y_as, r_x_as, r_y_as, r_yp_as
        )

        tangent_times.append(tangent_time)

        if l_xid == -1:
            # logg.debug(f"Tangent not found")
            continue

        # find where the tangent touches the segments
        l_x_touch = l_x_as[l_xid]
        r_x_touch = r_x_as[r_xid]

        if r_x_touch < l_x_touch:
            # logg.debug(f"Tangent goes the wrong way")
            continue

        # compute how far are the two contacts
        dist_x_touch = r_x_touch - l_x_touch

        # if this shift does not improve the distance, go to the next
        if dist_x_touch >= best_dist_x_touch:
            continue

        # save info about the current shift
        best_dist_x_touch = dist_x_touch
        best_shift = shift
        best_r_x_as = r_x_as
        best_l_tang_y_as = l_tang_y_as

        # extend the points of contact
        best_l_x_ext = l_x_touch - dist_x_touch / 2
        best_r_x_ext = r_x_touch + dist_x_touch / 2
        # recap = f"l_x_touch: {l_x_touch:.4f} r_x_touch {r_x_touch:.4f}"
        # recap += f" dist_x_touch: {dist_x_touch:.4f}"
        # recap += f" best_l_x_ext: {best_l_x_ext:.4f} best_r_x_ext {best_r_x_ext:.4f}"
        # logg.debug(recap)

    tangent_time_mean = sum(tangent_times) / len(tangent_times)
    logg.debug(f"Mean tangent time: {tangent_time_mean:.6f}")

    # extract the best value as current (r_x_as = r_x_orig_as + best_shift)
    r_x_as = best_r_x_as

    # find the index of the touch point on the left segment
    l_lower_x = l_x_as < best_l_x_ext
    # argmin returns the *first* occurrence of the min value
    l_id_e_x = np.argmin(l_lower_x)
    # for symmetry, if we can, we keep the previous index (the last of the True)
    if l_id_e_x > 0:
        l_id_e_x -= 1

    # find the index of the touch point on the right segment
    r_lower_x = r_x_as < best_r_x_ext
    r_id_e_x = np.argmin(r_lower_x)

    # recap = f"l_id_e_x: {l_id_e_x}"
    # recap += f" l_x_as[l_id_e_x]: {l_x_as[l_id_e_x]:.4f}"
    # recap += f" r_id_e_x: {r_id_e_x}"
    # recap += f" r_x_as[r_id_e_x]: {r_x_as[r_id_e_x]:.4f}"
    # logg.debug(recap)

    # find the extended contact point
    l_p_ext = OrientedPoint(
        l_x_as[l_id_e_x], l_y_as[l_id_e_x], slope2deg(l_yp_as[l_id_e_x])
    )
    r_p_ext = OrientedPoint(
        r_x_as[r_id_e_x], r_y_as[r_id_e_x], slope2deg(r_yp_as[r_id_e_x])
    )
    _, ext_x_as, ext_y_as, _ = compute_aligned_cubic_segment(
        l_p_ext, r_p_ext, x_stride,
    )

    # recap = f"l_id_e_x: {l_id_e_x}"
    # recap += f" l_x_as[l_id_e_x]: {l_x_as[l_id_e_x]:.4f}"
    # recap += f" ext_x_as[0]: {ext_x_as[0]:.4f}"
    # recap += f" ext_x_as[-1]: {ext_x_as[-1]:.4f}"
    # recap += f" r_id_e_x: {r_id_e_x}"
    # recap += f" r_x_as[r_id_e_x]: {r_x_as[r_id_e_x]:.4f}"
    # logg.debug(recap)

    # show id to use when plotting
    l_id_s_x = l_id_e_x
    r_id_s_x = r_id_e_x

    # fix the ext ids, there is a gap of 1 (one) stride missing on one side
    if not math.isclose(l_x_as[l_id_e_x], ext_x_as[0]):
        logg.debug(f"Left not close")
        # check that is not the last
        if l_id_e_x < l_x_as.shape[0] - 1:
            l_id_s_x = l_id_e_x + 1

    if not math.isclose(r_x_as[r_id_e_x], ext_x_as[-1]):
        logg.debug(f"Right not close")
        # check that is not the first
        if r_id_e_x > 0:
            r_id_s_x = r_id_e_x - 1

    shift_end = timer()
    logg.debug(f"Time to find optimal shift: {shift_end - shift_start:.6f}")

    return (
        best_shift,
        best_r_x_as,
        best_l_tang_y_as,
        l_id_s_x,
        r_id_s_x,
        l_p_ext,
        r_p_ext,
        ext_x_as,
        ext_y_as,
    )


def align_letter_1(spline_sequence_l, spline_sequence_r, x_stride):
    """TODO: what is align_letter_1 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.align_letter_1")
    # logg.debug(f"Start align_letter_1")

    # extract the last and the first glyphs in the two letters
    # gly_seq_l = spline_sequence_l[-1]
    # gly_seq_r = spline_sequence_r[0]
    gly_seq_l = deepcopy(spline_sequence_l[-1])
    gly_seq_r = deepcopy(spline_sequence_r[0])

    # compute the data for the left and right glyph
    _, l_x_as, l_y_as, l_yp_as = compute_aligned_glyph(gly_seq_l, x_stride)
    _, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_glyph(gly_seq_r, x_stride)

    (best_shift, _, _, _, _, l_p_ext, r_p_ext, _, _,) = find_best_shift(
        l_x_as, l_y_as, l_yp_as, r_x_orig_as, r_y_as, r_yp_as, x_stride
    )
    # logg.debug(f"best_shift: {best_shift}")

    # find where to chop the left glyph, at the last point left to l_p_ext
    for l_p_id, op in enumerate(gly_seq_l):
        if op.x >= l_p_ext.x:
            break
    # l_p_id is the first that is right of l_p_ext, the slice *excludes* it
    gly_chop_l = gly_seq_l[:l_p_id]

    # find where to chop the right glyph, at the first point right of r_p_ext
    for r_p_id, op in enumerate(gly_seq_r):
        if op.x > r_p_ext.x:
            break
    # r_p_id is the first that is right of r_p_ext, the slice *includes* it
    gly_chop_r = gly_seq_r[r_p_id:]
    translate_spline_sequence([gly_chop_r], best_shift, 0)

    # build the connecting glyph
    gly_seq_con = [gly_chop_l[-1], l_p_ext, r_p_ext, gly_chop_r[0]]
    spline_sequence_con = [gly_seq_con]

    return spline_sequence_con, gly_chop_l, gly_chop_r, best_shift


def align_letter_2(spline_sequence_l, spline_sequence_r, x_stride):
    """TODO: what is align_letter_2 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.align_letter_2")
    # logg.debug(f"Start align_letter_2")

    # extract the last and the first glyphs in the two letters
    gly_seq_l = spline_sequence_l[-1]
    gly_seq_r = spline_sequence_r[0]

    # compute the data for the left and right glyph
    _, l_x_as, l_y_as, l_yp_as = compute_aligned_glyph(gly_seq_l, x_stride)
    _, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_glyph(gly_seq_r, x_stride)

    # build a point oriented like r_first_op on l_last_op
    r_first_op_ori_deg = slope2deg(r_yp_as[0])
    l_line_op = OrientedPoint(l_x_as[-1], l_y_as[-1], r_first_op_ori_deg)
    a, b = l_line_op.to_ab_line()

    # the x value of r_first_op.y along l_line_op
    x_shift_r_first = (r_y_as[0] - b) / a
    r_x_shift = x_shift_r_first - r_x_orig_as[0]
    r_x_shift_al = math.floor(r_x_shift / x_stride) * x_stride

    # create the OrientedPoint for the ligature
    l_last_op_ori_deg = slope2deg(l_yp_as[-1])
    l_last_op = OrientedPoint(l_x_as[-1], l_y_as[-1], l_last_op_ori_deg)
    # r_first_op = OrientedPoint(r_x_as[0], r_y_as[0], r_first_op_ori_deg)
    r_first_op = OrientedPoint(
        r_x_orig_as[0] + r_x_shift_al, r_y_as[0], r_first_op_ori_deg
    )

    # build the connecting glyph
    gly_seq_con = [l_last_op, r_first_op]
    spline_sequence_con = [gly_seq_con]

    return spline_sequence_con, r_x_shift_al, (a, b)
