
import numpy as np
import pandas as pd


def generate_earth_grid(
    latitude_step=5,
    longitude_step=5
):
    """
    Generate a global latitude-longitude grid.

    Each row represents a geographic search cell.
    """

    latitudes = np.arange(
        -90,
        90,
        latitude_step
    )

    longitudes = np.arange(
        -180,
        180,
        longitude_step
    )

    cells = []

    cell_id = 1

    for lat in latitudes:
        for lon in longitudes:

            cells.append({
                "cell_id": cell_id,
                "latitude": lat + latitude_step / 2,
                "longitude": lon + longitude_step / 2,
                "latitude_min": lat,
                "latitude_max": lat + latitude_step,
                "longitude_min": lon,
                "longitude_max": lon + longitude_step
            })

            cell_id += 1

    return pd.DataFrame(cells)


if __name__ == "__main__":

    earth_grid = generate_earth_grid()

    print("TERRATIME 4D - EARTH DISCOVERY ENGINE")
    print("--------------------------------------")

    print("Total geographic cells:", len(earth_grid))

    print("\nFirst 10 geographic cells:")
    print(earth_grid.head(10))

    earth_grid.to_csv(
        "data/processed/earth_grid.csv",
        index=False
    )

    print("\nEarth grid successfully generated!")
