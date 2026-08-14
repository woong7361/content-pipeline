"""케이스를 사람이 읽는 문장으로 옮긴다.

시나리오 형식을 **출력에만** 쓴다. 입력을 자연어로 만들면 같은 조작이 run마다 다른 문장이 되어
표류하지만(실측: `hotspot` -> `hotspot_multi`), 닫힌 enum을 문장으로 옮기는 것은 표류하지 않는다.

원자 케이스 수십 개를 그대로 늘어놓으면 사람이 못 읽고, 못 읽으면 최종 검수가 형식이 된다.
"""

from __future__ import annotations


ACTION_PHRASES = {
    "select_correct": "정답 보기를 고른다",
    "select_wrong": "오답 보기를 고른다",
    "select_all_correct": "정답 자리를 모두 고른다",
    "enter_answer": "정답 값을 입력한다",
    "enter_wrong_answer": "오답 값을 입력한다",
    "drag_to_correct": "정답 조각을 자리로 옮긴다",
    "drag_to_wrong": "오답 조각을 자리로 옮긴다",
    "drag_values_correct": "값 조각을 순서대로 옮긴다",
    "drag_values_wrong": "값 조각을 잘못된 순서로 옮긴다",
    "advance_beat": "다음 대사로 넘긴다",
    "advance_page": "다음 장으로 넘긴다",
    "activate": "진행 조작을 누른다",
}

EXPECT_PHRASES = {
    "feedback_correct_visible": "정답 피드백이 보인다",
    "feedback_wrong_visible": "오답 피드백이 보인다",
    "retry_available": "다시 시도할 수 있다",
    "answer_revealed": "정답이 공개된다",
    "advanced": "그 문항에서 벗어난다",
    "no_console_error": "오류가 없다",
}


def narrate(case: dict) -> dict:
    return {
        "given": given_phrase(case),
        "when": when_phrases(case["steps"]),
        "then": [then_phrase(item) for item in case["expect"]],
    }


def given_phrase(case: dict) -> str:
    where = case["section_id"] or "첫 화면"
    if case["question_id"]:
        return f"{where} 화면의 {case['question_id']} 문항에서"
    return f"{where} 화면에서"


def when_phrases(steps: list[dict]) -> list[str]:
    """같은 조작이 이어지면 묶는다. '오답을 고른다'가 세 줄 뜨는 것보다 x3 이 읽힌다."""
    phrases: list[str] = []
    for step in steps:
        phrase = ACTION_PHRASES.get(step["action"], step["action"])
        if step["action"] == "activate" and step["values"]:
            phrase = f"{step['values'][0]} 로 가는 진행 조작을 누른다"
        elif step["values"]:
            phrase = f"{phrase} ({' '.join(step['values'])})"
        if phrases and phrases[-1][0] == phrase:
            phrases[-1][1] += 1
        else:
            phrases.append([phrase, 1])
    return [text if count == 1 else f"{text} x{count}" for text, count in phrases]


def then_phrase(item: dict) -> str:
    kind = item["kind"]
    if kind == "text_visible":
        return f"'{item['value']}' 가 화면에 보인다"
    if kind == "correct_target_count":
        return f"정답 자리가 {item['value']}개다"
    if kind == "scene_active":
        return f"{item['value']} 화면이 열린다"
    return EXPECT_PHRASES.get(kind, kind)


def render_scenario(case: dict, status: str, details: list[str]) -> list[str]:
    story = narrate(case)
    lines = [f"[{status}] {story['given']}"]
    for phrase in story["when"]:
        lines.append(f"        {phrase}")
    if not story["when"]:
        lines.append("        (조작 없음)")
    for phrase in story["then"]:
        lines.append(f"     -> {phrase}")
    for detail in details:
        lines.append(f"        ! {detail}")
    return lines
