"""
Bootstrap technique for estimating confidence intervals of response time statistics.
Useful for quantifying uncertainty in single service measurements.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic response time data with a realistic distribution
# Using log-normal distribution to simulate typical web service response times
# (positive values with right skew - some outliers with very high latency)
n_samples = 200
mean_response = 150  # ms
std_response = 40    # ms

# Generate log-normal distributed response times
mu = np.log(mean_response**2 / np.sqrt(mean_response**2 + std_response**2))
sigma = np.sqrt(np.log(1 + (std_response**2 / mean_response**2)))
response_times = np.random.lognormal(mu, sigma, n_samples)

# Create DataFrame
df = pd.DataFrame({'response_time': response_times})

# Bootstrap configuration
n_bootstrap = 10000

# Generate bootstrap samples and calculate statistics
bootstrap_means = []
bootstrap_medians = []
bootstrap_stds = []
bootstrap_p95 = []

print("Generating bootstrap samples...")
for i in range(n_bootstrap):
    # Resample with replacement
    sample = np.random.choice(response_times, size=len(response_times), replace=True)
    
    # Calculate statistics for this bootstrap sample
    bootstrap_means.append(np.mean(sample))
    bootstrap_medians.append(np.median(sample))
    bootstrap_stds.append(np.std(sample))
    bootstrap_p95.append(np.percentile(sample, 95))
    
    if (i + 1) % 2000 == 0:
        print(f"  {i + 1}/{n_bootstrap} samples generated...")

bootstrap_means = np.array(bootstrap_means)
bootstrap_medians = np.array(bootstrap_medians)
bootstrap_stds = np.array(bootstrap_stds)
bootstrap_p95 = np.array(bootstrap_p95)

# Calculate confidence intervals (95%)
def calculate_ci(bootstrap_samples):
    """Calculate 95% confidence interval"""
    ci_lower = np.percentile(bootstrap_samples, 2.5)
    ci_upper = np.percentile(bootstrap_samples, 97.5)
    return ci_lower, ci_upper

ci_mean_lower, ci_mean_upper = calculate_ci(bootstrap_means)
ci_median_lower, ci_median_upper = calculate_ci(bootstrap_medians)
ci_std_lower, ci_std_upper = calculate_ci(bootstrap_stds)
ci_p95_lower, ci_p95_upper = calculate_ci(bootstrap_p95)

# Observed statistics
observed_mean = np.mean(response_times)
observed_median = np.median(response_times)
observed_std = np.std(response_times)
observed_p95 = np.percentile(response_times, 95)

# Print results
print("\n" + "=" * 70)
print("BOOTSTRAP ANALYSIS RESULTS")
print("=" * 70)

print(f"\nOriginal sample:")
print(f"  Size: {len(response_times)}")
print(f"  Mean: {observed_mean:.2f} ms")
print(f"  Median: {observed_median:.2f} ms")
print(f"  Std: {observed_std:.2f} ms")
print(f"  95th percentile: {observed_p95:.2f} ms")

print(f"\nBootstrap configuration:")
print(f"  Number of resamples: {n_bootstrap}")
print(f"  Confidence level: 95%")

print(f"\n{'─' * 70}")
print("MEAN:")
print(f"  Observed:         {observed_mean:.2f} ms")
print(f"  95% CI:           [{ci_mean_lower:.2f}, {ci_mean_upper:.2f}] ms")
print(f"  CI width:         {ci_mean_upper - ci_mean_lower:.2f} ms")

print(f"\nMEDIAN:")
print(f"  Observed:         {observed_median:.2f} ms")
print(f"  95% CI:           [{ci_median_lower:.2f}, {ci_median_upper:.2f}] ms")
print(f"  CI width:         {ci_median_upper - ci_median_lower:.2f} ms")

print(f"\nSTANDARD DEVIATION:")
print(f"  Observed:         {observed_std:.2f} ms")
print(f"  95% CI:           [{ci_std_lower:.2f}, {ci_std_upper:.2f}] ms")
print(f"  CI width:         {ci_std_upper - ci_std_lower:.2f} ms")

print(f"\n95TH PERCENTILE:")
print(f"  Observed:         {observed_p95:.2f} ms")
print(f"  95% CI:           [{ci_p95_lower:.2f}, {ci_p95_upper:.2f}] ms")
print(f"  CI width:         {ci_p95_upper - ci_p95_lower:.2f} ms")

print("\n" + "=" * 70)

# Visualization
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 1. Original response time distribution
ax1 = fig.add_subplot(gs[0, :])
ax1.hist(response_times, bins=40, color='steelblue', alpha=0.7, edgecolor='black')
ax1.axvline(observed_mean, color='red', linestyle='--', linewidth=2.5, 
            label=f'Mean: {observed_mean:.1f}ms')
ax1.axvline(observed_median, color='green', linestyle='--', linewidth=2.5,
            label=f'Median: {observed_median:.1f}ms')
ax1.axvline(observed_p95, color='orange', linestyle='--', linewidth=2.5,
            label=f'95th percentile: {observed_p95:.1f}ms')
ax1.set_xlabel('Response Time (ms)', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.set_title('Original Response Time Distribution', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Bootstrap distribution of means
ax2 = fig.add_subplot(gs[1, 0])
ax2.hist(bootstrap_means, bins=50, density=True, alpha=0.7, edgecolor='black', color='lightblue')
ax2.axvline(observed_mean, color='red', linestyle='--', linewidth=2.5, label='Observed mean')
ax2.axvline(ci_mean_lower, color='green', linestyle='--', linewidth=2, label='95% CI')
ax2.axvline(ci_mean_upper, color='green', linestyle='--', linewidth=2)
ax2.fill_betweenx([0, ax2.get_ylim()[1]], ci_mean_lower, ci_mean_upper, 
                   color='green', alpha=0.2)
ax2.set_xlabel('Mean Response Time (ms)', fontsize=10)
ax2.set_ylabel('Density', fontsize=10)
ax2.set_title('Bootstrap Distribution of Means', fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# Add CI annotation
ci_text = f'95% CI:\n[{ci_mean_lower:.1f}, {ci_mean_upper:.1f}] ms'
ax2.text(0.98, 0.97, ci_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 3. Bootstrap distribution of medians
ax3 = fig.add_subplot(gs[1, 1])
ax3.hist(bootstrap_medians, bins=50, density=True, alpha=0.7, edgecolor='black', color='lightcoral')
ax3.axvline(observed_median, color='red', linestyle='--', linewidth=2.5, label='Observed median')
ax3.axvline(ci_median_lower, color='green', linestyle='--', linewidth=2, label='95% CI')
ax3.axvline(ci_median_upper, color='green', linestyle='--', linewidth=2)
ax3.fill_betweenx([0, ax3.get_ylim()[1]], ci_median_lower, ci_median_upper, 
                   color='green', alpha=0.2)
ax3.set_xlabel('Median Response Time (ms)', fontsize=10)
ax3.set_ylabel('Density', fontsize=10)
ax3.set_title('Bootstrap Distribution of Medians', fontsize=11, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

ci_text = f'95% CI:\n[{ci_median_lower:.1f}, {ci_median_upper:.1f}] ms'
ax3.text(0.98, 0.97, ci_text, transform=ax3.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 4. Bootstrap distribution of standard deviations
ax4 = fig.add_subplot(gs[2, 0])
ax4.hist(bootstrap_stds, bins=50, density=True, alpha=0.7, edgecolor='black', color='lightgreen')
ax4.axvline(observed_std, color='red', linestyle='--', linewidth=2.5, label='Observed std')
ax4.axvline(ci_std_lower, color='green', linestyle='--', linewidth=2, label='95% CI')
ax4.axvline(ci_std_upper, color='green', linestyle='--', linewidth=2)
ax4.fill_betweenx([0, ax4.get_ylim()[1]], ci_std_lower, ci_std_upper, 
                   color='green', alpha=0.2)
ax4.set_xlabel('Standard Deviation (ms)', fontsize=10)
ax4.set_ylabel('Density', fontsize=10)
ax4.set_title('Bootstrap Distribution of Standard Deviations', fontsize=11, fontweight='bold')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

ci_text = f'95% CI:\n[{ci_std_lower:.1f}, {ci_std_upper:.1f}] ms'
ax4.text(0.98, 0.97, ci_text, transform=ax4.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 5. Bootstrap distribution of 95th percentiles
ax5 = fig.add_subplot(gs[2, 1])
ax5.hist(bootstrap_p95, bins=50, density=True, alpha=0.7, edgecolor='black', color='plum')
ax5.axvline(observed_p95, color='red', linestyle='--', linewidth=2.5, label='Observed P95')
ax5.axvline(ci_p95_lower, color='green', linestyle='--', linewidth=2, label='95% CI')
ax5.axvline(ci_p95_upper, color='green', linestyle='--', linewidth=2)
ax5.fill_betweenx([0, ax5.get_ylim()[1]], ci_p95_lower, ci_p95_upper, 
                   color='green', alpha=0.2)
ax5.set_xlabel('95th Percentile (ms)', fontsize=10)
ax5.set_ylabel('Density', fontsize=10)
ax5.set_title('Bootstrap Distribution of 95th Percentiles', fontsize=11, fontweight='bold')
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)

ci_text = f'95% CI:\n[{ci_p95_lower:.1f}, {ci_p95_upper:.1f}] ms'
ax5.text(0.98, 0.97, ci_text, transform=ax5.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.savefig('docs/img/bootstrap_results.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'docs/img/bootstrap_results.png'")
plt.show()
