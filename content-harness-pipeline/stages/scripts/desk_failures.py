"""차시 작업대 작업이 실패했을 때 로그에서 **사람이 할 일**을 찾아 한 줄로 알려 준다.

실측(2026-09-30, 4-1/04) — 그림 굽기가 두 번 "종료 코드 1" 로만 실패했다. 로그 안에는 코덱스 서버가
`refresh_token_invalidated — Your session has ended. Please log in again.` 이라고 답해 있었는데
화면에는 안 나와서 사람이 이유를 몰랐다. 원인은 코드가 아니라 CLI 로그인이었다.

알려진 문구만 본다. 모르는 실패는 빈 문자열 — 화면은 원래대로 "○○ 실패 (종료 코드 N)" 과 로그를 보여 준다.
"""

from __future__ import annotations

from pathlib import Path

# (로그에 이 문구 중 하나가 있으면, 사람에게 보일 이유와 할 일) — 위에서부터 먼저 맞는 것
PATTERNS: list[tuple[tuple[str, ...], str]] = [
    (("refresh_token_invalidated", "token_revoked", "Please log in again"),
     "코덱스 로그인이 끊겼습니다 — 터미널에서 codex login 을 다시 한 뒤 [다시 맡기기]"),
    (("at capacity",),
     "코덱스 서버가 혼잡합니다 — 잠시 뒤 [다시 맡기기]"),
    (("Invalid API key", "Please run /login", "OAuth token has expired", "authentication_error"),
     "클로드 로그인이 끊겼습니다 — 터미널에서 claude 를 실행해 /login 한 뒤 [다시 맡기기]"),
    (("usage limit", "rate_limit_error", "Rate limit reached"),
     "AI 사용 한도에 걸렸습니다 — 한도가 풀린 뒤 [다시 맡기기]"),
    (("timed out in non-interactive", "TimeoutExpired", "TimeoutError"),
     "AI 가 제한 시간 안에 끝내지 못했습니다 — 메모를 나눠 적어 [다시 맡기기]"),
    (("npm ERR!", "npm error"),
     "빌드 명령이 실패했습니다 — 로그 끝부분을 확인하세요"),
]


def reason(log_text: str) -> str:
    for needles, message in PATTERNS:
        if any(needle in log_text for needle in needles):
            return message
    return ""


def reason_from_log(path: Path) -> str:
    if not path.exists():
        return ""
    return reason(path.read_text(encoding="utf-8", errors="replace"))
