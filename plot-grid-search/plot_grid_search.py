import argparse
import logging
import json

import numpy as np

from random import seed
from timeit import default_timer as timer
from itertools import product
from textwrap import wrap
from pprint import pformat

import matplotlib
import matplotlib.pyplot as plt


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(
        description="Plot grid search results, at most 3 params can be changed"
    )

    parser.add_argument(
        "-io",
        "--template_files",
        type=str,
        default="default_{}",
        help="template to input and output files",
    )

    parser.add_argument("-s", "--seed", type=int, default=-1, help="random seed to use")

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    log_format_module = "%(name)s: %(message)s"
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def load_results(template_input):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.load_results")
    logg.debug(f"Start load_results")

    fp_hypagrid = template_input.format("hyper_params_grid.json")
    fp_hp_ids = template_input.format("hp_ids.json")
    fp_grid_loss_results = template_input.format("gridres.json")

    # load dict of hyper_params_grid
    with open(fp_hypagrid, "r") as f:
        hyper_params_grid = json.load(f)

    # load dict ID to hp_set
    with open(fp_hp_ids, "r") as f:
        hp_ids = json.load(f)

    # load dict ID to loss
    with open(fp_grid_loss_results, "r") as f:
        res = json.load(f)

    #  logg.debug(f"hp_ids {hp_ids}\nres {res}")

    # link hp_set to loss
    #  hp2res = {tuple(hp_ids[id_]): res[id_] for id_ in hp_ids}

    # get hp labels
    hp_labels = sorted(hp_ids["0"])
    logg.debug(f"sorted labels {hp_labels}")

    hp2res = {}
    for id_ in hp_ids:
        #  hp_set = (hp_ids[id_][lab_hp] for lab_hp in sorted(hp_ids[id_]))
        # hp_set is the set of hypa that we want to link to a result
        hp_set = []
        # we build it using the sorted hp_labels, to be consistent
        for lab_hp in hp_labels:
            # extract the values from the dict
            hp_set.append(hp_ids[id_][lab_hp])
        hp_set = tuple(hp_set)
        hp2res[hp_set] = res[id_]

    #  logg.debug(f"hp2res {hp2res}")
    logg.debug(f"loaded hp2res {len(hp2res)}")

    return hyper_params_grid, hp2res, hp_labels


def run_plot_grid_search(template_input, template_output):
    """Can change up to 3 hypa
    """
    logg = logging.getLogger(f"c.{__name__}.run_plot_grid_search")
    logg.debug(f"Start plotting")

    # HYPERPARAMETERS!
    #  hyper_params_grid = {
    #  "num_epochs": [10, 20],
    #  "Nh1": [5, 10],
    #  "Nh2": [5, 10],
    #  "lr": [0.01, 0.001],
    #  "lr_final": [False, 0.0001, 0.00001],
    #  "early_stop_pad": [20],
    #  "epsilon_loss": [0.0001],
    #  }
    hyper_params_grid, hp2res, hp_labels = load_results(template_input)
    #  pprint(hyper_params_grid, stream=logg)
    logg.debug(f"hyper_params_grid\n{pformat(hyper_params_grid)}")

    # hypa that we want to change WITHIN the same plot
    #  do_change = ["Nh1", "lr", "lr_final"]
    #  do_change = ["Nh1"]
    #  do_change = ["Nh1", "lr"]
    #  do_change = ["lr", "lr_final"]
    do_change = ["num_epochs", "lr", "lr_final"]

    # these hypa will change in DIFFERENT plots, fixed in each
    dont_change = split_labels(hyper_params_grid, do_change)
    logg.debug(f"do_change {do_change} dont_change {dont_change}")

    #  do_prod = list(product(*[hyper_params_grid[l] for l in do_change]))
    #  dont_prod = list(product(*[hyper_params_grid[l] for l in dont_change]))
    #  logg.debug(f"do_prod {len(do_prod)} dont_prod {len(dont_prod)}")
    #  logg.debug(f"do_prod {do_prod} dont_prod {dont_prod}")

    # dnp has all the combinations of the fixed parameters
    # we want to pass them labeled, so we build a dict
    # THIS is to do triple_hist
    # the third parameter is linked to a color and we show *only* the points
    # for the three changing param in the plot, all the other params are fixed
    for dnp in product(*[hyper_params_grid[l] for l in dont_change]):
        # create fixed hypa dict
        fixed = {label: p for label, p in zip(dont_change, dnp)}
        logg.debug(f"fixed {fixed}")

        # build filename to save plot
        out_file = ""
        for label in fixed:
            if label in ["early_stop_pad", "epsilon_loss"]:
                continue
            out_file += f"{label}_{fixed[label]}_"
        out_file += "{}"
        template_output = template_output.format(out_file)
        logg.debug(f"template_output {template_output}")

        multigram(
            hyper_params_grid, do_change, fixed, hp2res, hp_labels, template_output
        )
        #  break

    # TODO or MAYBE we pass do_change e dont_change and compute the mean/stddev
    # of all the points for each changing set of params
    # using this we do fancy double_hist
    # for 2 params, we show *all* possible values when changing the others

    # MAYBE do some frequency count and plot horizontal bars as wide as the freq

    plt.show()


def split_labels(hyper_params_grid, do_change):
    """Splits the labels of the hypa in change/not change
    """
    logg = logging.getLogger(f"c.{__name__}.split_labels")
    logg.debug(f"Splitting")

    dont_change = []
    for label in hyper_params_grid:
        #  logg.debug(f"label {label}")
        if label not in do_change:
            dont_change.append(label)

    return dont_change


def res_get(hp2res, hp_dict, hp_labels):
    """Get the res linked to the hypa in hp_dict
    """
    logg = logging.getLogger(f"c.{__name__}.res_get")
    logg.setLevel("INFO")
    logg.debug(f"Start res_get")

    # build the hp_set for the corresponding bar
    hp_set = []
    for label in hp_labels:
        hp_set.append(hp_dict[label])
    hp_set = tuple(hp_set)
    # get the corresponding loss value
    hp_val = hp2res[hp_set]

    logg.debug(f"hp_set {hp_set} hp_val {hp_val}")
    return hp_val


def multigram(
    hyper_params_grid,
    do_change,
    fixed,
    hp2res,
    hp_labels,
    template_output,
    ax=None,
    fig=None,
    **kwargs,
):
    """Plot the multi histogram

    hyper_params_grid:
        dict { labels : [values, of, hypa], }
    do_change:
        list of labels of hypa to change in this plot
    fixed:
        dict { label : fixed_val }
    hp2res:
        dict { (hp, set, used) : loss }

    Style of the function vaguely inspired from here
    https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
    No idea on fig/ax 
    use https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.subplots.html

    Info on bar https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.bar.html
    """
    logg = logging.getLogger(f"c.{__name__}.multigram")
    logg.debug(f"Start multigram")
    logg.debug(f"do_change {do_change} fixed {fixed}")

    if len(do_change) == 1:
        single_hist(
            hyper_params_grid,
            do_change,
            fixed,
            hp2res,
            hp_labels,
            template_output,
            ax,
            fig,
            **kwargs,
        )
    elif len(do_change) == 2:
        double_hist(
            hyper_params_grid,
            do_change,
            fixed,
            hp2res,
            hp_labels,
            template_output,
            ax,
            fig,
            **kwargs,
        )
    elif len(do_change) == 3:
        triple_hist(
            hyper_params_grid,
            do_change,
            fixed,
            hp2res,
            hp_labels,
            template_output,
            ax,
            fig,
            **kwargs,
        )
    else:
        logg.critical(f"You can change from 1 to 3 hyper parameters")


def single_hist(
    hyper_params_grid,
    do_change,
    fixed,
    hp2res,
    hp_labels,
    template_output,
    ax,
    fig,
    **kwargs,
):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.single_hist")
    logg.debug(f"Start single_hist")

    if ax is None or fig is None:
        fig, ax = plt.subplots()

    # only one label, change the values on this parameter
    la = do_change[0]

    bin_width = 0.8
    # bin_pos is the CENTER of the bar
    #  bin_pos = [i + bin_width/2 for i in range(1, len(hyper_params_grid[la])+1)]
    bin_pos = [i + bin_width / 2 for i in range(0, len(hyper_params_grid[la]))]
    logg.debug(f"bin_width {bin_width} bin_pos {bin_pos}")

    # copy the fixed param dict
    # in hp_dict we add the changing params
    hp_dict = fixed.copy()

    for index, val_a in enumerate(hyper_params_grid[la]):
        hp_dict[la] = val_a
        hp_val = res_get(hp2res, hp_dict, hp_labels)
        ax.bar(x=bin_pos[index], height=hp_val, width=bin_width)

    ax.set_xticks(bin_pos)
    ax.set_xticklabels([x for x in hyper_params_grid[la]], rotation=90)
    ax.set_xlabel(f"{la}")
    ax.set_ylabel(f"Loss")
    title = f"Loss for fixed params {fixed}"
    max_title_len = 80
    wrapped_title = "\n".join(wrap(title, max_title_len))
    ax.set_title(wrapped_title)

    #  fig.savefig("./output/test_single_hist.png")
    fig.savefig(template_output.format("single_hist"))


def double_hist(
    hyper_params_grid,
    do_change,
    fixed,
    hp2res,
    hp_labels,
    template_output,
    ax,
    fig,
    **kwargs,
):
    """
    This is for double hist when showing all the points for the 2 param combo
    Instead of just points on the line, might use swarmplot
    https://seaborn.pydata.org/generated/seaborn.swarmplot.html
    """
    logg = logging.getLogger(f"c.{__name__}.double_hist")
    logg.debug(f"Start double_hist")

    if ax is None or fig is None:
        fig, ax = plt.subplots()

    colors = ["b", "g", "r", "c", "m", "y", "k"]

    # two params to change
    la = do_change[0]
    lb = do_change[1]

    bin_width = 0.8
    # bin_pos is the CENTER of the bar
    bin_pos = [i + bin_width / 2 for i in range(len(hyper_params_grid[la]))]
    # sub length of a step for secondary param
    bin_step = bin_width / len(hyper_params_grid[lb])

    logg.debug(f"bin_width {bin_width} bin_pos {bin_pos} bin_step {bin_step}")

    hp_dict = fixed.copy()

    # iterate over the first
    for ia, val_a in enumerate(hyper_params_grid[la]):
        hp_dict[la] = val_a
        last_bars = []
        bar_labels = []
        # iterate over the second
        for ib, val_b in enumerate(hyper_params_grid[lb]):
            hp_dict[lb] = val_b
            hp_val = res_get(hp2res, hp_dict, hp_labels)
            bar_pos = ia + bin_step * ib + bin_step / 2
            bar_label = f"{val_b}"
            bar_labels.append(bar_label)
            c = colors[ib % len(colors)]
            new_bar = ax.bar(x=bar_pos, height=hp_val, width=bin_step, color=c)
            last_bars.append(new_bar)

    # we do the horror of last_bars to set the legend only once, as the lb
    # params are the same in all la bins
    for i, last_bar in enumerate(last_bars):
        last_bar.set_label(bar_labels[i])

    ax.set_xticks(bin_pos)
    #  ax.set_xticklabels([x for x in hyper_params_grid[la]], rotation=90)
    ax.set_xticklabels([x for x in hyper_params_grid[la]], rotation=0)
    ax.set_xlabel(f"{la} - {lb}")
    ax.set_ylabel(f"Loss")
    ax.legend()

    title = f"Loss for fixed params {fixed}"
    max_title_len = 70
    wrapped_title = "\n".join(wrap(title, max_title_len))
    ax.set_title(wrapped_title)

    #  fig.savefig("./output/test_double_hist.png")
    fig.savefig(template_output.format("double_hist"))


def triple_hist(
    hyper_params_grid,
    do_change,
    fixed,
    hp2res,
    hp_labels,
    template_output,
    ax,
    fig,
    **kwargs,
):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.triple_hist")
    logg.debug(f"Start triple_hist")

    if ax is None or fig is None:
        fig, ax = plt.subplots()

    colors = ["b", "g", "r", "c", "m", "y", "k"]

    # three params to change
    la = do_change[0]
    lb = do_change[1]
    lc = do_change[2]

    bin_width = 0.8
    # bin_pos is the CENTER of the group
    bin_pos = [i + bin_width / 2 for i in range(len(hyper_params_grid[la]))]
    # sub length of a step for secondary param
    bin_step = bin_width / len(hyper_params_grid[lb])

    logg.debug(f"bin_width {bin_width} bin_pos {bin_pos} bin_step {bin_step}")

    hp_dict = fixed.copy()

    # save here precise positions of ticks
    detailed_bin_pos = []
    detailed_labels_ab = []

    # iterate over the first
    for ia, val_a in enumerate(hyper_params_grid[la]):
        hp_dict[la] = val_a

        # iterate over the second
        for ib, val_b in enumerate(hyper_params_grid[lb]):
            hp_dict[lb] = val_b
            bar_pos = ia + bin_step * ib + bin_step / 2

            detailed_bin_pos.append(bar_pos)
            label_ab = f"{val_a} - {val_b}"
            detailed_labels_ab.append(label_ab)

            # legend label only on the last set of dot added
            last_dots = []
            dot_labels = []

            # iterate over the third
            for ic, val_c in enumerate(hyper_params_grid[lc]):
                hp_dict[lc] = val_c
                hp_val = res_get(hp2res, hp_dict, hp_labels)

                c = colors[ic % len(colors)]
                new_dot = ax.scatter(x=bar_pos, y=hp_val, color=c)
                dot_label = f"{val_c}"
                dot_labels.append(dot_label)
                last_dots.append(new_dot)

    # put labels
    for i, last_dot in enumerate(last_dots):
        last_dot.set_label(dot_labels[i])

    #  ax.set_xticks(bin_pos)
    ax.set_xticks(detailed_bin_pos)
    ax.set_xticklabels(detailed_labels_ab, rotation=45)
    #  ax.set_xticklabels([x for x in hyper_params_grid[la]], rotation=90)
    #  ax.set_xticklabels([x for x in hyper_params_grid[la]], rotation=0)

    ax.set_xlabel(f"{la} - {lb}")
    ax.set_ylabel(f"Loss")
    ax.legend()

    title = f"Loss for fixed params {fixed}"
    max_title_len = 70
    wrapped_title = "\n".join(wrap(title, max_title_len))
    ax.set_title(wrapped_title)

    fig.tight_layout()
    #  fig.savefig("./output/test_triple_hist.png")
    fig.savefig(template_output.format("triple_hist"))


def main():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    template_files = args.template_files

    recap = f"python3 plot_grid_search.py"
    recap += f" --seed {myseed}"
    recap += f" --template_files {template_files}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    template_input = f"./input/{template_files}"
    template_output = f"./output/{template_files}"
    logmain.debug(f"template_input {template_input} template_output {template_output}")
    run_plot_grid_search(template_input, template_output)


if __name__ == "__main__":
    main()
