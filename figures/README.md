# Figure 5. Greedy sparse search for R9–R12

[Figure 5 (PDF)](figure5.pdf) compares four candidate sets. The left panel shows the distribution of final counts of independent intermediate variables over 64 runs per candidate set. The right panel shows how many quadratic terms remain after each accepted form in the run with the fewest independent intermediate variables. The smallest seed breaks ties.

| Candidate set | Final count across 64 runs | Accepted forms in the plotted run |
| --- | ---: | ---: |
| Coordinates, degree in G | 144 | 144 |
| Coordinates, occurrence count | 146–152 | 146 |
| Coordinates and pairwise XOR | 95–101 | 95 |
| Structured sparse forms | 66 | 66 |

## Data

[final_counts.csv](final_counts.csv) gives the number of runs that ended at each observed count. Cumulative frequencies divided by 64 give the left panel. [term_counts.csv](term_counts.csv) gives the right panel. Each column starts with 1,937 terms at step zero and ends at zero terms. Blank cells follow the end of that run.

## Reproduce the figure

From this directory, use Python 3 and Matplotlib to run

```sh
python plot_figure5.py --output figure5-reproduced.pdf
```

The script checks the archived counts before plotting. The paper figure was reproduced with Matplotlib 3.11.2, Times New Roman for text and STIX for math. Systems without Times New Roman use DejaVu Serif.
