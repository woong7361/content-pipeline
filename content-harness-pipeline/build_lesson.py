"""gyo6_content 차시 폴더를 만든다 (LLM 1회 + 되먹임 재시도).

    lesson/lesson.json      런타임이 읽는 데이터        (모델)
    lesson/player-ext.js    원자로 안 되는 조작만        (모델, 비는 것이 정상)
    lesson/player-ext.css   차시 전용 배치·스킨          (모델, 거의 항상 필요)
    lesson/manifest.json    에셋 목록과 상태             (코드)


초안 경로는 하나다. 스토리보드 원본을 읽어 gyo6_content 차시 번들을 바로 만든다.

    python -B ./build_lesson.py runs/{run_id}                      # 디렉토리 → 원본 초안 재검증
    python -B ./build_lesson.py "../스토리보드.pdf" --run-id g4l02   # 파일 → 원본에서 바로
    python -B ./build_lesson.py runs/{run_id} --check-only          # LLM 0회. 검사만 다시

상류 게이트가 없으므로 읽기 경로 확인과 페이지 대응표가 충실도 기준이다.
에셋은 여기서 만들지 않는다. gyo6_content 빌드의 imagegen 이 만든다.

배치는 하지 않는다. `install_lesson.py` 가 한다 — 남의 git 을 건드리는 일과 산출물을 만드는
일을 한 스크립트에 두면 어느 쪽이 실패했는지 사후에 갈라내지 못한다.

종료 코드
  0  번들을 만들었고 확정된 위반이 없다
  2  만들었지만 위반이 있다. 배치하지 않는다(무엇이 걸렸는지는 출력에 있다)
  1  실행 자체가 실패했다
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from stages.lesson_drafter import draft_lesson as build_from_storyboard
from stages.scripts.atom_registry import describe, load_atom_registry
from stages.scripts.lesson_check import (
    check_lesson_standalone,
    errors_only,
    format_violations,
)
from stages.scripts.lesson_manifest import build_manifest
from stages.scripts.storyboard_readability import check_storyboard_readable, format_readability
from validate import validate_file

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서
# 죽는다. 출력은 항상 UTF-8로 고정하고, 못 싣는 글자는 크래시 대신 치환한다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


KST = timezone(timedelta(hours=9))
PROJECT_DIR = Path(__file__).resolve().parent
REJECTED_EXIT = 2


@dataclass
class Source:
    """근거에 따라 달라지는 것만 모은다. 나머지는 두 경로가 한 몸이다.

    새 근거를 추가한다면 여기에 한 항목을 더하고 아래 루프는 건드리지 않는다.
    """

    kind: str  # "storyboard"
    label: str  # 사람이 읽는 이름
    stage: Callable[..., object]  # 모델을 부르는 함수
    stage_kwargs: dict  # 그 함수의 근거 인자
    schema_artifact: str  # 보고서 schema 이름
    report_path: Path  # 보고서를 남길 자리
    check: Callable[[dict, dict, Path, dict | None], list[dict]]
    manifest_paths: Callable[[dict, Path], tuple[list[str], dict[str, int]]]
    summary: Callable[[dict], str]
    next_hint: str
    extra: dict = field(default_factory=dict)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a gyo6_content lesson bundle straight from a storyboard."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="스토리보드 파일 또는 기존 runs/{run_id} 디렉토리(원본 초안 재검증)",
    )
    parser.add_argument("--run-id", default=None, help="원본에서 만들 때의 run_id. 기본값은 {오늘}_{파일명}")
    parser.add_argument("--runs-dir", type=Path, default=PROJECT_DIR / "runs")
    parser.add_argument("--model", default=None)
    parser.add_argument("--provider", default=None, choices=("codex", "claude"))
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument(
        "--max-retries", type=int, default=2, help="검증 실패를 프롬프트에 되먹여 다시 부르는 횟수"
    )
    parser.add_argument(
        "--gyo6-root",
        type=Path,
        default=None,
        help="gyo6_content 경로. 주면 그쪽 런타임의 PROBLEM_ATOMS 를 읽어 같은 기준으로 검사한다",
    )
    parser.add_argument("--overwrite", action="store_true", help="이미 있는 번들을 다시 만든다")
    parser.add_argument(
        "--screen-report",
        type=Path,
        default=None,
        help=(
            "tools/check_rendered.mjs 출력 파일. 첫 시도부터 프롬프트에 되먹인다. "
            "데이터 게이트가 못 보는 것(버튼이 화면 밖으로 밀림 등)을 고치게 하는 유일한 통로다"
        ),
    )
    parser.add_argument("--check-only", action="store_true", help="이미 만든 것만 검사한다. LLM 0회")
    parser.add_argument(
        "--allow-unreadable",
        action="store_true",
        help="원본에서 만들 때, 읽기 경로가 없어도 진행한다. 에이전트가 내용을 지어낼 수 있다",
    )
    args = parser.parse_args()

    gyo6_root = args.gyo6_root.resolve() if args.gyo6_root else None
    registry = load_atom_registry(gyo6_root)

    try:
        run_dir, source = resolve_source_mode(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    lesson_dir = run_dir / "lesson"
    lesson_path = lesson_dir / "lesson.json"

    print(f"run_id={run_dir.name} · 근거={source.label}")
    print(describe(registry, gyo6_root))

    if source.kind == "storyboard" and not args.check_only:
        # 읽기 경로 확인 — 못 읽는 원본으로 만들면 에이전트가 지어내고, 그 결과는 스키마를
        # 통과하므로 파이프라인이 "성공" 이라고 보고한다. 이 경로에는 걸러 줄 상류가 없다.
        readable = check_storyboard_readable(source.extra["storyboard"])
        print(format_readability(readable))
        if not readable["ok"] and not args.allow_unreadable:
            print("\n만들지 않았다. 위 방법 중 하나로 해결한 뒤 다시 돌린다.")
            print("(그래도 강행하려면 --allow-unreadable)")
            return REJECTED_EXIT

    if not args.check_only:
        if lesson_path.exists() and not args.overwrite:
            print(f"\n이미 있다. 다시 만들려면 --overwrite: {lesson_path}", file=sys.stderr)
            return 1
        lesson_dir.mkdir(parents=True, exist_ok=True)
        if source.kind == "storyboard":
            staged = stage_storyboard(source.extra["storyboard"], run_dir)
            source.stage_kwargs["storyboard_path"] = staged
            print(f"원본을 run 안으로 옮겨 읽힌다: {staged.relative_to(PROJECT_DIR).as_posix()}")
        run_build_loop(args, source, run_dir, lesson_path, registry)

    if not source.report_path.exists():
        print(f"\n보고서가 없다: {source.report_path}", file=sys.stderr)
        return 1
    if not lesson_path.exists():
        print(f"\nlesson.json 이 없다: {lesson_path}", file=sys.stderr)
        return 1

    report = json.loads(source.report_path.read_text(encoding="utf-8"))
    try:
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"\nlesson.json 파싱 실패: {exc}", file=sys.stderr)
        return REJECTED_EXIT

    print()
    print(source.summary(report))
    print()
    violations = source.check(lesson, report, run_dir, registry)
    print(format_violations(violations))
    if errors_only(violations):
        print("\n배치하지 않는다. 위반을 고친 뒤 --check-only 로 다시 본다.")
        return REJECTED_EXIT

    manifest = build_manifest(lesson, *source.manifest_paths(report, run_dir))
    (lesson_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print()
    print(f"lesson 번들: {lesson_dir}")
    for name in ("lesson.json", "player-ext.js", "player-ext.css", "manifest.json", "page-map.md"):
        path = lesson_dir / name
        if path.exists():
            print(f"  {name:16} {path.stat().st_size:,} bytes")
    print(
        f"  assets           {len(manifest['assets'])}개"
        + (f" (사람이 채울 것 {len(manifest['manualRequired'])}개)" if manifest["manualRequired"] else "")
    )
    print()
    print(source.next_hint.format(run_dir=run_dir))
    return 0


def resolve_source_mode(args: argparse.Namespace) -> tuple[Path, Source]:
    """인자로 준 것에서 근거를 정한다. **추측하지 않는다** — 디렉토리냐 파일이냐로 갈린다.

    파일이면 새 원본 초안을 만든다. 디렉토리면 원본에서 만든 run 을 `--check-only` 로
    다시 볼 수 있도록 `lesson_draft.json` 이 있는 경우만 허용한다.
    """
    given = args.source.resolve()

    if given.is_file():
        run_id = args.run_id or f"{datetime.now(KST).date().isoformat()}_{slugify(given.stem)}"
        run_dir = (args.runs_dir / run_id).resolve()
        return run_dir, storyboard_source(args, run_dir, given)

    if not given.is_dir():
        raise ValueError(f"디렉토리도 파일도 아니다: {given}")

    if (given / "lesson_draft.json").exists():
        # 원본에서 만든 run 을 다시 검사하는 경우. 원본 경로는 근거 파일을 안 붙잡아 둔다.
        return given, storyboard_source(args, given, storyboard=None)

    raise ValueError(
        f"이 디렉토리에는 근거가 없다: {given}\n"
        "  원본에서 만들려면 스토리보드 파일 경로를 인자로 주고,\n"
        "  기존 run을 재검증하려면 lesson_draft.json 이 있어야 한다"
    )


def storyboard_source(args: argparse.Namespace, run_dir: Path, storyboard: Path | None) -> Source:
    """스토리보드 원본에서 곧바로 만든다. planner 를 거치지 않아 싸고, 그래서 상류 게이트가 없다."""
    return Source(
        kind="storyboard",
        label=f"스토리보드 원본 ({storyboard.name})" if storyboard else "스토리보드 원본",
        stage=build_from_storyboard,
        stage_kwargs={
            "storyboard_path": storyboard,
            "gyo6_root": args.gyo6_root.resolve() if args.gyo6_root else None,
        },
        schema_artifact="lesson_draft_output",
        report_path=run_dir / "lesson_draft.json",
        check=lambda lesson, report, rd, reg: check_lesson_standalone(lesson, report, rd, reg),
        manifest_paths=lambda report, _run_dir: (list(report.get("asset_refs") or []), {}),
        summary=draft_summary,
        next_hint=(
            "다음: python -B ./install_lesson.py {run_dir} --target <gyo6_content 경로> --lesson <슬롯>/<id>\n"
            "      이 경로는 에셋을 만들지 않는다 — 그쪽 npm run build:lesson 의 imagegen 이 생성한다"
        ),
        extra={"storyboard": storyboard},
    )


def stage_storyboard(storyboard: Path, run_dir: Path) -> Path:
    """원본을 run 디렉토리 안으로 복사하고 그 사본을 읽힌다.

    **에이전트는 프로젝트 디렉토리 안만 읽는다.** 그 밖의 파일을 절대 경로로 줘도 열지 못한다.

    실측(2026-09-10) — `../3학년_5차시(편지배달)_우체국.md`(프로젝트 한 단계 위)를 넘겼더니
    에이전트가 "스토리보드 원문을 한 글자도 읽지 못했다"고 보고하고 `lesson.json` 을 만들지
    않았다. 다행히 지어내지 않았고 `page-map.md` 에 이유까지 남겼지만, **읽기 경로 확인은
    그 파일을 통과시켰다** — 그 검사는 PDF 에서 글자가 뽑히는지만 보고 "에이전트가 그 자리에
    닿을 수 있는가"는 안 본다. md 는 무조건 `native` 로 통과한다.

    gyo6_content 도 같은 이유로 cwd 기준 상대 경로로 바꿔 넘기고 원본을 차시 폴더에 둔다
    (`lessons/<id>/storyboard.pdf`, `lessonJsonGenerator.mjs` 의 `toRel`).

    run 디렉토리에 파이프라인 산출물만 두는 규칙과 어긋나지 않는다 — 이 파일은 이 경로의
    **선언된 입력**이고 프롬프트가 이름을 대서 읽힌다. 규칙이 막는 것은 아무도 이름을 대지
    않은 파일이다.
    """
    destination = run_dir / f"storyboard{storyboard.suffix.lower()}"
    if destination.resolve() == storyboard.resolve():
        return destination
    shutil.copyfile(storyboard, destination)
    return destination


def run_build_loop(
    args: argparse.Namespace,
    source: Source,
    run_dir: Path,
    lesson_path: Path,
    registry: dict[str, list[str]] | None,
) -> None:
    """검증 실패를 프롬프트에 되먹여 다시 부른다. 근거가 무엇이든 이 루프는 같다.

    gyo6_content 의 `agent/lessonJsonGenerator.mjs` 에서 가져온 구조다. 그쪽은 `parseLesson`
    실패 메시지를 되먹였고, 여기서는 `lesson_check` 위반 목록을 그대로 되먹인다.

    실패한 산출물은 `.rejected` 로 옮기고 **지운다.** 남기면 다음 실행이 "이미 있음" 으로
    건너뛰어, 깨진 산출물이 조용히 최종본이 된다(그쪽이 실측으로 얻은 함정이다).

    마지막 시도까지 실패해도 예외를 던지지 않는다. 무엇이 걸렸는지는 호출한 쪽이 같은 검사를
    다시 돌려 보고하며, 그때는 산출물이 남아 있어야 사람이 볼 수 있다.
    """
    feedback = screen_feedback(args)
    provider = args.provider or default_provider(source)

    for attempt in range(args.max_retries + 1):
        print(
            f"\n{source.kind} 시도 {attempt + 1}/{args.max_retries + 1} "
            f"provider={provider} model={args.model or 'default'}"
        )
        with tempfile.TemporaryDirectory(prefix="content-harness-lesson-") as temp_dir:
            temp_output = Path(temp_dir) / "lesson-output.json"
            try:
                source.stage(
                    run_dir=run_dir,
                    output_path=temp_output,
                    feedback=feedback,
                    codex_bin=args.codex_bin,
                    claude_bin=args.claude_bin,
                    llm_provider=provider,
                    model=args.model,
                    timeout_seconds=args.timeout_seconds,
                    **source.stage_kwargs,
                )
            except Exception as exc:  # 타임아웃·실행 실패도 되먹임 대상이다
                feedback = f"{type(exc).__name__}: {exc}"
                print(f"  실행 실패: {feedback}")
                reject(lesson_path, attempt < args.max_retries)
                continue

            result = validate_file(temp_output, artifact=source.schema_artifact)
            if result["status"] != "PASS":
                feedback = "; ".join(str(error) for error in result.get("errors", [])[:5])
                print(f"  보고 schema 실패: {feedback}")
                reject(lesson_path, attempt < args.max_retries)
                continue
            report = json.loads(temp_output.read_text(encoding="utf-8"))

        source.report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        if not lesson_path.exists():
            feedback = f"lesson.json 이 저장되지 않았다: {lesson_path}"
            print(f"  {feedback}")
            continue
        try:
            lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            feedback = f"lesson.json 파싱 실패: {exc}"
            print(f"  {feedback}")
            reject(lesson_path, attempt < args.max_retries)
            continue

        violations = source.check(lesson, report, run_dir, registry)
        if not errors_only(violations):
            return
        feedback = format_violations(violations)
        print(f"  검증 실패 {len(errors_only(violations))}건")
        for item in errors_only(violations)[:5]:
            print(f"    · [{item['kind']}] {item['where']} — {item['detail']}")
        reject(lesson_path, attempt < args.max_retries)


def default_provider(source: Source) -> str:
    """원본 경로는 claude 가 기본이다 — PDF 를 페이지 단위로 봐야 하기 때문이다."""
    return "claude" if source.kind == "storyboard" else "codex"


def screen_feedback(args: argparse.Namespace) -> str:
    """지난 회차의 화면 결과를 첫 시도에 실어 보낸다.

    화면 검사는 빌드 뒤에야 돌 수 있어 이 루프 안에서 못 돈다. 이 통로가 없으면 데이터 게이트를
    통과한 산출물은 화면이 깨져 있어도 **모델에게 아무 신호도 가지 않는다** — 실측(2026-09-09)으로
    확인했다. 계약서에 뷰포트 조항만 넣고 다시 돌렸더니 산출물이 바이트까지 같았다.
    """
    report_path = getattr(args, "screen_report", None)
    if not report_path or not report_path.exists():
        return ""
    report = report_path.read_text(encoding="utf-8").strip()
    if not report:
        return ""
    print(f"  화면 보고를 되먹인다: {report_path}")
    return (
        "지난 회차의 산출물을 실제로 빌드해 화면에서 확인한 결과다. "
        "데이터는 유효했지만 화면이 이렇게 나왔다. 이번에는 이것부터 고친다.\n" + report
    )


def reject(lesson_path: Path, remove: bool) -> None:
    """깨진 산출물을 옆으로 치운다.

    `remove` 가 False 면(마지막 시도) 사본만 남기고 원본은 둔다 — 사람이 무엇이 걸렸는지
    직접 열어 봐야 하기 때문이다.
    """
    if not lesson_path.exists():
        return
    try:
        shutil.copyfile(lesson_path, lesson_path.with_suffix(".json.rejected"))
        if remove:
            lesson_path.unlink()
    except OSError:
        pass


def draft_summary(report: dict) -> str:
    lines = [
        f"페이지 {report.get('pages_mapped', 0)}/{report.get('pages_total', 0)} 대응 · "
        f"문항 {report.get('problems_total', 0)}개 · "
        f"asset {len(report.get('asset_refs') or [])}개 · "
        f"draft_notes {len(report.get('draft_notes') or [])}건"
    ]
    for note in report.get("draft_notes") or []:
        if isinstance(note, dict):
            lines.append(
                f"  · {note.get('where', '?')} — {note.get('what', '')} ({note.get('why', '')})"
            )
    return "\n".join(lines)


def slugify(value: str) -> str:
    keep = [char if char.isalnum() else "-" for char in value]
    return "".join(keep).strip("-")[:40] or "storyboard"


if __name__ == "__main__":
    sys.exit(main())
