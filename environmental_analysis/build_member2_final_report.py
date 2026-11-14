from pathlib import Path
import pandas as pd

root = Path("data/processed")
out = root / "member2_final"
out.mkdir(parents=True, exist_ok=True)

files = {
    "Environmental comparison": root / "environmental_comparison/six_candidate_environmental_comparison.csv",
    "Cold-climate screening": root / "ice_climate_analysis/six_candidate_cold_climate_screening.csv",
    "Aerosol variability": root / "dust_aerosol_analysis/candidate_aerosol_variability.csv",
    "Mineral/lithology screening": root / "mineral_lithology_analysis/candidate_mineral_lithology_screening.csv",
    "Volcanic/karst screening": root / "volcanic_karst_analysis/volcanic_karst_candidate_screening.csv",
}

for label, path in files.items():
    if not path.exists():
        raise FileNotFoundError(f"{label} missing: {path}")

tables = {label: pd.read_csv(path) for label, path in files.items()}

for label, table in tables.items():
    if len(table) != 6:
        raise ValueError(f"{label}: expected 6 candidates, got {len(table)}")

lines = [
    "# TERRATIME4D — MEMBER 2 FINAL ENVIRONMENTAL AND GEOLOGY REPORT",
    "",
    "## Scope",
    "Comparative environmental, geological and terrain screening of six priority Earth candidate locations.",
    "",
    "## Datasets and analysis outputs",
]

for label, table in tables.items():
    lines += [
        f"### {label}",
        f"- Candidates analysed: {len(table)}",
        f"- Output columns: {', '.join(table.columns)}",
        "",
        table.to_string(index=False),
        ""
    ]

lines += [
    "## Scientific limitations and outstanding work",
    "- Climate and aerosol measurements represent 2020, not long-term climatology.",
    "- Aerosol optical depth is not a dust-specific concentration measurement.",
    "- Cold-climate screening is not confirmed glacier or ice-cover mapping.",
    "- No dedicated glacier inventory was available locally for exact 50 km coverage analysis.",
    "- Macrostrat lithology descriptions are not confirmed mineral deposits.",
    "- Volcanic rock mentions do not establish active or extinct volcano locations.",
    "- Karst host-rock mentions do not establish cave locations.",
    "- Surface-water occurrence is historical (1984–2024), not current water availability.",
    "- Terrain metrics are based on elevation data and do not measure temporal change.",
    "",
    "## Conclusion",
    "The six candidate environments have been compared using available climate, aerosol,",
    "surface-water, geology and terrain evidence. Cold-climate, mineral-lithology and",
    "volcanic/karst indicator screenings provide preliminary evidence only. Dedicated",
    "glacier, dust, mineral-deposit, volcano and cave inventories remain necessary for",
    "confirmed feature mapping."
]

target = out / "MEMBER2_FINAL_ENVIRONMENTAL_GEOLOGY_REPORT.md"
target.write_text("\n".join(lines), encoding="utf-8")

print("FINAL MEMBER 2 REPORT CREATED")
print("Validated datasets:", len(tables))
print("Candidates per dataset: 6")
print("Report:", target)
