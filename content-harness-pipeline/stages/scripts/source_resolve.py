from __future__ import annotations

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_DIR / "source"


def teacher_root_from_input(input_data: dict | None) -> str:
    """input에서 teacher root 문자열만 꺼낸다.

    stage마다 `metadata.style_reference_set.root`를 파고드는 코드를 반복하지 않게 한다.
    `content_eval`처럼 input을 못 받는 stage는 빈 문자열이 되고, 그러면 common만 쓴다.
    """
    if not isinstance(input_data, dict):
        return ""
    reference_set = input_data.get("metadata", {}).get("style_reference_set")
    if not isinstance(reference_set, dict):
        return ""
    root = reference_set.get("root", "")
    return root if isinstance(root, str) else ""


def resolve_teacher_root(teacher_root: str | Path | None) -> Path | None:
    """input의 style_reference_set.root를 절대 경로로 만든다. 없으면 None."""
    if not teacher_root:
        return None
    root = Path(teacher_root)
    if not root.is_absolute():
        root = PROJECT_DIR / root
    root = root.resolve()
    return root if root.is_dir() else None


def shadowed_dirs(
    common_dir: Path,
    teacher_root: Path | None,
    subdir: str,
    marker: str,
) -> list[Path]:
    """이름이 같으면 teacher가 common을 **통째로** 덮는다.

    세부가 일반을 이긴다. 같은 `keypad`가 common과 teacher 양쪽에 있으면
    그 선생님 콘텐츠에서는 teacher 것만 쓴다.

    **병합하지 않고 통째로 교체한다.** 둘을 섞으면 teacher가 뺀 규칙이 common에서 되살아나고,
    무엇이 실제로 적용되는지 파일만 봐서는 알 수 없게 된다. 덮어쓸 거면 전부 책임진다.

    `marker`(component.md / example.md)가 있는 디렉토리만 항목으로 본다.
    `_shared`나 `example`처럼 부속 디렉토리가 섞여 들어오는 것을 막는다.
    """
    resolved: dict[str, Path] = {}
    for base in (common_dir, (teacher_root / subdir) if teacher_root else None):
        if base is None or not base.is_dir():
            continue
        for contract in sorted(base.glob(f"*/{marker}")):
            resolved[contract.parent.name] = contract.parent
    return [resolved[name] for name in sorted(resolved)]


def shadow_report(
    common_dir: Path,
    teacher_root: Path | None,
    subdir: str,
    marker: str,
) -> list[str]:
    """teacher가 덮은 이름 목록. 로그와 문서용이고 판정에는 쓰지 않는다."""
    if teacher_root is None:
        return []
    teacher_dir = teacher_root / subdir
    if not teacher_dir.is_dir():
        return []
    common_names = {p.parent.name for p in common_dir.glob(f"*/{marker}")}
    teacher_names = {p.parent.name for p in teacher_dir.glob(f"*/{marker}")}
    return sorted(common_names & teacher_names)
