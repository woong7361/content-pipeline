"""차시 작업대의 [AI 맡기기] 중 **코드 메모** — 열린 코드 메모대로 **gyo6 차시 폴더를 직접** 고친다. `lesson_desk.py` 가 작업으로 부른다.

    python -B ./desk_fix.py --gyo6-root <gyo6_content> --lesson 4-1/04 --desk-dir desk/4-1-04 --baseline <작업 전 사본>

- 코드 메모는 **차시 폴더 안의 무엇이든** 한다 — 세 파일 고치기만이 아니라 파일 이름 바꾸기 · 데드코드·안 쓰는 파일 치우기 ·
  메모가 가리키는 md 대로 하기(2026-10-01 사용자 지적, problem.md [desk-code-scope-too-narrow]). 그림을 새로 그리는 것과
  검증만 코덱스 몫이다. 범위와 방법은 `prompts/desk_fix_system.md`.
- claude 는 파이프라인 폴더에서 돌고(`--setting-sources project`), gyo6 는 `--add-dir` 로만 연다.
  허용 명령은 자가 검사(`stages.scripts.desk_check`)와 파일 옮기기(`mv` · `mkdir` · `cp`)뿐이다. **`rm` 은 막는다** —
  지울 파일은 `REMOVED_DIR`(작업대 폴더)로 옮기게 해서 사람이 되살릴 수 있다. 실패하면 작업대가 차시 폴더 전체를 되돌린다.
- 메모에 md 파일 경로가 적혀 있으면 그 폴더도 `--add-dir` 로 열어 읽을 수 있게 한다.
- 끝나고 gyo6 에서 **차시 폴더 밖**이 바뀌었으면(git status) 결과에 ⚠ 로 적는다 — `mv` 는 경로를 막을 수 없어서다.
- 결과(메모별 fixed · needs_image · needs_confirm · not_fixed)는 `{desk-dir}/last-fix.json` 에 남긴다.
  메모 상태를 바꾸는 것은 작업대가 한다 — 이 스크립트는 결과만 낸다.

종료 코드: 0 끝남 · 1 실패
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
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
# 자가 검사 + 파일 옮기기. 지우기는 **거부 목록으로** 막는다 — 허용 목록에서 빼는 것만으로는 안 막힌다:
# acceptEdits 가 작업 폴더 안의 rm 을 자동 허락했다(2026-10-01 실측). 지울 것은 REMOVED_DIR 로 옮긴다(되살릴 수 있게)
ALLOWED_TOOLS = ("Bash(python -B -m stages.scripts.desk_check:*)", "Bash(mv:*)", "Bash(mkdir:*)", "Bash(cp:*)")
DENIED_TOOLS = ("Bash(rm:*)", "Bash(rmdir:*)", "Bash(del:*)", "Bash(git:*)")
MD_PATH = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|*?]+?\.md\b|(?:\.{0,2}/)?[^\s\"'<>|*?:]+\.md\b")


def md_dirs(notes: list[dict], bases: list[Path]) -> list[str]:
    """메모(보완 포함)에 적힌 md 파일의 폴더 — claude 가 읽을 수 있게 --add-dir 로 연다. 실제로 있는 파일만."""
    text = "\n".join(lesson_notes.prompt_block(n) for n in notes)
    found = []
    for raw in MD_PATH.findall(text):
        candidates = [Path(raw)] if Path(raw).is_absolute() else [base / raw for base in bases]
        for path in candidates:
            if path.is_file():
                found.append(str(path.resolve().parent))
                break
    return list(dict.fromkeys(found))


def git_changes(gyo6: Path) -> set[str] | None:
    """gyo6 의 바뀐 파일(git status). git 이 없거나 저장소가 아니면 None."""
    try:
        out = subprocess.run(["git", "-C", str(gyo6), "status", "--porcelain", "-uall"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {line[3:].strip().strip('"') for line in out.stdout.splitlines()} if out.returncode == 0 else None


def build_prompt(lesson_dir: Path, gyo6: Path, lesson_ref: str, notes: list[dict], self_check: str, removed_dir: Path,
                 desk_dir: Path | None = None) -> str:
    open_notes = [n for n in notes if n.get("status") == "open"]
    body = "\n\n".join(lesson_notes.prompt_block(n, desk_dir) for n in open_notes)
    return "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {lesson_ref}\nLESSON_DIR: {lesson_dir}\nGYO6_ROOT: {gyo6}\nREMOVED_DIR: {removed_dir}",
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
    removed_dir = desk_dir / "removed" / (os.environ.get("DESK_STEP") or "manual")
    extra_dirs = md_dirs(notes, [lesson_dir, gyo6, PROJECT_DIR])
    client = ClaudeClient(effort=args.effort or "", claude_bin=args.claude_bin, project_dir=PROJECT_DIR, timeout_seconds=args.timeout_seconds,
                          allowed_tools=ALLOWED_TOOLS, disallowed_tools=DENIED_TOOLS,
                          add_dirs=tuple(dict.fromkeys((str(gyo6), str(lesson_dir), str(desk_dir), *extra_dirs))))
    output = desk_dir / "last-fix.json"
    if output.exists():
        output.unlink()
    print(f"AI 고치기: {args.lesson} · 메모 {sum(1 for n in notes if n['status'] == 'open')}건"
          + (f" · 메모의 md 폴더: {', '.join(extra_dirs)}" if extra_dirs else ""))
    before = git_changes(gyo6)
    client.run_prompt(build_prompt(lesson_dir, gyo6, args.lesson, notes, self_check, removed_dir, desk_dir), SCHEMA, output,
                      stage="desk_fix", model=args.model or None)
    if not output.exists():
        print("결과 파일이 없다")
        return 1
    result = json.loads(output.read_text(encoding="utf-8"))
    # 차시 폴더 밖이 바뀌었나 — mv 는 경로를 막을 수 없다. 되돌리지는 않고(사람이 따로 고친 것일 수 있다) 크게 적는다
    after = git_changes(gyo6)
    if before is not None and after is not None:
        try:
            inside = lesson_dir.resolve().relative_to(gyo6).as_posix() + "/"
        except ValueError:
            inside = None
        outside = sorted(p for p in after - before if not (inside and p.startswith(inside)))
        if outside:
            warn = f"- ⚠ 차시 폴더 밖 gyo6 파일이 바뀌었다(이 작업 또는 그사이 다른 손): {', '.join(outside[:10])}"
            print(warn)
            for item in result.get("notes", []):
                item["detail"] = "\n".join([str(item.get("detail", "")).rstrip(), warn]).strip()
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in result.get("notes", []):
        print(f"  {item['id']}: {item['result']} — {item['detail']}")
    print(f"자가 검사: {result.get('self_check')} · {result.get('summary')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
