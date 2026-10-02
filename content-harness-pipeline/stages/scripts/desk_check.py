"""차시 작업대의 AI 고치기가 **끝내기 전에 스스로 돌리는** 검사. 읽기만 한다.

    python -B -m stages.scripts.desk_check <gyo6 차시 폴더> --baseline <작업 전 사본 폴더> --gyo6-root <gyo6_content>

`self_check` 와 다른 점 — 작업대는 gyo6 에 이미 있는 차시(사람이 만든 것 포함)를 고친다. 그런 차시는
파이프라인 게이트를 처음부터 다 지키지 않는다. 그래서 위반 **전체**가 아니라 **작업 전보다 새로 생긴 것**만 본다.
있던 것까지 고치라고 하면 메모에 없는 곳을 건드린다.

    · lesson.json 이 JSON 인가
    · player-ext.js 문법(node --check)
    · 게이트(check_lesson_standalone) 위반 중 작업 전 사본에 없던 것

게이트는 run 의 `lesson/` 구조를 기대하므로 두 쪽 모두 임시 폴더에 같은 모양으로 옮겨 잰다(그림은 옮기지 않는다 —
그림 존재 검사는 양쪽에 똑같이 걸려 차이에서 빠진다).

종료 코드: 0 통과 · 2 새 위반 있음 · 1 실행 실패
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from stages.scripts.atom_registry import load_atom_registry
from stages.scripts.lesson_check import check_lesson_standalone, collect_asset_refs, errors_only, resolve_source

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BUNDLE = ("lesson.json", "player-ext.js", "player-ext.css")


def gate(folder: Path, registry) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp)
        (run / "lesson").mkdir()
        for name in BUNDLE:
            if (folder / name).exists():
                shutil.copy2(folder / name, run / "lesson" / name)
        lesson = json.loads((run / "lesson" / "lesson.json").read_text(encoding="utf-8"))
        refs: set[str] = set()
        collect_asset_refs(lesson, refs)
        draft = {"asset_refs": sorted(refs)}
        if (run / "lesson" / "player-ext.js").exists():
            draft["player_ext_js_path"] = "lesson/player-ext.js"
        if (run / "lesson" / "player-ext.css").exists():
            draft["player_ext_css_path"] = "lesson/player-ext.css"
        return errors_only(check_lesson_standalone(lesson, draft, run, registry))


def broken_refs(folder: Path) -> set[str]:
    """lesson.json 이 가리키는데 그 폴더에 파일이 없는 그림 경로(확장자는 따지지 않는다 — webp 로 압축돼 있을 수 있다)."""
    refs: set[str] = set()
    collect_asset_refs(json.loads((folder / "lesson.json").read_text(encoding="utf-8")), refs)
    return {ref for ref in refs if resolve_source(folder, ref) is None}


def key(item: dict) -> str:
    return f"{item.get('kind')}|{item.get('where')}|{item.get('detail')}"


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 자가 검사(읽기 전용)")
    parser.add_argument("lesson_dir", type=Path)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--gyo6-root", type=Path, default=None)
    args = parser.parse_args()

    lesson_dir = args.lesson_dir.resolve()
    try:
        json.loads((lesson_dir / "lesson.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"lesson.json 이 없다: {lesson_dir}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"자가 검사 실패 — lesson.json 이 JSON 이 아니다: {exc}")
        return 2

    js_error = ""
    ext_js = lesson_dir / "player-ext.js"
    if ext_js.exists():
        result = subprocess.run(["node", "--check", str(ext_js)], capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if result.returncode != 0:
            js_error = (result.stderr or result.stdout).strip()[:800]

    registry = load_atom_registry(args.gyo6_root.resolve() if args.gyo6_root else None)
    before = {key(v) for v in gate(args.baseline.resolve(), registry)}
    new = [v for v in gate(lesson_dir, registry) if key(v) not in before]

    # 코드 메모가 파일 이름을 바꾸거나 지울 수 있게 되면서(2026-10-01) — 작업 전엔 있던 그림이 이제 깨졌는지 본다.
    # 작업 전 사본이 차시 폴더 전체(그림 포함)이므로 양쪽을 같은 방식으로 잴 수 있다
    baseline = args.baseline.resolve()
    broken = sorted(broken_refs(lesson_dir) - (broken_refs(baseline) if (baseline / "lesson.json").exists() else set()))

    for item in new:
        print(f"- 새 위반: [{item.get('kind')}] {item.get('where')} — {item.get('detail')}")
    for ref in broken:
        print(f"- 깨진 그림 참조: lesson.json 이 가리키는 {ref} 파일이 차시 폴더에 없다(작업 전에는 있었거나 새로 넣은 참조)")
    if js_error:
        print(f"\nplayer-ext.js 문법 오류:\n{js_error}")
    if not new and not js_error and not broken:
        print("\n자가 검사 통과 — 새 게이트 위반 0 · 깨진 그림 참조 0 · ext 문법 정상")
        return 0
    print(f"\n자가 검사 실패 — 새 게이트 위반 {len(new)}건 · 깨진 그림 참조 {len(broken)}건{' · ext 문법 오류' if js_error else ''}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
