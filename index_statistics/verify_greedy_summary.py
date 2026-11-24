"""Verify the Holm decisions using only the rounded greedy summaries."""

import csv
from fractions import Fraction
from math import isqrt
from pathlib import Path

from scipy.stats import binomtest


FAMILY_SIZE = 111 + 13 + 6
THRESHOLD = Fraction(5, 100) / FAMILY_SIZE


def rounding_interval(text):
    value = Fraction(text)
    digits = len(text.partition(".")[2])
    half_unit = Fraction(1, 2 * 10**digits)
    return value - half_unit, value + half_unit


def coordinate_p_lower(n, largest_z):
    """Evaluate the exact two-sided test at the largest possible integer deviation."""
    root = isqrt(n)
    if n % 2 or root * root != n:
        raise ValueError("This check requires an even square sample size.")
    # A displacement d from the mean corresponds to |z| = 2d/sqrt(n).
    deviation = int(rounding_interval(largest_z)[1] * root / 2)
    midpoint = n // 2
    if not 1 <= deviation <= midpoint:
        raise ValueError("Absolute z-score is outside the supported range.")

    return binomtest(midpoint + deviation, n, p=0.5, alternative="two-sided").pvalue


def main():
    source = Path(__file__).with_name("greedy_summary.csv")
    with source.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    designs = [row["sample_design"] for row in rows]
    if sorted(designs) != ["all_32_subspaces", "single_subspace"]:
        raise ValueError("Expected one single-subspace and one mixed sample.")
    for row in rows:
        if int(row["sample_size"]) != 2**20 or int(row["tests_per_family"]) != FAMILY_SIZE:
            raise ValueError("Unexpected sample or family size.")
        p_coordinate = coordinate_p_lower(int(row["sample_size"]), row["largest_absolute_z"])
        group_bounds = [rounding_interval(row[f"minimum_raw_p_groups_{width}"])[0]
                        for width in (8, 16)]
        smallest = min(p_coordinate, *group_bounds)
        if smallest <= THRESHOLD:
            raise ValueError("The available bounds do not establish zero Holm rejections.")
        if int(row["holm_rejections_at_0_05"]) != 0:
            raise ValueError("The archived Holm decision disagrees with the calculation.")
        # Truncate the display downward so the printed value is also a lower bound.
        displayed = int(smallest * 10**8) / 10**8
        print(f"{row['sample_design']}  all raw p >= {displayed:.8f}  "
              f"Holm rejections = 0/{FAMILY_SIZE} at familywise alpha = 0.05")


if __name__ == "__main__":
    main()
