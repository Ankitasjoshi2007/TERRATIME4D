\# TERRATIME 4D — Earth Data Collection Guide



\## 1. Purpose



This guide documents the Earth datasets collected for the TERRATIME 4D NASA challenge project.



The goal is to identify locations across the globe that may serve as useful analogs for lunar and Martian environments.



Earth data will support:

\- Terrain and elevation analysis

\- Geological and mineral comparisons

\- Temperature and climate analysis

\- Surface reflectance and albedo studies

\- Ice and permafrost investigations

\- Dust, wind, and environmental studies



No Earth location is a perfect copy of the Moon or Mars. Scientific comparisons must explain both similarities and limitations.



\## 2. Member 1 — Responsibilities



Member 1 is responsible for Earth Data Collection.



Main responsibilities:

1\. Identify suitable Earth observation datasets.

2\. Collect and organize available data.

3\. Record each dataset's source and metadata.

4\. Check file integrity, coordinate systems, resolution, and missing values.

5\. Document geographical coverage and data limitations.

6\. Provide clean datasets and documented interfaces to other team members.



Member 1 does not own the complete 3D/4D application or frontend implementation.



\## 3. Team Handoff



\- Member 1: Earth Data Collection

\- Member 2: Terrain Analysis

\- Member 3: Moon and Mars Comparison

\- Member 4: Similarity Scoring and Visualization

\- Member 5: Frontend, Backend and Integration



Collected datasets should be organized so other members can reuse them without repeating the collection process.
## 4. Earth Data Sources



The project uses or plans to evaluate the following data sources:



| Data source | Purpose |

|---|---|

| NASA SRTM | Elevation and terrain |

| Copernicus DEM GLO-90 | Global elevation and surface models |

| NASA Earthdata / MODIS | Surface temperature and reflectance |

| USGS | Geological and mineral information |

| ERA5 | Temperature, wind, and climate |

| NSIDC | Snow, ice, and permafrost |



Dataset availability does not mean that the data has already been downloaded or validated.



\## 5. Current Collected Data



\### NASA SRTM



Two 1-arc-second HGT tiles have been downloaded and validated:



\- N12E077

\- N13E077



Both files passed the current raster validation checks:

\- Dimensions: 3601 × 3601 pixels

\- Coordinate reference system: EPSG:4326

\- Data type: Int16

\- NoData value: -32768

\- Resolution: 1 arc-second



\### Copernicus DEM



Seven GeoTIFF files have been identified locally.



Their metadata has been inspected, including:

\- Dimensions

\- Coordinate reference system

\- Geographic bounds

\- Pixel resolution

\- Data type



Full pixel-quality validation is still pending.



\## 6. Global Coverage



The project contains a global grid of 2,592 cells.



Each cell represents a 5° × 5° geographic area.



The grid provides a framework for tracking worldwide data coverage. It does not mean that every cell already has downloaded or validated elevation data.



Actual raster coverage must be calculated from the geographic bounds of verified files.
## 7. Data Quality Checks



Before sharing a dataset, check:



1\. File opens successfully.

2\. Coordinate reference system is recorded.

3\. Geographic bounds are recorded.

4\. Pixel dimensions and resolution are recorded.

5\. NoData values and missing pixels are identified.

6\. Minimum, maximum, and mean values are checked where appropriate.

7\. Source, version, and download status are documented.



Do not treat zero elevation as missing data unless the dataset's documentation or valid-data mask confirms it.



\## 8. Known Limitations



\- SRTM does not provide complete global or polar coverage.

\- Copernicus GLO-90 is a digital surface model and may include vegetation and buildings.

\- Raster resolution and dimensions can vary by location.

\- Different elevation datasets may use different processing methods and vertical references.

\- A listed or available tile is not necessarily downloaded.

\- A downloaded file is not automatically a validated file.

\- Six regional terrain summaries do not represent complete global terrain coverage.



\## 9. Data Organization



Main project folders:



\- data/raw/ — downloaded source data

\- data/processed/ — cleaned datasets, summaries, and reports

\- src/data\_collection/ — data collection modules

\- src/global\_data/ — global data validation utilities

\- docs/ — documentation and handoff guides



Avoid committing large raw raster files to Git unless the team explicitly agrees.



\## 10. Handoff to Other Members



Member 2 can use verified elevation rasters for terrain analysis.



Member 3 can use documented Earth datasets for planetary comparisons.



Member 4 can use quality-checked features and metadata for similarity scoring and visualization.



Member 5 can integrate documented outputs into the application.



Every handoff should state:

\- File location

\- Dataset source

\- Geographic coverage

\- Resolution and units

\- Validation status

\- Known limitations



\## 11. Current Status



The global 2,592-cell grid has been structurally validated.



Two NASA SRTM tiles have passed validation.



Seven local Copernicus DEM files have had their metadata inspected. Full pixel-quality checks remain pending.



Global elevation coverage tracking and additional environmental dataset collection remain ongoing.



This guide will be updated as collection and validation progress.

