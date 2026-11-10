# TERRATIME4D — Member 2: Global Terrain Analysis Report

## 1. Objective

The objective was to process Copernicus GLO-90 elevation data, derive terrain characteristics, classify surface morphology, and screen terrain tiles for preliminary rover mobility and landing-study relevance.

## 2. Global processing coverage

- Advanced terrain summary records: **645**
- Rover screening records: **645**
- Ranked terrain tiles: **645**
- Advanced terrain raster outputs: 645, each containing 10 bands.
- Local-relief scales: 270 m, 630 m and 1,350 m.

## 3. Terrain measurements

The analysis derives slope in degrees, local elevation roughness at three spatial scales, local relief at three scales, hidden ruggedness indicators and terrain-transition hotspot indicators.

Local roughness represents neighbourhood elevation variability. Local relief represents the neighbourhood elevation range (maximum minus minimum).

## 4. Terrain classification

Terrain classification outputs are available in `global_terrain_classification_summary.csv` and `classification_rasters/`. The classification distinguishes flat/smooth, rolling, rugged, relative ridge and relative valley terrain using the implemented TPI-based method.

## 5. Rover terrain screening

Exploratory pixel thresholds were applied: lower-relief (slope <= 5 degrees and 630 m roughness <= 2 m), intermediate (slope <= 15 degrees and roughness <= 5 m, excluding lower-relief), and challenging (remaining valid pixels).

| Tile-level percentage measure | Mean across 645 tiles |
|---|---:|
| Lower-relief | 44.87% |
| Intermediate | 19.69% |
| Challenging | 35.44% |

These are unweighted averages of tile-level percentages, not pixel-weighted global surface estimates.

## 6. Global ranking method

Tiles were ranked using a weighted relative score: slope 35%, 630 m roughness 25%, 630 m local relief 20%, and lower-relief screening share 20%. The score is a comparative screening index within this dataset, not a probability or certified site rating.

## 7. Geographic candidate groups

- Polar candidates (absolute latitude >= 60 degrees): **25 shortlisted**
- Non-polar candidates (absolute latitude < 60 degrees): **25 shortlisted**

### Top 10 non-polar candidates

                                                     tile  rover_screening_score_100  latitude  longitude
copernicus_dsm_cog_30_n07_00_e032_00_dem_advanced_terrain                    98.8062    7.5004    32.4996
copernicus_dsm_cog_30_n57_00_w093_00_dem_advanced_terrain                    97.3566   57.5004   -92.5006
copernicus_dsm_cog_30_s33_00_w063_00_dem_advanced_terrain                    93.4109  -32.4996   -62.5004
copernicus_dsm_cog_30_s23_00_e022_00_dem_advanced_terrain                    91.1705  -22.4996    22.4996
copernicus_dsm_cog_30_s18_00_e017_00_dem_advanced_terrain                    90.5659  -17.4996    17.4996
copernicus_dsm_cog_30_n12_00_e017_00_dem_advanced_terrain                    89.4961   12.5004    17.4996
copernicus_dsm_cog_30_s18_00_e132_00_dem_advanced_terrain                    89.2946  -17.4996   132.4996
copernicus_dsm_cog_30_s28_00_w063_00_dem_advanced_terrain                    89.2248  -27.4996   -62.5004
copernicus_dsm_cog_30_s23_00_w063_00_dem_advanced_terrain                    87.3566  -22.4996   -62.5004
copernicus_dsm_cog_30_s33_00_w053_00_dem_advanced_terrain                    86.9767  -32.4996   -52.5004

### Top 10 polar candidates

                                                     tile  rover_screening_score_100  latitude  longitude
copernicus_dsm_cog_30_n72_00_w038_00_dem_advanced_terrain                    99.5271   72.5004   -37.5012
copernicus_dsm_cog_30_s78_00_e122_00_dem_advanced_terrain                    98.9922  -77.4996   122.4988
copernicus_dsm_cog_30_s78_00_e147_00_dem_advanced_terrain                    98.8527  -77.4996   147.4988
copernicus_dsm_cog_30_s83_00_e047_00_dem_advanced_terrain                    98.4341  -82.4996    47.4979
copernicus_dsm_cog_30_s73_00_e052_00_dem_advanced_terrain                    98.4031  -72.4996    52.4988
copernicus_dsm_cog_30_s78_00_e112_00_dem_advanced_terrain                    98.2868  -77.4996   112.4988
copernicus_dsm_cog_30_s78_00_e117_00_dem_advanced_terrain                    98.2403  -77.4996   117.4988
copernicus_dsm_cog_30_s73_00_e157_00_dem_advanced_terrain                    98.1550  -72.4996   157.4988
copernicus_dsm_cog_30_s73_00_e112_00_dem_advanced_terrain                    97.9302  -72.4996   112.4988
copernicus_dsm_cog_30_s78_00_e087_00_dem_advanced_terrain                    97.5969  -77.4996    87.4988

## 8. Interpretation

The ranking identifies tiles with comparatively favourable slope, roughness, local-relief and lower-relief screening values. Separating polar and non-polar groups prevents very low-relief polar tiles from automatically dominating every candidate list. The shortlist is a basis for further investigation, not a final selection of rover landing sites.

## 9. Limitations

- Copernicus GLO-90 is a digital surface model; vegetation and built structures can influence terrain measurements.
- A 90 m elevation product cannot resolve every small-scale hazard.
- The 645 processed tiles represent sampled coverage, not a continuous, complete global terrain survey.
- Screening thresholds and weights are exploratory and are not NASA-certified engineering criteria.
- Climate, surface material, imagery, illumination, communications, and mission-specific constraints require separate assessment.
- Static DEM metrics describe terrain morphology, not measured terrain change through time.

## 10. Output inventory

- `global_advanced_terrain_summary.csv`
- `global_terrain_fingerprints.csv`
- `advanced_rasters/`
- `global_terrain_classification_summary.csv`
- `classification_rasters/`
- `rover_screening/global_rover_screening_summary.csv`
- `rover_screening/global_rover_screening_map.png`
- `rover_screening/global_rover_terrain_ranking.csv`
- `rover_screening/global_rover_terrain_ranking_map.png`
- `rover_screening/geographic_candidate_shortlist.csv`
- `rover_screening/geographic_candidate_shortlist_map.png`
- `rover_screening/CANDIDATE_EVIDENCE_ASSESSMENT.md`
