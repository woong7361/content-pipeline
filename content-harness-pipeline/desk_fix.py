"""차시 작업대의 [AI 맡기기] 중 **코드 메모** — 열린 코드 메모대로 **gyo6 차시 폴더를 직접** 고친다. `lesson_desk.py` 가 작업으로 부른다.

    python -B ./desk_fix.py --gyo6-root <gyo6_content> --lesson 4-1/04 --desk-dir desk/4-1-04 --baseline <작업 전 사본>

- 고치는 것은 `lessons/{차시}/` 의 lesson.json · player-ext.css · player-ext.js 뿐이다(`prompts/desk_fix_system.md`).
- claude 는 파이프라인 폴더에서 돌고(`--setting-sources project`), gyo6 는 `--add-dir` 로만 연다.
  명령은 자가 검사(`stages.scripts.desk_check`) 하나만 허용한다.
- 결과(메모별 fixed · needs_image · needs_confirm · not_fixed)는 `{desk-dir}/last-fix.json` 에 남긴다.
  메모 상태를 바꾸는 것은 작업대가 한다 — 이 스크립트는 결과만 낸다.

종료 코드: 0 끝남 · 1 실패
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import lesson_notes, usage_log  # noqa: E402
from stages.scripts.codex_client import ClaudeClient  # noqa: E402
from stages.scripts.prompt_parts import load_lesson_contract  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = PROJECT_DIR / "prompts" / "desk_fix_system.md"
SCHEMA = PROJECT_DIR / "schemas" / "desk_fix_output.schema.json"
SELF_CHECK_TOOLS = ("Bash(python -B -m stages.scripts.desk_check:*)",)


def build_prompt(lesson_dir: Path, gyo6: Path, lesson_ref: str, notes: list[dict], self_check: str) -> str:
    open_notes = [n for n in notes if n.get("status") == "open"]
    body = "\n\n".join(f"### {n['id']}\n\n{n['text'].strip()}" for n in open_notes)
    return "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {lesson_ref}\nLESSON_DIR: {lesson_dir}\nGYO6_ROOT: {gyo6}",
        f"## NOTES — 이번에 고칠 메모 {len(open_notes)}건\n\n{body}",
        "## 참고: lesson 계약서 (파이프라인이 만드는 차시 기준 — 이미 있는 차시가 다 지키지는 않는다. "
        "메모를 고치는 데 필요한 부분만 참고한다)\n\n" + load_lesson_contract(),
        f"SELF_CHECK:\n{self_check}",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 AI 고치기")
    parser.add_argument("--gyo6-root", type=Path, required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--desk-dir", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--lesson-dir", type=Path, default=None,
                        help="고칠 차시 폴더(작업대가 지정). 없으면 <gyo6>/lessons/<lesson>")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max", "ultra"],
                        help="추론 강도(작업대 사이드바에서 고른 것). 없으면 CLI 설정")
    parser.add_argument("--model", default=None, help="이 AI 의 모델(작업대 사이드바에서 고른 것). 없으면 CLI 기본")
    parser.add_argument("--timeout-seconds", type=int, default=2400)
    args = parser.parse_args()

    gyo6 = args.gyo6_root.resolve()
    lesson_dir = args.lesson_dir.resolve() if args.lesson_dir else gyo6 / "lessons" / args.lesson
    desk_dir = args.desk_dir.resolve()
    # 작업대가 메모를 '고치는 중'으로 바꾼 뒤 부른다. 프롬프트에는 그중 코드 메모만 넘긴다.
    notes = [dict(n, status="open") for n in lesson_notes.load(desk_dir)
             if n.get("status") == "working" and lesson_notes.kind_of(n) == "code"]
    if not notes:
        print("고칠 코드 메모가 없다")
        return 1

    self_check = (f'python -B -m stages.scripts.desk_check "{lesson_dir}" --baseline "{args.baseline.resolve()}" '
                  f'--gyo6-root "{gyo6}"')
    usage_log.bind(desk_dir, f"desk_fix {args.lesson}", tag=os.environ.get("DESK_STEP", ""))
    client = ClaudeClient(effort=args.effort or "", claude_bin=args.claude_bin, project_dir=PROJECT_DIR, timeout_seconds=args.timeout_seconds,
                          allowed_tools=SELF_CHECK_TOOLS,
                          add_dirs=tuple(dict.fromkeys((str(gyo6), str(lesson_dir)))))
    output = desk_dir / "last-fix.json"
    if output.exists():
        output.unlink()
    print(f"AI 고치기: {args.lesson} · 메모 {sum(1 for n in notes if n['status'] == 'open')}건")
    client.run_prompt(build_prompt(lesson_dir, gyo6, args.lesson, notes, self_check), SCHEMA, output, stage="desk_fix", model=args.model or None)
    if not output.exists():
        print("결과 파일이 없다")
        return 1
    result = json.loads(output.read_text(encoding="utf-8"))
    for item in result.get("notes", []):
        print(f"  {item['id']}: {item['result']} — {item['detail']}")
    print(f"자가 검사: {result.get('self_check')} · {result.get('summary')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
