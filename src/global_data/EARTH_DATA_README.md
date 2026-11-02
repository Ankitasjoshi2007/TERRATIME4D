# TerraTime 4D — Earth Data Collection

## 1. Purpose

This module collects and processes Earth elevation data to identify terrain characteristics that may help evaluate potential analog environments for future Moon and Mars missions.

The current dataset contains six test locations:
- Bengaluru, India
- Atacama Desert, Chile
- Iceland
- Hawaii, USA
- Australian Outback
- Antarctica

These are initial test locations, not newly discovered or scientifically validated planetary analogs.

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

## 3. Processing Workflow

1. Generate geographic sample locations.
2. Download Copernicus DEM tiles.
3. Verify downloaded raster files using Rasterio.
4. Calculate elevation statistics.
5. Calculate terrain slope in degrees.
6. Calculate local elevation roughness using a 3 × 3 pixel window.
7. Combine terrain measurements and location information into one CSV.

## 4. Generated Outputs

| File | Purpose |
|---|---|
| global_sample_locations.csv | Selected test locations |
| copernicus_download_summary.csv | Download status |
| dem_quality_report.csv | DEM quality checks |
| global_terrain_features.csv | Elevation and slope statistics |
| global_roughness_summary.csv | Local elevation roughness |
| combined_earth_features.csv | Combined terrain dataset |
| srtm_elevation_summary.csv | Bengaluru SRTM elevation statistics |

## 5. Scientific Limitations

- The six locations are demonstration samples, not a complete global discovery search.
- Copernicus DEM is a digital surface model; buildings, vegetation and other surface features can affect elevation measurements.
- Slope estimates depend on raster resolution and geographic latitude.
- Roughness is calculated as local elevation standard deviation in a 3 × 3 pixel window.
- Hawaii's tile contains extensive ocean coverage. Its current land filter is provisional and needs a proper coastline mask.
- DEM resolution and processing scales must be considered when comparing locations.
- Earth cannot reproduce lunar gravity, vacuum, or planetary radiation conditions.
- Earth analog similarity must be evaluated for a particular mission objective, not treated as universal.

## 6. How Teammates Can Use the Dataset

Load the combined CSV using pandas:

```python
import pandas as pd

earth_data = pd.read_csv(
    "data/processed/combined_earth_features.csv"
)

print(earth_data.head())
```

The dataset provides location coordinates, elevation statistics, slope statistics and local roughness measurements for further analysis.

## 7. Future Improvements

- Expand the search to a genuinely global collection of land tiles.
- Add a reliable land/ocean mask.
- Improve terrain roughness and multi-scale analysis.
- Add geological and mineralogical datasets.
- Add temperature, dust and ice information where suitable data exists.
- Compare Earth features with lunar and Martian datasets.
- Develop mission-specific similarity scores with uncertainty reporting.