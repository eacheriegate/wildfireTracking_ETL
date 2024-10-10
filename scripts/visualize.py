import os
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from IPython.display import display
import webbrowser

# File paths
PROCESSED_FIRE_FILE = "data/processed/VIIRS_FireData_LACo.shp"
LA_COUNTY_BOUNDARY_FILE = "data/processed/LA_County_Boundary.shp"

def format_time(acq_time):
    """Convert acq_time from HHMM to HH:MM:SS format."""
    acq_time_str = str(acq_time).zfill(4)  # Ensure acq_time has 4 digits
    return f"{acq_time_str[:2]}:{acq_time_str[2:]}:00"  # Format as HH:MM:SS

def create_interactive_fire_map(fire_data_file, boundary_file):
    # Load the fire data and the LA County boundary shapefile
    fire_gdf = gpd.read_file(fire_data_file)
    la_boundary_gdf = gpd.read_file(boundary_file)

    # Create a base map centered on LA County with no default tiles
    la_center = [34.0522, -118.2437]  # Lat/Long of LA County
    fire_map = folium.Map(location=la_center, zoom_start=8, tiles=None)

    # Add CartoDB Positron (Light) as the default tile layer
    folium.TileLayer('cartodb positron', name="Light Mode Tile", attr='Map data © OpenStreetMap contributors, © CARTO').add_to(fire_map)

    # Add CartoDB Dark Matter (Dark) as another option
    folium.TileLayer('cartodbdark_matter', name="Dark Mode Tile", attr='Map data © OpenStreetMap contributors, © CARTO').add_to(fire_map)

    # Add LA County boundary as a separate layer with a more subtle outline
    folium.GeoJson(
        la_boundary_gdf,
        name="LA County Boundary",
        style_function=lambda feature: {
            'color': '#3388ff',  # Lighter blue outline
            'weight': 2,         # Thinner border
            'fillOpacity': 0     # No fill
        }
    ).add_to(fire_map)

    # Add a feature group for the fire data (this can be toggled in the LayerControl)
    fire_layer = folium.FeatureGroup(name="Active Fires")

    # Define color scheme based on fire radiative power (frp)
    def get_marker_style(row):
        frp = row.get('frp', 0)  # Fire radiative power (intensity)
        if frp > 1.5:
            return {"color": "#d73027", "radius": 10, "fillOpacity": 0.7}  # Red for high intensity
        elif frp > 0.5:
            return {"color": "#fc8d59", "radius": 8, "fillOpacity": 0.6}  # Orange for medium intensity
        else:
            return {"color": "#fee08b", "radius": 6, "fillOpacity": 0.5}  # Yellow for low intensity

    # Add markers to the map for each fire event
    for _, row in fire_gdf.iterrows():
        lat = row['geometry'].y
        lon = row['geometry'].x

        # Adjust marker size and color based on fire intensity (frp)
        style = get_marker_style(row)

         # Format acq_time from HHMM to HH:MM:SS
        formatted_time = format_time(row['acq_time'])

        # Enhanced popup with more information
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; background-color: #f9f9f9; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px #888;">
            <b>Date:</b> {row['acq_date']}<br>
            <b>Time:</b> {formatted_time}<br>
            <b>Brightness:</b> {row.get('bright_ti4', 'N/A')} K<br>
            <b>FRP:</b> {row.get('frp', 'N/A')}
        </div>
        """
        popup = folium.Popup(popup_html, max_width=300)

        # Add marker to the fire layer
        folium.CircleMarker(
            location=(lat, lon),
            radius=style["radius"],
            popup=popup,
            color=style["color"],
            fill=True,
            fill_opacity=style["fillOpacity"]
        ).add_to(fire_layer)

    # Add the fire layer to the map
    fire_layer.add_to(fire_map)

    # Optionally, add a heatmap layer for fire intensity
    heat_data = [[row['geometry'].y, row['geometry'].x, row.get('frp', 0)] for _, row in fire_gdf.iterrows()]
    HeatMap(heat_data, name="Fire Intensity Heatmap", radius=15).add_to(fire_map)

    # Add LayerControl to toggle layers on and off
    folium.LayerControl().add_to(fire_map)

    # Custom legend for fire markers
    legend_html = """
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: 100px; 
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; padding: 10px;">
     <b>Active Fire Intensity Guide</b> <br>
     <i style="background: #d73027; border-radius: 50%; width: 12px; height: 12px; display: inline-block;"></i> High Intensity Fire<br>
     <i style="background: #fc8d59; border-radius: 50%; width: 12px; height: 12px; display: inline-block;"></i> Medium Intensity Fire<br>
     <i style="background: #fee08b; border-radius: 50%; width: 12px; height: 12px; display: inline-block;"></i> Low Intensity Fire<br>
     </div>
    """
    fire_map.get_root().html.add_child(folium.Element(legend_html))

    # Display the map
    return fire_map

# Call the function to create the map and display it
if __name__ == "__main__":
    fire_map = create_interactive_fire_map(PROCESSED_FIRE_FILE, LA_COUNTY_BOUNDARY_FILE)
    display(fire_map)

    # Save the map as an HTML file
    html_file = "fire_interactive_map.html"
    fire_map.save(html_file)
    print(f"Map saved to {html_file}")

    # Upload to S3 bucket automatically
    bucket_name = 'viirs-active-fire-map'
    os.system(f"aws s3 cp {html_file} s3://{bucket_name}/fire_interactive_map.html")
    print(f"Uploaded {html_file} to s3://{bucket_name}/fire_interactive_map.html")

    # Open web map in web browser
    #webbrowser.open(html_file)
    #print("Map opened in your default web browser.")
