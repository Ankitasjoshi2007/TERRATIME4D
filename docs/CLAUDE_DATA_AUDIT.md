TERRATIME4D — VERIFIED CSV DATA AUDIT
Generated from the local main-branch working repository.

IMPORTANT:
This audit reports actual CSV files found locally.
Do not invent values or replace these datasets with demo data.

KEY MEMBER 1 TERRAIN OUTPUTS:
data/processed/global_terrain_features.csv
Rows: 13
Columns: location_tile, valid_elevation_pixels, valid_slope_pixels, minimum_elevation_m, maximum_elevation_m, average_elevation_m, average_slope_degrees, maximum_slope_degrees, relief_m, pixel_width_m_approx, pixel_height_m_approx, average_roughness_m, terrain_class

data/processed/global_roughness_summary.csv
Rows: 13
Columns: tile, valid_pixels, average_roughness_m, maximum_roughness_m, minimum_roughness_m

data/processed/advanced_terrain/advanced_terrain_summary.csv
Rows: 6
Columns: location, raster_file, raster_width, raster_height, raster_valid_pixels, analysis_pixels, mask_method, pixel_width_mean_m, pixel_height_mean_m, elevation_min_m, elevation_max_m, elevation_mean_m, roughness_270m_mean, roughness_270m_p90, roughness_270m_window, roughness_630m_mean, roughness_630m_p90, roughness_630m_window, roughness_1350m_mean, roughness_1350m_p90, roughness_1350m_window, hidden_slope_p30_degrees, hidden_roughness_p70_m, hidden_ruggedness_pixels, hidden_ruggedness_percent, transition_score_p95, transition_hotspot_pixels, transition_hotspot_percent, slope_mean_degrees, slope_p90_degrees

data/processed/advanced_terrain/terrain_classification.csv
Rows: 6
Columns: location, raster_file, valid_classification_pixels, tpi_window_pixels, tpi_target_scale_m, land_mask_method, slope_p30_degrees, slope_p80_degrees, roughness_p30_m, roughness_p80_m, tpi_median_m, tpi_standard_deviation_m, flat_smooth_pixels, flat_smooth_percent, rolling_pixels, rolling_percent, rugged_pixels, rugged_percent, relative_ridge_pixels, relative_ridge_percent, relative_valley_pixels, relative_valley_percent

data/processed/global_terrain/rover_screening/global_rover_screening_summary.csv
Rows: 645
Columns: tile, valid_pixels, mean_slope_degrees, p90_slope_degrees, mean_roughness_630m_m, p90_roughness_630m_m, lower_relief_screen_percent, intermediate_screen_percent, challenging_terrain_percent, screening_raster

data/processed/global_terrain/rover_screening/global_rover_terrain_ranking.csv
Rows: 645
Columns: rank, tile, rover_screening_score_100, p90_slope_degrees, p90_roughness_630m_m, local_relief_630m_p90_m, lower_relief_screen_percent, mean_slope_degrees, mean_roughness_630m_m, challenging_terrain_percent, longitude, latitude

KEY MEMBER 2 ENVIRONMENT/GEOLOGY OUTPUTS:

data/processed/dust_aerosol_analysis/candidate_aerosol_variability.csv
Rows: 6
Columns: candidate, annual_mean_aod, adjusted_annual_mean_aod, peak_aod, peak_month, minimum_aod, minimum_month, aod_range, monthly_aod_std, high_loading_months, months_analysed

data/processed/dust_aerosol_analysis/monthly_aerosol_loading_flags.csv
Rows: 72
Columns: location, latitude, longitude, year, month, aod_55, aod_55_adjusted, high_aerosol_loading_month

data/processed/environmental/nasa_power_monthly_temperature_2020.csv
Rows: 72
Columns: location, latitude, longitude, year, month, mean_temperature_c, mean_daily_max_temperature_c, mean_daily_min_temperature_c

data/processed/environmental/nasa_power_monthly_solar_2020.csv
Rows: 72
Columns: location, latitude, longitude, year_month, solar_irradiance_w_m2

data/processed/ice_climate_analysis/six_candidate_cold_climate_screening.csv
Rows: 6
Columns: candidate, months_with_mean_temp_at_or_below_0C, months_with_mean_daily_min_at_or_below_0C, months_with_mean_daily_max_at_or_below_0C, annual_mean_temperature_c, coldest_month, coldest_month_mean_temperature_c, lowest_monthly_mean_daily_min_c, months_analysed

data/processed/mineral_lithology_analysis/candidate_mineral_lithology_screening.csv
Rows: 6
Columns: latitude, longitude, geological_records, igneous_mentions, volcanic_mentions, metamorphic_mentions, sedimentary_mentions, quartz_mentions, feldspar_mentions, mica_mentions, carbonate_mentions, sulfide_mentions, iron_oxide_mentions

data/processed/volcanic_karst_analysis/volcanic_karst_candidate_screening.csv
Rows: 6
Columns: latitude, longitude, geological_records, volcanic_rock_mentions, possible_karst_host_rock_mentions

data/processed/environmental_comparison/six_candidate_environmental_comparison.csv
Rows: 6
Columns: candidate, mean_temperature_c, mean_solar_irradiance_w_m2, annual_mean_aod_55, mean_water_occurrence_percent, pixels_with_detected_water_percent, persistent_water_pixels_percent, geological_record_count, terrain_slope_mean_degrees, terrain_roughness_630m_mean, terrain_hidden_ruggedness_percent

KEY MEMBER 3 PLANETARY COMPARISON OUTPUTS:

results/member3_global_analysis_v3/moon_mars_latitude_band_analysis_v3.csv
Rows: 36
Columns: planet, latitude_band, elevation_mean_km, elevation_min_km, elevation_max_km, slope_mean_degrees, slope_p90_degrees, roughness_mean_km, roughness_p90_km

results/member3_global_analysis_v3/moon_mars_physical_summary_v3.csv
Rows: 2
Columns: planet, rows, columns, total_cells, elevation_min_km, elevation_max_km, elevation_grid_mean_km, elevation_area_weighted_mean_km, slope_mean_degrees, slope_area_weighted_mean_degrees, slope_median_degrees, slope_p90_degrees, slope_valid_cells, roughness_mean_km, roughness_area_weighted_mean_km, roughness_median_km, roughness_p90_km, roughness_valid_cells, equatorial_pixel_size_km, roughness_target_km

results/member3_global_comparison_v3/planetary_comparison_values_v3.csv
Rows: 3
Columns: Planet, Mean_Slope_Degrees, Mean_Elevation_km, Mean_Roughness_m, Earth_Roughness_270m_m, Earth_Roughness_630m_m, Earth_Roughness_1350m_m, Roughness_Scale, Reference_Coverage

results/member3_global_analysis_v3/earth_reference_tile_records_v3.csv
Rows: 648
Columns: location, raster_file, raster_width, raster_height, raster_valid_pixels, analysis_pixels, mask_method, pixel_width_mean_m, pixel_height_mean_m, elevation_min_m, elevation_max_m, elevation_mean_m, roughness_270m_mean, roughness_270m_p90, roughness_270m_window, roughness_630m_mean, roughness_630m_p90, roughness_630m_window, roughness_1350m_mean, roughness_1350m_p90, roughness_1350m_window, hidden_slope_p30_degrees, hidden_roughness_p70_m, hidden_ruggedness_pixels, hidden_ruggedness_percent, transition_score_p95, transition_hotspot_pixels, transition_hotspot_percent, slope_mean_degrees, slope_p90_degrees

KEY MEMBER 4 FINAL SCORING OUTPUTS:

results/member4_similarity_scoring/environmental_screening_scores.csv
Rows: 6
Columns: candidate, mean_temperature_c, mean_solar_irradiance_w_m2, solar_power_relative_index, solar_rank, annual_mean_aod_55, low_aerosol_relative_index, aerosol_rank, mean_water_occurrence_percent, dry_site_relative_index, dry_site_rank, water_resource_relative_index, water_resource_rank, persistent_water_pixels_percent, persistent_water_relative_index, geological_record_count

results/member4_similarity_scoring/integrated_candidate_evidence.csv
Rows: 6
Columns: 59
Includes candidate, latitude, longitude, elevation, slope, roughness, temperature, solar, aerosol, water, cold-climate, mineral, volcanic and karst evidence fields.

results/member4_similarity_scoring/integrated_mission_scores.csv
Rows: 42
Columns: 32
Columns:
mission_profile, target_planet, profile_type, candidate, screening_index_0_100, terrain_index, solar_index, terrain_contribution, solar_contribution, evidence_sources_present, evidence_sources_expected, cold_months_index, water_index, cold_months_contribution, water_contribution, dry_site_index, aerosol_mean_index, dry_site_contribution, aerosol_mean_contribution, persistent_water_index, persistent_water_contribution, aerosol_variability_index, high_loading_months_index, aerosol_variability_contribution, high_loading_months_contribution, volcanic_evidence_rate_index, karst_evidence_rate_index, volcanic_evidence_rate_contribution, karst_evidence_rate_contribution, coldest_month_index, coldest_month_contribution, mission_rank

results/member4_similarity_scoring/mission_specific_scores.csv
Rows: 24
Columns: 17
Columns:
mission_profile, target_planet, candidate, mission_screening_score, mission_rank, terrain_rank_relative_index, terrain_contribution, solar_power_relative_index, solar_contribution, dry_site_relative_index, dry_site_contribution, water_resource_relative_index, water_resource_contribution, persistent_water_relative_index, persistent_water_contribution, mean_temperature_c, geological_record_count

results/member4_similarity_scoring/terrain_similarity_scores.csv
Rows: 12
Columns: 12
Columns:
candidate, latitude, latitude_band, planet, earth_slope_mean_degrees, planetary_band_slope_mean_degrees, earth_slope_p90_degrees, planetary_band_slope_p90_degrees, mean_slope_difference_degrees, p90_slope_difference_degrees, combined_slope_difference_degrees, rank_within_planet

results/member4_similarity_scoring/weight_sensitivity_summary.csv
Rows: 7
Columns: mission_profile, scenarios_tested, top_candidate_changes, mean_rank_shift, maximum_rank_shift

IMPORTANT TEMPORAL DATA:

data/processed/temporal_analysis/global/global_temporal_targets.csv
Rows: 645
Columns: tile, raster, west, south, east, north, center_lon, center_lat, width, height

data/processed/temporal_analysis/global/global_temporal_observation_coverage.csv
Rows: 5160
Columns: dem_tile, year, selected_scene_count, status, discovery_status

data/processed/temporal_analysis/global/global_tile_change_metrics_fast.csv
Rows: 1847
Columns: pair_id, mgrs_tile, quarter, first_scene, first_date, last_scene, last_date, gap_days, longitude, latitude, first_mean_ndvi, last_mean_ndvi, ndvi_change, first_vegetation_fraction, last_vegetation_fraction, vegetation_fraction_change, first_bare_soil_fraction, last_bare_soil_fraction, first_water_fraction, last_water_fraction, first_valid_fraction, last_valid_fraction

data/processed/temporal_analysis/dune_displacement/dune_displacement_summary.csv
Rows: 7
Columns: reference_year, comparison_year, accepted_blocks, apparent_dx_pixels, apparent_dy_pixels, apparent_dx_metres, apparent_dy_metres, apparent_displacement_metres, median_peak_ratio

IMPORTANT:
The temporal data is much richer than just the 2020 NASA POWER monthly data. The repository contains Sentinel temporal observation and change metrics, including NDVI, bare soil, water fraction and dune displacement over multiple dates/years.

DO NOT:
- invent missing values
- replace real data with dummy data
- modify scientific CSVs
- recompute Member 4 scores in the frontend
- ignore Member 1–4 provenance

Use this audit to inspect the repository more efficiently. The frontend must consume the actual scientific outputs.

End of audit.
