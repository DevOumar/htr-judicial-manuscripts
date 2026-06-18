# Segmentation Evaluation

## Status

Geometric IoU evaluation is implemented in:

- `src/evaluation/segmentation_iou.py`

Output:

- `outputs/segmentation_iou/segmentation_iou_report.json`

## Method

Predicted and reference polygons are rasterized as binary masks. IoU is computed as:

```text
IoU = area(intersection) / area(union)
```

## Available References

The judicial Gallica pages do not include ground-truth line polygons, so IoU cannot be computed directly on the final business corpus.

The script computes IoU only when a page output contains:

- `polygons.json`
- `ground_truth_objects.json`
- `segmentation_input.png`

This supports CATMuS segmentation validation when reference polygons are exposed in the loaded sample.

## Usage

```bash
python src/evaluation/segmentation_iou.py --input-dir outputs/segmentation
```

## Interpretation

If no comparable reference polygons are available, the report explicitly marks the page as `missing_reference` or `no_comparable_polygons`. This is a data limitation, not a pipeline failure.
