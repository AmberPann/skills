#!/usr/bin/env python3
"""Validate, persist, load, and clean one Agent Skill review state."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_VERSION = 2
CLEANUP_STATE_VERSIONS = {1, STATE_VERSION}
DIMENSIONS = (
    ("feasibility", "可行性"),
    ("necessity", "内容必要性、增量和信息密度"),
    ("clarity", "内容清晰度"),
    ("terminology", "术语与指代"),
)
STATUSES = {"通过", "有问题", "未覆盖", "不适用"}
LIFECYCLE_STATUSES = {"applicable", "not_applicable"}
FILE_KINDS = {"main", "reference", "supporting"}
EVIDENCE_KINDS = {
    "document",
    "code",
    "schema",
    "runtime",
    "tool_call",
    "log",
    "history",
    "inference",
}
SEVERITIES = {"P1", "P2", "P3", None}
MARKER_NAME = ".review-agent-skills-state"


class StateError(RuntimeError):
    """Raised when review state is incomplete, stale, or unsafe to use."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise StateError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise StateError(f"JSON root must be an object: {path}")
    return value


def require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StateError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise StateError(f"{field} must be an array")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{field} must be a non-empty string")
    return value


def require_text_list(value: Any, field: str) -> list[str]:
    return [
        require_text(item, f"{field}[{index}]")
        for index, item in enumerate(require_list(value, field))
    ]


def require_unique(values: list[str], field: str) -> None:
    if len(values) != len(set(values)):
        raise StateError(f"{field} must contain unique values")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_scope_files(review: dict[str, Any]) -> None:
    scope = require_object(review.get("scope"), "scope")
    files = require_list(scope.get("files"), "scope.files")
    if not files:
        raise StateError("scope.files must not be empty")
    for index, item in enumerate(files):
        field = f"scope.files[{index}]"
        source = require_object(item, field)
        path = Path(require_text(source.get("path"), f"{field}.path")).resolve()
        if not path.is_file():
            raise StateError(f"{field}.path is not a file: {path}")
        source["path"] = str(path)
        source["sha256"] = file_sha256(path)


def validate_review(review: dict[str, Any], *, verify_hashes: bool) -> None:
    if review.get("analysisStatus") != "complete":
        raise StateError("analysisStatus must be complete before saving")
    require_text(review.get("language"), "language")
    require_text(review.get("title"), "title")

    scope = require_object(review.get("scope"), "scope")
    require_text(scope.get("target"), "scope.target")
    agent = require_object(scope.get("agent"), "scope.agent")
    require_text(agent.get("name"), "scope.agent.name")
    require_text(agent.get("boundary"), "scope.agent.boundary")
    agent_evidence_refs = require_text_list(
        agent.get("evidenceRefs"), "scope.agent.evidenceRefs"
    )
    if not agent_evidence_refs:
        raise StateError("scope.agent.evidenceRefs must not be empty")
    require_text(scope.get("environment"), "scope.environment")
    scope_files = require_list(scope.get("files"), "scope.files")
    if not scope_files:
        raise StateError("scope.files must not be empty")

    source_paths: list[str] = []
    reading_unit_paths: set[str] = set()
    for index, item in enumerate(scope_files):
        field = f"scope.files[{index}]"
        source = require_object(item, field)
        path = Path(require_text(source.get("path"), f"{field}.path"))
        if not path.is_absolute() or not path.is_file():
            raise StateError(f"{field}.path must be an existing absolute file path")
        kind = source.get("kind")
        if kind not in FILE_KINDS:
            raise StateError(f"{field}.kind is invalid")
        require_text(source.get("role"), f"{field}.role")
        digest = require_text(source.get("sha256"), f"{field}.sha256")
        if verify_hashes and file_sha256(path) != digest:
            raise StateError(f"source file changed after analysis: {path}")
        path_text = str(path)
        source_paths.append(path_text)
        if kind in {"main", "reference"}:
            reading_unit_paths.add(path_text)
    require_unique(source_paths, "scope.files[].path")

    context = require_object(review.get("context"), "context")
    for key in (
        "problem",
        "readBoundary",
        "mechanism",
        "organization",
        "evidenceBoundary",
    ):
        require_text(context.get(key), f"context.{key}")

    evidence_ids: list[str] = []
    for index, item in enumerate(require_list(review.get("evidence"), "evidence")):
        field = f"evidence[{index}]"
        evidence = require_object(item, field)
        evidence_id = require_text(evidence.get("id"), f"{field}.id")
        if evidence.get("kind") not in EVIDENCE_KINDS:
            raise StateError(f"{field}.kind is invalid")
        require_text(evidence.get("source"), f"{field}.source")
        require_text(evidence.get("summary"), f"{field}.summary")
        evidence_ids.append(evidence_id)
    if not evidence_ids:
        raise StateError("evidence must not be empty")
    require_unique(evidence_ids, "evidence[].id")
    evidence_id_set = set(evidence_ids)
    unknown_agent_refs = sorted(set(agent_evidence_refs) - evidence_id_set)
    if unknown_agent_refs:
        raise StateError(
            f"scope.agent.evidenceRefs are unknown: {unknown_agent_refs}"
        )

    dimensions = require_list(review.get("dimensions"), "dimensions")
    if len(dimensions) != len(DIMENSIONS):
        raise StateError("dimensions must contain exactly four entries")

    coverage: dict[str, tuple[str, str, list[str]]] = {}
    dimension_problem_ids: dict[str, list[str]] = {}
    for index, ((expected_key, expected_title), item) in enumerate(
        zip(DIMENSIONS, dimensions, strict=True)
    ):
        field = f"dimensions[{index}]"
        dimension = require_object(item, field)
        if (
            dimension.get("key") != expected_key
            or dimension.get("title") != expected_title
        ):
            raise StateError(
                f"{field} must be {expected_key!r} / {expected_title!r} in fixed order"
            )
        require_text(dimension.get("purpose"), f"{field}.purpose")
        require_text(dimension.get("overallConclusion"), f"{field}.overallConclusion")
        rows = require_list(dimension.get("coverage"), f"{field}.coverage")
        if not rows:
            raise StateError(f"{field}.coverage must not be empty")
        dimension_problem_ids[expected_key] = []
        for row_index, row_item in enumerate(rows):
            row_field = f"{field}.coverage[{row_index}]"
            row = require_object(row_item, row_field)
            row_id = require_text(row.get("id"), f"{row_field}.id")
            if row_id in coverage:
                raise StateError(f"duplicate coverage id: {row_id}")
            require_text(row.get("question"), f"{row_field}.question")
            require_text(row.get("conclusion"), f"{row_field}.conclusion")
            status = row.get("status")
            if status not in STATUSES:
                raise StateError(f"{row_field}.status is invalid")
            refs = require_text_list(
                row.get("evidenceRefs"), f"{row_field}.evidenceRefs"
            )
            unknown_refs = sorted(set(refs) - evidence_id_set)
            if unknown_refs:
                raise StateError(
                    f"{row_field}.evidenceRefs are unknown: {unknown_refs}"
                )
            problem_ids = require_text_list(
                row.get("problemIds"), f"{row_field}.problemIds"
            )
            if status == "有问题" and not problem_ids:
                raise StateError(f"{row_field} needs problemIds when status is 有问题")
            if status != "有问题" and problem_ids:
                raise StateError(
                    f"{row_field} may only link problems when status is 有问题"
                )
            coverage[row_id] = (expected_key, status, problem_ids)
            dimension_problem_ids[expected_key].extend(problem_ids)

    unit_paths: list[str] = []
    for index, item in enumerate(
        require_list(review.get("readingUnits"), "readingUnits")
    ):
        field = f"readingUnits[{index}]"
        unit = require_object(item, field)
        path = str(Path(require_text(unit.get("path"), f"{field}.path")))
        if path not in reading_unit_paths:
            raise StateError(f"{field}.path is not a main/reference scope file")
        unit_paths.append(path)
        for key in (
            "purpose",
            "readWhen",
            "skipWhen",
            "inputs",
            "consumer",
            "placement",
        ):
            require_text(unit.get(key), f"{field}.{key}")
        lifecycle = require_object(unit.get("lifecycle"), f"{field}.lifecycle")
        if lifecycle.get("status") not in LIFECYCLE_STATUSES:
            raise StateError(f"{field}.lifecycle.status is invalid")
        require_text(lifecycle.get("detail"), f"{field}.lifecycle.detail")
        row_ids = require_text_list(
            unit.get("coverageRowIds"), f"{field}.coverageRowIds"
        )
        if not row_ids:
            raise StateError(f"{field}.coverageRowIds must not be empty")
        unknown_rows = sorted(set(row_ids) - set(coverage))
        if unknown_rows:
            raise StateError(f"{field}.coverageRowIds are unknown: {unknown_rows}")
    require_unique(unit_paths, "readingUnits[].path")
    if set(unit_paths) != reading_unit_paths:
        missing = sorted(reading_unit_paths - set(unit_paths))
        extra = sorted(set(unit_paths) - reading_unit_paths)
        raise StateError(f"reading unit mismatch; missing={missing}, extra={extra}")

    problems = require_list(review.get("problems"), "problems")
    problem_ids: list[str] = []
    problem_rows: dict[str, list[str]] = {}
    problem_dimensions: dict[str, str] = {}
    for index, item in enumerate(problems):
        field = f"problems[{index}]"
        problem = require_object(item, field)
        problem_id = require_text(problem.get("id"), f"{field}.id")
        dimension_key = require_text(
            problem.get("dimensionKey"), f"{field}.dimensionKey"
        )
        if dimension_key not in dict(DIMENSIONS):
            raise StateError(f"{field}.dimensionKey is invalid")
        severity = problem.get("severity")
        if severity not in SEVERITIES:
            raise StateError(f"{field}.severity is invalid")
        for key in (
            "title",
            "location",
            "problem",
            "introducedBy",
            "trigger",
            "impact",
            "fix",
        ):
            require_text(problem.get(key), f"{field}.{key}")
        file_value = problem.get("file")
        line_value = problem.get("line")
        if file_value is not None:
            file_path = Path(require_text(file_value, f"{field}.file"))
            if not file_path.is_absolute() or not file_path.is_file():
                raise StateError(f"{field}.file must be an existing absolute path")
            if not isinstance(line_value, int) or line_value < 1:
                raise StateError(f"{field}.line must be a positive integer")
        elif line_value is not None:
            raise StateError(f"{field}.line requires {field}.file")
        rows = require_text_list(
            problem.get("coverageRowIds"), f"{field}.coverageRowIds"
        )
        if not rows:
            raise StateError(f"{field}.coverageRowIds must not be empty")
        for row_id in rows:
            if row_id not in coverage:
                raise StateError(f"{field}.coverageRowIds contains unknown id {row_id}")
            row_dimension, row_status, _ = coverage[row_id]
            if row_dimension != dimension_key or row_status != "有问题":
                raise StateError(f"{field} must link 有问题 rows in the same dimension")
        refs = require_text_list(problem.get("evidenceRefs"), f"{field}.evidenceRefs")
        unknown_refs = sorted(set(refs) - evidence_id_set)
        if unknown_refs:
            raise StateError(f"{field}.evidenceRefs are unknown: {unknown_refs}")
        problem_ids.append(problem_id)
        problem_rows[problem_id] = rows
        problem_dimensions[problem_id] = dimension_key
    require_unique(problem_ids, "problems[].id")
    problem_id_set = set(problem_ids)

    linked_problem_ids = {
        problem_id
        for _, status, row_problem_ids in coverage.values()
        if status == "有问题"
        for problem_id in row_problem_ids
    }
    if linked_problem_ids != problem_id_set:
        missing = sorted(problem_id_set - linked_problem_ids)
        unknown = sorted(linked_problem_ids - problem_id_set)
        raise StateError(
            f"problem linkage mismatch; missing={missing}, unknown={unknown}"
        )
    for problem_id, rows in problem_rows.items():
        for row_id in rows:
            if problem_id not in coverage[row_id][2]:
                raise StateError(
                    f"problem {problem_id} and coverage row {row_id} disagree"
                )
        if problem_id not in dimension_problem_ids[problem_dimensions[problem_id]]:
            raise StateError(f"problem {problem_id} is not linked from its dimension")

    assessment = require_object(review.get("finalAssessment"), "finalAssessment")
    require_text(assessment.get("overall"), "finalAssessment.overall")
    require_text_list(assessment.get("unresolved"), "finalAssessment.unresolved")


def save_state(input_path: str, root_arg: str | None) -> dict[str, Any]:
    review = copy.deepcopy(read_json(Path(input_path)))
    normalize_scope_files(review)
    validate_review(review, verify_hashes=True)

    root = Path(root_arg).resolve() if root_arg else None
    if root is not None:
        if not root.is_dir():
            raise StateError(f"state root is not a directory: {root}")
        state_dir = Path(tempfile.mkdtemp(prefix="skill-review-", dir=root))
    else:
        state_dir = Path(tempfile.mkdtemp(prefix="skill-review-"))
    os.chmod(state_dir, 0o700)

    state_id = secrets.token_hex(16)
    state = {
        "stateVersion": STATE_VERSION,
        "stateId": state_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "review": review,
    }
    marker_path = state_dir / MARKER_NAME
    marker_path.write_text(f"{state_id}\n", encoding="utf-8")
    os.chmod(marker_path, 0o600)
    state_path = state_dir / "review-state.json"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".review-state-", dir=state_dir
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, state_path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)

    return {
        "statePath": str(state_path),
        "dimensionCount": len(review["dimensions"]),
        "coverageCount": sum(
            len(dimension["coverage"]) for dimension in review["dimensions"]
        ),
        "problemCount": len(review["problems"]),
    }


def load_state(state_arg: str) -> dict[str, Any]:
    state_path = Path(state_arg).resolve()
    state = read_json(state_path)
    if state.get("stateVersion") != STATE_VERSION:
        raise StateError("unsupported review state version")
    state_id = require_text(state.get("stateId"), "stateId")
    marker_path = state_path.parent / MARKER_NAME
    try:
        marker_id = marker_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise StateError(f"review state marker is missing: {error}") from error
    if not secrets.compare_digest(state_id, marker_id):
        raise StateError("review state marker does not match stateId")
    review = require_object(state.get("review"), "review")
    validate_review(review, verify_hashes=True)
    return state


def cleanup_state(state_arg: str) -> dict[str, Any]:
    state_path = Path(state_arg).resolve()
    state_dir = state_path.parent
    if state_path.name != "review-state.json" or not state_dir.name.startswith(
        "skill-review-"
    ):
        raise StateError(
            "refusing to clean a path outside a skill-review state directory"
        )
    if not state_path.is_file():
        raise StateError(f"review state does not exist: {state_path}")
    state = read_json(state_path)
    state_id = state.get("stateId")
    marker_path = state_dir / MARKER_NAME
    try:
        marker_id = marker_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise StateError(f"review state marker is missing: {error}") from error
    if (
        state.get("stateVersion") not in CLEANUP_STATE_VERSIONS
        or not isinstance(state.get("review"), dict)
        or not isinstance(state_id, str)
        or not secrets.compare_digest(state_id, marker_id)
    ):
        raise StateError("refusing to clean an unrecognized review state")
    shutil.rmtree(state_dir)
    return {"cleaned": str(state_dir)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    save = subparsers.add_parser("save", help="validate and save a complete review")
    save.add_argument("--input", required=True, help="complete draft JSON")
    save.add_argument(
        "--root", help="optional existing directory under which to create state"
    )

    load = subparsers.add_parser("load", help="load and revalidate saved state")
    load.add_argument("--state", required=True, help="review-state.json")

    cleanup = subparsers.add_parser(
        "cleanup", help="remove one validated state directory"
    )
    cleanup.add_argument("--state", required=True, help="review-state.json")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.command == "save":
            result = save_state(args.input, args.root)
        elif args.command == "load":
            result = load_state(args.state)
        else:
            result = cleanup_state(args.state)
    except (OSError, StateError) as error:
        print(f"review_state: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
