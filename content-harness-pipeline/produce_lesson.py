"""실제 콘텐츠 제작 흐름에 맞춘 차시 초안 파이프라인.

    storyboard
      → senior_planner      planning/content-plan.md
      → senior_designer     design/wireframe.md, design/concept.md
      → interview package   interview/questions.md
      → interview_brief     planning/production-guide.md
      → visual_design       design/visual-design.md, design/asset-plan.md
      → review log          review/design-review-log.md
      → senior_developer    lesson/lesson.json, ext, development-notes.md
      → asset_render        lesson/assets/**  (그림을 실제로 굽는다)

인터뷰는 사람이 답을 채우는 멈춤점이다. `--through interview`까지 먼저 돌리고,
답변을 `--interview-notes`로 넘겨 나머지 단계를 이어간다.

그림은 **개발 뒤에** 굽는다. 그래야 `lesson.json`이 확정한 경로에 정확히 그 이름으로
저장할 수 있다 — 먼저 구우면 개발자가 다른 이름을 쓰고 참조가 어긋난다.
그림 단계만 provider가 codex로 고정된다(이미지 생성 도구가 거기 있다).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stages.scripts.atom_registry import (
    build_class_names_section,
    build_ext_hooks_section,
    describe as describe_atom_registry,
    load_atom_registry,
)
from stages.scripts.codex_client import PROVIDER_CLAUDE, create_prompt_client
from stages.scripts.layout_reference import build_layout_reference_section
from concurrent.futures import ThreadPoolExecutor, as_completed

from stages.scripts.lesson_check import (
    check_lesson_standalone,
    collect_asset_refs,
    errors_only,
    format_violations,
    iter_asset_prompts,
)
from stages.scripts.asset_alpha import chroma_key, has_alpha
from stages.scripts.asset_plan_check import (
    check_asset_plan_file,
    format_asset_plan_violations,
)
from stages.scripts.lesson_manifest import build_manifest
from stages.scripts.prompt_parts import with_asset_spec, with_lesson_contract
from stages.scripts.pipeline_graph import DagNode, PipelineDag, StageCache
from stages.scripts.spec_tests import validate_lesson_spec, write_and_verify
from stages.scripts.storyboard_readability import (
    check_page_count,
    check_storyboard_readable,
    format_page_count,
    format_readability,
)
from stages.scripts import usage_log
from validate import ARTIFACT_SCHEMAS, validate_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


KST = timezone(timedelta(hours=9))
PROJECT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = PROJECT_DIR / "prompts"
REJECTED_EXIT = 2


@dataclass(frozen=True)
class ProductionStage:
    name: str
    prompt_path: Path
    report_name: str
    artifact: str
    expected_files: tuple[str, ...]
    depends_on: tuple[str, ...]
    estimate_input_tokens: int
    estimate_output_tokens: int
    estimate_minutes: float
    # **둘 중 하나만 있으면 되는** 입력. `depends_on` 은 전부 있어야 하지만 이쪽은 하나면 된다.
    # `asset_render` 가 그렇다 — 그릴 목록은 `design/asset-plan.json`(개발과 동시에 돌 때)이나
    # `lesson/lesson.json`(개발이 끝난 뒤·옛 run) 어느 쪽에서든 나온다.
    # 기본값이 있으므로 **반드시 맨 뒤**에 둔다(dataclass 는 기본값 없는 필드를 뒤에 못 둔다).
    depends_any: tuple[str, ...] = ()


STAGES = [
    ProductionStage(
        name="senior_planner",
        prompt_path=PROMPTS_DIR / "senior_planner_system.md",
        report_name="senior_planner.json",
        artifact="content_stage_output",
        expected_files=("planning/content-plan.md",),
        depends_on=(),
        estimate_input_tokens=18000,
        estimate_output_tokens=3500,
        estimate_minutes=8,
    ),
    ProductionStage(
        name="senior_designer",
        prompt_path=PROMPTS_DIR / "senior_designer_system.md",
        report_name="senior_designer.json",
        artifact="content_stage_output",
        expected_files=("design/wireframe.md", "design/concept.md"),
        depends_on=("planning/content-plan.md",),
        estimate_input_tokens=9000,
        estimate_output_tokens=3000,
        estimate_minutes=6,
    ),
    ProductionStage(
        name="interview_brief",
        prompt_path=PROMPTS_DIR / "interview_brief_system.md",
        report_name="interview_brief.json",
        artifact="content_stage_output",
        expected_files=("planning/production-guide.md",),
        depends_on=("planning/content-plan.md", "design/wireframe.md", "design/concept.md"),
        estimate_input_tokens=11000,
        estimate_output_tokens=2500,
        estimate_minutes=5,
    ),
    ProductionStage(
        name="lesson_spec",
        prompt_path=PROMPTS_DIR / "lesson_spec_system.md",
        report_name="lesson_spec.json",
        artifact="content_stage_output",
        expected_files=("spec/lesson-spec.json",),
        depends_on=("planning/content-plan.md", "planning/production-guide.md", "design/wireframe.md", "design/concept.md"),
        estimate_input_tokens=14000,
        estimate_output_tokens=5000,
        estimate_minutes=7,
    ),
    ProductionStage(
        name="visual_design",
        prompt_path=PROMPTS_DIR / "visual_design_system.md",
        report_name="visual_design.json",
        artifact="content_stage_output",
        expected_files=(
            "design/visual-design.md",
            "design/asset-plan.md",
            # 사람이 읽는 md 와 **같은 목록**을 줄임 없이 펼친 기계용 사본이다.
            # 이게 있어야 그림 단계가 `lesson.json` 을 기다리지 않고 개발과 동시에 돈다.
            "design/asset-plan.json",
            "review/design-review-checklist.md",
        ),
        depends_on=("spec/lesson-spec.json", "design/wireframe.md", "design/concept.md"),
        estimate_input_tokens=12000,
        estimate_output_tokens=3500,
        estimate_minutes=7,
    ),
    ProductionStage(
        name="senior_developer",
        prompt_path=PROMPTS_DIR / "senior_developer_system.md",
        report_name="lesson_draft.json",
        artifact="lesson_draft_output",
        expected_files=("lesson/lesson.json", "lesson/page-map.md", "lesson/development-notes.md"),
        # `content-plan.md` 가 여기 있는 이유: 스토리보드의 **장면별 인물 위치·연출 지시**는
        # `senior_planner` 가 `content-plan.md` 에 표로 정확히 옮기는데, `interview_brief` 가
        # 그것을 `production-guide.md` 로 요약하면서 떨어뜨렸다(실측 2026-09-11 — 3-1/05 에서
        # 인물이 전 장면 좌측 고정, 전환 연출 전멸). 개발 단계가 원본 계획을 아예 못 보는
        # 구조였다. 상류가 제대로 받아적어도 중간이 요약하면 하류는 존재 자체를 모른다.
        depends_on=(
            "planning/content-plan.md",
            "planning/production-guide.md",
            "spec/lesson-spec.json",
            "design/visual-design.md",
            "design/asset-plan.md",
        ),
        estimate_input_tokens=18000,
        estimate_output_tokens=6000,
        estimate_minutes=12,
    ),
    ProductionStage(
        name="asset_render",
        prompt_path=PROMPTS_DIR / "asset_render_system.md",
        report_name="asset_render.json",
        artifact="asset_render_output",
        # 그릴 목록이 차시마다 다르므로 고정 파일로 못 적는다. 대신 `lesson.json` 이
        # 참조하는 것이 전부 놓였는지를 배치 단계가 확인한다.
        expected_files=(),
        # **`lesson.json` 을 기다리지 않는다.** 그릴 목록과 지시는 `visual_design` 이 낸
        # `asset-plan.json` 에 이미 다 있다(경로·mustInclude·reservedUiZones·forbidden).
        # 그래서 이 단계는 개발과 **동시에** 돌 수 있다 — 실측으로 개발이 18~36분이라
        # 그 시간에 그림이 같이 구워진다.
        depends_on=(),
        # 둘 중 하나면 된다. 사이드카가 없는 옛 run 은 `lesson.json` 으로 그대로 돈다.
        depends_any=("design/asset-plan.json", "lesson/lesson.json"),
        estimate_input_tokens=14000,
        estimate_output_tokens=2500,
        estimate_minutes=25,
    ),
]

# 이미지 생성 도구는 codex 쪽에 있다. 실측(run 2026-09-08_5cbd474e 의 감사 기록) —
# 에이전트가 자기 도구로 그린 뒤 `generated_images/exec-*.png` 를 목적지 이름으로 복사했다.
# claude 로 이 단계를 돌리면 그릴 수단이 없어 "파일을 만들지 못했다" 로 끝난다.
IMAGE_CAPABLE_PROVIDER = "codex"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the senior production lesson pipeline.")
    parser.add_argument("source", type=Path, help="스토리보드 원본 파일 또는 기존 runs/{run_id}")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--runs-dir", type=Path, default=PROJECT_DIR / "runs")
    parser.add_argument("--provider", choices=("codex", "claude"), default=PROVIDER_CLAUDE)
    parser.add_argument("--model", default=None)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--gyo6-root", type=Path, default=None)
    parser.add_argument("--interview-notes", type=Path, default=None, help="사람 인터뷰 답변 md/jsonl")
    parser.add_argument("--screen-report", type=Path, default=None, help="이전 화면 캡처 리뷰 텍스트")
    parser.add_argument(
        "--through",
        choices=["planning", "interview", "design", "develop", "render", "all"],
        default="all",
    )
    parser.add_argument("--start-at", choices=[stage.name for stage in STAGES], default=STAGES[0].name)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="입력 해시 캐시를 사용하지 않고 선택 범위를 다시 실행한다")
    parser.add_argument("--invalidate", action="append", default=[], choices=[stage.name for stage in STAGES], help="이 단계와 모든 하위 단계를 캐시에서 무효화한다. 여러 번 지정 가능")
    parser.add_argument("--explain-dag", action="store_true", help="단계 의존 관계를 출력한다")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--allow-unreadable", action="store_true")
    parser.add_argument(
        "--asset-batch-size",
        type=int,
        default=6,
        help="그림을 한 호출에 몇 장까지 맡길지. 한 인물의 감정 묶음은 이 값보다 커도 쪼개지 않는다",
    )
    parser.add_argument(
        "--asset-parallel",
        type=int,
        default=4,
        help="그림 배치를 동시에 몇 개까지 돌릴지",
    )
    parser.add_argument(
        "--style-anchor",
        default=None,
        help=(
            "화풍 기준 그림을 **직접 고른다**(번들 안 상대 경로. 예: assets/ui/bin-wood.png). "
            "안 주면 이미 구워진 것 중 첫 장을 자동으로 집는데, 그 자동 선택이 원하는 화풍이 "
            "아닐 수 있다(실측 2026-09-11 — 우편물이 '너무 그래픽적'으로 나왔다). "
            "주면 기준을 만드는 직렬 단계를 건너뛰고 곧바로 병렬로 간다"
        ),
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="개발 단계에서 검증 실패를 프롬프트에 되먹여 다시 부르는 횟수",
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="끝에서 대사 음성 단계(Typecast 웹 대본 내보내기)를 건너뛴다",
    )
    parser.add_argument(
        "--rerender-from",
        type=Path,
        default=None,
        help=(
            "`verify_lesson.py` 가 낸 `verify/to-asset.json`. 목록의 그림을 옆으로 치우고 그것만 다시 굽는다. "
            "항목의 notes 가 그 그림의 수정 지시로 실린다. `--start-at asset_render --through render` 와 함께 쓴다"
        ),
    )
    args = parser.parse_args()

    run_dir, storyboard_path = resolve_run(args)
    run_dir.mkdir(parents=True, exist_ok=True)
    usage_log.bind(run_dir, f"produce_lesson {args.start_at}→{args.through}")
    dag = build_pipeline_dag()
    cache = StageCache(run_dir, dag)
    if args.explain_dag:
        print_dag(dag)
    if args.invalidate:
        affected = cache.invalidate(args.invalidate)
        print(f"캐시 무효화: {', '.join(sorted(affected))}")
    args.rerender_notes = {}
    if args.rerender_from:
        try:
            args.rerender_notes = prepare_rerender(run_dir, args.rerender_from.resolve())
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        # 입력이 그대로라 캐시가 적중해 버린다. 그림 단계만 풀어 준다.
        cache.invalidate(["asset_render"])

    if storyboard_path is not None and not args.check_only:
        readable = check_storyboard_readable(storyboard_path)
        print(format_readability(readable))
        if not readable["ok"] and not args.allow_unreadable:
            return REJECTED_EXIT
        # History 표의 쪽수는 **실제와 자주 다르다** — 실측 4종 중 3종이 적게 적혀 있었다.
        # 막지 않고 알리기만 한다. 기획 단계는 페이지 이미지를 직접 보므로 읽기는 문제없고,
        # 위험한 것은 사람이 그 숫자를 믿고 뒷장을 안 보는 것이다.
        pages = check_page_count(storyboard_path)
        note = format_page_count(pages)
        if note:
            print(note)
        if pages.get("mismatch"):
            write_pipeline_log(run_dir, "page_count_mismatch", {
                "declared": pages["declared"], "actual": pages["actual"],
            })
        staged = stage_storyboard(storyboard_path, run_dir)
        storyboard_path = staged
        print(f"원본을 run 안으로 옮겨 읽힌다: {staged.relative_to(PROJECT_DIR).as_posix()}")

    if args.check_only:
        # 검사만 할 때는 이번 실행이 어디까지 갔는지가 없다. 보고서 존재 여부로 판단한다.
        return check_outputs(run_dir, args, expected_lesson=False)

    write_pipeline_log(
        run_dir,
        "pipeline_start",
        {
            "run_id": run_dir.name,
            "through": args.through,
            "start_at": args.start_at,
            "provider": args.provider,
            "model": args.model or "default",
        },
    )

    selected = select_stages(args.start_at, args.through)
    registry = load_atom_registry(args.gyo6_root.resolve() if args.gyo6_root else None)

    # 개발과 그림은 서로를 기다리지 않는다 — 둘 다 `visual_design` 만 있으면 된다.
    # 짝을 이뤄 선택됐고 사이드카가 있을 때만 겹친다. 없으면 예전처럼 줄을 세운다.
    pair = pair_developer_and_assets(selected, run_dir, args)
    if pair and not args.no_cache:
        pair_fingerprints = {stage.name: stage_fingerprint(cache, stage, args) for stage in pair}
        hits = {stage.name: cache.hit(stage.name, pair_fingerprints[stage.name]) for stage in pair}
        if any(hits.values()):
            # 한쪽만 캐시 적중이면 적중한 작업까지 다시 돌리지 않는다. 각 노드로 나눠 실행한다.
            pair = None

    index = 0
    while index < len(selected):
        stage = selected[index]
        if pair and stage.name == pair[0].name:
            run_developer_and_assets_together(pair, run_dir, storyboard_path, args, registry)
            if not args.no_cache:
                for done in pair:
                    cache.record(done.name, stage_fingerprint(cache, done, args))
            index += 2
            continue
        fingerprint = stage_fingerprint(cache, stage, args)
        if not args.no_cache and not args.overwrite and cache.hit(stage.name, fingerprint):
            print(f"{stage.name} 캐시 적중 — 입력과 상위 산출물이 바뀌지 않았다")
            write_pipeline_log(run_dir, "stage_cached", {"stage": stage.name})
            index += 1
            continue
        ensure_dependencies(run_dir, stage)
        if stage.name == "asset_render":
            run_asset_render(stage, run_dir, args, force=True)
        elif stage.artifact == "lesson_draft_output":
            run_stage_with_feedback(stage, run_dir, storyboard_path, args, registry, force=True)
        else:
            run_stage(stage, run_dir, storyboard_path, args, force=True)
        if stage.name == "lesson_spec":
            validate_spec_file(run_dir)
        if stage.name == "visual_design":
            enforce_asset_plan(stage, run_dir, storyboard_path, args)
        if not args.no_cache:
            cache.record(stage.name, fingerprint)
        write_pipeline_log(run_dir, "stage_done", {"stage": stage.name, "report": stage.report_name})
        index += 1
        # 질문은 **항상** 질문지로 흘려보낸다. 예전에는 `--through interview` 로 끊었을 때만
        # 써서, 통째로 돌리면 각 단계가 낸 질문이 보고서 JSON 안에만 남아 아무도 안 봤다.
        if stage.name == "senior_designer":
            write_interview_package(run_dir)
            if args.through == "interview":
                print(f"인터뷰 질문: {run_dir / 'interview' / 'questions.md'}")
                print("답변을 정리한 뒤 --interview-notes 로 넘겨 이어서 실행한다.")
                return 0

    if any(stage.name in ("visual_design", "senior_developer") for stage in selected):
        write_review_log(run_dir, args)
    # 뒤 단계들이 낸 질문까지 모아 질문지를 갱신한다. 이미 답이 적혀 있으면 덮지 않는다.
    write_interview_package(run_dir)
    # 개발 단계까지 돌렸으면 `lesson.json` 이 있어야 한다. 없으면 실패다 —
    # 인터뷰에서 끊은 경우와 개발이 실패한 경우를 같은 종료 코드로 보고하면
    # 자동화가 실패를 성공으로 읽는다.
    expected_lesson = any(stage.artifact == "lesson_draft_output" for stage in selected)
    with usage_log.step("check_outputs"):
        result = check_outputs(run_dir, args, expected_lesson=expected_lesson)
    write_pipeline_log(run_dir, "pipeline_end", {"exit_code": result})
    print_estimates()
    if result == 0 and (run_dir / "lesson" / "lesson.json").exists():
        with usage_log.step("voice_script"):
            voice_state = run_voice_step(run_dir, args)
        if voice_state != "waiting":
            print_verify_required(run_dir, args)
    return result


def run_voice_step(run_dir: Path, args: argparse.Namespace) -> str:
    """대사 음성 단계. 인물 대표 그림이 나와 있으면 Typecast 웹 대본을 내보내고 사람에게 알린다.

    음성은 초안 위에 얹는 것이라 여기서 실패해도 **초안은 실패가 아니다.** 알리기만 한다.
    """
    if args.no_voice:
        return "skipped"
    import voice_lesson
    from stages.scripts import voice_lines

    lesson = json.loads((run_dir / "lesson" / "lesson.json").read_text(encoding="utf-8"))
    lines, _ = voice_lines.collect(lesson)
    speakers = {line.speaker for line in lines} - {voice_lines.NARRATOR}
    if not lines:
        return "skipped"
    if not all(voice_lesson.character_image(run_dir, lesson, speaker) for speaker in speakers):
        print("\n음성: 인물 대표 그림이 아직 없다 — 그림 단계가 끝난 뒤 voice_lesson.py 를 돌린다")
        return "skipped"
    print("\n── 대사 음성 (Typecast 웹 편집기) ──")
    # 웹 요금제로 만든다 — 대본을 내보내고 사람이 웹에서 만든 파일을 받아들인다. API 는 부르지 않는다.
    code = voice_lesson.run_web(run_dir)
    return "waiting" if code == voice_lesson.WAITING_EXIT else ("done" if code == 0 else "failed")


def print_verify_required(run_dir: Path, args: argparse.Namespace) -> None:
    """여기까지의 검사는 **데이터만** 봤다. 화면 검증은 따로 돌려야 끝난다고 분명히 말한다.

    화면 검증은 gyo6_content 에 배치·빌드해야 돌 수 있어 이 스크립트가 하지 않는다 — 만드는 일과
    남의 레포를 건드리는 일을 섞지 않는다(`install_lesson.py` 가 따로 있는 이유와 같다).
    대신 건너뛰었다는 흔적이 남도록 로그에 적는다. `verify_lesson.py` 가 끝나면 `verify_end` 가 붙는다.
    """
    gyo6 = str(args.gyo6_root.resolve()) if args.gyo6_root else "{GYO6}"
    try:
        run = run_dir.resolve().relative_to(PROJECT_DIR).as_posix()
    except ValueError:
        run = str(run_dir)
    lesson = "{슬롯}/{차시}"
    write_pipeline_log(run_dir, "verify_required", {"run": run})
    print(
        "\n" + "=" * 72 + "\n"
        "초안이 끝났다. **아직 화면을 한 번도 열지 않았다** — 위 검사는 데이터만 본 것이다.\n"
        "반드시 배치 → 빌드 → 화면 검증까지 돌린다. 걸린 것은 담당자별 파일로 나뉜다.\n\n"
        f"  python -B ./install_lesson.py {run} --target {gyo6} --lesson {lesson}\n"
        f"  cd {gyo6} && npm run build:lesson -- {lesson}\n"
        f"  python -B ./verify_lesson.py {run} --target {gyo6} --lesson {lesson}\n\n"
        f"결과: {run}/verify/report.md\n"
        + "=" * 72
    )


def prepare_rerender(run_dir: Path, route_path: Path) -> dict[str, list[str]]:
    """`verify/to-asset.json` 의 그림을 옆으로 치우고, 그림마다 수정 지시를 돌려준다.

    그림 단계는 **파일이 없는 것만** 굽는다(`rendered_asset_gaps`). 그래서 다시 구울 그림은 치워야 한다.
    지우지 않고 `verify/rejected-assets/<시각>/` 로 옮긴다 — `lesson/` 안에 두면
    `install_lesson.py` 가 `assets/` 를 통째로 옮기면서 같이 배치된다.
    """
    if not route_path.exists():
        raise ValueError(f"다시 구울 목록이 없다: {route_path}")
    entries = json.loads(route_path.read_text(encoding="utf-8")).get("assets") or []
    unresolved = [entry for entry in entries if not str(entry.get("path") or "").startswith("assets/")]
    if unresolved:
        lines = [f"경로를 못 정한 항목 {len(unresolved)}건 — `path` 를 채운 뒤 다시 넘긴다:"]
        lines += [f"  · {' / '.join(entry.get('notes') or [entry.get('finding', '?')])[:120]}" for entry in unresolved]
        raise ValueError("\n".join(lines))

    stamp = datetime.now(KST).strftime("%Y%m%d-%H%M%S")
    shelf = run_dir / "verify" / "rejected-assets" / stamp
    notes: dict[str, list[str]] = {}
    for entry in entries:
        ref = entry["path"]
        notes.setdefault(ref, []).extend(str(n) for n in entry.get("notes") or [])
        source = run_dir / "lesson" / ref
        # 배치가 `.webp` 로 바꿨을 수 있다. 같은 이름 줄기를 전부 치운다.
        for candidate in {source, source.with_suffix(".png"), source.with_suffix(".webp")}:
            if candidate.exists():
                destination = shelf / candidate.relative_to(run_dir / "lesson")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(candidate), str(destination))
                print(f"다시 굽는다: {ref} (원본은 {destination.relative_to(run_dir).as_posix()})")
    write_pipeline_log(run_dir, "asset_rerender_requested", {"paths": sorted(notes)})
    return notes


def resolve_run(args: argparse.Namespace) -> tuple[Path, Path | None]:
    source = args.source.resolve()
    if source.is_file():
        run_id = args.run_id or f"{datetime.now(KST).date().isoformat()}_{slugify(source.stem)}"
        return (args.runs_dir / run_id).resolve(), source
    if source.is_dir():
        return source, None
    raise ValueError(f"디렉토리도 파일도 아니다: {source}")


def stage_storyboard(storyboard: Path, run_dir: Path) -> Path:
    destination = run_dir / f"storyboard{storyboard.suffix.lower()}"
    if destination.resolve() != storyboard.resolve():
        shutil.copyfile(storyboard, destination)
    return destination


def select_stages(start_at: str, through: str) -> list[ProductionStage]:
    start_index = next(index for index, stage in enumerate(STAGES) if stage.name == start_at)
    end_by_through = {
        "planning": "senior_planner",
        "interview": "senior_designer",
        "design": "visual_design",
        "develop": "senior_developer",
        "render": "asset_render",
        "all": "asset_render",
    }
    end_name = end_by_through[through]
    end_index = next(index for index, stage in enumerate(STAGES) if stage.name == end_name)
    if start_index > end_index:
        raise ValueError(f"start-at {start_at} is after through {through}")
    return STAGES[start_index : end_index + 1]


def build_pipeline_dag() -> PipelineDag:
    """실행 순서가 아니라 데이터 의존 관계를 선언한다.

    `senior_developer`와 `asset_render`는 둘 다 visual_design만 기다리므로 서로 독립이다.
    이 관계가 DAG이며, 캐시는 이 그래프를 따라 상위 변경을 하위 fingerprint에 전파한다.
    """
    upstream = {
        "senior_planner": (),
        "senior_designer": ("senior_planner",),
        "interview_brief": ("senior_planner", "senior_designer"),
        "lesson_spec": ("interview_brief",),
        "visual_design": ("lesson_spec", "senior_designer"),
        "senior_developer": ("lesson_spec", "visual_design"),
        "asset_render": ("visual_design",),
    }
    nodes = []
    for stage in STAGES:
        outputs = (stage.report_name, *stage.expected_files)
        if stage.name == "asset_render":
            outputs = (*outputs, "lesson/assets")
        inputs = (*stage.depends_on, *stage.depends_any)
        if stage.name == "senior_planner":
            inputs = ("storyboard.pdf", "storyboard.md")
        nodes.append(DagNode(stage.name, upstream[stage.name], tuple(inputs), tuple(outputs)))
    return PipelineDag(nodes)


def stage_fingerprint(cache: StageCache, stage: ProductionStage, args: argparse.Namespace) -> str:
    prompt_hash = hashlib.sha256(stage.prompt_path.read_bytes()).hexdigest()
    extra = {
        "prompt_hash": prompt_hash,
        "provider": provider_for(stage, args),
        "model": args.model or "default",
        "interview_notes": read_optional(args.interview_notes),
        "screen_report": read_optional(args.screen_report),
        "style_anchor": getattr(args, "style_anchor", None),
    }
    return cache.fingerprint(stage.name, extra)


def print_dag(dag: PipelineDag) -> None:
    print("파이프라인 DAG")
    for name in dag.topological_order():
        parents = dag.nodes[name].upstream
        print(f"  {name} <- {', '.join(parents) if parents else '(root)'}")


def validate_spec_file(run_dir: Path) -> None:
    path = run_dir / "spec" / "lesson-spec.json"
    if not path.exists():
        raise FileNotFoundError(f"lesson_spec가 단일 명세를 만들지 않았다: {path}")
    spec = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_lesson_spec(spec, PROJECT_DIR / "schemas" / "lesson_spec.schema.json")
    if errors:
        raise RuntimeError("lesson-spec 검증 실패: " + "; ".join(errors[:8]))


def pair_developer_and_assets(
    selected: list[ProductionStage],
    run_dir: Path,
    args: argparse.Namespace,
) -> tuple[ProductionStage, ProductionStage] | None:
    """`senior_developer` 와 `asset_render` 를 겹쳐 돌려도 되는지 판정한다.

    겹치는 조건은 셋이다. 하나라도 빠지면 예전처럼 줄을 세운다 — 병렬은 빨라지자고 넣은 것이지
    새 실패 모드를 만들자고 넣은 것이 아니다.

    · 두 단계가 **나란히** 선택됐다(`--through render` 이상).
    · `design/asset-plan.json` 이 있다. 없으면 그림 단계가 `lesson.json` 을 기다려야 한다.
    · 그림 단계를 건너뛰지 않는다(`asset_render.json` 이 이미 있고 `--overwrite` 가 아니면 건너뛴다).
    """
    names = [stage.name for stage in selected]
    try:
        at = names.index("senior_developer")
    except ValueError:
        return None
    if at + 1 >= len(names) or names[at + 1] != "asset_render":
        return None
    if not (run_dir / "design" / "asset-plan.json").exists():
        print("design/asset-plan.json 이 없다 — 그림 단계를 개발 뒤에 줄 세운다(옛 방식)")
        return None
    if (run_dir / "asset_render.json").exists() and not args.overwrite:
        return None
    return (selected[at], selected[at + 1])


def run_developer_and_assets_together(
    pair: tuple[ProductionStage, ProductionStage],
    run_dir: Path,
    storyboard_path: Path | None,
    args: argparse.Namespace,
    registry: dict[str, list[str]] | None,
) -> None:
    """개발과 그림을 동시에 돌린다.

    실측(2026-09) — `senior_developer` 18~36분, `asset_render` 4~37분. 둘은 서로의 산출물을
    읽지 않으므로 줄 세울 이유가 없었다. 그림이 보는 것은 `visual_design` 이 낸 목록이고,
    개발이 하는 일은 그 목록을 `lesson.json` 으로 옮겨 적는 것이다.

    **둘 다 실패할 수 있으므로 예외를 삼키지 않는다.** 한쪽이 죽으면 그 예외를 그대로 올리되,
    다른 쪽은 끝까지 기다린다 — 그림 굽기를 중간에 끊으면 반쯤 구운 파일이 남는다.
    """
    developer, assets = pair
    ensure_dependencies(run_dir, developer)
    ensure_dependencies(run_dir, assets)
    print(f"{developer.name} 와 {assets.name} 를 동시에 돌린다 (그림 목록은 design/asset-plan.json)")

    errors: dict[str, BaseException] = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(
                run_stage_with_feedback, developer, run_dir, storyboard_path, args, registry, True
            ): developer,
            pool.submit(run_asset_render, assets, run_dir, args, True): assets,
        }
        for future in as_completed(futures):
            stage = futures[future]
            try:
                future.result()
            except BaseException as error:  # noqa: BLE001 — 그대로 올리되 상대는 기다린다
                errors[stage.name] = error
            else:
                write_pipeline_log(
                    run_dir, "stage_done", {"stage": stage.name, "report": stage.report_name}
                )

    for stage_name, error in errors.items():
        write_pipeline_log(
            run_dir, "stage_rejected", {"stage": stage_name, "reason": f"{type(error).__name__}: {error}"[:200]}
        )
    if errors:
        first = next(iter(errors.values()))
        raise first

    report_asset_plan_drift(run_dir)


def report_asset_plan_drift(run_dir: Path) -> None:
    """계획대로 구웠는데 `lesson.json` 이 다른 이름을 가리키면 알린다.

    동시에 돌리면 생기는 **유일한 새 위험**이 이것이다 — 그림은 `asset-plan.json` 을 보고
    굽는데 개발자가 경로를 바꿔 적으면 구운 그림이 고아가 되고 화면은 빈다. 계약서가
    `targetAsset` 을 한 글자도 바꾸지 말라고 못박고 있으므로 정상이면 0건이다.
    막지는 않는다 — 배치 단계가 어차피 다시 본다. 여기서는 **조용히 지나가지만 않게** 한다.
    """
    lesson_path = run_dir / "lesson" / "lesson.json"
    plan_path = run_dir / "design" / "asset-plan.json"
    if not lesson_path.exists() or not plan_path.exists():
        return
    try:
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    planned = {
        entry.get("path")
        for entry in (plan.get("assets") or [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    used: set[str] = set()
    collect_asset_refs(lesson, used)
    used = {ref for ref in used if not ref.startswith(("assets/photos/", "assets/audio/"))}

    orphaned = sorted(planned - used)
    unplanned = sorted(used - planned)
    if not orphaned and not unplanned:
        return
    print("\n계획과 lesson.json 의 그림 목록이 어긋난다 — 동시 실행에서 이 어긋남이 빈 화면이 된다")
    for ref in orphaned[:8]:
        print(f"  · 구웠는데 아무도 안 쓴다: {ref}")
    for ref in unplanned[:8]:
        print(f"  · lesson.json 이 쓰는데 계획에 없다(안 구워졌다): {ref}")
    if len(orphaned) + len(unplanned) > 16:
        print(f"  … 모두 {len(orphaned) + len(unplanned)}건")


def ensure_dependencies(run_dir: Path, stage: ProductionStage) -> None:
    missing = [rel for rel in stage.depends_on if not (run_dir / rel).exists()]
    if missing:
        raise FileNotFoundError(f"{stage.name}에 필요한 파일이 없다: {missing}")
    if stage.depends_any and not any((run_dir / rel).exists() for rel in stage.depends_any):
        raise FileNotFoundError(
            f"{stage.name}에 필요한 파일이 하나도 없다(하나면 된다): {list(stage.depends_any)}"
        )


def run_stage_with_feedback(
    stage: ProductionStage,
    run_dir: Path,
    storyboard_path: Path | None,
    args: argparse.Namespace,
    registry: dict[str, list[str]] | None,
    force: bool = False,
) -> None:
    """검사에 걸린 것을 프롬프트에 되먹여 다시 부른다. **게이트가 있는 단계에만** 돈다.

    `senior_developer` 가 그렇다 — `check_lesson_standalone` 위반 목록을 되먹인다.
    그림 단계는 배치 병렬이라 전용 드라이버(`run_asset_render`)가 따로 되먹인다.
    앞 단계들은 서류(md)를 내고 판정 기준이 schema 뿐이라 되먹일 것이 없다. 걸린 것을
    **그대로** 넣어야 모델이 그 자리를 고친다. 요약해서 주면 다른 곳을 고친다.

    gyo6_content 의 `agent/lessonJsonGenerator.mjs` 가 실측으로 얻은 장치이고, 실제로
    2026-09-10 재생성이 **3번째 시도에서** 통과했다 — 되먹임이 없었으면 실패로 끝날 run 이었다.

    실패한 `lesson.json` 은 `.rejected` 로 옮기고 지운다. 남기면 다음 실행이 "이미 있음" 으로
    건너뛰어 깨진 산출물이 조용히 최종본이 된다.
    """
    lesson_path = run_dir / "lesson" / "lesson.json"
    report_path = run_dir / stage.report_name
    feedback = ""
    # `lesson.json` 은 개발 단계의 산출물이다. 그림 단계에서 그것을 치우면 이미 통과한
    # 데이터를 이유 없이 날린다.
    owns_lesson = stage.artifact == "lesson_draft_output"

    def reject_if_owned() -> None:
        if owns_lesson:
            reject_lesson(lesson_path, attempt < args.max_retries)

    for attempt in range(args.max_retries + 1):
        if attempt:
            print(f"{stage.name} 되먹임 재시도 {attempt}/{args.max_retries}")
        try:
            run_stage(stage, run_dir, storyboard_path, args, feedback=feedback, force=force or bool(attempt))
        except Exception as exc:  # schema 실패·파일 누락·타임아웃도 되먹임 대상이다
            feedback = f"{type(exc).__name__}: {exc}"
            print(f"  실행 실패: {feedback}")
            write_pipeline_log(
                run_dir,
                "stage_rejected",
                {"stage": stage.name, "attempt": attempt + 1, "reason": feedback[:200]},
            )
            reject_if_owned()
            continue

        if not report_path.exists() or not lesson_path.exists():
            feedback = f"보고서나 lesson.json 이 없다: {report_path.name} / {lesson_path}"
            print(f"  {feedback}")
            write_pipeline_log(
                run_dir,
                "stage_rejected",
                {"stage": stage.name, "attempt": attempt + 1, "reason": feedback[:200]},
            )
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            feedback = f"JSON 파싱 실패: {exc}"
            print(f"  {feedback}")
            write_pipeline_log(
                run_dir,
                "stage_rejected",
                {"stage": stage.name, "attempt": attempt + 1, "reason": feedback[:200]},
            )
            reject_if_owned()
            continue

        violations = check_lesson_standalone(lesson, report, run_dir, registry)
        if not errors_only(violations):
            return
        feedback = format_violations(violations)
        print(f"  검증 실패 {len(errors_only(violations))}건")
        for item in errors_only(violations)[:5]:
            print(f"    · [{item['kind']}] {item['where']} — {item['detail'][:100]}")
        write_pipeline_log(
            run_dir,
            "stage_rejected",
            {"stage": stage.name, "attempt": attempt + 1, "violations": len(errors_only(violations))},
        )
        reject_if_owned()

    # 마지막 시도의 산출물은 남긴다. 무엇이 걸렸는지 사람이 봐야 하고,
    # 최종 판정은 `check_outputs` 가 한 번 더 돌려 보고한다.
    print(f"{args.max_retries + 1}회 시도했지만 위반이 남았다.")


def reject_lesson(lesson_path: Path, remove: bool) -> None:
    """깨진 산출물을 옆으로 치운다. `remove` 가 False 면(마지막 시도) 사본만 남긴다."""
    if not lesson_path.exists():
        return
    try:
        shutil.copyfile(lesson_path, lesson_path.with_suffix(".json.rejected"))
        if remove:
            lesson_path.unlink()
    except OSError:
        pass


def asset_jobs(run_dir: Path) -> list[dict]:
    """`lesson.json` 이 가리키는 그림 하나하나에 **그릴 근거**를 붙여 목록으로 만든다.

    근거는 둘이다 — 그 그림을 겨냥한 `assetPrompt`(mustInclude·reservedUiZones·forbidden)와
    화면 어디에 쓰이는지. 둘 다 없으면 그쪽 생성기가 파일 이름으로 지어내는 것과 다를 바 없다.

    **`lesson.json` 이 아직 없으면 `design/asset-plan.json` 으로 돈다.** 그 목록과 지시는
    `visual_design` 이 낸 것이고 개발 단계는 그것을 `assetPrompt` 로 옮겨 적을 뿐이라,
    그림을 굽는 데 필요한 것은 그 시점에 이미 다 정해져 있다. 이 갈래가 있어야 그림 단계가
    개발과 동시에 돈다. 개발이 끝난 뒤(재실행·옛 run)에는 `lesson.json` 이 이긴다 —
    그쪽이 실제로 화면이 참조하는 최종 목록이기 때문이다.
    """
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not lesson_path.exists():
        return asset_jobs_from_plan(run_dir)
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))

    prompts_by_target: dict[str, dict] = {}
    usage: dict[str, list[str]] = {}
    for index, step in enumerate(lesson.get("steps") or []):
        if not isinstance(step, dict):
            continue
        for _key, asset_prompt in iter_asset_prompts(step):
            target = asset_prompt.get("targetAsset")
            if isinstance(target, str):
                prompts_by_target[target] = asset_prompt
        label = f"steps[{index}] {step.get('type', '')} {step.get('title', '')}".strip()
        step_refs: set[str] = set()
        collect_asset_refs(step, step_refs)
        for ref in step_refs:
            usage.setdefault(ref, []).append(label)
    for key, member in (lesson.get("cast") or {}).items():
        if not isinstance(member, dict):
            continue
        member_refs: set[str] = set()
        collect_asset_refs(member, member_refs)
        for ref in member_refs:
            usage.setdefault(ref, []).append(f"cast.{key} ({member.get('name', '')})")

    refs: set[str] = set()
    collect_asset_refs(lesson, refs)
    jobs = []
    for ref in sorted(refs):
        if ref.startswith("assets/photos/") or ref.startswith("assets/audio/"):
            continue
        jobs.append(
            {
                "path": ref,
                "role": asset_role(ref),
                "family": asset_family(ref),
                "assetPrompt": prompts_by_target.get(ref),
                "usedIn": sorted(set(usage.get(ref, [])))[:4],
            }
        )
    return jobs


def asset_jobs_from_plan(run_dir: Path) -> list[dict]:
    """`design/asset-plan.json` 으로 그릴 목록을 만든다. `lesson.json` 이 아직 없을 때 쓴다.

    사이드카는 `visual_design` 이 `asset-plan.md` 와 **같은 목록**을 줄임 없이 펼쳐 낸 것이다.
    md 를 파싱하지 않는 이유는 그쪽이 `(공통 5)` 처럼 줄여 적는 사람용 문서이기 때문이다 —
    줄임말을 코드가 펼치려 들면 규칙이 바뀔 때마다 조용히 어긋난다.
    """
    plan_path = run_dir / "design" / "asset-plan.json"
    if not plan_path.exists():
        return []
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"asset-plan.json 을 읽지 못했다({error}). lesson.json 을 기다린다")
        return []

    jobs = []
    for entry in plan.get("assets") or []:
        if not isinstance(entry, dict):
            continue
        ref = entry.get("path")
        if not isinstance(ref, str) or not ref.startswith("assets/"):
            continue
        if ref.startswith("assets/photos/") or ref.startswith("assets/audio/"):
            continue
        # `assetPrompt` 와 같은 모양으로 맞춘다 — 뒤의 배치·프롬프트 조립이 그 모양을 읽는다.
        asset_prompt = {
            "sceneType": entry.get("sceneType", ""),
            "targetAsset": ref,
            "mustInclude": entry.get("mustInclude") or [],
            "reservedUiZones": entry.get("reservedUiZones") or [],
            "forbidden": entry.get("forbidden") or [],
        }
        if entry.get("size"):
            asset_prompt["size"] = entry["size"]
        if entry.get("transparent") is not None:
            asset_prompt["transparent"] = entry["transparent"]
        # 인물 프레이밍은 **굽는 쪽까지 닿아야** 한다. 계획에만 있으면 그림은 안 바뀐다.
        for key in ("framing", "headRatio"):
            if entry.get(key) is not None:
                asset_prompt[key] = entry[key]
        jobs.append(
            {
                "path": ref,
                "role": asset_role(ref),
                "family": asset_family(ref),
                "assetPrompt": asset_prompt,
                "usedIn": [u for u in (entry.get("usedIn") or []) if isinstance(u, str)][:4],
            }
        )
    jobs.sort(key=lambda job: job["path"])
    if jobs:
        print(f"그릴 목록을 design/asset-plan.json 에서 읽었다 — {len(jobs)}장 (개발과 동시에 돈다)")
    return jobs


def asset_role(ref: str) -> str:
    if ref.startswith("assets/backgrounds/"):
        return "background"
    if ref.startswith("assets/character/") or ref.startswith("assets/customers/"):
        return "character"
    return "ui"


def asset_family(ref: str) -> str:
    """같은 배치에 **함께 들어가야 하는** 묶음의 이름.

    한 인물의 감정 그림들이 그렇다. `child-idle` 과 `child-happy` 가 다른 호출로 갈라지면
    두 호출이 서로를 못 보므로 **다른 사람이 된다.** 그래서 인물은 이름으로 묶는다.
    나머지는 각자 하나의 묶음이다.
    """
    if ref.startswith("assets/character/") or ref.startswith("assets/customers/"):
        stem = Path(ref).stem
        return f"character:{stem.split('-')[0]}"
    return f"single:{ref}"


def pack_batches(jobs: list[dict], batch_size: int) -> list[list[dict]]:
    """묶음을 쪼개지 않으면서 배치에 채운다.

    두 가지를 지킨다.

    · **한 인물이 두 호출로 갈라지지 않는다.** 갈라지면 두 호출이 서로를 못 봐서 다른 사람이 된다.
    · **같은 역할끼리 한 배치에 담는다.** 배경 12장이 흩어지면 호출마다 조명과 원근이 달라진다.
      한 호출 안에 있으면 앞서 그린 것을 보고 맞출 수 있다.

    역할이 다른 것을 섞지 않으므로 배치 수가 조금 늘 수 있다. 화풍 일관성이 더 비싸다.
    """
    families: dict[str, list[dict]] = {}
    for job in jobs:
        families.setdefault(job["family"], []).append(job)

    role_order = {"background": 0, "character": 1, "ui": 2}
    ordered = sorted(
        families.values(),
        key=lambda group: (role_order.get(group[0]["role"], 9), -len(group), group[0]["path"]),
    )

    batches: list[list[dict]] = []
    for group in ordered:
        role = group[0]["role"]
        placed = False
        for batch in batches:
            if batch[0]["role"] != role:
                continue
            if len(batch) + len(group) <= max(batch_size, len(group)):
                batch.extend(group)
                placed = True
                break
        if not placed:
            batches.append(list(group))
    return batches


def provider_for(stage: ProductionStage, args: argparse.Namespace) -> str:
    """이 단계를 어느 쪽으로 부를지. 그림 단계만 예외다.

    이미지 생성 도구가 codex 쪽에만 있어서, 사용자가 `--provider claude` 를 줘도 그림 단계는
    codex 로 돌린다. 안 그러면 그릴 수단 없이 "파일을 만들지 못했다" 로 세 번 재시도하고 끝난다.
    """
    if stage.name == "asset_render":
        return IMAGE_CAPABLE_PROVIDER
    return args.provider


def run_asset_render(
    stage: ProductionStage,
    run_dir: Path,
    args: argparse.Namespace,
    force: bool = False,
) -> None:
    """그림을 굽는다. **화풍 기준 그림을 먼저 만들고 나머지가 그것을 보고 맞춘다.**

    배치는 각각 독립된 호출이라 서로를 못 본다. 그래서 `artDirection` 텍스트만 주면 같은 글을
    호출마다 다르게 해석한다 — 실측(2026-09-10)으로 같은 지시에서 배경은 사진 같은 3D 로,
    봉투는 납작한 빗금으로 나왔다. **글로는 화풍을 못 묶는다. 그림을 보여줘야 한다.**

    그래서 순서를 둔다.

        1) 전체 기준 한 장을 혼자 굽는다(배경 우선). 이것이 이 차시의 화풍이다.
        2) 역할(배경·인물·UI)마다 첫 배치를 혼자 굽는다. 그 역할의 기준이 된다.
        3) 남은 배치는 병렬로 굽되, 위 두 기준 파일을 **실제로 열어** 맞춘다.

    병렬은 3)에만 있다. 기준을 만드는 동안은 줄을 세운다 — 기준이 흔들리면 뒤가 전부 흔들린다.

    **인물은 쪼개지 않는다.** 한 인물의 감정 그림이 다른 호출로 갈라지면 다른 사람이 된다.
    `pack_batches` 가 묶어서 담는다.

    되먹임은 전체 단위로 돈다 — 한 바퀴 돌고 아직 파일이 없는 것만 다시 담는다.
    """
    report_path = run_dir / stage.report_name
    if report_path.exists() and not args.overwrite and not force:
        print(f"{stage.name} 건너뜀: {report_path}")
        return

    jobs = asset_jobs(run_dir)
    if not jobs:
        print(f"{stage.name}: 그릴 그림이 없다")
        return
    # 화면 검증에서 되돌아온 그림은 **왜 되돌아왔는지**를 그 그림의 일감에 붙인다.
    revision = getattr(args, "rerender_notes", None) or {}
    for job in jobs:
        if job["path"] in revision:
            job["revisionNotes"] = revision[job["path"]]

    rendered: list[dict] = []
    skipped: list[dict] = []
    notes: list[str] = []

    def absorb(report: dict) -> int:
        rendered.extend(item for item in report.get("rendered") or [] if isinstance(item, dict))
        skipped.extend(item for item in report.get("skipped") or [] if isinstance(item, dict))
        notes.extend(item for item in report.get("notes") or [] if isinstance(item, str))
        return len(report.get("rendered") or [])

    for attempt in range(args.max_retries + 1):
        # 없는 그림만 다시 굽는 것이 아니다. **투명으로 지시했는데 알파가 없는 그림**도
        # 다시 굽는다 — 파일은 있으니 예전에는 "끝났다" 로 셌고, 화면에서 회색 판이 됐다
        # (실측 2026-09-23, 4-1/03 인물 6장).
        opaque = opaque_transparent_assets(run_dir, jobs)
        if opaque and attempt:
            print(f"  알파가 없어 다시 굽는다: {len(opaque)}장")
        pending_paths = set(rendered_asset_gaps(run_dir)) | set(opaque)
        if not pending_paths:
            break
        pending = [job for job in jobs if job["path"] in pending_paths]
        label = "재시도 " if attempt else ""
        print(f"\n{stage.name} {label}{attempt + 1}/{args.max_retries + 1} — 남은 그림 {len(pending)}장")

        # 1) 전체 기준. 배경이 재질·광원·시점을 가장 많이 보여주므로 배경을 먼저 고른다.
        #
        # 다만 **사람이 고를 수 있어야 한다.** 자동 선택은 "이미 구워진 것 중 첫 장"이라
        # 원하는 화풍이 아닐 수 있다 — 실측(2026-09-11) 우편물 12장이 그렇게 나와
        # "너무 그래픽적"이라는 지적을 받았다. 사람이 원한 기준은 회화적인 `bin-wood.png` 였다.
        pinned = getattr(args, "style_anchor", None)
        # `new` 는 **기존 그림을 기준으로 삼지 않는다.** 목표 화풍이 이 차시에 아직 없을 때 쓴다 —
        # 실측(2026-09-11): 평면적인 `bin-wood.png` 를 기준으로 지정해 놓고 "실사·입체로"를
        # 요구했더니 당연히 평면적인 결과가 나왔다. 기준 지정은 있는 것 중 고르는 통로일 뿐,
        # 없는 화풍을 만들지는 못한다. 이 값이면 이번 배치에서 기준 한 장을 새로 굽는다.
        fresh = pinned == "new"
        if pinned and not fresh and not (run_dir / "lesson" / pinned).exists():
            raise FileNotFoundError(f"--style-anchor 가 가리키는 그림이 없다: {pinned}")
        anchor = None if fresh else (pinned or style_anchor(run_dir, jobs))
        if pinned and not fresh:
            print(f"  화풍 기준(지정): {pinned}")
        if fresh:
            print("  화풍 기준을 이 배치에서 새로 만든다 (--style-anchor new)")
        if anchor is None:
            seed = pending[0] if fresh else next(
                (job for job in pending if job["role"] == "background"), pending[0]
            )
            print(f"  화풍 기준을 먼저 굽는다: {seed['path']}")
            try:
                absorb(render_batch(stage, run_dir, [seed], 0, args, anchors=[]))
            except Exception as exc:
                print(f"  화풍 기준 실패: {type(exc).__name__}: {exc}")
            anchor = style_anchor(run_dir, jobs)
            pending = [job for job in pending if job["path"] != seed["path"]]

        anchors = [anchor] if anchor else []

        # 2)·3) 역할별로 — 첫 배치는 혼자(그 역할의 기준), 나머지는 병렬.
        for role in ("background", "character", "ui"):
            role_jobs = [job for job in pending if job["role"] == role]
            if not role_jobs:
                continue
            batches = pack_batches(role_jobs, args.asset_batch_size)
            print(f"\n  [{role}] {len(role_jobs)}장 → 배치 {len(batches)}개")

            role_anchor = role_reference(run_dir, jobs, role, anchor)
            head: list[list[dict]] = []
            tail = batches
            # 기준을 사람이 지정했으면 **만들 것이 없다.** 그 그림은 이미 있으므로
            # 기준 배치를 혼자 굽는 직렬 단계를 건너뛰고 곧바로 병렬로 간다.
            # `new` 일 때 역할 기준을 **기존 그림에서 집으면 안 된다.** 그것이 바로 우리가
            # 벗어나려는 화풍이다 — 실측(2026-09-11): 새로 구운 실사 기준과 함께 이미 있던
            # 일러스트 UI 그림이 두 번째 기준으로 실려, 배치들이 일러스트 쪽을 따랐다.
            # 기준은 방금 구운 씨앗 하나뿐이어야 한다.
            if pinned:
                role_anchor = None
            elif role_anchor is None and batches:
                head, tail = [batches[0]], batches[1:]

            for batch in head:
                print(f"    기준 배치 {len(batch)}장 (혼자 굽는다) — "
                      f"{', '.join(Path(j['path']).name for j in batch)}")
                try:
                    absorb(render_batch(stage, run_dir, batch, 1, args, anchors=anchors))
                except Exception as exc:
                    print(f"    기준 배치 실패: {type(exc).__name__}: {exc}")
                role_anchor = role_reference(run_dir, jobs, role, anchor)

            if not tail:
                continue
            batch_anchors = [a for a in (anchor, role_anchor) if a]
            with ThreadPoolExecutor(max_workers=max(1, args.asset_parallel)) as pool:
                futures = {
                    pool.submit(render_batch, stage, run_dir, batch, index, args, batch_anchors): index
                    for index, batch in enumerate(tail, start=2)
                }
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        report = future.result()
                    except Exception as exc:
                        print(f"    배치 {index} 실패: {type(exc).__name__}: {exc}")
                        write_pipeline_log(
                            run_dir, "asset_batch_failed", {"batch": index, "error": str(exc)[:200]}
                        )
                        continue
                    print(f"    배치 {index} 완료 — {absorb(report)}장 보고")

    # 보고서는 **실제로 파일이 있는 것** 기준으로 정리한다. 저장했다고 보고했는데 파일이 없는
    # 경우가 있고, 그때 보고서를 믿으면 manifest 가 거짓말을 한다.
    lesson_dir = run_dir / "lesson"
    seen: set[str] = set()
    confirmed = []
    for item in rendered:
        path = str(item.get("path") or "")
        if path and path not in seen and (lesson_dir / path).exists():
            seen.add(path)
            confirmed.append(item)
    gaps = rendered_asset_gaps(run_dir)
    for ref in gaps:
        skipped.append({"path": ref, "why": "여러 번 시도했지만 파일이 생기지 않았다"})
    still_opaque = opaque_transparent_assets(run_dir, jobs)
    for ref in still_opaque:
        skipped.append({"path": ref, "why": "투명으로 지시했는데 알파가 없다 — 화면에서 사각형 판이 된다"})
        write_pipeline_log(run_dir, "asset_opaque", {"path": ref})
    if still_opaque:
        print(f"\n투명 지시를 못 지킨 그림 {len(still_opaque)}장 — 사람이 봐야 한다")
        for ref in still_opaque:
            print(f"  · {ref}")

    report_path.write_text(
        json.dumps({"rendered": confirmed, "skipped": skipped, "notes": notes},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n{stage.name}: {len(confirmed)}장 확인됨 · 남은 것 {len(gaps)}장")


def style_anchor(run_dir: Path, jobs: list[dict]) -> str | None:
    """이 차시의 화풍 기준 그림. 이미 구워진 배경 중 첫 장을 쓴다."""
    lesson_dir = run_dir / "lesson"
    for role in ("background", "ui", "character"):
        for job in jobs:
            if job["role"] == role and (lesson_dir / job["path"]).exists():
                return job["path"]
    return None


def role_reference(run_dir: Path, jobs: list[dict], role: str, exclude: str | None) -> str | None:
    """그 역할에서 이미 구워진 그림 하나. 같은 역할끼리 맞출 기준이다."""
    lesson_dir = run_dir / "lesson"
    for job in jobs:
        if job["role"] != role or job["path"] == exclude:
            continue
        if (lesson_dir / job["path"]).exists():
            return job["path"]
    return None


def render_batch(
    stage: ProductionStage,
    run_dir: Path,
    batch: list[dict],
    index: int,
    args: argparse.Namespace,
    anchors: list[str] | None = None,
) -> dict:
    """배치 하나를 굽는다. 스레드에서 돌므로 **자기 임시 파일만** 만진다."""
    prompt = build_asset_batch_prompt(stage, run_dir, batch, anchors or [])
    client = create_prompt_client(
        provider=IMAGE_CAPABLE_PROVIDER,
        codex_bin=args.codex_bin,
        claude_bin=args.claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=args.timeout_seconds,
    )
    with tempfile.TemporaryDirectory(prefix=f"content-asset-{index}-") as temp_dir:
        temp_output = Path(temp_dir) / "batch-output.json"
        client.run_prompt(
            prompt=prompt,
            output_schema=ARTIFACT_SCHEMAS[stage.artifact],
            output_path=temp_output,
            model=args.model,
            stage=f"{stage.name}#{index}",
        )
        result = validate_file(temp_output, artifact=stage.artifact)
        if result["status"] != "PASS":
            raise RuntimeError(f"schema 실패: {result['errors'][:3]}")
        report = json.loads(temp_output.read_text(encoding="utf-8"))

    # **배경 제거는 코드가 한다.** 모델은 작품에 없는 색으로 배경을 칠하기만 하고,
    # 지우는 것은 여기서 한다. 모델이 스스로 키잉하면 작품 안의 색까지 지운다
    # (실측 2026-09-10 — 캐릭터 청바지에 구멍이 뚫렸다).
    lesson_dir = run_dir / "lesson"
    for item in report.get("rendered") or []:
        if not isinstance(item, dict):
            continue
        chroma = str(item.get("chroma") or "none")
        target = lesson_dir / str(item.get("path") or "")
        if chroma == "none" or not target.exists():
            continue
        outcome = chroma_key(target, chroma)
        if outcome.get("keyed"):
            print(f"    크로마 제거 {target.name} ({chroma}, {outcome['removed_ratio'] * 100:.0f}%)")
    report["opaque"] = opaque_transparent_assets(run_dir, batch)
    for path in report["opaque"]:
        print(f"    투명으로 지시했는데 알파가 없다: {path}")
    return report


def build_asset_batch_prompt(
    stage: ProductionStage, run_dir: Path, batch: list[dict], anchors: list[str]
) -> str:
    """이 배치가 그릴 것만 싣는다. 화풍은 **먼저 구워진 기준 그림**이 소유한다."""
    # 계획한 규격과 **같은 문서**를 굽는 쪽도 받는다. 투명·전신 비례가 여기서 깨지면
    # 계획이 아무리 옳아도 화면이 틀린다.
    guide = with_asset_spec(stage.prompt_path.read_text(encoding="utf-8"))
    # 개발과 **동시에** 돌 때는 `lesson.json` 이 아직 없다. 그때 화풍 지시는 서류에서 온다.
    lesson_json = run_dir / "lesson" / "lesson.json"
    lesson = json.loads(lesson_json.read_text(encoding="utf-8")) if lesson_json.exists() else {}
    lesson_dir = (run_dir / "lesson").resolve()
    anchor_lines = []
    if anchors:
        anchor_lines.append("STYLE_ANCHOR — 이 차시에서 **이미 구워진** 그림입니다:")
        for path in anchors:
            anchor_lines.append(f"  {lesson_dir / path}")
        anchor_lines.append("")
        anchor_lines.append(
            "**그리기 전에 이 파일을 실제로 여십시오.** 설명문을 읽고 짐작하지 않습니다. "
            "매체(붓·질감), 명암의 세기, 광원 방향, 가장자리 처리, 채도, 디테일 밀도를 "
            "그 그림에 맞춥니다. 이 배치의 그림이 그 옆에 놓였을 때 같은 사람이 같은 날 "
            "그린 것처럼 보여야 합니다."
        )
        anchor_lines.append(
            "기준 그림과 **주제**를 맞추라는 뜻이 아닙니다. 소재는 각자 다르고, 맞출 것은 화풍입니다."
        )
    else:
        anchor_lines.append(
            "STYLE_ANCHOR: 없음. 이 배치가 **이 차시의 첫 그림**입니다. "
            "여기서 정해지는 화풍을 이후 모든 그림이 따라오므로, artDirection 을 가장 충실하게 그립니다."
        )
    anchor_text = "\n".join(anchor_lines)


    art_direction = json.dumps(lesson.get("artDirection") or {}, ensure_ascii=False, indent=2)

    # 차시 `artDirection` 은 **모든 그림을 이긴다** — 계약이 그렇게 못박고 있다
    # (`consistencyRule`: 개별 assetPrompt 의 표현 어휘는 형태 요구로만 읽는다).
    # 그래서 특정 그림만 다른 화풍으로 뽑으려면 **예외를 명시적으로 선언해야** 한다.
    # 실측(2026-09-11): 우편물 12장에 "실사·입체·래스터"를 적어 넣었는데 계속 일러스트가
    # 나왔다. 모델이 틀린 것이 아니라 계약대로 artDirection 을 따른 것이었다.
    overrides: dict[str, str] = {}
    for step in lesson.get("steps") or []:
        if not isinstance(step, dict):
            continue
        for _key, prompt_spec in iter_asset_prompts(step):
            target = prompt_spec.get("targetAsset")
            note = prompt_spec.get("artDirectionOverride")
            if isinstance(target, str) and isinstance(note, str) and note.strip():
                overrides[target] = note.strip()
    batch_overrides = {job["path"]: overrides[job["path"]] for job in batch if job["path"] in overrides}
    override_text = ""
    if batch_overrides:
        lines = [
            "ART_DIRECTION_OVERRIDE — **이 그림들만은 위 ART_DIRECTION 을 따르지 않습니다.**",
            "아래에 적힌 화풍이 우선입니다. 형태·구성 요구는 그대로 지키되, 질감·명암·입체·매체감은",
            "이쪽을 따릅니다. 여기 없는 그림은 위 ART_DIRECTION 그대로입니다.",
            "",
        ]
        for path, note in batch_overrides.items():
            lines.append(f"  {path}")
            lines.append(f"    {note}")
        override_text = "\n".join(lines) + "\n"

    # 투명 대상은 **이름으로 짚어 준다.** 규칙은 시스템 프롬프트에 이미 있는데, 배치가
    # 한 장뿐일 때(기준 배치) 모델이 스스로 키잉해 어두운 후광을 30% 남긴 일이 두 번 있었다
    # (실측 2026-09-23, child-idle). 목록으로 짚으면 "이 그림이 그 대상이다" 가 분명해진다.
    transparent_paths = [
        job["path"] for job in batch if (job.get("assetPrompt") or {}).get("transparent")
    ]
    chroma_text = ""
    if transparent_paths:
        chroma_text = (
            "CHROMA_REQUIRED — 아래 그림은 **투명 배경**입니다. 배경을 크로마 색으로 평평하게 "
            "칠하고 `chroma` 에 그 색 이름을 적습니다. **`\"none\"` 을 적거나 스스로 지우면 안 됩니다** "
            "— 지우는 것은 코드가 합니다.\n"
            + "".join(f"  {path}\n" for path in transparent_paths)
        )

    revised = [job for job in batch if job.get("revisionNotes")]
    revision_text = ""
    if revised:
        lines = [
            "REVISION — 아래 그림은 **빌드된 화면을 검증하다 되돌아온 것**입니다. 앞서 구운 것이 틀렸습니다.",
            "`revisionNotes` 가 무엇이 틀렸는지입니다. 그 지적을 반드시 고치고, 나머지 요구(mustInclude 등)는 그대로 지킵니다.",
        ]
        for job in revised:
            lines.append(f"  {job['path']}")
            lines.extend(f"    - {note}" for note in job["revisionNotes"])
        revision_text = "\n".join(lines) + "\n"

    jobs_json = json.dumps(batch, ensure_ascii=False, indent=2)
    asset_plan = read_optional(run_dir / "design" / "asset-plan.md")
    visual_design = read_optional(run_dir / "design" / "visual-design.md")
    return f"""{guide}

ART_DIRECTION (이 배치의 모든 그림이 상속합니다):
{art_direction}

{override_text}
{anchor_text}

{chroma_text}
{revision_text}
이번 배치에서 그릴 것 — **이 목록만** 그립니다. 다른 그림은 다른 호출이 맡습니다:
{jobs_json}

저장 위치는 `{(run_dir / "lesson").resolve()}` 아래이며, `path` 를 그대로 이어 붙입니다.
예: `assets/ui/stamp.png` → `{(run_dir / "lesson").resolve()}\\assets\\ui\\stamp.png`

DESIGN_ASSET_PLAN (참고):
{asset_plan[:6000]}

VISUAL_DESIGN (참고):
{visual_design[:4000]}

마지막 응답은 schema 에 맞는 JSON 하나만 출력하고, `rendered` 에는
**이번 배치에서 실제로 저장에 성공한 것만** 넣습니다.
"""


def opaque_transparent_assets(run_dir: Path, jobs: list[dict]) -> list[str]:
    """`transparent: true` 로 지시했는데 알파가 없는 그림.

    파일이 있으면 끝난 것으로 세던 자리다. 그런데 생성기는 "투명 배경" 을 **회색으로 칠해서**
    돌려주는 일이 있다 — 파일은 멀쩡히 있고, 화면에서는 인물 뒤에 사각형 판이 생긴다.
    실측 2026-09-23(4-1/03) — 인물 6장이 전부 그 상태였고 어떤 검사도 못 봤다.

    판정은 `asset_alpha.has_alpha` 가 한다. 모드만 보면 안 된다 — RGBA 로 저장해 놓고
    전 픽셀이 불투명한 경우가 있고, 그건 투명 배경이 아니라 그냥 4채널 파일이다.
    """
    lesson_dir = run_dir / "lesson"
    opaque: list[str] = []
    for job in jobs:
        prompt_spec = job.get("assetPrompt") or {}
        if not prompt_spec.get("transparent"):
            continue
        target = lesson_dir / job["path"]
        if not target.exists():
            continue
        try:
            if not has_alpha(target):
                opaque.append(job["path"])
        except OSError:
            continue
    return opaque


def enforce_asset_plan(
    stage: ProductionStage,
    run_dir: Path,
    storyboard_path: Path | None,
    args: argparse.Namespace,
) -> None:
    """`design/asset-plan.json` 이 그림 규격 계약과 어긋나면 되먹여 다시 부른다.

    이 단계에는 원래 게이트가 없었다. schema 만 보고 넘어가므로 계약서와 **정반대로** 적어도
    통과했다(2026-09-23, 4-1/03 — 인물 6장을 "허리 위까지만" 으로 계획했다). 그림은 계획대로
    구워지므로 여기서 안 막으면 47분을 들여 틀린 그림을 굽는다. 계약서를 프롬프트에 싣는 것이
    1차 방어이고 이것이 2차다.

    **막되 멈추지는 않는다.** 계획은 사람이 열어서 고칠 수 있는 서류이고, 여기서 예외를
    던지면 인터뷰까지 끝낸 run 이 통째로 죽는다. 되먹임을 다 쓰고도 남으면 크게 적어 남긴다.
    """
    violations = check_asset_plan_file(run_dir)
    if not violations:
        return
    for attempt in range(args.max_retries):
        print(f"\n그림 계획이 규격과 어긋난다 — {len(violations)}건")
        for item in violations[:6]:
            print(f"  · [{item['kind']}] {item['where']} — {item['detail'][:110]}")
        write_pipeline_log(
            run_dir,
            "asset_plan_rejected",
            {"attempt": attempt + 1, "violations": [v["kind"] for v in violations]},
        )
        feedback = (
            "`design/asset-plan.json` 과 `design/asset-plan.md` 가 그림 규격 계약과 어긋납니다.\n"
            "**두 파일을 함께 고칩니다** — 사이드카만 고치면 사람이 읽는 문서와 갈립니다.\n\n"
            + format_asset_plan_violations(violations)
        )
        run_stage(stage, run_dir, storyboard_path, args, feedback=feedback, force=True)
        violations = check_asset_plan_file(run_dir)
        if not violations:
            print("그림 계획이 규격에 맞다")
            return
    print(f"\n그림 계획에 규격 위반 {len(violations)}건이 남았다. 이대로 구우면 화면이 틀어진다")
    write_pipeline_log(
        run_dir, "asset_plan_unresolved", {"violations": [v["kind"] for v in violations]}
    )


def rendered_asset_gaps(run_dir: Path) -> list[str]:
    """`lesson.json` 이 가리키는데 파일이 없는 그림. 사람이 넣을 사진·오디오는 뺀다."""
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not lesson_path.exists():
        return []
    try:
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    refs: set[str] = set()
    collect_asset_refs(lesson, refs)
    gaps = []
    for ref in sorted(refs):
        if ref.startswith("assets/photos/") or ref.startswith("assets/audio/"):
            continue
        if not (run_dir / "lesson" / ref).exists():
            gaps.append(ref)
    return gaps


def run_stage(
    stage: ProductionStage,
    run_dir: Path,
    storyboard_path: Path | None,
    args: argparse.Namespace,
    feedback: str = "",
    force: bool = False,
) -> None:
    report_path = run_dir / stage.report_name
    if report_path.exists() and not args.overwrite and not force:
        print(f"{stage.name} 건너뜀: {report_path}")
        return

    prompt = build_prompt(stage, run_dir, storyboard_path, args, feedback=feedback)
    provider = provider_for(stage, args)
    client = create_prompt_client(
        provider=provider,
        codex_bin=args.codex_bin,
        claude_bin=args.claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=args.timeout_seconds,
        # 개발 단계만 자가 검사 명령 **하나**를 돌릴 수 있다. 쓰는 명령·git·삭제는 허용하지 않는다.
        allowed_tools=SELF_CHECK_TOOLS if stage.artifact == "lesson_draft_output" else (),
    )
    print(f"{stage.name} provider={provider} model={args.model or 'default'}")
    with tempfile.TemporaryDirectory(prefix=f"content-{stage.name}-") as temp_dir:
        temp_output = Path(temp_dir) / "stage-output.json"
        client.run_prompt(
            prompt=prompt,
            output_schema=ARTIFACT_SCHEMAS[stage.artifact],
            output_path=temp_output,
            model=args.model,
            stage=stage.name,
        )
        result = validate_file(temp_output, artifact=stage.artifact)
        if result["status"] != "PASS":
            raise RuntimeError(f"{stage.name} schema failed: {result['errors']}")
        report = json.loads(temp_output.read_text(encoding="utf-8"))

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    missing = [rel for rel in stage.expected_files if not (run_dir / rel).exists()]
    if missing:
        raise FileNotFoundError(f"{stage.name}가 보고는 했지만 파일이 없다: {missing}")


# 개발 단계가 끝내기 전에 돌리는 자가 검사. 허용 목록은 **이 명령의 앞부분**과 맞아야 한다.
SELF_CHECK_TOOLS = ("Bash(python -B -m stages.scripts.self_check:*)",)


def self_check_command(run_dir: Path, args: argparse.Namespace) -> str:
    gyo6 = f' --gyo6-root "{args.gyo6_root.resolve()}"' if args.gyo6_root else ""
    return f'python -B -m stages.scripts.self_check "{run_dir.resolve()}"{gyo6}'


# 그림 규격(prompts/asset_spec_contract.md)을 함께 받는 stage.
# 계획하는 쪽과 옮겨 적는 쪽이 같은 문서를 봐야 둘이 안 갈린다.
ASSET_SPEC_STAGES = ("visual_design", "senior_developer")


def build_prompt(
    stage: ProductionStage,
    run_dir: Path,
    storyboard_path: Path | None,
    args: argparse.Namespace,
    feedback: str = "",
) -> str:
    guide = stage.prompt_path.read_text(encoding="utf-8")
    if stage.artifact == "lesson_draft_output":
        # lesson.json 을 쓰는 단계는 **계약서를 반드시 함께 받는다.** 검사(`check_lesson_standalone`)가
        # 요구하는 것 — 원자 어휘, step 4종과 exitCondition, stimulus 필드, sourcePanel·acceptance
        # 3줄, ui 배치 옵트인, 타이틀 로고 고정 파일명 — 이 전부 계약서에만 적혀 있다.
        # 이어 붙이지 않으면 모델은 그 규칙을 볼 길이 없는데 게이트는 그대로 판정한다.
        guide = with_lesson_contract(guide)
    if stage.name in ASSET_SPEC_STAGES:
        # 그림을 **계획하는** 단계는 계약서 전문을 받지 않는다. 그런데 계약서에만 적힌
        # 규격(전신 비례·투명·타이틀 고정 경로)을 어기면 굽는 단계가 그대로 따라간다.
        # 실측 2026-09-23(4-1/03) — asset-plan.json 이 인물을 "허리 위까지만"으로 지시해
        # 계약서와 정반대가 됐고, 어떤 게이트도 그 모순을 못 봤다.
        guide = with_asset_spec(guide)
    context = {
        "run_dir": str(run_dir.resolve()),
        "storyboard_path": str(storyboard_path.resolve()) if storyboard_path else "",
        "expected_files": list(stage.expected_files),
        "depends_on": list(stage.depends_on),
        "interview_notes": str(args.interview_notes.resolve()) if args.interview_notes else "",
        "screen_report": str(args.screen_report.resolve()) if args.screen_report else "",
    }
    interview = read_optional(args.interview_notes)
    screen = read_optional(args.screen_report)
    references = "\n\n".join(
        part
        for part in (
            build_class_names_section(args.gyo6_root.resolve() if args.gyo6_root else None)
            if stage.name == "senior_developer"
            else "",
            build_ext_hooks_section(args.gyo6_root.resolve() if args.gyo6_root else None)
            if stage.name == "senior_developer"
            else "",
            build_layout_reference_section(args.gyo6_root.resolve() if args.gyo6_root else None)
            if stage.name in ("senior_designer", "visual_design", "senior_developer")
            else "",
        )
        if part
    )
    retry_block = ""
    if feedback:
        # 걸린 것을 **그대로** 준다. 요약하면 모델이 다른 곳을 고친다.
        retry_block = f"""

이전 시도가 검증에 실패했습니다. 걸린 것은 이렇습니다.

{feedback}

**이 원인만 고친 완전한 산출물을 같은 경로에 다시 저장합니다.**
고치지 않은 부분은 그대로 두고, 문항 수나 문구를 줄여서 통과시키려 하지 않습니다.
"""
    final_instruction = (
        "반드시 RUN_DIR 아래의 expected_files를 작성한 뒤, 아래 SELF_CHECK 를 돌려 **위반 0 이 될 때까지** 고칩니다.\n"
        f"SELF_CHECK: {self_check_command(run_dir, args)}\n"
        "(이 명령만 실행 권한이 있습니다. 다른 명령은 거부됩니다.) 통과한 뒤 "
        "`schemas/lesson_draft_output.schema.json`에 맞는 JSON 객체 하나만 마지막 응답으로 출력합니다."
        if stage.artifact == "lesson_draft_output"
        else "반드시 RUN_DIR 아래의 expected_files를 작성한 뒤, schema에 맞는 JSON 객체 하나만 마지막 응답으로 출력합니다."
    )
    return f"""{guide}{retry_block}

CONTEXT_JSON:
{json.dumps(context, ensure_ascii=False, indent=2)}

RUN_DIR:
{run_dir.resolve()}

STORYBOARD_PATH:
{storyboard_path.resolve() if storyboard_path else ""}

INTERVIEW_NOTES:
{interview}

SCREEN_REPORT:
{screen}

RUNTIME_REFERENCES:
{references}

{final_instruction}
"""


def read_optional(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


STAGE_QUESTION_LABEL = {
    "senior_planner": "기획 — 원문이 비워 둔 것",
    "senior_designer": "디자인 — 화면에서 부딪히는 것",
    "interview_brief": "제작 지침 — 확인이 필요한 것",
    "lesson_spec": "단일 명세 — 추적할 수 없는 것",
    "visual_design": "비주얼 — 확인이 필요한 것",
    "senior_developer": "개발 — 확인이 필요한 것",
}


def collect_open_questions(run_dir: Path) -> list[tuple[str, list[str]]]:
    """각 단계가 낸 `open_questions` 를 순서대로 모은다.

    **이것이 인터뷰의 본체다.** 단계들이 "원문에 없어서 못 정했다"고 남긴 것이라, 사람이
    답해야 하는 진짜 질문은 전부 여기 있다. 예전에는 질문지가 고정 문구 6줄만 담고 이 목록을
    안 실어서, 물어볼 것이 보고서 JSON 안에만 있었다(실측 2026-09-10 — 기획 14건·디자인 4건이
    질문지에 하나도 안 올라왔다).
    """
    collected: list[tuple[str, list[str]]] = []
    for stage in STAGES:
        report_path = run_dir / stage.report_name
        if not report_path.exists():
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        questions = [q for q in (report.get("open_questions") or []) if isinstance(q, str) and q.strip()]
        if questions:
            collected.append((stage.name, questions))
    return collected


def read_existing_answers(path: Path) -> dict[str, str]:
    """이미 만들어 둔 질문지에서 `질문 → 답` 을 읽어 온다.

    질문 번호(Q1, Q2 …)는 단계가 늘 때마다 밀리므로 **질문 본문**을 열쇠로 쓴다.
    """
    if not path.exists():
        return {}
    answers: dict[str, str] = {}
    question: str | None = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("### "):
            question = question_key(stripped[4:])
            continue
        if question and stripped.startswith("답:"):
            body = stripped[2:].strip()
            if not body:  # 다음 줄에 쓴 경우
                for follow in lines[index + 1 : index + 6]:
                    text = follow.strip()
                    if not text:
                        continue
                    if text.startswith(("#", "---", "```")):
                        break
                    body = text
                    break
            if body:
                answers[question] = body
            question = None
    return answers


def question_key(heading: str) -> str:
    """질문 번호를 떼고 본문 앞부분만 남긴다. 번호가 밀려도 같은 질문으로 알아본다."""
    import re as _re

    return _re.sub(r"^Q[\w-]+\.\s*", "", heading).strip()[:80]


BASELINE_QUESTIONS = [
    "스토리보드에서 반드시 살려야 하는 장면·문항·대사가 있습니까?",
    "피해야 할 색·화풍·연출이 있습니까?",
    "배치할 자리(슬롯/id)와 런타임 제약이 있습니까?",
]


def write_interview_package(run_dir: Path) -> None:
    """사람이 답을 적어 넣을 질문지를 만든다.

    **이미 답한 질문을 다시 묻지 않는다.** 단계마다 자기 `open_questions` 를 새로 내므로
    그대로 모으면 앞서 답한 것이 계속 다시 실린다. 실측(2026-09-10) — 43건 중 **27건이
    이미 답한 것의 재출제**였고, 진짜 새 질문은 16건뿐이었다. 답하는 사람이 매번 전체를
    다시 훑어야 하면 인터뷰 자체가 건너뛰어진다.

    그래서 답을 그대로 들고 오고, **안 답한 것만 맨 위로 모은다.**
    """
    interview_dir = run_dir / "interview"
    interview_dir.mkdir(parents=True, exist_ok=True)
    target = interview_dir / "questions.md"
    known = read_existing_answers(target)

    pending: list[tuple[str, str]] = []  # (구분, 질문)
    answered: list[tuple[str, str, str]] = []  # (구분, 질문, 답)
    for stage_name, questions in collect_open_questions(run_dir):
        label = STAGE_QUESTION_LABEL.get(stage_name, stage_name)
        for question in questions:
            key = question_key(question)
            if key in known:
                answered.append((label, question.strip(), known[key]))
            else:
                pending.append((label, question.strip()))
    for question in BASELINE_QUESTIONS:
        key = question_key(question)
        if key in known:
            answered.append(("그 밖에 정해 둘 것", question, known[key]))
        else:
            pending.append(("그 밖에 정해 둘 것", question))

    lines = [
        "# 인터뷰 질문",
        "",
        f"**답이 필요한 것 {len(pending)}건** (이미 답한 {len(answered)}건은 아래에 그대로 두었습니다).",
        "",
        "각 질문의 `답:` 뒤에 그대로 적으면 됩니다. 다 적을 필요는 없습니다 —",
        "비워 두면 그 자리는 확정되지 않은 채로 남고, 이후 단계가 지어내지 않습니다.",
        "",
        "```bash",
        f"python -B ./produce_lesson.py runs/{run_dir.name} \\",
        "    --start-at interview_brief \\",
        f"    --interview-notes runs/{run_dir.name}/interview/questions.md",
        "```",
        "",
        "---",
        "",
        f"## 답이 필요한 것 ({len(pending)}건)",
        "",
    ]
    if pending:
        number = 0
        current = None
        for label, question in pending:
            if label != current:
                current = label
                lines += [f"### — {label}", ""]
            number += 1
            lines += [f"### Q{number}. {question}", "", "답:", ""]
    else:
        lines += ["앞 단계가 새로 낸 질문이 없습니다.", ""]

    if answered:
        lines += [
            "---",
            "",
            f"## 이미 답한 것 ({len(answered)}건) — 고칠 것만 고치면 됩니다",
            "",
        ]
        for index, (label, question, answer) in enumerate(answered, start=1):
            lines += [f"### A{index}. [{label}] {question}", "", f"답: {answer}", ""]

    lines += [
        "---",
        "",
        "## 참고 — 지금까지 정해진 것",
        "",
        "- 기획서: `planning/content-plan.md`",
        "- 화면 배치: `design/wireframe.md`",
        "- 비주얼 콘셉트: `design/concept.md`",
        "- 제작 지침: `planning/production-guide.md`",
        "",
        "요약을 여기 옮겨 적지 않습니다. 요약을 보고 답하면 원문과 어긋난 채로 굳습니다.",
        "",
    ]

    body = "\n".join(lines) + "\n"
    if target.exists() and has_answers(target):
        fresh = interview_dir / "questions-new.md"
        fresh.write_text(body, encoding="utf-8")
        print(f"  새 질문 {len(pending)}건 · 기존 답 {len(answered)}건 → {fresh.name}")
        return
    target.write_text(body, encoding="utf-8")
    print(f"  질문 {len(pending)}건을 질문지에 실었다")


def has_answers(path: Path) -> bool:
    """질문지에 사람이 답을 적었는가.

    **두 가지 형태를 다 본다.** 사람은 `답:` 뒤에 바로 이어 쓰기도 하고 다음 줄에 쓰기도 한다.
    실측(2026-09-10) — 처음에는 "다음 줄" 만 봐서, 같은 줄에 적은 답 24건을 "안 적었다" 로
    판정했다. 그 상태로 질문지를 다시 썼으면 **사람이 적은 답이 통째로 날아갔다.**
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("답:"):
            continue
        if stripped[2:].strip():  # `답: 여기에 바로 쓴 경우`
            return True
        for follow in lines[index + 1 : index + 4]:  # 다음 줄에 쓴 경우
            text = follow.strip()
            if not text:
                continue
            if text.startswith(("#", "---", "```")):
                break
            return True
    return False


def write_review_log(run_dir: Path, args: argparse.Namespace) -> None:
    review_dir = run_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    checklist = read_optional(run_dir / "review" / "design-review-checklist.md")
    screen = read_optional(args.screen_report)
    log = [
        "# 디자인 리뷰 로그",
        "",
        f"- created_at: {datetime.now(KST).isoformat()}",
        f"- screen_report: {str(args.screen_report) if args.screen_report else ''}",
        "",
        "## 체크리스트",
        checklist,
        "",
        "## 화면 보고",
        screen or "아직 화면 캡처 보고가 없다. 배치와 빌드 뒤 `review_lesson.py` 또는 check_rendered 결과를 추가한다.",
    ]
    (review_dir / "design-review-log.md").write_text("\n".join(log) + "\n", encoding="utf-8")


def check_outputs(run_dir: Path, args: argparse.Namespace, expected_lesson: bool = True) -> int:
    """마지막 판정. `expected_lesson` 은 이번 실행이 개발 단계까지 갔는가다.

    개발까지 갔는데 `lesson.json` 이 없으면 **실패다.** 예전에는 무조건 0을 돌려줘서
    개발이 실패해 파일이 안 생긴 경우와 인터뷰에서 의도적으로 끊은 경우가 구분되지 않았다.
    """
    lesson_path = run_dir / "lesson" / "lesson.json"
    report_path = run_dir / "lesson_draft.json"
    # 보고서가 있는데 lesson.json 이 없으면 개발 단계가 돌다 깨진 것이다 —
    # `--check-only` 로 들어와도 그건 성공이 아니다.
    expected_lesson = expected_lesson or report_path.exists()
    if not lesson_path.exists():
        if not expected_lesson:
            print(f"아직 개발 산출물이 없다(여기까지가 이번 실행의 범위다): {lesson_path}")
            return 0
        print(f"개발 단계까지 돌았는데 lesson.json 이 없다: {lesson_path}", file=sys.stderr)
        return REJECTED_EXIT
    if not report_path.exists():
        print(f"개발 보고서가 없다: {report_path}", file=sys.stderr)
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    gyo6_root = args.gyo6_root.resolve() if args.gyo6_root else None
    registry = load_atom_registry(gyo6_root)
    print(describe_atom_registry(registry, gyo6_root))
    violations = check_lesson_standalone(lesson, report, run_dir, registry)
    print(format_violations(violations))
    if errors_only(violations):
        return REJECTED_EXIT

    spec_path = run_dir / "spec" / "lesson-spec.json"
    if spec_path.exists():
        spec_errors = write_and_verify(run_dir, PROJECT_DIR / "schemas" / "lesson_spec.schema.json")
        if spec_errors:
            print(f"\n명세 추적·기능 테스트 실패 {len(spec_errors)}건", file=sys.stderr)
            for error in spec_errors[:12]:
                print(f"  · {error}", file=sys.stderr)
            return REJECTED_EXIT
        plan = json.loads((run_dir / "tests" / "functional-test-plan.json").read_text(encoding="utf-8"))
        print(f"\n명세 추적 PASS · 자동 생성 테스트 {len(plan.get('cases', []))}건")
    else:
        print("\nlegacy run: spec/lesson-spec.json 이 없어 명세 기반 검사는 생략한다")

    # 그림을 여기서 굽고 나면 **실제 파일 크기**를 manifest 에 적을 수 있다.
    # 크기가 0 이 아니면 그쪽 빌드가 "이미 있는 에셋" 으로 보고 다시 생성하지 않는다.
    lesson_dir = run_dir / "lesson"
    refs = list(report.get("asset_refs") or [])
    sizes = {
        ref: (lesson_dir / ref).stat().st_size for ref in refs if (lesson_dir / ref).exists()
    }
    manifest = build_manifest(lesson, refs, sizes)
    (lesson_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    gaps = rendered_asset_gaps(run_dir)
    if gaps:
        print(f"\n아직 파일이 없는 그림 {len(gaps)}장 (그쪽 빌드가 생성 대상으로 본다):")
        for ref in gaps[:8]:
            print(f"  · {ref}")
        if len(gaps) > 8:
            print(f"  · … {len(gaps) - 8}장 더")
    else:
        print(f"\n그림 {len(sizes)}장이 전부 파일로 있다")
    return 0


def write_pipeline_log(run_dir: Path, event: str, payload: dict) -> None:
    log_path = run_dir / "pipeline-log.jsonl"
    item = {"time": datetime.now(KST).isoformat(), "event": event, **payload}
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def print_estimates() -> None:
    print("\n예상 비용 감각")
    total_input = sum(stage.estimate_input_tokens for stage in STAGES)
    total_output = sum(stage.estimate_output_tokens for stage in STAGES)
    total_minutes = sum(stage.estimate_minutes for stage in STAGES)
    for stage in STAGES:
        print(
            f"  {stage.name:17} input~{stage.estimate_input_tokens:,} "
            f"output~{stage.estimate_output_tokens:,} {stage.estimate_minutes:g}분"
        )
    print(f"  total             input~{total_input:,} output~{total_output:,} {total_minutes:g}분")


def slugify(value: str) -> str:
    keep = [char if char.isalnum() else "-" for char in value]
    return "".join(keep).strip("-")[:40] or "storyboard"


if __name__ == "__main__":
    sys.exit(main())
