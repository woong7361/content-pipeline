"""에이전트가 실제로 무엇을 읽었는지 남긴다.

정보 차단 표(`CLAUDE.md`)는 **페이로드 계약**이다 — 코드가 프롬프트에 무엇을 싣는지는 강제된다.
그러나 stage는 프로젝트 디렉토리를 cwd로 두고 샌드박스 없이 돌기 때문에(`codex_client.py`의
`--dangerously-bypass-approvals-and-sandbox`, `permission-mode acceptEdits`), 모델이 원하면
`runs/{run_id}/` 아래 다른 stage 산출물을 직접 열 수 있다. 막을 방법이 없는 것은 아니지만
(stage별 샌드박스 디렉토리) 비용이 크고, **먼저 실제로 그런 일이 일어나는지 알아야** 값을 정할 수 있다.

이 모듈은 막지 않는다. **관측 가능하게만 만든다.**

- codex: stdout이 JSONL이고 `item.completed` 의 `command_execution` 항목에 셸 명령 전문이 실린다.
  실측으로 확인한 형태다(`{"type":"item.completed","item":{"type":"command_execution","command":"...powershell ... Get-Content -LiteralPath '.\\\\content_rubric.yaml' ..."}}`).
- claude: `--output-format json` 은 결과 객체 하나만 준다. 도구 호출 기록이 없어 **감사되지 않는다.**
  감사하려면 `--output-format stream-json --verbose` 로 바꿔야 한다. 지금은 그 사실을 기록에 남긴다.

기록은 신호이지 확정 위반이 아니다. 명령에 파일명이 나왔다는 것은 **열어 봤다는 강한 정황**이지만,
grep 대상으로 이름만 스쳤을 수도 있다. 판단은 사람이 한다.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# 이 이름들이 명령에 나오면 그 stage가 그 산출물에 손을 댄 정황이다.
ARTIFACT_PATTERNS: dict[str, re.Pattern] = {
    "input": re.compile(r"[\w-]*_input\.json", re.I),
    "planner": re.compile(r"[\w-]*_planner(?:_pre_refine|_pre_interview|_refine_rejected)?\.json", re.I),
    "asset_generator": re.compile(r"[\w-]*_asset_generator\.json", re.I),
    "builder": re.compile(r"[\w-]*_builder\.json", re.I),
    "design_review": re.compile(r"[\w-]*_design_review\.json", re.I),
    "content_critique": re.compile(r"[\w-]*_content_critique\.json", re.I),
    "content_eval": re.compile(r"[\w-]*_content_eval\.json", re.I),
    "html": re.compile(r"\bindex\.html\b", re.I),
    "content_rubric": re.compile(r"\bcontent_rubric\.yaml\b", re.I),
}

# 정보 차단 표(CLAUDE.md "정보 차단 규칙")를 그대로 옮긴 것이다.
# 값은 **그 stage가 보면 안 되는 것**이다. 표를 고치면 여기도 함께 고친다.
#
# planner 이후 stage에 `input`이 들어 있는 것은 payload가 `metadata`만 싣기 때문이다
# (`prompt_parts.downstream_input_view`). 파일을 직접 열면 payload가 의도적으로 뺀
# 기획 지시까지 함께 읽으므로, 파일 단위로 보면 그 접근은 전부 정황이다.
FORBIDDEN: dict[str, set[str]] = {
    "planner": {"asset_generator", "builder", "design_review", "content_critique", "content_eval", "html"},
    "planner_refine": {"asset_generator", "builder", "design_review", "content_critique", "content_eval", "html"},
    "asset_generator": {"input", "builder", "design_review", "content_critique", "content_eval", "html"},
    "builder": {"input", "design_review", "content_critique", "content_eval"},
    "design_review": {"input", "content_critique", "content_eval"},
    "content_critique": {"input", "content_eval", "design_review"},
    "content_eval": {"input", "content_critique", "design_review"},
    "design_refine": {"input", "content_eval"},
    "content_refine": {"input", "content_eval"},
}


@dataclass
class AuditSink:
    path: Path | None = None
    stage: str | None = None
    unaudited: set[str] = field(default_factory=set)


_SINK = AuditSink()


def configure(path: Path | None) -> None:
    """run 하나에 대해 감사 기록 경로를 정한다. None이면 기록하지 않는다."""
    _SINK.path = path
    _SINK.unaudited = set()


def record_codex(stage: str | None, stdout: str) -> None:
    """codex stdout(JSONL)에서 셸 명령을 뽑아 기록한다."""
    if _SINK.path is None or not stage:
        return
    for command in extract_codex_commands(stdout):
        _append({"stage": stage, "provider": "codex", "command": command,
                 "touched": sorted(match_artifacts(command))})


def record_claude_unaudited(stage: str | None) -> None:
    """claude 경로는 도구 기록이 없다는 사실 자체를 남긴다. 조용히 비면 '위반 0건'으로 오독된다."""
    if _SINK.path is None or not stage:
        return
    if stage in _SINK.unaudited:
        return
    _SINK.unaudited.add(stage)
    _append({"stage": stage, "provider": "claude", "command": None, "touched": [],
             "note": "claude --output-format json 에는 도구 호출 기록이 없다. 이 stage는 감사되지 않았다."})


def _append(entry: dict) -> None:
    try:
        _SINK.path.parent.mkdir(parents=True, exist_ok=True)
        with _SINK.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # 감사 기록이 실패해도 run을 죽이지 않는다. 관측 장치가 본체를 멈추면 안 된다.
        pass


def extract_codex_commands(stdout: str) -> list[str]:
    commands: list[str] = []
    seen: set[str] = set()
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") if isinstance(event, dict) else None
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        command = item.get("command")
        # item.started 와 item.completed 가 같은 명령을 두 번 싣는다. 한 번만 남긴다.
        if isinstance(command, str) and command not in seen:
            seen.add(command)
            commands.append(command)
    return commands


def match_artifacts(command: str) -> set[str]:
    return {name for name, pattern in ARTIFACT_PATTERNS.items() if pattern.search(command)}


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def find_violations(entries: list[dict]) -> list[dict]:
    """차단 표를 어긴 정황만 골라낸다."""
    out = []
    for entry in entries:
        forbidden = FORBIDDEN.get(entry.get("stage", ""), set())
        hit = sorted(forbidden.intersection(entry.get("touched", [])))
        if hit:
            out.append({**entry, "violates": hit})
    return out
