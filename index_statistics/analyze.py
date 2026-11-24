"""Recount the R9-R12 rank-65 index statistics in Table 7 from archived samples."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, chi2


DATA = Path(__file__).resolve().parent / "data"
DIMENSION = 111


def read_indices(record):
    path = DATA / record["indices_file"]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError(f"Unexpected SHA-256 for {path.name}")
    if len(raw) != record["samples"] * 16:
        raise ValueError(f"Unexpected byte length for {path.name}")
    words = np.frombuffer(raw, dtype="<u8").reshape(-1, 2)
    if np.any(words[:, 1] >= 1 << (DIMENSION - 64)):
        raise ValueError(f"Nonzero padding bits in {path.name}")
    return words


def affine_rank(words):
    """Reduce differences from the first point until the rank reaches 111."""
    origin = int(words[0, 0]) | (int(words[0, 1]) << 64)
    basis = {}
    for low, high in words[1:]:
        difference = (int(low) | (int(high) << 64)) ^ origin
        while difference:
            pivot = difference.bit_length() - 1
            if pivot in basis:
                difference ^= basis[pivot]
            else:
                basis[pivot] = difference
                break
        if len(basis) == DIMENSION:
            break
    return len(basis)


def analyze(words):
    size = len(words)
    tests = []
    for bit in range(DIMENSION):
        ones = int(((words[:, bit // 64] >> (bit % 64)) & 1).sum())
        z = (ones - size / 2) / math.sqrt(size / 4)
        p = binomtest(ones, size, p=0.5, alternative="two-sided").pvalue
        tests.append(dict(kind="coordinate", first_bit=bit, ones=ones, z=z, p=float(p)))

    for width in (8, 16):
        categories = 1 << width
        expected = size / categories
        for start in range(0, DIMENSION - width + 1, width):
            # A group of width 8 or 16 fits within its little-endian 64-bit word.
            group = (words[:, start // 64] >> (start % 64)) & (categories - 1)
            counts = np.bincount(group.astype(np.int64), minlength=categories)
            statistic = np.sum((counts - expected) ** 2 / expected)
            p = chi2.sf(statistic, categories - 1)
            tests.append(dict(kind=f"group{width}", first_bit=start, chi_square=float(statistic), p=float(p)))

    # Holm-adjust all 130 p-values as one family within this sampling design.
    largest = 0.0
    for position, test in enumerate(sorted(tests, key=lambda entry: entry["p"])):
        largest = max(largest, (len(tests) - position) * test["p"])
        test["p_holm"] = min(largest, 1.0)

    _, counts = np.unique(words[:, 0] & ((1 << 24) - 1), return_counts=True)
    pairs = int(np.sum(counts * (counts - 1) // 2, dtype=np.int64))
    summary = {
        "sampled_affine_rank": affine_rank(words),
        "largest_abs_coordinate_z": max(abs(t["z"]) for t in tests if t["kind"] == "coordinate"),
        "minimum_p_groups8": min(t["p"] for t in tests if t["kind"] == "group8"),
        "minimum_p_groups16": min(t["p"] for t in tests if t["kind"] == "group16"),
        "colliding_pairs_first24": pairs,
        "pair_count_expectation": math.comb(size, 2) / 2**24,
        "rejected_tests_holm_0_05": sum(t["p_holm"] <= 0.05 for t in tests),
    }
    return summary, tests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON file for all 260 tests.")
    args = parser.parse_args()
    references = json.loads((DATA / "reference.json").read_text(encoding="utf-8"))
    results = {}
    for design, record in references.items():
        summary, tests = analyze(read_indices(record))
        for key, expected in record["expected_statistics"].items():
            if not math.isclose(summary[key], expected, rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError(f"{design}/{key}: calculated {summary[key]}, archived {expected}")
        results[design] = {
            "samples": record["samples"],
            "sampler_logged_outside": record["sampler_logged_outside"],
            "recalculated": summary,
            "tests": tests,
        }

    print("| Table 7 | One subspace | 32 subspaces |")
    print("|---|---:|---:|")
    print("| Indices outside the affine space (sampler log) | "
          f"{results['single']['sampler_logged_outside']} | {results['mixed']['sampler_logged_outside']} |")
    rows = [
        ("Affine dimension of sampled indices", "sampled_affine_rank", "d"),
        ("Largest absolute coordinate z", "largest_abs_coordinate_z", ".2f"),
        ("Minimum raw p over 13 groups of 8 coordinates", "minimum_p_groups8", ".3f"),
        ("Minimum raw p over 6 groups of 16 coordinates", "minimum_p_groups16", ".3f"),
        ("Pairs on the first 24 coordinates", "colliding_pairs_first24", ",d"),
        ("Holm rejections at 0.05", "rejected_tests_holm_0_05", "d"),
    ]
    for label, key, fmt in rows:
        single = results["single"]["recalculated"][key]
        mixed = results["mixed"]["recalculated"][key]
        print(f"| {label} | {single:{fmt}} | {mixed:{fmt}} |")
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(DATA) or target == Path(__file__).resolve():
            parser.error("Choose an output file outside the packaged data and source files.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
