from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.source_resolve import resolve_teacher_root, shadowed_dirs


PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
CRAFT_EXAMPLES_DIR = PROJECT_DIR / "source" / "common" / "craft-examples"
CRAFT_EXAMPLES_RULES = CRAFT_EXAMPLES_DIR / "CLAUDE.md"

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

# example.md에서 프롬프트로 넘길 필드.
# manifest의 일은 "어떤 예시를 열어볼지 고르게 하는 것"까지다.
# 구조·재질 논리의 상세는 stage가 고른 뒤 example.md와 이미지를 직접 연다.
LIST_FIELDS = ("Images", "Applies to", "Take", "Do not take")
SCALAR_FIELDS = ("Type", "Status", "Source")


def load_rules() -> str:
    """craft example 축 전체의 우선순위와 합격 판정.

    이 블록만은 manifest 경로로 넘기지 않고 프롬프트에 통째로 싣는다.
    common_components의 base.css와 같은 이유다 — 여기 적힌 "art_direction이 예시를
    이긴다"가 빠지면 모델이 identity_context 습관대로 예시의 팔레트와 모티프를 복제해
    그 run의 art_direction을 덮어쓴다. 개별 예시는 그렇지 않아서 경로만 넘긴다.
    """
    return CRAFT_EXAMPLES_RULES.read_text(encoding="utf-8")


def parse_example_md(path: Path) -> dict:
    """example.md의 머리 목록만 얕게 읽는다.

    `## 상세` 이후는 읽지 않는다. stage가 이 예시를 고른 뒤 직접 읽는다.
    파싱 규칙은 common_components.parse_component_md와 같다.
    """
    data: dict = {"name": path.parent.name, "title": ""}
    current_list: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and not data["title"]:
            data["title"] = line[2:].strip()
            continue
        if line.startswith("## "):
            break
        if line.startswith("- "):
            body = line[2:]
            key, _, value = body.partition(":")
            key = key.strip()
            value = value.strip()
            if key in SCALAR_FIELDS:
                data[key.lower().replace(" ", "_")] = value
                current_list = None
            elif key in LIST_FIELDS:
                current_list = key.lower().replace(" ", "_")
                data[current_list] = []
                if value:
                    data[current_list].append(value)
            else:
                current_list = None
        elif current_list and line.startswith(("  - ", "    - ")):
            data[current_list].append(line.strip()[2:])
    return data


def list_example_images(example_dir: Path) -> list[str]:
    return [
        path.relative_to(example_dir).as_posix()
        for path in sorted(example_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]


def load_examples(teacher_root: str | Path | None = None) -> list[dict]:
    """source/common/craft-examples를 스캔해 manifest를 만든다.

    목록을 프롬프트에 손으로 적지 않는 이유는 common_components와 같다.
    예시가 늘어날 때 프롬프트와 디렉토리가 서로 어긋나는 것을 막는다.
    """
    if not CRAFT_EXAMPLES_DIR.is_dir():
        return []
    examples = []
    for example_dir in shadowed_dirs(
        CRAFT_EXAMPLES_DIR, resolve_teacher_root(teacher_root), "craft-examples", "example.md"
    ):
        contract = example_dir / "example.md"
        entry = parse_example_md(contract)
        entry["dir"] = str(example_dir.resolve())
        entry["contract"] = str(contract.resolve())
        # example.md가 적은 Images는 사람이 읽는 목록이고, 실제 존재하는 파일은 스캔이 정한다.
        entry["images"] = list_example_images(example_dir)
        examples.append(entry)
    return examples


def build_craft_examples_json(teacher_root: str | Path | None = None) -> str:
    examples = load_examples(teacher_root)
    payload = {
        "enabled": bool(examples),
        "root": str(CRAFT_EXAMPLES_DIR.resolve()),
        "rules": "이 payload 앞의 CRAFT_EXAMPLES_RULES 블록을 따른다. 특히 art_direction이 예시 이미지보다 우선한다.",
        "how_to_choose": "만들려는 asset이 어떤 예시의 applies_to에 해당하는지 보고, 해당하면 그 예시의 contract와 images를 실제로 열어 확인한다.",
        "examples": examples,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_craft_examples_section(teacher_root: str | Path | None = None) -> str:
    """글자를 이미지에 굽는 asset을 만드는 stage 프롬프트에 붙는 블록."""
    return f"""CRAFT_EXAMPLES_RULES:
{load_rules()}

CRAFT_EXAMPLES_JSON:
{build_craft_examples_json(teacher_root)}"""
