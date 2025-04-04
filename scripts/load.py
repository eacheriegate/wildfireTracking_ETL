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
    acq_time_str = str(acq_time).zfill(4) 
    return f"{acq_time_str[:2]}:{acq_time_str[2:]}:00" 

def create_interactive_fire_map(fire_data_file, boundary_file):
    fire_gdf = gpd.read_file(fire_data_file)
    la_boundary_gdf = gpd.read_file(boundary_file)

    # Create base map centered on LA County
    la_center = [34.0522, -118.2437]
    fire_map = folium.Map(location=la_center, zoom_start=8, tiles=None)

    # Add light, dark, and satellite imagery as base tile layers
    folium.TileLayer('Esri.WorldImagery', name="Satellite Imagery", attr="Esri World Imagery").add_to(fire_map)
    folium.TileLayer('cartodb positron', name="Light Mode Tile", attr='Map data © OpenStreetMap contributors, © CARTO').add_to(fire_map)
    folium.TileLayer('cartodbdark_matter', name="Dark Mode Tile", attr='Map data © OpenStreetMap contributors, © CARTO').add_to(fire_map)

    # Add LA County boundary
    folium.GeoJson(
        la_boundary_gdf,
        name="LA County Boundary",
        style_function=lambda feature: {
            'color': '#3388ff',  # Lighter blue outline
            'weight': 2,         # Thinner border
            'fillOpacity': 0     # No fill
        }
    ).add_to(fire_map)

    # Add fire data
    fire_layer = folium.FeatureGroup(name="Fires/Hotspots")

    # FRP color scheme
    def get_marker_style(row):
        frp = row.get('frp', 0)
        
        # Define FRP thresholds
        high_intensity_threshold = 3.0
        medium_intensity_threshold = 1.5
        
        # Define marker styles based on FRP values
        if frp > high_intensity_threshold:
            return {"color": "#d73027", "radius": 10, "fillOpacity": 0.8}
        elif frp > medium_intensity_threshold:
            return {"color": "#fc8d59", "radius": 8, "fillOpacity": 0.6}
        else:
            return {"color": "#fee08b", "radius": 6, "fillOpacity": 0.5}

    # Add markers for each fire event
    for _, row in fire_gdf.iterrows():
        lat = row['geometry'].y
        lon = row['geometry'].x

        # Adjust marker size and color based on frp
        style = get_marker_style(row)

         # Format acq_time to HH:MM:SS
        formatted_time = format_time(row['acq_time'])

        # Pop up styling
        popup_html = f"""
        <div style="max-width: 600px; font-family: Arial, sans-serif; font-size: 12px; border-radius: 8px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3); word-break: break-word; background-color: transparent;">
            <table style="border: none; text-align: left; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background-color: #4a90e2; color: white;">
                        <th style="padding: 6px; text-align: left; border-bottom: 2px solid #fff; white-space: nowrap;">DATE</th>
                        <th style="padding: 6px; text-align: left; border-bottom: 2px solid #fff; white-space: nowrap;">TIME</th>
                        <th style="padding: 6px; text-align: left; border-bottom: 2px solid #fff; white-space: nowrap;">
                            FIRE HOTSPOTS<br>
                            <span style="font-size: 12px; color: #e0e0e0;">(bright_ti4)</span>
                        </th>
                        <th style="padding: 6px; text-align: left; border-bottom: 2px solid #fff; white-space: nowrap;">
                            GENERAL HEAT DETECTION<br>
                            <span style="font-size: 12px; color: #e0e0e0;">(bright_ti5)</span>
                        </th>
                        <th style="padding: 6px; text-align: left; border-bottom: 2px solid #fff; white-space: nowrap;">
                            FIRE INTENSITY<br>
                            <span style="font-size: 12px; color: #e0e0e0;">(fire radiative power, FRP)</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px; background-color: #f9f9f9; white-space: nowrap;">{row['acq_date']}</td>
                        <td style="padding: 8px; background-color: #f9f9f9; white-space: nowrap;">{formatted_time}</td>
                        <td style="padding: 8px; background-color: #f9f9f9;">{row.get('bright_ti4', 'N/A')} K</td>
                        <td style="padding: 8px; background-color: #f9f9f9;">{row.get('bright_ti5', 'N/A')} K</td>
                        <td style="padding: 8px; background-color: #f9f9f9;">{row.get('frp', 'N/A')}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        popup = folium.Popup(popup_html, max_width=600)

        # Add marker to fire layer
        folium.CircleMarker(
            location=(lat, lon),
            radius=style["radius"],
            popup=popup,
            color=style["color"],
            fill=True,
            fill_opacity=style["fillOpacity"]
        ).add_to(fire_layer)

    # Add fire layer to map
    fire_layer.add_to(fire_map)

    # Heatmap layer for fire intensity
    heat_data = [[row['geometry'].y, row['geometry'].x, row.get('frp', 0)] for _, row in fire_gdf.iterrows()]
    HeatMap(heat_data, name="Fire Intensity Heatmap", radius=15).add_to(fire_map)

    # LayerControl to toggle layers
    folium.LayerControl().add_to(fire_map)

    # Fire marker legend
    legend_html = """
        <style>
        /* Style for small screens */
        @media (max-width: 600px) {
            .legend {
                width: 150px;
                font-size: 12px;
                bottom: 20px;
                left: 20px;
            }
        }
        
        /* Style for larger screens */
        @media (min-width: 601px) {
            .legend {
                width: 200px;
                font-size: 14px;
                bottom: 50px;
                left: 50px;
            }
        }
        </style>

    <div class="legend" style="position: fixed; 
        bottom: 30px; left: 30px; 
        background-color: white; 
        border-radius: 8px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
        z-index: 9999; 
        padding: 10px 15px;
        width: 250px; 
        font-size: 14px;
        line-height: 1.4; 
        border: 2px solid #ccc;">
        
        <b style="font-size: 16px; margin-bottom: 6px; display: block;">Active Fire Intensity</b>
        
        <div style="margin-bottom: 4px;">
            <i style="background: #d73027; border-radius: 50%; width: 14px; height: 14px; display: inline-block; margin-right: 6px;"></i> 
            High Intensity (> 3 FRP)
        </div>
        <div style="margin-bottom: 4px;">
            <i style="background: #fc8d59; border-radius: 50%; width: 14px; height: 14px; display: inline-block; margin-right: 6px;"></i> 
            Medium Intensity (1.5 - 3 FRP)
        </div>
        <div>
            <i style="background: #fee08b; border-radius: 50%; width: 14px; height: 14px; display: inline-block; margin-right: 6px;"></i> 
            Low Intensity (0 - 1.5 FRP)
        </div>
    </div>
        """
    fire_map.get_root().html.add_child(folium.Element(legend_html))

    # Display map
    return fire_map

# Create map and display it
if __name__ == "__main__":
    fire_map = create_interactive_fire_map(PROCESSED_FIRE_FILE, LA_COUNTY_BOUNDARY_FILE)
    display(fire_map)

    # Save map as HTML file
    html_file = "fire_interactive_map.html"
    fire_map.save(html_file)
    print(f"Map saved to {html_file}")

    # Upload to S3 bucket 
    bucket_name = 'viirs-active-fire-map'
    os.system(f"aws s3 cp {html_file} s3://{bucket_name}/fire_interactive_map.html")
    print(f"Uploaded {html_file} to s3://{bucket_name}/fire_interactive_map.html")

    # Open map in web browser
    webbrowser.open(html_file)
    print("Map opened in your default web browser.")

