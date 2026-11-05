
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GRID_FILE = PROJECT_ROOT / "data" / "processed" / "earth_grid.csv"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_dem_inventory.csv"
)


def create_tile_name(latitude, longitude):
    """Create a Copernicus one-degree DEM tile name."""

    lat_degree = int(latitude)
    lon_degree = int(longitude)

    north_south = "N" if lat_degree >= 0 else "S"
    east_west = "E" if lon_degree >= 0 else "W"

    return (
        f"Copernicus_DSM_COG_30_"
        f"{north_south}{abs(lat_degree):02d}_00_"
        f"{east_west}{abs(lon_degree):03d}_00_DEM"
    )


def main():
    print("\nTERRATIME 4D - GLOBAL DEM INVENTORY")
    print("-----------------------------------")

    if not GRID_FILE.exists():
        raise FileNotFoundError(
            f"Earth grid not found: {GRID_FILE}"
        )

    grid = pd.read_csv(GRID_FILE)

    inventory = []

    for _, cell in grid.iterrows():

        lat_min = int(cell["latitude_min"])
        lat_max = int(cell["latitude_max"])
        lon_min = int(cell["longitude_min"])
        lon_max = int(cell["longitude_max"])

        for latitude in range(lat_min, lat_max):
            for longitude in range(lon_min, lon_max):

                inventory.append({
                    "cell_id": int(cell["cell_id"]),
                    "tile_latitude": latitude,
                    "tile_longitude": longitude,
                    "tile_name": create_tile_name(
                        latitude,
                        longitude
                    ),
                    "availability": "Not checked",
                    "download_status": "Not downloaded"
                })

    result = pd.DataFrame(inventory)

    result = result.drop_duplicates(
        subset=["tile_name"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Discovery cells:", len(grid))
    print("Unique candidate tiles:", len(result))
    print("Inventory saved to:")
    print(OUTPUT_FILE)

    print("\nFirst 10 inventory records:")
    print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
