# Four-round SHA3-512 paper results

Numerical companion to *SAT-Aided Conditional Collision Analysis of Four Consecutive Rounds of SHA3-512* by Ning Kang, Zhongyi Zhang, and Keiichi Nakata. The data correspond to the manuscript of 24 November 2026.

| Manuscript location | Material | Main check |
| --- | --- | --- |
| Tables 4 and 6 | [Assignment rank records and summary tables](statistics/) | Recount 12,288 assignments across two windows and six methods. |
| Table 7 and Section VII-D | [Index samples and statistical summaries](index_statistics/) | Recompute the cover statistics from two samples and inspect the separate greedy summaries. |
| Figure 5 | [Vector figure, count data and plotting script](figures/) | Redraw the manuscript curves from the count data. |
| Section VII-C | [Full-round SHA3-512 reference check](reference_hash/check_sha3_512.py) | Compare 14 digest outputs with Python's hashlib. |

The statistical checks and plot run offline on the recorded data. The complete experimental research archive and the manuscript source are distributed separately.

## Run the checks

From the repository root, the assignment tables and the full-round hash check use the Python standard library.

```sh
python statistics/verify_statistics.py
python reference_hash/check_sha3_512.py
```

For the Table 7 analysis, greedy Holm check and Figure 5 plot, use Python 3.12 and install the dependencies in a virtual environment.

```sh
python -m pip install -r requirements.txt
python index_statistics/analyze.py --output results/table7-tests.json
python index_statistics/verify_greedy_summary.py
python figures/plot_figure5.py --output results/figure5.pdf
```

The supplied [Figure 5 PDF](figures/figure5.pdf) matches the figure in the manuscript. Details of the original fonts and the plotting fallback are in the [figure notes](figures/README.md).

## Citation

Cite the manuscript for the scientific results. Cite the tagged version of this repository for the numerical companion. The version and authors are recorded in [CITATION.cff](CITATION.cff).
