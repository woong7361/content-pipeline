from __future__ import annotations

import hashlib
import json
from pathlib import Path

from stages.scripts.teacher_source import load_catalog


STYLE_REFERENCE_METADATA_KEY = "style_reference_set"
SUPPORTED_CATEGORIES = ("backgrounds", "characters", "props", "ctas")
SUPPORTED_IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}


def resolve_style_reference_set(input_data: dict, project_dir: Path) -> dict:
    """Resolve and validate optional style references without changing old inputs."""
    metadata = input_data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("input.metadata must be an object")

    raw_set = metadata.get(STYLE_REFERENCE_METADATA_KEY)
    if raw_set is None:
        return _empty_reference_set()
    if not isinstance(raw_set, dict):
        raise ValueError(f"input.metadata.{STYLE_REFERENCE_METADATA_KEY} must be an object")

    reference_id = raw_set.get("id", "")
    if not isinstance(reference_id, str):
        raise ValueError(f"input.metadata.{STYLE_REFERENCE_METADATA_KEY}.id must be a string")

    must_follow = raw_set.get("must_follow", False)
    if not isinstance(must_follow, bool):
        raise ValueError(
            f"input.metadata.{STYLE_REFERENCE_METADATA_KEY}.must_follow must be a boolean"
        )

    root_value = raw_set.get("root")
    if not isinstance(root_value, str) or not root_value.strip():
        raise ValueError(f"input.metadata.{STYLE_REFERENCE_METADATA_KEY}.root is required")
    root = Path(root_value)
    if not root.is_absolute():
        root = project_dir / root
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"style reference root not found: {root}")

    # categories를 생략하면 root의 md catalog를 스캔한다.
    # 이렇게 두는 이유는 프롬프트에 컴포넌트 목록을 손으로 적지 않는 것과 같다 —
    # 손으로 적으면 차시마다 같은 use/avoid를 다시 쓰게 되고 그 사본이 catalog와 갈라진다.
    # 명시하면 그대로 쓴다. catalog 밖의 이미지를 한 번만 끼워 넣는 경우가 있고,
    # 기존 input이 계속 동작해야 한다.
    categories = raw_set.get("categories")
    if categories is None:
        categories = load_catalog(root)
    if not isinstance(categories, dict):
        raise ValueError(
            f"input.metadata.{STYLE_REFERENCE_METADATA_KEY}.categories must be an object"
        )
    unknown_categories = sorted(set(categories) - set(SUPPORTED_CATEGORIES))
    if unknown_categories:
        raise ValueError(f"unsupported style reference categories: {unknown_categories}")

    resolved_categories: dict[str, list[dict]] = {}
    for category in SUPPORTED_CATEGORIES:
        raw_items = categories.get(category, [])
        if not isinstance(raw_items, list):
            raise ValueError(f"style reference category '{category}' must be an array")
        resolved_categories[category] = [
            _resolve_reference_item(item=item, category=category, root=root)
            for item in raw_items
        ]

    if must_follow and not any(resolved_categories.values()):
        raise ValueError("must_follow style reference set must contain at least one image")

    role_conflicts = find_component_asset_conflicts(resolved_categories)
    if role_conflicts:
        raise ValueError(
            "style reference conflicts with a component asset — 한 파일이 두 역할을 가질 수 없습니다. "
            "컴포넌트 asset은 output/assets로 **복사**되고, 화풍 참조는 **참조만** 합니다. "
            "컴포넌트가 이미 소유한 파일이면 catalog에서 빼거나 Status를 deprecated로 둡니다: "
            + "; ".join(role_conflicts)
        )

    usage_policy = raw_set.get("usage_policy", {})
    if not isinstance(usage_policy, dict):
        raise ValueError("style reference usage_policy must be an object")

    return {
        "enabled": True,
        "id": reference_id,
        "must_follow": must_follow,
        "root": str(root),
        "usage_policy": usage_policy,
        "categories": resolved_categories,
    }


def build_style_reference_prompt(input_data: dict, project_dir: Path) -> str:
    resolved = resolve_style_reference_set(input_data=input_data, project_dir=project_dir)
    return json.dumps(resolved, ensure_ascii=False, indent=2)


def _resolve_reference_item(item: object, category: str, root: Path) -> dict:
    if not isinstance(item, dict):
        raise ValueError(f"style reference item in '{category}' must be an object")

    path_value = item.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise ValueError(f"style reference item in '{category}' requires path")
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"style reference path escapes its root: {resolved}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"style reference image not found: {resolved}")
    if resolved.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(f"unsupported style reference image format: {resolved}")

    result = {"path": str(resolved)}
    for field in ("role", "use", "avoid"):
        value = item.get(field, "")
        if not isinstance(value, str):
            raise ValueError(f"style reference item field '{field}' must be a string")
        result[field] = value
    return result


def find_component_asset_conflicts(resolved_categories: dict[str, list[dict]]) -> list[str]:
    """화풍 참조가 공용 컴포넌트 asset과 같은 파일인지 본다.

    두 디렉토리의 계약이 정반대다. 컴포넌트 `assets/`는 `output/assets/`로 **복사**하라는 것이고
    (`prompts/common_html_contract.md`), teacher `assets/`는 **참조만** 하고 복사하지 말라는 것이다.
    같은 파일이 양쪽에 있으면 어느 계약이 맞는지 판정할 수 없다.

    내용으로 비교한다. 파일명이 달라도(`activity-cta-body` vs `cta-activity-body`) 같은 그림이면
    같은 문제이고, 실제로 그렇게 어긋났다.

    이걸 안 잡으면 run은 정상 동작하지만 design_review가 "참조를 복제했다"는 오판을 낸다.
    builder는 계약대로 컴포넌트 asset을 복사했을 뿐인데 결과 파일이 참조와 같기 때문이다.
    """
    component_hashes = _component_asset_hashes()
    if not component_hashes:
        return []

    conflicts = []
    for category, items in resolved_categories.items():
        for item in items:
            path = Path(item["path"])
            digest = _file_digest(path)
            owner = component_hashes.get(digest)
            if owner is not None:
                conflicts.append(f"{category}/{path.name} == components/{owner}")
    return conflicts


def _component_asset_hashes() -> dict[str, str]:
    """컴포넌트 asset의 내용 해시. `example/`은 조립 확인 전용이라 output에 안 나가므로 뺀다."""
    root = Path(__file__).resolve().parent.parent.parent / "source" / "common" / "components"
    if not root.is_dir():
        return {}
    hashes = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "example":
            continue
        hashes[_file_digest(path)] = relative.as_posix()
    return hashes


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _empty_reference_set() -> dict:
    return {
        "enabled": False,
        "id": "",
        "must_follow": False,
        "root": "",
        "usage_policy": {},
        "categories": {category: [] for category in SUPPORTED_CATEGORIES},
    }
