"""개발 단계가 **끝내기 전에 스스로 돌리는** 검사. 읽기만 한다.

    python -B -m stages.scripts.self_check <run_dir> --gyo6-root <gyo6_content>

왜 있는가 — 개발 단계는 claude 를 `--permission-mode acceptEdits` 로 부른다. 파일은 고칠 수 있지만
명령은 못 돌린다(비대화형이라 허락해 줄 사람이 없다). 그래서 고친 결과가 맞는지 **다음 검증에서야**
알았고, 한 바퀴를 더 돌았다(실측 2026-09-29 — 개발 노트: "node·python 실행 권한이 없어 검사를 못 돌렸다").
이 명령 **하나만** 허용 목록에 올린다(`ClaudeClient.allowed_tools`). 쓰는 명령·git·삭제는 허용하지 않는다.

보는 것은 파이프라인이 최종 판정에 쓰는 것과 같은 게이트다.

    · check_lesson_standalone   lesson.json — 원자 어휘·step 구조·말풍선·정답 모양 …
    · node --check              player-ext.js 문법

화면은 못 본다 — 배치·빌드가 있어야 열 수 있다. 그건 `verify_lesson.py` 몫이다.
쪽수 대응(`pages_total`/`pages_mapped`)은 모델이 마지막에 내는 보고서에 있어 여기서는 건너뛴다.

종료 코드: 0 통과 · 2 위반 있음 · 1 실행 실패
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from stages.scripts.atom_registry import load_atom_registry
from stages.scripts.lesson_check import check_lesson_standalone, collect_asset_refs, errors_only, format_violations

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="개발 단계 자가 검사(읽기 전용)")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--gyo6-root", type=Path, default=None)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    lesson_path = run_dir / "lesson" / "lesson.json"
    try:
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"lesson.json 이 없다: {lesson_path}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"lesson.json 이 JSON 이 아니다: {exc}")
        return 2

    # 게이트 일부는 **보고서와 파일이 맞는가**를 본다(asset_refs · ext 경로). 보고서는 모델이 마지막에 내므로
    # 여기서는 실제 파일과 lesson.json 으로 채운다 — 보고서 일치는 파이프라인의 최종 판정이 다시 본다.
    ext_js = run_dir / "lesson" / "player-ext.js"
    refs: set[str] = set()
    collect_asset_refs(lesson, refs)
    draft = {"asset_refs": sorted(refs)}
    if ext_js.exists():
        draft["player_ext_js_path"] = "lesson/player-ext.js"
    if (run_dir / "lesson" / "player-ext.css").exists():
        draft["player_ext_css_path"] = "lesson/player-ext.css"
    registry = load_atom_registry(args.gyo6_root.resolve() if args.gyo6_root else None)
    violations = check_lesson_standalone(lesson, draft, run_dir, registry)
    errors = errors_only(violations)

    js_error = ""
    if ext_js.exists():
        result = subprocess.run(["node", "--check", str(ext_js)], capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if result.returncode != 0:
            js_error = (result.stderr or result.stdout).strip()[:800]

    if violations:
        print(format_violations(violations))
    if js_error:
        print(f"\nplayer-ext.js 문법 오류:\n{js_error}")
    if not errors and not js_error:
        print("\n자가 검사 통과 — 게이트 위반 0 · ext 문법 정상")
        return 0
    print(f"\n자가 검사 실패 — 게이트 위반 {len(errors)}건{' · ext 문법 오류' if js_error else ''}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
