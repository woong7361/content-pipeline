"""차시 작업대의 [AI 맡기기] 중 **그림 메모** — 코덱스가 gyo6 차시의 그림 파일을 다시 굽는다.

    python -B ./desk_image.py --gyo6-root <gyo6_content> --lesson 4-1/04 --desk-dir desk/4-1-04

- 그림은 코덱스가 굽는다(`asset_render` 와 같은 이유 — 그림을 만들고 여는 도구가 그쪽에 있다).
- 고치는 것은 `lessons/{차시}/assets/` 의 그림 파일뿐이다(`prompts/desk_image_system.md`). 메모가 원하면 새 그림도
  만든다(2026-09-30 사용자 요청 — 예전에는 덮어쓰기만 해서 "CTA 버튼 새로" 를 못 했다). 9-slice 판이면 `-9slice.json` 도 낸다.
  새 그림을 화면에 붙이는 일은 결과의 `follow_up` 으로 넘기고, 작업대가 그것을 코드 메모로 이어서 넣는다.
- 투명이 필요한 그림은 코덱스가 크로마 색을 평평하게 칠해 저장하고, **지우는 것은 코드**(`asset_alpha.chroma_key`)다.
- 원래 투명이던 그림이 불투명해졌거나, 픽셀 크기가 바뀌었으면 결과에 적는다(막지는 않는다 — 사람이 화면에서 본다).
- 결과는 `{desk-dir}/last-image.json`. 메모 상태를 바꾸는 것은 작업대가 한다.

종료 코드: 0 끝남 · 1 실패
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import lesson_notes, usage_log  # noqa: E402
from stages.scripts.asset_alpha import chroma_key, has_alpha  # noqa: E402
from stages.scripts.codex_client import CodexClient  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = PROJECT_DIR / "prompts" / "desk_image_system.md"
SCHEMA = PROJECT_DIR / "schemas" / "desk_image_output.schema.json"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def all_files(assets: Path) -> set[str]:
    return {p.relative_to(assets.parent).as_posix() for p in assets.rglob("*") if p.is_file()} if assets.is_dir() else set()


def shelve_orphans(lesson_dir: Path, desk_dir: Path, before: set[str], reported: set[str]) -> list[str]:
    """이번 작업이 assets/ 에 새로 남겼는데 결과에 안 적힌 파일을 작업대 폴더로 옮긴다(지우지 않는다).

    실측(2026-09-30, 4-1/04 복사본) — 코덱스가 혼잡해 두 번 다시 불렀더니 부를 때마다 처음부터 그려서, 앞 시도의
    그림·설명 파일과 이름이 깨진 파일(`cta-button-9slice.png.Replace('.png','.json')`)이 차시 폴더에 남았다.
    결과에는 마지막 파일만 적혀 있어 아무도 모르게 배포까지 따라갈 뻔했다.
    적힌 그림의 짝 설명 파일(`이름.json`)은 남긴다.
    """
    keep = set(reported) | {str(Path(r).with_suffix(".json").as_posix()) for r in reported}
    stray = sorted(all_files(lesson_dir / "assets") - before - keep)
    if not stray:
        return []
    shelf = desk_dir / "orphans" / (os.environ.get("DESK_STEP") or datetime.now().strftime("%Y%m%d-%H%M%S"))
    for rel in stray:
        dest = shelf / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(lesson_dir / rel), str(dest))
    return stray


def code_ran_alongside(desk_dir: Path, since: str) -> bool:
    """이 그림 작업이 도는 동안 코드 메모 작업(클로드)이 함께 돌았나 — 지금 돌고 있거나, 이 작업이 시작한 뒤에 끝났다.

    코드 메모는 그림 이름을 바꾸거나 새 파일을 만들 수 있다(2026-10-01). 그러면 assets/ 에 새로 생긴 파일이
    이 그림 작업의 찌꺼기인지 코드가 만든 것인지 못 가른다 — 그때는 치우지 않고 알리기만 한다.
    """
    if (desk_dir / "active-job-claude.json").exists():
        return True
    log = desk_dir / "jobs.jsonl"
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()] if log.exists() else []
    return any(r.get("note_kind") == "code" and (r.get("ended") or "") >= since for r in rows)


def image_facts(assets: Path) -> dict[str, dict]:
    """그리기 전 그림마다 픽셀 크기와 투명 여부 — 그린 뒤 대조한다."""
    from PIL import Image

    facts = {}
    for path in assets.rglob("*"):
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            with Image.open(path) as handle:
                size = handle.size
            facts[path.relative_to(assets.parent).as_posix()] = {"size": size, "alpha": has_alpha(path)}
        except OSError:
            continue
    return facts


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 그림 다시 굽기(코덱스)")
    parser.add_argument("--gyo6-root", type=Path, required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--desk-dir", type=Path, required=True)
    parser.add_argument("--lesson-dir", type=Path, default=None,
                        help="고칠 차시 폴더(작업대가 지정). 없으면 <gyo6>/lessons/<lesson>")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max", "ultra"],
                        help="추론 강도(작업대 사이드바에서 고른 것). 없으면 CLI 설정")
    parser.add_argument("--model", default=None, help="이 AI 의 모델(작업대 사이드바에서 고른 것). 없으면 CLI 기본")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()

    from PIL import Image

    lesson_dir = args.lesson_dir.resolve() if args.lesson_dir else args.gyo6_root.resolve() / "lessons" / args.lesson
    desk_dir = args.desk_dir.resolve()
    notes = [n for n in lesson_notes.load(desk_dir)
             if n.get("status") == "working" and lesson_notes.kind_of(n) == "image"]
    if not notes:
        print("그릴 그림 메모가 없다")
        return 1

    started = datetime.now(lesson_notes.KST).isoformat(timespec="seconds")
    before = image_facts(lesson_dir / "assets")
    before_files = all_files(lesson_dir / "assets")
    body = "\n\n".join(lesson_notes.prompt_block(n, desk_dir) for n in notes)
    prompt = "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {args.lesson}\nLESSON_DIR: {lesson_dir}",
        f"## NOTES — 이번에 그릴 그림 메모 {len(notes)}건\n\n{body}",
    ])
    usage_log.bind(desk_dir, f"desk_image {args.lesson}", tag=os.environ.get("DESK_STEP", ""))
    client = CodexClient(effort=args.effort or "", codex_bin=args.codex_bin, project_dir=PROJECT_DIR, timeout_seconds=args.timeout_seconds)
    output = desk_dir / "last-image.json"
    output.unlink(missing_ok=True)
    print(f"그림 다시 굽기: {args.lesson} · 메모 {len(notes)}건")
    client.run_prompt(prompt, SCHEMA, output, stage="desk_image", model=args.model or None)
    if not output.exists():
        print("결과 파일이 없다")
        return 1

    result = json.loads(output.read_text(encoding="utf-8"))
    for item in result.get("notes", []):
        warnings = []
        created: list[str] = []
        for entry in item.get("files", []):
            rel = str(entry.get("path", "")).replace("\\", "/")
            target = lesson_dir / rel
            # 새 그림을 만들 수 있게 됐으므로 자리를 확인한다 — 차시의 assets/ 밖에 쓴 것은 건드리지 않고 알린다
            if (lesson_dir / "assets").resolve() not in target.resolve().parents:
                warnings.append(f"{rel} 은(는) assets/ 밖이다 — 쓰지 않는 자리")
                continue
            if not target.exists():
                warnings.append(f"{rel} 파일이 없다")
                continue
            if rel not in before:
                created.append(rel)
            if entry.get("chroma", "none") != "none":
                keyed = chroma_key(target, entry["chroma"])
                if keyed.get("keyed"):
                    print(f"    크로마 제거 {rel} ({entry['chroma']}, {keyed['removed_ratio'] * 100:.0f}%)")
            old = before.get(rel)
            if old:
                with Image.open(target) as handle:
                    size = handle.size
                if tuple(size) != tuple(old["size"]):
                    warnings.append(f"{rel} 크기가 바뀜 {old['size'][0]}x{old['size'][1]} → {size[0]}x{size[1]}")
                if old["alpha"] and not has_alpha(target):
                    warnings.append(f"{rel} 원래 투명이었는데 불투명해짐")
        # 작업대는 headline 만 보이고 detail 은 접어 둔다 — 덧붙이는 것도 "- " 한 줄씩
        extra = ([f"- 새로 만든 파일: {', '.join(created)}"] if created else []) + [f"- ⚠ {w}" for w in warnings]
        if extra:
            item["detail"] = "\n".join([item.get("detail", "").rstrip(), *extra]).strip()
        print(f"  {item['id']}: {item['result']} — {item['detail']}")
    reported = {str(e.get("path", "")).replace("\\", "/") for item in result.get("notes", []) for e in item.get("files", [])}
    if code_ran_alongside(desk_dir, started):
        # 코드 메모가 함께 돌았다 — 새 파일이 그쪽 것(이름 바꾼 그림 등)일 수 있어 치우지 않고 알리기만 한다
        keep = reported | {Path(r).with_suffix(".json").as_posix() for r in reported}
        unknown = sorted(all_files(lesson_dir / "assets") - before_files - keep)
        if unknown:
            print(f"  코드 작업이 함께 돌아 결과에 안 적힌 새 파일 {len(unknown)}개를 치우지 않음: {', '.join(unknown)}")
        stray = []
    else:
        stray = shelve_orphans(lesson_dir, desk_dir, before_files, reported)
    if stray:
        where = (desk_dir / "orphans").as_posix()
        print(f"  결과에 안 적힌 새 파일 {len(stray)}개를 차시 밖으로 옮김({where}): {', '.join(stray)}")
        result["summary"] = f"{result.get('summary', '')} ⚠ 결과에 안 적힌 새 파일 {len(stray)}개는 차시 밖으로 옮겼다({where})"
        for item in result.get("notes", []):
            note = f"- ⚠ 재시도 등으로 남은 파일 {len(stray)}개를 차시 밖으로 옮겨 둠: {', '.join(stray)}"
            item["detail"] = "\n".join([item.get("detail", "").rstrip(), note]).strip()
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"요약: {result.get('summary')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
