# 1-2/08 수정 목록

기준 참고 차시: `production/1-2/01` (같은 선생님 스토리보드). 공통 규칙은 같은 폴더의 `CLAUDE.md` 참조.

상태 표기: `열림` / `진행중` / `완료` / `보류`

## 씬 순서 (현재 index.html)

| # | id | stage 라벨 | 비고 |
| --- | --- | --- | --- |
| 1 | `section_intro` | 수리력 + | 타이틀 로고 + 시작하기 + 작업자 대화 + 담장 수리 연출 |
| 2 | `section_shape_find` | 수리가 필요해요 1 | 교실에서 모양 찾기와 세기 |
| 3 | `section_arithmetic_tutorial` | 수리가 필요해요 2 | 세 수의 덧셈과 뺄셈 |
| 4 | `section_random_problems` | 수리로 해결해요 | 무작위 계산 문제 |
| 5 | `section_free_drawing` | 수리로 해결해요 | 모양으로 자유 그리기 |
| 6 | `section_math_story` | 수리 이야기 | |
| 7 | `section_completion` | 수리 이야기 | |

---

새 작업은 아래에 `## N.` 형식으로 추가하되,
**번호는 이미 쓰인 1~34 다음인 35부터** 이어 쓴다(번호 재사용 금지 — 다른 문서가 번호로 참조한다).

---

## 배경 담장 면 실측값 (stage 1920×1080 좌표)

배경 에셋은 전부 1672×941이고 `.bg{object-fit:cover}`라 stage 환산 배율은 **×1.1483**이다(종횡비가 1.7768 vs 1.7778로 거의 같아 크롭은 무시해도 된다).
**작업 면 위에 요소를 놓을 때 매번 다시 재지 말고 이 표를 쓴다.** 새 배경을 추가하면 여기에 한 줄 더 적는다.

| 배경 | 쓰는 씬 | 색칠 가능한 면 (stage) |
| --- | --- | --- |
| `school-wall-closeup.png` | 씬3 덧셈, 씬2 paint-intro | y **367~878**, x 98~1848 |
| `school-wall-second.png` | 씬3 뺄셈 | y **364~990** |
| `school-wall-problem-scene.png` | 씬4 무작위 문제 | y **380~946** |
| `school-wall-drawing.png` | 씬5 자유 그리기 | x **172~1776**, y **308~877** |

측정 방법: 해당 x 열에서 위→아래로 RGB 차 45 이상인 전이를 찾아 캡(벽돌/파란 띠) 아래 첫 평면과 하단 굽도리 위 마지막 평면을 잡았다. 재검증이 필요하면 같은 방법으로 다시 잰다.

---

## 열려 있는 작업

### 24. `section_shape_find` 공책·도시락이 책상 위에 놓인 느낌이 안 난다

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `findObjects`(`square_notebook` / `square_lunchbox`) / `.find-object`(index.html:271) / `assets/classroom-notebook.png`
- 사용자 지적: "책과 도시락이 책상 위에 놓여져 있는 분위기가 안 산다. 살짝 눕혀 달라."
- 원인은 셋이고, **비중이 큰 쪽은 기울기가 아니라 좌표다.** 배경을 stage(1920×1080) 좌표로 실측한 값:
  1. **좌표가 상판 밖이다.**
     - 가운데 책상 상판 x 580~1051, 뒷모서리 y≈901, 앞모서리 y≈985. 의자 등받이가 x 631~913을 y≈953부터 앞에서 가린다.
     - 오른쪽 책상 상판 x 1243~1636, 뒷모서리 y≈901, 앞모서리 y≈979. 의자 등받이가 x 1381~1616을 y≈956부터 가린다.
     - 현재 `square_notebook` `[860,790,185,185]` → 위쪽 111px가 상판보다 높은 허공.
     - 현재 `square_lunchbox` `[1480,790,185,185]` → 오른쪽 끝 x=1665가 책상 뒷모서리 오른쪽 끝 1636을 29px 넘어간다.
     - 물건을 놓을 수 있는 깨끗한 면은 **뒷쪽 띠(y 901~955) 전폭**과 **의자 옆**뿐이다.
  2. **시점이 안 맞는다.** 배경 책상 상판의 깊이 압축비는 폭 470 : 깊이 84 ≈ **0.18**(하이앵글)인데 `classroom-notebook.png`는 완전 정면 정투영이라 "세워 둔 책"으로 읽힌다. `classroom-lunchbox.png`는 이미 약간 하이앵글이라 상대적으로 낫다.
  3. **접지 그림자가 없다.** `.find-object{filter:var(--ds-sm)}`의 균일 드롭섀도뿐이라 바닥에 닿은 느낌이 안 난다.
- 조치 방향(눕히기 방식은 사용자 결정 대기 — 아래 "확인이 필요한 항목" 참조):
  - 공통: `findObjects`의 두 rect를 상판 폴리곤 안으로 내린다. 좌표는 `findObjects` 한 곳에만 있고 핫스팟이 여기서 파생되므로 rect만 고치면 클릭 영역도 따라온다.
  - 공통: 접지 그림자용 CSS를 만들어 `.find-object`에 적용한다. 3번 공(`circle_ball`)도 같은 증상이라 함께 적용한다.
  - 눕히기: A안(CSS `transform:perspective(900px) rotateX(50deg) rotate(-6deg)`, `transform-origin:center bottom`) 또는 B안(공책 에셋을 3/4 하이앵글로 재생성) 중 택일.
- **주의(A안을 고를 경우):** `problem.md` `[overlay-plane-perspective-mismatch]`의 2026-07-13 조치와 같은 해법이지만, 그때 대상은 "얇은 사진"이었고 이번은 두께가 있는 사물이다. 정면 정투영 raster에 `rotateX`를 걸면 측면이 사라져 종이 한 장이 된다. **도시락은 입체라 `rotateX`가 몸통을 뭉개므로 A안을 적용하면 안 된다.** 또 핫스팟 rect는 축정렬이라 시각 위치와 어긋나므로 rect를 따로 보정해야 한다.
- **주의:** 도시락을 상판 안(x 1243~1636)으로 옮길 때 23번의 `#shapeSceneStudent` 실루엣(stage x 1165~1296 / y 509~880)과의 간격을 다시 본다.

### 25. `section_shape_find`의 삼각 깃발을 다른 삼각형 오브젝트로 교체

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `findObjects.triangle_pennant` / `searchQuestions.q_triangle_find_two` / `assets/classroom-pennant-flag.png`
- 사용자 지적: 깃발이 어색하다. 다른 삼각형 오브젝트가 좋겠다.
- 진단: 문제는 삼각형 자체가 아니라 **교실 실재성**이다. 벽에 짧은 막대 삼각 깃발이 홀로 박혀 있는 교실은 없어서 "사물"이 아니라 "붙여 놓은 도형 스티커"로 보인다. 삼각자와 나란히 떠 있어 둘이 같은 인상을 준다.
- 후보 비교:

  | 후보 | 교실 실재성 | ▲ 인지 | 삼각자와 구분 | 배치 |
  | --- | --- | --- | --- | --- |
  | **트라이앵글(악기)** ← 1순위 | 높음(1학년 음악 교구) | 명확(외곽선이 곧 삼각형) | 은색 금속 vs 주황 나무, 완전 구분 | 벽 고리. **현재 깃발 rect `[1490,220,180,180]` 그대로 사용 가능** |
  | 고깔모자 | 중간(상시 비치 아님) | 가장 쉬움(면이 크고 알록달록) | 형태·색 구분 좋음 | 사물함 위/책상 위로 좌표 이동 필요 |
  | 삼각 가랜드(만국기) | 가장 높음 | 명확 | 좋음 | **부적합** — 보통 5~6장이 줄지어 있어 "▲ 2개 찾기"와 충돌 |
  | 삼각김밥 | 낮음(교실 아님) | 김에 갇혀 약함 | — | 도시락과 주제 중복 |

- 함께 고칠 곳: `findObjects`의 id `triangle_pennant` → 새 id, `searchQuestions`의 `q_triangle_find_two.answers` 배열, `alt` 텍스트, 에셋 파일명. 새 에셋은 `1-2/01/lesson.json`의 `artDirection`을 읽어 프롬프트에 반영한다(기억으로 재작성 금지).
- **영향 없음 확인:** 카운트 씬(`countQuestions`의 `q_count_triangle`, 답 2)은 CSS `.paint-shape`로 그리므로 찾기 씬 오브젝트 교체와 무관하다.

### 26. `section_shape_find` 정답 뒤 아무 데나 누르면 진행 경로가 사라지는 데드엔드

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `renderSearch`(searchArea.onclick) / `registerSearchWrong` / `showWrongFeedback` / `resetFeedbackOverlay` / `showFeedback`
- 사용자 지적: "동그라미 세모 네모 선택이 틀리면 다음으로 못 넘어가는 버그가 있어."
- **재현 확인 (headless Chrome + CDP, 2026-08-03).** 오답을 1회만 눌러도, 3회 눌러도 진행은 정상이다. 막히는 것은 **정답 직후의 오답 처리**다.
  1. 정답 2개를 찾으면 `selectHotspot`이 `setHotspotsEnabled(false)`로 hotspot 6개를 전부 `disabled`로 만들고, `showFeedback(shapeMark, '정답입니다.', advanceSearch)`로 진행 경로를 `#feedbackSpeech` 클릭 **하나에만** 건다.
  2. 그런데 `renderSearch`가 건 `searchArea.onclick`(장면 전체를 오답 판정 영역으로 삼는 핸들러)은 정답 이후에도 살아 있다.
  3. 말풍선이 아닌 곳을 한 번 누르면 → `registerSearchWrong` → `showWrongFeedback` → `resetFeedbackOverlay()`가 `feedbackContinueAction=null`로 만들고 말풍선을 지운다.
  4. 이 시점에 **진행 가능한 표면이 0개** — hotspot 전부 disabled, 말풍선 소멸. 새로고침이나 디버그 패널 외에 탈출 경로가 없다.
- 재현 로그(요약): 정답 2개 → `feedbackSpeech {cls:'…', txt:'잘 찾았어요!다음 ▸', hasOnclick:true}` → `#shapeSearch` 1회 클릭 → `{cls:'… hidden', txt:'', hasOnclick:false, hotspotsDisabled:[true×6]}`.
- 조치 방향(둘 다 넣는 것을 권장 — 하나만으로도 막히지만 원인이 둘이다):
  - (a) **씬4의 `randomAwaitingContinue` 패턴을 그대로 가져온다.** 문항이 정답 처리된 뒤에는 `registerSearchWrong`이 즉시 `return`하도록 "해결됨" 플래그를 둔다. 씬4의 `judgeRandomChoice`·`judgeRandomKey`가 이미 같은 가드를 갖고 있어 그쪽은 이 버그가 없다.
  - (b) `showWrongFeedback`이 **armed된 `feedbackContinueAction`을 지우지 않게** 한다. 지금은 `resetFeedbackOverlay()`를 무조건 부르므로 어느 씬에서든 같은 사고가 날 수 있다.
- **주의:** 씬3(계산)·씬4는 정답 시 `setKeypadEnabled(false)`라 오답 입력 자체가 불가능해 지금은 증상이 안 난다. (b)만 고치고 (a)를 빼면 씬2만 우연히 살아나는 형태가 된다.
- **주의:** `searchArea.onclick`은 17번 이후 "hotspot 밖 클릭도 오답으로 센다"는 요구로 들어온 것이다. 핸들러를 통째로 떼면 그 요구가 깨진다. 끄지 말고 **게이트만** 건다.
- 연관: `problem.md` `[content-flow-state-scaffolding-regression]`(7회) — 17번과 같은 씬에서 같은 성격의 데드엔드 재발.

### 27. 피드백 말풍선이 캐릭터에서 너무 멀리 떨어져 있다

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `.speech.feedback-speech`(index.html:430) / `.feedback-character`(index.html:426)
- 사용자 지적: "피드백 시 캐릭터 옆에 `정답` 말풍선이 너무 멀리 떨어져 있다."
- 실측(stage 좌표):
  - `.feedback-character{left:80px;bottom:-10px;width:360px;height:590px}` → 박스는 x 80~440 / y 500~1090. `object-fit:contain`이라 그림은 360×540(y 525~1065)로 들어간다.
  - `teacher-praising.png`(1024×1536)의 알파 bbox는 x 444~786 / y 66~1456 → **눈에 보이는 인물은 x 236~356 / y 548~1037**. 즉 박스 폭 360px 중 실제로 그려진 것은 **120px**뿐이고, 오른쪽 84px은 투명이다.
  - `.speech.feedback-speech{left:500px;top:250px}` → 꼬리 끝이 약 (466, 300). 인물 오른쪽 끝에서 **110px 밖**, 머리 위로 **약 260px**.
- 왜 이렇게 됐나: 17번 주석이 "앵커는 피드백 캐릭터(x 80~440)를 덮지 않는 위치로 옮겼다"고 적고 있다. **박스 좌표(440)를 기준으로 피했기 때문에** 실제 인물(356)에서 84px 더 밀려났다.
- 참고(정상 조합): `.character.left`(박스 x 62~502, 인물 x 253~400) + `.speech.left-speaker{left:390px;top:220px}` → 꼬리 x 356이 인물 x 범위 **안**에 들어간다. 이 씬들에 대해서는 지적이 없었다.
- 조치 방향: `.speech.feedback-speech`의 `left`/`top`을 인물의 알파 bbox 기준으로 다시 잡는다. 꼬리(`left - 34px`)가 인물 x 236~356 안에 들어오고 머리 위 여백이 100px 안쪽이 되도록. **`.speech` 공통 규칙(폭·패딩)은 건드리지 않는다** — 15번의 자동 크기 조정이 깨진다(의존 관계 참조). 바꿔도 되는 것은 앵커 좌표뿐이다.
- **주의:** `#feedbackSpeech`는 `showFeedback`이 띄우고 화자는 항상 `teacher-praising.png`다. `showWrongFeedback`은 말풍선을 띄우지 않으므로(`sp.classList.add('hidden')`) `student-thinking.png`의 다른 bbox는 고려하지 않아도 된다.

### 28. `section_arithmetic_tutorial` 도형이 3줄이면 담장 위로 삐져나온다

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `.work-area`(index.html:284) / `#arithShapes`
- 사용자 지적: "모양이 3줄이 되면 담장 바깥으로 모양이 삐져나온다."
- 실측: `.work-area{left:150px;top:250px;width:1050px;height:570px;grid-template-columns:repeat(5,1fr);align-content:center}` + `.paint-shape{height:150px}` + `gap:18px`.
  - 10개(2행) → stage y 376~694. 담장 면(367~878) 안. 그래서 지금까지 안 보였다.
  - 12개(3행) → stage y **292~778**. 1행 상단이 담장 벽돌 면 위 캡·하늘로 **75px** 올라간다.
- 3행이 되는 문항: `q_add_10_2` / `q_add_7_3_2` / `q_subtract_12_2` / `q_subtract_12_2_3` (전부 `count:12`).
- 조치 방향: `.work-area`의 세로 앵커를 담장 면 중앙에 맞춘다. 면 중앙은 (367+878)/2 = **622**, 현재 박스 중앙은 250+285 = 535 → `top`을 약 **88px 내린다**(250 → 338). 그러면 3행 380~866, 2행 463~781로 둘 다 면 안에 들어간다.
  - 3행 높이(486px)는 담장 면 높이(511px)보다 작으므로 **도형 크기를 줄일 필요는 없다.** 좌표만 내리면 된다.
  - 가로는 x 150~1200으로 이미 면(98~1848) 안이다.
- **주의:** `.work-area`는 `#paintIntroVisual`·`#countShapes`·`#arithShapes`·`#randomShapes`가 공유한다(22번 의존 관계). `#randomShapes`는 `#randomShapes{left:290px;top:250px;width:1340px;height:560px}`로 이미 개별 오버라이드가 있고 배경도 다르므로(면 y 380~946), **공통 `.work-area`를 옮기면 씬2·씬4까지 같이 움직인다.** 씬2(`school-wall-closeup.png`)는 같은 배경이라 함께 내려가는 게 맞고, 씬4는 자기 오버라이드를 함께 손봐야 한다(29번과 같이 처리).

### 29. `section_random_problems` — 유형 4종 전부 출제 + 그림과 문제를 같이 보여주기

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `startRandomEngine`(`randomSequence`) / `renderRandom` / `playRandomShapeIntro` / `clearRandomShapeIntro` / `#section_random_problems.shape-intro #randomPanel`(index.html:397) / `#randomShapes`(index.html:398) / `#randomWorkProgress`
- 사용자 지적: "A: 10이 되는 덧셈, B: 10에서 뺄셈, C: 세 수의 덧셈, D: 세 수의 뺄셈 이렇게 4개가 나와야 하는데 3개가 나오고 있고, 초등학생이 알 수 있도록 그림이 같이 보여져야 하는데 그림이 보여지고 사라진다. 같이 볼 수 있도록 표시해줘야 한다. 담장에 생성 규칙은 input.json을 참조해야 한다."

**(29-a) 유형이 3개만 나온다**

- 현재: `randomSequence = Math.random()<.5 ? [0,2,3] : [1,4,5]` — **A+C 묶음이나 B+D 묶음 중 하나만** 뽑아 3문항으로 끝난다.
- `randomType` ↔ `staticExamples` 인덱스 매핑: `0`=A(보기 선택) / `1`=B / `2`=C-1단계 / `3`=C-2단계 / `4`=D-1단계 / `5`=D-2단계.
- 원문 근거(`dfbc1027_input.json`의 `brief.md_path` = 워크스페이스 최상단 `수리력 1차_1학년 2학기 8차시 (백승용) 723 요청.md`, **325~394행**):
  - 개요에 A·B·C·D 4유형이 모두 명시돼 있다.
  - 예시화면 문구도 A·B·C(2단계)·D(2단계) 전부 적혀 있다 → 화면 수로는 **6개**.
  - 생성 규칙 표(391~394행):

    | 유형 | 생성 규칙 | 현재 구현(`startRandomEngine`) |
    | --- | --- | --- |
    | A `10이 되는 덧셈 찾기` | `A + B = 10`, A는 1~9 무작위, `B = 10 − A`. 보기 3개(정답 1 + `A + 무작위(B 제외)` 2) | `add.a=1~9`, `add.b=10-a`, 오답 2개 — **일치** |
    | B `10에서 빼기` | `10 − A = ( )`, A는 1~9 무작위 | `subtract.c = 1~9` 사용 — **일치** |
    | C `세 수의 덧셈` | `A + B + C`, A는 1~9, `B = 10 − A`, C는 1~9 | `add.{a,b,c}` — **일치** |
    | D `세 수의 뺄셈` | `A − B − C`, B는 1~9, `A = B + 10`, C는 **1~8** | `subtract.a=b+10`, `subtract.c=1~8` — **일치** |

  - **즉 생성 규칙 자체는 원문과 맞다. 어긋난 것은 "몇 개를 내느냐"뿐이다.** `randomSequence`를 `[0,1,2,3,4,5]`로 바꾸는 것이 최소 수정이다.
- 왜 3개가 됐나: 2026-07-31 `content-flow-state-scaffolding-regression` 조치에서 "A→같은 operand를 쓰는 C, 또는 B→같은 operand를 쓰는 D 묶음 하나를 선택"하도록 **의도적으로 좁힌** 것이다. 되돌릴 때 그 조치가 지키려던 것(단계 간 operand 공유)은 유지해야 한다 — `randomBundle`은 그대로 두면 A·C가, B·D가 각각 같은 수를 쓴다.
- **함께 고쳐야 하는 곳(빠뜨리기 쉬움):**
  - `#randomWorkProgress`는 마크업에 도형 **3개**가 하드코딩돼 있다(index.html:533). `updateRandomWorkProgress`가 `index < randomCompletedCount`로 칠하므로 문항이 6개가 되면 3개까지만 채워지고 멈춘다.
  - `setProgress(72 + randomCompletedCount*4)`는 6문항이면 72→96이 되는데, 다음 씬(`resetDrawingIntro`)이 84로 되돌린다. **진행률이 역행한다.** 씬4 구간을 72~82 정도로 재배분한다.
  - `armRandomContinue`의 `aria-label`이 마지막 문항일 때 `모양으로 자유 그리기`로 바뀌는 분기(`randomSequenceIndex===randomSequence.length-1`)는 길이에 의존하므로 자동으로 따라온다.
- (선택) 원문 387행: "`A + B = 10` 외에 `B + C = 10`이나 `A + C = 10`이 되는 무작위 문제도 가능하면 해달라"는 **감사 요청(필수 아님)**이다. 범위에 넣을지는 아래 확인 항목 참조.

**(29-b) 그림이 보였다가 사라진다**

- 현재 흐름: `renderRandom` → `playRandomShapeIntro(script, revealQuestion)` → 연출 종료 → `finishRandomShapeIntro` → `clearRandomShapeIntro()`가 `#randomShapes`를 **숨기고** → 그제서야 `revealQuestion()`이 식·키패드를 연다. 그림과 문제가 **한 화면에 절대 공존하지 않는다.**
- 구조적 원인: `#randomShapes`(left 290 / top 250 / 1340×560)와 `#randomPanel`(left 245 / top 205 / 1040×700)이 **완전히 겹쳐** 있어서, 연출 중에는 `#section_random_problems.shape-intro #randomPanel{visibility:hidden}`으로 패널을 가릴 수밖에 없다. 그림을 남기려면 **좌표를 다시 나눠야 한다.** `visibility:hidden` 한 줄만 지우면 겹쳐서 둘 다 못 읽는다.
- 조치 방향: 담장 면(`school-wall-problem-scene.png` → stage y 380~946)을 상하 또는 좌우로 쪼갠다.
  - 도형은 연출이 끝나도 그대로 두고(`clearRandomShapeIntro`에서 숨기지 않음), 문제 패널을 도형과 안 겹치는 자리로 옮긴다.
  - 도형 개수는 최대 `base + add` = D-2단계 기준 최대 19개까지 나올 수 있다(`subtract.a` 최대 19). **최대 개수로 줄 수를 계산해 면 안에 들어가는지 확인한다**(28번과 같은 실수를 반복하지 않기 위함).
- **주의:** `#randomShapeSkip`(연출 건너뛰기 탭 레이어)은 연출 중에만 뜬다. 도형을 상시 표시로 바꾸면 이 레이어가 문제 패널 위를 덮지 않도록 `clearRandomShapeIntro`에서의 숨김 처리를 그대로 유지한다.

### 30. `section_free_drawing` — 크기·기울기 조절 추가 + 그리기 영역을 담장 안쪽으로

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `.paint-tools`(index.html:352) / `#drawingCanvas`(index.html:358) / `.drawn-shape`(index.html:360) / `drawingCanvas.onclick` / `drawingState` / `renderCompletedMural`
- 사용자 지적: "그리기 툴에 도형 크기 변경 실린더와 기울이기 실린더가 추가적으로 있으면 좋겠다. 그리고 담장 바깥에 이미지가 짤리기도 하는데 짤리지 않도록 담장 안쪽에 그리기 가능한 영역을 약간 줄이면 좋겠다."
- **가정:** "실린더"는 **슬라이더(`<input type="range">`)** 로 읽었다. 다르면 알려 달라(아래 확인 항목).

**(30-a) 크기·기울기 슬라이더**

- 지금 `.paint-tools`에는 모양 3개 + 색 4개 버튼만 있다. `.drawn-shape{width:150px;height:150px;transform:translate(-50%,-50%)}`로 크기가 고정이고 회전은 없다.
- 조치 방향: `drawShape`·`drawColor`와 같은 자리에 `drawSize`·`drawTilt` 상태를 두고, 생성 시 `width/height`와 `transform: translate(-50%,-50%) rotate(Ndeg)`에 반영한다.
- **주의(중요):** `drawingState()`가 지금 저장하는 것은 `{shape, color, left, top}`뿐이고 `renderCompletedMural()`이 이 값으로 씬7 담장에 다시 그린다. **크기·기울기를 저장 항목에 같이 넣지 않으면 완료 화면에서 그림이 달라진다.** 저장·복원 양쪽을 함께 고친다.
- **주의:** `.drawn-shape`는 `.paint-shape`와 항상 같이 붙고 `.paint-shape.triangle`은 `clip-path`로 그려진다. `rotate`는 clip-path와 문제없지만, 22번의 `--shape-stroke` 안쪽 폴리곤 계산은 **정삼각형 비율 전제**라 `width≠height`로 늘리면 선 두께가 어긋난다. 크기 슬라이더는 **가로세로 같은 배율**로만 건다.

**(30-b) 담장 바깥 잘림**

- 실측: 담장 면은 stage x **172~1776** / y **308~877**인데 `#drawingCanvas`는 x 390~1760 / y **275**~815 → 위로 **33px** 튀어나와 있다.
- 더 큰 원인은 `overflow:hidden` + 중앙 정렬이다. `.drawn-shape`는 150px를 클릭점 중심에 놓으므로 **가장자리에서 최대 75px가 캔버스 밖으로 나가 잘린다.** 스크린샷에서 네 모서리 도형이 전부 반쪽으로 잘리는 것을 확인했다.
- 조치 방향(둘 다 필요):
  - 캔버스 박스를 담장 면 **안쪽으로** 넣는다. 예: `top:320px`(면 상단 308 + 여유), `height` 축소로 하단 ≤ 865. 좌측은 `.paint-tools`(x 38~348)와 겹치지 않게 390 유지, 우측은 1700 근처로 당긴다.
  - 클릭 좌표를 **도형 반지름만큼 clamp**한다. `drawingCanvas.onclick`에서 `(e.clientX-r.left)`를 `[halfW, r.width-halfW]`로 가둔 뒤 %로 환산한다. 30-a로 크기가 가변이 되면 `halfW`도 그때의 크기를 따라야 한다.
- **주의:** `#completedMuralPreview`(씬7)는 `left:390px;top:275px;width:1370px;height:540px`로 **`#drawingCanvas`와 같은 값이 하드코딩**돼 있다(index.html:433). 캔버스 좌표를 바꾸면 여기도 같이 바꿔야 저장된 그림이 같은 자리에 복원된다. 씬7 배경은 `school-wall-completed.png`라 담장 면 좌표를 따로 실측해야 한다(위 실측표에 아직 없다).

### 31. `section_free_drawing` — 완료 버튼 라벨과 요약 도형 개수 제한

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `#drawingDone`(index.html:545) / `renderDrawingSummary` / `.drawing-summary`(index.html:431)
- 사용자 지적: "3가지 이상을 하면 아래 버튼이 나오는데 글이 `버튼`이 아니라 `완성하기`로 바꿔주고, `그림을 완성했나요?` 아래 도형이 6개 이상 나오면 넘친다. 5개 이상이면 `...`으로 표시되도록 바꾸자."

**(31-a) `버튼` → `완성하기`**

- 마크업이 문자 그대로 `<button … id="drawingDone" aria-label="그림 완성하기">버튼</button>`이다.
- 이건 실수가 아니라 **원문 보존 계약의 부작용**이다. 원문 md 405~410행의 UI 요소 표에 `| 3 | 버튼 | 버튼 |`이라고 적혀 있어 "UI 요소 이름"이 그대로 라벨이 됐고, 2026-07-31 critique가 네 번 지적했지만 매번 "planner에 없는 새 문구는 못 넣는다"며 `aria-label`만 붙이고 보이는 글자는 `버튼`으로 유지했다(`problem.md` `[content-flow-state-scaffolding-regression]`).
- **이번에 사용자가 직접 `완성하기`로 바꾸라고 지시했으므로 production 사본에서는 사용자 지시가 원문 계약보다 우선한다.** 바꾸고 `aria-label`은 `그림 완성하기` 그대로 둔다.

**(31-b) 요약 도형 넘침**

- 실측: `.confirm-panel{width:850px;padding:55px}` → `.drawing-summary`의 clientWidth **728px**. `.drawing-summary .paint-shape{width:112px;flex:0 0 112px}` + `gap:18px`.
  - 5개 = 632px → 들어감. 6개 = **762px → 34px 넘침**(실측 scrollWidth 745).
  - `renderDrawingSummary`는 `shape-color` 조합의 중복만 제거하므로 **3모양 × 4색 = 최대 12개**까지 늘 수 있다. 12개면 1542px로 패널을 완전히 벗어난다. 상한이 없다는 것이 진짜 문제다.
- 조치 방향: `renderDrawingSummary`에서 표시 개수 상한을 두고 초과분은 `…` 한 칸으로 대신한다. 사용자 문구("5개 이상이면 `...`")를 그대로 따르면 **4개까지 표시 + `…`** 다.
- 참고: 물리적으로는 5개까지 들어간다(632 ≤ 728). "5개까지 표시 + `…`"로 해도 700px 내외라 맞는다. 어느 쪽으로 할지는 아래 확인 항목.

### 32. `section_math_story` 인트로 판에 ● ■ ▲ 가 없다

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `#storyIntroBoard`(index.html:552) / `storyBeats[0]` / `.story-intro-board`(index.html:405)
- 사용자 지적: "`모양을 길에서 본 적 있나요?` 위에 아무 모양도 안 나오는데 여기에 동그라미 세모 네모가 필요하다. 원문에 그렇게 나와 있다. 그 다음 화면에 나오는 게 아니라."
- 원문 근거(`…723 요청.md` 449~451행, 예시화면 문구): `수리 이야기<br><br>모양을 길에서 본 적이 있나요?` → `● ■ ▲` → `무슨 표지판일까요?`
- 현재 구현: `● ■ ▲`가 인트로 판이 아니라 **다음 화면의 `storyBeats[0]`**(`.story-card`, `{text:'● ■ ▲', sign:-1}`)로 밀려 있다. 스크린샷으로 인트로 화면에 도형이 전혀 없는 것을 확인했다.
- 조치 방향: `#storyIntroBoard` 안(문구 **위**)에 도형 3개를 넣는다. **22번 이후 도형은 raster가 아니라 `.paint-shape` CSS로 그린다** — `<div class="paint-shape circle green">` 식으로 `#paintIntroVisual`(index.html:503)과 같은 조합을 쓴다.
  - `.story-intro-board`는 `display:grid;place-items:center`에 `height:220px`, `padding:33px 80px 59px`이라 도형 줄을 넣으려면 세로 배치(`grid-auto-flow:row` + gap)와 높이 재검토가 필요하다. 배경 에셋(`story-roadside-info-board.png`)이 1420×220 원본 그대로 쓰이는 곳이라 **높이를 늘리면 이 판도 늘어난다**(33번의 `.story-card`와 정반대 상황이니 같이 본다).
- **주의:** `● ■ ▲`를 인트로로 옮기면 `storyBeats[0]`이 비게 된다. beat 배열 길이가 7 → 6으로 줄면 `setProgress(94+storyIndex)`와 `storyCard.onclick`의 마지막 분기가 함께 움직인다. beat를 지울지, `sign:-1`(표지판 3개 동시 강조) beat로 남길지 정해서 반영한다.
- **19번 주의:** 씬2 `#paintIntroVisual`이 세운 `초록=● / 파랑=■ / 빨강=▲` 매핑이 있다. 인트로 판 도형 색도 여기에 맞춘다.

### 33. `section_math_story` 표지판 설명이 아래로 치우쳐 잘리고 글자가 작다

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `.story-card`(index.html:375) / `.sign-row`(index.html:366) / `assets/story-roadside-info-board.png`
- 사용자 지적: "표지판 설명이 그림 가운데 정렬이 되어 있는 게 아니라 아래로 치우쳐져 있어 잘리고 있고, 글자 크기도 더 키우면 좋겠다."
- 실측:
  - `.story-card{left:310px;bottom:-115px;width:1300px;height:600px;padding:282px 108px 118px;font-size:var(--fs-sm)}` → 카드는 stage x 310~1610 / y **595~1195**. **아래 115px이 무대(1080) 밖이다.**
  - 글 영역은 y **877~1077**, 높이 **200px**뿐.
  - 배경 에셋 `story-roadside-info-board.png`는 **원본 1420×220**인데 `background-size:100% 100%`로 1300×600에 늘려 쓴다(세로 2.7배). 에셋의 크림 면은 비율 y **0.168~0.736** → 카드 기준 y 101~442, stage **696~1037**.
  - **즉 글이 크림 면(696~1037) 가운데가 아니라 하단 끝(877~1077)에 걸려 있다.** 가장 긴 beat(▲ 표지판 — 제목 1줄 + 빈 줄 + 본문 2줄 + 빈 줄 + 마무리 1줄 + `다음 ▸` 버튼 ≈ 360px 이상)는 200px 영역을 넘쳐 화면 아래로 잘린다. 스크린샷에서 마지막 줄 "다녀야 해요."가 잘리고 `다음 ▸` 버튼이 아예 안 보이는 것을 확인했다.
- 조치 방향(순서대로):
  1. **패딩을 크림 면 비율로 다시 잡는다.** 상단 패딩 = `height × 0.168`, 하단 패딩 = `height × (1 − 0.736)`. 지금처럼 손으로 잡은 282/118을 두면 어떤 높이로 바꿔도 계속 어긋난다.
  2. **글이 들어갈 세로 공간을 만든다.** 크림 면 높이는 카드 높이의 **56.8%** 뿐이다. 글자를 키우면(아래 3번) 필요 높이가 더 커진다. `--fs-md`(41px) 기준 6줄 + 버튼 ≈ 400px → 카드 높이가 **약 700px 이상** 필요하다.
  3. **글자 크기를 사다리 한 단계 올린다** (`--fs-sm` 37px → `--fs-md` 41px). 16번 규칙대로 개별 px를 쓰지 말고 사다리를 통해 올린다.
- **막히는 지점(확인 필요):** 카드를 키우면 위로 자라는데 `.sign-row`가 y 275~665에 있어 표지판과 겹친다. 셋 중 하나를 골라야 한다 — (i) `.sign-row`를 위로 올리고 높이를 줄인다, (ii) 카드를 무대 안으로 완전히 넣고(`bottom:-115px` → 0 근처) 높이를 늘린다, (iii) 세로로 긴 안내판 에셋을 새로 만들어 늘어짐 자체를 없앤다. 아래 확인 항목 참조.
- **주의:** `.story-intro-board`(32번)는 **같은 에셋을 원본 비율 1420×220 그대로** 쓰고 있어 문제가 없다. `.story-card`만 늘려 쓰는 것이 원인이므로, 인트로 판까지 같은 값으로 바꾸지 않는다.

### 34. `section_shape_find` 첫 대사의 화자를 선생님으로, 오른쪽에서 나오게

- 상태: 열림 (2026-08-03 접수)
- 대상: `index.html` `shapeDialogues[0]`(index.html:758) / `#shapeDialogue` 정적 마크업(index.html:501)
- 사용자 지적: "`여러 가지 모양으로 그리면 좋겠어요` 대사는 선생님이 할 거야. 오른쪽에서 나오게 해 줘."
- 현재: `['여러 가지 모양으로 그리면 좋겠어요.', 'worker-explaining.png', '오른쪽을 바라보며 열린 손바닥으로 …공사 작업자', 'left']` — **공사 작업자가 왼쪽에서** 말한다.
- 원문 근거: `수리력 1차_1학년 2학기 8차시 (백승용) 723 음성 스크립트.md` 씬2가 화자를 번호로 명시한다(`1. 주인공 / 2. 교사 / 3. 교사 / 4. 주인공`). 요청 md 116~120행의 UI 요소 표도 같다. **사용자 지적이 원문과 일치한다.**
- 조치 방향(두 곳을 같이 고친다 — 하나만 고치면 첫 프레임에 작업자가 번쩍한다):
  1. `shapeDialogues[0]`을 `teacher-explaining.png` / 교사 alt / `'right'`로 바꾼다. alt는 같은 파일이 이미 쓰는 문구를 그대로 복사한다 — `민트색 블라우스를 입고 밝게 미소 지으며 왼쪽 학습 대상을 열린 손으로 안내하는 여 교사`.
  2. 정적 마크업(index.html:501)의 `class="character left"` → `right`, `src`/`alt` → 교사, `class="speech left-speaker"` → `right-speaker`, 안의 텍스트는 그대로.
- 바뀐 뒤 오프닝 4 beat: 교사(우) → 주인공(좌) → 교사(우) → 주인공(좌)로 좌우가 번갈아 서서 오히려 읽기 좋아진다.
- **주의:** `teacher-explaining.png`는 왼쪽을 보고 있어(alt 참조) 오른쪽 배치가 맞다. `.character.right`는 `right:52px`라 좌표를 따로 잡을 필요가 없다.
- **주의(23번):** 오프닝 동안 `#shapeSceneStudent`는 `hideSceneStudent()`로 숨어 있으므로, 화자가 교사가 되어도 인물 중복(23번)은 생기지 않는다. beat 1·3은 여전히 `student-*`이라 이 전제는 유지된다.
- **확인 없이 건드리지 않은 것:** 원문 음성 스크립트 기준으로는 주인공의 `벽화를 어떻게 그려야 되지?`가 **1번**, 이 교사 대사가 **2번**이라 지금 구현은 순서까지 뒤바뀌어 있다. 사용자가 요청한 것은 화자·방향뿐이라 순서는 그대로 뒀다 — 아래 확인 항목 참조.

---

## 확인이 필요한 항목 정리

작업 착수 전 사용자에게 확인할 것.

- **(18·22번) 미참조가 된 에셋을 삭제할지.** 아래 3개는 index.html에서 참조가 0이 됐다. 과거 미참조 에셋은 사용자 확인 후 삭제해 왔다.
  - `shape-tile-body.png` — 22번(도형 CSS화)으로 폐기. 682KB.
  - `classroom-window.png` / `classroom-locker.png` — 18번(공책·도시락 교체)으로 폐기. 합계 2.5MB.
- **(무관) `cta-intro-body.png`도 미참조다.** 이번 작업 이전부터 그랬다. 함께 정리할지 확인 필요.
- **(rule 승격 제안)** `problem.md`에서 승격 기준(5회)을 넘긴 태그가 2026-08-03 기준 셋이다. AGENTS.md에 규칙으로 올릴지 사용자 결정이 필요하다.
  - `[content-scale-too-small]` **13회** (33번으로 +1)
  - `[content-flow-state-scaffolding-regression]` **7회** (26·31번으로 +2) — 5회에서 이미 제안했으나 미결인 채 같은 씬에서 데드엔드가 재발했다.
  - `[bg-anchor-alignment]` **9회** (28·30·33번으로 +3) — 초안에 "배경 위 콘텐츠 박스는 면의 stage 좌표를 실측하고, 개수에 따라 자라는 박스는 **최대 개수 기준**으로 검사한다"를 추가 제안.
- **(30번) "실린더"가 슬라이더가 맞는지.** `<input type="range">` 두 개(크기·기울기)로 읽고 진행할 예정이다. 다이얼/휠 같은 다른 조작기를 뜻한 것이면 알려 달라.
- **(30번) 크기·기울기의 범위.** 권장 — 크기 80~220px(기본 150), 기울기 −30°~+30°(기본 0). 저학년이 조작해도 담장 밖으로 못 나가는 상한이다. 다른 범위를 원하면 지정해 달라.
- **(31-b번) 요약 도형 표시 상한.** 사용자 문구("5개 이상이면 `…`")를 그대로 따르면 **4개 + `…`**. 다만 실측상 5개(632px)까지는 728px 안에 들어가므로 **5개 + `…`**(약 700px)도 가능하다. **권장 4개 + `…`** — 지시 문구와 정확히 맞고 여백도 넉넉하다.
- **(29-a번) 원문 387행의 선택 요청을 범위에 넣을지.** "`A + B = 10` 외에 `B + C = 10`이나 `A + C = 10`이 되는 무작위 문제도 가능하면 해달라"는 필수가 아닌 감사 요청이다. **권장 이번 범위 제외** — 4유형 6문항 복원과 그림·문제 동시 표시가 먼저다.
- **(33번) 표지판 설명 카드를 어떻게 키울지.** 셋 중 택일.
  - (i) `.sign-row`를 위로 올리고(top 275 → 200, height 390 → 330) 카드 높이를 700~760으로 키운다. 비용 0, 에셋 그대로. 표지판이 작아진다.
  - (ii) 카드를 무대 안으로 넣고(`bottom:-115px` → 0) 높이만 키운다. 표지판과 겹친다 — 단독으로는 불충분.
  - (iii) 세로로 긴 안내판 에셋을 새로 생성해 2.7배 늘어짐 자체를 없앤다. 생성 1~2회 + 화풍 일관성 리스크.
  - **권장 (i)** — 표지판은 이미 stage 390px 높이로 충분히 크고, 에셋 재생성 없이 글자 확대까지 함께 해결된다.
- **(34번) 오프닝 대사 순서도 원문대로 되돌릴지.** 원문 음성 스크립트 씬2는 `1. 주인공 "벽화를 어떻게 그려야 되지?" → 2. 교사 "여러 가지 모양으로 그리면 좋겠어요." → 3. 교사 → 4. 주인공`인데, 구현은 1·2가 뒤바뀌어 교사 대사로 시작한다. 화자만 고치면 "교사가 먼저 제안 → 주인공이 고민"이 되어 인과가 거꾸로 남는다. **권장 순서까지 원문대로 되돌리기** — `shapeDialogues`의 앞 두 원소를 맞바꾸기만 하면 되고(문구는 그대로), UI 요소 표의 "2 교사 **등장** 및 오디오"도 이 순서라야 말이 된다. 다만 사용자가 요청한 범위 밖이라 별도 지시 없이는 손대지 않는다.
- **(30번) 씬7 `school-wall-completed.png`의 담장 면을 실측해야 한다.** `#completedMuralPreview`가 `#drawingCanvas`와 같은 좌표를 하드코딩하고 있어, 캔버스를 옮기면 여기도 옮겨야 하는데 씬7 배경의 면 좌표가 아직 실측표에 없다.
- **(24번) 공책을 어떻게 눕힐지.** A안 = CSS `rotateX`만(비용 0, 즉시 되돌림, 대신 두께가 사라져 종이 한 장이 되고 핫스팟 rect 보정 필요) / B안 = 공책 에셋만 3/4 하이앵글로 재생성(생성 1~2회, 화풍 일관성 리스크, 대신 핫스팟 축정렬 유지). **권장 B안** — 두께가 있는 사물이라 CSS로 눕히면 종이가 된다. 도시락은 둘 다 아니고 좌표만 옮기면 된다.
- **(25번) 삼각형 오브젝트를 무엇으로 할지.** **권장 트라이앵글(악기)** — 좌표를 안 건드려도 되고 삼각자와 재질·색이 확실히 갈린다. 저학년 ▲ 인지를 최우선으로 두면 차선은 고깔모자(면이 커서 더 쉽지만 좌표 이동 필요).

**해소됨**

- ~~(15번) 08 topbar의 기존 `.header-voice-volume-button`이 01의 음소거 버튼과 같은 것인가.~~ → **같다.** `#soundButton`으로 클래스명·SVG 구조까지 동일해 중복 배치하지 않았다. 2026-07-31 조사로 확정.
- ~~(15번) 01의 "다음 버튼"이 대사 진행 버튼인가, 씬 전환 버튼인가.~~ → **대사 진행 버튼(`.repair-narr-next`)으로 확정**, 2026-07-31. 이식 결과 17번의 데드엔드도 함께 풀렸다.
- ~~(18번) 네모 대상으로 쓸 "책상 위에 있을 법한" 사물을 무엇으로 할지. 창문·사물함 중 남길 것이 있는지.~~ → **공책 + 도시락으로 확정, 창문·사물함 둘 다 폐기**, 2026-07-31 완료.
- ~~(22번) 표지판 도형(`road-sign-*.png`)도 CSS로 바꿀 범위에 포함할지.~~ → **제외 확정**(14번의 "픽토그램·글자 모두 굽기" 결정 유지), 2026-07-31.
- ~~(3번) "title CTA 이미지"가 타이틀 로고 교체인지 CTA 버튼의 이미지화인지.~~ → 로고 교체로 확정, 2026-07-31 완료.
- ~~(3번) 타이틀 이미지의 아트가 01 `title-logo.png`와 색감·글자 형태가 다르다.~~ → 01 화풍으로 재생성 완료.
- ~~(2번) 삭제 대상이 `section_global_ui`인지 `section_intro`인지.~~ → `section_global_ui`로 확정, 완료.
- ~~(1번) 08에 `lesson.json`을 새로 만들지 여부 / 코스 메뉴를 할지 말지.~~ → **코스 메뉴는 한다. 데이터는 index.html 내부 상수(`COURSE_MENU`).** 한때 todo에 "범위 제외"로 적혔던 것을 2026-07-31 사용자 확인으로 뒤집었다.
- ~~(7번) 교실 배경 에셋 신규 생성 여부와 찾을 도형 사물 목록.~~ → 배경 신규 생성 + 사물 6종 개별 에셋으로 확정, 완료.
- ~~(8번) 도형 에셋화 범위.~~ → 기존 스프라이트를 유지하고 CSS 마스크로 색 새어나감을 고치는 것으로 해소, 완료. **22번에서 스프라이트 자체가 폐기되며 이 조치도 함께 걷혔다.**
- ~~(4번) 서체 `Jua`를 타이틀 화면에만 둘지 전역 적용할지.~~ → 01처럼 전역 적용으로 확정.
- ~~(11번) 망치를 떠 있는 아이콘으로 둘지 캐릭터가 드는 형태로 갈지.~~ → 떠 있는 아이콘으로 확정, 완료.
- ~~(12번) 키패드 교체 범위.~~ → 08의 모든 키패드로 확정, 완료.
- ~~(14번) 표지판 픽토그램을 이미지에 굽을지.~~ → 픽토그램 + 글자 모두 굽기로 확정, 완료.
- ~~(12번) 확인 키 글자를 `O`로 둘지 `확인`으로 바꿀지.~~ → **`확인`으로 확정**, 2026-07-31 반영 완료.
- ~~(10번) 디버그 패널 게이팅(`?debug=1`) 여부.~~ → 2026-07-31 사용자 지시로 항목을 닫았다. **게이팅 없이 항상 활성인 현재 상태를 유지한다.**
- ~~(4번) Jua 웹폰트 실브라우저 확인 / self-host 여부.~~ → 2026-07-31 사용자 지시로 항목을 닫았다. **01과 동일하게 CDN 의존 상태를 유지한다.**
- ~~(1번) `COURSE_MENU`에서 08의 차시 번호가 `no:8`인지 `no:13`인지.~~ → **`no:8`로 확정**, 2026-07-31.
- ~~(11번) 수리 연출 스킵 허용 여부.~~ → **스킵 불가(끝까지 보게 함) + 종료 후 1초 유지**로 확정, 2026-07-31 반영 완료.
- ~~(13번) 도형 연출 재생 범위.~~ → **매 문제 재생**으로 확정, 2026-07-31 반영 완료.
- ~~(2·6·7·14번) 미참조 에셋 삭제 여부.~~ → **삭제 확정**, 2026-07-31 6개 삭제 완료(`school-wall-wide` / `overview-mural-triptych-frame` / `school-speech-bubble-body` / `school-yard-shape-search` / `road-sign-body` / `global-hud-frame`).

## 항목 간 의존 관계

- 2번(첫 페이지 삭제) → 1번 헤더 진행률, `sceneMeta` progress 재배분, 10번 디버그 패널 목록에 **자동 반영됨**(디버그 패널이 `data-qa-order`에서 목록을 만들기 때문).
- 1번(코스 메뉴 드로어 교체) → 10번의 "점프 시 `unlockedMenuScenes` 해제" 로직이 **불필요해져 제거**됐다. 씬 잠금 개념 자체가 사라졌다.
- 12번(키패드) → 세 키패드가 `buildKeypad` 하나를 공유한다. `KEYPAD_KEYS` 배열을 바꾸면 셋 다 바뀐다.
- 6번·15번(말풍선) → `.speech`는 `#introSpeech`·`#shapeSpeech`·`#arithSpeech`·`#arithContext`·`#drawingSpeech`·`#feedbackSpeech`가 공유한다. **씬별 폭·패딩 보정을 다시 넣으면 15번의 자동 크기 조정이 깨진다.** 씬별로 남겨도 되는 것은 앵커 좌표뿐이다.
- 15번(01 값 이식) → **01의 값을 px로 재계산하지 말 것.** 01이 `cqw`/`cqh`로 적혀 있고 08의 `#stage`도 `container-type:size`라 선언을 그대로 옮기면 ×1.4056 환산이 자동으로 된다. 앞으로 01에서 무엇을 더 가져오든 이 경로를 먼저 확인한다.
- 15번(다음 버튼) → 17번의 데드엔드가 함께 풀렸다. 진행 표면은 이제 `ADVANCE_NAV_HTML` / `ensureAdvanceNav(el)` 한 곳에서 나온다. **새 대사·피드백 표면을 만들면 여기를 통해 진행 버튼을 붙인다.**
- 15번(자동 크기) → 16번(글자 확대)의 전제였다. 순서를 지켜 15 → 16으로 진행했다.
- 16번(글자 확대) → 좁은 컨테이너(`.keypad-wrap` 510px)에서 줄바꿈이 깨진다. **사다리를 또 올리면 `.keypad-wrap .prompt`의 단계와 `word-break:keep-all`을 다시 확인한다.**
- 8번 → 22번: 8번의 `mask-image` 색칠 우회는 22번에서 **완전히 제거됐다.** 지금 `.paint-shape`는 raster를 전혀 쓰지 않는다.
- 22번(도형 CSS화) → `#paintIntroVisual`·`#countShapes`·`#arithShapes`·`#randomShapes`·`#randomWorkProgress`·`.drawn-shape`·`.drawing-summary`가 모두 `.paint-shape` 하나를 공유한다. 도형 모양·선 두께를 바꾸면 7곳이 함께 바뀐다.
- 22번 → 20번: `.added` 표시는 `.paint-shape` 요소에 배경이 없다는 전제 위에서 `box-shadow`로 사각 테두리를 만든다. **요소에 배경을 다시 넣으면 표시가 도형을 덮는다.**
- 19번(초록 단색) → 씬3에만 적용했다. 씬4(`#randomShapes`)와 `.random-progress`는 3색 3모양 그대로다. 씬3의 색 규칙을 다시 손대면 씬2 `#paintIntroVisual`의 `초록=● / 파랑=■ / 빨강=▲` 매핑과 충돌하지 않는지 먼저 본다.
- 18번(사물 배치) → 좌표는 `findObjects` 한 곳에만 있고 핫스팟은 여기서 파생된다. 좌표를 바꿀 때는 `#shapeSceneStudent` 및 `.search-prompt`와의 겹침을 함께 본다. **23번으로 학생 박스가 x 1080~1380 / 실루엣 x 1165~1296 · y 509~880으로 바뀌었다**(이전 x 1080~1420 · 화면 하단).
- 23번(학생 등장·포즈) → `#shapeSceneStudent`를 직접 `classList`로 여닫지 말고 `showSceneStudent()` / `hideSceneStudent()` / `setSceneStudentPose()`를 쓴다. `showWrongFeedback`·`showFeedback`이 `sceneStudentVisible()`로 분기하므로 **학생을 다른 시점에 띄우면 그 시점의 피드백 주체가 함께 바뀐다.**
- 24번(공책·도시락 접지) → **배경 `classroom-shape-search.png`의 책상 상판 실측값은 24번 항목 본문에 있다.** 앞으로 이 씬에 사물을 더 놓거나 옮길 때 매번 다시 재지 말고 그 값을 쓴다. 접지 그림자 CSS는 `.find-object` 전체에 걸리므로 6종 모두에 영향을 준다.
- 24번 ↔ 25번 → 둘 다 `findObjects`를 건드린다. 25번의 오브젝트 교체를 먼저 하면 24번의 좌표 조정에서 6종 배치를 한 번에 볼 수 있다.
- ~~3번(타이틀 로고 교체) → 9번의 140px 오프셋 재계산 필요.~~ → 알파 bbox가 동일해 재계산 불필요. 로고를 또 바꾸면 이 확인은 다시 해야 한다.
- 26번(데드엔드) ↔ 17번 → **17번이 만든 "수동 진행 게이트"와 그 뒤 추가된 "장면 전체 오답 판정"이 서로를 무효화한다.** 앞으로 새 오답 판정 표면을 추가할 때는 **정답 확정 이후에도 그 핸들러가 살아 있는지** 반드시 확인한다. 씬4의 `randomAwaitingContinue` 가드가 참고 구현이다.
- 26번 → `resetFeedbackOverlay()`는 `feedbackContinueAction`을 무조건 지운다. **`showWrongFeedback`을 새 지점에서 부를 때마다 진행 경로가 armed 상태인지 본다.**
- 27번 → 15번(`.speech` 자동 크기)과 충돌하지 않게 **앵커 좌표(`left`/`top`)만** 바꾼다. 폭·패딩을 손대면 15번이 깨진다.
- 28번 → `.work-area`는 `#paintIntroVisual`·`#countShapes`·`#arithShapes`·`#randomShapes` 4곳이 공유한다(22번 참조). **공통 `top`을 내리면 씬2·씬4도 함께 내려간다.** 씬4는 `#randomShapes` 개별 오버라이드가 있고 배경 면도 다르므로 29번과 함께 처리한다.
- 28·30·33번 → 좌표를 잡을 때 이 문서 상단의 **"배경 담장 면 실측값" 표**를 쓴다. 다시 재지 말 것. 씬7(`school-wall-completed.png`)만 아직 미측정이다.
- 29번(유형 6문항) → `#randomWorkProgress`의 하드코딩된 도형 3개, `setProgress(72+n*4)`의 상한(96 > 다음 씬 84), `armRandomContinue`의 마지막 문항 분기가 **전부 문항 수에 묶여 있다.** 문항 수를 바꾸면 셋을 같이 본다.
- 29번(도형 상시 표시) → `#randomShapes`와 `#randomPanel`이 완전히 겹쳐 있어 `visibility:hidden` 한 줄만 지우면 둘 다 못 읽는다. **좌표 재배치가 전제다.**
- 30번(캔버스 좌표) → `#completedMuralPreview`(씬7)가 `#drawingCanvas`와 **같은 값을 하드코딩**하고 있다(390/275/1370×540). 한쪽만 바꾸면 완성 그림이 다른 자리에 복원된다.
- 30번(크기·기울기) → `drawingState()`가 저장하는 항목과 `renderCompletedMural()`이 복원하는 항목이 **한 쌍**이다. 새 속성을 추가하면 양쪽을 같이 고친다.
- 30번(크기) → 22번의 `.paint-shape.triangle` 안쪽 폴리곤은 **정삼각형 비율 전제**다. 가로세로를 다른 배율로 늘리면 선 두께가 어긋난다.
- 32·33번 → `story-roadside-info-board.png` 하나를 `.story-intro-board`(원본 비율 1420×220)와 `.story-card`(1300×600으로 2.7배 세로 늘림)가 공유한다. **인트로 판은 멀쩡하고 카드만 문제다.** 한쪽 값을 다른 쪽에 그대로 복사하지 않는다.
- 32번 → `● ■ ▲`를 인트로로 옮기면 `storyBeats` 길이가 7 → 6이 되어 `setProgress(94+storyIndex)`와 마지막 beat 분기가 함께 움직인다.
- 32번 → 도형 색은 19번이 세운 `초록=● / 파랑=■ / 빨강=▲` 매핑(씬2 `#paintIntroVisual`)을 따른다.
- 34번 → 대사 데이터(`shapeDialogues[0]`)와 정적 마크업(index.html:501)이 **같은 첫 beat를 두 벌 갖고 있다.** 한쪽만 고치면 첫 프레임에 이전 인물이 번쩍인다. `renderShapeDialogue`가 덮어쓰기 전에 정적 마크업이 먼저 그려지기 때문이다. 다른 씬의 첫 대사(`#introSpeech`·`#arithSpeech`·`#drawingSpeech`)도 같은 구조라 화자를 바꿀 때마다 두 곳을 본다.
- 34번 ↔ 23번 → 오프닝 동안 `#shapeSceneStudent`가 숨겨져 있다는 전제 위에서 안전하다. **학생을 오프닝에 다시 세우면 beat 1·3의 `student-*` 화자와 인물이 중복된다.**
