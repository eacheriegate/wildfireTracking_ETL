# Active Wildfire Tracking with VIIRS Data: Automated ETL & Web Map for LA County

This project focuses on creating an interactive web map that tracks active wildfires in the Los Angeles County area using NASA VIIRS (Visible Infrared Imaging Radiometer Suite) data.

This ETL (Extract, Transform, Load) pipeline extracts active fire detection data, clips it to the Los Angeles County boundary, transforms it to the correct projection, and generates an interactive web map for visualization.

[Click Here to View the Web Map](https://viirs-active-fire-map.s3.amazonaws.com/fire_interactive_map.html)

---

## Table of Contents
- [Overview](#10-overview)
- [Data Sources](#11-data-sources)
- [Method Workflow](#12-method-workflow)
- [Results Example](#13-results-example)
- [Installation](#20-installation)

## 1.0 Overview

This repository details the functions capturing the standardized workflow. Broadly, this includes:

1. **Extraction of VIIRS Active Fire Detection Data**
   
2. **Transformation of Data:** This includes clipping to Los Angeles County boundaries and reprojecting the data to the correct coordinate system.

3. **Loading the Data:** The processed fire detection data is visualized in an interactive web map.

4. **Data Visualization:** The data is displayed as an interactive web map with fire locations overlaid on a basemap.

## 1.1 Data Sources

1. **NASA Fire Information for Resource Management System (FIRMS):**  
   [Link to dataset](https://firms.modaps.eosdis.nasa.gov/usfs/)
   
2. **NASA FIRMS' API Documentation for Python:**  
   [Link to API Instructions](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html)

## 1.2 Method Workflow

The ETL process for this project follows these steps:
- **Extract**: Pull the latest active fire detection data from NASA FIRMS using their API.
- **Transform**: Clip the fire data to the Los Angeles County boundary, reproject the data, and clean it up for visualization.
- **Load**: Load the processed data into an interactive web map for visualization and access by end-users.

## 1.3 Results Example

An interactive web map that displays active fire detections with detailed information about the fires and options to view different basemap layers.

## 2.0 Installation

To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eacheriegate/work_ETL.git
   cd flood-risk-analysis


1. **Clone the repository:**
   ```bash
   git clone https://github.com/eacheriegate/floodRisk_ETL.git
   cd flood-risk-analysis

2. **Set up virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate

3. **Install required dependencies and run the project:**
   ```bash
   pip install -r requirements.txt
   python run_analysis.py

