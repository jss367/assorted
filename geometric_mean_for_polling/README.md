# Geometric Mean for Polling Data

A Python visualization demonstrating why geometric mean is superior to arithmetic mean for analyzing polling data with outliers.

## The Problem

When polling people about small percentages (like "What percentage of the US budget is foreign aid?"), a few high estimates can dramatically skew the arithmetic mean, making it a poor representation of public perception.

Example from our simulation:
- True value: 1.0%
- Arithmetic mean: 6.76% (576% error!)
- Geometric mean: 3.15% (215% error)

## The Solution

**Geometric mean** is much less sensitive to outliers than arithmetic mean. Mathematically, it's equivalent to:
```
geometric_mean(x) = exp(mean(log(x)))
```

This is the same as asking respondents to estimate on a log scale and then transforming back - but without the confusion of using log scales in actual surveys!

## Visualizations

The script generates four educational visualizations:

1. **Distribution Histogram** (`distribution_histogram.png`)
   - Shows the distribution of poll responses
   - Compares true value, arithmetic mean, and geometric mean

2. **Linear Scale Comparison** (`linear_scale_comparison.png`)
   - Shows data on linear scale
   - Direct comparison of arithmetic vs geometric mean

3. **Log-Scale Transformation** (`log_scale_transformation.png`)
   - Shows data in log space
   - Demonstrates that geometric mean = exp(mean(log(x)))

4. **Outlier Sensitivity Analysis** (`outlier_sensitivity.png`)
   - Shows how removing the largest outlier affects each mean
   - Geometric mean changes much less than arithmetic mean

## Installation

```bash
# Required packages
pip install numpy matplotlib pytest
```

## Usage

Run the main script to generate all visualizations:

```bash
python main.py
```

Output files will be saved in the `./output/` directory.

## Running Tests

The project follows Test-Driven Development (TDD). Run tests with:

```bash
pytest test_geometric_mean.py -v
```

All core functions have comprehensive test coverage:
- Data generation
- Geometric mean calculation
- Visualization creation

## Project Structure

```
.
├── README.md                      # This file
├── main.py                        # Main script to generate visualizations
├── geometric_mean_polling.py      # Core functions
├── test_geometric_mean.py         # Test suite
└── output/                        # Generated visualizations
    ├── distribution_histogram.png
    ├── linear_scale_comparison.png
    ├── log_scale_transformation.png
    └── outlier_sensitivity.png
```

## Key Insights

1. **Arithmetic mean is vulnerable to outliers**: Even a single extreme value can dramatically shift the mean
2. **Geometric mean is more robust**: It gives less weight to extreme values
3. **Mathematical equivalence**: Geometric mean IS the arithmetic mean in log space
4. **Practical application**: No need to ask respondents to think logarithmically - just use geometric mean on the results!

## Use Cases

This technique is valuable for:
- Survey analysis where extreme values are common
- Public perception polling
- Economic data (incomes, prices, etc.)
- Any ratio or percentage data with wide variability

## License

MIT
