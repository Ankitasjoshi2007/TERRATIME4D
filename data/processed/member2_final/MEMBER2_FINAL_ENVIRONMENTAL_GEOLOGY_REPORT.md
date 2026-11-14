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