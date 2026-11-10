
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
MOON_DATA_DIR = PROJECT_DIR / "data" / "raw" / "moon"

IMG_FILE = MOON_DATA_DIR / "ldem_8_float (1).img"

def main():
    elevation = np.fromfile(IMG_FILE, dtype="<f4")
    elevation = elevation.reshape((1440, 2880))

    plt.figure(figsize=(12, 6))
    plt.imshow(
        elevation,
        cmap="terrain",
        extent=[0, 360, -90, 90],
        origin="upper"
    )

    plt.colorbar(label="Height relative to reference radius (km)")
    plt.xlabel("Longitude (degrees east)")
    plt.ylabel("Latitude (degrees)")
    plt.title("NASA LOLA Moon Elevation Map")
    plt.tight_layout()

    output_file = PROJECT_DIR / "data" / "processed" / "moon" / "moon_elevation.png"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_file, dpi=200)
    print("Moon elevation map saved at:", output_file)

    plt.show()

if __name__ == "__main__":
    main()
