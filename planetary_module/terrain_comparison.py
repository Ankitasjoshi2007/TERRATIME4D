
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]

MOON_FILE = PROJECT_DIR / "data/raw/moon/ldem_8_float (1).img"
MARS_FILE = PROJECT_DIR / "data/raw/mars/megt90n000eb.img"


def load_moon():
    data = np.fromfile(MOON_FILE, dtype="<f4")
    return data.reshape((1440, 2880))


def load_mars():
    data = np.fromfile(MARS_FILE, dtype=">i2")
    return data.reshape((2880, 5760))


def print_statistics(name, data, unit):
    print(f"\n{name} TERRAIN STATISTICS")
    print("Minimum:", np.min(data), unit)
    print("Maximum:", np.max(data), unit)
    print("Mean:", np.mean(data), unit)
    print("Standard deviation:", np.std(data), unit)


def main():
    print("Loading Moon and Mars terrain...")

    moon = load_moon()
    mars = load_mars()

    print_statistics("MOON", moon, "km relative to reference radius")
    print_statistics("MARS", mars, "meters above areoid")

    moon_small = moon[::4, ::4]
    mars_small = mars[::8, ::8]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    moon_plot = axes[0].imshow(
        moon_small,
        cmap="terrain",
        extent=[0, 360, -90, 90],
        origin="upper"
    )
    axes[0].set_title("Moon Terrain (NASA LOLA)")
    axes[0].set_xlabel("Longitude (degrees east)")
    axes[0].set_ylabel("Latitude (degrees)")
    fig.colorbar(
        moon_plot,
        ax=axes[0],
        label="Height relative to reference radius (km)"
    )

    mars_plot = axes[1].imshow(
        mars_small,
        cmap="terrain",
        extent=[0, 360, -90, 90],
        origin="upper"
    )
    axes[1].set_title("Mars Terrain (NASA MOLA)")
    axes[1].set_xlabel("Longitude (degrees east)")
    axes[1].set_ylabel("Latitude (degrees)")
    fig.colorbar(
        mars_plot,
        ax=axes[1],
        label="Elevation above areoid (m)"
    )

    plt.tight_layout()

    output_file = (
        PROJECT_DIR / "data/processed/comparison/moon_mars_comparison.png"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_file, dpi=200)

    print("\nComparison map saved at:", output_file)

    plt.show()


if __name__ == "__main__":
    main()
