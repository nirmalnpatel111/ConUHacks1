import pandas as pd
import folium
import geopandas as gdp
from folium.plugins import FastMarkerCluster

parkingSigns = pd.read_pickle("Datasets/parking_signs_processed.pkl")

map = folium.Map(location=[45.5017, -73.5673], 
                 zoom_start=24,
                 prefer_canvas=True)

segments = []

for _, row in parkingSigns.iterrows():
    segment = [(row['segmentX1'], row['segmentY1']), (row['segmentX2'], row['segmentY2'])]
    folium.PolyLine(segment, weight=2.5, opacity=1, color="blue").add_to(map)

cluster = FastMarkerCluster(
    [[row['segmentY1'], row['segmentX1']] for _, row in parkingSigns.iterrows()] +
    [[row['segmentY2'], row['segmentX2']] for _, row in parkingSigns.iterrows()]
).add_to(map)

map.save("maps/traffic_signs.html")