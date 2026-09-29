"""배치 기록 — 무엇을 어디에 놓았는지 해시로 남겨, **그 뒤에 어느 쪽이 바뀌었는지** 가른다.

왜 필요한가 — 실측(2026-09-29, 4-1/03). 배치해 둔 차시를 누군가 gyo6_content 쪽에서 직접 고쳤다
(그림 6장을 다시 굽고 lesson.json 의 그림 지시 2곳을 바꿨다). run 은 그 사실을 몰랐고,
`install_lesson.py --overwrite` 가 경고 없이 run 의 옛 그림으로 덮었다. 같은 일이 화면 결함의
원인이기도 했다 — gyo6 쪽에서 다보탑을 다시 구웠는데 각 좌표는 옛 그림 기준이라 탑 밖에 떴다.
시각(mtime)만 보는 검사로는 이것이 안 보인다. 내용이 갈라졌는지는 해시로만 안다.

기록은 run 쪽에 둔다(`runs/{id}/install-record.json`). 한 run 을 여러 자리에 놓을 수 있으므로
`{target}|{lesson}` 마다 따로 적는다.

    source   run 쪽 원본(lesson/lesson.json · player-ext.* · assets/**)의 해시 — run 이 배치 뒤 바뀌었나
    placed   gyo6 쪽에 **우리가 쓴 파일**의 해시 — gyo6 쪽이 배치 뒤 바뀌었나

빌드가 차시 폴더에 새로 만드는 파일(thumbnail · 9-slice 등)은 우리가 쓴 것이 아니므로 보지 않는다.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

RECORD_NAME = "install-record.json"
KST = timezone(timedelta(hours=9))
SOURCE_FILES = ("lesson.json", "player-ext.js", "player-ext.css")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(lesson_dir: Path) -> dict[str, str]:
    """run 쪽 번들의 해시. 배치가 경로·확장자를 고쳐 쓰므로 **원본** 쪽을 따로 적는다."""
    hashes = {name: digest(lesson_dir / name) for name in SOURCE_FILES if (lesson_dir / name).exists()}
    assets = lesson_dir / "assets"
    if assets.is_dir():
        for path in sorted(assets.rglob("*")):
            if path.is_file():
                hashes[path.relative_to(lesson_dir).as_posix()] = digest(path)
    return hashes


def placed_hashes(dest_dir: Path, relpaths: list[str]) -> dict[str, str]:
    return {rel: digest(dest_dir / rel) for rel in sorted(set(relpaths)) if (dest_dir / rel).exists()}


def key(target_root: Path, lesson_ref: str) -> str:
    return f"{target_root.resolve().as_posix()}|{lesson_ref}"


def load(run_dir: Path) -> dict:
    path = run_dir / RECORD_NAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def entry(run_dir: Path, target_root: Path, lesson_ref: str) -> dict | None:
    return load(run_dir).get(key(target_root, lesson_ref))


def save(run_dir: Path, target_root: Path, lesson_ref: str, lesson_dir: Path, dest_dir: Path,
         relpaths: list[str]) -> None:
    data = load(run_dir)
    data[key(target_root, lesson_ref)] = {
        "installed_at": datetime.now(KST).isoformat(timespec="seconds"),
        "source": source_hashes(lesson_dir),
        "placed": placed_hashes(dest_dir, relpaths),
    }
    (run_dir / RECORD_NAME).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def target_drift(record: dict, dest_dir: Path) -> list[str]:
    """배치 뒤 gyo6 쪽에서 바뀌거나 사라진, **우리가 쓴** 파일."""
    changed = []
    for rel, value in (record.get("placed") or {}).items():
        path = dest_dir / rel
        if not path.exists():
            changed.append(f"{rel} (지워짐)")
        elif digest(path) != value:
            changed.append(rel)
    return changed


def source_drift(record: dict, lesson_dir: Path) -> list[str]:
    """배치 뒤 run 쪽에서 바뀐 파일 — 다시 배치해야 화면에 닿는다."""
    before = record.get("source") or {}
    now = source_hashes(lesson_dir)
    return sorted(rel for rel in set(before) | set(now) if before.get(rel) != now.get(rel))


def unrecorded_differences(dest_dir: Path, planned: dict[str, bytes | Path]) -> list[str]:
    """기록이 없을 때 — 지금 놓으려는 것과 이미 놓인 것이 **다른** 파일.

    기록이 없으면 그 차이가 run 이 새로워서인지 gyo6 쪽에서 고쳐서인지 가를 수 없다.
    그래서 목록을 보여 주고 사람이 정하게 한다.
    """
    differs = []
    for rel, content in planned.items():
        path = dest_dir / rel
        if not path.exists():
            continue
        new = content if isinstance(content, bytes) else content.read_bytes()
        if path.read_bytes() != new:
            differs.append(rel)
    return sorted(differs)
