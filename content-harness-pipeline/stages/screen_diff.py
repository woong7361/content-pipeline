"""스토리보드 예시화면과 완성 화면을 쪽 단위로 대조한다.

`lesson_review` 와 축이 다르다.

    lesson_review   화면 **자체**가 멀쩡한가 — 진행 불능, 누락, 가독성
    screen_diff     화면이 **기획된 그림처럼 보이는가** — 배치·비례·색·글자

이 층이 없었다. `tools/check_rendered.mjs` 는 스토리보드를 받지 않아 볼 수가 없고,
`stages/lesson_review.py` 는 스토리보드를 `STORYBOARD_MARKDOWN` **글로만** 넘긴다 —
원본 PDF 왼쪽 절반을 차지하는 **예시화면 그림이 프롬프트에 실리지 않는다.**
그래서 이 파이프라인은 "완성 화면이 기획된 화면처럼 보이는가"를 한 번도 묻지 않았고,
레이아웃·비례·글자 크기가 어긋나도 사람이 눈으로 볼 때만 드러났다(problem.md
`[screen-not-matched-to-storyboard-mockup]`).

그림을 봐야 하므로 provider 는 codex 로 고정한다. `asset_render` 가 codex 고정인 것과 같은 이유다.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from stages.scripts.codex_client import PROVIDER_CODEX, create_prompt_client

PROJECT_DIR = Path(__file__).resolve().parent.parent
SCREEN_DIFF_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "screen_diff_system.md"
SCREEN_DIFF_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "screen_diff_output.schema.json"
SCREEN_FIX_SYSTEM_PROMPT = PROJECT_DIR / "prompts" / "screen_fix_system.md"
SCREEN_FIX_OUTPUT_SCHEMA = PROJECT_DIR / "schemas" / "screen_fix_output.schema.json"

# 수정안을 만들려면 실제 소스를 봐야 한다. 경로만 넘기고 모델이 직접 연다 —
# 본문을 프롬프트에 싣지 않는 이유는 `lesson.json` 이 12만 바이트라 대조할 그림 자리를 먹기 때문이다.
FIX_SOURCE_FILES = ("lesson.json", "player-ext.css", "player-ext.js")
BUNDLED_POPPLER_BIN = PROJECT_DIR / "tools" / "poppler" / "poppler-26.07.0" / "Library" / "bin"

# 쪽 이미지 가로 픽셀. 예시화면 안의 말풍선 글자까지 읽혀야 하므로 넉넉히 준다.
PAGE_WIDTH_PX = 1600


def find_pdftoppm() -> str | None:
    """번들된 poppler 를 먼저 쓰고, 없으면 PATH 를 본다.

    PATH 에만 기대면 셸마다 결과가 달라진다 — 이 레포는 `tools/poppler` 를 함께 들고 있으므로
    그쪽을 1순위로 본다.
    """
    for name in ("pdftoppm.exe", "pdftoppm"):
        bundled = BUNDLED_POPPLER_BIN / name
        if bundled.exists():
            return str(bundled)
    return shutil.which("pdftoppm")


def render_storyboard_pages(storyboard_path: Path, out_dir: Path, pages: str | None = None) -> list[Path]:
    """스토리보드 PDF 쪽을 PNG 로 렌더한다. PDF 가 아니면 빈 목록이다.

    `pages` 는 `5-7` 같은 범위다. 없으면 전부 렌더한다.
    """
    if storyboard_path.suffix.lower() != ".pdf":
        return []
    tool = find_pdftoppm()
    if not tool:
        raise FileNotFoundError(
            "pdftoppm 을 찾지 못했다. 스토리보드 쪽을 이미지로 못 만들면 대조할 수 없다.\n"
            f"  번들 경로: {BUNDLED_POPPLER_BIN}"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [tool, "-png", "-r", "0", "-scale-to-x", str(PAGE_WIDTH_PX), "-scale-to-y", "-1"]
    if pages:
        first, _, last = pages.partition("-")
        command += ["-f", first, "-l", last or first]
    command += [str(storyboard_path), str(out_dir / "page")]

    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm 실패: {result.stderr.strip()[:400]}")
    return sorted(out_dir.glob("page-*.png"))


def diff_screens(
    capture_dir: Path,
    page_dir: Path,
    lesson_path: Path,
    output_path: Path,
    storyboard_text: str = "",
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    model: str | None = None,
    timeout_seconds: int = 1800,
) -> dict | None:
    prompt = build_prompt(
        capture_dir=capture_dir,
        page_dir=page_dir,
        lesson_path=lesson_path,
        storyboard_text=storyboard_text,
    )
    client = create_prompt_client(
        # 그림을 여는 도구가 codex 쪽에만 있다. 사용자가 claude 를 골라도 여기는 codex 다 —
        # 안 그러면 경로만 읽고 "봤다"고 답하는 대조가 된다.
        provider=PROVIDER_CODEX,
        codex_bin=codex_bin,
        claude_bin=claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=SCREEN_DIFF_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
        stage="screen_diff",
    )


def build_prompt(
    capture_dir: Path,
    page_dir: Path,
    lesson_path: Path,
    storyboard_text: str = "",
) -> str:
    system_prompt = SCREEN_DIFF_SYSTEM_PROMPT.read_text(encoding="utf-8")
    capture = json.loads((capture_dir / "capture.json").read_text(encoding="utf-8"))

    screens = [
        {
            "file": shot.get("file", ""),
            "absolute_path": str((capture_dir / shot["file"]).resolve()),
            "clicked": shot.get("clicked", ""),
            "stage_text": shot.get("stage_text", ""),
        }
        for shot in capture.get("shots", [])
        if isinstance(shot, dict) and shot.get("file")
    ]
    pages = [
        {"file": page.name, "absolute_path": str(page.resolve())}
        for page in sorted(page_dir.glob("page-*.png"))
    ]

    stuck_note = ""
    if capture.get("stuck"):
        stuck_note = (
            "\n**주의: 진행이 멈췄습니다.** 같은 화면이 반복돼 캡처를 중단했습니다. "
            "뒤쪽 화면은 찍히지 않았으므로, 짝을 못 찾은 쪽을 `unmatched_pages` 에 넣되 "
            "`reason` 에 '캡처가 거기까지 못 갔다'고 적습니다. 구현 누락으로 단정하지 않습니다.\n"
        )

    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    lesson_view = {
        "title": lesson.get("title", ""),
        "artDirection": lesson.get("artDirection", {}),
        "cast": {
            key: {"position": value.get("position"), "assetRef": value.get("assetRef")}
            for key, value in (lesson.get("cast") or {}).items()
            if isinstance(value, dict)
        },
        "steps": [
            {
                "id": step.get("id", ""),
                "type": step.get("type", ""),
                "backgroundRef": step.get("backgroundRef", ""),
                "cuts": len(step.get("stageDirections") or []),
                "rounds": len(step.get("rounds") or []),
            }
            for step in lesson.get("steps") or []
            if isinstance(step, dict)
        ],
    }

    return f"""{system_prompt}
{stuck_note}
STORYBOARD_PAGES (예시화면. 먼저 연다):
{json.dumps(pages, ensure_ascii=False, indent=2)}

SCREENS (완성 화면):
{json.dumps(screens, ensure_ascii=False, indent=2)}

LESSON_VIEW (어느 파일을 고칠지 정하는 데 쓴다):
{json.dumps(lesson_view, ensure_ascii=False, indent=2)}

STORYBOARD_TEXT (그림이 무엇인지 읽는 보조 자료. 대조 대상이 아니다):
{storyboard_text}
"""


def plan_fixes(
    diff_path: Path,
    capture_dir: Path,
    page_dir: Path,
    lesson_dir: Path,
    output_path: Path,
    codex_bin: str = "codex",
    claude_bin: str = "claude",
    model: str | None = None,
    timeout_seconds: int = 1800,
) -> dict | None:
    """대조 결과를 **그대로 적용할 수 있는 수정안**으로 내린다.

    1차 대조는 "무엇이 다른가"까지만 낸다 — `약 65~70% 로 줄인다` 는 그대로 못 고친다.
    여기서는 같은 그림을 다시 보되 **실제 소스까지 열어** 앵커·현재 값·바꿀 값을 확정한다.
    1차 결과를 재사용하므로 대조를 다시 돌리지 않는다.
    """
    prompt = build_fix_prompt(
        diff_path=diff_path,
        capture_dir=capture_dir,
        page_dir=page_dir,
        lesson_dir=lesson_dir,
    )
    client = create_prompt_client(
        provider=PROVIDER_CODEX,
        codex_bin=codex_bin,
        claude_bin=claude_bin,
        project_dir=PROJECT_DIR,
        timeout_seconds=timeout_seconds,
    )
    return client.run_prompt(
        prompt=prompt,
        output_schema=SCREEN_FIX_OUTPUT_SCHEMA,
        output_path=output_path,
        model=model,
        stage="screen_fix",
    )


def build_fix_prompt(diff_path: Path, capture_dir: Path, page_dir: Path, lesson_dir: Path) -> str:
    system_prompt = SCREEN_FIX_SYSTEM_PROMPT.read_text(encoding="utf-8")
    diff = json.loads(diff_path.read_text(encoding="utf-8"))

    capture = json.loads((capture_dir / "capture.json").read_text(encoding="utf-8"))
    screens = [
        {"file": shot["file"], "absolute_path": str((capture_dir / shot["file"]).resolve())}
        for shot in capture.get("shots", [])
        if isinstance(shot, dict) and shot.get("file")
    ]
    pages = [
        {"file": page.name, "absolute_path": str(page.resolve())}
        for page in sorted(page_dir.glob("page-*.png"))
    ]
    sources = [
        {
            "file": f"lesson/{name}",
            "absolute_path": str((lesson_dir / name).resolve()),
            "bytes": (lesson_dir / name).stat().st_size,
        }
        for name in FIX_SOURCE_FILES
        if (lesson_dir / name).exists()
    ]

    return f"""{system_prompt}

CHANGES (앞 단계가 낸 대조 결과. 이것을 수정안으로 내린다):
{json.dumps(diff.get("changes") or [], ensure_ascii=False, indent=2)}

UNMATCHED_PAGES (짝이 될 화면을 못 찾은 쪽. 장면 누락일 수 있다):
{json.dumps(diff.get("unmatched_pages") or [], ensure_ascii=False, indent=2)}

SOURCE_FILES (**반드시 연다.** `current` 는 여기서 그대로 옮긴다):
{json.dumps(sources, ensure_ascii=False, indent=2)}

STORYBOARD_PAGES (목표 값을 여기서 잰다):
{json.dumps(pages, ensure_ascii=False, indent=2)}

SCREENS (현재 값을 여기서 잰다):
{json.dumps(screens, ensure_ascii=False, indent=2)}
"""


def format_fixes(report: dict) -> str:
    fixes = {fix.get("id"): fix for fix in report.get("fixes") or []}
    ordered = [fixes[i] for i in report.get("order") or [] if i in fixes]
    ordered += [f for f in fixes.values() if f not in ordered]
    lines = [
        f"{report.get('status', '?')} · 수정안 {len(fixes)}건 · "
        f"사람이 정할 것 {len(report.get('needs_decision') or [])}건"
    ]
    for fix in ordered:
        lines.append(f"  [{fix.get('priority', '?')}] {fix.get('id', '?')} · {fix.get('file', '?')} · {fix.get('anchor', '?')}")
        lines.append(f"      현재: {(fix.get('current') or '(없음)').strip()[:110]}")
        lines.append(f"      변경: {(fix.get('replacement') or '').strip()[:110]}")
        lines.append(f"      근거: {(fix.get('why_this_value') or '').strip()[:110]}")
    for item in report.get("needs_decision") or []:
        lines.append(f"  [결정 필요] {item.get('question', '')}")
        for option in item.get("options") or []:
            lines.append(f"      · {option}")
    if report.get("notes"):
        lines.append(f"  메모: {report['notes']}")
    return "\n".join(lines)


def write_fix_markdown(report: dict, path: Path) -> None:
    fixes = {fix.get("id"): fix for fix in report.get("fixes") or []}
    ordered = [fixes[i] for i in report.get("order") or [] if i in fixes]
    ordered += [f for f in fixes.values() if f not in ordered]

    lines = [
        "# 화면 대조 — 수정안",
        "",
        "대조 결과를 그대로 적용할 수 있는 형태로 내린 것이다. **위에서부터 순서대로** 적용한다.",
        "",
        f"- 상태: `{report.get('status', '?')}`",
        f"- 수정안: {len(fixes)}건",
        f"- 사람이 정할 것: {len(report.get('needs_decision') or [])}건",
        "",
    ]
    for index, fix in enumerate(ordered, start=1):
        lines += [
            f"## {index}. `{fix.get('id', '')}` — {fix.get('file', '')}",
            "",
            f"- 우선순위: **{fix.get('priority', '')}**",
            f"- 근거 항목: {fix.get('from_change', '')}",
            f"- 자리: `{fix.get('anchor', '')}`",
            "",
            "현재",
            "",
            "```",
            (fix.get("current") or "(없음 — 새로 추가한다)").rstrip(),
            "```",
            "",
            "변경",
            "",
            "```",
            (fix.get("replacement") or "").rstrip(),
            "```",
            "",
            f"**왜 이 값인가** — {fix.get('why_this_value', '')}",
            "",
            f"**확인** — {fix.get('verify', '')}",
            "",
            f"**딸려 틀어질 수 있는 것** — {fix.get('risk', '')}",
            "",
        ]

    decisions = report.get("needs_decision") or []
    if decisions:
        lines += ["## 사람이 정해야 하는 것", ""]
        for item in decisions:
            lines.append(f"### {item.get('question', '')}")
            lines.append("")
            lines.append(f"- 근거 항목: {item.get('from_change', '')}")
            lines.append(f"- 왜 여기서 못 정하는가: {item.get('why_cannot_decide', '')}")
            for option in item.get("options") or []:
                lines.append(f"  - {option}")
            lines.append("")

    if report.get("notes"):
        lines += ["## 메모", "", report["notes"], ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_diff(report: dict) -> str:
    changes = report.get("changes") or []
    order = {"high": 0, "medium": 1, "low": 2}
    lines = [
        f"{report.get('status', '?')} · 짝지은 쌍 {report.get('pairs_compared', 0)} · "
        f"고칠 것 {len(changes)}건 · 짝 못 찾은 쪽 {len(report.get('unmatched_pages') or [])}"
    ]
    for item in sorted(changes, key=lambda c: order.get(c.get("priority"), 9)):
        lines.append(
            f"  [{item.get('priority', '?')}] {item.get('aspect', '?')} "
            f"· {item.get('target_file', '?')} · {item.get('screen', '?')} ← {item.get('page', '?')}"
        )
        lines.append(f"      기획: {item.get('storyboard_shows', '')}")
        lines.append(f"      화면: {item.get('screen_shows', '')}")
        lines.append(f"      → {item.get('change', '')}")
    for miss in report.get("unmatched_pages") or []:
        lines.append(f"  [짝없음] {miss.get('page', '')} — {miss.get('expected', '')} ({miss.get('reason', '')})")
    if report.get("notes"):
        lines.append(f"  메모: {report['notes']}")
    return "\n".join(lines)


def write_markdown(report: dict, path: Path) -> None:
    """사람이 읽고 그대로 고칠 수 있는 목록. run 디렉토리에 남는 것은 이쪽이다."""
    order = {"high": 0, "medium": 1, "low": 2}
    changes = sorted(report.get("changes") or [], key=lambda c: order.get(c.get("priority"), 9))
    lines = [
        "# 화면 대조 — 고칠 것",
        "",
        "스토리보드 예시화면과 완성 화면을 쪽 단위로 대조한 결과다. 판정이 아니라 고칠 것 목록이다.",
        "",
        f"- 상태: `{report.get('status', '?')}`",
        f"- 짝지은 쌍: {report.get('pairs_compared', 0)}",
        f"- 고칠 것: {len(changes)}건",
        "",
    ]
    if changes:
        lines += ["## 고칠 것", "", "| 우선 | 축 | 고칠 파일 | 화면 | 기획 | 화면 | 바꿀 것 |", "|---|---|---|---|---|---|---|"]
        for item in changes:
            cells = [
                item.get("priority", ""),
                item.get("aspect", ""),
                f"`{item.get('target_file', '')}`",
                item.get("screen", ""),
                item.get("storyboard_shows", "").replace("|", "\\|"),
                item.get("screen_shows", "").replace("|", "\\|"),
                item.get("change", "").replace("|", "\\|"),
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    unmatched = report.get("unmatched_pages") or []
    if unmatched:
        lines += ["## 짝이 될 화면을 못 찾은 스토리보드 쪽", "",
                  "**그 장면이 구현되지 않았다는 뜻일 수 있다.**", ""]
        for miss in unmatched:
            lines.append(f"- `{miss.get('page', '')}` — {miss.get('expected', '')} ({miss.get('reason', '')})")
        lines.append("")

    extra = report.get("unmatched_screens") or []
    if extra:
        lines += ["## 대응하는 스토리보드 쪽이 없는 화면", ""]
        for item in extra:
            lines.append(f"- `{item.get('screen', '')}` — {item.get('reason', '')}")
        lines.append("")

    if report.get("notes"):
        lines += ["## 메모", "", report["notes"], ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
