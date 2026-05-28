from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from embedding_sps.manifest import build_and_write_manifest, build_manifest_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text_json(root: Path, relative_path: str) -> None:
    path = root / Path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"paper_id": path.stem, "pages": [{"page_index": 0, "text": "SPS text"}]}),
        encoding="utf-8",
    )


def make_sps_root(tmp_path: Path) -> Path:
    sps_root = tmp_path / "sps-review"
    ref_dir = sps_root / "data" / "references"

    write_text_json(sps_root, "data/extraction_json/text/1.json")
    write_text_json(sps_root, "data/extraction_json/text_proceedings_ready/2.json")
    write_text_json(sps_root, "data/extraction_json/text_case_series_split/3.json")

    write_csv(
        ref_dir / "paper_artifact_registry.csv",
        [
            {
                "paper_id": "1",
                "covidence_id": "1",
                "title": "Single case",
                "pdf_present": "true",
                "text_json_present": "true",
                "text_json_path": "data/extraction_json/text/1.json",
                "source_category": "single_case_report",
                "source_likely_sps_case_count": "1",
            },
            {
                "paper_id": "2",
                "covidence_id": "2",
                "title": "Proceedings",
                "pdf_present": "true",
                "text_json_present": "true",
                "text_json_path": "data/extraction_json/text/2.json",
                "text_proceedings_ready_present": "true",
                "text_proceedings_ready_path": "data/extraction_json/text_proceedings_ready/2.json",
                "source_category": "conference_abstract",
            },
            {
                "paper_id": "3",
                "covidence_id": "3",
                "title": "Case series",
                "pdf_present": "true",
                "text_json_present": "true",
                "text_json_path": "data/extraction_json/text/3.json",
                "source_category": "case_series_or_multi_case",
            },
            {
                "paper_id": "4",
                "covidence_id": "4",
                "title": "Missing PDF",
                "pdf_present": "false",
                "text_json_present": "false",
                "source_category": "single_case_report",
            },
            {
                "paper_id": "5",
                "covidence_id": "5",
                "title": "Wrong source",
                "pdf_present": "true",
                "text_json_present": "true",
                "text_json_path": "data/extraction_json/text/5.json",
                "source_category": "single_case_report",
            },
        ],
    )
    write_csv(
        ref_dir / "source_categorisation_registry.csv",
        [
            {
                "paper_id": "1",
                "source_category": "single_case_report",
                "preferred_langextract_mode": "individual",
                "langextract_eligible": "true",
            },
            {
                "paper_id": "2",
                "source_category": "conference_abstract",
                "preferred_langextract_mode": "individual",
                "langextract_eligible": "true",
            },
            {
                "paper_id": "3",
                "source_category": "case_series_or_multi_case",
                "preferred_langextract_mode": "individual_case_split",
                "langextract_eligible": "true",
            },
        ],
    )
    write_csv(
        ref_dir / "source_sps_case_count_registry.csv",
        [
            {
                "paper_id": "1",
                "source_category": "single_case_report",
                "count_eligible": "true",
                "likely_sps_case_count": "1",
            },
            {
                "paper_id": "2",
                "source_category": "conference_abstract",
                "count_eligible": "true",
                "count_manual_review_required": "true",
            },
            {
                "paper_id": "3",
                "source_category": "case_series_or_multi_case",
                "count_eligible": "true",
                "likely_sps_case_count": "2",
            },
        ],
    )
    write_csv(
        ref_dir / "case_series_split_registry.csv",
        [
            {
                "paper_id": "3",
                "split_status": "split_auto",
                "split_text_json_path": "data/extraction_json/text_case_series_split/3.json",
                "case_count": "2",
                "manual_review_required": "false",
            }
        ],
    )
    write_csv(
        ref_dir / "paper_revisit_registry.csv",
        [
            {
                "paper_id": "5",
                "stage": "02_source_linkage",
                "issue_type": "source_alignment_failed",
                "severity": "high",
                "blocking_downstream": "true",
            }
        ],
    )
    return sps_root


def test_build_manifest_prefers_split_and_proceedings_text(tmp_path: Path) -> None:
    rows = build_manifest_rows(make_sps_root(tmp_path))
    by_id = {row["paper_id"]: row for row in rows}

    assert by_id["1"]["preferred_text_source"] == "text_json"
    assert by_id["1"]["source_langextract_mode"] == "individual"
    assert by_id["2"]["preferred_text_source"] == "proceedings_ready"
    assert by_id["3"]["preferred_text_source"] == "case_series_split_auto"
    assert by_id["3"]["case_series_split_case_count"] == "2"


def test_build_manifest_marks_ineligible_rows(tmp_path: Path) -> None:
    rows = build_manifest_rows(make_sps_root(tmp_path))
    by_id = {row["paper_id"]: row for row in rows}

    assert by_id["4"]["embedding_eligible"] == "false"
    assert by_id["4"]["skip_reason"] == "missing_pdf"
    assert by_id["5"]["embedding_eligible"] == "false"
    assert by_id["5"]["skip_reason"] == "source_linkage_issue"


def test_build_and_write_manifest_outputs_full_and_pilot_files(tmp_path: Path) -> None:
    sps_root = make_sps_root(tmp_path)
    out_dir = tmp_path / "out"
    results_dir = tmp_path / "results"

    summary = build_and_write_manifest(sps_root, out_dir, results_dir, pilot_size=2)

    assert summary["total_rows"] == 5
    assert summary["eligible_rows"] == 3
    assert summary["pilot_rows"] == 2
    assert (out_dir / "full.csv").exists()
    assert (out_dir / "full.jsonl").exists()
    assert (out_dir / "pilot_2.csv").exists()
    assert (out_dir / "pilot_2.jsonl").exists()
    assert (results_dir / "summary.json").exists()
    assert (results_dir / "summary.md").exists()
