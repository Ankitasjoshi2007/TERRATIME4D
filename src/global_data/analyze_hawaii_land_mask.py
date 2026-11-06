
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling


dem_path = Path(
    "data/copernicus_glo90/"
    "Copernicus_DSM_COG_30_N19_00_W155_00_DEM.tif"
)

worldcover_path = Path(
    "data/raw/earth/land_cover/ESA_WorldCover_Hawaii.tif"
)

output_path = Path("data/processed/hawaii_land_mask_report.txt")

print("Reading Hawaii DEM and WorldCover data...")

with rasterio.open(dem_path) as dem:
    elevation = dem.read(1).astype(np.float32)
    dem_profile = dem.profile.copy()
    dem_transform = dem.transform
    dem_crs = dem.crs
    dem_nodata = dem.nodata

with rasterio.open(worldcover_path) as wc:
    land_cover = np.zeros(
        (dem_profile["height"], dem_profile["width"]),
        dtype=np.uint8
    )

    reproject(
        source=rasterio.band(wc, 1),
        destination=land_cover,
        src_transform=wc.transform,
        src_crs=wc.crs,
        dst_transform=dem_transform,
        dst_crs=dem_crs,
        resampling=Resampling.nearest,
        src_nodata=0,
        dst_nodata=0,
    )

print("Matching land-cover classes to DEM pixels...")

valid_dem = np.isfinite(elevation)

if dem_nodata is not None:
    valid_dem &= elevation != dem_nodata

valid_cover = land_cover != 0
valid = valid_dem & valid_cover

water = valid & (land_cover == 80)
land = valid & (land_cover != 80)

land_elevation = elevation[land]

lines = [
    "HAWAII DEM LAND MASK REPORT",
    "===========================",
    f"Total DEM pixels: {elevation.size}",
    f"Valid DEM pixels: {int(valid_dem.sum())}",
    f"Pixels with classified WorldCover: {int(valid.sum())}",
    f"Permanent water pixels (class 80): {int(water.sum())}",
    f"Land-classified pixels: {int(land.sum())}",
    f"Unclassified or NoData pixels: {int((~valid).sum())}",
    "",
    "CLASS-BY-CLASS ELEVATION CHECK",
    "==============================",
]

for class_id in sorted(np.unique(land_cover[valid])):
    selected = valid & (land_cover == class_id)
    values = elevation[selected]

    lines.extend([
        f"Class {int(class_id)}:",
        f"  Pixels: {values.size}",
        f"  Minimum elevation: {values.min():.2f} m",
        f"  Maximum elevation: {values.max():.2f} m",
        f"  Mean elevation: {values.mean():.2f} m",
    ])

if land_elevation.size:
    lines.extend([
        "",
        "LAND-ONLY ELEVATION STATISTICS",
        "==============================",
        f"Minimum: {land_elevation.min():.2f} m",
        f"Maximum: {land_elevation.max():.2f} m",
        f"Mean: {land_elevation.mean():.2f} m",
        f"Standard deviation: {land_elevation.std():.2f} m",
    ])

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print(f"\nReport saved to: {output_path}")
