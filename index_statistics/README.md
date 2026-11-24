# Index statistics

## Minimum-rank cover (Table 7)

The two sample files in [data](data/) contain projected indices from the R9-R12 cover experiment. The single-subspace sample contains 1,048,576 observations. The mixed sample contains 32,768 observations from each of 32 subspaces. Each observation occupies 16 bytes, as two little-endian unsigned 64-bit integers. The first word starts with coordinate zero. The top 17 bits of the second word are padding.

Run the following command from the repository root with NumPy and SciPy installed.

```sh
python index_statistics/analyze.py --output results/table7-tests.json
```

The script verifies the two file digests, checks the encoding, and recounts 111 two-sided binomial tests and 19 Pearson chi-square tests per sample. It reports the unadjusted group minima and applies Holm correction at 0.05 to each family of 130 tests. It also counts equal pairs on the first 24 coordinates and computes the affine dimension. The ambient-space membership count in the first row of Table 7 comes from the sampler log because these files store only projected coordinates.

The one-subspace and mixed designs yield 32,823 and 33,064 equal pairs, respectively, compared with an expectation of 32,767.96875. Each design has affine dimension 111 and zero Holm rejections. [Reference values](data/reference.json)

## Greedy sparse search (Section VII-D)

The [archived summaries](greedy_summary.csv) describe a separate pair of sample designs. Their 24-coordinate pair counts are 33,089 and 32,630. For each sample, the smallest unadjusted group p-value and the coordinate p-value implied by the largest absolute z-score both exceed 0.05/130. Holm's procedure therefore gives zero rejections in each family. These results are based on the archived aggregate statistics.

Run the independent summary check from the repository root with SciPy installed. The tested version is pinned in [requirements.txt](../requirements.txt).

```sh
python index_statistics/verify_greedy_summary.py
```

The script allows half a unit in the last recorded decimal place, rounding the largest absolute z-score upward and the minimum group p-values downward. It calls SciPy's two-sided `binomtest` at the largest integer count deviation consistent with that z-score. This gives a lower bound for all 111 coordinate p-values. The 13 eight-coordinate and six sixteen-coordinate tests complete the family of 130. If every raw p-value exceeds the first Holm threshold of 0.05/130, the procedure stops without rejecting any hypothesis. The descriptive pair count is outside this family.
