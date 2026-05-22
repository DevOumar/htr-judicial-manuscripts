
import json
from pathlib import Path
from datasets import Dataset

def load_local_dataset():
    gt_path = Path("data/sample_ground_truth/ground_truth.json")

    with open(gt_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Dataset.from_list(data)

if __name__ == "__main__":
    ds = load_local_dataset()
    print(ds)
