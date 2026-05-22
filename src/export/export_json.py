
import json
from pathlib import Path

data = {
    "id": "page_001",
    "transcription": "registre judiciaire",
    "confidence": 0.93,
    "needs_review": False,
    "polygon": [[10,10],[100,10],[100,50],[10,50]]
}

Path("dataset_nlp").mkdir(exist_ok=True)

with open("dataset_nlp/output.json","w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)

print("Export generated.")
