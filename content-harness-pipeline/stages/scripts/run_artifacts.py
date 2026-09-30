"""초안 파이프라인 화면에서 **단계별 산출물**을 바로 열어 보게 — 어느 단계가 어떤 파일을 냈는지 목록을 만든다.

`lesson_desk.py` 의 /pipeline 화면이 쓴다(2026-09-30 사용자 요청). 읽기만 한다.
파일 목록은 단계 순서로, 있는 것만 낸다. 그림은 썸네일로 늘어놓고 누르면 크게 본다.

열 수 있는 것은 아래 확장자뿐이고, 경로는 반드시 run 폴더 안이어야 한다(`resolve`).
"""

from __future__ import annotations

from pathlib import Path

TEXT_SUFFIXES = {".md", ".json", ".css", ".js", ".txt", ".jsonl", ".log"}
IMAGE_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg"}
OPEN_SUFFIXES = TEXT_SUFFIXES | IMAGE_SUFFIXES | {".pdf"}

# (단계 이름, 보일 이름, 파일 목록, 그림 glob) — 파이프라인 순서
GROUPS: list[tuple[str, str, list[str], list[str]]] = [
    ("storyboard", "원본 스토리보드", ["storyboard.pdf", "storyboard.md"], ["review/storyboard-pages/*.png"]),
    ("senior_planner", "기획", ["planning/content-plan.md"], []),
    ("senior_designer", "디자인", ["design/wireframe.md", "design/concept.md"], []),
    ("interview", "인터뷰", ["interview/questions.md", "interview/questions-new.md"], []),
    ("interview_brief", "제작 지침", ["planning/production-guide.md"], []),
    ("lesson_spec", "요구 명세", ["spec/lesson-spec.json"], []),
    ("visual_design", "비주얼 설계", ["design/visual-design.md", "design/asset-plan.md", "design/asset-plan.json"],
     ["design/characters/*.png", "design/characters/*.webp"]),
    ("design_review", "디자인 검토", ["review/design-review-log.md", "review/design-review-checklist.md"], []),
    ("senior_developer", "개발", ["lesson/lesson.json", "lesson/page-map.md", "lesson/development-notes.md",
                                "lesson/player-ext.css", "lesson/player-ext.js"], []),
    ("asset_render", "그림 굽기", [], ["lesson/assets/**/*.png", "lesson/assets/**/*.webp", "lesson/assets/**/*.jpg"]),
    ("verify", "화면 검증", ["verify/report.md", "verify/to-developer.md", "verify/to-asset.md", "verify/to-storyboard.md",
                            "verify/to-runtime.md", "verify/to-human.md"], ["verify/screens/*.png"]),
    ("usage", "사용량", ["usage-report.md"], []),
]


def _entry(run_dir: Path, path: Path) -> dict:
    stat = path.stat()
    return {"path": path.relative_to(run_dir).as_posix(), "name": path.name, "size": stat.st_size,
            "mtime": int(stat.st_mtime), "kind": "image" if path.suffix.lower() in IMAGE_SUFFIXES else
            ("pdf" if path.suffix.lower() == ".pdf" else "text")}


def artifacts(run_dir: Path) -> list[dict]:
    """[{stage, label, files: [...], images: [...]}] — 파일이 하나도 없는 단계는 뺀다."""
    out = []
    for stage, label, files, globs in GROUPS:
        found = [_entry(run_dir, run_dir / rel) for rel in files if (run_dir / rel).is_file()]
        images: list[dict] = []
        seen = set()
        for pattern in globs:
            for path in sorted(run_dir.glob(pattern)):
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path not in seen:
                    seen.add(path)
                    images.append(_entry(run_dir, path))
        if found or images:
            out.append({"stage": stage, "label": label, "files": found, "images": images})
    return out


def safe_path(run_dir: Path, rel: str) -> Path | None:
    """run 폴더 안의, 열어도 되는 확장자인 파일이면 그 경로. 아니면 None."""
    if not rel:
        return None
    path = (run_dir / rel).resolve()
    root = run_dir.resolve()
    if root not in path.parents or not path.is_file() or path.suffix.lower() not in OPEN_SUFFIXES:
        return None
    return path
