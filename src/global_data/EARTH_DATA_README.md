# TerraTime 4D — Earth Data Collection

## 1. Purpose

This module collects and processes Earth elevation data to identify terrain characteristics that may help evaluate potential analog environments for future Moon and Mars missions.

The current global terrain dataset contains 13 Copernicus DEM tiles used for terrain analysis.

These are Earth terrain samples for analysis and are not newly discovered or scientifically validated planetary analogs.

## 2. Data Sources

### Copernicus DEM

- Product: Copernicus DEM
- Download source: Public Copernicus DEM AWS bucket
- Data format: GeoTIFF
- Coordinate reference system: EPSG:4326
- Geographic coverage: Selected one-degree tiles

### NASA SRTM

- Product: Shuttle Radar Topography Mission Global 1 arc second V003
- Data format: HGT
- Resolution: Approximately 30 metres
- Current coverage: Bengaluru test region

### NASA POWER

Environmental temperature and solar irradiance datasets are collected separately for selected candidate locations.

## 3. Processing Workflow

1. Generate geographic sample locations.
2. Download Copernicus DEM tiles.
3. Verify downloaded raster files using Rasterio.
4. Calculate elevation statistics.
5. Calculate terrain slope in degrees.
6. Calculate local elevation roughness using a 3 × 3 pixel window.
7. Calculate terrain relief from elevation range.
8. Classify terrain using slope and roughness thresholds.
9. Combine terrain measurements into standardized CSV outputs.

### Terrain Classification

The current terrain classes are based on transparent heuristic thresholds using average slope and average roughness:

- Flat
- Rolling
- Hilly
- Steep
- Rugged

These classes are analytical categories developed for TerraTime 4D and are not official NASA or ESA terrain classifications.

## 4. Generated Outputs

| File | Purpose |
|---|---|
| global_sample_locations.csv | Selected geographic sample locations |
| copernicus_download_summary.csv | DEM download status |
| dem_quality_report.csv | DEM quality checks |
| global_terrain_features.csv | Elevation, slope, relief, roughness and terrain class |
| global_roughness_summary.csv | Local elevation roughness |
| combined_earth_features.csv | Combined terrain dataset |
| srtm_elevation_summary.csv | Bengaluru SRTM elevation statistics |

### Global Terrain Features

`global_terrain_features.csv` contains:

- Valid elevation pixels
- Valid slope pixels
- Minimum elevation
- Maximum elevation
- Average elevation
- Average slope
- Maximum slope
- Relief
- Approximate pixel width
- Approximate pixel height
- Average roughness
- Terrain class

## 5. Scientific Limitations

- The 13 DEM tiles represent selected Earth terrain samples and are not a complete global discovery search.
- Copernicus DEM is a digital surface model; buildings, vegetation and other surface features can affect elevation measurements.
- Slope estimates depend on raster resolution and geographic latitude.
- Roughness is calculated as local elevation standard deviation in a 3 × 3 pixel window.
- Terrain classification uses heuristic thresholds and should not be interpreted as an official geological or planetary classification.
- Hawaii's tile contains extensive ocean coverage. Its current land filter is provisional and needs a proper coastline mask.
- DEM resolution and processing scales must be considered when comparing locations.
- Earth cannot reproduce lunar gravity, vacuum, or planetary radiation conditions.
- Earth analog similarity must be evaluated for a particular mission objective, not treated as universal.

## 6. How Teammates Can Use the Dataset

Load the global terrain CSV using pandas:

```python
import pandas as pd

earth_data = pd.read_csv(
    "data/processed/global_terrain_features.csv"
)

print(earth_data.head())