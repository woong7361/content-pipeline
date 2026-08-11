# 좌표계 도메인 레퍼런스 조사 — "픽셀을 재지 말고 좌표를 선언하라"

작성일: 2026-08-08
계기: `problem.md` [visual-qa-pixel-measure-cost] — playwright 스크린샷을 LLM이 열어 픽셀 오프셋을 측정하는 구조의 토큰·시간 비용
관련 이력: `problem.md` [design-review-no-image-input] (이 구조가 도입된 경위)

---

## 0. 지금 구조의 비용이 어디서 나오는가

대표 사례("이미지 내부에 글자를 중앙에 넣기")의 현재 경로:

```
asset_generator  →  composition_notes에 safe zone을 "산문"으로 기술
                    "가변부가 얹힐 중심축과 오버레이 safe zone을 명시합니다"
                         ↓  (좌표 정보 소실)
image gen        →  슬롯이 그려진 raster PNG. 슬롯의 실제 좌표는 아무 데도 안 적힘
                         ↓
builder          →  CSS로 눈대중 배치 (place-items:center 등)
                         ↓
playwright       →  1920x1080 스크린샷 11장
                         ↓
design_review    →  ★ LLM이 스샷을 열어 표면 중심 vs 텍스트 중심을 px로 측정
                    alignment_offset{dx_px, dy_px, surface_w, surface_h} 채움
                         ↓
코드             →  오프셋/표면 비율로 severity 파생
                         ↓
design_refine    →  CSS 좌표 수정  →  다시 ★로  (iteration마다 반복)
```

★ 지점이 비용의 핵심이다. 두 가지가 동시에 잘못돼 있다.

1. **정보이론적 낭비.** 필요한 두 좌표는 이미 결정되어 있다. 슬롯 중심은 *에셋 저작 시점*에, DOM 박스 중심은 *CSS*에 있다. 렌더된 픽셀에서 역산하는 것은 이미 아는 값을 가장 비싼 경로로 다시 구하는 것이다.
2. **iteration마다 반복.** 에셋은 안 바뀌는데 측정은 `씬 N × 표면 M × iteration K`번 일어난다. 실측 기록으로 `alignment_offset` 필수화만으로 리뷰 생성이 1.7~2배 느려졌다(cell9 642초).

그리고 그렇게 비싸게 얻은 값이 흔들려서(cell6/7/8에서 같은 ~12px를 high/none/low로 판정) 코드 임계값을 덧대야 했다. **비싸고 부정확하다**는 것이 문제의 정확한 형태다.

---

## 1. 도면/CAD — 구속(constraint)과 기준(datum)

### 그 도메인의 문제

기계 도면에서 "구멍을 판 중앙에 뚫어라"를 좌표로 적으면, 판 크기가 바뀌는 순간 전부 틀린다. 설계 변경은 상시로 일어난다.

### 해법

**절대 좌표를 안 쓴다.** FreeCAD Sketcher를 보면 사용자가 넣는 것은 숫자가 아니라 관계다 — `coincident(점A, 점B)`, `concentric(원1, 원2)`, `symmetric(점, 점, 축)`. 이 구속들을 `Sketcher::Sketch`가 PlaneGCS(`GCS::System`)의 파라미터로 변환하고, 솔버가 Jacobian의 rank와 residual을 보며 수치적으로 푼다. 마우스를 움직이는 동안 솔버가 반복 호출되어 Geometry를 갱신한다. 솔버는 덤으로 **conflict / redundancy / over-constrained**를 검출해 준다.

여기에 두 개념이 더 붙는다.

- **Datum(기준면).** 모든 치수는 임의의 원점이 아니라 명시적으로 선언한 기준면에서 파생된다. 기준을 한 번 정하면 이후 치수는 전부 상대값이다.
- **GD&T 공차.** "중앙"은 이진값이 아니라 `⌖ 0.2` 같은 **위치도 공차**로 적는다. 합불 판정이 사람 눈이 아니라 숫자로 못 박힌다.

### 우리에게 옮길 것

- "중앙에 놓아라"를 CSS 결과로 검증하지 말고 **관계로 선언**한다: `concentric(#tutorialDrop, slot:clock_hole)`.
- 에셋의 슬롯이 **datum**이다. 한 번 정하고, 이후 모든 배치는 거기서 파생.
- severity 임계값(현재 2~4% mid / >4% high)이 곧 **위치도 공차**다. 이 방향은 이미 맞게 잡혀 있다 — 다만 측정 주체가 LLM일 필요가 없다.
- over-constrained 검출은 그대로 유용하다: `[entrance-anim-clobbers-centering-transform]`(애니메이션 keyframe의 `transform:none`이 `translateX(-50%)`를 덮어씀)은 CAD 용어로 정확히 **구속 충돌**이다. 솔버가 있었으면 자동 검출됐을 종류의 결함이다.

---

## 2. UI 제약 솔버 — Cassowary / Auto Layout

CAD 아이디어를 UI로 가져온 것이 Cassowary다. 선형 제약만 다루는 대신 incremental dual simplex로 실시간에 푼다. Apple Auto Layout, GTK의 Emeus, JS의 kiwi/autolayout이 전부 이 알고리즘이다.

핵심은 두 가지다.

- **속성 어휘**: `left, right, top, bottom, width, height, centerX, centerY, baseline`. "프레임을 계산"하는 게 아니라 요소 간 관계를 선언한다. `text.centerX == slot.centerX`.
- **priority(강도)**: `required / strong / medium / weak`. 다 만족 못 할 때 무엇을 먼저 포기할지가 데이터에 들어 있다. 이게 CAD 솔버와의 실용적 차이다 — 과제약 상태에서 에러를 내지 않고 **우아하게 열화**한다.

### 우리에게 옮길 것

우리는 이미 CSS라는 제약 솔버(flexbox/grid) 위에 있다. 문제는 CSS가 **DOM 박스**만 알고 **에셋 안에 그려진 슬롯**을 모른다는 것 — problem.md가 정확히 이렇게 적어 뒀다: "CSS에 `text-align:center`가 있어도 그것은 DOM 박스 기준이라 asset에 그려진 슬롯 중심과 어긋날 수 있다".

→ 결론: **새 솔버를 도입할 게 아니라, 에셋의 슬롯을 CSS가 볼 수 있는 좌표로 만들어 주면 기존 솔버가 그대로 푼다.** 이게 3장의 9-patch로 이어진다.

priority 개념은 별도로 쓸모가 있다. `[content-overflows-fixed-surface]`(가변 길이 콘텐츠가 고정 표면을 넘침)는 "safe zone 안에 들어간다=required, 지정 폰트 크기 유지=weak" 같은 우선순위로 표현하면 자연스럽게 풀린다.

---

## 3. ★ 9-patch / 스프라이트 슬라이스 — 이미지가 자기 좌표를 들고 다닌다

**우리 문제("이미지 내부에 글자 중앙 배치")에 가장 직접적인 레퍼런스.**

### 그 도메인의 문제

Android 버튼 배경은 raster PNG인데, 그 위에 올라갈 라벨 길이는 런타임에 정해진다. 이미지 안 어디가 "글자 놓을 자리"인지 매번 잴 수는 없다.

### 해법

**이미지 자신에게 적게 한다.** `.9.png`는 1px 테두리에 메타데이터를 인코딩한다.

- **왼쪽/위 테두리** = 늘어나도 되는 구간 (stretchable patch)
- **오른쪽/아래 테두리** = **content(padding) box — 콘텐츠가 들어가도 되는 영역**

즉 "이 이미지 안에서 글자가 놓일 사각형"이 이미지 파일 자체에 박혀 있다. 레이아웃 엔진은 아무것도 측정하지 않고 그 rect 안에 텍스트를 넣는다.

같은 패턴이 게임 툴체인에도 있다. Aseprite는 **slice**를 지원하고 `--data` / Export Sprite Sheet로 JSON을 뽑으면 `meta.slices[].keys[]`에 `bounds`, **`center`(9-slice 중앙 사각형)**, **`pivot`**이 나온다. TexturePacker 계열도 프레임마다 pivot과 `spriteSourceSize`를 낸다.

### 우리에게 옮길 것 — 이게 1순위 제안이다

`composition_notes`에 산문으로 적는 safe zone을 **정규화 좌표 sidecar로 승격**한다.

```json
// output/assets/tutorial_clock_repair_tray.meta.json
{
  "asset_id": "tutorial_clock_repair_tray",
  "natural_size": [1536, 1024],
  "slots": [
    { "id": "clock_hole",  "role": "asset_mount", "rect": [0.31, 0.22, 0.24, 0.36], "anchor": "center" },
    { "id": "answer_slot", "role": "text",        "rect": [0.62, 0.40, 0.28, 0.18], "anchor": "center" }
  ]
}
```

`rect`는 0~1 정규화 — SVG `viewBox`나 Unity anchor와 같은 이유로, 1920×1080 스테이지 스케일이 바뀌어도 값이 안 깨진다.

그러면 builder는 측정 없이 좌표를 CSS로 옮기기만 하면 된다.

```css
.tray { position: relative; aspect-ratio: 1536/1024; }  /* [bg-anchor-alignment]의 교훈: 비율 안 맞으면 레터박스가 %좌표를 어긋냄 */
.tray > [data-slot="answer_slot"] {
  position: absolute;
  left: 62%; top: 40%; width: 28%; height: 18%;
  display: grid; place-items: center;
}
```

**측정이 파이프라인에서 사라진다.** LLM은 정렬을 재지 않고, CSS가 자기가 아는 좌표계 안에서 중앙정렬을 푼다.

---

## 4. 정규화 anchor/pivot — Unity RectTransform, SVG viewBox

Unity UI가 해상도 독립을 얻는 방식: `anchorMin`/`anchorMax`(부모 기준 0~1 정규화)로 **어디에 매달릴지**, `pivot`(자기 기준 0~1)으로 **자기 어느 점을 그 자리에 둘지**를 나눈다. 중앙 배치는 `anchorMin=anchorMax=pivot=(0.5,0.5)`, `anchoredPosition=0`. 픽셀 숫자가 한 개도 안 나온다.

SVG도 같은 사고다. `viewBox`로 논리 좌표계를 정의하고 `preserveAspectRatio`로 매핑 규칙을 정하면, `x="50%" y="50%" text-anchor="middle" dominant-baseline="central"`이 해상도와 무관하게 성립한다.

### 우리에게 옮길 것

- 3장의 slot rect는 반드시 **정규화**로 저장한다. px로 저장하면 에셋 재생성 시 크기가 달라지는 순간 전부 무효가 된다.
- **anchor와 pivot을 분리**하는 것이 특히 말풍선에 유효하다. `[speech-bubble-anchor-detached]`(말풍선이 화자에서 떨어짐)와 `[speech-bubble-fixed-box-not-content-sized]`(고정 크기라 대사 길이에 안 맞음)는 둘 다 "고정 좌표"로 풀려던 문제다. Unity식으로 적으면: anchor = 화자 머리 좌표(따라다님), pivot = 말풍선 꼬리 위치(자기 어디를 거기 붙일지), 크기 = 콘텐츠 기준. 셋을 분리하면 두 결함이 동시에 사라진다.

---

## 5. 조판 — TeX의 box / glue / penalty

Knuth의 모델: 모든 것은 `width, height, depth`를 가진 **box**이고, box 사이에는 늘고 줄 수 있는 **glue**가, 줄바꿈 후보에는 **penalty**가 놓인다. 엔진은 전체 badness를 최소화하는 배치를 푼다.

중앙정렬을 TeX는 이렇게 쓴다.

```tex
\hbox to \hsize{\hfil 텍스트 \hfil}
```

`\hfil`은 **무한 신축성 glue**다. "중앙"이라는 좌표를 계산하는 게 아니라, 양쪽에 똑같이 무한히 늘어나는 스프링을 두면 결과적으로 중앙이 된다. 좌표는 존재하지 않고 관계만 존재한다.

또 하나 — TeX는 텍스트의 세로 기준을 **baseline**으로 잡고 `height`(baseline 위)와 `depth`(baseline 아래)를 따로 관리한다. 폰트 메트릭(ascent/descent/cap-height/x-height)에서 나온 값이라 렌더링 없이 계산된다.

### 우리에게 옮길 것

**시각적 중앙 ≠ 기하학적 중앙.** 이게 실용적으로 중요하다. `[icon-glyph-not-centered-in-button]`(정사각 버튼의 `×` 글리프가 중앙에 안 옴)이 정확히 이 문제다 — CSS `place-items:center`는 **line-box** 기준으로 맞추는데, 사람 눈은 **cap-height** 기준으로 본다. 폰트의 ascent/descent 비대칭 때문에 항상 몇 px 어긋난다.

이건 스크린샷을 아무리 봐도 원인을 못 찾고 "±3px 조정"만 반복하게 되는 종류의 버그다. 해법은 측정이 아니라 알려진 보정:

```css
/* 글리프 하나짜리 버튼: line-box가 아니라 cap-height 기준으로 광학 중앙 */
.icon-btn { display: grid; place-items: center; line-height: 1; }
.icon-btn > span { display: block; transform: translateY(var(--optical-nudge, 0.06em)); }
```

혹은 `leading-trim`/`text-box-trim`이 쓸 수 있으면 그쪽이 정공법이다.

---

## 6. 지도 라벨 배치 — anchor + offset + collision index

Mapbox GL의 symbol layer는 라벨 겹침을 **렌더 결과를 보고** 판정하지 않는다.

- `text-variable-anchor`로 후보 앵커를 여러 개 주고(top-left, bottom 등), `text-radial-offset`으로 앵커에서의 거리를, `text-justify`로 정렬을 선언한다.
- 겹침은 별도의 **collision index**(공간 인덱스)에 각 라벨의 collision box/circle을 넣고 **기하학적으로** 판정한다. `text-allow-overlap` / `icon-ignore-placement` 등으로 정책을 데이터로 준다.
- 앵커 후보를 순회하며 충돌 없는 자리를 고르고, 없으면 라벨을 뺀다.

(참고로 이 도메인에도 알려진 함정이 있다 — 충돌 판정이 `text-offset`을 반영 안 하는 이슈 #4798, `text-anchor`를 무시하는 #9313. "선언한 좌표와 판정에 쓰는 좌표가 어긋나면 버그"라는 교훈은 우리에게도 그대로 적용된다.)

### 우리에게 옮길 것

- 현재 `visual_qa.py`의 overlap 검사는 이미 이 방향이다(`rectOf` + 교집합 면적, 974~1001행). 즉 **겹침은 이미 코드가 결정적으로 판정하고 있다.** 정렬만 LLM에게 맡겨 둔 것이 비대칭이다.
- 후보 앵커 개념은 `[cta-reveal-reflow-shift]`(CTA가 나타나며 중앙 콘텐츠를 밀어 올림) 같은 결함에 유효하다 — CTA 자리를 미리 예약(reserve)하거나 후보 앵커를 주면 reflow가 없어진다.

---

## 7. 종합 — 여섯 도메인의 공통 원리

| 도메인 | "중앙에 놓기"를 어떻게 표현하나 | 검증 방식 |
|---|---|---|
| CAD 도면 | `concentric(A, B)` 구속 | 솔버 residual + GD&T 위치도 공차 |
| Auto Layout | `a.centerX == b.centerX`, priority | 솔버가 unsatisfiable 보고 |
| 9-patch / slice | 이미지가 content rect를 자기 안에 인코딩 | 검증 불필요(측정이 애초에 없음) |
| Unity / SVG | 정규화 anchor(0.5,0.5) + pivot(0.5,0.5) | 해상도 무관하게 항등 |
| TeX | `\hfil ... \hfil` (무한 신축 glue) | badness 최소화 |
| 지도 라벨 | anchor + radial offset + 충돌 정책 | collision index 기하 판정 |

**여섯 도메인 중 어디도 "완성된 그림을 보고 좌표를 역산"하지 않는다.**

공통 원리는 셋이다.

1. **좌표는 산출물에서 읽는 게 아니라 입력으로 선언한다.** 각 요소가 자기 기준계(anchor/pivot/slot)를 신고한다.
2. **기준은 한 번만 정한다(datum).** 이후 모든 값은 상대값으로 파생되므로, 재측정할 것이 없다.
3. **검증은 결정적으로 하고 위반만 보고한다.** 정상인 것에 대해 "정상임"을 서술하는 비용이 0이다.

3번이 토큰 절감의 직접적 근거다. 지금은 34개 finding 전부에 `alignment_offset`을 채우게 하지만(정상 포함), 결정적 검사는 **위반 건수에 비례**해 출력한다. 정렬이 다 맞으면 출력이 0바이트다.

---

## 8. 우리 파이프라인 적용안

문제를 두 층으로 나눈다. **둘은 독립적이라 따로 도입할 수 있다.**

- **층 A (생성)**: 슬롯 좌표를 어떻게 확보해 builder에게 줄 것인가 → 측정 자체를 없앰
- **층 B (검증)**: 배치가 맞는지 어떻게 판정할 것인가 → LLM 측정을 코드로 대체

### 층 A — 슬롯 좌표 확보: 세 가지 선택지

핵심 난점을 먼저 인정해야 한다. **image gen 모델은 "safe zone을 여기 남겨라"라는 좌표 지시를 정확히 안 지킨다.** 계획 좌표를 그대로 신뢰하면 계획-실제 불일치가 그대로 결함이 된다. 세 안은 이 난점을 다르게 푼다.

#### A-1. 계획 좌표를 권위로 (가장 싸고, 가장 부정확)

`planner_output` / `asset_plan`에 `slots[]`를 추가하고 그 값을 그대로 CSS로 옮긴다.

- 장점: 코드 변경 최소. 측정 완전 소멸.
- 단점: 생성 이미지가 계획을 안 지키면 그대로 어긋난다. **에셋이 단순하고 슬롯이 큰 경우에만 안전.**

#### A-2. 1회 등록(registration) — CAD의 datum 설정 (권장)

에셋 생성 **직후 딱 한 번** 실제 그려진 슬롯 위치를 측정해 `{asset_id}.meta.json`에 고정한다. 이후 모든 iteration은 읽기만 한다.

- 측정 횟수: `씬 N × 표면 M × iteration K` → **에셋당 1회**
- 측정 주체 선택지:
  - LLM 1회 호출 (지금과 같은 능력, 횟수만 급감 — 즉시 도입 가능)
  - 결정적 코드: alpha bbox / flood-fill. **이 프로젝트에 이미 전례가 있다** — `[bg-anchor-alignment]` 조치에서 모니터 유리면을 flood-fill로 실측(left25.2/top14.4/w49.1/h34%)했고, 책 지면도 크림 지면 flood-fill(left11.8/top8.3/w76.4/h65.3%)로 잡았다. 그 1회성 수작업을 함수로 만드는 것이다.
- 장점: 계획-실제 불일치를 흡수하면서 반복 비용이 상수. 에셋이 재생성될 때만 다시 등록.
- 단점: 등록 스텝이 파이프라인에 하나 늘어난다. flood-fill은 배경이 단색/저대비일 때만 신뢰할 수 있다.

#### A-3. 레지스트레이션 마크 — 인쇄/크로마키 도메인 기법 (가장 정확, 리스크 있음)

에셋 생성 시 **safe zone을 마젠타 단색으로 칠하게** 지시하고, 후처리 코드가 마젠타 영역을 검출해 rect를 뽑은 뒤 그 영역을 투명/배경색으로 치환한다. 인쇄의 crop mark, 방송의 크로마키와 같은 발상.

- 장점: image gen이 "빈 자리를 남겨라"(부정 지시, 잘 안 지켜짐)보다 "여기를 마젠타로 칠해라"(긍정 지시)를 훨씬 잘 지킨다. 검출이 결정적이고 정확하다.
- 단점: 색 누출(despill). 이 프로젝트는 이미 알파/크로마키 계열에서 데인 적이 있다 — `[transparent-asset-alpha-not-validated]`·`[decorative-asset-background-alpha]` 모두 **보류(SKIP)** 상태다. 다만 그쪽은 "생성 모델에게 진짜 알파를 요구"하는 문제였고, 이쪽은 "명시적으로 칠한 단색 영역을 코드가 검출"하는 문제라 층위가 다르다. 프린지가 생겨도 rect **좌표만** 필요하고 픽셀 품질은 안 쓰므로 despill 요구 수준이 훨씬 낮다.

**권장: A-2를 기본으로, 슬롯 검출이 어려운 에셋만 A-3.**

### 층 B — 결정적 정렬 검증

`visual_qa.py`에 concentricity 검사를 추가한다. HTML은 자기가 어느 슬롯에 앉는지 선언한다.

```html
<div class="tray" data-slot-source="tutorial_clock_repair_tray">
  <div data-slot="answer_slot">[?]</div>
</div>
```

`build_inspection_script()`에 추가할 계산(기존 `rectOf`를 그대로 재사용):

```js
// slot rect(정규화) × 컨테이너 rect → 기대 중심
// vs 실제 자식 요소 중심 → dx, dy
// 표면 대비 % 로 정규화해 임계값 판정 (GD&T 위치도 공차)
```

출력은 **위반 건만** `render_checks.alignment_offsets`에 넣는다. 정상이면 배열이 빈다.

이때 얻는 것:

- 오프셋이 **항상 같은 값**이다. cell6/7/8의 severity 흔들림이 원리적으로 제거된다(코드 임계값을 덧대는 우회가 아니라, 측정 자체가 결정적).
- `design_review_system.md`의 STEP1에서 **정렬 축(축 3의 오프셋 측정 부분)을 걷어낼 수 있다.** `alignment_offset` 필수 필드도 제거 가능 → 리뷰 생성 1.7~2배 지연의 직접 원인 소멸.
- 남는 축(재질·구도·에셋 통합·화풍)은 여전히 LLM이 스샷을 봐야 한다. **스크린샷 리뷰 전체가 없어지는 게 아니라 정렬 축만 코드로 이관되는 것**이다. 이 점은 정직하게 계산에 넣어야 한다.

### 도입 순서 제안

| 단계 | 작업 | 얻는 것 | 비용 |
|---|---|---|---|
| 1 | 층 B만 — `visual_qa.py` concentricity 검사 + `data-slot` 계약 | 정렬 판정이 결정적·무료가 됨. 층 A 없이도 **DOM 박스 간** 정렬은 즉시 검증 가능 | 작음. 기존 `rectOf`/`build_selector_findings` 재사용 |
| 2 | `design_review_system.md`에서 정렬 측정 지시 제거, `alignment_offset` 스키마 되돌림 | 리뷰 생성 지연 1.7~2배 → 원복 | 작음. 단 두 스키마 동시 수정 필수 ([design-review-no-image-input]에서 한쪽만 고쳐 파이프라인이 깨진 전례) |
| 3 | 층 A-2 — 에셋 등록 스텝 + `{asset_id}.meta.json` | **에셋 안 슬롯**까지 검증 범위 확대. builder가 눈대중을 안 함 | 중간. 새 스테이지 하나 |
| 4 | 검출 실패 에셋에 A-3 마커 적용 | 복잡한 에셋 커버 | 중간. despill 검증 필요 |

1·2단계만으로도 이번 지적의 직접 원인(측정 필수화로 인한 지연)은 해소된다. 3·4는 근본 해결이다.

### 채택하지 않을 것

- **범용 제약 솔버(kiwi.js 등) 도입.** CSS grid/flex가 이미 솔버다. 문제는 솔버 부재가 아니라 슬롯 좌표 부재이므로, 솔버를 더 넣어도 안 풀린다. 불필요한 추상화.
- **스크린샷 리뷰 전면 폐지.** 재질·화풍·구도 판정은 픽셀을 봐야 한다. `[design-review-no-image-input]`의 실측이 "모델은 픽셀을 본다, 문제는 satisficing"이라고 이미 결론냈다 — 시각 리뷰 자체는 유효하다.

---

## 참고 문헌

- [The Cassowary linear arithmetic constraint solving algorithm — ACM TOCHI](https://dl.acm.org/doi/10.1145/504704.504705)
- [Emeus — Constraint-based layout manager for GTK+](https://ebassi.github.io/emeus/)
- [lume/autolayout — Auto Layout + VFL for JavaScript (cassowary)](https://github.com/lume/autolayout)
- [FreeCAD — Constraint System and GCS Solver (DeepWiki)](https://deepwiki.com/FreeCAD/FreeCAD/3.1.2-constraint-system-and-gcs-solver)
- [CAD Sketcher — Constraints](https://hlorus.github.io/CAD_Sketcher/constraints/)
- [Salusoft89/planegcs — WebAssembly wrapper for FreeCAD's 2D geometric solver](https://github.com/Salusoft89/planegcs)
- [Android Draw 9-patch tool](https://stuff.mit.edu/afs/sipb/project/android/OldFiles/docs/tools/help/draw9patch.html)
- [Nine Patches — skin-composer wiki](https://github.com/raeleus/skin-composer/wiki/Nine-Patches)
- [Aseprite — Slices (9-slice, pivot, JSON export)](https://www.aseprite.org/docs/slices/)
- [Aseprite API — Slice](https://www.aseprite.org/api/slice)
- [Unity — Basic Layout (RectTransform anchors/pivot)](https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/UIBasicLayout.html)
- [Unity Scripting API — RectTransform.anchoredPosition](https://docs.unity3d.com/ScriptReference/RectTransform-anchoredPosition.html)
- [Mapbox — Optimize map label placement](https://docs.mapbox.com/help/dive-deeper/optimize-map-label-placement/)
- [mapbox-gl-native — Collision Detection](https://github.com/mapbox/mapbox-gl-native/wiki/Collision-Detection)
- [mapbox-gl-js #4798 — Respect text-offset in collision handling](https://github.com/mapbox/mapbox-gl-js/issues/4798)
- [mapbox-gl-js #9313 — text-anchor not supported in collision circle placement](https://github.com/mapbox/mapbox-gl-js/issues/9313)
