
import cv2
from pathlib import Path
from skimage.filters import threshold_sauvola
from jdeskew.estimator import get_angle
from jdeskew.utility import rotate

INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def preprocess_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    angle = get_angle(image)
    image = rotate(image, angle)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    image = clahe.apply(image)

    image = cv2.medianBlur(image, 3)

    thresh = threshold_sauvola(image, window_size=25)
    binary = (image > thresh).astype("uint8") * 255

    out = OUTPUT_DIR / path.name
    cv2.imwrite(str(out), binary)

    print(f"Processed {path.name}")

if __name__ == "__main__":
    for p in INPUT_DIR.glob("*.png"):
        preprocess_image(p)
