"""planner 산출물을 화면 하나씩 사람이 읽을 수 있는 전개도로 되돌린다. LLM 0회.

인터뷰는 planner 뒤에 선다. 그 자리에서 사람이 판단해야 하는 것이 두 종류이기 때문이다.

- **빈 자리** — planner가 규칙상 채우지 못한 것. `prompts/planner_system.md`는 스토리보드에
  없는 학습 내용·수치·보상 구조를 만들지 못하게 막으므로, 스토리보드가 비워둔 구조는
  계획에서도 비어 있다.
- **조용히 채워진 자리** — planner가 승인 없이 정한 것. 같은 규칙이 **시각 층은 덮지 않아서**
  에셋의 그림 내용과 화면 연출은 planner가 스스로 만들어 낸다. 이 값들은 그대로 그림이 되고
  그대로 화면이 되지만, 계획을 열어보기 전에는 아무도 그것이 결정된 줄 모른다.

그래서 이 전개도는 **비어 있는 것과 채워져 있는 것을 같은 화면에 함께** 놓는다. 결손 목록만
뽑으면 두 번째 종류가 통째로 보이지 않는다.

판정은 하지 않는다. 어떤 값이 요청에서 왔고 어떤 값이 planner가 지어낸 것인지는 원문 독해가
필요하며, 그것은 사람이 원본과 대조해 판단한다. 여기서는 확정할 수 있는 것 — 필드가 비었는가 —
만 `???`로 표시한다.

사용법:
    python -B -m stages.scripts.plan_scene_view <planner.json>              # 화면 목록
    python -B -m stages.scripts.plan_scene_view <planner.json> <section_id> # 화면 하나 전개
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

# 노출 시점을 사람이 읽는 순서로 세운다. 이 순서가 곧 학습자가 겪는 순서다.
REVEAL_ORDER = ("scene_enter", "beat", "on_page", "on_correct", "on_wrong")
MISSING = "???"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clip(text: str, width: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= width else text[: width - 1] + "…"


def reveal_key(element: dict) -> tuple[int, int]:
    reveal = element.get("reveal") or {}
    when = reveal.get("when") or "scene_enter"
    order = REVEAL_ORDER.index(when) if when in REVEAL_ORDER else len(REVEAL_ORDER)
    return order, int(reveal.get("index") or 0)


def reveal_label(element: dict) -> str:
    reveal = element.get("reveal") or {}
    when = reveal.get("when") or "scene_enter"
    if when == "beat":
        return f"beat {reveal.get('index') or 0}"
    question_id = reveal.get("question_id") or ""
    return f"{when} {question_id}".strip()


def section_gaps(section: dict, assets: dict[str, dict], is_last: bool = False) -> list[str]:
    """비어 있는 것만 센다. 채워진 값이 옳은지는 여기서 판정하지 않는다.

    화면 성격에 따라 비어 있는 것이 정상인 자리가 있다. 마지막 화면에 출구가 없는 것이
    그렇다 — 계약이 그 자리를 빈 문자열로 정하므로 결손으로 세면 매번 같은 거짓 신호가 뜬다.
    """
    gaps = []
    if not (section.get("staging_notes") or []):
        gaps.append("연출 — staging_notes 가 비어 있다")
    if not is_last and not (section.get("advance") or {}).get("to_section_id"):
        gaps.append("전환 — 이 화면을 벗어나는 길이 없다")
    for question in section.get("questions") or []:
        feedback = question.get("feedback") or {}
        for key, label in (("correct", "정답"), ("wrong", "오답")):
            if not (feedback.get(key) or "").strip():
                gaps.append(f"피드백 — {question.get('id')} 의 {label} 문구가 없다")
    for asset_id in section.get("asset_ids") or []:
        asset = assets.get(asset_id)
        if asset is None:
            gaps.append(f"에셋 — {asset_id} 가 asset_plan 에 없다")
        elif not (asset.get("prompt_brief") or "").strip():
            gaps.append(f"에셋 — {asset_id} 의 그림 내용이 없다")
    return gaps


def render_section(plan: dict, section: dict, is_last: bool = False) -> str:
    assets = {asset.get("id"): asset for asset in plan.get("asset_plan") or []}
    interactions = {item.get("id"): item for item in plan.get("interactions") or []}
    out: list[str] = []
    out.append(f"{section.get('title')}  ({section.get('id')})")
    out.append(f"목적  {clip(section.get('purpose', ''), 100)}")
    out.append("")

    out.append("순서")
    elements = sorted(section.get("elements") or [], key=reveal_key)
    for element in elements:
        out.append(f"  ├ {reveal_label(element):<16} [{element.get('channel')}]")
        out.append(f"  │ {'':16} {clip(element.get('content', ''), 88)}")
        rendered = [text for text in (element.get("rendered_text") or []) if text.strip()]
        if rendered:
            out.append(f"  │ {'':16} 화면 문구 {rendered}")

    for question in section.get("questions") or []:
        out.append(f"  ├ 조작             {question.get('id')} [{question.get('input_type')}]")
        out.append(f"  │ {'':16} {clip(question.get('prompt', ''), 88)}")
        choices = question.get("choices") or []
        if choices:
            labels = [
                f"{choice.get('label')}{'(정답)' if choice.get('correct') else ''}"
                for choice in choices
            ]
            out.append(f"  │ {'':16} 보기 {labels}")
        feedback = question.get("feedback") or {}
        for key, label in (("correct", "정답"), ("wrong", "오답")):
            out.append(f"  │ {'':16} {label} 문구 {clip(feedback.get(key, ''), 70) or MISSING}")
        policy = question.get("attempt_policy") or {}
        if policy.get("max_attempts"):
            out.append(
                f"  │ {'':16} {policy.get('max_attempts')}회 후 {policy.get('on_exhausted')}"
            )

    advance = section.get("advance") or {}
    if advance.get("to_section_id"):
        trigger = interactions.get(advance.get("interaction_id")) or {}
        out.append(
            f"  └ 전환             {advance.get('interaction_id')}"
            f"({trigger.get('type', '?')}) → {advance.get('to_section_id')}"
        )
    else:
        out.append(f"  └ 전환             {MISSING}")

    out.append("")
    out.append("연출  staging_notes")
    for note in section.get("staging_notes") or [MISSING]:
        out.append(f"  · {note}")

    out.append("")
    out.append("에셋  planner 가 정한 그림 내용")
    for asset_id in section.get("asset_ids") or []:
        asset = assets.get(asset_id) or {}
        out.append(f"  {asset_id}  —  {clip(asset.get('visual_role', ''), 70)}")
        out.append(f"    그림  {clip(asset.get('prompt_brief', ''), 150) or MISSING}")
        out.append(f"    배치  {clip(asset.get('composition_notes', ''), 150) or MISSING}")
    if not (section.get("asset_ids") or []):
        out.append("  (없음)")

    gaps = section_gaps(section, assets, is_last)
    out.append("")
    out.append(f"빈 자리 {len(gaps)}")
    for gap in gaps:
        out.append(f"  · {gap}")
    return "\n".join(out)


def render_index(plan: dict) -> str:
    assets = {asset.get("id"): asset for asset in plan.get("asset_plan") or []}
    sections = plan.get("sections") or []
    out = [f"화면 {len(sections)} · 에셋 {len(assets)} · 캐릭터 {len(plan.get('characters') or [])}", ""]
    for index, section in enumerate(sections, start=1):
        gaps = section_gaps(section, assets, index == len(sections))
        out.append(
            f"{index:>2}. {section.get('id'):<28} 빈자리 {len(gaps):<2} "
            f"문항 {len(section.get('questions') or []):<2} "
            f"에셋 {len(section.get('asset_ids') or []):<2} {clip(section.get('title', ''), 46)}"
        )
    return "\n".join(out)


def main(argv: list[str]) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    plan = load(Path(argv[0]))
    if len(argv) == 1:
        print(render_index(plan))
        return 0
    wanted = argv[1]
    sections = plan.get("sections") or []
    for index, section in enumerate(sections, start=1):
        if section.get("id") == wanted:
            print(render_section(plan, section, index == len(sections)))
            return 0
    print(f"그런 화면이 없다: {wanted}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
