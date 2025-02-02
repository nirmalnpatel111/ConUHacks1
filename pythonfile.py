# import pandas as pd
# import folium
# from collections import defaultdict

# # Load CSV file
# df = pd.read_csv("one.csv")  # Replace with your actual filename

# # Ensure Latitude & Longitude are numeric
# df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
# df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# # Drop rows with missing coordinates
# df = df.dropna(subset=["Latitude", "Longitude"])
# print("Rows with missing coordinates have been removed.")

# # Create a map centered on Montreal
# m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=12)

# # Group data by intersection and coordinates
# location_data = defaultdict(lambda: defaultdict(int))

# for _, row in df.iterrows():
#     key = (row["Nom_Intersection"], row["Longitude"], row["Latitude"], row["Date"])
#     location_data[key][row["Description_Code_Banque"]] += row["Amount"]

# # Add markers with grouped information
# for (intersection, lon, lat, date), vehicles in location_data.items():
#     vehicle_info = "<br>".join([f"{v}: {count}" for v, count in vehicles.items()])
#     popup_content = f"""
#     <b>Intersection:</b> {intersection}<br>
#     <b>Date:</b> {date}<br>
#     <b>Counts:</b><br>{vehicle_info}
#     """
#     folium.Marker(
#         location=[lat, lon],
#         popup=folium.Popup(popup_content, max_width=300),
#         tooltip=intersection  # Shows intersection name on hover
#     ).add_to(m)

# # Save the map as an HTML file
# m.save("montreal_collision_map.html")

# print("Map created! Open 'montreal_collision_map.html' in your browser.")

import pandas as pd
import folium
from collections import defaultdict

# Load CSV file
df = pd.read_csv("one.csv")  # Replace with your actual filename

# Ensure Latitude & Longitude are numeric
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Drop rows with missing coordinates
df = df.dropna(subset=["Latitude", "Longitude"])
print("Rows with missing coordinates have been removed.")

# Create a map centered on Montreal
m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=12)

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
    ).add_to(m)

# Save the map as an HTML file
m.save("montreal_collision_map.html")

print("Map created! Open 'montreal_collision_map.html' in your browser.")
