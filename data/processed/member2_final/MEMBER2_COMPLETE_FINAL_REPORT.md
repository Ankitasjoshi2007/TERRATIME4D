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
# TERRATIME4D — MEMBER 2 FINAL ENVIRONMENTAL AND GEOLOGY REPORT

## Scope
Comparative environmental, geological and terrain screening of six priority Earth candidate locations.

## Datasets and analysis outputs
### Environmental comparison
- Candidates analysed: 6
- Output columns: candidate, mean_temperature_c, mean_solar_irradiance_w_m2, annual_mean_aod_55, mean_water_occurrence_percent, pixels_with_detected_water_percent, persistent_water_pixels_percent, geological_record_count, terrain_slope_mean_degrees, terrain_roughness_630m_mean, terrain_hidden_ruggedness_percent

             candidate  mean_temperature_c  mean_solar_irradiance_w_m2  annual_mean_aod_55  mean_water_occurrence_percent  pixels_with_detected_water_percent  persistent_water_pixels_percent  geological_record_count  terrain_slope_mean_degrees  terrain_roughness_630m_mean  terrain_hidden_ruggedness_percent
     Western Australia           16.769167                  231.785000            0.056667                       0.099288                            0.348125                         0.000000                        3                    1.454839                     4.307965                           0.293056
  Queensland Australia           23.354167                  248.691667            0.091667                       0.085663                            0.640625                         0.000000                        3                    1.147186                     2.962100                           0.344792
Baja California Mexico           23.631667                  254.790833            0.096667                       0.001050                            0.011875                         0.000000                        3                    6.340235                    17.240425                           0.028750
        Ontario Canada            2.686667                  142.100000            0.165833                       1.688044                            2.313750                         0.837500                        4                    3.634919                     8.329711                           3.358472
   Brooks Range Alaska           -8.393333                  108.025000            0.076667                       8.578312                            9.752500                         6.464375                        5                    9.678308                    29.449533                           0.114722
           Scandinavia           -2.510833                   85.600833            0.089167                       2.684738                            3.845000                         1.186250                        5                   10.871079                    35.468834                           0.132083

### Cold-climate screening
- Candidates analysed: 6
- Output columns: candidate, months_with_mean_temp_at_or_below_0C, months_with_mean_daily_min_at_or_below_0C, months_with_mean_daily_max_at_or_below_0C, annual_mean_temperature_c, coldest_month, coldest_month_mean_temperature_c, lowest_monthly_mean_daily_min_c, months_analysed

        candidate  months_with_mean_temp_at_or_below_0C  months_with_mean_daily_min_at_or_below_0C  months_with_mean_daily_max_at_or_below_0C  annual_mean_temperature_c  coldest_month  coldest_month_mean_temperature_c  lowest_monthly_mean_daily_min_c  months_analysed
     Brooks Range                                     7                                          9                                          7                  -8.393333              1                            -27.78                           -30.95               12
      Scandinavia                                     8                                          8                                          8                  -2.510833              2                            -10.26                           -13.33               12
          Ontario                                     6                                          7                                          4                   2.686667              2                            -12.99                           -18.98               12
  Baja California                                     0                                          0                                          0                  23.631667              1                             15.76                            12.12               12
       Queensland                                     0                                          0                                          0                  23.354167              7                             15.73                             9.39               12
Western Australia                                     0                                          0                                          0                  16.769167              7                              9.70                             5.19               12

### Aerosol variability
- Candidates analysed: 6
- Output columns: candidate, annual_mean_aod, adjusted_annual_mean_aod, peak_aod, peak_month, minimum_aod, minimum_month, aod_range, monthly_aod_std, high_loading_months, months_analysed

             candidate  annual_mean_aod  adjusted_annual_mean_aod  peak_aod  peak_month  minimum_aod  minimum_month  aod_range  monthly_aod_std  high_loading_months  months_analysed
        Ontario Canada         0.165833                  0.165833      0.42           9         0.05              2       0.37         0.100314                    8               12
Baja California Mexico         0.096667                  0.097500      0.20           9         0.04             12       0.16         0.045991                    3               12
  Queensland Australia         0.091667                  0.091667      0.23           1         0.05              7       0.18         0.051669                    2               12
           Scandinavia         0.089167                  0.089167      0.17           7         0.03              1       0.14         0.044202                    3               12
   Brooks Range Alaska         0.076667                  0.076667      0.24           7         0.00              1       0.24         0.084996                    3               12
     Western Australia         0.056667                  0.056667      0.10           2         0.02              7       0.08         0.023868                    0               12

### Mineral/lithology screening
- Candidates analysed: 6
- Output columns: latitude, longitude, geological_records, igneous_mentions, volcanic_mentions, metamorphic_mentions, sedimentary_mentions, quartz_mentions, feldspar_mentions, mica_mentions, carbonate_mentions, sulfide_mentions, iron_oxide_mentions

 latitude  longitude  geological_records  igneous_mentions  volcanic_mentions  metamorphic_mentions  sedimentary_mentions  quartz_mentions  feldspar_mentions  mica_mentions  carbonate_mentions  sulfide_mentions  iron_oxide_mentions
    -32.5      117.5                   3                 1                  0                     1                     0                0                  0              0                   0                 0                    0
    -22.5      147.5                   3                 0                  2                     0                     1                0                  0              0                   0                 0                    0
     27.5     -112.5                   3                 1                  3                     0                     1                0                  0              0                   0                 0                    0
     47.5      -82.5                   4                 2                  1                     2                     2                0                  0              0                   0                 0                    0
     67.5     -147.5                   5                 0                  0                     2                     3                2                  0              2                   1                 0                    0
     67.5       17.5                   5                 4                  0                     3                     0                0                  0              1                   0                 0                    0

### Volcanic/karst screening
- Candidates analysed: 6
- Output columns: latitude, longitude, geological_records, volcanic_rock_mentions, possible_karst_host_rock_mentions

 latitude  longitude  geological_records  volcanic_rock_mentions  possible_karst_host_rock_mentions
    -32.5      117.5                   3                       0                                  0
    -22.5      147.5                   3                       2                                  0
     27.5     -112.5                   3                       3                                  0
     47.5      -82.5                   4                       1                                  0
     67.5     -147.5                   5                       0                                  2
     67.5       17.5                   5                       0                                  0

## Scientific limitations and outstanding work
- Climate and aerosol measurements represent 2020, not long-term climatology.
- Aerosol optical depth is not a dust-specific concentration measurement.
- Cold-climate screening is not confirmed glacier or ice-cover mapping.
- No dedicated glacier inventory was available locally for exact 50 km coverage analysis.
- Macrostrat lithology descriptions are not confirmed mineral deposits.
- Volcanic rock mentions do not establish active or extinct volcano locations.
- Karst host-rock mentions do not establish cave locations.
- Surface-water occurrence is historical (1984–2024), not current water availability.
- Terrain metrics are based on elevation data and do not measure temporal change.

## Conclusion
The six candidate environments have been compared using available climate, aerosol,
surface-water, geology and terrain evidence. Cold-climate, mineral-lithology and
volcanic/karst indicator screenings provide preliminary evidence only. Dedicated
glacier, dust, mineral-deposit, volcano and cave inventories remain necessary for
confirmed feature mapping.