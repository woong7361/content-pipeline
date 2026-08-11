from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.source_resolve import teacher_root_from_input
from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client
from stages.scripts.common_components import build_common_components_section
from stages.scripts.prompt_parts import with_common_html_contract
from stages.scripts.style_references import build_style_reference_prompt


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONTENT_REFINE_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "content_refine_system.md"
BUILDER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "builder_output.schema.json"


def refine_content(
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    content_critique_path: Path,
    run_dir: Path,
    output_path: Path,
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    llm_provider: str = PROVIDER_CODEX,
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    asset_output = load_asset_output(asset_generator_path)
    builder_output = json.loads(builder_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    critique_output = json.loads(content_critique_path.read_text(encoding="utf-8"))
    refine_packet = build_refine_packet(critique_output=critique_output)
    prompt = build_prompt(
        input_data=input_data,
        planner_output=planner_output,
        asset_output=asset_output,
        builder_output=builder_output,
        html=html,
        refine_packet=refine_packet,
        run_dir=run_dir,
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
        output_schema=BUILDER_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
    )


def load_asset_output(asset_generator_path: Path | None) -> dict:
    if asset_generator_path is None:
        return {"assets": []}
    return json.loads(asset_generator_path.read_text(encoding="utf-8"))


def build_refine_packet(*, critique_output: dict) -> dict:
    return {
        "content": {
            "priority_issues": critique_output.get("priority_issues", []),
            "refine_suggestions": critique_output.get("refine_suggestions", []),
        },
    }


def build_prompt(
    input_data: dict,
    planner_output: dict,
    asset_output: dict,
    builder_output: dict,
    html: str,
    refine_packet: dict,
    run_dir: Path,
) -> str:
    system_prompt = with_common_html_contract(CONTENT_REFINE_SYSTEM_PROMPT.read_text(encoding="utf-8"))
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    planner_json = json.dumps(planner_output, ensure_ascii=False, indent=2)
    asset_json = json.dumps(asset_output, ensure_ascii=False, indent=2)
    builder_json = json.dumps(builder_output, ensure_ascii=False, indent=2)
    refine_packet_json = json.dumps(refine_packet, ensure_ascii=False, indent=2)
    style_reference_json = build_style_reference_prompt(input_data, PROJECT_DIR)
    return f"""{system_prompt}

RUN_DIR:
{run_dir.resolve()}

{build_common_components_section(teacher_root_from_input(input_data))}

INPUT_JSON:
{input_json}

STYLE_REFERENCE_SET_JSON:
{style_reference_json}

PLANNER_OUTPUT_JSON:
{planner_json}

ASSET_GENERATOR_OUTPUT_JSON:
{asset_json}

PREVIOUS_BUILDER_OUTPUT_JSON:
{builder_json}

REFINE_PACKET_JSON:
{refine_packet_json}

PREVIOUS_HTML:
{html}
"""
