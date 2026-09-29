from __future__ import annotations

from pathlib import Path

from stages.scripts.atom_registry import build_class_names_section, build_ext_hooks_section
from stages.scripts.codex_client import PROVIDER_CLAUDE, create_prompt_client
from stages.scripts.layout_reference import build_layout_reference_section
from stages.scripts.prompt_parts import with_lesson_contract


PROJECT_DIR = Path(__file__).resolve().parent.parent
LESSON_DRAFT_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "lesson_draft_system.md"
LESSON_DRAFT_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "lesson_draft_output.schema.json"


def draft_lesson(
    storyboard_path: Path,
    run_dir: Path,
    output_path: Path,
    feedback: str = "",
    gyo6_root: Path | None = None,
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    llm_provider: str = PROVIDER_CLAUDE,
    model: str | None = None,
    timeout_seconds: int = 1800,
) -> dict | None:
    """스토리보드 원본에서 lesson.json 을 직접 만든다.

    gyo6_content 의 `agent/lessonJsonGenerator.mjs` 와 같은 자리다. planner 를 거치지 않으므로
    LLM 호출이 1회이고, 그만큼 **상류 게이트가 없다** — 지어낸 내용을 걸러 줄 층이 뒤에 없다.
    그래서 호출 전에 `storyboard_readability.check_storyboard_readable` 로 읽기 경로를 확인하고,
    호출 뒤에는 `lesson_check` 위반을 `feedback` 으로 되먹여 다시 부른다.

    기본 provider 가 claude 인 이유는 PDF 를 페이지 단위로 읽어야 하기 때문이다.
    """
    prompt = build_prompt(
        storyboard_path=storyboard_path,
        run_dir=run_dir,
        feedback=feedback,
        gyo6_root=gyo6_root,
    )
    client = create_prompt_client(
        provider=llm_provider,
        codex_bin=codex_bin,
        claude_bin=claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=LESSON_DRAFT_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
        stage="lesson_draft",
    )


def build_prompt(
    storyboard_path: Path,
    run_dir: Path,
    feedback: str = "",
    gyo6_root: Path | None = None,
) -> str:
    """계획 경로와 **같은 참조 블록**을 싣는다.

    이 경로에도 `player-ext.css` 를 쓰는 것은 같다. 그런데 오래 이 세 블록이 계획 경로에만
    붙어 있었고, 그래서 여기서는 base 가 실제로 쓰는 class 이름도 `window.lessonExt` 훅 이름도
    모른 채 ext 를 썼다. 실측(2026-09-10) — 이 경로로 만든 첫 차시가 `player-ext.css` 를
    19KB 썼는데 모델이 "대상 레포를 못 읽어 런타임으로 확인하지 못했다"고 보고했다.
    이름을 지어내면 그 규칙은 아무것도 하지 않는다(오류도 안 난다).
    """
    system_prompt = with_lesson_contract(LESSON_DRAFT_SYSTEM_PROMPT.read_text(encoding="utf-8"))
    retry_block = ""
    if feedback:
        # 되먹임은 gyo6_content 와 같은 방식이다 — 무엇이 왜 걸렸는지를 그대로 준다.
        # 요약하면 모델이 다른 곳을 고친다.
        retry_block = f"""

이전 시도가 검증에 실패했습니다. 걸린 것은 이렇습니다.

{feedback}

**이 원인만 고친 완전한 lesson.json 을 같은 경로에 다시 저장합니다.**
고치지 않은 부분은 그대로 두고, 문항 수나 문구를 줄여서 통과시키려 하지 않습니다.
"""
    return f"""{system_prompt}

{build_class_names_section(gyo6_root)}
{build_ext_hooks_section(gyo6_root)}
{build_layout_reference_section(gyo6_root)}

RUN_DIR:
{run_dir.resolve()}

STORYBOARD_PATH:
{storyboard_path.resolve()}

LESSON_JSON_PATH:
{(run_dir / "lesson" / "lesson.json").resolve()}

PAGE_MAP_PATH:
{(run_dir / "lesson" / "page-map.md").resolve()}
{retry_block}"""
