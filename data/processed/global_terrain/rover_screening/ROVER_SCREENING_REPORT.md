# Global Preliminary Rover Terrain Screening

Date: 9 November 2026

## 1. Overview

A preliminary terrain screening was performed using the advanced terrain rasters for 645 Copernicus DEM tiles.

## 2. Input data

- Input tiles: 645
- Successfully processed: 645
- Failed: 0
- Output screening rasters: 645
- Summary CSV: global_rover_screening_summary.csv
- Global map: global_rover_screening_map.png

## 3. Screening methodology

Slope and 630 m local elevation roughness were used as exploratory indicators.

The following thresholds were applied:

- Lower-relief: slope <= 5 degrees AND roughness <= 2 m.
- Intermediate: slope <= 15 degrees AND roughness <= 5 m, excluding lower-relief pixels.
- Challenging: all remaining valid pixels.

Invalid pixels were excluded from the class percentage calculations.

## 4. Results

Mean percentages across the 645 individual tiles:

| Category | Mean percentage |
|---|---:|
| Lower-relief | 44.87% |
| Intermediate | 19.69% |
| Challenging | 35.44% |

The three mean percentages sum to 100%.

These are unweighted averages of tile-level percentages, not pixel-weighted global area estimates.

## 5. Validation

- Summary records: 645
- Unique tiles: 645
- Duplicate tiles: 0
- Screening rasters: 645
- Category percentage checks passed: 645/645
- Processing failures: 0

## 6. Limitations

This is a preliminary terrain-screening product, not a certified rover mobility or landing-site safety assessment.

The thresholds are exploratory and are not NASA-approved operational limits. Copernicus GLO-90 is a digital surface model; vegetation, buildings and other surface features can influence elevation-derived metrics.

The 645 processed tiles are sampled geographic coverage, not continuous global coverage. Results should be interpreted alongside imagery, data quality, local hazards and mission-specific engineering constraints.

## 7. Output locations

- Screening rasters: screening_rasters/
- Summary: global_rover_screening_summary.csv
- Map: global_rover_screening_map.png
