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
