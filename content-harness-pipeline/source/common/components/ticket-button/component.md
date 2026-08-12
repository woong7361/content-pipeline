# Ticket Button

- Type: `ui_component`
- Role: 다음 단계로 넘어가는 진행·전환 CTA 버튼
- Status: `candidate`
- Source: `production/1-2/08/index.html` `.cta.activity-cta`
- Final output: inline into `output/index.html`
- Assets: 없음. **이 컴포넌트는 이미지를 소유하지 않는다**
- Requires art:
  - `--cta-body` — 버튼 몸체 표면. **선택**. 안 만들면 `base.css` 토큰으로 만든 알약 버튼으로 성립한다. 만들면 문구가 얹힐 안쪽 면을 비우고 투명 배경으로 그린다
- Slots:
  - `label`
- States: `:hover`, `:active`, 네이티브 `disabled`
- Runtime API:
  - `CommonTicketButton.setLabel(button, label)`
- Position: 컴포넌트가 `position:absolute`와 `z-index:var(--z-interactive)`를 갖는다.
  사용처는 `left`/`top`만 준다. `position`을 덮어써 `static`으로 만들면 배경 뒤로 깔린다.
- Text policy: HTML text overlay
- Use when:
  - 한 씬 안에서 같은 라벨이 반복되는 진행 버튼
  - 라벨이 콘텐츠에 따라 갈리는 CTA
- Avoid:
  - 문제 보기 카드
  - 긴 설명판
  - **씬을 여닫는 CTA** — 그 씬을 특정하는 문구는 이미지에 굽는다

## 이미지를 소유하지 않는 이유

버튼 몸체 art는 **콘텐츠마다 세계관이 달라 재사용 대상이 아니다.**
`source/common/craft-examples`가 도장에 대해 "콘텐츠 세계관이 다르면 도장도 그 세계의 물건이어야 한다"고
말하는 것과 같은 이유다. 학교 담장 차시의 크림·갈색 알약을 도서관 차시에 그대로 쓰면 그 화면만 팔레트가 어긋난다.

특정 선생님 art를 `common`에 두지 않는다는 규칙(`CLAUDE.md`의 "여기 두지 않는 것")도 같은 곳을 가리킨다.

상태는 스프라이트 프레임이 아니라 CSS(`transform`, `filter`)로 낸다.
프레임을 쓰면 **문구를 구운 CTA에서 프레임마다 글자를 다시 그려야 하고 누를 때 글자가 어긋난다.**
그래서 굽는 CTA도 이 컴포넌트를 그대로 쓸 수 있다 — `--cta-body`에 그 이미지를 주면 된다.
굽기 판정은 `prompts/planner_system.md`의 "이미지 안의 텍스트(가변 vs 고정)" 절이 정한다.
