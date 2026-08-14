"""굳기 전의 계획을 한 번 고친다. LLM 1회.

품질 루프는 critique·eval·refine을 각각 LLM으로 돌리지만 계획 층은 그 값을 못 낸다. 계획의
결함은 대부분 **자기 안에서 앞뒤가 안 맞는 것**이고 그건 코드가 확정할 수 있어서, 여기서는
critique와 eval 역할을 `planner_check`가 맡는다(LLM 0회). 모델이 필요한 자리는 하나만 남는다 —
스토리보드가 요구했는데 계획에 안 내려온 것. 그건 원문 독해라 기계가 못 본다.

점수도 게이트도 만들지 않는다. 무엇이 남았는지는 고친 결과를 같은 검사에 다시 통과시켜 안다.
그래서 이 stage는 판정을 내지 않고 계획만 낸다.

**줄어든 것은 고친 것이 아니라 잃은 것이다.** 계획을 통째로 다시 쓰는 이상 잃을 수 있고, 이
파이프라인은 HTML 층에서 같은 일을 이미 겪었다. 그래서 채택 전에 회귀 검사를 통과해야 한다.
"""

from __future__ import annotations

import json
from pathlib import Path

from stages.planner import PLANNER_OUTPUT_SCHEMA, resolve_markdown_path
from stages.scripts.codex_client import CodexClient
from stages.scripts.common_components import build_required_art_section
from stages.scripts.planner_check import check_planner, compare_planner
from stages.scripts.source_resolve import teacher_root_from_input
from stages.scripts.style_references import build_style_reference_prompt


PROJECT_DIR = Path(__file__).resolve().parent.parent
PLANNER_REFINE_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "planner_refine_system.md"


def refine_plan(
    input_path: Path,
    planner_output: dict,
    violations: list[dict],
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    markdown_path = resolve_markdown_path(input_data=input_data, input_path=input_path)
    prompt = build_prompt(
        input_data=input_data,
        markdown=markdown_path.read_text(encoding="utf-8"),
        planner_output=planner_output,
        violations=violations,
    )
    client = CodexClient(
        codex_bin=codex_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=PLANNER_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def build_prompt(
    input_data: dict,
    markdown: str,
    planner_output: dict,
    violations: list[dict],
) -> str:
    system_prompt = PLANNER_REFINE_SYSTEM_PROMPT.read_text(encoding="utf-8")
    # 계획을 만들 때 받았던 재료를 그대로 다시 준다. 여기서 빠지면 고치는 김에 그 제약을 잃는다.
    required_art = build_required_art_section(input_data, teacher_root_from_input(input_data))
    style_reference_json = build_style_reference_prompt(input_data, PROJECT_DIR)
    return f"""{system_prompt}

INPUT_JSON:
{json.dumps(input_data, ensure_ascii=False, indent=2)}

STYLE_REFERENCE_SET_JSON:
{style_reference_json}

{required_art}

CHECK_REPORT_JSON:
{json.dumps({"violations": violations}, ensure_ascii=False, indent=2)}

PLANNER_JSON:
{json.dumps(planner_output, ensure_ascii=False, indent=2)}

STORY_BOARD_MARKDOWN:
{markdown}
"""


def review_refined(before: dict, after: dict) -> dict:
    """고친 계획을 채택해도 되는지 코드가 판정한다. LLM 0회.

    두 가지를 본다 — 잃은 것이 있는가(회귀), 확정된 위반이 늘었는가. 어느 쪽이든 채택하지
    않는다. 위반이 남아 있는 것은 막지 않는다. 고칠 자리가 없어 못 고친 것까지 되돌리면 같은
    호출을 영원히 반복하게 되고, 남은 위반은 다음 검사에 그대로 다시 잡힌다.
    """
    losses = compare_planner(before, after)
    violations_before = check_planner(before)
    violations_after = check_planner(after)
    added = [item for item in violations_after if item not in violations_before]
    return {
        "accepted": not losses and not added,
        "losses": losses,
        "added_violations": added,
        "resolved": len(violations_before) - len(violations_after) + len(added),
        "remaining_violations": violations_after,
    }


def format_review(review: dict) -> str:
    if review["accepted"]:
        remaining = len(review["remaining_violations"])
        return f"채택 — 위반 {review['resolved']}건 해소, {remaining}건 남음"
    lines = ["기각 — 원본을 유지한다"]
    lines += [f"  · 잃음: {item}" for item in review["losses"]]
    lines += [
        f"  · 새 위반: [{item['kind']}] {item['where']} — {item['detail']}"
        for item in review["added_violations"]
    ]
    return "\n".join(lines)
