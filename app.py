import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon, Point
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import json
import xml.etree.ElementTree as ET
from geopy.distance import geodesic

# Incluir o CSS personalizado
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

st.title("Map Area Measurement App")

# Inicializar o mapa
m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

# Função para salvar os pontos em um arquivo JSON
def save_points(points, filename):
    with open(filename, 'w') as f:
        json.dump(points, f)

# Função para carregar pontos de um arquivo JSON
def load_points(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Função para exportar o mapa e os dados para PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Map Area Measurement Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()

# Função para carregar pontos de um arquivo KML
def load_kml(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    points = []
    for placemark in root.findall('.//kml:Placemark', namespace):
        coordinates = placemark.find('.//kml:coordinates', namespace).text.strip()
        lon, lat, _ = map(float, coordinates.split(','))
        points.append((lat, lon))
    return points

# Função para calcular a distância entre dois pontos
def calculate_distance(point1, point2):
    return geodesic(point1, point2).meters

# Função para manipular cliques no mapa
if "points" not in st.session_state:
    st.session_state["points"] = []

st.write("Click on the map to add points.")
output = st_folium(m, width=700, height=500)

# Obter pontos clicados
if output["last_clicked"] is not None:
    lat, lon = output["last_clicked"]["lat"], output["last_clicked"]["lng"]
    st.session_state["points"].append((lat, lon))

# Adicionar marcadores para cada ponto
for point in st.session_state["points"]:
    folium.Marker(location=point).add_to(m)

st_folium(m, width=700, height=500)

# Entrada para o nome do mapa
map_name = st.text_input("Map Name")

# Exibir a lista de pontos
st.write("Coordinates of clicked points:")
for point in st.session_state["points"]:
    st.write(f"{point[0]}, {point[1]}")

# Calcular a área do polígono formado pelos pontos
if len(st.session_state["points"]) >= 3:
    polygon = Polygon(st.session_state["points"])
    area = polygon.area / 10000  # Convertendo de m² para hectares
    st.write(f"Area: {area:.2f} hectares")

    # Calcular distâncias entre pontos consecutivos
    distances = []
    for i in range(1, len(st.session_state["points"])):
        distance = calculate_distance(st.session_state["points"][i-1], st.session_state["points"][i])
        distances.append(distance)
    total_distance = sum(distances) / 1000  # Convertendo de metros para quilômetros
    st.write(f"Total Distance: {total_distance:.2f} km")

    # Criar DataFrame
    df = pd.DataFrame(st.session_state["points"], columns=["Latitude", "Longitude"])

    # Gráfico de dispersão
    fig_scatter = px.scatter(df, x="Longitude", y="Latitude", title="Scatter Plot of Points")
    st.plotly_chart(fig_scatter)

    # Gráfico de linhas (assumindo uma ordem ou caminho dos pontos)
    fig_line = px.line(df, x="Longitude", y="Latitude", title="Line Plot of Points")
    st.plotly_chart(fig_line)

    # Gráfico de área (mostrando área cumulativa, se necessário)
    df["Index"] = range(len(df))
    fig_area = px.area(df, x="Index", y=["Latitude", "Longitude"], title="Area Plot of Points")
    st.plotly_chart(fig_area)

# Opções de salvar e carregar pontos
if st.button("Save Points"):
    save_points(st.session_state["points"], "points.json")
    st.success("Points saved successfully.")

if st.button("Load Points"):
    st.session_state["points"] = load_points("points.json")
    st.success("Points loaded successfully.")

# Opção para importar KML
uploaded_file = st.file_uploader("Choose a KML file", type="kml")
if uploaded_file is not None:
    kml_points = load_kml(uploaded_file)
    st.session_state["points"].extend(kml_points)
    st.success("KML file loaded successfully.")

# Opção para exportar para PDF
if st.button("Export to PDF"):
    pdf.add_page()
    pdf.chapter_title("Map Name:")
    pdf.chapter_body(map_name)
    pdf.chapter_title("Coordinates of clicked points:")
    for point in st.session_state["points"]:
        pdf.chapter_body(f"{point[0]}, {point[1]}")

    if len(st.session_state["points"]) >= 3:
        pdf.chapter_title("Area Measurement")
        pdf.chapter_body(f"Area: {area:.2f} hectares")
        pdf.chapter_body(f"Total Distance: {total_distance:.2f} km")

    pdf.output("report.pdf")
    st.success("Report exported successfully.")
