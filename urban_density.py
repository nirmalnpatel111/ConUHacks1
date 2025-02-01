import folium
import geopandas as gpd
from shapely.ops import transform
from pyproj import Transformer
import branca

# Create a map
map = folium.Map(location=[45.5017, -73.5673], zoom_start=12)

# Download JSON data
json_file = gpd.read_file("https://montreal-prod.storage.googleapis.com/resources/7a59762e-ac17-4a9f-bb2a-12e2d5673906/densitepu.geojson?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=test-datapusher-delete%40amplus-data.iam.gserviceaccount.com%2F20250201%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250201T212302Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&x-goog-signature=b9d3513dcb8bb569c802c02ec6cfae960e146c6e671c1963b4a8da240fc610e94be402f0ba4a507a24bc06f33d4aceb846eac4afac5e201150f1b0d6c4615cd44888712f9c6643ca5f621e3eac9d5d3e010dec3c0be1aecad32a31d4609659cadd083accb2561abfdcbb22f090ded48d7e5e1dc97c36f35718eba1484dff2aabf9944d82eea858bfd38c85a0719bfe2014476bf97c19623e8d68b8d4909f29526708f8994bc8255dcc7fc56f602795d52a3b9aa5ece7f2182d608ca4d19dd5217fe80a212c857c2466fdfde128a4d2fd7cff1547d1bd97bc3dc94e78e5773a8f28a0274e7c9c46c9579c5b8c1c60b9c4ecc566350c38c2b6ec3195a1150158de")

#Convert to proper format
transformer = Transformer.from_crs("EPSG:32188", "EPSG:4326", always_xy=True)
json_file["geometry"] = json_file["geometry"].apply(lambda geom: transform(transformer.transform, geom))
json_file = json_file.to_json()

# Create a style function to add colors based on index
colormap = branca.colormap.linear.OrRd_09.scale(1, 14)

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
folium.GeoJson(json_file, 
               style_function=style_function, 
               tooltip=folium.GeoJsonTooltip(fields=["indice"],
                                             localize=True,
                                             sticky=True)).add_to(map)

map.save("maps/urban_density.html")