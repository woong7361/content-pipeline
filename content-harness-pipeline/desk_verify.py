"""차시 작업대의 [AI 맡기기] 중 **검증 메모** — 코덱스가 빌드된 화면을 열어 확인만 한다.

    python -B ./desk_verify.py --gyo6-root <gyo6_content> --lesson 4-1/04 --desk-dir desk/4-1-04 \
        --view-url http://127.0.0.1:8790/view/4-1/04/index.html

- 검증·테스트는 코덱스가 한다(2026-09-30 사용자 결정). 캡처를 실제로 여는 도구가 그쪽에 있다.
- 화면은 작업대 서버의 http 주소로 연다. `file://` 은 글꼴을 막아 실제와 다르게 보인다.
- **파일을 고치지 않는다.** 코덱스는 샌드박스 없이 돌기 때문에 프롬프트만 믿지 않는다 — 전후 해시를 대조해
  lesson.json · player-ext.* 가 바뀌었으면 되돌리고 실패로 끝낸다. 그림(assets)이 바뀌었으면 목록을 적고 실패로 끝낸다.
- 결과는 `{desk-dir}/last-verify.json`, 캡처는 `{desk-dir}/verify/{시각}/`.

종료 코드: 0 끝남 · 1 실패
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import lesson_notes, usage_log  # noqa: E402
from stages.scripts.codex_client import CodexClient  # noqa: E402
from stages.scripts.lesson_notes import KST  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = PROJECT_DIR / "prompts" / "desk_verify_system.md"
SCHEMA = PROJECT_DIR / "schemas" / "desk_verify_output.schema.json"
BUNDLE = ("lesson.json", "player-ext.js", "player-ext.css")


def hashes(lesson_dir: Path) -> dict[str, str]:
    out = {}
    for path in [lesson_dir / n for n in BUNDLE] + sorted((lesson_dir / "assets").rglob("*")):
        if path.is_file():
            out[path.relative_to(lesson_dir).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 검증(코덱스)")
    parser.add_argument("--gyo6-root", type=Path, required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--desk-dir", type=Path, required=True)
    parser.add_argument("--view-url", required=True)
    parser.add_argument("--lesson-dir", type=Path, default=None,
                        help="고칠 차시 폴더(작업대가 지정). 없으면 <gyo6>/lessons/<lesson>")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max", "ultra"],
                        help="추론 강도(작업대 사이드바에서 고른 것). 없으면 CLI 설정")
    parser.add_argument("--model", default=None, help="이 AI 의 모델(작업대 사이드바에서 고른 것). 없으면 CLI 기본")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()

    gyo6 = args.gyo6_root.resolve()
    lesson_dir = args.lesson_dir.resolve() if args.lesson_dir else gyo6 / "lessons" / args.lesson
    desk_dir = args.desk_dir.resolve()
    notes = [n for n in lesson_notes.load(desk_dir)
             if n.get("status") == "working" and lesson_notes.kind_of(n) == "verify"]
    if not notes:
        print("확인할 검증 메모가 없다")
        return 1

    out_dir = desk_dir / "verify" / datetime.now(KST).strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot = out_dir / "_bundle-before"
    snapshot.mkdir()
    for name in BUNDLE:
        if (lesson_dir / name).exists():
            shutil.copy2(lesson_dir / name, snapshot / name)
    before = hashes(lesson_dir)

    body = "\n\n".join(f"### {n['id']}\n\n{n['text'].strip()}" for n in notes)
    prompt = "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {args.lesson}\nLESSON_DIR: {lesson_dir}\nGYO6_ROOT: {gyo6}\nVIEW_URL: {args.view_url}\nOUT_DIR: {out_dir}",
        f"## NOTES — 이번에 확인할 검증 메모 {len(notes)}건\n\n{body}",
    ])
    usage_log.bind(desk_dir, f"desk_verify {args.lesson}", tag=os.environ.get("DESK_STEP", ""))
    client = CodexClient(effort=args.effort or "", codex_bin=args.codex_bin, project_dir=PROJECT_DIR, timeout_seconds=args.timeout_seconds)
    output = desk_dir / "last-verify.json"
    output.unlink(missing_ok=True)
    print(f"검증: {args.lesson} · 메모 {len(notes)}건 · {args.view_url}")
    client.run_prompt(prompt, SCHEMA, output, stage="desk_verify", model=args.model or None)

    after = hashes(lesson_dir)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if changed:
        for name in BUNDLE:
            if name in changed and (snapshot / name).exists():
                shutil.copy2(snapshot / name, lesson_dir / name)
        print(f"검증이 파일을 바꿨다 — 코드 파일은 되돌림, 그림은 확인 필요: {', '.join(changed)}")
        return 1
    if not output.exists():
        print("결과 파일이 없다")
        return 1
    result = json.loads(output.read_text(encoding="utf-8"))
    for item in result.get("notes", []):
        # 펼쳤을 때 판정을 되짚을 수 있게 기대·본 것을 맨 앞 줄로(작업대는 headline 만 보이고 detail 은 접어 둔다)
        lines = [f"- 기대: {item.get('expected', '')}", f"- 본 것: {item.get('observed', '')}", item.get("detail", "").strip()]
        item["detail"] = "\n".join(line for line in lines if line)
        print(f"  {item['id']}: {item['result']} — {item['detail']}")
        for shot in item.get("evidence", []):
            print(f"      근거: {shot}")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"요약: {result.get('summary')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
