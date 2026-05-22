
from transformers import TrOCRProcessor
from transformers import VisionEncoderDecoderModel

MODEL_NAME = "microsoft/trocr-base-handwritten"

processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)

print("Model loaded successfully.")

print("Next steps:")
print("- Add real CATMuS dataset")
print("- Build DataLoader")
print("- Fine-tune model")
print("- Save checkpoints")
