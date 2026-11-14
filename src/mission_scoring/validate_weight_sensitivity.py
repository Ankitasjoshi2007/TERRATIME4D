from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/member4_similarity_scoring"
SOURCE = OUT / "integrated_mission_scores.csv"

WEIGHTS = {
    "Lunar rover mobility": {
        "terrain": 0.80, "solar": 0.20
    },
    "Lunar polar operations": {
        "terrain": 0.25, "solar": 0.25,
        "cold_months": 0.25, "water": 0.25
    },
    "Mars rover mobility": {
        "terrain": 0.65, "dry_site": 0.15,
        "solar": 0.10, "aerosol_mean": 0.10
    },
    "Lunar resource prospecting": {
        "terrain": 0.20, "water": 0.60,
        "persistent_water": 0.20
    },
    "Mars dust-process analogue": {
        "aerosol_mean": 0.40,
        "aerosol_variability": 0.35,
        "high_loading_months": 0.25
    },
    "Volcanic and cave analogue reconnaissance": {
        "volcanic_evidence_rate": 0.50,
        "karst_evidence_rate": 0.50
    },
    "Cold-region operations analogue": {
        "cold_months": 0.50, "coldest_month": 0.50
    },
}

df = pd.read_csv(SOURCE)
records = []
baseline_rows = []

for profile, weights in WEIGHTS.items():
    group = df[df["mission_profile"] == profile].copy()

    if len(group) != 6:
        raise ValueError(f"Incomplete profile: {profile}")

    components = {}
    for component in weights:
        column = f"{component}_index"
        if column not in group.columns or group[column].isna().any():
            raise ValueError(f"Missing component data: {profile}/{column}")
        components[component] = group[column].astype(float)

    baseline = sum(
        components[c] * weight for c, weight in weights.items()
    )
    stored = group["screening_index_0_100"].astype(float)

    if not (baseline - stored).abs().lt(1e-8).all():
        raise ValueError(f"Baseline reproducibility failed: {profile}")

    baseline_rank = baseline.rank(ascending=False, method="min")
    baseline_top = group.loc[baseline.idxmax(), "candidate"]

    baseline_rows.append({
        "mission_profile": profile,
        "baseline_top_candidate": baseline_top,
        "baseline_top_score": float(baseline.max()),
    })

    # Test each component independently at -20% and +20%.
    for changed_component, original_weight in weights.items():
        for direction, factor in [("decrease", 0.8), ("increase", 1.2)]:
            adjusted = dict(weights)
            adjusted[changed_component] = original_weight * factor

            # Redistribute the remaining weight proportionally.
            other_total = sum(
                value for key, value in weights.items()
                if key != changed_component
            )
            remaining = 1.0 - adjusted[changed_component]

            for key in adjusted:
                if key != changed_component:
                    adjusted[key] = (
                        weights[key] * remaining / other_total
                    )

            scores = sum(
                components[c] * adjusted[c] for c in adjusted
            )
            ranks = scores.rank(ascending=False, method="min")
            top_index = scores.idxmax()
            top_candidate = group.loc[top_index, "candidate"]

            records.append({
                "mission_profile": profile,
                "perturbed_component": changed_component,
                "direction": direction,
                "baseline_weight": original_weight,
                "adjusted_weight": adjusted[changed_component],
                "top_candidate": top_candidate,
                "top_candidate_changed": top_candidate != baseline_top,
                "mean_absolute_rank_shift": float(
                    (ranks - baseline_rank).abs().mean()
                ),
                "maximum_absolute_rank_shift": int(
                    (ranks - baseline_rank).abs().max()
                ),
            })

sensitivity = pd.DataFrame(records)
baseline = pd.DataFrame(baseline_rows)

sensitivity.to_csv(
    OUT / "weight_sensitivity_results.csv", index=False
)
baseline.to_csv(
    OUT / "weight_sensitivity_baseline.csv", index=False
)

summary = sensitivity.groupby("mission_profile").agg(
    scenarios_tested=("top_candidate_changed", "size"),
    top_candidate_changes=("top_candidate_changed", "sum"),
    mean_rank_shift=("mean_absolute_rank_shift", "mean"),
    maximum_rank_shift=("maximum_absolute_rank_shift", "max"),
).reset_index()

summary.to_csv(
    OUT / "weight_sensitivity_summary.csv", index=False
)

print("\nWEIGHT SENSITIVITY VALIDATION: PASSED")
print("Baseline reproducibility: all 42 scores reproduced")
print("Profiles tested:", len(WEIGHTS))
print("Perturbation scenarios:", len(sensitivity))
print("Weight perturbation: +/-20% relative, renormalized")
print("\nSensitivity summary:")
print(summary.to_string(index=False))
print("\nBaseline leaders:")
print(baseline.to_string(index=False))
print("\nSaved:")
print(OUT / "weight_sensitivity_results.csv")
print(OUT / "weight_sensitivity_summary.csv")
