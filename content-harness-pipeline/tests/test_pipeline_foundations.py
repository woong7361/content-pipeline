from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import (  # noqa: E402
    desk_failures, install_record, interview_form, lesson_notes, pipeline_status, redo_report, voice_lines,
)
from stages.scripts.pipeline_graph import DagNode, PipelineDag, StageCache  # noqa: E402
from stages.scripts.spec_tests import build_test_plan, validate_lesson_spec, verify_lesson_against_spec  # noqa: E402
from stages.scripts.verify_routing import (  # noqa: E402
    asset_routes,
    from_functional,
    from_rendered,
    from_review,
    sort_findings,
)


def sample_spec() -> dict:
    return {
        "schema_version": "1.0",
        "lesson": {"title": "덧셈", "grade": "4", "lesson_no": "2-02", "learning_objectives": ["계산한다"]},
        "requirements": [
            {"id": "REQ-CONTENT-01", "kind": "content", "statement": "문제를 제시한다", "source": {"artifact": "storyboard.pdf", "locator": "p.1"}, "targets": ["Q-01"], "verification": "functional"}
        ],
        "scenes": [
            {"id": "SCN-01", "title": "문제", "order": 1, "requirement_ids": [], "entry": "start", "exit": "correct"}
        ],
        "questions": [
            {"id": "Q-01", "scene_id": "SCN-01", "prompt": "1+1은?", "answer": 2, "interaction": "numberInput", "requirement_ids": ["REQ-CONTENT-01"]}
        ],
        "assets": [],
        "decisions": [],
    }


class SpecTests(unittest.TestCase):
    def test_spec_links_and_generated_tests(self) -> None:
        spec = sample_spec()
        errors = validate_lesson_spec(spec, PROJECT_DIR / "schemas" / "lesson_spec.schema.json")
        self.assertEqual([], errors)
        plan = build_test_plan(spec)
        self.assertEqual(3, len(plan["cases"]))
        self.assertEqual([], plan["coverage"]["uncovered"])

    def test_missing_question_is_rejected(self) -> None:
        errors = verify_lesson_against_spec(sample_spec(), {"id": "SCN-01", "title": "문제"})
        self.assertTrue(any("question not implemented" in error for error in errors))


class CacheTests(unittest.TestCase):
    def test_parent_change_changes_child_fingerprint(self) -> None:
        dag = PipelineDag([
            DagNode("plan", (), ("input.txt",), ("plan.json",)),
            DagNode("build", ("plan",), ("plan.json",), ("lesson.json",)),
        ])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "input.txt").write_text("v1", encoding="utf-8")
            (root / "plan.json").write_text("{}", encoding="utf-8")
            (root / "lesson.json").write_text("{}", encoding="utf-8")
            cache = StageCache(root, dag)
            first_plan = cache.fingerprint("plan")
            cache.record("plan", first_plan)
            first_build = cache.fingerprint("build")
            cache.record("build", first_build)
            self.assertTrue(cache.hit("build", first_build))

            (root / "input.txt").write_text("v2", encoding="utf-8")
            second_plan = cache.fingerprint("plan")
            self.assertNotEqual(first_plan, second_plan)
            (root / "plan.json").write_text(json.dumps({"changed": True}), encoding="utf-8")
            cache.record("plan", second_plan)
            self.assertNotEqual(first_build, cache.fingerprint("build"))


class VerifyRoutingTests(unittest.TestCase):
    """화면 검증의 지적이 **고칠 수 있는 담당자**에게 가는지 본다. 실측 사례(2026-09-29, 4-1/03)로 짰다."""

    def review(self, **item) -> dict:
        base = {"screen": "s01.png", "priority": "medium", "issue": "", "evidence": "", "fix_target": "unknown"}
        return {"priority_findings": [{**base, **item}], "storyboard_gaps": []}

    def test_text_verbatim_in_storyboard_goes_to_storyboard_owner(self) -> None:
        source = "4-1 표4: 삼각형의 두 각을 보고 어느 삼각형인지 골라보세요."
        review = self.review(issue="지시문이 “삼각형의 두 각을 보고”인데 세 각이 제시된다", fix_target="lesson.json")
        [item] = from_review(review, Path("."), source, [])
        self.assertEqual(item["owner"], "storyboard")

    def test_text_not_in_storyboard_stays_with_developer(self) -> None:
        review = self.review(issue="“다음으로 가요”라는 원문에 없는 안내가 떴다", fix_target="lesson.json")
        [item] = from_review(review, Path("."), "전혀 다른 원문", [])
        self.assertEqual(item["owner"], "developer")

    def test_layout_goes_to_developer_even_if_quote_matches(self) -> None:
        # 배치 지적은 원문과 글이 같아도 개발 몫이다 — 문구 대조는 lesson.json 문구 지적에만 건다.
        review = self.review(issue="“삼각형의 두 각을 보고” 말풍선이 도형판에 가려진다", fix_target="player-ext.css")
        [item] = from_review(review, Path("."), "삼각형의 두 각을 보고", [])
        self.assertEqual(item["owner"], "developer")

    def test_asset_finding_guesses_path_only_when_unique(self) -> None:
        planned = ["assets/backgrounds/dabotap.png", "assets/backgrounds/hanok-side.png"]
        review = self.review(issue="dabotap 배경의 탑 층수가 실물과 다르다", fix_target="asset")
        [item] = from_review(review, Path("."), "", planned)
        self.assertEqual(item["owner"], "asset")
        self.assertIn("assets/backgrounds/dabotap.png", item["evidence"])
        [route] = asset_routes(sort_findings([item]))
        self.assertEqual(route["path"], "assets/backgrounds/dabotap.png")

    def test_asset_without_path_is_left_for_a_person(self) -> None:
        review = self.review(issue="배경 그림에 사람이 그려져 있다", fix_target="asset")
        [route] = asset_routes(sort_findings(from_review(review, Path("."), "", ["assets/backgrounds/a.png"])))
        self.assertEqual(route["path"], "")

    def test_broken_image_missing_file_is_asset_else_developer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lesson_dir = Path(tmp)
            (lesson_dir / "assets").mkdir()
            (lesson_dir / "assets" / "here.webp").write_bytes(b"x")
            report = {"violations": [
                {"kind": "broken_image", "where": "a", "detail": "그림을 못 불러온다: assets/gone.png"},
                {"kind": "broken_image", "where": "b", "detail": "그림을 못 불러온다: assets/here.png"},
            ]}
            owners = [item["owner"] for item in from_rendered(report, lesson_dir)]
        self.assertEqual(owners, ["asset", "developer"])

    def test_unvalidated_text_checks_do_not_block_and_are_grouped(self) -> None:
        report = {"violations": [], "advisories": [
            {"kind": "text_overlap", "where": "gj-measure", "detail": "글자 \"40\" 와 \"140\" 가 4×7px 겹친다"},
            {"kind": "text_overlap", "where": "gj-measure", "detail": "글자 \"130\" 와 \"120\" 가 8×9px 겹친다"},
        ]}
        [item] = from_rendered(report, Path("."))
        self.assertEqual((item["owner"], item["severity"]), ("developer", "medium"))
        self.assertIn("외 1건", item["issue"])

    def test_functional_failure_blocks_and_maps_to_plan_cases(self) -> None:
        results = {
            "problems": [{"id": "Q-01", "atoms": ["keypad"], "mode": "ui", "shots": [],
                          "tests": {"retry": {"status": "pass"}, "correct": {"status": "fail", "detail": "안 넘어간다"}}}],
            "seen_ids": ["SCN-01-talk"], "stuck": False, "page_errors": [],
        }
        plan = build_test_plan(sample_spec())
        items, cases = from_functional(results, plan, sample_spec(), Path("."), Path("."))
        self.assertEqual([(i["owner"], i["severity"]) for i in items], [("developer", "blocking")])
        status = {case["id"]: case["status"] for case in cases}
        self.assertEqual(status["TEST-Q-01-CORRECT"], "fail")
        self.assertEqual(status["TEST-Q-01-RETRY"], "pass")
        self.assertEqual(status["TEST-SCN-01-REACHABLE"], "pass")

    def test_unreached_question_after_full_walk_is_reported(self) -> None:
        results = {"problems": [], "seen_ids": [], "stuck": False, "page_errors": []}
        items, cases = from_functional(results, build_test_plan(sample_spec()), sample_spec(), Path("."), Path("."))
        self.assertTrue(any("not_reached" in item["issue"] for item in items))

    def test_asset_case_uses_confirmed_path_and_skips_dropped_proposals(self) -> None:
        spec = sample_spec()
        spec["assets"] = [
            {"id": "AST-01", "path": "assets/bg/a.png", "path_status": "proposed — asset-plan 경로가 우선한다"},
            {"id": "AST-02", "path": "assets/ui/stamp.png", "path_status": "proposed — asset-plan 경로가 우선한다"},
        ]
        plan = {"cases": [
            {"id": "TEST-AST-01-EXISTS", "kind": "asset_exists", "target": "AST-01", "expected": {"path": "assets/bg/a.png"}},
            {"id": "TEST-AST-02-EXISTS", "kind": "asset_exists", "target": "AST-02", "expected": {"path": "assets/ui/stamp.png"}},
        ]}
        results = {"problems": [], "seen_ids": [], "stuck": True, "page_errors": []}
        with tempfile.TemporaryDirectory() as tmp:
            lesson_dir = Path(tmp)
            (lesson_dir / "assets" / "backgrounds").mkdir(parents=True)
            (lesson_dir / "assets" / "backgrounds" / "a.png").write_bytes(b"x")
            items, cases = from_functional(results, plan, spec, lesson_dir, lesson_dir,
                                           {"AST-01": "assets/backgrounds/a.png"})
        self.assertEqual({c["id"]: c["status"] for c in cases},
                         {"TEST-AST-01-EXISTS": "pass", "TEST-AST-02-EXISTS": "skip"})
        self.assertFalse(any(i["owner"] == "asset" for i in items))

    def test_automation_crash_is_not_a_pass(self) -> None:
        results = {"problems": [], "seen_ids": [], "stuck": False, "page_errors": ["automation: boom"]}
        items, _ = from_functional(results, {"cases": []}, {}, Path("."), Path("."))
        self.assertEqual([(i["owner"], i["severity"]) for i in items], [("human", "blocking")])


class InstallRecordTests(unittest.TestCase):
    """배치 뒤 **어느 쪽이** 바뀌었는지 가르는지 본다. 실측(2026-09-29, 4-1/03) — gyo6 쪽 수정이 조용히 덮였다."""

    def setup_dirs(self, tmp: str) -> tuple[Path, Path, Path]:
        run = Path(tmp) / "run"
        lesson = run / "lesson"
        dest = Path(tmp) / "gyo6" / "lessons" / "4-1" / "03"
        (lesson / "assets").mkdir(parents=True)
        (dest / "assets").mkdir(parents=True)
        (lesson / "lesson.json").write_text("{}", encoding="utf-8")
        (lesson / "assets" / "bg.png").write_bytes(b"run-bg")
        (dest / "lesson.json").write_text("{}", encoding="utf-8")
        (dest / "assets" / "bg.png").write_bytes(b"run-bg")
        return run, lesson, dest

    def test_gyo6_side_edit_is_detected_but_build_outputs_are_not(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run, lesson, dest = self.setup_dirs(tmp)
            target = Path(tmp) / "gyo6"
            install_record.save(run, target, "4-1/03", lesson, dest, ["lesson.json", "assets/bg.png"])
            record = install_record.entry(run, target, "4-1/03")
            self.assertEqual(install_record.target_drift(record, dest), [])
            (dest / "thumbnail.webp").write_bytes(b"build")      # 빌드가 만든 것 — 우리가 쓴 것이 아니다
            self.assertEqual(install_record.target_drift(record, dest), [])
            (dest / "assets" / "bg.png").write_bytes(b"rebaked-in-gyo6")
            self.assertEqual(install_record.target_drift(record, dest), ["assets/bg.png"])
            self.assertEqual(install_record.source_drift(record, lesson), [])

    def test_run_side_change_is_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run, lesson, dest = self.setup_dirs(tmp)
            target = Path(tmp) / "gyo6"
            install_record.save(run, target, "4-1/03", lesson, dest, ["lesson.json", "assets/bg.png"])
            (lesson / "lesson.json").write_text('{"v": 2}', encoding="utf-8")
            record = install_record.entry(run, target, "4-1/03")
            self.assertEqual(install_record.source_drift(record, lesson), ["lesson.json"])

    def test_without_record_lists_files_that_would_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run, lesson, dest = self.setup_dirs(tmp)
            (dest / "assets" / "bg.png").write_bytes(b"something-else")
            differs = install_record.unrecorded_differences(
                dest, {"lesson.json": b"{}", "assets/bg.png": lesson / "assets" / "bg.png", "assets/new.png": b"x"})
            self.assertEqual(differs, ["assets/bg.png"])


class VoiceLineTests(unittest.TestCase):
    """런타임이 **재생하는 자리에만** 음성을 모으고 거는지 본다."""

    def lesson(self) -> dict:
        return {
            "cast": {"child": {"name": "여자아이"}},
            "steps": [
                {"stageDirections": [
                    {"id": "SCN-01", "speechText": "안녕 / 반가워"},
                    {"id": "SCN-02", "captionText": "자막만 있다"},
                    {"id": "SCN-03", "speechText": "반짝", "sound": "sparkle"},
                ],
                 "rounds": [{"problems": [
                     {"id": "Q-01", "prompt": "각을 재어 봐", "interaction": {},
                      "hintAfterWrong": {"speechText": "**각도기**를 대 봐"}},
                 ]}]},
                {"scenes": [{"type": "realLifeSlide", "slides": [
                    {"id": "SCN-09", "title": "1. 제목", "caption": "• 첫째 줄\n• 둘째 줄"},
                ]}]},
            ],
        }

    def test_collects_only_playable_places_in_order(self) -> None:
        lines, skipped = voice_lines.collect(self.lesson())
        self.assertEqual([(l.audio_id, l.kind, l.speaker) for l in lines], [
            ("vo-SCN-01", "cut", "child"),
            ("vo-Q-01-prompt", "problem", "child"),
            ("vo-Q-01-hint", "hint", "child"),
            ("vo-SCN-09", "slide", "narrator"),
        ])
        self.assertEqual(lines[0].text, "안녕\n반가워")
        self.assertEqual(lines[2].text, "각도기를 대 봐")
        self.assertEqual(lines[3].text, "1. 제목\n첫째 줄\n둘째 줄")
        self.assertTrue(any("자막만" in s for s in skipped))
        self.assertTrue(any("sparkle" in s for s in skipped))    # 남의 효과음은 덮지 않는다

    def test_apply_wires_audio_map_and_fields_and_is_idempotent(self) -> None:
        lesson = self.lesson()
        lines, _ = voice_lines.collect(lesson)
        voice_lines.apply(lesson, lines)
        cut, problem = lesson["steps"][0]["stageDirections"][0], lesson["steps"][0]["rounds"][0]["problems"][0]
        self.assertEqual(cut["sound"], "vo-SCN-01")
        self.assertEqual(problem["narration"], "vo-Q-01-prompt")
        self.assertEqual(problem["hintAfterWrong"]["sound"], "vo-Q-01-hint")
        self.assertEqual(lesson["steps"][1]["scenes"][0]["slides"][0]["narration"], {"audio": "vo-SCN-09"})
        self.assertEqual(lesson["audioMap"]["narration"]["vo-SCN-01"], "assets/audio/narration/vo-SCN-01.mp3")
        again, _ = voice_lines.collect(lesson)                     # 다시 돌아도 같은 자리·같은 id
        self.assertEqual([l.audio_id for l in again], [l.audio_id for l in lines])

    def test_pose_variants_of_one_person_share_a_speaker(self) -> None:
        lesson = {
            "cast": {"girl": {"name": "여자아이"}, "girlWave": {"name": "여자아이(엔딩 — 손 흔들기)"},
                     "staff": {"name": "축제 관계자"}},
            "steps": [{"stageDirections": [
                {"id": "A", "speechText": "안녕", "characterRef": "girlWave"},
                {"id": "B", "speechText": "반가워", "characterRef": "staff"},
            ]}],
        }
        lines, _ = voice_lines.collect(lesson)
        self.assertEqual([l.speaker for l in lines], ["girl", "staff"])

    def test_web_script_is_one_paragraph_per_line_without_numbers(self) -> None:
        import voice_lesson
        lesson = self.lesson()
        lines, skipped = voice_lines.collect(lesson)
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            voice_lesson.export_script(run, lesson, lines, skipped)
            script = (run / "audio" / "web" / "script-all.txt").read_text(encoding="utf-8")
            paragraphs = [p for p in script.split("\n\n") if p.strip()]
            self.assertEqual(len(paragraphs), len(lines))             # 대사 하나 = 문단 하나
            self.assertEqual(paragraphs[0].strip(), "안녕 반가워")       # 줄바꿈은 합친다, 번호는 없다
            narrator = (run / "audio" / "web" / "script-narrator.txt").read_text(encoding="utf-8")
            self.assertEqual(narrator.strip(), "1. 제목 첫째 줄 둘째 줄")
            self.assertTrue((run / "audio" / "web-inbox").is_dir())


class LessonNotesTests(unittest.TestCase):
    """사람이 화면을 보고 적은 메모 — 적으면 대기열, 순서대로 같은 종류 묶음을 가져간다."""

    def test_status_changes_are_logged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            first = lesson_notes.add(desk, "Q-03 보기 글자가 잘림")
            second = lesson_notes.add(desk, "타이틀 로고가 관문 지붕을 가림")
            self.assertEqual([first["id"], second["id"]], ["U01", "U02"])
            lesson_notes.set_status(desk, ["U02"], "review", "AI 고침")
            notes = {n["id"]: n for n in lesson_notes.load(desk)}
            self.assertEqual(notes["U01"]["status"], "queued")   # 적으면 바로 대기열
            self.assertEqual(notes["U02"]["status"], "review")
            self.assertTrue(notes["U02"]["log"][-1].endswith("AI 고침"))
            with self.assertRaises(ValueError):
                lesson_notes.set_status(desk, ["U01"], "bogus")

    def test_attached_images_reach_prompt(self) -> None:
        """메모에 붙인 그림은 desk 폴더에 저장하고, AI 에게 넘길 때 절대 경로를 붙인다."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            note = lesson_notes.add(desk, "보기 글자가 잘림 — 캡처의 빨간 곳")
            lesson_notes.attach(desk, note["id"], [("image.png", b"\x89PNG..."), ("b.JPG", b"jpg")])
            saved = lesson_notes.load(desk)[0]["images"]
            self.assertEqual(len(saved), 2)
            self.assertTrue((desk / saved[0]).is_file())
            self.assertTrue(saved[1].endswith("img-2.jpg"))
            block = lesson_notes.prompt_block(lesson_notes.load(desk)[0], desk)
            self.assertIn(str((desk / saved[0]).resolve()), block)
            with self.assertRaises(ValueError):
                lesson_notes.attach(desk, note["id"], [("notes.txt", b"x")])

    def test_refine_with_images(self) -> None:
        """보완해서 다시 맡길 때 붙인 그림은 그 보완 기록에 따로 저장하고, AI 에게 보완 메모와 함께 경로를 넘긴다."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            note = lesson_notes.add(desk, "버튼 다시 그리기")
            lesson_notes.attach(desk, note["id"], [("a.png", b"png")])
            lesson_notes.set_status(desk, [note["id"]], "review", "AI 고침")
            with self.assertRaises(ValueError):   # 그림이 아니면 보완 기록도 남기지 않는다
                lesson_notes.refine(desk, note["id"], "빛 약하게", [("x.txt", b"x")])
            self.assertFalse(lesson_notes.load(desk)[0].get("refinements"))
            lesson_notes.refine(desk, note["id"], "빛 약하게 — 캡처의 노란 곳", [("c.png", b"png"), ("d.webp", b"webp")])
            saved = lesson_notes.load(desk)[0]
            self.assertEqual(saved["images"], ["attachments/U01/img-1.png"])          # 원래 메모 그림은 그대로
            self.assertEqual(saved["refinements"][0]["images"], ["attachments/U01/r1-img-1.png", "attachments/U01/r1-img-2.webp"])
            self.assertTrue((desk / "attachments/U01/r1-img-2.webp").is_file())
            block = lesson_notes.prompt_block(saved, desk)
            self.assertIn(str((desk / "attachments/U01/r1-img-1.png").resolve()), block.split("#### 보완 1")[1])

    def test_edit_text_only_while_queued(self) -> None:
        """처리 전(대기) 메모만 글을 고친다 — AI 가 집어 간 뒤에 고치면 반영되지 않으므로 거절한다."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            note = lesson_notes.add(desk, "문3 글자 잘림")
            lesson_notes.edit_text(desk, note["id"], "  문3 보기 글자 잘림 — 보기 2번  ")
            saved = lesson_notes.load(desk)[0]
            self.assertEqual(saved["text"], "문3 보기 글자 잘림 — 보기 2번")
            self.assertEqual(saved["status"], "queued")
            self.assertTrue(saved["log"][-1].endswith("사람이 글을 고침"))
            with self.assertRaises(ValueError):
                lesson_notes.edit_text(desk, note["id"], "   ")
            lesson_notes.set_status(desk, [note["id"]], "working", "AI 가 집음")
            with self.assertRaises(ValueError):
                lesson_notes.edit_text(desk, note["id"], "늦게 고침")

    def test_ids_never_reused_after_delete(self) -> None:
        """작업 기록·사용량이 번호로 메모를 가리키므로 지운 번호를 다시 쓰지 않는다."""
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            lesson_notes.add(run, "하나")
            lesson_notes.add(run, "둘")
            lesson_notes.remove(run, "U02")
            self.assertEqual(lesson_notes.add(run, "셋")["id"], "U03")
            lesson_notes.remove(run, "U03")
            lesson_notes.remove(run, "U01")
            self.assertEqual(lesson_notes.add(run, "넷")["id"], "U04")

    def test_insert_before_and_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            for text in ("a", "b", "c"):
                lesson_notes.add(desk, text)                       # U01 U02 U03
            lesson_notes.add(desk, "끼움", before="U02")           # U04 → U02 앞
            self.assertEqual([n["id"] for n in lesson_notes.load(desk)], ["U01", "U04", "U02", "U03"])
            lesson_notes.move(desk, "U03", "U01")                  # 맨 앞으로
            lesson_notes.move(desk, "U04", None)                   # 맨 뒤로
            self.assertEqual([n["id"] for n in lesson_notes.load(desk)], ["U03", "U01", "U02", "U04"])
            lesson_notes.set_status(desk, ["U01"], "working")
            with self.assertRaises(ValueError):
                lesson_notes.move(desk, "U01", None)               # 처리 중인 것은 못 옮긴다
            with self.assertRaises(ValueError):
                lesson_notes.remove(desk, "U01")                   # 지우지도 못한다

    def test_code_lane_takes_leading_same_kind_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            lesson_notes.add(desk, "c1", "code")
            lesson_notes.add(desk, "c2", "code")
            lesson_notes.add(desk, "i1", "image")
            lesson_notes.add(desk, "c3", "code")
            code = lambda: [[n["id"] for n in g] for lane, g in lesson_notes.runnable_groups(lesson_notes.load(desk)) if lane == "claude"]
            self.assertEqual(code(), [["U01", "U02"]])            # 같은 종류 연속 묶음만
            lesson_notes.set_status(desk, ["U01", "U02"], "review")
            self.assertEqual(code(), [["U04"]])
            lesson_notes.add(desk, "앞에 끼운 코드", "code", before="U04")   # 순서를 바꾸면 다음 묶음이 바뀐다
            self.assertEqual(code(), [["U05", "U04"]])
            lesson_notes.set_status(desk, ["U03", "U04", "U05"], "open")
            self.assertEqual(code(), [])                           # 열림은 저절로 다시 돌지 않는다
            self.assertFalse(lesson_notes.has_queued(lesson_notes.load(desk)))

    def test_runnable_groups_runs_code_and_image_side_by_side(self) -> None:
        """코드(클로드) ∥ 그림(코덱스) — 서로 기다리지 않는다. 검증만 칸막이."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            for text, kind in [("A", "code"), ("B", "image"), ("C", "code"), ("D", "verify"), ("E", "image")]:
                lesson_notes.add(desk, text, kind)

            def plan(busy=frozenset()):
                return [(lane, [n["id"] for n in group])
                        for lane, group in lesson_notes.runnable_groups(lesson_notes.load(desk), busy)]

            self.assertEqual(plan(), [("claude", ["U01"]), ("codex", ["U02"])])   # A ∥ B
            lesson_notes.set_status(desk, ["U01", "U02"], "working")
            self.assertEqual(plan({"claude", "codex"}), [])
            lesson_notes.set_status(desk, ["U01"], "review")
            self.assertEqual(plan({"codex"}), [("claude", ["U03"])])   # C 는 그림 B 를 기다리지 않는다
            lesson_notes.set_status(desk, ["U03"], "working")
            self.assertEqual(plan({"claude", "codex"}), [])
            lesson_notes.set_status(desk, ["U02"], "review")
            self.assertEqual(plan({"claude"}), [])             # D(검증)는 C 가 걸려 있어 못 돈다
            self.assertEqual(plan({"claude"}), [])             # E 는 위의 검증 D 를 기다린다
            lesson_notes.set_status(desk, ["U03"], "review")
            self.assertEqual(plan(), [("codex", ["U04"])])     # 검증은 혼자
            lesson_notes.set_status(desk, ["U04"], "working")
            self.assertEqual(plan({"codex"}), [])
            lesson_notes.set_status(desk, ["U04"], "review")
            self.assertEqual(plan(), [("codex", ["U05"])])

    def test_build_checkpoint_is_a_barrier(self) -> None:
        """빌드 지점(2026-10-01) — A · B 를 처리하고 빌드한 뒤 C."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            for text, kind in [("A", "code"), ("B", "image"), ("여기까지 처리하고 빌드", "build"), ("C", "code"), ("D", "code")]:
                lesson_notes.add(desk, text, kind)

            def plan(busy=frozenset()):
                return [(lane, [n["id"] for n in group])
                        for lane, group in lesson_notes.runnable_groups(lesson_notes.load(desk), busy)]

            self.assertEqual(plan(), [("claude", ["U01"]), ("codex", ["U02"])])   # 빌드 지점 아래 C 는 아직
            lesson_notes.set_status(desk, ["U01", "U02"], "working")
            lesson_notes.set_status(desk, ["U01"], "review")
            self.assertEqual(plan({"codex"}), [])                 # B 가 끝나야 빌드
            lesson_notes.set_status(desk, ["U02"], "review")
            self.assertEqual(plan(), [("build", ["U03"])])        # 빌드는 혼자
            lesson_notes.set_status(desk, ["U03"], "working")
            self.assertEqual(plan({"build"}), [])                 # 빌드하는 동안 C 는 기다린다
            lesson_notes.set_status(desk, ["U03"], "done")
            self.assertEqual(plan(), [("claude", ["U04", "U05"])])

    def test_runnable_groups_image_does_not_wait_for_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            for text, kind in [("c1", "code"), ("c2", "code"), ("i1", "image"), ("i2", "image"), ("c3", "code")]:
                lesson_notes.add(desk, text, kind)
            groups = lesson_notes.runnable_groups(lesson_notes.load(desk))
            self.assertEqual([(lane, [n["id"] for n in g]) for lane, g in groups],
                             [("claude", ["U01", "U02"]), ("codex", ["U03", "U04"])])   # 묶음은 같은 종류 연속
            # 4-1/03 실제 모양 — 그림이 도는 중이고 그 아래 코드 둘이 대기 → 코드가 바로 돈다
            lesson_notes.set_status(desk, ["U01", "U02"], "review")
            lesson_notes.set_status(desk, ["U03", "U04"], "working")
            groups = lesson_notes.runnable_groups(lesson_notes.load(desk), {"codex"})
            self.assertEqual([(lane, [n["id"] for n in g]) for lane, g in groups], [("claude", ["U05"])])

    def test_set_kind_fixes_wrong_kind(self) -> None:
        """종류를 잘못 골랐을 때 — 대기면 종류만, 처리된 것은 다시 대기열로, 처리 중은 거절."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            lesson_notes.add(desk, "하늘 땅 그림을 울퉁불퉁하게", "code")
            lesson_notes.add(desk, "버튼 그림", "code")
            lesson_notes.add(desk, "문6 표시 없애기", "code")
            lesson_notes.set_kind(desk, "U01", "image")
            lesson_notes.set_result(desk, "U02", "open", {"kind": "needs_image", "headline": "그림이 필요"})
            lesson_notes.set_kind(desk, "U02", "image")
            lesson_notes.set_status(desk, ["U03"], "working")
            with self.assertRaises(ValueError):
                lesson_notes.set_kind(desk, "U03", "image")
            with self.assertRaises(ValueError):
                lesson_notes.set_kind(desk, "U01", "bogus")
            notes = {n["id"]: n for n in lesson_notes.load(desk)}
            self.assertEqual((notes["U01"]["kind"], notes["U01"]["status"]), ("image", "queued"))
            self.assertEqual((notes["U02"]["kind"], notes["U02"]["status"]), ("image", "queued"))
            self.assertNotIn("result", notes["U02"])                  # 지난 결과는 치운다
            self.assertIn("다시 맡김", notes["U02"]["log"][-1])
            self.assertEqual([n["id"] for n in lesson_notes.load(desk)], ["U01", "U02", "U03"])   # 자리는 그대로

    def test_refine_requeues_with_previous_result(self) -> None:
        """보완해서 다시 맡기기 — 원래 메모는 그대로, 지난 결과와 보완 메모가 AI 프롬프트에 함께 간다."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            lesson_notes.add(desk, "철탑 노란 부분이 빛나게", "image")
            lesson_notes.set_result(desk, "U01", "review", {"kind": "rendered", "label": "그림 새로 구움",
                                                            "headline": "노란 부분에 빛을 넣었어요", "detail": "- 바깥 빛 번짐 추가",
                                                            "images": [{"path": "assets/bg/tower.png", "new": False}]})
            with self.assertRaises(ValueError):
                lesson_notes.refine(desk, "U01", "   ")
            lesson_notes.refine(desk, "U01", "빛을 조금 약하게")
            note = lesson_notes.load(desk)[0]
            self.assertEqual((note["status"], note["text"]), ("queued", "철탑 노란 부분이 빛나게"))
            self.assertNotIn("result", note)
            block = lesson_notes.prompt_block(note)
            for part in ("철탑 노란 부분이 빛나게", "보완 1", "노란 부분에 빛을 넣었어요", "assets/bg/tower.png", "빛을 조금 약하게"):
                self.assertIn(part, block)
            lesson_notes.set_status(desk, ["U01"], "working")
            with self.assertRaises(ValueError):
                lesson_notes.refine(desk, "U01", "또")
            plain = lesson_notes.add(desk, "그냥 메모", "code")
            self.assertEqual(lesson_notes.prompt_block(plain), "### U02\n\n그냥 메모")   # 보완이 없으면 예전 모양 그대로

    def test_release_working_only_given_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            lesson_notes.add(desk, "코드", "code")
            lesson_notes.add(desk, "그림", "image")
            lesson_notes.set_status(desk, ["U01", "U02"], "working")
            lesson_notes.release_working(desk, "그림 실패", ids=["U02"])   # 코드 줄은 계속 돈다
            self.assertEqual([n["status"] for n in lesson_notes.load(desk)], ["working", "open"])

    def test_release_working_reopens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            lesson_notes.add(run, "하나")
            lesson_notes.set_status(run, ["U01"], "working")
            lesson_notes.release_working(run, "끊김")
            note = lesson_notes.load(run)[0]
            self.assertEqual(note["status"], "open")
            self.assertTrue(note["log"][-1].endswith("끊김"))
            lesson_notes.set_status(run, ["U01"], "working")
            lesson_notes.release_working(run, "멈춤", to="queued")   # 멈춤이면 대기로 돌아간다
            self.assertEqual(lesson_notes.load(run)[0]["status"], "queued")

    def test_note_kind_defaults_to_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            self.assertEqual(lesson_notes.add(desk, "하나")["kind"], "code")
            self.assertEqual(lesson_notes.add(desk, "둘", "image")["kind"], "image")
            with self.assertRaises(ValueError):
                lesson_notes.add(desk, "셋", "sound")
            self.assertEqual(lesson_notes.kind_of({"id": "U09"}), "code")   # 종류가 없던 옛 메모

    def test_result_is_structured_and_cleared_on_requeue(self) -> None:
        """카드는 headline 한 줄만 보이고 detail 은 접는다 — 결과를 구조로 붙이고, 다시 맡기면 지난 결과를 치운다."""
        with tempfile.TemporaryDirectory() as tmp:
            desk = Path(tmp)
            lesson_notes.add(desk, "문1 입력칸 위치")
            lesson_notes.set_result(desk, "U01", "review",
                                    {"kind": "fixed", "label": "고침", "headline": "입력칸을 사과 이름 아래로 옮겼어요",
                                     "detail": "- 문1 표를 4열 격자로\n- player-ext.js decorate()"}, "코드 고치기 — 고침")
            note = lesson_notes.load(desk)[0]
            self.assertEqual(note["status"], "review")
            self.assertEqual(note["result"]["headline"], "입력칸을 사과 이름 아래로 옮겼어요")
            self.assertIn("at", note["result"])
            lesson_notes.set_status(desk, ["U01"], "queued", "다시 맡김")
            self.assertNotIn("result", lesson_notes.load(desk)[0])

    def test_empty_note_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                lesson_notes.add(Path(tmp), "   ")

    def test_gyo6_lessons_listed_by_semester(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ref in ("4-1/02", "4-1/01", "3-1/05", "4-2/01"):
                (root / "lessons" / ref).mkdir(parents=True)
                (root / "lessons" / ref / "lesson.json").write_text("{}", encoding="utf-8")
            (root / "lessons" / "4-1" / "99").mkdir()          # lesson.json 없는 폴더는 빠진다
            (root / "lessons" / "1-1" / "01").mkdir(parents=True)
            (root / "lessons" / "1-1" / "01" / "lesson.json").write_text("{}", encoding="utf-8")
            self.assertEqual(lesson_notes.gyo6_lessons(root, ["4-1", "3-1", "3-2"]), ["4-1/01", "4-1/02", "3-1/05"])
            self.assertEqual(lesson_notes.desk_id("4-1/04"), "4-1-04")


class PipelineStatusTests(unittest.TestCase):
    """초안 대시보드 — 로그로 실행을 나누고, pid 로 '도는 중'을 가르고, 토큰을 시각으로 단계에 담는다."""

    def write(self, run: Path, name: str, rows: list[dict]) -> None:
        (run / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    def test_running_finished_interview_and_broken(self) -> None:
        import os
        from datetime import datetime, timedelta
        now = datetime.now(pipeline_status.KST)
        t = lambda m: (now - timedelta(minutes=m)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            self.write(run, "pipeline-log.jsonl", [
                {"time": t(50), "event": "pipeline_start", "start_at": "senior_planner", "through": "interview", "pid": 1,
                 "stages": ["senior_planner", "senior_designer"]},
                {"time": t(49), "event": "stage_start", "stage": "senior_planner"},
                {"time": t(45), "event": "stage_done", "stage": "senior_planner"},
                {"time": t(44), "event": "pipeline_end", "exit_code": 0, "waiting": "interview"},
                {"time": t(40), "event": "pipeline_start", "start_at": "interview_brief", "through": "all", "pid": 999999,
                 "stages": ["interview_brief"]},
                {"time": t(39), "event": "stage_start", "stage": "interview_brief"},
                # 프로세스가 생긴 뒤에 시작 기록을 쓴다 — 이 테스트 프로세스의 pid 를 지금 시각으로 적는다
                {"time": t(0), "event": "pipeline_start", "start_at": "senior_developer", "through": "develop",
                 "pid": os.getpid(), "stages": ["senior_developer", "asset_render"]},
                {"time": t(0), "event": "stage_start", "stage": "senior_developer"},
            ])
            self.write(run, "usage-log.jsonl", [
                {"at": t(46), "kind": "llm", "stage": "senior_planner", "provider": "claude", "input": 100, "cached": 10,
                 "output": 5, "cost_usd": 0.5, "seconds": 60, "ok": True},
                {"at": t(0), "kind": "llm", "stage": "senior_developer", "provider": "claude", "input": 200, "cached": 0,
                 "output": 7, "cost_usd": 1.0, "seconds": 30, "ok": True},
            ])
            detail = pipeline_status.run_detail(run)
            first, second, third = detail["executions"][::-1]
            self.assertEqual(first["status"], "인터뷰 답 대기")
            self.assertEqual(first["totals"]["input"], 100)
            self.assertEqual(second["status"], "끊김")                     # pid 가 없는데 끝 기록도 없다
            self.assertEqual([s["state"] for s in second["stages"]], ["stopped"])
            self.assertTrue(third["running"])                              # 이 테스트 프로세스의 pid — 살아 있다
            self.assertEqual(third["current"], ["개발"])
            self.assertEqual([s["state"] for s in third["stages"]], ["running", "pending"])
            self.assertEqual(third["totals"]["cost_usd"], 1.0)
            self.assertEqual(detail["cumulative_totals"]["input"], 300)


class DeskFailureTests(unittest.TestCase):
    """실패한 작업 로그에서 사람이 할 일을 찾는다 — 실측(2026-09-30, 4-1/04) 코덱스 로그인 만료."""

    def test_known_reasons(self) -> None:
        codex_expired = ('ERROR codex_login::auth::manager: Failed to refresh token status=401 Unauthorized '
                         'detail=TokenErrorDetail { error_code: Some("refresh_token_invalidated"), '
                         'error_message: Some("Your session has ended. Please log in again."), .. }')
        self.assertIn("codex login", desk_failures.reason(codex_expired))
        self.assertIn("클로드 로그인", desk_failures.reason("Invalid API key · Please run /login"))
        self.assertIn("혼잡", desk_failures.reason("Selected model is at capacity"))
        self.assertIn("빌드 명령", desk_failures.reason("npm ERR! code ELIFECYCLE"))
        self.assertEqual(desk_failures.reason("Traceback ... KeyError: 'x'"), "")   # 모르는 실패는 비운다


class DraftInterviewTests(unittest.TestCase):
    """작업대에서 초안을 만들 때 — 인터뷰에서 한 번 멈추고(정할 것은 멈추지 않고 정리), 화면에서 적은 답을 파이프라인이 다시 읽는다."""

    def test_open_decisions_pause_instead_of_crash(self) -> None:
        import produce_lesson
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            spec = sample_spec()
            spec["decisions"] = [{"id": "DEC-01", "question": "그래프 눈금 간격은?", "answer": "", "status": "open", "targets": []}]
            (run / "spec").mkdir()
            (run / "spec" / "lesson-spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(produce_lesson.validate_spec_file(run), ["DEC-01"])     # 예외가 아니라 목록
            produce_lesson.write_interview_package(run)
            text = (run / "interview" / "questions.md").read_text(encoding="utf-8")
            self.assertIn("[DEC-01] 그래프 눈금 간격은?", text)                     # 질문지에 오른다

    def test_decisions_after_interview_never_pause(self) -> None:
        """인터뷰는 한 번(2026-10-02 사용자 결정) — 남은 정할 것은 멈추지 않고 assumed 로 정리해 assumed.md 에 모은다."""
        import produce_lesson
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            spec = sample_spec()
            spec["decisions"] = [
                {"id": "DEC-01", "question": "눈금 간격은?", "answer": "", "status": "open", "targets": []},
                {"id": "DEC-02", "question": "시작 버튼 자리", "answer": "왼쪽 아래 — 예시화면", "status": "assumed", "targets": ["REQ-UI-01"]},
                {"id": "DEC-03", "question": "영역", "answer": "변화와 관계", "status": "confirmed", "targets": []},
            ]
            (run / "spec").mkdir()
            (run / "spec" / "lesson-spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            assumed = produce_lesson.settle_decisions(run, produce_lesson.validate_spec_file(run))
            self.assertEqual(assumed, ["DEC-01", "DEC-02"])
            saved = json.loads((run / "spec" / "lesson-spec.json").read_text(encoding="utf-8"))
            self.assertFalse([d for d in saved["decisions"] if d["status"] == "open"])
            self.assertEqual(produce_lesson.validate_spec_file(run), [])
            text = (run / produce_lesson.ASSUMED_NAME).read_text(encoding="utf-8")
            self.assertIn("DEC-02 — 시작 버튼 자리", text)
            self.assertIn("왼쪽 아래 — 예시화면", text)

    def test_design_table_questions_reach_interview(self) -> None:
        """디자인 문서 표에만 적힌 질문도 인터뷰에 오른다 — 보고서 open_questions 에 있는 번호는 겹쳐 싣지 않는다."""
        import produce_lesson
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "design").mkdir()
            (run / "design" / "wireframe.md").write_text("\n".join([
                "| 번호 | 질문 | 선택지 |", "|---|---|---|",
                "| Q-D1 | 모바일 세로 대응? | (a) 레터박스(권장) (b) 세로 배치 |",
                "| Q-D2 | 문제 화면 인물 | (a) 숨김 (b) 남김 |",
            ]), encoding="utf-8")
            found = produce_lesson.table_only_questions(run, ["Q-D2: 문제 화면에서 인물을 숨길지"])
            self.assertEqual(found, ["Q-D1: 모바일 세로 대응? — 선택지: (a) 레터박스(권장) (b) 세로 배치"])

    def test_answers_saved_from_screen_are_read_back(self) -> None:
        import produce_lesson
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "interview").mkdir()
            (run / "interview" / "questions.md").write_text("\n".join([
                "# 인터뷰 질문", "", "## 답이 필요한 것 (1건)", "", "### — 기획", "", "### Q1. 정답은?", "", "답:", "",
                "---", "", "## 이미 답한 것 (1건)", "", "### A1. [디자인] 세로 화면은?", "", "답: 그대로", "",
            ]), encoding="utf-8")
            form = interview_form.load(run)
            self.assertEqual([(i["key"], i["answered"]) for i in form["items"]], [("정답은?", False), ("세로 화면은?", True)])
            interview_form.save(run, {"정답은?": "3번\n(보기 기준)"})
            known = produce_lesson.read_existing_answers(run / "interview" / "questions.md")
            self.assertEqual(known["정답은?"], "3번 / (보기 기준)")     # 여러 줄은 한 줄로
            self.assertEqual(known["세로 화면은?"], "그대로")           # 예전에는 A 번호 칸을 못 읽었다
            self.assertTrue(any(p.name.startswith("questions.bak-") for p in (run / "interview").iterdir()))
            with self.assertRaises(ValueError):
                interview_form.save(run, {"없는 질문": "x"})


class VoiceImportTests(unittest.TestCase):
    """음성 파일 넣기 — 자동 짝짓기 · 교체 · 원래 형식 유지."""

    LESSON = {
        "cast": {"child": {"name": "아이"}},
        "audioMap": {"narration": {"take1": "assets/audio/narration/take1.mp3"}, "sfx": {"sparkle": "assets/audio/sfx/sparkle.mp3"}},
        "steps": [{"stageDirections": [
            {"id": "c1", "speechText": "안녕! 오늘은 박물관에 가 보자.", "sound": "take1"},
            {"id": "c2", "speechText": "입장료를 볼까?"},
            {"id": "c3", "speechText": "특별전시도 보고 싶은데 만 원이구나."},
        ]}],
    }

    def test_auto_match_text_then_order(self) -> None:
        from stages.scripts import voice_import
        table = voice_import.rows(self.LESSON, "all")
        self.assertEqual([r["current"] for r in table], ["take1", "", ""])
        pairs = voice_import.auto_match(table, ["05_아이_특별전시도 보고.wav", "001.mp3", "002.mp3"])
        self.assertEqual(pairs["vo-c3"], {"file": "05_아이_특별전시도 보고.wav", "method": "글자"})   # 번호가 커도 글자가 먼저
        self.assertEqual((pairs["vo-c1"]["file"], pairs["vo-c2"]["file"]), ("001.mp3", "002.mp3"))
        self.assertEqual(pairs["vo-c1"]["method"], "순서")
        self.assertEqual([r["key"] for r in voice_import.rows(self.LESSON, "empty")], ["vo-c2", "vo-c3"])

    def test_apply_replaces_keeps_format_and_shelves_old(self) -> None:
        from stages.scripts import voice_import
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lesson_dir = root / "lesson"
            (lesson_dir / "assets/audio/narration").mkdir(parents=True)
            (lesson_dir / "assets/audio/narration/take1.mp3").write_bytes(b"old")
            raw = json.dumps(self.LESSON, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
            (lesson_dir / "lesson.json").write_bytes(raw.encode("utf-8"))
            session = voice_import.stage(root / "sess", self.LESSON, "all", [("001.wav", b"new1"), ("002.mp3", b"new2")])
            result = voice_import.apply(lesson_dir, root / "sess", {k: v["file"] for k, v in session["pairs"].items()}, root / "removed")
            self.assertEqual((result["placed"], result["replaced"]), (2, 1))
            after_raw = (lesson_dir / "lesson.json").read_bytes().decode("utf-8")
            self.assertTrue(all(line.endswith("\r") for line in after_raw.split("\n")[:-1]))   # CRLF 그대로
            after = json.loads(after_raw)
            self.assertEqual(after["steps"][0]["stageDirections"][0]["sound"], "vo-c1")
            self.assertEqual(after["audioMap"]["narration"]["vo-c1"], "assets/audio/narration/vo-c1.wav")   # 받은 확장자 그대로
            self.assertNotIn("take1", after["audioMap"]["narration"])                       # 아무도 안 쓰면 뺀다
            self.assertTrue((root / "removed/assets/audio/narration/take1.mp3").is_file())   # 지우지 않고 보관
            self.assertIn("sparkle", after["audioMap"]["sfx"])                              # 상관없는 소리는 그대로
            with self.assertRaises(ValueError):
                voice_import.apply(lesson_dir, root / "sess", {"vo-c2": "002.mp3"}, root / "removed")   # 이미 넣은 세션
            # 올린 뒤에 대사 글이 바뀌면 엉뚱한 줄에 소리가 붙지 않게 막는다
            session2 = voice_import.stage(root / "sess2", after, "empty", [("x.mp3", b"x")])
            changed = json.loads(after_raw)
            changed["steps"][0]["stageDirections"][2]["speechText"] = "바뀐 대사"
            (lesson_dir / "lesson.json").write_bytes(json.dumps(changed, ensure_ascii=False, indent=2).encode("utf-8"))
            if session2["pairs"]:
                with self.assertRaises(ValueError):
                    voice_import.apply(lesson_dir, root / "sess2", {k: v["file"] for k, v in session2["pairs"].items()}, root / "removed")


class VoiceReplaceSoundTests(unittest.TestCase):
    """연결 표의 조각 [바꾸기] — id 와 걸린 자리는 그대로, 파일만 바꾼다."""

    def test_replace_keeps_id_moves_old_and_updates_extension(self) -> None:
        from stages.scripts import voice_import
        with tempfile.TemporaryDirectory() as tmp:
            lesson_dir, removed = Path(tmp) / "lesson", Path(tmp) / "removed"
            (lesson_dir / "assets/audio/narration").mkdir(parents=True)
            (lesson_dir / "assets/audio/narration/vo-s-2.mp3").write_bytes(b"old")
            lesson = {"audioMap": {"narration": {"vo-s-2": "assets/audio/narration/vo-s-2.mp3", "shared": "x.mp3", "also": "x.mp3"}},
                      "steps": [{"slides": [{"narration": {"audio": "vo-s-1", "sequence": ["vo-s-1", "vo-s-2"]}}]}]}
            (lesson_dir / "lesson.json").write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
            result = voice_import.replace_sound(lesson_dir, "vo-s-2", "new.wav", b"new", removed)
            self.assertEqual(result["path"], "assets/audio/narration/vo-s-2.wav")
            self.assertEqual((lesson_dir / result["path"]).read_bytes(), b"new")
            self.assertEqual((removed / "assets/audio/narration/vo-s-2.mp3").read_bytes(), b"old")   # 지우지 않고 보관
            saved = json.loads((lesson_dir / "lesson.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["audioMap"]["narration"]["vo-s-2"], result["path"])
            self.assertEqual(saved["steps"][0]["slides"][0]["narration"]["sequence"], ["vo-s-1", "vo-s-2"])
            with self.assertRaises(ValueError):   # 같은 파일을 다른 id 도 쓰면 거절
                voice_import.replace_sound(lesson_dir, "shared", "n.mp3", b"n", removed)


class DeliveryQaTests(unittest.TestCase):
    """커밋 전 점검 — 체크리스트 읽기 · 에셋 참조 · 코드/코덱스 판정 합치기."""

    def test_checklist_items_parsed_from_markdown(self) -> None:
        from stages.scripts import delivery_qa
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.md"
            path.write_text("## A\n\n- [ ] **A1. 외부 절대 URL 없음** — `index.html`에 CDN 없음\n  - 검증: rg ...\n"
                            "- [x] **E3. 문장 단위 줄바꿈** — 문장 끝마다\n- 그냥 줄\n", encoding="utf-8")
            items = delivery_qa.checklist_items(path)
        self.assertEqual([(i["id"], i["title"]) for i in items], [("A1", "외부 절대 URL 없음"), ("E3", "문장 단위 줄바꿈")])

    def test_source_refs_skip_meta_and_prose(self) -> None:
        """메타 자리(artDirection · styleRef · assetPrompt)와 설명문 속 경로는 404 판정에서 뺀다(배포 21차시 실측)."""
        from stages.scripts import delivery_qa
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "lesson.json").write_text(json.dumps({
                "artDirection": {"styleRef": "assets/style/style-sheet.png"},
                "cast": {"child": {"assetRef": "assets/character/child.png", "styleRef": "assets/style/x.png"}},
                "steps": [{"assetPrompt": {"targetAsset": "assets/backgrounds/a.png"},
                           "backgroundRef": "assets/backgrounds/b.png",
                           "note": "화풍 앵커: assets/backgrounds/old.png — 정리됨",
                           "sound": "assets/audio/v1.wav"}],
            }), encoding="utf-8")
            (src / "player-ext.js").write_text("const m = {'assets/photos/old.jpg': 'assets/photos/new.jpg'};", encoding="utf-8")
            data, code = delivery_qa.source_refs(src)
            self.assertEqual(data, {"assets/character/child.png", "assets/backgrounds/b.png", "assets/audio/v1.wav"})
            self.assertEqual(code, {"assets/photos/old.jpg", "assets/photos/new.jpg"})
            dist = src / "dist"
            (dist / "assets/backgrounds").mkdir(parents=True)
            (dist / "assets/audio").mkdir(parents=True)
            (dist / "assets/backgrounds/b.webp").write_bytes(b"x")    # 빌드가 png → webp
            (dist / "assets/audio/v1.mp3").write_bytes(b"x")          # 빌드가 wav → mp3
            self.assertTrue(delivery_qa.exists_any_suffix(dist, "assets/backgrounds/b.png"))
            self.assertTrue(delivery_qa.exists_any_suffix(dist, "assets/audio/v1.wav"))
            self.assertFalse(delivery_qa.exists_any_suffix(dist, "assets/character/child.png"))

    def test_merge_uses_recheck_for_code_items_and_claude_for_screen_items(self) -> None:
        """클로드가 점검·고침(2026-10-01) — 코드로 재는 항목은 다시 빌드한 뒤 다시 잰 결과가 최종이다."""
        import desk_qa
        code = lambda i, r, obs="": {"id": i, "title": i, "result": r, "observed": obs, "evidence": [], "by": "code"}
        before = [code("B3", "fail", "png 1개"), code("D1", "fail", "404 2개"), code("C5", "warn", "console — AI 가 가린다"),
                  code("C1", "pass"), {"id": "E3", "title": "E3", "result": "unchecked", "observed": "", "evidence": [], "by": ""},
                  {"id": "E7", "title": "E7", "result": "unchecked", "observed": "", "evidence": [], "by": ""}]
        self.assertEqual([i["id"] for i in before if desk_qa.needs_ai(i)], ["B3", "D1", "C5", "E3", "E7"])
        ai = [{"id": "B3", "result_before": "fail", "action": "protractor.png 를 webp 로", "result": "fixed", "observed": "", "evidence": [],
               "files": ["assets/ui/protractor.webp"], "fix_hint": ""},
              {"id": "D1", "result_before": "fail", "action": "참조 고침", "result": "fixed", "observed": "", "evidence": [], "files": [], "fix_hint": ""},
              {"id": "C5", "result_before": "warn", "action": "", "result": "pass", "observed": "공통 런타임 것", "evidence": [], "files": [], "fix_hint": ""},
              {"id": "E3", "result_before": "fail", "action": "개행 8곳 정리", "result": "fixed", "observed": "임의 개행 8건", "evidence": [],
               "files": ["lesson.json"], "fix_hint": ""}]
        after = [code("B3", "pass"), code("D1", "fail", "404 1개"), code("C5", "warn", "console — AI 가 가린다"), code("C1", "pass")]
        merged = {i["id"]: i for i in desk_qa.merge(before, ai, after)}
        self.assertEqual((merged["B3"]["result"], merged["B3"]["before"]), ("fixed", "fail"))   # 다시 재서 통과 → 고침
        self.assertEqual(merged["D1"]["result"], "fail")              # 고쳤다고 했지만 다시 재니 아직 걸림 → 실패
        self.assertEqual(merged["C5"]["result"], "pass")              # 'AI 가 가린다' 경고는 클로드 판정
        self.assertEqual(merged["C1"]["result"], "pass")
        self.assertEqual((merged["E3"]["result"], merged["E3"]["files"]), ("fixed", ["lesson.json"]))
        self.assertEqual(merged["E7"]["result"], "unchecked")         # 클로드가 빠뜨리면 못 본 것으로 남는다


class RedoReportTests(unittest.TestCase):
    """[스토리보드와 대조해 다시 만들기] — 대조 결과 + 사람 메모 → 개발 단계 되먹임 목록."""

    def test_uses_only_files_written_after_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "review").mkdir()
            fix = run / "review" / "screen-fix-4-1-05.md"
            fix.write_text("- 지난번 수정안", encoding="utf-8")
            later = fix.stat().st_mtime + 10
            self.assertEqual(redo_report.build(run, "4-1/05", "", later), "")   # 지난 수정안은 다시 쓰지 않는다
            text = redo_report.build(run, "4-1/05", "인물이 크다", later)
            self.assertIn("인물이 크다", text)
            self.assertNotIn("지난번 수정안", text)
            text = redo_report.build(run, "4-1/05", "", fix.stat().st_mtime)
            self.assertIn("지난번 수정안", text)


if __name__ == "__main__":
    unittest.main()
