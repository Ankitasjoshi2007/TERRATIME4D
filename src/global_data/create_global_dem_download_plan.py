
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

GRID_FILE = ROOT / "data/processed/earth_grid.csv"
LAND_FILE = ROOT / "data/processed/land_classification/global_land_classification.csv"
INVENTORY_FILE = ROOT / "data/processed/copernicus_official_dem_inventory.csv"
DEM_DIR = ROOT / "data/copernicus_glo90"

OUTPUT_DIR = ROOT / "data/processed/global_dem_plan"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

grid = pd.read_csv(GRID_FILE)
land = pd.read_csv(LAND_FILE)
inventory = pd.read_csv(INVENTORY_FILE)

# Select global land grid centres
land_grid = grid.merge(
    land[["cell_id", "land_class"]],
    on="cell_id",
    how="inner"
)
land_grid = land_grid[land_grid["land_class"] == "land"].copy()

# Match each 5-degree land centre to its 1-degree DEM tile
land_grid["tile_latitude"] = land_grid["latitude"].apply(lambda x: int(x // 1))
land_grid["tile_longitude"] = land_grid["longitude"].apply(lambda x: int(x // 1))

matched = land_grid.merge(
    inventory[
        ["tile_latitude", "tile_longitude", "tile_name", "availability"]
    ],
    on=["tile_latitude", "tile_longitude"],
    how="left"
)

if matched["tile_name"].isna().any():
    raise ValueError("Some land centres have no matching official DEM tile.")

# Identify existing local downloads
existing_tiles = {
    path.stem for path in DEM_DIR.rglob("*.tif")
}

matched["local_status"] = matched["tile_name"].apply(
    lambda name: "Already downloaded"
    if name in existing_tiles
    else "Not downloaded"
)

matched["region"] = matched["latitude"].apply(
    lambda lat: "Antarctica" if lat <= -60 else
    "Arctic" if lat >= 60 else
    "Other regions"
)

# Save centre-to-tile mapping
matched.to_csv(
    OUTPUT_DIR / "global_land_centre_dem_mapping.csv",
    index=False
)

# Create unique tile download plan
plan = matched.drop_duplicates(subset=["tile_name"]).copy()

plan["download_priority"] = plan.apply(
    lambda row: (
        "Complete" if row["local_status"] == "Already downloaded"
        else "Priority 1 - Non-Antarctic"
        if row["region"] == "Other regions"
        else "Priority 2 - Arctic"
        if row["region"] == "Arctic"
        else "Priority 3 - Antarctica"
    ),
    axis=1
)

plan.to_csv(
    OUTPUT_DIR / "global_dem_download_plan.csv",
    index=False
)

print("\nTERRATIME 4D - GLOBAL DEM DOWNLOAD PLAN")
print("---------------------------------------")
print("Land centres:", len(land_grid))
print("Matched land centres:", len(matched))
print("Unique DEM tiles required:", len(plan))
print("Already downloaded:", (plan["local_status"] == "Already downloaded").sum())
print("Still needed:", (plan["local_status"] == "Not downloaded").sum())

print("\nTiles by region:")
print(plan.groupby("region").size().to_string())

print("\nDownload priority:")
print(plan.groupby("download_priority").size().to_string())

print("\nFiles saved:")
print(OUTPUT_DIR / "global_land_centre_dem_mapping.csv")
print(OUTPUT_DIR / "global_dem_download_plan.csv")
