# TERRATIME4D
# MEMBER 3 – MOON AND MARS COMPARISON

## 1. Objective

To study Moon and Mars terrain using planetary elevation datasets,
identify comparable terrain characteristics, compare them with
available Earth terrain statistics, and document where Earth
terrain analogies work and where they have limitations.

## 2. Dataset Research

### Earth
Existing processed reference statistics from 645 terrain tiles.
The available data is partial and does not represent complete
global Earth coverage.

### Moon
Dataset: Lunar Digital Elevation Model (LOLA).
Source file: ldem_16.tif.
Resolution: 16 pixels per degree.
Elevation unit: kilometres.
Source: NASA Lunar Reconnaissance Orbiter / LOLA data.

### Mars
Dataset: Mars Orbiter Laser Altimeter (MOLA) MEGDR.
Source file: megt90n000eb.img.
Grid: 2880 x 5760.
Resolution: 16 pixels per degree.
Elevation values converted from metres to kilometres.
Source: NASA Planetary Data System.

## 3. Terrain Characteristics

The analysis considers:
- Elevation
- Slope
- Surface roughness
- Latitude-based terrain variation

Moon and Mars were analysed using global elevation grids.
Slope and approximate 11 km roughness were calculated.

## 4. Quantitative Results

| Characteristic | Earth | Moon | Mars |
|---|---:|---:|---:|
| Mean elevation | 1.102 km | -0.248 km | -0.551 km |
| Mean slope | 3.564° | 4.179° | 1.233° |
| Mean roughness | 4.836 m at 270 m scale | 0.237 km at approx. 11 km scale | 0.071 km at approx. 11 km scale |

Earth values are based on 645 processed tiles. Its mean elevation
and slope are unweighted averages of tile statistics. Moon and Mars
values are area-weighted global statistics.

Earth roughness and planetary roughness were measured at different
spatial scales. Therefore, their numerical values are not directly
comparable.

## 5. Earth Terrain Analogies

### Impact craters
Earth impact craters help explain crater geometry, rims and
impact-related structures. The Moon and Mars also contain impact
craters, but preservation conditions differ.

### Volcanic terrain
Earth volcanic regions help explain lava flows and volcanic landforms.
The Moon has basaltic maria, while Mars contains large volcanic
structures. Differences in gravity and geological history limit
direct comparisons.

### Valleys and channels
Earth river valleys help explain branching channels and erosion.
Some Martian valley networks resemble these landforms, but their
formation history must be assessed independently. This analogy is
limited for the Moon.

### Dunes
Earth deserts are useful analogues for wind-shaped Martian dunes.
The Moon does not have a substantial atmosphere to support
Earth-like wind-driven dunes.

### Polar and ice terrain
Earth glaciers and permafrost environments help interpret selected
Martian ice-related landforms. Environmental conditions differ.

## 6. Where Analogies Fail

- Gravity differs between Earth, Moon and Mars.
- The Moon lacks substantial atmosphere and Earth-like weathering.
- Mars has a thin atmosphere and a different geological history.
- Earth has active plate tectonics and a hydrological cycle.
- Similar shapes do not prove identical geological origins.
- Earth data coverage is limited to 645 processed tiles.
- Roughness analysis uses different spatial scales.

## 7. Generated Results

### Elevation maps
- 01_moon_global_elevation.png
- 02_mars_global_elevation.png

### Planetary comparison graphs
- 01_mean_slope_comparison.png
- 02_earth_roughness_scales.png
- 03_moon_mars_roughness_comparison.png
- 04_mean_elevation_comparison.png
- 05_latitude_slope_comparison.png
- 06_latitude_roughness_comparison.png
- 07_planetary_comparison_dashboard.png

### Analysis files
- moon_mars_physical_summary_v3.csv
- moon_mars_latitude_band_analysis_v3.csv
- planetary_comparison_values_v3.csv
- member3_analogy_assessment.md

## 8. Interpretation

The Moon has a higher area-weighted mean slope than Mars in
the analysed grids. Mars has a lower mean slope, although local
volcanic, crater and canyon regions can still be steep.

Earth's mean tile slope lies between the Moon and Mars values.
However, this is not a fully matched global comparison because
the coverage and statistical weighting differ.

The roughness results describe surface variability at the
selected analysis scales and should not be interpreted as
a direct comparison across all three bodies.

## 9. Conclusion

Earth provides useful analogues for selected lunar and Martian
landforms, including impact craters, volcanic terrain, valleys,
dunes and ice-related features.

These analogies help interpret planetary surface morphology
and support exploration planning. However, differences in
gravity, atmosphere, geological history and surface processes
limit direct equivalence.

The elevation maps, terrain statistics and comparison graphs
provide a quantitative and visual basis for this study.
The results are exploratory and do not prove identical
geological origins.

## 10. Limitations

1. Earth coverage includes only 645 processed terrain tiles.
2. Earth and planetary statistics use different coverage and weighting.
3. Earth roughness scales differ from the approximately 11 km
   Moon and Mars analysis scale.
4. The Moon TIFF has no embedded georeferencing; the map uses
   an assumed global cylindrical grid orientation.
5. Latitude-band orientation is assumed north-to-south.
6. The analysis does not establish geological equivalence.

## 11. References

1. NASA CGI Moon Kit – Lunar elevation data:
   https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS

2. NASA Planetary Data System – MOLA:
   https://pds-geosciences.wustl.edu/missions/mgs/

3. NASA Lunar Reconnaissance Orbiter:
   https://science.nasa.gov/mission/lunar-reconnaissance-orbiter/

4. NASA Mars Global Surveyor:
   https://science.nasa.gov/mission/mars-global-surveyor/

