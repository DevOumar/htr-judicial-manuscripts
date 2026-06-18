# Preprocessing Pipeline

## Existing Implementation

The preprocessing pipeline already exists in `src/preprocessing/preprocess.py`.

It implements the MD5 image preprocessing requirements:

| Requirement | Status | Location |
| --- | --- | --- |
| Deskew / inclination correction | Present | `preprocess_image()` using `jdeskew.get_angle()` and `rotate()` |
| CLAHE | Present | `cv2.createCLAHE()` |
| Sauvola adaptive binarization | Present | `skimage.filters.threshold_sauvola()` |
| Reproducible parameters | Added/enforced | `config.yaml`, section `preprocessing` |

## Parameters

```yaml
preprocessing:
  deskew: true
  clahe_clip_limit: 2.0
  clahe_tile_grid_size: [8, 8]
  median_blur_kernel: 3
  sauvola_window_size: 25
```

## Algorithmic Steps

1. Read the input image in grayscale.
2. Estimate skew angle with `jdeskew`.
3. Rotate the image to correct inclination.
4. Apply CLAHE to improve local contrast.
5. Apply median blur to reduce isolated noise.
6. Compute a Sauvola local threshold.
7. Export a binary image to `data/processed/`.

## Scientific Justification

Deskew improves line segmentation by aligning text baselines. CLAHE is appropriate for historical manuscripts because illumination and ink contrast vary locally across the page. Sauvola binarization is a standard adaptive thresholding method for document images where a global threshold would fail due to paper aging, stains, shadows, or heterogeneous ink density.

## Usage

```bash
python src/preprocessing/preprocess.py --config config.yaml --input-dir data/raw --output-dir data/processed
```

## Before / After Examples

The repository contains sample raw and processed images when local sample data is present:

- Before: `data/raw/sample_1.png`
- After: `data/processed/sample_1.png`

For the judicial demo, preprocessing is intentionally conservative: the segmentation pipeline resizes full pages for Kraken, while this standalone module documents and validates the required MD5 image-processing chain.
