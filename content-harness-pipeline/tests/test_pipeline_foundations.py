from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from stages.scripts import install_record, voice_lines  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
