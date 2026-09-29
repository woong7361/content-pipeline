"""lesson.json + 배치된 asset -> manifest.json (LLM 0회).

gyo6_content의 `agent/manifestWriter.mjs`가 만드는 것과 같은 모양을 만든다. 그쪽은
`npm run build:lesson` 안에서 도므로, 우리가 만들지 않아도 배치 후 빌드가 채워 준다.
그래도 여기서 만드는 이유는 **차시 폴더가 그 자체로 완결되어야** 하기 때문이다 —
manifest가 없으면 무엇이 자동 생성물이고 무엇이 사람이 채울 자리인지 폴더만 봐서는 모른다.

모델이 쓰지 않는다. asset 배치와 lesson.json의 참조에서 전부 유도되므로 지어낼 자리가 없고,
지어내면 그쪽 빌드가 덮어쓸 때 조용히 달라진다.

역할·타입 판정은 `manifestWriter.mjs`의 ROLE_MAP·getType을 그대로 옮긴 것이다.
**그쪽이 바뀌면 여기도 함께 고친다.**
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path


ROLE_MAP = (
    ("assets/character/", "character-emotion"),
    ("assets/customers/", "customer-character"),
    ("assets/backgrounds/", "background"),
    ("assets/ui/", "ui-component"),
    ("assets/photos/", "reallife-photo"),
    ("assets/audio/bgm/", "bgm"),
    ("assets/audio/narration/", "narration"),
    ("assets/audio/sfx/", "sfx"),
)

IMAGE_SUFFIXES = re.compile(r"\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
AUDIO_SUFFIXES = re.compile(r"\.(mp3|wav|ogg|m4a)$", re.IGNORECASE)

# 사람이 직접 넣어야 하는 것. 이 파이프라인은 사진과 오디오를 만들지 않는다.
MANUAL_PREFIXES = ("assets/photos/", "assets/audio/")


def build_manifest(lesson: dict, asset_paths: list[str], sizes: dict[str, int]) -> dict:
    """차시 폴더 기준 상대 경로 목록으로 manifest를 만든다.

    `asset_paths`는 실제로 놓인 이미지 경로이고, 오디오는 `lesson.json`의 `audioMap`에서
    나온다. 오디오 파일 자체는 이 파이프라인이 만들지 않으므로 크기 0의 manual-required로 남는다.
    """
    paths = list(dict.fromkeys(asset_paths + audio_paths(lesson)))
    entries = []
    for path in sorted(paths):
        size = sizes.get(path, 0)
        status = "manual-required" if is_manual(path) else "auto-generate"
        entry = {
            "path": path,
            "type": get_type(path),
            "role": get_role(path),
            "size": size,
            "status": status,
        }
        if status == "manual-required" and size == 0:
            label = "오디오 파일" if path.startswith("assets/audio/") else "수동 에셋"
            entry["todo"] = f"{label}을 직접 추가하세요: {path}"
        entries.append(entry)

    return {
        "id": lesson.get("id", ""),
        "title": lesson.get("title", ""),
        "version": "1.0.0",
        "created": date.today().isoformat(),
        "assets": entries,
        "manualRequired": [
            entry["path"]
            for entry in entries
            if entry["status"] == "manual-required" and entry["size"] == 0
        ],
    }


def audio_paths(lesson: dict) -> list[str]:
    """audioMap의 값(파일 경로)만 모은다. 식별자는 키이고 경로는 값이다."""
    audio_map = lesson.get("audioMap")
    if not isinstance(audio_map, dict):
        return []
    found = []
    for group in audio_map.values():
        if isinstance(group, dict):
            found += [value for value in group.values() if isinstance(value, str) and value]
        elif isinstance(group, str) and group:
            found.append(group)
    return [value for value in found if value.startswith("assets/")]


def is_manual(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in MANUAL_PREFIXES)


def get_role(path: str) -> str:
    for prefix, role in ROLE_MAP:
        if path.startswith(prefix):
            return role
    return "asset"


def get_type(path: str) -> str:
    if IMAGE_SUFFIXES.search(path):
        return "image"
    if AUDIO_SUFFIXES.search(path):
        return "audio"
    return "asset"


def collect_sizes(base_dir: Path, paths: list[str]) -> dict[str, int]:
    """놓일 파일의 크기를 원본에서 잰다. 같은 바이트를 복사하므로 배치 전에도 값이 같다."""
    sizes = {}
    for path in paths:
        candidate = base_dir / path
        if candidate.exists():
            sizes[path] = candidate.stat().st_size
    return sizes
