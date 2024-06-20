import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon

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
