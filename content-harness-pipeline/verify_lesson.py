"""배치·빌드된 차시를 **화면으로** 검증하고, 걸린 것을 고칠 담당자별로 나눠 보낸다.

    python -B ./verify_lesson.py runs/{run_id} --target {GYO6} --lesson 4-1/03
    python -B ./verify_lesson.py runs/{run_id} --target {GYO6} --lesson 4-1/03 --skip-llm

`produce_lesson.py` 의 마지막 검사(`check_outputs`)는 데이터만 본다 — 화면을 한 번도 열지 않는다.
그래서 4-1/03 은 그 검사를 통과한 채로 힌트 가림 · 탑 밖에 뜬 각 · 원문 문구 문제를 안고 있었고,
전부 사람이 시킨 수동 검수에서야 나왔다(2026-09-29). 이 스크립트가 그 자리다.

네 층을 싼 것부터 돈다.

    ① 화면 결함      tools/check_rendered.mjs       LLM 0  깨진 그림·겹침·넘침·진행 막힘
    ② 기능 테스트    tools/run_functional_tests.mjs LLM 0  문항마다 오답→재시도·힌트·정답을 **실제로 푼다**
    ③ 캡처          ②의 학습자 경로 전 화면         LLM 0  멈췄으면 capture_lesson --scene-jump 로 채운다
    ④ 화면 판정      lesson_review · screen_diff    LLM 2  ③을 보고 판정 / 스토리보드 예시화면과 대조

①②에서 막는 것(blocking)이 나오면 ④는 건너뛴다 — 고치고 다시 돌면 ④가 볼 화면이 바뀐다.
`--force-review` 로 그래도 돌릴 수 있다.

만드는 일과 남의 레포를 건드리는 일을 섞지 않는다. 이 스크립트는 **배치도 빌드도 하지 않는다.**
배치된 것과 빌드가 run 보다 오래됐으면 멈추고 할 일을 알려 준다.

결과는 `runs/{run_id}/verify/` 에 모인다.

    report.md          요약 · 층별 결과 · 담당자별 건수 · 다음 명령
    findings.json      모든 지적(담당자·심각도·근거 캡처)
    test-results.json  tests/functional-test-plan.json 의 케이스별 결과
    to-developer.md    senior_developer 되먹임 — `--screen-report` 로 그대로 넘긴다
    to-asset.json/.md  다시 구울 그림 — `--rerender-from` 으로 그대로 넘긴다
    to-storyboard.md   원고 담당 확인 — 원문 그대로인데 틀린 문구
    to-runtime.md      gyo6 공통 런타임 — 이 차시 밖
    to-human.md        담당을 정할 근거가 없는 것

종료 코드
  0  막는 것이 없다(medium·low 는 남을 수 있다)
  2  막는 것이 있다 — blocking 또는 high
  1  실행 자체가 실패했다
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from diff_screens import find_storyboard
from stages.lesson_review import review_lesson
from stages.screen_diff import diff_screens, render_storyboard_pages, write_markdown as write_diff_markdown
from stages.scripts import install_record
from stages.scripts.storyboard_readability import extract_pdf_text
from stages.scripts.verify_routing import (
    OWNER_LABEL,
    OWNERS,
    asset_routes,
    from_diff,
    from_functional,
    from_rendered,
    from_review,
    is_blocking,
    sort_findings,
)
from stages.scripts import usage_log
from validate import validate_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

KST = timezone(timedelta(hours=9))
PROJECT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = PROJECT_DIR / "tools"
BLOCKED_EXIT = 2


def main() -> int:
    parser = argparse.ArgumentParser(description="배치·빌드된 차시를 화면으로 검증하고 담당자별로 나눈다.")
    parser.add_argument("run_dir", type=Path, help="runs/{run_id}")
    parser.add_argument("--target", type=Path, required=True, help="gyo6_content 프로젝트 루트")
    parser.add_argument("--lesson", required=True, help="배치한 자리. 예: 4-1/03")
    parser.add_argument("--storyboard", type=Path, default=None, help="원본 PDF. 없으면 run 안에서 찾는다")
    parser.add_argument("--max-shots", type=int, default=80, help="장면 이동 캡처 최대 장수")
    parser.add_argument("--skip-llm", action="store_true", help="①②③만 돈다 (LLM 0회)")
    parser.add_argument("--force-review", action="store_true", help="①②에서 막는 것이 나와도 ④를 돈다")
    parser.add_argument("--allow-stale", action="store_true", help="배치·빌드가 run 보다 오래됐어도 검사한다")
    parser.add_argument("--model", default=None)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    usage_log.bind(run_dir, f"verify_lesson {args.lesson}")
    # 초안 대시보드가 "검증이 도는 중인가" 를 pid 로 본다(끝 기록만으로는 도중에 죽은 것과 못 가른다).
    append_log(run_dir, {"lesson": args.lesson, "pid": os.getpid()}, event="verify_start")
    target = args.target.resolve()
    lesson_dir = run_dir / "lesson"
    lesson_path = lesson_dir / "lesson.json"
    if not lesson_path.exists():
        print(f"lesson 번들이 없다: {lesson_path}", file=sys.stderr)
        return 1
    dist_index = target / "dist" / Path(args.lesson) / "index.html"
    installed = target / "lessons" / Path(args.lesson) / "lesson.json"

    stale = staleness(run_dir, target, args.lesson, installed, dist_index)
    if stale:
        print("검증할 화면이 이 run 의 것이 아니다:", file=sys.stderr)
        for line in stale:
            print(f"  · {line}", file=sys.stderr)
        print("\n먼저 배치하고 빌드한다:", file=sys.stderr)
        print(f"  python -B ./install_lesson.py {rel(run_dir)} --target {target} --lesson {args.lesson}", file=sys.stderr)
        print(f"  cd {target} && npm run build:lesson -- {args.lesson}", file=sys.stderr)
        if not args.allow_stale:
            return 1
        print("--allow-stale — 그대로 검사한다", file=sys.stderr)

    verify_dir = run_dir / "verify"
    screens_dir = verify_dir / "screens"
    screens_dir.mkdir(parents=True, exist_ok=True)
    layers: dict[str, str] = {}
    findings: list[dict] = []

    # ── ① 화면 결함
    print("① 화면 결함 (check_rendered)")
    rendered_path = verify_dir / "rendered.json"
    code = run_node([TOOLS_DIR / "check_rendered.mjs", target, args.lesson, "--json", rendered_path])
    if code not in (0, 1) or not rendered_path.exists():
        return 1
    rendered = read_json(rendered_path)
    findings += from_rendered(rendered, lesson_dir)
    layers["① 화면 결함"] = f"위반 {len(rendered.get('violations') or [])}건"

    # ── ② 기능 테스트
    print("\n② 기능 테스트 (run_functional_tests)")
    code = run_node([TOOLS_DIR / "run_functional_tests.mjs", dist_index, screens_dir, target])
    results_path = screens_dir / "functional-results.json"
    if code not in (0, 1) or not results_path.exists():
        return 1
    results = read_json(results_path)
    spec = read_json(run_dir / "spec" / "lesson-spec.json") if (run_dir / "spec" / "lesson-spec.json").exists() else {}
    plan_path = run_dir / "tests" / "functional-test-plan.json"
    plan = read_json(plan_path) if plan_path.exists() else {"cases": []}
    functional, cases = from_functional(results, plan, spec, lesson_dir, screens_dir, confirmed_assets(run_dir))
    findings += functional
    flow_only = [p["id"] for p in results.get("problems") or [] if p.get("mode") == "flow-only"]
    failed_cases = [c for c in cases if c["status"] in ("fail", "not_reached")]
    layers["② 기능 테스트"] = (
        f"문항 {len(results.get('problems') or [])}개 · 케이스 {len(cases)}건 중 실패·미도달 {len(failed_cases)}건"
        + (f" · 진행 멈춤" if results.get("stuck") else "")
        + (f" · UI 대신 흐름만 본 문항 {len(flow_only)}개({', '.join(flow_only)})" if flow_only else "")
    )
    write_json(verify_dir / "test-results.json", {"cases": cases, "flow_only": flow_only})

    # ── ③ 캡처
    # ②가 학습자 경로를 **끝까지** 걸었으면 그 순서대로 찍은 화면(대사·이야기·문제 상태·완료·인증서)이
    # 곧 전 화면이다. 장면 이동 캡처를 또 붙이면 같은 화면이 두 벌이 되어 ④의 판정 비용만 는다.
    # 중간에 멈췄으면 뒤쪽을 못 봤으므로 장면 이동(`--scene-jump`)으로 나머지 화면을 채운다.
    capture_path = screens_dir / "capture.json"
    timeline = [
        {"file": item["file"], "clicked": f"학습자 경로 · {item['label']}", "stage_text": ""}
        for item in results.get("timeline") or []
    ]
    walked = not results.get("stuck") and not any(e.startswith("automation:") for e in results.get("page_errors") or [])
    if walked:
        print("\n③ 캡처 — ②가 끝까지 걸은 화면을 쓴다")
        capture = {"url": results.get("url"), "mode": "functional-walk", "shots": timeline,
                   "stuck": False, "page_errors": results.get("page_errors") or []}
        layers["③ 캡처"] = f"{len(timeline)}장 (학습자 경로 전체 + 문제 상태별)"
    else:
        print("\n③ 캡처 — ②가 멈췄다. 장면 이동으로 나머지 화면을 채운다 (capture_lesson --scene-jump)")
        code = run_node([TOOLS_DIR / "capture_lesson.mjs", dist_index, screens_dir, str(args.max_shots), target, "--scene-jump"])
        if code != 0 or not capture_path.exists():
            return 1
        capture = read_json(capture_path)
        capture["shots"] = timeline + (capture.get("shots") or [])
        layers["③ 캡처"] = f"{len(capture['shots'])}장 (멈추기 전 학습자 경로 + 장면 이동)"
    write_json(capture_path, capture)

    # ── ④ 화면 판정 (LLM)
    blocked_early = [f for f in findings if f["severity"] == "blocking"]
    if args.skip_llm:
        layers["④ 화면 판정"] = "건너뜀 (--skip-llm)"
    elif blocked_early and not args.force_review:
        layers["④ 화면 판정"] = f"건너뜀 — ①②에서 막는 것 {len(blocked_early)}건. 고친 뒤 다시 돈다 (--force-review 로 강제)"
    else:
        findings += run_llm_layers(run_dir, lesson_path, screens_dir, verify_dir, args, layers)

    # ── 나눠 보내기
    findings = sort_findings(findings)
    write_json(verify_dir / "findings.json", {"findings": findings})
    routes = asset_routes(findings)
    write_json(verify_dir / "to-asset.json", {"assets": routes})
    commands = next_commands(run_dir, target, args.lesson)
    for owner in OWNERS:
        write_owner_file(verify_dir, owner, [f for f in findings if f["owner"] == owner], routes, commands)
    blocking = [f for f in findings if is_blocking(f)]
    write_report(verify_dir, args.lesson, layers, findings, cases, commands)
    append_log(run_dir, {
        "lesson": args.lesson,
        "findings": len(findings),
        "blocking": len(blocking),
        "by_owner": {owner: sum(1 for f in findings if f["owner"] == owner) for owner in OWNERS},
    })

    print()
    for name, summary in layers.items():
        print(f"{name}: {summary}")
    print(f"\n지적 {len(findings)}건 · 막는 것 {len(blocking)}건")
    for owner in OWNERS:
        mine = [f for f in findings if f["owner"] == owner]
        if mine:
            stop = sum(1 for f in mine if is_blocking(f))
            print(f"  {owner:<10} {len(mine)}건 (막는 것 {stop}) → {rel(verify_dir / f'to-{owner}.md')}")
    print(f"\n요약: {rel(verify_dir / 'report.md')}")
    return BLOCKED_EXIT if blocking else 0


def staleness(run_dir: Path, target: Path, lesson_ref: str, installed: Path, dist_index: Path) -> list[str]:
    """검사할 화면이 **이 run 의 지금 산출물**로 만든 것인지 본다.

    배치 기록(`install-record.json`)이 있으면 **내용**으로 본다 — run 이 배치 뒤 바뀌었나,
    gyo6 쪽이 배치 뒤 바뀌었나. 실측(2026-09-29) — gyo6 쪽에서 그림 6장을 다시 구워 run 과
    갈라졌는데, 시각만 보는 검사는 "최신" 이라고 통과시켰다. 기록이 없는 옛 배치만 시각으로 본다.
    """
    if not installed.exists():
        return [f"배치된 차시가 없다: {installed}"]
    if not dist_index.exists():
        return [f"빌드 산출물이 없다: {dist_index}"]
    problems = []
    record = install_record.entry(run_dir, target, lesson_ref)
    if record:
        changed = install_record.source_drift(record, run_dir / "lesson")
        if changed:
            problems.append(f"배치 뒤 run 쪽이 바뀌었다 — 다시 배치해야 한다: {', '.join(changed[:6])}")
        drifted = install_record.target_drift(record, installed.parent)
        if drifted:
            problems.append(
                f"배치 뒤 gyo6 쪽이 바뀌었다 — 화면이 이 run 의 것이 아니다: {', '.join(drifted[:6])}"
            )
    else:
        problems.append("배치 기록이 없다(옛 배치) — 시각으로만 본다")
        if installed.stat().st_mtime < (run_dir / "lesson" / "lesson.json").stat().st_mtime:
            problems.append("run 의 lesson.json 이 배치된 것보다 새것이다 — 다시 배치해야 한다")
        problems = problems if len(problems) > 1 else []
    if dist_index.stat().st_mtime < installed.stat().st_mtime:
        problems.append("배치가 빌드보다 새것이다 — 다시 빌드해야 한다")
    return problems


def run_llm_layers(run_dir: Path, lesson_path: Path, screens_dir: Path, verify_dir: Path,
                   args: argparse.Namespace, layers: dict[str, str]) -> list[dict]:
    source_text = storyboard_source_text(run_dir)
    planned = planned_assets(run_dir)
    items: list[dict] = []

    print("\n④-1 화면 판정 (lesson_review, codex)")
    review_path = verify_dir / "lesson_review.json"
    storyboard_md = run_dir / "storyboard.md"
    # 지난 실행의 판정이 남아 있으면 이번 호출이 실패해도 그것을 새 결과로 읽는다. 먼저 치운다.
    review_path.unlink(missing_ok=True)
    try:
        review_lesson(
            capture_dir=screens_dir,
            lesson_path=lesson_path,
            storyboard_path=storyboard_md if storyboard_md.exists() else None,
            output_path=review_path,
            codex_bin=args.codex_bin,
            claude_bin=args.claude_bin,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
        )
    except (RuntimeError, TimeoutError) as exc:
        # 판정이 죽어도 ①②③ 결과와 보고서는 남긴다. 못 본 것은 통과가 아니므로 사람 몫으로 올린다.
        print(f"  화면 판정 실패: {str(exc).splitlines()[0][:160]}")
        review_path.unlink(missing_ok=True)
    if review_path.exists() and validate_file(review_path, artifact="lesson_review_output")["status"] == "PASS":
        review = read_json(review_path)
        items += from_review(review, screens_dir, source_text, planned)
        layers["④-1 화면 판정"] = f"{review.get('status')} · 지적 {len(review.get('priority_findings') or [])}건"
    else:
        layers["④-1 화면 판정"] = "실패 — 판정 파일이 없거나 schema 가 안 맞는다"
        items.append(unfinished("review", "화면 판정(lesson_review)이 결과를 못 냈다"))

    print("\n④-2 스토리보드 대조 (screen_diff, codex)")
    storyboard = find_storyboard(run_dir, args.storyboard)
    page_dir = run_dir / "review" / "storyboard-pages"
    pages = []
    if storyboard is not None:
        try:
            pages = render_storyboard_pages(storyboard, page_dir)
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"  {exc}")
    if not pages:
        layers["④-2 스토리보드 대조"] = "건너뜀 — 스토리보드 PDF 쪽 이미지를 못 만들었다(예시화면 그림은 PDF 에만 있다)"
        return items
    diff_path = verify_dir / "screen_diff.json"
    diff_path.unlink(missing_ok=True)
    try:
        diff_screens(
            capture_dir=screens_dir,
            page_dir=page_dir,
            lesson_path=lesson_path,
            output_path=diff_path,
            storyboard_text=storyboard_md.read_text(encoding="utf-8") if storyboard_md.exists() else "",
            codex_bin=args.codex_bin,
            claude_bin=args.claude_bin,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
        )
    except (RuntimeError, TimeoutError) as exc:
        print(f"  스토리보드 대조 실패: {str(exc).splitlines()[0][:160]}")
        diff_path.unlink(missing_ok=True)
    if diff_path.exists() and validate_file(diff_path, artifact="screen_diff_output")["status"] == "PASS":
        diff = read_json(diff_path)
        write_diff_markdown(diff, verify_dir / "screen-diff.md")
        items += from_diff(diff, screens_dir, planned)
        layers["④-2 스토리보드 대조"] = f"{diff.get('status')} · 고칠 것 {len(diff.get('changes') or [])}건"
    else:
        layers["④-2 스토리보드 대조"] = "실패 — 대조 파일이 없거나 schema 가 안 맞는다"
        items.append(unfinished("screen_diff", "스토리보드 대조(screen_diff)가 결과를 못 냈다"))
    return items


def unfinished(layer: str, issue: str) -> dict:
    # 못 본 것을 통과로 세지 않는다.
    return {"layer": layer, "severity": "high", "owner": "human", "where": "검사 도구", "issue": issue,
            "evidence": [], "route_reason": "판정이 없으면 화면이 괜찮은지 모른다"}


def storyboard_source_text(run_dir: Path) -> str:
    """문구가 원문 그대로인지 볼 때 대조할 글. 원본에 가까운 것부터 모은다.

    PDF 는 글자 추출이 안 되는 것이 있다(ToUnicode 없음 — 4-1/01). 그래서 기획서도 함께 본다.
    `content-plan.md` 는 대사·문항을 **원문 그대로** 옮기도록 강제된 문서다.
    """
    parts = []
    for name in ("storyboard.md",):
        path = run_dir / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    pdf = run_dir / "storyboard.pdf"
    if pdf.exists():
        extracted = extract_pdf_text(pdf)
        if extracted and extracted.get("hangul", 0) > 200:
            parts.append(extracted["text"])
    plan = run_dir / "planning" / "content-plan.md"
    if plan.exists():
        parts.append(plan.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def confirmed_assets(run_dir: Path) -> dict[str, str]:
    """`asset-plan.json` 의 `specId → path`. 명세의 잠정 경로 대신 이것으로 파일을 찾는다."""
    path = run_dir / "design" / "asset-plan.json"
    if not path.exists():
        return {}
    return {
        a["specId"]: a["path"]
        for a in read_json(path).get("assets") or []
        if isinstance(a, dict) and a.get("specId") and a.get("path")
    }


def planned_assets(run_dir: Path) -> list[str]:
    path = run_dir / "design" / "asset-plan.json"
    if not path.exists():
        return []
    return [a["path"] for a in read_json(path).get("assets") or [] if isinstance(a, dict) and a.get("path")]


def next_commands(run_dir: Path, target: Path, lesson: str) -> dict[str, list[str]]:
    run = rel(run_dir)
    again = [
        f"python -B ./install_lesson.py {run} --target {target} --lesson {lesson}",
        f"cd {target} && npm run build:lesson -- {lesson}",
        f"python -B ./verify_lesson.py {run} --target {target} --lesson {lesson}",
    ]
    return {
        "developer": [
            f"python -B ./produce_lesson.py {run} --gyo6-root {target} --start-at senior_developer "
            f"--through develop --screen-report {run}/verify/to-developer.md",
            *again,
        ],
        "asset": [
            f"python -B ./produce_lesson.py {run} --gyo6-root {target} --start-at asset_render "
            f"--through render --rerender-from {run}/verify/to-asset.json",
            *again,
        ],
        "again": again,
    }


OWNER_INTRO = {
    "developer": [
        "`verify_lesson.py` 가 빌드된 화면을 검사해 **개발 단계가 고칠 것**만 모은 것이다.",
        "",
        "- 지금 있는 `lesson/lesson.json` · `lesson/player-ext.css` · `lesson/player-ext.js` 를 **기준으로** "
        "`# 고칠 것` 절의 항목만 고친다. `# 참고` 절은 고치지 않는다. 처음부터 다시 만들지 않는다.",
        "- 캡처 경로가 적혀 있으면 **실제로 열어 본다.** 글만 읽고 짐작하지 않는다.",
        "- 그림과 좌표가 어긋나면 **구워진 그림에 좌표를 맞춘다.** 그림 파일은 바꾸지 않는다.",
        "- 문구를 고칠 때 스토리보드 원문과 다르게 만들지 않는다. 원문이 틀린 것은 이 목록에 없다(원고 담당에게 따로 갔다).",
        "- 문항 수·보기·정답을 줄여서 통과시키지 않는다.",
    ],
    "asset": [
        "그림 **자체**가 잘못 그려진 것이다. 위치가 어긋난 것은 여기 없다(개발이 좌표를 맞춘다).",
        "",
        "- `to-asset.json` 의 경로가 빈 항목은 **어느 그림인지 코드가 못 정한 것**이다. 사람이 `path` 를 채운 뒤 넘긴다.",
        "- `--rerender-from` 은 목록의 그림을 `lesson/assets/.rejected/` 로 옮긴 뒤 그것만 다시 굽는다. 각 항목의 `notes` 가 그 그림의 수정 지시로 실린다.",
    ],
    "storyboard": [
        "화면에 나온 문구가 **스토리보드 원문 그대로**인데 틀렸다고 지적된 것이다.",
        "원문 보존 규칙 때문에 개발 단계가 임의로 고치지 않는다. 원고 담당이 원문을 확인하고,",
        "고치기로 하면 인터뷰 답(`--interview-notes`)으로 넘겨 개발 단계를 다시 돌린다.",
    ],
    "runtime": [
        "gyo6_content 공통 런타임(base)에서 난 문제다. 이 차시의 파일로 고칠 수 없다.",
        "그쪽 레포에 따로 알린다. 이 차시를 막는 이유로 세지 않을지는 사람이 정한다.",
    ],
    "human": [
        "담당을 정할 근거가 없거나(LLM 이 `unknown` 이라고 했다), 검사 도구가 끝까지 못 돈 것이다.",
        "사람이 보고 담당을 정한다. 검사 도구가 못 돈 것은 **통과가 아니다.**",
    ],
}


def write_owner_file(verify_dir: Path, owner: str, items: list[dict], routes: list[dict],
                     commands: dict[str, list[str]]) -> None:
    lines = [f"# 화면 검증 — {OWNER_LABEL[owner]}", "", *OWNER_INTRO[owner], ""]
    if not items:
        lines += ["이번 검증에서 이 담당으로 온 것이 없다.", ""]

    def render(item: dict) -> list[str]:
        stop = " · **막음**" if is_blocking(item) else ""
        out = [f"## {item['id']} [{item['severity']}{stop}] {item['where']}", "", item["issue"], ""]
        out += [f"- {evidence}" for evidence in item["evidence"]]
        return out + [f"- 층: {item['layer']} · 이 담당인 이유: {item['route_reason']}", ""]

    if owner == "developer":
        # **막는 것만 고친다.** 실측(2026-09-29, 4-1/03) — 23건을 한꺼번에 넘겼더니 막는 3건은 고쳤지만
        # medium 배치 재설계 20건을 함께 바꾸다 새로 막는 것 5건(라벨 겹침·말풍선 화면 밖)을 만들었다.
        # 한 바퀴에 바뀌는 범위를 줄여야 무엇이 무엇을 깼는지 거슬러 갈 수 있다.
        must = [item for item in items if is_blocking(item)]
        rest = [item for item in items if not is_blocking(item)]
        if items:
            lines += ["# 고칠 것 — 막는 것(blocking·high)", ""]
            lines += [line for item in must for line in render(item)] or ["없다.", ""]
        if rest:
            lines += [
                "# 참고 — 이번에 고치지 않는다",
                "",
                "medium·low 다. **이 절의 항목은 고치지 않는다.** 사람이 골라 다음 바퀴의 '고칠 것' 으로 올린다.",
                "",
            ]
            lines += [line for item in rest for line in render(item)]
    else:
        lines += [line for item in items for line in render(item)]
    if owner == "asset" and routes:
        lines += ["## 다시 구울 목록 (`to-asset.json`)", ""]
        for route in routes:
            lines.append(f"- `{route['path'] or '(경로 미정 — 채워야 한다)'}` ← {', '.join(n.split(' ', 1)[0] for n in route['notes'])}")
        lines.append("")
    actionable = [i for i in items if is_blocking(i)] if owner == "developer" else items
    if actionable and owner in commands:
        lines += ["## 다음 명령", "", "```bash", *commands[owner], "```", ""]
    (verify_dir / f"to-{owner}.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(verify_dir: Path, lesson: str, layers: dict[str, str], findings: list[dict],
                 cases: list[dict], commands: dict[str, list[str]]) -> None:
    blocking = [f for f in findings if is_blocking(f)]
    lines = [
        f"# 화면 검증 — {lesson}",
        "",
        f"- 검증 시각: {datetime.now(KST).isoformat(timespec='seconds')}",
        f"- 판정: **{'막음' if blocking else '통과'}** — 지적 {len(findings)}건 · 막는 것 {len(blocking)}건",
        "",
        "## 층별 결과",
        "",
        "| 층 | 결과 |",
        "|---|---|",
        *[f"| {name} | {summary} |" for name, summary in layers.items()],
        "",
        "## 담당자별",
        "",
        "| 담당 | 건수 | 막는 것 | 파일 |",
        "|---|---:|---:|---|",
    ]
    for owner in OWNERS:
        mine = [f for f in findings if f["owner"] == owner]
        lines.append(f"| {OWNER_LABEL[owner]} | {len(mine)} | {sum(1 for f in mine if is_blocking(f))} | `to-{owner}.md` |")
    lines += ["", "## 지적 목록", "", "| id | 심각도 | 담당 | 위치 | 내용 |", "|---|---|---|---|---|"]
    for item in findings:
        issue = item["issue"].replace("|", "\\|").replace("\n", " ")[:140]
        lines.append(f"| {item['id']} | {item['severity']} | {item['owner']} | {item['where']} | {issue} |")
    unreached = [c for c in cases if c["status"] not in ("pass", "skip")]
    if unreached:
        lines += ["", "## 테스트 계획 중 통과 못 한 케이스", "", "| 케이스 | 상태 | 내용 |", "|---|---|---|"]
        for case in unreached:
            lines.append(f"| {case['id']} | {case['status']} | {case['detail']} |")
        lines += ["", "`not_observed` 는 판정이 아니다 — 대사·문항 id 로 그 장면을 확인하지 못했다는 뜻이다."]
    lines += ["", "## 다음 명령", ""]
    owners_with_work = [
        o for o in ("developer", "asset")
        if any(f["owner"] == o and (o != "developer" or is_blocking(f)) for f in findings)
    ]
    if not owners_with_work:
        lines.append("개발·그림 쪽으로 보낼 것이 없다. 원고·런타임·사람 몫은 각 파일을 본다.")
    for owner in owners_with_work:
        lines += [f"{OWNER_LABEL[owner]}:", "", "```bash", *commands[owner], "```", ""]
    (verify_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_log(run_dir: Path, payload: dict, event: str = "verify_end") -> None:
    record = {"at": datetime.now(KST).isoformat(), "event": event, **payload}
    with (run_dir / "pipeline-log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_node(argv: list) -> int:
    """node 도구를 부르고 출력을 그대로 보여 준다. 도구마다 0/1 은 판정이고 2 는 실행 실패다."""
    with usage_log.step(Path(str(argv[0])).stem):
        result = subprocess.run(
            ["node", *[str(a) for a in argv]],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,
        )
    out = (result.stdout or "").strip()
    if out:
        print("  " + out.replace("\n", "\n  "))
    if result.returncode not in (0, 1):
        print((result.stderr or "").strip(), file=sys.stderr)
    return result.returncode


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_DIR).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
