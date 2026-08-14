"""planner_output -> test_spec 파생. LLM을 쓰지 않는다.

같은 planner에 대해 항상 같은 spec이 나와야 게이트가 흔들리지 않는다. 그래서 이 모듈은
순수 함수다 — 모델 호출도, 시각도, 난수도 쓰지 않는다.

파생하지 못한 것은 버리지 않고 `underivable`에 모은다. 그 목록이 "planner를 실행 층까지
구조화해야 하는가"를 판단할 근거이고, 조용히 줄어든 커버리지를 통과로 착각하지 않게 한다.
"""

from __future__ import annotations

import re
from typing import Any


SPEC_VERSION = "1"

# 대괄호는 두 가지로 쓰인다. 보기 라벨의 일부(`[3시]`, `[1일]`)이거나 채울 빈칸(`[12]시 [0]분`)이다.
# 안이 전부 숫자일 때만 빈칸으로 읽는다. 라벨이면 choices 경로가 먼저 잡는다.
BRACKET_GROUP = re.compile(r"\[([^\[\]]*)\]")

# 실행기가 조작을 아는 입력 방식. 여기 없는 방식이 오면 spec을 만들어도 실행기가 못 밀므로
# 케이스를 만들지 않고 사람 판단으로 올린다. 실행기의 action enum과 함께 움직여야 한다.
SUPPORTED_INPUT_TYPES = frozenset({"choice", "keypad", "drag_drop", "hotspot"})

# 누가 고칠 수 있는가. 이 값이 게이트 동작을 가른다.
#   repo    — 실행기·계약을 늘려야 한다. builder는 손쓸 수 없으므로 게이트를 막지 않는다.
#   planner — planner 산출물이 정보를 안 들고 있다. 위쪽에서 고칠 수 있다.
FIX_REPO = "repo"
FIX_PLANNER = "planner"


def derive_test_spec(planner_output: dict, source_name: str) -> dict:
    cases: list[dict] = []
    underivable: list[dict] = []

    section_ids = {s["id"] for s in planner_output.get("sections", [])}
    interaction_ids = {i["id"] for i in planner_output.get("interactions", [])}
    correct_steps: dict[str, list[dict]] = {}
    pace_steps: dict[str, list[dict]] = {}
    for section in planner_output.get("sections", []):
        section_id = section["id"]
        reveals, reveal_gaps = collect_reveals(section)
        underivable.extend({"section_id": section_id, **item} for item in reveal_gaps)
        pace_steps[section_id] = build_pace_steps(reveals)
        cases.extend(build_timing_cases(section, reveals))
        correct_steps[section_id] = []
        for question in section.get("questions", []):
            derived, question_gap = build_question_cases(section_id, question, reveals)
            cases.extend(derived)
            for derived_case in derived:
                if derived_case["id"].endswith("_correct"):
                    correct_steps[section_id].extend(derived_case["steps"])
            if question_gap:
                underivable.append({"section_id": section_id, "ref": question["id"], **question_gap})
        # 출구는 대사·문항을 마쳐야 나타날 수 있다(reveal·attempt가 그 시점을 계약으로 들고
        # 있으므로 정당한 구현이다). flow 케이스도 journey처럼 그 길을 걸어서 출구에 간다.
        flow_case, flow_gaps = build_flow_case(
            section,
            section_ids,
            interaction_ids,
            lead_steps=pace_steps[section_id] + correct_steps[section_id],
        )
        if flow_case is not None:
            cases.append(flow_case)
        underivable.extend({"section_id": section_id, "ref": "advance", **item} for item in flow_gaps)

    journey = build_journey_case(planner_output, correct_steps, pace_steps)
    if journey is not None:
        cases.append(journey)

    underivable.extend(collect_prose_only_rules(planner_output))

    return {
        "spec_version": SPEC_VERSION,
        "source_planner": source_name,
        "cases": cases,
        "underivable": underivable,
        "coverage": build_coverage(planner_output, cases, underivable),
    }


def collect_reveals(section: dict) -> tuple[dict, list[dict]]:
    """rendered_text를 노출 시점별로 나눈다.

    `rendered_text`가 '무엇이 뜨는가'라면 `reveal`은 '언제 뜨는가'다. 시점을 안 나누고 전부
    화면 진입 시점에 단언하면, 조작해야 나타나는 문구(피드백, 두 번째 말풍선, 다음 장)가
    전부 누락으로 잡힌다. `reveal`이 없는 planner는 전부 scene_enter로 읽어 이전 동작을 지킨다.

    on_correct/on_wrong인데 question_id가 비어 있으면 시점은 아는데 주소를 모르는 것이다.
    scene_enter로 읽으면 "맞혀야 뜨는 문구"를 진입 즉시 단언해 영구 false 실패가 되므로,
    케이스로 만들지 않고 underivable로 올린다 — 조용히 오분류하지 않는다.
    """
    reveals: dict = {"scene_enter": [], "beat": {}, "on_page": {}, "on_correct": {}, "on_wrong": {}}
    gaps: list[dict] = []
    for element in section.get("elements", []):
        texts = element.get("rendered_text", [])
        if not texts:
            continue
        reveal = element.get("reveal") or {}
        when = reveal.get("when", "scene_enter")
        index = reveal.get("index", 0)
        question_id = reveal.get("question_id", "")

        if when in ("on_correct", "on_wrong"):
            if not question_id:
                gaps.append(
                    {
                        "ref": element.get("channel", ""),
                        **gap(
                            "unaddressed_reveal",
                            FIX_PLANNER,
                            f"reveal.when={when} 인데 question_id가 비어 어느 문항의 피드백인지 알 수 없다",
                            scope="rule",
                        ),
                    }
                )
                continue
            bucket = reveals[when].setdefault(question_id, [])
        elif when in ("beat", "on_page"):
            bucket = reveals[when].setdefault(index, [])
        else:
            bucket = reveals["scene_enter"]
        for text in texts:
            if text not in bucket:
                bucket.append(text)
    return reveals, gaps


def build_pace_steps(reveals: dict) -> list[dict]:
    """이 화면의 대사·장을 끝까지 넘기는 조작.

    여정 케이스는 화면을 코드로 옮기지 않고 걷는다. 출구 버튼이 마지막 대사 뒤에야 나타나는
    구현은 정당한데(reveal이 그 시점을 계약으로 들고 있다), 여정이 대사를 안 넘기고 출구만
    찾으면 그 정당한 구현이 실패로 잡힌다. 화면에 들어가면 먼저 끝까지 넘긴다.
    """
    steps: list[dict] = []
    if reveals["beat"]:
        steps.extend(
            {"action": "advance_beat", "values": [], "question_id": ""} for _ in range(max(reveals["beat"]))
        )
    if reveals["on_page"]:
        steps.extend(
            {"action": "advance_page", "values": [], "question_id": ""} for _ in range(max(reveals["on_page"]))
        )
    return steps


def build_timing_cases(section: dict, reveals: dict) -> list[dict]:
    """화면 진입 시점과, 조작으로 넘겨야 나오는 시점을 각각 케이스로 만든다."""
    cases: list[dict] = []
    section_id = section["id"]

    if reveals["scene_enter"]:
        cases.append(
            text_case(
                case_id=f"case_{section_id}_text",
                section_id=section_id,
                intent=f"{section_id} 화면에 들어가면 읽어야 할 문구가 노출된다",
                steps=[],
                texts=reveals["scene_enter"],
            )
        )

    # 장 넘김 UI는 대사가 끝나야 나타날 수 있다(실측: 대사 소진 전에는 page-next가 숨어 있다).
    # 대사 케이스는 진입 직후부터 세지만, 장 케이스는 대사를 다 넘긴 뒤부터 센다.
    beat_lead = [
        {"action": "advance_beat", "values": [], "question_id": ""}
        for _ in range(max(reveals["beat"]) if reveals["beat"] else 0)
    ]
    for when, action, label, lead in (
        ("beat", "advance_beat", "대사", []),
        ("on_page", "advance_page", "장", beat_lead),
    ):
        for index in sorted(reveals[when]):
            cases.append(
                text_case(
                    case_id=f"case_{section_id}_{when}_{index}",
                    section_id=section_id,
                    intent=f"{label}를 {index}번 넘기면 그 시점의 문구가 노출된다",
                    steps=lead + [{"action": action, "values": [], "question_id": ""} for _ in range(index)],
                    texts=reveals[when][index],
                )
            )
    return cases


def build_flow_case(
    section: dict, section_ids: set, interaction_ids: set, lead_steps: list[dict] | None = None
) -> tuple[dict | None, list[dict]]:
    """이 화면에서 다음 화면으로 실제로 넘어가지는지 확인한다.

    다른 케이스는 전부 `__contentHarnessShowScene`으로 목적지에 바로 간다. 케이스를 격리하려면
    그래야 하지만, 그것만 있으면 **전환 버튼이 전부 죽어 있어도 모든 케이스가 통과한다.**
    도달 가능성은 여기서만 확인된다.

    화면마다 하나씩 만들고 처음부터 끝까지 걷지는 않는다. 통짜로 걸으면 앞에서 한 번 막힐 때
    뒤가 전부 죽어 어디가 문제인지 짚을 수 없다.
    """
    advance = section.get("advance") or {}
    target = advance.get("to_section_id", "")
    if not target:
        return None, []

    # schema의 pattern은 형태만 본다. 없는 화면을 가리켜도 통과하고, 그러면 이 케이스가 영영
    # 실패하면서 원인이 planner에 있는데 HTML 결함처럼 보인다. 같은 파일 안의 참조라 여기서 대조한다.
    gaps: list[dict] = []
    if target not in section_ids:
        return None, [
            gap(
                "dangling_advance",
                FIX_PLANNER,
                f"advance.to_section_id={target!r} 가 sections에 없다",
                scope="rule",
            )
        ]
    interaction = advance.get("interaction_id", "")
    if interaction and interaction not in interaction_ids:
        # 실행은 to_section_id 만 쓰므로 케이스는 만든다. 다만 planner가 없는 조작을 출구로
        # 적었다는 뜻이라 builder가 무엇을 만들지 알 수 없다.
        gaps.append(
            gap(
                "dangling_interaction",
                FIX_PLANNER,
                f"advance.interaction_id={interaction!r} 가 interactions에 없다",
                scope="rule",
            )
        )

    return {
        "id": f"case_{section['id']}_advance",
        "kind": "flow",
        "section_id": section["id"],
        "question_id": "",
        "input_type": "",
        "intent": f"{section['id']} 에서 진행 조작으로 {target} 에 도달한다",
        "steps": [*(lead_steps or []), {"action": "activate", "values": [target], "question_id": ""}],
        "expect": [
            {"kind": "scene_active", "value": target},
            {"kind": "no_console_error", "value": ""},
        ],
    }, gaps


def build_journey_case(
    planner_output: dict, correct_steps: dict[str, list[dict]], pace_steps: dict[str, list[dict]]
) -> dict | None:
    """첫 화면부터 마지막까지 실제로 걸어서 통과한다.

    다른 케이스는 전부 화면을 JS로 옮겨 놓고 시작하므로 "학습자가 여기까지 올 수 있는가"에
    답하지 못한다. 이 케이스만 처음부터 조작으로만 간다 — 문항을 만나면 풀고, 출구를 누르고,
    다음 화면으로. 끝까지 도달하면 그 콘텐츠는 통과 가능하다.

    하나만 만든다. 통짜로 걷는 케이스는 앞에서 막히면 뒤가 전부 죽어 국소화에 쓸 수 없고,
    국소화는 화면별 flow 케이스가 이미 담당한다. 이건 "통과 가능한가" 하나에만 답한다.
    """
    sections = planner_output.get("sections", [])
    if not sections:
        return None
    advance_map = {s["id"]: (s.get("advance") or {}).get("to_section_id", "") for s in sections}

    steps: list[dict] = []
    walked = [sections[0]["id"]]
    current = sections[0]["id"]
    while True:
        # 대사·장을 먼저 끝까지 넘긴다. 문항과 출구가 마지막 대사 뒤에 나타나는 화면에서도
        # 학습자가 하는 그대로 도달하기 위해서다.
        steps.extend(pace_steps.get(current, []))
        steps.extend(correct_steps.get(current, []))
        target = advance_map.get(current, "")
        if not target or target in walked:
            break
        steps.append({"action": "activate", "values": [target], "question_id": ""})
        walked.append(target)
        current = target

    if len(walked) < 2:
        return None
    return {
        "id": "case_journey",
        "kind": "scenario",
        "section_id": walked[0],
        "question_id": "",
        "input_type": "",
        "intent": f"첫 화면부터 조작만으로 {walked[-1]} 까지 끝까지 통과한다 ({len(walked)}화면)",
        "steps": steps,
        "expect": [
            {"kind": "scene_active", "value": walked[-1]},
            {"kind": "no_console_error", "value": ""},
        ],
    }


def text_case(*, case_id: str, section_id: str, intent: str, steps: list[dict], texts: list[str]) -> dict:
    return {
        "id": case_id,
        "kind": "scene",
        "section_id": section_id,
        "question_id": "",
        "input_type": "",
        "intent": intent,
        "steps": steps,
        "expect": [{"kind": "text_visible", "value": text} for text in texts]
        + [{"kind": "no_console_error", "value": ""}],
    }


def build_question_cases(section_id: str, question: dict, reveals: dict) -> tuple[list[dict], dict]:
    input_type = question.get("input_type", "")
    choices = question.get("choices", [])
    correct_labels = [c["label"] for c in choices if c.get("correct")]
    wrong_labels = [c["label"] for c in choices if not c.get("correct")]

    # 조작 방식을 실행기가 모르면 값을 아무리 잘 뽑아도 밀 수가 없다. 먼저 본다.
    if input_type not in SUPPORTED_INPUT_TYPES:
        return [], gap(
            "unsupported_interaction",
            FIX_REPO,
            f"input_type={input_type!r} 는 실행기가 미는 방법을 모른다",
        )

    # step은 자족적이어야 한다. 여러 문항을 지나는 여정 케이스에서는 케이스 하나의
    # question_id로 모든 step을 해석할 수 없다.
    owner = question["id"]
    extra_correct_expect: list[dict] = []
    if input_type == "hotspot":
        # 그림 위에서 정답 자리를 여러 개 고르는 방식이다. 어디가 정답인지는 spec이 아니라
        # 화면이 `data-qa-correct`로 들고 있으므로 좌표를 실을 필요가 없다. 대신 planner가 말한
        # 정답 개수는 실어서, 화면이 표시한 정답 자리 수와 어긋나면 잡는다.
        correct_step = {"action": "select_all_correct", "values": [], "question_id": owner}
        wrong_step = {"action": "select_wrong", "values": [], "question_id": owner}
        count = target_count(question.get("answer", ""))
        if count:
            extra_correct_expect.append({"kind": "correct_target_count", "value": count})
    elif choices:
        if not correct_labels:
            return [], gap("bad_choices", FIX_PLANNER, "choices에 correct=true가 없다")
        if not wrong_labels:
            return [], gap("bad_choices", FIX_PLANNER, "choices에 오답 보기가 없어 오답 케이스를 만들 수 없다")
        correct_step = {"action": action_for(input_type, correct=True), "values": [], "question_id": owner}
        wrong_step = {"action": action_for(input_type, correct=False), "values": [], "question_id": owner}
    else:
        values = numeric_blanks(question.get("answer", ""))
        if values is None:
            return [], gap(
                "unreadable_answer",
                FIX_PLANNER,
                f"input_type={input_type} answer={question.get('answer', '')!r} 에서 실행 값을 뽑지 못했다",
            )
        correct_step = {"action": value_action_for(input_type, correct=True), "values": values, "question_id": owner}
        wrong_step = {"action": value_action_for(input_type, correct=False), "values": wrong_values(values), "question_id": owner}

    question_id = question["id"]
    feedback = question.get("feedback", {})
    # 판정 뒤에 나타나는 문구는 두 곳에서 온다. 문항이 직접 들고 있는 feedback 문구와,
    # elements가 reveal=on_correct/on_wrong로 이 문항을 가리키며 들고 있는 문구다. 합쳐서 단언한다.
    correct_texts = merge_texts(feedback.get("correct", ""), reveals["on_correct"].get(question_id, []))
    wrong_texts = merge_texts(feedback.get("wrong", ""), reveals["on_wrong"].get(question_id, []))

    cases = [
        {
            "id": f"case_{question_id}_correct",
            "kind": "question",
            "section_id": section_id,
            "question_id": question_id,
            "input_type": input_type,
            "intent": "정답을 제출하면 정답 피드백이 나온다",
            "steps": [correct_step],
            "expect": [{"kind": "feedback_correct_visible", "value": ""}]
            + extra_correct_expect
            + [{"kind": "text_visible", "value": text} for text in correct_texts]
            + [{"kind": "no_console_error", "value": ""}],
        },
        {
            "id": f"case_{question_id}_wrong",
            "kind": "question",
            "section_id": section_id,
            "question_id": question_id,
            "input_type": input_type,
            "intent": "오답을 제출하면 오답 피드백이 나오고 다시 시도할 수 있다",
            "steps": [wrong_step],
            "expect": [
                {"kind": "feedback_wrong_visible", "value": ""},
                {"kind": "retry_available", "value": ""},
            ]
            + [{"kind": "text_visible", "value": text} for text in wrong_texts]
            + [{"kind": "no_console_error", "value": ""}],
        },
    ]

    attempt_case = build_attempt_case(section_id, question, wrong_step)
    if attempt_case is not None:
        cases.append(attempt_case)
    return cases, {}


def build_attempt_case(section_id: str, question: dict, wrong_step: dict) -> dict | None:
    """시도 횟수를 다 썼을 때 학습자가 갇히지 않는지 확인한다.

    story board가 이 규칙을 정해 두고도 아무도 검증하지 않으면, 틀린 채로 진행이 막히는
    화면이 그대로 나간다. 규칙이 없으면 케이스를 만들지 않는다 — 없는 규칙을 요구하지 않는다.
    """
    policy = question.get("attempt_policy") or {}
    max_attempts = policy.get("max_attempts", 0)
    on_exhausted = policy.get("on_exhausted", [])
    if not max_attempts or not on_exhausted:
        return None

    expect: list[dict] = []
    if "reveal_answer" in on_exhausted:
        # 값 입력 문항만 정답 값을 실어 보낸다. 값을 안 실으면 "표시 속성이 붙었는가"밖에 못 묻고,
        # 그건 학습자가 보는 것이 아니라 구현이 남긴 자국이기 때문이다.
        # 보기·hotspot 문항은 반대다 — 정답 문구가 처음부터 보기로 떠 있어(개수 문항은 값이
        # 정답 그 자체가 아니어서) 값을 실으면 공개를 구현하지 않아도 무조건 통과한다.
        # 이 문항들은 값을 비워 실행기가 표시 속성으로만 판정하게 한다.
        attribute_only = bool(question.get("choices")) or question.get("input_type") == "hotspot"
        expect.append(
            {"kind": "answer_revealed", "value": "" if attribute_only else question.get("answer", "")}
        )
    if "advance" in on_exhausted:
        expect.append({"kind": "advanced", "value": ""})

    return {
        "id": f"case_{question['id']}_attempts",
        "kind": "question",
        "section_id": section_id,
        "question_id": question["id"],
        "input_type": question.get("input_type", ""),
        "intent": f"{max_attempts}번 틀리면 {'/'.join(on_exhausted)} 로 학습자가 갇히지 않는다",
        "steps": [dict(wrong_step) for _ in range(max_attempts)],
        "expect": expect + [{"kind": "no_console_error", "value": ""}],
    }


def merge_texts(feedback_text: str, revealed_texts: list[str]) -> list[str]:
    merged: list[str] = []
    for text in [feedback_text.strip(), *revealed_texts]:
        if text and text not in merged:
            merged.append(text)
    return merged


def gap(kind: str, fixable_by: str, reason: str, scope: str = "question") -> dict:
    """파생하지 못한 것 하나. `scope`는 이 결손이 문항 전체를 덮는지 규칙 하나인지 가른다."""
    return {
        "kind": kind,
        "scope": scope,
        "fixable_by": fixable_by,
        "reason": reason,
    }


def action_for(input_type: str, correct: bool) -> str:
    if input_type == "drag_drop":
        return "drag_to_correct" if correct else "drag_to_wrong"
    return "select_correct" if correct else "select_wrong"


def value_action_for(input_type: str, correct: bool) -> str:
    if input_type == "drag_drop":
        return "drag_values_correct" if correct else "drag_values_wrong"
    return "enter_answer" if correct else "enter_wrong_answer"


def numeric_blanks(answer: str) -> list[str] | None:
    """정답 문자열에서 채워 넣을 숫자를 뽑는다.

    planner마다 표기가 갈린다. 빈칸을 대괄호로 표시하기도 하고(`[12]시 [0]분`) 값만 쓰기도
    한다(`10`). 같은 schema·같은 프롬프트에서 둘 다 나왔으므로 어느 쪽도 오답이 아니고,
    파생기가 둘 다 읽는다. 대괄호가 있으면 그것이 빈칸의 개수와 순서를 말해 주므로 먼저 본다.
    """
    groups = [group.strip().strip(",").strip() for group in BRACKET_GROUP.findall(answer)]
    if groups:
        return groups if all(group.isdigit() for group in groups) else None
    bare = answer.strip()
    return [bare] if bare.isdigit() else None


def target_count(answer: str) -> str:
    """`정답 2개`, `▲모양 2개`처럼 개수로 적힌 정답에서 숫자만 뽑는다. 없으면 빈 문자열."""
    match = re.search(r"\d+", answer)
    return match.group(0) if match else ""


def wrong_values(values: list[str]) -> list[str]:
    """첫 칸만 확실히 틀린 값으로 바꾼다. 99를 넘기지 않게 감싼다."""
    wrong = list(values)
    first = int(wrong[0])
    wrong[0] = str(first + 1) if first < 99 else str(first - 1)
    return wrong


def collect_prose_only_rules(planner_output: dict) -> list[dict]:
    """산문에만 있고 문항에 연결되지 않은 판정 규칙을 찾아 남긴다.

    지금은 시도 횟수 규칙만 본다. 이런 규칙은 planner가 원문을 온전히 보존하고 있는데도
    (a) 산문이고 (b) 어느 문항에 걸리는지 주소가 없어서 실행 단언으로 못 바뀐다.
    같은 section의 문항이 `attempt_policy`를 채웠으면 주소가 생긴 것이므로 보고하지 않는다.
    """
    found: list[dict] = []
    seen: set[tuple[str, str]] = set()
    attempt_pattern = re.compile(r"\d+\s*회|\d+\s*번\s*오답")
    for section in planner_output.get("sections", []):
        if any(
            (question.get("attempt_policy") or {}).get("max_attempts")
            for question in section.get("questions", [])
        ):
            continue
        for element in section.get("elements", []):
            blob = f"{element.get('content', '')} {element.get('notes', '')}"
            match = attempt_pattern.search(blob)
            if not match:
                continue
            # 같은 화면에서 같은 규칙이 여러 줄에 걸쳐 있어도 사람이 내릴 결정은 하나다.
            key = (section["id"], match.group(0))
            if key in seen:
                continue
            seen.add(key)
            found.append(
                {
                    "kind": "attempt_policy",
                    "scope": "rule",
                    "fixable_by": FIX_PLANNER,
                    "section_id": section["id"],
                    "ref": element.get("channel", ""),
                    "reason": (
                        f"'{match.group(0)}' 시도 규칙이 산문에만 있고 questions[] 어느 항목에도 "
                        "연결되어 있지 않다"
                    ),
                }
            )
    return found


def format_decision_report(spec: dict) -> str:
    """파생하지 못한 것을 사람이 결정할 수 있는 형태로 요약한다. CLI와 runner가 같은 문안을 쓴다."""
    repo_items = [item for item in spec["underivable"] if item.get("fixable_by") == FIX_REPO]
    planner_items = [item for item in spec["underivable"] if item.get("fixable_by") == FIX_PLANNER]

    lines = ["=" * 72, "파생하지 못한 것이 있다. 진행 전에 정해야 한다.", "=" * 72]

    if repo_items:
        lines.append("")
        lines.append("[레포를 늘려야 하는 것] — builder가 고칠 수 없다. 실행기·계약이 모르는 것이다.")
        lines.extend(f"  · {item['section_id']}/{item['ref']} — {item['reason']}" for item in repo_items)

    if planner_items:
        lines.append("")
        lines.append("[planner가 안 들고 있는 것] — 위쪽에서 고칠 수 있다.")
        lines.extend(f"  · {item['section_id']}/{item['ref']} — {item['reason']}" for item in planner_items)

    uncovered = spec["coverage"]["questions_uncovered"]
    total = spec["coverage"]["questions_total"]
    if uncovered:
        lines.append("")
        lines.append(f"검증되지 않는 문항: {uncovered}/{total}")

    lines.append(
        "\n고를 것\n"
        "  ① 확장한다      실행기 action / planner schema를 늘린다. 이후 모든 차시가 쓴다\n"
        "  ② 넘어간다      `--accept-test-gaps` 로 다시 돌린다. 그 문항은 검증되지 않고 리포트에 남는다\n"
        "  ③ planner 고친다 이 상호작용을 이미 지원하는 방식으로 다시 설계한다"
    )
    return "\n".join(lines)


def build_coverage(planner_output: dict, cases: list[dict], underivable: list[dict]) -> dict:
    questions = [q for s in planner_output.get("sections", []) for q in s.get("questions", [])]
    covered = {c["question_id"] for c in cases if c["kind"] == "question"}
    text_total = sum(
        1
        for c in cases
        if c["kind"] == "scene"
        for e in c["expect"]
        if e["kind"] == "text_visible"
    )
    # 케이스를 하나도 못 얻은 문항 수. 이 값이 0이 아닌데 리포트가 PASS면 "전부 검증됨"으로
    # 오독되므로, 실행 리포트까지 그대로 실어 보낸다.
    uncovered = [item for item in underivable if item.get("scope") == "question"]
    return {
        "questions_total": len(questions),
        "questions_covered": len(covered),
        "questions_uncovered": len(uncovered),
        "question_cases": sum(1 for c in cases if c["kind"] == "question"),
        "scene_cases": sum(1 for c in cases if c["kind"] == "scene"),
        "text_assertions": text_total,
        "underivable_total": len(underivable),
        "needs_repo_change": sum(1 for item in underivable if item.get("fixable_by") == FIX_REPO),
        "needs_planner_change": sum(1 for item in underivable if item.get("fixable_by") == FIX_PLANNER),
    }
