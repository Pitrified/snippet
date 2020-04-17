import argparse
import logging
import math
import matplotlib.pyplot as plt

from pathlib import Path
from timeit import default_timer as timer

from cursive_writer.ligature.ligature import find_best_shift
from cursive_writer.spliner.spliner import compute_aligned_cubic_segment
from cursive_writer.spliner.spliner import compute_aligned_glyph
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils import plot_utils
from cursive_writer.utils.geometric_utils import find_align_stride
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils.geometric_utils import slope2deg
from cursive_writer.utils.geometric_utils import translate_spline_sequence
from cursive_writer.utils.geometric_utils import find_spline_sequence_bbox
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.utils import load_spline
from cursive_writer.utils.setup import setup_logger


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-il",
        "--path_input_left",
        type=str,
        default="v1_001.txt",
        help="Path to input spline to use on the left side",
    )
    parser.add_argument(
        "-ir",
        "--path_input_right",
        type=str,
        default="i1_h_006.txt",
        help="Path to input spline to use on the right side",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env():
    setup_logger(msg_type="m")

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 spliner_examples.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def ex_parametric_tangent(p0, p1, x_stride, ax):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_parametric_tangent")
    logg.debug(f"\nStarting ex_parametric_tangent")

    t_a_sample, x_a_sample, y_a_sample, yp_a_sample = compute_aligned_cubic_segment(
        p0, p1, x_stride, ax
    )

    # xid = 24
    xid = math.floor(x_a_sample.shape[0] / 2)
    recap = f"At point x_a_sample[{xid}] {x_a_sample[xid]}"
    recap += f" y_a_sample[{xid}] {y_a_sample[xid]}"
    recap += f" yp_a_sample[{xid}] {yp_a_sample[xid]}"
    logg.debug(recap)

    # plot an example of tangent line
    tang_op = OrientedPoint(
        x_a_sample[xid], y_a_sample[xid], slope2deg(yp_a_sample[xid])
    )
    tang_coeff = tang_op.to_ab_line()
    tang_y_a_sample = poly_model(x_a_sample, tang_coeff, flip_coeff=True)
    ax.plot(x_a_sample, tang_y_a_sample, color="g", ls="-", marker="")


def exs_parametric_tangent():
    """TODO: what is exs_parametric_tangent doing?
    """
    logg = logging.getLogger(f"c.{__name__}.exs_parametric_tangent")
    logg.debug(f"Start exs_parametric_tangent")

    # p0: (967.5267, 974.1696) # -85.8470 p1: (1006.2328, 822.0541) # -62.3541
    x_stride = 1
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    p0 = OrientedPoint(967.5267, 974.1696, -85.8470)
    p1 = OrientedPoint(1006.2328, 822.0541, -62.3541)
    ex_parametric_tangent(p0, p1, x_stride, ax)

    x_stride = 0.3

    # create the plot
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    p0 = OrientedPoint(10, 10, -30)
    p1 = OrientedPoint(30, 20, 70)
    ax[0][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][0])

    p0 = OrientedPoint(10, 13, -30)
    p1 = OrientedPoint(30, 20, 50)
    ax[0][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][1])

    p0 = OrientedPoint(10, 10, -10)
    p1 = OrientedPoint(30, 20, 70)
    ax[1][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][0])

    p0 = OrientedPoint(10, 10, -10)
    p1 = OrientedPoint(30, 20, 50)
    ax[1][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][1])

    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    p0 = OrientedPoint(100, 100, -30)
    p1 = OrientedPoint(300, 200, 70)
    ax[0][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][0])

    p0 = OrientedPoint(100, 130, -30)
    p1 = OrientedPoint(300, 200, 50)
    ax[0][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][1])

    p0 = OrientedPoint(100, 100, -10)
    p1 = OrientedPoint(300, 200, 70)
    ax[1][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][0])

    p0 = OrientedPoint(100, 100, -10)
    p1 = OrientedPoint(300, 200, 50)
    ax[1][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][1])


def ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax):
    """TODO: what is ex_ligature_2segments doing?
    """
    logg = logging.getLogger(f"c.{__name__}.ex_ligature_2segments")
    logg.debug(f"\nStarting ex_ligature_2segments")
    logg.debug(f"l_p0.x: {l_p0.x} l_p1.x: {l_p1.x} r_p0.x: {r_p0.x} r_p1.x: {r_p1.x}")

    # find stride roughly a hundredth of the segment length
    x_stride = max(l_p1.x - l_p0.x, r_p1.x - r_p0.x) / 100
    x_stride = 10 ** math.floor(math.log(x_stride, 10))
    logg.debug(f"x_stride: {x_stride}")

    segment_start = timer()
    _, l_x_as, l_y_as, l_yp_as = compute_aligned_cubic_segment(l_p0, l_p1, x_stride)
    _, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_cubic_segment(
        r_p0, r_p1, x_stride,
    )
    segment_end = timer()
    logg.debug(f"Time to compute aligned segments: {segment_end - segment_start:.6f}")

    (
        best_shift,
        best_r_x_as,
        best_l_tang_y_as,
        l_id_s_x,
        r_id_s_x,
        l_p_ext,
        r_p_ext,
        ext_x_as,
        ext_y_as,
    ) = find_best_shift(l_x_as, l_y_as, l_yp_as, r_x_orig_as, r_y_as, r_yp_as, x_stride)
    logg.debug(f"best_shift: {best_shift}")

    # plot the segments
    ax.plot(l_x_as, l_y_as, color="c", ls="--", marker="")
    ax.plot(best_r_x_as, r_y_as, color="c", ls="--", marker="")
    ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", ls="-")
    ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="k", ls="-")
    # ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="k", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", marker=".")
    # ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", marker=".")
    ax.plot(ext_x_as, ext_y_as, color="k", ls="-", marker="")

    ax.plot(l_p_ext.x, l_p_ext.y, color="r", ls="", marker="o", fillstyle="none")
    ax.plot(r_p_ext.x, r_p_ext.y, color="r", ls="", marker="o", fillstyle="none")

    ax.plot(l_x_as, best_l_tang_y_as, color="b", ls=":", marker="")

    vec_len = max(l_p1.x, r_p1.y) / 10
    plot_utils.add_vector(l_p_ext, ax, color="r", vec_len=vec_len)
    plot_utils.add_vector(r_p_ext, ax, color="r", vec_len=vec_len)


def exs_ligature_2segments():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.exs_build_ligature")
    logg.debug(f"Starting exs_build_ligature")

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    l_p0 = OrientedPoint(10, 10, 0)
    l_p1 = OrientedPoint(30, 20, 60)
    r_p0 = OrientedPoint(15, 10, 40)
    r_p1 = OrientedPoint(32, 20, 10)
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    l_p0 = OrientedPoint(1213, 682, -12)
    l_p1 = OrientedPoint(1579, 937, 60)
    r_p0 = OrientedPoint(50, 700, -15)
    r_p1 = OrientedPoint(582, 976, 70)
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax)

    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    l_p0 = OrientedPoint(10, 10, -30)
    l_p1 = OrientedPoint(30, 20, 70)
    r_p0 = OrientedPoint(15, 10, -10)
    r_p1 = OrientedPoint(32, 20, 50)
    ax[0][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(10, 13, -30)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 12, -10)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 70)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][1])

    # create the plot
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    l_p0 = OrientedPoint(100, 100, -30)
    l_p1 = OrientedPoint(300, 200, 70)
    r_p0 = OrientedPoint(150, 100, -10)
    r_p1 = OrientedPoint(320, 200, 50)
    ax[0][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(100, 130, -30)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 120, -10)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 70)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][1])

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    l_p0 = OrientedPoint(1213, 682, -3)
    l_p1 = OrientedPoint(1579, 937, 50)
    r_p0 = OrientedPoint(50, 700, -15)
    r_p1 = OrientedPoint(582, 976, 70)
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax)


def ex_align_glyphs(pf_spline_left, pf_spline_right, data_dir):
    """TODO: what is ex_align_glyphs doing?
    """
    logg = logging.getLogger(f"c.{__name__}.ex_align_glyphs")
    logg.debug(f"Start ex_align_glyphs")

    spline_sequence_l = load_spline(pf_spline_left, data_dir)
    gly_seq_l = spline_sequence_l[-1]
    spline_sequence_r = load_spline(pf_spline_right, data_dir)
    gly_seq_r = spline_sequence_r[0]

    # find a proper x_stride for this pair of files
    x_stride = find_align_stride((gly_seq_l, gly_seq_r))

    # compute the data for the left and right glyph
    _, l_x_as, l_y_as, l_yp_as = compute_aligned_glyph(gly_seq_l, x_stride)
    _, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_glyph(gly_seq_r, x_stride)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    fig.suptitle("Example of glyph alignment", fontsize=16)
    fig.canvas.set_window_title("Example of glyph alignment")

    # plot original glyphs
    # ax.plot(l_x_as, l_y_as, color="y", ls="", marker=".")
    # ax.plot(r_x_orig_as, r_y_as, color="g", ls="", marker=".")

    (
        best_shift,
        best_r_x_as,
        best_l_tang_y_as,
        l_id_s_x,
        r_id_s_x,
        l_p_ext,
        r_p_ext,
        ext_x_as,
        ext_y_as,
    ) = find_best_shift(l_x_as, l_y_as, l_yp_as, r_x_orig_as, r_y_as, r_yp_as, x_stride)
    logg.debug(f"best_shift: {best_shift}")

    # plot the segments
    # ax.plot(l_x_as, l_y_as, color="g", ls="", marker=".")
    # ax.plot(best_r_x_as, r_y_as, color="y", ls="", marker=".")
    ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", ls="-")
    ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="k", ls="-")
    # ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="k", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", marker=".")
    # ax.plot(best_r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", marker=".")
    ax.plot(ext_x_as, ext_y_as, color="k", ls="-", marker="")

    ax.plot(l_p_ext.x, l_p_ext.y, color="r", ls="", marker="o", fillstyle="none")
    ax.plot(r_p_ext.x, r_p_ext.y, color="r", ls="", marker="o", fillstyle="none")

    ax.plot(l_x_as, best_l_tang_y_as, color="b", ls=":", marker="")

    vec_len = max(l_x_as[-1], l_y_as[-1], r_x_orig_as[-1], r_y_as[-1]) / 10
    plot_utils.add_vector(l_p_ext, ax, color="r", vec_len=vec_len)
    plot_utils.add_vector(r_p_ext, ax, color="r", vec_len=vec_len)


def ex_align_letters(pf_spline_left, pf_spline_right, data_dir, thickness):
    """TODO: what is ex_align_letters doing?
    """
    logg = logging.getLogger(f"c.{__name__}.ex_align_letters")
    logg.debug(f"Start ex_align_letters")

    spline_sequence_l = load_spline(pf_spline_left, data_dir)
    gly_seq_l = spline_sequence_l[-1]
    spline_sequence_r = load_spline(pf_spline_right, data_dir)
    gly_seq_r = spline_sequence_r[0]

    # find a proper x_stride for this pair of files
    x_stride = find_align_stride((*spline_sequence_l, *spline_sequence_r))

    # compute the data for the left and right glyph
    _, l_x_as, l_y_as, l_yp_as = compute_aligned_glyph(gly_seq_l, x_stride)
    _, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_glyph(gly_seq_r, x_stride)

    (
        best_shift,
        best_r_x_as,
        best_l_tang_y_as,
        l_id_s_x,
        r_id_s_x,
        l_p_ext,
        r_p_ext,
        ext_x_as,
        ext_y_as,
    ) = find_best_shift(l_x_as, l_y_as, l_yp_as, r_x_orig_as, r_y_as, r_yp_as, x_stride)
    logg.debug(f"best_shift: {best_shift}")

    # find where to chop the left glyph, at the last point left to l_p_ext
    for l_p_id, op in enumerate(gly_seq_l):
        if op.x >= l_p_ext.x:
            break
    # l_p_id is the first that is right of l_p_ext, the slice *excludes* it
    spline_sequence_l[-1] = gly_seq_l[:l_p_id]

    # find where to chop the right glyph, at the first point right of r_p_ext
    for r_p_id, op in enumerate(gly_seq_r):
        if op.x > r_p_ext.x:
            break
    # r_p_id is the first that is right of r_p_ext, the slice *includes* it
    spline_sequence_r[0] = gly_seq_r[r_p_id:]

    # translate the right spline along x axis
    translate_spline_sequence(spline_sequence_r, best_shift, 0)

    # build the connecting glyph
    gly_seq_con = [spline_sequence_l[-1][-1], l_p_ext, r_p_ext, spline_sequence_r[0][0]]
    spline_sequence_con = [gly_seq_con]

    # build a single sequence
    spline_sequence_all = []
    spline_sequence_all.extend(spline_sequence_l)
    spline_sequence_all.extend(spline_sequence_con)
    spline_sequence_all.extend(spline_sequence_r)

    # compute the thick spline
    spline_samples_con = compute_long_thick_spline(spline_sequence_con, thickness)
    spline_samples_l = compute_long_thick_spline(spline_sequence_l, thickness)
    spline_samples_r = compute_long_thick_spline(spline_sequence_r, thickness)

    # merge in a single one
    spline_samples_all = []
    spline_samples_all.extend(spline_samples_l)
    spline_samples_all.extend(spline_samples_con)
    spline_samples_all.extend(spline_samples_r)

    # find dimension of the plot
    xlim, ylim = find_spline_sequence_bbox(spline_sequence_all)
    # inches to point
    ratio = 8 / 1000
    wid = xlim[1] - xlim[0]
    hei = ylim[1] - ylim[0]
    fig_dims = (wid * ratio, hei * ratio)

    # create plot
    fig = plt.figure(figsize=fig_dims, frameon=False)
    ax = fig.add_axes((0, 0, 1, 1))
    fig.canvas.set_window_title("Example of glyph alignment")
    ax.set_axis_off()

    # colors = False
    colors = True
    if colors:
        for glyph in spline_samples_r:
            for segment in glyph:
                ax.plot(*segment, color="g", marker=".", ls="")
        for glyph in spline_samples_con:
            for segment in glyph:
                ax.plot(*segment, color="r", marker=".", ls="")
        for glyph in spline_samples_l:
            for segment in glyph:
                ax.plot(*segment, color="y", marker=".", ls="")
    else:
        for glyph in spline_samples_all:
            for segment in glyph:
                ax.plot(*segment, color="k", marker=".", ls="")


def run_ligature_examples(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_ligature_examples")
    logg.debug(f"Starting run_ligature_examples")

    logg = logging.getLogger(f"c.{__name__}.main")
    logg.debug(f"Starting main")
    # logg.setLevel("INFO")

    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    data_dir = main_dir.parent / "src" / "cursive_writer" / "data"
    logg.debug(f"data_dir: {data_dir}")

    path_input_left = args.path_input_left
    pf_spline_left = data_dir / path_input_left
    logg.debug(f"pf_spline_left: {pf_spline_left}")
    path_input_right = args.path_input_right
    pf_spline_right = data_dir / path_input_right
    logg.debug(f"pf_spline_right: {pf_spline_right}")

    # exs_parametric_tangent()
    # exs_ligature_2segments()

    # ex_align_glyphs(pf_spline_left, pf_spline_right, data_dir)
    thickness = 10
    ex_align_letters(pf_spline_left, pf_spline_right, data_dir, thickness)

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_ligature_examples(args)
