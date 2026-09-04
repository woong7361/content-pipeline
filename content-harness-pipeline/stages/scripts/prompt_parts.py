from __future__ import annotations

from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
COMMON_HTML_CONTRACT = PROMPTS_DIR / "common_html_contract.md"


def load_common_html_contract() -> str:
    """output/index.html을 만들거나 고치는 stage가 공통으로 지키는 계약을 읽는다.

    builder, content_refine, design_refine은 모두 같은 HTML을 산출물로 삼으므로
    저장 경로, 출력 schema, 고정 캔버스, 원문 보존, asset 사용, channel 렌더링,
    Visual QA hook 규칙이 동일해야 한다. 세 프롬프트에 각각 적어두면 한쪽만 고쳐져
    서로 어긋나므로(실제로 content_refine에만 고정 캔버스 규칙이 빠져 있었다) 한 곳에서 관리한다.
    """
    return COMMON_HTML_CONTRACT.read_text(encoding="utf-8")


def with_common_html_contract(system_prompt: str) -> str:
    """stage system prompt 뒤에 공통 계약을 잇는다. 충돌 시 공통 계약이 우선한다."""
    return f"{system_prompt}\n\n{load_common_html_contract()}"


DOWNSTREAM_INPUT_KEYS = ("metadata",)


def downstream_input_view(input_data: dict) -> dict:
    """planner 이후 stage의 프롬프트에 싣는 input 부분집합을 만든다.

    input.json은 성격이 다른 둘을 한 파일에 나른다. `brief`는 planner에게 주는 기획
    지시(무엇을 어떤 범위로 만들라)이고, `metadata`는 하류가 실제로 쓰는 제작 설정
    (어떤 컴포넌트를 쓰는가, 어떤 style reference를 따르는가)이다.

    planner 산출물이 스토리보드와 하류 사이의 계약이므로, planner 이후로는 그것이
    유일한 요구사항 원본이다. 기획 지시를 계속 실으면 "계획이 맞나 요청이 맞나"라는
    분쟁이 생겨 그 계층이 무너진다. 같은 이유로 content_eval은 input을 아예 받지 않는다
    (`stages/content_evaluator.py`).

    실측으로 확인된 것이다 — 하류 프롬프트 어느 곳도 `brief`를 참조하라고 지시하지 않는데
    `brief.user_request`에는 구현 범위와 개수를 지정하는 planner 대상 문장이 들어 있었다.
    지시받지 않은 요구사항이 컨텍스트에만 떠 있으면 어느 stage가 그것을 읽었는지조차
    사후에 알 수 없다.

    차단은 페이로드 계약이지 격리가 아니다. stage는 input.json을 직접 열 수 있으므로
    실제로 열었는지는 `audit_agent_access.py`로 사후에 본다.
    """
    return {key: input_data[key] for key in DOWNSTREAM_INPUT_KEYS if key in input_data}
