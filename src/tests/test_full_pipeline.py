import json
from pathlib import Path
from xml.etree import ElementTree as ET


PAGE_NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"}


def test_judicial_demo_artifacts_are_complete() -> None:
    report_path = Path("outputs/judicial_demo/demo_report.json")
    assert report_path.exists(), "Run python src/demo/judicial_pipeline.py --config config.yaml first."

    report = json.load(report_path.open("r", encoding="utf-8"))
    assert report["num_pages"] >= 1
    assert report["total_lines"] > 0
    assert report["total_transcribed_lines"] == report["total_lines"]

    for page in report["pages"]:
        pipeline = page["pipeline"]
        required_keys = [
            "original",
            "segmentation_input",
            "annotated",
            "polygons",
            "page_xml",
            "transcriptions",
            "full_page_transcription",
            "report",
        ]
        for key in required_keys:
            assert Path(pipeline[key]).exists(), f"Missing {key}: {pipeline[key]}"

        lines_dir = Path(pipeline["output_dir"]) / "lines"
        line_crops = sorted(lines_dir.glob("*.png"))
        assert len(line_crops) == pipeline["num_lines"]

        lines = json.load(Path(pipeline["transcriptions"]).open("r", encoding="utf-8"))
        assert len(lines) == pipeline["num_lines"]
        assert sum(1 for line in lines if line.get("prediction")) == pipeline["num_transcribed_lines"]

        full_text = Path(pipeline["full_page_transcription"]).read_text(encoding="utf-8")
        assert len(full_text.splitlines()) == pipeline["num_lines"]

        tree = ET.parse(pipeline["page_xml"])
        text_lines = tree.findall(".//p:TextLine", PAGE_NS)
        unicode_nodes = tree.findall(".//p:TextEquiv/p:Unicode", PAGE_NS)
        assert len(text_lines) == pipeline["num_lines"]
        assert len(unicode_nodes) == pipeline["num_lines"]

        for text_line in text_lines:
            assert text_line.find("p:Coords", PAGE_NS) is not None
            assert text_line.find("p:Baseline", PAGE_NS) is not None
            unicode_node = text_line.find("p:TextEquiv/p:Unicode", PAGE_NS)
            assert unicode_node is not None
            assert unicode_node.text is not None
