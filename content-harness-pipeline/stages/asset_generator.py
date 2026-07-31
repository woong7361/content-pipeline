from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import CodexClient
from stages.scripts.prompt_parts import ASSET_EXAMPLES_DIR, load_asset_examples
from stages.scripts.style_references import build_style_reference_prompt


PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSET_GENERATOR_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "asset_generator_system.md"
ASSET_GENERATOR_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "asset_generator_output.schema.json"


def generate_assets(
    input_path: Path,
    planner_path: Path,
    run_dir: Path,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 1200,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    prompt = build_prompt(input_data=input_data, planner_output=planner_output, run_dir=run_dir)
    client = CodexClient(
        codex_bin=codex_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=ASSET_GENERATOR_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def build_prompt(input_data: dict, planner_output: dict, run_dir: Path) -> str:
    system_prompt = ASSET_GENERATOR_SYSTEM_PROMPT.read_text(encoding="utf-8")
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    planner_json = json.dumps(planner_output, ensure_ascii=False, indent=2)
    style_reference_json = build_style_reference_prompt(input_data, PROJECT_DIR)
    return f"""{system_prompt}

{load_asset_examples()}

RUN_DIR:
{run_dir.resolve()}

ASSET_EXAMPLES_DIR:
{ASSET_EXAMPLES_DIR.resolve()}

저장 규칙:
- JSON의 `path`는 planner의 `intended_path`와 같은 `output/assets/...` 상대 경로를 사용합니다.
- 실제 이미지 파일은 `RUN_DIR / path` 위치에 저장합니다.
- 예: path가 `output/assets/hero.png`이면 실제 파일은 `{run_dir.resolve()}\\output\\assets\\hero.png`입니다.

INPUT_JSON:
{input_json}

STYLE_REFERENCE_SET_JSON:
{style_reference_json}

PLANNER_OUTPUT_JSON:
{planner_json}
"""
