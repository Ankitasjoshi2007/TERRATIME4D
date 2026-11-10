
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# TERRATIME4D
# MEMBER 3 - PLANETARY COMPARISON VERSION 3
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "results" / "member3_global_analysis_v3"
EARTH_FILE = INPUT_DIR / "earth_existing_reference_statistics_v3.csv"
PLANET_FILE = INPUT_DIR / "moon_mars_physical_summary_v3.csv"
LATITUDE_FILE = INPUT_DIR / "moon_mars_latitude_band_analysis_v3.csv"

OUTPUT_DIR = BASE_DIR / "results" / "member3_global_comparison_v3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_metric(metric_name):
    data = pd.read_csv(EARTH_FILE)
    row = data.loc[data["metric"] == metric_name]

    if row.empty:
        raise ValueError(f"Earth metric not found: {metric_name}")

    return float(row.iloc[0]["mean"])


def main():

    print("\nTERRATIME4D - PLANETARY COMPARISON V3")
    print("=" * 50)

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    planets = pd.read_csv(PLANET_FILE)
    latitude = pd.read_csv(LATITUDE_FILE)

    moon = planets.loc[planets["planet"] == "Moon"].iloc[0]
    mars = planets.loc[planets["planet"] == "Mars"].iloc[0]

    # Earth values are means across 645 processed tiles.
    earth_slope = load_metric("slope_mean_degrees")
    earth_elevation = load_metric("elevation_mean_m")

    earth_roughness_270 = load_metric("roughness_270m_mean")
    earth_roughness_630 = load_metric("roughness_630m_mean")
    earth_roughness_1350 = load_metric("roughness_1350m_mean")

    # --------------------------------------------------
    # BUILD COMPARISON TABLE
    # --------------------------------------------------

    comparison = pd.DataFrame([
        {
            "Planet": "Earth",
            "Mean_Slope_Degrees": earth_slope,
            "Mean_Elevation_km": earth_elevation / 1000,
            "Mean_Roughness_m": np.nan,
            "Roughness_Scale": "270m, 630m and 1350m"
        },
        {
            "Planet": "Moon",
            "Mean_Slope_Degrees": moon["slope_area_weighted_mean_degrees"],
            "Mean_Elevation_km": moon["elevation_area_weighted_mean_km"],
            "Mean_Roughness_m": moon["roughness_area_weighted_mean_km"] * 1000,
            "Roughness_Scale": "Approximately 11 km"
        },
        {
            "Planet": "Mars",
            "Mean_Slope_Degrees": mars["slope_area_weighted_mean_degrees"],
            "Mean_Elevation_km": mars["elevation_area_weighted_mean_km"],
            "Mean_Roughness_m": mars["roughness_area_weighted_mean_km"] * 1000,
            "Roughness_Scale": "Approximately 11 km"
        }
    ])

    comparison.to_csv(
        OUTPUT_DIR / "planetary_comparison_values_v3.csv",
        index=False
    )

    # --------------------------------------------------
    # GRAPH 1: MEAN SLOPE COMPARISON
    # --------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.bar(
        ["Earth", "Moon", "Mars"],
        [
            earth_slope,
            moon["slope_area_weighted_mean_degrees"],
            mars["slope_area_weighted_mean_degrees"]
        ]
    )

    plt.title("Mean Terrain Slope Comparison")
    plt.ylabel("Mean Slope (degrees)")
    plt.xlabel("Planet")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "01_mean_slope_comparison.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 2: EARTH ROUGHNESS AT THREE SCALES
    # --------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.bar(
        ["270 m", "630 m", "1350 m"],
        [
            earth_roughness_270,
            earth_roughness_630,
            earth_roughness_1350
        ]
    )

    plt.title("Earth Terrain Roughness at Different Scales")
    plt.ylabel("Mean Roughness (m)")
    plt.xlabel("Approximate Spatial Scale")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "02_earth_roughness_scales.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 3: MOON AND MARS ROUGHNESS
    # --------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.bar(
        ["Moon", "Mars"],
        [
            moon["roughness_area_weighted_mean_km"] * 1000,
            mars["roughness_area_weighted_mean_km"] * 1000
        ]
    )

    plt.title("Moon and Mars Roughness Comparison")
    plt.ylabel("Area-Weighted Mean Roughness (m)")
    plt.xlabel("Planet")
    plt.text(
        0.5, 0.95,
        "Both calculated at approximately 11 km target scale",
        transform=plt.gca().transAxes,
        ha="center"
    )
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "03_moon_mars_roughness_comparison.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 4: ELEVATION COMPARISON
    # --------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.bar(
        ["Earth", "Moon", "Mars"],
        [
            earth_elevation / 1000,
            moon["elevation_area_weighted_mean_km"],
            mars["elevation_area_weighted_mean_km"]
        ]
    )

    plt.title("Mean Elevation Comparison")
    plt.ylabel("Mean Elevation (km)")
    plt.xlabel("Planet")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "04_mean_elevation_comparison.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 5: LATITUDE-WISE SLOPE
    # --------------------------------------------------

    latitude["latitude_center"] = latitude["latitude_band"].str.extract(
        r"(-?\d+)\s+to"
    )[0].astype(float) + 5

    plt.figure(figsize=(11, 6))

    for planet in ["Moon", "Mars"]:

        subset = latitude[latitude["planet"] == planet].sort_values(
            "latitude_center"
        )

        plt.plot(
            subset["latitude_center"],
            subset["slope_mean_degrees"],
            marker="o",
            label=planet
        )

    plt.title("Terrain Slope Across Latitude Bands")
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Mean Slope (degrees)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "05_latitude_slope_comparison.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 6: LATITUDE-WISE ROUGHNESS
    # --------------------------------------------------

    plt.figure(figsize=(11, 6))

    for planet in ["Moon", "Mars"]:

        subset = latitude[latitude["planet"] == planet].sort_values(
            "latitude_center"
        )

        plt.plot(
            subset["latitude_center"],
            subset["roughness_mean_km"] * 1000,
            marker="o",
            label=planet
        )

    plt.title("Terrain Roughness Across Latitude Bands")
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Mean Roughness (m)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "06_latitude_roughness_comparison.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # GRAPH 7: COMBINED PLANETARY DASHBOARD
    # --------------------------------------------------

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].bar(
        ["Earth", "Moon", "Mars"],
        [
            earth_slope,
            moon["slope_area_weighted_mean_degrees"],
            mars["slope_area_weighted_mean_degrees"]
        ]
    )
    axes[0, 0].set_title("Mean Slope (degrees)")

    axes[0, 1].bar(
        ["Earth", "Moon", "Mars"],
        [
            earth_elevation / 1000,
            moon["elevation_area_weighted_mean_km"],
            mars["elevation_area_weighted_mean_km"]
        ]
    )
    axes[0, 1].set_title("Mean Elevation (km)")

    axes[1, 0].bar(
        ["270 m", "630 m", "1350 m"],
        [
            earth_roughness_270,
            earth_roughness_630,
            earth_roughness_1350
        ]
    )
    axes[1, 0].set_title("Earth Roughness at Different Scales (m)")

    axes[1, 1].bar(
        ["Moon", "Mars"],
        [
            moon["roughness_area_weighted_mean_km"] * 1000,
            mars["roughness_area_weighted_mean_km"] * 1000
        ]
    )
    axes[1, 1].set_title("Moon and Mars Roughness at ~11 km (m)")

    fig.suptitle(
        "TERRATIME4D - Planetary Terrain Comparison V3",
        fontsize=15
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "07_planetary_comparison_dashboard.png",
        dpi=300
    )
    plt.close()

    # --------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------

    report = [
        "TERRATIME4D",
        "MEMBER 3 - PLANETARY COMPARISON VERSION 3",
        "=" * 55,
        "",
        "OBJECTIVE",
        "Compare available physical terrain measurements",
        "for Earth, Moon and Mars.",
        "",
        "EARTH",
        "Reference: 645 processed terrain tiles.",
        f"Mean tile slope: {earth_slope:.4f} degrees.",
        f"Mean tile elevation: {earth_elevation:.4f} metres.",
        f"Mean roughness at 270 m: {earth_roughness_270:.4f} m.",
        f"Mean roughness at 630 m: {earth_roughness_630:.4f} m.",
        f"Mean roughness at 1350 m: {earth_roughness_1350:.4f} m.",
        "",
        "MOON",
        f"Area-weighted mean slope: {moon['slope_area_weighted_mean_degrees']:.4f} degrees.",
        f"Area-weighted mean elevation: {moon['elevation_area_weighted_mean_km']:.4f} km.",
        f"Area-weighted mean roughness: {moon['roughness_area_weighted_mean_km']:.4f} km.",
        "",
        "MARS",
        f"Area-weighted mean slope: {mars['slope_area_weighted_mean_degrees']:.4f} degrees.",
        f"Area-weighted mean elevation: {mars['elevation_area_weighted_mean_km']:.4f} km.",
        f"Area-weighted mean roughness: {mars['roughness_area_weighted_mean_km']:.4f} km.",
        "",
        "SCIENTIFIC LIMITATIONS",
        "1. Earth represents 645 processed tiles, not complete global coverage.",
        "2. Earth statistics are unweighted averages of tile-level statistics.",
        "3. Moon and Mars are global elevation grids.",
        "4. Earth roughness scales are 270 m, 630 m and 1350 m.",
        "5. Moon and Mars roughness target is approximately 11 km.",
        "6. Roughness values at different scales must not be treated as directly equivalent.",
        "7. Moon and Mars latitude-band rows assume north-to-south grid orientation.",
        "8. The comparison is exploratory and does not establish geological similarity.",
        "",
        "OUTPUT",
        "Seven comparison graphs and one comparison CSV were generated."
    ]

    (OUTPUT_DIR / "member3_planetary_comparison_report_v3.txt").write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nComparison completed successfully!")
    print(f"Output folder: {OUTPUT_DIR}")
    print("Generated 7 graphs, 1 CSV and 1 report.")


if __name__ == "__main__":
    main()
