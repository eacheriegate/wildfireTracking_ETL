import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from io import StringIO
import pytz

# Configure NASA FIRMS API and location variables
MAP_KEY = 'fcaac2af71c612e0b3bea31ad6ab7abe'  # Replace with your API key
source = 'VIIRS_SNPP_NRT'
bbox = '-118.9,33.7,-117.6,34.8'  # Bounding box for Los Angeles County
area_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/7'

# Fetch VIIRS Fire Data
def fetch_viirs_fire_data():
    try:
        response = requests.get(area_url)
        print(f"Response status code: {response.status_code}")
        print(f"Response text preview (first 500 chars): {response.text[:500]}")

        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            print(f"DataFrame created with shape: {df.shape}")
            print(f"DataFrame columns: {df.columns.tolist()}")
            print("Head of DataFrame:")
            print(df.head())

            return df
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching VIIRS fire data: {e}")
        return None

# Subset data for Los Angeles County
def subset_data(df):
    if df is not None:
        # Ensure 'acq_date' and 'acq_time' columns are available
        if 'acq_date' in df.columns and 'acq_time' in df.columns:
            # Convert 'acq_time' to a 4-digit string with leading zeros
            df['acq_time'] = df['acq_time'].astype(str).str.zfill(4)

            # Combine 'acq_date' and 'acq_time' into a datetime column
            df['acq_datetime'] = pd.to_datetime(
                df['acq_date'] + ' ' + df['acq_time'], 
                format='%Y-%m-%d %H%M'
            )

            # Localize the datetime to UTC
            df['acq_datetime'] = df['acq_datetime'].dt.tz_localize('UTC')

            print("Datetime column created successfully.")
            print("Date range in data:", df['acq_datetime'].min(), "to", df['acq_datetime'].max())

            return df
        else:
            print("Required fields 'acq_date' and 'acq_time' are missing in the data.")
            return None
    else:
        print("No data to subset.")
        return None

# Convert datetime to local timezone (Los Angeles)
def convert_to_local_timezone(df):
    if df is not None:
        # Convert UTC datetime to Los Angeles timezone
        la_timezone = pytz.timezone('America/Los_Angeles')
        df['acq_datetime_local'] = df['acq_datetime'].dt.tz_convert(la_timezone)

        print("Datetime converted to Los Angeles timezone.")
        print("Date range in local time:", df['acq_datetime_local'].min(), "to", df['acq_datetime_local'].max())

        return df
    else:
        print("No data to convert.")
        return None

# Main function to execute the workflow
def main():
    # Step 1: Fetch data
    df = fetch_viirs_fire_data()

    # Step 2: Subset data and create datetime column
    df = subset_data(df)

    # Step 3: Convert datetime to local timezone
    df = convert_to_local_timezone(df)

    # Step 4: Display final data
    if df is not None:
        print("Final DataFrame with local timezone:")
        print(df[['latitude', 'longitude', 'acq_datetime', 'acq_datetime_local']].head())
    
    # Step 5: Save file to csv
    output_file = r'C:\Users\eache\.vscode\projects\wildfireTracking_ETL\data\raw\Cumulative_FireData_LACo.csv'
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")    

# Execute the main function
if __name__ == "__main__":
    main()