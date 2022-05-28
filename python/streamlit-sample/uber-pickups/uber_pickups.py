import numpy as np
import pandas as pd  # type: ignore
import streamlit as st


DATE_COLUMN = "date/time"
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


def lowercase(x):
    return str(x).lower()


@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


# Title bro
st.title("Uber pickups in NYC")

# Create a text element and let the reader know the data is loading.
data_load_state = st.text("Loading data...")
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

########################################################################################
# Show data with checkbox to toggle
if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)

########################################################################################
# Histogram
st.subheader("Number of pickups by hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
st.bar_chart(hist_values)

########################################################################################
# # Maps
# st.subheader("Map of all pickups")
# st.map(data)

########################################################################################
# Filter data

# # hour_to_filter = 17
# hour_to_filter = st.slider("hour", 0, 23, 17)  # min: 0h, max: 23h, default: 17h
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
# st.subheader(f"Map of all pickups at {hour_to_filter}:00")
# st.map(filtered_data)

########################################################################################
# Start messing with things

# use placeholder
map_filter_header = st.subheader("Map of all pickups at some time")
hour_to_filter_2 = st.slider("Slide to change the pickup hour:", 0, 23, 17, key="htf2")
map_filter_header.subheader(f"Map of all pickups at {hour_to_filter_2}:00")
filtered_data_2 = data[data[DATE_COLUMN].dt.hour == hour_to_filter_2]
st.map(filtered_data_2)

# # doesn't work
# contain_3 = st.container()
# hour_to_filter_3 = st.slider("Slide to change the pickup hour:", 0, 23, 17, key="htf3")
# st.subheader(f"Map of all pickups at {hour_to_filter_3}:00")
# contain_3.write(hour_to_filter_3)
# filtered_data_3 = data[data[DATE_COLUMN].dt.hour == hour_to_filter_3]
# st.map(filtered_data_3)

########################################################################################
# Session states and columns
st.subheader("Counter Example using Callbacks")
if "count" not in st.session_state:
    st.session_state.count = 0

increment_value = st.number_input("Enter a value", value=0, step=1)


def increment_counter(increment_value):
    st.session_state.count += increment_value


col1, col2 = st.columns(2)

with col1:
    increment = st.button(
        "Increment", on_click=increment_counter, args=(increment_value,)
    )

with col2:
    decrement = st.button(
        "Decrement",
        on_click=increment_counter,
        kwargs=dict(increment_value=-increment_value),
    )

st.write("Count = ", st.session_state.count)
