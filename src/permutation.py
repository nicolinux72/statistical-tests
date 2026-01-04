"""
Permutation test for comparing two web service versions.
More robust when independence assumptions are difficult to guarantee.
Uses block sampling (time windows) to achieve exchangeability.
"""

import numpy as np
import pandas as pd
from scipy.stats import permutation_test
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Simulate response times with temporal correlation (blocks/windows)
def generate_correlated_response_times(base_mean, base_std, n_windows=30, window_size=10):
    """
    Generate response times grouped in time windows with internal correlation.
    Each window has slightly different characteristics (simulating system state).
    """
    all_times = []
    window_ids = []
    
    for window_id in range(n_windows):
        # Each window has its own mean (simulating varying system load)
        window_mean = np.random.normal(base_mean, base_std * 0.3)
        window_std = base_std * 0.5
        
        # Generate correlated times within the window
        times = np.random.normal(window_mean, window_std, window_size)
        times = np.abs(times)  # Ensure positive values
        
        all_times.extend(times)
        window_ids.extend([window_id] * window_size)
    
    return np.array(all_times), np.array(window_ids)

# Generate data for both versions
old_times, old_windows = generate_correlated_response_times(base_mean=150, base_std=30, 
                                                             n_windows=30, window_size=10)
new_times, new_windows = generate_correlated_response_times(base_mean=140, base_std=28, 
                                                             n_windows=30, window_size=10)

# Create DataFrames
df_old = pd.DataFrame({
    'response_time': old_times,
    'window_id': old_windows
})

df_new = pd.DataFrame({
    'response_time': new_times,
    'window_id': new_windows
})

# Calculate block means (one mean per time window)
old_blocks = df_old.groupby('window_id')['response_time'].mean().values
new_blocks = df_new.groupby('window_id')['response_time'].mean().values

# Define statistic function for permutation test
def statistic(x, y):
    """Difference of means"""
    return np.mean(x) - np.mean(y)

# Perform permutation test
result = permutation_test((old_blocks, new_blocks), statistic, 
                         permutation_type='independent', n_resamples=10000,
                         random_state=42)

# Calculate observed difference
observed_diff = np.mean(old_blocks) - np.mean(new_blocks)

print("=" * 70)
print("PERMUTATION TEST RESULTS (Block Sampling)")
print("=" * 70)

print(f"\nOld version:")
print(f"  Overall mean:     {df_old['response_time'].mean():.2f} ms")
print(f"  Overall std:      {df_old['response_time'].std():.2f} ms")
print(f"  Number of blocks: {len(old_blocks)}")
print(f"  Observations:     {len(df_old)}")

print(f"\nNew version:")
print(f"  Overall mean:     {df_new['response_time'].mean():.2f} ms")
print(f"  Overall std:      {df_new['response_time'].std():.2f} ms")
print(f"  Number of blocks: {len(new_blocks)}")
print(f"  Observations:     {len(df_new)}")

print(f"\nBlock-level analysis:")
print(f"  Old blocks mean:  {np.mean(old_blocks):.2f} ms")
print(f"  New blocks mean:  {np.mean(new_blocks):.2f} ms")
print(f"  Observed diff:    {observed_diff:.2f} ms")

print(f"\nPermutation test results:")
print(f"  Statistic:        {result.statistic:.4f}")
print(f"  p-value:          {result.pvalue:.4f}")
print(f"  Null dist mean:   {result.null_distribution.mean():.4f}")
print(f"  Null dist std:    {result.null_distribution.std():.4f}")
print(f"  Resamples:        {len(result.null_distribution)}")
print(f"\n  Result: {'Significant difference ✓' if result.pvalue < 0.05 else 'No significant difference'}")
print(f"  (using α=0.05 significance level)")

print("\n" + "=" * 70)

# Visualization
fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# 1. Time series of block means
ax1 = fig.add_subplot(gs[0, :])
window_indices = np.arange(len(old_blocks))
ax1.plot(window_indices, old_blocks, 'o-', color='red', alpha=0.6, 
         label='Old version', linewidth=2, markersize=6)
ax1.plot(window_indices, new_blocks, 's-', color='green', alpha=0.6, 
         label='New version', linewidth=2, markersize=6)
ax1.axhline(np.mean(old_blocks), color='darkred', linestyle='--', linewidth=1.5,
            label=f'Old mean: {np.mean(old_blocks):.1f}ms')
ax1.axhline(np.mean(new_blocks), color='darkgreen', linestyle='--', linewidth=1.5,
            label=f'New mean: {np.mean(new_blocks):.1f}ms')
ax1.set_xlabel('Time Window (Block ID)', fontsize=11)
ax1.set_ylabel('Mean Response Time (ms)', fontsize=11)
ax1.set_title('Block Means Over Time', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Histogram of block means
ax2 = fig.add_subplot(gs[1, 0])
ax2.hist(old_blocks, bins=15, alpha=0.6, label='Old blocks', 
         color='red', edgecolor='black')
ax2.hist(new_blocks, bins=15, alpha=0.6, label='New blocks', 
         color='green', edgecolor='black')
ax2.set_xlabel('Mean Response Time (ms)', fontsize=10)
ax2.set_ylabel('Frequency', fontsize=10)
ax2.set_title('Distribution of Block Means', fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# 3. Box plot of blocks
ax3 = fig.add_subplot(gs[1, 1])
data_to_plot = [old_blocks, new_blocks]
bp = ax3.boxplot(data_to_plot, labels=['Old', 'New'], patch_artist=True,
                  showmeans=True, meanline=True)
bp['boxes'][0].set_facecolor('lightcoral')
bp['boxes'][1].set_facecolor('lightgreen')
ax3.set_ylabel('Mean Response Time (ms)', fontsize=10)
ax3.set_title('Block Means Comparison', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 4. Permutation null distribution
ax4 = fig.add_subplot(gs[2, :])
ax4.hist(result.null_distribution, bins=50, color='skyblue', alpha=0.7, 
         edgecolor='black', label='Null distribution')
ax4.axvline(observed_diff, color='red', linestyle='--', linewidth=3,
            label=f'Observed difference: {observed_diff:.2f}ms')
ax4.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)

# Mark the rejection region
alpha = 0.05
percentile_lower = np.percentile(result.null_distribution, alpha/2 * 100)
percentile_upper = np.percentile(result.null_distribution, (1 - alpha/2) * 100)
ax4.axvline(percentile_lower, color='orange', linestyle=':', linewidth=2, alpha=0.7)
ax4.axvline(percentile_upper, color='orange', linestyle=':', linewidth=2, alpha=0.7,
            label=f'Critical values (α={alpha})')

ax4.set_xlabel('Difference in Means (ms)', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('Permutation Test: Null Distribution', fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# Add text annotation
p_text = f"p-value = {result.pvalue:.4f}\n{'✓ Significant' if result.pvalue < 0.05 else '✗ Not significant'}"
ax4.text(0.02, 0.98, p_text, transform=ax4.transAxes, fontsize=11,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.savefig('docs/img/permutation_test_results.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'docs/img/permutation_test_results.png'")
plt.show()
