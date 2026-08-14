from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.source_resolve import teacher_root_from_input
from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client
from stages.scripts.common_components import build_common_components_section
from stages.scripts.prompt_parts import with_common_html_contract
from stages.scripts.style_references import build_style_reference_prompt


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONTENT_REFINE_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "content_refine_system.md"
BUILDER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "builder_output.schema.json"


def refine_content(
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    content_critique_path: Path | None,
    run_dir: Path,
    output_path: Path,
    test_report_path: Path | None = None,
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    llm_provider: str = PROVIDER_CODEX,
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    asset_output = load_asset_output(asset_generator_path)
    builder_output = json.loads(builder_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    # functional_test가 REJECT면 그 iteration의 LLM 리뷰는 건너뛰므로 critique가 없다.
    # 기능이 깨진 HTML에 대한 학습 품질 비평은 어차피 다음 iteration에서 다시 쓰인다.
    critique_output = (
        json.loads(content_critique_path.read_text(encoding="utf-8"))
        if content_critique_path is not None and content_critique_path.exists()
        else None
    )
    test_report = json.loads(test_report_path.read_text(encoding="utf-8")) if test_report_path else None
    refine_packet = build_refine_packet(critique_output=critique_output, test_report=test_report)
    prompt = build_prompt(
        input_data=input_data,
        planner_output=planner_output,
        asset_output=asset_output,
        builder_output=builder_output,
        html=html,
        refine_packet=refine_packet,
        run_dir=run_dir,
    )
    client = create_prompt_client(
        provider=llm_provider,
        codex_bin=codex_bin,
        claude_bin=claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=BUILDER_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def load_asset_output(asset_generator_path: Path | None) -> dict:
    if asset_generator_path is None:
        return {"assets": []}
    return json.loads(asset_generator_path.read_text(encoding="utf-8"))


def build_refine_packet(*, critique_output: dict | None, test_report: dict | None = None) -> dict:
    """critique는 방향을, 테스트 실패는 사실을 준다. 어느 한쪽만 있어도 packet은 성립한다.

    점수를 넘기지 않는다는 원칙은 그대로다 — 여기 실리는 것은 판정 총점이 아니라
    "이 조작을 했더니 이것이 일어나지 않았다"는 관찰이다. 고칠 대상이 특정되므로
    산문 지적보다 훨씬 좁게 고칠 수 있다.
    """
    critique_output = critique_output or {}
    packet = {
        "content": {
            "priority_issues": critique_output.get("priority_issues", []),
            "refine_suggestions": critique_output.get("refine_suggestions", []),
        },
    }
    if test_report:
        packet["functional"] = build_functional_packet(test_report)
    return packet


# 고치는 사람이 달라진다. 계약 위반은 표시를 붙이는 일이고, 동작 결함은 동작을 고치는 일이다.
FAILURE_GROUPS = {
    "hook_missing": "검증 표시가 없어 확인할 수 없었다. 그 표시를 계약대로 붙인다",
    "action_failed": "학습자가 그 조작을 할 수 없었다. 누를 수 없거나 가려져 있다",
    "expect_failed": "조작은 됐는데 일어나야 할 일이 일어나지 않았다. 동작 결함이다",
}

# HTML 결함이 아닌 실패. 실행기·spec·환경 문제라 refiner가 손댈 자리가 없고, 섞어 보내면
# 없는 결함을 "고친다". 건수만 알려 요약과 실패 목록의 차이가 설명되게 한다.
NON_HTML_FAILURES = {
    "runtime_error": "실행기 자체가 진행하지 못했다(브라우저·로딩 오류). 파이프라인 문제다",
    "unknown_action": "spec이 실행기가 모르는 조작을 요구했다. spec 문제다",
    "unknown_expect": "spec이 실행기가 모르는 단언을 요구했다. spec 문제다",
    "spec_error": "spec이 단언에 필요한 정보를 안 들고 있다. spec 문제다",
}


def build_functional_packet(test_report: dict) -> dict:
    failed = [item for item in test_report.get("scenarios", []) if item.get("status") != "PASS"]
    by_reason = {item["case_id"]: item for item in failed}
    grouped: dict[str, list[dict]] = {}
    excluded: dict[str, int] = {}
    for failure in test_report.get("failures", []):
        reason = failure["reason"]
        if reason not in FAILURE_GROUPS:
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        story = by_reason.get(failure["case_id"])
        if story is None:
            continue
        grouped.setdefault(reason, []).append(
            {
                "화면": story.get("section_id", ""),
                "상황": story.get("given", ""),
                "조작": story.get("when", []),
                "일어나야 했던 일": story.get("then", []),
                "관찰": failure.get("detail", ""),
            }
        )
    packet = {
        "요약": f"{test_report.get('passed', 0)}/{test_report.get('total', 0)} 통과",
        "무엇을 뜻하나": {k: v for k, v in FAILURE_GROUPS.items() if k in grouped},
        "실패": grouped,
    }
    if excluded:
        packet["HTML 결함이 아닌 실패"] = {
            reason: {"건수": count, "뜻": NON_HTML_FAILURES.get(reason, "분류되지 않은 실행 문제다")}
            for reason, count in excluded.items()
        }
    return packet


def build_prompt(
    input_data: dict,
    planner_output: dict,
    asset_output: dict,
    builder_output: dict,
    html: str,
    refine_packet: dict,
    run_dir: Path,
) -> str:
    system_prompt = with_common_html_contract(CONTENT_REFINE_SYSTEM_PROMPT.read_text(encoding="utf-8"))
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    planner_json = json.dumps(planner_output, ensure_ascii=False, indent=2)
    asset_json = json.dumps(asset_output, ensure_ascii=False, indent=2)
    builder_json = json.dumps(builder_output, ensure_ascii=False, indent=2)
    refine_packet_json = json.dumps(refine_packet, ensure_ascii=False, indent=2)
    style_reference_json = build_style_reference_prompt(input_data, PROJECT_DIR)
    return f"""{system_prompt}

RUN_DIR:
{run_dir.resolve()}

{build_common_components_section(teacher_root_from_input(input_data))}

INPUT_JSON:
{input_json}

STYLE_REFERENCE_SET_JSON:
{style_reference_json}

PLANNER_OUTPUT_JSON:
{planner_json}

ASSET_GENERATOR_OUTPUT_JSON:
{asset_json}

PREVIOUS_BUILDER_OUTPUT_JSON:
{builder_json}

REFINE_PACKET_JSON:
{refine_packet_json}

PREVIOUS_HTML:
{html}
"""
