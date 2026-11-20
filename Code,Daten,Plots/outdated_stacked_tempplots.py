"""Plot every resonance scan in WithTemp and both WithoutTemp series.

Run from this directory with:
    python visualize_all_resonance_curves.py

The figures are saved in Plots/all_resonance_curves and then shown on screen.
"""

from pathlib import Path
import math
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize


ROOT = Path(__file__).resolve().parent
DATASETS = {
    "With temperature": ROOT / "WithTemp",
    "Without temperature – series 1": ROOT / "WithoutTemp_Messreihe1",
    "Without temperature – series 2": ROOT / "WithoutTemp_Messreihe2",
}
OUTPUT_DIR = ROOT / "Plots" / "all_resonance_curves"


def natural_key(path):
    """Sort names containing numbers in human order (2 before 10)."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


def load_data(path):
    # Same columns used by Plot_and_forloop_file.ipynb: FQ, A and dA.
    return np.loadtxt(
        path, usecols=(0, 5, 6), delimiter=",", skiprows=1, unpack=True
    )


def load_temperature_data(path):
    """Load frequency, amplitude, and the temperature recorded for each point."""
    return np.loadtxt(
        path, usecols=(0, 5, 9), delimiter=",", skiprows=1, unpack=True
    )


def plot_dataset(title, folder):
    files = sorted(folder.glob("*.csv"), key=natural_key)
    if not files:
        print(f"No CSV files found in {folder}")
        return

    ncols = 2
    nrows = math.ceil(len(files) / ncols)
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(13, 3.4 * nrows), squeeze=False
    )
    fig.suptitle(title, fontsize=15)

    for ax, path in zip(axes.flat, files):
        frequency, amplitude, amplitude_error = load_data(path)
        ax.errorbar(
            frequency,
            amplitude,
            yerr=amplitude_error,
            fmt=".-",
            markersize=2.5,
            linewidth=0.8,
            elinewidth=0.35,
            capsize=0,
            label="measured amplitude",
        )

        peak = int(np.nanargmax(amplitude))
        ax.axvline(
            frequency[peak],
            color="tab:red",
            linestyle="--",
            linewidth=0.9,
            label=f"maximum: {frequency[peak]:.3f} Hz",
        )
        label = path.stem.replace("abgebrochen", "aborted: ")
        ax.set_title(label)
        ax.set_xlabel("frequency [Hz]")
        ax.set_ylabel("amplitude A [V]")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)

    for ax in axes.flat[len(files):]:
        ax.remove()

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    output = OUTPUT_DIR / f"{folder.name}.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"Plotted {len(files):2d} files -> {output.relative_to(ROOT)}")


def plot_temperature_overlay(temperatures, title, output_name):
    """Overlay one temperature run, colouring points by recorded temperature."""
    folder = ROOT / "WithTemp"
    available_files = list(folder.glob("*.csv"))
    files = []
    for target in temperatures:
        match = next(
            (path for path in available_files
             if re.search(rf"TempFreq{target}(?:\D|$)", path.stem)),
            None,
        )
        if match is None:
            print(f"Warning: no temperature file found for {target} °C")
        else:
            files.append(match)

    fig, ax = plt.subplots(figsize=(12, 7))
    temperature_cmap = LinearSegmentedColormap.from_list(
        "temperature_red_yellow", ["#6b0000", "#c93b16", "#ffd43b"]
    )
    temperature_norm = Normalize(vmin=40, vmax=58, clip=True)

    for path in files:
        frequency, amplitude, temperature = load_temperature_data(path)
        points = np.column_stack((frequency, amplitude))
        segments = np.stack((points[:-1], points[1:]), axis=1)
        segment_temperature = (temperature[:-1] + temperature[1:]) / 2

        lines = LineCollection(
            segments,
            cmap=temperature_cmap,
            norm=temperature_norm,
            linewidth=2.6,
            alpha=0.55,
            zorder=2,
        )
        lines.set_array(segment_temperature)
        ax.add_collection(lines)
        ax.scatter(
            frequency,
            amplitude,
            c=temperature,
            cmap=temperature_cmap,
            norm=temperature_norm,
            s=18,
            alpha=0.65,
            linewidths=0,
            zorder=3,
        )

    ax.set_xlim(248.5, 251.5)
    ax.autoscale_view(scalex=False, scaley=True)
    ax.set_title(title)
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("amplitude A [V]")
    ax.grid(alpha=0.25)
    colorbar = fig.colorbar(lines, ax=ax, pad=0.02)
    colorbar.set_label("temperature recorded at each point [°C]")
    fig.tight_layout()

    output = OUTPUT_DIR / output_name
    fig.savefig(output, dpi=200, bbox_inches="tight")
    print(f"Plotted temperature overlay -> {output.relative_to(ROOT)}")


def plot_single_resonance(path):
    """Create a detailed plot for one standard resonance CSV file."""
    frequency, amplitude, amplitude_error = load_data(path)
    peak = int(np.nanargmax(amplitude))

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.errorbar(
        frequency,
        amplitude,
        yerr=amplitude_error,
        fmt="o-",
        color="#9e1b1b",
        markersize=3,
        linewidth=1.5,
        elinewidth=0.6,
        alpha=0.8,
        label="measured amplitude",
    )
    ax.axvline(
        frequency[peak],
        color="#e3a008",
        linestyle="--",
        linewidth=1.5,
        label=f"maximum: {frequency[peak]:.3f} Hz",
    )
    ax.set_title(path.stem)
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("amplitude A [V]")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    output = OUTPUT_DIR / f"{path.stem}.png"
    fig.savefig(output, dpi=200, bbox_inches="tight")
    print(f"Plotted single resonance -> {output.relative_to(ROOT)}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for title, folder in DATASETS.items():
        plot_dataset(title, folder)
    plot_temperature_overlay(
        [40, 44, 48, 52, 56],
        "Temperature run 1 (night of August 4–5)",
        "WithTemp_overlay_run1_40-44-48-52-56.png",
    )
    plot_temperature_overlay(
        [42, 46, 50, 54, 58],
        "Temperature run 2 (night of August 5–6)",
        "WithTemp_overlay_run2_42-46-50-54-58.png",
    )
    single_file = ROOT / "PC2_3h_ResFreq0.csv"
    if single_file.exists():
        plot_single_resonance(single_file)
    plt.show()


if __name__ == "__main__":
    main()
