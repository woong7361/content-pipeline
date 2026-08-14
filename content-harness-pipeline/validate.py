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


def validate_file(file_path: Path, artifact: str, revalidation: bool = False) -> dict:
    """`revalidation=True`는 저장된 산출물을 다시 검사할 때 쓴다.

    생성 게이트는 지금의 계약을 그대로 강제하지만, 이미 굳은 산출물은 과거 계약으로 만들어졌다.
    계약을 조일 때마다 기존 run의 재개 경로가 전부 죽으면 조일 수 없게 되므로, 재검증은
    "지금 계약과 같은가"가 아니라 "파이프라인이 아직 처리할 수 있는가"를 본다.
    처리할 수 없는 값은 여기서 조용히 통과되는 것이 아니라 하류(파생기)가 사람 판단으로 올린다.
    """
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
    if revalidation and artifact == "planner_output":
        data = normalize_stored_planner_output(data)
        schema = relax_stored_planner_schema(schema)
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


def normalize_stored_planner_output(data: Any) -> Any:
    """계약이 추가된 뒤에 굳은 planner 산출물이 안 들고 있는 키를 기본값으로 채운다.

    기본값은 전부 "정보 없음"을 뜻하는 값(빈 출구, 진입 즉시 노출, 시도 제한 없음)이라
    없던 사실을 지어내지 않는다. 파일은 건드리지 않고 검증에 쓰는 사본만 채운다.
    """
    if not isinstance(data, dict):
        return data
    data = json.loads(json.dumps(data))
    for section in data.get("sections") or []:
        if not isinstance(section, dict):
            continue
        section.setdefault("advance", {"interaction_id": "", "to_section_id": ""})
        for element in section.get("elements") or []:
            if isinstance(element, dict):
                element.setdefault("reveal", {"when": "scene_enter", "index": 0, "question_id": ""})
        for question in section.get("questions") or []:
            if isinstance(question, dict):
                question.setdefault("attempt_policy", {"max_attempts": 0, "on_exhausted": []})
    return data


def relax_stored_planner_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """생성 계약이 어휘를 닫은 자리를, 저장된 산출물에 한해 문자열로 되돌린다.

    구 planner가 만든 `input_type` 이름과 빈 `answer`는 여기서 통과하더라도
    파생기가 underivable(unsupported_interaction / unreadable_answer)로 모아
    사람 판단으로 올린다. 재검증에서 REJECT하면 그 결정 지점에 도달하지도 못한다.
    """
    schema = json.loads(json.dumps(schema))
    question_props = schema["properties"]["sections"]["items"]["properties"]["questions"]["items"]["properties"]
    question_props["input_type"] = {"type": "string", "minLength": 1}
    question_props["answer"].pop("minLength", None)
    return schema


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
    parser.add_argument(
        "--revalidation",
        action="store_true",
        help="저장된 산출물 재검증 모드. 지금 계약과 같은가가 아니라 파이프라인이 처리할 수 있는가를 본다.",
    )
    args = parser.parse_args()

    result = validate_file(file_path=args.file, artifact=args.artifact, revalidation=args.revalidation)

    if args.write_result:
        write_result(result, args.write_result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
