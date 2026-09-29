"""lesson.json이 gyo6_content 런타임에 실릴 수 있는지 코드로 확정한다.

`planner_check`와 같은 자리에 선다 — 모델이 자기 결과를 판정하지 않고, 기계로 확정 가능한 것만
여기서 본다. gyo6_content 쪽에는 external과 달리 lessons/ 산출물을 막아 주는 게이트가 있지만
(`npm run validate`), 그것은 **차시가 이미 배치된 뒤**에 돈다. 여기서 먼저 걸러야 남의 레포에
깨진 차시를 밀어 넣지 않는다.

확정할 수 있는 것만 본다. "연출이 좋은가"는 여기서 판정하지 않는다.
"""

from __future__ import annotations

import re
from pathlib import Path


# tasks/00_pdf_to_json.md §4 의 고정 어휘. 이 밖의 이름은 즉석 작명이다.
PROBLEM_ATOM_VOCAB = (
    "tapCount",
    "tapMove",
    "dragToSlot",
    "sortToBin",
    "tenFrameFill",
    "compareMark",
    "choicePick",
    "multiPick",
    "wordChoice",
    "keypad",
    "arrangeOrder",
    "dragToCanvas",
    "drawEdge",
)

# 아래 둘은 **대상 레포를 못 읽을 때만 쓰는 대체본**이다. 진짜 기준은 gyo6_content 런타임의
# `PROBLEM_ATOMS` 레지스트리이며 `stages/scripts/atom_registry.py` 가 거기서 직접 읽는다.
# 문서 표와 런타임이 어긋난 적이 있으므로(multiPick·keypad·tenFrameFill 이 문서에만 더 엄격했다)
# 레지스트리를 읽을 수 있으면 언제나 그쪽을 쓴다.
FALLBACK_BASE_RENDERED_ATOMS = frozenset(
    {"dragToSlot", "tenFrameFill", "choicePick", "multiPick", "keypad", "dragToCanvas"}
)

FALLBACK_ATOM_REQUIRED_FIELDS = {
    "tapCount": ("item", "count"),
    "tapMove": ("item", "count", "target"),
    "dragToSlot": ("sources", "slots", "answer"),
    "sortToBin": ("items", "bins", "answer"),
    "tenFrameFill": ("count",),
    "compareMark": ("criterion", "pairs", "answer"),
    "choicePick": ("options", "answer"),
    "multiPick": ("items", "answer"),
    "wordChoice": ("sentences",),
    "keypad": ("answer",),
    "arrangeOrder": ("items", "order", "answer"),
    "dragToCanvas": ("palette", "answer"),
    "drawEdge": ("generate", "guideDots"),
}

STEP_ORDER = ("intro", "tutorial", "problemBank", "outro")

# 런타임이 읽지 않는 옛 스키마 필드. 있으면 옛 차시(2-2/01)를 베낀 것이다.
FORBIDDEN_TOP_LEVEL = ("world", "trophyCriteria")

# 아무도 읽지 않는 `ui` 키. 배포된 18차시를 훑어 확인했다(2026-09-10) — base 런타임 0건,
# 빌드 0건, 차시 ext 0건이고 **선언한 것은 우리 산출물뿐이었다.** 선언해도 아무 일이 없고,
# 그것 때문에 만든 이미지는 아무도 안 그리는 에셋이 된다.
UI_KEYS_UNREAD = {
    "headerPanelRule": "런타임·빌드·ext 어디에도 그런 이름이 없다",
    "tabletTextRule": "글자 크기는 player-ext.css 가 정한다",
}

# 타이틀 로고는 두 층이 각자 다른 이유로 이 경로를 요구한다. 헷갈리기 쉬운 자리라 적어 둔다.
#
#   · base `renderIntroStart` 는 `<img src="assets/ui/title-logo.png">` 를 **경로째 하드코딩**한다.
#     그래서 화면에 나오는 것은 언제나 이 경로의 파일이고, `ui.titleLogoRef` 의 값이 아니다.
#   · 그쪽 `lessonParser.collectAssets` 는 lesson.json 의 **모든 문자열**을 훑어 `assets/…(png|jpg|jpeg)`
#     를 manifest 에 올린다. 그래서 이 경로가 lesson.json 어딘가에 문자열로 있어야 manifest 에
#     오르고 그쪽 imagegen 이 생성한다. 배포 차시 10개가 `ui.titleLogoRef` 에 적어 두는 이유다.
#
# 정리하면 **선언은 생성·추적용, 파일명은 렌더링용**이고 둘 다 같은 경로여야 한다.
TITLE_LOGO_PATH = "assets/ui/title-logo.png"

# 런타임이 읽는 이름과 허용값. **문서와 갈리는 자리라 런타임을 기준으로 적는다** —
# 대상 레포 `CLAUDE.md` 는 `ui.speechBubble.position: "bottom-right"` 로 적어 놨지만
# `runtime/src/player.js` 가 읽는 것은 `side` 이고 값은 above|left|right 다.
SPEECH_BUBBLE_SIDES = ("above", "left", "right")
CHARACTER_POSITIONS = ("left", "right", "center")

# 오디오 선언은 검사하지 않는다. 이 파이프라인은 오디오를 만들지 않으므로 "선언했는데 파일이
# 없다"가 언제나 참이고, 배포된 18차시가 전부 audioMap 을 갖고 있어 이 축으로 재면 전 차시가
# 걸린다. 계약서에 "파일을 넣기 전까지 쓰지 않는다"로 두고 검사는 두지 않는다.

CHARACTER_EMOTIONS = (
    "idle",
    "happy",
    "surprised",
    "thinking",
    "praising",
    "encouraging",
)

ASSET_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")


def check_lesson(
    lesson: dict,
    planner_output: dict,
    builder_output: dict,
    run_dir: Path,
    registry: dict[str, list[str]] | None = None,
) -> list[dict]:
    """확정된 위반 목록을 낸다. 빈 목록이면 배치해도 되는 상태다.

    `registry` 는 gyo6_content 런타임에서 읽은 `PROBLEM_ATOMS` 다. 주면 그쪽 `lessonParser` 와
    **같은 기준**으로 검사하므로, 여기서 통과한 것이 거기서도 통과한다.
    """
    has_ext_js = bool(builder_output.get("player_ext_js_path"))
    violations: list[dict] = []
    violations += check_top_level(lesson)
    violations += check_ui_declarations(lesson)
    violations += check_cast_renderable(lesson)
    violations += check_steps(lesson)
    violations += check_atoms(lesson, has_ext_js=has_ext_js, registry=registry)
    violations += check_traceability(lesson)
    violations += check_step_structure(lesson, has_ext_intro=ext_defines_intro(builder_output, run_dir))
    violations += check_feedback_refs(lesson, builder_output)
    violations += check_placement_used(lesson, builder_output)
    violations += check_coverage(builder_output, planner_output)
    violations += check_text_preserved(lesson, planner_output)
    violations += check_acceptance_variety(lesson)
    violations += check_mojibake(lesson, builder_output, run_dir)
    violations += check_placements(builder_output, planner_output, run_dir)
    violations += check_ext(lesson, builder_output, run_dir)
    return violations


def check_lesson_standalone(
    lesson: dict,
    draft_output: dict,
    run_dir: Path,
    registry: dict[str, list[str]] | None = None,
) -> list[dict]:
    """planner 없이 스토리보드에서 바로 만든 lesson.json 을 검사한다.

    planner 를 기준으로 하는 검사(문구 보존·문항 대조·asset 배치)는 여기서 돌 수 없다.
    비교할 상류가 없기 때문이다. **그만큼 이 경로가 위험하다** — 지어낸 내용을 걸러 줄 층이
    앞에도 뒤에도 없으므로, 대신 원본 대비 충실도를 페이지 대응표로 본다.
    """
    has_ext_js = bool(draft_output.get("player_ext_js_path"))
    violations: list[dict] = []
    violations += check_top_level(lesson)
    violations += check_ui_declarations(lesson)
    violations += check_cast_renderable(lesson)
    violations += check_steps(lesson)
    violations += check_atoms(lesson, has_ext_js=has_ext_js, registry=registry)
    violations += check_traceability(lesson)
    violations += check_step_structure(lesson, has_ext_intro=ext_defines_intro(draft_output, run_dir))
    violations += check_bubble_controls(lesson)
    violations += check_cast_extra_sized(lesson, run_dir)
    violations += check_certificate_openable(lesson, run_dir)
    violations += check_answer_shapes(
        lesson, ext_owns_bank=ext_defines_problem_bank(draft_output, run_dir)
    )
    violations += check_page_map(draft_output)
    violations += check_title_logo_tracked(lesson)
    violations += check_background_asset_prompt(lesson)
    violations += check_acceptance_variety(lesson)
    violations += check_mojibake(lesson, draft_output, run_dir)
    violations += check_asset_refs(lesson, draft_output)
    violations += check_ext(lesson, draft_output, run_dir)
    return violations


# 화면과 조작을 말하는 두 축만 본다. `정답:` 은 판정 기준이라 조작이 달라도 "X 를 넣으면
# 도장이 뜬다" 로 같은 것이 정상이고, 여기에 다양성을 요구하면 없는 차이를 지어내게 된다
# (2026-09-09 실측 — 되먹임 3회를 전부 `정답:` 축에 썼고 배치는 그만큼 안 좋아졌다).
LAYOUT_AXES = ("보인다", "만지면")


def check_acceptance_variety(lesson: dict) -> list[dict]:
    """`acceptance` 가 문항마다 다른 말을 하는지 본다.

    이 세 줄은 그 화면의 배치도다. 4-1/01 은 여기에 "왼쪽 지갑과 오른쪽 낸 돈 판, 아래 확인
    버튼만 있다. 아이 캐릭터와 말풍선은 나오지 않는다" 처럼 **어디에 무엇이 놓이는지**를 적고,
    그 문장이 그대로 `player-ext.css` 의 규칙이 된다.

    문항만 갈아 끼운 같은 문장이 반복되면 배치를 안 정한 것이고, 안 정한 배치는 CSS 에도
    안 써진다. 계약서에 적어 두는 것으로는 막지 못했다(2026-09-09 실측 — 대비 예시를 넣은
    다음 회차에서도 `만지면:` 줄이 전 문항 글자까지 같았다). 그래서 코드로 확정한다.

    한 줄이 통째로 같으면 그것대로, 앞뒤가 같고 가운데 문항만 다르면 골격이 같은 것으로 본다.

    **같은 문장이 반복되는 것 자체는 위반이 아니다.** 키패드 문항 여섯 개가 "키패드로 숫자를
    눌러 빈칸에 쓰고 확인을 누른다"로 같은 것은 실제로 같기 때문이고, 배포 중인 4-1/01 과
    2-1/02 가 그렇다. 위반은 **조작이 서로 다른데도 같은 문장인 경우**다. 그 문장은 조작을
    설명한 것이 아니라 어느 문항에나 붙는 빈 말이라는 뜻이다.
    """
    axis_lines: dict[str, list[tuple[str, str, str]]] = {axis: [] for axis in LAYOUT_AXES}
    for path, scene in iter_scenes(lesson):
        atom = _atom_signature(scene)
        for line in scene.get("acceptance") or []:
            if not isinstance(line, str):
                continue
            for axis in LAYOUT_AXES:
                if line.startswith(f"{axis}:"):
                    axis_lines[axis].append((line.strip(), path, atom))
                    break

    violations: list[dict] = []
    for axis, entries in axis_lines.items():
        if len(entries) < 3:
            continue
        groups: list[list[tuple[str, str, str]]] = []
        for entry in entries:
            for group in groups:
                if _same_skeleton(entry[0], group[0][0]):
                    group.append(entry)
                    break
            else:
                groups.append([entry])
        for group in groups:
            atoms = {atom for _, _, atom in group if atom}
            if len(group) < 3 or len(atoms) < 2:
                continue
            violations.append(
                violation(
                    "acceptance_template",
                    group[0][1],
                    f"`{axis}:` 줄이 조작이 다른 {len(group)}곳에서 같은 골격이다"
                    f"({' · '.join(sorted(atoms))}): {group[0][0][:48]!r}. "
                    "조작이 다른데 문장이 같다면 그 문장은 이 화면을 설명하지 않는다. "
                    "무엇이 왼쪽·오른쪽·아래에 놓이고 무엇이 나오지 않는지를 문항마다 다르게 쓴다",
                )
            )
    return violations


def _atom_signature(scene: dict) -> str:
    """이 장면이 쓰는 원자를 한 줄로 만든다."""
    interaction = scene.get("interaction")
    if isinstance(interaction, str):
        return interaction
    if isinstance(interaction, list):
        return "+".join(str(item) for item in interaction if isinstance(item, str))
    if isinstance(interaction, dict):
        kind = (
            interaction.get("primitives")
            or interaction.get("type")
            or interaction.get("atom")
            or interaction.get("kind")
        )
        if isinstance(kind, str):
            return kind
        if isinstance(kind, list):
            return "+".join(str(item) for item in kind if isinstance(item, str))
    return ""


def _same_skeleton(left: str, right: str, ratio: float = 0.7) -> bool:
    """앞뒤가 같고 가운데만 다른 두 문장을 같은 골격으로 본다."""
    if left == right:
        return True
    shorter = min(len(left), len(right))
    if shorter == 0:
        return False
    head = 0
    while head < shorter and left[head] == right[head]:
        head += 1
    tail = 0
    while tail < shorter - head and left[-1 - tail] == right[-1 - tail]:
        tail += 1
    return (head + tail) / shorter >= ratio


MOJIBAKE_QUESTION = re.compile(r"\?{2,}")
JAMO_ALONE = re.compile(r"[ㄱ-ㆎ]")


def check_mojibake(lesson: dict, builder_output: dict, run_dir: Path) -> list[dict]:
    """읽다가 깨진 한글이 데이터로 굳었는지 본다.

    이 장비의 PowerShell 은 코드페이지 949 로 stdout 을 내보내고, `Get-Content` 는
    인코딩을 안 주면 UTF-8 파일을 cp949 로 **읽는다.** 그래서 에이전트가 참조 파일을
    그렇게 열면 한글이 `???` 로 보이고, 본 대로 옮겨 적으면 그것이 그대로 학습자 화면에
    뜬다. 실측(2026-09-09) — `lesson.json` 79 줄이 `만지면: keypad ??? ?? ??? ? ??.`
    였고 스키마·엄격 검증·빌드를 **전부 통과했다.** 사람 눈으로만 잡혔다.

    `?` 하나는 정상 물음표이므로 연속 2개부터 본다. 낱자 자모는 cp949 로 깨졌을 때
    남는 흔적이지만 한글 학습 콘텐츠에서는 정상일 수 있어 경고로만 올린다.

    **알려진 함정** — `player-ext.js` 에서 JS 의 nullish 연산자(`a ?? b`)를 쓰거나 주석에
    적으면 여기 걸린다(실측 2026-09-11). 공백으로 둘러싸인 `??` 를 빼 주고 싶겠지만
    **그러면 안 된다** — 실제 깨짐도 같은 모양으로 나온다(`keypad ??? ?? ??? ? ??.`).
    이 파이프라인의 ext 는 ES5 문법으로 쓰므로, 걸리면 그 자리를 `||` 나 명시적 분기로 바꾼다.
    """
    violations: list[dict] = []

    def scan(text: str, where: str) -> None:
        if "�" in text:
            violations.append(violation(
                "mojibake", where,
                f"복원 불가 문자(U+FFFD)가 들어 있다: {text[:40]!r}. "
                "파일을 잘못된 인코딩으로 읽었다는 뜻이다",
            ))
        elif MOJIBAKE_QUESTION.search(text):
            violations.append(violation(
                "mojibake", where,
                f"물음표가 연달아 있다: {text[:40]!r}. 한글이 코드페이지에서 깨진 자국이다. "
                "참조 파일을 UTF-8 로 다시 읽고 원문을 그대로 쓴다",
            ))
        elif JAMO_ALONE.search(text):
            violations.append(violation(
                "jamo_alone", where,
                f"낱자 자모가 섞여 있다: {text[:40]!r}. 의도한 것이 아니면 깨진 것이다",
                severity="warning",
            ))

    def walk(node, path: str) -> None:
        if isinstance(node, str):
            scan(node, path)
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk(lesson, "lesson")

    # ext 파일도 같은 경로로 깨진다. 거기 깨진 한글은 화면의 버튼 문구가 된다.
    for key in ("player_ext_js_path", "player_ext_css_path"):
        rel = builder_output.get(key)
        if not rel:
            continue
        path = run_dir / rel
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            scan(line, f"{rel}:{lineno}")

    return violations


def check_page_map(draft_output: dict) -> list[dict]:
    """스토리보드의 모든 페이지가 대응표에 올랐는지 본다.

    이 경로의 유일한 충실도 기준이다. 페이지를 빠뜨리면 그 장면은 만들어지지 않고,
    결과는 스키마를 통과하므로 아무도 그것이 빠진 줄 모른다.
    """
    total = draft_output.get("pages_total")
    mapped = draft_output.get("pages_mapped")
    if not isinstance(total, int) or not isinstance(mapped, int):
        return []
    if total == 0:
        # 페이지 개념이 없는 원본(.md)이면 대응표로 잴 수 없다.
        return []
    if mapped < total:
        return [
            violation(
                "page_unmapped",
                "page-map.md",
                f"스토리보드 {total}쪽 중 {mapped}쪽만 대응표에 있다. "
                f"{total - mapped}쪽이 어느 장면도 되지 못했다",
            )
        ]
    return []


def check_asset_refs(lesson: dict, draft_output: dict) -> list[dict]:
    """보고한 asset 목록과 lesson.json 이 실제로 가리키는 것이 같은지 본다.

    manifest 를 이 목록으로 만들므로, 어긋나면 gyo6_content 빌드가 엉뚱한 것을 생성하거나
    필요한 것을 안 만든다.
    """
    declared = {str(value) for value in draft_output.get("asset_refs") or []}
    used: set[str] = set()
    collect_asset_refs(lesson, used)
    missing = sorted(used - declared)
    extra = sorted(declared - used)
    violations = []
    if missing:
        violations.append(
            violation(
                "asset_ref_unreported",
                "asset_refs",
                f"lesson.json 이 쓰는데 보고에 없다: {missing[:5]}",
            )
        )
    if extra:
        violations.append(
            violation(
                "asset_ref_unused",
                "asset_refs",
                f"보고했는데 lesson.json 이 안 쓴다: {extra[:5]}",
            )
        )
    return violations


ASSET_REF_PATTERN = re.compile(
    r"^assets/[A-Za-z0-9_\-/]+\.(?:png|jpe?g|webp|mp3|wav|ogg|m4a)$", re.IGNORECASE
)


def collect_asset_refs(node: object, found: set[str]) -> None:
    if isinstance(node, str):
        if ASSET_REF_PATTERN.match(node):
            found.add(node)
        return
    if isinstance(node, dict):
        for value in node.values():
            collect_asset_refs(value, found)
        return
    if isinstance(node, list):
        for value in node:
            collect_asset_refs(value, found)


# acceptance 3축. gyo6_content tasks/00_pdf_to_json.md §5 를 옮긴 것이다.
ACCEPTANCE_AXES = ("보인다", "만지면", "정답")


def check_traceability(lesson: dict) -> list[dict]:
    """원본 추적과 검수 기준이 붙어 있는지 본다.

    이 검사가 `content_eval` 의 `content_fidelity` 축이 하던 일을 대신한다. 그쪽은 LLM 1회에
    루브릭 5축을 매기고 그중 한 축으로 누락을 잡았는데, 누락은 **점수가 아니라 유무**라서
    코드로 확정할 수 있다. 점수로 재면 4.8 같은 값이 나오고 그게 통과인지 아닌지 또 사람이 정해야 한다.

    · `sourcePanel` — 없으면 이 문항이 원문 어디서 왔는지 사후에 못 찾는다.
    · `acceptance` 3줄 — 화면을 보고 O/X 판정이 가능한 문장. `design_review` 가 LLM으로
      훑던 것을 사람이 5분에 보는 근거로 바꾼다.
    """
    violations = []
    for where, task in iter_scenes(lesson):
        if not has_source_panel(task):
            violations.append(
                violation("no_source_panel", where, "sourcePanel 이 없다. 원문 추적이 끊긴다")
            )
        acceptance = task.get("acceptance")
        if not isinstance(acceptance, list) or not acceptance:
            violations.append(
                violation("no_acceptance", where, "acceptance 가 없다. 검수 기준이 없으면 아무도 못 본다")
            )
            continue
        # 축은 **줄 첫머리**에 있어야 한다. gyo6_content `checkAcceptance` 가
        # `line.trimStart().startsWith(axis)` 로 보므로, 문장 중간에 그 낱말이 섞인 것은
        # 축으로 세지 않는다. 여기서 느슨하게 통과시키면 거기서 막힌다.
        missing = [
            axis
            for axis in ACCEPTANCE_AXES
            if not any(
                isinstance(line, str) and line.lstrip().startswith(axis) for line in acceptance
            )
        ]
        if missing:
            violations.append(
                violation(
                    "acceptance_axis",
                    where,
                    f"acceptance 축이 줄 첫머리에 없다: {missing}. \"보인다: …\" 처럼 시작한다",
                )
            )
        violations += check_stimulus(task, where)
    return violations


# 런타임이 실제로 그리는 stimulus 필드. gyo6_content `runtime/src/player.js` 의
# paStimulusHtml 이 읽는 것과 같아야 한다. 밖의 이름은 화면에 안 나온다.
STIMULUS_FIELDS = (
    "text",
    "highlight",
    "highlightRange",
    "style",
    "imageRef",
    "caption",
    "sequence",
    "cards",
)


def check_stimulus(task: dict, where: str) -> list[dict]:
    """제시 자료가 런타임이 읽는 필드에 담겼는지 본다.

    스토리보드의 문제는 대부분 "자료를 보고 답하기"인데, 자료를 담을 필드를 모르면
    변환자가 `semiDialogue`(말풍선)나 `prompt` 에 밀어 넣는다. 그러면 화면에는 말풍선만 뜨고
    문제 화면에는 아무 자료도 없다(gyo6_content 실측: 신문 기사·비교할 수·그림이 사라졌다).
    """
    stimulus = task.get("stimulus")
    if stimulus is None:
        return []
    if not isinstance(stimulus, dict):
        return [violation("stimulus_shape", where, "stimulus 는 객체여야 한다")]
    violations = []
    unknown = [key for key in stimulus if key not in STIMULUS_FIELDS]
    if unknown:
        # gyo6_content 는 이것을 warn 으로 둔다. 배포 중인 4-1/01 이 stepLabel 을 쓴다.
        violations.append(
            warning(
                "stimulus_field",
                where,
                f"런타임이 읽지 않는 stimulus 필드다: {unknown}. 화면에는 안 나온다",
            )
        )
    if not any(stimulus.get(field) is not None for field in STIMULUS_FIELDS):
        violations.append(
            violation(
                "stimulus_empty",
                where,
                f"stimulus 에 그릴 내용이 없다. {list(STIMULUS_FIELDS[:4])} 중 하나는 채운다",
            )
        )
    for field in ("highlight", "sequence", "cards"):
        if stimulus.get(field) is None:
            continue
        if not isinstance(stimulus[field], list):
            violations.append(violation("stimulus_type", where, f"stimulus.{field} 는 배열이어야 한다"))
            continue
        # 런타임은 이 배열의 원소를 `esc(String(v))` 로 그린다. 객체를 넣으면 화면에
        # `[object Object]` 가 찍힌다(2026-09-09 실측 — 표를 `cards[{imageRef, caption}]`
        # 로 넣어 그렇게 됐다). 그림이 필요하면 `imageRef`, 여러 줄 자료는 `text` 다.
        bad = [item for item in stimulus[field] if not isinstance(item, (str, int, float))]
        if bad:
            violations.append(
                violation(
                    "stimulus_item_shape",
                    where,
                    f"stimulus.{field} 에 객체가 들어 있다: {str(bad[0])[:60]}. "
                    "런타임은 원소를 글자로만 그려서 화면에 [object Object] 가 찍힌다. "
                    "여러 줄 자료는 text(줄바꿈 유지), 그림 한 장은 imageRef 로 옮긴다",
                )
            )
    prompt = str(task.get("prompt") or "").strip()
    text = str(stimulus.get("text") or "").strip()
    if prompt and text and prompt == text:
        violations.append(
            violation(
                "stimulus_repeats_prompt",
                where,
                f"stimulus.text 가 prompt 와 같은 문장이다: {prompt[:34]!r}. "
                "화면에 같은 말이 두 번 나오고 그만큼 자리를 먹는다. "
                "제시 자료가 없으면 text 를 비우고, 있으면 자료를 넣는다",
            )
        )

    if stimulus.get("highlight") and not stimulus.get("text") and not isinstance(stimulus.get("sequence"), list):
        violations.append(
            violation("stimulus_highlight", where, "highlight 가 있는데 강조할 text 나 sequence 가 없다")
        )
    return violations


# 런타임이 읽는 말풍선 종류. gyo6_content `runtime/src/player.js` 의 BUBBLE_TYPES.
BUBBLE_TYPES = ("narrationNext", "narration", "plain")

BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
# 대괄호로만 이뤄진 줄은 버튼 라벨이다 — 원문이 [시작하기] 처럼 표기한다.
TABLE_SEPARATOR = re.compile(r"\s[/|]\s|	")
BRACKET_LABEL = re.compile(r"[\[`]\s*[^\]`]{1,40}\s*[\]`]")


def check_step_structure(lesson: dict, has_ext_intro: bool = False) -> list[dict]:
    """step 단위 구조를 gyo6_content `checkStepStructure` 와 같은 기준으로 본다.

    여기 있는 것은 **specVersion 2 에서 전부 오류**다(경고가 아니다). 하나라도 걸리면
    `npm run validate` 가 통째로 실패하므로, 배치 전에 여기서 잡아야 한다.

    `has_ext_intro` 는 차시가 `renderIntroFlow` 를 자체 구현하는가다. 자체 구현하면 컷을
    그 코드가 그리므로 base 렌더러 전제의 검사(자막 전용 컷)를 걸지 않는다.
    """
    violations: list[dict] = []
    for index, step in enumerate(lesson.get("steps") or []):
        if not isinstance(step, dict):
            violations.append(violation("step_shape", f"steps[{index}]", "객체가 아니다"))
            continue
        step_path = f"steps[{index}]" + (f" ({step['id']})" if step.get("id") else "")

        for cut_index, cut in enumerate(step.get("stageDirections") or []):
            where = f"{step_path}.stageDirections[{cut_index}]"
            violations += check_stage_direction(cut, where)
            if isinstance(cut, dict):
                violations += check_caption_only_cut(cut, where, has_ext_intro)
        for round_index, round_ in enumerate(step.get("rounds") or []):
            if not isinstance(round_, dict):
                continue
            for cut_index, cut in enumerate(round_.get("stageDirections") or []):
                where = f"{step_path}.rounds[{round_index}].stageDirections[{cut_index}]"
                violations += check_stage_direction(cut, where)
                if isinstance(cut, dict):
                    violations += check_caption_only_cut(cut, where, has_ext_intro)

        # 미션은 문제와 같은 스키마다. interaction 이 없으면 원자가 없으니 화면이 비고,
        # acceptance 도 없으면 is_scene 판정에도 안 걸려 다른 검사가 통째로 건너뛴다.
        for mission_index, mission in enumerate(step.get("missions") or []):
            mission_path = f"{step_path}.missions[{mission_index}]"
            if not isinstance(mission, dict):
                violations.append(violation("mission_shape", mission_path, "객체가 아니다"))
                continue
            if not mission.get("interaction"):
                violations.append(
                    violation(
                        "mission_interaction",
                        mission_path,
                        "interaction.primitives 가 없다. 미션도 문제와 같은 원자 어휘로 쓴다",
                    )
                )

        violations += check_step_asset_prompt(step, step_path)
        violations += check_step_background(step, step_path)
        violations += check_cut_numbering(step, step_path)

        criteria = step.get("acceptanceCriteria")
        if criteria is not None and (not isinstance(criteria, list) or not criteria):
            violations.append(
                violation(
                    "acceptance_criteria",
                    f"{step_path}.acceptanceCriteria",
                    "있다면 비어 있지 않은 배열이어야 한다",
                )
            )
    return violations


def check_placement_used(lesson: dict, builder_output: dict) -> list[dict]:
    """배치하기로 한 이미지를 lesson.json 이 실제로 쓰는지 본다.

    실측(2026-09-08, 4학년 1차시): `asset_placements` 로 22장을 배치했는데 `lesson.json` 은
    8장만 참조했다. 나머지 14장은 만들어서 옮겨 놓고 **아무도 안 쓰는 상태**가 됐고,
    화면에서는 타이틀 로고·문제 표면·유물 그림·실생활 카드 4장이 통째로 사라졌다.

    그런데 모든 게이트가 통과했다 —
      · `install_lesson` 은 "참조하는 것이 다 놓였나"만 본다(반대 방향을 안 본다)
      · gyo6_content `lessonParser` 도 lesson.json 이 가리키는 것만 센다
      · 빌드는 성공하고 `dist` 도 나온다

    **놓은 것과 쓰는 것이 어긋나는 자리는 여기 말고 아무도 보지 않는다.**

    참조되는 자리는 이렇다(실측):
      cast[].assetRef · ui.certificate.surfaceRef · ui.feedbackCorrectRef / WrongRef
      steps[].stageDirections[].backgroundRef · steps[].rounds[].background
      steps[].rounds[].problems[].stimulus.imageRef
      interaction.palette[].imageRef · interaction.canvas.assetRef
    """
    placed = {
        str(item.get("dest_path") or "")
        for item in builder_output.get("asset_placements") or []
        if isinstance(item, dict) and item.get("dest_path")
    }
    used: set[str] = set()
    collect_asset_refs(lesson, used)
    violations: list[dict] = []

    # 반대 방향도 본다. 참조는 하는데 배치를 안 보고하면 install 이 아무것도 옮기지 않아
    # 화면의 그림이 **전부** 깨진다. 실측(2026-09-09) — `asset_placements` 가 빈 배열인데
    # lesson.json 은 22장을 가리켰고, 이 함수가 `if not placed: return []` 로 조용히
    # 빠져나가서 통과했다. 한쪽만 보는 검사는 반대쪽이 0일 때 아무것도 못 본다.
    unplaced = sorted(used - placed)
    if unplaced:
        violations.append(
            violation(
                "ref_not_placed",
                "asset_placements",
                f"lesson.json 이 가리키는 {len(used)}장 중 {len(unplaced)}장을 배치하지 않는다. "
                f"그 그림은 차시 폴더에 없어서 화면에서 깨진다: "
                f"{[Path(p).name for p in unplaced][:8]}",
            )
        )

    orphans = sorted(placed - used) if placed else []
    if orphans:
        violations.append(
            violation(
                "asset_unused",
                "asset_placements",
                f"배치하는 {len(placed)}장 중 {len(orphans)}장을 lesson.json 이 참조하지 않는다. "
                f"그 자리는 화면에서 빈다: {[Path(p).name for p in orphans][:8]}",
            )
        )
    return violations


STAMP_PATTERN = re.compile(r"stamp|feedback", re.IGNORECASE)


def check_feedback_refs(lesson: dict, builder_output: dict) -> list[dict]:
    """정오 도장을 만들어 놓고 띄울 통로가 없는 상태를 막는다.

    실측: `stamp_correct`/`stamp_wrong` 을 계획하고 생성까지 했는데 `ui.feedbackCorrectRef`
    선언이 빠져 있었다. 그쪽 파서는 이 필드를 요구하지 않으므로 빌드는 통과하고,
    **화면에서 판정만 조용히 사라진다.**
    """
    placed = [
        str(item.get("dest_path") or "")
        for item in builder_output.get("asset_placements") or []
        if isinstance(item, dict)
    ]
    stamps = [path for path in placed if STAMP_PATTERN.search(Path(path).stem)]
    if not stamps:
        return []
    ui = lesson.get("ui") if isinstance(lesson.get("ui"), dict) else {}
    missing = [key for key in ("feedbackCorrectRef", "feedbackWrongRef") if not ui.get(key)]
    if not missing:
        return []
    return [
        violation(
            "feedback_ref",
            "root.ui",
            f"정오 도장을 {len(stamps)}장 배치하는데 {missing} 선언이 없다. "
            "만들어 놓고 화면에 띄울 통로가 없다",
        )
    ]


def ext_defines_intro(builder_output: dict, run_dir: Path) -> bool:
    """차시 ext 가 `renderIntroFlow` 를 맡는가. 맡으면 base 전제의 컷 검사를 걸지 않는다."""
    path = str(builder_output.get("player_ext_js_path") or "")
    if not path:
        return False
    source = read_text(run_dir / path)
    return bool(source and "renderIntroFlow" in source)


def ext_defines_problem_bank(draft_output: dict, run_dir: Path) -> bool:
    """차시 ext 가 `renderProblemBank` 를 맡는가.

    맡으면 문항의 `answer` 를 base 의 원자 렌더러가 읽지 않으므로, base 전제의 정답 모양
    검사를 걸지 않는다. 배포 중인 2-1/02 가 그렇다 — `options[].no` 를 자기 렌더러에서
    직접 읽는데(그쪽 ext 1380행), base `paOption` 은 `no` 를 안 본다.
    """
    path = str(draft_output.get("player_ext_js_path") or "")
    if not path:
        return False
    source = read_text(run_dir / path)
    return bool(source and "renderProblemBank" in source)


def _option_values(options: object) -> set[str]:
    """`paOption`(player.js:2720)이 그 보기에서 뽑아 쓰는 값."""
    values: set[str] = set()
    for index, option in enumerate(options if isinstance(options, list) else []):
        if isinstance(option, dict):
            value = option.get("value", option.get("id", option.get("label", option.get("text"))))
            values.add(str(value if value is not None else index))
        else:
            values.add(str(option))
    return values


def check_answer_shapes(lesson: dict, ext_owns_bank: bool = False) -> list[dict]:
    """원자의 `answer` 가 **런타임이 채점할 수 있는 모양**인지 본다.

    실측(2026-09-17) — 4-2/02 의 키패드 9문항이 `answer: "2.64"` 였다. 키패드에는 숫자 키만
    있고(`player.js:2819`) 채점은 문자열 비교라(`paNorm`, 2709) **학습자가 절대 못 맞혔다.**
    문항 텍스트도 정답값도 원문 그대로였고 schema·기존 게이트·빌드·화면검사가 전부 통과했다.
    사람이 화면에서 직접 풀어 보기 전에는 드러나지 않는 종류다.

    **불변식은 배포 17차시에서 위반 0건인 것만 골랐다**(2026-09-22 실측).

    | 검사 | 표본 | 위반 |
    |---|---|---|
    | 키패드 답에 숫자 아닌 글자 | 37 | 0 |
    | `□` 개수 = 답 배열 길이(다른 빈칸 필드가 없을 때) | 26 | 0 |
    | `dragToSlot` 답 길이 = `slots` 길이 | 8 | 0 |
    | `multiPick` 답 ⊆ `items` | 2 | 0 |
    | `choicePick` 답 ∈ `options` | 7 | **1** → ext 소유 차시를 빼면 0 |

    빼 둔 자리도 실측으로 정했다 — 키패드 빈칸은 `□` 말고 `placeValueFill`·`sequence`·`cards`
    로도 생기고(배포에 7건), 그때는 `□` 개수로 잴 수 없다. `multiPick` 은 `answer` 가 아예
    없는 차시가 6건이라 있을 때만 본다.
    """
    violations: list[dict] = []
    for path, scene in iter_scenes(lesson):
        interaction = scene.get("interaction")
        if not isinstance(interaction, dict):
            continue
        primitives = interaction.get("primitives")
        primitives = primitives if isinstance(primitives, list) else [primitives]
        answer = interaction.get("answer")
        stimulus = scene.get("stimulus") if isinstance(scene.get("stimulus"), dict) else {}

        if "keypad" in primitives and answer is not None:
            elements = answer if isinstance(answer, list) else [answer]
            bad = [str(e) for e in elements if not re.fullmatch(r"\d+", str(e))]
            if bad:
                violations.append(
                    violation(
                        "keypad_answer_untypeable",
                        f"{path}.interaction.answer",
                        f"키패드 정답에 숫자가 아닌 글자가 있다: {bad[:3]}. 키패드는 0~9 만 있고"
                        "(player.js:2819) 채점은 문자열 비교라(2709) 학습자가 이 답을 만들 수 없다. "
                        "화면에 이미 찍혀 있는 소수점·단위는 빼고 **칸에 들어갈 숫자만** 적는다",
                    )
                )
            blanks = str(stimulus.get("text") or "").count("□")
            other_blank_source = any(k in stimulus for k in ("placeValueFill", "sequence", "cards"))
            # 칸이 여럿인데 답을 **한 덩어리 문자열**로 두면 첫 칸에 전부 들어가고 나머지는 빈다.
            # 배포에서 "문자열 답 + □ 2칸 이상 + 다른 빈칸 필드 없음" 은 0건이다(2026-09-22 실측).
            if blanks > 1 and not other_blank_source and isinstance(answer, str):
                violations.append(
                    violation(
                        "keypad_answer_not_split",
                        f"{path}.interaction.answer",
                        f"입력칸(`□`)이 {blanks}개인데 정답이 한 덩어리 문자열 {answer!r} 이다. "
                        "키패드는 answers[step] 을 blanks[step] 에 쓰므로(player.js:2880) "
                        "칸마다 한 원소씩 배열로 쪼갠다",
                    )
                )
            if blanks and not other_blank_source and isinstance(answer, list) and len(answer) != blanks:
                violations.append(
                    violation(
                        "keypad_blank_count_mismatch",
                        f"{path}.interaction.answer",
                        f"입력칸(`□`)은 {blanks}개인데 정답 배열은 {len(answer)}개다. "
                        "`□` 하나가 칸 하나가 되고(player.js:3499) 키패드는 answers[step] 을 "
                        "blanks[step] 에 쓴다 — 개수가 다르면 칸이 남거나 모자란다",
                    )
                )

        if "dragToSlot" in primitives and isinstance(answer, list) and isinstance(interaction.get("slots"), list):
            if len(answer) != len(interaction["slots"]):
                violations.append(
                    violation(
                        "dragtoslot_answer_length",
                        f"{path}.interaction.answer",
                        f"놓는 칸은 {len(interaction['slots'])}개인데 정답 배열은 {len(answer)}개다. "
                        "배열로 쓰면 **칸 순서대로** 짝지으므로 길이가 같아야 한다",
                    )
                )

        if "multiPick" in primitives and isinstance(answer, list) and isinstance(interaction.get("items"), list):
            ids = _option_values(interaction["items"])
            missing = sorted({str(a) for a in answer} - ids)
            if missing:
                violations.append(
                    violation(
                        "multipick_answer_not_in_items",
                        f"{path}.interaction.answer",
                        f"정답에 items 에 없는 값이 있다: {missing[:3]}. 고를 수 없는 것을 정답으로 두면 못 푼다",
                    )
                )

        if not ext_owns_bank and "choicePick" in primitives and answer is not None:
            options = interaction.get("options")
            if isinstance(options, list) and options:
                if str(answer) not in _option_values(options):
                    violations.append(
                        violation(
                            "choicepick_answer_not_in_options",
                            f"{path}.interaction.answer",
                            f"정답 {answer!r} 이 options 에 없다. base 는 보기의 "
                            "`value ?? id ?? label ?? text` 로 값을 잡는다(player.js:2720) — "
                            "`no` 같은 다른 이름으로 짝지으려면 ext 가 renderProblemBank 를 맡아야 한다",
                        )
                    )
    return violations


def check_caption_only_cut(cut: dict, where: str, has_ext_intro: bool) -> list[dict]:
    """자막만 있고 대사가 없는 컷을 잡는다. **base 렌더러를 쓸 때만 위반이다.**

    base 의 컷 재생은 이렇게 돈다.

        setSpeechBubble(d.speechText ?? '', { onNarrationEnd: reveal })
        → speechText 가 비면 곧바로 'plain' 을 반환하고 **onNarrationEnd 를 안 부른다**
        → 그런데 [다음] 버튼은 `opacity:0; pointer-events:none` 로 시작해
          `reveal()` 로만 보이게 된다
        → 버튼이 영영 안 나온다. 화면이 그 컷에서 멈춘다

    실측(2026-09-11) — 자막만 있는 첫 컷에서 `다음 ▸` 을 네 번 눌러도 안 넘어갔다.
    데이터·스키마·빌드가 전부 통과한 뒤 화면 검사에서만 드러났다.

    배포된 16차시에 이 형태가 98개 있지만 **전부 `renderIntroFlow` 를 자체 구현한 차시**다.
    base 경로로 자막 전용 컷을 쓴 차시는 하나도 없다.
    """
    if has_ext_intro:
        return []
    speech = str(cut.get("speechText") or "").strip()
    caption = str(cut.get("captionText") or "").strip()
    if speech or not caption:
        return []
    return [
        violation(
            "caption_only_cut",
            where,
            "자막만 있고 speechText 가 없다. base 컷 재생은 나레이션이 끝나야 [다음] 버튼을 "
            "보여주는데, speechText 가 비면 그 신호가 안 온다 — 화면이 이 컷에서 멈춘다. "
            "말할 사람을 정해 speechText 로 옮기거나, player-ext.js 가 renderIntroFlow 를 맡는다",
        )
    ]


def cast_refs_used(lesson: dict) -> tuple[set[str], set[str]]:
    """컷이 실제로 부르는 인물과, 그중 **감정을 안 적고** 부르는 인물.

    안 불리는 `cast` 항목은 검사하지 않는다 — 배포 차시에 모양이 다른 미사용 항목이 있고
    (1-2/02 의 `children` 은 인물이 아니라 묶음이다), 그것을 잡으면 축이 틀린 것이다.
    """
    used: set[str] = set()
    without_emotion: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            ref = node.get("characterRef")
            if isinstance(ref, str) and ref:
                used.add(ref)
                if not str(node.get("characterEmotion") or "").strip():
                    without_emotion.add(ref)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(lesson.get("steps") or [])
    return used, without_emotion


def check_cast_renderable(lesson: dict) -> list[dict]:
    """무대에 서는 인물이 실제로 그려지는지 본다.

    base `setSceneChar` 는 **`cast[ref].emotions` 에서만** 그림을 찾는다.

        const cast = (L.cast ?? {})[ref];
        const src = (cast?.emotions ?? {})[em] ?? (cast?.emotions ?? {}).idle ?? ... ?? '';

    `assetRef` 는 **읽지 않는다.** 그래서 `emotions` 없이 `assetRef` 만 두면 `src` 가 빈 문자열이
    되어 **인물이 화면에 아예 안 나온다.** 오류도 안 나고 말풍선만 떠 있다.
    실측(2026-09-11) — 컷 19개 전부 인물이 없었고 데이터·빌드·화면검사가 다 통과했다.

    자리도 같다. `resolveCharPos` 는 `cast[ref].position` 이 없으면 주인공을 전부 `left` 로
    보낸다 — 두 사람이 번갈아 말해도 **말풍선이 계속 같은 쪽**에 뜬다.
    """
    violations = []
    cast = lesson.get("cast")
    if not isinstance(cast, dict) or not cast:
        return violations
    used, without_emotion = cast_refs_used(lesson)
    for key, member in cast.items():
        if not isinstance(member, dict) or key not in used:
            continue
        emotions = member.get("emotions")
        if not isinstance(emotions, dict) or not emotions:
            violations.append(
                violation(
                    "cast_not_renderable",
                    f"root.cast.{key}.emotions",
                    "emotions 가 없다. base 는 emotions 에서만 그림을 찾으므로 이 인물은 "
                    "화면에 안 나온다. 포즈가 하나뿐이어도 "
                    '`"emotions": {"idle": "<그 그림 경로>"}` 는 있어야 한다',
                )
            )
        elif key in without_emotion and not str(
            emotions.get("idle") or ""
        ).strip():
            # `idle` 은 **감정을 안 적은 컷이 있을 때만** 필요하다. 배포 차시 중에는
            # `explain`·`worry` 만 두고 컷마다 감정을 지정해 잘 도는 것이 있다(2-2/05 의 teacher).
            violations.append(
                violation(
                    "cast_not_renderable",
                    f"root.cast.{key}.emotions.idle",
                    "감정을 안 적은 컷이 이 인물을 부르는데 idle 이 없다. 그 컷에서 인물이 사라진다",
                )
            )
        position = member.get("position")
        if position is not None and position not in CHARACTER_POSITIONS:
            violations.append(
                violation(
                    "cast_not_renderable",
                    f"root.cast.{key}.position",
                    f"{position!r} 는 허용값이 아니다: {'|'.join(CHARACTER_POSITIONS)}",
                )
            )
    if len(used) > 1 and not any(
        isinstance(cast.get(key), dict) and cast[key].get("position") for key in used
    ):
        violations.append(
            warning(
                "cast_same_side",
                "root.cast[].position",
                f"무대에 서는 인물이 {len(used)}명인데 아무도 자리를 선언하지 않았다. 주인공은 전부 왼쪽으로 "
                "떨어져 두 사람이 번갈아 말해도 말풍선이 계속 같은 쪽에 뜬다",
            )
        )
    return violations


def check_step_background(step: dict, step_path: str) -> list[dict]:
    """step 단위 배경이 있는지 본다.

    런타임은 step 을 열 때 배경을 한 번 깔고, 컷의 `backgroundRef` 는 **교체할 때만** 읽는다.
    컷에만 두면 첫 화면이 배경 없이 뜬다.

    실측(2026-09-08): `intro` 의 배경이 `stageDirections[0].backgroundRef` 에만 있어
    타이틀 화면이 검은 바탕으로 렌더됐다. **데이터는 유효했고 그쪽 검증기도 빌드도 통과했다** —
    썸네일을 눈으로 보고서야 찾았다. 그래서 여기서 막는다.

    읽는 필드는 step 타입마다 다르다(`runtime/src/player.js` 의 setBg 호출부).
    """
    kind = step.get("type")
    if kind == "problemBank":
        # round 마다 배경이 있으면 step 기본이 없어도 화면이 채워진다.
        rounds = [r for r in (step.get("rounds") or []) if isinstance(r, dict)]
        if rounds and all(r.get("background") for r in rounds):
            return []
        step_bg = step.get("background")
        if isinstance(step_bg, dict) and step_bg.get("ref"):
            return []
        if step.get("backgroundRef"):
            return [
                violation(
                    "step_background",
                    f"{step_path}.backgroundRef",
                    "problemBank 는 step.background.ref 를 읽는다. backgroundRef 는 안 읽힌다",
                )
            ]
        return [
            violation(
                "step_background",
                f"{step_path}.background.ref",
                "배경이 없다. 배경 없는 화면으로 시작한다",
            )
        ]

    if kind == "outro":
        scenes = [s for s in (step.get("scenes") or []) if isinstance(s, dict)]
        if scenes and all(s.get("backgroundRef") for s in scenes):
            return []

    violations = []
    if not step.get("backgroundRef") and not step.get("startBackgroundRef"):
        violations.append(
            violation(
                "step_background",
                f"{step_path}.backgroundRef",
                "배경이 없다. 컷에만 두면 첫 화면이 배경 없이 시작한다",
            )
        )

    # intro 는 화면이 둘로 나뉜다 — 타이틀(renderIntroStart)과 컷 재생(renderIntroFlow).
    #   renderIntroStart  setBg(step.startBackgroundRef ?? step.backgroundRef)
    #   renderIntroFlow   if (d.backgroundRef) setBg(d.backgroundRef)   ← step 배경을 안 읽는다
    #
    # 그래서 `startBackgroundRef` **만** 두면 타이틀에는 배경이 있지만 컷 재생으로 넘어가는
    # 순간 아무도 배경을 다시 깔지 않아 **검은 화면**이 된다(2026-09-09 실측).
    # 배포 중인 4-1/01 은 `backgroundRef` 만 쓰기 때문에 그 배경이 그대로 남아 문제가 없다.
    if kind == "intro" and step.get("startBackgroundRef") and not step.get("backgroundRef"):
        violations.append(
            violation(
                "intro_background_only_title",
                f"{step_path}.backgroundRef",
                "startBackgroundRef 만 있다. 그것은 타이틀 화면에서만 읽히므로 "
                "[시작하기] 를 누르면 배경이 사라져 검은 화면이 된다. backgroundRef 를 함께 둔다",
            )
        )
    return violations


def check_cut_numbering(step: dict, step_path: str) -> list[dict]:
    """컷 번호가 step 안에서 이어지는지 본다.

    실측(2026-09-09): 원문 화면이 바뀔 때마다  를 1로 되돌려  이
    됐다. 컷은 화면 단위가 아니라 **재생 순서**라 번호가 겹치면 순서를 읽을 수 없다.
    """
    cuts = [c for c in (step.get("stageDirections") or []) if isinstance(c, dict)]
    numbers = [c.get("no") for c in cuts if isinstance(c.get("no"), int)]
    if len(numbers) < 2:
        return []
    duplicated = sorted({n for n in numbers if numbers.count(n) > 1})
    if not duplicated:
        return []
    return [
        violation(
            "cut_numbering",
            f"{step_path}.stageDirections[].no",
            f"번호가 겹친다: {duplicated}. step 안에서 1부터 끊기지 않게 이어 쓴다",
        )
    ]


def lesson_has_audio(lesson: dict) -> bool:
    """이 차시에 소리가 하나라도 선언돼 있는가."""
    if lesson.get("audioMap"):
        return True
    for _path, cut in iter_speech_cuts(lesson):
        if cut.get("sound"):
            return True
    return False


def iter_speech_cuts(lesson: dict):
    """말풍선이 뜨는 컷(= `speechText` 가 있는 컷)만 훑는다.

    자막 전용 컷(`captionText` 만)은 말풍선이 없으므로 제외한다.
    """
    for step_index, step in enumerate(lesson.get("steps") or []):
        if not isinstance(step, dict):
            continue
        label = f"steps[{step_index}]" + (f" ({step['id']})" if step.get("id") else "")
        for cut_index, cut in enumerate(step.get("stageDirections") or []):
            if isinstance(cut, dict) and cut.get("speechText"):
                yield f"{label}.stageDirections[{cut_index}]", cut
        for round_index, round_ in enumerate(step.get("rounds") or []):
            if not isinstance(round_, dict):
                continue
            for cut_index, cut in enumerate(round_.get("stageDirections") or []):
                if isinstance(cut, dict) and cut.get("speechText"):
                    yield f"{label}.rounds[{round_index}].stageDirections[{cut_index}]", cut


def check_bubble_controls(lesson: dict) -> list[dict]:
    """말풍선의 스피커·`다음 ▸` 이 실제로 그려지는 상태인지 본다.

    base 는 컨트롤을 `type !== 'plain'` 일 때만 그리고, `다음 ▸` 은 `narrationNext` 에서만
    더 붙인다(`runtime/src/player.js:1972`). 타입은 **선언이 없으면 소리가 정한다** —
    `resolveBubbleType`(1932)이 `if (!hasSound) return 'plain'` 이다.

    **오디오가 있는 차시에는 이 검사를 걸지 않는다.** 배포 17차시는 대사 컷 287개 중 286개가
    `bubbleType` 을 안 적지만 `sound` 로 컨트롤이 켜진다 — 거기에 걸면 거짓 양성 286건이다.
    걸리는 것은 **소리가 하나도 없는 차시**뿐이고, 그때는 선언 말고 켤 방법이 없다.

    실측(2026-09-22): 이 판정식으로 배포 17차시 **거짓 양성 0건**, 우리 초안 43건 적발.

    왜 막는가 — 사용자 결정(2026-09-22): "모든 말풍선에 우선적으로 `다음` 버튼과 스피커
    아이콘을 넣되, 오디오를 아직 넣지 않아도 강제로 나오게 한다. 뺄 때는 사람이 정한다."
    """
    if lesson_has_audio(lesson):
        return []
    violations: list[dict] = []
    for path, cut in iter_speech_cuts(lesson):
        if cut.get("bubbleType") in ("narration", "narrationNext"):
            continue
        declared = cut.get("bubbleType")
        how = f"`{declared}` 로 적혔다" if declared else "안 적혔다"
        violations.append(
            violation(
                "bubble_controls_missing",
                f"{path}.bubbleType",
                f"bubbleType 이 {how}. 이 차시는 소리가 하나도 없어 선언이 없으면 `plain` 이 되고, "
                "그러면 말풍선의 스피커와 [다음 ▸] 이 통째로 안 그려진다. "
                "`narrationNext` 를 적는다 — 오디오 파일이 없어도 그렇게 한다",
            )
        )
    return violations


def check_cast_extra_sized(lesson: dict, run_dir: Path) -> list[dict]:
    """`castOnStage: "keep"` 를 켰으면 남은 인물의 크기를 차시가 정했는지 본다.

    base `updateCastExtras`(player.js:1876)는 `.charzone.cast-extra` 상자를 만들고 그 안에
    **클래스도 id 도 없는 `<img>`** 를 넣는다. base CSS 는 말하는 쪽만 `#charImg{width:100%}`
    (player.css:487)로 잡고 `.cast-extra img` 에는 `width` 를 주지 않는다(2390행은
    `display`·`filter` 뿐). 그래서 원본 픽셀 그대로 떠서 **말하지 않는 인물만 거대해진다.**

    실측(2026-09-22): `castOnStage:"keep"` 인 배포 4차시는 **전부** `.cast-extra img` 에 크기를
    준다(3-1/05 는 `width:100%`, 4-1/01 은 `height:var(--i1-char-h)`). 거짓 양성 0건이다.
    우리 초안 3개는 전부 켜 놓고 전부 안 줬다.
    """
    if (lesson.get("ui") or {}).get("castOnStage") != "keep":
        return []
    css_path = run_dir / "lesson" / "player-ext.css"
    if not css_path.exists():
        return [
            violation(
                "cast_extra_unsized",
                "lesson/player-ext.css",
                'ui.castOnStage 가 "keep" 인데 player-ext.css 가 없다. base 는 말하지 않는 인물의 '
                "크기를 안 주므로 그림이 원본 픽셀 그대로 떠서 혼자 거대해진다",
            )
        ]
    body = strip_css_comments(css_path.read_text(encoding="utf-8"))
    blocks = re.findall(r"\.cast-extra\s+img[^{]*\{([^}]*)\}", body)
    if any(re.search(r"\b(width|height)\s*:", block) for block in blocks):
        return []
    return [
        violation(
            "cast_extra_unsized",
            "lesson/player-ext.css",
            'ui.castOnStage 가 "keep" 인데 `.cast-extra img` 의 width/height 규칙이 없다. '
            "base 는 말하는 인물만 `#charImg{width:100%}` 로 잡는다 — 남은 인물은 원본 픽셀 그대로 "
            "떠서 혼자 거대해진다. `#app .cast-extra img { width: 100% }` 를 넣는다",
        )
    ]


def check_certificate_openable(lesson: dict, run_dir: Path) -> list[dict]:
    """인증서를 선언했으면 **여는 통로**가 있는지 본다.

    `ui.certificate` 는 패널의 **내용**이지 **여는 스위치가 아니다.** `renderOutroFrame` 은
    `clearSequence` 를 훑다가 `type === 'certificate'` 인 컷을 만났을 때만 패널을 연다
    (`runtime/src/player.js:4334`).

    실측(2026-09-17) — 4-2/02 에서 `ui.certificate` 12개 필드를 다 채워 놓고 컷을 안 넣어
    인증서가 한 번도 안 떴다. **schema·lesson_check·빌드·화면검사가 전부 통과했다.**

    예외 하나 — 차시 ext 가 `lessonCert.open()` 을 직접 부르면 컷 없이도 열린다.
    배포 중인 3-1/05 가 그렇게 한다("clearSequence 에서 certificate 컷을 뺐으므로 도장
    버튼이 인증서로 바뀌지 않는다" — 그쪽 ext 주석). 그 예외를 넣어야 거짓 양성 0 이다.

    `body` 는 따로 본다. 런타임이 `Array.isArray(c.body) && c.body.length` 로 거르므로
    문자열로 적으면 **원문 문구가 통째로 버려지고 base 기본 문구가 대신 나온다**(4768행).
    """
    cert = (lesson.get("ui") or {}).get("certificate")
    if not isinstance(cert, dict):
        return []

    violations: list[dict] = []

    body = cert.get("body")
    if body is not None and not isinstance(body, list):
        violations.append(
            violation(
                "certificate_body_not_list",
                "ui.certificate.body",
                f"body 가 {type(body).__name__} 다. 런타임은 배열일 때만 읽으므로 "
                "적어 둔 문구가 통째로 버려지고 기본 문구('인증서를 잘 보관해요.')가 대신 나온다. "
                "줄 단위 배열로 적는다",
            )
        )

    has_cut = any(
        isinstance(cut, dict) and cut.get("type") == "certificate"
        for step in (lesson.get("steps") or [])
        if isinstance(step, dict)
        for cut in (step.get("clearSequence") or [])
    )
    if has_cut:
        return violations

    ext_js = run_dir / "lesson" / "player-ext.js"
    if ext_js.exists() and "lessonCert.open(" in ext_js.read_text(encoding="utf-8"):
        return violations

    violations.append(
        violation(
            "certificate_never_opens",
            "steps[].clearSequence",
            "ui.certificate 를 선언했는데 clearSequence 에 {\"type\":\"certificate\"} 컷이 없다. "
            "ui.certificate 는 패널의 내용이지 여는 스위치가 아니다 — 런타임은 그 컷을 만났을 때만 "
            "패널을 연다(player.js:4334). 컷을 넣거나, player-ext.js 가 lessonCert.open() 을 직접 부른다",
        )
    )
    return violations


def check_stage_direction(cut: object, where: str) -> list[dict]:
    """장면 지시 한 컷이 렌더 가능한지 본다.

    `action` 은 렌더되지 않지만 **필수**다. 그쪽 파서가 요구한다 — 산문 메모가 있어야
    나중에 사람이 "이 컷이 무엇을 하려던 것인지" 대조할 수 있기 때문이다.
    렌더되지 않는다는 것과 없어도 된다는 것은 다르다.
    """
    if not isinstance(cut, dict):
        return [violation("cut_shape", where, "객체가 아니다")]

    violations = []
    if cut.get("no") is None:
        violations.append(violation("cut_no", where, "no(스토리보드 번호)가 없다"))
    if not cut.get("action"):
        violations.append(violation("cut_action", where, "action(연출 내용)이 없다"))

    # `source` 와 `layer` 도 렌더되지 않지만 필수다. 배포 중인 15개 차시의 컷 **573개 전부**가
    # 둘을 들고 있다(실측 2026-09-11, 예외 0건). `timing`·`motion`·`sound` 는 차시마다 편차가
    # 커서 게이트로 못 쓴다.
    #
    # 왜 이걸 막는가 — `source` 는 이 컷이 스토리보드 어디서 왔는지를 적는 자리다. 그게 없으면
    # 스토리보드의 어떤 지시가 통째로 빠졌는지 **아무도 기계적으로 알 수 없다.** 실측(2026-09-11):
    # 3-1/05 에서 장면별 인물 위치와 전환 연출이 전부 누락됐는데, schema PASS · 기존 게이트 PASS ·
    # 빌드 성공을 모두 통과하고 사람 눈에만 걸렸다. 그 차시의 컷 39개는 `source` 가 하나도 없었다.
    # `layer` 는 그 컷이 어느 채널을 건드리는지(배경·인물·말풍선·전환·오디오…)를 적는 자리라,
    # 연출 지시를 산문 대신 채널로 생각하게 만든다.
    if not str(cut.get("source") or "").strip():
        violations.append(
            violation("cut_source", where, "source(스토리보드 출처)가 없다. 어느 페이지·컷에서 왔는지 적는다")
        )
    if not str(cut.get("layer") or "").strip():
        violations.append(
            violation(
                "cut_layer",
                where,
                "layer(이 컷이 건드리는 채널)가 없다. "
                "background · character · speechBubble · caption · object · ui · cta · interactive · transition · audio 중에서 고른다",
            )
        )

    bubble = cut.get("bubbleType")
    if bubble is not None and bubble not in BUBBLE_TYPES:
        violations.append(
            violation("cut_bubble", where, f"bubbleType 허용값이 아니다: {bubble!r} — {list(BUBBLE_TYPES)}")
        )

    speech = cut.get("speechText")
    if speech is not None:
        if not isinstance(speech, str) or not speech.strip():
            violations.append(
                violation("cut_speech", where, "speechText 는 비어 있지 않은 문자열이어야 한다")
            )
        elif BR_PATTERN.search(speech):
            violations.append(
                violation("cut_speech_br", where, "speechText 에 <br> 를 넣지 않는다. 런타임이 문장 단위로 줄바꿈한다")
            )

    # 재생되지 않는 컷에 화면 요소를 달면 그것도 함께 사라진다.
    #     stageBeats = step.stageDirections.filter(d => d.speechText || d.captionText)
    # 실측(2026-09-08): ctaText 만 가진 컷 4개가 통째로 증발해 [시작하기] 버튼 라벨이 없어졌다.
    playable = bool(cut.get("speechText") or cut.get("captionText"))
    if not playable:
        carried = [key for key in ("ctaText", "motion", "backgroundRef") if cut.get(key)]
        if carried:
            violations.append(
                violation(
                    "cut_not_played",
                    where,
                    f"speechText/captionText 가 없어 이 컷은 재생되지 않는데 {carried} 를 달았다. "
                    "대사나 자막이 있는 컷에 함께 단다",
                )
            )

    # 재생되게 만들려고 captionText 에 아무거나 넣으면 화면에 나오면 안 되는 것이 자막이 된다.
    # 실측(2026-09-09): 배경 지시("외부에서 바라 본 경주 박물관"), 버튼 문구("[시작하기]"),
    # 표 데이터("구분/성인/어린이…")가 전부 자막으로 떴다.
    caption = str(cut.get("captionText") or "")
    if caption:
        if BRACKET_LABEL.fullmatch(caption.strip()):
            violations.append(
                violation(
                    "caption_is_button",
                    where,
                    f"버튼 문구를 자막에 넣었다: {caption.strip()[:30]!r}. ctaText 에 쓴다",
                )
            )
        elif ASSET_REF_PATTERN.match(caption.strip()):
            violations.append(
                violation("caption_is_ref", where, "asset 경로를 자막에 넣었다. backgroundRef 에 쓴다")
            )
        elif ".rounds[" in where:
            # round 컷에 자막을 쓰지 않는다. 배포 중인 세 차시(4-1/01·2-1/02·1-1/04)의
            # round 컷 12개에 captionText 가 **하나도 없다**. 그 자리는 대사를 쓰는 곳이고
            # 자료는 stimulus 가 받는다. step 컷의 자막은 정상이다(1-1/04 에 13건).
            #
            # 길이나 모양으로 "표인지" 재지 않는다. 그렇게 했더니 모델이 표를
            # `구분 / 성인 / 어린이` 처럼 다시 포맷해서 빠져나갔다(2026-09-09 실측).
            violations.append(
                violation(
                    "caption_in_round",
                    where,
                    f"round 컷에 자막을 넣었다: {caption.strip()[:36]!r}. "
                    "자막은 한 줄로 이어 읽는 문장이라 표나 자료를 넣으면 뭉개진다. "
                    "대사는 speechText 로, 자료는 문항의 stimulus 로 옮긴다",
                )
            )
        else:
            lines = [line.strip() for line in caption.splitlines() if line.strip()]
            if len(lines) >= 2 and sum(1 for line in lines if TABLE_SEPARATOR.search(line)) >= 2:
                violations.append(
                    violation(
                        "caption_is_table",
                        where,
                        f"표 데이터를 자막에 넣었다({len(lines)}줄: {lines[0][:24]}…). "
                        "자막은 한 줄로 이어 읽는 문장이라 표가 뭉개진다. stimulus 로 옮긴다",
                    )
                )

    # 스토리보드는 버튼을 `[시작하기]` 로 적는다. 그 대괄호는 "이건 버튼이다" 라는 표기이지
    # 버튼에 새길 글자가 아니다. 그대로 옮기면 화면에 대괄호가 찍힌다.
    cta = str(cut.get("ctaText") or "").strip()
    if cta and BRACKET_LABEL.fullmatch(cta):
        violations.append(
            violation(
                "cta_bracket_label",
                where,
                f"버튼 문구에 스토리보드 표기용 대괄호가 남았다: {cta!r}. "
                "괄호를 벗기고 안쪽 글자만 쓴다. exitCondition.buttonText 도 같이 고친다",
            )
        )

    emotion = cut.get("characterEmotion")
    if emotion is not None and emotion not in CHARACTER_EMOTIONS:
        violations.append(
            violation(
                "cut_emotion",
                where,
                f"characterEmotion 허용값이 아니다: {emotion!r} — {list(CHARACTER_EMOTIONS)}",
            )
        )
    return violations


def iter_asset_prompts(container: dict):
    """`assetPrompt` 로 끝나는 키를 전부 훑는다.

    그쪽 `imageGenerator._assetPromptFor` 와 **같은 규칙**이다 — 키 이름이 `assetPrompt` 나
    `...AssetPrompt` 로 끝나면 전부 후보이고, `targetAsset` 이 그림 경로와 같은 것을 고른다.
    그래서 한 step 이 배경·문제표면·소품에 각각 다른 지시를 달 수 있다(배포 2-2/05 가 7개).
    `step.assetPrompt` 하나만 보면 그 형태를 통째로 놓친다.
    """
    for key, value in (container or {}).items():
        if isinstance(value, dict) and (key.endswith("assetPrompt") or key.endswith("AssetPrompt")):
            yield key, value


def check_step_asset_prompt(step: dict, step_path: str) -> list[dict]:
    """`assetPrompt` 는 그쪽 이미지 생성기에 주는 지시다. 쓰려면 형식을 지켜야 한다.

    **이 파이프라인은 이미지를 만들지 않는다.** 그림은 그쪽 `npm run build:lesson` 의
    imagegen 이 굽고, 그때 무엇을 그릴지는 `artDirection` 과 이 `assetPrompt` 로만 정해진다.
    둘 다 없으면 그쪽은 **파일 이름으로 지어낸다** — `moon-jar.png` → "moon jar in
    educational setting". 그래서 반쯤 쓴 assetPrompt 는 빌드를 막고, 안 쓴 배경은 운에 맡긴다.
    """
    violations = []
    for key, asset_prompt in iter_asset_prompts(step):
        where = f"{step_path}.{key}"
        if not asset_prompt.get("sceneType"):
            violations.append(violation("asset_prompt", where, "sceneType 이 없다"))
        if not asset_prompt.get("targetAsset"):
            violations.append(
                violation(
                    "asset_prompt",
                    where,
                    "targetAsset 이 없다. 이 값이 그림 경로와 같아야 그 지시가 그 그림에 붙는다",
                )
            )
        if asset_prompt.get("sceneType") == "full-storyboard-panel":
            violations.append(
                violation(
                    "asset_prompt",
                    where,
                    'sceneType "full-storyboard-panel" 은 자동 생성 지시로 쓰지 않는다(base-background 를 쓴다)',
                )
            )
    return violations


def check_background_asset_prompt(lesson: dict) -> list[dict]:
    """배경 그림에 생성 지시가 붙었는지 본다.

    배경은 **요구사항이 가장 많은 그림**이다 — 무엇이 들어가야 하고, 어디를 런타임 UI 가
    덮으니 비워야 하는지가 정해져 있다. 그 자리를 안 비우면 그림 한가운데에 인물이 들어차고
    그 위에 문제 UI 가 겹친다. `reservedUiZones` 가 그걸 막는 유일한 통로다.

    막지는 않는다(warning) — 배포된 4-1/01 은 assetPrompt 가 0개인데도 화면이 나온다.
    다만 그 그림들은 파일 이름 수준의 지시만 받고 그려진 것이다.
    """
    targeted: set[str] = set()
    for step in lesson.get("steps") or []:
        if not isinstance(step, dict):
            continue
        for _key, asset_prompt in iter_asset_prompts(step):
            target = asset_prompt.get("targetAsset")
            if isinstance(target, str):
                targeted.add(target)

    violations = []
    for index, step in enumerate(lesson.get("steps") or []):
        if not isinstance(step, dict):
            continue
        background = step.get("backgroundRef") or step.get("startBackgroundRef")
        if not isinstance(background, str) or not background.startswith("assets/backgrounds/"):
            continue
        if background in targeted:
            continue
        violations.append(
            warning(
                "background_prompt_absent",
                f"steps[{index}].backgroundRef",
                f"{background} 에 생성 지시가 없다. 그쪽 imagegen 이 파일 이름으로 지어낸다. "
                "무엇이 들어가고 어디를 UI 가 덮는지는 assetPrompt(mustInclude·reservedUiZones)로만 전달된다",
            )
        )
    return violations


def has_source_panel(task: dict) -> bool:
    """한 장면이 여러 페이지에 걸치면 배열로 온다. 둘 다 받는다."""
    value = task.get("sourcePanel")
    if isinstance(value, list):
        return any(str(item).strip() for item in value)
    return bool(str(value or "").strip())


def check_coverage(builder_output: dict, planner_output: dict) -> list[dict]:
    """계획의 문항이 하나도 빠지지 않았는지 확정한다.

    문항 누락은 배치 뒤에는 아무도 못 찾는다. 화면이 멀쩡해 보이기 때문이다.
    """
    questions = [
        question.get("id")
        for section in planner_output.get("sections") or []
        if isinstance(section, dict)
        for question in section.get("questions") or []
        if isinstance(question, dict)
    ]
    done = set(builder_output.get("implemented_questions") or [])
    missing = [value for value in questions if value and value not in done]
    if not missing:
        return []
    return [
        violation(
            "question_lost",
            "implemented_questions",
            f"계획의 문항 {len(missing)}개가 안 실렸다: {missing[:5]}",
        )
    ]


def check_top_level(lesson: dict) -> list[dict]:
    violations = []
    if lesson.get("specVersion") != 2:
        violations.append(
            violation(
                "spec_version",
                "root.specVersion",
                "2 가 아니다. 빠지면 gyo6_content 검증기의 스토리보드 충실도 검사가 통과로 처리된다",
            )
        )
    for key in FORBIDDEN_TOP_LEVEL:
        if key in lesson:
            violations.append(
                violation("legacy_field", f"root.{key}", "런타임이 읽지 않는 옛 스키마 필드다. 지운다")
            )
    ui = lesson.get("ui")
    if not isinstance(ui, dict) or "courseMenu" not in ui:
        violations.append(
            violation(
                "common_ui",
                "root.ui.courseMenu",
                '선언이 없어 헤더 차시 목록이 안 붙는다. 빈 객체 {} 로 충분하고 목록은 빌드가 채운다',
            )
        )
    # gyo6_content `agent/lessonParser.mjs` 의 REQUIRED_FIELDS 와 같아야 한다.
    # 거기서는 없으면 곧바로 throw 이므로 npm run validate 가 통째로 죽는다.
    for key in ("id", "title", "subject", "grade", "lessonNo"):
        if not str(lesson.get(key) or "").strip():
            violations.append(violation("missing_field", f"root.{key}", "비어 있다"))

    # 식별자의 **모양**을 본다. 그쪽 파서는 존재만 보므로 여기서 안 보면 아무도 안 본다.
    # 실측: 화풍 참조 세트 이름이 차시 식별자로 새어 `id` 가
    # 'gyo6-1-1-04-big-numbers-museum', `lessonNo` 가 '1-1-04' 으로 나왔다.
    # 빌드는 통과하지만 커리큘럼에서 이 차시가 어느 칸인지 알 수 없게 된다.
    lesson_id = str(lesson.get("id") or "")
    if lesson_id and not re.fullmatch(r"\d{2}", lesson_id):
        violations.append(
            violation("id_shape", "root.id", f"차시 번호 두 자리여야 한다(예: '01'): {lesson_id!r}")
        )
    lesson_no = str(lesson.get("lessonNo") or "")
    if lesson_no and not re.fullmatch(r"\d-\d{2}", lesson_no):
        violations.append(
            violation("id_shape", "root.lessonNo", f"'{{학기}}-{{차시}}' 여야 한다(예: '1-01'): {lesson_no!r}")
        )
    return violations


def check_ui_declarations(lesson: dict) -> list[dict]:
    """배치·연출 옵트인이 **실제로 읽는 이름**으로 선언됐는지 본다.

    이 축의 실패는 오류를 내지 않는다. 이름이 틀리면 그 UI 는 그냥 안 뜨고, 데이터는 유효하고
    빌드도 성공한다. 그래서 "화면이 base 기본값 그대로 나왔다"는 결과만 남고 무엇이 빠졌는지는
    아무 데도 안 적힌다(problem.md `no-per-lesson-css-layout-raw`).

    판정 기준은 문서가 아니라 **런타임과 배포된 차시**다. `atom_registry` 가 원자 어휘에서 겪은
    드리프트와 같은 성격이다 — 대상 레포 문서가 런타임보다 앞서거나 뒤처진다. 그래서 여기 실린
    이름은 전부 배포된 18차시에 돌려 거짓 양성을 걷어낸 것이다.
    """
    violations: list[dict] = []
    ui = lesson.get("ui") if isinstance(lesson.get("ui"), dict) else {}

    for key, why in UI_KEYS_UNREAD.items():
        if key in ui:
            violations.append(
                warning(
                    "ui_unread_key",
                    f"root.ui.{key}",
                    f"아무도 읽지 않는다({why}). 이 선언 때문에 만든 이미지는 화면에 안 나온다",
                )
            )

    title_logo = ui.get("titleLogoRef")
    if title_logo is not None and title_logo != TITLE_LOGO_PATH:
        violations.append(
            warning(
                "ui_bad_value",
                "root.ui.titleLogoRef",
                f"base 는 {TITLE_LOGO_PATH} 를 경로째 하드코딩해 그린다. 다른 경로를 적으면 "
                f"그 그림은 화면에 안 나오고 하드코딩된 자리는 비어 있게 된다: {title_logo!r}",
            )
        )

    bubble = ui.get("speechBubble")
    if isinstance(bubble, dict):
        if "position" in bubble and "side" not in bubble:
            # 배포된 18차시 중 16차시가 `position` 으로 적어 놨다. 대상 레포 CLAUDE.md 가
            # 그렇게 적어 놨기 때문이고, 런타임(`player.js:1689`)은 `side` 만 읽는다.
            # 전 차시가 걸리는 축이라 막지 않고 알린다 — 다만 우리 산출물은 `side` 를 쓴다.
            violations.append(
                warning(
                    "ui_stale_field",
                    "root.ui.speechBubble.position",
                    f"런타임이 읽는 이름은 side 다(값: {'|'.join(SPEECH_BUBBLE_SIDES)}). "
                    "position 은 대상 레포 문서에만 있는 이름이라 선언이 조용히 죽고 말풍선이 "
                    "기본 위치(above)로 나온다",
                )
            )
        side = bubble.get("side")
        if side is not None and side not in SPEECH_BUBBLE_SIDES:
            violations.append(
                violation(
                    "ui_bad_value",
                    "root.ui.speechBubble.side",
                    f"{side!r} 는 허용값이 아니다: {'|'.join(SPEECH_BUBBLE_SIDES)}",
                )
            )

    cast_on_stage = ui.get("castOnStage")
    if cast_on_stage is not None and cast_on_stage != "keep":
        violations.append(
            warning(
                "ui_bad_value",
                "root.ui.castOnStage",
                f'{cast_on_stage!r} 는 "keep" 이 아니라 아무 일도 하지 않는다',
            )
        )

    for where, position in iter_character_positions(lesson):
        if position not in CHARACTER_POSITIONS:
            violations.append(
                violation(
                    "ui_bad_value",
                    where,
                    f"{position!r} 는 허용값이 아니다: {'|'.join(CHARACTER_POSITIONS)}",
                )
            )
    return violations


def check_title_logo_tracked(lesson: dict) -> list[dict]:
    """타이틀 로고가 **그쪽 빌드의 생성 대상으로 잡히는지** 본다. 초안 경로 전용이다.

    이 경로는 에셋을 하나도 만들지 않고 그쪽 `npm run build:lesson` 의 imagegen 에 맡긴다.
    그쪽이 무엇을 만들지는 `collectAssets` 가 lesson.json 문자열에서 훑어 정하므로,
    이 경로가 lesson.json 어디에도 문자열로 없으면 **아무도 그 그림을 만들지 않는다.**
    그런데 base 는 그 자리를 하드코딩해서 그리므로 타이틀 화면에 깨진 그림이 뜬다.

    emit 경로에는 걸지 않는다 — 거기서는 우리가 파일을 직접 만들어 배치한다.
    """
    has_intro = any(
        isinstance(step, dict) and step.get("type") == "intro" for step in lesson.get("steps") or []
    )
    if not has_intro or TITLE_LOGO_PATH in dump_strings(lesson):
        return []
    return [
        violation(
            "title_logo_untracked",
            "root.ui.titleLogoRef",
            f"{TITLE_LOGO_PATH} 가 lesson.json 어디에도 없다. 이 경로는 에셋을 만들지 않고 "
            "그쪽 빌드에 맡기는데, 그쪽은 lesson.json 문자열에서 만들 것을 정하므로 이대로면 "
            "그 그림이 생성되지 않는다. base 는 그 자리를 하드코딩해 그리므로 타이틀 화면이 "
            f'깨진다. `"ui": {{ "titleLogoRef": "{TITLE_LOGO_PATH}" }}` 로 적는다',
        )
    ]


def iter_character_positions(lesson: dict):
    """step 단위 캐릭터 위치 선언을 훑는다. 미지정은 intro=right, 나머지 left 가 기본이다."""
    for index, step in enumerate(lesson.get("steps") or []):
        if not isinstance(step, dict):
            continue
        character = step.get("character")
        if isinstance(character, dict) and character.get("position") is not None:
            yield f"steps[{index}].character.position", character["position"]


# exitCondition.type — step 타입마다 다르다.
EXIT_TYPES = {
    "intro": "buttonClick",
    "tutorial": "allMissionsComplete",
    "problemBank": "allProblemsComplete",
}


def check_step_flow(lesson: dict) -> list[dict]:
    """step 이 실제로 이어지는지 본다.

    런타임은 `goToStep(step.exitCondition?.transitionTo)` 로 넘어가고, 그 안에서
    `L.steps.findIndex(s => s.id === targetId)` 로 대상을 찾는다. 그래서 둘 다 필요하다.

    실측(2026-09-08): 세 step 모두 `exitCondition` 이 없어 `[시작하기]` 를 11번 눌러도
    타이틀 화면에 머물렀다. **데이터는 유효했고 그쪽 검증기도 빌드도 통과했다** —
    playwright 로 클릭해 보고서야 찾았다.
    """
    steps = [s for s in (lesson.get("steps") or []) if isinstance(s, dict)]
    if not steps:
        return []
    violations = []

    ids = [str(s.get("id") or "") for s in steps]
    for index, (step, sid) in enumerate(zip(steps, ids)):
        where = f"steps[{index}]({step.get('type', '?')})"
        if not sid:
            violations.append(
                violation("step_id", f"{where}.id", "id 가 없다. transitionTo 가 가리킬 대상이 없다")
            )
    present = [value for value in ids if value]
    duplicated = sorted({value for value in present if present.count(value) > 1})
    if duplicated:
        violations.append(
            violation("step_id", "steps[].id", f"같은 id 가 둘 이상이다: {duplicated}")
        )

    known = {value for value in ids if value}
    for index, step in enumerate(steps):
        where = f"steps[{index}]({step.get('type', '?')})"
        last = index == len(steps) - 1
        exit_condition = step.get("exitCondition")
        if not isinstance(exit_condition, dict):
            if not last:
                violations.append(
                    violation(
                        "step_exit",
                        f"{where}.exitCondition",
                        "없다. transitionTo 가 undefined 라 버튼을 눌러도 넘어가지 않는다",
                    )
                )
            continue

        target = str(exit_condition.get("transitionTo") or "")
        if not target:
            if not last:
                violations.append(
                    violation("step_exit", f"{where}.exitCondition.transitionTo", "비어 있다")
                )
        elif target not in known:
            violations.append(
                violation(
                    "step_exit",
                    f"{where}.exitCondition.transitionTo",
                    f"그런 step id 가 없다: {target!r}. 조용히 아무 일도 안 한다",
                )
            )

        expected = EXIT_TYPES.get(step.get("type"))
        actual = exit_condition.get("type")
        if expected and actual and actual != expected:
            violations.append(
                violation(
                    "step_exit",
                    f"{where}.exitCondition.type",
                    f"{step.get('type')} 는 {expected!r} 를 쓴다: {actual!r}",
                )
            )
    return violations


def check_steps(lesson: dict) -> list[dict]:
    violations = []
    steps = lesson.get("steps")
    if not isinstance(steps, list) or not steps:
        return [violation("missing_field", "root.steps", "비어 있다")]
    violations += check_step_flow(lesson)

    types = [step.get("type") for step in steps if isinstance(step, dict)]
    unknown = [value for value in types if value not in STEP_ORDER]
    if unknown:
        violations.append(
            violation("step_type", "steps[].type", f"허용되지 않는 타입: {sorted(set(unknown))}")
        )

    known = [value for value in types if value in STEP_ORDER]
    ranks = [STEP_ORDER.index(value) for value in known]
    if ranks != sorted(ranks):
        violations.append(
            violation(
                "step_order",
                "steps[]",
                f"intro → tutorial → problemBank → outro 순서가 아니다: {known}",
            )
        )
    if "problemBank" not in known:
        violations.append(violation("step_missing", "steps[]", "problemBank 단계가 없다"))
    return violations


def check_atoms(
    lesson: dict,
    has_ext_js: bool = False,
    registry: dict[str, list[str]] | None = None,
) -> list[dict]:
    """원자 이름과 필수 필드를 본다.

    `registry` 가 주어지면 그것이 기준이다 — gyo6_content 런타임에서 직접 읽은 것이라
    "이름은 있는데 화면에 안 나오는" 경우를 정확히 가른다. 없으면 문서 표로 떨어진다.
    """
    base_rendered = set(registry) if registry else set(FALLBACK_BASE_RENDERED_ATOMS)
    required_fields = registry if registry else FALLBACK_ATOM_REQUIRED_FIELDS
    violations = []
    for where, task in iter_scenes(lesson):
        interaction = task.get("interaction")
        if not isinstance(interaction, dict):
            # 조작이 없는 장면도 있다 — 완료 화면처럼 acceptance 만 가진 노드다.
            # gyo6_content 도 `if (node.interaction) checkInteraction(...)` 으로 건너뛴다.
            # 여기서 막으면 배포 중인 차시가 반려된다(실측: 2-1/02 의 steps[3].completion).
            # 미션에 interaction 이 없는 것은 `check_step_structure` 가 따로 잡는다.
            continue

        if "interactionType" in task or "interactionType" in interaction:
            violations.append(
                violation("legacy_field", where, "interactionType 은 옛 형태다. primitives 를 쓴다")
            )

        primitives = interaction.get("primitives")
        if not isinstance(primitives, list) or not primitives:
            violations.append(
                violation("missing_primitives", where, "interaction.primitives 가 비어 있다")
            )
            continue

        # 어휘는 문서 표와 **런타임 레지스트리의 합집합**이다. 런타임이 문서보다 앞서 갈 수 있다 —
        # 실측: 4-1/01 이 쓰는 judgeRows 는 PROBLEM_ATOMS 에 있는데 문서 13종에는 없다.
        allowed = set(PROBLEM_ATOM_VOCAB) | base_rendered
        for name in primitives:
            if name not in allowed:
                violations.append(
                    violation(
                        "unknown_atom",
                        where,
                        f"어휘 밖의 이름이다: {name!r}. 지어내지 말고 unmapped 로 보고한다",
                    )
                )
                continue
            if name not in base_rendered:
                # ext 가 있으면 거기서 그릴 수 있다. gyo6_content 도 같은 판정이다.
                make = warning if has_ext_js else violation
                violations.append(
                    make(
                        "unrendered_atom",
                        where,
                        f"{name} 은 base 렌더러가 없다. player-ext.js 에서 처리되는지 확인한다",
                    )
                )
            missing = missing_atom_fields(name, required_fields, interaction, task)
            if missing:
                make = warning if has_ext_js else violation
                violations.append(
                    make("atom_field", where, f"{name} 의 필수 필드가 비었다: {missing}")
                )
    return violations


def missing_atom_fields(
    name: str,
    required_fields: dict,
    interaction: dict,
    task: dict,
) -> list[str]:
    """gyo6_content `checkAtomFields` 와 같은 판정.

    두 가지가 우리보다 느슨하다. 맞추지 않으면 멀쩡한 차시를 반려한다.

    · `answer` 는 `interaction.answer` 가 없으면 **문항 노드의 answer** 를 본다.
    · 빈 문자열은 누락으로 세지 않는다(`undefined`/`null`/빈 배열만).
    """
    required = required_fields.get(name) or ()
    if not required:
        # 필수 필드가 없는 원자는 커버리지 쪽에서 다룬다.
        return []
    missing = []
    for field in required:
        value = interaction.get(field)
        if field == "answer" and value is None:
            value = task.get("answer")
        if value is None or (isinstance(value, (list, tuple)) and not value):
            missing.append(field)
    return missing


def is_scene(node: dict) -> bool:
    """gyo6_content `lessonParser.isScene` 과 같은 판정.

    `interaction` 이 있거나 `acceptance` 배열이 있으면 장면이다. 문항·미션만 훑으면
    outro 의 scenes 나 intro 안의 상호작용처럼 **다른 자리에 있는 장면을 통째로 놓친다** —
    그쪽은 트리 전체를 걷는다.
    """
    return bool(node.get("interaction")) or isinstance(node.get("acceptance"), list)


def locate(node: dict, node_path: str) -> str:
    """사람이 읽을 위치 표시. 되먹임 프롬프트에 그대로 실리므로 어디를 고칠지 보여야 한다."""
    name = (
        node.get("title")
        or node.get("label")
        or node.get("prompt")
        or node.get("question")
        or node.get("id")
    )
    if not name:
        return node_path or "root"
    return f'{node_path or "root"} ("{str(name)[:40]}")'


def iter_scenes(lesson: dict):
    """트리 전체를 걸으며 장면을 낸다. gyo6_content `validateFidelity` 의 walk 와 같다."""
    seen: set[int] = set()

    def walk(node: object, node_path: str):
        if node is None or not isinstance(node, (dict, list)):
            return
        if id(node) in seen:
            return
        seen.add(id(node))
        if isinstance(node, list):
            for index, child in enumerate(node):
                yield from walk(child, f"{node_path}[{index}]")
            return
        if is_scene(node):
            yield locate(node, node_path), node
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                yield from walk(value, f"{node_path}.{key}")

    yield from walk(lesson, "")


def check_ext(lesson: dict, builder_output: dict, run_dir: Path) -> list[dict]:
    """player-ext.{js,css}가 base와 싸우지 않는지 본다.

    ext는 base 뒤에 그대로 이어붙는 같은 스코프다. 그래서 base가 이미 하는 일을 다시 하면
    두 구현이 공존하고, 같은 버그를 두 곳에서 고쳐야 한다. gyo6_content가 실측으로 겪은
    문제다 — 16개 차시 중 인증서 16/16, 뒤로가기 15/16이 각자 다시 구현돼 있었다.
    """
    violations = []
    ui = lesson.get("ui") if isinstance(lesson.get("ui"), dict) else {}
    scene_layout_owned = ui.get("sceneLayout") == "lesson"

    js_path = str(builder_output.get("player_ext_js_path") or "")
    css_path = str(builder_output.get("player_ext_css_path") or "")

    if js_path:
        source = read_text(run_dir / js_path)
        if source is None:
            violations.append(violation("missing_file", js_path, "보고했는데 파일이 없다"))
        else:
            violations += check_ext_js(js_path, source)
    if css_path:
        source = read_text(run_dir / css_path)
        if source is None:
            violations.append(violation("missing_file", css_path, "보고했는데 파일이 없다"))
        else:
            violations += check_ext_css(css_path, source, scene_layout_owned)

    if scene_layout_owned and not css_path:
        violations.append(
            violation(
                "layout_orphan",
                "ui.sceneLayout",
                '"lesson" 을 선언하면 base 기하가 꺼지는데 player-ext.css 가 없다. '
                "배치를 아무도 소유하지 않는다",
            )
        )
    elif not css_path:
        # `player-ext.js` 는 비는 것이 정상이지만 CSS 는 다르다. 없으면 모든 요소가
        # base 기본 위치에 그냥 놓여 이 차시만의 화면 구성이 아무 데도 없다.
        # 실측(2026-09-08): 0줄로 냈더니 레이아웃이 정돈되지 않았다.
        # gyo6_content 기존 차시는 1,206~7,285줄을 쓴다.
        violations.append(
            violation(
                "no_lesson_css",
                "player_ext_css_path",
                "player-ext.css 가 없다. 캐릭터·말풍선 배치, 문제 표면 크기, 글자 크기가 "
                "base 기본값 그대로가 된다",
            )
        )
    return violations


def check_ext_js(where: str, source: str) -> list[dict]:
    violations = []
    if "window.lessonExt" not in source:
        violations.append(
            violation("ext_no_hook", where, "window.lessonExt 등록이 없다. base가 부를 수 없다")
        )
    for pattern in ("L.id ===", "L.id ==", "L.id !==", "L.id!="):
        if pattern in source:
            violations.append(
                violation(
                    "ext_id_hardcoded",
                    where,
                    f"차시 id 분기가 있다({pattern}). 차이는 lesson.json 의 데이터 필드로 표현한다",
                )
            )
            break
    for marker, what in (
        ("lessonSettingsBtn", "소리 설정"),
        ("data-audio-settings", "소리 설정"),
        ("installVoiceVolumeButton", "음성 볼륨(레거시)"),
        ("course-menu", "차시 목록"),
        ("courseMenuPanel", "차시 목록"),
    ):
        if marker in source:
            violations.append(
                violation(
                    "ext_reimplements_base",
                    where,
                    f"{what} UI를 자체 구현한다({marker}). base가 소유하므로 선언만 한다",
                )
            )
    violations += check_ext_reentry_guard(where, source)
    return violations


# 화면을 넘기는 호출과, 연타를 한 번으로 접는 흔적.
TRANSITION_CALL = re.compile(r"\bgoToStep\s*\(|\bfadeSwap\s*\(|\bnextLocation\s*\(")
REENTRY_GUARD = re.compile(r"\bonce\s*\(|\bused\b|\bswapping\b|isTransitioning|\bguard(?:ed)?\b|\blocked\b")


def check_ext_reentry_guard(where: str, source: str) -> list[dict]:
    """화면을 넘기는 ext 에 연타 가드가 있는지 본다.

    대상 레포가 배포 뒤에 같은 결함을 두 차시에서 고쳤다 —
    `fix(2-2/01): CTA·뒤로가기 연타 시 전환 반복`, `fix(2-2/05): 시작하기·CTA 연타 시 검은 화면·장소 건너뜀`.
    두 번 먹으면 같은 전환이 두 번 예약돼 페이드가 누른 횟수만큼 반복되거나, 장소를 한 칸 건너뛰거나,
    막이 안 걷혀 멈춘다. **아이는 버튼을 한 번 누르지 않는다.**

    막지는 않는다(warning). 가드의 형태는 여러 가지이고, 이름만 보고 없다고 단정할 수 없다.
    """
    if not TRANSITION_CALL.search(source) or REENTRY_GUARD.search(source):
        return []
    return [
        warning(
            "ext_no_reentry_guard",
            where,
            "화면을 넘기는 호출이 있는데 연타 가드가 안 보인다. 두 번 눌리면 같은 전환이 두 번 "
            "예약돼 페이드가 반복되거나 화면을 건너뛴다. 넘기는 버튼은 once() 로 감싼다",
        )
    ]


CQ_UNIT = re.compile(r"[0-9.]+cq[whib]")
ABS_UNIT = re.compile(r"[0-9.]+(?:px|v[hw])")


def strip_css_comments(source: str) -> str:
    """`/* ... */` 를 걷어낸다. 줄 수는 유지해 위반 위치가 어긋나지 않게 한다.

    왜 필요한가 — 이 검사들은 전부 **문자열 매칭**이라 주석 안의 글자를 규칙으로 읽는다.
    실측(2026-09-11): `.charzone 에 overflow:hidden 을 걸면 안 된다` 라는 **경고 주석**이
    `layout_conflict` 로 잡혀 멀쩡한 번들이 반려됐다. 주석에 적은 `216px`·`547px` 같은
    실측 메모도 `ext_absolute_units` 의 px 카운트에 들어가 단위 비율을 왜곡한다.
    """
    out = []
    i = 0
    while i < len(source):
        start = source.find("/*", i)
        if start < 0:
            out.append(source[i:])
            break
        out.append(source[i:start])
        end = source.find("*/", start + 2)
        if end < 0:
            out.append("\n" * source.count("\n", start))
            break
        out.append("\n" * source.count("\n", start, end))
        i = end + 2
    return "".join(out)


def check_ext_css(where: str, source: str, scene_layout_owned: bool) -> list[dict]:
    violations = []
    source = strip_css_comments(source)

    # 무대는 16:9 컨테이너다. 거기 비례하는 단위(cqw/cqh)로 잡아야 창 크기가 바뀌어도
    # 배치가 그대로 간다. px·vh 로 잡으면 한 해상도에서만 맞고 나머지에서 무너진다.
    #
    # 배포 중인 차시가 전부 그렇게 쓴다 — 4-1/01 cq264:px14, 2-1/02 cq844:px58,
    # 1-1/04 cq652:px124. 우리 산출물은 **cq 0회, px 56, vh 6** 이었고, 그래서 720px
    # 높이에서 확인 버튼이 화면 밖으로 밀렸다(2026-09-09 실측).
    cq_count = len(CQ_UNIT.findall(source))
    abs_count = len(ABS_UNIT.findall(source))
    total = cq_count + abs_count
    if total >= 10 and cq_count / total < 0.5:
        violations.append(
            violation(
                "ext_absolute_units",
                where,
                f"길이를 px·vh 로 잡았다(cq {cq_count}회 : px·vh {abs_count}회). "
                "무대는 16:9 컨테이너라 `cqw`·`cqh` 로 잡아야 창 크기가 바뀌어도 배치가 유지된다. "
                "배포 중인 차시는 전부 cq 가 절대다수다(4-1/01 264:14, 2-1/02 844:58). "
                "테두리 두께 같은 잔값만 px 로 남긴다",
            )
        )

    if "!important" in source:
        violations.append(
            violation(
                "ext_important",
                where,
                "!important 로 base 를 덮는다. 선택자 구조나 sceneLayout 소유권으로 해결한다",
            )
        )
    if not scene_layout_owned:
        # `#app` 으로 스코프한 규칙은 base 와 싸우지 않는다 — 명시도를 한 단계 올려
        # 이 차시 안으로만 범위를 좁히는 정상적인 방법이다.
        # 배포 중인 4-1/01 이 `#app.i1-prob .charzone { display:none }` 을 이렇게 쓰며,
        # `sceneLayout` 은 선언하지 않는다. 그것까지 막으면 멀쩡한 차시가 반려된다.
        unscoped = [
            line
            for line in source.splitlines()
            if any(marker in line for marker in (".charzone", ".speech"))
            and "#app" not in line
            and not line.lstrip().startswith(("/*", "*", "//"))
        ]
        if unscoped:
            violations.append(
                violation(
                    "layout_conflict",
                    where,
                    "캐릭터·말풍선 기하를 `#app` 스코프 없이 건드린다. base 규칙과 같은 명시도로 "
                    f"싸운다: {unscoped[0].strip()[:60]!r}",
                )
            )
    return violations


def read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def check_text_preserved(lesson: dict, planner_output: dict) -> list[dict]:
    """planner가 원문에서 옮겨온 문구가 lesson.json 안에 남아 있는지 본다.

    옮기는 stage는 다듬고 싶어 한다. 문항을 요약하거나 보기를 줄이면 학습 내용이 조용히
    사라지는데, 그것은 배치 뒤에는 아무도 못 찾는다. 정규화해 비교하므로 줄바꿈·공백 손질은
    손실로 세지 않는다.
    """
    haystack = normalize(dump_strings(lesson))
    violations = []
    for section in planner_output.get("sections") or []:
        if not isinstance(section, dict):
            continue
        section_id = section.get("id", "?")
        for question in section.get("questions") or []:
            if not isinstance(question, dict):
                continue
            question_id = question.get("id", "?")
            for label, value in question_texts(question):
                if value and normalize(value) not in haystack:
                    violations.append(
                        violation(
                            "text_lost",
                            f"{section_id}/{question_id}",
                            f"{label} 이 lesson.json 에 없다: {value[:40]!r}",
                        )
                    )
    return violations


def question_texts(question: dict):
    yield "문항 문구", str(question.get("prompt") or "")
    for choice in question.get("choices") or []:
        if isinstance(choice, dict):
            yield "보기", str(choice.get("label") or "")
        else:
            yield "보기", str(choice)


def dump_strings(node: object) -> str:
    """중첩 구조의 모든 문자열을 한 줄로 잇는다. 어느 필드에 실렸든 남아 있으면 통과다."""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return " ".join(dump_strings(value) for value in node.values())
    if isinstance(node, list):
        return " ".join(dump_strings(value) for value in node)
    if isinstance(node, (int, float)):
        return str(node)
    return ""


def check_placements(builder_output: dict, planner_output: dict, run_dir: Path) -> list[dict]:
    violations = []
    placements = builder_output.get("asset_placements") or []
    planned_ids = {
        asset.get("id")
        for asset in planner_output.get("asset_plan") or []
        if isinstance(asset, dict)
    }

    destinations: list[str] = []
    for index, placement in enumerate(placements):
        if not isinstance(placement, dict):
            continue
        where = f"asset_placements[{index}]"
        asset_id = placement.get("asset_id")
        source = str(placement.get("source_path") or "")
        destination = str(placement.get("dest_path") or "")
        destinations.append(destination)

        if asset_id not in planned_ids:
            violations.append(
                violation("unknown_asset", where, f"planner asset_plan 에 없는 id 다: {asset_id!r}")
            )
        if resolve_source(run_dir, source) is None:
            violations.append(violation("missing_file", where, f"원본 파일이 없다: {source}"))
        if destination.startswith("assets/character/"):
            stem = Path(destination).stem
            if stem not in CHARACTER_EMOTIONS and "-" not in stem:
                violations.append(
                    violation(
                        "emotion_name",
                        where,
                        f"주인공 감정 6종({', '.join(CHARACTER_EMOTIONS)})이 아니다: {stem!r}",
                    )
                )

    duplicated = sorted({value for value in destinations if destinations.count(value) > 1})
    if duplicated:
        violations.append(
            violation("duplicate_dest", "asset_placements", f"같은 목적지가 둘 이상이다: {duplicated}")
        )
    return violations


def resolve_source(run_dir: Path, source: str) -> Path | None:
    """계획된 경로의 파일을 찾되 확장자는 따지지 않는다.

    asset의 정체는 stem이지 확장자가 아니다. planner는 늘 .png로 계획하는데 산출물을
    .webp로 압축해 두면 계획한 이름으로는 하나도 못 찾는다(runner.resolve_existing_asset과 같은 이유).
    """
    if not source:
        return None
    exact = run_dir / source
    if exact.exists():
        return exact
    for suffix in ASSET_SUFFIXES:
        candidate = exact.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def normalize(text: str) -> str:
    return "".join(text.split())


def violation(kind: str, where: str, detail: str, severity: str = "error") -> dict:
    return {"kind": kind, "where": where, "detail": detail, "severity": severity}


def warning(kind: str, where: str, detail: str) -> dict:
    """막지는 않고 알린다.

    gyo6_content 가 `warn` 으로 두는 것을 우리가 오류로 막으면, **실제로 배포돼 도는 차시를
    반려한다.** 실측으로 확인했다 — 우리 게이트를 2-1/02·4-1/01(둘 다 배포 중)에 걸었더니
    21건이 걸렸고 그 대부분이 이 성격이었다.
    """
    return violation(kind, where, detail, severity="warn")


def errors_only(violations: list[dict]) -> list[dict]:
    return [item for item in violations if item.get("severity", "error") == "error"]


def format_violations(violations: list[dict]) -> str:
    errors = errors_only(violations)
    warns = [item for item in violations if item.get("severity") == "warn"]
    if not errors and not warns:
        return "확정된 위반 없음"
    lines = []
    if errors:
        lines.append(f"확정된 위반 {len(errors)}건 (배치를 막는다)")
        lines += [f"  · [{item['kind']}] {item['where']} — {item['detail']}" for item in errors]
    if warns:
        lines.append(f"경고 {len(warns)}건 (막지 않는다)")
        lines += [f"  · [{item['kind']}] {item['where']} — {item['detail']}" for item in warns]
    return "\n".join(lines)


def coverage_report(builder_output: dict, planner_output: dict) -> str:
    """무엇이 실렸고 무엇이 안 실렸는지 한 줄로 낸다. 위반은 아니지만 사람이 봐야 한다."""
    sections = [
        section.get("id")
        for section in planner_output.get("sections") or []
        if isinstance(section, dict)
    ]
    questions = [
        question.get("id")
        for section in planner_output.get("sections") or []
        if isinstance(section, dict)
        for question in section.get("questions") or []
        if isinstance(question, dict)
    ]
    done_sections = set(builder_output.get("implemented_sections") or [])
    done_questions = set(builder_output.get("implemented_questions") or [])
    missing_sections = [value for value in sections if value not in done_sections]
    missing_questions = [value for value in questions if value not in done_questions]
    unmapped = builder_output.get("unmapped") or []

    lines = [
        f"화면 {len(done_sections)}/{len(sections)} · 문항 {len(done_questions)}/{len(questions)} · unmapped {len(unmapped)}건"
    ]
    if missing_sections:
        lines.append(f"  안 실린 화면: {missing_sections}")
    if missing_questions:
        lines.append(f"  안 실린 문항: {missing_questions}")
    for item in unmapped:
        if isinstance(item, dict):
            lines.append(
                f"  · unmapped {item.get('section_id', '?')}/{item.get('question_id', '')} "
                f"— {item.get('needed_action', '')}: {item.get('why', '')}"
            )
    return "\n".join(lines)
