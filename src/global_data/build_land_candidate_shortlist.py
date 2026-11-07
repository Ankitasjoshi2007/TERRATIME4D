
import pandas as pd
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/global_geology_land_pilot/land_geology_records.csv"
)

OUTPUT_FILE = Path(
    "data/processed/global_geology_land_pilot/land_candidate_shortlist.csv"
)

df = pd.read_csv(INPUT_FILE).fillna("")

candidates = []

for (latitude, longitude), group in df.groupby(
    ["latitude", "longitude"]
):
    names = sorted(set(
        str(x).strip() for x in group["name"] if str(x).strip()
    ))

    lithologies = sorted(set(
        str(x).strip() for x in group["lithology"] if str(x).strip()
    ))

    text = " ".join(names + lithologies).lower()

    categories = []

    if any(word in text for word in ["basalt", "volcanic", "lava"]):
        categories.append("volcanic")

    if any(word in text for word in ["granite", "igneous", "tonalite"]):
        categories.append("igneous")

    if any(word in text for word in ["metamorphic", "gneiss", "schist"]):
        categories.append("metamorphic")

    if any(word in text for word in ["sedimentary", "sandstone", "shale"]):
        categories.append("sedimentary")

    if "ice" in text:
        categories.append("ice")

    candidates.append({
        "latitude": latitude,
        "longitude": longitude,
        "record_count": len(group),
        "geology_categories": "; ".join(categories),
        "geological_names": "; ".join(names),
        "lithologies": "; ".join(lithologies)
    })

result = pd.DataFrame(candidates)

result.to_csv(OUTPUT_FILE, index=False)

print("\nLAND CANDIDATE SHORTLIST CREATED")
print("Locations grouped:", len(result))
print("Output file:", OUTPUT_FILE)
print("\nGeology category summary:")

print(
    result["geology_categories"]
    .str.get_dummies(sep="; ")
    .sum()
    .sort_values(ascending=False)
)
