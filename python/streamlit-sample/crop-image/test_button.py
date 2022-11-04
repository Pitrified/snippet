"""Test when a button is true or false.

It will be true the run after you clicked it,
then false if you change something else.
"""

import streamlit as st

cl = st.button("click")

if cl:
    st.write("clicked")
else:
    st.write("not clicked")

st.slider("slide", 1, 10)
