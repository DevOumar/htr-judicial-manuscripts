
import random
import numpy as np

def bootstrap_metric(values, n=1000):
    scores = []

    for _ in range(n):
        sample = [random.choice(values) for _ in values]
        scores.append(np.mean(sample))

    lower = np.percentile(scores, 2.5)
    upper = np.percentile(scores, 97.5)

    return lower, upper

if __name__ == "__main__":
    values = [0.1, 0.2, 0.15, 0.12]
    print(bootstrap_metric(values))
