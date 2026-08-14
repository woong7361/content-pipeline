"""test_spec을 실제 브라우저에서 실행한다. LLM 호출 0회.

test_spec.json은 데이터이고 실행 로직은 전부 여기 있다. spec은 자족적이어야 하므로 이 모듈은
planner를 읽지 않는다 — planner 구조가 바뀌어도 실행기는 흔들리지 않는다.

가장 중요한 규칙: **셀렉터가 아무것도 못 잡았을 때 통과를 반환하지 않는다.** hook이 없으면
`hook_missing`이고, 그건 "테스트 실패"가 아니라 "계약 위반"으로 따로 센다. 이 구분이 없으면
hook이 하나도 없는 HTML이 전 항목 통과로 나온다.

이 층이 답하는 것은 **있는가 · 도달하는가 · 동작하는가**까지다. 읽히는가(대비, 가려짐,
`opacity`)는 DOM으로 알 수 없고 픽셀을 봐야 하므로 `design_review`의 축이다. 두 축을 한 곳에
합치려 들면 JS 주입이 되돌아오고 판정이 중복된다.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from stages.scripts.narrate import narrate
from stages.visual_qa import build_show_scene_script, launch_browser


ACTION_TIMEOUT_MS = 1500
EXPECT_TIMEOUT_MS = 2000

# 파생기가 실제로 내보내는 것만 둔다. 아무도 내보내지 않는 action을 남겨두면 fixture가
# 시연할 수 없고, 커버리지 불변식이 그것을 영구 실패로 만든다. 필요해질 때 함께 넣는다.
KNOWN_ACTIONS = {
    "select_correct",
    "select_wrong",
    "drag_to_correct",
    "drag_to_wrong",
    "enter_answer",
    "enter_wrong_answer",
    "drag_values_correct",
    "drag_values_wrong",
    "advance_beat",
    "advance_page",
    "select_all_correct",
    "activate",
}
KNOWN_EXPECTS = {
    "feedback_correct_visible",
    "feedback_wrong_visible",
    "retry_available",
    "text_visible",
    "correct_target_count",
    "scene_active",
    "answer_revealed",
    "advanced",
    "no_console_error",
}

INPUT_SELECTOR = "[data-qa-choice], [data-qa-key], [data-qa-block]"

# 문항을 한 번에 하나씩 내보내는 화면에서, 그 문항까지 순서대로 풀지 않고 바로 확인하기 위한 통로.
# 화면 전환(`__contentHarnessShowScene`)과 같은 성격의 셋업이며 단위 케이스에서만 쓴다.
SHOW_QUESTION_SCRIPT = """
(questionId) => {
  if (typeof window.__contentHarnessShowQuestion === 'function') {
    window.__contentHarnessShowQuestion(questionId);
    return true;
  }
  return false;
}
"""

# 각 조작·단언이 어떤 값을 받는지. 빈 문자열이면 값을 받지 않는다.
# 시나리오 저작 프롬프트가 이 표를 그대로 싣는다 — 이름만 알려주면 값을 지어낸다(실측: `activate`에
# 화면 id 대신 interaction id, `answer_revealed`에 정답 대신 문항 id).
ACTION_VALUES = {
    "select_correct": "",
    "select_wrong": "",
    "select_all_correct": "",
    "drag_to_correct": "",
    "drag_to_wrong": "",
    "advance_beat": "",
    "advance_page": "",
    "enter_answer": "채울 칸마다 입력할 값을 순서대로. 칸이 하나면 값 하나",
    "enter_wrong_answer": "같은 형식의 틀린 값",
    "drag_values_correct": "빈칸에 넣을 값을 순서대로",
    "drag_values_wrong": "같은 형식의 틀린 값",
    "activate": "도착할 화면의 sections[].id 하나. interaction id가 아니다",
}
EXPECT_VALUES = {
    "feedback_correct_visible": "",
    "feedback_wrong_visible": "",
    "retry_available": "",
    "advanced": "",
    "no_console_error": "",
    "text_visible": "화면에서 읽혀야 할 문구 그대로",
    "correct_target_count": "정답 자리의 개수",
    "scene_active": "열려야 할 화면의 sections[].id",
    "answer_revealed": "값 입력 문항이면 그 정답 값(문항 id가 아니다). 보기·hotspot 문항이면 빈 문자열",
}


def run_functional_test(
    *,
    spec_path: Path,
    html_path: Path,
    output_path: Path,
    screenshots_dir: Path,
    timeout_seconds: int = 60,
) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    html_uri = html_path.resolve().as_uri()
    show_scene = build_show_scene_script()

    results: list[dict] = []
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        try:
            for case in spec["cases"]:
                results.append(
                    run_case(
                        context=context,
                        case=case,
                        html_uri=html_uri,
                        show_scene=show_scene,
                        screenshots_dir=screenshots_dir,
                        timeout_seconds=timeout_seconds,
                    )
                )
        finally:
            context.close()
            browser.close()

    report = build_report(spec=spec, results=results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def run_case(
    *,
    context: Any,
    case: dict,
    html_uri: str,
    show_scene: str,
    screenshots_dir: Path,
    timeout_seconds: int,
) -> dict:
    """케이스마다 새 페이지를 연다. 시도 횟수·진행 상태가 케이스 사이로 새지 않게 격리한다."""
    page = context.new_page()
    console_errors: list[str] = []
    page.on("console", lambda message: collect_console_error(console_errors, message))
    page.on("pageerror", lambda error: console_errors.append(str(error)))

    # 시나리오는 학습자가 실제로 겪는 경로를 재현하는 층이다. 화면을 JS로 옮겨 놓고 시작하면
    # "여기까지 올 수 있는가"를 건너뛴 채 그 화면만 보게 되고, 그건 E2E가 아니다.
    # 규칙을 주석에만 두면 다음 수정에서 새어 들어오므로 실행 중에 막는다.
    if case["kind"] == "scenario":
        page.evaluate = forbid_evaluate

    failures: list[dict] = []
    try:
        page.goto(html_uri, wait_until="networkidle", timeout=timeout_seconds * 1000)
        page.wait_for_timeout(200)
        # 단위 케이스는 목적지 화면으로 바로 간다. 9번째 화면의 문항을 보려고 매번 처음부터
        # 걸으면 앞에서 한 번 막힐 때 뒤가 전부 죽어 어디가 깨졌는지 짚을 수 없다.
        #
        # 화면 이동 스크립트는 셀렉터가 안 잡히면 조용히 아무것도 안 한다. 그대로 두면 조인 키
        # (`data-qa-scene` = planner section id) 불일치가 "이동 실패" 한 마디 대신, 첫 화면에서
        # 실행된 케이스들의 hook_missing/action_failed 수십 건으로 흩어져 보고된다(실측:
        # 65126dad run은 12개 화면 중 0개가 일치). 이동하기 전에 조인부터 확인한다.
        if case["kind"] != "scenario" and case["section_id"]:
            if page.locator(f'[data-qa-scene="{case["section_id"]}"]').count() == 0:
                failures.append(
                    failure(
                        case,
                        "hook_missing",
                        "data-qa-scene",
                        f'[data-qa-scene="{case["section_id"]}"] 가 없다. '
                        "이 값은 planner sections[].id 를 글자 그대로 써야 검증기가 그 화면을 연다",
                    )
                )
            else:
                page.evaluate(show_scene, case["section_id"])
                page.wait_for_timeout(200)
        # 화면에 도착해도 그 문항이 지금 떠 있다는 보장은 없다. 퀴즈가 문항을 하나씩 갈아 끼우면
        # 앞 문항을 다 풀어야 뒤 문항이 나오고, 그러면 뒤 문항은 단위 케이스로 확인할 수 없다.
        if not failures and case["kind"] == "question" and case["question_id"]:
            page.evaluate(SHOW_QUESTION_SCRIPT, case["question_id"])
            page.wait_for_timeout(200)

        if not failures:
            root_error = resolve_question_root(page, case)
            if root_error:
                failures.append(root_error)
        if not failures:
            for step in case["steps"]:
                step_error = run_action(page, case, step)
                if step_error:
                    failures.append(step_error)
                    break
                page.wait_for_timeout(300)

        if not failures:
            for expectation in case["expect"]:
                expect_error = check_expectation(page, case, expectation, console_errors)
                if expect_error:
                    failures.append(expect_error)
    except PlaywrightError as error:
        failures.append(failure(case, "runtime_error", "", str(error)))

    screenshot = ""
    if failures:
        screenshot_path = screenshots_dir / f"{case['id']}.png"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            screenshot = screenshot_path.name
        except PlaywrightError:
            screenshot = ""
    page.close()

    for item in failures:
        item["screenshot"] = screenshot
    return {
        "case_id": case["id"],
        "kind": case["kind"],
        "section_id": case["section_id"],
        "status": "REJECT" if failures else "PASS",
        "scenario": narrate(case),
        "failures": failures,
    }


def resolve_question_root(page: Any, case: dict) -> dict | None:
    if case["kind"] != "question":
        return None
    locator = page.locator(f'[data-qa-question="{case["question_id"]}"]')
    if locator.count() == 0:
        return failure(
            case,
            "hook_missing",
            "data-qa-question",
            f'[data-qa-question="{case["question_id"]}"] 를 찾지 못했다',
        )
    return None


def run_action(page: Any, case: dict, step: dict) -> dict | None:
    action = step["action"]
    if action not in KNOWN_ACTIONS:
        return failure(case, "unknown_action", action, f"실행기가 모르는 action: {action}")

    if action == "activate":
        # 다음 화면으로 나가는 출구. hook이 목적지를 값으로 들고 있어 분기가 있어도 지목된다.
        target = step["values"][0] if step["values"] else ""
        selector = f'[data-qa-advance="{target}"]' if target else "[data-qa-advance]"
        control = visible_control(page, selector)
        if control is None:
            return failure(case, "hook_missing", "data-qa-advance", f"{selector} 가 없거나 보이지 않는다")
        try:
            control.click(timeout=ACTION_TIMEOUT_MS)
        except PlaywrightTimeout as error:
            return failure(case, "action_failed", action, str(error).splitlines()[0])
        return None

    # 화면 단위 조작은 문항 root가 없다. 씬 안에서 찾는다.
    if action in ("advance_beat", "advance_page"):
        hook = "data-qa-beat-next" if action == "advance_beat" else "data-qa-page-next"
        control = visible_control(page, f"[{hook}]")
        if control is None:
            return failure(case, "hook_missing", hook, f"[{hook}] 이 없거나 보이지 않는다")
        try:
            control.click(timeout=ACTION_TIMEOUT_MS)
        except PlaywrightTimeout as error:
            return failure(case, "action_failed", action, str(error).splitlines()[0])
        return None

    # 여정 케이스는 한 케이스가 여러 문항을 지난다. 그래서 문항은 케이스가 아니라 step이 정한다.
    owner = step.get("question_id") or case["question_id"]
    root = page.locator(f'[data-qa-question="{owner}"]').first
    try:
        if action == "select_all_correct":
            # 정답 자리가 여럿인 방식(그림에서 모양 찾기 등). 표시된 정답을 모두 누른다.
            targets = root.locator('[data-qa-choice][data-qa-correct="true"]')
            if targets.count() == 0:
                return failure(case, "hook_missing", "data-qa-correct", "정답으로 표시된 자리가 없다")
            for index in range(targets.count()):
                targets.nth(index).click(timeout=ACTION_TIMEOUT_MS)
                page.wait_for_timeout(150)

        elif action in ("select_correct", "select_wrong"):
            wanted = "true" if action == "select_correct" else "false"
            target = root.locator(f'[data-qa-choice][data-qa-correct="{wanted}"]')
            if target.count() == 0:
                return failure(case, "hook_missing", "data-qa-choice", f'data-qa-correct="{wanted}" 보기가 없다')
            target.first.click(timeout=ACTION_TIMEOUT_MS)

        elif action in ("drag_to_correct", "drag_to_wrong"):
            wanted = "true" if action == "drag_to_correct" else "false"
            source = root.locator(f'[data-qa-choice][data-qa-correct="{wanted}"]')
            slot = root.locator("[data-qa-slot]")
            if source.count() == 0 or slot.count() == 0:
                return failure(case, "hook_missing", "data-qa-choice/data-qa-slot", "드래그 원본 또는 대상이 없다")
            click_through(source.first, slot.first)

        elif action in ("drag_values_correct", "drag_values_wrong"):
            slots = root.locator("[data-qa-slot]")
            if slots.count() == 0:
                return failure(case, "hook_missing", "data-qa-slot", "드롭 대상이 없다")
            for index, value in enumerate(step["values"]):
                block = root.locator(f'[data-qa-block="{value}"]')
                if block.count() == 0:
                    return failure(case, "hook_missing", "data-qa-block", f'값 {value} 블록이 없다')
                if slots.count() <= index:
                    return failure(case, "hook_missing", "data-qa-slot", f"{index + 1}번째 빈칸이 없다")
                click_through(block.first, slots.nth(index))

        elif action in ("enter_answer", "enter_wrong_answer"):
            # 키패드는 화면·문항마다 하나씩 있어 페이지 전체에 여러 벌일 수 있다. 페이지 전체
            # 첫 번째를 집으면 숨은 화면의 키를 누르게 된다 — visible_control 주석의 그 실패 모드다.
            for index, value in enumerate(step["values"]):
                blank = root.locator("[data-qa-blank]")
                if blank.count() > index:
                    blank.nth(index).click(timeout=ACTION_TIMEOUT_MS)
                for digit in value:
                    key = visible_control(page, f'[data-qa-key="{digit}"]')
                    if key is None:
                        return failure(case, "hook_missing", "data-qa-key", f"키패드 키 {digit} 가 없거나 보이지 않는다")
                    key.click(timeout=ACTION_TIMEOUT_MS)
            submit = visible_control(page, '[data-qa-key="submit"]')
            if submit is None:
                return failure(case, "hook_missing", "data-qa-key", 'data-qa-key="submit" 이 없거나 보이지 않는다')
            submit.click(timeout=ACTION_TIMEOUT_MS)

    except PlaywrightTimeout as error:
        return failure(case, "action_failed", action, str(error).splitlines()[0])
    return None


def click_through(source: Any, target: Any) -> None:
    """옮기기를 끌지 않고 두 번 눌러서 수행한다.

    HTML5 native DnD(`draggable` + `dragstart`)는 driver가 합성한 마우스 이벤트로 발화하지
    않으므로 `drag_to`로는 밀 수 없다. 계약이 "끌 수 있는 것은 탭 두 번으로도 같은 결과에
    도달해야 한다"를 요구하므로(드래그 전용 조작은 접근성 장벽이기도 하다) 이 경로를 민다.

    따라서 이 단언이 보증하는 것은 **결과에 도달할 수 있다**이지 드래그 제스처 자체가
    동작한다가 아니다. 제스처는 이 층에서 검증되지 않는다.
    """
    source.click(timeout=ACTION_TIMEOUT_MS)
    target.click(timeout=ACTION_TIMEOUT_MS)


# 문항을 지목해야 판정할 수 있는 단언. 여정·시나리오 케이스는 케이스 레벨 question_id가 없으므로
# step이 지목한 문항으로 해석한다.
QUESTION_SCOPED_EXPECTS = {"advanced", "retry_available", "answer_revealed", "correct_target_count"}


def question_owner(case: dict) -> str:
    """이 케이스의 문항 단언이 가리키는 문항.

    단위 케이스는 케이스가 문항을 들고 있지만, 여러 문항을 지나는 케이스는 step이 들고 있다.
    마지막으로 조작한 문항이 단언의 대상이다 — 시나리오는 조작의 나열이고, 문항 단언은
    직전 조작의 결과를 묻는 것이기 때문이다.
    """
    if case["question_id"]:
        return case["question_id"]
    for step in reversed(case["steps"]):
        if step.get("question_id"):
            return step["question_id"]
    return ""


def check_expectation(page: Any, case: dict, expectation: dict, console_errors: list[str]) -> dict | None:
    kind = expectation["kind"]
    if kind not in KNOWN_EXPECTS:
        return failure(case, "unknown_expect", kind, f"실행기가 모르는 expect: {kind}")

    owner = question_owner(case)
    if kind in QUESTION_SCOPED_EXPECTS and not owner:
        # HTML 결함이 아니라 spec 결함이다. hook_missing으로 내면 refiner가 없는 결함을 고친다.
        return failure(
            case,
            "spec_error",
            kind,
            f"{kind} 는 문항 단언인데 케이스도 step도 문항을 지목하지 않았다",
        )

    if kind == "no_console_error":
        if console_errors:
            return failure(case, "expect_failed", kind, console_errors[0][:200])
        return None

    if kind == "text_visible":
        # 로케이터 가시성은 `visibility:hidden`과 크기 0으로 접힌 요소를 걸러낸다. innerText 조회는
        # 그 둘을 "보인다"로 통과시킨다.
        #
        # 다만 `opacity:0`과 다른 요소에 덮인 문구는 여기서도 통과한다(실측 확인). DOM만 봐서는
        # 알 수 없고, 계산된 스타일을 조회하려면 JS를 주입해야 한다. 그건 이 층에서 없애기로 한
        # 것이므로 잡지 않는다. **읽히는가는 픽셀을 보는 design_review의 축이다.**
        # 이 층이 답하는 것은 있는가/도달하는가/동작하는가까지다.
        needle = expectation["value"]
        if locator_visible(page.get_by_text(needle, exact=False)):
            return None
        # 이미지에 구운 문구는 텍스트 노드가 없다. planner가 alt_text로 보존하게 한 계약을 여기서 읽는다.
        if locator_visible(page.get_by_alt_text(needle, exact=False), timeout=500):
            return None
        return failure(case, "expect_failed", kind, f"화면에서 읽을 수 없는 문구: {needle}")

    if kind == "scene_active":
        target = page.locator(f'[data-qa-scene="{expectation["value"]}"]')
        if target.count() == 0:
            return failure(case, "hook_missing", "data-qa-scene", f'[data-qa-scene="{expectation["value"]}"] 가 없다')
        try:
            target.first.wait_for(state="visible", timeout=EXPECT_TIMEOUT_MS)
        except PlaywrightTimeout:
            return failure(case, "expect_failed", kind, f'{expectation["value"]} 화면이 열리지 않았다')
        return None

    if kind == "correct_target_count":
        selector = f'[data-qa-question="{owner}"] [data-qa-choice][data-qa-correct="true"]'
        targets = page.locator(selector)
        if targets.count() == 0:
            return failure(case, "hook_missing", "data-qa-correct", "정답으로 표시된 자리가 없다")
        if str(targets.count()) != expectation["value"]:
            return failure(
                case,
                "expect_failed",
                kind,
                f"정답 자리가 {expectation['value']}개여야 하는데 화면에는 {targets.count()}개다",
            )
        return None

    if kind == "answer_revealed":
        # 공개된 정답을 학습자가 어떻게 알게 되는지는 입력 방식에 따라 다르다.
        #   값 입력(키패드·블록) — 화면에 없던 정답 값이 나타난다. 그대로 관찰된다.
        #   보기 선택·hotspot — 정답 문구는 처음부터 보기로 떠 있다(개수 문항은 값이 정답 그
        #     자체가 아니다). 문구 노출로 판정하면 공개를 구현하지 않아도 무조건 통과하므로,
        #     파생기가 value를 비워 보내고 여기서는 표시 속성으로만 판정한다.
        if expectation["value"] and locator_visible(
            page.get_by_text(expectation["value"], exact=False), timeout=500
        ):
            return None
        marked = page.locator(
            f'[data-qa-question="{owner}"] [data-qa-correct="true"][data-qa-revealed="true"]'
        )
        if marked.count() > 0:
            return None
        return failure(
            case,
            "expect_failed",
            kind,
            f"시도를 다 썼는데 정답({expectation['value']})이 드러나지 않았다",
        )

    if kind == "advanced":
        root = page.locator(f'[data-qa-question="{owner}"]')
        if root.count() == 0:
            return failure(case, "hook_missing", "data-qa-question", "문항 root를 다시 찾지 못했다")
        if root.first.is_visible():
            return failure(case, "expect_failed", kind, "시도를 다 썼는데 같은 문항에 머물러 있다")
        return None

    if kind == "retry_available":
        root = page.locator(f'[data-qa-question="{owner}"]')
        if root.count() == 0:
            return failure(case, "hook_missing", "data-qa-question", "문항 root를 다시 찾지 못했다")
        if root.first.get_attribute("data-qa-locked") == "true":
            return failure(case, "expect_failed", kind, "문항이 잠겨 다시 시도할 수 없다")
        # disabled 속성만 보면 투명 레이어에 덮여 클릭이 안 되는 상태를 "가능"으로 판정한다.
        # trial 클릭은 실제로 누를 수 있는지까지 확인하고 누르지는 않는다.
        inputs = root.first.locator(INPUT_SELECTOR)
        if inputs.count() == 0:
            return failure(case, "hook_missing", "data-qa-choice", "다시 시도할 입력 요소가 없다")
        for index in range(inputs.count()):
            try:
                inputs.nth(index).click(trial=True, timeout=500)
                return None
            except PlaywrightError:
                continue
        return failure(case, "expect_failed", kind, "오답 뒤에 다시 누를 수 있는 입력이 없다")

    wanted = "correct" if kind == "feedback_correct_visible" else "wrong"
    selector = f'[data-qa-feedback="{wanted}"]'
    # count()==0 을 통과로 처리하지 않는다. hook이 없는 것과 hook이 안 뜨는 것은 다른 결함이고,
    # 여기서 섞으면 hook이 하나도 없는 HTML이 전 항목 통과로 나온다.
    if page.locator(selector).count() == 0:
        return failure(case, "hook_missing", "data-qa-feedback", f"{selector} 가 없다")
    # 피드백 표면은 문항마다 하나씩이라 페이지 전체에 여러 개다. `.first`로 기다리면 앞 화면의
    # 숨은 표면에 묶여 지금 뜬 피드백을 못 보고 시간 초과된다 — visible_control 주석의 그 실패
    # 모드다. wait_for_selector는 매칭 중 **하나라도** 보이면 돌아온다.
    try:
        page.wait_for_selector(selector, state="visible", timeout=EXPECT_TIMEOUT_MS)
    except PlaywrightTimeout:
        return failure(case, "expect_failed", kind, f"{selector} 가 {EXPECT_TIMEOUT_MS}ms 안에 보이지 않았다")
    return None


def forbid_evaluate(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "시나리오 케이스는 JS를 주입할 수 없다. 화면 이동과 상태 변경은 실제 조작으로만 한다."
    )


def visible_control(page: Any, selector: str) -> Any:
    """화면 단위 조작 hook은 화면마다 하나씩 있어 페이지 전체에 여러 개다.

    그래서 페이지 전체에서 첫 번째를 집으면 **숨은 화면의 것**을 누르게 되고, 클릭이 시간 초과로
    끝난다(실측: `advance_beat` 15건, `advance_page` 11건이 이 이유로 실패했다).
    지금 보이는 것만 고른다 — 학습자가 누를 수 있는 것도 그것뿐이다.
    """
    visible = page.locator(f"{selector}:visible")
    return visible.first if visible.count() else None


def locator_visible(locator: Any, timeout: int = EXPECT_TIMEOUT_MS) -> bool:
    """매칭된 것 **전부**를 훑어 하나라도 보이면 참.

    `.first.wait_for(visible)`는 첫 매칭 하나에 묶인다. 같은 문구가 앞 화면에도 숨어 있으면
    지금 화면에 멀쩡히 보이는 문구를 놓치고 시간 초과된다 — visible_control 주석의 그 실패 모드다.
    """
    deadline = time.monotonic() + timeout / 1000
    while True:
        try:
            for index in range(locator.count()):
                if locator.nth(index).is_visible():
                    return True
        except PlaywrightError:
            return False
        if time.monotonic() >= deadline:
            return False
        locator.page.wait_for_timeout(100)


def collect_console_error(console_errors: list[str], message: Any) -> None:
    if message.type == "error":
        console_errors.append(message.text)


def failure(case: dict, reason: str, subject: str, detail: str) -> dict:
    return {
        "case_id": case["id"],
        "kind": case["kind"],
        "section_id": case["section_id"],
        "question_id": case["question_id"],
        "reason": reason,
        "subject": subject,
        "detail": detail,
        "screenshot": "",
    }


def build_report(*, spec: dict, results: list[dict]) -> dict:
    failures = [item for result in results for item in result["failures"]]
    hook_missing = [item for item in failures if item["reason"] == "hook_missing"]
    failed_cases = [result for result in results if result["failures"]]
    total = len(results)
    passed = total - len(failed_cases)
    coverage = spec.get("coverage", {})
    # 애초에 케이스를 못 얻은 문항 수를 verdict 옆에 함께 싣는다. 이게 빠지면 `passed=30/30`이
    # "전부 검증됨"으로 읽히는데, 실제로는 몇 문항이 조용히 빠져 있을 수 있다.
    unsupported = coverage.get("questions_uncovered", 0)
    return {
        "spec_version": spec.get("spec_version", ""),
        "source_planner": spec.get("source_planner", ""),
        "total": total,
        "passed": passed,
        "failed": len(failed_cases),
        "hook_missing": len(hook_missing),
        "unsupported": unsupported,
        "questions_total": coverage.get("questions_total", 0),
        "questions_covered": coverage.get("questions_covered", 0),
        # unsupported는 verdict를 막지 않는다. builder가 고칠 수 없는 것을 게이트로 세우면
        # refine 루프가 영원히 돈다. 대신 집계되어 리포트에 남는다.
        "verdict": "PASS" if passed == total else "REJECT",
        "underivable": spec.get("underivable", []),
        "scenarios": [
            {
                "case_id": result["case_id"],
                "kind": result["kind"],
                "section_id": result["section_id"],
                "status": result["status"],
                **result["scenario"],
                "problems": [item["detail"] for item in result["failures"]],
            }
            for result in results
        ],
        "failures": failures,
    }
