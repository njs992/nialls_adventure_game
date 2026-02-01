import numpy as np

# Generate 300 numbers from a normal distribution
# with mean=32 and standard deviation=6
age_distribution = np.random.normal(loc=45, scale=15, size=3000)

print(f"Mean: {np.mean(age_distribution):.2f}")
print(f"Std Dev: {np.std(age_distribution):.2f}")
print(f"Sample: {sorted(age_distribution[:3000])}")