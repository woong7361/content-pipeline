"""단계마다 **토큰과 시간**을 run 에 기록한다.

    runs/{id}/usage-log.jsonl   한 줄 = 한 번의 LLM 호출 또는 한 코드 단계(원본)
    runs/{id}/usage-report.md   사람이 읽는 표 — 기록할 때마다 다시 만든다

왜 필요한가 — 두 클라이언트(`codex_client.py`)가 호출이 끝나면 토큰 사용량을 돌려주는데 **아무도 받아
적지 않았다.** 그래서 "이 차시 하나에 토큰이 얼마, 시간이 얼마" 를 물을 수 없었고, 문서의 예상치
(`print_estimates`)는 실측과 비교된 적이 없다.

LLM 호출은 클라이언트가 스스로 적는다(`record_call`). 어느 run 에 적을지는 진입 스크립트가 `bind(run_dir)` 로
정한다 — 묶지 않으면 아무것도 안 한다. 그림 배치처럼 스레드에서 동시에 불리므로 잠금을 건다.
코드 단계는 `with step(...)` 으로 시간만 잰다.

토큰은 두 제공자가 세는 방식이 달라서 한 모양으로 맞춘다.

    codex  usage.input_tokens(캐시 포함) · cached_input_tokens · output_tokens
    claude usage.input_tokens(캐시 제외) · cache_read_input_tokens · cache_creation_input_tokens · output_tokens
           + total_cost_usd
    →      input(캐시 포함 전체) · cached(캐시에서 읽은 것) · output · cost_usd(claude 만)
"""

from __future__ import annotations

import json
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_NAME = "usage-log.jsonl"
REPORT_NAME = "usage-report.md"

_lock = threading.Lock()
_run_dir: Path | None = None
_session = ""
_tag = ""


def bind(run_dir: Path, session: str, tag: str = "") -> None:
    """이 프로세스의 기록을 run_dir 에 적는다. session 은 어느 명령이 돌았는지(표에서 묶는 단위).
    tag 는 부른 쪽이 기록을 다시 찾을 열쇠다 — 차시 작업대는 작업 번호를 넣어 작업별 사용량을 묶는다."""
    global _run_dir, _session, _tag
    _run_dir = run_dir
    _session = f"{datetime.now(KST).strftime('%m-%d %H:%M')} {session}"
    _tag = tag


def normalize(provider: str, usage: dict | None) -> dict:
    if not isinstance(usage, dict):
        return {"input": None, "cached": None, "output": None, "cost_usd": None}
    if provider == "claude":
        raw = usage.get("usage") or {}
        fresh = int(raw.get("input_tokens") or 0)
        read = int(raw.get("cache_read_input_tokens") or 0)
        write = int(raw.get("cache_creation_input_tokens") or 0)
        return {"input": fresh + read + write, "cached": read, "output": int(raw.get("output_tokens") or 0),
                "cost_usd": usage.get("total_cost_usd")}
    return {"input": int(usage.get("input_tokens") or 0), "cached": int(usage.get("cached_input_tokens") or 0),
            "output": int(usage.get("output_tokens") or 0), "cost_usd": None}


def _write(record: dict) -> None:
    if _run_dir is None:
        return
    record = {"at": datetime.now(KST).isoformat(timespec="seconds"), "session": _session,
              **({"tag": _tag} if _tag else {}), **record}
    with _lock:
        with (_run_dir / LOG_NAME).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        write_report(_run_dir)


def record_call(stage: str | None, provider: str, model: str | None, seconds: float,
                usage: dict | None, ok: bool, error: str = "") -> None:
    _write({"kind": "llm", "stage": stage or "?", "provider": provider, "model": model or "default",
            "seconds": round(seconds, 1), "ok": ok, "error": error[:160], **normalize(provider, usage)})


@contextmanager
def step(stage: str, note: str = ""):
    """코드 단계의 시간만 잰다. 실패해도 적는다."""
    started = time.monotonic()
    ok = False
    try:
        yield
        ok = True
    finally:
        _write({"kind": "code", "stage": stage, "provider": "-", "model": "-", "seconds": round(time.monotonic() - started, 1),
                "ok": ok, "error": "", "note": note, "input": None, "cached": None, "output": None, "cost_usd": None})


def _num(value) -> str:
    return "–" if value is None else f"{value:,}"


def _dur(seconds: float) -> str:
    seconds = int(round(seconds))
    return f"{seconds // 60}분 {seconds % 60:02d}초" if seconds >= 60 else f"{seconds}초"


def write_report(run_dir: Path) -> None:
    path = run_dir / LOG_NAME
    if not path.exists():
        return
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    llm = [r for r in rows if r["kind"] == "llm"]

    def total(key: str, items: list) -> int | None:
        values = [r[key] for r in items if r.get(key) is not None]
        return sum(values) if values else None

    cost = total("cost_usd", llm)
    lines = [
        f"# 토큰·시간 기록 — {run_dir.name}",
        "",
        "`usage-log.jsonl` 에서 만든 표다. 파이프라인이 기록할 때마다 다시 쓴다(손으로 고치지 않는다).",
        "시간은 **그 단계가 걸린 시간의 합**이다 — 개발과 그림처럼 동시에 돈 단계는 실제 경과 시간보다 합이 크다.",
        "",
        "## 합계",
        "",
        f"- LLM 호출 {len(llm)}회 (실패 {sum(1 for r in llm if not r['ok'])}회) · LLM 시간 합 {_dur(sum(r['seconds'] for r in llm))}",
        f"- 입력 토큰 {_num(total('input', llm))} (그중 캐시 {_num(total('cached', llm))}) · 출력 토큰 {_num(total('output', llm))}",
        f"- claude 비용 ${cost:.2f}" if cost is not None else "- claude 비용 –",
        "",
        "## 단계별",
        "",
        "| 단계 | 종류 | 제공자 | 횟수 | 시간 합 | 입력 토큰 | 캐시 | 출력 토큰 | 비용(USD) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    order: list[str] = []
    grouped: dict[str, list] = {}
    for r in rows:
        name = r["stage"].split("#", 1)[0]          # 그림 배치(asset_render#3)는 한 단계로 묶는다
        key = f"{name}|{r['kind']}|{r['provider']}"
        if key not in grouped:
            order.append(key)
        grouped.setdefault(key, []).append(r)
    for key in order:
        items = grouped[key]
        name, kind, provider = key.split("|")
        c = total("cost_usd", items)
        lines.append(
            f"| {name} | {'LLM' if kind == 'llm' else '코드'} | {provider} | {len(items)} | {_dur(sum(r['seconds'] for r in items))} | "
            f"{_num(total('input', items))} | {_num(total('cached', items))} | {_num(total('output', items))} | "
            f"{'–' if c is None else f'{c:.2f}'} |"
        )

    lines += ["", "## 전체 기록 (실행 순서)", ""]
    for session in dict.fromkeys(r["session"] for r in rows):
        mine = [r for r in rows if r["session"] == session]
        lines += [f"### {session}", "", "| 시각 | 단계 | 제공자 | 모델 | 시간 | 입력 | 캐시 | 출력 | 결과 |", "|---|---|---|---|---:|---:|---:|---:|---|"]
        for r in mine:
            # 실패 이유는 여러 줄일 수 있다(`Codex CLI failed\ncommand: …`) — 표 칸에 줄바꿈이나 | 가 들어가면
            # 표 한 줄이 쪼개진다(2026-10-01, problem.md [dashboard-md-viewer-hang]). 한 줄로 접고 | 는 이스케이프한다
            error = " ".join(str(r.get("error", "")).split())[:40].replace("|", "\\|")
            result = "✓" if r["ok"] else f"✗ {error}"
            lines.append(
                f"| {r['at'][11:19]} | {r['stage']} | {r['provider']} | {r['model']} | {_dur(r['seconds'])} | "
                f"{_num(r['input'])} | {_num(r['cached'])} | {_num(r['output'])} | {result} |"
            )
        lines.append("")
    (run_dir / REPORT_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
