from __future__ import annotations

from pathlib import Path


# catalog 항목 하나를 이루는 필드.
# reusable-source-design.md 3.2의 항목 템플릿과 같은 이름을 쓴다.
SCALAR_FIELDS = ("Path", "Category", "Status", "Role")
LIST_FIELDS = ("Use", "Avoid")

SUPPORTED_CATEGORIES = ("backgrounds", "characters", "props", "ctas")


def load_catalog(root: Path) -> dict[str, list[dict]]:
    """source/[teacher]의 md catalog를 스캔해 범주별 reference 목록을 만든다.

    input.json에 categories를 손으로 적지 않게 하는 것이 목적이다.
    손으로 적으면 차시마다 같은 use/avoid를 다시 쓰게 되고, 그 사본이 catalog와 갈라진다.
    components/craft-examples 축이 프롬프트에 목록을 손으로 적지 않는 것과 같은 이유다.

    항목은 md의 `## 제목` 하나가 하나다. `- Path:`가 없는 절은 항목이 아니라 설명으로 보고 건너뛴다.
    따라서 사람이 읽는 산문과 기계가 읽는 항목이 한 파일에 공존할 수 있다.
    """
    catalog: dict[str, list[dict]] = {category: [] for category in SUPPORTED_CATEGORIES}
    if not root.is_dir():
        return catalog

    for md_path in sorted(root.glob("*.md")):
        for entry in parse_catalog_md(md_path):
            category = entry.pop("category", "")
            if category not in catalog:
                raise ValueError(
                    f"unsupported category '{category}' in {md_path.name}#{entry.get('name')}"
                    f" (지원: {', '.join(SUPPORTED_CATEGORIES)})"
                )
            if entry.pop("status", "") == "deprecated":
                continue
            catalog[category].append(entry)
    return catalog


def parse_catalog_md(path: Path) -> list[dict]:
    """md에서 `## 제목` + 머리 목록 형태의 catalog 항목만 뽑는다."""
    entries: list[dict] = []
    current: dict | None = None
    current_list: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()

        if line.startswith("## "):
            _append_if_entry(entries, current)
            current = {"name": line[3:].strip()}
            current_list = None
            continue
        if current is None:
            continue
        if line.startswith("#"):
            # 더 얕은 제목을 만나면 그 항목은 끝난다. 하위 제목(### Poses 등)은 본문이므로 건드리지 않는다.
            if not line.startswith("###"):
                _append_if_entry(entries, current)
                current = None
                current_list = None
            continue

        if line.startswith("- "):
            key, _, value = line[2:].partition(":")
            key = key.strip()
            value = _strip_code_ticks(value.strip())
            if key in SCALAR_FIELDS:
                current[key.lower()] = value
                current_list = None
            elif key in LIST_FIELDS:
                current_list = key.lower()
                current[current_list] = [value] if value else []
            else:
                current_list = None
        elif current_list and line.startswith(("  - ", "    - ")):
            current[current_list].append(_strip_code_ticks(line.strip()[2:]))

    _append_if_entry(entries, current)
    return entries


def _append_if_entry(entries: list[dict], candidate: dict | None) -> None:
    """`Path`가 있는 절만 catalog 항목으로 본다."""
    if candidate and candidate.get("path"):
        entries.append(
            {
                "name": candidate.get("name", ""),
                "path": candidate["path"],
                "category": candidate.get("category", ""),
                "status": candidate.get("status", ""),
                "role": candidate.get("role", ""),
                "use": " / ".join(candidate.get("use", [])),
                "avoid": " / ".join(candidate.get("avoid", [])),
            }
        )


def _strip_code_ticks(value: str) -> str:
    return value.strip().strip("`").strip()
