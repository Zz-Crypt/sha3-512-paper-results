"""Check the two assignment tables against their recorded rank pairs and print them."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
WINDOWS = ("R0-R3", "R9-R12")
METHODS = {
    "ec2023": "First-factor rule (EUROCRYPT 2023)",
    "cover": "Minimum-rank vertex cover",
    "degree": "Coordinates, degree in the interaction graph",
    "occurrence": "Coordinates, occurrence count",
    "pair": "Coordinates and pairwise XOR",
    "sparse": "Structured sparse forms",
}
DRAWS = 1024
FIELDS = ["window", "method", "draw_order", "coefficient_rank", "augmented_rank", "dimension"]


def verify():
    expected = json.loads((HERE / "expected_summary.json").read_text(encoding="utf-8"))
    if expected["draws_per_method"] != DRAWS or set(expected["windows"]) != set(WINDOWS):
        raise ValueError("Expected two round windows and 1,024 draws per method.")

    counts, seen = {}, {}
    for window in WINDOWS:
        if set(expected["windows"][window]["methods"]) != set(METHODS):
            raise ValueError(f"{window} must have all six methods.")
        for method in METHODS:
            counts[window, method] = Counter()
            seen[window, method] = set()

    with (HERE / "assignment_ranks.csv").open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        if rows.fieldnames != FIELDS:
            raise ValueError("Unexpected CSV column names or order.")
        for line, row in enumerate(rows, 2):
            key = window, method = row["window"], row["method"]
            if key not in seen:
                raise ValueError(f"Line {line}: unknown window or method.")
            draw = int(row["draw_order"])
            if draw not in range(DRAWS) or draw in seen[key]:
                raise ValueError(f"Line {line}: duplicate or out-of-range draw number.")
            seen[key].add(draw)

            group = expected["windows"][window]
            kernel = group["methods"][method]["kernel_dimension"]
            a, b = int(row["coefficient_rank"]), int(row["augmented_rank"])
            if not (0 <= a <= min(kernel, group["equation_count"]) and a <= b <= min(a + 1, group["equation_count"])):
                raise ValueError(f"Line {line}: impossible coefficient or augmented rank.")
            if a == b:
                dimension = kernel - a
                if row["dimension"] != str(dimension):
                    raise ValueError(f"Line {line}: dimension must equal kernel dimension minus coefficient rank.")
                counts[key][dimension] += 1
            elif row["dimension"] != "":
                raise ValueError(f"Line {line}: an inconsistent draw must have a blank dimension.")

    for (window, method), histogram in counts.items():
        if len(seen[window, method]) != DRAWS:
            raise ValueError(f"{window}/{method}: missing draws.")
        reference = expected["windows"][window]["methods"][method]
        archived = {int(dim): count for dim, count in reference["dimension_counts"].items()}
        if sum(histogram.values()) != reference["consistent"] or dict(histogram) != archived:
            raise ValueError(f"{window}/{method}: totals differ from the archived dimension counts.")
    return counts


def format_tables(counts):
    tables = []
    for window in WINDOWS:
        lines = [
            f"### {window}",
            "",
            "| Method | Consistent / 1,024 | Dimension range |",
            "| --- | ---: | ---: |",
        ]
        for method, label in METHODS.items():
            histogram = counts[window, method]
            low, high = min(histogram), max(histogram)
            span = str(low) if low == high else f"{low}-{high}"
            lines.append(f"| {label} | {sum(histogram.values()):,} | {span} |")
        tables.append("\n".join(lines))
    return "\n\n".join(tables)


if __name__ == "__main__":
    try:
        results = verify()
    except (ValueError, KeyError, OSError) as error:
        sys.exit(f"Verification failed: {error}")
    print(format_tables(results))
    print("\nVerified 12,288 draws across two round windows and six methods per window.")
