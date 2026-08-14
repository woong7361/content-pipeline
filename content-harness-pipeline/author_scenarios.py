"""planner_output.json -> scenarios.json (LLM 1회, 같은 planner면 재사용).

    python -B ./author_scenarios.py runs/{run_id}/{hash}_planner.json -o runs/{run_id}/{hash}_scenarios.json
"""

import argparse
import json
import sys
from pathlib import Path

from stages.scenario_author import author_scenarios

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다(실측: 결정 리포트의 U+2014). 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는
# 크래시 대신 치환한다 -- 멈춰서 물어야 할 순간에 보고 자체가 죽으면 안 된다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Author free-form flow scenarios from planner output.")
    parser.add_argument("planner", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--force", action="store_true", help="같은 planner여도 다시 쓴다")
    args = parser.parse_args()

    result = author_scenarios(
        planner_path=args.planner,
        output_path=args.output,
        codex_bin=args.codex_bin,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        force=args.force,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] == "REUSED":
        return 0

    authored = json.loads(args.output.read_text(encoding="utf-8"))
    for item in authored.get("dropped", []):
        print(f"DROPPED [{item['id']}] {'; '.join(item['problems'])} — {item['intent']}")
    for item in authored.get("missing", []):
        print(f"MISSING {item['need']}: {item['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
