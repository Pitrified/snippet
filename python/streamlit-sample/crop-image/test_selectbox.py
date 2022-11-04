"""Test if a new list can be passed to a selectbox."""

import streamlit as st
from loguru import logger as lg

if "count" not in st.session_state:
    st.session_state["count"] = 0


def main():
    """Test if a new list can be passed to a selectbox."""
    st.title("Select box")

    curr = st.session_state["count"]

    st.write(f"Got {curr}")

    lst = list(range(curr, curr + 10))
    sel = st.selectbox("Select me", lst, index=curr)

    st.session_state["count"] += 1

    save_btn = st.button("Save")

    st.write(f"Now {sel} {save_btn}")


if __name__ == "__main__":
    main()
