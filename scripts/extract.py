from IPython.display import display
import requests
import os
import pandas as pd
from datetime import datetime, timedelta

# Configure NASA FIIRMS API, data, and location variables
OUTPUT_DIR = "data/raw/"
MAP_KEY = 'fcaac2af71c612e0b3bea31ad6ab7abe'
source = 'VIIRS_SNPP_NRT'
bbox = '-118.9,33.7,-117.6,34.8'
area_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/1'
LACo_bndry_url = "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/15/query?outFields=*&where=1%3D1&f=geojson"

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Fetch LA County Boundary
def fetch_LACo_boundary():
    try:
        response = requests.get(LACo_bndry_url)
        if response.status_code == 200:
            file_path = os.path.join(OUTPUT_DIR, "LA_County_Boundary.geojson")
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved to {file_path}")
        else:
            print(f"Failed to download LA County boundary. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching LA County boundary: {e}")

# Fetch VIIRS Fire Data and focus on active fires (last 24 hours)
def fetch_viirs_fire_data_lacounty():
    try:
        # Make the API request and read the data into a pandas DataFrame
        df_area = pd.read_csv(area_url)
        
        # Check for date and time fields in the extracted data
        if 'acq_date' in df_area.columns and 'acq_time' in df_area.columns:
            df_area['datetime'] = pd.to_datetime(df_area['acq_date'] + ' ' + df_area['acq_time'].astype(str).str.zfill(4), format='%Y-%m-%d %H%M')
            print('Time series field successfully created.')
        
            # Filter to include only fires in the last 24 hours
            recent_fires = df_area[df_area['datetime'] >= (datetime.now() - timedelta(days=1))]
            print(f"{len(recent_fires)} recent fire records extracted.")
        
        else:
            print("Required fields 'acq_date' and 'acq_time' not found in the data.")
            return
        
        # Save the data to a cumulative file (tracking fires over time)
        cumulative_file_path = os.path.join(OUTPUT_DIR, "Cumulative_FireData_LACo.csv")
        
        if os.path.exists(cumulative_file_path):
            df_cumulative = pd.read_csv(cumulative_file_path)
            df_cumulative['datetime'] = pd.to_datetime(df_cumulative['datetime'])
            
            # Append new data to the cumulative dataset
            df_combined = pd.concat([df_cumulative, recent_fires])
            df_combined = df_combined.drop_duplicates(subset=['latitude', 'longitude', 'datetime'])
        else:
            df_combined = recent_fires
        
        # Save updated cumulative data
        df_combined.to_csv(cumulative_file_path, index=False)
        print(f"Updated cumulative fire data saved to {cumulative_file_path}")
        
        # Optionally, save the latest extract with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_file_path = os.path.join(OUTPUT_DIR, f"VIIRS_FireData_LACo_{timestamp}.csv")
        recent_fires.to_csv(new_file_path, index=False)
        print(f"Recent fire data saved to {new_file_path}")
    
    except Exception as e:
        print(f"Error fetching VIIRS fire data: {e}")

# Execute the functions
if __name__ == "__main__":
    fetch_LACo_boundary()
    fetch_viirs_fire_data_lacounty()
