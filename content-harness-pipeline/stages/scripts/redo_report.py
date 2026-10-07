"""초안 [스토리보드와 대조해 다시 만들기]의 가운데 — 대조 결과와 사람 메모를 개발 단계가 읽을 목록 하나로 묶는다.

`lesson_desk.py` 의 /pipeline 화면이 쓴다(2026-10-06 사용자 요청 — 초안이 이상하면 스토리보드를 다시 보고 고치게).

    diff_screens.py --fix-plan   → review/screen-fix-{slot}.md (없으면 screen-diff-{slot}.md)
    이 스크립트                   → review/redo-{작업 번호}.md   = 사람 메모 + 위 파일
    produce_lesson.py --start-at senior_developer --through develop --screen-report <위 파일>

대조 파일은 **이번 작업이 시작된 뒤에 쓴 것만** 싣는다. 대조에서 다른 점이 없으면 diff_screens 는 수정안을
새로 쓰지 않으므로, 시각을 안 보면 지난번 수정안을 다시 적용하게 된다.

종료 코드: 0 목록 만듦 · 3 고칠 것 없음(대조도 메모도 비었다 — 개발 단계를 부르지 않는다).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

NOTHING_EXIT = 3


def fresh(path: Path, since: float) -> bool:
    return path.is_file() and path.stat().st_mtime >= since


def build(run_dir: Path, slot: str, note: str, since: float) -> str:
    slot_id = slot.replace("/", "-")
    review = run_dir / "review"
    fix, diff = review / f"screen-fix-{slot_id}.md", review / f"screen-diff-{slot_id}.md"
    source = fix if fresh(fix, since) else diff if fresh(diff, since) else None
    parts = []
    if note.strip():
        parts.append("## 사람이 본 것 — 먼저 고친다\n\n" + note.strip())
    if source is not None:
        what = "수정안" if source == fix else "대조 결과(수정안 없음 — 소스를 열어 값을 정한다)"
        parts.append(f"## 스토리보드 예시화면과 대조한 {what} — `{source.relative_to(run_dir).as_posix()}`\n\n"
                     + source.read_text(encoding="utf-8").strip())
    if not parts:
        return ""
    head = ("# 스토리보드를 다시 보고 고칠 것\n\n"
            "지금 `lesson/` 을 기준으로 아래 항목만 고친다. 스토리보드 원본(storyboard_path)을 열어 해당 쪽을 직접 확인하고,\n"
            "목록에 없는 곳은 건드리지 않는다.")
    return head + "\n\n" + "\n\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="대조 결과 + 사람 메모 → 개발 단계 되먹임 목록")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--lesson", required=True, help="배치한 자리. 예: 4-1/05")
    parser.add_argument("--since", type=float, required=True, help="이번 작업 시작 시각(epoch 초)")
    parser.add_argument("--note", type=Path, default=None, help="사람이 적은 메모 파일")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    note = args.note.read_text(encoding="utf-8") if args.note and args.note.is_file() else ""
    text = build(args.run_dir.resolve(), args.lesson, note, args.since)
    if not text:
        print("대조에서 다른 점이 없고 메모도 비었다. 고칠 것 없음. 개발 단계를 부르지 않는다")
        return NOTHING_EXIT
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"고칠 목록: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
