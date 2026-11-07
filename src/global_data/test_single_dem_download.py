from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TILE_NAME = "Copernicus_DSM_COG_30_S89_00_E016_00_DEM"

BASE_URL = "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"

OUTPUT_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

def main():

    print("\nTERRATIME 4D - SINGLE DEM DOWNLOAD TEST")
    print("---------------------------------------")

    url = f"{BASE_URL}/{TILE_NAME}/{TILE_NAME}.tif"

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_FOLDER / f"{TILE_NAME}.tif"
    temporary_file = OUTPUT_FOLDER / f"{TILE_NAME}.tif.part"

    if output_file.exists():
        print("Tile already exists:", output_file)
        return

    try:
        with requests.get(
            url,
            stream=True,
            timeout=(15, 120)
        ) as response:

            response.raise_for_status()

            with open(temporary_file, "wb") as file:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        file.write(chunk)

        if not temporary_file.exists() or temporary_file.stat().st_size == 0:
            raise IOError("Downloaded file is empty.")

        temporary_file.replace(output_file)

        print("Download successful!")
        print("File:", output_file)
        print("Size:", round(output_file.stat().st_size / (1024 * 1024), 2), "MB")

    except Exception as error:

        if temporary_file.exists():
            temporary_file.unlink()

        print("Download failed:", error)


if __name__ == "__main__":
    main()