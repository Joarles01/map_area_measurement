import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pandas as pd
import plotly.express as px

# Incluir o CSS diretamente no código
css = """
<style>
body {
    background-color: #f0f2f6;
}

.stApp {
    background-color: #f0f2f6;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
}

.stButton>button:hover {
    background-color: white;
    color: black;
    border: 2px solid #4CAF50;
}

.stTitle {
    color: #4CAF50;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.title("Map Area Measurement App")

# Initialize the map
m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

# Function to handle map clicks
if "points" not in st.session_state:
    st.session_state["points"] = []

st.write("Click on the map to add points.")
output = st_folium(m, width=700, height=500)

# Get clicked points
if output["last_clicked"] is not None:
    lat, lon = output["last_clicked"]["lat"], output["last_clicked"]["lng"]
    st.session_state["points"].append((lat, lon))

# Add markers for each point
for point in st.session_state["points"]:
    folium.Marker(location=point).add_to(m)

st_folium(m, width=700, height=500)

# Display the list of points
st.write("Coordinates of clicked points:")
for point in st.session_state["points"]:
    st.write(f"{point[0]}, {point[1]}")

# Calculate the area of the polygon formed by the points
if len(st.session_state["points"]) >= 3:
    polygon = Polygon(st.session_state["points"])
    area = polygon.area
    st.write(f"Area: {area:.2f} square meters")

    # Create DataFrame
    df = pd.DataFrame(st.session_state["points"], columns=["Latitude", "Longitude"])

    # Scatter plot
    fig_scatter = px.scatter(df, x="Longitude", y="Latitude", title="Scatter Plot of Points")
    st.plotly_chart(fig_scatter)

    # Line plot (assuming a path or order of points)
    fig_line = px.line(df, x="Longitude", y="Latitude", title="Line Plot of Points")
    st.plotly_chart(fig_line)

    # Area plot (showing cumulative area if needed)
    df["Index"] = range(len(df))
    fig_area = px.area(df, x="Index", y=["Latitude", "Longitude"], title="Area Plot of Points")
    st.plotly_chart(fig_area)
