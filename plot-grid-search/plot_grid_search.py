import argparse
import logging
import json

import numpy as np

from random import seed
from timeit import default_timer as timer
from itertools import product

import matplotlib
import matplotlib.pyplot as plt


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(
        description="Plot grid search results, at most 3 params can be changed"
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
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def load_results():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.load_results")
    logg.debug(f"Start load_results")

    fp_ids = "./hp_ids.json"
    fp_res = "./gridres.json"

    # load dict ID to hp_set
    with open(fp_ids, "r") as f:
        hp_ids = json.load(f)

    # load dict ID to loss
    with open(fp_res, "r") as f:
        res = json.load(f)

    #  logg.debug(f"hp_ids {hp_ids} res {res}")

    # link hp_set to loss
    hp2res = {tuple(hp_ids[id_]): res[id_] for id_ in hp_ids}

    #  logg.debug(f"hp2res {hp2res}")
    logg.debug(f"loaded hp2res {len(hp2res)}")

    return hp2res


def run_plot_grid_search():
    """Can change up to 3 hypa
    """
    logg = logging.getLogger(f"c.{__name__}.run_plot_grid_search")
    logg.debug(f"Start plotting")

    # HYPERPARAMETERS!
    hyper_params_grid = {
        "num_epochs": [10, 20],
        "Nh1": [5, 10],
        "Nh2": [5, 10],
        "lr": [0.01, 0.001],
        "lr_final": [False, 0.0001, 0.00001],
        "early_stop_pad": [20],
        "epsilon_loss": [0.0001],
    }
    results = load_results()

    # hypa that we want to change WITHIN the same plot
    #  do_change = ["Nh1", "lr", "lr_final"]
    do_change = ["Nh1"]

    # these hypa will change in DIFFERENT plots, fixed in each
    dont_change = split_labels(hyper_params_grid, do_change)
    logg.debug(f"do_change {do_change} dont_change {dont_change}")

    #  do_prod = list(product(*[hyper_params_grid[l] for l in do_change]))
    #  dont_prod = list(product(*[hyper_params_grid[l] for l in dont_change]))
    #  logg.debug(f"do_prod {len(do_prod)} dont_prod {len(dont_prod)}")
    #  logg.debug(f"do_prod {do_prod} dont_prod {dont_prod}")

    # dnp has all the combinations of the fixed parameters
    # we want to pass them labeled, so we build a dict
    for dnp in product(*[hyper_params_grid[l] for l in dont_change]):
        fixed = {label: p for label, p in zip(dont_change, dnp)}
        logg.debug(fixed)
        multigram(hyper_params_grid, do_change, fixed)
        break

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


def multigram(hyper_params_grid, do_change, fixed, ax=None, **kwargs):
    """Plot the multi histogram

    hyper_params_grid:
        dict { labels : [values, of, hypa], }
    do_change:
        list of labels of hypa to change in this plot
    fixed:
        dict { label : fixed_val }

    Style of the function vaguely inspired from here
    https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
    """
    logg = logging.getLogger(f"c.{__name__}.multigram")
    logg.debug(f"Start multigram")
    logg.debug(f"do_change {do_change} fixed {fixed}")

    if not ax:
        ax = plt.gca()
    #  im = ax.hist([1,2])
    # use https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.subplots.html
    # if you need the fig as well?

    if len(do_change) == 1:
        single_hist(hyper_params_grid, do_change, fixed, ax, **kwargs)
    elif len(do_change) == 2:
        double_hist(hyper_params_grid, do_change, fixed, ax, **kwargs)
    elif len(do_change) == 3:
        triple_hist(hyper_params_grid, do_change, fixed, ax, **kwargs)
    else:
        logg.critical(f"You can change from 1 to 3 hyper parameters")


def single_hist(hyper_params_grid, do_change, fixed, ax, **kwargs):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.single_hist")
    logg.debug(f"Start single_hist")


def double_hist(hyper_params_grid, do_change, fixed, ax, **kwargs):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.double_hist")
    logg.debug(f"Start double_hist")


def triple_hist(hyper_params_grid, do_change, fixed, ax, **kwargs):
    """

    Instead of just points on the line, might use swarmplot
    https://seaborn.pydata.org/generated/seaborn.swarmplot.html
    """
    logg = logging.getLogger(f"c.{__name__}.triple_hist")
    logg.debug(f"Start triple_hist")


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

    recap = f"python3 plot_grid_search.py"
    recap += f" --seed {myseed}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    run_plot_grid_search()


if __name__ == "__main__":
    main()
