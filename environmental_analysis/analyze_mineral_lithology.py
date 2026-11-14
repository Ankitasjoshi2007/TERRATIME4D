from pathlib import Path
import pandas as pd

source = Path(
    "data/processed/global_geology_land_pilot/"
    "priority_candidate_records.csv"
)
out = Path("data/processed/mineral_lithology_analysis")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source).fillna("")
df["description"] = (
    df["name"].astype(str) + " " + df["lithology"].astype(str)
).str.lower()

categories = {
    "igneous_mentions": r"igneous|granite|granitoid|tonalite|diorite|syenite",
    "volcanic_mentions": r"volcanic|basalt|extrusive",
    "metamorphic_mentions": r"metamorphic|gneiss|schist|amphibolite|granulite",
    "sedimentary_mentions": r"sedimentary|sandstone|clay|gravel|silt",
    "quartz_mentions": r"quartz",
    "feldspar_mentions": r"feldspar",
    "mica_mentions": r"mica",
    "carbonate_mentions": r"limestone|dolomite|carbonate",
    "sulfide_mentions": r"sulfide|sulphide|pyrite|chalcopyrite",
    "iron_oxide_mentions": r"hematite|magnetite|goethite"
}

for column, pattern in categories.items():
    df[column] = df["description"].str.contains(
        pattern, regex=True, case=False
    )

summary = df.groupby(
    ["latitude", "longitude"], dropna=False
).agg(
    geological_records=("description", "size"),
    **{
        col: (col, "sum") for col in categories
    }
).reset_index()

summary.to_csv(out / "candidate_mineral_lithology_screening.csv", index=False)
df.to_csv(out / "classified_geological_records.csv", index=False)

report = [
    "# Geological and Mineral-Indicator Screening",
    "",
    f"Geological records examined: {len(df)}",
    f"Candidate locations: {len(summary)}",
    "",
    "## Candidate-level keyword screening",
    summary.to_string(index=False),
    "",
    "## Interpretation and limitations",
    "- Categories are text-based lithology indicators.",
    "- Mineral keyword mentions do not confirm economic mineral deposits.",
    "- Absence of a keyword does not prove absence of a mineral.",
    "- Dedicated mineral occurrence data are still required for deposit mapping.",
    "- Volcanic lithology does not establish the location of a volcano."
]

(out / "mineral_lithology_screening_report.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print("GEOLOGY AND MINERAL-INDICATOR SCREENING COMPLETE")
print(summary.to_string(index=False))
print("\nSaved outputs:", out)
