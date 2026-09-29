"""화면 검증에서 나온 문제를 **누가 고칠 수 있는가**로 나눈다.

`verify_lesson.py` 의 네 층(화면 결함 · 기능 테스트 · 화면 판정 · 스토리보드 대조)이 각자
다른 모양의 결과를 낸다. 여기서 한 모양(finding)으로 모으고 담당자를 붙인다.

담당자를 먼저 가르는 이유 — 한 곳에서 다 고치려 하면 엉뚱한 자리를 고친다. 탑 그림의 위치가
틀렸는데 CSS 를 고치거나, 스토리보드 원문이 틀렸는데 개발자가 문구를 "교정" 해 버린다
(원문 보존 규칙 위반). 실측(2026-09-29, 4-1/03) — 한 번의 검수에서 나온 12건이 배치(개발) ·
그림↔좌표(개발) · 원문 문구(원고) · 공통 런타임(gyo6) 네 갈래로 갈렸다.

    developer   senior_developer 를 되먹여 다시 부른다 — lesson.json · player-ext.*
    asset       asset_render 로 그 그림만 다시 굽는다 — 그림 **자체**가 잘못 그려진 것
    storyboard  원고 담당이 확인한다 — 화면 문구가 스토리보드 원문 그대로인데 틀린 것
    runtime     gyo6_content 공통 런타임 — 이 차시가 고칠 수 없다
    human       사람이 판단한다 — 담당을 정할 근거가 없는 것, 검사 도구가 끝까지 못 돈 것

**그림 ↔ 좌표 불일치는 developer 다.** 구워진 그림을 기준으로 좌표를 맞춘다. 그림을 다시
구워도 같은 자리에 나온다는 보장이 없기 때문이다(개발과 그림이 동시에 돌아서 개발자는 그림을
못 보고 계획만 보고 좌표를 잡는다).

심각도는 넷이다. `blocking` 은 코드 판정이라 거짓 양성이 없는 것(화면 결함 게이트 · 기능 실패)이고,
`high` 는 LLM 판정의 "이대로 내보낼 수 없다" 다. 둘 다 차시를 막는다.
"""

from __future__ import annotations

import re
from pathlib import Path

OWNERS = ("developer", "asset", "storyboard", "runtime", "human")
OWNER_LABEL = {
    "developer": "개발 단계(senior_developer) — lesson.json · player-ext.*",
    "asset": "그림 단계(asset_render) — 그 그림만 다시 굽는다",
    "storyboard": "원고 담당 — 스토리보드 원문 확인",
    "runtime": "gyo6_content 공통 런타임 — 이 차시 밖",
    "human": "사람 판단 — 담당을 정할 근거가 없다",
}
BLOCKING = ("blocking", "high")
SEVERITY_ORDER = {"blocking": 0, "high": 1, "medium": 2, "low": 3}

# 원문 대조에 쓸 인용. 따옴표 종류가 섞여 들어온다(LLM 이 “ ” 도 " " 도 쓴다).
QUOTE_RE = re.compile(r"“([^”]{2,})”|\"([^\"]{2,})\"|「([^」]{2,})」|‘([^’]{2,})’|'([^']{2,})'")
ASSET_PATH_RE = re.compile(r"assets/[\w./-]+\.(?:png|webp|jpg|jpeg|svg)")


def finding(layer: str, severity: str, owner: str, where: str, issue: str,
            evidence: list[str] | None = None, why: str = "") -> dict:
    return {
        "layer": layer,
        "severity": severity,
        "owner": owner,
        "where": where,
        "issue": issue,
        "evidence": evidence or [],
        "route_reason": why,
    }


def squash(text: str) -> str:
    """공백·줄바꿈 차이로 원문 대조가 어긋나지 않게 걷어낸다."""
    return re.sub(r"\s+", "", text or "")


def quoted_strings(text: str) -> list[str]:
    return [next(group for group in match.groups() if group) for match in QUOTE_RE.finditer(text or "")]


def verbatim_in_source(text: str, source_text: str) -> str:
    """지적 안의 인용문이 원문에 **그대로** 있으면 그 인용문을 돌려준다.

    네 글자 미만은 보지 않는다 — "각도" 처럼 짧은 낱말은 원문 어디에나 있어서 근거가 못 된다.
    """
    if not source_text:
        return ""
    haystack = squash(source_text)
    for quote in quoted_strings(text):
        needle = squash(quote)
        if len(needle) >= 4 and needle in haystack:
            return quote
    return ""


def asset_exists(lesson_dir: Path, ref: str) -> bool:
    """계획은 `.png` 로 적히는데 배치에서 `.webp` 로 바뀔 수 있다. 이름 줄기로 본다."""
    path = lesson_dir / ref
    return path.exists() or path.with_suffix(".webp").exists() or path.with_suffix(".png").exists()


def guess_asset_path(text: str, planned: list[str]) -> str:
    """지적 문장에서 그림 경로를 찾는다. 경로가 없으면 **파일 이름 줄기가 딱 하나** 맞을 때만 고른다."""
    direct = ASSET_PATH_RE.findall(text or "")
    if direct:
        return direct[0]
    lowered = (text or "").lower()
    hits = [path for path in planned if Path(path).stem.lower() in lowered]
    return hits[0] if len(hits) == 1 else ""


def runtime_or_developer(detail: str) -> tuple[str, str]:
    if "player.js" in detail and "player-ext" not in detail:
        return "runtime", "오류가 base 런타임(player.js)에서 났다"
    return "developer", "차시 데이터·ext 가 일으킨 것으로 본다"


# ── 층별 변환 ─────────────────────────────────────────────────────────────

def from_rendered(report: dict, lesson_dir: Path) -> list[dict]:
    """`check_rendered.mjs --json`. 배포 차시 거짓 양성 0건을 확인한 게이트라 전부 blocking 이다."""
    items = []
    for violation in report.get("violations") or []:
        kind = violation.get("kind", "")
        detail = violation.get("detail", "")
        where = violation.get("where", "")
        issue = f"[{kind}] {detail}"
        if kind == "broken_image":
            ref = detail.split(":", 1)[-1].strip()
            ref = ref[ref.find("assets/"):] if "assets/" in ref else ref
            if ref.startswith("assets/") and not asset_exists(lesson_dir, ref):
                items.append(finding("rendered", "blocking", "asset", where, issue, [ref],
                                     "그림 파일이 run 에 없다 — 굽지 못했다"))
            else:
                items.append(finding("rendered", "blocking", "developer", where, issue, [ref],
                                     "파일은 있는데 화면이 못 불러온다 — 참조 경로가 틀렸다"))
            continue
        if kind in ("page_error", "console_error"):
            owner, why = runtime_or_developer(detail)
            items.append(finding("rendered", "blocking", owner, where, issue, [], why))
            continue
        items.append(finding("rendered", "blocking", "developer", where, issue, [],
                             "배치·데이터 결함 — 차시가 고친다"))
    # 기준선 확인 전인 검사(글자 겹침·화면 밖)는 막지 않는다. 같은 자리에서 여러 건이면 한 건으로 묶는다.
    grouped: dict[tuple[str, str], list[str]] = {}
    for advisory in report.get("advisories") or []:
        grouped.setdefault((advisory.get("kind", ""), advisory.get("where", "")), []).append(advisory.get("detail", ""))
    for (kind, where), details in grouped.items():
        more = f" 외 {len(details) - 1}건" if len(details) > 1 else ""
        items.append(finding("rendered", "medium", "developer", where, f"[{kind}] {details[0]}{more}",
                             details[1:6], "기계 검사(참고) — 거짓 양성 기준선 확인 전이라 막지 않는다"))
    return items


def from_functional(results: dict, plan: dict, spec: dict, lesson_dir: Path, shot_dir: Path,
                    confirmed: dict[str, str] | None = None) -> tuple[list[dict], list[dict]]:
    """기능 테스트 결과를 finding 과 **테스트 계획의 케이스별 결과**로 바꾼다.

    `confirmed` 는 `asset-plan.json` 의 `specId → path` 다. 명세의 그림 경로는 잠정일 수 있고
    (`path_status: proposed — visual_design 의 asset-plan 경로가 우선한다`), 실측(4-1/03)으로
    23건 중 14건이 확정 단계에서 바뀌었다. `spec_tests` 와 같은 규칙으로 확정 경로를 본다.
    """
    confirmed = confirmed or {}
    spec_assets = {a.get("id"): a for a in spec.get("assets") or [] if isinstance(a, dict)}
    items: list[dict] = []
    problems = {p.get("id"): p for p in results.get("problems") or []}
    seen = set(results.get("seen_ids") or [])
    scene_of = {q.get("id"): q.get("scene_id") for q in spec.get("questions") or []}
    reached_scenes = {scene_of.get(pid) for pid in problems if scene_of.get(pid)}

    def shots(problem: dict) -> list[str]:
        return [str((shot_dir / name).resolve()) for name in problem.get("shots") or []]

    for problem in results.get("problems") or []:
        for name, test in (problem.get("tests") or {}).items():
            if test.get("status") != "fail":
                continue
            items.append(finding(
                "functional", "blocking", "developer", f"{problem.get('id')} · {name}",
                f"[{name}] {test.get('detail', '')} (원자 {', '.join(problem.get('atoms') or [])}, {problem.get('mode')})",
                shots(problem), "정오·흐름이 안 돈다 — 문항 데이터나 ext 원자",
            ))
    if results.get("stuck"):
        items.append(finding("functional", "blocking", "developer", "진행",
                             f"[stuck] {results.get('stuck_detail', '')}", [],
                             "넘어가는 버튼이 안 먹는다 — exitCondition·CTA 배치"))
    for error in results.get("page_errors") or []:
        if error.startswith("automation:"):
            items.append(finding("functional", "blocking", "human", "검사 도구",
                                 f"[automation] 기능 테스트가 끝까지 못 돌았다: {error[11:200]}", [],
                                 "차시 결함인지 도구 한계인지 사람이 가른다 — 못 본 것을 통과로 세지 않는다"))
            continue
        owner, why = runtime_or_developer(error)
        items.append(finding("functional", "blocking", owner, "런타임", f"[page_error] {error}", [], why))

    cases = []
    walked_to_end = not results.get("stuck") and not any(
        e.startswith("automation:") for e in results.get("page_errors") or [])
    for case in plan.get("cases") or []:
        kind, target = case.get("kind"), case.get("target")
        status, detail = "pass", ""
        if kind in ("question_correct", "question_retry"):
            problem = problems.get(target)
            if not problem:
                status = "not_reached"
                detail = "화면에 한 번도 안 나왔다" if walked_to_end else "진행이 그 앞에서 멈췄다"
            else:
                test = (problem.get("tests") or {}).get("correct" if kind == "question_correct" else "retry") or {}
                status = test.get("status", "not_run")
                detail = f"{test.get('detail', '')} ({problem.get('mode')})"
        elif kind == "scene_reachable":
            hit = target in seen or any(s.startswith(f"{target}-") for s in seen) or target in reached_scenes
            status, detail = ("pass", "") if hit else ("not_observed", "대사·문항 id 로 확인하지 못했다(판정 아님)")
        elif kind == "asset_exists":
            path = confirmed.get(target) or (case.get("expected") or {}).get("path", "")
            proposed = "proposed" in str(spec_assets.get(target, {}).get("path_status", "")).lower()
            if target not in confirmed and proposed:
                # 명세 스스로 잠정이라 했고 확정 목록에도 없다 — 설계에서 빠진 그림이다(base 가 그리는 도장 등).
                status, detail = "skip", f"잠정 경로({path})이고 확정 목록에 없다"
            else:
                status = "pass" if path and asset_exists(lesson_dir, path) else "fail"
                detail = path
        cases.append({"id": case.get("id"), "kind": kind, "target": target, "status": status, "detail": detail})

    # 명세 문항이 끝까지 걸었는데도 안 나왔으면 개발 쪽 누락이다. 멈춰서 못 간 것은 위 stuck 이 이미 말한다.
    if walked_to_end:
        for case in cases:
            if case["kind"] == "question_correct" and case["status"] == "not_reached":
                items.append(finding("functional", "high", "developer", case["target"],
                                     f"[not_reached] 명세 문항 {case['target']} 가 학습자 경로에 한 번도 안 나왔다", [],
                                     "문항 id 를 안 옮겼거나 흐름에서 빠졌다"))
    for case in cases:
        if case["kind"] == "asset_exists" and case["status"] == "fail":
            items.append(finding("functional", "blocking", "asset", case["target"],
                                 f"[asset_missing] 명세 그림 파일이 없다: {case['detail']}", [case["detail"]],
                                 "굽지 못한 그림"))
    return items, cases


def from_review(review: dict, capture_dir: Path, source_text: str, planned_assets: list[str]) -> list[dict]:
    """`lesson_review` (LLM). `fix_target` 이 담당을 정하고, 문구는 원문과 대조해 한 번 더 가른다."""
    items = []
    for item in review.get("priority_findings") or []:
        target = item.get("fix_target", "unknown")
        text = f"{item.get('issue', '')} {item.get('evidence', '')}"
        evidence = [str((capture_dir / item["screen"]).resolve())] if item.get("screen") else []
        quote = verbatim_in_source(text, source_text) if target == "lesson.json" else ""
        if quote:
            owner, why = "storyboard", f"문제된 글 「{quote}」 이 스토리보드 원문에 그대로 있다 — 원문 보존 규칙상 개발이 고치면 안 된다"
        elif target in ("player-ext.css", "lesson.json"):
            owner, why = "developer", f"fix_target={target}"
        elif target == "asset":
            owner, why = "asset", "그림 자체가 잘못 그려졌다(fix_target=asset)"
            path = guess_asset_path(text, planned_assets)
            if path:
                evidence.append(path)
        else:
            owner, why = "human", "fix_target=unknown"
        items.append(finding("review", item.get("priority", "medium"), owner, item.get("screen", ""),
                             item.get("issue", ""), evidence + [f"근거: {item.get('evidence', '')}"], why))
    for gap in review.get("storyboard_gaps") or []:
        # 캡처에 없는 것을 "없다" 로 단정할 수 없다. 화면이 빠졌는지 캡처가 못 닿았는지는 사람이 가른다.
        items.append(finding("review", "medium", "human", gap.get("screen", "") or "(화면 없음)",
                             f"[원문 누락?] {gap.get('expected', '')}", [f"판단: {gap.get('why', '')}"],
                             "구현이 빠졌는지 캡처가 못 닿았는지 코드가 못 가른다"))
    return items


def from_diff(diff: dict, capture_dir: Path, planned_assets: list[str]) -> list[dict]:
    """`screen_diff` (LLM). 스토리보드 예시화면과 다른 것이라 원문 쪽 책임이 아니다."""
    items = []
    for change in diff.get("changes") or []:
        target = change.get("target_file", "unknown")
        text = f"{change.get('change', '')} {change.get('screen_shows', '')}"
        evidence = [str((capture_dir / change["screen"]).resolve())] if change.get("screen") else []
        evidence.append(f"스토리보드: {change.get('page', '')} — {change.get('storyboard_shows', '')}")
        if target in ("lesson.json", "player-ext.css", "player-ext.js"):
            owner, why = "developer", f"target_file={target}"
        elif target == "asset":
            owner, why = "asset", "그림 구성이 예시화면과 다르다(target_file=asset)"
            path = guess_asset_path(text, planned_assets)
            if path:
                evidence.append(path)
        else:
            owner, why = "human", "target_file=unknown"
        items.append(finding("screen_diff", change.get("priority", "medium"), owner,
                             f"{change.get('screen', '')} · {change.get('aspect', '')}",
                             change.get("change", ""), evidence, why))
    for page in diff.get("unmatched_pages") or []:
        # 막지 않는다. 실측(2026-09-29, 4-1/03) — "장면 누락" high 5건이 전부 캡처가 못 닿은 화면
        # (인증서·이야기 카드 뒷장)이었고 구현은 있었다. 장면 도달은 ② 기능 테스트가 코드로 본다.
        items.append(finding("screen_diff", "medium", "human", page.get("page", ""),
                             f"[장면 누락?] {page.get('expected', '')}", [f"판단: {page.get('reason', '')}"],
                             "짝이 될 화면을 못 찾았다 — 구현 누락인지 캡처 누락인지 사람이 가른다"))
    for screen in diff.get("unmatched_screens") or []:
        items.append(finding("screen_diff", "low", "human", screen.get("screen", ""),
                             "[원문에 없는 화면] 대응하는 스토리보드 쪽이 없다", [f"판단: {screen.get('reason', '')}"],
                             "지어낸 화면인지 공통 화면인지 사람이 가른다"))
    return items


def sort_findings(items: list[dict]) -> list[dict]:
    ordered = sorted(items, key=lambda f: (OWNERS.index(f["owner"]), SEVERITY_ORDER.get(f["severity"], 9)))
    for index, item in enumerate(ordered, start=1):
        item["id"] = f"V{index:02d}"
    return ordered


def is_blocking(item: dict) -> bool:
    return item.get("severity") in BLOCKING


def asset_routes(items: list[dict]) -> list[dict]:
    """그림 단계로 보낼 목록. 경로를 못 정한 것은 **빈 경로로 남긴다** — 짐작으로 엉뚱한 그림을 굽지 않는다."""
    routes: dict[str, dict] = {}
    unresolved = []
    for item in items:
        if item["owner"] != "asset":
            continue
        path = next((e for e in item["evidence"] if e.startswith("assets/")), "")
        note = f"{item['id']} {item['issue']}"
        if not path:
            unresolved.append({"path": "", "notes": [note], "finding": item["id"]})
            continue
        routes.setdefault(path, {"path": path, "notes": [], "finding": item["id"]})["notes"].append(note)
    return list(routes.values()) + unresolved
