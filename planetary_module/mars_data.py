from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
MARS_DATA_DIR = PROJECT_DIR / "data" / "raw" / "mars"

IMG_FILE = MARS_DATA_DIR / "megt90n000eb.img"


def main():
    print("Loading NASA MOLA Mars elevation data...")

    elevation = np.fromfile(IMG_FILE, dtype=">i2")
    elevation = elevation.reshape((2880, 5760))

    plt.figure(figsize=(12, 6))

    plt.imshow(
        elevation,
        cmap="terrain",
        extent=[0, 360, -90, 90],
        origin="upper"
    )

    plt.colorbar(label="Elevation above Mars areoid (meters)")
    plt.xlabel("Longitude (degrees east)")
    plt.ylabel("Latitude (degrees)")
    plt.title("NASA MOLA Mars Elevation Map")
    plt.tight_layout()

    output_file = (
        PROJECT_DIR / "data" / "processed" / "mars" / "mars_elevation.png"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=200)

    print("Mars elevation map saved at:", output_file)
    plt.show()


if __name__ == "__main__":
    main()