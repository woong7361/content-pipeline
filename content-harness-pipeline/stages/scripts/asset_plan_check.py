"""`design/asset-plan.json` 이 그림 규격 계약과 어긋나지 않는지 본다.

왜 필요한가 — 그림을 **계획하는** 단계는 계약서 전문을 받지 않았다. 그래서 계약서와
정반대로 지시해도 아무도 못 봤다. 실측 2026-09-23(4-1/03) — 인물 6장이 전부
`"허리 위까지만, 캔버스 아래 끝에서 허리가 잘림"` 으로 계획됐고 `"전신을 작게 그리기"` 가
금지 항목에 올라 있었다. 계약서는 정확히 그 반대를 요구한다(머리가 캔버스 높이의 0.238 인
전신, 발끝이 캔버스 아래 변에 닿음). 계획이 틀리면 굽는 단계는 충실히 틀린 그림을 굽는다.

`prompts/asset_spec_contract.md` 를 `visual_design` 에 싣는 것이 1차 방어이고, 이 검사가
2차다. 프롬프트는 안 지켜질 수 있지만 검사는 안 지켜지면 걸린다.

**게이트로 올린 것만 넣는다.** 글에서 의도를 추론하는 판정은 거짓 양성이 안 잡힌다
(`CLAUDE.md` 「게이트는 배포 차시에서 거짓 양성 0건일 때만 넣는다」). 여기 있는 것은
전부 **낱말이 있는가 / 필드가 무엇인가** 만 본다.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


# 인물 프레이밍은 **필드로** 적는다. 산문에서 낱말로 추론하지 않는다 —
# `CLAUDE.md` 「게이트는 배포 차시에서 거짓 양성 0건일 때만 넣는다」. 실제로 낱말 판정을
# 먼저 써 봤더니, `mustInclude` 의 "무대가 아래를 잘라 **가슴 위만** 보이게 한다" 라는
# **옳은 설명문**과 `forbidden` 의 "**발끝** 아래에 여백 두기" 라는 **옳은 금지문**이 둘 다 걸렸다.
# 설명문과 지시문을 낱말로 가를 방법이 없다. 그래서 값을 본다.
FULLBODY_FRAMING = "full-body"
HEAD_RATIO_MIN = 0.20
HEAD_RATIO_MAX = 0.28

TITLE_PATH = "assets/ui/title-logo.png"
SIZE_RE = re.compile(r"^\s*(\d{3,5})\s*[x×]\s*(\d{3,5})\s*$")
MD_HEADING = re.compile(r"^#{1,6}\s+(assets/\S+)\s*$", re.M)


def asset_role(path: str) -> str:
    if path.startswith("assets/backgrounds/"):
        return "background"
    if path.startswith("assets/character/") or path.startswith("assets/customers/"):
        return "character"
    return "ui"


def _lines(entry: dict, *keys: str) -> list[str]:
    out: list[str] = []
    for key in keys:
        for line in entry.get(key) or []:
            if isinstance(line, str):
                out.append(line)
    return out


def _hit(lines: list[str], words) -> str:
    for line in lines:
        low = line.lower()
        for word in words:
            if word.lower() in low:
                return line
    return ""


def _violation(kind: str, where: str, detail: str) -> dict:
    return {"kind": kind, "where": where, "detail": detail, "severity": "error"}


def check_asset_plan(plan: dict, plan_md: str = "") -> list[dict]:
    """계획 하나를 규격과 대조한다. 위반 목록을 돌려준다."""
    violations: list[dict] = []
    assets = plan.get("assets")
    if not isinstance(assets, list) or not assets:
        return [_violation("asset_plan_empty", "design/asset-plan.json", "assets 목록이 비었다")]

    seen: list[str] = []
    for entry in assets:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path.startswith("assets/"):
            violations.append(
                _violation("asset_plan_path", str(path), "path 는 assets/ 로 시작하는 문자열이어야 한다")
            )
            continue
        seen.append(path)
        role = asset_role(path)
        must_and_forbidden = _lines(entry, "mustInclude", "forbidden")

        shorthand = _hit(must_and_forbidden, ("(공통", "（공통"))
        if shorthand:
            violations.append(
                _violation(
                    "asset_plan_shorthand",
                    path,
                    "사이드카는 줄임말을 펼쳐 적는다. 줄임이 남으면 그 지시가 그림에 닿지 않는다 — "
                    + repr(shorthand),
                )
            )

        size = entry.get("size")
        matched = SIZE_RE.match(size) if isinstance(size, str) else None
        if not matched:
            violations.append(
                _violation("asset_plan_missing_size", path, "size 가 없거나 'WxH' 가 아니다: " + repr(size))
            )
        elif role == "background":
            width, height = (int(g) for g in matched.groups())
            if (width, height) != (1920, 1080):
                violations.append(
                    _violation(
                        "asset_plan_background_size",
                        path,
                        "배경은 1920x1080 이다(계약). 지금은 " + size,
                    )
                )

        transparent = entry.get("transparent")
        if role == "character" and transparent is not True:
            violations.append(
                _violation(
                    "asset_plan_character_opaque",
                    path,
                    "인물은 투명 PNG 다(계약). transparent=" + repr(transparent),
                )
            )
        if role == "background" and transparent is True:
            violations.append(
                _violation(
                    "asset_plan_background_transparent",
                    path,
                    "배경은 불투명하다(계약). 투명 배경은 화면 뒤가 비친다",
                )
            )

        if role == "character":
            framing = entry.get("framing")
            if framing != FULLBODY_FRAMING:
                violations.append(
                    _violation(
                        "asset_plan_character_framing",
                        path,
                        '인물은 전신이다. framing 을 "' + FULLBODY_FRAMING + '" 로 적는다'
                        "(지금 " + repr(framing) + "). 자르는 주체는 무대의 overflow 이고, "
                        "base 의 --char-bottom 은 전신 비례(머리 0.238)를 전제한다",
                    )
                )
            ratio = entry.get("headRatio")
            if isinstance(ratio, (int, float)) and not (HEAD_RATIO_MIN <= ratio <= HEAD_RATIO_MAX):
                violations.append(
                    _violation(
                        "asset_plan_head_ratio",
                        path,
                        "머리가 캔버스 높이에서 차지하는 비율은 "
                        + str(HEAD_RATIO_MIN) + "~" + str(HEAD_RATIO_MAX)
                        + " 다(계약 실측 0.238). 지금 " + str(ratio),
                    )
                )

        if "title" in path.rsplit("/", 1)[-1] and path != TITLE_PATH:
            violations.append(
                _violation(
                    "asset_plan_title_path",
                    path,
                    "타이틀 로고 경로는 " + TITLE_PATH + " 로 고정이다. base 가 이 경로를 하드코딩해 그린다",
                )
            )

    duplicates = sorted({p for p in seen if seen.count(p) > 1})
    for path in duplicates:
        violations.append(_violation("asset_plan_duplicate_path", path, "같은 경로가 두 번 올라왔다"))

    if plan_md:
        in_md = {m.group(1).strip() for m in MD_HEADING.finditer(plan_md)}
        if in_md:
            only_md = sorted(in_md - set(seen))
            only_json = sorted(set(seen) - in_md)
            if only_md or only_json:
                violations.append(
                    _violation(
                        "asset_plan_sidecar_mismatch",
                        "design/asset-plan.json",
                        "md 에만 있음 " + str(only_md[:5]) + " · json 에만 있음 " + str(only_json[:5]),
                    )
                )
    return violations


def check_asset_plan_file(run_dir: Path) -> list[dict]:
    """run 의 `design/asset-plan.json` 을 검사한다. 파일이 없으면 검사하지 않는다."""
    plan_path = run_dir / "design" / "asset-plan.json"
    if not plan_path.exists():
        return []
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [_violation("asset_plan_unparsable", str(plan_path), str(error))]
    md_path = run_dir / "design" / "asset-plan.md"
    plan_md = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    return check_asset_plan(plan, plan_md)


def format_asset_plan_violations(violations: list[dict]) -> str:
    return "\n".join("- [" + v["kind"] + "] " + v["where"] + " — " + v["detail"] for v in violations)


if __name__ == "__main__":  # 거짓 양성 확인용
    import sys

    for target in sys.argv[1:]:
        found = check_asset_plan_file(Path(target))
        print("== " + target + ": " + str(len(found)) + "건")
        print(format_asset_plan_violations(found))
