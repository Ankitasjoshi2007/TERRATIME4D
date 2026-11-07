# TERRATIME 4D — Earth Data Collection Handoff

**Team role:** Member 1 — Earth Data Collection  
**Project:** TERRATIME 4D  
**Status:** Earth data collection and preliminary terrain analysis substantially completed; final validation and handoff in progress.

## 1. Project contribution

Developed a global Earth-data collection workflow to identify and characterize potential terrestrial environments relevant to lunar and Martian mission research.

The work provides preliminary geological, geographical and terrain evidence for further analysis by the project team.

## 2. Completed work

### Global land classification

- Created a global Earth grid containing 2,592 grid cells.
- Classified 869 grid centres as land.
- Classified 1,723 as ocean or unclassified.
- Used Natural Earth land polygons for classification.

### Worldwide geological collection

- Queried the Macrostrat geological API at 869 land grid centres.
- Successfully completed all 869 requests.
- Collected 1,708 geological records from 796 cells.
- Identified 73 cells with no geological records; these are in Antarctica.
- Generated reports for incomplete records and zero-record cells.

### Preliminary candidate terrain analysis

Analyzed six priority candidate regions:

| Candidate region | Latitude | Longitude |
|---|---:|---:|
| Western Australia | -32.5 | 117.5 |
| Queensland, Australia | -22.5 | 147.5 |
| Baja California, Mexico | 27.5 | -112.5 |
| Ontario, Canada | 47.5 | -82.5 |
| Brooks Range, Alaska | 67.5 | -147.5 |
| Scandinavia | 67.5 | 17.5 |

Collected preliminary elevation, slope and local roughness measurements for these regions.

These are broad grid-centre locations, not confirmed field sites or mission-ready landing locations.

### Copernicus DEM inventory and planning

- Retrieved and processed the official Copernicus GLO-90 tile inventory.
- Matched all 869 land grid centres to official DEM tiles.
- Identified 869 unique target tiles.
- Six relevant DEM tiles are already available locally.
- 863 tiles remain undownloaded.
- Created a targeted download plan with separate Antarctic, Arctic and other-region priorities.

### Environmental data — NASA POWER temperature

Collected monthly temperature data for six candidate locations for 2020.

- 72 monthly records.
- Mean, average daily maximum and average daily minimum temperature parameters.
- No missing values or duplicate rows.
- Temperature ordering validation passed.

**Dataset:** `data/processed/environmental/nasa_power_monthly_temperature_2020.csv`

**Collection script:** `src/global_data/collect_nasa_power_temperature.py`

**Limitation:** This is a one-year, six-point comparison dataset, not a long-term climate assessment or full regional climate map.

### Solar radiation data — NASA POWER

Collected monthly all-sky surface shortwave downward irradiance data for six candidate locations for 2020.

- 72 monthly records (12 per location).
- NASA POWER parameter: `ALLSKY_SFC_SW_DWN`.
- Parameter description: All Sky Surface Shortwave Downward Irradiance.
- Unit reported by NASA POWER: W/m².
- No missing values or duplicate rows.

**Dataset:** `data/processed/environmental/nasa_power_monthly_solar_2020.csv`

**Collection script:** `src/global_data/collect_nasa_power_solar_radiation.py`

**Limitation:** This is a one-year, six-point dataset, not a long-term solar climate assessment or full regional solar map.

## 3. Important output files

### Global geology

- `data/processed/global_geology_worldwide/worldwide_geology_records.csv`
- `data/processed/global_geology_worldwide/worldwide_geology_cell_status.csv`
- `data/processed/global_geology_worldwide/zero_record_cells.csv`
- `data/processed/global_geology_worldwide/incomplete_geology_records.csv`

### Land classification

- `data/processed/land_classification/global_land_classification.csv`
- `data/processed/earth_grid.csv`

### Candidate terrain analysis

- `data/processed/combined_priority_candidate_terrain.csv`
- `data/processed/priority_candidate_elevations.csv`
- `data/processed/priority_candidate_slope_analysis.csv`
- `data/processed/priority_candidate_roughness_analysis.csv`

### Global DEM planning

- `data/processed/copernicus_official_dem_inventory.csv`
- `data/processed/global_dem_plan/global_dem_download_plan.csv`
- `data/processed/global_dem_plan/global_land_centre_dem_mapping.csv`
- `data/processed/copernicus_global_grid_coverage.csv`

### Environmental data

- `data/processed/environmental/nasa_power_monthly_temperature_2020.csv`
- `data/processed/environmental/nasa_power_monthly_solar_2020.csv`

## 4. Important limitations

1. The global grid uses 5-degree sampling. It is not a complete high-resolution survey of Earth's land surface.
2. Macrostrat records may have incomplete geological attributes.
3. The 73 Antarctic cells without geological records should not be interpreted as having no geology.
4. Copernicus GLO-90 terrain measurements are not sufficient to certify landing-site safety.
5. Local slope and roughness calculations are preliminary and require appropriate geospatial validation.
6. The six candidate regions are preliminary hypotheses requiring further geological, environmental and planetary comparison.
7. Only six of the 869 targeted DEM tiles are currently downloaded. The remaining 863 have not been collected.
8. The temperature and solar datasets cover only six candidate points and one year (2020). They are not long-term climate assessments or complete regional maps.

## 5. Recommended next work for the team

- Validate terrain measurements and expand DEM coverage where useful.
- Collect additional relevant environmental data, including surface conditions.
- Investigate mineral and resource potential.
- Compare Earth environments with lunar and Martian datasets.
- Develop separate Lunar Analog, Martian Analog and Mission Utility assessments.
- Validate candidate regions using multiple independent data sources.
- Document where Earth analogies differ from actual lunar and Martian conditions.

## 6. Handoff status

The Earth-data collection work provides a preliminary global dataset, geological records, candidate terrain measurements, environmental comparison data and a targeted DEM acquisition plan.

The datasets are intended as inputs to the team's subsequent analysis, not as final confirmation that any location is suitable for a space mission.

**Prepared by:** Member 1 — Earth Data Collection  
**Project:** TERRATIME 4D