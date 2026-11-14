
from pathlib import Path
from datetime import date
import csv
from statistics import mean, median


BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "results" / "member3_final_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = BASE_DIR / "results" / "member3_global_analysis_v3"

REPORT_FILE = OUTPUT_DIR / "member3_analogy_assessment.md"


def load_earth_data():
    tile_file = DATA_DIR / "earth_reference_tile_records_v3.csv"
    audit_file = DATA_DIR / "earth_reference_audit_v3.csv"

    with tile_file.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    with audit_file.open("r", encoding="utf-8-sig", newline="") as file:
        audit = next(csv.DictReader(file))

    def values(column):
        return [
            float(row[column])
            for row in rows
            if row[column] not in ("", None)
        ]

    return {
        "audit": audit,
        "elevation": mean(values("elevation_mean_m")),
        "slope": mean(values("slope_mean_degrees")),
        "median_slope": median(values("slope_mean_degrees")),
        "slope_p90": mean(values("slope_p90_degrees")),
        "roughness_270": mean(values("roughness_270m_mean")),
        "roughness_630": mean(values("roughness_630m_mean")),
        "roughness_1350": mean(values("roughness_1350m_mean")),
    }


def main():

    earth = load_earth_data()
    audit = earth["audit"]

    earth_count = int(audit["advanced_summary_records"])
    unique_count = int(audit["unique_locations"])
    processing_count = int(audit["processing_log_records"])
    classification_count = int(audit["classification_summary_records"])
    extra_count = int(audit["summary_only_records"])

    moon_elevation = -0.2484
    moon_slope = 4.1790
    moon_roughness = 0.2371

    mars_elevation = -0.5507
    mars_slope = 1.2327
    mars_roughness = 0.0706

    report = f"""# TERRATIME4D
# MEMBER 3 - EARTH, MOON AND MARS TERRAIN ANALOGY ASSESSMENT

Date: {date.today()}

## 1. Objective

To compare available physical terrain measurements from Earth, the Moon
and Mars and assess where Earth environments can serve as useful
planetary analogues.

The assessment considers elevation, slope, surface roughness,
geological landforms and environmental processes.

## 2. Data used

### Earth

- Source: Member 2 processed global advanced terrain summary.
- Advanced terrain summary records: {earth_count}.
- Unique Earth locations: {unique_count}.
- Processing log records: {processing_count}.
- Classification summary records: {classification_count}.
- Additional summary-only records: {extra_count}.
- Coverage represents sampled terrain tiles, not complete global coverage.

Latest arithmetic averages of tile-level measurements:

- Mean tile elevation: {earth["elevation"] / 1000:.4f} km.
- Mean tile slope: {earth["slope"]:.4f} degrees.
- Median tile mean slope: {earth["median_slope"]:.4f} degrees.
- Mean tile 90th-percentile slope: {earth["slope_p90"]:.4f} degrees.
- Mean roughness at 270 m: {earth["roughness_270"]:.4f} m.
- Mean roughness at 630 m: {earth["roughness_630"]:.4f} m.
- Mean roughness at 1350 m: {earth["roughness_1350"]:.4f} m.

These Earth values are arithmetic averages of tile-level statistics.
They are not pooled pixel-level or area-weighted global measurements.

### Moon

- Dataset: Lunar Digital Elevation Model (LDEM 16).
- Source file: ldem_16.tif.
- Global elevation grid used for physical terrain analysis.
- Area-weighted mean elevation: {moon_elevation:.4f} km.
- Area-weighted mean slope: {moon_slope:.4f} degrees.
- Area-weighted mean roughness: {moon_roughness:.4f} km.
- Approximate roughness analysis scale: 11 km.

### Mars

- Dataset: Mars Orbiter Laser Altimeter (MOLA MEGDR).
- Source file: megt90n000eb.img.
- Global elevation grid used for physical terrain analysis.
- Area-weighted mean elevation: {mars_elevation:.4f} km.
- Area-weighted mean slope: {mars_slope:.4f} degrees.
- Area-weighted mean roughness: {mars_roughness:.4f} km.
- Approximate roughness analysis scale: 11 km.

## 3. Quantitative comparison

| Characteristic | Earth | Moon | Mars |
|---|---:|---:|---:|
| Mean elevation | {earth["elevation"] / 1000:.4f} km | {moon_elevation:.4f} km | {mars_elevation:.4f} km |
| Mean slope | {earth["slope"]:.4f} degrees | {moon_slope:.4f} degrees | {mars_slope:.4f} degrees |
| Roughness mean | {earth["roughness_270"]:.4f} m at 270 m | {moon_roughness * 1000:.1f} m at approx. 11 km | {mars_roughness * 1000:.1f} m at approx. 11 km |

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

7. Earth reference coverage consists of {unique_count} unique tile
   summaries, not a complete global dataset.

8. The advanced Earth summary contains {earth_count} records, while
   the processing and classification summaries each contain
   {processing_count} records. The {extra_count} additional records
   require separate provenance consideration.

9. MOLA MEGDR includes interpolated elevation values in bins without
   direct laser-altimeter observations.

10. The Moon source TIFF does not contain embedded georeferencing.
    Its global grid orientation is assumed for the analysis.

## 6. Interpretation of measured terrain characteristics

The Moon's area-weighted mean slope is approximately
{moon_slope:.4f} degrees, compared with {mars_slope:.4f} degrees
for Mars in the analysed global grids.

The Moon therefore has a higher mean slope in these results.
This does not mean every lunar region is steep or every Martian
region is flat.

Earth's mean tile slope is approximately {earth["slope"]:.4f} degrees.
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
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("MEMBER 3 - ANALOGY ASSESSMENT")
    print("=" * 45)
    print("Assessment report created successfully.")
    print(f"Saved at: {REPORT_FILE}")


if __name__ == "__main__":
    main()
