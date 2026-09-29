from __future__ import annotations

import argparse
from pathlib import Path

from stages.scripts.spec_tests import write_and_verify


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate spec-based tests and verify lesson coverage.")
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    errors = write_and_verify(args.run_dir.resolve(), PROJECT_DIR / "schemas" / "lesson_spec.schema.json")
    if errors:
        print(f"REJECT: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 2
    print("PASS: lesson spec, traceability, and generated functional test plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
