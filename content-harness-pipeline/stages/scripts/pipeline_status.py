"""초안 파이프라인이 **지금 어디를 돌고 있는지**와 **단계별 토큰**을 run 기록에서 읽어 낸다.

`lesson_desk.py` 의 /pipeline 화면이 쓴다. 읽기만 한다.

    runs/{id}/pipeline-log.jsonl   produce_lesson.py  pipeline_start(pid·stages) · stage_start · stage_done ·
                                                      stage_cached · stage_rejected · pipeline_end
                                   verify_lesson.py   verify_start(pid) · verify_end
    runs/{id}/usage-log.jsonl      LLM 호출마다 시간·토큰(`usage_log`) — 시각으로 실행에 나눠 담는다

**도는 중인가**는 로그만으로는 못 가른다 — 도중에 죽은 실행도 끝 기록이 없다. 그래서 시작 기록의 pid 가 살아
있는지 본다. pid 는 다시 쓰일 수 있으므로 그 프로세스가 **시작 기록 즈음에 생겼는지**까지 대조한다.
2026-09-30 이전 기록에는 pid 가 없다 — 끝 기록이 없으면 "끝 기록 없음" 으로 둔다(도는지 모른다).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_NAME = "pipeline-log.jsonl"
USAGE_NAME = "usage-log.jsonl"

# produce_lesson.STAGES 순서. 여기서 produce_lesson 을 import 하지 않는다(무거운 의존을 끌고 온다) —
# 시작 기록에 stages 가 있으면 그것을 쓰고, 이 표는 이름과 옛 기록용이다.
STAGE_ORDER = ["senior_planner", "senior_designer", "interview_brief", "lesson_spec", "visual_design",
               "senior_developer", "asset_render"]
STAGE_LABEL = {
    "senior_planner": "기획",
    "senior_designer": "디자인 · 인터뷰 질문",
    "interview_brief": "제작 지침",
    "lesson_spec": "요구 명세",
    "visual_design": "비주얼 설계",
    "senior_developer": "개발",
    "asset_render": "그림 굽기",
    "check_outputs": "산출물 검사",
    "voice_script": "음성 대본",
    "check_rendered": "화면 결함 검사",
    "run_functional_tests": "기능 테스트",
    "capture_lesson": "캡처",
    "lesson_review": "화면 판정(LLM)",
    "screen_diff": "스토리보드 대조(LLM)",
    "screen_fix": "수정안(LLM)",
}
EXIT_LABEL = {0: "끝남", 1: "실패", 2: "위반 남음"}
# 표에 그릴 순서 — 제작 단계 다음에 제작 뒤 코드 단계, 그다음 화면 검증 층 순서
DISPLAY_ORDER = STAGE_ORDER + ["check_outputs", "voice_script", "check_rendered", "run_functional_tests",
                               "capture_lesson", "lesson_review", "screen_diff", "screen_fix"]


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=KST)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _process_created(pid: int) -> datetime | None:
    """살아 있는 프로세스면 생성 시각, 아니면 None."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259:  # STILL_ACTIVE
                return None
            times = [wintypes.FILETIME() for _ in range(4)]
            if not kernel32.GetProcessTimes(handle, *[ctypes.byref(t) for t in times]):
                return None
            ticks = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime  # 1601-01-01 부터 100ns
            return datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ticks // 10)
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    return None  # 생성 시각을 모르면 None 으로 두되, 아래에서 살아 있음은 따로 본다


def pid_running(pid: int | None, started: datetime | None) -> bool:
    if not pid or not started:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    created = _process_created(int(pid))
    if created is None:
        return False
    # 같은 번호를 다른 프로세스가 다시 쓴 경우를 거른다 — 시작 기록 조금 전에 생긴 프로세스여야 한다
    return started - timedelta(minutes=10) <= created <= started + timedelta(seconds=30)


def executions(run_dir: Path, now: datetime | None = None) -> list[dict]:
    """pipeline-log 를 실행 단위로 나눈다(초안 제작 = pipeline_start~end, 화면 검증 = verify_start~end). 오래된 것이 앞."""
    now = now or datetime.now(KST)
    out: list[dict] = []
    current: dict | None = None
    verify: dict | None = None
    for row in read_jsonl(run_dir / LOG_NAME):
        event = row.get("event")
        at = parse_time(row.get("time") or row.get("at"))
        if event == "pipeline_start":
            current = {"type": "produce", "started": at, "ended": None, "pid": row.get("pid"),
                       "start_at": row.get("start_at"), "through": row.get("through"),
                       "planned": row.get("stages") or [], "exit_code": None, "waiting": "",
                       "stages": {}, "events": []}
            out.append(current)
        elif event == "verify_start":
            verify = {"type": "verify", "started": at, "ended": None, "pid": row.get("pid"), "lesson": row.get("lesson"),
                      "exit_code": None, "findings": None, "blocking": None, "stages": {}, "events": []}
            out.append(verify)
        elif event == "verify_end":
            if verify is None or verify["ended"] is not None:  # 시작 기록이 없던 옛 검증
                verify = {"type": "verify", "started": None, "ended": None, "pid": None, "lesson": row.get("lesson"),
                          "exit_code": None, "stages": {}, "events": []}
                out.append(verify)
            verify.update({"ended": at, "findings": row.get("findings"), "blocking": row.get("blocking"),
                           "exit_code": 2 if row.get("blocking") else 0})
        elif current is not None and current["ended"] is None:
            stage = row.get("stage")
            if event == "stage_start" and stage:
                current["stages"][stage] = {"state": "running", "started": at, "ended": None}
            elif event in ("stage_done", "stage_cached", "stage_rejected") and stage:
                entry = current["stages"].setdefault(stage, {"started": None})
                entry.update({"state": {"stage_done": "done", "stage_cached": "cached",
                                        "stage_rejected": "rejected"}[event], "ended": at,
                              "reason": row.get("reason", "")})
            elif event == "pipeline_end":
                current.update({"ended": at, "exit_code": row.get("exit_code"), "waiting": row.get("waiting", "")})
            elif event:
                current["events"].append({"at": at, "event": event})
    for item in out:
        item["running"] = item["ended"] is None and pid_running(item.get("pid"), item.get("started"))
        if item["ended"] is not None:
            item["status"] = {"interview": "인터뷰 답 대기", "decisions": "정할 것 답 대기"}.get(item.get("waiting") or "") \
                or EXIT_LABEL.get(item.get("exit_code"), f"종료 {item.get('exit_code')}")
        elif item["running"]:
            item["status"] = "도는 중"
        elif item.get("pid"):
            item["status"] = "끊김"          # 프로세스가 없는데 끝 기록도 없다 — 도중에 죽었다
        else:
            item["status"] = "끝 기록 없음"  # 옛 기록 — 도는지 모른다
    return out


def attach_usage(run_dir: Path, items: list[dict], now: datetime | None = None) -> None:
    """usage-log 의 호출을 시각으로 실행에 나눠 담고 단계별로 더한다."""
    now = now or datetime.now(KST)
    rows = read_jsonl(run_dir / USAGE_NAME)
    windows = []
    for i, item in enumerate(items):
        start = item.get("started")
        if start is None and item["type"] == "verify" and item.get("ended"):
            # 시작 기록이 없던 옛 검증 — 앞 실행이 끝난 뒤부터 이 끝 기록까지의 verify_lesson 호출
            before = [x.get("ended") or x.get("started") for x in items[:i] if (x.get("ended") or x.get("started"))]
            windows.append((max(before) if before else item["ended"] - timedelta(hours=2),
                            item["ended"] + timedelta(seconds=5), item, "verify_lesson"))
            continue
        if start is None:
            continue
        end = item.get("ended") or (now if item.get("running") else None)
        if end is None:  # 끊긴 실행 — 다음 실행 시작 전까지
            later = [x["started"] for x in items[i + 1:] if x.get("started")]
            end = later[0] if later else now
        # 끝 기록 뒤에 적힌 음성·검사 단계까지 90초 — 단, 다음 실행이 그 안에 시작하면 거기서 끊는다
        # (실측 2026-09-30 — 답을 적고 바로 이어서 돌리니 앞 실행의 호출이 뒤 실행으로 넘어가 셌다)
        tail_end = end + timedelta(seconds=90)
        later = [x["started"] for x in items[i + 1:] if x.get("started")]
        if later and later[0] < tail_end:
            tail_end = max(end, later[0] - timedelta(seconds=1))
        windows.append((start, tail_end, item, ""))
    for item in items:
        item["usage"] = {}
    for row in rows:
        at = parse_time(row.get("at"))
        if at is None:
            continue
        match = [w for w in windows if w[0] - timedelta(seconds=2) <= at <= w[1]
                 and (not w[3] or w[3] in str(row.get("session") or ""))]
        if not match:
            continue
        # 2초 여유는 초 단위로 잘린 호출 시각 때문이다. 여유 없이도 들어가는 구간이 있으면 그쪽이 먼저다 —
        # 앞 실행 끝 바로 뒤에 다음 실행이 시작하면 여유 때문에 뒤 실행으로 잘못 가던 것을 막는다
        exact = [w for w in match if w[0] <= at]
        item = (exact or match)[-1][2]
        stage = str(row.get("stage") or "?").split("#")[0]
        entry = item["usage"].setdefault(stage, {"calls": 0, "llm_calls": 0, "input": 0, "cached": 0, "output": 0,
                                                 "cost_usd": None, "seconds": 0.0, "providers": [], "failed": 0})
        entry["calls"] += 1
        entry["seconds"] += float(row.get("seconds") or 0)
        if row.get("kind") == "llm":
            entry["llm_calls"] += 1
            for key in ("input", "cached", "output"):
                entry[key] += int(row.get(key) or 0)
            if row.get("cost_usd") is not None:
                entry["cost_usd"] = (entry["cost_usd"] or 0) + float(row["cost_usd"])
            if row.get("provider") and row["provider"] not in entry["providers"]:
                entry["providers"].append(row["provider"])
            if not row.get("ok", True):
                entry["failed"] += 1


def _iso(value: datetime | None) -> str:
    return value.astimezone(KST).isoformat(timespec="seconds") if value else ""


def stage_rows(item: dict) -> list[dict]:
    """화면에 그릴 단계 표 — 계획된 단계 + 기록에 나온 단계 + 토큰만 있는 단계(음성·검사 등)."""
    names = list(item.get("planned") or [])
    for name in list(item.get("stages", {})) + list(item.get("usage", {})):
        if name not in names:
            names.append(name)
    planned = list(item.get("planned") or [])
    names.sort(key=lambda n: (planned.index(n) if n in planned else len(planned),
                              DISPLAY_ORDER.index(n) if n in DISPLAY_ORDER else len(DISPLAY_ORDER)))
    rows = []
    for name in names:
        stage = item.get("stages", {}).get(name, {})
        usage = item.get("usage", {}).get(name, {})
        state = stage.get("state") or ("done" if usage else "pending")
        if state == "running" and not item.get("running"):
            state = "stopped"
        elif state == "pending" and item.get("ended") is not None:
            state = "skipped"
        started, ended = stage.get("started"), stage.get("ended")
        seconds = (ended - started).total_seconds() if started and ended else \
            ((datetime.now(KST) - started).total_seconds() if started and state == "running" else usage.get("seconds"))
        rows.append({"name": name, "label": STAGE_LABEL.get(name, name), "state": state,
                     "started": _iso(started), "ended": _iso(ended), "seconds": round(seconds or 0, 1),
                     "reason": stage.get("reason", ""), **{k: usage.get(k) for k in
                     ("calls", "llm_calls", "input", "cached", "output", "cost_usd", "providers", "failed")}})
    return rows


def totals(rows: list[dict]) -> dict:
    cost = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    return {"input": sum(r.get("input") or 0 for r in rows), "cached": sum(r.get("cached") or 0 for r in rows),
            "output": sum(r.get("output") or 0 for r in rows), "cost_usd": round(sum(cost), 4) if cost else None,
            "llm_calls": sum(r.get("llm_calls") or 0 for r in rows)}


def public(item: dict) -> dict:
    rows = stage_rows(item)
    return {
        "type": item["type"], "status": item["status"], "running": item["running"],
        "started": _iso(item.get("started")), "ended": _iso(item.get("ended")),
        "start_at": item.get("start_at"), "through": item.get("through"), "lesson": item.get("lesson"),
        "exit_code": item.get("exit_code"), "findings": item.get("findings"), "blocking": item.get("blocking"),
        "current": [r["label"] for r in rows if r["state"] == "running"],
        "stages": rows, "totals": totals(rows),
    }


def run_detail(run_dir: Path, limit: int = 10) -> dict:
    items = executions(run_dir)
    attach_usage(run_dir, items)
    shown = [public(item) for item in items[-limit:]][::-1]
    # run 전체 단계별 누계 — 기록이 남은 모든 호출
    all_usage: dict[str, dict] = {}
    for item in items:
        for name, usage in item.get("usage", {}).items():
            acc = all_usage.setdefault(name, {"input": 0, "cached": 0, "output": 0, "cost_usd": None, "llm_calls": 0})
            for key in ("input", "cached", "output", "llm_calls"):
                acc[key] += usage.get(key) or 0
            if usage.get("cost_usd") is not None:
                acc["cost_usd"] = (acc["cost_usd"] or 0) + usage["cost_usd"]
    cumulative = [{"name": n, "label": STAGE_LABEL.get(n, n), **v} for n, v in all_usage.items() if v["llm_calls"]]
    cumulative.sort(key=lambda r: -(r["input"] + r["output"]))
    return {"run_id": run_dir.name, "executions": shown, "total_executions": len(items),
            "cumulative": cumulative, "cumulative_totals": totals(cumulative)}


def run_summary(run_dir: Path) -> dict:
    items = executions(run_dir)
    last = items[-1] if items else None
    log = run_dir / LOG_NAME
    lesson = run_dir / "lesson" / "lesson.json"
    title = ""
    if lesson.exists():
        try:
            title = str(json.loads(lesson.read_text(encoding="utf-8")).get("title") or "")
        except (json.JSONDecodeError, AttributeError):
            title = ""
    summary = {"run_id": run_dir.name, "title": title, "updated": _iso(datetime.fromtimestamp(log.stat().st_mtime, KST)),
               "executions": len(items), "running": any(i["running"] for i in items)}
    if last:
        attach_usage(run_dir, items)
        summary["last"] = public(last)
        current = [public(i) for i in items if i["running"]]
        summary["current"] = current[-1] if current else None
        stage_all: list[dict] = []
        for item in items:
            stage_all += stage_rows(item)
        summary["cumulative_totals"] = totals(stage_all)
    return summary


def overview(runs_dir: Path, limit: int = 30) -> list[dict]:
    runs = [p for p in runs_dir.iterdir() if p.is_dir() and (p / LOG_NAME).exists()]
    runs.sort(key=lambda p: (p / LOG_NAME).stat().st_mtime, reverse=True)
    return [run_summary(p) for p in runs[:limit]]
