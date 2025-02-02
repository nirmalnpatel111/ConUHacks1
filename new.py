import pandas as pd
import folium
from collections import defaultdict
import geopandas as gpd
from shapely.ops import transform
from pyproj import Transformer
import branca
from folium.plugins import FeatureGroupSubGroup
from folium.plugins import FastMarkerCluster

# Load CSV file
df = pd.read_csv("one.csv")  # Replace with your actual filename

# Ensure Latitude & Longitude are numeric
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Drop rows with missing coordinates
df = df.dropna(subset=["Latitude", "Longitude"])
print("Rows with missing coordinates have been removed.")

# Create a base map
m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=12,  prefer_canvas=True)

# Create feature groups for toggling
collision_layer = folium.FeatureGroup(name="Collision Data", show=True).add_to(m)
geojson_layer = folium.FeatureGroup(name="GeoJSON Data", show=True).add_to(m)
traffic_signs_layer = folium.FeatureGroup(name="Traffic Signs", show=True).add_to(m)

# Group data by intersection and coordinates (ignoring Date in the key)
location_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for _, row in df.iterrows():
    key = (row["Nom_Intersection"], row["Longitude"], row["Latitude"])
    location_data[key][row["Date"]][row["Description_Code_Banque"]] += row["Amount"]

# Add markers with combined date info
for (intersection, lon, lat), dates in location_data.items():
    all_dates_info = ""
    
    for date, vehicles in dates.items():
        vehicle_info = "<br>".join([f"{v}: {count}" for v, count in vehicles.items()])
        all_dates_info += f"<b>Date:</b> {date}<br>{vehicle_info}<br><br>"

    popup_content = f"""
    <b>Intersection:</b> {intersection}<br>
    {all_dates_info}
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_content, max_width=400),
        tooltip=intersection  # Shows intersection name on hover
    ).add_to(collision_layer)

# Download JSON data
gdf = gpd.read_file("https://montreal-prod.storage.googleapis.com/resources/7a59762e-ac17-4a9f-bb2a-12e2d5673906/densitepu.geojson?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=test-datapusher-delete%40amplus-data.iam.gserviceaccount.com%2F20250201%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250201T212302Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&x-goog-signature=b9d3513dcb8bb569c802c02ec6cfae960e146c6e671c1963b4a8da240fc610e94be402f0ba4a507a24bc06f33d4aceb846eac4afac5e201150f1b0d6c4615cd44888712f9c6643ca5f621e3eac9d5d3e010dec3c0be1aecad32a31d4609659cadd083accb2561abfdcbb22f090ded48d7e5e1dc97c36f35718eba1484dff2aabf9944d82eea858bfd38c85a0719bfe2014476bf97c19623e8d68b8d4909f29526708f8994bc8255dcc7fc56f602795d52a3b9aa5ece7f2182d608ca4d19dd5217fe80a212c857c2466fdfde128a4d2fd7cff1547d1bd97bc3dc94e78e5773a8f28a0274e7c9c46c9579c5b8c1c60b9c4ecc566350c38c2b6ec3195a1150158de")

# Convert to proper format
transformer = Transformer.from_crs("EPSG:32188", "EPSG:4326", always_xy=True)
gdf["geometry"] = gdf["geometry"].apply(lambda geom: transform(transformer.transform, geom))
gdf = gdf.to_json()

# Create a style function to add colors based on index
colormap = branca.colormap.linear.OrRd_09.scale(1, 14)
colormap.caption = "Indice Density Scale"
colormap.add_to(m)

def style_function(feature):
    indice = feature["properties"].get("indice", 0)
    if indice == 0 or indice == 0.1:
        color = "green"
    elif indice == 0.2:
        color = "grey"
    else:
        color = colormap(indice)
    
    return {
        "fillColor": color,
        "color": "black",  # Outline color
        "weight": 1,
        "fillOpacity": 0.7
    }

# Load JSON data onto map
folium.GeoJson(gdf, 
               style_function=style_function, 
               tooltip=folium.GeoJsonTooltip(fields=["indice"],
                                             localize=True,
                                             sticky=True)).add_to(geojson_layer)

# Load parking signs data
parkingSigns = pd.read_pickle("Datasets/parking_signs_processed.pkl")

for _, row in parkingSigns.iterrows():
    segment = [(row['segmentX1'], row['segmentY1']), (row['segmentX2'], row['segmentY2'])]
    folium.PolyLine(segment, weight=2.5, opacity=1, color="blue").add_to(traffic_signs_layer)

cluster = FastMarkerCluster(
    [[row['segmentY1'], row['segmentX1']] for _, row in parkingSigns.iterrows()] +
    [[row['segmentY2'], row['segmentX2']] for _, row in parkingSigns.iterrows()]
).add_to(traffic_signs_layer)

# Add layer control
folium.LayerControl().add_to(m)

# Save the final combined map
m.save("new.html")

print("Map created! Open 'new.html' in your browser.")
