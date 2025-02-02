import pandas as pd
import folium
from folium.plugins import MarkerCluster
import requests

# Create basic map centered on mtl
montreal_map = folium.Map(location=[45.5017, -73.5673], zoom_start=12, prefer_canvas=True)

base_url = "https://donnees.montreal.ca/api/3/action/datastore_search"
resource_id = "05deae93-d9fc-4acb-9779-e0942b5e962f"
limit = 32000 # API restriction
offset = 0
all_records = []

#Fetch all data in chunks
while True:
    response = requests.get(base_url, params={"resource_id":  resource_id, "limit": limit, "offset": offset})
    json_file = response.json()
   
    #Extract records
    records = json_file["result"]["records"]

   # If no records are returned, break the loop
    if not records:
        break
   
    all_records.extend(records)
    offset += limit # Move to the next batch

#Convert to DataFrame
col_routieres = pd.DataFrame(all_records)

# Print the total num of records fetched
print(f"Total records fetched: {len(col_routieres)}")

# Convert DT_ACCDN to string and sxtract the year
col_routieres["YEAR"] = col_routieres["DT_ACCDN"].astype(str).str[:4]

# Remove rows where LOC_LAT or LOC_LONG is missing
col_routieres = col_routieres.dropna(subset=["LOC_LAT", "LOC_LONG","NB_MORTS", "NB_BLESSES_GRAVES", "NB_BLESSES_LEGERS"]) 
col_routieres = col_routieres[(col_routieres["LOC_LAT"] != 0) & (col_routieres["LOC_LONG"] != 0)]
col_routieres = col_routieres[(col_routieres["NB_MORTS"] != 0) | (col_routieres["NB_BLESSES_GRAVES"] != 0) | (col_routieres["NB_BLESSES_LEGERS"] != 0)]


# Convert data types to save memory
col_routieres["NB_MORTS"] = col_routieres["NB_MORTS"].astype("int8")
col_routieres["YEAR"] = col_routieres["YEAR"].astype("category")

# Create a dictionary to hold FeatureGroups for each year
year_groups = {}

# Iterate through unique years in dataset
for year in col_routieres["YEAR"].unique():
    # Filter crashes by year
    yearly_data = col_routieres[col_routieres["YEAR"] == year]

    # Create a cluster layer for this year
    cluster = MarkerCluster(name=f"Collisions in {year}").add_to(montreal_map)

    # Function to determine marker color
    def get_marker_color(fatalities, injuries, grave_injury):
        if fatalities > 0:
            return "red"  # Use red for fatalities
        elif injuries > 0:
            return "yellow"  # Use blue for injuries
        elif grave_injury > 0:
            return "blue"  # Use green for graves
        else:
            return "gray"  # Gray for no fatalities, injuries, or graves

    #Add markers to the cluster
    for _, row in yearly_data.iterrows():
        folium.CircleMarker(
            location=[row["LOC_LAT"], row["LOC_LONG"]],
            radius=6,
            color=get_marker_color(row["NB_MORTS"], row["NB_BLESSES_GRAVES"], row["NB_BLESSES_LEGERS"]),
            fill=True,
            fill_color=get_marker_color(row["NB_MORTS"], row["NB_BLESSES_GRAVES"], row["NB_BLESSES_LEGERS"]),
            fill_opacity=0.8,
            popup=folium.Popup(f"Year: {year} Fatalities: {row['NB_MORTS']} Grave Injuries: {row['NB_BLESSES_GRAVES']} Injuries: {row['NB_BLESSES_LEGERS']}", parse_html=True),
        ).add_to(cluster)

    # Save the final map
    montreal_map.save("collision_map.html")

    print("Collision map created: Open 'collision_map.html' in a browser.")