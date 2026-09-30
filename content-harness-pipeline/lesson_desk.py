"""차시 작업대 — 사람이 화면을 보고 적은 메모를 AI 가 차례로 처리하고, 빌드·멈춤을 버튼으로 한다.

    python -B ./lesson_desk.py --gyo6-root <gyo6_content>      # http://127.0.0.1:8790
    python -B ./lesson_desk.py                                  # 두 번째부터는 desk/config.json 의 값을 쓴다
    python -B ./lesson_desk.py --semesters 3-1,3-2,4-1,4-2 --port 8800

**gyo6 차시 폴더를 직접** 고친다(2026-09-30 사용자 결정). 목록은 gyo6 `lessons/{학기}/*/lesson.json` 이다.
차시마다 카드 하나.

    적기        메모를 종류와 함께 대기열에 넣는다(맨 뒤, 또는 고른 메모 앞). **넣으면 바로 처리가 시작된다**
                → desk/{학기-차시}/notes.json (`stages/scripts/lesson_notes.py`)
    대기열      위에서부터 차례로 처리한다. 한 번에 맨 앞의 **같은 종류 연속 묶음**을 한 작업으로 맡긴다
                  코드  클로드가 lesson.json · player-ext.* 를 고친다        (`desk_fix.py`)
                  그림  코덱스가 assets 의 그림을 다시 굽는다                (`desk_image.py`)
                  검증  빌드한 뒤 코덱스가 화면을 열어 확인만 한다           (`desk_verify.py`)
                작업이 끝날 때마다 대기열을 다시 읽으므로, 도는 중에 끼워 넣거나 순서를 바꿔도 반영된다
    자동 빌드   대기열이 비면 한 번 [빌드]를 돈다 — 이번 대기열에서 코드·그림 작업이 끝났을 때만(사용자 요청 2026-09-30).
                작업마다 빌드하지 않는다(빌드 + 검사가 4분쯤 걸려 대기열이 밀린다). 멈춤으로 세웠으면 하지 않는다
    끝나면 멈춤 도는 작업은 끝까지 마치게 두고, 다음 메모로 넘어가지 않고 멈춘다. 바뀐 것이 있으면 바로 빌드한다
                (2026-09-30 사용자 요청 — [멈춤]은 끊고 되돌려 그 작업의 AI 비용을 버린다. 중간 결과만 보려면 이쪽)
    멈춤        지금 작업의 프로세스 트리를 끊고 그 작업이 바꾼 것을 되돌린다. 대기열은 멈춘 채로 둔다
    다시 시작   멈춘 대기열을 이어서 처리한다
    빌드        gyo6 build:lesson → 화면 결함 검사(check_rendered) → 기능 테스트(run_functional_tests). AI 없음
                **KB 서버로 보내지 않는다** — 서버 배포는 지금처럼 gyo6 에서 `npm run deploy`
    화면 보기   빌드된 차시를 이 서버가 http 로 연다(file:// 은 글꼴을 막아 화면이 다르게 보인다)
    작업 경로   AI 가 고칠 차시 폴더. 기본은 gyo6 lessons/{차시}. 카드에서 바꾸고 되돌릴 수 있다
                → desk/{학기-차시}/lesson-config.json. 빌드·화면 보기는 그 폴더가 속한 gyo6 체크아웃
                (`<root>/lessons/<학기>/<차시>`)에서 한다. 그 모양이 아니면 코드·그림 메모만 된다
    사용량      AI 작업마다 토큰·비용·시간. 차시마다 최근 10개만 남기고 오래된 것은 지운다(usage-log.jsonl)
    AI 모델     사이드바 아래에서 클로드 · 코덱스 모델을 고른다(두 화면 공용, desk/config.json). 다음 작업부터 적용
                  클로드 — 코드 메모 · 초안의 클로드 단계      코덱스 — 그림·검증 메모 · 초안의 그림 굽기
                코덱스 목록은 코덱스 CLI 가 받아 둔 ~/.codex/models_cache.json 에서 읽는다(지어내지 않는다)
    알림        Windows 바탕화면 알림(사용자 요청 2026-09-30). 브라우저를 닫아도 서버가 켜져 있으면 뜬다
                  실패하면 바로 — 어느 차시의 무슨 작업이 왜(`stages/scripts/desk_failures.py`)
                  대기열이 끝나면 — 자동 빌드까지 끝난 뒤 한 번: 고침 · 못 한 것 · 실패 수와 빌드 결과
                `--no-notify` 로 끈다

/pipeline 은 **초안 파이프라인 대시보드**다. runs/*/pipeline-log.jsonl 과 usage-log.jsonl 로
지금 어느 단계를 돌고 있는지와 단계별 토큰을 보여 준다(`stages/scripts/pipeline_status.py`).
거기서 초안을 만들고 이어 간다(2026-09-30 사용자 요청):

    새 초안        스토리보드 PDF 를 올리고 [초안 만들기] → produce_lesson.py … --through interview --no-voice
                   (올린 PDF 는 desk/uploads/{run}.pdf, 넣을 차시 등은 runs/{run}/desk-draft.json)
    답 대기        인터뷰 질문 · 요구 명세의 정할 것 — 화면의 답 칸에 적고 [답 저장하고 이어서 만들기]
                   (`stages/scripts/interview_form.py` 가 questions.md 로 돌려놓는다)
                   → produce_lesson.py runs/{run} --start-at interview_brief --interview-notes …/questions.md --no-voice
    gyo6에 넣기    버튼으로만 — install_lesson → build:lesson(빌드 줄 세우기) → verify_lesson --skip-llm
                   같은 차시가 이미 있으면 사람이 [덮어쓰기]를 눌러야 --overwrite 로 넣는다(gyo6 쪽 수정은 그래도 막힌다)
    음성 단계는 건너뛴다(--no-voice, 사용자 결정 — 가져오기가 아직 없다)

지키는 것
- 127.0.0.1 에만 붙는다. POST 는 `X-Desk` 헤더가 있어야 받는다(다른 사이트가 몰래 누르지 못하게).
- 명령은 목록에 있는 차시로만 만든다. 요청 값으로 경로를 짓지 않는다.
- 차시 하나에 작업은 하나만 돈다(대기열 처리기 하나 · 빌드와 동시에 안 돈다). 차시끼리는 병렬로 돈다.
- **빌드 명령(build:lesson)은 gyo6 체크아웃마다 한 번에 하나만** 돈다(2026-09-30 사용자 결정). 차시별 빌드라도
  gyo6 의 `postbuild:lesson` → `tools/clean-tmp.mjs` 가 레포 전체의 `*.tmp*` 를 지워서, 동시에 돌던 다른 차시 빌드의
  임시 파일(음성 `이름.tmp.mp3` · webp 캐시 `….<pid>.tmp`, `agent/distBuilder.mjs`)을 지울 수 있다. 뒤 차시는 "빌드 대기".
  빌드 뒤의 화면 결함 검사·기능 테스트는 읽기만 하므로 줄 세우지 않는다. 작업대 밖에서 사람이 직접 하는 빌드는 못 막는다.
- AI 작업은 시작 전에 그 작업이 바꿀 수 있는 파일을 desk/{id}/backup/{작업 번호}/ 에 복사한다. 실패·멈춤이면 되돌린다.
  작업대가 작업 중에 꺼졌으면 다음에 켤 때 되돌리고 대기열을 멈춰 둔다(켜자마자 AI 비용이 나가지 않게).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import queue
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import (  # noqa: E402
    desk_failures, interview_form, lesson_notes, notify, pipeline_status, run_artifacts, usage_log,
)

_THUMBS: dict[tuple[str, float, int], bytes] = {}


EDITOR_SUFFIXES = {".md", ".json", ".css", ".js", ".txt", ".jsonl", ".log"}


def open_in_editor(run_id: str, rel: str) -> dict:
    """산출물 글 파일을 VS Code 로 연다(2026-09-30 사용자 요청). 이 PC 에서 서버가 `code` 를 부른다.

    run 폴더 안의 글 파일만 연다(`run_artifacts.safe_path`). VS Code 가 없으면 이유를 돌려준다 — 화면은 [보기]로 대신한다.
    """
    if run_id not in {p.name for p in RUNS_DIR.iterdir() if p.is_dir()}:
        raise ValueError("없는 run")
    path = run_artifacts.safe_path(RUNS_DIR / run_id, rel)
    if path is None or path.suffix.lower() not in EDITOR_SUFFIXES:
        raise ValueError("VS Code 로 열 수 있는 글 파일이 아니다")
    code = shutil.which("code.cmd") or shutil.which("code")
    if not code:
        raise ValueError("VS Code 명령(code)을 찾지 못했다 — VS Code 에서 'Shell Command: Install code command in PATH' 를 켜거나 [보기]를 쓴다")
    subprocess.Popen([code, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
    return {"ok": True, "opened": str(path)}


def thumbnail(path: Path, size: int = 320) -> bytes:
    """산출물 그림의 작은 사본(JPEG). 원본이 장당 2~3MB 라 그대로 늘어놓으면 화면이 느리다. 수정 시각으로 캐시한다."""
    import io
    from PIL import Image

    key = (str(path), path.stat().st_mtime, size)
    if key not in _THUMBS:
        with Image.open(path) as image:
            image = image.convert("RGBA")
            image.thumbnail((size, size))
            flat = Image.new("RGB", image.size, (238, 241, 246))   # 투명 그림은 옅은 회색 위에
            flat.paste(image, mask=image.getchannel("A"))
            buffer = io.BytesIO()
            flat.save(buffer, "JPEG", quality=82)
        if len(_THUMBS) > 800:
            _THUMBS.clear()
        _THUMBS[key] = buffer.getvalue()
    return _THUMBS[key]
from stages.scripts.lesson_notes import KST  # noqa: E402

DESK_DIR = PROJECT_DIR / "desk"
CONFIG = DESK_DIR / "config.json"
PAGE = PROJECT_DIR / "tools" / "lesson_desk.html"
PIPELINE_PAGE = PROJECT_DIR / "tools" / "pipeline_dashboard.html"
RUNS_DIR = PROJECT_DIR / "runs"
BUNDLE = ("lesson.json", "player-ext.js", "player-ext.css")
ACTIVE_GLOB = "active-job*.json"   # 줄마다 active-job-{claude|codex}.json · 옛 active-job.json 도 켤 때 되돌린다
LESSON_CONFIG = "lesson-config.json"
JOBS_NAME = "jobs.jsonl"
USAGE_KEEP = 10
IS_WINDOWS = os.name == "nt"
NPM = "npm.cmd" if IS_WINDOWS else "npm"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
# 메모 종류 → (단계 이름, 스크립트, 결과 파일, 맡는 AI)
AI_KIND = {
    "code": ("코드 고치기", "desk_fix.py", "last-fix.json", "클로드"),
    "image": ("그림 굽기", "desk_image.py", "last-image.json", "코덱스"),
    "verify": ("검증", "desk_verify.py", "last-verify.json", "코덱스"),
}
RESULT_LABEL = {"fixed": "고침", "rendered": "그림 새로 구움", "passed": "검증 통과", "needs_image": "그림 필요",
                "needs_confirm": "확인 필요", "not_fixed": "못 고침", "not_done": "못 그림", "failed": "검증 실패",
                "unclear": "확인 못 함", "created": "새 그림 만듦", "partial": "일부만 함"}
# 확인 대기로 보내는 결과 — 파일이 실제로 바뀐 것. partial 도 넣는다: 한 것은 화면에 반영(자동 빌드)해야 하고,
# 남은 것은 detail 에 적혀 있다(2026-09-30 4-1/04 — 로고를 다시 그리고도 '확인 필요' 로 적어 빌드가 안 돌았다)
DONE_RESULTS = {"fixed", "rendered", "passed", "created", "partial"}
CHECK_STEPS = ("화면 결함 검사", "기능 테스트")  # 0 통과 · 1 걸림 · 2 실행 실패 — 걸린 것은 작업 실패가 아니다
NOT_BUILDABLE = "작업 경로가 gyo6 체크아웃의 lessons/<학기>/<차시> 가 아니라 빌드할 수 없다"

KIND_LABEL = {"ai": "AI 맡기기", "build": "빌드", "draft": "초안", "install": "gyo6에 넣기"}
UPLOADS_DIR = DESK_DIR / "uploads"
DRAFT_META = "desk-draft.json"
DRAFT_JOBS_DIR = "desk-jobs"
RUN_ID_RE = __import__("re").compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,39}$")
SLOT_RE = __import__("re").compile(r"^\d-\d/\d{2}$")
# 이 종료 코드는 실패가 아니다 — 초안: 3 = 사람이 답할 차례 · 화면 검증: 2 = 막는 지적 있음(보고서로 본다)
SOFT_EXIT = {"초안 만들기": {3}, "이어서 만들기": {3}, "화면 검증": {2}}

SETTINGS = {"gyo6_root": Path(), "semesters": ["3-1", "3-2", "4-1", "4-2"], "port": 8790, "notify": True,
            "claude_model": "", "codex_model": "", "claude_effort": "", "codex_effort": ""}   # 빈 값 = CLI 기본
# 클로드 CLI 는 별칭(opus · sonnet · fable …)이나 전체 모델 이름을 받는다(`claude --help`). 목록에 없으면 직접 적는다
MODEL_RE = __import__("re").compile(r"^[A-Za-z0-9._:\[\]-]{1,60}$")
EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
EFFORT_LABEL = {"low": "Low", "medium": "Medium", "high": "High", "xhigh": "Extra high", "max": "Max", "ultra": "Ultra"}


def claude_models() -> list[dict]:
    """Claude Code 가 받아 둔 모델 목록(~/.claude/cache/model-catalog/*-cc.json) — 이름 · 추론 강도 · 추천값.

    지어내지 않는다(2026-09-30 — 처음에는 opus·sonnet 별칭만 넣어서 Opus 4.8 · 4.6 같은 버전을 못 골랐다).
    못 읽으면 별칭 몇 개로 대신한다(CLI 가 별칭을 받는다 — `claude --help`).
    """
    folder = Path.home() / ".claude" / "cache" / "model-catalog"
    for path in sorted(folder.glob("*-cc.json"), key=lambda p: p.stat().st_mtime, reverse=True) if folder.is_dir() else []:
        try:
            models = json.loads(path.read_text(encoding="utf-8"))["catalog"]["config"]["models"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            continue
        out = []
        for m in models:
            thinking = m.get("thinking") or {}
            options = thinking.get("effort_options") or []
            out.append({"id": m["id"], "name": m.get("name") or m["id"], "main": m.get("section") == "main",
                        "efforts": [o["id"] for o in options],
                        "recommended": next((o["id"] for o in options if (o.get("badge") or {}).get("message") == "Recommended"), "")})
        if out:
            return out
    return [{"id": a, "name": n, "main": True, "efforts": ["low", "medium", "high", "xhigh", "max"], "recommended": ""}
            for a, n in (("opus", "Opus"), ("sonnet", "Sonnet"), ("fable", "Fable"), ("haiku", "Haiku"))]


def codex_models() -> tuple[list[dict], str, str]:
    """코덱스 CLI 가 받아 둔 모델 목록(~/.codex/models_cache.json, 보이는 것만, 추천 순)과 CLI 기본 모델 · 기본 강도."""
    home = Path.home() / ".codex"
    out: list[dict] = []
    try:
        models = json.loads((home / "models_cache.json").read_text(encoding="utf-8")).get("models", [])
        for m in sorted((m for m in models if m.get("visibility") == "list"), key=lambda m: m.get("priority", 99)):
            if m.get("slug"):
                out.append({"id": m["slug"], "name": m.get("display_name") or m["slug"], "main": True,
                            "efforts": [lv["effort"] for lv in m.get("supported_reasoning_levels") or []],
                            "recommended": m.get("default_reasoning_level") or ""})
    except (OSError, json.JSONDecodeError, AttributeError, KeyError):
        pass
    default_model = default_effort = ""
    try:
        for line in (home / "config.toml").read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "model" and not default_model:
                default_model = value.strip().strip('"')
            if key.strip() == "model_reasoning_effort" and not default_effort:
                default_effort = value.strip().strip('"')
    except OSError:
        pass
    return out, default_model, default_effort


def model_state() -> dict:
    codex, codex_default, codex_default_effort = codex_models()
    return {"claude": SETTINGS["claude_model"], "claude_effort": SETTINGS["claude_effort"],
            "codex": SETTINGS["codex_model"], "codex_effort": SETTINGS["codex_effort"],
            "claude_models": claude_models(), "codex_models": codex,
            "codex_default": codex_default, "codex_default_effort": codex_default_effort, "effort_label": EFFORT_LABEL}


def set_models(claude: str, codex: str, claude_effort: str = "", codex_effort: str = "") -> None:
    for value in (claude, codex):
        if value and not MODEL_RE.match(value):
            raise ValueError(f"모델 이름에 쓸 수 없는 글자가 있다: {value}")
    for value in (claude_effort, codex_effort):
        if value and value not in EFFORTS:
            raise ValueError(f"모르는 추론 강도: {value}")
    SETTINGS["claude_model"], SETTINGS["codex_model"] = claude, codex
    SETTINGS["claude_effort"], SETTINGS["codex_effort"] = claude_effort, codex_effort
    save_settings()


def model_args(kind: str) -> list[str]:
    """AI 스크립트에 붙일 모델 · 추론 강도. 코드 = 클로드, 그림·검증 = 코덱스."""
    model = SETTINGS["claude_model"] if kind == "code" else SETTINGS["codex_model"]
    effort = SETTINGS["claude_effort"] if kind == "code" else SETTINGS["codex_effort"]
    return (["--model", model] if model else []) + (["--effort", effort] if effort else [])


def pipeline_model_args() -> list[str]:
    out = []
    for key, flag in (("claude_model", "--claude-model"), ("codex_model", "--codex-model"),
                      ("claude_effort", "--claude-effort"), ("codex_effort", "--codex-effort")):
        if SETTINGS[key]:
            out += [flag, SETTINGS[key]]
    return out


def gyo6() -> Path:
    return SETTINGS["gyo6_root"]


def desk_dir(lesson_ref: str) -> Path:
    return DESK_DIR / lesson_notes.desk_id(lesson_ref)


# ── 차시 설정: 작업 경로 · 멈춤 ─────────────────────────────────────────────

def default_dir(lesson_ref: str) -> Path:
    return gyo6() / "lessons" / lesson_ref


def lesson_config(lesson_ref: str) -> dict:
    path = desk_dir(lesson_ref) / LESSON_CONFIG
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {}


def save_config(lesson_ref: str, config: dict) -> None:
    desk_dir(lesson_ref).mkdir(parents=True, exist_ok=True)
    (desk_dir(lesson_ref) / LESSON_CONFIG).write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                                                      encoding="utf-8")


def lesson_dir(lesson_ref: str) -> Path:
    """AI 가 고칠 차시 폴더 — 사람이 지정했으면 그곳, 아니면 gyo6 lessons/{차시}."""
    custom = lesson_config(lesson_ref).get("lesson_dir")
    return Path(custom) if custom else default_dir(lesson_ref)


def set_lesson_dir(lesson_ref: str, raw: str) -> None:
    """빈 값이면 기본으로 되돌린다. 폴더에 lesson.json 이 있어야 받는다."""
    config = lesson_config(lesson_ref)
    raw = raw.strip().strip('"')
    if not raw:
        config.pop("lesson_dir", None)
    else:
        path = Path(raw).expanduser().resolve()
        if not (path / "lesson.json").is_file():
            raise ValueError(f"lesson.json 이 없는 폴더다: {path}")
        if path == default_dir(lesson_ref).resolve():
            config.pop("lesson_dir", None)
        else:
            config["lesson_dir"] = str(path)
    save_config(lesson_ref, config)


def is_paused(lesson_ref: str) -> bool:
    return bool(lesson_config(lesson_ref).get("paused"))


def set_paused(lesson_ref: str, paused: bool) -> None:
    config = lesson_config(lesson_ref)
    if paused:
        config["paused"] = True
    else:
        config.pop("paused", None)
    config.pop("pause_after", None)   # 멈췄든 다시 시작했든 '끝나면 멈춤' 예약은 끝났다
    save_config(lesson_ref, config)


def pause_after_pending(lesson_ref: str) -> bool:
    return bool(lesson_config(lesson_ref).get("pause_after"))


def set_pause_after(lesson_ref: str, on: bool) -> None:
    config = lesson_config(lesson_ref)
    if on:
        config["pause_after"] = True
    else:
        config.pop("pause_after", None)
    save_config(lesson_ref, config)


def build_target(lesson_ref: str) -> tuple[Path, str] | None:
    """작업 폴더가 `<root>/lessons/<학기>/<차시>` 이고 root 가 gyo6 체크아웃이면 (root, "학기/차시")."""
    folder = lesson_dir(lesson_ref).resolve()
    if len(folder.parents) < 3 or folder.parents[1].name != "lessons":
        return None
    root = folder.parents[2]
    if not (root / "package.json").is_file():
        return None
    return root, f"{folder.parent.name}/{folder.name}"


# ── 작업 ─────────────────────────────────────────────────────────────────────

class Job:
    def __init__(self, lesson_ref: str, kind: str, steps: list[tuple[str, list[str], Path]], stamp: str,
                 note_ids: list[str] | None = None, note_kind: str = "", auto: bool = False,
                 folder: Path | None = None):
        self.lesson = lesson_ref    # 차시("4-1/04") — 초안 작업이면 run 이름
        self.auto = auto            # 대기열이 끝나 저절로 돈 빌드
        self.auto = auto            # 대기열이 끝나 저절로 돈 빌드
        self.kind = kind            # "ai" | "build"
        self.steps = steps
        self.stamp = stamp          # 작업 번호 — 로그·백업·사용량(tag)을 잇는다
        self.note_ids = note_ids or []
        self.note_kind = note_kind
        self.dir = folder or desk_dir(lesson_ref)   # 초안 작업은 runs/{run}/desk-jobs/
        self.started = datetime.now(KST)
        self.log_path = self.dir / "jobs" / f"{stamp}-{kind}.log"
        self.state = "running"
        self.step = ""
        self.summary = ""
        self.results: dict[str, int] = {}
        self.outcomes: dict[str, int] = {}   # AI 작업 — 결과 종류별 메모 수(fixed · needs_confirm …)
        self.proc: subprocess.Popen | None = None
        self.stop_requested = False
        self.ended: datetime | None = None

    def public(self) -> dict:
        return {
            "id": self.stamp,
            "kind": self.kind,
            "note_kind": self.note_kind,
            "note_ids": self.note_ids,
            "auto": self.auto,
            "state": self.state,
            "step": self.step,
            "summary": self.summary,
            "started": self.started.isoformat(timespec="seconds"),
            "ended": self.ended.isoformat(timespec="seconds") if self.ended else "",
            "log": self.log_path.relative_to(PROJECT_DIR).as_posix(),
            "tail": tail(self.log_path),
        }


JOBS: dict[str, Job] = {}          # 차시 → 지금(또는 마지막) 작업 — 마지막에 시작한 것
LANES: dict[str, dict[str, Job]] = {}   # 차시 → {줄("claude"|"codex"): 도는 AI 작업}
BUILD_LOCKS: dict[str, threading.Lock] = {}   # gyo6 체크아웃 → 빌드 자리(한 번에 하나)
BUILD_HOLDER: dict[str, str] = {}             # gyo6 체크아웃 → 지금 빌드 중인 차시
RUNNERS: set[str] = set()          # 대기열 처리기가 도는 차시
WAKE: dict[str, "queue.Queue"] = {}   # 차시 → 처리기가 기다리는 통(끝난 작업 · 깨우기 None)
LOCK = threading.RLock()
_STAMP_LOCK = threading.Lock()
_last_stamp = ""


def new_stamp() -> str:
    """작업 번호. 한 초에 여러 작업이 생겨도 겹치지 않게 뒤에 번호를 붙인다."""
    global _last_stamp
    with _STAMP_LOCK:
        base = datetime.now(KST).strftime("%Y%m%d-%H%M%S")
        stamp, n = base, 1
        while stamp <= _last_stamp:
            stamp = f"{base}-{n}"
            n += 1
        _last_stamp = stamp
        return stamp


def tail(path: Path, lines: int = 40) -> str:
    if not path.exists():
        return ""
    return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])


def write_log(job: Job, message: str) -> None:
    job.log_path.parent.mkdir(parents=True, exist_ok=True)
    with job.log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n[{datetime.now(KST).strftime('%H:%M:%S')}] {message}\n")


def active_marker(lesson_ref: str, lane: str) -> Path:
    """줄마다 따로 두는 '작업 중' 표시 — 두 줄이 함께 돌 때 한쪽을 되돌려도 다른 쪽 표시가 남게."""
    return desk_dir(lesson_ref) / f"active-job-{lane}.json"


def backup_bundle(lesson_ref: str, stamp: str, kind: str) -> Path:
    """이 작업이 바꿀 수 있는 파일만 작업 전 상태로 남기고, 작업 중 표시를 둔다.

    코드·검증은 세 파일, 그림은 그림 파일만. 코드와 그림이 함께 돌므로 그림 작업이 실패해 되돌릴 때
    그사이 코드 작업이 고친 lesson.json 을 옛것으로 덮으면 안 된다 — 그래서 겹치지 않게 나눈다.
    """
    source = lesson_dir(lesson_ref)
    backup = desk_dir(lesson_ref) / "backup" / stamp
    backup.mkdir(parents=True, exist_ok=True)
    if kind == "image":
        files = [p.relative_to(source).as_posix() for p in sorted((source / "assets").rglob("*"))
                 if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES] if (source / "assets").is_dir() else []
    else:
        files = [name for name in BUNDLE if (source / name).exists()]
    for rel in files:
        (backup / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, backup / rel)
    marker = {"lesson": lesson_ref, "dir": str(source), "backup": backup.relative_to(desk_dir(lesson_ref)).as_posix(),
              "files": files, "kind": kind}
    active_marker(lesson_ref, lesson_notes.LANE[kind]).write_text(json.dumps(marker, ensure_ascii=False), encoding="utf-8")
    return backup


def restore_bundle(lesson_ref: str, marker_path: Path) -> list[str]:
    """작업 전으로 되돌린다. 작업 전에 없던 파일을 AI 가 새로 만들었으면 그대로 두고 알린다(지우지 않는다)."""
    if not marker_path.exists():
        return []
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    backup = desk_dir(lesson_ref) / marker["backup"]
    target = Path(marker["dir"]) if marker.get("dir") else lesson_dir(lesson_ref)
    restored = []
    for rel in marker["files"]:
        if (backup / rel).exists() and (not (target / rel).exists()
                                        or (target / rel).read_bytes() != (backup / rel).read_bytes()):
            shutil.copy2(backup / rel, target / rel)
            restored.append(rel)
    known = set(marker["files"])
    extra = [n for n in BUNDLE if n not in known and (target / n).exists()] if marker.get("kind") != "image" else []
    marker_path.unlink()
    return restored + [f"(새로 생긴 {n} 은 남김)" for n in extra]


def kill_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if IS_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.kill()


def wait_build_slot(job: Job, label: str, root: Path) -> bool:
    """이 체크아웃의 빌드 자리를 얻을 때까지 기다린다. 기다리는 중에 멈추면 False."""
    key = str(root.resolve()).lower()
    with LOCK:
        lock = BUILD_LOCKS.setdefault(key, threading.Lock())
    announced = False
    while not lock.acquire(timeout=1):
        if job.stop_requested:
            return False
        holder = BUILD_HOLDER.get(key, "다른 차시")
        job.step = f"빌드 대기 — {holder} 빌드 중"
        if not announced:
            write_log(job, f"… {label} 대기: 같은 gyo6 에서 {holder} 가 빌드 중이다(빌드는 한 번에 하나)")
            announced = True
    BUILD_HOLDER[key] = job.lesson
    if announced:
        write_log(job, f"… {label} 차례가 왔다")
    return True


def release_build_slot(root: Path) -> None:
    key = str(root.resolve()).lower()
    BUILD_HOLDER.pop(key, None)
    BUILD_LOCKS[key].release()


def run_job(job: Job) -> None:
    """작업의 단계를 차례로 돈다. 이 함수를 부른 스레드에서 끝까지 돈다."""
    rc = 0
    try:
        for label, cmd, cwd in job.steps:
            if job.stop_requested:
                break
            is_build = "build:lesson" in cmd
            if is_build and not wait_build_slot(job, label, cwd):
                break
            job.step = label
            write_log(job, f"▶ {label}: {' '.join(cmd)}")
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", DESK_STEP=job.stamp)
            flags = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
            try:
                with job.log_path.open("a", encoding="utf-8") as out:
                    job.proc = subprocess.Popen(cmd, cwd=cwd, stdout=out, stderr=subprocess.STDOUT, env=env,
                                                creationflags=flags)
                    rc = job.proc.wait()
            finally:
                if is_build:
                    release_build_slot(cwd)
            job.results[label] = rc
            write_log(job, f"■ {label} 종료 코드 {rc}")
            if job.stop_requested:
                break
            if rc != 0 and not (label in CHECK_STEPS and rc == 1) and rc not in SOFT_EXIT.get(label, ()):
                break
        finish(job, rc)
    except Exception as exc:  # 작업 스레드가 조용히 죽으면 버튼이 영영 '도는 중'으로 남는다
        write_log(job, f"작업대 오류: {exc!r}")
        finish(job, 1)


def finish(job: Job, rc: int) -> None:
    folder = job.dir
    last_label = job.steps[-1][0]
    if job.stop_requested:
        job.state, job.summary = "stopped", "멈춤"
    elif job.step == last_label and (rc == 0 or (last_label in CHECK_STEPS and rc == 1)
                                     or rc in SOFT_EXIT.get(last_label, ())):
        job.state = "ok"
    else:
        why = desk_failures.reason_from_log(job.log_path)
        job.summary = f"{job.step} 실패 — {why}" if why else f"{job.step} 실패 (종료 코드 {rc})"
        job.state = "failed"

    if job.kind == "ai":
        # 두 줄이 함께 끝나거나 사람이 그사이 메모를 적어도 notes.json 을 서로 덮지 않게 LOCK 안에서
        with LOCK:
            marker = active_marker(job.lesson, lesson_notes.LANE[job.note_kind])
            if job.state == "ok":
                marker.unlink(missing_ok=True)
                job.summary = apply_ai_result(job)
            else:
                restored = restore_bundle(job.lesson, marker)
                write_log(job, f"작업 전으로 되돌림: {', '.join(restored) or '바뀐 것 없음'}")
                if job.state == "stopped":
                    lesson_notes.release_working(folder, f"멈춤 — 되돌리고 대기로 ({job.stamp})", to="queued",
                                                 ids=job.note_ids)
                else:
                    lesson_notes.release_working(folder, f"{job.summary} — 되돌림 ({job.stamp})", ids=job.note_ids)
            # 다른 줄이 아직 돌면 사용량 기록을 다시 쓰지 않는다 — 그 작업이 같은 파일에 덧붙이는 중일 수 있다
            if not any(j is not job for j in LANES.get(job.lesson, {}).values()):
                prune_usage(folder)
    elif job.kind == "build":
        if job.state == "ok":
            screen = "화면 결함 없음" if job.results.get("화면 결함 검사") == 0 else "화면 결함 있음"
            func = "기능 테스트 통과" if job.results.get("기능 테스트") == 0 else "기능 테스트 실패 있음"
            included = f"{', '.join(job.note_ids)} 반영 · " if job.note_ids else "새 메모 없음 · "
            job.summary = f"{included}빌드 끝 · {screen} · {func} — 로그에서 자세히"
        elif job.state == "stopped":
            job.summary = "멈춤 — 빌드가 반쯤 됐을 수 있다. 다시 [빌드]하세요"
    elif job.kind in ("draft", "install"):
        finish_draft(job)

    job.ended = datetime.now(KST)
    tally(job)
    if job.state == "failed":
        what = f"{NOTE_KIND_LABEL.get(job.note_kind, '')} {', '.join(job.note_ids)}".strip() if job.kind == "ai" else \
            KIND_LABEL.get(job.kind, job.kind) if job.kind in ("draft", "install") else ("자동 빌드" if job.auto else "빌드")
        alert(f"{job.lesson} 작업 실패 — {what}", job.summary)
    write_log(job, f"끝 — {job.state} {job.summary}")
    record = {k: v for k, v in job.public().items() if k != "tail"}
    with (folder / JOBS_NAME).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


NOTE_KIND_LABEL = {"code": "코드", "image": "그림", "verify": "검증"}
SESSIONS: dict[str, dict] = {}   # 차시 → 이번 대기열 한 바퀴의 집계(끝날 때 알림으로 보낸다)


def alert(title: str, body: str) -> None:
    """바탕화면 알림. 기다리지 않는다 — PowerShell 이 느려도 작업을 붙잡지 않게 따로 띄운다."""
    if not SETTINGS.get("notify"):
        return
    threading.Thread(target=notify.toast, args=(f"차시 작업대 · {title}", body), daemon=True).start()


def tally(job: Job) -> None:
    session = SESSIONS.setdefault(job.lesson, {"done": 0, "open": 0, "failed": 0, "jobs": 0})
    if job.kind != "ai" or job.state == "stopped":
        return
    session["jobs"] += 1
    if job.state == "failed":
        session["failed"] += len(job.note_ids)
        return
    for outcome, count in job.outcomes.items():
        session["done" if outcome in DONE_RESULTS else "open"] += count


def alert_queue_done(lesson_ref: str, build: Job | None, built_by_verify: bool = False, title: str = "대기열 완료") -> None:
    """대기열 한 바퀴가 끝났다 — 집계를 한 번 알리고 비운다. AI 작업이 없었으면(빌드만) 알리지 않는다."""
    session = SESSIONS.pop(lesson_ref, None)
    if not session or not session["jobs"]:
        return
    parts = [f"고침 {session['done']}"] + ([f"못 한 것 {session['open']}"] if session["open"] else []) \
        + ([f"실패 {session['failed']}"] if session["failed"] else [])
    if build is None:
        tail_text = "검증 전 빌드로 화면에 반영됨" if built_by_verify else             ("화면 반영할 변경 없음" if not session["done"] else "빌드 안 함")
    elif build.state == "ok":
        tail_text = "자동 빌드 끝 — 화면에 반영됨"
    else:
        tail_text = "자동 빌드 실패 — 작업대에서 확인"
    if title == "멈춤":
        tail_text += " · 남은 메모는 [다시 시작]으로 이어서"
    alert(f"{lesson_ref} {title}", f"{' · '.join(parts)} · {tail_text}")


def short_line(text: str, limit: int = 60) -> str:
    """긴 설명에서 카드에 보일 한 줄 — 첫 줄의 첫 문장을 limit 자로."""
    first = text.strip().lstrip("- ").splitlines()[0] if text.strip() else ""
    first = first.split(". ")[0].split("다. ")[0]
    return first if len(first) <= limit else first[:limit].rstrip() + "…"


def keep_result_images(job: Job, paths: list[str]) -> list[dict]:
    """그림 작업이 고치거나 만든 그림을 `desk/{id}/after/{작업 번호}/` 에 남기고 [{path, new}] 를 돌려준다.

    사용자 요청(2026-10-01) — 카드의 [그림 보기]로 바로 보게. 전(前)은 작업 전 백업 `backup/{작업 번호}/` 에 이미 있다.
    지금 파일이 아니라 사본을 보이는 것은, 나중 작업이 같은 그림을 또 바꿔도 이 메모가 만든 그림을 보이려는 것이다.
    """
    source = lesson_dir(job.lesson)
    backup = job.dir / "backup" / job.stamp
    after = job.dir / "after" / job.stamp
    out = []
    for raw in paths:
        rel = raw.replace("\\", "/").lstrip("/")
        path = (source / rel).resolve()
        if (source / "assets").resolve() not in path.parents or not path.is_file() \
                or path.suffix.lower() not in IMAGE_SUFFIXES or any(e["path"] == rel for e in out):
            continue
        (after / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, after / rel)
        out.append({"path": rel, "new": not (backup / rel).exists()})
    return out


def result_image(lesson_ref: str, stamp: str, rel: str, ver: str) -> Path | None:
    """[그림 보기]가 여는 그림. before = 작업 전 백업, after = 작업이 낸 사본(없으면 지금 파일).
    작업 번호·경로를 그대로 받으므로 정해진 폴더 밖이나 그림이 아닌 파일은 내주지 않는다."""
    if lesson_ref not in lessons() or not __import__("re").fullmatch(r"\d{8}-\d{6}(-\d+)?", stamp) \
            or Path(rel).suffix.lower() not in IMAGE_SUFFIXES:
        return None
    folder = desk_dir(lesson_ref)
    roots = {"before": [folder / "backup" / stamp],
             "after": [folder / "after" / stamp, lesson_dir(lesson_ref)]}.get(ver, [])
    for root in roots:
        path = (root / rel).resolve()
        if root.resolve() in path.parents and path.is_file():
            return path
    return None


def backfill_result_images(lesson_ref: str) -> None:
    """[그림 보기] 전에 끝난 그림 메모 — 작업 전 백업과 지금 파일을 비교해 바뀐 그림을 한 번 찾아 적는다.

    결과 파일에 경로가 남아 있으면(마지막 그림 작업) 그것을 쓴다. 새로 만든 그림은 백업에 없어 비교로는 못 찾는다.
    그 뒤에 또 바뀌었을 수 있으므로 '후' 는 지금 파일이다(after 사본이 없다).
    """
    folder = desk_dir(lesson_ref)
    todo = [n for n in lesson_notes.load(folder) if lesson_notes.kind_of(n) == "image"
            and (n.get("result") or {}).get("job") and "images" not in n["result"]]
    if not todo:
        return
    source = lesson_dir(lesson_ref)
    last = {}
    try:
        last = {i.get("id"): i for i in json.loads((folder / AI_KIND["image"][2]).read_text(encoding="utf-8")).get("notes", [])}
    except (OSError, ValueError):
        pass
    found: dict[str, list[dict]] = {}
    for note in todo:
        backup = folder / "backup" / note["result"]["job"]
        item = last.get(note["id"])
        if item and item.get("files"):
            rels = [str(e.get("path", "")).replace("\\", "/") for e in item["files"]]
        else:
            rels = [p.relative_to(backup).as_posix() for p in sorted(backup.rglob("*"))
                    if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES and (source / p.relative_to(backup)).is_file()
                    and (source / p.relative_to(backup)).read_bytes() != p.read_bytes()] if backup.is_dir() else []
        found[note["id"]] = [{"path": r, "new": not (backup / r).exists()} for r in rels if (source / r).is_file()]
    with LOCK:
        notes = lesson_notes.load(folder)
        for note in notes:
            if note["id"] in found and note.get("result") and "images" not in note["result"]:
                note["result"]["images"] = found[note["id"]]
        lesson_notes.save(folder, notes)


def apply_ai_result(job: Job) -> str:
    """결과 파일대로 이 작업이 맡은 메모의 상태를 바꾼다. 된 것만 '확인 대기', 나머지는 이유를 달고 '열림'."""
    folder = job.dir
    label, _, result_name, _ = AI_KIND[job.note_kind]
    result_path = folder / result_name
    items = json.loads(result_path.read_text(encoding="utf-8")).get("notes", []) if result_path.exists() else []
    pending = list(job.note_ids)
    counts: dict[str, int] = {}
    for item in items:
        if item.get("id") not in pending:
            continue
        pending.remove(item["id"])
        outcome = item.get("result", "")
        counts[outcome] = counts.get(outcome, 0) + 1
        # 결과는 구조로 붙인다 — 카드는 headline 한 줄만 보이고 detail 은 접어 둔다(2026-09-30 사용자 요청).
        # headline 이 없으면(옛 결과·모델이 빠뜨림) detail 첫 문장을 줄여 쓴다
        detail = str(item.get("detail") or "").strip()
        headline = str(item.get("headline") or "").strip() or short_line(detail)
        result = {"kind": outcome, "label": RESULT_LABEL.get(outcome, outcome), "step": label,
                  "headline": headline, "detail": detail, "job": job.stamp}
        if job.note_kind == "image":
            result["images"] = keep_result_images(job, [str(e.get("path", "")) for e in item.get("files", [])])
        lesson_notes.set_result(folder, item["id"], "review" if outcome in DONE_RESULTS else "open", result,
                                f"{label} — {RESULT_LABEL.get(outcome, outcome)}: {headline}")
        follow = str(item.get("follow_up") or "").strip()
        if job.note_kind == "image" and follow and outcome in DONE_RESULTS:
            # 새 그림을 화면에 붙이는 일은 코드 몫 — 그 그림 메모 **바로 다음 차례**에 코드 메모로 넣는다.
            # 대기열 맨 앞이 아니라 그림 메모 뒤 첫 대기 메모 앞 — 코드 줄이 함께 돌아 그림 메모보다 앞선
            # 코드 메모가 아직 대기 중일 수 있다
            notes = lesson_notes.load(folder)
            at = next(i for i, n in enumerate(notes) if n["id"] == item["id"])
            after = [n["id"] for n in notes[at + 1:] if n["status"] == "queued"]
            note = lesson_notes.add(folder, f"[{item['id']} 이어서 — 그림 단계가 넘김] {follow}", "code",
                                    before=after[0] if after else None)
            lesson_notes.set_status(folder, [item["id"]], "review", f"화면에 붙이는 일은 코드 메모 {note['id']} 로 이어 넣음")
    if pending:
        lesson_notes.set_status(folder, pending, "open", f"{label} — AI 가 이 메모의 결과를 안 적었다")
    if pending:
        counts["missing"] = len(pending)
    job.outcomes = counts
    parts = [f"{RESULT_LABEL.get(k, k)} {v}건" for k, v in counts.items() if k != "missing"] \
        + ([f"결과 없음 {len(pending)}건"] if pending else [])
    return " · ".join(parts)


def ai_job(lesson_ref: str, group: list[dict]) -> Job:
    """대기열 맨 앞 묶음으로 작업 하나를 만든다(메모를 '처리 중'으로 바꾸고 백업을 뜬다)."""
    folder = desk_dir(lesson_ref)
    stamp = new_stamp()
    kind = lesson_notes.kind_of(group[0])
    ids = [n["id"] for n in group]
    label, script, result_name, _ = AI_KIND[kind]
    target = build_target(lesson_ref)
    if not (lesson_dir(lesson_ref) / "lesson.json").is_file():
        raise ValueError(f"작업 경로에 lesson.json 이 없다: {lesson_dir(lesson_ref)}")
    if kind == "verify" and not target:
        raise ValueError("검증 메모인데 " + NOT_BUILDABLE)
    (folder / result_name).unlink(missing_ok=True)  # 지난 작업의 결과를 이번 것으로 읽지 않게
    backup = backup_bundle(lesson_ref, stamp, kind)
    lesson_notes.set_status(folder, ids, "working", f"{label} 시작 ({stamp})")
    py = sys.executable
    common = ["--gyo6-root", str(gyo6()), "--lesson", lesson_ref, "--desk-dir", str(folder),
              "--lesson-dir", str(lesson_dir(lesson_ref))]
    steps = []
    common = [*common, *model_args(kind)]
    if kind == "code":
        steps.append((label, [py, "-B", script, *common, "--baseline", str(backup)], PROJECT_DIR))
    elif kind == "image":
        steps.append((label, [py, "-B", script, *common], PROJECT_DIR))
    else:
        build_root, build_ref = target
        view = f"http://127.0.0.1:{SETTINGS['port']}/view/{lesson_notes.desk_id(lesson_ref)}/{build_ref}/index.html"
        steps.append(("검증 전 빌드", [NPM, "run", "build:lesson", "--", build_ref], build_root))
        steps.append((label, [py, "-B", script, *common, "--view-url", view], PROJECT_DIR))
    job = Job(lesson_ref, "ai", steps, stamp, ids, kind)
    write_log(job, f"{lesson_ref} · {label} · 메모 {', '.join(ids)}")
    return job


def run_queue(lesson_ref: str) -> None:
    """대기열이 빌 때까지(또는 멈출 때까지) 처리한다. 클로드 줄(코드)과 코덱스 줄(그림·검증)이 함께 돈다.

    사용자 요청(2026-10-01). 무엇을 지금 시작할 수 있는지는 `lesson_notes.runnable_groups` 가 순서로 정한다 —
    작업 하나가 끝날 때마다 대기열을 다시 읽으므로 도는 중에 끼워 넣거나 옮겨도 반영된다.
    자동 빌드·'이번 작업 끝나면 멈춤'은 **두 줄이 다 끝난 뒤에** 한다.
    """
    folder = desk_dir(lesson_ref)
    changed = False  # 마지막 빌드 뒤에 코드·그림 작업이 파일을 바꿨나 — 검증 묶음은 직전에 빌드하므로 거기서 지운다
    built_by_verify = False  # 바뀐 것을 검증 전 빌드가 이미 화면에 올렸나(끝 알림 문구용)
    lanes = LANES.setdefault(lesson_ref, {})
    finished: queue.Queue[Job | None] = queue.Queue()   # 끝난 작업, 또는 None = "대기열이 바뀌었으니 다시 봐라"(kick)
    with LOCK:
        WAKE[lesson_ref] = finished

    def lane_worker(job: Job) -> None:
        try:
            run_job(job)
        finally:
            finished.put(job)

    while True:
        with LOCK:
            paused = is_paused(lesson_ref)
            soft = pause_after_pending(lesson_ref)
            while not paused and not soft:
                groups = lesson_notes.runnable_groups(lesson_notes.load(folder), set(lanes))
                if not groups:
                    break
                lane, group = groups[0]
                try:
                    job = ai_job(lesson_ref, group)
                except ValueError as exc:
                    # 이 묶음을 못 만들면 사람이 볼 때까지 둔다 — 같은 실패를 되풀이하지 않게
                    lesson_notes.set_status(folder, [n["id"] for n in group], "open", f"시작 못 함: {exc}")
                    continue
                lanes[lane] = job
                JOBS[lesson_ref] = job
                threading.Thread(target=lane_worker, args=(job,), daemon=True).start()
            if not lanes:
                RUNNERS.discard(lesson_ref)
                WAKE.pop(lesson_ref, None)
                if soft and not paused:
                    # '이번 작업 끝나면 멈춤' — 도는 작업이 다 끝났다. 바뀐 것이 있으면 지금까지 한 것을 빌드한다
                    set_paused(lesson_ref, True)
                    if changed and build_target(lesson_ref):
                        start_build(lesson_ref, auto=True, pause=True)
                    else:
                        alert_queue_done(lesson_ref, None, built_by_verify, title="멈춤")
                elif changed and not paused and build_target(lesson_ref):
                    start_build(lesson_ref, auto=True)   # 완료 알림은 빌드가 끝난 뒤에
                elif not paused:
                    alert_queue_done(lesson_ref, None, built_by_verify)
                return
        job = finished.get()
        if job is None:
            continue   # 한 줄이 도는 중에 메모가 들어왔거나 바뀌었다 — 쉬는 줄에 줄 것이 생겼는지 다시 본다
        with LOCK:
            lanes.pop(lesson_notes.LANE[job.note_kind], None)
        if job.note_kind == "verify":
            built_by_verify = built_by_verify or (changed and job.results.get("검증 전 빌드") == 0)
            changed = False
        elif job.state == "ok" and any(n["id"] in job.note_ids and n["status"] == "review"
                                       for n in lesson_notes.load(folder)):
            changed = True  # 고침·그림 새로 구움이 하나라도 있었다(확인 필요만 나왔으면 파일이 그대로다)


def kick(lesson_ref: str) -> None:
    """대기열에 할 일이 있고 멈춤이 아니고 아무것도 안 돌면 처리기를 띄운다."""
    with LOCK:
        if lesson_ref in RUNNERS:
            # 처리기가 한 줄을 돌리며 기다리는 중 — 깨워서 쉬는 줄에 줄 것이 생겼는지 보게 한다
            # (그러지 않으면 코드가 도는 동안 적은 그림 메모가 코드가 끝날 때까지 기다린다)
            if lesson_ref in WAKE:
                WAKE[lesson_ref].put(None)
            return
        if is_paused(lesson_ref):
            return
        if pause_after_pending(lesson_ref):   # 끝낼 작업 없이 예약만 남았다(빌드가 끝난 직후 등) — 그냥 멈춘다
            set_paused(lesson_ref, True)
            return
        current = JOBS.get(lesson_ref)
        if current and current.state == "running":
            return  # 빌드가 도는 중 — 빌드가 끝나면 다시 부른다
        if not lesson_notes.next_group(lesson_notes.load(desk_dir(lesson_ref))):
            return
        RUNNERS.add(lesson_ref)
    threading.Thread(target=run_queue, args=(lesson_ref,), daemon=True).start()


def last_built_at(lesson_ref: str) -> str:
    """마지막으로 빌드된 시각(빌드 결과물 index.html 의 수정 시각, ISO). 빌드된 적 없으면 빈 문자열."""
    target = build_target(lesson_ref)
    built = (target[0] / "dist" / target[1] / "index.html") if target else None
    if not built or not built.exists():
        return ""
    return datetime.fromtimestamp(built.stat().st_mtime, KST).isoformat(timespec="seconds")


def unbuilt_notes(lesson_ref: str) -> list[str]:
    """마지막 빌드 뒤에 AI 가 파일을 바꾼 메모(코드·그림 · 확인 대기/완료) — 다음 빌드에 새로 들어갈 것.

    사용자 요청(2026-09-30) — 빌드마다 무엇이 새로 들어가는지 보이게. 검증 메모는 파일을 안 바꾸므로 뺀다.
    """
    since = last_built_at(lesson_ref)
    out = []
    for note in lesson_notes.load(desk_dir(lesson_ref)):
        if note.get("status") not in ("review", "done") or lesson_notes.kind_of(note) == "verify":
            continue
        result = note.get("result") or {}
        if result and result.get("kind") not in DONE_RESULTS:
            continue
        changed_at = result.get("at") or note.get("updated_at") or ""
        if not since or changed_at > since:
            out.append(note["id"])
    return out


def start_build(lesson_ref: str, auto: bool = False, pause: bool = False) -> None:
    target = build_target(lesson_ref)
    if not target:
        raise ValueError(NOT_BUILDABLE)
    folder = desk_dir(lesson_ref)
    build_root, build_ref = target
    dist_index = build_root / "dist" / build_ref / "index.html"
    steps = [
        ("빌드", [NPM, "run", "build:lesson", "--", build_ref], build_root),
        ("화면 결함 검사", ["node", "tools/check_rendered.mjs", str(build_root), build_ref, "--json",
                            str(folder / "rendered.json")], PROJECT_DIR),
        ("기능 테스트", ["node", "tools/run_functional_tests.mjs", str(dist_index), str(folder / "screens"),
                        str(build_root)], PROJECT_DIR),
    ]
    job = Job(lesson_ref, "build", steps, new_stamp(), note_ids=unbuilt_notes(lesson_ref), auto=auto)
    write_log(job, f"{lesson_ref} · {'자동 빌드(대기열 끝)' if auto else '빌드'} · "
                   + (f"새로 들어가는 메모: {', '.join(job.note_ids)}" if job.note_ids else "새로 들어가는 메모 없음"))
    JOBS[lesson_ref] = job

    def run_then_resume() -> None:
        run_job(job)
        # 빌드하는 동안 새 메모가 들어왔으면 한 바퀴가 아직 안 끝났다 — 알림은 그 뒤로 미룬다
        if pause:
            alert_queue_done(lesson_ref, job, title="멈춤")
        elif auto and (is_paused(lesson_ref) or not lesson_notes.next_group(lesson_notes.load(folder))):
            alert_queue_done(lesson_ref, job)
        kick(lesson_ref)

    threading.Thread(target=run_then_resume, daemon=True).start()


# ── 초안 파이프라인 ─────────────────────────────────────────────────────────

def draft_key(run_id: str) -> str:
    return f"run:{run_id}"


def draft_meta(run_id: str) -> dict:
    path = RUNS_DIR / run_id / DRAFT_META
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {}


def save_draft_meta(run_id: str, meta: dict) -> None:
    (RUNS_DIR / run_id).mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / run_id / DRAFT_META).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def last_produce(run_id: str) -> dict | None:
    items = [i for i in pipeline_status.executions(RUNS_DIR / run_id) if i["type"] == "produce"]
    return items[-1] if items else None


def draft_state(run_id: str) -> dict:
    """화면이 어떤 버튼을 보여 줄지 — 도는 중 · 답 대기 · 초안 끝 · 넣음."""
    job = JOBS.get(draft_key(run_id))
    last = last_produce(run_id)
    running = bool(job and job.state == "running") or bool(last and last["running"])
    waiting = "" if running or not last or last["ended"] is None else (last.get("waiting") or "")
    lesson_ready = (RUNS_DIR / run_id / "lesson" / "lesson.json").exists()
    done = bool(last and last["ended"] and last.get("exit_code") == 0 and not waiting and lesson_ready)
    record_path = RUNS_DIR / run_id / "install-record.json"
    installed = []
    if record_path.exists():
        try:
            installed = [k.rpartition("|")[2] for k in json.loads(record_path.read_text(encoding="utf-8"))]
        except json.JSONDecodeError:
            installed = []
    meta = draft_meta(run_id)
    slot = meta.get("slot", "")
    return {
        "run_id": run_id, "slot": slot, "running": running, "waiting": waiting, "done": done,
        "lesson_ready": lesson_ready, "installed": installed,
        "slot_exists": bool(slot) and (gyo6() / "lessons" / slot / "lesson.json").exists(),
        "can_continue": not running and last is not None and (bool(waiting) or last["status"] in ("끊김", "실패", "위반 남음")),
        "job": job.public() if job else None,
        "questions": interview_form.load(RUNS_DIR / run_id) if waiting else {"file": "", "items": []},
    }


def start_draft_job(run_id: str, label: str, steps: list[tuple[str, list[str], Path]], kind: str = "draft") -> Job:
    key = draft_key(run_id)
    current = JOBS.get(key)
    last = last_produce(run_id) if (RUNS_DIR / run_id).exists() else None
    if (current and current.state == "running") or (last and last["running"]):
        raise ValueError("이 run 에서 파이프라인이 이미 돌고 있다")
    job = Job(run_id, kind, steps, new_stamp(), folder=RUNS_DIR / run_id / DRAFT_JOBS_DIR)
    write_log(job, f"{run_id} · {label}")
    JOBS[key] = job
    threading.Thread(target=run_job, args=(job,), daemon=True).start()
    return job


def new_draft(run_id: str, slot: str, filename: str, data_b64: str) -> None:
    import base64
    if not RUN_ID_RE.match(run_id):
        raise ValueError("run 이름은 영문·숫자·-·_ 2~40자(예: g4l05)")
    if (RUNS_DIR / run_id).exists():
        raise ValueError(f"이미 있는 run 이름이다: {run_id}")
    if slot and not SLOT_RE.match(slot):
        raise ValueError("넣을 차시는 4-1/05 모양으로 적는다")
    if not filename.lower().endswith(".pdf"):
        raise ValueError("스토리보드는 PDF 만 받는다")
    blob = base64.b64decode(data_b64.split(",", 1)[-1])
    if not blob.startswith(b"%PDF"):
        raise ValueError("PDF 파일이 아니다")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    pdf = UPLOADS_DIR / f"{run_id}.pdf"
    pdf.write_bytes(blob)
    save_draft_meta(run_id, {"slot": slot, "pdf": pdf.relative_to(PROJECT_DIR).as_posix(), "source_name": filename,
                             "created": datetime.now(KST).isoformat(timespec="seconds")})
    py = sys.executable
    start_draft_job(run_id, "초안 만들기", [("초안 만들기", [
        py, "-B", "produce_lesson.py", str(pdf), "--run-id", run_id, "--gyo6-root", str(gyo6()),
        "--through", "interview", "--no-voice", *pipeline_model_args()], PROJECT_DIR)])


def continue_draft(run_id: str) -> None:
    py = sys.executable
    notes = RUNS_DIR / run_id / "interview" / "questions.md"
    if not notes.exists():
        # 인터뷰 질문이 나오기 전에 멈췄다 — 처음부터 인터뷰까지 다시(끝난 단계는 캐시로 건너뛴다).
        # run 폴더만 넘기면 스토리보드 경로가 비어 기획 단계가 원본을 못 본다 — 올린 PDF 를 다시 넘긴다
        pdf = PROJECT_DIR / draft_meta(run_id).get("pdf", "")
        if not pdf.is_file():
            pdf = RUNS_DIR / run_id / "storyboard.pdf"
        if not pdf.is_file():
            raise ValueError("올린 스토리보드 PDF 를 찾지 못했다 — 새 초안으로 다시 올린다")
        cmd = [py, "-B", "produce_lesson.py", str(pdf), "--run-id", run_id, "--gyo6-root", str(gyo6()),
               "--through", "interview", "--no-voice", *pipeline_model_args()]
        start_draft_job(run_id, "이어서 만들기", [("이어서 만들기", cmd, PROJECT_DIR)])
        return
    cmd = [py, "-B", "produce_lesson.py", str(RUNS_DIR / run_id), "--gyo6-root", str(gyo6()),
           "--start-at", "interview_brief", "--no-voice", "--interview-notes", str(notes), *pipeline_model_args()]
    start_draft_job(run_id, "이어서 만들기", [("이어서 만들기", cmd, PROJECT_DIR)])


def install_draft(run_id: str, slot: str, overwrite: bool) -> None:
    if not SLOT_RE.match(slot):
        raise ValueError("넣을 차시를 4-1/05 모양으로 적는다")
    if not (RUNS_DIR / run_id / "lesson" / "lesson.json").exists():
        raise ValueError("아직 초안(lesson.json)이 없다")
    if (gyo6() / "lessons" / slot / "lesson.json").exists() and not overwrite:
        raise ValueError(f"gyo6 에 {slot} 이(가) 이미 있다 — 덮어쓰려면 [덮어쓰기]로 다시 누른다")
    meta = draft_meta(run_id)
    meta["slot"] = slot
    save_draft_meta(run_id, meta)
    py = sys.executable
    install = [py, "-B", "install_lesson.py", str(RUNS_DIR / run_id), "--target", str(gyo6()), "--lesson", slot]
    if overwrite:
        install.append("--overwrite")
    start_draft_job(run_id, f"gyo6에 넣기 → {slot}", [
        ("배치", install, PROJECT_DIR),
        ("빌드", [NPM, "run", "build:lesson", "--", slot], gyo6()),
        ("화면 검증", [py, "-B", "verify_lesson.py", str(RUNS_DIR / run_id), "--target", str(gyo6()), "--lesson", slot,
                       "--skip-llm"], PROJECT_DIR),
    ], kind="install")


def finish_draft(job: Job) -> None:
    """초안 작업이 끝났다 — 무엇을 할 차례인지 요약하고 알린다."""
    run_id = job.lesson
    if job.state == "stopped":
        job.summary = "멈춤 — [이어서 만들기]로 다시 돌릴 수 있다(끝난 단계는 캐시로 건너뛴다)"
        return
    if job.state != "ok":
        return  # 실패 알림은 finish 가 공통으로 보낸다
    if job.kind == "install":
        slot = draft_meta(run_id).get("slot", "")
        verify = job.results.get("화면 검증")
        tail_text = "화면 검증 통과" if verify == 0 else "화면 검증에서 막는 지적 있음 — runs/{}/verify/report.md".format(run_id)
        job.summary = f"gyo6 {slot} 에 넣고 빌드함 · {tail_text} — 이제 차시 작업대에서 고칠 수 있다"
        alert(f"{run_id} → {slot} gyo6에 넣음", job.summary)
        return
    last = last_produce(run_id)
    if last and last.get("waiting"):
        questions = interview_form.load(RUNS_DIR / run_id)["items"]
        pending = sum(1 for q in questions if not q["answered"])
        what = "인터뷰 질문" if last["waiting"] == "interview" else "요구 명세의 정할 것"
        job.summary = f"{what} 답 대기 — 답이 필요한 것 {pending}건. 답을 적고 [답 저장하고 이어서 만들기]"
        alert(f"{run_id} 답을 적어 주세요", job.summary)
    elif (RUNS_DIR / run_id / "lesson" / "lesson.json").exists():
        job.summary = "초안 끝 — [gyo6에 넣기]로 차시에 넣는다"
        alert(f"{run_id} 초안 완료", job.summary)
    else:
        job.summary = "끝났지만 초안(lesson.json)이 없다 — 로그를 확인"
        alert(f"{run_id} 초안 확인 필요", job.summary)


def stop_draft(run_id: str) -> None:
    job = JOBS.get(draft_key(run_id))
    if not job or job.state != "running":
        raise ValueError("작업대에서 띄운, 도는 작업이 없다(터미널에서 직접 돌린 것은 거기서 끈다)")
    job.stop_requested = True
    write_log(job, "멈춤 요청")
    if job.proc:
        kill_tree(job.proc)


def running_jobs(lesson_ref: str) -> list[Job]:
    """이 차시에서 지금 도는 작업 — 클로드 줄 · 코덱스 줄 · 빌드. 시작한 순서."""
    with LOCK:
        jobs = [JOBS.get(lesson_ref), *LANES.get(lesson_ref, {}).values()]
    unique = {id(j): j for j in jobs if j and j.state == "running"}
    return sorted(unique.values(), key=lambda j: j.stamp)


def stop(lesson_ref: str) -> None:
    """대기열을 멈추고, 도는 작업이 있으면 끊는다(AI 작업이면 finish 가 되돌리고 메모를 대기로 돌린다)."""
    set_paused(lesson_ref, True)
    for job in running_jobs(lesson_ref):   # 두 줄 모두 · 빌드
        job.stop_requested = True
        write_log(job, "멈춤 요청")
        if job.proc:
            kill_tree(job.proc)


def resume(lesson_ref: str) -> None:
    set_paused(lesson_ref, False)
    kick(lesson_ref)


def recover_interrupted() -> None:
    """작업대가 작업 중에 꺼졌으면 — 작업 전으로 되돌리고, 메모는 대기로, 대기열은 멈춰 둔다."""
    if not DESK_DIR.is_dir():
        return
    for folder in sorted(p for p in DESK_DIR.iterdir() if p.is_dir()):
        markers = sorted(folder.glob(ACTIVE_GLOB))
        if not markers:
            continue
        lesson_ref = json.loads(markers[0].read_text(encoding="utf-8"))["lesson"]
        restored = [f for marker in markers for f in restore_bundle(lesson_ref, marker)]
        lesson_notes.release_working(folder, "작업대가 작업 중에 꺼짐 — 되돌리고 대기로", to="queued")
        set_paused(lesson_ref, True)
        print(f"  {lesson_ref}: 끊긴 AI 작업 {len(markers)}개를 되돌림({', '.join(restored) or '바뀐 것 없음'}) — 대기열은 멈춰 둠")


# ── 사용량 ───────────────────────────────────────────────────────────────────

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def prune_usage(folder: Path) -> None:
    """AI 작업 사용량을 최근 USAGE_KEEP 개만 남긴다(사용자 요청 2026-09-30). 작업 번호가 없는 옛 기록도 지운다."""
    path = folder / usage_log.LOG_NAME
    rows = read_jsonl(path)
    tags = []
    for row in rows:
        tag = row.get("tag")
        if tag and tag not in tags:
            tags.append(tag)
    keep = set(tags[-USAGE_KEEP:])
    kept = [row for row in rows if row.get("tag") in keep]
    if len(kept) == len(rows):
        return
    with LOCK:
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
        usage_log.write_report(folder)


def usage_rows(folder: Path) -> list[dict]:
    """작업별 사용량(최근 것이 위). 작업 기록(jobs.jsonl)과 작업 번호로 잇는다."""
    jobs = {j.get("id"): j for j in read_jsonl(folder / JOBS_NAME) if j.get("id")}
    by_tag: dict[str, dict] = {}
    for row in read_jsonl(folder / usage_log.LOG_NAME):
        tag = row.get("tag")
        if not tag or row.get("kind") != "llm":
            continue
        entry = by_tag.setdefault(tag, {"id": tag, "provider": row.get("provider"), "model": row.get("model"),
                                        "input": 0, "cached": 0, "output": 0, "cost_usd": None, "seconds": 0.0,
                                        "calls": 0})
        entry["calls"] += 1
        entry["seconds"] += float(row.get("seconds") or 0)
        for key in ("input", "cached", "output"):
            entry[key] += int(row.get(key) or 0)
        if row.get("cost_usd") is not None:
            entry["cost_usd"] = (entry["cost_usd"] or 0) + float(row["cost_usd"])
    out = []
    for tag, entry in by_tag.items():
        job = jobs.get(tag, {})
        entry.update({"note_kind": job.get("note_kind", ""), "note_ids": job.get("note_ids", []),
                      "state": job.get("state", "running"), "started": job.get("started", "")})
        entry["seconds"] = round(entry["seconds"], 1)
        out.append(entry)
    return sorted(out, key=lambda e: e["id"], reverse=True)[:USAGE_KEEP]


# ── 상태 ─────────────────────────────────────────────────────────────────────

def lessons() -> list[str]:
    return lesson_notes.gyo6_lessons(gyo6(), SETTINGS["semesters"])


def state() -> dict:
    out = []
    for lesson_ref in lessons():
        folder = desk_dir(lesson_ref)
        backfill_result_images(lesson_ref)
        job = JOBS.get(lesson_ref)
        history = read_jsonl(folder / JOBS_NAME)
        work = lesson_dir(lesson_ref)
        stamps = [(work / n).stat().st_mtime for n in BUNDLE if (work / n).exists()]
        target = build_target(lesson_ref)
        built = (target[0] / "dist" / target[1] / "index.html") if target else None
        out.append({
            "lesson": lesson_ref,
            "semester": lesson_ref.split("/")[0],
            "title": lesson_title(lesson_ref),
            "notes": lesson_notes.load(folder),
            "job": job.public() if job else None,
            # 지금 도는 작업 전부 — 클로드 줄 · 코덱스 줄이 함께 돌 수 있다(빌드는 AI 작업과 겹치지 않는다)
            "jobs": [j.public() for j in running_jobs(lesson_ref)],
            "paused": is_paused(lesson_ref),
            "pause_after": pause_after_pending(lesson_ref),
            "queue_running": lesson_ref in RUNNERS,
            "history": history[-5:][::-1],
            "unbuilt": unbuilt_notes(lesson_ref),
            "usage": usage_rows(folder),
            "edited_at": datetime.fromtimestamp(max(stamps), KST).isoformat(timespec="seconds") if stamps else "",
            "built_at": datetime.fromtimestamp(built.stat().st_mtime, KST).isoformat(timespec="seconds")
            if built and built.exists() else "",
            "view": f"/view/{lesson_notes.desk_id(lesson_ref)}/{target[1]}/index.html" if built and built.exists() else "",
            "work_dir": str(work),
            "default_dir": str(default_dir(lesson_ref)),
            "work_custom": "lesson_dir" in lesson_config(lesson_ref),
            "work_ok": (work / "lesson.json").is_file(),
            "buildable": target is not None,
        })
    return {"lessons": out, "gyo6_root": str(gyo6()), "models": model_state()}


_TITLES: dict[str, tuple[float, str]] = {}


def lesson_title(lesson_ref: str) -> str:
    path = lesson_dir(lesson_ref) / "lesson.json"
    if not path.is_file():
        path = default_dir(lesson_ref) / "lesson.json"
    mtime = path.stat().st_mtime
    cached = _TITLES.get(lesson_ref)
    if cached and cached[0] == mtime:
        return cached[1]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        title = str(data.get("title") or (data.get("meta") or {}).get("title") or "")
    except (json.JSONDecodeError, AttributeError):
        title = ""
    _TITLES[lesson_ref] = (mtime, title)  # 경로를 바꾸면 mtime 이 달라져 다시 읽는다
    return title


# ── HTTP ─────────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # 폴링이 잦아 요청마다 찍지 않는다
        pass

    def send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data, code: int = 200) -> None:
        self.send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if path == "/":
            return self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/pipeline":
            return self.send(200, PIPELINE_PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/state":
            return self.send_json(state())
        if path == "/api/pipeline":
            return self.send_json({"runs": pipeline_status.overview(RUNS_DIR), "models": model_state()})
        if path == "/api/pipeline/run":
            run_id = dict(p.split("=", 1) for p in url.query.split("&") if "=" in p).get("id", "")
            run_id = unquote(run_id)
            names = {p.name for p in RUNS_DIR.iterdir() if p.is_dir()}
            if run_id not in names:  # 요청 값으로 경로를 짓지 않는다 — 있는 run 이름만 받는다
                return self.send_json({"error": "없는 run"}, 404)
            detail = pipeline_status.run_detail(RUNS_DIR / run_id)
            detail["draft"] = draft_state(run_id)
            return self.send_json(detail)
        if path in ("/api/pipeline/files", "/api/pipeline/file"):
            query = {k: unquote(v) for k, v in (p.split("=", 1) for p in url.query.split("&") if "=" in p)}
            run_id = query.get("id", "")
            if run_id not in {p.name for p in RUNS_DIR.iterdir() if p.is_dir()}:
                return self.send_json({"error": "없는 run"}, 404)
            if path == "/api/pipeline/files":
                return self.send_json({"groups": run_artifacts.artifacts(RUNS_DIR / run_id)})
            return self.serve_run_file(RUNS_DIR / run_id, query.get("path", ""), query.get("thumb") == "1")
        if path == "/api/desk/image":
            query = {k: unquote(v) for k, v in (p.split("=", 1) for p in url.query.split("&") if "=" in p)}
            found = result_image(query.get("lesson", ""), query.get("job", ""), query.get("path", ""), query.get("ver", ""))
            if found is None:
                return self.send(404, b"not found", "text/plain")
            if query.get("thumb") == "1":
                return self.send(200, thumbnail(found, 480), "image/jpeg")
            return self.send(200, found.read_bytes(), mimetypes.guess_type(found.name)[0] or "application/octet-stream")
        if path.startswith("/view/"):
            return self.serve_dist(path[len("/view/"):])
        self.send(404, b"not found", "text/plain")

    def serve_run_file(self, run_dir: Path, rel: str, thumb: bool) -> None:
        """run 산출물 하나 — 글은 utf-8 글로, 그림은 그대로(thumb 이면 작게 줄여서), PDF 는 PDF 로."""
        path = run_artifacts.safe_path(run_dir, rel)
        if path is None:
            return self.send(404, b"not found", "text/plain")
        suffix = path.suffix.lower()
        if suffix in run_artifacts.TEXT_SUFFIXES:
            return self.send(200, path.read_bytes(), "text/plain; charset=utf-8")
        if suffix == ".pdf":
            return self.send(200, path.read_bytes(), "application/pdf")
        if thumb:
            return self.send(200, thumbnail(path), "image/jpeg")
        self.send(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")

    def serve_dist(self, rest: str) -> None:
        """/view/<학기-차시>/<dist 기준 경로> — 그 차시 작업 폴더가 속한 체크아웃의 dist 를 연다.
        빌드된 index.html 이 ../../assets/fonts 로 글꼴을 찾으므로 <학기-차시> 아래가 dist 루트와 같은 모양이어야 한다."""
        desk_key, _, sub = rest.partition("/")
        match = [ref for ref in lessons() if lesson_notes.desk_id(ref) == desk_key]
        target = build_target(match[0]) if match else None
        if not target:
            return self.send(404, b"not found", "text/plain")
        root = (target[0] / "dist").resolve()
        file = (root / sub).resolve()
        if root not in file.parents or not file.is_file():
            return self.send(404, b"not found", "text/plain")
        ctype = "font/woff2" if file.suffix == ".woff2" else (mimetypes.guess_type(file.name)[0] or "application/octet-stream")
        self.send(200, file.read_bytes(), ctype)

    def do_POST(self):
        if self.headers.get("X-Desk") != "1":
            return self.send_json({"error": "X-Desk 헤더가 없다"}, 403)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            path = urlparse(self.path).path
            if path.startswith("/api/draft/"):
                return self.draft_post(path, body)
            if path == "/api/pipeline/open":
                return self.send_json(open_in_editor(str(body.get("run_id", "")), str(body.get("path", ""))))
            if path == "/api/models":
                with LOCK:
                    set_models(str(body.get("claude", "")).strip(), str(body.get("codex", "")).strip(),
                               str(body.get("claude_effort", "")).strip(), str(body.get("codex_effort", "")).strip())
                return self.send_json({"ok": True, "models": model_state()})
            lesson_ref = str(body.get("lesson", ""))
            if lesson_ref not in lessons():
                raise ValueError("목록에 없는 차시")
            folder = desk_dir(lesson_ref)
            note_id = str(body.get("id", ""))
            with LOCK:
                current = JOBS.get(lesson_ref)
                busy = lesson_ref in RUNNERS or (current is not None and current.state == "running")
                if path == "/api/notes":
                    lesson_notes.add(folder, str(body.get("text", "")), str(body.get("kind", "code")),
                                     str(body.get("before") or "") or None)
                    kick(lesson_ref)
                elif path == "/api/notes/move":
                    lesson_notes.move(folder, note_id, str(body.get("before") or "") or None)
                    kick(lesson_ref)   # 옮기면 쉬는 줄에 줄 것이 생길 수 있다
                elif path == "/api/notes/kind":
                    lesson_notes.set_kind(folder, note_id, str(body.get("kind", "")))
                    kick(lesson_ref)
                elif path == "/api/notes/requeue":
                    if any(n["id"] == note_id and n["status"] == "working" for n in lesson_notes.load(folder)):
                        raise ValueError("처리 중인 메모다")
                    lesson_notes.set_status(folder, [note_id], "queued", "사람이 다시 맡김")
                    kick(lesson_ref)
                elif path == "/api/notes/status":
                    if any(n["id"] == note_id and n["status"] == "working" for n in lesson_notes.load(folder)):
                        raise ValueError("처리 중인 메모는 상태를 바꿀 수 없다 — 먼저 멈춘다")
                    lesson_notes.set_status(folder, [note_id], str(body.get("status")), "사람이 상태를 바꿈")
                elif path == "/api/notes/delete":
                    lesson_notes.remove(folder, note_id)
                elif path == "/api/build":
                    if busy:
                        raise ValueError("AI 작업이나 빌드가 도는 중이다 — 끝난 뒤나 멈춘 뒤에 빌드한다")
                    start_build(lesson_ref)
                elif path == "/api/stop":
                    stop(lesson_ref)
                elif path == "/api/resume":
                    resume(lesson_ref)
                elif path == "/api/pause_after":
                    if not body.get("on"):
                        set_pause_after(lesson_ref, False)
                    elif busy:
                        set_pause_after(lesson_ref, True)   # 도는 작업이 끝나면 run_queue 가 멈춘다
                    else:
                        set_paused(lesson_ref, True)         # 도는 게 없으면 바로 멈춘다
                elif path == "/api/path":
                    if busy:
                        raise ValueError("작업이 도는 중에는 작업 경로를 바꿀 수 없다")
                    set_lesson_dir(lesson_ref, str(body.get("path", "")))
                else:
                    return self.send_json({"error": "없는 경로"}, 404)
            self.send_json({"ok": True})
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)


def _draft_post(self, path: str, body: dict) -> None:
    run_id = str(body.get("run_id", ""))
    if path == "/api/draft/new":
        with LOCK:
            new_draft(run_id, str(body.get("slot", "")).strip(), str(body.get("filename", "")), str(body.get("data", "")))
        return self.send_json({"ok": True})
    if run_id not in {p.name for p in RUNS_DIR.iterdir() if p.is_dir()}:
        raise ValueError("없는 run")
    with LOCK:
        if path == "/api/draft/answers":
            interview_form.save(RUNS_DIR / run_id, {str(k): str(v) for k, v in (body.get("answers") or {}).items()})
            if body.get("continue"):
                continue_draft(run_id)
        elif path == "/api/draft/continue":
            continue_draft(run_id)
        elif path == "/api/draft/install":
            install_draft(run_id, str(body.get("slot", "")).strip(), bool(body.get("overwrite")))
        elif path == "/api/draft/stop":
            stop_draft(run_id)
        else:
            return self.send_json({"error": "없는 경로"}, 404)
    self.send_json({"ok": True})


Handler.draft_post = _draft_post


def load_settings(args: argparse.Namespace) -> None:
    saved = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    root = args.gyo6_root or saved.get("gyo6_root")
    if not root:
        raise SystemExit("처음에는 --gyo6-root 로 gyo6_content 경로를 알려 주세요. 다음부터는 기억합니다.")
    SETTINGS["gyo6_root"] = Path(root).resolve()
    if args.semesters:
        SETTINGS["semesters"] = [s.strip() for s in args.semesters.split(",") if s.strip()]
    elif saved.get("semesters"):
        SETTINGS["semesters"] = saved["semesters"]
    if not (SETTINGS["gyo6_root"] / "lessons").is_dir():
        raise SystemExit(f"gyo6_content 가 아니다(lessons/ 가 없다): {SETTINGS['gyo6_root']}")
    SETTINGS["claude_model"] = saved.get("claude_model", "")
    SETTINGS["claude_effort"] = saved.get("claude_effort", "")
    SETTINGS["codex_effort"] = saved.get("codex_effort", "")
    SETTINGS["codex_model"] = saved.get("codex_model", "")
    save_settings()


def save_settings() -> None:
    DESK_DIR.mkdir(exist_ok=True)
    CONFIG.write_text(json.dumps({"gyo6_root": str(SETTINGS["gyo6_root"]), "semesters": SETTINGS["semesters"],
                                  "claude_model": SETTINGS["claude_model"], "codex_model": SETTINGS["codex_model"],
                                  "claude_effort": SETTINGS["claude_effort"], "codex_effort": SETTINGS["codex_effort"]},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="차시별 메모 대기열 · AI 처리 · 빌드 · 멈춤 대시보드")
    parser.add_argument("--gyo6-root", default=None, help="gyo6_content 경로 (한 번 주면 desk/config.json 에 기억)")
    parser.add_argument("--semesters", default=None, help="보일 학기, 쉼표로 (기본 3-1,3-2,4-1,4-2)")
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--no-notify", action="store_true", help="바탕화면 알림을 띄우지 않는다")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    load_settings(args)
    SETTINGS["port"] = args.port
    SETTINGS["notify"] = not args.no_notify
    recover_interrupted()
    for lesson_ref in lessons():
        kick(lesson_ref)  # 멈춤이 아닌 차시의 남은 대기열을 이어서 처리한다
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"차시 작업대: http://127.0.0.1:{args.port}  · gyo6: {gyo6()} · 학기 {', '.join(SETTINGS['semesters'])}")
    print("끄려면 Ctrl+C (돌던 작업은 끊기고, 다음에 켤 때 되돌린다)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        for key in list(JOBS):   # 차시 작업(두 줄 · 빌드)과 초안 작업
            for job in running_jobs(key):
                job.stop_requested = True
                if job.proc:
                    kill_tree(job.proc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
