# TERRATIME4D — Member 4 Final Report
## Integrated Similarity Screening and Mission-Specific Scoring

**Role:** Member 4 — Similarity and Mission Scoring Engine
**Candidate set:** Six Earth regions
**Planetary references:** Moon and Mars
**Mission profiles:** Seven
**Primary integrated output:** `integrated_mission_scores.csv`

## 1. Objective

Member 4 combines terrain, environmental, aerosol, cold-climate,
mineral/geological, and volcanic/karst evidence to screen Earth regions
for different lunar and Martian analogue research objectives.

The engine produces mission-specific, relative screening indices.
It does not identify validated landing sites, establish physical
equivalence between planetary environments, or predict mission success.

## 2. Integrated evidence

The integrated candidate evidence joins six evidence families:

1. Terrain metrics and terrain classifications.
2. Environmental indicators, including solar irradiance and water occurrence.
3. Aerosol loading and variability indicators.
4. Cold-climate screening indicators.
5. Mineral and lithological geological records.
6. Volcanic and possible karst geological evidence.

The integrated evidence build contains six Earth candidates, with all
six evidence families represented for every candidate. Evidence coverage
means that source records were available; it does not mean that every
candidate has equally detailed or equally reliable observations.

## 3. Planetary terrain similarity

Terrain similarity compares Earth candidate slope statistics with
available Moon and Mars latitude-band summaries. The calculation uses
mean slope and 90th-percentile slope differences. Lower combined
differences indicate closer slope statistics within the selected band.

Roughness is excluded from the planetary similarity calculation because
the available Earth and planetary measurements use incompatible spatial
scales. Elevation is excluded because vertical reference datums are not
sufficiently harmonized.

### Moon terrain ranking

| candidate | combined_slope_difference_degrees | rank_within_planet |
| --- | --- | --- |
| Ontario Canada | 1.84 | 1.00 |
| Brooks Range Alaska | 3.16 | 2.00 |
| Baja California Mexico | 5.19 | 3.00 |
| Western Australia | 6.31 | 4.00 |
| Queensland Australia | 6.42 | 5.00 |
| Scandinavia | 14.55 | 6.00 |

### Mars terrain ranking

| candidate | combined_slope_difference_degrees | rank_within_planet |
| --- | --- | --- |
| Queensland Australia | 1.45 | 1.00 |
| Western Australia | 1.48 | 2.00 |
| Ontario Canada | 3.96 | 3.00 |
| Baja California Mexico | 9.80 | 4.00 |
| Brooks Range Alaska | 10.35 | 5.00 |
| Scandinavia | 21.73 | 6.00 |

## 4. Environmental screening context

Environmental indices are relative comparisons among the six Earth
candidates. They are not percentages of lunar or Martian similarity.

- Solar irradiance: higher values are favoured where the profile uses solar input.
- Dry-site indicator: lower surface-water occurrence is favoured.
- Water-resource indicator: higher surface-water occurrence is favoured.
- Persistent-water indicator: reported as a separate Earth observation.
- Temperature indicators describe Earth climate records, not planetary surface conditions.
- Geological record counts describe evidence availability, not mineral abundance.

### Solar irradiance ranking

| candidate | mean_solar_irradiance_w_m2 | solar_rank |
| --- | --- | --- |
| Baja California Mexico | 254.79 | 1.00 |
| Queensland Australia | 248.69 | 2.00 |
| Western Australia | 231.78 | 3.00 |
| Ontario Canada | 142.10 | 4.00 |
| Brooks Range Alaska | 108.03 | 5.00 |
| Scandinavia | 85.60 | 6.00 |

### Water-occurrence context

| candidate | mean_water_occurrence_percent |
| --- | --- |
| Brooks Range Alaska | 8.58 |
| Scandinavia | 2.68 |
| Ontario Canada | 1.69 |
| Western Australia | 0.10 |
| Queensland Australia | 0.09 |
| Baja California Mexico | 0.00 |

## 5. Integrated mission-specific scoring

Each mission profile uses an explicit set of weighted components.
For every component, the model calculates a relative index among the
six candidates and multiplies it by the profile weight.

The final score is the sum of the weighted component contributions.
Scores range from 0 to 100 and are relative to this six-candidate
comparison set. They are not probabilities or universal suitability
measurements.

### 5.1 Profile weights

| Mission profile | Weighted components | Weight total |
| --- | --- | --- |
| Lunar rover mobility | Terrain similarity: 80%; Solar irradiance: 20% | 1.00 |
| Lunar polar operations | Terrain similarity: 25%; Solar irradiance: 25%; Cold-month frequency: 25%; Surface-water occurrence: 25% | 1.00 |
| Mars rover mobility | Terrain similarity: 65%; Dry-site indicator: 15%; Solar irradiance: 10%; Mean aerosol loading: 10% | 1.00 |
| Lunar resource prospecting | Terrain similarity: 20%; Surface-water occurrence: 60%; Persistent water indicator: 20% | 1.00 |
| Mars dust-process analogue | Mean aerosol loading: 40%; Aerosol variability: 35%; High-aerosol months: 25% | 1.00 |
| Volcanic and cave analogue reconnaissance | Volcanic geological evidence rate: 50%; Possible karst host-rock evidence rate: 50% | 1.00 |
| Cold-region operations analogue | Cold-month frequency: 50%; Coldest-month temperature indicator: 50% | 1.00 |

### Lunar rover mobility

**Target:** Moon
**Profile type:** Planetary terrain screening

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Ontario Canada | 86.68 | 1.00 | 6.00 | 6.00 |
| Baja California Mexico | 68.00 | 2.00 | 6.00 | 6.00 |
| Brooks Range Alaska | 66.65 | 3.00 | 6.00 | 6.00 |
| Western Australia | 49.28 | 4.00 | 6.00 | 6.00 |
| Queensland Australia | 35.28 | 5.00 | 6.00 | 6.00 |
| Scandinavia | 0.00 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Terrain similarity | Solar irradiance |
| --- | --- | --- |
| Ontario Canada | 80.00 | 6.68 |
| Baja California Mexico | 48.00 | 20.00 |
| Brooks Range Alaska | 64.00 | 2.65 |
| Western Australia | 32.00 | 17.28 |
| Queensland Australia | 16.00 | 19.28 |
| Scandinavia | 0.00 | 0.00 |

### Lunar polar operations

**Target:** Moon
**Profile type:** Terrestrial polar-environment analogue

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Brooks Range Alaska | 70.19 | 1.00 | 6.00 | 6.00 |
| Ontario Canada | 57.02 | 2.00 | 6.00 | 6.00 |
| Baja California Mexico | 40.00 | 3.00 | 6.00 | 6.00 |
| Scandinavia | 32.82 | 4.00 | 6.00 | 6.00 |
| Western Australia | 31.89 | 5.00 | 6.00 | 6.00 |
| Queensland Australia | 29.35 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Terrain similarity | Solar irradiance | Cold-month frequency | Surface-water occurrence |
| --- | --- | --- | --- | --- |
| Brooks Range Alaska | 20.00 | 3.31 | 21.88 | 25.00 |
| Ontario Canada | 25.00 | 8.35 | 18.75 | 4.92 |
| Baja California Mexico | 15.00 | 25.00 | 0.00 | 0.00 |
| Scandinavia | 0.00 | 0.00 | 25.00 | 7.82 |
| Western Australia | 10.00 | 21.60 | 0.00 | 0.29 |
| Queensland Australia | 5.00 | 24.10 | 0.00 | 0.25 |

### Mars rover mobility

**Target:** Mars
**Profile type:** Planetary terrain and dry-site screening

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Queensland Australia | 92.70 | 1.00 | 6.00 | 6.00 |
| Western Australia | 75.47 | 2.00 | 6.00 | 6.00 |
| Ontario Canada | 64.39 | 3.00 | 6.00 | 6.00 |
| Baja California Mexico | 54.66 | 4.00 | 6.00 | 6.00 |
| Brooks Range Alaska | 16.16 | 5.00 | 6.00 | 6.00 |
| Scandinavia | 13.28 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Terrain similarity | Dry-site indicator | Solar irradiance | Mean aerosol loading |
| --- | --- | --- | --- | --- |
| Queensland Australia | 65.00 | 14.85 | 9.64 | 3.21 |
| Western Australia | 52.00 | 14.83 | 8.64 | 0.00 |
| Ontario Canada | 39.00 | 12.05 | 3.34 | 10.00 |
| Baja California Mexico | 26.00 | 15.00 | 10.00 | 3.66 |
| Brooks Range Alaska | 13.00 | 0.00 | 1.33 | 1.83 |
| Scandinavia | 0.00 | 10.31 | 0.00 | 2.98 |

### Lunar resource prospecting

**Target:** Moon
**Profile type:** Terrestrial water-indicator screening

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Brooks Range Alaska | 96.00 | 1.00 | 6.00 | 6.00 |
| Ontario Canada | 34.39 | 2.00 | 6.00 | 6.00 |
| Scandinavia | 22.44 | 3.00 | 6.00 | 6.00 |
| Baja California Mexico | 12.00 | 4.00 | 6.00 | 6.00 |
| Western Australia | 8.69 | 5.00 | 6.00 | 6.00 |
| Queensland Australia | 4.59 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Terrain similarity | Surface-water occurrence | Persistent water indicator |
| --- | --- | --- | --- |
| Brooks Range Alaska | 16.00 | 60.00 | 20.00 |
| Ontario Canada | 20.00 | 11.80 | 2.59 |
| Scandinavia | 0.00 | 18.77 | 3.67 |
| Baja California Mexico | 12.00 | 0.00 | 0.00 |
| Western Australia | 8.00 | 0.69 | 0.00 |
| Queensland Australia | 4.00 | 0.59 | 0.00 |

### Mars dust-process analogue

**Target:** Mars
**Profile type:** Earth aerosol-process analogue

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Ontario Canada | 100.00 | 1.00 | 6.00 | 6.00 |
| Brooks Range Alaska | 36.01 | 2.00 | 6.00 | 6.00 |
| Baja California Mexico | 33.69 | 3.00 | 6.00 | 6.00 |
| Queensland Australia | 31.14 | 4.00 | 6.00 | 6.00 |
| Scandinavia | 28.52 | 5.00 | 6.00 | 6.00 |
| Western Australia | 0.00 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Mean aerosol loading | Aerosol variability | High-aerosol months |
| --- | --- | --- | --- |
| Ontario Canada | 40.00 | 35.00 | 25.00 |
| Brooks Range Alaska | 7.33 | 19.31 | 9.38 |
| Baja California Mexico | 14.66 | 9.66 | 9.38 |
| Queensland Australia | 12.82 | 12.07 | 6.25 |
| Scandinavia | 11.91 | 7.24 | 9.38 |
| Western Australia | 0.00 | 0.00 | 0.00 |

### Volcanic and cave analogue reconnaissance

**Target:** Not planet-specific
**Profile type:** Earth geological analogue screening

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Baja California Mexico | 50.00 | 1.00 | 6.00 | 6.00 |
| Brooks Range Alaska | 50.00 | 1.00 | 6.00 | 6.00 |
| Queensland Australia | 33.33 | 3.00 | 6.00 | 6.00 |
| Ontario Canada | 12.50 | 4.00 | 6.00 | 6.00 |
| Scandinavia | 0.00 | 5.00 | 6.00 | 6.00 |
| Western Australia | 0.00 | 5.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Volcanic geological evidence rate | Possible karst host-rock evidence rate |
| --- | --- | --- |
| Baja California Mexico | 50.00 | 0.00 |
| Brooks Range Alaska | 0.00 | 50.00 |
| Queensland Australia | 33.33 | 0.00 |
| Ontario Canada | 12.50 | 0.00 |
| Scandinavia | 0.00 | 0.00 |
| Western Australia | 0.00 | 0.00 |

### Cold-region operations analogue

**Target:** Not planet-specific
**Profile type:** Earth cold-environment analogue screening

**Candidate ranking**

| candidate | Screening index (0–100) | Rank | Evidence sources present | Evidence sources expected |
| --- | --- | --- | --- | --- |
| Brooks Range Alaska | 93.75 | 1.00 | 6.00 | 6.00 |
| Scandinavia | 79.88 | 2.00 | 6.00 | 6.00 |
| Ontario Canada | 70.52 | 3.00 | 6.00 | 6.00 |
| Western Australia | 6.96 | 4.00 | 6.00 | 6.00 |
| Queensland Australia | 0.03 | 5.00 | 6.00 | 6.00 |
| Baja California Mexico | 0.00 | 6.00 | 6.00 | 6.00 |

**Weighted component contributions**

| Candidate | Cold-month frequency | Coldest-month temperature indicator |
| --- | --- | --- |
| Brooks Range Alaska | 43.75 | 50.00 |
| Scandinavia | 50.00 | 29.88 |
| Ontario Canada | 37.50 | 33.02 |
| Western Australia | 0.00 | 6.96 |
| Queensland Australia | 0.00 | 0.03 |
| Baja California Mexico | 0.00 | 0.00 |

## 6. Weight sensitivity analysis

A deterministic one-at-a-time sensitivity test was performed for every
active component in each mission profile. Each component weight was
independently decreased by 20% and increased by 20% relative to its
baseline value. The remaining component weights were proportionally
renormalized so that the profile weights continued to sum to 1.0.

This produced 40 perturbation scenarios across seven mission profiles.
The baseline calculation was also reconstructed from the stored
component indices and original weights. All 42 baseline scores were reproduced within a numerical tolerance of 1e-8.

The test measures local ranking stability under the selected weight
changes. It is not a statistical confidence interval, probability
estimate, or validation of the weights as mission requirements.

### 6.1 Sensitivity summary

| Mission profile | Scenarios tested | Top-candidate changes | Mean absolute rank shift | Maximum absolute rank shift |
| --- | --- | --- | --- | --- |
| Cold-region operations analogue | 4.00 | 0.00 | 0.00 | 0.00 |
| Lunar polar operations | 8.00 | 0.00 | 0.25 | 2.00 |
| Lunar resource prospecting | 6.00 | 0.00 | 0.00 | 0.00 |
| Lunar rover mobility | 4.00 | 0.00 | 0.25 | 1.00 |
| Mars dust-process analogue | 6.00 | 0.00 | 0.11 | 1.00 |
| Mars rover mobility | 8.00 | 0.00 | 0.04 | 1.00 |
| Volcanic and cave analogue reconnaissance | 4.00 | 2.00 | 0.17 | 1.00 |

### 6.2 Baseline leaders

| Mission profile | Baseline top candidate | Baseline top score |
| --- | --- | --- |
| Lunar rover mobility | Ontario Canada | 86.68 |
| Lunar polar operations | Brooks Range Alaska | 70.19 |
| Mars rover mobility | Queensland Australia | 92.70 |
| Lunar resource prospecting | Brooks Range Alaska | 96.00 |
| Mars dust-process analogue | Ontario Canada | 100.00 |
| Volcanic and cave analogue reconnaissance | Baja California Mexico | 50.00 |
| Cold-region operations analogue | Brooks Range Alaska | 93.75 |

### 6.3 Interpretation

The volcanic and cave reconnaissance profile changed its top-ranked candidate in 2 of 4 perturbation scenarios. Its baseline result is therefore more sensitive to the selected component weights than the other profiles. The baseline tie between Baja California and Brooks Range should be interpreted cautiously.

The following profiles retained their baseline top-ranked candidate in every tested scenario: Cold-region operations analogue, Lunar polar operations, Lunar resource prospecting, Lunar rover mobility, Mars dust-process analogue, Mars rover mobility. This indicates local top-rank stability under the tested weight changes, not general validity under all possible assumptions.

## 7. Interpretation and scientific limitations


1. **Limited candidate sample:** The six Earth candidates are not a
   global ranking of all possible analogue sites.
2. **Relative normalization:** Component indices are normalized within
   this candidate set. Adding or removing candidates can change scores
   and rankings.
3. **Terrain reference limits:** Planetary terrain references are
   latitude-band averages, not exact local landing-site measurements.
4. **Resolution differences:** Earth and planetary terrain datasets
   differ in spatial resolution and aggregation.
5. **Roughness:** Roughness is excluded from direct planetary similarity
   scoring because measurement scales are incompatible.
6. **Elevation:** Elevation is excluded from direct similarity scoring
   because vertical datums differ.
7. **Water interpretation:** Earth surface-water occurrence does not
   establish the presence of lunar ice or Martian subsurface water.
8. **Solar interpretation:** Earth solar irradiance does not represent
   lunar polar illumination or a mission-specific power budget.
9. **Aerosol interpretation:** Aerosol optical depth is an atmospheric
   aerosol proxy, not a dust-only measurement or direct dust-event record.
10. **Cold-region interpretation:** Earth cold-month indicators are
    terrestrial climate analogues, not measurements of lunar or Martian
    surface temperatures.
11. **Geological evidence:** Volcanic and possible karst record rates
    describe mentions in available geological records. They do not
    confirm lava tubes, caves, mineral reserves, or resource abundance.
12. **Time coverage:** NASA POWER temperature and solar inputs represent
    2020; water occurrence represents its source observation period.
13. **Static terrain:** Static DEM-derived terrain metrics do not describe
    terrain change, seasonal movement, or dust migration over time.
14. **Model assumptions:** Profile weights are initial screening
    assumptions, not validated mission requirements.
15. **Physical non-equivalence:** Earth analogues cannot reproduce lunar
    gravity and vacuum or the full Martian atmospheric and radiation
    environment.
16. **Score meaning:** Scores are weighted screening indices, not
    probabilities, mission-success estimates, or physical similarity
    percentages.

## 8. Validation summary

- Terrain similarity: 12 records (six candidates × two planets).
- Environmental screening: six unique candidates.
- Integrated evidence: six candidates with six evidence families represented.
- Integrated mission profiles: seven.
- Integrated mission score records: 42.
- Candidate coverage: six candidates in every mission profile.
- Required screening scores: no missing values.
- Profile weights: each profile totals 1.0.
- Weighted component contributions: validated against final scores.
- Score range: 0–100.

## 9. Conclusion

The integrated results show that the leading Earth analogue depends on
the mission objective. Ontario leads the Mars dust-process analogue
profile and lunar rover mobility under the current model assumptions.
Queensland leads the Mars rover mobility profile. Brooks Range leads
lunar resource prospecting, lunar polar operations, and cold-region
operations. The volcanic and cave reconnaissance profile produces a
tie between Baja California and Brooks Range.

These rankings are screening results, not operational site selections.
They demonstrate the value of mission-specific evaluation while
highlighting the need for better spatially matched planetary data,
validated mission requirements, temporal analysis, and expert review.

---
**Member 4 deliverables:** terrain similarity scores, environmental
screening scores, integrated candidate evidence, seven-profile
integrated mission scores, methodology files, scoring code, and this
consolidated report.
