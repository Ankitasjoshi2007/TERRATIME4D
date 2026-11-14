# TERRATIME4D
# MEMBER 3 - EARTH, MOON AND MARS TERRAIN ANALOGY ASSESSMENT

Date: 2026-11-14

## 1. Objective

To compare available physical terrain measurements from Earth, the Moon
and Mars and assess where Earth environments can serve as useful
planetary analogues.

The assessment considers elevation, slope, surface roughness,
geological landforms and environmental processes.

## 2. Data used

### Earth

- Source: Member 2 processed global advanced terrain summary.
- Advanced terrain summary records: 648.
- Unique Earth locations: 648.
- Processing log records: 645.
- Classification summary records: 645.
- Additional summary-only records: 3.
- Coverage represents sampled terrain tiles, not complete global coverage.

Latest arithmetic averages of tile-level measurements:

- Mean tile elevation: 1.0997 km.
- Mean tile slope: 3.5687 degrees.
- Median tile mean slope: 1.6115 degrees.
- Mean tile 90th-percentile slope: 7.8453 degrees.
- Mean roughness at 270 m: 4.8402 m.
- Mean roughness at 630 m: 10.1794 m.
- Mean roughness at 1350 m: 17.2959 m.

These Earth values are arithmetic averages of tile-level statistics.
They are not pooled pixel-level or area-weighted global measurements.

### Moon

- Dataset: Lunar Digital Elevation Model (LDEM 16).
- Source file: ldem_16.tif.
- Global elevation grid used for physical terrain analysis.
- Area-weighted mean elevation: -0.2484 km.
- Area-weighted mean slope: 4.1790 degrees.
- Area-weighted mean roughness: 0.2371 km.
- Approximate roughness analysis scale: 11 km.

### Mars

- Dataset: Mars Orbiter Laser Altimeter (MOLA MEGDR).
- Source file: megt90n000eb.img.
- Global elevation grid used for physical terrain analysis.
- Area-weighted mean elevation: -0.5507 km.
- Area-weighted mean slope: 1.2327 degrees.
- Area-weighted mean roughness: 0.0706 km.
- Approximate roughness analysis scale: 11 km.

## 3. Quantitative comparison

| Characteristic | Earth | Moon | Mars |
|---|---:|---:|---:|
| Mean elevation | 1.0997 km | -0.2484 km | -0.5507 km |
| Mean slope | 3.5687 degrees | 4.1790 degrees | 1.2327 degrees |
| Roughness mean | 4.8402 m at 270 m | 237.1 m at approx. 11 km | 70.6 m at approx. 11 km |

Important limitations:

- Earth roughness measurements use 270 m, 630 m and 1350 m scales.

- Moon and Mars roughness measurements use an approximately 11 km
  target scale.

- Earth statistics are unweighted averages of tile-level values.

- Moon and Mars statistics are area-weighted global grid measurements.

- These differences prevent a perfectly matched numerical comparison.

## 4. Where Earth terrain analogies work

### 4.1 Impact craters

Earth impact craters provide examples of crater rims, central uplifts,
impact deformation and crater geometry.

The Moon preserves many impact structures because it lacks the active
weathering and erosion processes that strongly modify Earth's surface.

Mars also contains impact craters modified by volcanic, wind-related
and possible water-related processes.

Assessment:

Earth impact structures are useful morphological analogues for
studying crater geometry and impact-related landforms. However,
preservation conditions and geological histories differ.

### 4.2 Volcanic landforms

Earth volcanic regions provide examples of lava flows, basaltic plains,
volcanic cones and related structures.

The Moon contains extensive ancient basaltic plains called lunar maria.
Mars contains large volcanic structures and broad volcanic provinces.

Assessment:

Earth volcanic terrain is useful for understanding lava-flow patterns
and volcanic landform geometry. Differences in gravity, eruption
history and environmental conditions limit the analogy.

### 4.3 Valleys and channels

Earth river valleys, channels and canyons demonstrate how flowing
water modifies terrain and creates branching networks.

Mars contains valley networks and channel-like landforms that provide
evidence of past surface-water activity.

Assessment:

Earth valleys are useful morphological comparisons for studying
Martian channel shapes. The origin of individual Martian features
must be investigated separately.

This analogy is much more limited for the Moon, which does not have
Earth-like active river erosion.

### 4.4 Dunes and wind-shaped terrain

Earth deserts provide examples of dunes, ripples and wind-shaped
sediment deposits.

Mars has widespread aeolian landforms produced by atmospheric winds.

Assessment:

Earth deserts are useful morphological and process analogues for
Martian dune patterns and sediment movement. They are not direct
process analogues for the Moon because it lacks a substantial
atmosphere capable of supporting wind-driven dunes.

### 4.5 Polar and ice-related terrain

Earth polar regions, glaciers and permafrost landscapes provide
examples of ice-related surface processes.

Some Martian regions contain surface and subsurface ice.

Assessment:

Earth cold-region environments can help investigate selected
Martian ice-related landforms. Differences in temperature,
atmospheric pressure and gravity remain important.

Modelled lunar polar ice-stability information can also help guide
scientific investigation. Modelled stability does not independently
confirm accessible ice deposits.

## 5. Where Earth analogies fail or become limited

1. Gravity differs between Earth, the Moon and Mars. This affects
   slope stability and the movement of surface materials.

2. The Moon has almost no atmosphere and lacks Earth-like rainfall,
   wind erosion and active river systems.

3. Mars has a thin carbon-dioxide atmosphere and a geological history
   involving volcanic, wind-related and possible water-related processes.

4. Earth has active plate tectonics, oceans and a strong hydrological
   cycle. These processes do not operate in the same way on the Moon
   and Mars.

5. Similar-looking landforms do not necessarily have the same origin.
   Shape alone cannot establish identical geological processes.

6. Earth roughness and planetary roughness were measured at different
   spatial scales.

7. Earth reference coverage consists of 648 unique tile
   summaries, not a complete global dataset.

8. The advanced Earth summary contains 648 records, while
   the processing and classification summaries each contain
   645 records. The 3 additional records
   require separate provenance consideration.

9. MOLA MEGDR includes interpolated elevation values in bins without
   direct laser-altimeter observations.

10. The Moon source TIFF does not contain embedded georeferencing.
    Its global grid orientation is assumed for the analysis.

## 6. Interpretation of measured terrain characteristics

The Moon's area-weighted mean slope is approximately
4.1790 degrees, compared with 1.2327 degrees
for Mars in the analysed global grids.

The Moon therefore has a higher mean slope in these results.
This does not mean every lunar region is steep or every Martian
region is flat.

Earth's mean tile slope is approximately 3.5687 degrees.
It falls between the Moon and Mars values, but the sampling and
weighting methods differ.

The roughness measurements describe terrain variability at their
respective analysis scales. They must not be interpreted as a
directly equivalent comparison because the spatial scales differ.

## 7. Relevance to planetary exploration

Earth analogues can support planetary exploration by helping researchers:

- Understand crater shape and geometry.
- Study volcanic and lava-flow terrain.
- Interpret valleys, channels and canyon-like features.
- Understand wind-shaped dunes on Mars.
- Investigate selected ice-related landforms.
- Examine slopes and rough surfaces relevant to rover mobility.

Analogue selection should depend on the specific landform or physical
process being investigated. Visual similarity alone is insufficient.

## 8. Relevance to the TERRATIME4D project

This assessment provides Member 4 and Member 5 with scientific context
for interpreting the planetary terrain reference data.

Member 3 supplies planetary reference measurements, comparison
outputs and scientific limitations.

Final Earth-site suitability ranking and mission-specific scoring
belong to Member 4's Similarity and Mission Scoring Engine.

Global visualization and application integration belong to Member 5.

## 9. Conclusion

Earth provides useful analogues for selected lunar and Martian
landforms, especially impact craters, volcanic structures, valleys
and wind-shaped terrain.

However, gravity, atmosphere, temperature, geological history and
surface processes differ between the planetary bodies.

The measured terrain statistics and elevation maps provide a
quantitative and visual basis for exploratory comparison. They do
not establish identical geological origins or complete environmental
equivalence.

## 10. Generated project outputs

- Moon global elevation map:
  results/member3_elevation_maps/01_moon_global_elevation.png
- Mars global elevation map:
  results/member3_elevation_maps/02_mars_global_elevation.png
- Planetary comparison graphs and CSV:
  results/member3_global_comparison_v3/
- Moon and Mars physical analysis:
  results/member3_global_analysis_v3/

## 11. Additional scientific limitations

- Earth elevation coverage is partial.
- Earth and planetary statistics use different sampling and weighting.
- Earth and planetary roughness use different spatial scales.
- The Moon elevation TIFF has no embedded georeferencing.
- MOLA elevation grids include interpolated values.
- Terrain resemblance does not prove geological equivalence.
- This assessment does not replace detailed geological, mineralogical
  or environmental investigation.
