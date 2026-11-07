import time
import requests
import pandas as pd
from pathlib import Path

LOCATIONS = [
    ("Western Australia", -32.5, 117.5),
    ("Queensland", -22.5, 147.5),
    ("Baja California", 27.5, -112.5),
    ("Ontario", 47.5, -82.5),
    ("Brooks Range", 67.5, -147.5),
    ("Scandinavia", 67.5, 17.5),
]

PARAMETERS = "T2M,T2M_MAX_AVG,T2M_MIN_AVG"
YEAR = 2020

output_dir = Path("data/processed/environmental")
output_dir.mkdir(parents=True, exist_ok=True)

rows = []

for name, latitude, longitude in LOCATIONS:
    print(f"Collecting temperature data: {name}")

    url = (
        "https://power.larc.nasa.gov/api/temporal/monthly/point"
        f"?parameters={PARAMETERS}&community=SB"
        f"&longitude={longitude}&latitude={latitude}"
        f"&start={YEAR}&end={YEAR}&format=JSON"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()["properties"]["parameter"]

    for month in range(1, 13):
        key = f"{YEAR}{month:02d}"

        rows.append({
            "location": name,
            "latitude": latitude,
            "longitude": longitude,
            "year": YEAR,
            "month": month,
            "mean_temperature_c": data["T2M"].get(key),
            "mean_daily_max_temperature_c": data["T2M_MAX_AVG"].get(key),
            "mean_daily_min_temperature_c": data["T2M_MIN_AVG"].get(key),
        })

    time.sleep(1)

df = pd.DataFrame(rows)
output_file = output_dir / "nasa_power_monthly_temperature_2020.csv"
df.to_csv(output_file, index=False)

print(f"\nSaved {len(df)} monthly records to {output_file}")
print(df.head(10).to_string(index=False))
