from pathlib import Path

import pandas as pd
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

GRID_FILE = PROJECT_ROOT / "data" / "processed" / "earth_grid.csv"
DEM_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_global_grid_coverage.csv"
)


def calculate_overlap(cell, bounds):
    """
    Calculate the geographic overlap between a grid cell
    and a DEM raster footprint.

    Returns overlap percentage based on coordinate degrees.
    This is a footprint measure, not valid-pixel coverage.
    """

    overlap_left = max(cell["longitude_min"], bounds.left)
    overlap_right = min(cell["longitude_max"], bounds.right)

    overlap_bottom = max(cell["latitude_min"], bounds.bottom)
    overlap_top = min(cell["latitude_max"], bounds.top)

    if overlap_right <= overlap_left or overlap_top <= overlap_bottom:
        return 0.0

    cell_area = (
        (cell["longitude_max"] - cell["longitude_min"])
        * (cell["latitude_max"] - cell["latitude_min"])
    )

    overlap_area = (
        (overlap_right - overlap_left)
        * (overlap_top - overlap_bottom)
    )

    return (overlap_area / cell_area) * 100.0


def build_coverage_report():
    grid = pd.read_csv(GRID_FILE)

    dem_files = sorted(DEM_FOLDER.glob("*.tif"))

    if not dem_files:
        raise FileNotFoundError(
            f"No DEM GeoTIFF files found in {DEM_FOLDER}"
        )

    raster_records = []

    for dem_path in dem_files:
        with rasterio.open(dem_path) as raster:
            if raster.crs is None:
                raise ValueError(f"Missing CRS: {dem_path.name}")

            if raster.crs.to_epsg() != 4326:
                raise ValueError(
                    f"Expected EPSG:4326, found {raster.crs}: "
                    f"{dem_path.name}"
                )

            raster_records.append({
                "file": dem_path.name,
                "bounds": raster.bounds,
                "resolution_x": raster.res[0],
                "resolution_y": raster.res[1],
                "width": raster.width,
                "height": raster.height,
            })

    rows = []

    for _, cell in grid.iterrows():
        intersecting_files = []
        coverage_percent = 0.0

        for raster in raster_records:
            overlap = calculate_overlap(
                cell,
                raster["bounds"]
            )

            if overlap > 0:
                intersecting_files.append(raster["file"])
                coverage_percent += overlap

        coverage_percent = min(coverage_percent, 100.0)

        rows.append({
            "cell_id": cell["cell_id"],
            "latitude": cell["latitude"],
            "longitude": cell["longitude"],
            "coverage_status": (
    "Meaningful DEM footprint"
    if coverage_percent >= 0.01
    else "Minor overlap"
    if coverage_percent > 0
    else "No local DEM footprint"
),
            "coverage_percent_approx": round(
                coverage_percent, 6
            ),
            "intersecting_dem_count": len(intersecting_files),
            "dem_files": ";".join(intersecting_files),
        })

    report = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_FILE, index=False)

    print("TERRATIME 4D - GLOBAL DEM COVERAGE REPORT")
    print("-----------------------------------------")
    print("Global grid cells:", len(report))
    print("Local DEM files:", len(raster_records))
    print(
        "Cells intersecting a DEM footprint:",
        (report["intersecting_dem_count"] > 0).sum()
    )
    print(
        "Cells without a local DEM footprint:",
        (report["intersecting_dem_count"] == 0).sum()
    )
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    build_coverage_report()