# Feedback Layer

- Type: `feedback_component`
- Status: `candidate`
- Source: `production/1-2/08/index.html` `showStamp`, `showFeedback`, `showWrongFeedback`
- Final output: inline into `output/index.html`
- Assets: 없음. **이 컴포넌트는 이미지를 소유하지 않는다**
  - 도장 art는 콘텐츠마다 세계관이 달라 재사용 대상이 아니다.
    `source/common/craft-examples/stamp-lettering`이 "콘텐츠 세계관이 다르면 도장도 그 세계의 물건이어야 한다"고
    적고 있고, 그 규칙을 이 컴포넌트가 어기고 있었다.
  - 사용처가 생성한 도장 경로를 `data-correct-src` / `data-wrong-src`로 준다.
    정답과 오답은 **완전히 별개의 asset**이다. 한 장을 CSS `filter`로 색만 바꿔 쓰지 않는다.
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
