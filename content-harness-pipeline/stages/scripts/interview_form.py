"""초안 파이프라인의 **인터뷰 질문지**를 화면에서 읽고, 화면에서 적은 답을 파일로 돌려놓는다.

`lesson_desk.py` 의 /pipeline 화면이 쓴다. 질문지 자체는 `produce_lesson.write_interview_package` 가 만든다.

    runs/{id}/interview/questions.md       사람이 답을 적는 질문지 — 파이프라인이 다시 읽는 것은 이 파일뿐이다
    runs/{id}/interview/questions-new.md   questions.md 에 이미 답이 있을 때 뒤 단계가 새 질문을 여기 낸다
                                           (답한 것도 '이미 답한 것' 칸에 함께 실려 있다)

화면은 둘 중 **새것**을 보여 준다. 저장할 때는 답까지 합친 전체를 questions.md 에 **파이프라인이 읽는 모양**
(`### Q번호. 질문` 다음 줄 `답: …`)으로 다시 쓴다 — 그래야 다음 번 질문지를 만들 때 답을 알아보고 다시 묻지 않는다.
덮기 전 questions.md 는 `questions.bak-{시각}.md` 로, 합친 questions-new.md 는 `questions-new.merged-{시각}.md` 로 옮겨 둔다.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
QUESTIONS = "questions.md"
NEW_QUESTIONS = "questions-new.md"
# `### Q3. 질문` 또는 `### A2. [구분] 질문`. 대괄호 구분은 A 칸에만 있다 — Q 칸의 `[DEC-01] …` 은 질문 본문이다
# (produce_lesson.question_key 와 같게 떼야 답이 짝지어진다).
HEADING = re.compile(r"^###\s+(?:A\d+\.\s*\[(?P<label>[^\]]*)\]\s*|Q[\w-]+\.\s*)(?P<text>.+)$")


def question_key(text: str) -> str:
    """produce_lesson.question_key 와 같은 열쇠 — 번호·구분을 떼고 본문 앞 80자."""
    return re.sub(r"^(?:Q[\w-]+\.|A\d+\.\s*\[[^\]]*\])\s*", "", text).strip()[:80]


def current_file(run_dir: Path) -> Path | None:
    folder = run_dir / "interview"
    main, new = folder / QUESTIONS, folder / NEW_QUESTIONS
    if new.exists() and (not main.exists() or new.stat().st_mtime >= main.stat().st_mtime):
        return new
    return main if main.exists() else None


def parse(text: str) -> list[dict]:
    """질문지 → [{key, question, group, answer, answered}]. '참고' 절과 그 밖의 글은 버린다."""
    items: list[dict] = []
    group = ""
    current: dict | None = None
    in_answer = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current, in_answer = None, False
            continue
        if stripped.startswith("### — ") or stripped.startswith("### -- "):
            group = stripped[6:].strip()
            current, in_answer = None, False
            continue
        match = HEADING.match(stripped)
        if match:
            question = match.group("text").strip()
            current = {"key": question_key(question), "question": question,
                       "group": match.group("label") or group, "answer_lines": []}
            items.append(current)
            in_answer = False
            continue
        if current is None:
            continue
        if stripped.startswith("---") or stripped.startswith("```"):
            current, in_answer = None, False
            continue
        if stripped.startswith("답:"):
            in_answer = True
            first = stripped[2:].strip()
            if first:
                current["answer_lines"].append(first)
            continue
        if in_answer:
            current["answer_lines"].append(line.rstrip())
    out = []
    seen = set()
    for item in items:
        if item["key"] in seen:  # 같은 질문이 두 칸에 있으면 처음 것(위 = 답이 필요한 칸)을 쓴다
            continue
        seen.add(item["key"])
        answer = "\n".join(item["answer_lines"]).strip()
        out.append({"key": item["key"], "question": item["question"], "group": item["group"],
                    "answer": answer, "answered": bool(answer)})
    return out


def load(run_dir: Path) -> dict:
    path = current_file(run_dir)
    if path is None:
        return {"file": "", "items": []}
    return {"file": path.name, "items": parse(path.read_text(encoding="utf-8"))}


def render(items: list[dict], run_id: str) -> str:
    pending = [i for i in items if not i["answer"].strip()]
    answered = [i for i in items if i["answer"].strip()]
    lines = [
        "# 인터뷰 질문",
        "",
        f"**답이 필요한 것 {len(pending)}건** (답한 {len(answered)}건 포함 — 차시 작업대 화면에서 저장함).",
        "",
        "각 질문의 `답:` 뒤에 적습니다. 비워 두면 그 자리는 확정되지 않은 채로 남고, 이후 단계가 지어내지 않습니다.",
        "",
        "```bash",
        f"python -B ./produce_lesson.py runs/{run_id} \\",
        "    --start-at interview_brief \\",
        f"    --interview-notes runs/{run_id}/interview/questions.md",
        "```",
        "",
        "---",
        "",
    ]
    number = 0
    for title, group_items in (("답이 필요한 것", pending), ("답한 것", answered)):
        lines += [f"## {title} ({len(group_items)}건)", ""]
        current = None
        for item in group_items:
            if item["group"] and item["group"] != current:
                current = item["group"]
                lines += [f"### — {current}", ""]
            number += 1
            answer = item["answer"].strip()
            lines += [f"### Q{number}. {item['question']}", "", f"답: {answer}" if answer else "답:", ""]
        lines += ["---", ""]
    return "\n".join(lines) + "\n"


def save(run_dir: Path, answers: dict[str, str]) -> dict:
    """answers = {key: 답}. 지금 질문지에 답을 채워 questions.md 로 쓴다. 저장 뒤의 질문지를 돌려준다."""
    folder = run_dir / "interview"
    path = current_file(run_dir)
    if path is None:
        raise ValueError("질문지가 아직 없다")
    items = parse(path.read_text(encoding="utf-8"))
    known = {item["key"] for item in items}
    unknown = [k for k in answers if k not in known]
    if unknown:
        raise ValueError(f"질문지에 없는 질문: {unknown[0][:40]}")
    for item in items:
        if item["key"] in answers:
            # 파이프라인은 답을 한 줄로 기억한다(read_existing_answers) — 여러 줄이면 다음 질문지에서 뒷줄이 사라진다
            lines = [line.strip() for line in str(answers[item["key"]]).splitlines() if line.strip()]
            item["answer"] = " / ".join(lines)
    stamp = datetime.now(KST).strftime("%Y%m%d-%H%M%S")
    main = folder / QUESTIONS
    if main.exists():
        main.replace(folder / f"questions.bak-{stamp}.md")
    if path.name == NEW_QUESTIONS:
        path.replace(folder / f"questions-new.merged-{stamp}.md")
    main.write_text(render(items, run_dir.name), encoding="utf-8")
    return load(run_dir)
