"""커밋 전 점검(차시 작업대 [커밋 전 점검]) — gyo6 `docs/DELIVERY_QA_CHECKLIST.md` 중 **명령으로 판정되는 항목**을 코드로 잰다.

    python -B -m stages.scripts.delivery_qa --gyo6-root <gyo6_content> --lesson 4-1/04 --out <결과.json>

사용자 결정(2026-10-01) — 체크리스트는 "코드 검사 + AI": 명령으로 정확히 되는 항목은 여기서 무료로 재고,
판단·화면이 필요한 항목은 `desk_qa.py`(클로드)가 이 결과를 받아 판정하고 고친다(2026-10-01 — 처음엔 코덱스 · 판정만이었다).

- 항목 목록은 체크리스트 md 를 읽어 만든다(`- [ ] **A1. 제목** — 설명`). 체크리스트가 바뀌면 따라간다.
- 여기서 재지 않는 항목은 `unchecked` 로 남겨 클로드에게 넘긴다.
- 차시 하나만 본다 — `dist/<학기>/<차시>/` 와 `lessons/<학기>/<차시>/`. 저장소 전체 항목(C1 등)은 base 를 본다.
- index.html 에는 공통 런타임이 인라인으로 들어 있어 그 안의 기본 경로 문자열이 많다. 그래서 그림 404(D1)는
  index.html 전체가 아니라 **이 차시 소스(lesson.json · player-ext.*)가 가리키는 그림**만 dist 에서 찾는다.

결과 한 줄: {id, title, result, observed, evidence, by: "code"}. result — pass · fail · warn · info · na · unchecked
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHECKLIST_NAMES = ("docs/DELIVERY_QA_CHECKLIST.md", "DELIVERY_QA_CHECKLIST.md")
ITEM = re.compile(r"^- \[[ xX]\] \*\*([A-F]\d+)\.\s*(.+?)\*\*\s*(?:—\s*(.*))?$")
IMAGE_SUFFIXES = (".webp", ".png", ".jpg", ".jpeg")
ASSET_REF = re.compile(r"assets/[A-Za-z0-9_./\-]+\.(?:webp|png|jpe?g|mp3|ogg|wav|json)")
URL = re.compile(r"https?://[^\s\"'<>)]+")
FONT_CDN = re.compile(r"fonts\.(?:googleapis|gstatic)\.com")
JUNK = (".map", ".bak", ".psd", ".tmp")
JUNK_NAMES = (".DS_Store", "Thumbs.db")


def checklist_path(gyo6: Path) -> Path:
    for name in CHECKLIST_NAMES:
        if (gyo6 / name).is_file():
            return gyo6 / name
    raise FileNotFoundError(f"체크리스트가 없다: {gyo6}/{CHECKLIST_NAMES[0]}")


def checklist_items(path: Path) -> list[dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ITEM.match(line.strip())
        if m:
            items.append({"id": m.group(1), "title": m.group(2).strip(), "desc": (m.group(3) or "").strip()})
    return items


def short(values, limit: int = 8) -> str:
    values = list(values)
    return ", ".join(values[:limit]) + (f" 외 {len(values) - limit}개" if len(values) > limit else "")


def is_meta_key(key: str) -> bool:
    """런타임이 안 불러오는 그림 메타 자리 — 체크리스트 D1 "artDirection 등 메타 참조는 런타임 미로드라 제외".
    실측(2026-10-01, 배포 21차시) — 남은 404 가 전부 artDirection · *.styleRef · *assetPrompt(targetAsset 포함) 였다."""
    low = key.lower()
    return low in ("artdirection", "styleref", "extraassets") or low.endswith("assetprompt")


def source_refs(lesson_src: Path) -> tuple[set[str], set[str]]:
    """이 차시 소스가 가리키는 에셋 경로 — (lesson.json 데이터 참조, player-ext.* 코드 안 문자열).

    lesson.json 은 **값 전체가 경로인 문자열만**, 메타 자리를 빼고 센다. 설명문 안에도 경로가 적혀 있어서다 —
    실측(2026-10-01, 3-1/05) "생성 당시 화풍 앵커: assets/…png — 그 원본은 정리됐다" 를 참조로 세어 404 4건을 냈다.
    player-ext.* 는 따로 돌려준다 — 옛 이름 → 새 이름 매핑의 옛 이름이나 기본값 후보처럼 안 불러오는 문자열이 섞여
    (2-2/02 · 2-2/04) 코드로는 실제 404 인지 못 가른다.
    """
    data_refs: set[str] = set()
    code_refs: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, str):
            if ASSET_REF.fullmatch(node.strip()):
                data_refs.add(node.strip())
        elif isinstance(node, dict):
            for key, value in node.items():
                if not is_meta_key(str(key)):
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    if (lesson_src / "lesson.json").is_file():
        walk(json.loads((lesson_src / "lesson.json").read_text(encoding="utf-8")))
    for name in ("player-ext.js", "player-ext.css"):
        if (lesson_src / name).is_file():
            code_refs |= set(ASSET_REF.findall((lesson_src / name).read_text(encoding="utf-8", errors="replace")))
    return data_refs, code_refs - data_refs


AUDIO_SUFFIXES = (".mp3", ".ogg", ".opus", ".wav")
FAVICON = re.compile(r"favicon|apple-touch-icon", re.I)   # 체크리스트 B3 의 "파비콘/베이스 외" — png 로 남는 것이 정상


def exists_any_suffix(folder: Path, rel: str) -> bool:
    """빌드가 확장자를 바꾸므로(그림 png→webp, 소리 wav→mp3) 같은 종류에서 stem 이 같으면 있다고 본다.
    실측(2026-10-01, 3-1/05) — 소스의 .wav 40개를 빌드가 .mp3 로 넣었는데 확장자째 찾아 전부 '없다' 고 셌다."""
    path = folder / rel
    if path.exists():
        return True
    for family in (IMAGE_SUFFIXES, AUDIO_SUFFIXES):
        if path.suffix.lower() in family:
            return any(path.with_suffix(s).exists() for s in family)
    return False


def run_checks(gyo6: Path, lesson: str, lesson_src: Path) -> dict[str, dict]:
    dist = gyo6 / "dist" / lesson
    html_path = dist / "index.html"
    if not html_path.is_file():
        raise FileNotFoundError(f"빌드 결과가 없다: {html_path} — 먼저 빌드한다")
    html = html_path.read_text(encoding="utf-8", errors="replace")
    files = sorted(p for p in dist.rglob("*") if p.is_file())
    rel = lambda p: p.relative_to(dist).as_posix()
    out: dict[str, dict] = {}

    def put(item_id: str, result: str, observed: str, evidence: list[str] | None = None) -> None:
        out[item_id] = {"result": result, "observed": observed, "evidence": evidence or []}

    # A — 자기완결성
    urls = sorted({u for u in URL.findall(html) if "w3.org" not in u})
    fonts = [u for u in urls if FONT_CDN.search(u)]
    others = [u for u in urls if not FONT_CDN.search(u)]
    if others:
        put("A1", "fail", f"외부 URL {len(others)}개: {short(others, 5)}", others[:20])
    elif fonts:
        put("A1", "warn", f"외부 URL 은 CDN 폰트 {len(fonts)}개뿐 — 온라인 배포면 정상, 오프라인 납품이면 A2 대로 임베드", fonts)
    else:
        put("A1", "pass", "외부 URL 없음(w3.org 제외)")
    font_count = len(FONT_CDN.findall(html))
    put("A2", "warn" if font_count else "pass",
        f"CDN 폰트 참조 {font_count}곳 — 오프라인 납품이면 CONTENT_EMBED_FONTS=1 로 다시 빌드" if font_count else "CDN 폰트 링크 0")
    local = sorted(set(re.findall(r"(?:localhost|127\.0\.0\.1)(?::\d+)?|[A-Za-z]:\\\\?[A-Za-z]|file://[^\s\"'<>]*", html)))
    put("A3", "warn" if local else "pass",
        f"환경 종속 경로처럼 보이는 문자열 {len(local)}종: {short(local, 5)} — 코드 주석이면 무해, 실제 href 인지 AI 가 확인" if local
        else "localhost · 127.0.0.1 · C:\\ · file:// 없음")
    put("A5", "na", "차시 하나 점검 — 납품 zip/tar 구성은 납품할 때 dist 전체로 본다")

    # B — 성능
    put("B2", "pass" if re.search(r"rel=[\"']?preload", html) else "fail",
        "head 에 rel=preload 있음" if re.search(r"rel=[\"']?preload", html) else "rel=preload 가 없다")
    raster = [rel(p) for p in files if p.suffix.lower() in (".png", ".jpg", ".jpeg") and not FAVICON.search(p.name)]
    put("B3", "fail" if raster else "pass", f"png/jpg {len(raster)}개(파비콘 제외): {short(raster)}" if raster else "그림은 전부 webp(파비콘 제외)", raster)
    wav = [rel(p) for p in files if p.suffix.lower() == ".wav"]
    mp3 = [p for p in files if p.suffix.lower() == ".mp3"]
    sizes: dict[int, list[str]] = {}
    for p in mp3:
        sizes.setdefault(p.stat().st_size, []).append(rel(p))
    dup = [names for names in sizes.values() if len(names) > 1]
    if wav:
        put("B5", "fail", f"wav {len(wav)}개: {short(wav)}", wav)
    elif dup:
        put("B5", "warn", f"크기가 같은 mp3 묶음 {len(dup)}개(같은 소리 복사일 수 있다): {short(' = '.join(d) for d in dup)}")
    else:
        put("B5", "pass", f"wav 0 · 크기가 같은 mp3 없음(mp3 {len(mp3)}개)")
    data_uris = len(re.findall(r"data:(?:image|font|audio)/", html))
    put("B6", "info", f"index.html {html_path.stat().st_size // 1024}KB · data: URI {data_uris}개 — 같은 그림의 이중 저장인지는 AI 가 본다")

    # C — 코드 품질
    player = gyo6 / "runtime" / "src" / "player.js"
    hits = [f"{i}: {line.strip()[:80]}" for i, line in enumerate(player.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if re.search(r"L\.id\s*===", line)] if player.is_file() else []
    put("C1", "fail" if hits else "pass", f"player.js 에 L.id === {len(hits)}곳" if hits else "player.js 에 L.id === 없음", hits[:10])
    css = lesson_src / "player-ext.css"
    imp = css.read_text(encoding="utf-8", errors="replace").count("!important") if css.is_file() else 0
    put("C3", "warn" if imp > 30 else "pass", f"player-ext.css 의 !important {imp}개" + (" — 30 초과, override 스태킹 신호" if imp > 30 else ""))
    debug = re.findall(r"console\.(?:log|warn|debug)|debugger", html)
    counts = {k: debug.count(k) for k in sorted(set(debug))}
    put("C5", "warn" if debug else "pass",
        f"console·debugger {len(debug)}곳 {counts} — 공통 런타임 것인지 이 차시 것인지 AI 가 가린다" if debug else "console.log/warn/debug · debugger 없음")
    lines = {name: len((lesson_src / name).read_text(encoding="utf-8", errors="replace").splitlines())
             for name in ("player-ext.js", "player-ext.css") if (lesson_src / name).is_file()}
    big = {k: v for k, v in lines.items() if v > 2000}
    put("C6", "warn" if big else "pass", f"ext 줄 수 {lines}" + (" — 2000줄 넘음(리팩터 후보, 납품 차단 아님)" if big else ""))

    # D — 에셋
    data_refs, code_refs = source_refs(lesson_src)
    missing = sorted(r for r in data_refs if not exists_any_suffix(dist, r))
    code_missing = sorted(r for r in code_refs if not exists_any_suffix(dist, r))
    if missing:
        put("D1", "fail", f"lesson.json 이 가리키는데 dist 에 없는 에셋 {len(missing)}개: {short(missing)}"
            + (f" · ext 코드 안 경로 중 없는 것 {len(code_missing)}개도 확인" if code_missing else ""), missing + code_missing)
    elif code_missing:
        put("D1", "warn", f"lesson.json 참조 {len(data_refs)}개는 모두 있음 · ext 코드 안 경로 중 dist 에 없는 것 {len(code_missing)}개: "
            f"{short(code_missing)} — 옛 이름 매핑·기본값 후보일 수 있어 실제로 불러오는지 AI 가 본다", code_missing)
    else:
        put("D1", "pass", f"소스가 가리키는 에셋 {len(data_refs) + len(code_refs)}개 모두 dist 에 있음")
    missing = missing + code_missing
    audio_missing = [r for r in missing if r.endswith((".mp3", ".ogg", ".wav"))]
    if audio_missing:
        put("D3", "fail", f"없는 오디오 {len(audio_missing)}개: {short(audio_missing)} — synth 대체인지 AI 가 확인", audio_missing)
    bad_names = [rel(p) for p in files if re.search(r"[ ]|[^\x00-\x7f]", rel(p))]
    put("D5", "fail" if bad_names else "pass", f"공백·비ASCII 파일명 {len(bad_names)}개: {short(bad_names)}" if bad_names else "파일명 위생 정상", bad_names)

    # F — 빌드 위생
    junk = [rel(p) for p in files if p.suffix.lower() in JUNK or p.name in JUNK_NAMES]
    put("F1", "fail" if junk else "pass", f"잔재 파일 {len(junk)}개: {short(junk)}" if junk else "잔재 파일 없음", junk)
    manifest = lesson_src / "manifest.json"
    meta = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    put("F2", "info", f"manifest status={meta.get('status', '(없음)')} · visibility={meta.get('visibility', '(없음)')} — 납품 목록에 넣을지 사람이 정한다")
    root_index = gyo6 / "dist" / "index.html"
    if root_index.is_file():
        linked = lesson in root_index.read_text(encoding="utf-8", errors="replace")
        # 차시 하나만 빌드(build:lesson)하면 목록 페이지는 안 바뀐다 — 새 차시가 없는 것은 실패가 아니라 전체 빌드에서 볼 것
        put("F3", "pass" if linked else "warn", f"dist/index.html 목록에 {lesson} 링크 있음" if linked
            else f"dist/index.html 목록에 {lesson} 링크 없음 — 차시만 빌드해서일 수 있다. 전체 빌드(npm run build) 뒤 목록에 뜨는지 확인")
    status = subprocess.run(["git", "-C", str(gyo6), "status", "--porcelain", "--", str(lesson_src)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    changed = [line[3:] for line in status.stdout.splitlines()] if status.returncode == 0 else []
    created = [line[3:] for line in changed if line.endswith("manifest.json")]
    put("F4", "info" if changed else "pass",
        f"커밋 안 된 변경 {len(changed)}개: {short(changed, 6)}" + (" · manifest.json 도 바뀜(created 날짜 노이즈인지 확인)" if created else "")
        if changed else "이 차시 폴더에 커밋 안 된 변경 없음", changed[:30])
    stems_in_html = html
    orphans = [rel(p) for p in files if p.parent != dist and p.stem not in stems_in_html]
    pairs = sorted({rel(p) for p in files if p.suffix.lower() == ".png" and p.with_suffix(".webp").exists()})
    if orphans or pairs:
        put("F6", "fail", f"index.html 이 안 쓰는 파일 {len(orphans)}개 · webp 와 겹친 png {len(pairs)}개: {short(orphans + pairs)}", orphans + pairs)
    else:
        put("F6", "pass", f"에셋 {len(files) - 1}개 모두 index.html 에서 쓰임 · 죽은 png 없음")
    if pairs:
        put("B4", "fail", f"webp 와 같은 이름의 png {len(pairs)}개(죽은 fallback): {short(pairs)}", pairs)
    else:
        put("B4", "pass", "webp 와 겹친 png 없음")
    external = (lesson_src / "index.html").is_file() and not (lesson_src / "lesson.json").is_file()
    if not external:
        put("F5", "na", "external 차시가 아니다(lesson.json 차시)")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="커밋 전 점검 — 체크리스트 중 코드로 재는 항목")
    parser.add_argument("--gyo6-root", type=Path, required=True)
    parser.add_argument("--lesson", required=True, help="학기/차시, 예: 4-1/04")
    parser.add_argument("--lesson-dir", type=Path, default=None, help="차시 소스 폴더. 없으면 <gyo6>/lessons/<lesson>")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    gyo6 = args.gyo6_root.resolve()
    lesson_src = (args.lesson_dir or gyo6 / "lessons" / args.lesson).resolve()
    checklist = checklist_path(gyo6)
    measured = run_checks(gyo6, args.lesson, lesson_src)
    items = []
    for item in checklist_items(checklist):
        got = measured.get(item["id"])
        items.append({**item, **(got or {"result": "unchecked", "observed": "", "evidence": []}), "by": "code" if got else ""})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"lesson": args.lesson, "checklist": str(checklist), "items": items},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tally: dict[str, int] = {}
    for item in items:
        tally[item["result"]] = tally.get(item["result"], 0) + 1
        if item["by"]:
            print(f"  {item['id']} {item['result']:<5} {item['title']} — {item['observed']}")
    print(f"코드 점검: {tally} · AI 에게 넘길 항목 {tally.get('unchecked', 0)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
