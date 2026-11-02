
import streamlit as st

st.set_page_config(
    page_title="TerraTime 4D",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 TerraTime 4D")
st.subheader("Scientific Earth Analog Discovery Platform")

st.write(
    "Discover potentially overlooked locations on Earth "
    "that could help us understand the Moon and Mars."
)

st.divider()

st.header("Mission Configuration")

planet = st.selectbox(
    "Select planetary target",
    ["Moon", "Mars"]
)

mission = st.selectbox(
    "Select mission objective",
    [
        "Rover Mobility",
        "Landing Site Assessment",
        "Geological Research",
        "Resource Exploration",
        "Robotics and Construction",
        "Human Operations"
    ]
)

st.subheader("Selected Mission")
st.write("Planet:", planet)
st.write("Mission:", mission)

st.info(
    "Global Earth discovery and scientific comparison "
    "will be developed in the next stages."
)

st.success("TerraTime 4D is running!")
