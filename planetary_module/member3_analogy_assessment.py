
from pathlib import Path
from datetime import date


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "results" / "member3_final_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_FILE = OUTPUT_DIR / "member3_analogy_assessment.md"


def main():

    report = f"""# TERRATIME4D
# MEMBER 3 - EARTH, MOON AND MARS TERRAIN ANALOGY ASSESSMENT

Date: {date.today()}

## 1. Objective

To identify similarities and differences between Earth's terrain and the
terrain of the Moon and Mars. The assessment considers elevation, slope,
surface roughness, geological landforms and the environmental processes
that shape planetary surfaces.

## 2. Data used

### Earth
- Existing processed reference statistics from 645 terrain tiles.
- Mean tile elevation: approximately 1.102 km.
- Mean tile slope: 3.5644 degrees.
- Median tile mean slope: 1.6260 degrees.
- Mean tile 90th-percentile slope: 7.8341 degrees.
- Earth data represents processed tiles, not complete global coverage.

### Moon
- Dataset: LDEM 16.
- Source file: ldem_16.tif.
- Global elevation grid used for the elevation map.
- Elevation values are in kilometres.
- Mean area-weighted elevation: -0.2484 km.
- Mean area-weighted slope: 4.1790 degrees.
- Mean area-weighted roughness: 0.2371 km.
- Approximate roughness analysis scale: 11 km.

### Mars
- Dataset: MOLA MEGDR.
- Source file: megt90n000eb.img.
- Global elevation grid used for the elevation map.
- Source elevation values converted from metres to kilometres.
- Mean area-weighted elevation: -0.5507 km.
- Mean area-weighted slope: 1.2327 degrees.
- Mean area-weighted roughness: 0.0706 km.
- Approximate roughness analysis scale: 11 km.

## 3. Quantitative comparison

| Characteristic | Earth | Moon | Mars |
|---|---:|---:|---:|
| Mean elevation | 1.102 km | -0.248 km | -0.551 km |
| Mean slope | 3.564 degrees | 4.179 degrees | 1.233 degrees |
| Roughness mean | 4.836 m at 270 m scale | 237.1 m at approx. 11 km scale | 70.6 m at approx. 11 km scale |

Important: Earth roughness values and Moon/Mars roughness values were
calculated at different spatial scales. They must not be treated as a
direct numerical comparison.

Earth statistics are based on 645 processed tiles, while Moon and Mars
statistics are based on global elevation grids. Therefore, the mean
elevation and slope values are useful descriptive results, not a
perfectly matched global comparison.

## 4. Where Earth terrain analogies work

### 4.1 Impact craters

Earth has impact craters that help researchers understand crater shape,
rim structure, central uplift and impact-related surface deformation.

The Moon has many preserved impact craters because it lacks the active
weathering and erosion processes that strongly modify Earth's surface.

Mars also contains impact craters, although its atmosphere, volcanic
history, wind and past water activity have modified many crater features.

Assessment:
Earth impact craters are useful morphological analogues for studying
crater geometry and impact structures. However, crater preservation
conditions differ between the three bodies.

### 4.2 Volcanic landforms

Earth volcanic regions provide examples of lava flows, volcanic cones,
basaltic plains and volcanic surface structures.

The Moon contains extensive ancient basaltic plains known as lunar maria.
Mars contains large volcanic structures and broad volcanic provinces.

Assessment:
Earth volcanic terrain is useful for understanding lava-flow patterns
and volcanic landform geometry. The scale, gravity, eruption history
and environmental conditions are different, so the analogy is not exact.

### 4.3 Valleys, channels and erosional landforms

Earth river valleys, channels and canyons help explain how flowing
water can produce branching networks and modify terrain.

Mars contains valley networks and channel-like landforms that provide
evidence of past surface-water activity.

Assessment:
Earth valleys are useful morphological comparisons for investigating
Martian channel shapes and drainage-like patterns. However, the
formation history of each Martian feature must be evaluated separately.

The Moon does not have Earth-like active river erosion, so this analogy
is much more limited for lunar terrain.

### 4.4 Dunes and wind-shaped terrain

Earth deserts provide examples of dunes, ripples and wind-shaped
sediment deposits.

Mars has widespread aeolian landforms produced by wind, making Earth
deserts useful for understanding dune shapes and sediment movement.

Assessment:
Earth deserts are strong morphological analogues for Martian aeolian
terrain. They are not direct process analogues for the Moon because
the Moon has no substantial atmosphere to support wind-driven dunes.

### 4.5 Polar and ice-related terrain

Earth polar regions, glaciers and permafrost landscapes provide
examples of ice-related surface processes.

Some Martian regions contain surface and subsurface ice, making
selected Earth cold-region environments useful comparative settings.

Assessment:
Earth polar environments can help investigate ice-related landforms
on Mars. Differences in atmospheric pressure, temperature and gravity
must still be considered.

## 5. Where Earth analogies fail or become limited

1. Gravity differs between Earth, the Moon and Mars. This changes
   slope stability, material movement and the behaviour of surface
   particles.

2. The Moon has almost no atmosphere and no Earth-like wind, rainfall
   or river erosion.

3. Mars has a thin atmosphere and a geological history that includes
   volcanic, wind-related and possible water-related surface processes.

4. Earth has active plate tectonics, oceans and a strong hydrological
   cycle. These processes do not operate in the same way on the Moon
   and Mars.

5. Similar-looking landforms do not necessarily have the same origin.
   Shape alone cannot prove that two features formed through identical
   geological processes.

6. Earth roughness was measured at 270 m, 630 m and 1350 m scales,
   whereas the Moon and Mars roughness comparison used an approximate
   11 km target scale.

7. Earth coverage is limited to 645 processed tiles. It must not be
   described as a complete global Earth dataset.

## 6. Interpretation of measured terrain characteristics

The Moon's area-weighted mean slope is approximately 4.179 degrees,
compared with 1.233 degrees for Mars in the analysed global grids.

The Moon therefore has a higher mean slope in these results.
Mars has a lower mean slope, although this does not mean every Martian
region is flat. Large volcanoes, crater rims and canyon systems can
contain steep local terrain.

Earth's mean tile slope is approximately 3.564 degrees. This value
falls between the Moon and Mars means, but the comparison is limited
because the Earth value is an unweighted average of processed tile
statistics, whereas Moon and Mars values are area-weighted global
statistics.

The roughness values show that the Moon and Mars have different
surface variability at the selected analysis scale. These values
should not be compared directly with Earth roughness because the
spatial scales are different.

## 7. Relevance to planetary exploration

Earth analogues can support planetary exploration in several ways:

- Understanding the shape and geometry of craters.
- Studying volcanic and lava-flow terrain.
- Interpreting valleys, channels and canyon-like features.
- Understanding wind-shaped dunes on Mars.
- Studying selected ice-related landforms.
- Identifying slopes and rough surfaces that may create rover
  navigation challenges.

However, an Earth analogue should be selected according to the
specific landform or physical process being studied. A visual
similarity alone is not sufficient.

## 8. Conclusion

Earth provides useful terrain analogues for selected lunar and Martian
landforms, especially impact craters, volcanic structures and certain
erosional features. Earth deserts are particularly useful for
understanding wind-shaped Martian terrain, while cold-region
environments can help interpret some Martian ice-related features.

These analogies have limitations because gravity, atmosphere,
temperature, geological history and surface processes differ between
the planetary bodies.

The measured terrain statistics and elevation maps provide a
quantitative and visual basis for comparison. The results are
exploratory and do not establish identical geological origins.

## 9. Generated project outputs

- Moon global elevation map:
  results/member3_elevation_maps/01_moon_global_elevation.png
- Mars global elevation map:
  results/member3_elevation_maps/02_mars_global_elevation.png
- Existing planetary comparison graphs:
  results/member3_global_comparison_v3/
- Moon and Mars physical analysis:
  results/member3_global_analysis_v3/

## 10. Limitations

- Earth elevation coverage is partial.
- Earth and planetary terrain statistics use different sampling
  and weighting approaches.
- Earth and planetary roughness values use different spatial scales.
- The Moon map uses an assumed global cylindrical grid orientation
  because its source TIFF has no embedded georeferencing.
- The analysis does not establish geological equivalence between
  visually similar landforms.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("MEMBER 3 - ANALOGY ASSESSMENT")
    print("=" * 45)
    print("Assessment report created successfully.")
    print(f"Saved at: {REPORT_FILE}")


if __name__ == "__main__":
    main()
