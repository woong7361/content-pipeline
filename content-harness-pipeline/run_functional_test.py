"""test_spec.json을 output/index.html에 실행한다 (LLM 0회).

    python -B ./run_functional_test.py runs/{run_id}/{hash}_test_spec.json \
        --html runs/{run_id}/output/index.html \
        -o runs/{run_id}/iter_001/{hash}_iter-001_test_report.json
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from stages.functional_test import run_functional_test

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다(실측: 결정 리포트의 U+2014). 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는
# 크래시 대신 치환한다 -- 멈춰서 물어야 할 순간에 보고 자체가 죽으면 안 된다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a functional test spec against built HTML.")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--show", type=int, default=10, help="문장으로 낼 실패 시나리오 개수")
    args = parser.parse_args()

    report = run_functional_test(
        spec_path=args.spec,
        html_path=args.html,
        output_path=args.output,
        screenshots_dir=args.output.parent / "functional_test",
        timeout_seconds=args.timeout_seconds,
    )

    print(
        f"verdict={report['verdict']} passed={report['passed']}/{report['total']} "
        f"failed={report['failed']} hook_missing={report['hook_missing']} "
        f"unsupported={report['unsupported']}"
    )
    if report["unsupported"]:
        print(
            f"주의: 문항 {report['questions_covered']}/{report['questions_total']} 만 검증됐다. "
            f"{report['unsupported']}개는 케이스가 만들어지지 않아 실행되지 않았다."
        )
    reasons = Counter(item["reason"] for item in report["failures"])
    print("failure reasons: " + json.dumps(reasons, ensure_ascii=False))
    subjects = Counter(item["subject"] for item in report["failures"] if item["reason"] == "hook_missing")
    if subjects:
        print("missing hooks: " + json.dumps(subjects, ensure_ascii=False))

    # 실패한 시나리오만 문장으로 낸다. 전부 찍으면 통과분에 묻혀 읽히지 않는다.
    broken = [item for item in report["scenarios"] if item["status"] != "PASS"]
    if broken:
        print(f"\n실패한 시나리오 {len(broken)}건 (앞 {min(len(broken), args.show)}건)")
        for item in broken[: args.show]:
            print()
            print(f"  {item['given']}")
            for phrase in item["when"] or ["(조작 없음)"]:
                print(f"      {phrase}")
            for phrase in item["then"]:
                print(f"   -> {phrase}")
            for problem in item["problems"]:
                print(f"      ! {problem}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
