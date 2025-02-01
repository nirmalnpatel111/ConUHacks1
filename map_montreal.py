
import folium

# Create basic map centered on mtl
montreal_map = folium.Map(location=[45.5017, -73.5673], zoom_start=12)

# Save map as html file
montreal_map.save("montreal_map.html")

print("Map has been created: Open 'montreal_map.html' in a browser.")

#