"""Load an epub and extract the chapters.

https://stackoverflow.com/questions/10908877/extracting-a-zipfile-to-memory
"""
from typing import (
    cast,
    IO,
)
from zipfile import ZipFile

from bs4 import BeautifulSoup  # type: ignore
import streamlit as st

VALID_EBOOK_EXT = [".epub"]
VALID_CHAP_EXT = ["xhtml", "xml", "html"]

st.title("Load and show an epub")

epub_file = cast(IO[bytes], st.file_uploader("Choose a file", type=VALID_EBOOK_EXT))

# wait for a file to be loaded
if epub_file is not None:

    # read it in memory
    input_zip = ZipFile(epub_file)

    # get the file list
    st.write(input_zip.namelist())

    # ch_file_name = "OPS/main3.xml"
    ch_file_name = "ch_0003.xhtml"

    ch_content_bytes = input_zip.read(ch_file_name)
    # st.write(ch_content_bytes[:300])
    # print(f"{type(ch_content_bytes)}")

    # ch_content_test = """<html><head><title>The Dormouse's story</title></head>
    # <body>
    # <p class="title"><b>The Dormouse's story</b></p>
    # <p class="story">Once upon a time there were three little sisters; and their names were
    # <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
    # <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
    # <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
    # and they lived at the bottom of a well.</p>
    # <p class="story">...</p>
    # """

    soup = BeautifulSoup(ch_content_bytes, features="html.parser")
    # soup = BeautifulSoup(ch_content_test, features="html.parser")
    # if soup is not None:
    #     st.write("Some soup found.")
    #     st.write(soup.prettify()[:200])
    #     print(soup.prettify())
    # else:
    #     st.write("No soup found.")

    body = soup.body
    for i, par in enumerate(body.find_all("p")):
        st.write(par.string)

else:
    st.write("Drop a file!")
