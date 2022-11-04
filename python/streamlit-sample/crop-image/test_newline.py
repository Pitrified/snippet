"""Test how to put a newline in a text."""

import streamlit as st
from loguru import logger as lg


def main():
    """Test how to put a newline in a text."""
    st.markdown("this text  \nhas newlines  \nin it")
    st.markdown("this text\nhas newlines\nin it")
    st.write("this text  \nhas newlines  \nin it")
    st.write("this text\nhas newlines\nin it")
    st.text("this text\nhas newlines\nin it")


if __name__ == "__main__":
    main()
