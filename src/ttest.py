"""
Standard t-test for comparing two web service versions.
Generates synthetic response time data and performs a t-test.
"""

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic response time data (in milliseconds)
# Old version: mean=150ms, std=30ms
n_samples_old = 100
old_response_times = np.random.normal(loc=150, scale=30, size=n_samples_old)
old_response_times = np.abs(old_response_times)  # Ensure positive values

# New version: mean=140ms, std=28ms (slightly faster)
n_samples_new = 100
new_response_times = np.random.normal(loc=140, scale=28, size=n_samples_new)
new_response_times = np.abs(new_response_times)

# Create DataFrames
df_old = pd.DataFrame({'response_time': old_response_times})
df_new = pd.DataFrame({'response_time': new_response_times})

# Perform standard t-test
t_stat, p_value = ttest_ind(df_old['response_time'], df_new['response_time'])

# Calculate Standard Error manually for educational purposes
n1, n2 = len(df_old), len(df_new)
var1, var2 = df_old['response_time'].var(ddof=1), df_new['response_time'].var(ddof=1)
pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
standard_error = pooled_std * np.sqrt(1/n1 + 1/n2)
mean_diff = df_old['response_time'].mean() - df_new['response_time'].mean()

print("=" * 60)
print("STANDARD T-TEST RESULTS")
print("=" * 60)
print(f"\nOld version:")
print(f"  Mean: {df_old['response_time'].mean():.2f} ms")
print(f"  Std:  {df_old['response_time'].std():.2f} ms")
print(f"  N:    {len(df_old)}")

print(f"\nNew version:")
print(f"  Mean: {df_new['response_time'].mean():.2f} ms")
print(f"  Std:  {df_new['response_time'].std():.2f} ms")
print(f"  N:    {len(df_new)}")

print(f"\nTest calculation:")
print(f"  Mean difference (μ₁ - μ₂): {mean_diff:.2f} ms")
print(f"  Standard Error (SE):      {standard_error:.2f} ms")
print(f"  t-statistic (diff/SE):    {t_stat:.2f}")
print(f"  Formula: t = ({df_old['response_time'].mean():.1f} - {df_new['response_time'].mean():.1f}) / {standard_error:.1f} ≈ {t_stat:.2f}")

print(f"\nTest results:")
print(f"  p-value:     {p_value:.4f}")
print(f"  Result:      {'Significant difference' if p_value < 0.05 else 'No significant difference'}")
print(f"  (using α=0.05 significance level)")
print("=" * 60)

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Histogram comparison
ax1.hist(df_old['response_time'], bins=20, alpha=0.6, label='Old version', 
         color='red', edgecolor='black')
ax1.hist(df_new['response_time'], bins=20, alpha=0.6, label='New version', 
         color='green', edgecolor='black')
ax1.axvline(df_old['response_time'].mean(), color='darkred', linestyle='--', 
            linewidth=2, label=f'Old mean: {df_old["response_time"].mean():.1f}ms')
ax1.axvline(df_new['response_time'].mean(), color='darkgreen', linestyle='--', 
            linewidth=2, label=f'New mean: {df_new["response_time"].mean():.1f}ms')
ax1.set_xlabel('Response Time (ms)', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.set_title('Response Time Distribution', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Student's t-distribution with observed difference
from scipy.stats import t as t_dist

# Calculate degrees of freedom
df_total = len(df_old) + len(df_new) - 2

# Generate t-distribution
t_values = np.linspace(-4, 4, 500)
t_density = t_dist.pdf(t_values, df_total)

ax2.plot(t_values, t_density, 'b-', linewidth=2, label='t-distribution')
ax2.fill_between(t_values, t_density, alpha=0.3)

# Mark the observed t-statistic
ax2.axvline(t_stat, color='red', linestyle='--', linewidth=2.5, 
            label=f'Observed t-stat: {t_stat:.2f}')

# Mark critical values for α=0.05 (two-tailed)
t_critical = t_dist.ppf(0.975, df_total)  # 97.5th percentile for two-tailed test
ax2.axvline(t_critical, color='orange', linestyle=':', linewidth=2, alpha=0.7,
            label=f'Critical value: ±{t_critical:.2f}')
ax2.axvline(-t_critical, color='orange', linestyle=':', linewidth=2, alpha=0.7)

# Shade rejection regions
rejection_left = t_values[t_values <= -t_critical]
rejection_right = t_values[t_values >= t_critical]
ax2.fill_between(rejection_left, t_dist.pdf(rejection_left, df_total), 
                  alpha=0.3, color='red', label='Rejection region (α=0.05)')
ax2.fill_between(rejection_right, t_dist.pdf(rejection_right, df_total), 
                  alpha=0.3, color='red')

ax2.set_xlabel('t-value', fontsize=11)
ax2.set_ylabel('Probability Density', fontsize=11)
ax2.set_title('Student\'s t-Distribution', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# Add p-value annotation
result_text = f"p-value = {p_value:.4f}\n{'✓ Significant (reject H₀)' if p_value < 0.05 else '✗ Not significant'}"
ax2.text(0.05, 0.95, result_text, transform=ax2.transAxes, 
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('docs/img/ttest_results.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'docs/img/ttest_results.png'")
plt.show()
