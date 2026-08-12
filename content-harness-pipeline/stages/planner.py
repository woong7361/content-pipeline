from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import CodexClient
from stages.scripts.common_components import build_required_art_section
from stages.scripts.source_resolve import teacher_root_from_input
from stages.scripts.style_references import build_style_reference_prompt


PROJECT_DIR = Path(__file__).resolve().parent.parent
PLANNER_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "planner_system.md"
PLANNER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "planner_output.schema.json"


def plan(
    input_path: Path,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    markdown_path = resolve_markdown_path(input_data=input_data, input_path=input_path)
    markdown = markdown_path.read_text(encoding="utf-8")
    prompt = build_prompt(input_data=input_data, markdown=markdown)
    client = CodexClient(
        codex_bin=codex_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=PLANNER_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def resolve_markdown_path(input_data: dict, input_path: Path) -> Path:
    brief = input_data.get("brief", {})
    if not isinstance(brief, dict):
        raise ValueError("input.brief must be an object")
    md_path = brief.get("md_path")
    if not isinstance(md_path, str) or not md_path:
        raise ValueError("input.brief.md_path is required")

    candidate = Path(md_path)
    if not candidate.is_absolute():
        candidate = input_path.parent / candidate
    resolved = candidate.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"story board markdown not found: {resolved}")
    if resolved.suffix.lower() != ".md":
        raise ValueError(f"story board path must point to a Markdown file: {resolved}")
    return resolved


def build_prompt(input_data: dict, markdown: str) -> str:
    system_prompt = PLANNER_SYSTEM_PROMPT.read_text(encoding="utf-8")
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    # 선택된 컴포넌트가 요구하는 art만 넘긴다. planner는 컴포넌트를 고르지 않는다.
    required_art = build_required_art_section(input_data, teacher_root_from_input(input_data))
    style_reference_json = build_style_reference_prompt(input_data, PROJECT_DIR)
    return f"""{system_prompt}

INPUT_JSON:
{input_json}

STYLE_REFERENCE_SET_JSON:
{style_reference_json}

{required_art}

STORY_BOARD_MARKDOWN:
{markdown}
"""
