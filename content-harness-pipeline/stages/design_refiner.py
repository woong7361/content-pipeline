from __future__ import annotations

import json
import re
from pathlib import Path

from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client


PROJECT_DIR = Path(__file__).resolve().parent.parent
DESIGN_REFINE_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "design_refine_system.md"
BUILDER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "builder_output.schema.json"
DEFAULT_TARGET_HTML_PATH = "output/index.html"


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
    claude_bin: str = "claude",
    llm_provider: str = PROVIDER_CODEX,
    model: str | None = None,
    timeout_seconds: int = 600,
    output_schema_path: Path | None = None,
    target_html_path: str = DEFAULT_TARGET_HTML_PATH,
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
        target_html_path=target_html_path,
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
        output_schema=output_schema_path or BUILDER_OUTPUT_SCHEMA,
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
        "iteration": extract_iteration(design_review_output),
        "reviewed_screenshots": design_review_output.get("reviewed_screenshots", []),
        "overall_assessment": design_review_output.get("overall_assessment"),
        "scene_reviews": design_review_output.get("scene_reviews", []),
        "asset_review": design_review_output.get("asset_review"),
        "priority_findings": design_review_output.get("priority_findings", []),
        "refine_suggestions": design_review_output.get("refine_suggestions", []),
    }


def extract_iteration(design_review_output: dict) -> str:
    screenshots = design_review_output.get("reviewed_screenshots", [])
    if isinstance(screenshots, list):
        for screenshot in screenshots:
            if not isinstance(screenshot, dict):
                continue
            path = screenshot.get("path")
            if not isinstance(path, str):
                continue
            match = re.search(r"(?:^|/)iter_(\d{3})(?:/|$)", path.replace("\\", "/"))
            if match:
                return match.group(1)
    return ""


def build_prompt(
    input_data: dict,
    planner_output: dict,
    asset_output: dict,
    builder_output: dict,
    design_refine_packet: dict,
    html: str,
    run_dir: Path,
    target_html_path: str,
) -> str:
    system_prompt = DESIGN_REFINE_SYSTEM_PROMPT.read_text(encoding="utf-8")
    return f"""{system_prompt}

RUN_DIR:
{run_dir.resolve()}

TARGET_HTML_PATH:
{target_html_path}

OUTPUT_CONTRACT:
- Use PREVIOUS_HTML as the source HTML.
- Write the refined HTML to RUN_DIR/TARGET_HTML_PATH.
- Return builder_output.html_path exactly equal to TARGET_HTML_PATH.
- If TARGET_HTML_PATH is not output/index.html, do not overwrite output/index.html.
- If you run the visual QA preview command, pass --html-path "<RUN_DIR>/{target_html_path}" so the preview captures the refined debug file.

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
