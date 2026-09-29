"""빌드된 차시 화면을 찍고 판정한다 (캡처 LLM 0회 + 판정 LLM 1회).

    python -B ./review_lesson.py runs/{run_id} --target ../gyo6_content --lesson 4-1/02
    python -B ./review_lesson.py runs/{run_id} --target ../gyo6_content --lesson 4-1/02 --capture-only

**코드 게이트가 못 보는 층을 본다.** 이 파이프라인은 같은 실패를 다섯 번 겪었다 —
데이터가 유효하고 대상 레포의 검증기가 엄격 모드로 통과하고 빌드까지 성공했는데
화면에서만 결함이 드러났고, 전부 사람이 눈으로 찾았다.

HTML 종단에는 `design_review`(스크린샷 LLM 판정)가 그 자리에 있었다. lesson 종단으로 오면서
품질 루프를 통째로 빼는 바람에 그 층이 사라졌다. 이 스크립트가 그것을 되살린다.

캡처는 `tools/capture_lesson.mjs`(node + gyo6_content 의 playwright)가 한다.
**학습자가 실제로 누르는 경로를 그대로 밟는다** — 그 과정에서 "눌러도 안 넘어가는" 결함이 함께 드러난다.

종료 코드
  0  PASS
  2  REJECT (우선순위 high 가 있거나 진행이 멈췄다)
  1  실행 자체가 실패했다
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from stages.lesson_review import review_lesson
from stages.scripts import usage_log
from validate import validate_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PROJECT_DIR = Path(__file__).resolve().parent
CAPTURE_SCRIPT = PROJECT_DIR / "tools" / "capture_lesson.mjs"
REJECTED_EXIT = 2
LESSON_REF_PATTERN = "{슬롯}/{id}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture and review a built lesson's screens.")
    parser.add_argument("run_dir", type=Path, help="runs/{run_id}")
    parser.add_argument("--target", type=Path, required=True, help="gyo6_content 프로젝트 루트")
    parser.add_argument("--lesson", required=True, help=f"배치한 자리. 예: 4-1/02 ({LESSON_REF_PATTERN})")
    parser.add_argument("--url", default=None, help="직접 URL 을 줄 때. 없으면 dist 의 index.html 을 연다")
    parser.add_argument("--max-shots", type=int, default=10)
    parser.add_argument("--storyboard", type=Path, default=None, help="원문 md. 화면 대조에 쓴다")
    parser.add_argument("--model", default=None)
    parser.add_argument("--provider", default="codex", choices=("codex", "claude"))
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--capture-only", action="store_true", help="찍기만 하고 판정하지 않는다 (LLM 0회)")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    usage_log.bind(run_dir, f"review_lesson {args.lesson}")
    target_root = args.target.resolve()
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not lesson_path.exists():
        print(f"lesson 번들이 없다: {lesson_path}", file=sys.stderr)
        return 1

    dist_index = target_root / "dist" / Path(args.lesson) / "index.html"
    if args.url is None and not dist_index.exists():
        print(f"빌드 산출물이 없다. 먼저 npm run build:lesson -- {args.lesson}", file=sys.stderr)
        print(f"  {dist_index}", file=sys.stderr)
        return 1
    target_url = args.url or str(dist_index)

    capture_dir = run_dir / "review" / args.lesson.replace("/", "-")
    capture_dir.mkdir(parents=True, exist_ok=True)

    print(f"캡처: {target_url}")
    result = subprocess.run(
        [
            "node",
            str(CAPTURE_SCRIPT),
            target_url,
            str(capture_dir),
            str(args.max_shots),
            str(target_root),
        ],
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
    print("  " + (result.stdout or "").strip())

    capture = json.loads((capture_dir / "capture.json").read_text(encoding="utf-8"))
    print(f"  화면 {len(capture.get('shots', []))}장 → {capture_dir}")
    if capture.get("stuck"):
        print("  ⚠ 진행이 멈췄다 — 같은 화면이 반복된다. exitCondition 을 먼저 본다")
    for error in capture.get("page_errors", [])[:3]:
        print(f"  ⚠ 페이지 오류: {error[:100]}")

    if args.capture_only:
        return REJECTED_EXIT if capture.get("stuck") else 0

    output_path = run_dir / f"lesson_review_{args.lesson.replace('/', '-')}.json"
    print(f"\nlesson_review provider={args.provider} model={args.model or 'default'}")
    review_lesson(
        capture_dir=capture_dir,
        lesson_path=lesson_path,
        storyboard_path=args.storyboard.resolve() if args.storyboard else None,
        output_path=output_path,
        codex_bin=args.codex_bin,
        claude_bin=args.claude_bin,
        llm_provider=args.provider,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    validation = validate_file(output_path, artifact="lesson_review_output")
    if validation["status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 1

    review = json.loads(output_path.read_text(encoding="utf-8"))
    print()
    print(format_review(review))
    print(f"\n판정: {output_path}")
    high = [f for f in review.get("priority_findings", []) if f.get("priority") == "high"]
    return REJECTED_EXIT if (high or capture.get("stuck")) else 0


def format_review(review: dict) -> str:
    findings = review.get("priority_findings") or []
    gaps = review.get("storyboard_gaps") or []
    order = {"high": 0, "medium": 1, "low": 2}
    lines = [
        f"{review.get('status', '?')} · 본 화면 {review.get('screens_reviewed', 0)}장 · "
        f"지적 {len(findings)}건 · 원문 대비 누락 {len(gaps)}건"
    ]
    for item in sorted(findings, key=lambda x: order.get(x.get("priority"), 9)):
        lines.append(
            f"  [{item.get('priority')}] {item.get('screen')} → {item.get('fix_target')}\n"
            f"      {item.get('issue')}\n"
            f"      근거: {item.get('evidence')}"
        )
    for gap in gaps:
        lines.append(f"  [누락] {gap.get('expected')} — {gap.get('why')}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
