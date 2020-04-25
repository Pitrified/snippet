import logging
import numpy as np

from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.utils import print_coeff

import math


def line_curve_ab_coeff(x0, y0, x1, y1):
    """Find the coefficient for a linear curve passing through two points

    y = ax + b
    """
    logg = logging.getLogger(f"c.{__name__}.line_curve")
    logg.setLevel("INFO")
    logg.debug(f"{fmt_cn('Starting')} line_curve")

    if x1 == x0:
        return [float("inf"), x0]

    a = (y1 - y0) / (x1 - x0)
    b = y0 - a * x0

    logg.debug(f"y = {a:.4f}*x + {b:.4f}")

    return [a, b]


def line_curve_point(x0, y0, x1, y1):
    """Find a point on the line with appropriate orientation
    """
    ori_deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
    return OrientedPoint(x0, y0, ori_deg)


def collide_line_box(bbox, line_point):
    """Collide a line with a rectangular box

    line_coeff = [a, b]
    y = ax + b

          top
          ---
    left |   | right
         |   |
          ---
         bottom

    Note that the y axis is reversed in tkinter
    """
    logg = logging.getLogger(f"c.{__name__}.collide_line_box")
    logg.setLevel("INFO")
    logg.debug(f"{fmt_cn('Start')} collide_line_box")

    left, top, right, bot = bbox
    line_coeff = line_point.to_ab_line()
    logg.debug(f"left: {left} top: {top} right: {right} bot: {bot} coeff: {line_coeff}")

    a = line_coeff[0]
    b = line_coeff[1]
    # horizontal line
    if a == 0:
        if top < b < bot:
            logg.debug(f"Horizontal top: {top} b: {b} bot: {bot}")
            left_inter = (left, b)
            right_inter = (right, b)
            return [left_inter, right_inter]
        else:
            logg.debug(f"Horizontal outside")
            return []

    # vertical line
    elif a == float("inf"):
        if left < b < right:
            logg.debug(f"Vertical left: {left} b: {b} right: {right}")
            top_inter = (b, top)
            bot_inter = (b, bot)
            return [top_inter, bot_inter]
        else:
            logg.debug(f"Vertical outside")
            return []

    # regular line, find intersections
    left_inter = (left, a * left + b)
    top_inter = ((top - b) / a, top)
    right_inter = (right, a * right + b)
    bot_inter = ((bot - b) / a, bot)
    logg.debug(
        f"Intersections left: {left_inter} top: {top_inter} right: {right_inter} bot: {bot_inter}"
    )

    # more readable tuple coefficient
    x, y = 0, 1
    # select admissible intersections
    admissible_inter = []
    if top < left_inter[y] < bot:
        logg.debug(f"top < left_inter < bot")
        admissible_inter.append(left_inter)
    if left < top_inter[x] < right:
        logg.debug(f"left < top_inter < right")
        admissible_inter.append(top_inter)
    if top < right_inter[y] < bot:
        logg.debug(f"top < right_inter < bot")
        admissible_inter.append(right_inter)
    if left < bot_inter[x] < right:
        logg.debug(f"left < bot_inter < right")
        admissible_inter.append(bot_inter)

    return admissible_inter


def translate_line(line_coeff, shift_x, shift_y):
    """Translate a line by changing the b coeff

    y = ax + b
    Remember that tkinter has y axis toward the bottom
    """
    logg = logging.getLogger(f"c.{__name__}.translate_line")
    #  logg.setLevel("INFO")
    logg.debug(f"{fmt_cn('Starting')} translate_line {line_coeff} {shift_x} {shift_y}")

    a, b = line_coeff

    b += shift_y
    b += -a * shift_x

    logg.debug(f"shifted: {[a, b]}")

    return [a, b]


def translate_point_dxy(orig_point, shift_x, shift_y):
    """Translate the orig_point of dx, dy and return a new one
    """
    return OrientedPoint(
        orig_point.x + shift_x, orig_point.y + shift_y, orig_point.ori_deg
    )


def translate_point_dir(orig_point, dir_deg, shift):
    """Translate the point along a direction of a certain amount
    """
    new_x = orig_point.x + shift * math.cos(math.radians(dir_deg))
    new_y = orig_point.y + shift * math.sin(math.radians(dir_deg))
    return OrientedPoint(new_x, new_y, orig_point.ori_deg)


def translate_spline_sequence(spline_sequence, dx, dy):
    """Changes a spline, translating the points by (dx, dy)
    """
    # logg = logging.getLogger(f"c.{__name__}.translate_spline_sequence")
    # logg.debug(f"Start translate_spline_sequence")

    for glyph in spline_sequence:
        for op in glyph:
            op.x += dx
            op.y += dy


def dist2D(p0, p1):
    """Distance between two points
    """
    return math.sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2)


def apply_affine_transform(F, x, y):
    """Left multiply the homogeneous point by the matrix

    res = F * p
    """
    logg = logging.getLogger(f"c.{__name__}.apply_affine_transform")
    #  logg.setLevel("TRACE")
    logg.trace(f"Start {fmt_cn('apply_affine_transform')}")

    hom_point = np.array([x, y, 1])
    transform_point = np.dot(F, hom_point)
    return [transform_point[0], transform_point[1]]


def poly_model(x, coeff, flip_coeff=False):
    """Compute y values of a polynomial

    The coeff start with the low degrees first

        y = coeff[0] + coeff[1] * x + coeff[2] * x^2 ...

    x: x vector
    coeff: polynomial parameters, low degrees first
    flip_coeff: flip the order of coeff
    """
    if flip_coeff:
        flipped_coeff = np.flip(coeff)
    else:
        flipped_coeff = coeff

    pol_order = len(coeff)
    x_matrix = np.array([x ** i for i in range(pol_order)]).transpose()
    y_true = np.matmul(x_matrix, flipped_coeff)
    return y_true


def slope2deg(slope, direction=1):
    """Convert the slope of a line to an angle in degrees
    """
    return math.degrees(np.arctan2(slope, direction))


def slope2rad(slope, direction=1):
    """Convert the slope of a line to an angle in radians
    """
    return np.arctan2(slope, direction)


def compute_rot_matrix(theta_deg):
    """Compute the 2x2 rotation matrix for angle theta_deg in degrees
    """
    logg = logging.getLogger(f"c.{__name__}.compute_rot_matrix")
    logg.setLevel("INFO")

    theta_deg = math.radians(theta_deg)
    ct = math.cos(theta_deg)
    st = math.sin(theta_deg)
    rot_mat = np.array(((ct, -st), (st, ct)))
    logg.debug(f"rot_mat = {rot_mat}")

    return rot_mat


def rotate_point(point, theta_deg):
    """Rotate a point (or Nx2 array of points) by theta_deg degree

    MAYBE automagically transpose the point mat if it is 2xN instead of Nx2
    """
    rot_mat = compute_rot_matrix(theta_deg)
    return np.matmul(point, rot_mat)


def compute_affine_transform(base_pt_abs, basis_length):
    """Update the affine transform matrix fm <-> abs coord

    Given basis e1, e2 at 0, moved into u, v at p

        e2              v
        |       ->     /
        ._ e1         ._ u
       0             p

    Write the u,v,p in canonical coord and the homogeneous matrix is

            [u1 v1 p1]
        F = [u2 v2 p2]
            [ 0  0  1]

    Move points to and from frame by multiplying by F
    Point in frame p_F is converted to canonical p_e

        p_e = F p_F
        p_F = F-1 p_e

    Clear lecture on the topic:
    http://www.cs.cornell.edu/courses/cs4620/2014fa/lectures/08transforms2d.pdf
    """
    logg = logging.getLogger(f"c.{__name__}.compute_affine_transform")
    #  logg.setLevel("TRACE")
    logg.trace(f"Start {fmt_cn('compute_affine_transform')}")
    logg.trace(f"base_point: {base_pt_abs}")

    # the orientation are aligned with abs, so y is flipped
    # this is ok, will be fixed in the affine transform
    base_ori_rad = base_pt_abs.ori_rad
    logg.trace(f"base_ori_rad: {base_ori_rad} radians")

    # basis vector of the FM frame, in img coord
    u = [math.cos(base_ori_rad) * basis_length, math.sin(base_ori_rad) * basis_length]
    v = [math.sin(base_ori_rad) * basis_length, -math.cos(base_ori_rad) * basis_length]
    p = base_pt_abs

    fm2abs = np.array([[u[0], v[0], p.x], [u[1], v[1], p.y], [0, 0, 1]])
    logg.trace(f"fm2abs: {fm2abs}")
    abs2fm = np.linalg.inv(fm2abs)
    logg.trace(f"abs2fm: {abs2fm}")

    return fm2abs, abs2fm


def bisect_poly(coeff, d_coeff, y_target, tolerance=1e-6, x_low=0, x_high=1):
    """Finds a value of x so that |y-p(x)| < tolerance

    Also returns when |x_low-x_high| < tolerance

    A simple bisection is used, take care of setting x_low and x_high
    properly in order to find the value that you vaguely expect.
    I'm too lazy to use the derivative to find a better midpoint.

    A lot of assumptions are made on the shape of p(x), mainly on the sign of
    its second derivative, that should not change if you expect good results.

    Ties when y_target is higher/lower than y_mid are broken using the first derivative
    """
    logg = logging.getLogger(f"c.{__name__}.bisect_poly")
    logg.setLevel("INFO")
    logg.debug(f"Start bisect_poly {y_target}")
    logg.debug(f"coeff: {print_coeff(coeff)}")
    logg.debug(f"d_coeff: {print_coeff(d_coeff)}")

    # deal with bad inputs
    if x_high < x_low:
        x_low, x_high = x_high, x_low

    while not math.isclose(x_low, x_high, abs_tol=tolerance):
        # find the midpoint
        x_mid = (x_low + x_high) / 2

        # compute the value of the function in low, mid, high
        y_low = poly_model(np.array([x_low]), coeff, flip_coeff=True)
        y_mid = poly_model(np.array([x_mid]), coeff, flip_coeff=True)
        y_high = poly_model(np.array([x_high]), coeff, flip_coeff=True)

        logg.debug(f"x_low: {x_low} x_mid: {x_mid} x_high: {x_high}")
        logg.debug(f"y_low: {y_low} y_mid: {y_mid} y_high: {y_high}")

        # if the midpoint is a good approx, return that
        if math.isclose(y_target, y_mid, abs_tol=tolerance):
            logg.debug(f"the y_target {y_target} is close to y_mid {y_mid}")
            return x_mid

        # the y_target is between y_low and y_mid
        elif y_low <= y_target <= y_mid or y_low >= y_target >= y_mid:
            logg.debug(f"the y_target {y_target} is between y_low and y_mid")
            x_high = x_mid

        # the y_target is between y_mid and y_high
        elif y_mid <= y_target <= y_high or y_mid >= y_target >= y_high:
            logg.debug(f"the y_target {y_target} is between y_mid and y_high")
            x_low = x_mid

        # the y_target is higher than y_mid (but not lower than y_high or y_low
        # else it would be in the other cases)
        elif y_target >= y_mid:
            logg.debug(f"the y_target {y_target} is over y_mid")
            y_d_mid = poly_model(np.array([x_mid]), d_coeff, flip_coeff=True)

            # the curve is going up at midpoint, pick right interval
            if y_d_mid >= 0:
                logg.debug(f"the curve is going up at midpoint, pick right interval")
                x_low = x_mid

            # the curve is going down at midpoint, pick left interval
            elif y_d_mid < 0:
                logg.debug(f"the curve is going down at midpoint, pick left interval")
                x_high = x_mid

        elif y_target <= y_mid:
            logg.debug(f"the y_target {y_target} is below y_mid")
            y_d_mid = poly_model(np.array([x_mid]), d_coeff, flip_coeff=True)

            # the curve is going up at midpoint, pick left interval
            if y_d_mid >= 0:
                logg.debug(f"the curve is going up at midpoint, pick left interval")
                x_high = x_mid

            # the curve is going down at midpoint, pick right interval
            elif y_d_mid < 0:
                logg.debug(f"the curve is going down at midpoint, pick right interval")
                x_low = x_mid

    # TODO before returning need to check if the y_mid is actually near
    # y_target, or if y_target was outside the interval requested
    return (x_low + x_high) / 2


def rotate_coeff(coeff, theta_deg):
    """Returns the parametric expression of the rotated coeff

    Given a cubic curve

        y = a*x^3 + b*x^2 + c*x + d

    It can be parametrized as

        [x] = [         t               ]
        [y] = [ a*t^3 + b*t^2 + c*t + d ]

    Apply a rotation of th radians

        [x'] = [cos(th) -sin(th)] * [         t               ]
        [y'] = [sin(th)  cos(th)]   [ a*t^3 + b*t^2 + c*t + d ]
    """
    logg = logging.getLogger(f"c.{__name__}.rotate_coeff")
    logg.setLevel("INFO")
    logg.debug(f"Starting rotate_coeff")

    theta_rad = math.radians(theta_deg)
    ct = math.cos(theta_rad)
    st = math.sin(theta_rad)

    a, b, c, d = coeff

    x_rot_coeff = [
        -st * a,
        -st * b,
        ct - st * c,
        -st * d,
    ]
    y_rot_coeff = [
        ct * a,
        ct * b,
        st + ct * c,
        ct * d,
    ]

    return x_rot_coeff, y_rot_coeff


def rotate_derive_coeff(coeff, theta_deg):
    """Returns the parametric expression of the derivative of the rotated coeff

    Given a cubic curve

        y = a*x^3 + b*x^2 + c*x + d

    It can be parametrized as

        [x] = [         t               ]
        [y] = [ a*t^3 + b*t^2 + c*t + d ]

    Apply a rotation of th radians

        [x'] = [cos(th) -sin(th)] * [         t               ]
        [y'] = [sin(th)  cos(th)]   [ a*t^3 + b*t^2 + c*t + d ]

    The derivative as function of t is

        dy   dy/dt
        -- = -----
        dx   dx/dt
    """
    theta_rad = math.radians(theta_deg)
    ct = math.cos(theta_rad)
    st = math.sin(theta_rad)

    a, b, c, d = coeff

    x_rot_d_coeff = [
        3 * -st * a,
        2 * -st * b,
        ct - st * c,
    ]
    y_rot_d_coeff = [
        3 * ct * a,
        2 * ct * b,
        st + ct * c,
    ]

    return x_rot_d_coeff, y_rot_d_coeff


def sample_parametric_aligned(
    x_coeff,
    y_coeff,
    x_d_coeff,
    y_d_coeff,
    x_min,
    x_max,
    x_stride,
    x_offset=0,
    x_low=None,
    x_high=None,
):
    """Sample a parametric curve along a grid

    Given a parametric curve and its derivative and an interval [x_min, x_max]

        [x] = [f(t)] (as x_coeff)       [x'] = [f'(t)] (as x_d_coeff)
        [y] = [g(t)] (as y_coeff)       [y'] = [g'(t)] (as y_d_coeff)

    Returns:
        * t_a_sample values that correspond to
        * x_a_sample values, aligned on multiples of x_stride, accounting for x_offset
        * y_a_sample
        * yp_a_sample

    Let x_min = 1.7, x_max = 4.5 and x_stride = 0.5, the curve will be sampled in

        x_sample = [2, 2.5, 3, 3.5, 4, 4.5]

    Note that the extremes are included on both sides.

    Use x_offset to shift the grid a bit: it will be correctly aligned after
    translating the points in the correct position: if p0.x = 3.8, the x_offset
    will be equal to 4 - 3.8 = 0.2 and the grid is

        x_sample = [2.2, 2.7, 3.2, 3.7, 4.2, 4.7]

    so that when translating up by 3.8, the x points will be aligned:

        x_sample = [6, 6.5, 7, 7.5, 8, 8.5]

    So x_offset is how much p0.x is misaligned with the grid

    TODO: better documentation of parameters/return
    """
    logg = logging.getLogger(f"c.{__name__}.sample_parametric_aligned")
    logg.setLevel("INFO")
    logg.debug(f"\nStart sample_parametric_aligned")
    logg.debug(f"x_min: {x_min} x_max: {x_max}")
    logg.debug(f"x_low: {x_low} x_high: {x_high}")
    logg.debug(f"x_stride: {x_stride} x_offset: {x_offset}")

    if x_low is None:
        x_low = 2 * x_min
    if x_high is None:
        x_high = 2 * x_max

    # find the value for t that corresponds to x_min and x_max
    t_min = bisect_poly(x_coeff, x_d_coeff, x_min, x_low, x_high)
    t_max = bisect_poly(x_coeff, x_d_coeff, x_max, x_low, x_high)
    logg.debug(f"t_min: {t_min} t_max: {t_max}")

    # check where the extremes are
    x_test_min = poly_model(np.array([t_min]), x_coeff, flip_coeff=True)
    y_test_min = poly_model(np.array([t_min]), y_coeff, flip_coeff=True)
    x_test_max = poly_model(np.array([t_max]), x_coeff, flip_coeff=True)
    y_test_max = poly_model(np.array([t_max]), y_coeff, flip_coeff=True)
    recap = f"x_test_min: {x_test_min} x_test_max: {x_test_max}"
    recap += f" y_test_min: {y_test_min} y_test_max: {y_test_max}"
    logg.debug(recap)

    # oversample in t, pad a bit the interval
    x_len = x_max - x_min
    # t_pad = x_len / 10
    t_pad = x_len / 10 * x_stride
    t_num_samples = int(x_len * 100 / x_stride)
    t_oversample = np.linspace(t_min - t_pad, t_max + t_pad, num=t_num_samples)
    x_oversample = poly_model(t_oversample, x_coeff, flip_coeff=True)
    # y_oversample = poly_model(t_oversample, y_coeff, flip_coeff=True)
    # x_d_oversample = poly_model(t_oversample, x_d_coeff, flip_coeff=True)
    # y_d_oversample = poly_model(t_oversample, y_d_coeff, flip_coeff=True)
    # return t_oversample, x_oversample, y_oversample, 0

    # find the aligned x values
    x_a_min = math.ceil(x_min / x_stride) * x_stride
    x_a_max = math.floor(x_max / x_stride) * x_stride
    logg.debug(f"x_a_min: {x_a_min} x_a_max: {x_a_max}")
    x_a_sample = np.arange(x_a_min, x_a_max + x_stride / 2, x_stride)
    logg.debug(f"x_a_sample.shape: {x_a_sample.shape} {x_a_sample[0]} {x_a_sample[-1]}")

    # translate the aligned x values to compensate the x_offset
    x_a_sample += x_offset
    logg.debug(f"x_a_sample.shape: {x_a_sample.shape} {x_a_sample[0]} {x_a_sample[-1]}")

    # find the closest x in the aligned grid and save the value there
    x_id = 0

    # save here the t values that generate x_a_sample values
    t_a_sample = np.empty_like(x_a_sample)

    # cycle all the t values
    for i, t in enumerate(t_oversample):
        # when the x_oversample at index i is bigger than the current aligned at x_id
        # you are straddling the x_a_sample point
        if x_oversample[i] > x_a_sample[x_id]:
            # logg.debug(f"x {x_oversample[i-1]} < {x_a_sample[x_id]} < {x_oversample[i]}")

            # more precise by weighing the two adjacent t_oversample values
            dist = x_oversample[i] - x_oversample[i - 1]
            al = (x_a_sample[x_id] - x_oversample[i - 1]) / dist

            # save the t value at the corresponding position
            t_a_sample[x_id] = (1 - al) * t_oversample[i - 1] + al * t_oversample[i]

            # check if there are more x_a_sample available
            x_id += 1
            if x_id >= x_a_sample.shape[0]:
                break

    y_a_sample = poly_model(t_a_sample, y_coeff, flip_coeff=True)
    x_a_d_sample = poly_model(t_a_sample, x_d_coeff, flip_coeff=True)
    y_a_d_sample = poly_model(t_a_sample, y_d_coeff, flip_coeff=True)

    # compute the value of the derivative
    yp_a_sample = np.divide(y_a_d_sample, x_a_d_sample)

    return t_a_sample, x_a_sample, y_a_sample, yp_a_sample


def find_align_stride(glyphs):
    """Given an iterable of glyphs, finds the stride to sample them
    """
    # logg = logging.getLogger(f"c.{__name__}.find_align_stride")
    # logg.debug(f"Start find_align_stride")

    x_strides = []
    for glyph in glyphs:
        for i in range(len(glyph) - 1):
            p0 = glyph[i]
            p1 = glyph[i + 1]
            x_strides.append((p1.x - p0.x) / 100)

    # keep the max: points close to each other will not be sampled well, but
    # points far away will be computed in reasonable time. If the min was kept,
    # large segments will become too slow.
    x_stride = max(x_strides)
    x_stride = 10 ** math.floor(math.log(x_stride, 10))
    # logg.debug(f"x_stride: {x_stride}")

    return x_stride


def find_spline_sequence_bbox(spline_sequence, old_xlim=None, old_ylim=None):
    """TODO: what is find_spline_sequence_bbox doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.find_spline_sequence_bbox")
    # logg.debug(f"Start find_spline_sequence_bbox")

    if old_xlim is None:
        min_x = float("inf")
        max_x = float("-inf")
    else:
        min_x, max_x = old_xlim
    if old_xlim is None:
        min_y = float("inf")
        max_y = float("-inf")
    else:
        min_y, max_y = old_ylim

    for glyph in spline_sequence:
        for point in glyph:
            # logg.debug(f"point: {point}")
            if point.x > max_x:
                max_x = point.x
            if point.x < min_x:
                min_x = point.x
            if point.y > max_y:
                max_y = point.y
            if point.y < min_y:
                min_y = point.y
    # logg.debug(f"max_x: {max_x} min_x: {min_x} max_y: {max_y} min_y: {min_y}")

    return (min_x, max_x), (min_y, max_y)
