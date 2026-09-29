from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client


PROJECT_DIR = Path(__file__).resolve().parent.parent
LESSON_REVIEW_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "lesson_review_system.md"
LESSON_REVIEW_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "lesson_review_output.schema.json"


def review_lesson(
    capture_dir: Path,
    lesson_path: Path,
    storyboard_path: Path | None,
    output_path: Path,
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    llm_provider: str = PROVIDER_CODEX,
    model: str | None = None,
    timeout_seconds: int = 1800,
) -> dict | None:
    """빌드된 차시 화면을 보고 판정한다.

    `lesson_check` 가 못 보는 층만 본다 — 화면이 실제로 어떻게 보이는가.
    이 파이프라인이 다섯 번 놓친 자리이고(전부 사람이 눈으로 찾았다), 그 자리를 메우려고 있다.

    스크린샷은 경로 목록으로 넘긴다. 모델이 직접 열어 본다(design_review 와 같은 방식).
    """
    prompt = build_prompt(
        capture_dir=capture_dir,
        lesson_path=lesson_path,
        storyboard_path=storyboard_path,
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
        output_schema=LESSON_REVIEW_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
        stage="lesson_review",
    )


def build_prompt(
    capture_dir: Path,
    lesson_path: Path,
    storyboard_path: Path | None,
) -> str:
    system_prompt = LESSON_REVIEW_SYSTEM_PROMPT.read_text(encoding="utf-8")
    capture = json.loads((capture_dir / "capture.json").read_text(encoding="utf-8"))

    screenshots = [
        {
            "file": shot.get("file", ""),
            "clicked": shot.get("clicked", ""),
            "absolute_path": str((capture_dir / shot["file"]).resolve()),
            "stage_text": shot.get("stage_text", ""),
        }
        for shot in capture.get("shots", [])
        if isinstance(shot, dict) and shot.get("file")
    ]

    # 화면이 안 넘어간 것은 판정이 아니라 사실이다. 모델이 짐작하지 않게 먼저 말해 준다.
    stuck_note = ""
    if capture.get("stuck"):
        stuck_note = (
            "\n**주의: 진행이 멈췄습니다.** 같은 화면이 반복돼 캡처를 중단했습니다. "
            "뒤쪽 화면은 찍히지 않았으므로 '없다'고 판정하지 말고, 못 봤다고 적습니다.\n"
        )

    storyboard = ""
    if storyboard_path and storyboard_path.exists():
        storyboard = storyboard_path.read_text(encoding="utf-8")

    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    # 화면 판정에 필요한 것만 싣는다. 문항 본문까지 실으면 프롬프트가 계획 검토로 흐른다.
    lesson_view = {
        "title": lesson.get("title", ""),
        "ui": lesson.get("ui", {}),
        "cast": lesson.get("cast", {}),
        "artDirection": lesson.get("artDirection", {}),
        "steps": [
            {
                "id": step.get("id", ""),
                "type": step.get("type", ""),
                "cuts": len(step.get("stageDirections") or []),
                "rounds": len(step.get("rounds") or []),
            }
            for step in lesson.get("steps") or []
            if isinstance(step, dict)
        ],
    }

    return f"""{system_prompt}
{stuck_note}
SCREENSHOTS:
{json.dumps(screenshots, ensure_ascii=False, indent=2)}

PAGE_ERRORS:
{json.dumps(capture.get("page_errors", []), ensure_ascii=False, indent=2)}

LESSON_VIEW:
{json.dumps(lesson_view, ensure_ascii=False, indent=2)}

STORYBOARD_MARKDOWN:
{storyboard}
"""
