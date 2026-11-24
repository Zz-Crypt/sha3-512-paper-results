"""Render Figure 5 from the two archived count tables."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
SERIES = {
    "coordinate_degree": ("Coordinates, degree in $G$", "#315a78", "-", "o"),
    "coordinate_occurrence": ("Coordinates, occurrence count", "#7a7a7a", "--", "s"),
    "coordinate_pairwise_xor": ("Coordinates and pairwise XOR", "#a76f25", "-.", "^"),
    "structured_sparse": ("Structured sparse forms", "#18756d", ":", "D"),
}


def read_counts():
    frequencies = {key: {} for key in SERIES}
    with (HERE / "final_counts.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            counts = frequencies[row["candidate_set"]]
            value = int(row["independent_variables"])
            runs = int(row["runs"])
            if value in counts or runs <= 0:
                raise ValueError(f"Invalid histogram entry: {row}")
            counts[value] = runs

    curves = {key: [] for key in SERIES}
    with (HERE / "term_counts.csv").open(encoding="utf-8", newline="") as f:
        for step, row in enumerate(csv.DictReader(f)):
            if int(row["accepted_forms"]) != step:
                raise ValueError(f"Missing step {step} in term_counts.csv")
            for key, curve in curves.items():
                if row[key]:
                    if len(curve) != step:
                        raise ValueError(f"Missing count in {key} before step {step}")
                    curve.append(int(row[key]))

    for key, curve in curves.items():
        counts = frequencies[key]
        if sum(counts.values()) != 64 or len(curve) != min(counts) + 1:
            raise ValueError(f"Inconsistent run or step counts for {key}")
        if curve[0] != 1937 or curve[-1] != 0 or any(a <= b for a, b in zip(curve, curve[1:])):
            raise ValueError(f"Invalid sequence of term counts for {key}")
    return frequencies, curves


def draw_figure(frequencies, curves):
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "mathtext.fontset": "stix", "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    fig, (left, right) = plt.subplots(1, 2, figsize=(7.0, 3.15))
    handles = []
    for key, (label, color, style, marker) in SERIES.items():
        counts = frequencies[key]
        values = sorted(counts)
        cumulative = []
        total = 0
        for value in values:
            total += counts[value]
            cumulative.append(total / 64)
        line, = left.step([55, *values, 160], [0, *cumulative, 1], where="post",
                          label=label, color=color, linestyle=style, lw=1.35)
        left.scatter(values, cumulative, s=15, marker=marker, color=color, zorder=3)
        handles.append(line)
        curve = curves[key]
        right.plot(range(len(curve)), curve, color=color, linestyle=style,
                   lw=1.35, marker=marker, markersize=3, markevery=max(1, len(curve) // 7))
    left.set(xlim=(55, 160), ylim=(-0.03, 1.04), xlabel="Independent intermediate variables, $r$",
             ylabel="Cumulative fraction of runs", title="(a) Distribution over 64 seeds")
    left.set_yticks([0, 0.25, 0.5, 0.75, 1])
    left.set_xticks([60, 80, 100, 120, 140, 160])
    right.set(xlim=(0, 155), ylim=(-40, 2000), xlabel="Accepted forms",
              ylabel="Remaining quadratic terms", title="(b) Best run per candidate set")
    right.set_xticks([0, 30, 60, 90, 120, 150])
    right.set_yticks([0, 500, 1000, 1500, 2000])
    for ax in (left, right):
        ax.grid(axis="y", color="#dddddd", lw=0.5)
        ax.set_axisbelow(True)
    fig.legend(handles, [line.get_label() for line in handles], loc="lower center", ncol=2,
               frameon=False, bbox_to_anchor=(0.5, 0.015), fontsize=8.2,
               handlelength=2.6, columnspacing=2.2)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.88, bottom=0.32, wspace=0.34)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("figure5-reproduced.pdf"),
                        help="path to the reproduced figure (default: figure5-reproduced.pdf)")
    args = parser.parse_args()
    figure = draw_figure(*read_counts())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, format="pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(figure)
