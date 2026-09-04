"""캡처한 스크린샷을 WebP로 압축해 저장한다.

Playwright는 png/jpeg만 직접 쓸 수 있어서, 캡처를 메모리로 받아 여기서 다시 인코딩한다.
전체 페이지 캡처는 PNG로 두면 장당 2MB에 달하고, 그대로 리뷰 단계 입력으로 들어간다.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any


# WebP 컨테이너가 한 변에 담을 수 있는 최대 픽셀. 넘으면 인코딩 자체가 실패한다.
WEBP_MAX_DIMENSION = 16383
DEFAULT_QUALITY = 80
QUALITY_ENV = "SCREENSHOT_WEBP_QUALITY"


def resolve_quality(quality: int | None = None) -> int:
    if quality is not None:
        return quality
    raw = os.environ.get(QUALITY_ENV, "").strip()
    if not raw.isdigit():
        return DEFAULT_QUALITY
    return max(1, min(100, int(raw)))


def capture_screenshot(
    *,
    page: Any,
    dest_dir: Path,
    filename_stem: str,
    full_page: bool = True,
    quality: int | None = None,
) -> Path:
    """페이지를 캡처해 압축 저장하고, 실제로 쓰인 파일 경로를 돌려준다."""
    png_bytes = page.screenshot(full_page=full_page)
    return write_compressed(png_bytes, dest_dir / filename_stem, quality=quality)


def write_compressed(png_bytes: bytes, dest_stem: Path, *, quality: int | None = None) -> Path:
    """PNG 바이트를 WebP로 저장한다. 압축할 수 없으면 PNG 그대로 남긴다."""
    dest_stem.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ModuleNotFoundError:
        # 압축은 부가 기능이다. Pillow가 없다고 캡처 자체를 실패시키지 않는다.
        return _write_png(png_bytes, dest_stem)

    try:
        with Image.open(io.BytesIO(png_bytes)) as image:
            image = _fit_webp_limit(image, Image)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            dest = dest_stem.with_suffix(".webp")
            image.save(dest, format="WEBP", quality=resolve_quality(quality), method=6)
    except OSError:
        return _write_png(png_bytes, dest_stem)

    _remove_stale(dest_stem.with_suffix(".png"))
    return dest


def _fit_webp_limit(image: Any, Image: Any) -> Any:
    width, height = image.size
    longest = max(width, height)
    if longest <= WEBP_MAX_DIMENSION:
        return image
    ratio = WEBP_MAX_DIMENSION / longest
    return image.resize((max(1, int(width * ratio)), max(1, int(height * ratio))), Image.LANCZOS)


def _write_png(png_bytes: bytes, dest_stem: Path) -> Path:
    dest = dest_stem.with_suffix(".png")
    dest.write_bytes(png_bytes)
    _remove_stale(dest_stem.with_suffix(".webp"))
    return dest


def _remove_stale(path: Path) -> None:
    """같은 이름의 이전 포맷 파일이 남아 리뷰 입력에 섞이지 않게 지운다."""
    if path.exists():
        path.unlink()
