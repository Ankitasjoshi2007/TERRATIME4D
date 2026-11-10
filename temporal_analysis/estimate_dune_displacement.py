import csv
from pathlib import Path

import numpy as np

BASE = Path("data/processed/temporal_analysis")
STACK_FILE = BASE / "namib_temporal_stack.npz"
OUT = BASE / "dune_displacement"

OUT.mkdir(parents=True, exist_ok=True)

BLOCK = 64
MAX_SHIFT = 16
MIN_VALID = 0.90
MIN_PEAK_RATIO = 1.20
PIXEL_SIZE_M = 10.0

data = np.load(STACK_FILE)

years = data["years"].astype(str)
texture = data["nir_texture"]

reference = texture[0]

print("TERRATIME4D - DUNE PATTERN DISPLACEMENT")
print("=" * 60)
print("Reference year:", years[0])
print("Block size:", BLOCK, "pixels")
print("Maximum search shift:", MAX_SHIFT, "pixels")

records = []
summaries = []

window_1d = np.hanning(BLOCK).astype("float32")
window_2d = np.outer(window_1d, window_1d)

def estimate_shift(ref, moving):
    common = np.isfinite(ref) & np.isfinite(moving)

    if common.mean() < MIN_VALID:
        return None

    a = ref.copy()
    b = moving.copy()

    a[~common] = np.nanmedian(a[common])
    b[~common] = np.nanmedian(b[common])

    a = a - np.mean(a)
    b = b - np.mean(b)

    std_a = np.std(a)
    std_b = np.std(b)

    if std_a < 1e-8 or std_b < 1e-8:
        return None

    a = (a / std_a) * window_2d
    b = (b / std_b) * window_2d

    fa = np.fft.fft2(a)
    fb = np.fft.fft2(b)

    cross = fa * np.conj(fb)
    magnitude = np.abs(cross)

    cross /= np.maximum(magnitude, 1e-12)

    correlation = np.abs(np.fft.ifft2(cross))

    # Search only within the configured displacement range.
    candidates = []

    for dy in range(-MAX_SHIFT, MAX_SHIFT + 1):
        for dx in range(-MAX_SHIFT, MAX_SHIFT + 1):
            y = dy % BLOCK
            x = dx % BLOCK
            candidates.append((correlation[y, x], dy, dx))

    candidates.sort(reverse=True)

    peak, dy, dx = candidates[0]

    # Ignore the immediate neighbourhood of the primary peak.
    second = max(
        value for value, sy, sx in candidates[1:]
        if abs(sy - dy) > 1 or abs(sx - dx) > 1
    )

    peak_ratio = float(peak / max(second, 1e-12))

    return dy, dx, peak_ratio


for index in range(1, len(years)):
    year = years[index]
    moving = texture[index]

    print(f"\nComparing {years[0]} with {year}")

    shifts = []

    height, width = reference.shape

    for row in range(0, height - BLOCK + 1, BLOCK):
        for col in range(0, width - BLOCK + 1, BLOCK):

            ref_block = reference[
                row:row + BLOCK, col:col + BLOCK
            ]

            mov_block = moving[
                row:row + BLOCK, col:col + BLOCK
            ]

            result = estimate_shift(ref_block, mov_block)

            if result is None:
                continue

            dy, dx, ratio = result

            accepted = ratio >= MIN_PEAK_RATIO

            at_limit = (
                abs(dy) == MAX_SHIFT or
                abs(dx) == MAX_SHIFT
            )

            record = {
                "reference_year": years[0],
                "comparison_year": year,
                "row": row,
                "col": col,
                "alignment_dy_px": dy,
                "alignment_dx_px": dx,
                "apparent_dy_px": -dy,
                "apparent_dx_px": -dx,
                "apparent_dy_m": -dy * PIXEL_SIZE_M,
                "apparent_dx_m": -dx * PIXEL_SIZE_M,
                "peak_ratio": ratio,
                "accepted": accepted,
                "search_limit_reached": at_limit,
            }

            records.append(record)

            if accepted and not at_limit:
                shifts.append((dy, dx, ratio))

    if shifts:
        shifts_array = np.array(shifts)

        median_dy = float(np.median(shifts_array[:, 0]))
        median_dx = float(np.median(shifts_array[:, 1]))

        apparent_dy = -median_dy
        apparent_dx = -median_dx

        summary = {
            "reference_year": years[0],
            "comparison_year": year,
            "accepted_blocks": len(shifts),
            "apparent_dx_pixels": apparent_dx,
            "apparent_dy_pixels": apparent_dy,
            "apparent_dx_metres": apparent_dx * PIXEL_SIZE_M,
            "apparent_dy_metres": apparent_dy * PIXEL_SIZE_M,
            "apparent_displacement_metres": float(
                np.hypot(apparent_dx, apparent_dy) * PIXEL_SIZE_M
            ),
            "median_peak_ratio": float(
                np.median(shifts_array[:, 2])
            ),
        }

        summaries.append(summary)

        print("Accepted blocks:", len(shifts))
        print("Apparent east-west shift:",
              round(summary["apparent_dx_metres"], 2), "m")
        print("Apparent north-south shift:",
              round(summary["apparent_dy_metres"], 2), "m")
        print("Apparent displacement:",
              round(summary["apparent_displacement_metres"], 2), "m")
    else:
        print("No blocks passed the quality threshold.")

block_csv = OUT / "dune_displacement_blocks.csv"
summary_csv = OUT / "dune_displacement_summary.csv"

if records:
    with open(block_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

if summaries:
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)

print("\n" + "=" * 60)
print("DISPLACEMENT ANALYSIS FINISHED")
print("Total blocks examined:", len(records))
print("Year comparisons:", len(years) - 1)
print("Summary:", summary_csv)
print("Block results:", block_csv)
print("\nIMPORTANT: These are apparent texture-pattern shifts,")
print("not yet validated physical dune migration measurements.")


