"""차시 대사의 음성을 **Typecast 웹 편집기**에서 만들도록 대본을 내보낸다. 사람이 만드는 멈춤점이 있다.

    python -B ./voice_lesson.py runs/{run_id}              # 대본 내보내기(멈춤) · 받은 파일 확인
    python -B ./voice_lesson.py runs/{run_id} --dry-run    # 소리를 붙일 줄과 글자 수만 본다

흐름

    ① 대본 내보내기  인물 대표 그림이 나와 있으면, 소리를 붙일 대사를 모아 대본을 낸다
                     → audio/web/script.md (붙여 넣을 파일과 순서표) · script-{인물}.txt · script-all.txt
                     → 바탕화면 알림 · 여기서 멈춘다
    ② 사람이 만듦    웹 편집기에서 인물마다 목소리를 골라 만들고, 내려받은 파일을 audio/web-inbox/ 에 넣는다
                     (웹 프로젝트는 그대로 남는다)
    ③ 가져오기       내려받은 파일을 대사와 짝지어 lesson/assets/audio/narration/vo-*.mp3 로 놓고
                     lesson.json 에 audioMap.narration 과 자리별 소리를 건다(`voice_lines.apply`).
                     **아직 없다** — 웹 편집기가 내려받는 파일 형식을 본 뒤 만든다.

왜 웹인가 — 사용자는 Typecast 웹 요금제만 쓴다. Typecast 는 웹 서비스와 API 요금제를 따로 운영하므로
웹 요금제로는 API 를 부를 수 없다(2026-09-29 사용자 결정 — API 경로는 파이프라인에서 뺐다).

종료 코드: 0 끝남 · 3 사람이 만들 차례(멈춤) · 1 실패
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stages.scripts import voice_lines
from stages.scripts.notify import toast

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

KST = timezone(timedelta(hours=9))
PROJECT_DIR = Path(__file__).resolve().parent
WAITING_EXIT = 3
WEB_DIR = "web"
INBOX = "web-inbox"


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 대사의 Typecast 웹 대본을 내보낸다.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="소리를 붙일 줄과 글자 수만 보여 준다")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if args.dry_run:
        return dry_run(run_dir)
    return run_web(run_dir)


def load_lines(run_dir: Path) -> tuple[dict, list, list[str]] | None:
    lesson_path = run_dir / "lesson" / "lesson.json"
    if not lesson_path.exists():
        print(f"lesson.json 이 없다: {lesson_path}", file=sys.stderr)
        return None
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    lines, skipped = voice_lines.collect(lesson)
    return lesson, lines, skipped


def dry_run(run_dir: Path) -> int:
    loaded = load_lines(run_dir)
    if loaded is None:
        return 1
    _, lines, skipped = loaded
    speakers = list(dict.fromkeys(line.speaker for line in lines))
    print(f"대사 {len(lines)}줄 · {sum(len(l.text) for l in lines)}자 · 화자 {', '.join(speakers)}")
    for line in lines:
        print(f"  {line.audio_id:<22} {line.kind:<8} {line.speaker:<10} {line.text[:40]!r}")
    for item in skipped:
        print(f"  (안 붙임) {item}")
    return 0


def run_web(run_dir: Path) -> int:
    loaded = load_lines(run_dir)
    if loaded is None:
        return 1
    lesson, lines, skipped = loaded
    audio_dir = run_dir / "audio"
    inbox = audio_dir / INBOX
    received = sorted(p for p in inbox.rglob("*") if p.is_file()) if inbox.exists() else []

    exported = audio_dir / WEB_DIR / "lines.json"
    fresh = not exported.exists() or json.loads(exported.read_text(encoding="utf-8")).get("fingerprint") != script_fingerprint(lines)
    if fresh:
        export_script(run_dir, lesson, lines, skipped)
    if not received:
        return announce_web(run_dir, lesson, lines, first_time=fresh)

    # 가져오기는 웹 편집기가 내려받는 **실제 파일 형식**을 본 뒤에 짝짓는 규칙을 정한다.
    # 문장별로 나뉘는지, 파일 이름이 어떻게 붙는지 모르는 채로 순서만 믿고 짝지으면 대사가 어긋난다.
    print(f"\n{INBOX}/ 에 파일 {len(received)}개가 있다:")
    for path in received[:10]:
        print(f"  · {path.relative_to(inbox).as_posix()}")
    print("\n가져오기(대사와 짝짓기)는 아직 없다 — 웹 편집기가 내려받는 파일 형식을 확인한 뒤 만든다.")
    return WAITING_EXIT


def character_image(run_dir: Path, lesson: dict, speaker: str) -> str:
    cast = lesson.get("cast") or {}
    entry = cast.get(speaker) if isinstance(cast, dict) else None
    if not isinstance(entry, dict):
        return ""
    emotions = entry.get("emotions") or {}
    ref = entry.get("assetRef") or emotions.get("idle") or next(iter(emotions.values()), "")
    return ref if ref and (run_dir / "lesson" / ref).exists() else ""


def script_fingerprint(lines: list) -> str:
    return hashlib.sha256("\n".join(f"{l.audio_id}|{l.speaker}|{l.text}" for l in lines).encode("utf-8")).hexdigest()


def one_paragraph(text: str) -> str:
    """대사 하나 = 문단 하나. 줄바꿈이 있으면 웹 편집기가 여러 블록으로 쪼갠다."""
    return re.sub(r"\s*\n\s*", " ", text).strip()


def export_script(run_dir: Path, lesson: dict, lines: list, skipped: list[str]) -> None:
    out = run_dir / "audio" / WEB_DIR
    out.mkdir(parents=True, exist_ok=True)
    cast = lesson.get("cast") or {}
    names = {s: ("내레이션" if s == voice_lines.NARRATOR else (cast.get(s) or {}).get("name") or s)
             for s in dict.fromkeys(l.speaker for l in lines)}

    # 붙여 넣을 대본 — 화자별 한 파일(한 목소리로 한 번에 만들기)과 전체 순서 한 파일(한 프로젝트에서 인물 지정).
    # 본문에는 번호·화자 표시를 넣지 않는다. 넣으면 그것까지 읽는다.
    (out / "script-all.txt").write_text("\n\n".join(one_paragraph(l.text) for l in lines) + "\n", encoding="utf-8")
    for speaker in names:
        mine = [l for l in lines if l.speaker == speaker]
        (out / f"script-{voice_lines.safe_id(speaker)}.txt").write_text(
            "\n\n".join(one_paragraph(l.text) for l in mine) + "\n", encoding="utf-8")

    table = [
        "# Typecast 웹 대본",
        "",
        f"대사 {len(lines)}줄 · {sum(len(l.text) for l in lines)}자 · 인물 {len(names)}명",
        "",
        "## 붙여 넣을 파일",
        "",
        *[f"- `script-{voice_lines.safe_id(s)}.txt` — {n} ({sum(1 for l in lines if l.speaker == s)}줄)" for s, n in names.items()],
        f"- `script-all.txt` — 전체를 재생 순서대로({len(lines)}줄). 한 프로젝트에서 줄마다 인물을 지정할 때",
        "",
        "## 순서표 — 가져올 때 이 순서·id 로 짝짓는다",
        "",
        "| # | 화자 | 화자 안 # | 파일 이름(가져온 뒤) | 대사 |",
        "|---:|---|---:|---|---|",
    ]
    per_speaker: dict[str, int] = {}
    for i, line in enumerate(lines, start=1):
        per_speaker[line.speaker] = per_speaker.get(line.speaker, 0) + 1
        text = one_paragraph(line.text).replace("|", "\\|")
        table.append(f"| {i} | {names[line.speaker]} | {per_speaker[line.speaker]} | `{line.audio_id}.mp3` | {text[:60]} |")
    if skipped:
        table += ["", "## 소리를 안 붙이는 자리 (런타임이 재생하지 않는다)", "", *[f"- {s}" for s in skipped]]
    (out / "script.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    (out / "lines.json").write_text(json.dumps({
        "fingerprint": script_fingerprint(lines),
        "lines": [{"order": i, "audio_id": l.audio_id, "speaker": l.speaker, "kind": l.kind,
                   "text": one_paragraph(l.text)} for i, l in enumerate(lines, start=1)],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "audio" / INBOX).mkdir(parents=True, exist_ok=True)


def announce_web(run_dir: Path, lesson: dict, lines: list, first_time: bool) -> int:
    out = run_dir / "audio" / WEB_DIR
    speakers = list(dict.fromkeys(l.speaker for l in lines))
    print("\n" + "=" * 72)
    print(f"⏸ Typecast 웹 편집기에서 음성을 만들 차례다 — 인물 {len(speakers)}명 · 대사 {len(lines)}줄")
    for speaker in speakers:
        image = character_image(run_dir, lesson, speaker)
        print(f"  · {speaker}: 대표 그림 {('lesson/' + image) if image else '(없음 — 내레이션)'}")
    print(f"  대본: {out / 'script.md'}  (붙여 넣을 파일과 순서표)")
    print(f"  내려받은 파일은 여기에: {run_dir / 'audio' / INBOX}")
    print(f"  넣은 뒤: python -B ./voice_lesson.py {rel(run_dir)}")
    print("=" * 72)
    if first_time:
        toast("보이스를 골라 음성을 만들어 주세요",
              f"{run_dir.name}: 인물 {len(speakers)}명·대사 {len(lines)}줄 대본이 준비됐습니다. audio/web/script.md")
        log(run_dir, "voice_web_script_ready", {"lines": len(lines), "speakers": speakers})
    return WAITING_EXIT


def log(run_dir: Path, event: str, payload: dict) -> None:
    record = {"time": datetime.now(KST).isoformat(), "event": event, **payload}
    with (run_dir / "pipeline-log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_DIR).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
