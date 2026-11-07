
import time
from pathlib import Path

import pandas as pd
import requests

LOCATIONS = {
    "Western Australia": (-32.5, 117.5),
    "Queensland": (-22.5, 147.5),
    "Baja California": (27.5, -112.5),
    "Ontario": (47.5, -82.5),
    "Brooks Range": (67.5, -147.5),
    "Scandinavia": (67.5, 17.5),
}

BASE_URL = (
    "https://power.larc.nasa.gov/api/temporal/monthly/point"
)

OUTPUT = Path(
    "data/processed/environmental/"
    "nasa_power_monthly_solar_2020.csv"
)


def collect_solar_data():
    records = []

    for location, (latitude, longitude) in LOCATIONS.items():
        print(f"Collecting solar data: {location}")

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN",
            "community": "SB",
            "longitude": longitude,
            "latitude": latitude,
            "start": "2020",
            "end": "2020",
            "format": "JSON",
        }

        response = requests.get(
            BASE_URL, params=params, timeout=60
        )
        response.raise_for_status()

        properties = response.json()["properties"]["parameter"]
        solar = properties["ALLSKY_SFC_SW_DWN"]

        for month, value in solar.items():
            if month.endswith("13"):
                continue

            records.append({
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "year_month": month,
                "solar_irradiance_w_m2": value,
            })

        time.sleep(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(OUTPUT, index=False)

    print(f"\nSaved {len(records)} records to {OUTPUT}")


if __name__ == "__main__":
    collect_solar_data()
