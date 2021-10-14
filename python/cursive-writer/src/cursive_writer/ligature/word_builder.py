import argparse
import logging
import jsons  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from pathlib import Path
from copy import deepcopy

from typing import Dict, Tuple
from cursive_writer.utils.type_utils import ThickSpline

from cursive_writer.ligature.letter_class import Letter
from cursive_writer.ligature.ligature import align_letter_1
from cursive_writer.ligature.ligature import align_letter_2
from cursive_writer.ligature.ligature_info import LigatureInfo
from cursive_writer.ligature.word_generator import generate_word
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.geometric_utils import find_thick_spline_bbox
from cursive_writer.utils.geometric_utils import translate_spline_sequence
from cursive_writer.utils.geometric_utils import translate_thick_spline
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.setup import setup_logger
from cursive_writer.utils.utils import serializer_oriented_point


def parse_arguments() -> argparse.Namespace:
    """Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--input_str",
        type=str,
        default="vivvmmiimv",
        help="Input string to write",
    )

    parser.add_argument(
        "-t", "--thickness", type=int, default=10, help="Thickness of the pen"
    )

    parser.add_argument(
        "-col",
        "--colors",
        type=str,
        default="k",
        help="Color to use, set 'cycle' to use a different one in each glyph",
    )

    parser.add_argument(
        "-llt",
        "--log_level_type",
        type=str,
        default="m",
        help="Message format for the debugging logger",
        choices=["anlm", "nlm", "lm", "nm", "m"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env() -> argparse.Namespace:
    args = parse_arguments()

    setup_logger("DEBUG", args.log_level_type)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = "python3 word_builder.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def load_letter_dict(thickness: int, data_dir: Path) -> Dict[str, Letter]:
    """TODO: what is load_letter_dict doing?"""
    logg = logging.getLogger(f"c.{__name__}.load_letter_dict")
    logg.debug("Start load_letter_dict")

    letters_info: Dict[str, Letter] = {}
    let = "a"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "a1_l_003.txt",
        pf_spline_high=data_dir / let / "a1_h_000.txt",
        thickness=thickness,
    )
    let = "b"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="high_up",
        pf_spline_low=data_dir / let / "b0_l_000.txt",
        pf_spline_high=data_dir / let / "b0_h_001.txt",
        thickness=thickness,
    )
    let = "c"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "c0_l_001.txt",
        pf_spline_high=data_dir / let / "c0_h_004.txt",
        thickness=thickness,
    )
    let = "d"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "d0_l_000.txt",
        pf_spline_high=data_dir / let / "d0_h_000.txt",
        thickness=thickness,
    )
    let = "e"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "e1_l_001.txt",
        pf_spline_high=data_dir / let / "e0_h_005.txt",
        thickness=thickness,
    )
    let = "g"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "g0_l_000.txt",
        pf_spline_high=data_dir / let / "g0_h_000.txt",
        thickness=thickness,
    )
    let = "h"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "h1_l_000.txt",
        pf_spline_high=data_dir / let / "h1_h_004.txt",
        thickness=thickness,
    )
    let = "i"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "i2_l_dot_000.txt",
        pf_spline_high=data_dir / let / "i2_h_dot_000.txt",
        thickness=thickness,
    )
    let = "j"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "j0_l_dot_000.txt",
        pf_spline_high=data_dir / let / "j0_h_dot_000.txt",
        thickness=thickness,
    )
    let = "k"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "k0_l_001.txt",
        pf_spline_high=data_dir / let / "k0_h_000.txt",
        thickness=thickness,
    )
    let = "l"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "l0_l_000.txt",
        pf_spline_high=data_dir / let / "l0_h_000.txt",
        thickness=thickness,
    )
    let = "m"
    letters_info[let] = Letter(
        let,
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / let / "m2_000.txt",
        thickness=thickness,
    )
    let = "n"
    letters_info[let] = Letter(
        let,
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / let / "n2_000.txt",
        thickness=thickness,
    )
    let = "o"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="high_up",
        pf_spline_low=data_dir / let / "o3_l_001.txt",
        pf_spline_high=data_dir / let / "o3_h_000.txt",
        thickness=thickness,
    )
    let = "p"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "p1_l_000.txt",
        pf_spline_high=data_dir / let / "p1_h_000.txt",
        thickness=thickness,
    )
    let = "q"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "q1_l_000.txt",
        pf_spline_high=data_dir / let / "q1_h_000.txt",
        thickness=thickness,
    )
    let = "t"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "t0_l_000.txt",
        pf_spline_high=data_dir / let / "t0_h_000.txt",
        thickness=thickness,
    )
    let = "u"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "u2_l_000.txt",
        pf_spline_high=data_dir / let / "u2_h_000.txt",
        thickness=thickness,
    )
    let = "v"
    letters_info[let] = Letter(
        let,
        left_type="high_down",
        right_type="high_up",
        pf_spline_alone=data_dir / let / "v3_000.txt",
        thickness=thickness,
    )
    let = "w"
    letters_info[let] = Letter(
        let,
        left_type="high_down",
        right_type="high_up",
        pf_spline_alone=data_dir / let / "w0_006.txt",
        thickness=thickness,
    )
    let = "y"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / let / "y0_l_004.txt",
        pf_spline_high=data_dir / let / "y0_h_010.txt",
        thickness=thickness,
    )
    let = "z"
    letters_info[let] = Letter(
        let,
        left_type="low_up",
        right_type="low_up",
        pf_spline_alone=data_dir / let / "z0_a_000.txt",
        pf_spline_low=data_dir / let / "z0_l_002.txt",
        pf_spline_high=data_dir / let / "z0_h_002.txt",
        thickness=thickness,
    )
    return letters_info


def compute_letter_alignement(
    f_let: Letter, s_let: Letter, x_stride: float, data_dir: Path, ligature_dir: Path
) -> LigatureInfo:
    """TODO: what is compute_letter_alignement doing?"""
    logg = logging.getLogger(f"c.{__name__}.compute_letter_alignement")
    logg.debug(f"Start compute_letter_alignement {f_let.letter} {s_let.letter}")

    # pick the correct align strategy

    # something like im or iv
    if f_let.right_type == "low_up" and s_let.left_type == "high_down":
        strategy = "align_letter_2"

        # the right side at the moment does not change, so get any one
        f_let_type = "alone"
        f_spline_seq = f_let.get_spline_seq(f_let_type)
        f_pf_name = f_let.get_pf(f_let_type).name
        f_hash_sha1 = f_let.get_hash(f_let_type)

        # we request the high because this *is* a high letter
        s_let_type = "high"
        s_spline_seq = s_let.get_spline_seq(s_let_type)
        s_pf_name = s_let.get_pf(s_let_type).name
        s_hash_sha1 = s_let.get_hash(s_let_type)

    # all other cases use align_letter_1
    else:
        strategy = "align_letter_1"

        # need to pick the correct version of the letters to join

        # the right side at the moment does not change, so get any one
        f_let_type = "alone"
        f_spline_seq = f_let.get_spline_seq(f_let_type)
        f_pf_name = f_let.get_pf(f_let_type).name
        f_hash_sha1 = f_let.get_hash(f_let_type)

        # look at the right of the first letter
        if f_let.right_type == "high_up":
            # use high version of the second letter
            s_let_type = "high"
        elif f_let.right_type == "low_up":
            # use low version of the second letter
            s_let_type = "low"

        # get relevant informations
        s_spline_seq = s_let.get_spline_seq(s_let_type)
        s_pf_name = s_let.get_pf(s_let_type).name
        s_hash_sha1 = s_let.get_hash(s_let_type)

    # load, if available, the ligature for this
    ligature_pf = ligature_dir / f"{f_let.letter}{s_let.letter}.txt"
    if ligature_pf.exists():
        # load the saved LigatureInfo
        ci_load = jsons.loads(ligature_pf.read_text(), LigatureInfo)

        # decide if the ligature loaded is the same
        # logg.debug(f"ci_load: {ci_load!r}")
        logg.debug(f"ci_load: {ci_load}")
        if f_pf_name != ci_load.f_pf_name or s_pf_name != ci_load.s_pf_name:
            logg.debug("The names in the loaded info are different than the current")
            equals = False
        elif f_let_type != ci_load.f_let_type or s_let_type != ci_load.s_let_type:
            logg.debug("The letter types in the loaded info are different")
            equals = False
        elif f_hash_sha1 != ci_load.f_hash_sha1 or s_hash_sha1 != ci_load.s_hash_sha1:
            logg.debug("The hash_sha1 in the loaded info are different")
            equals = False
        else:
            logg.debug("The ligature is valid!")
            equals = True

        if equals:
            return ci_load

    if strategy == "align_letter_2":
        # load and compute
        spline_seq_con, shift, _ = align_letter_2(f_spline_seq, s_spline_seq, x_stride)

        # there is no need to chop the last/first glyphs
        f_gly_chop = f_spline_seq[-1]
        s_gly_chop = s_spline_seq[0]

    else:
        # load and compute
        (
            spline_seq_con,
            f_gly_chop,
            s_gly_chop,
            shift,
        ) = align_letter_1(f_spline_seq, s_spline_seq, x_stride)

    con_info = LigatureInfo(
        f_pf_name=f_pf_name,
        s_pf_name=s_pf_name,
        f_let_type=f_let_type,
        s_let_type=s_let_type,
        spline_seq_con=spline_seq_con,
        f_gly_chop=f_gly_chop,
        s_gly_chop=s_gly_chop,
        shift=shift,
        f_hash_sha1=f_hash_sha1,
        s_hash_sha1=s_hash_sha1,
    )
    # logg.debug(f"con_info: {con_info!r}")
    logg.debug(f"con_info: {con_info}")

    # save the LigatureInfo
    jsons.set_serializer(serializer_oriented_point, OrientedPoint)
    ligature_info_encoded = jsons.dumps(con_info, indent=4)
    logg.debug(f"\nligature_info_encoded: {ligature_info_encoded}")

    with ligature_pf.open("w") as f_li:
        f_li.write(ligature_info_encoded)

    return con_info


def fill_ligature_info(
    input_str: str,
    letters_info: Dict[str, Letter],
    x_stride: float,
    data_dir: Path,
    ligature_dir: Path,
    thickness: int,
) -> Tuple[Dict[str, LigatureInfo], Dict[str, ThickSpline]]:
    """TODO: what is fill_ligature_info doing?"""
    logg = logging.getLogger(f"c.{__name__}.fill_ligature_info")
    logg.debug("Start fill_ligature_info")

    # where to keep the connection info
    ligature_info: Dict[str, LigatureInfo] = {}
    thick_con_info: Dict[str, ThickSpline] = {}

    for i in range(len(input_str) - 1):
        # get the current pair
        pair = input_str[i : i + 2]
        logg.debug(f"\nDoing pair: {pair}")

        # compute info for this pair if needed
        if pair not in ligature_info:
            f_let = letters_info[pair[0]]
            s_let = letters_info[pair[1]]
            ligature_info[pair] = compute_letter_alignement(
                f_let, s_let, x_stride, data_dir, ligature_dir
            )
        else:
            logg.debug("Pair already computed")

        # link all the spline info
        full_spline_con = [ligature_info[pair].f_gly_chop]
        full_spline_con.extend(ligature_info[pair].spline_seq_con)
        # shift the second glyph
        s_gly_chop = deepcopy(ligature_info[pair].s_gly_chop)
        shift = ligature_info[pair].shift
        translate_spline_sequence([s_gly_chop], shift, 0)
        full_spline_con.append(s_gly_chop)

        # precompute the full thick ligature information
        full_thick_con = compute_long_thick_spline(full_spline_con, thickness)
        thick_con_info[pair] = full_thick_con

    return ligature_info, thick_con_info


def build_word(
    input_str: str,
    letters_info: Dict[str, Letter],
    ligature_info: Dict[str, LigatureInfo],
    thick_con_info: Dict[str, ThickSpline],
    thickness: int,
) -> ThickSpline:
    """TODO: what is build_word doing?"""
    logg = logging.getLogger(f"c.{__name__}.build_word")
    logg.debug(f"Start build_word {input_str}")

    # the final thick spline for the word
    word_thick_spline: ThickSpline = []

    # the accumulated shift
    acc_shift: float = 0

    # the first letter of the word
    first_letter = input_str[0]

    # save the first thick letter
    word_thick_spline.extend(
        letters_info[first_letter].get_thick_samples("alone", thickness)
    )

    for i in range(len(input_str) - 1):
        # get the current pair
        pair = input_str[i : i + 2]
        logg.debug(f"Doing pair: {pair}")

        # extract the second letter info
        s_let = letters_info[pair[1]]

        # remove the last glyph: it will be replaecd by the first of the thick_spline_con
        word_thick_spline.pop()

        # extract the thick connection
        thick_spline_con = thick_con_info[pair]
        # translate it
        tra_thick_spline_con = translate_thick_spline(thick_spline_con, acc_shift, 0)
        word_thick_spline.extend(tra_thick_spline_con)

        # update the total shift
        acc_shift += ligature_info[pair].shift

        # add the second letter
        # extract the thick spline of the correct type of the second letter to use
        s_thick_spline = s_let.get_thick_samples(
            ligature_info[pair].s_let_type, thickness
        )
        # translate it
        s_tra_thick_spline = translate_thick_spline(s_thick_spline, acc_shift, 0)
        # add it to the list of glyphs, without the first glyph
        word_thick_spline.extend(s_tra_thick_spline[1:])

    return word_thick_spline


def plot_results(
    thick_spline: ThickSpline, input_str: str = "", colors: str = "k", fig=None, ax=None
) -> None:

    # inches to point
    ratio = 3 / 1000
    # find dimension of the plot
    xlim, ylim = find_thick_spline_bbox(thick_spline)
    wid = xlim[1] - xlim[0]
    hei = ylim[1] - ylim[0]
    fig_dims = (wid * ratio, hei * ratio)

    # create plot
    if fig is None or ax is None:
        fig = plt.figure(frameon=False)
        ax = fig.add_axes((0, 0, 1, 1))

    ax.set_axis_off()
    fig.set_size_inches(*fig_dims)
    fig.canvas.set_window_title(f"Writing {input_str}")

    # style = {"color": "k", "marker": ".", "ls": ""}
    if colors == "cycle":
        col_list = ["g", "r", "y", "c", "m", "k", "b"]
    else:
        col_list = ["k"]

    # i_s = 0
    for i_g, glyph in enumerate(thick_spline):
        # logg.debug(f"Plotting glyph: {glyph}")
        cc = col_list[i_g % len(col_list)]
        style = {"color": cc, "marker": ".", "ls": ""}
        for segment in glyph:
            # cc = col_list[i_s % len(col_list)]
            # i_s += 1
            # style = {"color": cc, "marker": ".", "ls": ""}
            ax.plot(*segment, **style)


def run_word_builder(args: argparse.Namespace) -> None:
    """TODO: What is word_builder doing?"""
    logg = logging.getLogger(f"c.{__name__}.run_word_builder")
    logg.debug("Starting run_word_builder")

    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    data_dir = main_dir.parent / "data"
    logg.debug(f"data_dir: {data_dir}")
    ligature_dir = main_dir.parent / "connections"
    logg.debug(f"ligature_dir {ligature_dir}")
    if not ligature_dir.exists():
        ligature_dir.mkdir(parents=True)

    thickness = args.thickness if args.thickness > 0 else 1

    letters_info = load_letter_dict(thickness, data_dir)
    logg.debug("letters_info:")
    for letter in letters_info:
        logg.debug(f"{letters_info[letter]}")

    # the sampling precision when shifting
    x_stride: float = 1

    # setup looping
    if args.input_str == ".cycle":
        new_input_str = ".random"
        loop = "english"
    elif args.input_str == ".cicla":
        new_input_str = ".casuale"
        loop = "italian"
    else:
        new_input_str = args.input_str
        loop = "wait"

    colors = args.colors

    fig = plt.figure(frameon=False)
    ax = fig.add_axes((0, 0, 1, 1))

    while not ".quit".startswith(new_input_str):
        logg.debug(f"new_input_str: {new_input_str}")

        # pick random word
        if ".casuale".startswith(new_input_str):
            word_file = data_dir / "wordlist" / "italian_megamix.txt"
            input_str = generate_word(letters_info.keys(), word_file)
        elif ".random".startswith(new_input_str):
            word_file = data_dir / "wordlist" / "3of6game_filt.txt"
            input_str = generate_word(letters_info.keys(), word_file)

        # show all ligature type
        elif len(new_input_str) >= 4 and ".ex" == new_input_str[0:3]:
            input_str = "{0}v{0}{0}i{0}".format(new_input_str[3])

        elif ".alfabeto".startswith(new_input_str):
            input_str = "".join(letters_info.keys())
        elif ".alphabet".startswith(new_input_str):
            input_str = "".join(letters_info.keys())

        # starts with . but not recognized
        elif new_input_str.startswith("."):
            input_str = "minimum"

        # change thickness to use
        elif new_input_str.startswith("-t"):
            thickness = int(new_input_str[2:])
            logg.debug(f"Using thickness: {thickness}")

        # use the new input, filter the letter that are not known yet
        else:
            input_str = "".join(
                list(filter(lambda x: x in letters_info.keys(), new_input_str))
            )
            if len(input_str) == 0:
                input_str = "minimum"

        logg.debug(f"Writing word: {input_str}")

        # the information on how to link the letters
        ligature_info, thick_con_info = fill_ligature_info(
            input_str, letters_info, x_stride, data_dir, ligature_dir, thickness
        )

        # build the word
        word_thick_spline = build_word(
            input_str, letters_info, ligature_info, thick_con_info, thickness
        )

        # plot results
        ax.clear()
        plot_results(word_thick_spline, input_str, colors, fig, ax)
        plt.pause(0.1)

        if loop == "italian":
            new_input_str = ".casuale"
        elif loop == "english":
            new_input_str = ".random"
        else:
            recap = "\nType the next word or enter a prefix of"
            recap += "\n\t'.exL' to show all ligatures for L"
            recap += "\n\t'.alphabet' or '.alfabeto' to show all available letters"
            recap += "\n\t'.random' to write a random word"
            recap += "\n\t'.casuale' to write an italian random word"
            recap += "\n\t'.quit' to exit"
            recap += "\n: "
            new_input_str = input(recap)


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
