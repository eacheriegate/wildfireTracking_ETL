import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os
from datetime import datetime, timedelta

# File paths
RAW_DATA_DIR = "data/raw/"
PROCESSED_DATA_DIR = "data/processed/"
CLIP_SHAPE_PATH = "data/raw/Borough Boundaries (Water Areas Included)/geo_export_bc45aa45-2790-41c4-a0db-da60a90fd08c.shp"
LaCO_bdnry_geojson = os.path.join(RAW_DATA_DIR, "LA_County_Boundary.geojson")

# Dynamically select the latest fire data file in the raw directory
VIIRS_FILE = max([os.path.join(RAW_DATA_DIR, f) for f in os.listdir(RAW_DATA_DIR) if f.startswith('Cumulative_FireData_LACo')], key=os.path.getctime)

def convert_file_format():
    """Convert GeoJSON to Shapefile."""
    shapefile_output = os.path.join(PROCESSED_DATA_DIR, "LA_County_Boundary.shp")

    try:
        gdf = gpd.read_file(LaCO_bdnry_geojson)
        gdf.to_file(shapefile_output, driver='ESRI Shapefile')
        print(f"GeoJSON converted to Shapefile: {shapefile_output}")
    except Exception as e:
        print(f"Error converting GeoJSON to Shapefile: {e}")

# Convert GeoJSON to Shapefile
if __name__ == "__main__":
    convert_file_format()

# Define LA County shapefile path
LACo_bndry_shapefile = os.path.join(PROCESSED_DATA_DIR, "LA_County_Boundary.shp")

# Ensure output directory exists
if not os.path.exists(PROCESSED_DATA_DIR):
    os.makedirs(PROCESSED_DATA_DIR)

def transform_fire_data_to_shapefile(viirs_file, boundary_shapefile, output_dir):
    """
    Transforms fire data from CSV by clipping it to the LA County boundary
    and saving the result as a Shapefile.
    """
    try:
        # Load LA County boundary shapefile as GeoDataFrame
        la_county_gdf = gpd.read_file(boundary_shapefile)
        print(f"Loaded LA County boundary with CRS: {la_county_gdf.crs}")

        # Load VIIRS fire data from CSV
        fire_data_df = pd.read_csv(viirs_file)
        fire_data_df['datetime'] = pd.to_datetime(fire_data_df['datetime'])
        print(f"Loaded VIIRS fire data with {len(fire_data_df)} records")

        # Filter to include only recent fires (last 24 hours)
        recent_fires = fire_data_df[fire_data_df['datetime'] >= (datetime.now() - timedelta(days=1))]
        print(f"Filtered to {len(recent_fires)} recent fire records")

        # Convert fire data to GeoDataFrame
        geometry = [Point(xy) for xy in zip(recent_fires.longitude, recent_fires.latitude)]
        fire_data_gdf = gpd.GeoDataFrame(recent_fires, crs="EPSG:4326", geometry=geometry)

        # Reproject fire data to match LA County boundary's CRS
        fire_data_gdf = fire_data_gdf.to_crs(la_county_gdf.crs)
        print(f"Reprojected fire data to CRS: {fire_data_gdf.crs}")

        # Clip fire data to LA County boundary
        fire_data_clipped = gpd.clip(fire_data_gdf, la_county_gdf)

        # Create output shapefile path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_shapefile = os.path.join(output_dir, f"VIIRS_FireData_LACo_{timestamp}.shp")

        # Save the clipped data to a new shapefile
        fire_data_clipped.to_file(output_shapefile)
        print(f"Fire data clipped to LA County boundary and saved to {output_shapefile}")
    except Exception as e:
        print(f"Error transforming fire data: {e}")

# Execute the function to clip and save fire data
if __name__ == "__main__":
    transform_fire_data_to_shapefile(VIIRS_FILE, LACo_bndry_shapefile, PROCESSED_DATA_DIR)
