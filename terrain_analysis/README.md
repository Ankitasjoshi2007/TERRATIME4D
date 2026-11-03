
# TerraTime 4D - Terrain Analysis

## Purpose
This module analyzes elevation raster data for Earth terrain
and produces basic terrain metrics.

## Features
- Minimum elevation
- Maximum elevation
- Mean elevation
- Mean slope in degrees
- Mean local roughness in metres
- Valid pixel count
- Coordinate reference system (CRS)

## Dependencies
Install the required libraries from the project root:

    python -m pip install -r requirements.txt

## Run the sample test

From the main TERRATIME4D project folder:

    python terrain_analysis/test_terrain.py

## Output
The test generates:

- sample_elevation.tif
- terrain_metrics.json

The JSON file contains the calculated terrain metrics.

## Notes
The sample elevation raster is synthetic test data.
It is not official NASA elevation data.

Real elevation rasters can be analyzed by passing their
file paths to the analyze_terrain() function.

Terrain metrics are indicators, not a landing-safety verdict.
Results require validation against the source dataset.
