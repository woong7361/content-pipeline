from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def validate_lesson_spec(spec: dict, schema_path: Path) -> list[str]:
    errors = [error.message for error in Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8"))).iter_errors(spec)]
    errors.extend(check_links(spec))
    return errors


def check_links(spec: dict) -> list[str]:
    errors: list[str] = []
    requirements = {item["id"] for item in spec.get("requirements", []) if isinstance(item, dict) and item.get("id")}
    scenes = {item["id"] for item in spec.get("scenes", []) if isinstance(item, dict) and item.get("id")}
    questions = {item["id"] for item in spec.get("questions", []) if isinstance(item, dict) and item.get("id")}
    assets = {item["id"] for item in spec.get("assets", []) if isinstance(item, dict) and item.get("id")}
    targets = scenes | questions | assets
    target_requirements = {
        item["id"]: set(item.get("requirement_ids", []))
        for group in ("scenes", "questions", "assets")
        for item in spec.get(group, [])
        if isinstance(item, dict) and item.get("id")
    }
    for req in spec.get("requirements", []):
        for target in req.get("targets", []):
            if target not in targets:
                errors.append(f"{req.get('id')}: unknown target {target}")
            elif req.get("id") not in target_requirements.get(target, set()):
                errors.append(f"{req.get('id')}: target {target} does not link back to requirement")
    for group in ("scenes", "questions", "assets"):
        for item in spec.get(group, []):
            for req_id in item.get("requirement_ids", []):
                if req_id not in requirements:
                    errors.append(f"{item.get('id')}: unknown requirement {req_id}")
    for item in spec.get("questions", []):
        if item.get("scene_id") not in scenes:
            errors.append(f"{item.get('id')}: unknown scene {item.get('scene_id')}")
    open_decisions = [item.get("id") for item in spec.get("decisions", []) if item.get("status") == "open"]
    if open_decisions:
        errors.append(f"unresolved decisions: {', '.join(open_decisions)}")
    return errors


def build_test_plan(spec: dict) -> dict:
    cases: list[dict] = []
    for scene in sorted(spec.get("scenes", []), key=lambda item: item.get("order", 0)):
        cases.append({
            "id": f"TEST-{scene['id']}-REACHABLE",
            "kind": "scene_reachable",
            "target": scene["id"],
            "requirement_ids": scene.get("requirement_ids", []),
            "expected": {"entry": scene.get("entry", ""), "exit": scene.get("exit", "")},
        })
    for question in spec.get("questions", []):
        cases.extend([
            {
                "id": f"TEST-{question['id']}-CORRECT",
                "kind": "question_correct",
                "target": question["id"],
                "requirement_ids": question.get("requirement_ids", []),
                "expected": {"answer": question.get("answer")},
            },
            {
                "id": f"TEST-{question['id']}-RETRY",
                "kind": "question_retry",
                "target": question["id"],
                "requirement_ids": question.get("requirement_ids", []),
                "expected": {"stays_until_correct": True},
            },
        ])
    for asset in spec.get("assets", []):
        cases.append({
            "id": f"TEST-{asset['id']}-EXISTS",
            "kind": "asset_exists",
            "target": asset["id"],
            "requirement_ids": asset.get("requirement_ids", []),
            "expected": {"path": asset["path"]},
        })
    covered = {req_id for case in cases for req_id in case["requirement_ids"]}
    return {
        "schema_version": "1.0",
        "cases": cases,
        "coverage": {
            "covered": sorted(covered),
            "uncovered": sorted(req["id"] for req in spec.get("requirements", []) if req["id"] not in covered and req.get("verification") in ("static", "functional")),
        },
    }


def verify_lesson_against_spec(spec: dict, lesson: dict, run_dir: Path | None = None) -> list[str]:
    """명세가 요구한 것이 `lesson.json` 에 실제로 들어갔는지 본다.

    **문자열이 같은지가 아니라 "그 자리가 구현됐는지" 를 본다.** 셋을 구분하지 않으면
    명세와 개발이 **둘 다 옳은데** 위반이 나온다 — 2026-09-23 실측(4-1/03)에서 36건이 그랬다.

    · 자산 — 명세의 `path` 는 **잠정**일 수 있다(`path_status` 가 그렇게 적는다).
      확정 경로는 `visual_design` 이 내는 `design/asset-plan.json` 이므로 그쪽과도 대조한다.
      실측: 명세 23건 중 경로가 그대로인 것은 9건뿐이었고 나머지는 `assets/bg/` → `assets/backgrounds/`
      처럼 **확정 단계에서 바뀐 것**이었다.
    · 문항 텍스트 — 명세의 `prompt` 는 **사람이 읽는 요약**이다. 화면에 올리면 계약서가 막는
      "원문에 없는 안내 문구" 가 된다. 그래서 문구가 통째로 없는 것은 위반으로 보지 않고,
      **정답이 살아 있는지**를 본다. 정답이 사라지면 그 문항은 풀 수 없다.
    · 장면 — 문항 화면은 `SCN-` 대신 문항 ID(`Q-`)로 짝지어도 구현된 것이다.
      명세가 `questions[].scene_id` 로 이미 그 연결을 갖고 있다.
    """
    errors: list[str] = []
    serialized = json.dumps(lesson, ensure_ascii=False)
    flat = normalize(serialized)
    ids = collect_ids(lesson)
    implemented = lambda ref: ref in ids or ref in serialized

    # 문항 화면은 문항 ID 로 짝지어도 구현된 것으로 본다.
    scene_covered_by_question = {
        question.get("scene_id")
        for question in spec.get("questions", [])
        if question.get("scene_id") and implemented(question["id"])
    }
    for scene in spec.get("scenes", []):
        if implemented(scene["id"]) or scene["id"] in scene_covered_by_question:
            continue
        # 힌트 장면은 독립 화면이 아니라 문항에 붙는 곁가지다(`hint`·`hintAfterWrong`).
        # 자기 `question_ids` 가 비어 있고 `entry`/`exit` 가 **이미 구현된 문항**을 가리키면
        # 그 문항 안에 들어간 것이다 — 실측 2026-09-23, SCN-07·15 가 그랬다.
        if scene_text_present(scene, flat) or scene_is_substate(scene, spec, implemented):
            continue
        errors.append(f"scene not implemented: {scene['id']} ({scene.get('title', '')})")

    for question in spec.get("questions", []):
        if not implemented(question["id"]):
            errors.append(f"question not implemented: {question['id']}")
            continue
        # 정답이 살아 있는지를 본다 — prompt 문구가 아니라.
        # **글이 아니라 정답 필드끼리** 비교한다. 글로 찾으면 같은 수가 도형 정의(`deg:30`)나
        # `acceptance` 문장("정답: 30을 넣고…")에도 있어 정답을 바꿔도 통과한다
        # (실측 2026-09-23 — 문항 스코프로 좁혀도 세 자리에서 걸렸다).
        #
        # 구조가 있는 정답(`sortToBin` 의 `{칸: [조각…]}` 처럼)은 명세와 구현의 표현이
        # 달라도 정상이므로 여기서 보지 않는다 — 그 모양은 `lesson_check` 의
        # `check_answer_shapes` 가 원자별 불변식으로 따로 본다.
        want = scalar_answers(question.get("answer"))
        if want:
            got = scalar_answers(lesson_answer(lesson, question["id"]))
            if got and not (set(want) & set(got)):
                errors.append(
                    f"question answer lost: {question['id']} (명세 {want[:3]} · 구현 {got[:3]})"
                )

    refs = collect_strings(lesson)
    confirmed = confirmed_asset_paths(run_dir)
    for asset in spec.get("assets", []):
        path = asset["path"]
        if path in refs:
            continue
        # 확정 단계에서 경로가 바뀌었을 수 있다 — 파일 이름으로 다시 본다.
        stem = path.rsplit("/", 1)[-1]
        if stem in confirmed and any(ref.endswith("/" + stem) for ref in refs):
            continue
        # **명세가 스스로 잠정이라고 적었으면 명세 경로를 강제하지 않는다.**
        # `path_status` 가 "visual_design 의 asset-plan 경로가 우선한다" 라고 말하는데
        # 그 경로를 위반으로 내면 명세가 자기 말을 어기는 셈이다(실측 2026-09-23, 14건).
        # 이름까지 바뀌는 경우도 있고(story-1 → story-1-playground), 설계 판단으로 그림
        # 자체가 사라지기도 한다(도장·인증서를 base 공통 UI 가 그리기로 한 차시).
        # 확정 목록(asset-plan.json)과 lesson.json 의 대조는 `lesson_check` 가 따로 한다.
        if "proposed" in str(asset.get("path_status", "")).lower():
            continue
        errors.append(f"asset not referenced: {asset['id']} -> {path}")

    plan = build_test_plan(spec)
    for req_id in plan["coverage"]["uncovered"]:
        errors.append(f"requirement has no generated test: {req_id}")
    return errors


def scene_text_present(scene: dict, flat: str) -> bool:
    """이 장면이 쓰는 글이 화면에 살아 있는가. 힌트처럼 곁가지로 구현되는 장면을 위한 것이다."""
    for key in ("text", "hint", "body", "title"):
        value = scene.get(key)
        if isinstance(value, str) and len(value) >= 6 and normalize(value) in flat:
            return True
    return False


def answer_tokens(answer: object) -> list[str]:
    """정답에서 **화면에 남아야 하는 조각**을 뽑는다.

    정답은 문자열·배열·객체 어느 모양이든 온다(`sortToBin` 은 `{칸: [조각…]}` 이다).
    통째로 문자열 비교하면 구조가 다를 때 무조건 어긋나므로 **잎 값**만 모은다.
    """
    leaves: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                leaves.append(str(key))
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif node not in (None, ""):
            leaves.append(str(node))

    walk(answer)
    return [normalize(v) for v in leaves if len(str(v)) >= 1]


def lesson_answer(lesson: object, question_id: str) -> object:
    """`lesson.json` 의 그 문항이 들고 있는 `interaction.answer`."""
    found: list[object] = []

    def walk(node: object) -> None:
        if found:
            return
        if isinstance(node, dict):
            if question_id in (str(node.get("id", "")), str(node.get("specId", ""))):
                interaction = node.get("interaction")
                if isinstance(interaction, dict):
                    found.append(interaction.get("answer"))
                return
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(lesson)
    return found[0] if found else None


def scalar_answers(answer: object) -> list[str]:
    """정답이 **스칼라이거나 스칼라 배열**일 때만 값을 낸다. 그 외(객체)는 빈 목록이다."""
    if answer is None:
        return []
    if isinstance(answer, (str, int, float)):
        return [normalize(str(answer))]
    if isinstance(answer, list) and all(isinstance(v, (str, int, float)) for v in answer):
        return [normalize(str(v)) for v in answer if str(v) != ""]
    return []


def question_scope(lesson: object, question_id: str) -> str | None:
    """`lesson.json` 에서 그 문항 하나의 하위 트리만 글로 만든다.

    정답이 살아 있는지는 **그 문항 안에서** 봐야 한다. 문서 전체를 훑으면 다른 문항의
    수에 걸려 무엇을 지워도 통과한다.
    """
    found: list[str] = []

    def walk(node: object) -> None:
        if found:
            return
        if isinstance(node, dict):
            if question_id in (str(node.get("id", "")), str(node.get("specId", ""))):
                found.append(json.dumps(node, ensure_ascii=False))
                return
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(lesson)
    return normalize(found[0]) if found else None


def scene_is_substate(scene: dict, spec: dict, implemented) -> bool:
    """이 장면이 **다른 문항의 하위 상태**인가(힌트 화면 등).

    자기 `question_ids` 가 비어 있고 `entry`/`exit` 산문이 이미 구현된 문항 ID 를 가리키면
    독립 화면이 아니라 그 문항 안에서 열리는 상태다.
    """
    if scene.get("question_ids"):
        return False
    text = f"{scene.get('entry', '')} {scene.get('exit', '')}"
    for question in spec.get("questions", []):
        qid = question.get("id")
        if qid and qid in text and implemented(qid):
            return True
    return False


def confirmed_asset_paths(run_dir: Path | None) -> set[str]:
    """`visual_design` 이 확정한 그림 경로의 **파일 이름** 집합.

    명세의 경로가 잠정일 때 이름으로 같은 그림인지 가린다.
    """
    if run_dir is None:
        return set()
    path = run_dir / "design" / "asset-plan.json"
    if not path.exists():
        return set()
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {
        str(item.get("path", "")).rsplit("/", 1)[-1]
        for item in plan.get("assets", [])
        if isinstance(item, dict) and item.get("path")
    }


def collect_ids(node: object) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("id", "sceneId", "questionId", "specId") and isinstance(value, str):
                found.add(value)
            found.update(collect_ids(value))
    elif isinstance(node, list):
        for value in node:
            found.update(collect_ids(value))
    return found


def collect_strings(node: object) -> set[str]:
    if isinstance(node, str):
        return {node}
    if isinstance(node, dict):
        return set().union(*(collect_strings(value) for value in node.values())) if node else set()
    if isinstance(node, list):
        return set().union(*(collect_strings(value) for value in node)) if node else set()
    return set()


def normalize(value: str) -> str:
    return "".join(str(value).split())


def write_and_verify(run_dir: Path, schema_path: Path) -> list[str]:
    spec_path = run_dir / "spec" / "lesson-spec.json"
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not spec_path.exists():
        return [f"missing canonical spec: {spec_path}"]
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors = validate_lesson_spec(spec, schema_path)
    tests_dir = run_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    plan = build_test_plan(spec)
    (tests_dir / "functional-test-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if lesson_path.exists():
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        errors.extend(verify_lesson_against_spec(spec, lesson, run_dir))
    result = {"status": "PASS" if not errors else "REJECT", "errors": errors, "case_count": len(plan["cases"]), "coverage": plan["coverage"]}
    (tests_dir / "spec-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return errors
