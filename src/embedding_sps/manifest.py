from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPS_ROOT = Path("C:/Projects/sps-review")
DEFAULT_INTERIM_DIR = REPO_ROOT / "data" / "interim" / "manifest"
DEFAULT_RESULTS_DIR = REPO_ROOT / "results" / "manifest"

REVISIT_SOURCE_LINKAGE_ISSUES = {
    "source_alignment_failed",
    "source_linkage_exclusion",
}

SEVERITY_RANK = {
    "": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "blocker": 4,
}

MANIFEST_FIELDS = [
    "paper_id",
    "covidence_id",
    "title",
    "authors",
    "published_year",
    "journal",
    "doi",
    "pdf_present",
    "pdf_paths_relative",
    "preferred_text_path",
    "preferred_text_source",
    "preferred_text_exists",
    "embedding_eligible",
    "skip_reason",
    "source_category",
    "source_subtype",
    "source_confidence",
    "source_route_source",
    "source_manual_override_present",
    "source_langextract_mode",
    "source_langextract_eligible",
    "source_case_series_split_candidate",
    "source_manual_review_required",
    "count_eligible",
    "likely_sps_case_count",
    "count_confidence",
    "count_basis",
    "count_manual_review_required",
    "count_reason",
    "case_series_split_status",
    "case_series_split_method",
    "case_series_split_case_count",
    "case_series_split_text_json_path",
    "case_series_split_manual_review_required",
    "revisit_issue_count",
    "revisit_highest_severity",
    "revisit_stages",
    "revisit_issue_types",
    "revisit_blocking_downstream",
    "text_n_pages",
    "text_needs_ocr",
    "text_ocr_applied",
    "text_quality_flags",
    "proceedings_ready_present",
    "proceedings_ready_source_kind",
    "pilot_selected",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local SPSD embedding manifests from sps-review registries."
    )
    parser.add_argument(
        "--sps-root",
        type=Path,
        default=DEFAULT_SPS_ROOT,
        help="Path to the upstream sps-review repository.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_INTERIM_DIR,
        help="Directory for manifest CSV/JSONL outputs.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory for manifest summary outputs.",
    )
    parser.add_argument(
        "--pilot-size",
        type=int,
        default=100,
        help="Number of eligible papers to include in the pilot manifest.",
    )
    return parser.parse_args(argv)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required registry not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def index_by_paper_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        paper_id = clean(row.get("paper_id"))
        if paper_id:
            indexed[paper_id] = row
    return indexed


def clean(value: Any) -> str:
    return str(value or "").strip()


def first_present(*values: Any) -> str:
    for value in values:
        text = clean(value)
        if text:
            return text
    return ""


def truthy(value: Any) -> bool:
    return clean(value).lower() in {"1", "true", "yes", "y"}


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def resolve_repo_path(sps_root: Path, path_text: str) -> Path | None:
    text = clean(path_text)
    if not text:
        return None
    path = Path(text.replace("\\", "/"))
    if path.is_absolute():
        return path
    return sps_root / path


def path_exists(sps_root: Path, path_text: str) -> bool:
    path = resolve_repo_path(sps_root, path_text)
    return bool(path and path.exists())


def paper_sort_key(row: dict[str, str]) -> tuple[int, str]:
    paper_id = clean(row.get("paper_id"))
    if paper_id.isdigit():
        return int(paper_id), paper_id
    return 10**12, paper_id


def highest_severity(severities: list[str]) -> str:
    ranked = sorted(
        (clean(value).lower() for value in severities),
        key=lambda value: SEVERITY_RANK.get(value, 0),
        reverse=True,
    )
    return ranked[0] if ranked else ""


def summarise_revisit_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        paper_id = clean(row.get("paper_id"))
        if paper_id:
            grouped[paper_id].append(row)

    summaries: dict[str, dict[str, str]] = {}
    for paper_id, paper_rows in grouped.items():
        stages = sorted({clean(row.get("stage")) for row in paper_rows if clean(row.get("stage"))})
        issue_types = sorted(
            {clean(row.get("issue_type")) for row in paper_rows if clean(row.get("issue_type"))}
        )
        blocking = any(truthy(row.get("blocking_downstream")) for row in paper_rows)
        summaries[paper_id] = {
            "revisit_issue_count": str(len(paper_rows)),
            "revisit_highest_severity": highest_severity(
                [clean(row.get("severity")) for row in paper_rows]
            ),
            "revisit_stages": ";".join(stages),
            "revisit_issue_types": ";".join(issue_types),
            "revisit_blocking_downstream": bool_text(blocking),
            "has_source_linkage_issue": bool_text(
                any(clean(row.get("issue_type")) in REVISIT_SOURCE_LINKAGE_ISSUES for row in paper_rows)
            ),
        }
    return summaries


def preferred_source_fields(
    artifact: dict[str, str],
    count_row: dict[str, str],
    source_row: dict[str, str],
) -> dict[str, str]:
    # Use resolved fields when present so manual source-routing overrides are
    # reflected in the manifest without carrying duplicate raw columns.
    return {
        "source_category": first_present(
            artifact.get("resolved_source_category"),
            count_row.get("source_category"),
            artifact.get("source_category"),
            source_row.get("source_category"),
        ),
        "source_subtype": first_present(
            artifact.get("resolved_source_subtype"),
            count_row.get("source_subtype"),
            artifact.get("source_subtype"),
            source_row.get("source_subtype"),
        ),
        "source_confidence": first_present(
            artifact.get("resolved_source_confidence"),
            artifact.get("source_classification_confidence"),
            source_row.get("classification_confidence"),
        ),
        "source_route_source": first_present(
            artifact.get("resolved_source_route_source"),
            "stage04_registry",
        ),
        "source_manual_override_present": first_present(
            artifact.get("source_manual_override_present"),
            "false",
        ),
        "source_langextract_mode": first_present(
            artifact.get("resolved_langextract_mode"),
            artifact.get("source_preferred_langextract_mode"),
            source_row.get("preferred_langextract_mode"),
        ),
        "source_langextract_eligible": first_present(
            artifact.get("resolved_langextract_eligible"),
            artifact.get("source_langextract_eligible"),
            source_row.get("langextract_eligible"),
        ),
        "source_case_series_split_candidate": first_present(
            artifact.get("resolved_case_series_split_candidate"),
            artifact.get("source_case_series_split_candidate"),
            source_row.get("case_series_split_candidate"),
        ),
        "source_manual_review_required": first_present(
            artifact.get("source_manual_review_required"),
            source_row.get("manual_review_required"),
            "false",
        ),
    }


def count_fields(artifact: dict[str, str], count_row: dict[str, str]) -> dict[str, str]:
    return {
        "count_eligible": first_present(count_row.get("count_eligible"), artifact.get("source_count_eligible")),
        "likely_sps_case_count": first_present(
            count_row.get("likely_sps_case_count"),
            artifact.get("source_likely_sps_case_count"),
        ),
        "count_confidence": first_present(
            count_row.get("count_confidence"),
            artifact.get("source_count_confidence"),
        ),
        "count_basis": first_present(count_row.get("count_basis"), artifact.get("source_count_basis")),
        "count_manual_review_required": first_present(
            count_row.get("count_manual_review_required"),
            artifact.get("source_count_manual_review_required"),
        ),
        "count_reason": first_present(count_row.get("count_reason"), artifact.get("source_count_reason")),
    }


def split_fields(artifact: dict[str, str], split_row: dict[str, str]) -> dict[str, str]:
    return {
        "case_series_split_status": first_present(
            split_row.get("split_status"),
            artifact.get("case_series_split_status"),
        ),
        "case_series_split_method": first_present(
            split_row.get("split_method"),
            artifact.get("case_series_split_method"),
        ),
        "case_series_split_case_count": first_present(
            split_row.get("case_count"),
            artifact.get("case_series_split_case_count"),
        ),
        "case_series_split_text_json_path": first_present(
            split_row.get("split_text_json_path"),
            artifact.get("case_series_split_text_json_path"),
        ),
        "case_series_split_manual_review_required": first_present(
            split_row.get("manual_review_required"),
            "false",
        ),
    }


def choose_preferred_text(
    sps_root: Path,
    artifact: dict[str, str],
    split_data: dict[str, str],
) -> tuple[str, str, bool]:
    split_path = split_data.get("case_series_split_text_json_path", "")
    if split_data.get("case_series_split_status") == "split_auto" and path_exists(sps_root, split_path):
        return split_path, "case_series_split_auto", True

    proceedings_path = clean(artifact.get("text_proceedings_ready_path"))
    if truthy(artifact.get("text_proceedings_ready_present")) and path_exists(sps_root, proceedings_path):
        return proceedings_path, "proceedings_ready", True

    text_path = clean(artifact.get("text_json_path"))
    if truthy(artifact.get("text_json_present")) and path_exists(sps_root, text_path):
        return text_path, "text_json", True

    candidate = first_present(split_path, proceedings_path, text_path)
    return candidate, "", False


def skip_reason_for(
    artifact: dict[str, str],
    source_data: dict[str, str],
    revisit_data: dict[str, str],
    preferred_text_path: str,
    preferred_text_exists: bool,
) -> str:
    if truthy(revisit_data.get("has_source_linkage_issue")):
        return "source_linkage_issue"
    if clean(source_data.get("source_langextract_mode")) == "incorrect_reference":
        return "incorrect_reference"
    if not truthy(artifact.get("pdf_present")):
        return "missing_pdf"
    if not preferred_text_path:
        return "missing_text"
    if not preferred_text_exists:
        return "preferred_text_missing"
    return ""


def build_manifest_rows(sps_root: Path) -> list[dict[str, str]]:
    ref_dir = sps_root / "data" / "references"
    artifacts = read_csv(ref_dir / "paper_artifact_registry.csv")
    sources = index_by_paper_id(read_csv(ref_dir / "source_categorisation_registry.csv"))
    counts = index_by_paper_id(read_csv(ref_dir / "source_sps_case_count_registry.csv"))
    splits = index_by_paper_id(read_csv(ref_dir / "case_series_split_registry.csv"))
    revisits = summarise_revisit_rows(read_csv(ref_dir / "paper_revisit_registry.csv"))

    manifest: list[dict[str, str]] = []
    for artifact in sorted(artifacts, key=paper_sort_key):
        paper_id = clean(artifact.get("paper_id"))
        source_row = sources.get(paper_id, {})
        count_row = counts.get(paper_id, {})
        split_data = split_fields(artifact, splits.get(paper_id, {}))
        source_data = preferred_source_fields(artifact, count_row, source_row)
        revisit_data = revisits.get(paper_id, {})
        preferred_text_path, preferred_text_source, preferred_text_exists = choose_preferred_text(
            sps_root,
            artifact,
            split_data,
        )
        skip_reason = skip_reason_for(
            artifact,
            source_data,
            revisit_data,
            preferred_text_path,
            preferred_text_exists,
        )

        row = {
            "paper_id": paper_id,
            "covidence_id": first_present(artifact.get("covidence_id"), paper_id),
            "title": clean(artifact.get("title")),
            "authors": clean(artifact.get("authors")),
            "published_year": clean(artifact.get("published_year")),
            "journal": clean(artifact.get("journal")),
            "doi": clean(artifact.get("doi")),
            "pdf_present": bool_text(truthy(artifact.get("pdf_present"))),
            "pdf_paths_relative": clean(artifact.get("pdf_paths_relative")),
            "preferred_text_path": preferred_text_path,
            "preferred_text_source": preferred_text_source,
            "preferred_text_exists": bool_text(preferred_text_exists),
            "embedding_eligible": bool_text(skip_reason == ""),
            "skip_reason": skip_reason,
            "revisit_issue_count": revisit_data.get("revisit_issue_count", "0"),
            "revisit_highest_severity": revisit_data.get("revisit_highest_severity", ""),
            "revisit_stages": revisit_data.get("revisit_stages", ""),
            "revisit_issue_types": revisit_data.get("revisit_issue_types", ""),
            "revisit_blocking_downstream": revisit_data.get(
                "revisit_blocking_downstream",
                "false",
            ),
            "text_n_pages": clean(artifact.get("text_n_pages")),
            "text_needs_ocr": clean(artifact.get("text_needs_ocr")),
            "text_ocr_applied": clean(artifact.get("text_ocr_applied")),
            "text_quality_flags": clean(artifact.get("remaining_text_quality_flags")),
            "proceedings_ready_present": bool_text(
                truthy(artifact.get("text_proceedings_ready_present"))
            ),
            "proceedings_ready_source_kind": clean(
                artifact.get("text_proceedings_ready_source_kind")
            ),
            "pilot_selected": "false",
        }
        row.update(source_data)
        row.update(count_fields(artifact, count_row))
        row.update(split_data)
        manifest.append({field: row.get(field, "") for field in MANIFEST_FIELDS})
    return manifest


def pilot_priority(row: dict[str, str]) -> tuple[int, int, int, int, tuple[int, str]]:
    review_signal = any(
        truthy(row.get(field))
        for field in (
            "source_manual_review_required",
            "count_manual_review_required",
            "case_series_split_manual_review_required",
            "revisit_blocking_downstream",
        )
    )
    has_revisit = clean(row.get("revisit_issue_count")) not in {"", "0"}
    proceedings = truthy(row.get("proceedings_ready_present"))
    split_auto = row.get("case_series_split_status") == "split_auto"
    return (
        0 if review_signal else 1,
        0 if has_revisit else 1,
        0 if proceedings else 1,
        0 if split_auto else 1,
        paper_sort_key(row),
    )


def select_pilot_rows(rows: list[dict[str, str]], pilot_size: int) -> list[dict[str, str]]:
    eligible_rows = [row for row in rows if truthy(row.get("embedding_eligible"))]
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in eligible_rows:
        category = clean(row.get("source_category")) or "unknown"
        by_category[category].append(row)

    for category_rows in by_category.values():
        category_rows.sort(key=pilot_priority)

    selected: list[dict[str, str]] = []
    category_names = sorted(by_category)
    while len(selected) < pilot_size and category_names:
        next_categories: list[str] = []
        for category in category_names:
            if len(selected) >= pilot_size:
                break
            category_rows = by_category[category]
            if category_rows:
                selected.append(category_rows.pop(0))
            if category_rows:
                next_categories.append(category)
        category_names = next_categories
    return selected


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts = Counter(clean(row.get(field)) or "<blank>" for row in rows)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def build_summary(
    sps_root: Path,
    rows: list[dict[str, str]],
    pilot_rows: list[dict[str, str]],
    pilot_size: int,
) -> dict[str, Any]:
    eligible_rows = [row for row in rows if truthy(row.get("embedding_eligible"))]
    skipped_rows = [row for row in rows if not truthy(row.get("embedding_eligible"))]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sps_root": str(sps_root),
        "total_rows": len(rows),
        "eligible_rows": len(eligible_rows),
        "skipped_rows": len(skipped_rows),
        "skip_reasons": count_values(skipped_rows, "skip_reason"),
        "source_categories": count_values(rows, "source_category"),
        "eligible_source_categories": count_values(eligible_rows, "source_category"),
        "count_manual_review_required": count_values(rows, "count_manual_review_required"),
        "case_series_split_status": count_values(rows, "case_series_split_status"),
        "revisit_highest_severity": count_values(rows, "revisit_highest_severity"),
        "pilot_size_requested": pilot_size,
        "pilot_rows": len(pilot_rows),
        "pilot_source_categories": count_values(pilot_rows, "source_category"),
    }


def render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Manifest Summary",
        "",
        f"Generated at UTC: `{summary['generated_at_utc']}`",
        f"SPS root: `{summary['sps_root']}`",
        "",
        "## Counts",
        "",
        f"- Total rows: {summary['total_rows']}",
        f"- Eligible rows: {summary['eligible_rows']}",
        f"- Skipped rows: {summary['skipped_rows']}",
        f"- Pilot rows: {summary['pilot_rows']} of requested {summary['pilot_size_requested']}",
        "",
        "## Skip Reasons",
        "",
    ]
    for reason, count in summary["skip_reasons"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Pilot Source Categories", ""])
    for category, count in summary["pilot_source_categories"].items():
        lines.append(f"- `{category}`: {count}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    out_dir: Path,
    results_dir: Path,
    rows: list[dict[str, str]],
    pilot_rows: list[dict[str, str]],
    summary: dict[str, Any],
    pilot_size: int,
) -> None:
    pilot_stem = f"pilot_{pilot_size}"
    write_csv(out_dir / "full.csv", rows, MANIFEST_FIELDS)
    write_jsonl(out_dir / "full.jsonl", rows)
    write_csv(out_dir / f"{pilot_stem}.csv", pilot_rows, MANIFEST_FIELDS)
    write_jsonl(out_dir / f"{pilot_stem}.jsonl", pilot_rows)
    write_json(results_dir / "summary.json", summary)
    (results_dir / "summary.md").write_text(render_summary_md(summary), encoding="utf-8")


def build_and_write_manifest(
    sps_root: Path,
    out_dir: Path,
    results_dir: Path,
    pilot_size: int,
) -> dict[str, Any]:
    rows = build_manifest_rows(sps_root)
    pilot_rows = select_pilot_rows(rows, pilot_size)
    pilot_ids = {row["paper_id"] for row in pilot_rows}
    for row in rows:
        row["pilot_selected"] = bool_text(row["paper_id"] in pilot_ids)
    # Refresh pilot rows from the full rows so the selected flag is consistent.
    pilot_rows = [row for row in rows if row["paper_id"] in pilot_ids]
    summary = build_summary(sps_root, rows, pilot_rows, pilot_size)
    write_outputs(out_dir, results_dir, rows, pilot_rows, summary, pilot_size)
    return summary


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    summary = build_and_write_manifest(
        sps_root=args.sps_root,
        out_dir=args.out_dir,
        results_dir=args.results_dir,
        pilot_size=args.pilot_size,
    )
    print(
        "Manifest built:",
        f"rows={summary['total_rows']}",
        f"eligible={summary['eligible_rows']}",
        f"skipped={summary['skipped_rows']}",
        f"pilot={summary['pilot_rows']}",
    )


if __name__ == "__main__":
    main()
