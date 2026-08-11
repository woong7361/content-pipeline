from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import json
import shutil
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from stages.asset_generator import generate_assets
from stages.builder import build_html
from stages.content_critic import critique_content
from stages.content_evaluator import evaluate_content
from stages.content_refiner import refine_content
from stages.design_review import review_design
from stages.design_refiner import refine_design
from stages.planner import plan
from stages.scripts.component_bundle import check_html_links, emit_common
from validate import validate_file, validate_schema, write_result


PROJECT_DIR = Path(__file__).resolve().parent
RUNS_DIR = PROJECT_DIR / "runs"
CONTENT_RUBRIC_PATH = PROJECT_DIR / "content_rubric.yaml"
BUILDER_OUTPUT_SCHEMA_PATH = PROJECT_DIR / "schemas" / "builder_output.schema.json"
KST = timezone(timedelta(hours=9))

MODEL_CODEX_DEFAULT = None
MODEL_GPT_5_6_SOL = "gpt-5.6-sol"
MODEL_GPT_5_5 = "gpt-5.5"
MODEL_GPT_5_4 = "gpt-5.4"
MODEL_GPT_5_4_MINI = "gpt-5.4-mini"
MODEL_O3 = "o3"
MODEL_CLAUDE_OPUS = "opus"
MODEL_CLAUDE_SONNET = "sonnet"

PROVIDER_CODEX = "codex"
PROVIDER_CLAUDE = "claude"


def default_claude_bin() -> str:
    if sys.platform != "win32":
        return "claude"

    claude_cmd = shutil.which("claude.cmd")
    if claude_cmd:
        claude_exe = (
            Path(claude_cmd).parent
            / "node_modules"
            / "@anthropic-ai"
            / "claude-code"
            / "bin"
            / "claude.exe"
        )
        if claude_exe.exists():
            return str(claude_exe)

    return "claude.cmd"


DEFAULT_CLAUDE_BIN = default_claude_bin()


def default_codex_bin() -> str:
    """실행할 codex 바이너리 경로를 확정한다.

    "codex" 문자열을 그대로 subprocess에 넘기면 Windows CreateProcess가 확장자 없는 이름에
    .exe만 붙여 찾으므로, npm이 설치한 codex.cmd를 건너뛰고 PATH 뒤쪽의 다른 codex.exe를
    실행할 수 있다. 실제로 구버전(0.133.0-alpha.1)이 잡혀 gpt-5.6-sol이 400으로 거절됐다
    (2026-07-15 run ch8c0716). shell은 0.144.3을 타는데 Python만 구버전을 타서, 같은 명령을
    터미널에서 돌리면 성공해 원인이 드러나지 않았다. shutil.which로 shell과 같은 해석을 쓴다.
    """
    if sys.platform != "win32":
        return "codex"

    return shutil.which("codex") or "codex"


DEFAULT_CODEX_BIN = default_codex_bin()

AGENT_PLANNER = "planner"
AGENT_ASSET_GENERATOR = "asset_generator"
AGENT_BUILDER = "builder"
AGENT_DESIGN_REVIEW = "design_review"
AGENT_DESIGN_REFINE = "design_refine"
AGENT_CONTENT_CRITIQUE = "content_critique"
AGENT_CONTENT_EVAL = "content_eval"
AGENT_CONTENT_REFINE = "content_refine"

AGENT_MODELS = {
    AGENT_PLANNER: MODEL_GPT_5_6_SOL,
    AGENT_ASSET_GENERATOR: MODEL_GPT_5_6_SOL,
    AGENT_BUILDER: MODEL_GPT_5_6_SOL,
    AGENT_DESIGN_REVIEW: MODEL_GPT_5_6_SOL,
    AGENT_DESIGN_REFINE: MODEL_GPT_5_6_SOL,
    AGENT_CONTENT_CRITIQUE: MODEL_GPT_5_6_SOL,
    AGENT_CONTENT_EVAL: MODEL_GPT_5_6_SOL,
    AGENT_CONTENT_REFINE: MODEL_GPT_5_6_SOL,
}
CLAUDE_HTML_AGENTS = (AGENT_BUILDER, AGENT_DESIGN_REFINE, AGENT_CONTENT_REFINE)
CLAUDE_MODEL_ALIASES = {MODEL_CLAUDE_OPUS, MODEL_CLAUDE_SONNET}

FINAL_CHECKED_RULES = ["schema", "brief_hash", "min_total", "min_axis"]
DEFAULT_ASSET_BATCH_SIZE = 3
DEFAULT_ASSET_PARALLELISM = 15
DEFAULT_ASSET_BUDGET = 9
DEFAULT_CONTENT_MAX_ITERATIONS = 5
MAX_ASSET_REVISION_REQUESTS = 6
DEFAULT_TIMEOUT_SECONDS = 2400
# design_refine은 10만 자 규모의 HTML을 통째로 다시 쓰므로 다른 stage보다 훨씬 오래 걸린다.
# 실제로 1200초에서 TimeoutError가 났다(2026-07-15 run ch8a0715 iter003).
DEFAULT_DESIGN_REFINE_TIMEOUT_SECONDS = 2400
# design_review도 같은 HTML 전문과 asset 이미지를 모두 읽으므로 무겁다.
# 실제로 1200초에서 TimeoutError가 났다(2026-07-15 run ch8c0717 iter002).
DEFAULT_DESIGN_REVIEW_TIMEOUT_SECONDS = 2400
DEFAULT_BUILDER_HTML_PATH = "output/index.html"
DEBUG_DESIGN_REFINE_HTML_PATH = "output/refine.html"


def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"


def format_running_duration(seconds: float) -> str:
    return f"{int(seconds)}s"


def format_score(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return "n/a"


def display_model(model: str | None) -> str:
    return model or "codex-cli-default"


def display_agent_runtime(provider: str, model: str | None) -> str:
    return f"provider={provider} model={display_model(model)}"


def summarize_errors(errors: list[object], limit: int = 3) -> str:
    if not errors:
        return ""
    visible_errors = [str(error) for error in errors[:limit]]
    if len(errors) > limit:
        visible_errors.append(f"... +{len(errors) - limit} more")
    return "; ".join(visible_errors)


class ProgressReporter:
    def __init__(self, stream=sys.stderr, refresh_seconds: float = 1.0) -> None:
        self.stream = stream
        self.refresh_seconds = refresh_seconds
        self.interactive = bool(stream.isatty())
        self._lock = threading.Lock()
        self._last_live_length = 0

    def line(self, message: str) -> None:
        with self._lock:
            self.stream.write(f"[{self._timestamp()}] {message}\n")
            self.stream.flush()

    @contextmanager
    def step(self, label: str, live: bool = False):
        start = time.perf_counter()
        live_line = _LiveProgressLine(self, label, start) if live and self.interactive else None
        if live_line:
            live_line.start()
        else:
            self.line(f"{label} start")

        try:
            yield
        except Exception as exc:
            elapsed = time.perf_counter() - start
            message = f"{label} ERROR {format_duration(elapsed)} error={type(exc).__name__}"
            if live_line:
                live_line.finish(message)
            else:
                self.line(message)
            raise
        else:
            elapsed = time.perf_counter() - start
            message = f"{label} done {format_duration(elapsed)}"
            if live_line:
                live_line.finish(message)
            else:
                self.line(message)

    def validation(self, label: str, result: dict, extra: str = "") -> None:
        if result["status"] == "PASS":
            return
        suffix = f" {extra}" if extra else ""
        error_summary = summarize_errors(result.get("errors", []))
        errors = f" errors={error_summary}" if error_summary else ""
        self.line(f"{label} {result['status']}{suffix}{errors}")

    def _write_live(self, message: str) -> None:
        with self._lock:
            padded = message.ljust(self._last_live_length)
            self.stream.write(f"\r{padded}")
            self.stream.flush()
            self._last_live_length = len(message)

    def _finish_live(self, message: str) -> None:
        with self._lock:
            padded = message.ljust(self._last_live_length)
            self.stream.write(f"\r{padded}\n")
            self.stream.flush()
            self._last_live_length = 0

    def _timestamp(self) -> str:
        return datetime.now(KST).strftime("%H:%M:%S")


class _LiveProgressLine:
    def __init__(self, reporter: ProgressReporter, label: str, started_at: float) -> None:
        self.reporter = reporter
        self.label = label
        self.started_at = started_at
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._write()
        self._thread.start()

    def finish(self, message: str) -> None:
        self._stop.set()
        self._thread.join()
        self.reporter._finish_live(f"[{self.reporter._timestamp()}] {message}")

    def _run(self) -> None:
        while not self._stop.wait(self.reporter.refresh_seconds):
            self._write()

    def _write(self) -> None:
        elapsed = time.perf_counter() - self.started_at
        self.reporter._write_live(
            f"[{self.reporter._timestamp()}] {self.label} running {format_running_duration(elapsed)}"
        )


@dataclass(frozen=True)
class RunContext:
    brief_hash: str
    iteration: str
    runs_dir: Path
    run_id: str

    @classmethod
    def create(cls, brief_hash: str, iteration: str, runs_dir: Path, run_id: str | None = None) -> "RunContext":
        today = datetime.now(KST).date().isoformat()
        return cls(
            brief_hash=brief_hash,
            iteration=iteration,
            runs_dir=runs_dir.resolve(),
            run_id=run_id or f"{today}_{brief_hash}",
        )

    @property
    def run_dir(self) -> Path:
        return self.runs_dir / self.run_id

    @property
    def iter_dir(self) -> Path:
        return self.run_dir / f"iter_{self.iteration}"

    @property
    def copied_input_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_input.json"

    @property
    def planner_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_planner.json"

    @property
    def planner_validation_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_planner.validation.json"

    @property
    def asset_generator_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_asset_generator.json"

    @property
    def asset_generator_validation_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_asset_generator.validation.json"

    @property
    def builder_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_builder.json"

    @property
    def builder_validation_path(self) -> Path:
        return self.run_dir / f"{self.brief_hash}_builder.validation.json"

    @property
    def design_review_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_design_review.json"

    @property
    def design_review_validation_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_design_review.validation.json"

    @property
    def design_refine_builder_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_design_refine_builder.json"

    @property
    def design_refine_builder_validation_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_design_refine_builder.validation.json"

    @property
    def content_critique_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_content_critique.json"

    @property
    def content_critique_validation_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_content_critique.validation.json"

    @property
    def content_eval_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_content_eval.json"

    @property
    def content_eval_validation_path(self) -> Path:
        return self.iter_dir / f"{self.brief_hash}_iter-{self.iteration}_content_eval.validation.json"

    @property
    def output_dir(self) -> Path:
        return self.run_dir / "output"

    @property
    def html_path(self) -> Path:
        return self.output_dir / "index.html"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def create_run_context(args: argparse.Namespace, brief_hash: str, iteration: str) -> RunContext:
    return RunContext.create(
        brief_hash=brief_hash,
        iteration=iteration,
        runs_dir=args.runs_dir,
        run_id=getattr(args, "run_id", None),
    )


def write_json(path: Path, data: dict, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_builder_output_schema(expected_html_path: str) -> dict:
    schema = load_json(BUILDER_OUTPUT_SCHEMA_PATH)
    html_schema = schema["properties"]["html_path"]
    html_schema["const"] = expected_html_path
    html_schema["description"] = f"run 디렉토리 기준 단일 HTML 저장 경로: {expected_html_path}"
    return schema


def write_builder_output_schema(path: Path, expected_html_path: str) -> None:
    write_json(path, build_builder_output_schema(expected_html_path), overwrite=True)


def validate_builder_output_file(file_path: Path, expected_html_path: str) -> dict:
    try:
        data = load_json(file_path)
    except ValueError as exc:
        return {
            "artifact": "builder_output",
            "checked_file": str(file_path),
            "status": "ERROR",
            "errors": [str(exc)],
        }

    errors = validate_schema(data, build_builder_output_schema(expected_html_path))
    return {
        "artifact": "builder_output",
        "checked_file": str(file_path),
        "status": "REJECT" if errors else "PASS",
        "errors": errors,
    }


def load_rubric(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"expected rubric YAML object: {path}")
    return data


def copy_input(source: Path, destination: Path, overwrite: bool = False) -> None:
    if source.resolve() == destination.resolve():
        return
    if destination.exists() and not overwrite:
        current = destination.read_text(encoding="utf-8")
        incoming = source.read_text(encoding="utf-8")
        if current == incoming:
            return
        raise FileExistsError(f"input file already exists with different content: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def ensure_pass(result: dict, result_path: Path | None = None) -> None:
    if result["status"] == "PASS":
        return
    if result_path:
        write_result(result, result_path)
    raise RuntimeError(json.dumps(result, ensure_ascii=False, indent=2))


def write_failed(
    run_dir: Path,
    brief_hash: str,
    run_id: str,
    stage: str,
    error: Exception,
    lineage: dict[str, str],
    config: dict[str, object],
) -> Path:
    failed_path = run_dir / f"{brief_hash}_failed.json"
    payload = {
        "brief_hash": brief_hash,
        "run_id": run_id,
        "failed_at": now_iso(),
        "stage": stage,
        "error_type": type(error).__name__,
        "message": str(error),
        "config": config,
        "lineage": lineage,
    }
    write_json(failed_path, payload, overwrite=True)
    return failed_path


def now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def relative_to_run(path: Path, run_dir: Path) -> str:
    try:
        return path.relative_to(run_dir).as_posix()
    except ValueError:
        return str(path)


def next_iteration(iteration: str) -> str:
    return f"{int(iteration) + 1:03d}"


def run_planner_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    stage = "input_validate"
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation(stage, input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    lineage = {
        "input": str(context.copied_input_path),
        "planner": str(context.planner_path),
    }
    config = {
        "codex_bin": args.codex_bin,
        "codex_access": "dangerously-bypass-approvals-and-sandbox",
        "agent_models": resolve_agent_models(args),
        "timeout_seconds": args.timeout_seconds,
        "mode": "planner_only",
    }
    progress.line(f"planner-only start brief={brief_hash} run_id={context.run_id}")

    try:
        stage = "prepare"
        copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)

        with tempfile.TemporaryDirectory(prefix="content-harness-planner-") as temp_dir:
            temp_planner_output_path = Path(temp_dir) / "planner-output.json"

            stage = "planner"
            with progress.step(
                f"planner model={display_model(config['agent_models'][AGENT_PLANNER])}",
                live=True,
            ):
                plan(
                    input_path=input_path,
                    output_path=temp_planner_output_path,
                    codex_bin=args.codex_bin,
                    model=config["agent_models"][AGENT_PLANNER],
                    timeout_seconds=args.timeout_seconds,
                )

            stage = "planner_output_validate"
            planner_result = validate_file(temp_planner_output_path, artifact="planner_output")
            progress.validation("planner_output_validate", planner_result)
            ensure_pass(planner_result, context.planner_validation_path)
            planner_output = load_json(temp_planner_output_path)

        stage = "planner_write"
        write_json(context.planner_path, planner_output, overwrite=args.overwrite)
        progress.line(f"planner-only PASS total_elapsed={format_duration(time.perf_counter() - started_at)}")
        return {
            "status": "PASS",
            "run_id": context.run_id,
            "input": str(context.copied_input_path),
            "planner": str(context.planner_path),
        }
    except Exception as exc:
        progress.line(
            f"planner-only ERROR stage={stage} total_elapsed={format_duration(time.perf_counter() - started_at)} "
            f"error={type(exc).__name__}"
        )
        failed_path = write_failed(context.run_dir, brief_hash, context.run_id, stage, exc, lineage, config)
        progress.line(f"planner-only failed artifact={failed_path}")
        raise RuntimeError(f"planner-only failed at {stage}; wrote {failed_path}") from exc


def split_items(items: list[dict], max_size: int) -> list[list[dict]]:
    return [items[index : index + max_size] for index in range(0, len(items), max_size)]


def build_asset_batches(planner_output: dict, max_batch_size: int) -> list[list[dict]]:
    asset_plan = planner_output.get("asset_plan", [])
    if not isinstance(asset_plan, list):
        raise ValueError("planner output asset_plan must be an array")
    if max_batch_size < 1:
        raise ValueError("--asset-batch-size must be at least 1")

    assets_by_id: dict[str, dict] = {}
    for asset in asset_plan:
        if not isinstance(asset, dict) or not isinstance(asset.get("id"), str):
            raise ValueError("each asset_plan entry must include a string id")
        assets_by_id[asset["id"]] = asset

    batches: list[list[dict]] = []
    consumed_ids: set[str] = set()
    asset_groups = planner_output.get("asset_groups", [])
    if not isinstance(asset_groups, list):
        raise ValueError("planner output asset_groups must be an array")

    for group in asset_groups:
        if not isinstance(group, dict):
            raise ValueError("each asset_groups entry must be an object")
        group_assets: list[dict] = []
        for asset_id in group.get("asset_ids", []):
            if asset_id not in assets_by_id:
                raise ValueError(f"asset_groups references unknown asset id: {asset_id}")
            if asset_id in consumed_ids:
                continue
            group_assets.append(assets_by_id[asset_id])
            consumed_ids.add(asset_id)
        batches.extend(split_items(group_assets, max_batch_size))

    remaining_assets = [
        asset for asset in asset_plan if isinstance(asset, dict) and asset.get("id") not in consumed_ids
    ]
    batches.extend(split_items(remaining_assets, max_batch_size))
    return [batch for batch in batches if batch]


def attach_identity_context(planner_output: dict, run_dir: Path) -> dict:
    """캐릭터별 기준 포즈와 형제 포즈를 planner_output에 붙인다.

    batch가 asset 하나로 쪼개지면 asset_plan에서 형제 포즈가 사라져, asset_generator의
    "batch 안의 asset끼리 캐릭터를 맞춘다"는 지시가 맞출 대상을 잃는다. 그 결과 포즈를 하나만
    재생성할 때마다 인물이 미묘하게 달라진다. identity_context는 asset_plan이 좁아져도 남으므로
    (build_batch_planner_output이 dict를 copy하기 때문에) 기준 포즈가 배치까지 따라간다.
    asset_plan에 넣지 않는 이유: 넣으면 형제 포즈까지 재생성돼 멀쩡한 asset을 덮어쓴다.
    """
    characters = planner_output.get("characters", [])
    asset_plan = planner_output.get("asset_plan", [])
    if not isinstance(characters, list) or not isinstance(asset_plan, list):
        return planner_output

    poses_by_character: dict[str, list[dict]] = {}
    for asset in asset_plan:
        if not isinstance(asset, dict):
            continue
        character_id = asset.get("character_id")
        if not isinstance(character_id, str) or not character_id:
            continue
        image_path = asset.get("intended_path", "")
        poses_by_character.setdefault(character_id, []).append(
            {
                "asset_id": asset.get("id"),
                "style_constraints": asset.get("style_constraints", ""),
                "image_path": image_path,
                "image_exists": bool(image_path) and (run_dir / image_path).exists(),
            }
        )

    identity_context = []
    for character in characters:
        if not isinstance(character, dict):
            continue
        character_id = character.get("id")
        if not isinstance(character_id, str):
            continue
        poses = poses_by_character.get(character_id, [])
        reference_asset_id = character.get("reference_asset_id", "")
        reference_image_path = ""
        for pose in poses:
            if pose["asset_id"] == reference_asset_id and pose["image_exists"]:
                reference_image_path = pose["image_path"]
                break
        if not reference_image_path:
            for pose in poses:
                if pose["image_exists"]:
                    reference_image_path = pose["image_path"]
                    break
        identity_context.append(
            {
                "character_id": character_id,
                "name": character.get("name", ""),
                "identity": character.get("identity", {}),
                "reference_asset_id": reference_asset_id,
                "reference_image_path": reference_image_path,
                "poses": poses,
            }
        )

    if not identity_context:
        return planner_output
    planner_output = planner_output.copy()
    planner_output["identity_context"] = identity_context
    return planner_output


def build_batch_planner_output(planner_output: dict, asset_batch: list[dict]) -> dict:
    batch_asset_ids = {asset["id"] for asset in asset_batch}
    batch_groups = []
    for group in planner_output.get("asset_groups", []):
        if not isinstance(group, dict):
            continue
        asset_ids = [asset_id for asset_id in group.get("asset_ids", []) if asset_id in batch_asset_ids]
        if asset_ids:
            batch_groups.append(
                {
                    "id": group["id"],
                    "asset_ids": asset_ids,
                    "grouping_reason": group["grouping_reason"],
                }
            )

    batch_output = planner_output.copy()
    batch_output["asset_plan"] = asset_batch
    batch_output["asset_groups"] = batch_groups
    return batch_output


def merge_asset_outputs(asset_outputs: list[dict], planner_output: dict) -> dict:
    asset_order = {
        asset["id"]: index
        for index, asset in enumerate(planner_output.get("asset_plan", []))
        if isinstance(asset, dict) and isinstance(asset.get("id"), str)
    }
    merged_assets = []
    for asset_output in asset_outputs:
        assets = asset_output.get("assets", [])
        if not isinstance(assets, list):
            raise ValueError("asset generator output assets must be an array")
        merged_assets.extend(assets)
    merged_assets.sort(key=lambda asset: asset_order.get(asset.get("id"), len(asset_order)))
    return {"assets": merged_assets}


def build_existing_asset_output(asset_plan: list[dict], run_dir: Path) -> tuple[dict, list[dict]]:
    existing_assets = []
    missing_assets = []
    for asset in asset_plan:
        if not isinstance(asset, dict):
            continue
        intended_path = asset.get("intended_path")
        if not isinstance(intended_path, str):
            missing_assets.append(asset)
            continue
        asset_path = run_dir / intended_path
        if not asset_path.exists():
            missing_assets.append(asset)
            continue
        existing_assets.append(
            {
                "id": asset["id"],
                "kind": "image",
                "path": intended_path,
                "status": "generated",
                "usage_section_ids": asset.get("usage_section_ids", []),
                "alt_text": asset.get("alt_text") or asset.get("purpose") or asset.get("prompt_brief") or asset["id"],
            }
        )
    return {"assets": existing_assets}, missing_assets


def validate_asset_output_matches_plan(asset_output: dict, asset_plan: list[dict]) -> list[str]:
    expected_ids = [asset.get("id") for asset in asset_plan if isinstance(asset, dict)]
    actual_ids = [asset.get("id") for asset in asset_output.get("assets", []) if isinstance(asset, dict)]
    errors = []

    missing_ids = [asset_id for asset_id in expected_ids if asset_id not in actual_ids]
    if missing_ids:
        errors.append(f"asset generator output missing asset ids: {', '.join(missing_ids)}")

    unexpected_ids = [asset_id for asset_id in actual_ids if asset_id not in expected_ids]
    if unexpected_ids:
        errors.append(f"asset generator output includes unexpected asset ids: {', '.join(unexpected_ids)}")

    duplicate_ids = sorted({asset_id for asset_id in actual_ids if actual_ids.count(asset_id) > 1})
    if duplicate_ids:
        errors.append(f"asset generator output includes duplicate asset ids: {', '.join(duplicate_ids)}")

    return errors


def generate_asset_batch(
    *,
    batch_index: int,
    asset_batch: list[dict],
    temp_dir: Path,
    input_path: Path,
    planner_output: dict,
    run_dir: Path,
    codex_bin: str,
    model: str | None,
    timeout_seconds: int,
) -> tuple[int, dict]:
    batch_planner_path = temp_dir / f"planner-batch-{batch_index:03d}.json"
    batch_output_path = temp_dir / f"asset-generator-batch-{batch_index:03d}.json"
    write_json(
        batch_planner_path,
        build_batch_planner_output(planner_output, asset_batch),
        overwrite=True,
    )
    generate_assets(
        input_path=input_path,
        planner_path=batch_planner_path,
        run_dir=run_dir,
        output_path=batch_output_path,
        codex_bin=codex_bin,
        model=model,
        timeout_seconds=timeout_seconds,
    )

    batch_result = validate_file(batch_output_path, artifact="asset_generator_output")
    ensure_pass(batch_result)
    return batch_index, load_json(batch_output_path)


def run_asset_generator_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    stage = "input_validate"
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation(stage, input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    lineage = {
        "input": str(context.copied_input_path),
        "planner": str(context.planner_path),
        "asset_generator": str(context.asset_generator_path),
    }
    config = {
        "codex_bin": args.codex_bin,
        "codex_access": "dangerously-bypass-approvals-and-sandbox",
        "agent_models": resolve_agent_models(args),
        "timeout_seconds": args.timeout_seconds,
        "asset_batch_size": args.asset_batch_size,
        "asset_parallelism": args.asset_parallelism,
        "asset_generator_missing_only": args.asset_generator_missing_only,
        "mode": "asset_generator_only",
    }
    progress.line(f"asset-generator-only start brief={brief_hash} run_id={context.run_id}")

    try:
        stage = "prepare"
        copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
        if not context.planner_path.exists():
            raise FileNotFoundError(f"planner output not found: {context.planner_path}")

        stage = "planner_output_validate"
        planner_result = validate_file(context.planner_path, artifact="planner_output")
        progress.validation("planner_output_validate", planner_result)
        ensure_pass(planner_result, context.planner_validation_path)
        planner_output = load_json(context.planner_path)
        asset_plan = planner_output.get("asset_plan", [])
        if not asset_plan:
            progress.line("asset-generator-only SKIPPED no asset_plan")
            return {
                "status": "SKIPPED",
                "run_id": context.run_id,
                "reason": "no asset_plan",
                "planner": str(context.planner_path),
            }

        context.output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="content-harness-assets-") as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_asset_output_path = Path(temp_dir) / "asset-generator-output.json"

            stage = "asset_generator"
            existing_asset_output = {"assets": []}
            assets_to_generate = asset_plan
            # 좁히기 전에 붙여야 형제 포즈와 기준 이미지가 살아남는다.
            planner_output = attach_identity_context(planner_output, context.run_dir)
            generation_planner_output = planner_output
            if args.asset_generator_missing_only:
                existing_asset_output, assets_to_generate = build_existing_asset_output(asset_plan, context.run_dir)
                generation_planner_output = build_batch_planner_output(planner_output, assets_to_generate)
                progress.line(
                    "asset_generator missing_only "
                    f"existing={len(existing_asset_output['assets'])} missing={len(assets_to_generate)}"
                )

            if assets_to_generate:
                asset_batches = build_asset_batches(generation_planner_output, args.asset_batch_size)
                worker_count = min(args.asset_parallelism, len(asset_batches))
                progress.line(
                    "asset_generator batches="
                    f"{len(asset_batches)} batch_size={args.asset_batch_size} parallelism={worker_count} "
                    f"model={display_model(config['agent_models'][AGENT_ASSET_GENERATOR])}"
                )
                with progress.step("asset_generator parallel", live=False):
                    batch_outputs: list[dict | None] = [None] * len(asset_batches)
                    with ThreadPoolExecutor(max_workers=worker_count) as executor:
                        futures = {
                            executor.submit(
                                generate_asset_batch,
                                batch_index=index,
                                asset_batch=asset_batch,
                                temp_dir=temp_dir_path,
                                input_path=input_path,
                                planner_output=generation_planner_output,
                                run_dir=context.run_dir,
                                codex_bin=args.codex_bin,
                                model=config["agent_models"][AGENT_ASSET_GENERATOR],
                                timeout_seconds=args.timeout_seconds,
                            ): index
                            for index, asset_batch in enumerate(asset_batches, start=1)
                        }
                        for future in as_completed(futures):
                            batch_index, batch_output = future.result()
                            batch_outputs[batch_index - 1] = batch_output
                            progress.line(f"asset_generator batch {batch_index:03d}/{len(asset_batches):03d} PASS")

                    asset_output = merge_asset_outputs(
                        [existing_asset_output]
                        + [batch_output for batch_output in batch_outputs if batch_output is not None],
                        planner_output,
                    )
                    write_json(temp_asset_output_path, asset_output, overwrite=True)
            else:
                asset_output = merge_asset_outputs([existing_asset_output], planner_output)
                write_json(temp_asset_output_path, asset_output, overwrite=True)
                progress.line("asset_generator missing_only SKIPPED all planned asset files already exist")

            stage = "asset_generator_output_validate"
            asset_result = validate_file(temp_asset_output_path, artifact="asset_generator_output")
            progress.validation("asset_generator_output_validate", asset_result)
            ensure_pass(asset_result, context.asset_generator_validation_path)
            asset_output = load_json(temp_asset_output_path)

        stage = "asset_plan_match_validate"
        asset_plan_errors = validate_asset_output_matches_plan(asset_output, asset_plan)
        if asset_plan_errors:
            raise ValueError("; ".join(asset_plan_errors))

        stage = "asset_files_validate"
        asset_file_errors = validate_asset_files(context.run_dir, asset_output)
        if asset_file_errors:
            raise FileNotFoundError("; ".join(asset_file_errors))

        stage = "asset_generator_write"
        write_json(context.asset_generator_path, asset_output, overwrite=args.overwrite)
        progress.line(f"asset-generator-only PASS total_elapsed={format_duration(time.perf_counter() - started_at)}")
        return {
            "status": "PASS",
            "run_id": context.run_id,
            "input": str(context.copied_input_path),
            "planner": str(context.planner_path),
            "asset_generator": str(context.asset_generator_path),
            "output": str(context.output_dir),
        }
    except Exception as exc:
        progress.line(
            f"asset-generator-only ERROR stage={stage} total_elapsed={format_duration(time.perf_counter() - started_at)} "
            f"error={type(exc).__name__}"
        )
        failed_path = write_failed(context.run_dir, brief_hash, context.run_id, stage, exc, lineage, config)
        progress.line(f"asset-generator-only failed artifact={failed_path}")
        raise RuntimeError(f"asset-generator-only failed at {stage}; wrote {failed_path}") from exc


def run_asset_generator_for_asset_ids(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    context: RunContext,
    asset_ids: list[str],
) -> dict:
    requested_ids = {asset_id for asset_id in asset_ids if isinstance(asset_id, str)}
    planner_output = load_json(context.planner_path)
    asset_plan = planner_output.get("asset_plan", [])
    if not isinstance(asset_plan, list):
        raise ValueError("planner output asset_plan must be an array")

    planned_ids = {asset.get("id") for asset in asset_plan if isinstance(asset, dict)}
    target_ids = requested_ids & planned_ids
    if not target_ids:
        progress.line("asset_revision asset_generator SKIPPED no planned asset ids to generate")
        return {
            "status": "SKIPPED",
            "run_id": context.run_id,
            "asset_generator": str(context.asset_generator_path),
        }

    target_assets = [
        asset
        for asset in asset_plan
        if isinstance(asset, dict) and asset.get("id") in target_ids
    ]
    if context.asset_generator_path.exists():
        previous_asset_output = load_json(context.asset_generator_path)
        preserved_assets = [
            asset
            for asset in previous_asset_output.get("assets", [])
            if isinstance(asset, dict)
            and asset.get("id") in planned_ids
            and asset.get("id") not in target_ids
        ]
        preserved_asset_output = {"assets": preserved_assets}
    else:
        non_target_assets = [
            asset
            for asset in asset_plan
            if isinstance(asset, dict) and asset.get("id") not in target_ids
        ]
        preserved_asset_output, _ = build_existing_asset_output(non_target_assets, context.run_dir)

    with tempfile.TemporaryDirectory(prefix="content-harness-asset-revision-") as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_asset_output_path = temp_dir_path / "asset-generator-output.json"
        # 좁히기 전에 붙여야 형제 포즈와 기준 이미지가 살아남는다.
        planner_output = attach_identity_context(planner_output, context.run_dir)
        generation_planner_output = build_batch_planner_output(planner_output, target_assets)
        asset_batches = build_asset_batches(generation_planner_output, args.asset_batch_size)
        worker_count = min(args.asset_parallelism, len(asset_batches))
        progress.line(
            "asset_revision asset_generator ids="
            f"{','.join(asset['id'] for asset in target_assets)} batches={len(asset_batches)} "
            f"batch_size={args.asset_batch_size} parallelism={worker_count} "
            f"model={display_model(resolve_agent_models(args)[AGENT_ASSET_GENERATOR])}"
        )
        with progress.step("asset_revision asset_generator parallel", live=False):
            batch_outputs: list[dict | None] = [None] * len(asset_batches)
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = {
                    executor.submit(
                        generate_asset_batch,
                        batch_index=index,
                        asset_batch=asset_batch,
                        temp_dir=temp_dir_path,
                        input_path=args.input.resolve(),
                        planner_output=generation_planner_output,
                        run_dir=context.run_dir,
                        codex_bin=args.codex_bin,
                        model=resolve_agent_models(args)[AGENT_ASSET_GENERATOR],
                        timeout_seconds=args.timeout_seconds,
                    ): index
                    for index, asset_batch in enumerate(asset_batches, start=1)
                }
                for future in as_completed(futures):
                    batch_index, batch_output = future.result()
                    batch_outputs[batch_index - 1] = batch_output
                    progress.line(f"asset_revision asset_generator batch {batch_index:03d}/{len(asset_batches):03d} PASS")

            asset_output = merge_asset_outputs(
                [preserved_asset_output]
                + [batch_output for batch_output in batch_outputs if batch_output is not None],
                planner_output,
            )
            write_json(temp_asset_output_path, asset_output, overwrite=True)

        asset_result = validate_file(temp_asset_output_path, artifact="asset_generator_output")
        progress.validation("asset_revision asset_generator_output_validate", asset_result)
        ensure_pass(asset_result, context.asset_generator_validation_path)
        asset_output = load_json(temp_asset_output_path)

    asset_plan_errors = validate_asset_output_matches_plan(asset_output, asset_plan)
    if asset_plan_errors:
        raise ValueError("; ".join(asset_plan_errors))

    asset_file_errors = validate_asset_files(context.run_dir, asset_output)
    if asset_file_errors:
        raise FileNotFoundError("; ".join(asset_file_errors))

    write_json(context.asset_generator_path, asset_output, overwrite=True)
    return {
        "status": "PASS",
        "run_id": context.run_id,
        "asset_generator": str(context.asset_generator_path),
        "output": str(context.output_dir),
    }


def run_builder_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    stage = "input_validate"
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation(stage, input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    lineage = {
        "input": str(context.copied_input_path),
        "planner": str(context.planner_path),
        "asset_generator": str(context.asset_generator_path),
        "builder": str(context.builder_path),
        "html": str(context.html_path),
    }
    config = {
        "codex_bin": args.codex_bin,
        "claude_bin": args.claude_bin,
        "codex_access": "dangerously-bypass-approvals-and-sandbox",
        "agent_models": resolve_agent_models(args),
        "agent_providers": resolve_agent_providers(args),
        "timeout_seconds": args.timeout_seconds,
        "mode": "builder_only",
    }
    progress.line(f"builder-only start brief={brief_hash} run_id={context.run_id}")

    try:
        stage = "prepare"
        copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
        if not context.planner_path.exists():
            raise FileNotFoundError(f"planner output not found: {context.planner_path}")

        stage = "planner_output_validate"
        planner_result = validate_file(context.planner_path, artifact="planner_output")
        progress.validation("planner_output_validate", planner_result)
        ensure_pass(planner_result, context.planner_validation_path)
        planner_output = load_json(context.planner_path)
        asset_generator_path: Path | None = None
        if planner_output.get("asset_plan"):
            if not context.asset_generator_path.exists():
                raise FileNotFoundError(f"asset generator output not found: {context.asset_generator_path}")
            asset_generator_path = context.asset_generator_path

        context.output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="content-harness-builder-") as temp_dir:
            temp_builder_output_path = Path(temp_dir) / "builder-output.json"

            stage = "builder"
            with progress.step(
                "builder runtime="
                f"{display_agent_runtime(config['agent_providers'][AGENT_BUILDER], config['agent_models'][AGENT_BUILDER])}",
                live=True,
            ):
                build_html(
                    input_path=input_path,
                    planner_path=context.planner_path,
                    asset_generator_path=asset_generator_path,
                    run_dir=context.run_dir,
                    output_path=temp_builder_output_path,
                    codex_bin=args.codex_bin,
                    claude_bin=args.claude_bin,
                    llm_provider=config["agent_providers"][AGENT_BUILDER],
                    model=config["agent_models"][AGENT_BUILDER],
                    timeout_seconds=args.timeout_seconds,
                )

            stage = "builder_output_validate"
            builder_result = validate_file(temp_builder_output_path, artifact="builder_output")
            progress.validation("builder_output_validate", builder_result)
            ensure_pass(builder_result, context.builder_validation_path)
            builder_output = load_json(temp_builder_output_path)

        stage = "builder_files_validate"
        builder_file_errors = finalize_html_artifact(context.run_dir, builder_output, progress)
        if builder_file_errors:
            raise FileNotFoundError("; ".join(builder_file_errors))

        stage = "builder_write"
        write_json(context.builder_path, builder_output, overwrite=args.overwrite)
        progress.line(f"builder-only PASS total_elapsed={format_duration(time.perf_counter() - started_at)}")
        return {
            "status": "PASS",
            "run_id": context.run_id,
            "input": str(context.copied_input_path),
            "planner": str(context.planner_path),
            "asset_generator": str(context.asset_generator_path) if asset_generator_path else None,
            "builder": str(context.builder_path),
            "html": str(context.html_path),
            "output": str(context.output_dir),
        }
    except Exception as exc:
        progress.line(
            f"builder-only ERROR stage={stage} total_elapsed={format_duration(time.perf_counter() - started_at)} "
            f"error={type(exc).__name__}"
        )
        failed_path = write_failed(context.run_dir, brief_hash, context.run_id, stage, exc, lineage, config)
        progress.line(f"builder-only failed artifact={failed_path}")
        raise RuntimeError(f"builder-only failed at {stage}; wrote {failed_path}") from exc


def validate_asset_files(run_dir: Path, asset_output: dict) -> list[str]:
    errors = []
    assets = asset_output.get("assets", [])
    if not isinstance(assets, list):
        return ["assets must be an array"]
    for asset in assets:
        if not isinstance(asset, dict):
            errors.append("asset entry must be an object")
            continue
        path = asset.get("path")
        if not isinstance(path, str):
            errors.append("asset.path must be a string")
            continue
        resolved = (run_dir / path).resolve()
        try:
            resolved.relative_to(run_dir.resolve())
        except ValueError:
            errors.append(f"asset path escapes run directory: {path}")
            continue
        if not resolved.exists():
            errors.append(f"asset file missing: {path}")
    return errors


def finalize_html_artifact(
    run_dir: Path,
    builder_output: dict,
    progress=None,
    expected_html_path: str = DEFAULT_BUILDER_HTML_PATH,
    teacher_root: str = "",
) -> list[str]:
    """HTML을 쓴 stage 뒤에 항상 도는 마무리.

    두 가지를 하는데 성격이 반대다.

    - `output/common.*`는 **덮어쓴다.** 코드가 소유하므로 모델이 뭘 했든 원본으로 돌아간다.
      되돌릴 수 있으니 검증할 이유가 없다.
    - `index.html`은 **검증한다.** 모델이 소유하므로 되돌릴 수 없고, `<link>`가 빠지면
      컴포넌트가 통째로 없는 화면이 나온다.

    이 함수를 세 HTML stage(builder, design_refine, content_refine) 뒤에서 부른다.
    stage 쪽이 아니라 runner에 두는 이유는 runner만 전체 시퀀스를 알고,
    이미 같은 자리에서 산출물 파일 검증을 하고 있었기 때문이다.
    """
    bundle = emit_common(run_dir, teacher_root)
    if bundle["drifted"] and progress is not None:
        for item in bundle["drifted"]:
            # 게이트가 아니라 로그다. 같은 항목이 반복되면 컴포넌트가 부족하다는 신호다.
            progress.line(
                f"common-restored {item['file']} "
                f"({item['previous_chars']}→{item['restored_chars']} chars)"
            )

    errors = validate_builder_files(run_dir, builder_output, expected_html_path)
    html_path = builder_output.get("html_path")
    if html_path == expected_html_path:
        errors.extend(check_html_links(run_dir / html_path))
    return errors


def validate_builder_files(
    run_dir: Path,
    builder_output: dict,
    expected_html_path: str = DEFAULT_BUILDER_HTML_PATH,
) -> list[str]:
    errors = []
    html_path = builder_output.get("html_path")
    if html_path != expected_html_path:
        errors.append(f"html_path must be {expected_html_path}")
    else:
        resolved_html = (run_dir / html_path).resolve()
        try:
            resolved_html.relative_to(run_dir.resolve())
        except ValueError:
            errors.append(f"html path escapes run directory: {html_path}")
        if not resolved_html.exists():
            errors.append(f"html file missing: {html_path}")

    asset_paths = builder_output.get("asset_paths", [])
    if not isinstance(asset_paths, list):
        return errors + ["asset_paths must be an array"]
    for path in asset_paths:
        if not isinstance(path, str):
            errors.append("asset_paths entries must be strings")
            continue
        resolved = (run_dir / path).resolve()
        try:
            resolved.relative_to(run_dir.resolve())
        except ValueError:
            errors.append(f"asset path escapes run directory: {path}")
            continue
        if not resolved.exists():
            errors.append(f"asset file missing: {path}")
    return errors


def get_content_eval_status(content_eval_output: dict, rubric: dict) -> tuple[str, list[str]]:
    errors = []
    rubric_scores = content_eval_output.get("rubric_scores", {})
    scores = rubric_scores.get("scores", {}) if isinstance(rubric_scores, dict) else {}
    weighted_total = rubric_scores.get("weighted_total") if isinstance(rubric_scores, dict) else None
    thresholds = rubric.get("thresholds", {})
    min_total = thresholds.get("min_total")
    if isinstance(min_total, (int, float)) and isinstance(weighted_total, (int, float)) and weighted_total < min_total:
        errors.append(f"min_total: {weighted_total} < {min_total}")

    min_axis = thresholds.get("min_axis", {})
    if isinstance(min_axis, dict) and isinstance(scores, dict):
        for axis, minimum in min_axis.items():
            score = scores.get(axis)
            if isinstance(minimum, (int, float)) and isinstance(score, (int, float)) and score < minimum:
                errors.append(f"min_axis.{axis}: {score} < {minimum}")

    return ("REJECT" if errors else "PASS"), errors


def format_content_eval_scores(content_eval_output: dict, rubric: dict) -> str:
    rubric_scores = content_eval_output.get("rubric_scores", {})
    if not isinstance(rubric_scores, dict):
        return "total=n/a"
    total = rubric_scores.get("weighted_total")
    min_total = rubric.get("thresholds", {}).get("min_total", "n/a")
    scores = rubric_scores.get("scores", {})
    axes = ""
    if isinstance(scores, dict):
        axes = " axes=" + " ".join(f"{axis}:{format_score(score)}" for axis, score in scores.items())
    return f"total={format_score(total)}/5 min={format_score(min_total)}{axes}"


def resolve_asset_generator_path(context: RunContext, planner_output: dict) -> Path | None:
    if not planner_output.get("asset_plan"):
        return None
    if not context.asset_generator_path.exists():
        raise FileNotFoundError(f"asset generator output not found: {context.asset_generator_path}")
    return context.asset_generator_path


def has_asset_review_changes(asset_review_output: dict) -> bool:
    asset_review = asset_review_output.get("asset_review", {})
    if not isinstance(asset_review, dict):
        return False
    change_keys = ("remove_assets", "regenerate_assets", "new_asset_requests")
    return any(isinstance(asset_review.get(key), list) and bool(asset_review.get(key)) for key in change_keys)


def merge_asset_review_outputs(*review_outputs: dict) -> dict:
    """asset_review를 합치고 중복을 제거한 뒤 MAX_ASSET_REVISION_REQUESTS 상한을 적용한다.

    현재 asset_review를 내는 stage는 design_review 하나뿐이라 인자도 보통 하나지만,
    상한·중복 제거가 여기에 있으므로 단일 입력이어도 이 경로를 거친다.
    """
    merged_asset_review = {
        "overall_asset_fit": "Normalized asset review from design review.",
        "keep_assets": [],
        "reposition_assets": [],
        "remove_assets": [],
        "regenerate_assets": [],
        "new_asset_requests": [],
    }
    seen_asset_decisions: dict[str, set[str]] = {
        "keep_assets": set(),
        "reposition_assets": set(),
        "remove_assets": set(),
        "regenerate_assets": set(),
    }
    seen_new_assets: set[str] = set()
    summaries = []

    for review_output in review_outputs:
        asset_review = review_output.get("asset_review", {}) if isinstance(review_output, dict) else {}
        if not isinstance(asset_review, dict):
            continue
        summary = asset_review.get("overall_asset_fit")
        if isinstance(summary, str) and summary.strip():
            summaries.append(summary.strip())

        for key in ("keep_assets", "reposition_assets", "remove_assets"):
            items = asset_review.get(key, [])
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get("asset_id"), str):
                    continue
                asset_id = item["asset_id"]
                if asset_id in seen_asset_decisions[key]:
                    continue
                seen_asset_decisions[key].add(asset_id)
                merged_asset_review[key].append(item)

        regenerate_items = asset_review.get("regenerate_assets", [])
        if isinstance(regenerate_items, list):
            for item in regenerate_items:
                used_revision_slots = (
                    len(merged_asset_review["regenerate_assets"])
                    + len(merged_asset_review["new_asset_requests"])
                )
                if used_revision_slots >= MAX_ASSET_REVISION_REQUESTS:
                    break
                if not isinstance(item, dict) or not isinstance(item.get("asset_id"), str):
                    continue
                asset_id = item["asset_id"]
                if asset_id in seen_asset_decisions["regenerate_assets"]:
                    continue
                seen_asset_decisions["regenerate_assets"].add(asset_id)
                merged_asset_review["regenerate_assets"].append(item)

        remaining_slots = (
            MAX_ASSET_REVISION_REQUESTS
            - len(merged_asset_review["regenerate_assets"])
            - len(merged_asset_review["new_asset_requests"])
        )
        new_asset_items = asset_review.get("new_asset_requests", [])
        if isinstance(new_asset_items, list):
            for item in new_asset_items:
                if len(merged_asset_review["new_asset_requests"]) >= remaining_slots:
                    break
                if not isinstance(item, dict) or not isinstance(item.get("suggested_id"), str):
                    continue
                suggested_id = item["suggested_id"]
                if suggested_id in seen_new_assets:
                    continue
                seen_new_assets.add(suggested_id)
                merged_asset_review["new_asset_requests"].append(item)

    if summaries:
        merged_asset_review["overall_asset_fit"] = " / ".join(summaries)
    return {"asset_review": merged_asset_review}


def resolve_design_refine_timeout(args: argparse.Namespace) -> int:
    """design_refine에 적용할 timeout을 정한다.

    명시적으로 --design-refine-timeout-seconds를 주면 그 값을 쓴다.
    아니면 기본 2400과 전역 --timeout-seconds 중 큰 값을 쓴다. 전역을 2400보다 높게 올린
    사용자의 의도를 깎지 않으면서, 전역이 기본값(1200)일 때도 design_refine만 넉넉히 준다.
    """
    override = getattr(args, "design_refine_timeout_seconds", None)
    if override:
        return override
    return max(args.timeout_seconds, DEFAULT_DESIGN_REFINE_TIMEOUT_SECONDS)


def resolve_design_review_timeout(args: argparse.Namespace) -> int:
    """design_review에 적용할 timeout을 정한다.

    resolve_design_refine_timeout과 같은 규칙이다. 명시적 override가 있으면 그 값을,
    없으면 기본 2400과 전역 --timeout-seconds 중 큰 값을 쓴다.
    """
    override = getattr(args, "design_review_timeout_seconds", None)
    if override:
        return override
    return max(args.timeout_seconds, DEFAULT_DESIGN_REVIEW_TIMEOUT_SECONDS)


def ensure_asset_spec_defaults(asset: dict) -> dict:
    asset.setdefault("character_id", "")
    asset.setdefault("visual_role", asset.get("purpose", "Support the section's learning goal"))
    asset.setdefault("style_constraints", "Follow the shared art_direction exactly.")
    asset.setdefault("composition_notes", asset.get("prompt_brief", "Use a clear composition for the target section."))
    asset.setdefault("negative_prompt", "No embedded text, no mismatched visual style, no unrelated decoration.")
    return asset


# design_review는 asset 하나의 문제만 보고 재생성을 요청하므로, 채우지 않은 필드까지 통째로 대입하면
# planner가 정해둔 나머지 지시가 조용히 사라진다. 빈 값은 "이 필드는 그대로 두라"는 뜻으로 읽고 원본을 보존한다.
# character_id는 여기에 없다 — asset이 어느 캐릭터를 그리는지는 planner의 characters만 정한다.
ASSET_REGENERATION_PATCH_FIELDS = (
    ("prompt_brief", "revised_prompt_brief"),
    ("visual_role", "visual_role"),
    ("style_constraints", "style_constraints"),
    ("composition_notes", "composition_notes"),
    ("negative_prompt", "negative_prompt"),
    ("usage_section_ids", "usage_section_ids"),
)


def apply_asset_regeneration_patch(asset: dict, regeneration: dict) -> dict:
    for target_key, source_key in ASSET_REGENERATION_PATCH_FIELDS:
        value = regeneration.get(source_key)
        if isinstance(value, str) and value.strip():
            asset[target_key] = value
        elif isinstance(value, list) and value:
            asset[target_key] = value
    return asset


def make_unique_asset_id(candidate: str, used_ids: set[str]) -> str:
    if candidate not in used_ids:
        return candidate
    index = 2
    while f"{candidate}_{index}" in used_ids:
        index += 1
    return f"{candidate}_{index}"


def asset_ids_from_decisions(decisions: object) -> set[str]:
    if not isinstance(decisions, list):
        return set()
    ids = set()
    for decision in decisions:
        if isinstance(decision, dict) and isinstance(decision.get("asset_id"), str):
            ids.add(decision["asset_id"])
    return ids


def apply_asset_review_to_planner(planner_output: dict, asset_review_output: dict, iteration: str) -> tuple[dict, dict]:
    asset_review = asset_review_output.get("asset_review", {})
    if not isinstance(asset_review, dict):
        return planner_output, {"removed": [], "regenerated": [], "added": []}

    remove_ids = asset_ids_from_decisions(asset_review.get("remove_assets"))
    regenerate_items = asset_review.get("regenerate_assets", [])
    if not isinstance(regenerate_items, list):
        regenerate_items = []
    regenerate_items = regenerate_items[:MAX_ASSET_REVISION_REQUESTS]
    regenerate_by_id = {
        item["asset_id"]: item
        for item in regenerate_items
        if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
    }
    new_asset_requests = asset_review.get("new_asset_requests", [])
    if not isinstance(new_asset_requests, list):
        new_asset_requests = []
    remaining_revision_slots = max(0, MAX_ASSET_REVISION_REQUESTS - len(regenerate_by_id))
    new_asset_requests = new_asset_requests[:remaining_revision_slots]

    asset_plan = planner_output.get("asset_plan", [])
    if not isinstance(asset_plan, list):
        raise ValueError("planner output asset_plan must be an array")

    updated_asset_plan = []
    used_ids: set[str] = set()
    regenerated_ids = []
    for asset in asset_plan:
        if not isinstance(asset, dict):
            continue
        asset_id = asset.get("id")
        if not isinstance(asset_id, str):
            continue
        if asset_id in remove_ids:
            continue
        updated_asset = ensure_asset_spec_defaults(asset.copy())
        regeneration = regenerate_by_id.get(asset_id)
        if regeneration:
            apply_asset_regeneration_patch(updated_asset, regeneration)
            regenerated_ids.append(asset_id)
        updated_asset_plan.append(updated_asset)
        used_ids.add(asset_id)

    added_ids = []
    for request in new_asset_requests:
        if not isinstance(request, dict) or not isinstance(request.get("suggested_id"), str):
            continue
        asset_id = make_unique_asset_id(request["suggested_id"], used_ids)
        intended_path = request.get("intended_path")
        if asset_id != request["suggested_id"] or not isinstance(intended_path, str):
            intended_path = f"output/assets/{asset_id}.png"
        updated_asset_plan.append(
            {
                "id": asset_id,
                "kind": request.get("kind", "image"),
                "character_id": request.get("character_id", ""),
                "intended_path": intended_path,
                "purpose": request["purpose"],
                "prompt_brief": request["prompt_brief"],
                "visual_role": request["visual_role"],
                "style_constraints": request["style_constraints"],
                "composition_notes": request["composition_notes"],
                "negative_prompt": request["negative_prompt"],
                "usage_section_ids": request["usage_section_ids"],
            }
        )
        used_ids.add(asset_id)
        added_ids.append(asset_id)

    planner_output = planner_output.copy()
    planner_output["asset_plan"] = updated_asset_plan

    asset_ids_by_section: dict[str, list[str]] = {}
    for asset in updated_asset_plan:
        asset_id = asset.get("id")
        if not isinstance(asset_id, str):
            continue
        for section_id in asset.get("usage_section_ids", []):
            if isinstance(section_id, str):
                asset_ids_by_section.setdefault(section_id, []).append(asset_id)

    sections = planner_output.get("sections", [])
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, dict):
                continue
            current_ids = section.get("asset_ids", [])
            if not isinstance(current_ids, list):
                current_ids = []
            section_id = section.get("id")
            planned_ids = asset_ids_by_section.get(section_id, [])
            kept_ids = [
                asset_id
                for asset_id in current_ids
                if isinstance(asset_id, str) and asset_id in used_ids and asset_id in planned_ids
            ]
            for asset_id in planned_ids:
                if asset_id not in kept_ids:
                    kept_ids.append(asset_id)
            section["asset_ids"] = kept_ids

    revision_ids = regenerated_ids + added_ids
    asset_groups = planner_output.get("asset_groups", [])
    sanitized_groups = []
    if isinstance(asset_groups, list):
        for group in asset_groups:
            if not isinstance(group, dict):
                continue
            group_asset_ids = [
                asset_id
                for asset_id in group.get("asset_ids", [])
                if isinstance(asset_id, str) and asset_id not in remove_ids and asset_id in used_ids
            ]
            if group_asset_ids:
                updated_group = group.copy()
                updated_group["asset_ids"] = group_asset_ids
                sanitized_groups.append(updated_group)
    if revision_ids:
        group_id = make_unique_asset_id(f"asset_revision_{iteration}", {group.get("id") for group in sanitized_groups if isinstance(group, dict)})
        sanitized_groups.append(
            {
                "id": group_id,
                "asset_ids": revision_ids,
                "grouping_reason": "Content critique requested these assets together because they must align with the same revised visual direction.",
            }
        )
    planner_output["asset_groups"] = sanitized_groups

    return planner_output, {
        "removed": sorted(remove_ids),
        "regenerated": regenerated_ids,
        "added": added_ids,
    }


def run_asset_revision_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
    asset_review_output: dict,
) -> dict:
    planner_output = load_json(context.planner_path)
    updated_planner_output, summary = apply_asset_review_to_planner(
        planner_output,
        asset_review_output,
        context.iteration,
    )
    write_json(context.planner_path, updated_planner_output, overwrite=True)
    progress.line(
        f"iter {context.iteration} asset_revision planner updated "
        f"removed={len(summary['removed'])} regenerated={len(summary['regenerated'])} added={len(summary['added'])}"
    )
    asset_result = run_asset_generator_for_asset_ids(
        args=args,
        progress=progress,
        context=context,
        asset_ids=summary["regenerated"] + summary["added"],
    )
    # 여기서 design_refine을 부르지 않는다. 호출자가 design 축을 따로 태우므로
    # 여기서도 부르면 한 iteration에 design_refine이 두 번 돈다.
    # asset 변경을 HTML에 반영하는 것은 호출자의 design_refine이 담당한다
    # (asset 변경 후 builder 재빌드가 아니라 refine으로 잇는다는 결정은 유지된다).
    progress.line(f"iter {context.iteration} asset_revision PASS")
    return {
        "asset_revision": summary,
        "asset_generator": asset_result.get("asset_generator"),
    }


def run_design_review_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    context: RunContext,
) -> dict:
    planner_output = load_json(context.planner_path)
    asset_generator_path = resolve_asset_generator_path(context, planner_output)
    with tempfile.TemporaryDirectory(prefix="content-harness-design-review-") as temp_dir:
        temp_design_review_path = Path(temp_dir) / "design-review-output.json"
        with progress.step(
            f"iter {context.iteration} design_review model="
            f"{display_model(resolve_agent_models(args)[AGENT_DESIGN_REVIEW])}",
            live=True,
        ):
            review_design(
                input_path=context.copied_input_path,
                planner_path=context.planner_path,
                asset_generator_path=asset_generator_path,
                builder_path=context.builder_path,
                html_path=context.html_path,
                run_dir=context.run_dir,
                iteration=context.iteration,
                output_path=temp_design_review_path,
                codex_bin=args.codex_bin,
                model=resolve_agent_models(args)[AGENT_DESIGN_REVIEW],
                timeout_seconds=resolve_design_review_timeout(args),
                asset_budget=getattr(args, "asset_budget", DEFAULT_ASSET_BUDGET),
            )

        design_review_result = validate_file(temp_design_review_path, artifact="design_review_output")
        progress.validation(f"iter {context.iteration} design_review_output_validate", design_review_result)
        ensure_pass(design_review_result, context.design_review_validation_path)
        design_review_output = load_json(temp_design_review_path)

    write_json(context.design_review_path, design_review_output, overwrite=args.overwrite)
    finding_count = len(design_review_output.get("priority_findings", []))
    progress.line(f"iter {context.iteration} design_review {design_review_output['status']} findings={finding_count}")
    return {
        "status": design_review_output["status"],
        "design_review": str(context.design_review_path),
        "priority_findings": design_review_output.get("priority_findings", []),
    }


def run_content_critique_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
    content_rubric: dict,
) -> dict:
    planner_output = load_json(context.planner_path)
    asset_generator_path = resolve_asset_generator_path(context, planner_output)
    with tempfile.TemporaryDirectory(prefix="content-harness-critique-") as temp_dir:
        temp_content_critique_path = Path(temp_dir) / "content-critique-output.json"
        progress.line(
            f"iter {context.iteration} content_critique model="
            f"{display_model(resolve_agent_models(args)[AGENT_CONTENT_CRITIQUE])} start"
        )
        critique_content(
            input_path=input_path,
            planner_path=context.planner_path,
            asset_generator_path=asset_generator_path,
            builder_path=context.builder_path,
            html_path=context.html_path,
            rubric=content_rubric,
            output_path=temp_content_critique_path,
            codex_bin=args.codex_bin,
            model=resolve_agent_models(args)[AGENT_CONTENT_CRITIQUE],
            timeout_seconds=args.timeout_seconds,
        )

        content_critique_result = validate_file(temp_content_critique_path, artifact="content_critique_output")
        progress.validation(f"iter {context.iteration} content_critique_output_validate", content_critique_result)
        ensure_pass(content_critique_result, context.content_critique_validation_path)
        content_critique_output = load_json(temp_content_critique_path)

    write_json(context.content_critique_path, content_critique_output, overwrite=args.overwrite)
    progress.line(f"iter {context.iteration} content_critique PASS")
    return {
        "content_critique": str(context.content_critique_path),
    }


def run_content_eval_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
    content_rubric: dict,
) -> dict:
    planner_output = load_json(context.planner_path)
    asset_generator_path = resolve_asset_generator_path(context, planner_output)
    with tempfile.TemporaryDirectory(prefix="content-harness-eval-") as temp_dir:
        temp_content_eval_path = Path(temp_dir) / "content-eval-output.json"
        progress.line(
            f"iter {context.iteration} content_eval model="
            f"{display_model(resolve_agent_models(args)[AGENT_CONTENT_EVAL])} start"
        )
        evaluate_content(
            planner_path=context.planner_path,
            asset_generator_path=asset_generator_path,
            builder_path=context.builder_path,
            html_path=context.html_path,
            rubric=content_rubric,
            output_path=temp_content_eval_path,
            codex_bin=args.codex_bin,
            model=resolve_agent_models(args)[AGENT_CONTENT_EVAL],
            timeout_seconds=args.timeout_seconds,
        )

        content_eval_result = validate_file(temp_content_eval_path, artifact="content_eval_output")
        progress.validation(f"iter {context.iteration} content_eval_output_validate", content_eval_result)
        ensure_pass(content_eval_result, context.content_eval_validation_path)
        content_eval_output = load_json(temp_content_eval_path)

    write_json(context.content_eval_path, content_eval_output, overwrite=args.overwrite)
    status, threshold_errors = get_content_eval_status(content_eval_output, content_rubric)
    score_summary = format_content_eval_scores(content_eval_output, content_rubric)
    errors = f" errors={summarize_errors(threshold_errors)}" if threshold_errors else ""
    progress.line(f"iter {context.iteration} content_eval {status} {score_summary}{errors}")
    return {
        "status": status,
        "content_eval": str(context.content_eval_path),
        "threshold_errors": threshold_errors,
    }


def run_content_review_set(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
    content_rubric: dict,
) -> tuple[dict, dict, dict]:
    with ThreadPoolExecutor(max_workers=3) as executor:
        design_review_future = executor.submit(
            run_design_review_stage,
            args=args,
            progress=progress,
            context=context,
        )
        critique_future = executor.submit(
            run_content_critique_stage,
            args=args,
            progress=progress,
            input_path=input_path,
            context=context,
            content_rubric=content_rubric,
        )
        eval_future = executor.submit(
            run_content_eval_stage,
            args=args,
            progress=progress,
            input_path=input_path,
            context=context,
            content_rubric=content_rubric,
        )
        design_review_result = design_review_future.result()
        critique_result = critique_future.result()
        eval_result = eval_future.result()
    return design_review_result, critique_result, eval_result


def run_content_refine_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
) -> dict:
    agent_models = resolve_agent_models(args)
    agent_providers = resolve_agent_providers(args)
    planner_output = load_json(context.planner_path)
    asset_generator_path = resolve_asset_generator_path(context, planner_output)
    with tempfile.TemporaryDirectory(prefix="content-harness-refine-") as temp_dir:
        temp_builder_output_path = Path(temp_dir) / "builder-output.json"
        with progress.step(
            f"iter {context.iteration} content_refine runtime="
            f"{display_agent_runtime(agent_providers[AGENT_CONTENT_REFINE], agent_models[AGENT_CONTENT_REFINE])}",
            live=True,
        ):
            refine_content(
                input_path=input_path,
                planner_path=context.planner_path,
                asset_generator_path=asset_generator_path,
                builder_path=context.builder_path,
                html_path=context.html_path,
                content_critique_path=context.content_critique_path,
                run_dir=context.run_dir,
                output_path=temp_builder_output_path,
                codex_bin=args.codex_bin,
                claude_bin=args.claude_bin,
                llm_provider=agent_providers[AGENT_CONTENT_REFINE],
                model=agent_models[AGENT_CONTENT_REFINE],
                timeout_seconds=args.timeout_seconds,
            )

        builder_result = validate_file(temp_builder_output_path, artifact="builder_output")
        progress.validation(f"iter {context.iteration} content_refine_builder_output_validate", builder_result)
        ensure_pass(builder_result, context.builder_validation_path)
        builder_output = load_json(temp_builder_output_path)

    builder_file_errors = finalize_html_artifact(context.run_dir, builder_output, progress)
    if builder_file_errors:
        raise FileNotFoundError("; ".join(builder_file_errors))

    write_json(context.builder_path, builder_output, overwrite=True)
    progress.line(f"iter {context.iteration} content_refine PASS")
    return {
        "builder": str(context.builder_path),
        "html": str(context.html_path),
        "output": str(context.output_dir),
    }


def run_design_refine_stage(
    *,
    args: argparse.Namespace,
    progress: ProgressReporter,
    input_path: Path,
    context: RunContext,
    target_html_path: str = DEFAULT_BUILDER_HTML_PATH,
    builder_output_path: Path | None = None,
    builder_validation_path: Path | None = None,
) -> dict:
    agent_models = resolve_agent_models(args)
    agent_providers = resolve_agent_providers(args)
    planner_output = load_json(context.planner_path)
    asset_generator_path = resolve_asset_generator_path(context, planner_output)
    builder_output_path = builder_output_path or context.builder_path
    builder_validation_path = builder_validation_path or context.builder_validation_path
    with tempfile.TemporaryDirectory(prefix="content-harness-design-refine-") as temp_dir:
        temp_builder_output_path = Path(temp_dir) / "builder-output.json"
        temp_builder_schema_path = Path(temp_dir) / "builder-output.schema.json"
        write_builder_output_schema(temp_builder_schema_path, target_html_path)
        with progress.step(
            f"iter {context.iteration} design_refine runtime="
            f"{display_agent_runtime(agent_providers[AGENT_DESIGN_REFINE], agent_models[AGENT_DESIGN_REFINE])}",
            live=True,
        ):
            refine_design(
                input_path=input_path,
                planner_path=context.planner_path,
                asset_generator_path=asset_generator_path,
                builder_path=context.builder_path,
                html_path=context.html_path,
                design_review_path=context.design_review_path,
                run_dir=context.run_dir,
                output_path=temp_builder_output_path,
                codex_bin=args.codex_bin,
                claude_bin=args.claude_bin,
                llm_provider=agent_providers[AGENT_DESIGN_REFINE],
                model=agent_models[AGENT_DESIGN_REFINE],
                timeout_seconds=resolve_design_refine_timeout(args),
                output_schema_path=temp_builder_schema_path,
                target_html_path=target_html_path,
            )

        builder_result = validate_builder_output_file(temp_builder_output_path, target_html_path)
        progress.validation(f"iter {context.iteration} design_refine_builder_output_validate", builder_result)
        ensure_pass(builder_result, builder_validation_path)
        builder_output = load_json(temp_builder_output_path)

    builder_file_errors = finalize_html_artifact(
        context.run_dir,
        builder_output,
        progress,
        expected_html_path=target_html_path,
    )
    if builder_file_errors:
        raise FileNotFoundError("; ".join(builder_file_errors))

    write_json(builder_output_path, builder_output, overwrite=True)
    progress.line(f"iter {context.iteration} design_refine PASS html={target_html_path}")
    return {
        "builder": str(builder_output_path),
        "html": str(context.run_dir / target_html_path),
        "output": str(context.output_dir),
    }


def run_content_critique_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation("input_validate", input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
    content_rubric = load_rubric(args.content_rubric.resolve())
    result = run_content_critique_stage(
        args=args,
        progress=progress,
        input_path=input_path,
        context=context,
        content_rubric=content_rubric,
    )
    progress.line(f"content-critique-only PASS total_elapsed={format_duration(time.perf_counter() - started_at)}")
    return {
        "status": "PASS",
        "run_id": context.run_id,
        **result,
    }


def run_design_review_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation("input_validate", input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
    if not context.builder_path.exists():
        raise FileNotFoundError(f"builder output not found: {context.builder_path}")
    if not context.html_path.exists():
        raise FileNotFoundError(f"HTML output not found: {context.html_path}")
    context.iter_dir.mkdir(parents=True, exist_ok=True)
    result = run_design_review_stage(
        args=args,
        progress=progress,
        context=context,
    )
    return {
        "status": result["status"],
        "run_id": context.run_id,
        "design_review": result["design_review"],
    }


def run_design_refine_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation("input_validate", input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
    if not context.builder_path.exists():
        raise FileNotFoundError(f"builder output not found: {context.builder_path}")
    if not context.html_path.exists():
        raise FileNotFoundError(f"HTML output not found: {context.html_path}")
    if not context.design_review_path.exists():
        raise FileNotFoundError(f"design review output not found: {context.design_review_path}")
    context.iter_dir.mkdir(parents=True, exist_ok=True)
    result = run_design_refine_stage(
        args=args,
        progress=progress,
        input_path=input_path,
        context=context,
        target_html_path=DEBUG_DESIGN_REFINE_HTML_PATH,
        builder_output_path=context.design_refine_builder_path,
        builder_validation_path=context.design_refine_builder_validation_path,
    )
    return {
        "status": "PASS",
        "run_id": context.run_id,
        "design_review": str(context.design_review_path),
        "builder": result["builder"],
        "html": result["html"],
        "output": result["output"],
    }


def run_content_eval_only(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation("input_validate", input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    config = {
        "codex_bin": args.codex_bin,
        "codex_access": "dangerously-bypass-approvals-and-sandbox",
        "agent_models": resolve_agent_models(args),
        "timeout_seconds": args.timeout_seconds,
        "mode": "content_eval_only",
        "content_rubric_path": str(args.content_rubric.resolve()),
    }
    lineage = {
        "input": str(context.copied_input_path),
        "planner": str(context.planner_path),
        "asset_generator": str(context.asset_generator_path),
        "builder": str(context.builder_path),
        "html": str(context.html_path),
        "content_eval": str(context.content_eval_path),
    }
    progress.line(f"content-eval-only start brief={brief_hash} run_id={context.run_id}")

    try:
        stage = "prepare"
        copy_input(input_path, context.copied_input_path, overwrite=args.overwrite)
        if not context.planner_path.exists():
            raise FileNotFoundError(f"planner output not found: {context.planner_path}")
        if not context.builder_path.exists():
            raise FileNotFoundError(f"builder output not found: {context.builder_path}")
        if not context.html_path.exists():
            raise FileNotFoundError(f"html not found: {context.html_path}")

        # planner를 검증하지 않으면 rendered_text가 없는 구형 planner로도 조용히 채점된다.
        # 그 경우 content_fidelity 체크리스트가 통째로 비어 "누락 0개 = 5점"이 나와 거짓 PASS가 된다.
        # 점수가 아니라 채점 기준이 사라진 것이므로, 여기서 schema로 막는다.
        stage = "planner_output_validate"
        planner_result = validate_file(context.planner_path, artifact="planner_output")
        progress.validation("planner_output_validate", planner_result)
        ensure_pass(planner_result, context.planner_validation_path)

        planner_output = load_json(context.planner_path)
        asset_generator_path: Path | None = None
        if planner_output.get("asset_plan"):
            if not context.asset_generator_path.exists():
                raise FileNotFoundError(f"asset generator output not found: {context.asset_generator_path}")
            asset_generator_path = context.asset_generator_path

        content_rubric = load_rubric(args.content_rubric.resolve())
        with tempfile.TemporaryDirectory(prefix="content-harness-eval-") as temp_dir:
            temp_content_eval_path = Path(temp_dir) / "content-eval-output.json"
            stage = "content_eval"
            with progress.step(
                f"content_eval model={display_model(config['agent_models'][AGENT_CONTENT_EVAL])}",
                live=True,
            ):
                evaluate_content(
                    planner_path=context.planner_path,
                    asset_generator_path=asset_generator_path,
                    builder_path=context.builder_path,
                    html_path=context.html_path,
                    rubric=content_rubric,
                    output_path=temp_content_eval_path,
                    codex_bin=args.codex_bin,
                    model=config["agent_models"][AGENT_CONTENT_EVAL],
                    timeout_seconds=args.timeout_seconds,
                )

            stage = "content_eval_output_validate"
            content_eval_result = validate_file(temp_content_eval_path, artifact="content_eval_output")
            progress.validation("content_eval_output_validate", content_eval_result)
            ensure_pass(content_eval_result, context.content_eval_validation_path)
            content_eval_output = load_json(temp_content_eval_path)

        stage = "content_eval_write"
        write_json(context.content_eval_path, content_eval_output, overwrite=args.overwrite)
        status, threshold_errors = get_content_eval_status(content_eval_output, content_rubric)
        score_summary = format_content_eval_scores(content_eval_output, content_rubric)
        errors = f" errors={summarize_errors(threshold_errors)}" if threshold_errors else ""
        progress.line(
            f"content-eval-only {status} {score_summary}{errors} "
            f"total_elapsed={format_duration(time.perf_counter() - started_at)}"
        )
        return {
            "status": status,
            "run_id": context.run_id,
            "content_eval": str(context.content_eval_path),
            "html": str(context.html_path),
            "threshold_errors": threshold_errors,
        }
    except Exception as exc:
        progress.line(
            f"content-eval-only ERROR stage={stage} total_elapsed={format_duration(time.perf_counter() - started_at)} "
            f"error={type(exc).__name__}"
        )
        failed_path = write_failed(context.run_dir, brief_hash, context.run_id, stage, exc, lineage, config)
        progress.line(f"content-eval-only failed artifact={failed_path}")
        raise RuntimeError(f"content-eval-only failed at {stage}; wrote {failed_path}") from exc


def run(args: argparse.Namespace) -> dict:
    progress = ProgressReporter()
    started_at = time.perf_counter()
    input_path = args.input.resolve()
    input_result = validate_file(input_path, artifact="input")
    progress.validation("input_validate", input_result)
    ensure_pass(input_result)

    input_data = load_json(input_path)
    brief_hash = input_data["brief_hash"]
    context = create_run_context(args, brief_hash, args.iteration)
    progress.line(
        "content run start "
        f"brief={brief_hash} run_id={context.run_id} "
        f"asset_batch_size={args.asset_batch_size} asset_parallelism={args.asset_parallelism} "
        f"timeout_seconds={args.timeout_seconds}"
    )

    if args.start_at == "planner":
        planner_result = run_planner_only(args)
    else:
        if not context.planner_path.exists():
            raise FileNotFoundError(f"planner output not found: {context.planner_path}")
        planner_validation = validate_file(context.planner_path, artifact="planner_output")
        progress.validation("planner_output_validate", planner_validation)
        ensure_pass(planner_validation, context.planner_validation_path)
        planner_result = {
            "status": "PASS",
            "run_id": context.run_id,
            "input": str(context.copied_input_path),
            "planner": str(context.planner_path),
        }

    if args.start_at in ("planner", "asset"):
        asset_result = run_asset_generator_only(args)
    else:
        planner_output = load_json(context.planner_path)
        asset_generator_path = resolve_asset_generator_path(context, planner_output)
        if asset_generator_path is None:
            asset_result = {
                "status": "SKIPPED",
                "run_id": context.run_id,
                "reason": "no asset_plan",
                "planner": str(context.planner_path),
            }
        else:
            asset_validation = validate_file(asset_generator_path, artifact="asset_generator_output")
            progress.validation("asset_generator_output_validate", asset_validation)
            ensure_pass(asset_validation, context.asset_generator_validation_path)
            asset_output = load_json(asset_generator_path)
            asset_file_errors = validate_asset_files(context.run_dir, asset_output)
            if asset_file_errors:
                raise FileNotFoundError("; ".join(asset_file_errors))
            asset_result = {
                "status": "PASS",
                "run_id": context.run_id,
                "asset_generator": str(asset_generator_path),
                "output": str(context.output_dir),
            }

    builder_result = run_builder_only(args)
    content_rubric = load_rubric(args.content_rubric.resolve())
    latest_design_review_result: dict = {}
    latest_critique_result: dict = {}
    latest_eval_result: dict = {}
    status = "REJECT"

    for iteration_number in range(1, args.content_max_iterations + 1):
        iteration = f"{iteration_number:03d}"
        context = create_run_context(args, brief_hash, iteration)
        context.iter_dir.mkdir(parents=True, exist_ok=True)
        progress.line(f"content quality loop iter {iteration}/{args.content_max_iterations:03d} start")

        latest_design_review_result, latest_critique_result, latest_eval_result = run_content_review_set(
            args=args,
            progress=progress,
            input_path=input_path,
            context=context,
            content_rubric=content_rubric,
        )
        design_status = latest_design_review_result.get("status", "REJECT")
        eval_status = latest_eval_result.get("status", "REJECT")
        status = "PASS" if design_status == "PASS" and eval_status == "PASS" else "REJECT"
        design_review_output = load_json(context.design_review_path)
        # asset 재생성/신규 요청은 design_review만 낸다. content_critique의 출력 계약
        # (content_critique_output.schema.json)에는 asset_review가 없고 additionalProperties도 막혀 있어
        # 여기에 넘겨봐야 항상 빈손이었다. 예산 상한과 중복 제거는 아래 merge가 그대로 담당한다.
        asset_review_output = merge_asset_review_outputs(design_review_output)
        asset_change_needed = has_asset_review_changes(asset_review_output)
        if status == "PASS" and not asset_change_needed:
            progress.line(
                f"content run PASS iteration={iteration} "
                f"total_elapsed={format_duration(time.perf_counter() - started_at)}"
            )
            break

        if iteration_number >= args.content_max_iterations:
            if asset_change_needed:
                status = "REJECT"
            progress.line(
                f"content run REJECT terminal_reason=max_content_iterations "
                f"last_iteration={iteration} total_elapsed={format_duration(time.perf_counter() - started_at)}"
            )
            break

        # design 축과 content 축은 독립이다. 예전에는 if/elif/else 한 줄로 묶여 있어
        # content_refine이 "design_review가 PASS일 때만" 도달하는 3순위 분기였고,
        # design_review가 REJECT인 동안에는 영원히 실행되지 않았다. 실제로 run
        # ch8c0716/ch8c0717은 10 iteration 전부 design REJECT라 content_refine이 0회 돌았고,
        # content_critique는 매 iter 생성만 되고 아무도 읽지 않았다.
        # 이제 각 축이 자기 게이트(design_review / content_eval)에만 반응한다.
        if asset_change_needed:
            revision_result = run_asset_revision_stage(
                args=args,
                progress=progress,
                input_path=input_path,
                context=context,
                asset_review_output=asset_review_output,
            )
            asset_result = {
                "status": "PASS",
                "asset_generator": revision_result.get("asset_generator"),
            }
            status = "REJECT"

        # design 축: asset이 바뀌었으면 HTML에 반영해야 하므로 함께 태운다.
        if asset_change_needed or design_status != "PASS":
            builder_result = run_design_refine_stage(
                args=args,
                progress=progress,
                input_path=input_path,
                context=context,
            )

        # content 축: design_refine이 HTML을 다시 썼을 수 있으므로 그 뒤에 순차로 돈다.
        # content_refine이 마지막인 이유는 더 보수적인 stage이기 때문이다(CSS·레이아웃을
        # 건드리지 않는다). 반대로 두면 design_refine의 통짜 재작성이 content 수정을 지운다.
        if eval_status != "PASS":
            builder_result = run_content_refine_stage(
                args=args,
                progress=progress,
                input_path=input_path,
                context=context,
            )

    progress.line(f"content run {status} total_elapsed={format_duration(time.perf_counter() - started_at)}")
    return {
        "status": status,
        "run_id": context.run_id,
        "input": planner_result.get("input"),
        "planner": planner_result.get("planner"),
        "asset_generator": asset_result.get("asset_generator"),
        "asset_status": asset_result.get("status"),
        "builder": builder_result.get("builder"),
        "design_review": latest_design_review_result.get("design_review"),
        "design_review_findings": latest_design_review_result.get("priority_findings", []),
        "content_critique": latest_critique_result.get("content_critique"),
        "content_eval": latest_eval_result.get("content_eval"),
        "threshold_errors": latest_eval_result.get("threshold_errors", []),
        "html": builder_result.get("html"),
        "output": builder_result.get("output"),
    }


def resolve_agent_models(args: argparse.Namespace) -> dict[str, str | None]:
    models = AGENT_MODELS.copy()
    if args.model:
        models[AGENT_PLANNER] = args.model
        models[AGENT_ASSET_GENERATOR] = args.model
        models[AGENT_BUILDER] = args.model
    if args.claude_html_stages:
        for agent in CLAUDE_HTML_AGENTS:
            models[agent] = args.claude_model
    if args.planner_model:
        models[AGENT_PLANNER] = args.planner_model
    if args.asset_generator_model:
        models[AGENT_ASSET_GENERATOR] = args.asset_generator_model
    if args.builder_model:
        models[AGENT_BUILDER] = args.builder_model
    if args.design_review_model:
        models[AGENT_DESIGN_REVIEW] = args.design_review_model
    if args.design_refine_model:
        models[AGENT_DESIGN_REFINE] = args.design_refine_model
    if args.content_critique_model:
        models[AGENT_CONTENT_CRITIQUE] = args.content_critique_model
    if args.content_eval_model:
        models[AGENT_CONTENT_EVAL] = args.content_eval_model
    if args.content_refine_model:
        models[AGENT_CONTENT_REFINE] = args.content_refine_model
    return models


def resolve_agent_providers(args: argparse.Namespace) -> dict[str, str]:
    providers = {agent: PROVIDER_CODEX for agent in AGENT_MODELS}
    if args.claude_html_stages:
        for agent in CLAUDE_HTML_AGENTS:
            providers[agent] = PROVIDER_CLAUDE
    return providers


def normalize_claude_options(args: argparse.Namespace) -> None:
    if not args.claude_html_stages:
        return

    args.claude_model = normalize_claude_model("--claude-model", args.claude_model)
    for option_name, attr in (
        ("--builder-model", "builder_model"),
        ("--design-refine-model", "design_refine_model"),
        ("--content-refine-model", "content_refine_model"),
    ):
        value = getattr(args, attr)
        if value:
            setattr(args, attr, normalize_claude_model(option_name, value))


def normalize_claude_model(option_name: str, value: str) -> str:
    normalized = value.lower()
    if normalized not in CLAUDE_MODEL_ALIASES:
        allowed = ", ".join(sorted(CLAUDE_MODEL_ALIASES))
        raise ValueError(f"{option_name} must be one of: {allowed}")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Run content harness pipeline.")
    parser.add_argument("input", type=Path, help="Path to an input JSON file matching input.schema.json.")
    parser.add_argument("--codex-bin", default=DEFAULT_CODEX_BIN)
    parser.add_argument("--claude-bin", default=DEFAULT_CLAUDE_BIN)
    parser.add_argument(
        "--claude-html-stages",
        action="store_true",
        help="Run only Builder, Design Refine, and Content Refine with Claude Code instead of Codex.",
    )
    parser.add_argument(
        "--claude-model",
        default=MODEL_CLAUDE_SONNET,
        help="Claude model alias for --claude-html-stages: opus or sonnet. Defaults to sonnet.",
    )
    parser.add_argument("--model", help="Alias for planner/asset/builder model in the current MVP.")
    parser.add_argument("--planner-only", action="store_true", help="Run only input validation and planner.")
    parser.add_argument("--asset-generator-only", action="store_true", help="Run only asset generation from an existing planner output.")
    parser.add_argument("--builder-only", action="store_true", help="Run only HTML builder from existing planner and asset outputs.")
    parser.add_argument("--design-review-only", action="store_true", help="Run only Senior Designer review from existing builder output.")
    parser.add_argument("--design-refine-only", action="store_true", help="Run only Design Refine from an existing design review and write output/refine.html for debugging.")
    parser.add_argument("--content-critique-only", action="store_true", help="Run only content HTML critique from existing builder output.")
    parser.add_argument("--content-eval-only", action="store_true", help="Run only content HTML evaluation from existing builder output.")
    parser.add_argument("--planner-model", help="Model for the Planner agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--asset-generator-model", help="Model for the Asset Generator agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--builder-model", help="Model for the Builder agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--design-review-model", help="Model for the Senior Designer Review agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--design-refine-model", help="Model for the Design Refine agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--content-critique-model", help="Model for the Content Critique agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--content-eval-model", help="Model for the Content Eval agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--content-refine-model", help="Model for the Content Refine agent. Defaults to the Codex CLI default model.")
    parser.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    parser.add_argument("--content-rubric", type=Path, default=CONTENT_RUBRIC_PATH)
    parser.add_argument("--iteration", default="001")
    parser.add_argument(
        "--run-id",
        help="Reuse a specific run directory id such as 2026-07-06_a1b2c3d4 instead of today's date-based id.",
    )
    parser.add_argument(
        "--start-at",
        choices=["planner", "asset", "builder"],
        default="planner",
        help="Start the full content pipeline at this stage, reusing earlier artifacts from the run directory.",
    )
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--content-max-iterations", type=int, default=DEFAULT_CONTENT_MAX_ITERATIONS)
    parser.add_argument("--asset-batch-size", type=int, default=DEFAULT_ASSET_BATCH_SIZE)
    parser.add_argument("--asset-parallelism", type=int, default=DEFAULT_ASSET_PARALLELISM)
    parser.add_argument(
        "--asset-budget",
        type=int,
        default=DEFAULT_ASSET_BUDGET,
        help="Max asset requests (regenerate + new combined) a single design review round may make.",
    )
    parser.add_argument(
        "--asset-generator-missing-only",
        action="store_true",
        help="Reuse existing files under output/assets and generate only missing planned assets.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--design-refine-timeout-seconds",
        type=int,
        help=(
            "Timeout for the Design Refine agent. Defaults to the larger of --timeout-seconds and "
            f"{DEFAULT_DESIGN_REFINE_TIMEOUT_SECONDS}, because rewriting the full HTML takes longer than other stages."
        ),
    )
    parser.add_argument(
        "--design-review-timeout-seconds",
        type=int,
        help=(
            "Timeout for the Senior Designer Review agent. Defaults to the larger of --timeout-seconds and "
            f"{DEFAULT_DESIGN_REVIEW_TIMEOUT_SECONDS}, because reading the full HTML and every asset takes longer "
            "than other stages."
        ),
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing artifacts for the same run.")
    args = parser.parse_args()
    normalize_claude_options(args)

    if len(args.iteration) != 3 or not args.iteration.isdigit():
        raise ValueError("--iteration must use a 3-digit value such as 001")
    if args.max_iterations < 1:
        raise ValueError("--max-iterations must be at least 1")
    if args.content_max_iterations < 1:
        raise ValueError("--content-max-iterations must be at least 1")
    if args.asset_batch_size < 1:
        raise ValueError("--asset-batch-size must be at least 1")
    if args.asset_parallelism < 1:
        raise ValueError("--asset-parallelism must be at least 1")
    if args.asset_budget < 1:
        raise ValueError("--asset-budget must be at least 1")

    single_stage_flags = [
        args.planner_only,
        args.asset_generator_only,
        args.builder_only,
        args.design_review_only,
        args.design_refine_only,
        args.content_critique_only,
        args.content_eval_only,
    ]
    if sum(1 for enabled in single_stage_flags if enabled) > 1:
        raise ValueError(
            "--planner-only, --asset-generator-only, --builder-only, --design-review-only, "
            "--design-refine-only, --content-critique-only, and --content-eval-only cannot be used together"
        )

    if args.planner_only:
        result = run_planner_only(args)
    elif args.asset_generator_only:
        result = run_asset_generator_only(args)
    elif args.builder_only:
        result = run_builder_only(args)
    elif args.design_review_only:
        result = run_design_review_only(args)
    elif args.design_refine_only:
        result = run_design_refine_only(args)
    elif args.content_critique_only:
        result = run_content_critique_only(args)
    elif args.content_eval_only:
        result = run_content_eval_only(args)
    else:
        result = run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
