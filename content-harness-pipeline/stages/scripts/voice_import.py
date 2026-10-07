"""음성 파일 넣기 — 사람이 대사마다 따로 받은 음성 파일(Typecast 웹 편집기 등)을 대사와 짝지어 차시에 건다.

사용자 결정(2026-10-01) — 차시 작업대와 초안 파이프라인 둘 다. 파일은 **대사 한 줄마다 따로** 온다.
짝짓기는 **자동 + 확인표**: 올리면 자동으로 짝짓고, 사람이 줄마다 들어 보고 바꾼 뒤 [넣기]. 작업대에서는 빈 대사 채우기와
기존 소리 교체 둘 다(교체된 예전 파일은 보관 폴더로).

    세션 폴더   files/ (올린 파일 그대로) · session.json (대사 목록 · 짝 · 상태)
    넣기        <차시>/assets/audio/narration/<id>.<받은 확장자> + lesson.json 의 audioMap.narration · 자리별 소리(`voice_lines.apply`)

자동 짝짓기 — 파일 이름을 먼저 본다.
  ① 글자: 이름에 대사 앞부분이 있으면(번호 · 인물 이름 · 구분자를 뗀 뒤 대사와 비슷하면) 그 대사.
  ② 순서: 남은 파일은 이름 속 번호(없으면 이름) 순으로 남은 대사에 차례로.
어느 쪽으로 짝지었는지(`method`)를 남겨 확인표에 보인다 — 순서로 짝지은 것은 사람이 들어 봐야 한다.
"""

from __future__ import annotations

import json
import re
import shutil
from difflib import SequenceMatcher
from pathlib import Path

from stages.scripts import voice_lines

AUDIO_SUFFIXES = (".mp3", ".wav", ".ogg", ".m4a")
MODES = ("empty", "all")   # empty = 소리가 없는 대사만 · all = 이미 있는 것까지(교체)


def lines_for(lesson: dict, mode: str) -> list[voice_lines.Line]:
    lines, _ = voice_lines.collect(lesson, include_existing=True)
    return [line for line in lines if not line.current] if mode == "empty" else lines


def audio_path(lesson: dict, sound_id: str) -> str:
    """소리 id 가 가리키는 파일(차시 기준 경로). narration → sfx → bgm 순(런타임 resolveAudioSource 와 같다)."""
    audio_map = lesson.get("audioMap") or {}
    for group in ("narration", "sfx", "bgm"):
        value = (audio_map.get(group) or {}).get(sound_id)
        if isinstance(value, str):
            return value
    return ""


def rows(lesson: dict, mode: str) -> list[dict]:
    """확인표에 보일 대사 목록(재생 순서)."""
    cast = lesson.get("cast") or {}
    name = lambda key: (cast.get(key) or {}).get("name", key) if isinstance(cast, dict) else key
    return [{"key": line.audio_id, "kind": line.kind, "speaker": line.speaker,
             "speaker_name": "나레이션" if line.speaker == voice_lines.NARRATOR else name(line.speaker),
             "text": line.text, "current": line.current, "current_path": audio_path(lesson, line.current) if line.current else ""}
            for line in lines_for(lesson, mode)]


def normalize(text: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", text.lower())


def name_text(stem: str, speakers: list[str]) -> str:
    """파일 이름에서 대사로 보이는 부분 — 번호 · 인물 이름 · 구분자를 뗀다."""
    text = re.sub(r"\d+", " ", stem)
    for speaker in speakers:
        if speaker:
            text = text.replace(speaker, " ")
    return normalize(text)


def first_number(stem: str) -> int | None:
    found = re.search(r"\d+", stem)
    return int(found.group()) if found else None


def auto_match(table: list[dict], files: list[str]) -> dict[str, dict]:
    """대사 key → {file, method}. 짝 못 지은 대사는 빠진다."""
    speakers = sorted({r["speaker_name"] for r in table} | {r["speaker"] for r in table}, key=len, reverse=True)
    stems = {f: name_text(Path(f).stem, speakers) for f in files}
    scored = []
    for f, stem in stems.items():
        if len(stem) < 4:
            continue
        for r in table:
            target = normalize(r["text"])
            if not target:
                continue
            head = target[:len(stem)]
            score = 1.0 if stem in target else SequenceMatcher(None, stem, head).ratio()
            if score >= 0.6:
                scored.append((score, f, r["key"]))
    pairs: dict[str, dict] = {}
    used: set[str] = set()
    for score, f, key in sorted(scored, reverse=True):
        if f in used or key in pairs:
            continue
        pairs[key] = {"file": f, "method": "글자"}
        used.add(f)
    rest_files = sorted((f for f in files if f not in used),
                        key=lambda f: (first_number(Path(f).stem) is None, first_number(Path(f).stem) or 0, f))
    rest_rows = [r for r in table if r["key"] not in pairs]
    for f, r in zip(rest_files, rest_rows):
        pairs[r["key"]] = {"file": f, "method": "순서"}
    return pairs


def stage(session_dir: Path, lesson: dict, mode: str, uploads: list[tuple[str, bytes]]) -> dict:
    """올린 파일을 세션 폴더에 두고 자동으로 짝지어 session.json 을 쓴다."""
    if mode not in MODES:
        raise ValueError(f"알 수 없는 범위: {mode}")
    files_dir = session_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    names = []
    for raw_name, blob in uploads:
        name = Path(raw_name).name
        if Path(name).suffix.lower() not in AUDIO_SUFFIXES:
            raise ValueError(f"음성 파일이 아니다: {name} (mp3 · wav · ogg · m4a)")
        (files_dir / name).write_bytes(blob)
        names.append(name)
    if not names:
        raise ValueError("올린 파일이 없다")
    table = rows(lesson, mode)
    if not table:
        raise ValueError("소리를 붙일 대사가 없다" + (" — 이미 다 있다. '교체' 로 올리면 바꿀 수 있다" if mode == "empty" else ""))
    session = {"mode": mode, "status": "ready", "rows": table, "files": sorted(names), "pairs": auto_match(table, names)}
    (session_dir / "session.json").write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return session


def dump_like(raw: str, data: dict) -> str:
    """원래 파일과 같은 들여쓰기 · 줄바꿈으로 쓴다 — git 에 소리를 건 자리만 바뀐 것으로 보이게."""
    second = raw.splitlines()[1] if len(raw.splitlines()) > 1 else ""
    indent = len(second) - len(second.lstrip(" ")) or 2
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(data, ensure_ascii=False, indent=indent).replace("\n", newline)
    return text + (newline if raw.endswith(("\n", "\r\n")) else "")


def referenced_ids(node: object, out: set[str]) -> set[str]:
    """audioMap 을 뺀 곳에서 쓰이는 문자열 — 아직 쓰이는 소리 id 를 가리는 데 쓴다."""
    if isinstance(node, str):
        out.add(node)
    elif isinstance(node, dict):
        for key, value in node.items():
            if key != "audioMap":
                referenced_ids(value, out)
    elif isinstance(node, list):
        for value in node:
            referenced_ids(value, out)
    return out


def apply(lesson_dir: Path, session_dir: Path, pairs: dict[str, str], removed_dir: Path) -> dict:
    """확인한 짝(대사 key → 세션 파일 이름)대로 파일을 놓고 lesson.json 에 건다.

    교체된 예전 소리는 다른 곳에서 안 쓰이면 audioMap 에서 빼고 파일을 removed_dir 로 옮긴다(지우지 않는다).
    """
    session_path = session_dir / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    if session.get("status") != "ready":
        raise ValueError("이미 넣었거나 버린 음성 세션이다 — 새로 올려서 짝짓는다")
    lesson_path = lesson_dir / "lesson.json"
    # 바이트로 읽는다 — read_text 는 CRLF 를 LF 로 바꿔 읽어서 원래 줄바꿈을 모른 채 LF 로 다시 썼다(파일 전체가 바뀐 것으로 보였다)
    raw = lesson_path.read_bytes().decode("utf-8")
    lesson = json.loads(raw)
    lines = {line.audio_id: line for line in lines_for(lesson, session["mode"])}
    expected = {r["key"]: r["text"] for r in session["rows"]}
    chosen = []
    for key, name in pairs.items():
        if not name:
            continue
        line = lines.get(key)
        if line is None or line.text != expected.get(key):
            raise ValueError("올린 뒤에 차시 대사가 바뀌었다 — 다시 올려서 짝짓는다")
        source = session_dir / "files" / Path(name).name
        if not source.is_file():
            raise ValueError(f"세션에 없는 파일: {name}")
        line.ext = source.suffix.lower()
        chosen.append((line, source))
    if not chosen:
        raise ValueError("넣을 짝이 없다")

    target_dir = lesson_dir / voice_lines.AUDIO_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    old_ids = {line.current for line, _ in chosen if line.current and line.current != line.audio_id}
    for line, source in chosen:
        target = lesson_dir / line.path
        for same in target_dir.glob(f"{line.audio_id}.*"):   # 같은 id 의 옛 파일(다른 확장자 포함)은 보관
            dest = removed_dir / same.relative_to(lesson_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(same), str(dest))
            moved.append(same.relative_to(lesson_dir).as_posix())
        shutil.copy2(source, target)
    voice_lines.apply(lesson, [line for line, _ in chosen])

    still_used = referenced_ids(lesson, set())
    for old in sorted(old_ids - still_used):
        for group in ("narration", "sfx", "bgm"):
            mapping = (lesson.get("audioMap") or {}).get(group) or {}
            rel = mapping.pop(old, None)
            if isinstance(rel, str) and (lesson_dir / rel).is_file() and not any(
                    rel == v for g in (lesson.get("audioMap") or {}).values() if isinstance(g, dict) for v in g.values()):
                dest = removed_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(lesson_dir / rel), str(dest))
                moved.append(rel)
    lesson_path.write_text(dump_like(raw, lesson), encoding="utf-8", newline="")
    session.update(status="applied", applied={line.audio_id: source.name for line, source in chosen}, moved=moved)
    session_path.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"placed": len(chosen), "replaced": len([l for l, _ in chosen if l.current]), "moved": moved}


def replace_sound(lesson_dir: Path, sound_id: str, name: str, blob: bytes, removed_dir: Path) -> dict:
    """이미 걸린 소리 id 하나의 **파일만** 바꾼다 — id 와 걸린 자리는 그대로(2026-10-06 사용자 요청, 연결 표에서 직접 넣기).

    이야기 카드 `narration.sequence` 의 조각처럼 대사 한 줄에 매이지 않은 소리를 바꿀 때 쓴다. 확장자가 달라지면
    audioMap 의 경로만 고친다. 예전 파일은 removed_dir 로 옮긴다(지우지 않는다). 다른 id 와 같은 파일을 쓰면 거절한다.
    """
    suffix = Path(name).suffix.lower()
    if suffix not in AUDIO_SUFFIXES:
        raise ValueError(f"음성 파일이 아니다: {name} (mp3 · wav · ogg · m4a)")
    lesson_path = lesson_dir / "lesson.json"
    raw = lesson_path.read_bytes().decode("utf-8")
    lesson = json.loads(raw)
    narration_map = (lesson.get("audioMap") or {}).get("narration") or {}
    old = narration_map.get(sound_id)
    if not isinstance(old, str) or not old:
        raise ValueError(f"audioMap.narration 에 없는 소리: {sound_id}")
    sharing = [k for g in (lesson.get("audioMap") or {}).values() if isinstance(g, dict)
               for k, v in g.items() if v == old and k != sound_id]
    if sharing:
        raise ValueError(f"{old} 를 다른 소리({', '.join(sharing)})도 쓴다 — 바꾸면 그쪽도 바뀐다")
    new = Path(old).with_suffix(suffix).as_posix()
    moved = []
    if (lesson_dir / old).is_file():
        dest = removed_dir / old
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(lesson_dir / old), str(dest))
        moved.append(old)
    (lesson_dir / new).parent.mkdir(parents=True, exist_ok=True)
    (lesson_dir / new).write_bytes(blob)
    if new != old:
        narration_map[sound_id] = new
        lesson_path.write_text(dump_like(raw, lesson), encoding="utf-8", newline="")
    return {"placed": 1, "replaced": 1, "moved": moved, "path": new}
