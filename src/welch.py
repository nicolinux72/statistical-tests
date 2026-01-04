"""
Welch's t-test for comparing two web service versions with unequal variances.
More robust than standard t-test when variance assumption is violated.
"""

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, levene
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic response time data with different variances
# Old version: mean=150ms, std=40ms (higher variance)
n_samples_old = 100
old_response_times = np.random.normal(loc=150, scale=40, size=n_samples_old)
old_response_times = np.abs(old_response_times)

# New version: mean=135ms, std=20ms (lower variance, faster and more stable)
n_samples_new = 120
new_response_times = np.random.normal(loc=135, scale=20, size=n_samples_new)
new_response_times = np.abs(new_response_times)

# Create DataFrames
df_old = pd.DataFrame({'response_time': old_response_times})
df_new = pd.DataFrame({'response_time': new_response_times})

# Test for equal variances (Levene's test)
levene_stat, levene_p = levene(df_old['response_time'], df_new['response_time'])

# Perform Welch's t-test (equal_var=False)
t_stat_welch, p_value_welch = ttest_ind(df_old['response_time'], df_new['response_time'], 
                                         equal_var=False)

# For comparison: standard t-test (equal_var=True)
t_stat_standard, p_value_standard = ttest_ind(df_old['response_time'], df_new['response_time'], 
                                               equal_var=True)

print("=" * 70)
print("WELCH'S T-TEST RESULTS (Unequal Variances)")
print("=" * 70)

print(f"\nOld version:")
print(f"  Mean:     {df_old['response_time'].mean():.2f} ms")
print(f"  Std:      {df_old['response_time'].std():.2f} ms")
print(f"  Variance: {df_old['response_time'].var():.2f}")
print(f"  N:        {len(df_old)}")

print(f"\nNew version:")
print(f"  Mean:     {df_new['response_time'].mean():.2f} ms")
print(f"  Std:      {df_new['response_time'].std():.2f} ms")
print(f"  Variance: {df_new['response_time'].var():.2f}")
print(f"  N:        {len(df_new)}")

print(f"\nLevene's test for equal variances:")
print(f"  Statistic: {levene_stat:.4f}")
print(f"  p-value:   {levene_p:.4f}")
print(f"  Result:    {'Variances are DIFFERENT' if levene_p < 0.05 else 'Variances are similar'}")
print(f"  → Welch's test is {'RECOMMENDED' if levene_p < 0.05 else 'not strictly necessary'}")

print(f"\n{'─' * 70}")
print("WELCH'S T-TEST (equal_var=False):")
print(f"  t-statistic: {t_stat_welch:.4f}")
print(f"  p-value:     {p_value_welch:.4f}")
print(f"  Result:      {'New version significantly faster ✓' if p_value_welch < 0.05 else 'No significant difference'}")

print(f"\nStandard t-test (equal_var=True) for comparison:")
print(f"  t-statistic: {t_stat_standard:.4f}")
print(f"  p-value:     {p_value_standard:.4f}")
print(f"  Result:      {'Significant difference' if p_value_standard < 0.05 else 'No significant difference'}")

print("\n" + "=" * 70)

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Histogram comparison (left)
ax1 = axes[0]
ax1.hist(df_old['response_time'], bins=25, alpha=0.6, label='Old version', 
         color='red', edgecolor='black')
ax1.hist(df_new['response_time'], bins=25, alpha=0.6, label='New version', 
         color='green', edgecolor='black')
ax1.axvline(df_old['response_time'].mean(), color='darkred', linestyle='--', 
            linewidth=2, label=f'Old mean: {df_old["response_time"].mean():.1f}ms')
ax1.axvline(df_new['response_time'].mean(), color='darkgreen', linestyle='--', 
            linewidth=2, label=f'New mean: {df_new["response_time"].mean():.1f}ms')
ax1.set_xlabel('Response Time (ms)', fontsize=10)
ax1.set_ylabel('Frequency', fontsize=10)
ax1.set_title('Response Time Distribution', fontsize=11, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# 2. Welch's t-distribution with observed difference (right)
from scipy.stats import t as t_dist

# Calculate Welch-Satterthwaite degrees of freedom
var1, var2 = df_old['response_time'].var(ddof=1), df_new['response_time'].var(ddof=1)
n1, n2 = len(df_old), len(df_new)
df_welch = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))

# Generate t-distribution
t_values = np.linspace(-5, 5, 500)
t_density = t_dist.pdf(t_values, df_welch)

ax2 = axes[1]
ax2.plot(t_values, t_density, 'b-', linewidth=2, label="Welch's t-distribution")
ax2.fill_between(t_values, t_density, alpha=0.3)

# Mark the observed t-statistic
ax2.axvline(t_stat_welch, color='red', linestyle='--', linewidth=2.5, 
            label=f'Observed t-stat: {t_stat_welch:.2f}')

# Mark critical values for α=0.05 (two-tailed)
t_critical = t_dist.ppf(0.975, df_welch)
ax2.axvline(t_critical, color='orange', linestyle=':', linewidth=2, alpha=0.7,
            label=f'Critical value: ±{t_critical:.2f}')
ax2.axvline(-t_critical, color='orange', linestyle=':', linewidth=2, alpha=0.7)

# Shade rejection regions
rejection_left = t_values[t_values <= -t_critical]
rejection_right = t_values[t_values >= t_critical]
ax2.fill_between(rejection_left, t_dist.pdf(rejection_left, df_welch), 
                  alpha=0.3, color='red', label='Rejection region (α=0.05)')
ax2.fill_between(rejection_right, t_dist.pdf(rejection_right, df_welch), 
                  alpha=0.3, color='red')

ax2.set_xlabel('t-value', fontsize=10)
ax2.set_ylabel('Probability Density', fontsize=10)
ax2.set_title("Welch's t-Distribution", fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# Add p-value annotation
result_text = f"p-value = {p_value_welch:.4f}\n{'✓ Significant (reject H₀)' if p_value_welch < 0.05 else '✗ Not significant'}"
ax2.text(0.05, 0.95, result_text, transform=ax2.transAxes, 
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('docs/img/welch_test_results.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'docs/img/welch_test_results.png'")
plt.show()
