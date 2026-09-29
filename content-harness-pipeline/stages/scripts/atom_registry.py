"""gyo6_content 런타임의 `PROBLEM_ATOMS` 레지스트리를 직접 읽는다.

**문서의 표를 복제하지 않는다.** gyo6_content 의 `agent/lessonParser.mjs` 가 같은 이유로 같은 일을 한다 —
어휘표에 이름이 있다는 것과 화면에 나온다는 것은 다르고, 둘이 어긋난 채 검증을 통과해서
문제가 열거된 lesson.json 이 **빈 화면으로 빌드된** 적이 있다.

실제로 이 파이프라인도 같은 드리프트를 겪었다. `tasks/00_pdf_to_json.md` 의 표를 옮겨 적었더니
런타임이 요구하지 않는 필드까지 필수로 잡혀 있었다.

    원자            런타임 requires        문서 표
    multiPick       items, answer          + confirmLabel
    keypad          answer                 + digits
    tenFrameFill    count                  + item, frames

문서 표를 기준으로 검사하면 멀쩡한 lesson.json 이 반려된다. 그래서 대상 레포가 주어지면
런타임에서 읽고, 없으면 문서 표로 떨어지되 **그 사실을 보고한다.**
"""

from __future__ import annotations

import json
import re
from pathlib import Path


RUNTIME_PLAYER = Path("runtime") / "src" / "player.js"

BLOCK_PATTERN = re.compile(r"const PROBLEM_ATOMS = \{(.*?)\n\};", re.DOTALL)
KEY_PATTERN = re.compile(r"^ {2}([A-Za-z][A-Za-z0-9]*): \{", re.MULTILINE)
REQUIRES_PATTERN = re.compile(r"requires:\s*\[([^\]]*)\]")
FIELD_PATTERN = re.compile(r"'([^']+)'|\"([^\"]+)\"")


def load_atom_registry(gyo6_root: Path | None) -> dict[str, list[str]] | None:
    """`{원자 이름: 필수 필드 목록}`. 못 읽으면 None.

    키에 있는 것이 **base 렌더러가 있는 원자**다. 여기 없는 원자는 차시가 구현해야 화면에 나온다.
    """
    if gyo6_root is None:
        return None
    player = gyo6_root / RUNTIME_PLAYER
    if not player.exists():
        return None
    try:
        source = player.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    block = BLOCK_PATTERN.search(source)
    if not block:
        return None
    body = block.group(1)

    keys = list(KEY_PATTERN.finditer(body))
    registry: dict[str, list[str]] = {}
    for index, match in enumerate(keys):
        start = match.start()
        end = keys[index + 1].start() if index + 1 < len(keys) else len(body)
        chunk = body[start:end]
        requires = REQUIRES_PATTERN.search(chunk)
        fields: list[str] = []
        if requires:
            fields = [
                found[0] or found[1] for found in FIELD_PATTERN.findall(requires.group(1))
            ]
        registry[match.group(1)] = fields
    return registry or None


RUNTIME_CSS = Path("runtime") / "styles" / "player.css"

# CSS 파일에서만 뽑는다. player.js 까지 긁으면 `abs`·`addEventListener` 같은
# **메서드 호출**이 class 로 잡힌다(실측: 830개 중 대부분이 그랬다).
# 그리고 선택자에 쓰인 것만 센다 — 값이나 주석에 섞인 점 표기를 걸러낸다.
SELECTOR_LINE = re.compile(r"^[^{}/@]*[.][A-Za-z][\w-]*[^{}]*\{", re.MULTILINE)
CLASS_PATTERN = re.compile(r"[.]([A-Za-z][\w-]*)")
# class 를 JS 가 붙이거나 찾는 경우도 본다. 네 형태가 실제로 쓰인다:
#   classList.add('x') · className = 'x' · class="x" · querySelector('.x')
# 마지막 두 형태가 없으면 `pa-choice` 처럼 문자열 조립으로만 붙는 이름을 놓친다(실측).
JS_CLASS_PATTERN = re.compile(
    r"classList\.(?:add|remove|toggle|contains)\(\s*['\"]([\w-]+)['\"]"
    r"|className\s*=\s*['\"]([^'\"]+)['\"]"
    r"|class=\\?[\"']([^\"'\\]+)"
    r"|querySelector(?:All)?\(\s*['\"][.]([\w-]+)"
)


def load_class_names(gyo6_root: Path | None) -> list[str]:
    """base 런타임이 실제로 쓰는 class 이름을 읽는다.

    **문서에 목록을 적어두지 않는다.** 원자 레지스트리와 같은 이유다 — 사본은 어긋난다.

    실측(2026-09-08): 계약에 이름 목록 없이 "`.pa-*` 로 재스킨하라"고만 썼더니 모델이
    `.lesson-player`·`.stage-character`·`.speech-bubble` 같은 **존재하지 않는 이름**으로 75줄을 썼고,
    최상위 래퍼가 없는 이름이라 그 안의 규칙이 통째로 죽었다. 화면은 그대로인데 파일만 생겼다.
    """
    if gyo6_root is None:
        return []
    names: set[str] = set()

    css = gyo6_root / RUNTIME_CSS
    if css.exists():
        try:
            source = css.read_text(encoding="utf-8", errors="replace")
        except OSError:
            source = ""
        for selector in SELECTOR_LINE.findall(source):
            names.update(CLASS_PATTERN.findall(selector))

    player = gyo6_root / RUNTIME_PLAYER
    if player.exists():
        try:
            source = player.read_text(encoding="utf-8", errors="replace")
        except OSError:
            source = ""
        for groups in JS_CLASS_PATTERN.findall(source):
            for value in groups:
                names.update(part for part in value.split() if part)

    return sorted(names)


def build_class_names_section(gyo6_root: Path | None) -> str:
    names = load_class_names(gyo6_root)
    if not names:
        return (
            "COMMON_CLASS_NAMES:\n"
            "(대상 레포를 못 읽었다. player-ext.css 를 쓸 때 클래스 이름을 지어내지 않는다 —\n"
            " 확신이 없으면 CSS 를 만들지 않는 편이 낫다.)\n"
        )
    return (
        "COMMON_CLASS_NAMES:\n"
        "base 런타임이 실제로 쓰는 class 다. **여기 없는 이름을 쓰면 그 규칙은 아무것도 하지 않는다.**\n"
        f"{json.dumps(names, ensure_ascii=False)}\n"
    )


EXT_HOOK_PATTERN = re.compile(r"window\.lessonExt\??\.\s*(\w+)")


def load_ext_hooks(gyo6_root: Path | None) -> list[str]:
    """런타임이 실제로 부르는 `window.lessonExt` 훅 이름을 읽는다.

    이름이 있는 것과 **그것이 언제 불리는가**는 다르다. 실측(2026-09-09) — 상태 클래스 갱신을
    `rerenderScene`·`restoreCheckpointScene` 에 달았는데, 둘 다 실재하는 이름이지만
    체크포인트 복원 경로에서만 불린다. 그래서 로드 직후 한 번 붙은 `bn-intro` 가 끝까지 남았고
    문제 화면용 CSS 는 전부 죽은 규칙이 됐다. **데이터 게이트는 전부 통과했다.**

    문항이 바뀔 때마다 불리는 것은 `randomizeProblem` 하나뿐이다.
    """
    if gyo6_root is None:
        return []
    player = Path(gyo6_root) / "runtime" / "src" / "player.js"
    if not player.exists():
        return []
    try:
        source = player.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return sorted({name for name in EXT_HOOK_PATTERN.findall(source)})


def build_ext_hooks_section(gyo6_root: Path | None) -> str:
    hooks = load_ext_hooks(gyo6_root)
    if not hooks:
        return ""
    return (
        "LESSON_EXT_HOOKS:\n"
        "런타임이 `window.lessonExt` 에서 실제로 찾아 부르는 이름이다.\n"
        "**여기 없는 이름에 함수를 달면 영영 불리지 않는다** — 오류도 안 나고 화면만 안 바뀐다.\n"
        "문항이 바뀔 때마다 무언가 하려면 `randomizeProblem` 을 쓴다(문항마다 불린다. "
        "받은 spec 을 그대로 돌려주면 렌더링은 base 가 계속 맡는다).\n"
        f"{json.dumps(hooks, ensure_ascii=False)}\n"
    )


def describe(registry: dict[str, list[str]] | None, gyo6_root: Path | None = None) -> str:
    """레지스트리를 어디서 읽었는지 한 줄로 말한다.

    **경로를 안 준 것과 줬는데 못 읽은 것을 구분한다.** 후자는 거의 항상 옛 체크아웃을 가리킨
    경우이고(실측 2026-09-10 — 같은 장비에 gyo6_content 체크아웃이 두 벌 있었고 한쪽은
    `PROBLEM_ATOMS` 가 아직 없는 리비전이었다), 그때 검사는 조용히 문서 표로 떨어진다.
    조용히 떨어지는 것이 이 축에서 가장 위험하다 — 통과했다는 결과만 남는다.
    """
    if registry is None:
        if gyo6_root is not None:
            return (
                f"⚠ 원자 레지스트리: 문서 표로 대체 — 준 경로에서 PROBLEM_ATOMS 를 못 읽었다: {gyo6_root}\n"
                f"  {RUNTIME_PLAYER.as_posix()} 가 없거나 그 상수가 없는 옛 리비전이다. "
                "체크아웃이 여러 벌이면 최신 쪽을 가리키는지 확인한다"
            )
        return (
            "원자 레지스트리: 문서 표로 대체 (대상 레포 경로를 안 줬다). "
            "--gyo6-root 를 주면 런타임에서 직접 읽어 정확해진다"
        )
    names = ", ".join(sorted(registry))
    return f"원자 레지스트리: 런타임에서 읽음 — base 렌더러 {len(registry)}종 ({names})"
