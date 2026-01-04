# Web Service Statistical Tests

Statistical analysis scripts for comparing web service performance, as described in the article "Is the New Web Service Really Faster?".

![](docs/img/Gemini_Generated_Image_Banner.png)

## Project Structure

```
.
├── docs/                      # Documentation and articles
│   ├── articolo.md           # Article in Italian (markdown)
│   ├── article-en.md         # Article in English (markdown)
│   └── img/                  # Generated visualizations
├── binomial.py               # Binomial distribution visualization
├── ttest.py                  # Standard t-test
├── welch.py                  # Welch's t-test
├── permutation.py            # Permutation test
├── bootstrap.py              # Bootstrap analysis
├── pyproject.toml            # Poetry dependencies
├── Makefile                  # Build automation
└── README.md                 # This file
```

## Overview

This repository contains independent Python scripts demonstrating various statistical tests for web service performance comparison:

- **binomial.py**: Generates the binomial distribution visualization
- **ttest.py**: Standard t-test for comparing two service versions
- **welch.py**: Welch's t-test for unequal variances
- **permutation.py**: Permutation test with block sampling
- **bootstrap.py**: Bootstrap analysis for confidence intervals

## Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

## Installation

### Using Poetry (Recommended)

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
make install
# or
poetry install
```

### Using pip (Alternative)

```bash
pip install numpy pandas scipy matplotlib
```

## Usage

### Using Make (Easiest)

```bash
# Run individual scripts
make binomial
make ttest
make welch
make permutation
make bootstrap

# Run all scripts at once
make all

# Clean generated images
make clean

# Show available commands
make help
```

### Using Poetry directly

```bash
poetry run python binomial.py
poetry run python ttest.py
poetry run python welch.py
poetry run python permutation.py
poetry run python bootstrap.py
```

### Using Python directly

```bash
python binomial.py
python ttest.py
python welch.py
python permutation.py
python bootstrap.py
```

## Output

Each script generates:
1. **Console output**: Statistical test results and interpretations
2. **PNG image**: Visualization saved in the current directory

Generated images (saved in `docs/img/`):
- `binomial.png` - Binomial distribution
- `ttest_results.png` - T-test comparison
- `welch_test_results.png` - Welch's test analysis
- `permutation_test_results.png` - Permutation test results
- `bootstrap_results.png` - Bootstrap confidence intervals

## Script Descriptions

### binomial.py
Generates the binomial distribution for 20 coin flips, illustrating:
- Probability distribution under the null hypothesis
- Most probable outcome (10 heads)
- Example outcome (13 heads)
- Rejection region for α=5%

### ttest.py
Demonstrates standard t-test comparing two web service versions:
- Generates synthetic response time data
- Performs two-sample t-test
- Visualizes distributions and results

### welch.py
Shows Welch's t-test for services with unequal variances:
- Tests for variance equality (Levene's test)
- Compares Welch vs. standard t-test
- Visualizes variance differences

### permutation.py
Implements permutation test with block sampling:
- Simulates correlated response times in time windows
- Uses block means for exchangeability
- Shows null distribution from permutations

### bootstrap.py
Bootstrap resampling for uncertainty quantification:
- Estimates confidence intervals for mean, median, std, and percentiles
- Visualizes bootstrap distributions
- Useful for single service analysis

## Documentation

Full articles explaining the theory and methodology are available in the `docs/` directory:

- **docs/articolo.md** - Italian version (markdown)
- **docs/article-en.md** - English version (markdown)
- **docs/img/** - Generated visualizations

## Customization

All scripts use synthetic data by default. To use your own data:

1. Modify the data generation section in each script
2. Replace with your actual response time data
3. Ensure data is in the expected format (pandas DataFrame with 'response_time' column)

Example:
```python
# Replace this:
response_times = np.random.normal(loc=150, scale=30, size=100)

# With your data:
df = pd.read_csv('your_data.csv')
response_times = df['response_time'].values
```

## Dependencies

- **numpy**: Numerical computations
- **pandas**: Data manipulation
- **scipy**: Statistical functions
- **matplotlib**: Visualization

## License

This code accompanies the article "Is the New Web Service Really Faster?" and is provided for educational purposes.

## Further Reading

Refer to the articles in the `docs/` directory for detailed explanations of:
- When to use each test
- Assumptions and limitations
- Sampling strategies for web services
- Interpretation of results
