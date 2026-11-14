# TERRATIME4D — Member 3 Planetary Data Handoff

## 1. Purpose and responsibility

Member 3 provides documented Moon and Mars planetary reference datasets and compares their physical terrain characteristics with the available Earth terrain reference data.

This handoff is intended for **Member 4**, who will use the planetary reference data in the similarity and mission-scoring engine.

**Project responsibility split**

| Member | Responsibility |
|---|---|
| Member 1 | Earth terrain foundation: elevation, slope, roughness, relief and terrain classification |
| Member 2 | Earth environmental and geological datasets |
| Member 3 | Moon/Mars reference datasets, physical terrain analysis, Earth–Moon–Mars comparison and analogy limitations |
| Member 4 | Similarity analysis and mission suitability scoring |
| Member 5 | Time-based analysis, rover movement, visualization and final application |

Member 3 supplies reference measurements and scientific context. The mission suitability scoring engine belongs to Member 4.

## 2. Earth reference dataset

**Primary input**

`data/processed/global_terrain/global_advanced_terrain_summary.csv`

The updated Earth reference contains:

- 648 unique tile-summary records.
- 645 records represented in the processing log.
- 645 records represented in the classification data.
- 3 additional summary-only records.

The three summary-only records are retained in the reference summary and are not counted as processing-log or classification records.

**Earth reference averages**

These values are unweighted arithmetic averages of the available tile-level summary statistics. They are not pixel-area-weighted global Earth averages.

| Metric | Mean |
|---|---:|
| Elevation | 1099.7189 m |
| Slope | 3.5687° |
| Roughness at 270 m scale | 4.8402 m |
| Roughness at 630 m scale | 10.1794 m |
| Roughness at 1350 m scale | 17.2959 m |

Earth reference coverage is incomplete. Do not interpret these 648 tiles as complete global coverage.

## 3. Moon reference dataset

**Primary source data**

- Dataset: Lunar Orbiter Laser Altimeter (LOLA) elevation data.
- Input file: `data/raw/moon/ldem_16.tif`
- Original grid: 5760 × 2880.
- The source raster used in this workflow does not provide ordinary geographic georeferencing metadata.

**Processed results**

The global physical analysis aggregates the elevation grid to 8 pixels per degree, producing a 1440 × 2880 grid.

| Metric | Moon result |
|---|---:|
| Area-weighted mean elevation | -0.2484 km |
| Area-weighted mean slope | 4.1790° |
| Roughness at approximately 11 km scale | 0.2371 km |

**Important limitation:** The available elevation grid does not provide a per-pixel direct-observation mask in this workflow. The analysis should not be interpreted as a map of observation confidence.

## 4. Mars reference dataset

**Primary source data**

- Dataset: Mars Orbiter Laser Altimeter (MOLA) Mission Experiment Gridded Data Record (MEGDR).
- Input elevation file: `data/raw/mars/megt90n000eb.img`
- Associated label: `data/raw/mars/megt90n000eb.lbl`
- Grid: 2880 × 5760.
- Product resolution: 1/16 degree.

**Processed results**

| Metric | Mars result |
|---|---:|
| Area-weighted mean elevation | -0.5507 km |
| Area-weighted mean slope | 1.2327° |
| Roughness at approximately 11 km scale | 0.0706 km |

**Important limitation:** MOLA MEGDR products include interpolated values in locations where observations are unavailable. The global grid must not be treated as if every cell were a direct measurement.

**Latitude orientation:** The Mars latitude-band analysis uses north-to-south row order, consistent with the official PDS label's global simple cylindrical projection, 16 pixels-per-degree resolution, latitude limits (+90 to -90 degrees), and equatorial line-projection offset (1440.5). This is a metadata-based orientation check, not an independent binary-to-raster validation.

## 5. Main Member 3 outputs

### A. Global physical analysis

Folder: `results/member3_global_analysis_v3/`

Important files:

- `moon_mars_physical_summary_v3.csv` — processed Moon and Mars physical summary.
- `moon_mars_latitude_band_analysis_v3.csv` — latitude-band terrain analysis.
- `earth_existing_reference_statistics_v3.csv` — Earth reference statistics.
- `earth_reference_audit_v3.csv` — record-count and coverage audit.
- `earth_reference_tile_records_v3.csv` — Earth tile records used in the analysis.
- `earth_summary_only_records_v3.csv` — three summary records without matching processing-log/classification records.
- `member3_physical_analysis_report_v3.txt` — global physical analysis report.

### B. Planetary comparison

Folder: `results/member3_global_comparison_v3/`

Important files:

- `planetary_comparison_values_v3.csv` — comparison values for Earth, Moon and Mars.
- `member3_planetary_comparison_report_v3.txt` — comparison report.
- `01_mean_slope_comparison.png`
- `02_earth_roughness_scales.png`
- `03_moon_mars_roughness_comparison.png`
- `04_mean_elevation_comparison.png`
- `05_latitude_slope_comparison.png`
- `06_latitude_roughness_comparison.png`
- `07_planetary_comparison_dashboard.png`

### C. Analogy assessment

File:

`results/member3_final_analysis/member3_analogy_assessment.md`

This assessment discusses where Earth terrain can be useful as a planetary analogue and where the comparison is scientifically limited.

### D. Final report

File:

`results/MEMBER3_FINAL/MEMBER3_FINAL_REPORT.md`

This report consolidates the Member 3 analysis, comparison results and scientific limitations.

## 6. Additional planetary environmental resources

Additional official planetary resources were investigated or downloaded for supporting context:

- Lunar Diviner polar resource tables, including temperature and modelled ice-stability information.
- Mars TES thermal-inertia day/night map products.
- THEMIS product inventory and regional product metadata.

These supporting resources should not be confused with the main elevation-based global comparison. In particular:

- Diviner modelled ice stability is not proof of accessible ice.
- THEMIS calibrated radiance is not automatically a direct surface-temperature measurement.
- Interpolated or masked thermal-map cells require careful interpretation.

Use these additional resources only when their product metadata, units, coverage and processing status are understood.

## 7. Official data sources

The planetary reference datasets are based on mission data products and documentation from official NASA planetary data archives.

**NASA Planetary Data System (PDS) — Geosciences Node**

https://pds-geosciences.wustl.edu/

**NASA PDS Geosciences Orbital Data Explorer**

https://ode.rsl.wustl.edu/

**NASA Planetary Data System**

https://pds.nasa.gov/

The Moon elevation reference is from the Lunar Reconnaissance Orbiter (LRO) LOLA data family. The Mars elevation reference is from the Mars Global Surveyor (MGS) MOLA MEGDR data family. The downloaded product labels and metadata should be retained alongside the raw data.

**Earth data provenance note:** The Earth reference used by Member 3 is the processed project dataset supplied through the TERRATIME4D Earth-data workflow. It is not a NASA planetary mission dataset. Its original source and processing details should be documented by the Earth-data team.

## 8. Scientific limitations and correct interpretation

The Earth, Moon and Mars values are not perfectly equivalent measurements.

1. Earth uses available tile-level summary records, while Moon and Mars use global elevation grids.
2. Earth averages are unweighted averages of tile statistics; Moon and Mars use area-weighted global-grid calculations.
3. Earth roughness is reported at 270 m, 630 m and 1350 m scales. Moon and Mars roughness is reported at approximately 11 km. These scales are not directly equivalent.
4. Elevation reference surfaces and datums differ between planetary products. Mean elevation values should not be treated as directly comparable heights above one shared zero level.
5. MOLA MEGDR includes interpolated values where observations are unavailable.
6. The Moon raster used in this workflow lacks ordinary geographic georeferencing metadata.
7. Earth cannot reproduce lunar gravity and vacuum or the Martian atmosphere and radiation environment.

Therefore, the comparison is a physical-terrain reference study, not proof that a particular Earth location fully reproduces a lunar or Martian environment.

## 9. Recommended use by Member 4

Member 4 can use the documented outputs as planetary reference inputs.

Recommended practices:

- Use the Moon and Mars summaries as separate reference profiles.
- Compare slope and roughness only after considering their spatial scales and calculation methods.
- Use latitude-band results when regional variation matters.
- Account for Earth coverage, tile weighting and planetary elevation-datum differences.
- Preserve the source and processing limitations when calculating similarity.
- Do not treat Member 3's comparison values as precomputed mission-suitability scores.

Member 4 remains responsible for implementing and validating the similarity and mission-scoring method.

## 10. Member 3 handoff checklist

- [x] Prepare Moon and Mars elevation reference datasets.
- [x] Calculate global physical terrain summaries.
- [x] Prepare the Earth reference audit and updated 648-record comparison.
- [x] Generate planetary comparison CSV, report and figures.
- [x] Prepare the scientific analogy assessment.
- [x] Prepare the consolidated Member 3 final report.
- [ ] Save this handoff document in the repository.
- [ ] Verify all referenced files and folders exist.
- [ ] Commit and push the handoff document to GitHub.
- [ ] Confirm the final handoff is visible on the remote repository.

**Handoff status:** The analysis outputs are prepared. The handoff is complete only after this document and its referenced deliverables have been verified and pushed to the project repository.

