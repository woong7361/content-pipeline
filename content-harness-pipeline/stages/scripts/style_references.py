from __future__ import annotations

import json
from pathlib import Path


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

    categories = raw_set.get("categories")
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


def _empty_reference_set() -> dict:
    return {
        "enabled": False,
        "id": "",
        "must_follow": False,
        "root": "",
        "usage_policy": {},
        "categories": {category: [] for category in SUPPORTED_CATEGORIES},
    }
