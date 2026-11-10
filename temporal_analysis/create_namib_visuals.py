from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path("data/processed/temporal_analysis")
OUT = BASE / "visuals"
OUT.mkdir(parents=True, exist_ok=True)

data = np.load(BASE / "namib_temporal_stack.npz")

years = data["years"].astype(int)
ndvi = data["ndvi"]
texture = data["nir_texture"]

def save_grid(stack, title, filename, cmap, vmin=None, vmax=None):
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, ax in enumerate(axes.flat):
        im = ax.imshow(
            stack[i],
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )
        ax.set_title(str(years[i]))
        ax.axis("off")

    fig.suptitle(title, fontsize=16)
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.75)
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Saved:", OUT / filename)

ndvi_limits = np.nanpercentile(ndvi, [2, 98])
texture_limits = np.nanpercentile(texture, [2, 98])

save_grid(
    ndvi,
    "Namib Sand Sea - NDVI comparison (2019-2026)",
    "namib_ndvi_yearly.png",
    "RdYlGn",
    *ndvi_limits
)

save_grid(
    texture,
    "Namib Sand Sea - NIR texture comparison (2019-2026)",
    "namib_texture_yearly.png",
    "gray",
    *texture_limits
)

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ndvi_change = ndvi[-1] - ndvi[0]
texture_change = texture[-1] - texture[0]

limit = np.nanpercentile(np.abs(ndvi_change), 98)
im = axes[0].imshow(
    ndvi_change, cmap="RdBu_r", vmin=-limit, vmax=limit
)
axes[0].set_title("NDVI change: 2026 minus 2019")
axes[0].axis("off")
fig.colorbar(im, ax=axes[0], shrink=0.75)

limit = np.nanpercentile(np.abs(texture_change), 98)
im = axes[1].imshow(
    texture_change, cmap="RdBu_r", vmin=-limit, vmax=limit
)
axes[1].set_title("NIR texture change: 2026 minus 2019")
axes[1].axis("off")
fig.colorbar(im, ax=axes[1], shrink=0.75)

fig.suptitle("Namib temporal change maps")
fig.savefig(OUT / "namib_change_maps_2019_2026.png",
            dpi=180, bbox_inches="tight")
plt.close(fig)

print("\nVISUALISATION COMPLETE")
print("Output folder:", OUT)
print("Images:", len(list(OUT.glob("*.png"))))
