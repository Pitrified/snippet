import argparse
import logging

import requests
import shutil

from random import seed as rseed
from timeit import default_timer as timer
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def parse_arguments():
    """Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-b",
        "--bzid",
        type=str,
        default="5wyb3",
        help="Id to download",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module"""
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def setup_env():
    setup_logger()

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 pic_downloader.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def parse_tabbz(bz_ID):
    """TODO: what is parse_tabbz doing?"""
    logg = logging.getLogger(f"c.{__name__}.parse_tabbz")
    logg.debug(f"Start parse_tabbz")

    bz_url = f"https://tab.bz/{bz_ID}"
    logg.debug(f"bz_url: {bz_url}")

    # driver = webdriver.Chrome(executable_path="/home/pietro/.local/bin/chromedriver")
    driver = webdriver.Chrome()
    driver.get(bz_url)

    # waits till the element with the specific id appears
    WebDriverWait(driver, 50).until(
        EC.visibility_of_element_located((By.ID, "publicList"))
    )
    src = driver.page_source  # gets the html source of the page
    # logg.debug(f"src: {src}")

    # parse the soup
    soup = BeautifulSoup(src, "html.parser")
    # logg.debug(f"soup.prettify():\n{soup.prettify()}")

    # find the saved urls
    el = soup.find_all("a", class_="externalLink")
    # logg.debug(f"el: {el}")
    # for e in el: logg.debug(f"e['href']: {e['href']}")

    urls = [e["href"] for e in el]

    return urls


def download_pic(pic_url, out_fold_path, session):
    """TODO: what is download_pic doing?"""
    logg = logging.getLogger(f"c.{__name__}.download_pic")
    logg.debug(f"Start download_pic pic_url: {pic_url}")
    # logg.debug(f"pic_url: {pic_url}")

    pic_url_path = Path(pic_url)
    # logg.debug(f"pic_url_path: {pic_url_path}")

    # list of valid extensions
    valid_pic_ext = [".jpg", ".png"]

    pic_name = pic_url_path.name
    # logg.debug(f"pic_name: {pic_name}")

    pic_ext = pic_url_path.suffix
    # logg.debug(f"pic_ext: {pic_ext}")

    full_path = out_fold_path / pic_name
    # logg.debug(f"full_path: {full_path}")

    with session.get(pic_url) as response:
        with open(full_path, "wb") as f:
            f.write(response.content)


def run_pic_downloader(args):
    """TODO: What is pic_downloader doing?"""
    logg = logging.getLogger(f"c.{__name__}.run_pic_downloader")
    logg.debug(f"Starting run_pic_downloader")

    # bz_ID = "3sgfv"
    # bz_ID = "5wyb3"
    bz_ID = args.bzid

    # get the pic urls to download
    pic_urls = parse_tabbz(bz_ID)
    # logg.debug(f"pic_urls: {pic_urls}")

    # create the output folder
    out_fold_path = Path("~/picdownloaderout").expanduser().absolute()
    logg.debug(f"out_fold_path: {out_fold_path}")
    if not out_fold_path.exists():
        out_fold_path.mkdir()

    # open the session for the downloads
    session = requests.Session()

    for pic_url in pic_urls:
        download_pic(pic_url, out_fold_path, session)


if __name__ == "__main__":
    args = setup_env()
    run_pic_downloader(args)

# TODO
# Get the number of links from tab.bz
# Send a warning if some links are not images
