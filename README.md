# ETL Workflow for a Web Map that Tracks Active Wildfires using NASA Visible Infrared Imaging Radiometer Suite (VIIRS) Data (Los Angeles, CA, USA)

This project focuses on creating an interactive web map that tracks active wildfires in Los Angeles County area using NASA NIIRS (Visible Infrared Imaging Radiometer Suite) data. 

This ETL (Extract, Transform, Load) pipeline extracts active fire detection data, clips it to Los Angeles County boundary, transforms it to the correct projection, and generates an interactive web map for visualization.

[Click Here to View the Web Map](https://viirs-active-fire-map.s3.amazonaws.com/fire_interactive_map.html)

---

## Table of Contents
- [Overview](#10-overview)
- [Data Sources](#11-data-sources)
- [Methods Workflow](12-method-workflow)
- [Results Example](13-results-example)
- [Installation](#20-installation)

## 1.0 Overview

This repository details the functions capturing the standardized workflow. Broadly, this includes:

1. **Extraction of Precipitation and Elevation Data from NOAA**
   
2. **Transformation _placeholder__**

3. **Loading _placeholder__**

4. **Data Visualization _placeholder__**

## 1.1 Data Sources

1. **NASA Fire Information for Resource Management (FIRMS) :** [Link to dataset](https://firms.modaps.eosdis.nasa.gov/usfs/)
2. **Link to Instructions on Using NASA FIRMS' API in Python:** [Link to Instructions](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html)

## 1.2 Method Workflow

## 1.3 Results Example

## 2.0 Installation

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

