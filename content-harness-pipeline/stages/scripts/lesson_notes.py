"""사람이 화면을 보고 적는 **차시별 수정 메모** — 저장·순서와 차시 목록.

왜 필요한가 — 초안 파이프라인과 화면 검증(`verify_lesson.py`)이 못 잡는 것이 사람 눈에 계속 걸린다
(화풍·글꼴·배치 취향 등). 그동안은 대화에 그때그때 말했고, 기록이 흩어져 AI 가 다시 볼 곳이 없었다.

차시 작업대(`lesson_desk.py`)는 **gyo6 차시 폴더를 직접** 고친다(2026-09-30 사용자 결정 — run 이 없는
차시가 대부분이고, 사람도 gyo6 에서 직접 고친다). 메모는 gyo6 가 아니라 이 레포에 둔다 —
`desk/{학기-차시}/notes.json`. gyo6 는 공유 레포이고 `npm run deploy` 가 더티 트리를 막는다.

    status   queued    대기 — 적으면 바로 여기 들어간다. 작업대가 **위에서부터** 차례로 AI 에게 맡긴다
             working   처리 중 — AI 작업이 이 메모를 들고 있다
             review    확인 대기 — AI 가 끝냈다(고침·그림 구움·검증 통과). **사람이 화면을 보고** 닫거나 다시 맡긴다
             open      열림 — AI 가 못 했다(확인 필요·못 고침 …). 이유가 log 에 있다. **저절로 다시 돌지 않는다**
             done      완료

AI 가 "고쳤다" 고 끝내도 바로 done 으로 두지 않는다. 화면을 본 것은 사람뿐이다.
열림을 저절로 다시 돌리지 않는 이유 — 같은 이유로 또 못 하고 AI 비용만 계속 든다. 사람이 고쳐 적거나 다시 맡긴다.

    kind     code      코드 — 클로드가 lesson.json · player-ext.* 를 고친다
             image     그림 — 코덱스가 그림 파일을 다시 굽는다
             verify    검증 — 코덱스가 빌드된 화면을 열어 확인만 한다(파일을 안 바꾼다)

종류는 사람이 적을 때 고른다(2026-09-30 사용자 결정). AI 가 나누게 하면 클로드를 한 번 더 부른다(호출마다 고정비).

**순서** — notes 배열 순서가 곧 처리 순서다. 새 메모는 맨 뒤나 "어느 메모 앞"에 넣고, 대기 중인 메모는 옮길 수 있다.
작업대는 **같은 종류 연속 묶음**을 한 작업으로 가져간다 — 작업이 끝날 때마다 순서를 다시 읽으므로 도는 중에 끼워
넣거나 옮겨도 반영된다. 같은 종류를 묶는 것은 AI 호출(고정비)을 줄이려는 것이다. 코드(클로드)와 그림·검증(코덱스)은
두 줄로 함께 돈다 — 무엇을 지금 시작할 수 있는지는 `runnable_groups` 가 정한다(2026-10-01).

번호(U01 …)는 지워도 다시 쓰지 않는다 — 작업 기록·사용량이 번호로 메모를 가리킨다.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
NOTES_NAME = "notes.json"
STATUSES = ("queued", "working", "review", "open", "done")
KINDS = ("code", "image", "verify")


def now() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _read(desk_dir: Path) -> dict:
    path = desk_dir / NOTES_NAME
    if not path.exists():
        return {"notes": [], "last_id": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"notes": [], "last_id": 0}
    return data if isinstance(data, dict) else {"notes": [], "last_id": 0}


def load(desk_dir: Path) -> list[dict]:
    return _read(desk_dir).get("notes", [])


def _number(note_id: str) -> int:
    return int(note_id[1:]) if note_id.startswith("U") and note_id[1:].isdigit() else 0


def save(desk_dir: Path, notes: list[dict]) -> None:
    desk_dir.mkdir(parents=True, exist_ok=True)
    last = max([_read(desk_dir).get("last_id", 0)] + [_number(str(n.get("id", ""))) for n in notes])
    body = json.dumps({"notes": notes, "last_id": last}, ensure_ascii=False, indent=2) + "\n"
    tmp = desk_dir / (NOTES_NAME + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(desk_dir / NOTES_NAME)


def next_id(desk_dir: Path, notes: list[dict]) -> str:
    last = max([_read(desk_dir).get("last_id", 0)] + [_number(str(n.get("id", ""))) for n in notes])
    return f"U{last + 1:02d}"


def kind_of(note: dict) -> str:
    return note.get("kind") if note.get("kind") in KINDS else "code"


def _index(notes: list[dict], note_id: str | None) -> int | None:
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            return i
    return None


def add(desk_dir: Path, text: str, kind: str = "code", before: str | None = None) -> dict:
    """대기열에 넣는다. before 가 있으면 그 메모 바로 앞, 없으면 맨 뒤."""
    text = text.strip()
    if not text:
        raise ValueError("빈 메모")
    if kind not in KINDS:
        raise ValueError(f"알 수 없는 종류: {kind}")
    notes = load(desk_dir)
    note = {"id": next_id(desk_dir, notes), "kind": kind, "text": text, "status": "queued", "created_at": now(),
            "updated_at": now(), "log": []}
    at = _index(notes, before) if before else None
    notes.insert(len(notes) if at is None else at, note)
    save(desk_dir, notes)
    return note


def move(desk_dir: Path, note_id: str, before: str | None) -> list[dict]:
    """대기 중인 메모를 옮긴다. before 메모 바로 앞으로, 없으면 맨 뒤로."""
    notes = load(desk_dir)
    at = _index(notes, note_id)
    if at is None:
        raise ValueError(f"없는 메모: {note_id}")
    if notes[at]["status"] != "queued":
        raise ValueError("대기 중인 메모만 옮길 수 있다")
    if before == note_id:
        return notes
    note = notes.pop(at)
    target = _index(notes, before) if before else None
    notes.insert(len(notes) if target is None else target, note)
    save(desk_dir, notes)
    return notes


def set_status(desk_dir: Path, ids: list[str], status: str, message: str = "") -> list[dict]:
    if status not in STATUSES:
        raise ValueError(f"알 수 없는 상태: {status}")
    notes = load(desk_dir)
    for note in notes:
        if note["id"] in ids:
            note["status"] = status
            note["updated_at"] = now()
            if status in ("queued", "working"):
                note.pop("result", None)  # 다시 맡기면 지난 결과는 새 결과로 바뀐다 — 그사이 옛 결과를 보이지 않는다
            if message:
                note.setdefault("log", []).append(f"{now()} {message}")
    save(desk_dir, notes)
    return notes


def set_result(desk_dir: Path, note_id: str, status: str, result: dict, message: str = "") -> None:
    """AI 결과를 메모에 **구조로** 붙인다 — {kind, label, step, headline, detail, at, job}.

    작업대 카드는 headline 한 줄만 보이고 detail 은 접어 둔다(2026-09-30 사용자 요청 — 긴 결과 문장이 카드를 덮었다).
    """
    notes = load(desk_dir)
    for note in notes:
        if note["id"] == note_id:
            note["result"] = {**result, "at": now()}
    save(desk_dir, notes)
    set_status(desk_dir, [note_id], status, message)


def set_kind(desk_dir: Path, note_id: str, kind: str) -> dict:
    """종류를 잘못 골랐을 때 고친다(2026-10-01 사용자 요청 — 그림으로 맡길 것을 코드로 적었다).

    대기 중이면 종류만 바꾼다(자리는 그대로). 이미 처리된 메모(확인 대기·열림·완료)면 종류를 바꾸고 **다시 대기열에**
    넣는다 — 다른 AI 가 처리해야 하는 일이므로. 처리 중인 메모는 AI 가 들고 있어서 못 바꾼다(먼저 멈춘다).
    """
    if kind not in KINDS:
        raise ValueError(f"알 수 없는 종류: {kind}")
    notes = load(desk_dir)
    at = _index(notes, note_id)
    if at is None:
        raise ValueError(f"없는 메모: {note_id}")
    note = notes[at]
    if note["status"] == "working":
        raise ValueError("처리 중인 메모는 종류를 바꿀 수 없다 — 먼저 멈춘다")
    old = kind_of(note)
    if old == kind:
        return note
    note["kind"] = kind
    save(desk_dir, notes)
    names = {"code": "코드", "image": "그림", "verify": "검증"}
    message = f"종류를 {names[old]} → {names[kind]} 로 바꿈"
    if note["status"] == "queued":
        set_status(desk_dir, [note_id], "queued", message)
    else:
        set_status(desk_dir, [note_id], "queued", message + " — 다시 맡김")
    return note


def remove(desk_dir: Path, note_id: str) -> list[dict]:
    notes = load(desk_dir)
    if any(n["id"] == note_id and n["status"] == "working" for n in notes):
        raise ValueError("처리 중인 메모는 지울 수 없다 — 먼저 멈춘다")
    notes = [n for n in notes if n["id"] != note_id]
    save(desk_dir, notes)
    return notes


def release_working(desk_dir: Path, message: str, to: str = "open", ids: list[str] | None = None) -> None:
    """작업이 끊겼을 때 — 들고 있던 메모를 되돌린다(멈춤이면 대기로, 실패면 열림으로).

    ids 를 주면 그 메모만 — 두 줄(클로드 · 코덱스)이 함께 돌 때 끊긴 작업의 메모만 되돌린다.
    """
    held = [n["id"] for n in load(desk_dir) if n["status"] == "working" and (ids is None or n["id"] in ids)]
    if held:
        set_status(desk_dir, held, to, message)


# 작업 줄 — 코드는 클로드, 그림·검증은 코덱스(2026-09-30 사용자 결정). 줄마다 한 번에 한 작업씩, 두 줄은 함께 돈다.
LANE = {"code": "claude", "image": "codex", "verify": "codex"}


def runnable_groups(notes: list[dict], busy: set[str] | frozenset[str] = frozenset()) -> list[tuple[str, list[dict]]]:
    """지금 시작할 수 있는 묶음 [(줄, 메모들)]. busy 는 작업이 도는 줄.

    사용자 요청(2026-10-01) — 코드(클로드)와 그림(코덱스)은 서로 기다리지 않는다. 바꾸는 파일이 겹치지 않는다
    (코드는 세 파일, 그림은 그림 파일). 새 그림을 화면에 붙이는 코드 메모(`follow_up`)는 그림이 **끝난 뒤에** 생기므로
    기다릴 일이 없다. 처음에 "코드는 위의 그림을 기다린다" 를 넣었다가 상관없는 코드 메모까지 묶여 뺐다
    (problem.md [desk-parallel-overblocked]).
    - 검증만 칸막이다 — 앞에 걸린 것이 없고 두 줄이 다 쉴 때만 돌고, 뒤의 것은 검증이 끝날 때까지 기다린다.
      검증은 빌드 뒤 화면을 보고, 코드 파일이 바뀌면 해시 가드가 되돌린다 — 코드와 함께 돌면 코드가 고친 것이 지워진다.
    묶음은 걸린 메모 가운데 그 메모부터 **이어지는 같은 종류 대기 메모**다(처리 중 메모나 다른 종류에서 끊는다).
    """
    busy = set(busy)
    pending = [n for n in notes if n.get("status") in ("queued", "working")]
    out: list[tuple[str, list[dict]]] = []
    before: list[str] = []   # 앞에 걸린 메모들의 종류
    for i, note in enumerate(pending):
        kind = kind_of(note)
        lane = LANE[kind]
        if note["status"] == "queued" and lane not in busy:
            if kind == "verify":
                ok = not before and not busy
            else:
                ok = "verify" not in before
            if ok:
                group = [note]
                for later in pending[i + 1:]:
                    if later["status"] != "queued" or kind_of(later) != kind:
                        break
                    group.append(later)
                out.append((lane, group))
                busy.add(lane)
        before.append(kind)
    return out


def next_group(notes: list[dict]) -> list[dict]:
    """대기열 맨 앞 메모와, 대기열에서 그 뒤로 **이어지는 같은 종류** 메모들."""
    queued = [n for n in notes if n.get("status") == "queued"]
    if not queued:
        return []
    kind = kind_of(queued[0])
    group = []
    for note in queued:
        if kind_of(note) != kind:
            break
        group.append(note)
    return group


def desk_id(lesson_ref: str) -> str:
    return lesson_ref.replace("/", "-")


def gyo6_lessons(gyo6_root: Path, semesters: list[str]) -> list[str]:
    """gyo6 `lessons/{학기}/{차시}/lesson.json` 이 있는 차시. 학기 순서는 받은 대로, 차시는 번호 순."""
    rows = []
    for semester in semesters:
        folder = gyo6_root / "lessons" / semester
        if not folder.is_dir():
            continue
        for lesson in sorted(p for p in folder.iterdir() if p.is_dir() and (p / "lesson.json").exists()):
            rows.append(f"{semester}/{lesson.name}")
    return rows
