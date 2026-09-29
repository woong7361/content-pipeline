"""`lesson.json` 에서 **소리를 붙일 수 있는 글**을 모으고, 만든 음성을 다시 적어 넣는다.

런타임(gyo6 `runtime/src/player.js`)이 실제로 재생하는 자리만 모은다. 재생 통로가 없는 곳에
mp3 를 만들면 크레딧만 쓰고 화면에 안 닿는다.

    컷 대사          stageDirections[].speechText        → 그 컷의 `sound`
    문제 안내 말풍선  problems[].semiDialogue ?? prompt    → 그 문제의 `narration`
    인물 힌트        problems[].hintAfterWrong.speechText → `hintAfterWrong.sound`
    이야기 카드      realLifeSlide.slides[].title+caption → 카드의 `narration: {audio}`
                     (글 없이 audio 만 주면 화면에 글을 겹쳐 띄우지 않고 소리만 낸다)

재생 통로가 **없어서** 모으지 않는 것 — 보고서에 남긴다.

    자막만 있는 컷(captionText, speechText 없음)  setSpeechBubble('') 가 소리 전에 돌아간다
    정답·오답 말풍선                              setSpeech() 는 sound 를 받지 않는다

`sound` id 는 `audioMap.narration` 에서 찾는다(`resolveAudioSource`: narration → sfx → bgm).
배포 차시 규약과 같다 — `{"take1-1": "assets/audio/narration/take1-1.wav"}` + 컷 `"sound": "take1-1"`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

NARRATOR = "narrator"
AUDIO_DIR = "assets/audio/narration"
ID_PREFIX = "vo-"


@dataclass
class Line:
    audio_id: str
    kind: str                    # cut · problem · hint · slide
    speaker: str                 # cast 키 또는 narrator
    text: str                    # 읽을 글(정리한 것)
    node: dict = field(repr=False)
    previous_text: str = ""
    next_text: str = ""

    @property
    def path(self) -> str:
        return f"{AUDIO_DIR}/{self.audio_id}.mp3"


def protagonist(lesson: dict) -> str:
    cast = lesson.get("cast") or {}
    if isinstance(cast, dict) and cast:
        return next(iter(cast))
    if isinstance(cast, list) and cast and isinstance(cast[0], dict):
        return str(cast[0].get("id") or "main")
    return "main"


def speakable(text: str) -> str:
    """화면 글을 읽을 글로. 원문 문구는 바꾸지 않고 **기호만** 걷어낸다."""
    text = str(text or "")
    text = re.sub(r"\*\*|__|`", "", text)          # 강조 표시
    text = re.sub(r"(?m)^\s*[•·\-]\s*", "", text)   # 줄머리 글머리표
    text = text.replace(" / ", "\n")               # 한 말풍선 안의 줄 나눔 표기
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def safe_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-") or "line"


def collect(lesson: dict) -> tuple[list[Line], list[str]]:
    """재생 순서대로 글을 모은다. 두 번째 값은 **모으지 못한 것**(재생 통로 없음·충돌)."""
    main = protagonist(lesson)
    lines: list[Line] = []
    skipped: list[str] = []
    used: set[str] = set()
    counter = {"n": 0}

    def new_id(raw: str | None, kind: str) -> str:
        counter["n"] += 1
        base = ID_PREFIX + safe_id(raw or f"{kind}-{counter['n']:03d}")
        audio_id, n = base, 2
        while audio_id in used:
            audio_id, n = f"{base}-{n}", n + 1
        used.add(audio_id)
        return audio_id

    def own_sound(value: object) -> bool:
        # 비어 있거나 우리가 붙인 것만 덮는다. 배포 차시가 쓰던 효과음 id(sparkle 등)는 건드리지 않는다.
        return not value or (isinstance(value, str) and (value.startswith(ID_PREFIX) or value.startswith("voice-")))

    def visit_cut(cut: dict, where: str) -> None:
        speech = cut.get("speechText")
        if not speech:
            if cut.get("captionText"):
                skipped.append(f"{cut.get('id') or where}: 자막만 있는 컷 — 런타임이 소리를 재생하지 않는다")
            return
        if not own_sound(cut.get("sound")):
            skipped.append(f"{cut.get('id') or where}: 이미 다른 소리({cut.get('sound')})가 걸려 있다")
            return
        lines.append(Line(new_id(cut.get("id"), "cut"), "cut", str(cut.get("characterRef") or main),
                          speakable(speech), cut))

    def visit_problem(problem: dict, where: str) -> None:
        text = problem.get("semiDialogue") or problem.get("prompt")
        narration = problem.get("narration")
        if text and (narration is None or (isinstance(narration, str) and own_sound(narration))):
            pid = problem.get("id")
            lines.append(Line(new_id(f"{pid}-prompt" if pid else None, "problem"), "problem",
                              str(problem.get("characterRef") or main), speakable(text), problem))
        hint = problem.get("hintAfterWrong")
        if isinstance(hint, dict) and hint.get("speechText") and own_sound(hint.get("sound")):
            pid = problem.get("id")
            lines.append(Line(new_id(f"{pid}-hint" if pid else None, "hint"), "hint",
                              str(hint.get("characterRef") or main), speakable(hint["speechText"]), hint))

    def visit_slides(scene: dict) -> None:
        for slide in scene.get("slides") or []:
            if not isinstance(slide, dict):
                continue
            text = "\n".join(part for part in (slide.get("title"), slide.get("caption")) if part)
            if not text:
                continue
            narration = slide.get("narration")
            current = narration.get("audio") if isinstance(narration, dict) else narration
            if not own_sound(current):
                skipped.append(f"{slide.get('id')}: 이미 다른 소리가 걸려 있다")
                continue
            lines.append(Line(new_id(slide.get("id"), "slide"), "slide", NARRATOR, speakable(text), slide))

    def walk(node: object, where: str) -> None:
        if isinstance(node, dict):
            if node.get("type") == "realLifeSlide":
                visit_slides(node)
            for key in ("stageDirections", "introDialogue"):
                for i, cut in enumerate(node.get(key) or []):
                    if isinstance(cut, dict):
                        visit_cut(cut, f"{where}.{key}[{i}]")
            for i, problem in enumerate(node.get("problems") or []):
                if isinstance(problem, dict):
                    visit_problem(problem, f"{where}.problems[{i}]")
            for key, value in node.items():
                if key not in ("stageDirections", "introDialogue", "problems", "slides"):
                    walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{where}[{i}]")

    walk(lesson.get("steps") or [], "steps")

    # 앞뒤 대사를 붙인다 — 같은 화자끼리가 아니라 **들리는 순서**의 앞뒤다(대화의 톤이 이어진다).
    for i, line in enumerate(lines):
        line.previous_text = lines[i - 1].text if i else ""
        line.next_text = lines[i + 1].text if i + 1 < len(lines) else ""
    return lines, skipped


def apply(lesson: dict, lines: list[Line]) -> None:
    """만든 음성을 `lesson.json` 에 건다. 파일이 실제로 있는 줄만 넘긴다."""
    audio_map = lesson.setdefault("audioMap", {})
    narration_map = audio_map.setdefault("narration", {})
    for line in lines:
        narration_map[line.audio_id] = line.path
        if line.kind in ("cut", "hint"):
            line.node["sound"] = line.audio_id
        elif line.kind == "problem":
            line.node["narration"] = line.audio_id
        elif line.kind == "slide":
            narration = line.node.get("narration")
            if isinstance(narration, dict):
                narration["audio"] = line.audio_id
            else:
                line.node["narration"] = {"audio": line.audio_id}
