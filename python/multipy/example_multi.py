import argparse
import logging

import numpy as np
import multiprocessing as mp

from random import seed
from timeit import default_timer as timer
from os import cpu_count
from os import getppid
from os import getpid
from time import sleep
from random import random


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_output",
        type=str,
        default="outfile_",
        help="basename of the output file",
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


def func_info(ident):
    """Returns some info on who did what
    """
    # delay more the first calls
    delay = random() * (cpu_count() * 2 - ident)
    sleep(delay)
    return ident, getpid(), getppid(), delay


def func_info_dict(ident):
    """Returns some info on who did what, as a dict
    """
    # delay more the first calls
    delay = random() * (cpu_count() * 2 - ident)
    sleep(delay)
    res_dict = {"id": ident, "pid": getpid(), "ppid": getppid(), "delay": delay}
    return res_dict


def cube(x):
    return x ** 3


def func_write_file(template_output, a, b):
    """A function that writes to a file

    All files will have different names
    """
    filename = template_output.format(a, b)
    with open(filename, "w") as f:
        f.write(f"Written by process {getpid()} at istant {timer():.6f}")

    return 0


def pool_example_1():
    """ https://sebastianraschka.com/Articles/2014_multiprocessing.html
    """
    logg = logging.getLogger(f"c.{__name__}.pool_example_1")
    logg.info(f"There are {cpu_count()} CPUs available")

    pool = mp.Pool(processes=cpu_count())
    results = [pool.apply_async(cube, args=(x,)) for x in range(1, 7)]
    output = [p.get() for p in results]
    logg.info(output)


def pool_example_2():
    """ 
    """
    logg = logging.getLogger(f"c.{__name__}.pool_example_2")
    logg.info(f"There are {cpu_count()} CPUs available")

    t1 = timer()
    pool = mp.Pool(processes=cpu_count())
    t2 = timer()
    #  results = [pool.apply_async(func_info, args=(x,)) for x in range(cpu_count() * 2)]
    results = [
        pool.apply_async(func_info_dict, args=(x,)) for x in range(cpu_count() * 2)
    ]
    t3 = timer()
    output = [p.get() for p in results]
    t4 = timer()

    tot_delay = 0
    for o in output:
        #  tot_delay += o[3]
        tot_delay += o["delay"]
        logg.info(o)

    logg.info(f"Total delay in the functions {tot_delay}")
    logg.info(f"t1 t2 {t2-t1:.6f}")
    logg.info(f"t2 t3 {t3-t2:.6f}")
    logg.info(f"t3 t4 {t4-t3:.6f}")


def pool_example_3(path_output):
    """Test what happens if you write a file in the called function
    """
    logg = logging.getLogger(f"c.{__name__}.pool_example_3")
    logg.info(f"There are {cpu_count()} CPUs available")

    template_output = path_output + "{}_{}.txt"
    # build the params for the function
    arguments = []
    arguments.append((template_output, 1, 3))
    arguments.append((template_output, 2, 5))
    arguments.append((template_output, 3, 7))

    pool = mp.Pool(processes=cpu_count())
    results = [pool.apply_async(func_write_file, args=a) for a in arguments]
    t3 = timer()
    output = [p.get() for p in results]
    t4 = timer()
    logg.info(f"t3 t4 {t4-t3:.6f}")


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

    path_output = args.path_output

    recap = f"python3 example_multi.py"
    recap += f" --path_output {path_output}"
    recap += f" --seed {myseed}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    #  pool_example_1()
    pool_example_2()
    #  pool_example_3(path_output)


if __name__ == "__main__":
    main()
