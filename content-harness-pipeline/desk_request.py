"""차시 작업대 [수정 요청서 올리기] — 수정 요청 PDF 를 클로드가 읽고 작업대 메모 목록으로 나눈다. 고치지 않는다.

    python -B ./desk_request.py --gyo6-root <gyo6_content> --lesson 4-1/04 --desk-dir desk/4-1-04 \
        --request-dir desk/4-1-04/requests/<작업 번호>

사용자 결정(2026-10-01) — 수정 요청은 PDF 로 온다. **차시 하나씩**, 나눈 항목은 **사람이 본 뒤** [대기열에 넣기]로 돌린다.
그 뒤 처리는 보통 메모와 같다(코드 = 클로드 · 그림·검증 = 코덱스, 병렬 · 백업 · 결과 · 보완).

- PDF 를 쪽마다 PNG 로 바꿔 둔다(`pages/page-NN.png`) — 캡처 위에 그린 표시는 글로 안 읽힌다. 메모에도 쪽 그림 경로를 붙여
  처리하는 AI 가 원본 쪽을 직접 열 수 있게 한다.
- 나누는 일은 기획에 가까워 클로드가 한다(PDF 를 직접 읽는 도구가 있다). **읽기만** 하게 수정 도구와 명령을 거부 목록으로 막는다
  (`acceptEdits` 는 파일 명령을 자동 허락하므로 허용 목록으로는 못 막는다 — CLAUDE.md 2026-10-01 실측).
- 결과는 `{request-dir}/items.json`(항목마다 include · 쪽 그림 경로를 붙여). 상태는 작업대가 `meta.json` 에 적는다.

종료 코드: 0 끝남 · 1 실패
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import usage_log  # noqa: E402
from stages.scripts.codex_client import ClaudeClient  # noqa: E402
from stages.screen_diff import render_storyboard_pages  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = PROJECT_DIR / "prompts" / "desk_request_system.md"
SCHEMA = PROJECT_DIR / "schemas" / "desk_request_output.schema.json"
# 읽기만 — 수정 도구 · 명령을 모두 거부한다(읽기 도구 Read · Grep · Glob 은 남는다)
DENIED_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit", "Bash")


def main() -> int:
    parser = argparse.ArgumentParser(description="차시 작업대 수정 요청서 나누기(클로드)")
    parser.add_argument("--gyo6-root", type=Path, required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--desk-dir", type=Path, required=True)
    parser.add_argument("--request-dir", type=Path, required=True)
    parser.add_argument("--lesson-dir", type=Path, default=None)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max", "ultra"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    args = parser.parse_args()

    gyo6 = args.gyo6_root.resolve()
    lesson_dir = (args.lesson_dir or gyo6 / "lessons" / args.lesson).resolve()
    request_dir = args.request_dir.resolve()
    pdf = request_dir / "request.pdf"
    if not pdf.is_file():
        print(f"요청서가 없다: {pdf}")
        return 1
    pages = render_storyboard_pages(pdf, request_dir / "pages")
    print(f"요청서 {pdf.name} — {len(pages)}쪽을 그림으로 바꿈")

    prompt = "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        f"LESSON: {args.lesson}\nLESSON_DIR: {lesson_dir}\nREQUEST_PDF: {pdf}",
        "PAGE_IMAGES:\n" + "\n".join(f"- {i}쪽: {p}" for i, p in enumerate(pages, 1)),
    ])
    usage_log.bind(args.desk_dir.resolve(), f"desk_request {args.lesson}", tag=os.environ.get("DESK_STEP", ""))
    client = ClaudeClient(effort=args.effort or "", claude_bin=args.claude_bin, project_dir=PROJECT_DIR,
                          timeout_seconds=args.timeout_seconds, disallowed_tools=DENIED_TOOLS,
                          add_dirs=tuple(dict.fromkeys((str(request_dir), str(lesson_dir), str(gyo6)))))
    output = request_dir / "split.json"
    output.unlink(missing_ok=True)
    client.run_prompt(prompt, SCHEMA, output, stage="desk_request", model=args.model or None)
    if not output.exists():
        print("결과 파일이 없다")
        return 1
    result = json.loads(output.read_text(encoding="utf-8"))
    by_page = {i: str(p) for i, p in enumerate(pages, 1)}
    items = [{**item, "include": True, "page_images": [by_page[n] for n in item.get("pages", []) if n in by_page]}
             for item in result.get("items", [])]
    (request_dir / "items.json").write_text(json.dumps({"headline": result.get("headline", ""), "summary": result.get("summary", ""),
                                                        "items": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for i, item in enumerate(items, 1):
        print(f"  {i}. [{item['kind']}] {item['text']}" + (f"  ❓ {item['question']}" if item.get("question") else ""))
    print(f"요약: {result.get('headline')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
