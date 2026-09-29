from __future__ import annotations

from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
LESSON_CONTRACT = PROMPTS_DIR / "lesson_contract.md"
ASSET_SPEC_CONTRACT = PROMPTS_DIR / "asset_spec_contract.md"


def load_lesson_contract() -> str:
    """lesson.json을 산출물로 삼는 stage가 지키는 계약을 읽는다."""
    return LESSON_CONTRACT.read_text(encoding="utf-8")


def with_lesson_contract(system_prompt: str) -> str:
    """stage system prompt 뒤에 lesson 계약을 잇는다. 충돌 시 계약이 우선한다."""
    return f"{system_prompt}\n\n{load_lesson_contract()}"


def load_asset_spec_contract() -> str:
    """그림을 계획하는 단계와 만드는 단계가 공통으로 지키는 규격을 읽는다."""
    return ASSET_SPEC_CONTRACT.read_text(encoding="utf-8")


def with_asset_spec(system_prompt: str) -> str:
    """stage system prompt 뒤에 그림 규격을 잇는다.

    계약서 전문은 lesson.json 을 쓰는 단계에만 실린다. 그래서 그림을 **계획하는** 단계가
    계약서를 한 줄도 못 본 채 규격을 다시 정하는 일이 있었다(2026-09-23, 4-1/03 —
    asset-plan.json 이 인물을 "허리 위까지만"으로 지시해 계약서와 정반대가 됐다).
    규격 중 그림에 해당하는 부분만 따로 떼어 양쪽에 싣는다.
    """
    return f"{system_prompt}\n\n{load_asset_spec_contract()}"
