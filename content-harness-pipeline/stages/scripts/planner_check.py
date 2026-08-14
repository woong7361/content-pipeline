"""planner_output이 자기 안에서 앞뒤가 맞는가만 본다. LLM 0회.

schema는 **모양**을 본다 — 타입, 패턴, 필수 여부. 어떤 id가 실제로 존재하는지는 모양이 아니라
상호참조라서 schema를 통과한 계획에도 미아 참조가 남는다(실측: schema PASS인 산출물에서
`elements[].refs`가 어디에도 없는 이름을 가리키고, asset이 쓴다고 적은 화면은 그 asset을
모른다고 적혀 있었다).

여기서 확정한 위반은 `planner_refine`의 입력이 된다. **확정할 수 없는 것은 여기서 다루지
않는다** — 스토리보드가 요구했는데 계획에 안 내려온 것은 원문 독해가 필요하고, 그건 refine의
축이다. 기계가 판정한 것과 모델이 판단할 것을 한 목록에 섞으면 refine이 둘을 같은 확신으로
다루게 된다.

회귀 검사(`compare_planner`)도 여기 둔다. 고친 계획과 고치기 전 계획을 대조해 **줄어든 것**만
본다. 원문 형식을 가정하지 않으므로 어떤 스토리보드에서 온 계획이든 같은 기준이 선다.
"""

from __future__ import annotations

# 장을 넘겨야 다음이 보이는 노출 시점. 이 값이 한 화면 안에 있으면 그 화면의 내용은 한 번에
# 다 조작할 수 없다. 같은 화면의 순차 대사(`beat`)는 대사만 차례로 뜰 뿐 나머지는 함께 있으므로
# 여기 넣지 않는다 — 넣으면 대사가 있는 거의 모든 화면이 걸려 신호가 죽는다.
PAGED_REVEAL = "on_page"
# 문항의 결과로 나타나는 노출 시점. 어느 문항인지 지목되어야 성립한다.
QUESTION_SCOPED_REVEALS = ("on_correct", "on_wrong")


def check_planner(planner_output: dict) -> list[dict]:
    """확정된 위반만 모은다. 판정이지 의견이 아니므로 애매한 것은 넣지 않는다."""
    violations: list[dict] = []
    sections = planner_output.get("sections") or []

    section_ids = [section.get("id", "") for section in sections]
    interaction_ids = [item.get("id", "") for item in planner_output.get("interactions") or []]
    asset_ids = [asset.get("id", "") for asset in planner_output.get("asset_plan") or []]
    character_ids = [character.get("id", "") for character in planner_output.get("characters") or []]
    question_ids = [
        question.get("id", "")
        for section in sections
        for question in section.get("questions") or []
    ]

    violations += duplicate_ids("sections", section_ids)
    violations += duplicate_ids("interactions", interaction_ids)
    violations += duplicate_ids("asset_plan", asset_ids)
    violations += duplicate_ids("characters", character_ids)
    violations += duplicate_ids("questions", question_ids)

    for section in sections:
        violations += check_section(
            section=section,
            section_ids=section_ids,
            interaction_ids=interaction_ids,
            asset_ids=asset_ids,
            question_ids=question_ids,
        )

    violations += check_flow(sections, section_ids)
    violations += check_assets(planner_output, section_ids, character_ids, asset_ids)
    return violations


def check_section(
    *,
    section: dict,
    section_ids: list[str],
    interaction_ids: list[str],
    asset_ids: list[str],
    question_ids: list[str],
) -> list[dict]:
    violations: list[dict] = []
    section_id = section.get("id", "")
    elements = section.get("elements") or []
    questions = section.get("questions") or []
    own_question_ids = [question.get("id", "") for question in questions]

    for interaction_id in section.get("interaction_ids") or []:
        if interaction_id not in interaction_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"{section_id}.interaction_ids",
                    f"{interaction_id!r} 를 가리키는데 interactions 에 그 id 가 없다",
                )
            )
    for asset_id in section.get("asset_ids") or []:
        if asset_id not in asset_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"{section_id}.asset_ids",
                    f"{asset_id!r} 를 가리키는데 asset_plan 에 그 id 가 없다",
                )
            )

    # 이 화면이 장으로 나뉘는가. 나뉜다면 그 화면의 문항은 한 번에 다 조작할 수 없다.
    is_paged = any((element.get("reveal") or {}).get("when") == PAGED_REVEAL for element in elements)
    referenced_questions: set[str] = set()

    for element in elements:
        channel = element.get("channel", "")
        reveal = element.get("reveal") or {}
        question_refs = [ref for ref in element.get("refs") or [] if ref in own_question_ids]
        referenced_questions.update(question_refs)

        for ref in element.get("refs") or []:
            if ref not in asset_ids and ref not in question_ids:
                violations.append(
                    violation(
                        "unknown_ref",
                        f"{section_id}.elements[{channel}].refs",
                        f"{ref!r} 를 가리키는데 asset_plan 에도 questions 에도 그 id 가 없다",
                    )
                )

        when = reveal.get("when", "")
        target = reveal.get("question_id", "")
        if when in QUESTION_SCOPED_REVEALS and not target:
            violations.append(
                violation(
                    "unresolved_reveal",
                    f"{section_id}.elements[{channel}].reveal",
                    f"{when} 는 어느 문항의 결과인지 지목되어야 하는데 question_id 가 비었다",
                )
            )
        elif target and target not in question_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"{section_id}.elements[{channel}].reveal.question_id",
                    f"{target!r} 를 가리키는데 questions 에 그 id 가 없다",
                )
            )
        elif when not in QUESTION_SCOPED_REVEALS and target:
            violations.append(
                violation(
                    "unresolved_reveal",
                    f"{section_id}.elements[{channel}].reveal",
                    f"{when} 는 문항의 결과가 아닌데 question_id 가 {target!r} 로 채워져 있다",
                )
            )

        # 한 요소가 여러 문항을 묶으면 그 문항들은 같은 시점에 함께 나타난다는 뜻이다. 장으로
        # 나뉜 화면에서 그 주장은 성립하지 않는다 — 문항이 어느 장에 있는지 계획에 없게 되고,
        # 하류는 "들어가면 바로 조작할 수 있다"로 읽어 넘기지 않은 채 조작하려 든다.
        # 문항의 결과로 나타나는 요소(on_correct·on_wrong)는 reveal.question_id 로 이미 어느 문항
        # 이야기인지 지목한다. 그건 노출 시점 주장이 아니라 결과 시점 주장이므로 여기서 세지 않는다.
        if is_paged and len(question_refs) > 1 and when not in QUESTION_SCOPED_REVEALS:
            violations.append(
                violation(
                    "timing_conflict",
                    f"{section_id}.elements[{channel}]",
                    f"장으로 나뉜 화면인데 문항 {question_refs} 를 한 시점"
                    f"({reveal.get('when', '')})으로 묶었다. 문항이 어느 장에 있는지 정할 수 없다 — "
                    "장마다 요소를 나눠 그 장의 문항만 가리킨다",
                )
            )

    for question in questions:
        violations += check_question(section_id=section_id, question=question)
    for question_id in own_question_ids:
        if question_id not in referenced_questions:
            violations.append(
                violation(
                    "unresolved_reveal",
                    f"{section_id}.questions[{question_id}]",
                    "어느 요소도 이 문항을 refs 로 가리키지 않아 언제 나타나는지 정할 수 없다",
                )
            )
    return violations


def check_question(*, section_id: str, question: dict) -> list[dict]:
    violations: list[dict] = []
    question_id = question.get("id", "")
    where = f"{section_id}.questions[{question_id}]"
    input_type = question.get("input_type", "")
    choices = question.get("choices") or []
    answer = question.get("answer", "")

    if input_type == "choice":
        labels = [choice.get("label", "") for choice in choices]
        correct = [choice for choice in choices if choice.get("correct")]
        if not choices:
            violations.append(violation("answer_mismatch", where, "보기로 고르는 문항인데 choices 가 비었다"))
        elif len(correct) != 1:
            violations.append(
                violation("answer_mismatch", where, f"정답 보기가 {len(correct)}개다. 하나여야 한다")
            )
        if labels and answer not in labels:
            violations.append(
                violation(
                    "answer_mismatch",
                    where,
                    f"answer {answer!r} 가 보기 {labels} 중에 없다. 정답 보기의 label 을 그대로 쓴다",
                )
            )
    elif choices:
        violations.append(
            violation(
                "answer_mismatch",
                where,
                f"input_type 이 {input_type!r} 인데 choices 가 채워져 있다. 보기로 고르는 문항이 아니다",
            )
        )
    return violations


def check_flow(sections: list[dict], section_ids: list[str]) -> list[dict]:
    """출구를 따라 걸어가 닿는지 본다. 화면은 나열이 아니라 이어져야 한다."""
    violations: list[dict] = []
    graph: dict[str, str] = {}

    for section in sections:
        section_id = section.get("id", "")
        advance = section.get("advance") or {}
        interaction_id = advance.get("interaction_id", "")
        to_section_id = advance.get("to_section_id", "")
        graph[section_id] = to_section_id

        if to_section_id and to_section_id not in section_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"{section_id}.advance.to_section_id",
                    f"{to_section_id!r} 로 나가는데 sections 에 그 화면이 없다",
                )
            )
        if to_section_id == section_id:
            violations.append(
                violation("unreachable", f"{section_id}.advance", "자기 자신으로 나간다"),
            )
        if bool(interaction_id) != bool(to_section_id):
            violations.append(
                violation(
                    "unresolved_advance",
                    f"{section_id}.advance",
                    "조작과 도착 화면 중 하나만 채워져 있다. 출구가 없으면 둘 다 비운다",
                )
            )

    # 출구를 하나도 선언하지 않은 계획은 걸을 길이 없다. `advance`는 나중에 추가된 계약이라
    # 그 이전 산출물이 전부 여기 걸리는데, 그건 계획이 끊긴 것이 아니라 계약이 없던 것이다.
    if not section_ids or not any(graph.values()):
        return violations

    reached: set[str] = set()
    cursor = section_ids[0]
    while cursor and cursor not in reached:
        reached.add(cursor)
        cursor = graph.get(cursor, "")
    unreachable = [section_id for section_id in section_ids if section_id not in reached]
    if unreachable:
        violations.append(
            violation(
                "unreachable",
                "sections",
                f"첫 화면에서 출구를 따라가면 {unreachable} 에 닿지 못한다",
            )
        )
    return violations


def check_assets(
    planner_output: dict,
    section_ids: list[str],
    character_ids: list[str],
    asset_ids: list[str],
) -> list[dict]:
    violations: list[dict] = []
    sections = planner_output.get("sections") or []
    asset_ids_of_section = {
        section.get("id", ""): set(section.get("asset_ids") or []) for section in sections
    }
    paths: list[str] = []

    for asset in planner_output.get("asset_plan") or []:
        asset_id = asset.get("id", "")
        paths.append(asset.get("intended_path", ""))
        character_id = asset.get("character_id", "")
        if character_id and character_id not in character_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"asset_plan[{asset_id}].character_id",
                    f"{character_id!r} 를 가리키는데 characters 에 그 id 가 없다",
                )
            )
        for section_id in asset.get("usage_section_ids") or []:
            if section_id not in section_ids:
                violations.append(
                    violation(
                        "unknown_ref",
                        f"asset_plan[{asset_id}].usage_section_ids",
                        f"{section_id!r} 에서 쓴다는데 sections 에 그 화면이 없다",
                    )
                )
            elif asset_id not in asset_ids_of_section.get(section_id, set()):
                # 어느 쪽이 참인지 코드가 정할 수 없다. 두 자리가 서로를 부정한다는 사실만 올린다.
                violations.append(
                    violation(
                        "usage_mismatch",
                        f"asset_plan[{asset_id}].usage_section_ids",
                        f"{section_id!r} 에서 쓴다는데 그 화면의 asset_ids 에는 이 asset 이 없다",
                    )
                )

    duplicated = sorted({path for path in paths if path and paths.count(path) > 1})
    if duplicated:
        violations.append(
            violation("duplicate_id", "asset_plan.intended_path", f"같은 경로를 여럿이 쓴다: {duplicated}")
        )

    for character in planner_output.get("characters") or []:
        reference = character.get("reference_asset_id", "")
        if reference and reference not in asset_ids:
            violations.append(
                violation(
                    "unknown_ref",
                    f"characters[{character.get('id', '')}].reference_asset_id",
                    f"{reference!r} 를 기준 포즈로 삼는데 asset_plan 에 그 id 가 없다",
                )
            )

    for group in planner_output.get("asset_groups") or []:
        for asset_id in group.get("asset_ids") or []:
            if asset_id not in asset_ids:
                violations.append(
                    violation(
                        "unknown_ref",
                        f"asset_groups[{group.get('id', '')}].asset_ids",
                        f"{asset_id!r} 를 묶는데 asset_plan 에 그 id 가 없다",
                    )
                )
    return violations


def duplicate_ids(where: str, ids: list[str]) -> list[dict]:
    duplicated = sorted({value for value in ids if value and ids.count(value) > 1})
    if not duplicated:
        return []
    return [violation("duplicate_id", where, f"같은 id 가 둘 이상 있다: {duplicated}")]


def violation(kind: str, where: str, detail: str) -> dict:
    return {"kind": kind, "where": where, "detail": detail}


def compare_planner(before: dict, after: dict) -> list[str]:
    """고친 계획이 무엇을 잃었는지만 본다.

    계획 전체를 다시 쓰는 stage는 고치는 김에 지운다. 이 파이프라인은 같은 위험을 이미 겪었다 —
    HTML을 통째로 재작성하는 stage가 앞선 수정을 지워서 순서를 고정해야 했다. 계획도 같아서,
    **줄어든 것은 고친 것이 아니라 잃은 것**으로 본다. 늘어난 것은 막지 않는다.
    """
    losses: list[str] = []
    for label, count in count_view(before).items():
        after_count = count_view(after)[label]
        if after_count < count:
            losses.append(f"{label} 가 {count} 개에서 {after_count} 개로 줄었다")
    for label, values in text_view(before).items():
        lost = sorted(values - text_view(after)[label])
        if lost:
            losses.append(f"{label} 에서 {len(lost)} 개가 사라졌다: {lost[:5]}")
    return losses


def count_view(planner_output: dict) -> dict[str, int]:
    sections = planner_output.get("sections") or []
    return {
        "화면": len(sections),
        "요소": sum(len(section.get("elements") or []) for section in sections),
        "문항": sum(len(section.get("questions") or []) for section in sections),
        "asset": len(planner_output.get("asset_plan") or []),
        "캐릭터": len(planner_output.get("characters") or []),
    }


def text_view(planner_output: dict) -> dict[str, set[str]]:
    """학습자가 읽게 될 문자열만 모은다. 정규화해 비교하므로 표기 손질은 손실로 세지 않는다."""
    sections = planner_output.get("sections") or []
    rendered = {
        normalize(text)
        for section in sections
        for element in section.get("elements") or []
        for text in element.get("rendered_text") or []
    }
    questions = {
        normalize(value)
        for section in sections
        for question in section.get("questions") or []
        for value in [question.get("prompt", ""), question.get("answer", "")]
        + [choice.get("label", "") for choice in question.get("choices") or []]
    }
    return {
        "화면 문구": {text for text in rendered if text},
        "문항 문구": {text for text in questions if text},
    }


def normalize(text: str) -> str:
    return "".join(text.split())


def format_violations(violations: list[dict]) -> str:
    if not violations:
        return "확정된 위반 없음"
    lines = [f"확정된 위반 {len(violations)}건"]
    lines += [f"  · [{item['kind']}] {item['where']} — {item['detail']}" for item in violations]
    return "\n".join(lines)
