from __future__ import annotations

import json
from pathlib import Path

from stages.scripts.source_resolve import resolve_teacher_root, shadowed_dirs


PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
COMPONENTS_DIR = PROJECT_DIR / "source" / "common" / "components"
BASE_CSS = COMPONENTS_DIR / "_shared" / "base.css"

# component.md에서 프롬프트로 넘길 필드.
# manifest의 일은 "어떤 컴포넌트를 열어볼지 고르게 하는 것"까지다.
# slot/state/DOM 계약은 stage가 고른 뒤 component.md를 직접 읽는다.
LIST_FIELDS = ("Runtime API", "Use when", "Avoid")
SCALAR_FIELDS = ("Type", "Status", "Final output")

# preview/example 전용 파일은 최종 output에 들어가지 않으므로 목록에서 뺀다.
EXCLUDED_FILES = ("preview.html",)


def load_base_css() -> str:
    """디자인 토큰 목록. **참고용이지 옮겨 적을 원본이 아니다.**

    실제 CSS는 `component_bundle.emit_common()`이 `output/common.css`로 내보낸다.
    그런데도 이 블록을 프롬프트에 싣는 이유는, 모델이 `var(--fs-xs)`처럼 토큰을 **참조**하려면
    어떤 토큰이 있는지 알아야 하기 때문이다. 이름을 모르면 raw 값을 새로 만든다.

    한때는 "builder가 :root를 처음 선언하는 주체"라서 실었지만 더는 아니다.
    선언은 코드가 하고, 여기 있는 것은 이름 목록으로서의 역할만 남았다.
    """
    return BASE_CSS.read_text(encoding="utf-8")


def parse_component_md(path: Path) -> dict:
    """component.md의 머리 부분만 얕게 읽는다.

    전체를 구조화하지 않는다. stage가 어떤 컴포넌트를 열어볼지 고르는 데 필요한
    만큼만 뽑고, 실제 계약은 stage가 이 파일을 직접 읽어 확인한다.
    """
    data: dict = {"name": path.parent.name, "title": ""}
    current_list: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and not data["title"]:
            data["title"] = line[2:].strip()
            continue
        if line.startswith("## "):
            break  # 머리 목록이 끝났다. 이후 본문은 stage가 직접 읽는다.
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


def list_component_files(component_dir: Path) -> list[str]:
    files = []
    for path in sorted(component_dir.rglob("*")):
        if path.is_dir() or path.name in EXCLUDED_FILES:
            continue
        files.append(path.relative_to(component_dir).as_posix())
    return files


def load_components(teacher_root: str | Path | None = None) -> list[dict]:
    """컴포넌트 manifest를 만든다. 같은 이름이면 teacher가 common을 덮는다.

    목록을 프롬프트에 손으로 적지 않는 이유는 common_html_contract.md가 있는 이유와 같다.
    컴포넌트가 늘어날 때 세 stage 프롬프트가 서로 어긋나는 것을 막는다.
    """
    if not COMPONENTS_DIR.is_dir():
        return []
    components = []
    for component_dir in shadowed_dirs(
        COMPONENTS_DIR, resolve_teacher_root(teacher_root), "components", "component.md"
    ):
        contract = component_dir / "component.md"
        entry = parse_component_md(contract)
        entry["dir"] = str(component_dir.resolve())
        entry["contract"] = str(contract.resolve())
        entry["files"] = list_component_files(component_dir)
        components.append(entry)
    return components


def build_common_components_json(teacher_root: str | Path | None = None) -> str:
    components = load_components(teacher_root)
    payload = {
        "enabled": bool(components),
        "root": str(COMPONENTS_DIR.resolve()),
        "rules": "prompts/common_html_contract.md 의 '공용 컴포넌트 재사용' 절을 따른다.",
        "components": components,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_common_components_section(teacher_root: str | Path | None = None) -> str:
    """세 HTML stage 프롬프트에 공통으로 붙는 블록."""
    return f"""COMMON_BASE_CSS:
{load_base_css()}

COMMON_COMPONENTS_JSON:
{build_common_components_json(teacher_root)}"""
