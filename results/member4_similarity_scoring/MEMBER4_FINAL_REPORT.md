# TERRATIME4D — Member 4 Final Report
## Similarity Screening and Mission-Specific Scoring

**Role:** Member 4 — Similarity and Mission Scoring Engine  
**Scope:** Six Earth candidate regions, Moon/Mars terrain comparisons, and four mission-oriented screening profiles.

## 1. Objective

The Member 4 module combines available terrain and environmental evidence
to compare six Earth candidate regions for different planetary mission
analogue objectives.

The output is a preliminary screening framework. It does not identify
validated mission sites or establish physical equivalence between Earth,
the Moon, and Mars.

## 2. Inputs and evidence

- Terrain similarity comparisons against Moon and Mars latitude-band
  averages.
- Environmental indicators for six Earth candidates.
- Terrain and environmental evidence are joined by candidate name.
- Four mission profiles are evaluated independently.

The environmental dataset contains six candidates. The terrain dataset
contains six candidates compared against each of two planetary references.

## 3. Terrain comparison results

The terrain comparison uses mean and 90th-percentile slope differences.
Lower combined differences indicate closer slope statistics within the
selected latitude band.

Roughness is excluded from the planetary similarity calculation because
the available Earth and planetary measurements use incompatible spatial
scales. Elevation is excluded because the vertical reference datums are
not sufficiently harmonized.

### Moon terrain ranking

| candidate | combined_slope_difference_degrees | rank_within_planet |
| --- | --- | --- |
| Ontario Canada | 1.84 | 1 |
| Brooks Range Alaska | 3.16 | 2 |
| Baja California Mexico | 5.19 | 3 |
| Western Australia | 6.31 | 4 |
| Queensland Australia | 6.42 | 5 |
| Scandinavia | 14.55 | 6 |

### Mars terrain ranking

| candidate | combined_slope_difference_degrees | rank_within_planet |
| --- | --- | --- |
| Queensland Australia | 1.45 | 1 |
| Western Australia | 1.48 | 2 |
| Ontario Canada | 3.96 | 3 |
| Baja California Mexico | 9.80 | 4 |
| Brooks Range Alaska | 10.35 | 5 |
| Scandinavia | 21.73 | 6 |

## 4. Environmental screening

Environmental indices are relative percentile positions among the six
Earth candidates only. They are not percentages of lunar or Martian
similarity.

- Solar power: higher irradiance is favoured.
- Low aerosol: lower aerosol optical depth is favoured.
- Dry-site analogue: lower surface-water occurrence is favoured.
- Water-resource prospecting: higher surface-water occurrence is favoured.
- Persistent water: higher observed persistence is reported as a separate
  indicator.
- Temperature remains a measured value without a directional ranking.
- Geological record count is evidence coverage only, not mineral abundance
  or resource value.

### Solar ranking

| candidate | mean_solar_irradiance_w_m2 | solar_rank |
| --- | --- | --- |
| Baja California Mexico | 254.79 | 1 |
| Queensland Australia | 248.69 | 2 |
| Western Australia | 231.78 | 3 |
| Ontario Canada | 142.10 | 4 |
| Brooks Range Alaska | 108.03 | 5 |
| Scandinavia | 85.60 | 6 |

### Dry-site ranking

| candidate | mean_water_occurrence_percent | dry_site_rank |
| --- | --- | --- |
| Baja California Mexico | 0.00 | 1 |
| Queensland Australia | 0.09 | 2 |
| Western Australia | 0.10 | 3 |
| Ontario Canada | 1.69 | 4 |
| Scandinavia | 2.68 | 5 |
| Brooks Range Alaska | 8.58 | 6 |

### Water-resource screening ranking

| candidate | mean_water_occurrence_percent | water_resource_rank |
| --- | --- | --- |
| Brooks Range Alaska | 8.58 | 1 |
| Scandinavia | 2.68 | 2 |
| Ontario Canada | 1.69 | 3 |
| Western Australia | 0.10 | 4 |
| Queensland Australia | 0.09 | 5 |
| Baja California Mexico | 0.00 | 6 |

## 5. Mission-specific screening profiles

Each profile uses explicit initial weights. Terrain input is converted
from its ordinal rank into a 0–100 rank-position index before weighting.
Environmental inputs use their relative indices.

| Mission profile | Terrain | Solar | Dry-site | Water | Persistent water |
|---|---:|---:|---:|---:|---:|
| Lunar rover mobility | 80% | 20% | — | — | — |
| Lunar polar operations | 35% | 35% | — | 30% | — |
| Mars rover mobility | 75% | 10% | 15% | — | — |
| Lunar resource prospecting | 20% | — | — | 60% | 20% |

These weights are preliminary model assumptions, not validated mission
requirements. Geological record count and temperature are reported
separately and are not included in the composite.

### Lunar polar operations

| candidate | mission_screening_score | mission_rank | mean_temperature_c | geological_record_count |
| --- | --- | --- | --- | --- |
| Ontario Canada | 72.50 | 1 | 2.69 | 4 |
| Brooks Range Alaska | 69.67 | 2 | -8.39 | 5 |
| Baja California Mexico | 61.00 | 3 | 23.63 | 3 |
| Western Australia | 52.33 | 4 | 16.77 | 3 |
| Queensland Australia | 46.17 | 5 | 23.35 | 3 |
| Scandinavia | 30.83 | 6 | -2.51 | 5 |

### Lunar resource prospecting

| candidate | mission_screening_score | mission_rank | mean_temperature_c | geological_record_count |
| --- | --- | --- | --- | --- |
| Brooks Range Alaska | 96.00 | 1 | -8.39 | 5 |
| Ontario Canada | 73.33 | 2 | 2.69 | 4 |
| Scandinavia | 66.67 | 3 | -2.51 | 5 |
| Western Australia | 44.67 | 4 | 16.77 | 3 |
| Queensland Australia | 30.67 | 5 | 23.35 | 3 |
| Baja California Mexico | 28.67 | 6 | 23.63 | 3 |

### Lunar rover mobility

| candidate | mission_screening_score | mission_rank | mean_temperature_c | geological_record_count |
| --- | --- | --- | --- | --- |
| Ontario Canada | 90.00 | 1 | 2.69 | 4 |
| Brooks Range Alaska | 70.67 | 2 | -8.39 | 5 |
| Baja California Mexico | 68.00 | 3 | 23.63 | 3 |
| Western Australia | 45.33 | 4 | 16.77 | 3 |
| Queensland Australia | 32.67 | 5 | 23.35 | 3 |
| Scandinavia | 3.33 | 6 | -2.51 | 5 |

### Mars rover mobility

| candidate | mission_screening_score | mission_rank | mean_temperature_c | geological_record_count |
| --- | --- | --- | --- | --- |
| Queensland Australia | 95.83 | 1 | 23.35 | 3 |
| Western Australia | 76.67 | 2 | 16.77 | 3 |
| Ontario Canada | 57.50 | 3 | 2.69 | 4 |
| Baja California Mexico | 55.00 | 4 | 23.63 | 3 |
| Brooks Range Alaska | 20.83 | 5 | -8.39 | 5 |
| Scandinavia | 6.67 | 6 | -2.51 | 5 |

## 6. Scientific limitations and interpretation

1. The six Earth candidates are a limited comparison set, not a global
   ranking of all possible analogue sites.
2. Planetary terrain references are latitude-band averages, not exact
   local landing-site measurements.
3. Earth and planetary terrain datasets differ in spatial resolution
   and aggregation.
4. Roughness is excluded from the planetary score because measurement
   scales are incompatible.
5. Elevation is excluded from direct similarity scoring because
   vertical datums differ.
6. Earth surface-water occurrence does not establish the presence of
   lunar ice or Martian subsurface water.
7. Earth solar irradiance does not represent lunar polar illumination
   or a mission-specific power budget.
8. Aerosol optical depth is not a dust-only measurement.
9. NASA POWER temperature and solar inputs represent 2020.
10. Geological record counts describe available records, not mineral
    abundance, diversity, or economic/resource value.
11. The scores are weighted screening indices, not probabilities,
    mission-success estimates, or physical similarity percentages.
12. Static DEM-derived terrain metrics do not describe terrain change
    over time.

## 7. Validation summary

- Terrain comparisons: 12 records (six candidates × two planets).
- Environmental screening: six unique candidates.
- Mission profiles: four.
- Mission-specific scores: 24 records.
- Six candidates are represented in every mission profile.
- Missing values in the validated mission score output: zero.
- Mission scores are within the 0–100 range.
- Weighted component contributions reproduce the reported score,
  within floating-point precision.

## 8. Conclusion

The current screening results identify different leading Earth
candidates for different mission objectives. Queensland and Western
Australia rank strongly in the preliminary Mars rover slope comparison,
while Ontario leads the lunar rover and lunar polar profiles under the
current assumptions. Brooks Range leads the lunar resource prospecting
profile because of its high Earth surface-water indicators.

These results demonstrate why analogue selection should be
mission-specific. They are preliminary comparative results and require
resolution-matched planetary site data, validated mission requirements,
and expert review before operational interpretation.

---
**Member 4 deliverables:** terrain similarity scores, environmental
screening scores, mission-specific scores, methodology files, and this
consolidated report.
