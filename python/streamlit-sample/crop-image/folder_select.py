"""Select a folder."""

from functools import partial
from pathlib import Path

import streamlit as st
from loguru import logger as lg


def partial_print(a):
    """Just print this."""
    lg.debug(a)


def change_curr_path(path):
    """Set the new current path in the state."""
    st.session_state["internal__curr_path"] = path
    lg.debug(f"Changing to {path}")
    # if we change dir, we want to wait for a confirmation
    st.session_state["internal__is_valid"] = False


def is_dir_safe(path: Path):
    """Check if a path is dir, recovering from PermissionError."""
    is_dir = False
    try:
        is_dir = path.is_dir()
        # lg.debug(f"{path.parts[-1]} {is_dir=}")
    except PermissionError as e:
        lg.debug(f"{e}")
    return is_dir


def print_stat():
    """Print something when the widget changes."""
    lg.debug("printing")


def folder_selector():
    """Select a folder."""
    # initialize the current path and set it as not accepted
    if "internal__curr_path" not in st.session_state:
        st.session_state["internal__curr_path"] = Path(".").absolute().expanduser()
    if "internal__is_valid" not in st.session_state:
        st.session_state["internal__is_valid"] = False

    with st.expander("Select a folder"):
        # st.title("Select a folder")

        # jump to a specific location
        lg.debug(f"Now have {st.session_state['internal__curr_path']}")
        jump_str = st.text_input(
            "Current folder:", value=st.session_state["internal__curr_path"]
        )
        if jump_str:
            jump_path = Path(jump_str)
            lg.debug(f"Maybe jumping to {jump_path}")
            if is_dir_safe(jump_path):
                # FileNotFoundError FIXME obiously this must exist
                lg.debug(f"      jumping to {jump_path}")
                st.session_state["internal__curr_path"] = jump_path
            else:
                lg.debug(f"  Not jumping to {jump_path}")
                st.warning(f"Not Found: {jump_path}")

        # extract it for ease of use
        curr_path = st.session_state["internal__curr_path"]
        st.text(f"Current folder: {curr_path}")

        # button to accept the current path
        done = st.button("Done")

        col1, col2 = st.columns(2)
        with col1:
            # st.header("Go up")
            st.write("Go up")

            # build the base of the path
            inc_path = Path(curr_path.parts[0])
            # add the first button
            inc_part = partial(change_curr_path, inc_path)
            st.button(f"{inc_path}", on_click=inc_part)

            for el_str in curr_path.parts[1:]:
                # build the progressive path
                inc_path = inc_path.joinpath(el_str)

                # build a button that leads you to this path
                inc_part = partial(change_curr_path, inc_path)
                st.button(f"{el_str}", on_click=inc_part)

        with col2:
            # st.header("Go down")
            st.write("Go down")

            # get all the children of the current path
            paths: list[Path] = list(curr_path.iterdir())
            dirs = sorted([p for p in paths if is_dir_safe(p)])
            files = sorted([p for p in paths if not is_dir_safe(p)])

            # add the folders
            if len(dirs) > 0:
                st.write(f"Dirs")
                for path in dirs:
                    inc_part = partial(change_curr_path, path)
                    st.button(f"{path.name}", on_click=inc_part)

            # add the files
            if len(files) > 0:
                st.write(f"Files")
                for path in files:
                    st.button(f"{path.name}")

        if done or st.session_state["internal__is_valid"]:
            st.session_state["internal__is_valid"] = True
            return st.session_state["internal__curr_path"]


def main():
    """Try the folder selector."""
    folder = folder_selector()

    st.write(f"You picked {folder}")

    st.slider("Slide me.")


if __name__ == "__main__":
    main()
