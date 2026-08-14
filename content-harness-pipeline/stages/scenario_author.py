"""planner -> 자유 흐름 시나리오. 이 파이프라인에서 LLM이 테스트에 관여하는 유일한 자리다.

파생기는 planner의 필드를 훑어 케이스를 만들므로 **그 필드에 없는 것은 구조적으로 못 본다.**
여러 화면에 걸친 흐름, 앞 조작이 뒤 결과를 바꾸는 경우, 안내대로 하지 않았을 때 갇히는지는
필드를 아무리 늘려도 규칙으로 뽑히지 않는다. 그 자리를 이 stage가 채운다.

**조합은 열고 어휘는 닫는다.** 시나리오는 이미 검증된 조작의 나열이라, 잘못 써도 엉뚱한 것을
검사할 뿐 조용히 통과하지 않는다. 반면 조작 자체를 새로 지어내면 실행기가 못 밀고, 억지로
통과시키면 거짓 확신이 생긴다. 그래서 어휘 밖 이름은 생성 직후 기계적으로 걸러낸다.

산출물은 run 디렉토리에 굳는다. 같은 planner면 다시 부르지 않는다 — 매번 새로 쓰면 같은
콘텐츠인데 검증 항목이 달라져 게이트가 흔들린다.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from stages.functional_test import (
    ACTION_VALUES,
    EXPECT_VALUES,
    KNOWN_ACTIONS,
    KNOWN_EXPECTS,
    QUESTION_SCOPED_EXPECTS,
)
from stages.scripts.codex_client import CodexClient


PROJECT_DIR = Path(__file__).resolve().parent.parent
SCENARIO_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "scenario_author_system.md"
SCENARIO_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "scenario_output.schema.json"

# 다른 stage와 같은 모델을 명시한다. 생략하면 CLI 설정 기본값에 맡기게 되는데, 값이 같아도
# 해석 경로가 달라 거절되는 경우가 있었다. 파이프라인이 쓰는 모델은 한 곳에서 보이게 둔다.
DEFAULT_MODEL = "gpt-5.6-sol"


def author_scenarios(
    planner_path: Path,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
    force: bool = False,
) -> dict:
    planner_sha = sha256_of(planner_path)
    if not force and output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        if existing.get("planner_sha") == planner_sha:
            return {"status": "REUSED", "scenarios": len(existing.get("scenarios", [])), "path": str(output_path)}

    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    client = CodexClient(codex_bin=codex_bin, project_dir=PROJECT_DIR, timeout_seconds=timeout_seconds)
    client.run_prompt(
        prompt=build_prompt(planner_output),
        output_schema=SCENARIO_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model or DEFAULT_MODEL,
    )

    authored = json.loads(output_path.read_text(encoding="utf-8"))
    kept, dropped, corrected = validate_scenarios(authored.get("scenarios", []), planner_output)
    authored["scenarios"] = kept
    authored["dropped"] = dropped
    authored["corrected"] = corrected
    authored["planner_sha"] = planner_sha
    output_path.write_text(json.dumps(authored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "status": "PASS",
        "scenarios": len(kept),
        "dropped": len(dropped),
        "corrected": len(corrected),
        "missing": len(authored.get("missing", [])),
        "path": str(output_path),
    }


def build_prompt(planner_output: dict) -> str:
    system_prompt = SCENARIO_SYSTEM_PROMPT.read_text(encoding="utf-8")
    # 어휘를 손으로 적지 않는다. 적으면 실행기가 늘 때 사본과 어긋나고, 어긋난 쪽이 조용히 이긴다.
    return f"""{system_prompt}

ACTION_VOCABULARY:
{json.dumps(sorted(KNOWN_ACTIONS), ensure_ascii=False, indent=2)}

EXPECT_VOCABULARY:
{json.dumps(sorted(KNOWN_EXPECTS), ensure_ascii=False, indent=2)}

PLANNER_FLOW_JSON:
{json.dumps(flow_view(planner_output), ensure_ascii=False, indent=2)}
"""


def flow_view(planner_output: dict) -> dict:
    """흐름을 쓰는 데 필요한 것만 남긴다.

    planner 전문에는 화풍·캐릭터 정체성·asset 계획이 함께 들어 있고 그게 분량의 대부분이다.
    시나리오 저작자가 그걸 볼 이유가 없고, 보면 검증과 무관한 것을 쓰기 시작한다. 다른 stage가
    각자 허용된 입력만 받는 것과 같은 규율이다.

    `elements`에서도 `content`(스토리보드 원문 서술)와 `notes`(연출 힌트)는 뺀다. 화면에 뜨는
    문구는 `rendered_text`가, 언제 뜨는지는 `reveal`이 이미 구조로 들고 있다.
    """
    return {
        "page": planner_output.get("page", {}),
        "interactions": planner_output.get("interactions", []),
        "sections": [
            {
                "id": section["id"],
                "title": section["title"],
                "purpose": section["purpose"],
                "advance": section.get("advance", {}),
                "interaction_ids": section.get("interaction_ids", []),
                "questions": section.get("questions", []),
                "elements": [
                    {
                        "channel": element["channel"],
                        "rendered_text": element["rendered_text"],
                        "reveal": element.get("reveal", {}),
                        "refs": element["refs"],
                    }
                    for element in section.get("elements", [])
                ],
            }
            for section in planner_output.get("sections", [])
        ],
    }


def validate_scenarios(scenarios: list[dict], planner_output: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """이름과 **값**을 함께 검사한다.

    이름만 보면 유효한 조작을 잘못된 의미로 쓴 것을 못 잡는다(실측: `advance_page`에 `previous`를
    넣어 뒤로 가려 했지만 실행기는 앞으로만 넘긴다). 값이 planner의 무엇을 가리켜야 하는지는
    여기서 기계적으로 대조된다.

    고칠 수 있는 것은 고치고 기록한다 — interaction id를 화면 id로, 문항 id를 정답 값으로.
    저작자가 헷갈릴 만한 자리이고 대응이 유일하게 정해지므로 버릴 이유가 없다.
    """
    section_ids = {s["id"] for s in planner_output.get("sections", [])}
    questions = [q for s in planner_output.get("sections", []) for q in s.get("questions", [])]
    answer_of = {q["id"]: q.get("answer", "") for q in questions}
    # 보기·hotspot 문항은 정답 문구가 처음부터 떠 있어 answer_revealed를 값으로 판정할 수 없다.
    # 문항 id로도, 정답 값으로도 지목될 수 있으므로 둘 다 모아 둔다.
    attribute_only_refs = {
        ref
        for q in questions
        if q.get("choices") or q.get("input_type") == "hotspot"
        for ref in (q["id"], q.get("answer", ""))
        if ref
    }
    # 빈 interaction_id는 "출구 없음"이지 조작 이름이 아니다. 키로 넣으면 값 없는 activate가
    # 이 항목에 걸려 엉뚱한 화면으로 교정된다.
    advance_target: dict[str, str] = {}
    for section in planner_output.get("sections", []):
        advance = section.get("advance") or {}
        if advance.get("interaction_id") and advance.get("to_section_id"):
            advance_target[advance["interaction_id"]] = advance["to_section_id"]

    kept: list[dict] = []
    dropped: list[dict] = []
    corrected: list[dict] = []

    for scenario in scenarios:
        problems: list[str] = []
        notes: list[str] = []

        for step in scenario["steps"]:
            action = step["action"]
            if action not in KNOWN_ACTIONS:
                problems.append(f"모르는 조작 {action}")
                continue
            if not ACTION_VALUES[action] and step["values"]:
                notes.append(f"{action}: 값을 받지 않아 {step['values']} 를 비웠다")
                step["values"] = []
            elif action == "activate":
                target = step["values"][0] if step["values"] else ""
                if not target:
                    problems.append("activate 대상이 비었다. 도착할 화면 id를 값으로 지목해야 한다")
                elif target in section_ids:
                    continue
                elif advance_target.get(target):
                    notes.append(f"activate: interaction id {target} -> 화면 {advance_target[target]}")
                    step["values"] = [advance_target[target]]
                else:
                    problems.append(f"activate 대상 {target!r} 이 화면 id가 아니다")

        has_question_step = any(step.get("question_id") for step in scenario["steps"])
        for item in scenario["expect"]:
            kind = item["kind"]
            if kind not in KNOWN_EXPECTS:
                problems.append(f"모르는 단언 {kind}")
                continue
            # 문항 단언은 실행기가 step의 question_id로 문항 root를 다시 찾는다. 지목이 없으면
            # 올바른 HTML에서도 root를 못 찾아 hook_missing으로 오귀속된다 — 실행 전에 거른다.
            if kind in QUESTION_SCOPED_EXPECTS and not has_question_step:
                problems.append(f"{kind} 는 문항 단언인데 어느 step도 question_id를 지목하지 않았다")
                continue
            if not EXPECT_VALUES[kind]:
                item["value"] = ""
            elif kind == "scene_active" and item["value"] not in section_ids:
                problems.append(f"scene_active 대상 {item['value']!r} 이 화면 id가 아니다")
            elif kind == "answer_revealed" and item["value"] in attribute_only_refs:
                notes.append(
                    f"answer_revealed: {item['value']!r} 는 보기·hotspot 문항이라 값 대신 표시 속성으로 판정"
                )
                item["value"] = ""
            elif kind == "answer_revealed" and item["value"] in answer_of:
                notes.append(f"answer_revealed: 문항 id {item['value']} -> 정답 {answer_of[item['value']]!r}")
                item["value"] = answer_of[item["value"]]

        if problems:
            dropped.append({"id": scenario["id"], "intent": scenario["intent"], "problems": problems})
            continue
        if notes:
            corrected.append({"id": scenario["id"], "notes": notes})
        kept.append(scenario)

    return kept, dropped, corrected


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_cases(authored: dict) -> list[dict]:
    """시나리오를 실행기가 그대로 도는 케이스 모양으로 옮긴다."""
    return [
        {
            "id": f"case_{scenario['id']}",
            "kind": "scenario",
            "section_id": scenario["start_section_id"],
            "question_id": "",
            "input_type": "",
            "intent": scenario["intent"],
            "steps": scenario["steps"],
            "expect": scenario["expect"],
        }
        for scenario in authored.get("scenarios", [])
    ]
