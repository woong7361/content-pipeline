"""run 하나의 에이전트 파일 접근 기록을 읽어 정보 차단 위반 정황을 보고한다. LLM 0회.

    python -B ./audit_agent_access.py runs/2026-08-19_7c829ae6

기록은 `{brief_hash}_agent_audit.jsonl`에 stage가 실행한 셸 명령으로 남는다.
**이 도구는 막지 않는다.** 차단 표(`CLAUDE.md` 정보 차단 규칙)가 실제로 지켜지는지만 관측한다.

명령에 파일명이 나온 것은 **열어 봤다는 정황**이지 확정이 아니다 — grep 대상으로 이름만
스쳤을 수도 있다. 판단은 사람이 한다. 그래서 종료 코드로 CI를 세우지 않는다.

종료 코드
  0  위반 정황 없음 (감사되지 않은 stage가 있어도 0이다 — 아래 경고를 읽는다)
  1  실행 자체가 실패했다
  2  위반 정황이 있다
"""

import argparse
import io
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stages.scripts import agent_audit  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VIOLATION_EXIT = 2


def main() -> int:
    parser = argparse.ArgumentParser(description="에이전트 파일 접근 감사 보고")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--all", action="store_true", help="위반이 아닌 명령도 전부 보여준다")
    args = parser.parse_args()

    run_dir: Path = args.run_dir
    if not run_dir.is_dir():
        print(f"run 디렉토리가 없다: {run_dir}")
        return 1

    audits = sorted(run_dir.glob("*_agent_audit.jsonl"))
    if not audits:
        print(f"감사 기록이 없다: {run_dir}/*_agent_audit.jsonl")
        print("이 run은 감사 장치가 붙기 전에 돌았거나, codex 경로를 한 번도 타지 않았다.")
        return 0

    entries = []
    for path in audits:
        entries.extend(agent_audit.load(path))

    commands = [e for e in entries if e.get("command")]
    unaudited = sorted({e["stage"] for e in entries if e.get("provider") == "claude"})
    violations = agent_audit.find_violations(commands)

    print(f"기록 {len(entries)}건 · 셸 명령 {len(commands)}건 · stage {len(set(e['stage'] for e in entries))}개\n")

    by_stage = Counter(e["stage"] for e in commands)
    touched = Counter(a for e in commands for a in e.get("touched", []))
    if by_stage:
        print("stage별 명령 수")
        for stage, count in by_stage.most_common():
            print(f"  {stage:20} {count}")
        print()
    if touched:
        print("건드린 산출물 (정황)")
        for name, count in touched.most_common():
            print(f"  {name:20} {count}")
        print()

    if unaudited:
        print("⚠ 감사되지 않은 stage — claude 경로는 도구 호출 기록이 없다")
        for stage in unaudited:
            print(f"  {stage}")
        print("  감사하려면 ClaudeClient를 `--output-format stream-json --verbose` 로 바꿔야 한다.")
        print("  여기 비어 있는 것은 '위반 없음'이 아니라 '모른다'이다.\n")

    if violations:
        print(f"■ 차단 표 위반 정황 {len(violations)}건\n")
        for item in violations:
            print(f"  [{item['stage']}] 보면 안 되는 것을 건드렸다: {', '.join(item['violates'])}")
            print(f"    {item['command'][:200]}")
            print()
    else:
        print("■ 차단 표 위반 정황 없음")
        if unaudited:
            print("  (단, 위 감사되지 않은 stage는 이 판정에 포함되지 않는다)")

    if args.all and commands:
        print("\n전체 명령")
        for item in commands:
            print(f"  [{item['stage']}] {item['command'][:180]}")

    return VIOLATION_EXIT if violations else 0


if __name__ == "__main__":
    sys.exit(main())
