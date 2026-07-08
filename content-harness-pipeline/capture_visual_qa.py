from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from stages.visual_qa import run_visual_qa


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_RUNS_DIR = PROJECT_DIR / "runs"


def infer_iteration(run_dir: Path) -> str:
    iter_dirs = [
        path
        for path in run_dir.glob("iter_*")
        if path.is_dir() and len(path.name) == len("iter_001") and path.name[5:].isdigit()
    ]
    if not iter_dirs:
        raise FileNotFoundError(f"no iter_XXX directories found under {run_dir}")
    return sorted(path.name[5:] for path in iter_dirs)[-1]


def resolve_run_dir(args: argparse.Namespace) -> Path:
    if args.run_dir:
        return args.run_dir.resolve()
    if args.run_id:
        return (args.runs_dir / args.run_id).resolve()
    raise ValueError("pass either --run-dir or --run-id")


def clean_artifact_dir(run_dir: Path, iteration: str, artifact_dir: str) -> None:
    target = (run_dir / f"iter_{iteration}" / artifact_dir).resolve()
    allowed_parent = (run_dir / f"iter_{iteration}").resolve()
    target.relative_to(allowed_parent)
    if not target.exists():
        return
    if target == allowed_parent:
        raise ValueError("refusing to clean the iteration directory itself")
    for child in target.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture quick Playwright screenshots for design refine self-review."
    )
    parser.add_argument("--run-dir", type=Path, help="Run directory, e.g. runs/2026-07-07_a1b2c3d4")
    parser.add_argument("--run-id", help="Run id under --runs-dir, e.g. 2026-07-07_a1b2c3d4")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--iteration", help="Iteration such as 001. Defaults to the latest iter_XXX directory.")
    parser.add_argument("--html-path", type=Path, help="HTML file to capture. Defaults to RUN_DIR/output/index.html.")
    parser.add_argument(
        "--artifact-dir",
        default="design_refine_preview",
        help="Folder under iter_XXX for screenshots. Defaults to design_refine_preview.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="JSON output path. Defaults to RUN_DIR/iter_XXX/ARTIFACT_DIR.json.",
    )
    parser.add_argument(
        "--viewports",
        nargs="+",
        choices=["desktop", "tablet", "mobile"],
        default=["desktop"],
        help="Viewports to capture. Defaults to desktop.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing files in the artifact screenshot folder before capture.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=600)
    args = parser.parse_args()

    run_dir = resolve_run_dir(args)
    iteration = args.iteration or infer_iteration(run_dir)
    html_path = (args.html_path or (run_dir / "output" / "index.html")).resolve()
    output_path = args.output or (run_dir / f"iter_{iteration}" / f"{args.artifact_dir}.json")

    if not run_dir.exists():
        raise FileNotFoundError(f"run dir not found: {run_dir}")
    if not html_path.exists():
        raise FileNotFoundError(f"HTML not found: {html_path}")

    if args.clean:
        clean_artifact_dir(run_dir, iteration, args.artifact_dir)

    run_visual_qa(
        html_path=html_path,
        run_dir=run_dir,
        iteration=iteration,
        output_path=output_path,
        timeout_seconds=args.timeout_seconds,
        artifact_dir_name=args.artifact_dir,
        viewport_names=tuple(args.viewports),
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
