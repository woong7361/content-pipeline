"""lesson 번들을 gyo6_content 의 lessons/{슬롯}/{id}/ 로 배치한다 (LLM 0회).

    python -B ./install_lesson.py runs/{run_id} --target ../gyo6_content --lesson 2-2/03
    python -B ./install_lesson.py runs/{run_id} --target ../gyo6_content --lesson 2-2/03 --dry-run

`build_lesson.py` 가 만든 것을 옮기기만 한다. **만들지 않는다.** 남의 git 을 건드리는 일과
산출물을 만드는 일을 한 스크립트에 두면 어느 쪽이 실패했는지 사후에 갈라내지 못한다.

여기서 확정하는 것 셋.

  · production 잠금 차시를 덮지 않는다. gyo6_content 의 규칙이고, 어기면 완성된 차시가 날아간다.
  · lesson.json 이 참조하는 이미지가 **전부 실제로 놓였는지** 본다. 빠진 것이 있으면
    gyo6_content 의 빌드가 그 자리를 "생성해야 할 에셋"으로 보고 codex image_gen 을 부른다.
  · 계획은 늘 .png 로 적히는데 산출물은 .webp 일 수 있다. 확장자가 어긋나면 실제 확장자로 놓고
    lesson.json 의 참조를 그 이름으로 함께 고친다.

종료 코드
  0  배치했다
  2  배치하지 않았다(잠금·충돌·참조 누락)
  1  실행 자체가 실패했다
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from stages.scripts import install_record
from stages.scripts.atom_registry import describe, load_atom_registry
from stages.scripts.lesson_check import check_atoms, check_top_level, errors_only, format_violations
from stages.scripts.lesson_manifest import build_manifest, collect_sizes

# Windows 콘솔 기본 인코딩(cp949)은 이 파이프라인이 쓰는 문장 부호를 못 실어 print에서 죽는다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REJECTED_EXIT = 2
ASSET_SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")

# base 런타임이 **경로를 하드코딩해서** 그리는 에셋. `renderIntroStart` 가
# `<img src="assets/ui/title-logo.png">` 를 그대로 박는다(`runtime/src/player.js:1510`).
# 하드코딩된 에셋 경로는 런타임 전체에서 이 한 곳뿐이고, 배포된 18차시가 **예외 없이** 이 이름이다.
#
# 그래서 이 자리만은 확장자를 실제 파일에 맞추면 안 된다 — 우리 에셋 생성기는 webp 로 압축하고
# 배치 코드는 보통 실제 확장자에 맞춰 이름과 참조를 함께 고치는데, 그렇게 하면 이름이 어긋나
# **타이틀 화면에 깨진 그림이 뜬다.** 어느 데이터 게이트도 이걸 못 본다(lesson.json 안에서는
# 참조와 파일이 일치하기 때문이다). 이름을 지키고 파일을 PNG 로 바꿔서 놓는다.
FIXED_NAME_ASSETS = {"assets/ui/title-logo.png"}
ASSET_REF_PATTERN = re.compile(r"^assets/[A-Za-z0-9_\-/]+\.(?:png|jpe?g|webp)$", re.IGNORECASE)
LESSON_REF_PATTERN = re.compile(r"^\d+-\d+/[A-Za-z0-9_-]+$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a lesson bundle into gyo6_content.")
    parser.add_argument("run_dir", type=Path, help="runs/{run_id}")
    parser.add_argument("--target", type=Path, required=True, help="gyo6_content 프로젝트 루트")
    parser.add_argument("--lesson", required=True, help="배치할 자리. 예: 2-2/03")
    parser.add_argument("--overwrite", action="store_true", help="이미 있는 차시를 덮어쓴다")
    parser.add_argument("--dry-run", action="store_true", help="무엇을 할지만 출력하고 쓰지 않는다")
    parser.add_argument(
        "--discard-target-changes",
        action="store_true",
        help="배치 뒤 gyo6_content 쪽에서 고친 파일이 있어도 run 것으로 덮는다. 목록을 보고 버려도 될 때만 쓴다",
    )
    args = parser.parse_args()

    if not LESSON_REF_PATTERN.match(args.lesson):
        print(f"--lesson 형식이 아니다(예: 2-2/03): {args.lesson}", file=sys.stderr)
        return 1

    run_dir = args.run_dir.resolve()
    target_root = args.target.resolve()
    lesson_dir = run_dir / "lesson"
    source_lesson = lesson_dir / "lesson.json"

    if not source_lesson.exists():
        print(f"lesson 번들이 없다. 먼저 build_lesson.py 를 돌린다: {source_lesson}", file=sys.stderr)
        return 1
    if not (target_root / "lessons").is_dir():
        print(f"gyo6_content 로 보이지 않는다(lessons/ 없음): {target_root}", file=sys.stderr)
        return 1

    try:
        builder_output, origin = load_builder_output(run_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if origin == "storyboard":
        baked = sorted(p for p in (lesson_dir / "assets").rglob("*") if p.is_file())
        if baked:
            print(f"번들이 그림 {len(baked)}장을 들고 있다 — lesson/assets/ 를 통째로 옮긴다")
        else:
            print(
                "번들에 그림이 없다 — manifest 의 auto-generate 로 올라가고\n"
                "  그쪽 npm run build:lesson 의 imagegen 이 생성한다"
            )

    slot, lesson_id = args.lesson.split("/")
    dest_dir = target_root / "lessons" / slot / lesson_id

    blockers = check_destination(dest_dir, target_root, args.lesson, args.overwrite)
    if blockers:
        print(f"막힌 것 {len(blockers)}건")
        for line in blockers:
            print(f"  · {line}")
        print("\n배치하지 않았다.")
        return REJECTED_EXIT

    lesson = json.loads(source_lesson.read_text(encoding="utf-8"))
    lesson, id_fixes = align_identifiers(lesson, slot, lesson_id)
    for field, (old, new) in id_fixes.items():
        print(f"  {field}: {old!r} → {new!r}  (배치 위치에서 유도)")

    # 대상 레포가 여기 있으므로 **그쪽 런타임을 기준으로** 다시 본다. emit 단계는 레지스트리
    # 없이 돌았을 수 있고, 그때는 문서 표라는 대체본으로 검사했다. 여기가 마지막 관문이다.
    registry = load_atom_registry(target_root)
    print(describe(registry, target_root))
    gate = check_top_level(lesson) + check_atoms(
        lesson,
        has_ext_js=bool(builder_output.get("player_ext_js_path")),
        registry=registry,
    )
    if errors_only(gate):
        print(format_violations(gate))
        print("\n배치하지 않았다. 이대로 넣으면 그쪽 npm run validate 가 막는다.")
        return REJECTED_EXIT

    placements, ref_fixes = resolve_placements(builder_output, run_dir)
    missing_sources = [item for item in placements if item["source"] is None]
    if missing_sources:
        for item in missing_sources:
            print(f"  · 원본 파일이 없다: {item['declared_source']}")
        print("\n배치하지 않았다.")
        return REJECTED_EXIT

    if ref_fixes:
        lesson = rewrite_refs(lesson, ref_fixes)

    planned = [(item["source"], dest_dir / item["dest"], item["convert"]) for item in placements]
    converts = [item for item in placements if item["convert"]]
    print(f"대상: {dest_dir}")
    print(f"이미지 {len(planned)}개" + (f" · 참조 경로 수정 {len(ref_fixes)}건" if ref_fixes else ""))
    for old, new in ref_fixes.items():
        print(f"  · {old} → {new}")
    for item in converts:
        print(
            f"  · {item['dest']} — 런타임이 이름을 하드코딩한 자리라 이름을 지키고 "
            f"{Path(item['declared_source']).suffix} → {Path(item['dest']).suffix} 로 변환해 놓는다"
        )

    # 놓을 파일 목록(차시 폴더 기준 상대 경로 → 내용). 덮기 전 대조와 배치 기록이 같은 목록을 쓴다.
    lesson_bytes = (json.dumps(lesson, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    to_place: dict[str, bytes | Path] = {"lesson.json": lesson_bytes}
    for name in ("player-ext.js", "player-ext.css"):
        if (lesson_dir / name).exists():
            to_place[name] = lesson_dir / name
    assets_src = lesson_dir / "assets"
    if assets_src.is_dir():
        for path in sorted(assets_src.rglob("*")):
            if path.is_file():
                to_place[path.relative_to(lesson_dir).as_posix()] = path
    for source, destination, convert in planned:
        if not convert:
            to_place[destination.relative_to(dest_dir).as_posix()] = source

    # gyo6 쪽에서 따로 고친 것을 조용히 덮지 않는다(`stages/scripts/install_record.py`).
    if dest_dir.exists() and any(dest_dir.iterdir()):
        record = install_record.entry(run_dir, target_root, args.lesson)
        if record:
            drift = install_record.target_drift(record, dest_dir)
            why = f"지난 배치({record.get('installed_at', '?')}) 뒤 gyo6 쪽에서 바뀐 파일"
        else:
            drift = install_record.unrecorded_differences(dest_dir, to_place)
            why = "배치 기록이 없다. 지금 놓으려는 것과 이미 놓인 것이 다른 파일 — gyo6 쪽 수정인지 run 이 새로운 것인지 못 가른다"
        if drift and not args.discard_target_changes:
            print(f"\n{why} {len(drift)}건:")
            for rel in drift[:20]:
                print(f"  · {rel}")
            if len(drift) > 20:
                print(f"  · … {len(drift) - 20}건 더")
            print(
                "\n배치하지 않았다. gyo6 쪽 수정이 맞으면 run 으로 먼저 가져온다.\n"
                "  버려도 되면 --discard-target-changes 를 붙인다."
            )
            return REJECTED_EXIT
        if drift:
            print(f"\n--discard-target-changes — {why} {len(drift)}건을 run 것으로 덮는다")

    if args.dry_run:
        for source, destination, convert in planned:
            verb = "convert" if convert else "copy"
            print(f"  {verb} {source.name} → {destination.relative_to(dest_dir).as_posix()}")
        print("\n--dry-run 이라 쓰지 않았다.")
        return 0

    dest_dir.mkdir(parents=True, exist_ok=True)
    for source, destination, convert in planned:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if convert:
            error = convert_image(source, destination)
            if error:
                print(f"\n{error}", file=sys.stderr)
                print("배치를 멈췄다. 이름이 어긋나면 타이틀 화면에 깨진 그림이 뜬다.", file=sys.stderr)
                return REJECTED_EXIT
        else:
            shutil.copyfile(source, destination)

    (dest_dir / "lesson.json").write_bytes(lesson_bytes)

    for name in ("player-ext.js", "player-ext.css"):
        source_file = lesson_dir / name
        if source_file.exists():
            shutil.copyfile(source_file, dest_dir / name)
            print(f"  {name} 배치")

    # 번들이 그림을 들고 있으면(우리가 구운 경우) 통째로 옮긴다. `asset_placements` 는
    # 계획 근거에서 쓰던 장치라 여기엔 없고, 대신 `lesson/assets/` 가 곧 배치 목록이다.
    copied_assets = copy_asset_tree(lesson_dir / "assets", dest_dir / "assets")
    if copied_assets:
        print(f"  assets/ 배치 {copied_assets}장")

    missing_fixed = missing_fixed_assets(lesson, lesson_dir, dest_dir)
    if missing_fixed and origin == "storyboard":
        # 원본 근거는 에셋을 안 만든다. 이 파일도 그쪽 imagegen 이 만들 자리이므로 막지 않되,
        # manifest 에 오르는지가 곧 생성되는지이므로 그것만 확실히 한다(아래 placed 에 넣는다).
        print(f"\n타이틀 로고 {missing_fixed} 는 그쪽 빌드가 만든다 — manifest 생성 대상으로 올린다")
    elif missing_fixed:
        print("\n런타임이 이름으로 찾는 파일이 없다. 그 화면에 깨진 그림이 뜬다:", file=sys.stderr)
        for path in missing_fixed:
            print(f"  · {path}", file=sys.stderr)
        print(
            "  base 가 경로를 하드코딩해 그리므로 lesson.json 이 가리키지 않아도 이 이름으로 있어야 한다.",
            file=sys.stderr,
        )
        return REJECTED_EXIT

    unresolved = unresolved_refs(lesson, dest_dir)
    if unresolved and origin == "storyboard":
        # 원본 근거는 에셋을 만들지 않는다. 참조가 파일 없이 남는 것이 **의도된 상태**이고,
        # 그쪽 `npm run build:lesson` 이 manifest 의 auto-generate 를 보고 생성한다.
        print(f"\n생성 대상 이미지 {len(unresolved)}장 — 그쪽 빌드가 만든다(원본 근거의 정상 상태):")
        for ref in unresolved[:8]:
            print(f"  · {ref}")
        if len(unresolved) > 8:
            print(f"  · … {len(unresolved) - 8}장 더")
    elif unresolved:
        print("\n참조가 실제 파일과 안 맞는다. gyo6_content 빌드가 이 자리를 생성 대상으로 본다:")
        for ref in unresolved:
            print(f"  · {ref}")
        return REJECTED_EXIT

    # manifest는 **놓인 파일 기준으로 다시** 만든다. 확장자가 어긋나 경로를 고쳤을 수 있고,
    # 그 경우 앞 단계에서 만든 manifest는 옛 이름을 가리킨다. 여기가 최종 판정이다.
    #
    # 원본 근거는 `lesson.json` 이 **참조하는 것 전부**를 목록으로 쓴다. 파일이 있으면 실제
    # 크기가 붙어 그쪽 빌드가 "이미 있는 에셋" 으로 보고, 없으면 크기 0 으로 생성 대상이 된다.
    # 예전에는 `unresolved`(파일이 없는 것)만 넣었는데, 그때는 이 경로가 그림을 하나도 안
    # 만들었기 때문이다. 이제는 우리가 구워서 전부 있으므로 그 목록이 **비어 버린다**
    # (실측 2026-09-11 — 52장을 옮겨 놓고 manifest 에 0개가 적혔다).
    if origin == "storyboard":
        refs: set[str] = set()
        collect_refs(lesson, refs)
        placed = sorted(refs | set(missing_fixed) | {item["dest"] for item in placements})
    else:
        placed = [item["dest"] for item in placements]
    manifest = build_manifest(lesson, placed, collect_sizes(dest_dir, placed))
    (dest_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  manifest.json 생성 (asset {len(manifest['assets'])}개)")

    # gyo6_content `lessonParser.collectAssets` 는 .png/.jpg/.jpeg 만 훑는다(webp 제외).
    # 런타임은 webp 를 그리므로 화면은 멀쩡하지만, 그쪽이 다시 만드는 manifest 에서는 빠져
    # 에셋 관리 대상에서 조용히 사라진다. 막지는 않고 알린다.
    webp = [item["dest"] for item in placements if Path(item["dest"]).suffix.lower() == ".webp"]
    if webp:
        print(
            f"  참고: webp {len(webp)}개는 그쪽 collectAssets 가 안 훑는다"
            " — manifest 재생성 시 목록에서 빠진다(화면에는 나온다)"
        )
    if manifest["manualRequired"]:
        print(f"  사람이 채울 것 {len(manifest['manualRequired'])}개:")
        for path in manifest["manualRequired"]:
            print(f"    · {path}")

    converted = [destination.relative_to(dest_dir).as_posix() for _, destination, convert in planned if convert]
    install_record.save(run_dir, target_root, args.lesson, lesson_dir, dest_dir, [*to_place, *converted])

    print(f"\n배치했다: {dest_dir}")
    print(f"배치 기록: {run_dir / install_record.RECORD_NAME}")
    print("다음:")
    print(f"  cd {target_root}")
    print(f"  npm run build:lesson -- {args.lesson}")
    print("  npm run serve")
    return 0


def align_identifiers(lesson: dict, slot: str, lesson_id: str) -> tuple[dict, dict]:
    """차시 식별자를 **배치 위치에서** 유도한다.

    `id` 와 `lessonNo` 는 "이 차시가 커리큘럼의 어느 칸인가"이므로 폴더 경로가 정답이다.
    모델이 정할 값이 아니고, 사람이 매번 손으로 고칠 값도 아니다.

    실측(2026-09-08): 화풍 참조 세트 이름이 새어 `id` 가 'gyo6-1-1-04-big-numbers-museum' 으로
    나왔고, 슬롯을 4-1/02 로 바꿀 때마다 `id` 를 손으로 고쳐야 했다.

        4-1/02  →  grade '4' · lessonNo '1-02' · id '02'
    """
    grade, semester = slot.split("-", 1)
    wanted = {
        "id": lesson_id,
        "lessonNo": f"{semester}-{lesson_id}",
        "grade": grade,
    }
    fixes = {}
    for field, value in wanted.items():
        current = str(lesson.get(field) or "")
        if current != value:
            fixes[field] = (current, value)
            lesson[field] = value
    return lesson, fixes


def load_builder_output(run_dir: Path) -> tuple[dict, str]:
    """번들을 만든 쪽의 보고서를 읽는다.

    초안 경로는 스토리보드 원본에서 `lesson_draft.json`을 만드는 하나뿐이다.
    에셋은 여기서 옮기지 않고 gyo6_content 빌드가 생성한다.
    """
    draft = run_dir / "lesson_draft.json"
    if draft.exists():
        return json.loads(draft.read_text(encoding="utf-8")), "storyboard"

    raise ValueError(
        f"번들 보고서가 없다: {run_dir}\n"
        "  build_lesson.py 를 스토리보드 원본으로 돌려 lesson_draft.json 을 만들어야 한다"
    )


def check_destination(dest_dir: Path, target_root: Path, lesson_ref: str, overwrite: bool) -> list[str]:
    blockers = []
    manifest = dest_dir / "manifest.json"
    if manifest.exists():
        try:
            existing = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        if existing.get("status") == "production":
            blockers.append(f"production 잠금 차시다. 덮지 않는다: {manifest}")
        # buildLock 은 status 와 다른 축이다 — 수정이 아니라 **빌드**를 동결한다. 그 자리에
        # 새 차시를 넣으면 manifestWriter 가 buildLock 을 보존하므로, 우리 차시가 라이브 런타임이
        # 아니라 커밋된 스냅샷(`runtime/locked/*`)으로 빌드된다. 새로 만든 차시가 옛 런타임으로
        # 도는 것은 거의 항상 사고이므로, 조용히 물려받지 않게 여기서 세운다.
        if existing.get("buildLock") is True:
            blockers.append(
                f"buildLock 차시 자리다. 덮으면 새 차시가 runtime/locked 스냅샷으로 빌드된다: {manifest}\n"
                "    라이브 런타임으로 빌드하려면 그 manifest 에서 buildLock 을 먼저 지운다"
            )
    if dest_dir.exists() and any(dest_dir.iterdir()) and not overwrite:
        blockers.append(f"이미 차시가 있다. 덮으려면 --overwrite: {dest_dir}")

    registry = target_root / "external" / "registry.json"
    if registry.exists():
        try:
            entries = json.loads(registry.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
        if isinstance(entries, dict):
            entries = entries.get("entries") or []
        for entry in entries:
            if isinstance(entry, dict) and entry.get("dir") == lesson_ref:
                blockers.append(
                    f"external 번들이 같은 슬롯을 쓴다: external/{lesson_ref}. "
                    "빌드가 슬롯 충돌로 세운다. registry 에서 빼거나 다른 칸을 쓴다"
                )
    return blockers


def resolve_placements(builder_output: dict, run_dir: Path) -> tuple[list[dict], dict[str, str]]:
    """선언된 목적지를 실제 파일에 맞춘다.

    planner 는 늘 `.png` 로 계획하는데 asset_generator 가 `.webp` 로 압축해 둘 수 있다.
    그 경우 선언된 이름으로 복사하면 확장자가 내용과 어긋나므로, 실제 확장자로 놓고
    lesson.json 의 참조도 함께 고친다.
    """
    placements = []
    ref_fixes: dict[str, str] = {}
    for item in builder_output.get("asset_placements") or []:
        if not isinstance(item, dict):
            continue
        declared_source = str(item.get("source_path") or "")
        declared_dest = str(item.get("dest_path") or "")
        source = resolve_source(run_dir, declared_source)
        dest = declared_dest
        convert = False
        mismatch = source is not None and source.suffix.lower() != Path(declared_dest).suffix.lower()
        if mismatch and declared_dest in FIXED_NAME_ASSETS:
            # 런타임이 이름을 하드코딩한 자리다. 이름을 못 바꾸므로 파일을 바꾼다.
            convert = True
        elif mismatch:
            dest = str(Path(declared_dest).with_suffix(source.suffix).as_posix())
            ref_fixes[declared_dest] = dest
        placements.append(
            {
                "declared_source": declared_source,
                "source": source,
                "dest": dest,
                "convert": convert,
            }
        )
    return placements, ref_fixes


def copy_asset_tree(source_dir: Path, dest_dir: Path) -> int:
    """번들이 들고 있는 그림을 그대로 옮긴다. 옮긴 파일 수를 돌려준다.

    **이름을 바꾸지 않는다.** `lesson.json` 의 참조가 이미 이 이름을 가리키고 있고,
    런타임이 이름을 하드코딩하는 자리(`assets/ui/title-logo.png`)도 여기 섞여 있다.
    """
    if not source_dir.is_dir():
        return 0
    copied = 0
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        destination = dest_dir / path.relative_to(source_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        copied += 1
    return copied


def missing_fixed_assets(lesson: dict, lesson_dir: Path, dest_dir: Path) -> list[str]:
    """런타임이 이름으로 찾는 파일이 배치 후에 그 자리에 있는지 본다.

    `lesson.json` 은 이 파일을 **참조하지 않는다** — base 가 경로를 하드코딩하기 때문이다.
    그래서 `ref_not_placed` 도 `unresolved_refs` 도 이 자리를 못 본다. 배포된 18차시가 전부
    `assets/ui/title-logo.png` 를 갖고 있는 이유이며, 없으면 타이틀 화면에 깨진 그림이 뜬다.

    차시 ext 가 `renderIntroStart` 를 통째로 대신하면 base 의 그 `<img>` 는 안 그려지므로
    요구하지 않는다.
    """
    has_intro = any(
        isinstance(step, dict) and step.get("type") == "intro" for step in lesson.get("steps") or []
    )
    if not has_intro:
        return []
    ext = lesson_dir / "player-ext.js"
    if ext.exists() and "renderIntroStart" in ext.read_text(encoding="utf-8", errors="replace"):
        return []
    return [path for path in sorted(FIXED_NAME_ASSETS) if not (dest_dir / path).exists()]


def convert_image(source: Path, destination: Path) -> str | None:
    """확장자가 다른 목적지로 다시 인코딩한다. 실패하면 사람이 읽을 이유를 돌려준다.

    `Pillow` 는 이미 `requirement.txt` 에 있다(에셋 webp 압축이 쓴다). 없으면 조용히 복사하지
    않는다 — 이름만 `.png` 인 webp 파일을 놓으면 브라우저가 못 그리고, 그것은 배치 시점에
    데이터로 확인할 수 없다.
    """
    try:
        from PIL import Image
    except ImportError:
        return (
            f"Pillow 가 없어 {source.name} 을 {destination.name} 으로 바꿀 수 없다.\n"
            "  python -m pip install -r ./requirement.txt"
        )
    try:
        with Image.open(source) as image:
            image.save(destination)
    except OSError as exc:
        return f"{source.name} → {destination.name} 변환 실패: {exc}"
    return None


def resolve_source(run_dir: Path, source: str) -> Path | None:
    if not source:
        return None
    exact = run_dir / source
    if exact.exists():
        return exact
    for suffix in ASSET_SUFFIXES:
        candidate = exact.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def rewrite_refs(node: object, ref_fixes: dict[str, str]) -> object:
    """lesson.json 안의 asset 경로 문자열만 바꾼다. 다른 문자열은 건드리지 않는다."""
    if isinstance(node, str):
        return ref_fixes.get(node, node)
    if isinstance(node, dict):
        return {key: rewrite_refs(value, ref_fixes) for key, value in node.items()}
    if isinstance(node, list):
        return [rewrite_refs(value, ref_fixes) for value in node]
    return node


def unresolved_refs(node: object, dest_dir: Path) -> list[str]:
    """lesson.json 이 가리키는 asset 중 실제로 없는 것을 모은다."""
    found: set[str] = set()
    collect_refs(node, found)
    return sorted(ref for ref in found if not (dest_dir / ref).exists())


def collect_refs(node: object, found: set[str]) -> None:
    if isinstance(node, str):
        if ASSET_REF_PATTERN.match(node):
            found.add(node)
        return
    if isinstance(node, dict):
        for value in node.values():
            collect_refs(value, found)
        return
    if isinstance(node, list):
        for value in node:
            collect_refs(value, found)


if __name__ == "__main__":
    sys.exit(main())
