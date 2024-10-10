import os
import rasterio
from rasterio.enums import Resampling
from rio_cogeo.cogeo import cog_translate, cog_validate  # Correct import for cog_translate and cog_validate
from rio_cogeo.profiles import cog_profiles  # Import cog_profiles for default COG profiles

# Define processed data directories
PROCESSED_DATA_DIR = "data/processed/"
COG_OUTPUT_DIR = "data/final_cog/"

def create_cog(input_tif, output_cog):
    """
    Convert a processed GeoTIFF to a Cloud-Optimized GeoTIFF (COG).
    """
    if not os.path.exists(COG_OUTPUT_DIR):
        os.makedirs(COG_OUTPUT_DIR)

    with rasterio.open(input_tif) as src:
        # Check resolution
        print(f"Original resolution: {src.res}")

        # Set internal tiling, compression, and other COG settings
        cog_profile = src.profile.copy()
        cog_profile.update({
            'driver': 'GTiff',  # GeoTIFF format
            'tiled': True,  # Enable internal tiling
            'blockxsize': 512,  # Tile size
            'blockysize': 512,
            'compress': 'deflate',  # Compression to reduce size
            'interleave': 'band'  # Band interleaving for better compression
        })

        # Write the Cloud-Optimized GeoTIFF
        with rasterio.open(output_cog, 'w', **cog_profile) as dst:
            # Write data to the new COG file
            for i in range(1, src.count + 1):  # Copy each band
                dst.write(src.read(i), i)

            # Create overviews after writing the data
            overviews = [2, 4, 8, 16]  # Downsampled overviews
            dst.build_overviews(overviews, Resampling.nearest)
            dst.update_tags(ns='rio_overview', resampling='nearest')
    
    # Use cog_translate to optimize the COG structure and fix errors
    cog_translate(output_cog, output_cog, cog_profiles.get("deflate"))

    # Validate the COG after creation
    if cog_validate(output_cog):
        print(f"COG validation successful for {output_cog}")
    else:
        print(f"COG validation failed for {output_cog}")


def load_to_cog():
    """
    Load processed GeoTIFFs and convert them to COGs.
    """
    for file_name in os.listdir(PROCESSED_DATA_DIR):
        if file_name.endswith(".tif"):
            input_tif = os.path.join(PROCESSED_DATA_DIR, file_name)
            output_cog = os.path.join(COG_OUTPUT_DIR, f"COG_{file_name}")
            
            # Convert the processed DEM or other raster data to COG format
            create_cog(input_tif, output_cog)

if __name__ == "__main__":
    load_to_cog()
