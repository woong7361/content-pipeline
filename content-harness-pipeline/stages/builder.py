from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client


PROJECT_DIR = Path(__file__).resolve().parent.parent
BUILDER_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "builder_system.md"
BUILDER_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "builder_output.schema.json"


def build_html(
    input_path: Path,
    planner_path: Path,
    asset_generator_path: Path | None,
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
    prompt = build_prompt(
        input_data=input_data,
        planner_output=planner_output,
        asset_output=asset_output,
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


def build_prompt(input_data: dict, planner_output: dict, asset_output: dict, run_dir: Path) -> str:
    system_prompt = BUILDER_SYSTEM_PROMPT.read_text(encoding="utf-8")
    input_json = json.dumps(input_data, ensure_ascii=False, indent=2)
    planner_json = json.dumps(planner_output, ensure_ascii=False, indent=2)
    asset_json = json.dumps(asset_output, ensure_ascii=False, indent=2)
    return f"""{system_prompt}

RUN_DIR:
{run_dir.resolve()}

저장 규칙:
- 실제 HTML 파일은 `{run_dir.resolve()}\\output\\index.html`에 저장합니다.
- HTML 파일 내부에서는 `output/assets/foo.png`가 아니라 `assets/foo.png`처럼 상대 경로를 사용합니다.
- 출력 JSON에는 run 디렉토리 기준 경로인 `output/index.html`, `output/assets/foo.png` 형태를 사용합니다.

INPUT_JSON:
{input_json}

PLANNER_OUTPUT_JSON:
{planner_json}

ASSET_GENERATOR_OUTPUT_JSON:
{asset_json}
"""
