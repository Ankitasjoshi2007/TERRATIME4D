
from pathlib import Path
import json

import numpy as np
import rasterio
from rasterio.transform import from_origin

from terrain import analyze_terrain


test_file = Path(__file__).parent / "sample_elevation.tif"
output_file = Path(__file__).parent / "terrain_metrics.json"

elevation = np.array(
    [
        [100, 101, 102, 103, 104],
        [101, 103, 105, 107, 109],
        [102, 105, 110, 115, 120],
        [103, 107, 115, 125, 135],
        [104, 109, 120, 135, 150],
    ],
    dtype=np.float32,
)

transform = from_origin(77.5, 13.0, 0.00027, 0.00027)

with rasterio.open(
    test_file,
    "w",
    driver="GTiff",
    height=elevation.shape[0],
    width=elevation.shape[1],
    count=1,
    dtype="float32",
    crs="EPSG:4326",
    transform=transform,
    nodata=-9999,
) as dataset:
    dataset.write(elevation, 1)

results = analyze_terrain(test_file)

with output_file.open("w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nTerraTime 4D | Sample Terrain Test")
print("----------------------------------")

for name, value in results.items():
    print(f"{name}: {value}")

print(f"\nMetrics saved to: {output_file}")
print("TEST PASSED: terrain analysis ran successfully!")
