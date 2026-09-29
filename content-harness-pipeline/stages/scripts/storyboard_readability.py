"""스토리보드를 변환 에이전트가 "정말 읽을 수 있는지" 먼저 확인한다.

gyo6_content 의 `agent/storyboardReadability.mjs` 를 옮긴 것이다. **그쪽이 바뀌면 여기도 함께 고친다.**

왜 있는가 (gyo6_content 2026-09 실측):
  `lessons/4-1/01` 의 storyboard.pdf 는 한글 폰트에 ToUnicode CMap 이 없어 pdftotext 로 뽑으면
  한글이 0자다(전체 17,796자 중 한글 0, 공백 16,764). 페이지를 이미지로 렌더할 pdftoppm 도 없어서
  변환 에이전트는 "4-01", "[401-01]", "10000" 같은 영숫자 720자만 본 채 초안을 만들었다.
  말풍선·문제·장면 순서·레이아웃이 전부 지어낸 것이 됐고, **lesson.json 은 스키마 검증을
  통과하므로 파이프라인은 "성공"이라고 보고했다.**

이 파이프라인에는 같은 함정이 더 깊다. 여기서 지어낸 내용은 planner 를 거치지 않고 곧바로
차시가 되며, 하류의 어떤 게이트도 "원문에 있었는가"를 묻지 못한다 —
`lesson_check.check_text_preserved` 도 planner 를 기준으로 비교하므로,
planner 자체가 지어낸 것이면 그것과 일치하는 lesson.json 은 통과한다.

그래서 초안을 만들기 전에 읽기 경로가 살아 있는지 확인하고, 없으면 멈춘다.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path


HANGUL = re.compile(r"[가-힣]")

# 한글이 이만큼도 안 나오면 "텍스트 경로 없음"으로 본다.
# 한국어 스토리보드 한 장에도 이보다는 훨씬 많은 글자가 있다.
MIN_HANGUL = 40

# 추출 모드는 하나로 정하면 안 된다 — 같은 PDF 에서 결과가 완전히 갈린다.
# gyo6_content 실측(4-1/01 storyboard.pdf): -layout 은 한글 0자, -raw 는 3,888자.
# -layout 은 칸을 맞추려고 글리프를 자리로 흩는데 CID 폰트에서 그 과정에 다 날아간다.
PDFTOTEXT_MODES = (
    ("-enc", "UTF-8", "-raw"),
    ("-enc", "UTF-8"),
    ("-enc", "UTF-8", "-layout"),
)

HINT = "\n".join(
    [
        "이대로 진행하면 변환 에이전트가 스토리보드를 못 본 채 초안을 \"지어냅니다\"",
        "(말풍선·문제·장면 순서·레이아웃이 전부 원본과 달라집니다).",
        "",
        "다음 중 하나로 해결하세요:",
        "  1) poppler 설치 → pdftoppm 이 생기면 페이지를 이미지로 읽습니다 (권장, 레이아웃까지 보존)",
        "     Windows: winget install oschwartz10612.Poppler  또는  choco install poppler",
        "     macOS:   brew install poppler",
        "     Linux:   apt-get install poppler-utils",
        "  2) 스토리보드를 텍스트가 살아 있는 PDF 로 다시 내보내기 (PPT → PDF 내보내기 시 글꼴 포함)",
        "  3) 스토리보드 내용을 .md 로 옮기고 그 파일을 넘기기",
    ]
)


def has_tool(name: str) -> bool:
    try:
        subprocess.run([name, "-v"], capture_output=True, timeout=20)
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return False
    except subprocess.TimeoutExpired:
        return True
    return True


def extract_pdf_text(pdf_path: Path) -> dict | None:
    """여러 모드를 시도해 한글을 가장 많이 건진 것을 쓴다. 도구가 없거나 전부 실패하면 None."""
    if not has_tool("pdftotext"):
        return None
    best: dict | None = None
    for index, mode in enumerate(PDFTOTEXT_MODES):
        out_path = Path(tempfile.gettempdir()) / f"sb-readability-{os.getpid()}-{index}.txt"
        try:
            result = subprocess.run(
                ["pdftotext", *mode, str(pdf_path), str(out_path)],
                capture_output=True,
                timeout=180,
            )
            if result.returncode != 0 or not out_path.exists():
                continue
            text = out_path.read_text(encoding="utf-8", errors="replace")
            hangul = len(HANGUL.findall(text))
            if best is None or hangul > best["hangul"]:
                best = {"text": text, "hangul": hangul, "mode": " ".join(mode)}
        except (OSError, subprocess.TimeoutExpired):
            continue
        finally:
            try:
                out_path.unlink(missing_ok=True)
            except OSError:
                pass
    return best


def check_storyboard_readable(storyboard_path: Path) -> dict:
    """변환 에이전트가 이 파일을 실제로 읽을 수 있는지 판정한다.

    반환: {ok, via, hangul?, mode?, reason?, hint?}
      via 는 'native'(PDF 아님) | 'page-image'(pdftoppm 있음) | 'text'(본문 추출됨)
    """
    if storyboard_path.suffix.lower() != ".pdf":
        # PDF 가 아니면(.md 등) 그대로 읽힌다.
        return {"ok": True, "via": "native"}

    # 1순위 — 페이지를 이미지로 렌더할 수 있으면 에이전트가 "보고" 옮긴다.
    #          레이아웃·장면 순서까지 살아 있는 유일한 경로다.
    if has_tool("pdftoppm"):
        return {"ok": True, "via": "page-image"}

    # 2순위 — 렌더는 못 해도 본문이 뽑히면 대사·문제는 옮길 수 있다.
    best = extract_pdf_text(storyboard_path)
    hangul = best["hangul"] if best else None
    if hangul is not None and hangul >= MIN_HANGUL:
        return {"ok": True, "via": "text", "hangul": hangul, "mode": best["mode"]}

    detail = (
        "pdftotext 로 본문을 뽑지 못했습니다"
        if hangul is None
        else f"pdftotext 의 어떤 모드로도 한글이 {hangul}자뿐입니다"
        "(한글 폰트에 ToUnicode CMap 이 없는 PDF)"
    )
    return {
        "ok": False,
        "hangul": hangul or 0,
        "reason": f"스토리보드를 읽을 수 없습니다 — 페이지를 이미지로 렌더할 pdftoppm 이 없고, {detail}.",
        "hint": HINT,
    }


def pdf_page_count(pdf_path: Path) -> int | None:
    """PDF 의 **실제** 쪽수. `pdfinfo` 가 없으면 None."""
    if not has_tool("pdfinfo"):
        return None
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)], capture_output=True, timeout=60, text=True, errors="replace"
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    match = re.search(r"^Pages:\s*(\d+)", result.stdout, re.M)
    return int(match.group(1)) if match else None


# History 표의 행은 `v1.0 26/9/8 • 4학년 2학기 7차시 신규 제작 13 최건혜` 모양이다.
# 쪽수는 **공백으로 끊기는 순수 숫자 토큰 중 마지막 것**이다 — 날짜(`26/9/8`)는 슬래시가
# 붙어 있고, 내용의 수(`4학년`·`7차시`)는 한글이 붙어 있어 걸리지 않는다.
# 실측(2026-09-22) — 스토리보드 4종에서 이 규칙이 전부 맞았다.
HISTORY_ROW = re.compile(r"^\s*v\d+(?:\.\d+)*\s+.*$", re.M)


def declared_page_count(pdf_path: Path) -> int | None:
    """History 표가 **적어 둔** 쪽수. 표가 없거나 못 읽으면 None."""
    if not has_tool("pdftotext"):
        return None
    out_path = Path(tempfile.gettempdir()) / f"sb-history-{os.getpid()}.txt"
    try:
        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-raw", "-f", "1", "-l", "1", str(pdf_path), str(out_path)],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0 or not out_path.exists():
            return None
        text = out_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return None
    finally:
        try:
            out_path.unlink(missing_ok=True)
        except OSError:
            pass

    if "History" not in text:
        return None
    for row in HISTORY_ROW.findall(text):
        digits = [token for token in row.split() if token.isdigit()]
        if digits:
            return int(digits[-1])
    return None


def check_page_count(storyboard_path: Path) -> dict:
    """History 표의 쪽수와 실제 쪽수를 대조한다.

    **막지 않는다. 알리기만 한다.** 표기가 틀려도 기획 단계는 페이지 이미지를 직접 보므로
    읽기 자체는 문제없다. 위험한 것은 **사람이 그 숫자를 믿고 뒷장을 안 보는 것**이다.

    실측(2026-09-22) — History 표가 있는 스토리보드 4종 중 **3종이 실제보다 적게** 적혀 있었다.

        storyboard-4-1-2   9 / 9    맞음
        storyboard-4-2-2  13 / 15   2쪽 적게
        storyboard-4-1-1   8 / 10   2쪽 적게
        1학년 1차시        10 / 11   1쪽 적게

    1학년 1차시는 기획 단계가 알아채고 `content-plan.md` 에 적었다("History 표는 Page 10 이라고
    적혀 있으나 실제 PDF 는 11쪽이다"). 4-2-2 에서는 **작업자가 13쪽으로 믿고 넘어갔다가**
    뒤늦게 15쪽인 것을 알았다. 그래서 사람이 먼저 보도록 앞단에서 알린다.
    """
    if storyboard_path.suffix.lower() != ".pdf":
        return {"checked": False}
    actual = pdf_page_count(storyboard_path)
    if actual is None:
        return {"checked": False}
    declared = declared_page_count(storyboard_path)
    return {
        "checked": True,
        "actual": actual,
        "declared": declared,
        "mismatch": declared is not None and declared != actual,
    }


def format_page_count(result: dict) -> str:
    if not result.get("checked"):
        return ""
    actual, declared = result["actual"], result.get("declared")
    if declared is None:
        return f"쪽수: {actual}쪽 (History 표에 쪽수 표기가 없다)"
    if not result["mismatch"]:
        return f"쪽수: {actual}쪽 (History 표기와 같다)"
    more = actual - declared
    return (
        f"⚠ 쪽수가 History 표기와 다르다 — 표기 {declared}쪽, 실제 {actual}쪽"
        + (f" ({more}쪽 더 있다)" if more > 0 else f" ({-more}쪽 적다)")
        + "\n  **실제 쪽수를 기준으로 읽는다.** 표기를 믿고 뒷장을 빠뜨리면 그 장면은 만들어지지 않는다."
    )


def format_readability(result: dict) -> str:
    if not result["ok"]:
        return f"{result['reason']}\n{result['hint']}"
    via = result["via"]
    if via == "page-image":
        return "읽기 경로: page-image (pdftoppm — 레이아웃·장면 순서까지 보인다)"
    if via == "text":
        return (
            f"읽기 경로: text (한글 {result['hangul']}자, mode={result['mode']}) "
            "— 페이지 이미지가 없어 레이아웃은 못 본다. pdftoppm 설치 권장"
        )
    # 이 검사는 **글자가 뽑히는가**만 본다. "에이전트가 그 자리에 닿을 수 있는가"는 다른 축이고
    # (프로젝트 디렉토리 밖 파일은 절대 경로로도 못 읽는다), 그쪽은 `build_lesson.stage_storyboard`
    # 가 원본을 run 안으로 옮겨서 해결한다. 실측 경위는 그 함수의 주석에 있다.
    return "읽기 경로: native (PDF 가 아니므로 글자는 그대로 읽힌다)"


if __name__ == "__main__":
    # PDF 를 md 로 옮기기 **전에** 돌린다. LLM 0회.
    #     python -B -m stages.scripts.storyboard_readability "../스토리보드.pdf"
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        print("사용법: python -B -m stages.scripts.storyboard_readability <스토리보드 경로>")
        raise SystemExit(1)
    outcome = check_storyboard_readable(Path(sys.argv[1]))
    print(format_readability(outcome))
    raise SystemExit(0 if outcome["ok"] else 2)
