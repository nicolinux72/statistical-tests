# Is the New Web Service Really Faster?

When load testing a new version of a web service, we often compare the average response times with those of the previous version. However, relying solely on averages can be misleading, as it doesn't account for the role of chance in the results.

For example, if we repeat the tests and collect new data samples, we'll get different averages each time. This means that the observed difference between the two services could depend on both actual speed and simple sampling luck.

To make a rational judgment, we need a minimum of statistics.


## Statistical Tests (Very Briefly)
A statistical test serves to verify a hypothesis (called the null hypothesis) using collected data. For example, if we flip a coin, the null hypothesis is that it's balanced (50% heads, 50% tails). The test tells us how likely it is to obtain the observed results if this hypothesis were true, aiming to refute the null hypothesis when this probability is very low.

![binomial](binomiale.png)
 
For a balanced coin, 20 flips follow a binomial distribution Bin(20;0.5) represented in the graph. The most likely value is 10 heads (17.6%), while extreme outcomes like 0 or 20 heads have almost zero probability (0.0001%).

The reasoning is as follows: if we get 13 heads in 20 flips, we calculate the probability of getting 13 or more heads assuming the null hypothesis is true. In our case it's 13.16%, so not particularly unlikely.

To decide when to reject the null hypothesis, we set a significance threshold α (typically 5%). If the probability p of the observed result is less than α, we reject the null hypothesis. In our example with α=5%, we would reject the balanced coin hypothesis only with 15 or more heads (probability 2.07%).

## T-test
Returning to our web service, we need to perform a test whose null hypothesis is that the average response of the online version is slower than the new one and discover if we can refute it.

To proceed as in the previous example, we need the distribution of the statistic used by the test, namely the difference of the means of the two service versions. Under some hypotheses we'll discuss shortly, the distribution we need is Student's t, formally the ratio between a normal distribution and the square root of a chi-square, both normalized.

```python
from scipy.stats import ttest_ind

# df_old and df_new are pandas DataFrames with 'response_time' column
t_stat, p_value = ttest_ind(df_old['response_time'], df_new['response_time'])
print(f"p-value: {p_value:.4f} - {'Significant difference' if p_value < 0.05 else 'No difference'}")
```

## Necessary Conditions for a T-test
Let's return to the assumptions that allow us to use the t-test:
•	__Independence__ the samples must be independent of each other as well as the observations within individual samples.
•	__Normality__ the probability distributions must be normal
•	__Homoscedasticity__ the two populations must have the same variance.
For our web services we can perform the sampling 

### Independence
Response times of a web service are rarely independent observations: the system state (pods, cache, network, ...) is shared between successive calls, creating correlation. Moreover, making N consecutive calls in a short interval, which is the most common sampling method, introduces artificial autocorrelation: a slow call is more likely to be followed by another equally slow one.

To mitigate dependencies related to system state, requests should be made under comparable conditions regarding system load, pod startup, cache, and failover. Also isolate the pods or VMs involved in sampling or, if not possible, balance requests across different backends in a completely random manner.

Regarding correlations induced by the sampling method, instead of using the entire sequence of calls made in a continuous time interval, one could use one request every k or select them randomly (subsampling). Alternatively or additionally, make several calls in different time windows and calculate aggregate values in these windows, treating them as sampling units.

### Normality
Response times of web services rarely follow a normal distribution: typically they have heavier right tails due to outliers with very long times. Fortunately, the central limit theorem comes to our aid.

The theorem guarantees that sample means tend to be normally distributed regardless of the original data distribution, provided the sample is sufficiently large. In practice, even if individual response times are not normal, as long as each sample contains at least 30 observations, their mean will be approximately normally distributed. This makes the t-test valid even starting from non-normal distributions.

If you want to verify the normality of sample means, you can use a Q-Q plot or the Shapiro-Wilk test, but with adequately sized samples, the central limit theorem is generally sufficient to justify using the t-test.

### Homoscedasticity
Homoscedasticity, or equality of variances between the two samples, is often problematic in web service comparisons. Different versions of a service can have different variances, violating this assumption of the standard t-test. To solve the problem, we resort to Welch's test, a variant of the t-test that doesn't assume equal variances and which we'll describe in the next section.

## Welch's Test
Welch's test is a variant of Student's t-test that relaxes the homoscedasticity assumption, allowing the two samples to have different variances. This makes it particularly suitable for comparing web services, where response time variances can differ significantly between versions or different configurations.

Unlike the standard t-test, Welch's test calculates degrees of freedom using the Welch-Satterthwaite approximation, which accounts for the variances and sample sizes. The test still requires that samples be independent and that sample means be approximately normal, a condition guaranteed by the central limit theorem with sufficiently large samples (n ≥ 30).

In Python, Welch's test is easily implemented using scipy by specifying the `equal_var=False` parameter:

```python
from scipy.stats import ttest_ind

# df_old and df_new are pandas DataFrames with 'response_time' column
t_stat, p_value = ttest_ind(df_old['response_time'], df_new['response_time'], equal_var=False)
print(f"p-value: {p_value:.4f} - {'New version significantly faster' if p_value < 0.05 else 'No significant difference'}")
```

This approach is generally preferable to the standard t-test in real contexts, as it's more robust and doesn't significantly penalize test power when variances are actually equal.

## Permutation Test
As we've seen, obtaining perfectly independent samples is not simple in distributed systems, and in some cases even the normality assumption can be problematic despite the central limit theorem. The permutation test offers an interesting alternative because it requires a weaker assumption: exchangeability instead of independence.

Exchangeability means that the order of observations contains no relevant information: if the null hypothesis were true (no difference between the two services), randomly permuting the "old" and "new" labels among observations shouldn't change the data distribution. The test works by calculating the statistic of interest (for example, the difference of means) on the original data, then repeating the calculation on many random permutations of the labels. The p-value is the fraction of permutations that produce a more extreme statistic than the observed one.

To obtain exchangeability in web services, instead of sampling individual requests, we sample in blocks: for example, we collect response times in 5-minute time windows and consider the mean of each window as a sampling unit. This way, correlations internal to each block don't violate the exchangeability assumption between blocks.

```python
import numpy as np
from scipy.stats import permutation_test

# Means calculated on time windows (blocks)
old_blocks = df_old.groupby('window_id')['response_time'].mean().values
new_blocks = df_new.groupby('window_id')['response_time'].mean().values

def statistic(x, y):
    return np.mean(x) - np.mean(y)

result = permutation_test((old_blocks, new_blocks), statistic, 
                         permutation_type='independent', n_resamples=10000)
print(f"p-value: {result.pvalue:.4f} - {'Significant difference' if result.pvalue < 0.05 else 'No difference'}")
```

The permutation test is particularly robust because it makes no assumptions about the distribution shape and works well even with small samples, making it a reliable choice when conditions for the t-test are questionable.

## Extra: Bootstrap
The bootstrap technique can be useful for estimating statistical properties of a single service's response times, such as the mean or variance, and quantifying the uncertainty of these estimates. Unlike previous tests, bootstrap doesn't serve to compare two services but to understand how much we can trust our measurements on a single system.

Bootstrap works by resampling with replacement from the original sample: if we've collected n observations, we generate thousands of new samples by randomly drawing n values from the original sample (with possibility of repetitions). For each of these "bootstrap" samples we calculate the statistic of interest, thus obtaining an empirical distribution of that statistic. This distribution allows us to calculate the confidence interval, a range of values within which we expect the true population value to fall with a certain probability (typically 95%).

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Observed response times (in milliseconds)
response_times = df['response_time'].values
n_bootstrap = 10000

# Generate bootstrap samples and calculate means
bootstrap_means = []
for _ in range(n_bootstrap):
    sample = np.random.choice(response_times, size=len(response_times), replace=True)
    bootstrap_means.append(np.mean(sample))

bootstrap_means = np.array(bootstrap_means)

# Calculate 95% confidence interval
ci_lower = np.percentile(bootstrap_means, 2.5)
ci_upper = np.percentile(bootstrap_means, 97.5)
observed_mean = np.mean(response_times)

print(f"Observed mean: {observed_mean:.2f} ms")
print(f"95% confidence interval: [{ci_lower:.2f}, {ci_upper:.2f}] ms")

# Visualize bootstrap means distribution
plt.figure(figsize=(10, 6))
plt.hist(bootstrap_means, bins=50, density=True, alpha=0.7, edgecolor='black')
plt.axvline(observed_mean, color='red', linestyle='--', linewidth=2, label='Observed mean')
plt.axvline(ci_lower, color='green', linestyle='--', linewidth=2, label='95% CI')
plt.axvline(ci_upper, color='green', linestyle='--', linewidth=2)
plt.xlabel('Average response time (ms)')
plt.ylabel('Density')
plt.title('Bootstrap Distribution of Means')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

The graph shows how means calculated on bootstrap samples are distributed. The 95% confidence interval tells us that if we repeated sampling infinitely many times, in 95% of cases the true population mean would fall within that interval. This gives us a quantitative measure of uncertainty in our estimates, precious information when making data-based performance decisions.

## Conclusions
In many companies, load test results are used directly to compare performance between different service versions, simply based on the difference of observed means. However, this approach has significant limitations: not only does it ignore the role of chance in results, but it's often based on sampling that violates the independence assumptions necessary for correct statistical analysis.

We've shown how to apply a more rigorous approach using appropriate statistical tests. Welch's test represents a solid choice when reasonably independent samples can be obtained through careful sampling strategies, while the permutation test offers greater robustness when independence is difficult to guarantee. Both approaches allow quantifying the probability that an observed difference is due to chance rather than a real performance difference.

The code examples provided can be easily adapted to specific contexts, allowing the transformation of raw load test data into statistically founded evidence. Ultimately, dedicating attention to sampling design and statistical analysis of results is not just an academic exercise: it's what distinguishes a decision based on impressions from a data-driven decision.
