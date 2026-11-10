import csv
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import uniform_filter

BASE = Path("data/processed/temporal_analysis")
PATCH_DIR = BASE / "namib_patches"

SCENES = [
    ("2019", "S2B_33KWP_20190714_0_L2A"),
    ("2020", "S2A_33KWP_20200713_1_L2A"),
    ("2021", "S2A_33KWP_20210718_1_L2A"),
    ("2022", "S2B_33KWP_20220715_0_L2A"),
    ("2023", "S2A_33KWP_20230715_0_L2A"),
    ("2024", "S2B_33KWP_20240714_0_L2A"),
    ("2025", "S2C_33KWP_20250714_0_L2A"),
    ("2026", "S2A_33KWP_20260714_1_L2A"),
]

years = []
ndvi_layers = []
texture_layers = []
valid_layers = []
rows = []
reference = None

print("TERRATIME4D - NAMIB TEMPORAL STACK")
print("=" * 55)

for year, scene_id in SCENES:
    spectral_path = PATCH_DIR / f"{scene_id}_red_nir.tif"
    scl_path = PATCH_DIR / f"{scene_id}_scl.tif"

    if not spectral_path.exists() or not scl_path.exists():
        raise FileNotFoundError(f"Missing patch for {scene_id}")

    with rasterio.open(spectral_path) as src, \
         rasterio.open(scl_path) as scl_src:

        if src.count < 2:
            raise ValueError(f"Expected Red and NIR bands: {scene_id}")

        if (src.width, src.height, src.crs, src.transform) != (
            scl_src.width, scl_src.height,
            scl_src.crs, scl_src.transform
        ):
            raise ValueError(f"Spectral/SCL grid mismatch: {scene_id}")

        grid = (src.width, src.height, src.crs, src.transform)

        if reference is None:
            reference = grid
        elif grid != reference:
            raise ValueError(f"Temporal grid mismatch: {scene_id}")

        red = src.read(1).astype("float32")
        nir = src.read(2).astype("float32")
        scl = scl_src.read(1)

        # Focus on bare, non-vegetated land pixels.
        valid = (scl == 5) & (red > 0) & (nir > 0)

        denominator = red + nir
        valid &= denominator > 0

        ndvi = np.full(red.shape, np.nan, dtype="float32")
        ndvi[valid] = (
            (nir[valid] - red[valid]) / denominator[valid]
        )

        # 9 x 9 pixel local NIR texture (approximately 90 m).
        # Mask-aware calculation avoids treating invalid pixels as data.
        weights = valid.astype("float32")
        safe_nir = np.where(valid, nir, 0)

        count = uniform_filter(weights, size=9, mode="constant")
        mean = uniform_filter(safe_nir, size=9, mode="constant")
        mean_sq = uniform_filter(
            safe_nir * safe_nir, size=9, mode="constant"
        )

        local_mean = np.divide(
            mean, count,
            out=np.zeros_like(mean),
            where=count > 0
        )
        local_mean_sq = np.divide(
            mean_sq, count,
            out=np.zeros_like(mean_sq),
            where=count > 0
        )

        texture = np.sqrt(
            np.maximum(local_mean_sq - local_mean**2, 0)
        ).astype("float32")

        # Require sufficient valid coverage in each texture window.
        texture[count < 0.75] = np.nan

        valid_percent = float(valid.mean() * 100)

        if not np.any(valid):
            raise ValueError(f"No valid bare-ground pixels: {scene_id}")

        ndvi_values = ndvi[valid]
        texture_values = texture[np.isfinite(texture)]

        rows.append({
            "year": year,
            "scene_id": scene_id,
            "valid_pixels": int(valid.sum()),
            "valid_percent": round(valid_percent, 3),
            "ndvi_p05": float(np.nanpercentile(ndvi_values, 5)),
            "ndvi_median": float(np.nanmedian(ndvi_values)),
            "ndvi_p95": float(np.nanpercentile(ndvi_values, 95)),
            "nir_texture_median": (
                float(np.nanmedian(texture_values))
                if texture_values.size else None
            ),
        })

        years.append(year)
        ndvi_layers.append(ndvi)
        texture_layers.append(texture)
        valid_layers.append(valid)

        print(
            f"{year}: valid={valid_percent:.2f}% | "
            f"NDVI median={np.nanmedian(ndvi_values):.4f} | "
            f"texture pixels={texture_values.size}"
        )

ndvi_stack = np.stack(ndvi_layers)
texture_stack = np.stack(texture_layers)
valid_stack = np.stack(valid_layers)

stack_path = BASE / "namib_temporal_stack.npz"

np.savez_compressed(
    stack_path,
    years=np.array(years),
    ndvi=ndvi_stack,
    nir_texture=texture_stack,
    valid_mask=valid_stack
)

csv_path = BASE / "namib_temporal_qc.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 55)
print("TEMPORAL STACK COMPLETE")
print("Scenes:", len(years))
print("Stack shape:", ndvi_stack.shape)
print("Stack:", stack_path)
print("QC report:", csv_path)
print("Grid validation: PASS")
