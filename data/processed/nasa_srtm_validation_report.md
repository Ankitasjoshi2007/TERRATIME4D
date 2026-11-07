
# NASA SRTM Elevation Data Validation Report

## 1. Data Source

- Provider: NASA
- Dataset: SRTMGL1 Version 003
- Product: SRTM 1 Arc-Second Global
- Resolution: 1 arc-second (approximately 30 metres)
- Data format: HGT
- Coordinate Reference System: EPSG:4326

## 2. Validated Tiles

### Tile 1: N12E077

- Dimensions: 3601 x 3601
- Data type: int16
- NoData value: -32768
- Valid pixels: 12,967,201
- Invalid pixels: 0
- Minimum elevation: 233 m
- Maximum elevation: 1505 m
- Mean elevation: 724.04 m
- Standard deviation: 158.21 m
- Validation result: PASSED

### Tile 2: N13E077

- Dimensions: 3601 x 3601
- Data type: int16
- NoData value: -32768
- Valid pixels: 12,967,201
- Invalid pixels: 0
- Minimum elevation: 579 m
- Maximum elevation: 1474 m
- Mean elevation: 805.57 m
- Standard deviation: 102.25 m
- Validation result: PASSED

## 3. Quality Checks

| Quality check | N12E077 | N13E077 |
|---|---|---|
| Expected dimensions | Passed | Passed |
| CRS available | Passed | Passed |
| Positive resolution | Passed | Passed |
| Valid elevation pixels | Passed | Passed |

## 4. Overall Result

BOTH TILES PASSED.

Both downloaded NASA SRTM HGT files were readable using Rasterio and passed the implemented technical validation checks.

## 5. Validation Script

`src/global_data/validate_srtm_hgt.py`

## 6. Important Note

This report records the checks implemented in the validation script. It does not establish independent confirmation of vertical accuracy, absolute geolocation accuracy, or complete scientific suitability.
