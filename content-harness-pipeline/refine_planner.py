"""planner_output.json -> 고친 planner_output.json (LLM 1회).

    python -B ./refine_planner.py runs/{run_id}/{hash}_planner.json \
        --input runs/{run_id}/{hash}_input.json -o runs/{run_id}/{hash}_planner_refined.json

runner는 계획이 굳기 전에 같은 일을 한다(`--no-planner-refine` 으로 끈다). 이 스크립트는 이미
굳은 계획을 손대볼 때 쓴다. **대상 파일을 덮어쓰지 않는다** — 어디에 쓸지는 `-o`로 정한다.

종료 코드
  0  고친 계획을 채택했다
  2  기각했다. 원본이 그대로 맞다(무엇을 잃었는지는 리포트에 있다)
  1  실행 자체가 실패했다
"""

import argparse
import json
import sys
from pathlib import Path

from stages.planner_refine import format_review, refine_plan, review_refined
from stages.scripts.planner_check import check_planner, format_violations
from validate import validate_file

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다(실측: 결정 리포트의 U+2014). 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는
# 크래시 대신 치환한다 -- 멈춰서 물어야 할 순간에 보고 자체가 죽으면 안 된다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REJECTED_EXIT = 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Refine a planner output in place of a full re-plan.")
    parser.add_argument("planner", type=Path)
    parser.add_argument("--input", type=Path, required=True, help="그 계획을 만든 input.json")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="기계 검사만 돌리고 끝낸다. LLM을 부르지 않는다.",
    )
    args = parser.parse_args()

    planner_output = json.loads(args.planner.read_text(encoding="utf-8"))
    violations = check_planner(planner_output)
    print(format_violations(violations))
    if args.check_only:
        return 0

    refine_plan(
        input_path=args.input.resolve(),
        planner_output=planner_output,
        violations=violations,
        output_path=args.output,
        codex_bin=args.codex_bin,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )

    result = validate_file(args.output, artifact="planner_output")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        print("\n기각 — 고친 계획이 schema를 통과하지 못했다. 원본이 그대로 맞다.")
        return REJECTED_EXIT

    review = review_refined(planner_output, json.loads(args.output.read_text(encoding="utf-8")))
    print("\n" + format_review(review))
    return 0 if review["accepted"] else REJECTED_EXIT


if __name__ == "__main__":
    sys.exit(main())
