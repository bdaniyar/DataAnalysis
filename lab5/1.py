import pandas as pd
import numpy as np

np.random.seed(42)
n = 10000

# Random assignment to groups (50/50)
group = np.random.choice(['A', 'B'], size=n, p=[0.5, 0.5])

# Base conversion rates
conv_rate_A = 0.05
conv_rate_B = 0.065   # +1.5% absolute
converted = np.where(group == 'A', 
                     np.random.binomial(1, conv_rate_A, n),
                     np.random.binomial(1, conv_rate_B, n))

# Time on site (seconds)
time_A = np.random.normal(120, 30, n)        # mean 120, sd 30
time_B = np.random.normal(130, 35, n)        # mean 130, sd 35
time_on_site = np.where(group == 'A', time_A, time_B)
time_on_site = np.clip(time_on_site, 0, None)  # no negative times

# Pages viewed
pages_A = np.random.poisson(4, n)             # mean 4
pages_B = np.random.poisson(4.3, n)           # mean 4.3
pages_viewed = np.where(group == 'A', pages_A, pages_B)

# Create DataFrame
df = pd.DataFrame({
    'visitor_id': range(1, n+1),
    'group': group,
    'converted': converted,
    'time_on_site': np.round(time_on_site, 1),
    'pages_viewed': pages_viewed
})

# Save to CSV
df.to_csv('ab_test_data.csv', index=False)
print("Dataset saved as 'ab_test_data.csv'")

