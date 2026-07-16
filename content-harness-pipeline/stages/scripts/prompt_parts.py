from __future__ import annotations

from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
COMMON_HTML_CONTRACT = PROMPTS_DIR / "common_html_contract.md"
ASSET_EXAMPLES = PROMPTS_DIR / "asset_examples.md"
ASSET_EXAMPLES_DIR = PROMPTS_DIR / "asset_examples"


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


def load_asset_examples() -> str:
    """글자를 이미지에 굽는 asset의 완성도 기준을 예시 이미지로 넘긴다.

    planner_system.md는 "도장 글자는 도장 면 안에 새겨지고, 타이틀 글자는 장식과 얽힘"을
    이미 말로 규정하지만, 그 합격선 자체는 말로 전달되지 않는다. 예시는 새 규칙이 아니라
    기존 규칙의 기준점이므로 run마다 변하지 않고, common_html_contract와 같은 층에 둔다.

    우선순위가 identity_context와 반대라는 점이 이 파일의 핵심이다. identity_context는
    같은 인물을 재현해야 하므로 이미지가 텍스트를 이기지만, 예시는 art_direction이
    이미지를 이겨야 한다. 명시하지 않으면 모델이 identity_context 습관대로 예시의
    팔레트와 모티프를 복제해, run마다 새로 정한 art_direction을 덮어쓴다.
    """
    return ASSET_EXAMPLES.read_text(encoding="utf-8")
