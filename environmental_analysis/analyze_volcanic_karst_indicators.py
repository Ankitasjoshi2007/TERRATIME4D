from pathlib import Path
import pandas as pd

source = Path(
    "data/processed/global_geology_land_pilot/"
    "priority_candidate_records.csv"
)
out = Path("data/processed/volcanic_karst_analysis")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source).fillna("")
df["description"] = (
    df["name"].astype(str) + " " + df["lithology"].astype(str)
).str.lower()

df["volcanic_rock_mention"] = df["description"].str.contains(
    r"volcanic|basalt|lava|extrusive", regex=True
)
df["karst_host_rock_mention"] = df["description"].str.contains(
    r"limestone|dolomite|carbonate|marble", regex=True
)
df["cave_or_karst_feature_confirmed"] = False
df["volcano_location_confirmed"] = False

summary = df.groupby(["latitude", "longitude"]).agg(
    geological_records=("description", "size"),
    volcanic_rock_mentions=("volcanic_rock_mention", "sum"),
    possible_karst_host_rock_mentions=("karst_host_rock_mention", "sum")
).reset_index()

summary.to_csv(out / "volcanic_karst_candidate_screening.csv", index=False)
df.to_csv(out / "classified_volcanic_karst_records.csv", index=False)

print("VOLCANIC AND KARST INDICATOR SCREENING COMPLETE")
print(summary.to_string(index=False))
print("\nNo volcano or cave locations are confirmed by these records.")
print("Saved:", out)
