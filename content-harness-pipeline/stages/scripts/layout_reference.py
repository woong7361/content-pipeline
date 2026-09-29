"""배포 중인 차시의 `player-ext.css`에서 **배치 골격만** 뽑아 프롬프트에 싣는다.

왜 필요한가 — 지금까지 프롬프트가 준 것은 클래스 이름 389개뿐이었다. 이름만으로는
"어디에 무엇을 놓는가"를 알 수 없어서, 모델은 base 를 색만 바꾼 CSS 를 냈다.
실측(2026-09-09) — 우리 산출물은 `background`·`color`·`border` 위주 27줄이었고
배포 중인 4-1/01 은 `width`·`padding`·`position`·`display` 위주 1,501줄이었다.

**문서에 예시를 적어 두지 않는다.** 원자 레지스트리·클래스 이름과 같은 이유다 — 사본은
어긋난다. 차시가 개선되면 참조도 같이 좋아져야 한다.

색·그림자·글꼴은 뺀다. 배치를 배우게 하는 것이 목적이고, 그것까지 실으면 프롬프트만
커지고 모델은 참조를 베끼려 든다. 주석은 **남긴다** — 왜 그렇게 잡았는지가 값이다.
"""

from __future__ import annotations

import re
from pathlib import Path


# 자리를 정하는 속성. 여기 없는 선언은 뺀다.
GEOMETRY_PROPERTIES = (
    "position", "inset", "top", "right", "bottom", "left", "z-index",
    "display", "flex", "flex-direction", "flex-wrap", "flex-grow", "flex-shrink", "flex-basis",
    "grid", "grid-template", "grid-template-columns", "grid-template-rows",
    "grid-column", "grid-row", "grid-area", "place-items", "place-content",
    "justify-content", "justify-items", "justify-self",
    "align-items", "align-content", "align-self", "gap", "row-gap", "column-gap", "order",
    "width", "min-width", "max-width", "height", "min-height", "max-height",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "padding-block", "padding-inline",
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "margin-block", "margin-inline",
    "aspect-ratio", "object-fit", "overflow", "overflow-x", "overflow-y",
    "transform", "translate", "scale", "container-type", "writing-mode",
)

RULE_PATTERN = re.compile(r"(?P<selector>[^{}]+)\{(?P<body>[^{}]*)\}", re.DOTALL)

# 문제 화면의 배치만 본다. 헤더·툴바·홈 버튼은 base 가 소유하고 차시마다 같으므로
# 참조로서 값이 없다 — 처음 뽑았을 때 `.topbar`·`.btn-home`·`.lesson-header-title` 이
# 앞자리를 다 차지했다(2026-09-09 실측).
PROBLEM_SCREEN = re.compile(
    r"#app\.[\w-]+"          # 상태 클래스로 스코프한 규칙 — 배치를 나누는 자리다
    r"|\.pa-[\w-]+"          # 문제 원자가 그리는 것
    r"|\.kp-[\w-]+"          # 키패드
    r"|\.charzone|\.bubble|\.speech|\.prob-panel|\.stage-"
)
SKIP_SELECTOR = re.compile(r"\.topbar|\.btn-home|\.lesson-header|\.header-|\.drawer|\.settings")
# 참조를 고를 때는 **문제 원자를 실제로 배치한 차시**를 본다. 우리가 그리는 화면이 그것이다.
ATOM_SELECTOR = re.compile(r"\.pa-[\w-]+|\.kp-[\w-]+|\.prob-panel")
COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
DECLARATION_PATTERN = re.compile(r"([-a-zA-Z]+)\s*:\s*([^;]+);?")


def extract_layout(source: str, max_chars: int = 9000) -> str:
    """기하 속성을 가진 규칙만 남긴 CSS 를 낸다. 규칙 앞의 주석은 함께 가져온다."""
    kept: list[str] = []
    used = 0
    cursor = 0

    for match in RULE_PATTERN.finditer(source):
        selector = match.group("selector")
        body = match.group("body")

        declarations = [
            f"  {name}: {value.strip()};"
            for name, value in DECLARATION_PATTERN.findall(body)
            if name.strip() in GEOMETRY_PROPERTIES
        ]
        if not declarations:
            cursor = match.end()
            continue

        # 이 규칙 바로 앞에 붙은 주석을 함께 가져온다. 왜 그렇게 잡았는지가 값이다.
        lead = source[cursor:match.start()]
        comments = COMMENT_PATTERN.findall(lead)
        note = comments[-1].strip() if comments else ""

        selector_text = COMMENT_PATTERN.sub("", selector).strip()
        if (
            not selector_text
            or SKIP_SELECTOR.search(selector_text)
            or not PROBLEM_SCREEN.search(selector_text)
        ):
            cursor = match.end()
            continue

        block = (f"{note}\n" if note else "") + selector_text + " {\n" + "\n".join(declarations) + "\n}\n"
        if used + len(block) > max_chars:
            break
        kept.append(block)
        used += len(block)
        cursor = match.end()

    return "\n".join(kept)


def pick_reference_lesson(gyo6_root: Path | None) -> Path | None:
    """배치를 가장 많이 잡아 둔 차시를 고른다.

    "가장 많이" 는 컨테이너 쿼리 단위(`cqw`/`cqh`)의 개수로 잰다. 그 단위를 많이 쓴
    차시가 무대에 비례해 자리를 잡아 둔 차시다. 손으로 고르지 않는 이유는 다른 스캔
    모듈과 같다 — 차시는 계속 늘어나고, 사본은 어긋난다.
    """
    if gyo6_root is None:
        return None
    lessons = Path(gyo6_root) / "lessons"
    if not lessons.is_dir():
        return None

    best: tuple[int, Path] | None = None
    for css in lessons.glob("*/*/player-ext.css"):
        try:
            source = css.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # 문제 화면 배치를 가장 많이 잡아 둔 차시를 고른다. cq 총량으로 재면
        # 헤더 치장이 많은 차시가 뽑힌다(실측 — 1-2/04 가 그렇게 뽑혔다).
        score = sum(
            1
            for rule in RULE_PATTERN.finditer(source)
            if ATOM_SELECTOR.search(rule.group("selector"))
            and not SKIP_SELECTOR.search(rule.group("selector"))
            and "cq" in rule.group("body")
        )
        if best is None or score > best[0]:
            best = (score, css)
    return best[1] if best and best[0] > 0 else None


def build_layout_reference_section(gyo6_root: Path | None, max_chars: int = 9000) -> str:
    css = pick_reference_lesson(gyo6_root)
    if css is None:
        return ""
    try:
        source = css.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    skeleton = extract_layout(source, max_chars=max_chars)
    if not skeleton:
        return ""
    slot = css.parent.parent.name + "/" + css.parent.name
    return (
        "LAYOUT_REFERENCE:\n"
        f"배포 중인 차시 `{slot}` 의 `player-ext.css` 에서 **자리를 정하는 규칙만** 뽑은 것이다.\n"
        "색·그림자·글꼴은 뺐다 — 배울 것은 배치다. 주석은 왜 그렇게 잡았는지를 말한다.\n"
        "**베끼지 않는다.** 이 차시의 화면은 다르다. 가져올 것은 다음 셋이다.\n"
        "  1. 길이를 `cqw`/`cqh` 로 잡는다(무대가 16:9 컨테이너다). px 는 테두리 같은 잔값만.\n"
        "  2. 문제 패널을 무대 안에 **자리 잡아 놓는다**(`position:absolute` + 네 변 + "
        "`height:fit-content` + `margin-block:auto`). 흐름에 맡기지 않는다.\n"
        "  3. 차시가 그림을 주는 자리는 base 의 상자·테두리를 **지운다**"
        "(`background:none; border:0; padding:0`). 그래야 그림만 남는다.\n"
        "```css\n"
        f"{skeleton}"
        "```\n"
    )
