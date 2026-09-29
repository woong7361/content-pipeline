"""완성 화면을 스토리보드 예시화면과 대조해 **고칠 것 목록**을 만든다 (LLM 1회, codex).

    python -B ./diff_screens.py runs/{run_id} --target ../gyo6_content --lesson 3-1/05
    python -B ./diff_screens.py runs/{run_id} --target ../gyo6_content --lesson 3-1/05 --pages 5-10
    python -B ./diff_screens.py runs/{run_id} --target ../gyo6_content --lesson 3-1/05 --prepare-only

**이 파이프라인에 없던 축이다.** 있던 것은 둘뿐이었다.

    tools/check_rendered.mjs   화면 **자체**의 결함 — 버튼 화면 밖, 겹침, 깨진 그림, 진행 막힘
    review_lesson.py           화면을 codex 가 보고 판정 — 다만 스토리보드는 **글로만** 넘어간다

원본 PDF 왼쪽 절반을 차지하는 **예시화면 그림**은 어느 쪽에도 실리지 않았다. 그래서
"완성 화면이 기획된 화면처럼 보이는가"를 한 번도 묻지 않았고, 레이아웃·비례·글자 크기가
어긋나도 사람이 눈으로 볼 때만 드러났다(problem.md `[screen-not-matched-to-storyboard-mockup]`).

게이트는 **결함**을 보고, 이 대조는 **의도**를 본다. 둘은 겹치지 않는다.

종료 코드
  0  고칠 것이 없거나 medium/low 만 있다
  2  high 가 있거나, 짝이 될 화면을 못 찾은 스토리보드 쪽이 있다 (장면 누락 신호)
  1  실행 자체가 실패했다
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from stages.screen_diff import (
    diff_screens,
    format_diff,
    format_fixes,
    plan_fixes,
    render_storyboard_pages,
    write_fix_markdown,
    write_markdown,
)
from stages.scripts import usage_log
from validate import validate_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent
CAPTURE_SCRIPT = PROJECT_DIR / "tools" / "capture_lesson.mjs"
NEEDS_CHANGE_EXIT = 2


def find_storyboard(run_dir: Path, given: Path | None) -> Path | None:
    """원본 스토리보드를 찾는다. **PDF 를 우선한다** — 예시화면 그림이 거기에만 있다.

    `stage_storyboard` 가 원본을 run 안으로 복사해 두므로 보통 `runs/{id}/storyboard.*` 다.
    전사본 `.md` 밖에 없으면 그림이 없다는 뜻이라, 그 사실을 부르는 쪽이 알아야 한다.
    """
    if given:
        return given.resolve()
    for suffix in (".pdf", ".md"):
        candidate = run_dir / f"storyboard{suffix}"
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="완성 화면을 스토리보드 예시화면과 대조한다.")
    parser.add_argument("run_dir", type=Path, help="runs/{run_id}")
    parser.add_argument("--target", type=Path, required=True, help="gyo6_content 프로젝트 루트")
    parser.add_argument("--lesson", required=True, help="배치한 자리. 예: 3-1/05")
    parser.add_argument("--storyboard", type=Path, default=None, help="원본 PDF. 없으면 run 안에서 찾는다")
    parser.add_argument("--pages", default=None, help="대조할 쪽 범위. 예: 5-10. 없으면 전부")
    parser.add_argument("--url", default=None, help="직접 URL 을 줄 때. 없으면 dist 의 index.html")
    parser.add_argument("--max-shots", type=int, default=30)
    parser.add_argument(
        "--no-scene-jump",
        action="store_true",
        help="학습자가 누르는 길만 밟는다. 기본은 base 의 `?dev` 장면 이동으로 **문제 화면까지** 찍는다",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="쪽 렌더와 화면 캡처만 하고 대조하지 않는다 (LLM 0회)",
    )
    parser.add_argument(
        "--fix-plan",
        action="store_true",
        help="대조에 이어 **수정안**까지 만든다. 소스를 열어 앵커·현재 값·바꿀 값을 확정한다 (LLM +1회)",
    )
    parser.add_argument(
        "--fix-plan-only",
        action="store_true",
        help="이미 있는 대조 결과로 수정안만 만든다. 대조를 다시 돌리지 않는다 (LLM 1회)",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    usage_log.bind(run_dir, f"diff_screens {args.lesson}")
    target_root = args.target.resolve()
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not lesson_path.exists():
        print(f"lesson 번들이 없다: {lesson_path}", file=sys.stderr)
        return 1

    dist_index = target_root / "dist" / Path(args.lesson) / "index.html"
    if args.url is None and not dist_index.exists():
        print(f"빌드 산출물이 없다. 먼저 npm run build:lesson -- {args.lesson}", file=sys.stderr)
        return 1
    target_url = args.url or str(dist_index)

    slot = args.lesson.replace("/", "-")
    output_path = run_dir / f"screen_diff_{slot}.json"
    capture_dir = run_dir / "review" / slot
    page_dir = run_dir / "review" / "storyboard-pages"

    # 이미 만든 대조 결과로 수정안만 낸다. 쪽 렌더도 캡처도 다시 하지 않는다 —
    # 대조를 다시 돌리면 같은 값을 또 사서 쓰는 셈이다.
    if args.fix_plan_only:
        if not output_path.exists():
            print(f"대조 결과가 없다: {output_path}\n  먼저 --fix-plan 없이 한 번 돌린다.", file=sys.stderr)
            return 1
        return run_fix_plan(run_dir, slot, output_path, capture_dir, page_dir, args)

    # ── ① 스토리보드 쪽을 이미지로. 이것이 대조의 한쪽이다.
    storyboard = find_storyboard(run_dir, args.storyboard)
    if storyboard is None:
        print("스토리보드를 찾지 못했다. --storyboard 로 원본 PDF 를 준다.", file=sys.stderr)
        return 1
    try:
        pages = render_storyboard_pages(storyboard, page_dir, args.pages)
    except (FileNotFoundError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not pages:
        print(
            f"예시화면 그림이 없다: {storyboard.name} 는 PDF 가 아니다.\n"
            "  전사본 .md 에는 설명 표만 있고 **예시화면 그림이 없다.** 원본 PDF 를 --storyboard 로 준다.",
            file=sys.stderr,
        )
        return 1
    print(f"스토리보드 쪽 {len(pages)}장 → {page_dir}")

    # ── ② 완성 화면. `review_lesson.py` 와 같은 캡처기를 쓴다.
    capture_dir.mkdir(parents=True, exist_ok=True)
    print(f"캡처: {target_url}")
    # 기본은 장면 이동이다. 배치를 보는 것이 목적인데 학습자 경로는 **문제 앞에서 멈춘다** —
    # 드래그·선 긋기·키패드를 자동으로 못 풀기 때문이다. 실측(2026-09-11): 그 모드로는
    # 15장이 전부 컷씬이었고 미션 다섯 개의 배치는 한 장도 안 찍혔다. 안 찍힌 화면은 대조도 못 한다.
    capture_command = ["node", str(CAPTURE_SCRIPT), target_url, str(capture_dir), str(args.max_shots), str(target_root)]
    if not args.no_scene_jump:
        capture_command.append("--scene-jump")
    result = subprocess.run(
        capture_command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1
    capture = json.loads((capture_dir / "capture.json").read_text(encoding="utf-8"))
    print(f"  화면 {len(capture.get('shots', []))}장 → {capture_dir}")
    if capture.get("stuck"):
        print("  ⚠ 진행이 멈췄다 — 뒤쪽 화면은 안 찍혔다. 누락으로 단정하지 않는다")

    if args.prepare_only:
        return 0

    # ── ③ 대조. 그림을 여는 도구가 codex 쪽에만 있어 provider 는 고정이다.
    storyboard_text = ""
    text_source = run_dir / "storyboard.md"
    if text_source.exists():
        storyboard_text = text_source.read_text(encoding="utf-8")

    print(f"\nscreen_diff provider=codex model={args.model or 'default'}")
    diff_screens(
        capture_dir=capture_dir,
        page_dir=page_dir,
        lesson_path=lesson_path,
        output_path=output_path,
        storyboard_text=storyboard_text,
        codex_bin=args.codex_bin,
        claude_bin=args.claude_bin,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    validation = validate_file(output_path, artifact="screen_diff_output")
    if validation["status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 1

    report = json.loads(output_path.read_text(encoding="utf-8"))
    markdown_path = run_dir / "review" / f"screen-diff-{slot}.md"
    write_markdown(report, markdown_path)

    print()
    print(format_diff(report))
    print(f"\n고칠 것 목록: {markdown_path}")
    print(f"원본 판정:    {output_path}")

    high = [c for c in report.get("changes") or [] if c.get("priority") == "high"]
    diff_code = NEEDS_CHANGE_EXIT if (high or report.get("unmatched_pages")) else 0

    # ── ④ 수정안. 대조가 "무엇이 다른가"까지라면 이쪽은 "어느 줄을 무엇으로"다.
    if args.fix_plan and report.get("changes"):
        fix_code = run_fix_plan(run_dir, slot, output_path, capture_dir, page_dir, args)
        if fix_code == 1:
            return 1
    return diff_code


def run_fix_plan(
    run_dir: Path,
    slot: str,
    diff_path: Path,
    capture_dir: Path,
    page_dir: Path,
    args: argparse.Namespace,
) -> int:
    """대조 결과를 그대로 적용할 수 있는 수정안으로 내린다.

    대조를 다시 돌리지 않는다 — 1차 결과를 재사용한다. 다시 돌리면 같은 값을 또 사서 쓰는 셈이다.
    """
    for needed, what in ((capture_dir / "capture.json", "화면 캡처"), (page_dir, "스토리보드 쪽 이미지")):
        if not needed.exists():
            print(f"{what}가 없다: {needed}", file=sys.stderr)
            print("  --prepare-only 로 먼저 만든다.", file=sys.stderr)
            return 1

    # 대조가 본 화면과 지금 캡처가 어긋나면 수정안이 조용히 부실해진다.
    # 실측(2026-09-11): 대조 뒤에 `--prepare-only` 를 다시 돌려 `capture.json` 을 덮는 바람에
    # 대조가 근거로 쓴 `s16` 이 사라졌고, 그 항목의 수정안이 "현재 화면을 못 봤다"로 내려앉았다.
    # 캡처는 `--max-shots` 와 진행 상태에 따라 장 수가 달라지므로 언제든 어긋날 수 있다.
    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    have = {
        shot.get("file")
        for shot in json.loads((capture_dir / "capture.json").read_text(encoding="utf-8")).get("shots", [])
        if isinstance(shot, dict)
    }
    want = {c.get("screen") for c in diff.get("changes") or [] if c.get("screen")}
    missing = sorted(want - have)
    if missing:
        print(f"⚠ 대조가 근거로 쓴 화면 {len(missing)}장이 지금 캡처에 없다: {', '.join(missing)}", file=sys.stderr)
        print("  그 항목은 현재 값을 못 재므로 수정안이 부실해진다.", file=sys.stderr)
        print("  대조할 때와 같은 --max-shots 로 다시 캡처한 뒤 돌린다.", file=sys.stderr)

    output_path = run_dir / f"screen_fix_{slot}.json"
    print()
    print(f"screen_fix provider=codex model={args.model or 'default'}")
    plan_fixes(
        diff_path=diff_path,
        capture_dir=capture_dir,
        page_dir=page_dir,
        lesson_dir=run_dir / "lesson",
        output_path=output_path,
        codex_bin=args.codex_bin,
        claude_bin=args.claude_bin,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    validation = validate_file(output_path, artifact="screen_fix_output")
    if validation["status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 1

    report = json.loads(output_path.read_text(encoding="utf-8"))
    markdown_path = run_dir / "review" / f"screen-fix-{slot}.md"
    write_fix_markdown(report, markdown_path)
    print()
    print(format_fixes(report))
    print()
    print(f"수정안:    {markdown_path}")
    print(f"원본 판정: {output_path}")
    return NEEDS_CHANGE_EXIT if report.get("fixes") else 0


if __name__ == "__main__":
    sys.exit(main())
