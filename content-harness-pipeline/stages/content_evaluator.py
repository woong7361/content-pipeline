from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import CodexClient


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONTENT_EVAL_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "content_eval_system.md"
CONTENT_EVAL_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "content_eval_output.schema.json"


def evaluate_content(
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    rubric: dict,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    asset_output = load_asset_output(asset_generator_path)
    builder_output = json.loads(builder_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    prompt = build_prompt(
        input_data=input_data,
        planner_output=planner_output,
        asset_output=asset_output,
        builder_output=builder_output,
        html=html,
        rubric=rubric,
    )
    client = CodexClient(
        codex_bin=codex_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=CONTENT_EVAL_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def load_asset_output(asset_generator_path: Path | None) -> dict:
    if asset_generator_path is None:
        return {"assets": []}
    return json.loads(asset_generator_path.read_text(encoding="utf-8"))


def build_prompt(
    input_data: dict,
    planner_output: dict,
    asset_output: dict,
    builder_output: dict,
    html: str,
    rubric: dict,
) -> str:
    system_prompt = CONTENT_EVAL_SYSTEM_PROMPT.read_text(encoding="utf-8")
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    planner_json = json.dumps(planner_output, ensure_ascii=False, indent=2)
    asset_json = json.dumps(asset_output, ensure_ascii=False, indent=2)
    builder_json = json.dumps(builder_output, ensure_ascii=False, indent=2)
    rubric_json = json.dumps(rubric, ensure_ascii=False, indent=2)
    return f"""{system_prompt}

INPUT_JSON:
{input_json}

PLANNER_OUTPUT_JSON:
{planner_json}

ASSET_GENERATOR_OUTPUT_JSON:
{asset_json}

BUILDER_OUTPUT_JSON:
{builder_json}

CONTENT_RUBRIC_JSON:
{rubric_json}

HTML:
{html}
"""
