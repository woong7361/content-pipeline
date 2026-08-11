# Feedback Layer

- Type: `feedback_component`
- Status: `candidate`
- Source: `production/1-2/08/index.html` `showStamp`, `showFeedback`, `showWrongFeedback`
- Assets:
  - `assets/feedback-stamp-correct.webp`
  - `assets/feedback-stamp-wrong.webp`
- States: class `show` (도장 이미지는 `data-correct-src` / `data-wrong-src`에서 교체)
- Runtime API:
  - `CommonFeedbackLayer.showStamp(el, "correct" | "wrong", { hold })` — `hold: false`면 900ms 후 자동 숨김
  - `CommonFeedbackLayer.hideStamp(el)`
- Scope: 현재는 stamp만 담당한다. pose swap과 center effect는 아직 콘텐츠 쪽에 있다.
- Use when:
  - 정답/오답 판정
  - 짧은 캐릭터 reaction
- Avoid:
  - 긴 해설
  - 다음 문제 진행을 막는 수동-only feedback
