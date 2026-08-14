"""planner_output.json -> test_spec.json (LLM 0회).

    python -B ./derive_test_spec.py runs/{run_id}/{hash}_planner.json -o runs/{run_id}/{hash}_test_spec.json

파생하지 못한 것이 있으면 **멈추고 사람에게 묻는다.** 이 자리에서 멈추는 이유는 planner 직후이자
asset_generator 이전이라, 이미지 수십 장을 굽기 전에 판단할 수 있기 때문이다.

종료 코드
  0  전부 파생됐다. 사람 판단이 필요 없다
  2  파생 못 한 것이 있다. 아래 세 갈래 중 하나를 골라야 한다
  1  실행 자체가 실패했다
"""

import argparse
import json
import sys
from pathlib import Path

from stages.scenario_author import to_cases
from stages.scripts.test_spec_derive import derive_test_spec, format_decision_report

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다(실측: 결정 리포트의 U+2014). 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는
# 크래시 대신 치환한다 -- 멈춰서 물어야 할 순간에 보고 자체가 죽으면 안 된다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DECISION_EXIT = 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a functional test spec from planner output.")
    parser.add_argument("planner", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument(
        "--accept-test-gaps",
        action="store_true",
        help="파생 못 한 것을 알고도 진행한다. 그 문항은 unsupported로 기록되고 검증되지 않는다.",
    )
    parser.add_argument(
        "--scenarios",
        type=Path,
        help="author_scenarios.py가 만든 자유 흐름 시나리오 파일. 있으면 spec에 합친다.",
    )
    args = parser.parse_args()

    planner_output = json.loads(args.planner.read_text(encoding="utf-8"))
    spec = derive_test_spec(planner_output, source_name=args.planner.name)

    if args.scenarios and args.scenarios.exists():
        authored = json.loads(args.scenarios.read_text(encoding="utf-8"))
        added = to_cases(authored)
        spec["cases"].extend(added)
        spec["coverage"]["authored_scenarios"] = len(added)
        print(f"자유 시나리오 {len(added)}건 합침 ({args.scenarios.name})")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    coverage = spec["coverage"]
    print(json.dumps(coverage, ensure_ascii=False, indent=2))

    if not spec["underivable"]:
        print("\n전부 파생됐다. 결정할 것 없음.")
        return 0

    print("\n" + format_decision_report(spec))
    if args.accept_test_gaps:
        print("\n--accept-test-gaps: 위 문항을 검증하지 않고 진행한다. 실행 리포트에 unsupported로 남는다.")
        return 0
    return DECISION_EXIT


if __name__ == "__main__":
    sys.exit(main())
