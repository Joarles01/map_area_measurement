import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import json

# Função para incluir o CSS personalizado
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

# Exibir a lista de pontos
st.write("Coordinates of clicked points:")
for point in st.session_state["points"]:
    st.write(f"{point[0]}, {point[1]}")

# Calcular a área do polígono formado pelos pontos
if len(st.session_state["points"]) >= 3:
    polygon = Polygon(st.session_state["points"])
    area = polygon.area
    st.write(f"Area: {area:.2f} square meters")

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

# Opção para exportar para PDF
if st.button("Export to PDF"):
    pdf.add_page()
    pdf.chapter_title("Coordinates of clicked points:")
    for point in st.session_state["points"]:
        pdf.chapter_body(f"{point[0]}, {point[1]}")

    if len(st.session_state["points"]) >= 3:
        pdf.chapter_title("Area Measurement")
        pdf.chapter_body(f"Area: {area:.2f} square meters")

    pdf.output("report.pdf")
    st.success("Report exported successfully.")
