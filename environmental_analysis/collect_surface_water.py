import requests
import rasterio
import numpy as np
import pandas as pd
from pathlib import Path
import math

locations = [
    ("Western Australia", -32.5, 117.5),
    ("Queensland Australia", -22.5, 147.5),
    ("Baja California Mexico", 27.5, -112.5),
    ("Ontario Canada", 47.5, -82.5),
    ("Brooks Range Alaska", 67.5, -147.5),
    ("Scandinavia", 67.5, 17.5),
]

def tile_name(lat, lon):
    west = math.floor(lon / 10) * 10
    north = math.floor(lat / 10) * 10 + 10

    ew = "E" if west >= 0 else "W"
    ns = "N" if north >= 0 else "S"

    return f"{abs(west)}{ew}_{abs(north)}{ns}"

folder = Path("data/raw/global_surface_water")
folder.mkdir(parents=True, exist_ok=True)
rows = []

for name, lat, lon in locations:
    tile = tile_name(lat, lon)
    filename = f"occurrence_{tile}_v1_5_2024.tif"
    path = folder / filename

    if not path.exists():
        url = (
            "https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/"
            "download2024/Aggregated/VER1-5/occurrence/" + filename
        )
        print("Downloading:", name, tile, flush=True)
        r = requests.get(url, timeout=180)
        r.raise_for_status()
        path.write_bytes(r.content)

    print("Analysing:", name, tile, flush=True)

    with rasterio.open(path) as src:
        if not (src.bounds.left <= lon <= src.bounds.right and
                src.bounds.bottom <= lat <= src.bounds.top):
            raise ValueError(f"Tile does not contain candidate: {name}")

        window = rasterio.windows.from_bounds(
            lon - 0.05, lat - 0.05,
            lon + 0.05, lat + 0.05,
            src.transform
        ).round_offsets().round_lengths()

        data = src.read(1, window=window, masked=True)
        values = data.compressed().astype(float)
        values = values[(values >= 0) & (values <= 100)]

        if len(values) == 0:
            raise ValueError(f"No valid observations: {name}")

        rows.append({
            "location": name,
            "latitude": lat,
            "longitude": lon,
            "tile": tile,
            "valid_pixels": len(values),
            "mean_water_occurrence_percent": values.mean(),
            "median_water_occurrence_percent": np.median(values),
            "pixels_with_detected_water_percent": (values > 0).mean() * 100,
            "persistent_water_pixels_percent": (values >= 90).mean() * 100,
            "source_period": "1984-2024"
        })

out = Path("data/processed/environmental")
out.mkdir(parents=True, exist_ok=True)

df = pd.DataFrame(rows)
target = out / "jrc_surface_water_occurrence_2024.csv"
df.to_csv(target, index=False)

print("\nSURFACE WATER ANALYSIS COMPLETE")
print("Locations:", len(df))
print("Missing values:", df.isna().sum().sum())
print(df.to_string(index=False))
print("Saved:", target)
