from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import CodexClient


PROJECT_DIR = Path(__file__).resolve().parent.parent
DESIGN_REFINE_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "design_refine_system.md"
BUILDER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "builder_output.schema.json"


def refine_design(
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    design_review_path: Path,
    run_dir: Path,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
) -> dict | None:
    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    asset_output = load_asset_output(asset_generator_path)
    builder_output = json.loads(builder_path.read_text(encoding="utf-8"))
    design_review_output = json.loads(design_review_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    prompt = build_prompt(
        input_data=input_data,
        planner_output=planner_output,
        asset_output=asset_output,
        builder_output=builder_output,
        design_refine_packet=build_design_refine_packet(design_review_output),
        html=html,
        run_dir=run_dir,
    )
    client = CodexClient(
        codex_bin=codex_bin,
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


def build_design_refine_packet(design_review_output: dict) -> dict:
    return {
        "status": design_review_output.get("status"),
        "html_path": design_review_output.get("html_path"),
        "reviewed_screenshots": design_review_output.get("reviewed_screenshots", []),
        "render_evidence": compact_render_evidence(design_review_output.get("render_evidence", {})),
        "designer_review": design_review_output.get("designer_review"),
        "asset_review": design_review_output.get("asset_review"),
        "priority_findings": design_review_output.get("priority_findings", []),
        "refine_suggestions": design_review_output.get("refine_suggestions", []),
    }


def compact_render_evidence(render_evidence: dict) -> dict:
    if not isinstance(render_evidence, dict):
        return {}
    render_checks = render_evidence.get("render_checks", {})
    if not isinstance(render_checks, dict):
        render_checks = {}
    return {
        "status": render_evidence.get("status"),
        "screenshots": render_evidence.get("screenshots", []),
        "render_checks": {
            key: render_checks.get(key, [])
            for key in (
                "console_errors",
                "page_errors",
                "request_failures",
                "broken_images",
                "horizontal_overflow",
                "text_clipping",
                "overlaps",
                "fixed_overlay_risks",
            )
        },
        "priority_findings": render_evidence.get("priority_findings", []),
        "refine_suggestions": render_evidence.get("refine_suggestions", []),
    }


def build_prompt(
    input_data: dict,
    planner_output: dict,
    asset_output: dict,
    builder_output: dict,
    design_refine_packet: dict,
    html: str,
    run_dir: Path,
) -> str:
    system_prompt = DESIGN_REFINE_SYSTEM_PROMPT.read_text(encoding="utf-8")
    return f"""{system_prompt}

RUN_DIR:
{run_dir.resolve()}

INPUT_JSON:
{json.dumps(input_data, ensure_ascii=False, indent=2)}

PLANNER_OUTPUT_JSON:
{json.dumps(planner_output, ensure_ascii=False, indent=2)}

ASSET_GENERATOR_OUTPUT_JSON:
{json.dumps(asset_output, ensure_ascii=False, indent=2)}

PREVIOUS_BUILDER_OUTPUT_JSON:
{json.dumps(builder_output, ensure_ascii=False, indent=2)}

DESIGN_REFINE_PACKET_JSON:
{json.dumps(design_refine_packet, ensure_ascii=False, indent=2)}

PREVIOUS_HTML:
{html}
"""
