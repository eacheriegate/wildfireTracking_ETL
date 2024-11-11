import requests
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from io import StringIO

# Configure NASA FIRMS API, data, and location variables
OUTPUT_DIR = "data/raw/"
MAP_KEY = 'fcaac2af71c612e0b3bea31ad6ab7abe'  # Replace with your valid key
source = 'VIIRS_SNPP_NRT'
bbox = '-118.9,33.7,-117.6,34.8'  # Update if needed to ensure correct area
area_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/1'
LACo_bndry_url = "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/15/query?outFields=*&where=1%3D1&f=geojson"

# Define the cumulative file path
cumulative_file_path = os.path.join(OUTPUT_DIR, "Cumulative_FireData_LACo.csv")

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

# Fetch VIIRS Fire Data and filter for fires in the last 48 hours
def fetch_viirs_fire_data_lacounty():
    try:
        # Make the API request and check the response
        response = requests.get(area_url)
        print(f"Response status code: {response.status_code}")
        print(f"Response text preview (first 500 chars): {response.text[:500]}")

        if response.status_code == 200:
            df_area = pd.read_csv(StringIO(response.text))
            print(f"DataFrame created with shape: {df_area.shape}")
            print(f"DataFrame columns: {df_area.columns.tolist()}")
            print("Head of DataFrame:")
            print(df_area.head())

            # Ensure 'acq_date' and 'acq_time' columns are available
            if 'acq_date' in df_area.columns and 'acq_time' in df_area.columns:
                # Convert acq_time to 4-digit format and create 'datetime' column in UTC
                df_area['acq_time'] = df_area['acq_time'].astype(str).str.zfill(4)
                df_area['datetime'] = pd.to_datetime(
                    df_area['acq_date'] + ' ' + df_area['acq_time'],
                    format='%Y-%m-%d %H%M'
                ).dt.tz_convert(timezone.utc)
                print("Datetime column created successfully.")
                print("Date range in data:", df_area['datetime'].min(), "to", df_area['datetime'].max())

                # Filter for recent fires in the last 48 hours using UTC time
                now_utc = datetime.now(timezone.utc)
                recent_fires = df_area[df_area['datetime'] >= (now_utc - timedelta(hours=48))]
                print(f"Number of recent fires found: {len(recent_fires)}")
                print("Recent fires data preview:")
                print(recent_fires[['latitude', 'longitude', 'datetime']].head())

                if recent_fires.empty:
                    print("No new fire records found within the last 48 hours.")
                    return
                else:
                    print(f"{len(recent_fires)} recent fire records extracted.")

            else:
                print("Required fields 'acq_date' and 'acq_time' are missing in the data.")
                return

            # Check if the cumulative file exists
            if os.path.exists(cumulative_file_path):
                print("Cumulative file found. Loading and updating it with new records.")
                df_cumulative = pd.read_csv(cumulative_file_path)
                df_cumulative['datetime'] = pd.to_datetime(df_cumulative['datetime']).dt.tz_convert(timezone.utc)

                # Combine new and existing data, removing duplicates
                df_combined = pd.concat([df_cumulative, recent_fires]).drop_duplicates(subset=['latitude', 'longitude', 'datetime'])
            else:
                print("Cumulative file not found. Creating a new cumulative file.")
                df_combined = recent_fires  # Use recent_fires if no cumulative file exists

            # Save the updated data to the cumulative file
            df_combined.to_csv(cumulative_file_path, index=False)
            print(f"Updated cumulative fire data saved to {cumulative_file_path}")

            # Log the most recent date in the cumulative file
            if not df_combined.empty:
                latest_date = df_combined['datetime'].max()
                print(f"Latest fire data date in cumulative file: {latest_date}")
            else:
                print("Combined DataFrame is empty.")

        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error fetching VIIRS fire data: {e}")

# Execute the functions
if __name__ == "__main__":
    fetch_LACo_boundary()
    fetch_viirs_fire_data_lacounty()
