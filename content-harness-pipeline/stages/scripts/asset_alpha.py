"""투명해야 하는 asset이 실제로 투명한지 보고, 아니면 고친다.

이미지 생성기는 알파 채널을 못 낸다. "투명 배경"을 주문하면 **투명을 흉내 낸 회색 격자무늬를
픽셀로 그려서** 돌려준다. 파일은 RGB라 알파가 아예 없고, 그대로 배치하면 도장·안내판 뒤에
체커보드 사각형이 얹힌다. 실측(2026-09-09) — 4학년 1차시에서 `problem_surface`,
`place_value_table`, `stamp_correct`, `stamp_wrong` 4장이 그 상태로 빌드까지 통과했다.

이 판정은 **planner가 이미 내려놨다.** `composition_notes`/`prompt_brief`에 "투명 배경"이라고
적힌 asset이 곧 알파가 있어야 하는 asset이다. 여기서 역할을 새로 분류하지 않는다.

고치는 방법은 `tools/remove_light_checkerboard.ps1`이 하던 것과 같다 — 테두리에서 시작해
밝고 무채색인 영역만 이어서 지운다. 테두리 연결을 보는 이유는, 밝고 무채색이라는 조건만으로
지우면 캐릭터의 흰자위처럼 **안쪽에 있는 흰색까지 뚫리기 때문**이다.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


# 배경으로 볼 밝기·채도. `remove_light_checkerboard.ps1`이 쓰던 값 그대로다.
BACKGROUND_MIN_LEVEL = 218
BACKGROUND_MAX_SPREAD = 20

TRANSPARENCY_WORDS = ("투명 배경", "투명배경", "배경 투명", "transparent background")


def wants_transparency(plan_entry: dict) -> bool:
    """planner가 이 asset에 투명 배경을 지시했는지 본다."""
    text = " ".join(
        str(plan_entry.get(key) or "")
        for key in ("composition_notes", "prompt_brief", "negative_prompt")
    )
    return any(word in text for word in TRANSPARENCY_WORDS)


def has_alpha(path: Path) -> bool:
    """알파 채널이 있고 실제로 투명한 픽셀이 있는지 본다.

    모드만 보면 안 된다. RGBA로 저장했지만 전 픽셀이 불투명한 경우가 있고,
    그것은 투명 배경이 아니라 그냥 4채널 파일이다.
    """
    with Image.open(path) as image:
        if image.mode not in ("RGBA", "LA", "PA"):
            return False
        alpha = image.convert("RGBA").getchannel("A")
        return alpha.getextrema()[0] < 250


def _background_mask(image: Image.Image) -> tuple[bytearray, int, int]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    data = rgb.tobytes()
    mask = bytearray(width * height)
    for index in range(width * height):
        red = data[index * 3]
        green = data[index * 3 + 1]
        blue = data[index * 3 + 2]
        low = red if red < green else green
        if blue < low:
            low = blue
        if low < BACKGROUND_MIN_LEVEL:
            continue
        high = red if red > green else green
        if blue > high:
            high = blue
        if high - low <= BACKGROUND_MAX_SPREAD:
            mask[index] = 1
    return mask, width, height


def _outside_mask(mask: bytearray, width: int, height: int) -> bytearray:
    """테두리에 닿아 있는 배경 영역만 남긴다(scanline flood fill)."""
    seen = bytearray(width * height)
    stack: list[tuple[int, int]] = []

    def seed(x: int, y: int) -> None:
        if mask[y * width + x]:
            stack.append((x, y))

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(height):
        seed(0, y)
        seed(width - 1, y)

    while stack:
        x, y = stack.pop()
        row = y * width
        if seen[row + x] or not mask[row + x]:
            continue
        left = x
        while left > 0 and mask[row + left - 1] and not seen[row + left - 1]:
            left -= 1
        right = x
        while right + 1 < width and mask[row + right + 1] and not seen[row + right + 1]:
            right += 1
        for xx in range(left, right + 1):
            seen[row + xx] = 1
        for ny in (y - 1, y + 1):
            if 0 <= ny < height:
                nrow = ny * width
                for xx in range(left, right + 1):
                    if mask[nrow + xx] and not seen[nrow + xx]:
                        stack.append((xx, ny))
    return seen


def strip_light_background(path: Path) -> float:
    """테두리에 이어진 밝은 배경을 알파 0으로 바꾼다. 투명해진 비율을 낸다."""
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    mask, width, height = _background_mask(image)
    outside = _outside_mask(mask, width, height)
    cleared = sum(outside)
    if not cleared:
        return 0.0
    alpha = image.getchannel("A")
    alpha_data = bytearray(alpha.tobytes())
    for index in range(width * height):
        if outside[index]:
            alpha_data[index] = 0
    image.putalpha(Image.frombytes("L", (width, height), bytes(alpha_data)))
    image.save(path, format="PNG")
    return cleared / (width * height)


def resolve_asset_file(assets_dir: Path, asset_id: str, asset_output: dict | None) -> Path | None:
    """asset id로 실제 파일을 찾는다. 파일명은 하이픈, id는 밑줄인 경우가 있다."""
    if asset_output:
        for entry in asset_output.get("assets") or []:
            if entry.get("id") != asset_id:
                continue
            for key in ("path", "file", "output_path"):
                value = entry.get(key)
                if value:
                    candidate = assets_dir / Path(str(value)).name
                    if candidate.exists():
                        return candidate
    for candidate in assets_dir.glob("*.png"):
        if candidate.stem.replace("-", "_") == asset_id:
            return candidate
    return None


def check_transparency(
    planner_output: dict,
    assets_dir: Path,
    asset_output: dict | None = None,
) -> list[dict]:
    """planner가 투명을 지시한 asset이 실제로 투명한지 확정한다."""
    violations: list[dict] = []
    for entry in planner_output.get("asset_plan") or []:
        if not wants_transparency(entry):
            continue
        asset_id = str(entry.get("id") or "")
        path = resolve_asset_file(assets_dir, asset_id, asset_output)
        if path is None:
            continue
        if not has_alpha(path):
            violations.append(
                {
                    "kind": "opaque_asset",
                    "where": f"assets/{path.name}",
                    "detail": (
                        f"planner가 투명 배경을 지시했는데 알파가 없다({Image.open(path).mode}). "
                        "생성기가 투명을 격자무늬로 그려 넣은 것이다. "
                        "그대로 두면 화면에 체커보드 사각형이 얹힌다"
                    ),
                    "severity": "error",
                }
            )
    return violations


def repair_assets(
    planner_output: dict,
    assets_dir: Path,
    asset_output: dict | None = None,
) -> list[tuple[str, float]]:
    """투명해야 하는데 불투명한 asset을 고친다. 고친 목록을 낸다."""
    repaired: list[tuple[str, float]] = []
    for violation in check_transparency(planner_output, assets_dir, asset_output):
        path = assets_dir / Path(violation["where"]).name
        ratio = strip_light_background(path)
        if ratio > 0:
            repaired.append((path.name, ratio))
    return repaired


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="투명 배경 asset을 검사하고 고친다.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--fix", action="store_true", help="검사만 하지 않고 고친다")
    args = parser.parse_args()

    run_dir: Path = args.run_dir
    planner_path = next(run_dir.glob("*_planner.json"), None)
    if planner_path is None:
        print("planner.json 없음")
        return 1
    planner_output = json.loads(planner_path.read_text(encoding="utf-8"))
    asset_path = next(run_dir.glob("*_asset_generator.json"), None)
    asset_output = json.loads(asset_path.read_text(encoding="utf-8")) if asset_path else None
    assets_dir = run_dir / "output" / "assets"

    if args.fix:
        for name, ratio in repair_assets(planner_output, assets_dir, asset_output):
            print(f"  고침 {name} — {ratio * 100:.1f}% 투명해짐")

    violations = check_transparency(planner_output, assets_dir, asset_output)
    if violations:
        for item in violations:
            print(f"  {item['kind']} {item['where']} — {item['detail']}")
        return 1
    print("투명 배경 위반 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# 격자 잔여물(투명을 흉내 낸 체커보드가 불투명하게 남는 것)을 코드로 잡으려 했으나 **접었다.**
# 2026-09-10 실측 — 색만 보면 흰 접시(무채색 밝은 픽셀 16.9%)가 걸리고, 고주파 교차를 함께 봐도
# 철망 바구니(`ball-storage-4.png`)처럼 규칙적인 회색 격자가 **진짜 그림인** 경우가 걸린다.
# 배포 120장 중 30장이 걸렸으므로 축이 틀린 것이다. 게이트로 세우지 않는다.
#
# 대신 두 곳에서 막는다.
#   · `prompts/asset_render_system.md` — 둘러싸인 안쪽 배경까지 투명이어야 한다고 못 박는다
#   · `review_lesson.py` / `check_rendered.mjs` — 화면에서 사람이 본다
#
# **후광(반투명 테두리) 게이트도 같은 이유로 접었다.** 2026-09-23 실측 — 크로마를 안 쓰고
# 구운 그림에 어두운 후광이 30.5% 남은 것을 보고 "반투명 비율이 높으면 건다" 를 재 봤더니,
# 배포 인물 그림 182장 중 **27장이 15% 를 넘었다**(4-1/02 는 대부분이 60% 대다). 부드러운
# 가장자리로 그린 그림과 후광이 낀 그림을 비율로 못 가른다. 알파가 **있는가/없는가** 는
# 갈리므로(`opaque_transparent_assets`) 그것만 게이트로 둔다.


# ── 크로마키 ────────────────────────────────────────────────────────────────
# **모델에게 배경을 지우게 하지 않는다.** 실측(2026-09-10) — 모델이 스스로 키잉하다가
# 작품 안에 있는 색까지 지워 캐릭터의 청바지에 구멍이 뚫렸고, 어떤 그림은 배경 46%가
# 반투명으로 남았으며, 어떤 그림은 아예 안 지워졌다(투명 0.1%).
#
# 대신 **작품에 없는 색**을 배경으로 칠하게 하고 그 색만 코드가 지운다.
# 지울 색을 아는 상태에서 지우는 것이라 작품을 파먹을 수 없다.
CHROMA_COLORS = {
    "magenta": (255, 0, 255),
    "green": (0, 255, 0),
    "cyan": (0, 255, 255),
}


def chroma_key(path: "Path", color: str, threshold: int = 40) -> dict:
    """지정한 크로마 색을 투명으로 바꾼다.

    **밝기가 아니라 색상(hue)으로 판정한다.** 모델이 크로마 배경을 평평하게 칠하지 않고
    명암을 넣는 경우가 있어서, 절대 거리로 재면 어두운 쪽이 안 지워진다
    (실측 2026-09-10 — 아래쪽 어두운 마젠타 `(176,35,175)` 가 그대로 남았다).
    마젠타는 밝든 어둡든 **R 과 B 가 G 보다 확실히 높다** — 그 관계는 명암과 무관하다.

    지운 자리의 RGB 도 정리한다. 마젠타를 그대로 두면 런타임이 크기를 줄일 때 가장자리에
    분홍 테두리가 배어 나온다.
    """
    from PIL import Image

    if color not in CHROMA_COLORS:
        return {"keyed": False, "why": f"모르는 크로마 색: {color}"}

    with Image.open(path) as handle:
        image = handle.convert("RGBA")
    # 모델이 어중간하게 남긴 알파를 먼저 없앤다 — 크로마 위에 얹어 전부 불투명으로 만든다.
    key = CHROMA_COLORS[color]
    flat = Image.alpha_composite(Image.new("RGBA", image.size, key + (255,)), image)
    pixels = flat.load()
    width, height = flat.size
    removed = 0

    def is_chroma(red: int, green: int, blue: int) -> bool:
        if color == "magenta":
            return green + threshold < red and green + threshold < blue
        if color == "green":
            return red + threshold < green and blue + threshold < green
        return red + threshold < green and red + threshold < blue  # cyan

    for y in range(height):
        for x in range(width):
            red, green, blue, _ = pixels[x, y]
            if is_chroma(red, green, blue):
                # 색은 중립으로 눌러 둔다. 투명이어도 축소·합성에서 배어 나오기 때문이다.
                level = (red + green + blue) // 3
                pixels[x, y] = (level, level, level, 0)
                removed += 1
            elif color == "magenta" and green < min(red, blue):
                # 가장자리 번짐 — 초록을 끌어올려 분홍기를 뺀다.
                lift = min(red, blue)
                pixels[x, y] = (red, (green + lift) // 2, blue, 255)

    flat.save(path)
    total = width * height
    return {"keyed": True, "color": color, "removed_ratio": removed / total if total else 0.0}
