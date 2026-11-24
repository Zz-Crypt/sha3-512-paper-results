# Assignment consistency by round window

The tables summarize 1,024 distinct assignments per method in each round window. An assignment is consistent when the coefficient matrix and its augmented matrix have equal rank over GF(2). The dimension range covers all consistent draws. A single value means every consistent draw had that dimension.

## Results

### R0-R3

| Method | Consistent / 1,024 | Dimension range |
| --- | ---: | ---: |
| First-factor rule (EUROCRYPT 2023) | 455 | 53-55 |
| Minimum-rank vertex cover | 886 | 129-130 |
| Coordinates, degree in the interaction graph | 897 | 64-66 |
| Coordinates, occurrence count | 904 | 63-64 |
| Coordinates and pairwise XOR | 740 | 106-107 |
| Structured sparse forms | 895 | 118-119 |

### R9-R12

| Method | Consistent / 1,024 | Dimension range |
| --- | ---: | ---: |
| First-factor rule (EUROCRYPT 2023) | 883 | 169-171 |
| Minimum-rank vertex cover | 1,024 | 200 |
| Coordinates, degree in the interaction graph | 1,024 | 121 |
| Coordinates, occurrence count | 1,024 | 119 |
| Coordinates and pairwise XOR | 1,024 | 170 |
| Structured sparse forms | 1,024 | 199 |

## Offline verification

Run the following command from this directory using Python 3.8 or newer. The script uses the Python standard library and the two data files in this folder.

```sh
python verify_statistics.py
```

[assignment_ranks.csv](assignment_ranks.csv) contains one row per draw. The `window`, `method`, and zero-based `draw_order` columns identify the observation. The next two columns give the coefficient and augmented ranks. The final column gives the subspace dimension for consistent draws and is empty for inconsistent draws. The assignments were sampled uniformly without replacement in the coordinate basis of each method.

[expected_summary.json](expected_summary.json) contains the archived consistent counts, dimension histograms, equation counts and kernel dimensions. For each consistent draw, the script subtracts the coefficient rank from the kernel dimension and compares the result with the CSV. It also checks the allowed ranks, the six method identifiers in both windows, all 1,024 distinct draw numbers per group, and the number of observations at each dimension.
