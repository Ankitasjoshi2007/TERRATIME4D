
import geopandas as gpd
import pandas as pd
from pathlib import Path

# Input files
GRID_FILE = Path("data/processed/earth_grid.csv")
LAND_FILE = Path(
    "data/raw/earth/land_cover/natural_earth/ne_10m_land.shp"
)

# Output folder
OUTPUT_DIR = Path("data/processed/land_classification")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading global Earth grid...")
grid = pd.read_csv(GRID_FILE)

print("Loading Natural Earth land polygons...")
land = gpd.read_file(LAND_FILE)

# Create geographic points from grid coordinates
points = gpd.GeoDataFrame(
    grid.copy(),
    geometry=gpd.points_from_xy(
        grid["longitude"],
        grid["latitude"]
    ),
    crs="EPSG:4326"
)

# Check which grid centres intersect land polygons
print("Classifying grid-cell centres...")
matches = gpd.sjoin(
    points,
    land[["geometry"]],
    how="left",
    predicate="intersects"
)

matches["land_class"] = matches["index_right"].notna().map({
    True: "land",
    False: "ocean_or_unclassified"
})

# Keep one result per grid cell
results = matches.drop_duplicates(
    subset=["cell_id"]
).copy()

results = results.drop(
    columns=["geometry", "index_right"],
    errors="ignore"
)

# Save results
output_file = OUTPUT_DIR / "global_land_classification.csv"
results.to_csv(output_file, index=False)

# Print summary
print("\nGLOBAL LAND CLASSIFICATION COMPLETE")
print("Total grid cells:", len(results))
print("\nClassification summary:")
print(results["land_class"].value_counts())
print("\nOutput saved to:", output_file)

print(
    "\nNote: This classifies grid-cell centres only. "
    "It does not establish whether an entire cell is land or ocean. "
    "Coastal, small-island and polar locations need further validation."
)
