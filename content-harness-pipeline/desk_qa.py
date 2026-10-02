"""차시 작업대 [커밋 전 점검] — gyo6 `docs/DELIVERY_QA_CHECKLIST.md` 를 **클로드가 돌리고, 걸린 것을 차시 폴더 안에서 고친다.**

    # 점검 · 고침(클로드)
    python -B ./desk_qa.py --gyo6-root <gyo6_content> --lesson 4-1/04 --build-ref 4-1/04 --desk-dir desk/4-1-04 \
        --out-dir desk/4-1-04/qa/<작업 번호> --view-url http://127.0.0.1:8790/view/4-1-04/4-1/04/index.html --baseline <작업 전 사본>
    # 보고서(다시 빌드 · 다시 코드 점검 뒤)
    python -B ./desk_qa.py --finalize --lesson 4-1/04 --build-ref 4-1/04 --out-dir desk/4-1-04/qa/<작업 번호> ...

사용자 결정(2026-10-01) — 처음엔 "코드 검사 + 코덱스, 판정만" 이었다가 "클로드가 실행하고 클로드가 고치는 것" 으로 바꿨다
(problem.md [desk-qa-judge-only]). 작업대(`start_qa`) 순서: 백업 → 빌드 → 코드 점검(`stages.scripts.delivery_qa`, code.json) →
**이 스크립트(클로드 점검 · 고침, claude.json)** → 다시 빌드 → 다시 코드 점검(code-after.json) → `--finalize`(report.json · report.md).

- 고치는 범위는 코드 메모와 같다 — 차시 폴더 안의 무엇이든. 공통 런타임 · 빌드 설정 · 그림 다시 그리기는 고치지 않고 고칠 곳을 적는다.
- 권한: `node`(캡처 · playwright · 그림 형식 바꾸기) · 자가 검사 · `mv` · `mkdir` · `cp`. `rm` · `git` · `npm` 은 거부 목록
  (`acceptEdits` 는 파일 명령을 자동 허락하므로 거부 목록으로 막아야 한다 — CLAUDE.md 2026-10-01 실측).
- 실패하거나 멈추면 작업대가 차시 폴더 전체를 되돌린다(작업 전 백업). 끝나고 gyo6 의 차시 폴더 밖이 바뀌었으면 결과에 ⚠ 로 적는다.

종료 코드: 0 끝남(남은 실패가 있어도) · 1 실패(점검을 못 끝냄)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from desk_fix import git_changes  # noqa: E402
from stages.scripts import usage_log  # noqa: E402
from stages.scripts.codex_client import ClaudeClient  # noqa: E402
from stages.scripts.lesson_notes import now  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = PROJECT_DIR / "prompts" / "desk_qa_system.md"
SCHEMA = PROJECT_DIR / "schemas" / "desk_qa_output.schema.json"
ALLOWED_TOOLS = ("Bash(node:*)", "Bash(python -B -m stages.scripts.desk_check:*)", "Bash(mv:*)", "Bash(mkdir:*)", "Bash(cp:*)")
DENIED_TOOLS = ("Bash(rm:*)", "Bash(rmdir:*)", "Bash(del:*)", "Bash(git:*)", "Bash(npm:*)", "Bash(npx:*)")
LABEL = {"fixed": "고침", "pass": "통과", "fail": "실패", "warn": "확인 필요", "info": "참고", "na": "해당 없음", "unchecked": "못 봄"}
ORDER = {"fail": 0, "warn": 1, "unchecked": 2, "fixed": 3, "info": 4, "pass": 5, "na": 6}


def needs_ai(item: dict) -> bool:
    """클로드가 볼 항목 — 코드가 못 잰 것(unchecked)과 코드가 걸었던 것(fail · warn)."""
    return item["result"] in ("unchecked", "fail", "warn")


def merge(before: list[dict], ai_items: list[dict], after: list[dict]) -> list[dict]:
    """최종 판정. 코드로 재는 항목은 **다시 빌드한 뒤의 코드 점검**이 최종이다(클로드가 고쳤다고 해도 재보고 정한다).
    코드가 못 재는 항목은 클로드 판정. 클로드가 빠뜨린 항목은 못 봄으로 남는다."""
    ai = {i["id"]: i for i in ai_items}
    again = {i["id"]: i for i in after if i.get("by") == "code"}
    merged = []
    for item in before:
        c, a = ai.get(item["id"]), again.get(item["id"])
        # 바꾼 파일이 없으면 고친 것으로 치지 않는다 — 확인만 한 항목에도 action 을 적는 일이 있었다(Haiku, 2026-10-01)
        action = (c or {}).get("action", "") if (c or {}).get("files") or (c or {}).get("result") == "fixed" else ""
        note = f" · 클로드가 고침: {action}" if action else ""
        if a:                                    # 코드로 재는 항목
            result = a["result"]
            if item["result"] in ("fail", "warn") and result == "pass" and action:
                result = "fixed"
            elif result == "warn" and c and c["result"] in ("pass", "na", "fail"):
                result = c["result"]             # 코드가 'AI 가 확인' 으로 넘긴 경고 — 클로드 판정을 따른다
            merged.append({**item, "result": result, "before": item["result"], "observed": a["observed"] + note,
                           "evidence": a.get("evidence", []) + (c or {}).get("evidence", []),
                           "fix_hint": (c or {}).get("fix_hint", "") if result in ("fail", "warn") else "",
                           "files": (c or {}).get("files", []), "by": "code+claude" if c else "code"})
        elif c:                                  # 화면 · 판단 항목
            merged.append({**item, "result": c["result"], "before": c.get("result_before", item["result"]),
                           "observed": c["observed"] + note, "evidence": c.get("evidence", []), "fix_hint": c.get("fix_hint", ""),
                           "files": c.get("files", []), "by": "claude"})
        else:
            merged.append({**item, "before": item["result"], "fix_hint": "", "files": []})
    return merged


def write_markdown(path: Path, lesson: str, items: list[dict], headline: str, summary: str) -> None:
    tally: dict[str, int] = {}
    for item in items:
        tally[item["result"]] = tally.get(item["result"], 0) + 1
    cell = lambda s: " ".join(str(s).split()).replace("|", "\\|")
    lines = [f"# 커밋 전 점검 — {lesson}", "", f"- 시각: {now()}", f"- 요약: {headline}",
             "- " + " · ".join(f"{LABEL[k]} {v}" for k, v in sorted(tally.items(), key=lambda kv: ORDER.get(kv[0], 9))), "",
             summary.strip(), "", "| 항목 | 판정 | 전 | 누가 | 본 것 · 고친 것 | 바꾼 파일 | 남은 일 |", "|---|---|---|---|---|---|---|"]
    for item in sorted(items, key=lambda i: (ORDER.get(i["result"], 9), i["id"])):
        lines.append(f"| {item['id']} {cell(item['title'])} | {LABEL.get(item['result'], item['result'])} | "
                     f"{LABEL.get(item.get('before', ''), item.get('before', ''))} | {item.get('by') or '-'} | {cell(item['observed'])[:400]} | "
                     f"{cell(', '.join(item.get('files', [])))} | {cell(item.get('fix_hint', ''))[:200]} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize(args: argparse.Namespace) -> int:
    out_dir = args.out_dir.resolve()
    before = json.loads((out_dir / "code.json").read_text(encoding="utf-8"))["items"]
    after_path = out_dir / "code-after.json"
    after = json.loads(after_path.read_text(encoding="utf-8"))["items"] if after_path.exists() else []
    ai = json.loads((out_dir / "claude.json").read_text(encoding="utf-8")) if (out_dir / "claude.json").exists() else {}
    items = merge(before, ai.get("items", []), after)
    tally: dict[str, int] = {}
    for item in items:
        tally[item["result"]] = tally.get(item["result"], 0) + 1
    fails = [i for i in items if i["result"] == "fail"]
    warns = [i for i in items if i["result"] in ("warn", "unchecked")]
    fixed = tally.get("fixed", 0)
    lead = f"고침 {fixed} · " if fixed else ""
    if fails:
        headline = f"{lead}남은 실패 {len(fails)} — " + " · ".join(i["title"] for i in fails[:2]) + (" 외" if len(fails) > 2 else "")
    elif warns:
        headline = f"{lead}막는 것 없음 · 확인 필요 {len(warns)}"
    else:
        headline = f"{lead}통과 — 막는 것 없음"
    summary = " ".join(part for part in (ai.get("headline", ""), ai.get("summary", "")) if part)
    report = {"lesson": args.lesson, "at": now(), "job": os.environ.get("DESK_STEP", ""), "headline": headline,
              "summary": summary, "counts": tally, "items": items}
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(out_dir / "report.md", args.lesson, items, headline, summary)
    for item in items:
        if item["result"] in ("fixed", "fail", "warn", "unchecked"):
            print(f"  {item['id']} {LABEL[item['result']]} — {item['title']}: {item['observed'][:160]}")
    print(f"요약: {headline} · {tally}")
    return 0


def run(args: argparse.Namespace) -> int:
    gyo6 = args.gyo6_root.resolve()
    lesson_dir = (args.lesson_dir or gyo6 / "lessons" / args.build_ref).resolve()
    desk_dir, out_dir = args.desk_dir.resolve(), args.out_dir.resolve()
    code = json.loads((out_dir / "code.json").read_text(encoding="utf-8"))
    todo = [i for i in code["items"] if needs_ai(i)]
    print(f"커밋 전 점검(클로드): {args.lesson} · 볼 항목 {len(todo)}개 — {', '.join(i['id'] for i in todo)}")
    if not todo:
        (out_dir / "claude.json").write_text(json.dumps({"items": [], "headline": "", "summary": ""}), encoding="utf-8")
        return 0
    removed_dir = desk_dir / "removed" / (os.environ.get("DESK_STEP") or "qa")
    self_check = (f'python -B -m stages.scripts.desk_check "{lesson_dir}" --baseline "{args.baseline.resolve()}" '
                  f'--gyo6-root "{gyo6}"')
    prompt = "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {args.build_ref}\nLESSON_DIR: {lesson_dir}\nDIST_DIR: {gyo6 / 'dist' / args.build_ref}\nGYO6_ROOT: {gyo6}\n"
        f"VIEW_URL: {args.view_url}\nOUT_DIR: {out_dir}\nREMOVED_DIR: {removed_dir}\nCHECKLIST: {code['checklist']}\n"
        f"CODE_RESULTS: {out_dir / 'code.json'}",
        "## 이번에 볼 항목\n\n" + "\n".join(f"- {i['id']} [{i['result']}] {i['title']} — {i['desc']}"
                                         + (f"\n  (코드가 본 것: {i['observed']})" if i.get("observed") else "") for i in todo),
        f"SELF_CHECK:\n{self_check}",
    ])
    usage_log.bind(desk_dir, f"desk_qa {args.lesson}", tag=os.environ.get("DESK_STEP", ""))
    client = ClaudeClient(effort=args.effort or "", claude_bin=args.claude_bin, project_dir=PROJECT_DIR,
                          timeout_seconds=args.timeout_seconds, allowed_tools=ALLOWED_TOOLS, disallowed_tools=DENIED_TOOLS,
                          add_dirs=tuple(dict.fromkeys((str(gyo6), str(lesson_dir), str(desk_dir)))))
    output = out_dir / "claude.json"
    output.unlink(missing_ok=True)
    before = git_changes(gyo6)
    client.run_prompt(prompt, SCHEMA, output, stage="desk_qa", model=args.model or None)
    if not output.exists():
        print("클로드 결과 파일이 없다")
        return 1
    result = json.loads(output.read_text(encoding="utf-8"))
    after = git_changes(gyo6)
    if before is not None and after is not None:
        try:
            inside = lesson_dir.relative_to(gyo6).as_posix() + "/"
        except ValueError:
            inside = None
        outside = sorted(p for p in after - before if not (inside and p.startswith(inside)) and not p.startswith("dist/"))
        if outside:
            warn = f"⚠ 차시 폴더 밖 gyo6 파일이 바뀌었다(이 점검 또는 그사이 다른 손): {', '.join(outside[:10])}"
            print(warn)
            result["summary"] = f"{result.get('summary', '')} {warn}".strip()
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in result.get("items", []):
        print(f"  {item['id']} {item.get('result_before')} → {item['result']}" + (f" · 고침: {item['action']}" if item.get("action") else ""))
    print(f"클로드: {result.get('headline')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 커밋 전 점검(클로드 — 점검 · 고침)")
    parser.add_argument("--finalize", action="store_true", help="다시 빌드 · 다시 코드 점검 뒤 보고서를 만든다")
    parser.add_argument("--gyo6-root", type=Path)
    parser.add_argument("--lesson", required=True, help="작업대 차시(4-1/04)")
    parser.add_argument("--build-ref", required=True, help="dist 안 경로(학기/차시)")
    parser.add_argument("--desk-dir", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--view-url", default="")
    parser.add_argument("--baseline", type=Path, help="작업 전 차시 폴더 사본(자가 검사 기준)")
    parser.add_argument("--lesson-dir", type=Path, default=None)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max", "ultra"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()
    if args.finalize:
        return finalize(args)
    if not (args.gyo6_root and args.desk_dir and args.baseline):
        parser.error("점검에는 --gyo6-root · --desk-dir · --baseline 이 필요하다")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
