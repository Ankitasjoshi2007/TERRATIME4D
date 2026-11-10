
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import from_origin


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
MOON_FILE = BASE_DIR / "data" / "raw" / "moon" / "ldem_16.tif"
MARS_FILE = BASE_DIR / "data" / "raw" / "mars" / "megt90n000eb.img"
MARS_LABEL = BASE_DIR / "data" / "raw" / "mars" / "megt90n000eb.lbl"

OUTPUT_DIR = BASE_DIR / "results" / "member3_elevation_maps"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_elevation_map(data, title, filename, unit):
    """Save a global cylindrical elevation map."""

    data = np.asarray(data, dtype=np.float32)

    # Ignore invalid values
    data[~np.isfinite(data)] = np.nan

    fig, ax = plt.subplots(figsize=(14, 7))

    image = ax.imshow(
        data,
        extent=[-180, 180, -90, 90],
        origin="upper",
        aspect="auto",
        cmap="terrain"
    )

    ax.set_title(title, fontsize=15)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")

    colorbar = fig.colorbar(image, ax=ax, shrink=0.85)
    colorbar.set_label(f"Elevation ({unit})")

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=250)
    plt.close(fig)

    print(f"Saved: {filename}")


def main():
    print("MEMBER 3 - MOON AND MARS ELEVATION MAPS")
    print("=" * 50)

    # Moon elevation
    print("\nReading Moon elevation data...")

    with rasterio.open(MOON_FILE) as dataset:
        moon = dataset.read(1).astype(np.float32)
        moon_nodata = dataset.nodata

    if moon_nodata is not None:
        moon[moon == moon_nodata] = np.nan

    save_elevation_map(
        moon,
        "Global Moon Elevation Map",
        "01_moon_global_elevation.png",
        "km"
    )

    # Mars elevation
    print("\nReading Mars elevation data...")

    # MOLA MEGDR: 2880 rows x 5760 columns, 16 pixels/degree.
    # The IMG contains signed 16-bit elevation values in metres.
    mars = np.fromfile(MARS_FILE, dtype=">i2")

    expected_size = 2880 * 5760

    if mars.size != expected_size:
        raise ValueError(
            f"Unexpected Mars data size: {mars.size} values; "
            f"expected {expected_size}."
        )

    mars = mars.reshape((2880, 5760)).astype(np.float32)

    # Convert metres to kilometres.
    mars /= 1000.0

    save_elevation_map(
        mars,
        "Global Mars Elevation Map",
        "02_mars_global_elevation.png",
        "km"
    )

    # Save a short record of the map data.
    report = OUTPUT_DIR / "elevation_map_information.txt"

    with report.open("w", encoding="utf-8") as file:
        file.write("MEMBER 3 - ELEVATION MAP INFORMATION\n")
        file.write("=" * 45 + "\n\n")

        file.write("MOON\n")
        file.write(f"Source: {MOON_FILE.name}\n")
        file.write(f"Grid shape: {moon.shape}\n")
        file.write("Elevation unit: kilometres (source data)\n\n")

        file.write("MARS\n")
        file.write(f"Source: {MARS_FILE.name}\n")
        file.write(f"Grid shape: {mars.shape}\n")
        file.write("Elevation unit: kilometres (converted from metres)\n\n")

        file.write(
            "Maps use a global cylindrical display with longitude "
            "from -180 to 180 degrees and latitude from -90 to 90 degrees.\n"
        )

    print("\nAll elevation maps generated.")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
