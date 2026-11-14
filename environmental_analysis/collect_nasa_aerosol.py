import requests
import pandas as pd
from pathlib import Path

locations = [
    ("Western Australia", -32.5, 117.5),
    ("Queensland Australia", -22.5, 147.5),
    ("Baja California Mexico", 27.5, -112.5),
    ("Ontario Canada", 47.5, -82.5),
    ("Brooks Range Alaska", 67.5, -147.5),
    ("Scandinavia", 67.5, 17.5),
]

rows = []

for name, lat, lon in locations:
    print(f"Collecting: {name}")

    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "AOD_55,AOD_55_ADJ",
        "community": "SB",
        "longitude": lon,
        "latitude": lat,
        "start": 2020,
        "end": 2020,
        "format": "JSON",
    }

    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    data = response.json()

    measurements = data["properties"]["parameter"]

    for month in range(1, 13):
        key = f"2020{month:02d}"
        rows.append({
            "location": name,
            "latitude": lat,
            "longitude": lon,
            "year": 2020,
            "month": month,
            "aod_55": measurements["AOD_55"].get(key),
            "aod_55_adjusted": measurements["AOD_55_ADJ"].get(key),
        })

    print("  12 months collected")

df = pd.DataFrame(rows)

out = Path("data/processed/environmental")
out.mkdir(parents=True, exist_ok=True)

file = out / "nasa_power_monthly_aerosol_2020.csv"
df.to_csv(file, index=False)

print("\nAEROSOL DATA COLLECTION COMPLETE")
print("Records:", len(df))
print("Locations:", df["location"].nunique())
print("Months per location:", df.groupby("location").size().to_dict())
print("Missing AOD values:", df[["aod_55", "aod_55_adjusted"]].isna().sum().to_dict())
print("Saved:", file)
