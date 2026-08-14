from __future__ import annotations

import re

from pathlib import Path

from stages.scripts.source_resolve import resolve_teacher_root, shadowed_dirs

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
COMPONENTS_DIR = PROJECT_DIR / "source" / "common" / "components"
BASE_CSS = COMPONENTS_DIR / "_shared" / "base.css"

# preview 전용 디렉토리는 최종 output에 들어가지 않는다.
EXCLUDED_DIRS = ("_shared", "example")

COMMON_CSS_NAME = "common.css"
COMMON_JS_NAME = "common.js"

CSS_LINK = f'<link rel="stylesheet" href="{COMMON_CSS_NAME}">'
JS_SCRIPT = f'<script src="{COMMON_JS_NAME}"></script>'

BANNER = (
    "/* 이 파일은 source/common/components에서 코드가 생성한다.\n"
    "   여기를 고쳐도 다음 stage가 끝나면 원본으로 되돌아간다.\n"
    "   이 차시에서만 값을 바꾸려면 index.html의 <style>에서 오버라이드한다.\n"
    "   <link>보다 뒤에 오므로 소스 순서로 이긴다. */\n"
)
JS_BANNER = BANNER.replace("/*", "/*", 1)


def component_dirs(teacher_root: str | Path | None = None) -> list[Path]:
    """같은 이름이면 teacher가 common을 덮는다. 세부가 일반을 이긴다."""
    if not COMPONENTS_DIR.is_dir():
        return []
    return [
        d
        for d in shadowed_dirs(
            COMPONENTS_DIR, resolve_teacher_root(teacher_root), "components", "component.md"
        )
        if d.name not in EXCLUDED_DIRS
    ]


def build_css(teacher_root: str | Path | None = None) -> str:
    """base.css + 전 컴포넌트 style.css.

    어떤 컴포넌트를 썼는지 탐지하지 않는다. 이 파일은 그 run이 쓸 수 있는 **공용 라이브러리**다.
    안 쓰는 `.c-keypad` 규칙은 아무것도 매치하지 않으므로 무해하고, 탐지를 넣는 순간
    `data-component` 이름과 디렉토리명의 불일치, 마크업 없는 runtime 컴포넌트(scene-controller),
    콘텐츠 CSS에 남은 오버라이드로 인한 오탐을 전부 다뤄야 한다.
    """
    parts = [BANNER, BASE_CSS.read_text(encoding="utf-8")]
    for directory in component_dirs(teacher_root):
        css = directory / "style.css"
        if css.is_file():
            parts.append(f"/* --- {directory.name} --- */\n{css.read_text(encoding='utf-8')}")
    return "\n".join(parts).rstrip() + "\n"


def build_js(teacher_root: str | Path | None = None) -> str:
    """전 컴포넌트 behavior.js. window.Common* 전역만 등록하고 아무것도 실행하지 않는다."""
    parts = [BANNER]
    for directory in component_dirs(teacher_root):
        js = directory / "behavior.js"
        if js.is_file():
            parts.append(f"/* --- {directory.name} --- */\n{js.read_text(encoding='utf-8')}")
    return "\n".join(parts).rstrip() + "\n"


def emit_common(run_dir: Path, teacher_root: str | Path | None = None) -> dict:
    """output/common.css와 output/common.js를 원본에서 다시 쓴다.

    검증이 아니라 덮어쓰기다. 모델이 이 파일을 고쳤든 지웠든 원본으로 돌아간다.
    되돌릴 수 있는 것은 되돌리고, 되돌릴 수 없는 것(index.html)만 검증한다.

    반환값의 `drifted`는 게이트가 아니라 로그다. 게이트로 만들면 정당한 오버라이드 시도까지
    run을 죽인다. 여기서 알고 싶은 것은 "모델이 무엇을 바꾸려 했는가"이고,
    같은 항목이 반복해서 나오면 그건 모델이 틀린 게 아니라 컴포넌트가 부족하다는 신호다.
    """
    output_dir = run_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    drifted = []
    for name, content in ((COMMON_CSS_NAME, build_css(teacher_root)), (COMMON_JS_NAME, build_js(teacher_root))):
        target = output_dir / name
        previous = target.read_text(encoding="utf-8") if target.is_file() else None
        if previous is not None and previous != content:
            # 되돌리기 전에 원본을 남긴다. 글자 수만 적으면 "무엇을 바꾸려 했는지"를 알 수 없고,
            # 그 답이 곧 컴포넌트에 무엇이 부족한지에 대한 답이다.
            rejected = output_dir / f"{name}.rejected"
            rejected.write_text(previous, encoding="utf-8")
            drifted.append(
                {
                    "file": name,
                    "previous_chars": len(previous),
                    "restored_chars": len(content),
                    "rejected_copy": rejected.name,
                }
            )
        target.write_text(content, encoding="utf-8")

    return {"drifted": drifted, "files": [COMMON_CSS_NAME, COMMON_JS_NAME]}


def check_html_links(html_path: Path) -> list[str]:
    """index.html이 common.css/common.js를 실어 오는지 확인한다.

    이건 진짜 검증이다. index.html은 모델이 소유하므로 코드가 되돌릴 수 없고,
    이 두 줄이 없으면 컴포넌트가 통째로 빠진 화면이 나온다.

    순서까지 본다. CSS는 소스 순서로 우선순위가 갈리므로 `<link>`가 콘텐츠 `<style>`보다
    앞에 있어야 콘텐츠가 컴포넌트를 오버라이드할 수 있다. 뒤집히면 반대가 된다.
    """
    if not html_path.is_file():
        return [f"html file missing: {html_path.name}"]

    # 주석을 지운 마크업만 본다. 계약이 순서를 강조하므로 모델이 그 규칙을 주석으로 부연하는데
    # (실측: `<!-- 반드시 콘텐츠 <style>보다 앞에 온다 -->`), 주석 속 문구를 태그로 읽으면
    # 계약을 지킨 HTML이 REJECT된다. 반대로 주석 처리된 <link>를 "실려 있다"로 읽어도 안 된다.
    html = re.sub(r"<!--.*?-->", "", html_path.read_text(encoding="utf-8"), flags=re.S)
    errors = []

    css_at = html.find(f'href="{COMMON_CSS_NAME}"')
    if css_at < 0:
        errors.append(f"index.html must load {COMMON_CSS_NAME}: add {CSS_LINK}")
    if f'src="{COMMON_JS_NAME}"' not in html:
        errors.append(f"index.html must load {COMMON_JS_NAME}: add {JS_SCRIPT}")

    style_at = html.find("<style")
    if css_at >= 0 and style_at >= 0 and style_at < css_at:
        errors.append(
            f"{COMMON_CSS_NAME} link must come before the content <style> block "
            "(source order decides the cascade; content must be able to override components)"
        )
    return errors
