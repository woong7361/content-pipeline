# Speech Bubble

- Type: `ui_component`
- Role: 캐릭터 옆에 붙는 대사 말풍선
- Status: `candidate`
- Source: `production/1-2/08/index.html` `.speech`, `.repair-bubble-nav`
- Final output: inline into `output/index.html`
- Slots:
  - `text`
  - optional `nav` — 대사 아래 진행 버튼(`[data-action="next"]`)
- States:
  - hidden
  - visible
- Required classes:
  - `.c-speechBubble`
  - `.left-speaker` or `.right-speaker` or `.top-speaker`
- State: `data-state="hidden | visible"`, nav는 네이티브 `hidden` 속성
- Position: `--speech-side-x`, `--speech-face-y` CSS 변수로 화자 옆에 붙인다
- Runtime API:
  - `CommonSpeechBubble.show(el, text, { next })`
  - `CommonSpeechBubble.hide(el)`
  - `CommonSpeechBubble.setText(el, text)`
  - `CommonSpeechBubble.setNext(el, label)` — 문구를 주면 켜고, `null`이면 끈다
  - event `common:speechnext` — 진행 버튼을 누르면 말풍선에서 올라온다
- Use when:
  - 캐릭터 대사
  - 짧은 feedback 대사
  - 다음으로 넘어갈 곳이 대사 자체인 화면
- Avoid:
  - 긴 설명문
  - 문제 본문
  - 화면 하단 자막 카드

## 진행 버튼

대사를 읽고 나서 다음으로 넘어가야 하는 화면에서, 말풍선 **아래**에 진행 버튼을 둘 수 있다.
버튼이 없으면 학습자는 대사가 끝난 것인지 화면이 멈춘 것인지 구분하지 못한다.

- 기본은 꺼짐이다. `setNext(el, "다음 ▸")`로 켜고 `setNext(el, null)`로 끈다.
- 문구는 상황을 말한다 — 다음 대사가 있으면 `다음 ▸`, 마지막이면 `닫기`.
- **버튼 클릭은 말풍선까지 버블링된다.** 말풍선 전체를 진행 표면으로 쓰는 콘텐츠는
  자기 클릭 핸들러만 두면 되고, 버튼만 따로 듣지 않는다.
  버튼만 진행 표면인 콘텐츠는 `common:speechnext`를 듣는다. 둘 다 듣지 않는다.
- `setText`는 `nav`를 건드리지 않는다. 대사만 갈아끼워도 버튼 상태는 유지된다.
- 버튼은 자체 art를 갖지 않는다. 토큰(`--accent`, `--bubble-line`, `--bubble-ink`)으로만 성립한다.
