# Active Wildfire Tracking with VIIRS Data: Automated ETL & Web Map for LA County

This project automates an Extract, Transform, and Load (ETL) workflow that fetches and visualizes active fire data within Los Angeles (LA) County using NASA VIIRS (Visible Infrared Imaging Radiometer Suite) satellite data. 

The workflow runs daily to update and publish an interactive fire map, which displays recent fires, intensity based on Fire Radiative Power (FRP), fire hotspots (bright_ti4), and general heat detection (bright_ti5).

[![View the Web Map](https://img.shields.io/badge/View-Web_Map-blue?style=for-the-badge)](https://viirs-active-fire-map.s3.amazonaws.com/fire_interactive_map.html)

---

## ✨ Features
- **Automated Daily Updates**: Workflow is scheduled to run daily at 8 AM PST using GitHub Actions' cron jobs.
- **Data Extraction**: Fetches the latest active fire data from NASA's Fire Information and Resource Management System (FIRMS) API and clips it to the LA County boundary.
- **Data Transformation:** Converts the raw data into a geospatial format, filters fires from the last 48 hours, and reprojects the data to match LA County’s geographic coordinates.
- **Interactive Map Visualization:** Displays active fire locations and intensities on an interactive map with customizable layers, including light, dark, and satellite imagery base map tile views, and a heatmap of fire intensity with associated legend.
- **Responsive Mobile Design:** Interactive web map includes responsive design so that its layout automatically adjusts across different screen sizes and devices.
- **Automated S3 Upload:** After generating the map, the workflow uploads the updated map to an AWS S3 bucket, making it accessible through a public link.

## 🚀 How It Works

### Data Sources

1. NASA FIRMS:
[Link to NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/map)

2. NASA FIRMS API Documentation for Python:
[Link to API Instructions](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html)

3. LA County Boundary:
[Link to Boundary Feature Layer](https://geohub.lacity.org/datasets/lahub::county-boundary/about)

### Data Pipeline
1. **Extract:**
   - Fetches the LA County boundary and active fire data (VIIRS) from NASA FIRMS API.
   - Saves raw data in the `data/raw/` directory.

2. **Transform:**
   - Converts LA County boundary GeoJSON into a shapefile format.
   - Clips the fire data to the LA County boundary and filters it to include only fires from the last 48 hours.
   - Reprojects fire data to match the LA County coordinate system.

3. **Load:**
   - Creates an interactive map using Folium, adding fire markers with intensity levels and a heatmap layer.
   - Saves the map as `fire_interactive_map.html` in the project root directory.

4. **S3 Upload:**
   - Automatically uploads the map to an AWS S3 bucket, making it available via a public link.

## 🛠 Technologies Used (Check [requirements.txt](https://github.com/eacheriegate/wildfireTracking_ETL/blob/master/requirements.txt) for full list of necessary packages)
- **NASA FIRMS API:** For fetching active fire data.
- **AWS S3:** For storing and sharing updated web map.
- **GitHub Actions:** For automating the daily workflow.

## 📜 License
This project is licensed under the **CC BY 4.0** License. See the LICENSE file for more details.
