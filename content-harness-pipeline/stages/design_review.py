from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stages.scripts.codex_client import CodexClient
from stages.visual_qa import run_visual_qa


PROJECT_DIR = Path(__file__).resolve().parent.parent
DESIGN_REVIEW_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "design_review_system.md"
DESIGN_REVIEW_MODEL_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "design_review_model_output.schema.json"
KST = timezone(timedelta(hours=9))


def review_design(
    *,
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    run_dir: Path,
    iteration: str,
    output_path: Path,
    codex_bin: str = "codex",
    model: str | None = None,
    timeout_seconds: int = 600,
    asset_budget: int = 9,
) -> dict | None:
    with tempfile.TemporaryDirectory(prefix="content-harness-design-review-") as temp_dir:
        visual_qa_output_path = Path(temp_dir) / "visual-qa-output.json"
        run_visual_qa(
            html_path=html_path,
            run_dir=run_dir,
            iteration=iteration,
            output_path=visual_qa_output_path,
            timeout_seconds=timeout_seconds,
            artifact_dir_name="design_review",
            viewport_names=("desktop",),
        )
        visual_qa_output = load_json(visual_qa_output_path)

        model_output_path = Path(temp_dir) / "design-review-model-output.json"
        prompt = build_prompt(
            input_path=input_path,
            planner_path=planner_path,
            asset_generator_path=asset_generator_path,
            builder_path=builder_path,
            html_path=html_path,
            run_dir=run_dir,
            visual_qa_output=visual_qa_output,
            asset_budget=asset_budget,
        )
        schema_path = write_budgeted_schema(Path(temp_dir), asset_budget)
        client = CodexClient(
            codex_bin=codex_bin,
            project_dir=PROJECT_DIR,
            timeout_seconds=timeout_seconds,
        )
        token_usage = client.run_prompt(
            prompt=prompt,
            output_schema=schema_path,
            output_path=model_output_path,
            model=model,
        )
        model_output = load_json(model_output_path)

    final_output = {
        "status": model_output["status"],
        "checked_at": datetime.now(KST).isoformat(timespec="seconds"),
        "html_path": "output/index.html",
        "reviewed_screenshots": build_reviewed_screenshots(visual_qa_output, run_dir),
        "overall_assessment": model_output["overall_assessment"],
        "scene_reviews": model_output["scene_reviews"],
        "motion_review": model_output["motion_review"],
        "asset_review": model_output["asset_review"],
        "priority_findings": model_output["priority_findings"],
        "refine_suggestions": model_output["refine_suggestions"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return token_usage


def build_reviewed_screenshots(visual_qa_output: dict, run_dir: Path) -> list[dict]:
    screenshots = visual_qa_output.get("screenshots", [])
    if not isinstance(screenshots, list):
        return []
    reviewed = []
    for screenshot in screenshots:
        if not isinstance(screenshot, dict):
            continue
        path = screenshot.get("path")
        if not isinstance(path, str):
            continue
        reviewed.append(
            {
                "viewport": screenshot.get("viewport", ""),
                "capture_label": screenshot.get("capture_label", ""),
                "path": path,
                "absolute_path": str((run_dir / path).resolve()),
                "width": screenshot.get("width"),
                "height": screenshot.get("height"),
            }
        )
    return reviewed


def write_budgeted_schema(temp_dir: Path, asset_budget: int) -> Path:
    """Write a per-run copy of the model output schema with the asset request
    cap set to asset_budget, so the budget is hard-enforced at generation time."""
    schema = json.loads(DESIGN_REVIEW_MODEL_OUTPUT_SCHEMA.read_text(encoding="utf-8"))
    asset_review_props = schema["properties"]["asset_review"]["properties"]
    asset_review_props["regenerate_assets"]["maxItems"] = asset_budget
    asset_review_props["new_asset_requests"]["maxItems"] = asset_budget
    schema_path = temp_dir / "design-review-model-output.budgeted.schema.json"
    schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")
    return schema_path


def build_prompt(
    *,
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
    builder_path: Path,
    html_path: Path,
    run_dir: Path,
    visual_qa_output: dict,
    asset_budget: int = 9,
) -> str:
    system_prompt = DESIGN_REVIEW_SYSTEM_PROMPT.read_text(encoding="utf-8")
    input_data = load_json(input_path)
    planner_output = load_json(planner_path)
    asset_output = load_asset_output(asset_generator_path)
    builder_output = load_json(builder_path)
    html = html_path.read_text(encoding="utf-8")
    screenshot_paths = [
        str((run_dir / screenshot["path"]).resolve())
        for screenshot in visual_qa_output.get("screenshots", [])
        if isinstance(screenshot, dict) and isinstance(screenshot.get("path"), str)
    ]

    return f"""{system_prompt}

ASSET_BUDGET:
{asset_budget}

RUN_DIR:
{run_dir.resolve()}

SCREENSHOT_FILES:
{json.dumps(screenshot_paths, ensure_ascii=False, indent=2)}

INPUT_JSON:
{json.dumps(input_data, ensure_ascii=False, indent=2)}

PLANNER_DESIGN_CONTEXT_JSON:
{json.dumps(compact_planner_context(planner_output), ensure_ascii=False, indent=2)}

ASSET_SUMMARY_JSON:
{json.dumps(compact_asset_output(asset_output), ensure_ascii=False, indent=2)}

BUILDER_OUTPUT_JSON:
{json.dumps(builder_output, ensure_ascii=False, indent=2)}

DESKTOP_SCREENSHOT_SUMMARY_JSON:
{json.dumps(compact_desktop_screenshot_summary(visual_qa_output), ensure_ascii=False, indent=2)}

HTML:
{html}
"""


def load_asset_output(asset_generator_path: Path | None) -> dict:
    if asset_generator_path is None:
        return {"assets": []}
    return load_json(asset_generator_path)


def compact_planner_context(planner_output: dict) -> dict:
    sections = planner_output.get("sections", [])
    if not isinstance(sections, list):
        sections = []
    asset_plan = planner_output.get("asset_plan", [])
    if not isinstance(asset_plan, list):
        asset_plan = []
    characters = planner_output.get("characters", [])
    if not isinstance(characters, list):
        characters = []
    return {
        # page.audience/tone은 디자인 판정의 기준이다. 대상 학습자를 모르면 "초등 대상인데 글자가 작다"
        # 같은 판단을 할 수 없다.
        "page": planner_output.get("page", {}),
        "art_direction": planner_output.get("art_direction", ""),
        "asset_groups": planner_output.get("asset_groups", []),
        "characters": [
            {
                "id": character.get("id"),
                "name": character.get("name"),
                "role": character.get("role"),
                "identity": character.get("identity", {}),
                "reference_asset_id": character.get("reference_asset_id", ""),
            }
            for character in characters
            if isinstance(character, dict)
        ],
        "interactions": planner_output.get("interactions", []),
        "sections": [
            {
                "id": section.get("id"),
                "title": section.get("title"),
                "purpose": section.get("purpose"),
                "interaction_ids": section.get("interaction_ids", []),
                "asset_ids": section.get("asset_ids", []),
            }
            for section in sections
            if isinstance(section, dict)
        ],
        "asset_plan": [
            {
                "id": asset.get("id"),
                "character_id": asset.get("character_id", ""),
                "purpose": asset.get("purpose"),
                "visual_role": asset.get("visual_role"),
                "style_constraints": asset.get("style_constraints", ""),
                "composition_notes": asset.get("composition_notes", ""),
                "negative_prompt": asset.get("negative_prompt", ""),
                "usage_section_ids": asset.get("usage_section_ids", []),
            }
            for asset in asset_plan
            if isinstance(asset, dict)
        ],
    }


def compact_asset_output(asset_output: dict) -> dict:
    assets = asset_output.get("assets", [])
    if not isinstance(assets, list):
        assets = []
    return {
        "assets": [
            {
                "id": asset.get("id"),
                "character_id": asset.get("character_id", ""),
                "path": asset.get("path"),
                "status": asset.get("status", ""),
                "usage_section_ids": asset.get("usage_section_ids", []),
                "alt_text": asset.get("alt_text", ""),
            }
            for asset in assets
            if isinstance(asset, dict)
        ]
    }


def compact_desktop_screenshot_summary(visual_qa_output: dict) -> dict:
    screenshots = visual_qa_output.get("screenshots", [])
    if not isinstance(screenshots, list):
        screenshots = []
    return {
        "screenshots": [
            screenshot
            for screenshot in screenshots
            if isinstance(screenshot, dict) and screenshot.get("viewport") == "desktop"
        ],
    }


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data
