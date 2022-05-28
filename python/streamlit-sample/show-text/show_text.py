import streamlit as st

SAMPLE_TEXT = [[f"{f'{s*10} '*10}{i}" for i in range(1, 3 + 1)] for s in "abcde"]

with st.sidebar:
    show_translated = st.checkbox("Show translated text")


st.title("Text side by side")

# st.write(SAMPLE_TEXT)

for par in SAMPLE_TEXT:

    if show_translated:
        col1, col2, col3 = st.columns(3)
        col1.write(par[0])
        col2.write(par[1])
        col3.write(par[2])
    else:
        col1, col2 = st.columns(2)
        col1.write(par[0])
        col2.write(par[1])
        col2.write("And also something else!")

st.write("There is method to the madness, stay tuned.")
