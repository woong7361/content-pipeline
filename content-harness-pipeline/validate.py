import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from stages.scripts.style_references import resolve_style_reference_set

PROJECT_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = PROJECT_DIR / "schemas"
ARTIFACT_SCHEMAS = {
    "input": SCHEMA_DIR / "input.schema.json",
    "planner_output": SCHEMA_DIR / "planner_output.schema.json",
    "asset_generator_output": SCHEMA_DIR / "asset_generator_output.schema.json",
    "builder_output": SCHEMA_DIR / "builder_output.schema.json",
    "design_review_output": SCHEMA_DIR / "design_review_output.schema.json",
    "content_critique_output": SCHEMA_DIR / "content_critique_output.schema.json",
    "content_eval_output": SCHEMA_DIR / "content_eval_output.schema.json",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc


def validate_file(file_path: Path, artifact: str) -> dict:
    if artifact not in ARTIFACT_SCHEMAS:
        raise ValueError(f"unknown artifact: {artifact}")

    try:
        data = load_json(file_path)
    except ValueError as exc:
        return {
            "artifact": artifact,
            "checked_file": str(file_path),
            "status": "ERROR",
            "errors": [str(exc)],
        }

    schema = load_json(ARTIFACT_SCHEMAS[artifact])
    errors = validate_schema(data, schema)

    # schema는 모양만 본다. 경로가 실제로 있는지는 파일시스템을 봐야 알고,
    # 그걸 stage에 맡기면 run 디렉토리를 만든 뒤에야 실패한다.
    if artifact == "input" and not errors:
        errors = validate_style_reference_set(data)

    return {
        "artifact": artifact,
        "checked_file": str(file_path),
        "status": "REJECT" if errors else "PASS",
        "errors": errors,
    }


def validate_style_reference_set(data: Any) -> list[str]:
    """화풍 참조가 실제로 해석되는지 run 시작 전에 확인한다.

    stage 안에서 처음 해석하면 planner를 부르기 직전에야 FileNotFoundError가 나고,
    그때는 이미 run 디렉토리와 input 사본이 만들어진 뒤다. 같은 검사를 여기서 먼저 돌린다.
    """
    if not isinstance(data, dict) or "style_reference_set" not in data.get("metadata", {}):
        return []
    try:
        resolved = resolve_style_reference_set(input_data=data, project_dir=PROJECT_DIR)
    except (ValueError, FileNotFoundError) as exc:
        return [f"style_reference_set: {exc}"]

    total = sum(len(items) for items in resolved["categories"].values())
    if total == 0:
        return [
            "style_reference_set: 참조가 0개다. "
            f"root '{resolved['root']}'의 md catalog에 `- Path:`가 달린 `## 항목`이 없거나 "
            "전부 `Status: deprecated`다."
        ]
    return []


def write_result(result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        format_schema_error(error)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path))
    ]


def format_schema_error(error: Any) -> str:
    path = "$"
    if error.path:
        path += "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.path)
    return f"schema {path}: {error.message}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a pipeline JSON artifact.")
    parser.add_argument("file", type=Path)
    parser.add_argument(
        "--artifact",
        required=True,
        choices=[
            "input",
            "planner_output",
            "asset_generator_output",
            "builder_output",
            "design_review_output",
            "content_critique_output",
            "content_eval_output",
        ],
    )
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()

    result = validate_file(file_path=args.file, artifact=args.artifact)

    if args.write_result:
        write_result(result, args.write_result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
