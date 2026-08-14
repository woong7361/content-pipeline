"""실행기 자체를 검증한다. 파이프라인 밖에서 도는 회귀 테스트이고 LLM을 쓰지 않는다.

같은 spec을 good.html과 broken.html에 돌려 good=PASS, broken=REJECT가 나와야 한다.
broken이 통과하면 콘텐츠가 좋은 것이 아니라 실행기가 죽은 것이다. 음성 대조군이 없으면
"전 항목 통과"를 품질 신호로 착각하게 되고, 그건 이 테스트 층을 추가하기 전과 같은 상태다.

    python -B ./tests/run_fixture_check.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stages.functional_test import KNOWN_ACTIONS, KNOWN_EXPECTS, run_functional_test  # noqa: E402
from stages.scripts.test_spec_derive import SUPPORTED_INPUT_TYPES, derive_test_spec  # noqa: E402

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다(실측: 결정 리포트의 U+2014). 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는
# 크래시 대신 치환한다 -- 멈춰서 물어야 할 순간에 보고 자체가 죽으면 안 된다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PROJECT_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
WORK_DIR = Path(__file__).resolve().parent / "_work"


def main() -> int:
    planner_output = json.loads((FIXTURES_DIR / "fixture_planner.json").read_text(encoding="utf-8"))
    spec = derive_test_spec(planner_output, source_name="fixture_planner.json")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = WORK_DIR / "fixture_test_spec.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"derived cases={len(spec['cases'])} coverage={json.dumps(spec['coverage'], ensure_ascii=False)}")

    reports = {}
    for name in ("good", "broken"):
        reports[name] = run_functional_test(
            spec_path=spec_path,
            html_path=FIXTURES_DIR / f"{name}.html",
            output_path=WORK_DIR / f"{name}_report.json",
            screenshots_dir=WORK_DIR / f"{name}_shots",
        )
        report = reports[name]
        print(
            f"{name:<7} verdict={report['verdict']} "
            f"passed={report['passed']}/{report['total']} "
            f"failed={report['failed']} hook_missing={report['hook_missing']}"
        )
        for failure in report["failures"]:
            print(f"          - {failure['case_id']} [{failure['reason']}] {failure['detail'][:90]}")

    errors = check_enum_coverage(spec=spec, planner_output=planner_output)
    if reports["good"]["verdict"] != "PASS":
        errors.append("good.html이 PASS가 아니다. 계약을 지킨 HTML을 실행기가 잡아내고 있다.")
    if reports["broken"]["verdict"] != "REJECT":
        errors.append("broken.html이 REJECT가 아니다. 실행기가 결함을 못 잡는다.")
    if reports["broken"]["hook_missing"] != 0:
        errors.append("broken.html의 결함이 hook_missing으로 잡혔다. 계약 위반과 동작 결함이 섞여 있다.")

    print()
    if errors:
        for error in errors:
            print(f"FIXTURE CHECK FAILED: {error}")
        return 1
    print("FIXTURE CHECK PASSED: good=PASS, broken=REJECT(expect_failed), enum 커버리지 100%")
    return 0


def check_enum_coverage(*, spec: dict, planner_output: dict) -> list[str]:
    """실행기가 아는 모든 조작을 fixture가 실제로 시연했는지 본다.

    이 검사가 없으면 enum에만 있고 한 번도 실행되지 않은 action이 생긴다. 실제로 `drag_to_*`가
    그렇게 검증되지 않은 채 "FIXTURE CHECK PASSED"가 떴다. 그 상태에서는 대조군이 통과해도
    그 action에 대해서는 아무것도 보증하지 않는다.
    """
    errors: list[str] = []
    used_actions = {step["action"] for case in spec["cases"] for step in case["steps"]}
    used_expects = {item["kind"] for case in spec["cases"] for item in case["expect"]}
    used_input_types = {
        question["input_type"]
        for section in planner_output["sections"]
        for question in section["questions"]
    }

    checks = [
        ("action", KNOWN_ACTIONS, used_actions, "실행기가 아는 action"),
        ("expect", KNOWN_EXPECTS, used_expects, "실행기가 아는 expect"),
        ("input_type", set(SUPPORTED_INPUT_TYPES), used_input_types, "파생기가 지원한다는 input_type"),
    ]
    for label, known, used, description in checks:
        missing = known - used
        if missing:
            errors.append(f"fixture가 시연하지 않는 {label}: {sorted(missing)} — {description}인데 한 번도 실행되지 않는다")
        unknown = used - known
        if unknown:
            errors.append(f"fixture가 쓰는데 실행기가 모르는 {label}: {sorted(unknown)}")

    print(
        f"enum coverage  action={len(used_actions)}/{len(KNOWN_ACTIONS)} "
        f"expect={len(used_expects)}/{len(KNOWN_EXPECTS)} "
        f"input_type={len(used_input_types & set(SUPPORTED_INPUT_TYPES))}/{len(SUPPORTED_INPUT_TYPES)}"
    )
    errors += check_author_prompt_names()
    return errors


def check_author_prompt_names() -> list[str]:
    """시나리오 저작 프롬프트가 실행기의 어휘를 빠짐없이 설명하는지 본다.

    값 계약은 프롬프트에 손으로 적혀 있다(구조화해 주입하면 요청이 거절된다). 손으로 적은 것은
    실행기가 늘 때 어긋나고, 어긋나면 저작자가 모르는 조작을 쓰거나 값을 지어낸다.
    """
    prompt = (PROJECT_DIR / "prompts" / "scenario_author_system.md").read_text(encoding="utf-8")
    missing = sorted(name for name in KNOWN_ACTIONS | KNOWN_EXPECTS if name not in prompt)
    if missing:
        return [f"저작 프롬프트가 설명하지 않는 어휘: {missing}"]
    print(f"저작 프롬프트 어휘 설명  {len(KNOWN_ACTIONS | KNOWN_EXPECTS)}/{len(KNOWN_ACTIONS | KNOWN_EXPECTS)}")
    return []


if __name__ == "__main__":
    sys.exit(main())
