"""
Script to generate the binomial distribution histogram explained in the article.
Visualizes the probability distribution of getting k heads in 20 coin flips.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

# Parameters
n_flips = 20
p_heads = 0.5

# Generate all possible outcomes (0 to 20 heads)
k_values = np.arange(0, n_flips + 1)

# Calculate probabilities for each outcome
probabilities = binom.pmf(k_values, n_flips, p_heads)

# Create the histogram
plt.figure(figsize=(12, 7))
plt.bar(k_values, probabilities, color='steelblue', alpha=0.7, edgecolor='black')

# Highlight the most probable value (10 heads)
plt.bar(10, probabilities[10], color='darkgreen', alpha=0.8, edgecolor='black', 
        label=f'Most probable: 10 heads ({probabilities[10]*100:.1f}%)')

# Highlight the example from the article (13 heads)
plt.bar(13, probabilities[13], color='orange', alpha=0.8, edgecolor='black',
        label=f'Example: 13 heads ({probabilities[13]*100:.1f}%)')

# Highlight rejection region (15+ heads for α=5%)
rejection_region = k_values >= 15
plt.bar(k_values[rejection_region], probabilities[rejection_region], 
        color='red', alpha=0.6, edgecolor='black', label='Rejection region (α=5%)')

# Labels and formatting
plt.xlabel('Number of Heads', fontsize=12)
plt.ylabel('Probability', fontsize=12)
plt.title('Binomial Distribution: 20 Coin Flips with Fair Coin (p=0.5)', fontsize=14, fontweight='bold', pad=20)
plt.xticks(k_values)
plt.ylim(0, max(probabilities) * 1.15)  # Extend y-axis to make room for labels
plt.grid(True, alpha=0.3, axis='y')
plt.legend(fontsize=10)

# Add annotation for key probabilities
plt.text(10, probabilities[10] + 0.008, f'{probabilities[10]*100:.1f}%', 
         ha='center', fontsize=9, fontweight='bold')
plt.text(13, probabilities[13] + 0.008, f'{probabilities[13]*100:.1f}%', 
         ha='center', fontsize=9, fontweight='bold')

# Calculate cumulative probability for 13 or more heads
cumulative_13_plus = 1 - binom.cdf(12, n_flips, p_heads)
cumulative_15_plus = 1 - binom.cdf(14, n_flips, p_heads)

print(f"Probability of getting exactly 10 heads: {probabilities[10]*100:.2f}%")
print(f"Probability of getting exactly 13 heads: {probabilities[13]*100:.2f}%")
print(f"Probability of getting 13 or more heads: {cumulative_13_plus*100:.2f}%")
print(f"Probability of getting 15 or more heads: {cumulative_15_plus*100:.2f}% (rejection region)")

# Save the figure
plt.tight_layout()
plt.savefig('docs/img/binomial.png', dpi=300, bbox_inches='tight')
print("\nFigure saved as 'docs/img/binomial.png'")
plt.show()
