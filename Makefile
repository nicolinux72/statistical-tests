.PHONY: help install binomial ttest welch permutation bootstrap all clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make install      - Install dependencies with Poetry"
	@echo "  make binomial     - Run binomial distribution script"
	@echo "  make ttest        - Run standard t-test script"
	@echo "  make welch        - Run Welch's t-test script"
	@echo "  make permutation  - Run permutation test script"
	@echo "  make bootstrap    - Run bootstrap analysis script"
	@echo "  make all          - Run all scripts sequentially"
	@echo "  make clean        - Remove generated images"

# Install dependencies
install:
	@echo "Installing dependencies with Poetry..."
	poetry install
	@echo "Installation complete!"

# Run individual scripts
binomial:
	@echo "Running binomial distribution analysis..."
	poetry run python src/binomial.py

ttest:
	@echo "Running standard t-test..."
	poetry run python src/ttest.py

welch:
	@echo "Running Welch's t-test..."
	poetry run python src/welch.py

permutation:
	@echo "Running permutation test..."
	poetry run python src/permutation.py

bootstrap:
	@echo "Running bootstrap analysis..."
	poetry run python src/bootstrap.py

docx:
	cd docs && pandoc articolo.md -o articolo.docx

# Run all scripts
all: binomial ttest welch permutation bootstrap
	@echo ""
	@echo "All scripts completed!"

# Clean generated files
clean:
	@echo "Removing generated images..."
	rm -f docs/img/binomial.png
	rm -f docs/img/ttest_results.png
	rm -f docs/img/welch_test_results.png
	rm -f docs/img/permutation_test_results.png
	rm -f docs/img/bootstrap_results.png
	@echo "Cleanup complete!"
