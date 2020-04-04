import argparse
import logging
import numpy as np
import math

from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.geometric_utils import rotate_point
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils import plot_utils


def translate_points_to_origin(p0, p1):
    """Translate to the origin and rotate the oriented points to have both on the x axis

    Returns 
        - two *new* OrientedPoint on the x axis, with ori_deg rotated
        - the direction from p0 to p1 in the original frame
    """
    logg = logging.getLogger(f"c.{__name__}.translate_points_to_origin")
    logg.setLevel("TRACE")
    logg.trace(f"Starting translate_points_to_origin")

    # direction from point 0 to 1
    dir_01 = math.degrees(math.atan2(p1.y - p0.y, p1.x - p0.x))
    logg.trace(f"dir_01: {dir_01}")

    # rotate the point and translate them in the origin
    rot_p0 = OrientedPoint(0, 0, p0.ori_deg - dir_01)

    # tranlsate p1 towards origin by p0
    tran_p1x = p1.x - p0.x
    tran_p1y = p1.y - p0.y
    # rotate p1 position by dir_01
    rototran_p1 = rotate_point(np.array([tran_p1x, tran_p1y]), dir_01)
    rot_p1 = OrientedPoint(rototran_p1[0], rototran_p1[1], p1.ori_deg - dir_01)
    logg.trace(f"rot_p0: {rot_p0} rot_p1: {rot_p1}")

    return rot_p0, rot_p1, dir_01


def rototranslate_points(x_sample, y_segment, offset_angle, offset_x, offset_y):
    """Rototranslate the 2d points [x_sample, y_segment]

    Apply first the rotation by offset_angle, then the translation by
    (offset_x, offset_y)

    Returns two arrays with x and y values
    """
    logg = logging.getLogger(f"c.{__name__}.rototranslate_points")
    logg.setLevel("TRACE")
    logg.trace(f"Starting rototranslate_points")

    # rotate the points back
    all_segment = np.array([x_sample, y_segment]).transpose()
    logg.trace(f"all_segment.shape: {all_segment.shape}")
    rotated_segment = rotate_point(all_segment, offset_angle)
    logg.trace(f"rotated_segment.shape: {rotated_segment.shape}")

    # translate them
    tran_segment = rotated_segment + np.array([offset_x, offset_y])
    tran_segment = tran_segment.transpose()
    logg.trace(f"tran_segment.shape: {tran_segment.shape}")
    rototran_x = tran_segment[0]
    rototran_y = tran_segment[1]

    return rototran_x, rototran_y


def fit_line(p0, p1):
    """Find the coefficient for a line passing through two points

    y = ax + b
    """
    logg = logging.getLogger(f"c.{__name__}.fit_line")
    logg.setLevel("TRACE")
    logg.trace(f"Starting fit_line")

    a = (p1.y - p0.y) / (p1.x - p0.x)
    b = p0.y - a * p0.x

    logg.trace(f"y = {a:.4f}*x + {b:.4f}")

    return np.array([a, b])


def fit_cubic(p0, p1):
    """Find the coefficient for a cubic curve passing through two points

    Tangents are the slope of the curve on the point
    p0 = (x0, y0) with tangent y0p
    p1 = (x1, y1) with tangent y1p

    y = a*x^3 + b*x^2 + c*x + d
    y' = 3*a*x^2 + 2*b*x + c

    Small tangent change is suggested to avoid deep min/max between the points
    Both tangents should be smallish, in the [-1, 1] range
    """
    logg = logging.getLogger(f"c.{__name__}.fit_cubic")
    logg.setLevel("TRACE")
    logg.trace(f"Starting fit_cubic")

    x0 = p0.x
    y0 = p0.y
    y0p = p0.ori_slo
    x1 = p1.x
    y1 = p1.y
    y1p = p1.ori_slo

    A = np.array(
        [
            [x0 ** 3, x0 ** 2, x0, 1],
            [3 * x0 ** 2, 2 * x0 ** 1, 1, 0],
            [x1 ** 3, x1 ** 2, x1, 1],
            [3 * x1 ** 2, 2 * x1 ** 1, 1, 0],
        ]
    )
    b = np.array([y0, y0p, y1, y1p])
    # x are the coefficients of the curve
    x = np.linalg.solve(A, b)

    #  logg.trace(f"x: {x}")
    logg.trace(f"y = {x[0]:.4f}*x^3 + {x[1]:.4f}*x^2 + {x[2]:.4f}*x + {x[3]:.4f}")

    return x


def sample_segment_points(x_start, x_end, coeff):
    """Sample a poly_model in the [x_start, x_end] range on natural numbers
    """
    logg = logging.getLogger(f"c.{__name__}.sample_segment_points")
    logg.setLevel("TRACE")
    logg.trace(f"Starting sample_segment_points")

    if x_start > x_end:
        x_start, x_end = x_end, x_start

    # align x_start and x_end to grid step
    x_start_align = math.ceil(x_start)
    x_end_align = math.floor(x_end)
    logg.trace(f"x_start_align: {x_start_align} x_end_align: {x_end_align}")

    # sample from x_start_align to x_end_align included
    x_sample = np.arange(x_start_align, x_end_align + 1)
    logg.trace(f"x_sample.shape: {x_sample.shape}")
    #  logg.trace(f"x_sample: {x_sample}")

    y_segment = poly_model(x_sample, np.flip(coeff))
    return x_sample, y_segment


def compute_cubic_segment(p0, p1, ax=None):
    """Compute the cubic segment between two points

    * translate to the origin and rotate the points to have both on the x axis
    * compute the spline
    * rotate and translate to original position
    """
    logg = logging.getLogger(f"c.{__name__}.compute_cubic_segment")
    logg.setLevel("TRACE")
    logg.trace(f"Starting compute_cubic_segment")

    # translate and rotate the point to the origin
    rot_p0, rot_p1, dir_01 = translate_points_to_origin(p0, p1)

    # plot the rotated vectors
    if not ax is None:
        plot_utils.add_vector(rot_p0, ax, color="r")
        plot_utils.add_vector(rot_p1, ax, color="r")

    # compute the segment points
    coeff = fit_cubic(rot_p0, rot_p1)
    x_sample, y_segment = sample_segment_points(rot_p0.x, rot_p1.x, coeff)
    if not ax is None:
        ax.plot(x_sample, y_segment, color="g", ls="-", marker="")

    # rototranslate points to the original position
    rototran_x, rototran_y = rototranslate_points(
        x_sample, y_segment, -dir_01, p0.x, p0.y,
    )

    return rototran_x, rototran_y


def build_contour(
    p0t,
    p0b,
    p1t,
    p1b,
    coeff_l,
    coeff_r,
    x_sample_t,
    y_segment_t,
    x_sample_b,
    y_segment_b,
    ax,
):
    """TODO: Docstring for build_contour.

    :p0t: TODO
    :p0b: TODO
    :p1t: TODO
    :p1b: TODO
    :coeff_l: TODO
    :coeff_r: TODO
    :x_sample_t: TODO
    :y_segment_t: TODO
    :x_sample_b: TODO
    :y_segment_b: TODO
    :returns: TODO

    """
    logg = logging.getLogger(f"c.{__name__}.build_contour")
    logg.setLevel("TRACE")
    logg.trace(f"Starting build_contour")

    # regular case, no overlaps
    if p0t.x <= p1t.x and p0b.x <= p1b.x:
        # sample the whole line
        x_sample_l, y_segment_l = sample_segment_points(p0t.x, p0b.x, coeff_l)
        x_sample_r, y_segment_r = sample_segment_points(p1t.x, p1b.x, coeff_r)
        logg.trace(f"x_sample_l.shape: {x_sample_l.shape}")
        logg.trace(f"x_sample_r.shape: {x_sample_r.shape}")

        # plot everything to debug things
        if not ax is None:
            # plot left and right segments
            ax.plot(x_sample_l, y_segment_l, color="g", marker=".", ls="")
            ax.plot(x_sample_r, y_segment_r, color="g", marker=".", ls="")

        # /\
        if coeff_l[0] >= 0 and coeff_r[0] <= 0:
            logg.trace(f"/\ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_t, x_sample_r))
            contour_t = np.hstack((y_segment_l, y_segment_t, y_segment_r))
            contour_b = y_segment_b

        # //
        elif coeff_l[0] >= 0 and coeff_r[0] >= 0:
            logg.trace(f"// coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_t))
            contour_t = np.hstack((y_segment_l, y_segment_t))
            contour_b = np.hstack((y_segment_b, y_segment_r))

        # \\
        elif coeff_l[0] <= 0 and coeff_r[0] <= 0:
            logg.trace(f"\\\\ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_b))
            contour_t = np.hstack((y_segment_t, y_segment_r))
            contour_b = np.hstack((y_segment_l, y_segment_b))

        # \/
        elif coeff_l[0] <= 0 and coeff_r[0] >= 0:
            logg.trace(f"\\/ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_b, x_sample_r))
            contour_t = y_segment_t
            contour_b = np.hstack((y_segment_l, y_segment_b, y_segment_r))

        return contour_t, contour_b, x_sample

    # both ends of p1tb are left of p0bt, this should not happen
    elif p0t.x <= p1t.x and p0b.x <= p1b.x:
        # MAYBE call this again with them swapped
        raise ValueError(f"Swap the points and try again {p0t} {p0b} {p1t} {p1b}")

    # compute the intersection between the two lines
    # x = (b2-b1)/(a1-a2)
    i_x = (coeff_l[1] - coeff_r[1]) / (coeff_r[0] - coeff_l[0])
    i_y = coeff_l[0] * i_x + coeff_l[1]
    logg.trace(f"i_x: {i_x} i_y: {i_y}")

    # /\ // \\ type, keep the lower part
    if p0t.x > p1t.x and p0b.x <= p1b.x:
        # x_sample = 0
        # contour_t = 0
        # contour_b = 0
        x_sample_l, y_segment_l = sample_segment_points(p0b.x, i_x, coeff_l)
        x_sample_r, y_segment_r = sample_segment_points(p1b.x, i_x, coeff_r)

        # /\
        if coeff_l[0] >= 0 and coeff_r[0] <= 0:
            logg.trace(f"/\ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_r))
            contour_t = np.hstack((y_segment_l, y_segment_r))
            contour_b = y_segment_b

        # //
        elif coeff_l[0] >= 0 and coeff_r[0] >= 0:
            logg.trace(f"// coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l))
            contour_t = np.hstack((y_segment_l))
            contour_b = np.hstack((y_segment_b, y_segment_r))

        # \\
        elif coeff_l[0] <= 0 and coeff_r[0] <= 0:
            logg.trace(f"\\\\ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_r))
            contour_t = np.hstack((y_segment_r))
            contour_b = np.hstack((y_segment_l, y_segment_b))

    # \/ // \\ type, keep the upper part
    elif p0t.x <= p1t.x and p0b.x > p1b.x:
        # x_sample = 0
        # contour_t = 0
        # contour_b = 0
        x_sample_l, y_segment_l = sample_segment_points(p0t.x, i_x, coeff_l)
        x_sample_r, y_segment_r = sample_segment_points(p1t.x, i_x, coeff_r)

        # //
        if coeff_l[0] >= 0 and coeff_r[0] >= 0:
            logg.trace(f"// coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_t))
            contour_t = np.hstack((y_segment_l, y_segment_t))
            contour_b = np.hstack((y_segment_r))

        # \\
        elif coeff_l[0] <= 0 and coeff_r[0] <= 0:
            logg.trace(f"\\\\ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l))
            contour_t = np.hstack((y_segment_t, y_segment_r))
            contour_b = np.hstack((y_segment_l))

        # \/
        elif coeff_l[0] <= 0 and coeff_r[0] >= 0:
            logg.trace(f"\\/ coeff_l[0]: {coeff_l[0]} coeff_r[0]: {coeff_r[0]}")
            x_sample = np.hstack((x_sample_l, x_sample_r))
            contour_t = y_segment_t
            contour_b = np.hstack((y_segment_l, y_segment_r))

    # plot everything to debug things
    if not ax is None:
        ## plot left and right segments
        ax.plot(x_sample_l, y_segment_l, color="g", marker=".", ls="")
        ax.plot(x_sample_r, y_segment_r, color="g", marker=".", ls="")
        ## intersection point
        ax.plot([i_x], [i_y], color="g", marker="x", ls="")
        ## plot the segments
        ax.plot([p0t.x, p0b.x], [p0t.y, p0b.y], color="b", marker="", ls="-")
        ax.plot([p1t.x, p1b.x], [p1t.y, p1b.y], color="b", marker="", ls="-")

    return contour_t, contour_b, x_sample


def compute_thick_spline(p0, p1, thickness, ax=None):
    """Compute the thick cubic spline between two points

    * translate to the origin and rotate the points to have both on the x axis
    * compute the spline
    * make it thicker
    * rotate and translate to original position
    """
    logg = logging.getLogger(f"c.{__name__}.compute_spline")
    logg.setLevel("TRACE")
    logg.trace(f"Starting compute_spline")

    # translate and rotate the point to the origin
    rot_p0, rot_p1, dir_01 = translate_points_to_origin(p0, p1)
    logg.trace(f"rot_p0: {rot_p0} rot_p1: {rot_p1}")

    # compute the normal direction to the vectors
    np0_ori_rad = rot_p0.ori_rad + math.pi / 2
    np1_ori_rad = rot_p1.ori_rad + math.pi / 2

    # compute the corner points of the thick spline
    offset_x_0 = math.cos(np0_ori_rad) * thickness
    offset_y_0 = math.sin(np0_ori_rad) * thickness
    logg.trace(f"offset_x_0: {offset_x_0} offset_y_0: {offset_y_0}")
    p0t = OrientedPoint(rot_p0.x + offset_x_0, rot_p0.y + offset_y_0, rot_p0.ori_deg)
    p0b = OrientedPoint(rot_p0.x - offset_x_0, rot_p0.y - offset_y_0, rot_p0.ori_deg)
    logg.trace(f"p0t: {p0t} p0b: {p0b}")
    offset_x_1 = math.cos(np1_ori_rad) * thickness
    offset_y_1 = math.sin(np1_ori_rad) * thickness
    logg.trace(f"offset_x_1: {offset_x_1} offset_y_1: {offset_y_1}")
    p1t = OrientedPoint(rot_p1.x + offset_x_1, rot_p1.y + offset_y_1, rot_p1.ori_deg)
    p1b = OrientedPoint(rot_p1.x - offset_x_1, rot_p1.y - offset_y_1, rot_p1.ori_deg)
    logg.trace(f"p1t: {p1t} p1b: {p1b}")

    # compute the coeff of the line passing through the points
    coeff_l = fit_line(p0t, p0b)
    coeff_r = fit_line(p1t, p1b)
    logg.trace(f"coeff_l: {coeff_l} coeff_r: {coeff_r}")

    # compute the spline points
    coeff_t = fit_cubic(p0t, p1t)
    coeff_b = fit_cubic(p0b, p1b)
    x_sample_t, y_segment_t = sample_segment_points(p0t.x, p1t.x, coeff_t)
    x_sample_b, y_segment_b = sample_segment_points(p0b.x, p1b.x, coeff_b)
    logg.trace(f"x_sample_t.shape: {x_sample_t.shape}")
    logg.trace(f"x_sample_b.shape: {x_sample_b.shape}")

    contour_t, contour_b, x_sample = build_contour(
        p0t,
        p0b,
        p1t,
        p1b,
        coeff_l,
        coeff_r,
        x_sample_t,
        y_segment_t,
        x_sample_b,
        y_segment_b,
        ax,
    )

    # compute the top and bottom contours
    logg.trace(f"x_sample.shape: {x_sample.shape}")
    logg.trace(f"contour_t.shape: {contour_t.shape}")
    logg.trace(f"contour_b.shape: {contour_b.shape}")

    # get the max and min y, aligned on the grid
    max_y = np.amax(contour_t)
    min_y = np.amin(contour_b)
    logg.trace(f"max_y: {max_y} min_y: {min_y}")
    max_y_aligned = math.floor(max_y)
    min_y_aligned = math.ceil(min_y)
    logg.trace(f"max_y_aligned: {max_y_aligned} min_y_aligned: {min_y_aligned}")

    #  sample all the points inside the spline, aligned on the grid
    on_points_x = []
    on_points_y = []
    for i, x_curr in enumerate(x_sample):
        for y_curr in range(min_y_aligned, max_y_aligned + 1):
            if contour_b[i] <= y_curr <= contour_t[i]:
                on_points_x.append(x_curr)
                on_points_y.append(y_curr)

    # rototranslate points to the original position
    rototran_x, rototran_y = rototranslate_points(
        on_points_x, on_points_y, -dir_01, p0.x, p0.y,
    )

    # plot everything to debug things
    if not ax is None:
        vec_len = 3
        ## plot the points
        plot_utils.add_vector(p0, ax, color="r", vec_len=vec_len)
        plot_utils.add_vector(p1, ax, color="r", vec_len=vec_len)
        ## plot the rotated vectors
        plot_utils.add_vector(rot_p0, ax, color="k", vec_len=vec_len)
        plot_utils.add_vector(rot_p1, ax, color="k", vec_len=vec_len)
        ## plot the corner of the spline
        plot_utils.add_vector(p0t, ax, color="k", vec_len=vec_len)
        plot_utils.add_vector(p1t, ax, color="k", vec_len=vec_len)
        plot_utils.add_vector(p0b, ax, color="k", vec_len=vec_len)
        plot_utils.add_vector(p1b, ax, color="k", vec_len=vec_len)
        ## plot top and bottom splines
        #  plot_utils.add_points(x_sample_t, y_segment_t, ax, color="b", marker=".", ls="")
        #  plot_utils.add_points(x_sample_b, y_segment_b, ax, color="b", marker=".", ls="")
        ax.plot(x_sample_t, y_segment_t, color="r", marker="", ls="-")
        ax.plot(x_sample_b, y_segment_b, color="r", marker="", ls="-")
        ## plot top and bottom contours
        ax.plot(x_sample, contour_t, color="r", marker=".", ls="")
        ax.plot(x_sample, contour_b, color="r", marker=".", ls="")
        ## plot on point
        ax.plot(on_points_x, on_points_y, color="b", marker=".", ls="")
        ## plot on point translated back to original position
        ax.plot(rototran_x, rototran_y, color="b", marker=".", ls="")

    return rototran_x, rototran_y
