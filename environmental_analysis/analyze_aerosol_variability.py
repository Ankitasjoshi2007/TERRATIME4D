from pathlib import Path
import pandas as pd

source = Path("data/processed/environmental/nasa_power_monthly_aerosol_2020.csv")
out = Path("data/processed/dust_aerosol_analysis")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source)

for col in ["month", "aod_55", "aod_55_adjusted"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df["location"].nunique() != 6 or len(df) != 72:
    raise ValueError("Expected 72 observations across six candidates.")

if df.groupby("location")["month"].nunique().ne(12).any():
    raise ValueError("Each candidate must have 12 months.")

threshold = df["aod_55"].quantile(0.75)
df["high_aerosol_loading_month"] = df["aod_55"] >= threshold

rows = []

for name, g in df.groupby("location"):
    peak = g.loc[g["aod_55"].idxmax()]
    low = g.loc[g["aod_55"].idxmin()]

    rows.append({
        "candidate": name,
        "annual_mean_aod": g["aod_55"].mean(),
        "adjusted_annual_mean_aod": g["aod_55_adjusted"].mean(),
        "peak_aod": peak["aod_55"],
        "peak_month": int(peak["month"]),
        "minimum_aod": low["aod_55"],
        "minimum_month": int(low["month"]),
        "aod_range": g["aod_55"].max() - g["aod_55"].min(),
        "monthly_aod_std": g["aod_55"].std(),
        "high_loading_months": int(g["high_aerosol_loading_month"].sum()),
        "months_analysed": len(g)
    })

summary = pd.DataFrame(rows).sort_values(
    "annual_mean_aod", ascending=False
)

summary.to_csv(out / "candidate_aerosol_variability.csv", index=False)
df.to_csv(out / "monthly_aerosol_loading_flags.csv", index=False)

report = [
    "# TERRATIME4D — Aerosol Variability Analysis",
    "",
    "Source: NASA POWER AOD at 550 nm, monthly observations for 2020.",
    f"High-loading threshold: pooled 75th percentile = {threshold:.4f}.",
    "",
    "## Candidate comparison",
    summary.to_string(index=False),
    "",
    "## Scientific limitations",
    "- AOD measures total atmospheric aerosol optical depth.",
    "- It does not isolate mineral dust from smoke, pollution or other aerosols.",
    "- High-loading months are relative to this six-candidate dataset.",
    "- This analysis does not measure surface dust deposition, dust storm frequency",
    "  or dust concentration.",
    "- The 2020 observations are not long-term climatological averages."
]

(out / "aerosol_variability_report.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print("\nAEROSOL VARIABILITY ANALYSIS COMPLETE")
print("Pooled 75th percentile:", round(threshold, 4))
print(summary.to_string(index=False))
print("\nSaved outputs in:", out)
