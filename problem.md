# problem.md

`index.html`과 content-pipeline(`content-harness-pipeline/` 전반)에 대한 사용자 피드백을 누적 기록하는 대장이다. 운영 규칙은 최상단 `AGENTS.md`의 "피드백 → problem.md → rule 루프" 섹션을 따른다.

## 사용 규칙

- 사용자가 결과를 교정·지적할 때마다 아래 "문제 로그"에 항목을 추가한다.
- 같은 **분류 태그(category)** 의 


항목이 이미 있으면 새로 만들지 말고 그 항목의 `발생 횟수`와 `최근 발생일`, `사례`를 갱신한다.
- 같은 분류 태그가 누적 **5회 이상**이 되면 다음 작업 전에 rule 승격을 제안한다.
- rule로 승격되면 해당 항목 `상태`를 `규칙화됨`으로 바꾸고 어느 AGENTS.md에 반영했는지 적는다.

## 항목 템플릿

```markdown
### [분류태그] 한 줄 요약

- 대상: content-harness-pipeline/... (구체 경로 또는 index.html)
- 분류 태그: <중복 감지 기준이 되는 짧은 카테고리>
- 상태: 열림 | 제안됨 | 규칙화됨
- 발생 횟수: N
- 최초 발생일: YYYY-MM-DD
- 최근 발생일: YYYY-MM-DD
- 사례:
  - YYYY-MM-DD: <사용자가 지적한 내용 요약>
- 조치: <이번에 어떻게 수정했는지>
- 규칙화 메모: <제안한 rule 초안 / 반영 위치 / 승인 여부>
```

## 문제 로그

<!-- 새 항목은 이 아래에 추가한다. 아직 기록된 문제가 없다. -->

### [ornate-asset-wrong-function] 장식성 강한 에셋(인증서/상장 등)을 기능 UI 표면으로 재사용해 주제와 안 어울림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-c` 숫자 트레이, `assets/certificate_library_repair.png`)
- 분류 태그: ornate-asset-wrong-function
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 C 숫자 블록 트레이 배경으로 `certificate_library_repair.png`(화려한 금색 인증서/상장 액자)를 얹었더니 "너무 안 어울린다"고 지적. 상장 느낌 액자를 기능적 숫자 키패드 표면으로 쓰니 주제(도서관 컴퓨터 재부팅)와 톤이 안 맞고, 좌우로 늘리며 프레임 장식(시계·책)까지 찌그러져 더 어색했음.
- 조치: 액자 제거. 숫자 블록을 모니터 키보드 위(측정 중심 ~69%)에 직접 배치(단순 트레이), 라벨만 크림색 알약 배경으로 가독 확보. 사용자에게 3가지 방향(액자 제거/단순 나무매트/왜곡 원복) 제시 후 "액자 제거" 선택. certificate 에셋 파일은 마무리 인증서용으로 보존.
- 규칙화 메모: 아직 1회. 반복되면 "에셋의 장식 강도를 기능에 맞춘다 — 인증서/상장/트로피 등 '보상·축하' 톤 에셋은 기능적 입력/트레이 표면으로 재사용하지 말고, 입력 표면엔 단순·중립 표면(나무 트레이/코르크/키보드 위 직접)을 쓴다. 장식 asset을 좌우로 늘려 aspect를 왜곡하지 않는다" 규칙을 builder_system.md에 제안 후보.
### [decorative-asset-background-alpha] 모니터 내부 장식 이미지에 불필요한 불투명 배경이 포함됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`assets/morning_evening_time_bar.png`)
- 분류 태그: decorative-asset-background-alpha
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 C 모니터 안에 추가한 아침→저녁 시간대 막대 이미지의 크림색 배경이 화면과 겹쳐 보여, 배경을 투명하게 해야 한다고 지적.
- 조치: 기존 구도를 마젠타 크로마키 배경으로 편집한 뒤 alpha PNG로 추출했다. 보라색 저녁 영역이 디스필에 손상되는 것을 검수에서 발견해 디스필을 끄고 edge-contract 1로 테두리를 정리한 final asset으로 HTML 참조를 교체했다.
- 규칙화 메모: 아직 1회. 반복되면 "기존 UI 표면 위에 얹는 장식용 raster asset은 생성 전에 투명 배경 필요 여부를 확인하고 alpha PNG로 검수한다" 규칙을 asset 생성 workflow에 제안 후보.

### [feedback-stamp-visual-overload] 피드백 도장 이미지가 과밀하고 컨셉 전달이 약함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/stamp_correct_time.png, stamp_fail_time.png
- 분류 태그: feedback-stamp-visual-overload
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 정답/실패 도장 시안이 시계 눈금, 바늘, 체크/X, 깨짐선, 큰 글자가 겹쳐 너무 이상하게 보임. 사용자가 원형 시계 배경 위에 `정답!`/`실패!` 글자를 단순히 얹는 방식이 낫다고 지적.
  - 2026-07-09: 재생성한 시계 배경까지 초록/빨강으로 물들어 `index.html`의 애니메이션풍 도서관 시계 톤과 맞지 않음. 사용자가 시계는 상태색이 아니라 index.html 느낌의 애니메이션풍 시계로 두고, 글자만 초록/빨강으로 하라고 지적.
  - 2026-07-09: 기존 시계 asset을 결합하는 방식이 아니라, 도장 자체를 단일 이미지로 생성해야 한다고 지적.
- 조치: 도장형 과밀 그래픽과 상태색 시계 배경을 버리고, 단일 생성 이미지 안에 애니메이션풍 시계 도장+`정답!`/`실패!` 텍스트가 포함되도록 재생성.
- 규칙화 메모: 아직 3회. 반복되면 "학습 피드백 이미지는 핵심 메시지 텍스트와 배경 메타포를 분리하고, 배경 오브젝트는 화면 기존 asset 팔레트를 유지하며 상태색은 텍스트/강조에만 쓴다. 사용자가 단일 asset을 요구하면 기존 asset 합성/코드 합성 대신 생성 이미지 하나로 만든다" 규칙을 asset generation workflow에 제안 후보.

### [character-asset-identity-alpha] 캐릭터 에셋의 정체성 불일치 또는 의상 투명도 오류

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`assets/teacher_*.png`, `assets/kid_librarian_*.png`)
- 분류 태그: character-asset-identity-alpha
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 사용자가 캐릭터 에셋 재생성이 필요하다고 지적. 사서 선생님은 치마가 투명하게 보이고, 학생/꼬마 사서는 원래 필요한 캐릭터가 아니라 다른 학생이 생성됨.
  - 2026-07-09: 꼬마 사서는 `kid_librarian_explaining.png`를 anchor로 삼는 방식도 버리고, 기존 꼬마 사서 에셋과 무관한 새 캐릭터로 설계하길 요청. 기존 에셋은 사용처/실패 사례 참고로만 취급해야 함.
  - 2026-07-09: 이미지 생성 실행 중 sub-agent를 쓰겠다고 해놓고 실제 생성 작업을 메인 에이전트가 단독 진행함. 또한 raw 크로마키 결과라 배경이 투명하지 않았고, `teacher_worried`의 돋보기가 손에 잡혀 있지 않아 포즈/소품 요구를 만족하지 못함.
  - 2026-07-10: output/assets의 꼬마 사서가 포즈마다 성별이 바뀜 — `idle`/`success`/`confused`는 예전 남자아이(7/8 생성), `explaining`만 새 여자아이(7/9 교체됨). 사용자가 asset-revisions final(일관된 여자아이)로 나머지도 교체 요청.
    - 조치: 두 세트 비교 montage로 불일치 확인(현재 idle/success/confused=남아, revision 전부=여아). revision final의 alpha 투명 검증 후 `kid_librarian_idle/success/confused.png`를 output/assets에 복사(파일명 동일 → HTML 수정 불필요). 교체 후 4개 포즈 여자아이 일관성 시각 확인.
- 조치: 원본 기획(`2학년_8차시(시간)_임상현_no_img.md`)과 산출 HTML의 캐릭터 사용 위치를 대조해 필요한 캐릭터별 포즈와 화면 배치 검토. 이후 꼬마 사서 design/prompt를 "reference image 없음, 텍스트 identity가 source of truth" 방식으로 수정. 이미지 생성 단계는 sub-agent 병렬 실행과 final alpha PNG 검증을 명시적으로 수행하도록 재진행.
- 규칙화 메모: 아직 3회. 반복되면 "캐릭터 에셋 생성 시 동일 인물 참조/의상 불투명/PNG alpha 검수/scene별 pose sheet 대조. 기존 에셋이 실패 사례인 경우 anchor로 쓰지 않고 새 textual identity를 source of truth로 명시. 생성 실행 시 raw/chroma 결과와 final alpha 결과를 구분하고, 소품을 손에 쥐는 등 포즈 핵심 요구를 QA한다" 규칙을 asset generation 또는 design review 단계에 제안 후보.

### [asset-batch-incomplete-execution] 캐릭터 에셋 배치를 일부만 생성하고 전체 세트를 완료하지 않음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/characters/generated/
- 분류 태그: asset-batch-incomplete-execution
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 사용자가 "이미지를 만들어줘"라고 전체 캐릭터 세트 생성을 요청했는데, `teacher_worried.png`와 `kid_librarian_explaining.png` 2개만 생성/검증하고 멈춤. 전체 포즈 세트를 끝까지 생성해야 한다고 지적.
- 조치: 남은 포즈 전체(`teacher_pointing`, `teacher_happy`, `kid_librarian_idle`, `kid_librarian_success`, `kid_librarian_confused`, `kid_librarian_proud`)를 sub-agent 병렬 배치로 생성하고 final alpha PNG 검증까지 진행.
- 규칙화 메모: 아직 1회. 반복되면 "asset batch 요청은 대표 샘플 성공으로 종료하지 말고, poses.md의 전체 required/optional 범위를 명시적으로 완료/보류 판정한다" 규칙을 asset generation workflow에 제안 후보.

### [character-pose-direction-mismatch] 캐릭터가 요구된 방향이 아닌 반대 방향을 가리킴

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/characters/generated/final/kid_librarian_explaining.png
- 분류 태그: character-pose-direction-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: `kid_librarian_explaining.png`가 오른쪽 상단을 가리키고 있는데, 의도는 왼쪽 상단을 가리키는 포즈라고 지적.
- 조치: `kid-librarian/poses.md`와 `prompts/batch-01.md`를 viewer 기준 왼쪽 상단을 가리키도록 명시하고, 해당 이미지를 재생성. final alpha PNG 검증 후 `output/assets/kid_librarian_explaining.png`에도 교체 반영.
- 규칙화 메모: 아직 1회. 반복되면 "포즈 방향은 left/right 대신 viewer 기준/화면 기준/캐릭터 기준을 함께 명시하고, 생성 후 시각 QA에서 방향을 확인" 규칙을 asset generation workflow에 제안 후보.

### [bg-anchor-alignment] 배경 아트에 그려진 자리(거치대/프레임)에 요소가 안 맞고 다른 곳에 배치됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#bigClock`, `#s-tut .wb-clock`)
- 분류 태그: bg-anchor-alignment
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 배경(bg_library_messy_lobby.png)에 시계가 들어갈 원형 거치대가 그려져 있는데, 벽시계가 그 원 밖 다른 위치에 정적 %로 배치되어 있었음. 원의 중심·크기에 맞춰 시계를 앉혀야 함. `background-size:cover`라 뷰포트 종횡비마다 원의 화면 좌표가 달라져 정적 %로는 정렬 불가.
    - 조치: 배경 아트에서 원의 중심선(중심 (862,292), 반지름 155)을 픽셀 측정 → 런타임에서 cover 스케일·크롭을 계산해 시계 중심/지름을 원에 맞추는 JS(`__placeBigClock`, resize 대응) 추가. 시계 PNG의 외곽 rim 채움비(0.859)까지 반영해 rim이 원과 일치하도록 크기 산정.
  - 2026-07-09: 튜토리얼 작업대 매트(repair_workbench_mat_blank.png) 위 시계가 좌하단에 치우쳐 매트에 그려진 연필과 겹침. 매트(푸른 영역) 상하 가운데로 올리고 오른쪽으로 살짝 이동해 연필과 분리 필요.
    - 조치: `#s-tut .wb-clock`을 `top:50%;transform:translateY(-50%);left:14%;width:24%`로 매트 세로 중앙+우측 이동. (workbench는 object-fit:contain이라 asset 좌표가 안정적이라 % 배치로 충분)
  - 2026-07-09: 유형 C 모니터 화면(`.mon-screen`) 텍스트가 모니터 유리 밖으로 삐져나옴("글자가 모니터 안에 안 들어감"). 원인: `library_monitor_body.png`는 세로형(1182×1330)인데 `.monitor-stage` aspect가 `1.5/1`(가로)이라 `object-fit:contain`으로 이미지가 레터박스(좌우 여백)되고, `.mon-screen`은 스테이지(박스) 기준 %라 실제 이미지의 화면 유리 위치와 어긋남. 게다가 height:50%로 유리(측정 34%)보다 큼.
    - 조치: 화면 유리를 픽셀 측정(flood-fill: left25.2/top14.4/w49.1/h34%). `.monitor-stage` aspect를 이미지에 맞춰 `1182/1330`으로 바꿔 레터박스 제거(박스=이미지). `.mon-screen`을 유리에 정렬(left26/top15.5/w47/h32.5, 약 1% inset). 세로형이라 `#s-c .monitor-stage` 폭 760→600px로 축소, 좁아진 유리에 맞게 mon-status/timeline/mon-q/eq-line/cblank 글자·gap 축소. 상단 상태문구(C_INTRO) 중복 꼬리 제거(안내는 새 선생님 말풍선이 담당). 오버레이 사각형을 아트에 그려 유리 안 정렬 시각 검증.
  - 2026-07-09: 이야기(s-story) 책 이미지가 너무 작고 텍스트가 책 지면 밖으로 넘침. 원인: `storybook_base.png`(1536×1024, aspect 1.5)인데 `.book-stage` aspect가 `1.4/1`이라 레터박스 발생 + `#s-story .book-page` 영역(top14/height64 → 하단 78%)이 실제 크림 지면(측정 하단 73.6%)보다 아래까지 내려가 글자가 페이지 밖으로 새어나감.
    - 조치: 크림 지면 픽셀 측정(left11.8/top8.3/w76.4/h65.3%). `.book-stage` aspect를 `1536/1024`로 맞춰 레터박스 제거하고 폭 860→1000px로 확대. `#s-story .book-page`를 금색 테두리 안(left13/top11/w74/h60%)으로 재정렬해 좌:삽화 우:글이 양 지면에 담기도록. 오버레이 사각형+접힘선 렌더로 정렬 시각 검증.
- 규칙화 메모: 4회. 교훈: **asset을 얹는 컨테이너는 `aspect-ratio`를 asset 원본 비율에 맞춰라 — 안 맞으면 `object-fit:contain`이 레터박스를 만들어 %좌표 오버레이가 어긋난다.** 반복되면 "배경/asset에 그려진 앵커(거치대/프레임/슬롯/화면유리/책지면)에 얹는 요소는 (a)컨테이너 aspect를 asset에 맞추고 (b)앵커 영역을 픽셀 측정해 %로 정렬, 소품과 겹치지 않게" 규칙을 builder_system.md에 제안 후보. (5회 임계 근접)

### [sequential-scene-choreography] 스토리 씬이 순차 대사 연출 없이 단일 장면·단일 애니메이션으로 끝남

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-problem`)
- 분류 태그: sequential-scene-choreography
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 문제 인트로 씬이 스토리보드(시계 회전 → 선생님 대사1 → 2초 후 대사2 → 사서 등장 대사 → 수리하러 가기 버튼)처럼 순차 연출되어야 하는데, 모든 요소가 한 번에 뜨는 단일 장면·단일 애니메이션으로 끝남. 대사가 시간축을 따라 beat 단위로 전개되지 않음.
- 조치: `#s-problem`을 타임라인 기반 beat 연출로 재구성(시계 스핀 → 말풍선 순차 노출 → 꼬마 사서 pop-in → CTA 버튼). 말풍선은 temp/dialogue_plaque_set.png의 말풍선을 크롭한 asset을 배경으로 사용. auto-timed(2초 간격) + 탭하면 다음 beat로 스킵.
- 규칙화 메모: 아직 발생 1회. 반복되면 "스토리/인트로 씬은 단일 장면이 아니라 순차 beat 연출로" 규칙을 builder_system.md에 제안 후보.

### [redundant-surface-label-text] 에셋/대사로 이미 표현된 정보를 텍스트 라벨·접두어로 중복

- 대상: content-harness-pipeline (builder_system.md / design_review_system.md), 예: runs/2026-07-08_ch802d08/output/index.html
- 분류 태그: redundant-surface-label-text
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 말풍선 위 `.who` 요약 라벨(`📢 도서관 고장 알림`, `🕑 깨진 전광판 안내`)이 바로 아래 대사와 같은 내용을 중복. 전광판 asset 위에 얹힌 문제 문구를 JS가 `전광판: … — 같은 시각의 시계는?`로 감싸, 이미 전광판 이미지로 표현된 맥락을 텍스트로 다시 명명함. 한 번의 피드백에 같은 성격의 사례 3건.
  - 2026-07-09: (재발/실적용) 사용자가 유형 A 화면의 `🕑 깨진 전광판 안내` 라벨과 `aPrompt`의 `전광판:` 접두어를 "AI가 자주 하는 의미 없는 설명"이라며 삭제 요청. 실제로 제거함.
- 조치: 유형 A(`#s-a`)에서 `.who`(🕑 깨진 전광판 안내) 라벨 제거, `aPrompt.innerHTML`에서 `전광판:` 접두어 제거. (검토 단계) builder에 중복 라벨/표면명 접두어 금지 제약 + design_review text_review에 "텍스트↔시각 중복" 판정 축 추가 제안은 사용자 승인 대기.
- 규칙화 메모: 최초 피드백 3사례 + 재발 1건(발생 횟수 2로 집계). 승격 임계값 5회 미도달. 도달 시 builder_system.md와 design_review_system.md 양쪽에 반영 제안.

### [asset-revision-refine-routing] asset 재생성 후 builder 재빌드 대신 refine으로 반영

- 대상: content-harness-pipeline/runner.py
- 분류 태그: asset-revision-refine-routing
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-07-08
- 사례:
  - 2026-07-08: 사용자가 design_review가 asset 생성 또는 수정을 요구했을 때 builder를 다시 돌리면 기존 refine 결과를 잃을 수 있으므로, asset 변경 후에는 refine으로 이어져야 한다고 지적했다.
- 조치: asset revision 흐름이 asset generator 이후 `builder_only`가 아니라 기존 HTML을 기준으로 `design_refine`을 실행하도록 수정한다.
- 규칙화 메모: 아직 발생 1회로 rule 승격 대상이 아니다.

### [intro-title-raster-image] 인트로 타이틀을 게임형 이미지 타이틀로 교체

- 대상: content-harness-pipeline/runs/2026-07-08_2d08c0de/output/index.html
- 분류 태그: intro-title-raster-image
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-07-08
- 사례:
  - 2026-07-08: 사용자가 인트로의 `시간이 뒤죽박죽! / 수학의 힘으로 도서관 시계를 수리하라!` 문구를 예시처럼 이미지 생성 타이틀로 만들고, 1번 후보를 인트로에 삽입하길 요청했다.
  - 2026-07-08: 사용자가 삽입된 생성 이미지를 화면 가운데에 오게 하고, 주변 화면을 어둡게 만들어 아직 시작하기 전이라는 느낌을 주길 요청했다.
- 조치: 이미지 생성 후보 1번을 `output/assets/intro_title_time_repair_v1.png`로 복사하고 인트로 타이틀 영역에 삽입한다. 이후 인트로 이미지 타이틀을 중앙 정렬하고 배경 dim/vignette를 강화한다.
- 규칙화 메모: 아직 발생 2회로 rule 승격 대상이 아니다.

### [backdrop-filter-render-artifact] dim/blur 오버레이의 backdrop-filter가 검은 선·깜빡임 유발

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-title::after`)
- 분류 태그: backdrop-filter-render-artifact
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 인트로 배경을 어둡게/흐릿하게 하려고 `#s-title::after`에 `backdrop-filter:blur(2.5px)`를 추가했더니, 타이틀 이미지 위에 특정 조건(합성 프레임)에서 검은색 선이 나타나고 dim 처리가 프레임마다 불안정하게(어두웠다 밝았다) 렌더됨. 헤드리스 스크린샷 두 컷에서 dim/blur 적용이 서로 달라 재현됨.
- 조치: `backdrop-filter`(및 `-webkit-` 접두어)를 제거하고 dim은 radial-gradient + rgba 오버레이만으로 처리. 흐림이 꼭 필요하면 backdrop-filter 대신 별도 블러 배경 레이어로 구현.
- 규칙화 메모: 아직 발생 1회. 반복되면 "오버레이 dim은 backdrop-filter 대신 gradient/rgba로" 규칙을 content-harness-pipeline/AGENTS.md에 제안 후보.

### [content-scale-too-small] 초등생용인데 이미지·글자가 너무 작음

- 대상: content-harness-pipeline (builder 산출물 전반), 예: runs/2026-07-08_ch802d08/output/index.html
- 분류 태그: content-scale-too-small
- 상태: 제안됨
- 발생 횟수: 6
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 콘텐츠가 초등학생용인데 이미지와 글자가 너무 작다. 지금보다 훨씬 크게 요청. 화면은 full-viewport stage에 clamp(min,vw,max) 기반 스케일이라 큰 화면에서 max 천장에 걸려 작게 보임.
    - 조치: clamp() 상단(vw 계수·max)을 ~1.28배로 올려 큰 화면에서 확대(작은 화면 min은 유지). 표면 박스와 그 안 텍스트를 같은 배율로 키워 art 안에 글자가 유지되도록 함. 튜토리얼 씬 오버플로는 티켓 tray를 한 줄(`flex-wrap:nowrap`)로 고정해 해결.
  - 2026-07-09: 전역 확대 후에도 캐릭터가 작다고 판단, 캐릭터(`.char`)만 현재 크기에서 추가 1.3배 요청.
    - 조치: `.char` height 3개 규칙(기본/`#s-problem`/모바일)의 vh 계수·max를 ×1.3, min 유지. 대사·티켓·작업대와 겹침 없음 확인.
  - 2026-07-09: 튜토리얼 씬의 설명글·질문·힌트 텍스트가 전체적으로 작음(초등 대상). `.wb-note`(clamp .6~1.05rem), `.wb-slot .qhint`(clamp .72~1.254rem) 등이 낮은 max 천장에 걸림.
    - 조치: 튜토리얼 스코프에서 질문/힌트/카드 글자 clamp를 상향(질문 max 1.254→1.72rem 등).
  - 2026-07-09: 튜토리얼 가운데 테이블(작업대)과 탁상시계가 전체적으로 작다며 키워달라고 요청. (같은 대상 반복 요청 — 한 번 키운 뒤에도 더 키워달라 함)
    - 조치: `#s-tut .workbench` 폭 780→860→**1118px(≈1.3배 추가)**, `.wb-clock` 24%→27%(판 확대로 시계도 비례 확대). 넓어진 보드가 우측 말풍선을 가리지 않도록 `.wb-slot`을 안쪽(right:11%, width:40%)으로 이동. 위로 올려달라는 요청에 `center-col` top 61%→54%. (같은 대상 반복 튜닝이라 발생 횟수는 증분하지 않고 이 사례에 통합.)
  - 2026-07-09: CTA 버튼 폰트가 너무 작음 — 인트로 `#btnStart`("시작하기"), 문제 씬 `#btnToTutorial`("시계의 힘으로 수리하러 가기"). 티켓 asset 위 텍스트가 asset 대비 작게 보임(`.ticket-btn` font clamp max 1.485~1.613rem).
    - 조치: `#btnStart` font clamp max 1.613→2.05rem, `#btnToTutorial` 1.485→1.74rem으로 상향(nowrap/keep-all 유지).
  - 2026-07-09: 유형 B(코르크 시간표 보드)의 미니 시계가 작아서 안 보임. `loadB`의 `miniclock` size가 데스크톱 78/모바일 62로 낮음. (같은 대상 반복 튜닝: 120→150으로 한 번 더 확대 요청)
    - 조치: `loadB`에서 clock size를 데스크톱 78→120→150→**175**/모바일 62→92→112→**130**로 확대, 빈 시계 placeholder도 동일 size로 맞춤. 확인 버튼을 보드 밖으로 빼 세로 여백 확보. `bContent`를 `justify-content:space-between`으로 바꿔 제목을 위, "걸린 시간=" 식을 아래로 벌리고 시계를 가운데에 크게 배치(영역은 top:12%/height:76% → 위·아래 2%씩 안쪽으로 top:14%/height:72% 조정). 시계 아래 라벨(시작/끝, `.qhint` .72rem/ink-soft)이 흐려 잘 안 보이던 것을 clamp(.86~1.15rem)·`font-weight:800`·`color:#4a2b0e`로 키우고 진하게. (발생 횟수는 같은 대상 반복이라 증분하지 않고 통합)
- 규칙화 메모: **발생 5회 → rule 승격 제안.** 초안: "초등(저학년) 대상 콘텐츠는 본문/질문/힌트/**버튼(CTA)** 글자 clamp의 max와 vw 계수를 성인 기준보다 크게 잡는다(예: 본문 max ≥ 1.6rem, 주요 CTA max ≥ 1.8rem). 표면 박스/티켓 asset 위 텍스트도 동일 배율." 반영 위치: content-harness-pipeline/builder_system.md. 사용자 승인 대기.

### [label-text-wrapping] 짧은 라벨(숫자+한글 토큰)이 좁은 표면에서 글자 단위로 줄바꿈됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`.card`, 튜토리얼 드래그 카드)
- 분류 태그: label-text-wrapping
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼 씬의 드래그 카드가 "3시"인데 좁은 카드 폭에서 "3 / 시"로 두 줄로 쪼개져 보임. `.card`에 `white-space`/`word-break` 지정이 없어 브라우저 기본값이 숫자(3)와 한글(시) 경계에서 줄바꿈을 허용함.
    - 조치: `.card`에 `white-space:nowrap`을 추가해 짧은 토큰이 한 줄로 유지되도록 함(!important 미사용).
  - 2026-07-09: 유형 C 모니터 화면의 질문/식이 한글 음절 단위로 줄바꿈됨("내일 오/후", "지나/면?"). `#s-c .mon-q`/`.eq-line`에 word-break 지정이 없어 좁은 화면 유리에서 단어 중간이 깨져 어색함.
    - 조치: `#s-c .mon-screen .mon-q`/`.eq-line`에 `word-break:keep-all` 추가(단어 경계에서만 줄바꿈). 모니터도 10%(640→704px) 확대해 줄바꿈 자체를 줄임.
- 규칙화 메모: 아직 1회. 반복되면 "짧은 라벨/버튼 토큰은 글자 단위 줄바꿈 방지(white-space:nowrap 또는 word-break:keep-all)" 규칙을 builder_system.md에 제안 후보.

### [fixed-pos-transformed-ancestor] position:fixed 드래그가 transform 조상 때문에 잡는 순간 우측 하단으로 점프

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`enableDrag`, `.card`/`.num-block`, 조상 `.center-col`)
- 분류 태그: fixed-pos-transformed-ancestor
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼("지금 멈춰있는 이 시계는 몇 시일까?")에서 3시/4시/5시 카드를 잡으면 마우스 포인터를 따라오지 않고 우측 하단으로 일정하게 튀고, 나머지 카드가 작아진다고 지적. `enableDrag`가 드래그 시 `el.style.position='fixed'`로 바꾸고 `left=origRect.left`(getBoundingClientRect=뷰포트 좌표)를 넣는데, 카드의 조상 `.center-col`에 `transform:translate(-50%,-50%)`가 있어 position:fixed의 컨테이닝 블록이 뷰포트가 아니라 그 조상이 됨. 그래서 뷰포트 좌표를 그대로 넣으면 조상의 뷰포트 offset만큼(측정값 +342,+228) 우측 하단으로 점프. Playwright 헤드리스로 pointerdown 즉시 카드 중심 (519,708)→(861,936) 점프 재현 확인. "카드 작아짐"은 카드를 position:fixed+margin:0로 flex 흐름에서 빼면서 tray가 재배치된 부수효과.
- 조치: `enableDrag`를 position:fixed+left/top 방식에서 **`transform:translate(dx,dy)` 델타 이동** 방식으로 교체(요소를 흐름에 유지, 컨테이닝 블록과 무관하게 포인터 델타만큼 이동). 드래그 중 `transition:none`으로 지연 제거. CSS/`!important` 미사용. 드롭 판정(`hitBlank`, clientX/Y 기반)은 그대로.
- 규칙화 메모: 아직 1회. 반복되면 "드래그로 요소를 움직일 때 position:fixed+뷰포트좌표 대신 transform:translate 델타를 쓴다(transform 조상 컨테이닝블록 문제 회피)" 규칙을 builder_system.md에 제안 후보.

### [dialogue-as-speech-bubble] 캐릭터 대사를 표면 빈 공간에 억지로 넣지 말고 말풍선/상단으로

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .wb-note`)
- 분류 태그: dialogue-as-speech-bubble
- 상태: 제안됨
- 발생 횟수: 5
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼에서 꼬마 사서 대사("걱정 마세요! …")를 작업대 보드의 빈 공간(`.wb-note`)에 작게 끼워 넣었는데, 위치가 어색하고 글자도 작음. 대사이므로 인트로처럼 캐릭터 위 말풍선으로 올리거나 상단에 크게 배치하는 게 맞음.
    - 조치: `.wb-note` 제거. `.speech`(말풍선 asset) 컴포넌트로 꼬마 사서 대사를 배치.
  - 2026-07-09: (후속) 말풍선을 상단 코너(`top:5%`)에 고정했더니 캐릭터와 떨어져 "붕 떠 보인다"고 지적. 인트로처럼 캐릭터 머리 옆에 붙여야 함.
    - 조치: 상단 코너 고정 제거. 인트로와 동일하게 head-height 앵커(`.speech` 기본 `bottom:calc(var(--char-h)-3rem)`)로 되돌리고 좌/우 5%로 캐릭터 옆 배치. 중앙 보드는 `top:61%`로 낮추고 폭(≤780px) 축소해 말풍선과 분리.
  - 2026-07-09: 유형 A에서 사서 선생님 안내 대사가 전광판(plaque) 안의 `.msg` 텍스트로 들어가 있었음. 사용자가 "선생님 대사니까 말풍선으로 바꾸고 이전 말풍선을 재사용하라"고 지적.
    - 조치: plaque의 `.msg` 제거, `#s-a`에 `.speech.teacher-say`(기존 speech_bubble asset 재사용) 추가. 전광판(plaque)과 겹치지 않게 말풍선은 `left:3%`로 좌측 고정, plaque 폭은 620px로 축소.
  - 2026-07-09: 유형 B(시간표 복구)도 유형 A처럼 사서 선생님을 왼쪽에 세우고, 보드에 있던 안내 문구(📌 독서 교실 시간표가 지워졌어요…)를 지운 뒤 선생님 안내 대사를 말풍선(speech_bubble)으로 넣도록 요청.
    - 조치: `#s-b`에 `char left`(teacher_pointing)와 `.speech.teacher-say`(기존 speech_bubble asset 재사용) 추가, `#s-b .speech` 스코프 CSS를 유형 A와 동일하게 지정. `loadB`의 `board-note-title`(`B_INTRO`) 라인 제거 및 미사용 `B_INTRO` 변수 삭제.
  - 2026-07-09: 유형 C(도서 대출 시스템 재부팅)에도 A·B처럼 사서 선생님 말풍선을 추가해달라고 요청(사용자가 첨부한 md는 다른 차시 SB였고, 이 run의 실제 원본 `2학년_8차시(시간)_임상현.md` Scene 3의 도입 대사를 사용).
    - 조치: `#s-c`에 `.speech.teacher-say`(기존 speech_bubble asset 재사용) 추가, 대사는 원본 SB Scene 3 도입 대사("도서 대출 시스템을 다시 켜려면 시간의 규칙을 풀어야 해! 1일과 24시간의 관계를 잘 생각해서 블록을 알맞게 넣어주렴!"). `#s-c .speech` 스코프 CSS를 A·B와 동일하게 지정.
- 규칙화 메모: **5회 → rule 승격 제안.** 초안: "캐릭터 발화는 표면(plaque/board/monitor) 텍스트가 아니라 화자 머리 옆(head-height) 말풍선(speech_bubble asset)으로 재사용하고, 미션 씬마다 화자(사서 선생님/꼬마 사서) 안내 말풍선을 일관되게 배치한다. 중앙 오브젝트와 겹치면 오브젝트를 낮추거나 줄여서 확보." 반영 위치: content-harness-pipeline/builder_system.md. 사용자 승인 대기.

### [weak-drag-affordance] 드래그 상호작용의 유도가 약함(정적 힌트만)

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut` 튜토리얼 카드/슬롯)
- 분류 태그: weak-drag-affordance
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: "아래 시간 티켓을 여기로 드래그!" 정적 텍스트만으로는 행동 유도가 약함. 카드 아래에 반짝이는 큐, 카드 자체의 grab 유도(글로우), 그리고 카드를 잡고 있는 동안 놓을 슬롯을 강하게 하이라이트하는 피드백이 필요.
- 조치: 빈 슬롯 pulse 애니메이션(`slotPulse`) + 카드 grab 유도 글로우(`cardInvite`) + tray 아래 sparkle 큐(`.tut-drag-cue`, `cueBounce`) 추가. `enableDrag`에 잡는 순간 대상 blank에 `.armed`(강조) 부여/해제 로직 추가(전 미션 공통 이점).
- 규칙화 메모: 아직 1회. 반복되면 "드래그 학습 상호작용은 (a)소스 grab 유도, (b)잡는 동안 타깃 하이라이트, (c)타깃 상시 pulse 큐를 기본 제공" 규칙을 builder_system.md에 제안 후보.

### [drag-drop-snap-fit] 드롭 시 카드가 슬롯에 물려야 하는데 텍스트만 기록되고 카드/슬롯 크기 불일치

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut #tutBlank`, `.card`)
- 분류 태그: drag-drop-snap-fit
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 정답 카드를 드롭하면 작은 `.blank`(82x66)에 "3시" 텍스트만 써지고 실제 카드는 tray에 opacity로 남아, 카드가 슬롯에 물려 들어가는 물리적 UX가 아님. 슬롯을 카드 크기에 맞추고, 카드가 그대로 슬롯에 스냅되어야 함.
    - 조치: `#tutBlank`을 티켓 카드 크기(aspect 1417/1140)로 확대. 정답 onDrop에서 텍스트 기록 대신 실제 카드 엘리먼트를 슬롯에 `appendChild`하여 스냅(`.placed`), 슬롯은 `.filled`로 카드 프레이밍.
  - 2026-07-10: 튜토리얼에서 정답을 맞히면 카드 크기가 변해 보임. 원인: 슬롯(`#tutBlank` `clamp(142px,24.5vw,206px)`)을 카드(`clamp(134px,23vw,196px)`)보다 크게 "프레임"으로 잡아서, 196 카드가 206 슬롯 안에 스냅되며 더 작아 보임.
    - 조치: 슬롯 폭을 카드와 동일한 `clamp(134px,23vw,196px)`로 맞춤 → 빈 슬롯·트레이 카드·스냅된 카드가 모두 같은 폭이라 크기 변화 없음.
- 규칙화 메모: 2회. 교훈: "드롭 타깃은 소스와 **정확히 동일 크기**로(프레임 여백을 주지 말 것), 드롭 성공 시 소스를 타깃에 물리적으로 스냅(텍스트 대체 금지)" 규칙을 builder_system.md에 제안 후보.

### [clock-hand-overflow] 아날로그 시계 바늘 길이가 문자판을 벗어남

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`.clock .hand.minute/.hour`)
- 분류 태그: clock-hand-overflow
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 시계 분침(`height:37%`)/시침(`height:26%`)이 너무 길어 문자판(숫자 12 근처)을 뚫고 삐져나옴.
- 조치: `.hand.minute` 37%→30%, `.hand.hour` 26%→21%로 전역 축소(문자판 안쪽 유지). 원점은 `--cy` 유지.
- 규칙화 메모: 아직 1회. 반복되면 "div로 그린 시계 바늘 길이는 문자판 반지름(숫자 링) 안쪽으로 제한(분침 ≤ ~0.32 지름)" 규칙을 builder_system.md에 제안 후보.

### [feedback-as-character-bubble] 학습 피드백이 좁은 태그에 세로로 깨지고 캐릭터 발화가 아님

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut` `.status-tag`)
- 분류 태그: feedback-as-character-bubble
- 상태: 제안됨
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 정답/오답 피드백이 3:1 좁은 `.status-tag` 표면에서 세로로 깨져 보이고, 피드백을 캐릭터(사서 선생님)가 말풍선으로 주면 더 자연스러움.
  - 2026-07-09: 활동 2 유형 A/B의 오답 피드백("다시 생각해보세요" 등)이 스펙과 달리 상단 `.status-tag`로 뜨고, 스펙이 요구한 "화면 중앙 말풍선 + 👆(손가락) 아이콘 2초 팝업"이 미적용됨.
  - 2026-07-09: (후속) 위에서 만든 `.hint-pop`이 "그냥 (흰) 카드"라 부자연스럽다고 지적. 원래 오답 피드백이 담겼던 in-world 이미지(`library_feedback_status_tag_blank.png`)에 담으라고 요청.
  - 2026-07-09: (후속) 오답 팝업은 좋으나 (a) 👆 손 이모지는 빼고, (b) 정답 피드백도 오답과 "똑같은 크기·위치" 팝업에 표시하되, 정답 note가 좁은 `.status-tag`에서 글자 단위로 세로로 깨지던 것을 가로로 표시하라고 요청.
  - 2026-07-09: (후속) in-world 이미지 표면에 얹으니 여전히 글자가 세로로 깨지고(고정 aspect PNG + `display:flex`의 min-content 축소) 크림색 여백 중앙정렬도 안 맞음. 사용자가 "차라리 이미지 없애고 자체 CSS 카드로 정답/오답 처리하자"고 결정.
    - 조치: 튜토리얼은 `.speech`(teacher-say) 말풍선으로 라우팅(1차). 활동 2 유형 A/B 정답·오답은 화면 중앙 `.hint-pop`으로 통합. 👆 아이콘 제거. 세로 깨짐의 원인은 flex 아이템이 min-content(가장 긴 단어)로 축소된 것. **PNG 표면(`library_feedback_status_tag_blank.png`) 폐기 → 순수 CSS 카드**로 전환(당시엔 이게 가변 텍스트에 최적).
  - 2026-07-10: 이제 정오답 피드백을 전용 **도장 이미지**(`stamp_correct_time.png` 정답!, `stamp_fail_time.png` 실패!)로 주자고 요청. 지금은 문자열 CSS 카드(`hintPop`)만 준다고 지적. (도장 asset은 `[feedback-stamp-visual-overload]`에서 다듬어 둔 것)
    - 조치: 공용 `.stamp-fx` 오버레이(도장 img + 선택적 개념 note 칩) + `showStamp(ok,note,ms)` 추가(쾅 찍히는 slam 애니메이션). 유형 A(`pickA`)·유형 B(`submitB`)의 `hintPop` 6곳을 `showStamp`로 교체(정답=녹색 시계 도장, 오답=금 간 시계 도장, 개념 note는 도장 아래 작은 칩으로 유지). 이어서 **튜토리얼**(정답/오답 드롭 시 도장, 기존 선생님 말풍선+꼬마 사서 표정+카드 흔들림은 유지)과 **퀴즈**(정답/오답 시 `showTag`→`showStamp` 교체, 정답 설명은 quizWin 말풍선이 담당)까지 확장. `hintPop`/`showTag`(quiz) 호출은 도장으로 대체. 유형 C는 자체 모니터 재부팅 연출 유지.
  - 2026-07-10: 피드백 시 꼬마 사서가 pose를 바꾸는데(성공/당황), 그 캐릭터 옆에 **간단한 말풍선 대사**(정답="정답이야!", 오답="다른 방안을 생각해보자")를 **모든 문제**에 달아달라고 요청.
    - 조치(1차): 공용 `.kid-say` CSS 말풍선 1개 + JS로 캐릭터 머리 옆 배치. → **사용자가 "새 말풍선 말고 기존에 쓰던 걸 재사용"이라 지적.**
    - 조치(2차): 커스텀 `.kid-say` 폐기하고 **기존 `.speech.kid-say`(speech_bubble 그림 에셋) 컴포넌트 재사용**. 각 씬(튜토리얼/유형 A/B/C) dlg-area에 `.speech.kid-say` 요소 추가(오른쪽 꼬마 사서 → 기본 right:19%+`_r.png` 오른쪽꼬리), 퀴즈는 왼쪽 꼬마 사서라 `#s-quiz .speech.kid-say{left:9%;background:speech_bubble_blank.png}`로 좌측·왼쪽꼬리로 뒤집어 재사용. `showKidSay(el,ok)`는 해당 speech의 `.msg`를 갱신하고 `.on` 토글. 정오답 10곳 연결(유형 C 오답·퀴즈 오답은 표정 변경도 함께). 도장(`showStamp`)과 병행.
- 규칙화 메모: **4회 → rule 승격 제안.** 교훈: 정오답 피드백은 (a)캐릭터 pose 변화 + (b)캐릭터 옆 간단 말풍선(고정 짧은 대사) + (c)중앙 도장/이미지의 3층으로 일관되게. 가변 길이 개념 설명만 별도 텍스트 칩. 초안 규칙: "미션/퀴즈 정오답 피드백은 씬마다 캐릭터 표정 변화 + 캐릭터 말풍선 짧은 대사를 기본 제공하고, 중앙 도장 이미지로 강조한다." 반영 위치: builder_system.md. 사용자 승인 대기.

### [card-aspect-stretch] flex 트레이의 align-items:stretch가 카드 aspect-ratio를 덮어 세로로 늘림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .card-tray`, `.card`)
- 분류 태그: card-aspect-stretch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 3시/4시/5시 티켓 카드가 위아래로 늘어나 보임(세로로 큼). 1차 원인은 부모 `.card-tray`(display:flex)의 기본 `align-items:stretch`가 카드 `aspect-ratio`를 덮어써 세로로 늘림.
  - 2026-07-09: (명확화) 요구의 핵심은 "카드 세로 높이를 줄여라"였음. stretch를 꺼 티켓 원본 비율(1417/1140)로 되돌렸어도 여전히 세로가 있었음 → 원본보다 더 납작하게 만들어야 함.
- 조치: `#s-tut .card-tray{align-items:center;}` + `#s-tut .card{flex:0 0 auto;height:auto}`로 stretch 제거. 그 위에 `aspect-ratio`를 원본(1417/1140)보다 납작한 **1417/820**으로 설정해 가로 유지·세로 축소. 드롭 슬롯(`#tutBlank`)도 동일 비율로 맞춰 스냅 시 일치. 카드가 납작해진 만큼 상하 padding도 축소(14%/15%→9%/10%).
- 규칙화 메모: 아직 1회. 반복되면 "aspect-ratio를 쓰는 카드/타일을 flex 컨테이너에 넣을 때는 `align-items:stretch`(기본)를 끄고(center 등) `flex:0 0 auto`로 비율을 보존" 규칙을 builder_system.md에 제안 후보.

### [flex-child-wider-than-container-misalign] flex 자식이 컨테이너보다 넓으면 auto마진이 flex-start로 정렬돼 한쪽으로 쏠림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .center-col` / `.workbench`)
- 분류 태그: flex-child-wider-than-container-misalign
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼 판(작업대)을 1118px로 키웠더니 화면 중앙이 아니라 오른쪽으로 치우침. `.center-col`(flex column, `width:min(900px,94vw)`=900px)보다 `.workbench`(1118px)가 넓은데, workbench의 `margin:0 auto`가 교차축 여백이 음수가 되며 auto→0으로 처리되어 align-items:center가 무시되고 flex-start(왼쪽)로 붙어 오른쪽으로 오버플로.
    - 조치: `#s-tut .center-col{width:min(1180px,96vw)}`로 컨테이너를 판보다 넓게 잡아 중앙 정렬 복구.
  - 2026-07-09: (재발) 이야기(s-story) 책을 1120px로 키웠더니 가운데 정렬이 깨져 한쪽으로 쏠림. `.book-stage`(1120px)가 `.center-col`(min(900px,94vw)=900px)보다 넓어 동일 증상.
    - 조치: `#s-story .center-col{width:min(1160px,98vw)}`로 컨테이너를 책보다 넓게 잡아 중앙 정렬 복구.
- 규칙화 메모: 2회. 반복되면 "flex 컨테이너 안의 요소(작업대/책/모니터 등 asset 스테이지)를 키울 때 컨테이너 폭을 자식보다 크게 유지 — 자식이 컨테이너보다 넓으면 `margin:0 auto`+align-items:center가 무너져 한쪽으로 쏠린다" 규칙을 builder_system.md에 제안 후보.

### [low-contrast-cue] 유도 문구가 배경색과 대비 부족으로 잘 안 보임

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .tut-drag-cue`)
- 분류 태그: low-contrast-cue
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B 보드의 문제 제목(`독서 교실이 8시에 시작해 9시에 끝났어요…`)이 코르크 배경 위에서 진갈색(`color:#5a3b1b`)이라 잘 안 보임. 다른 색으로 요청.
    - 조치: 제목을 크림색 라벨 칩(`#s-b .b-qtitle`, `background:rgba(255,248,232,.94)` + 진한 적갈색 글자 `#7a1f10`)으로 감싸 코르크 배경과 무관하게 고대비 확보.
  - 2026-07-09: "✨ 카드를 끌어서 놓아요 ✨" 큐가 갈색 계열(`color:#b5791b`)이라 나무 바닥/러그 배경 위에서 잘 안 보임. 더 하이라이트 필요.
    - 조치: 큐를 어두운 알약 배경(갈색 그라디언트)+금색 글자(`#ffe89a`)+내부 금테/글로우 box-shadow로 변경하고 bounce에 글로우 맥동 추가. 배경과 무관하게 대비 확보.
  - 2026-07-09: (후속) 큐가 실제 화면에서 아예 안 보인다고 지적. 원인은 대비가 아니라 **CSS 애니메이션 override로 인한 opacity 미해제**: 큐 엘리먼트에 `enter d3`가 있어 `.scene .enter{opacity:0}`로 시작하는데, opacity를 1로 올리는 `enterUp` 애니메이션이 내가 큐에 준 `cueBounce`(명시도 `#s-tut ...`가 더 높음)에 덮여 실행되지 않음 → opacity 0 고정. (검증 스크린샷은 opacity를 강제로 켜서 버그가 가려져 있었음.)
    - 조치: `#s-tut .tut-drag-cue`에 `opacity:1` 명시. opacity 강제 없이(실제 CSS만) virtual-time 렌더로 큐 표시 확인.
- 규칙화 메모: 아직 1회(가독) + 별개의 가시성 버그 1건. 반복되면 (a) "유도 큐/힌트는 고대비 칩으로", (b) "`.enter`(entrance opacity:0)를 가진 엘리먼트에 별도 `animation`을 주면 `enterUp` 리빌이 덮여 안 보일 수 있으니 opacity를 명시하거나 `.enter`를 빼거나 애니메이션을 합성" 규칙을 builder_system.md에 제안 후보.

### [ambient-effect-hover-only] 상시로 요구된 이펙트(글로우)를 호버 상태에만 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#btnStart`, `#btnToTutorial`, `.ticket-btn`)
- 분류 태그: ambient-effect-hover-only
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: CTA 버튼에 글로우가 필요하다고 했는데 `.ticket-btn`의 글로우/샤인이 `:hover`(및 `::before` 샤인 hover)에만 있어 평상시엔 글로우가 없음. 상시 글로우 필요.
    - 조치(1차): `z-index:-1` 헤일로 `::after` 레이어(금색 radial+blur)를 상시 맥동으로 추가.
  - 2026-07-09: (후속) 1차 글로우가 "너무 이상하다/부자연스럽다"고 지적. 원인은 `::after` radial 블롭이 **버튼(티켓) 실루엣을 안 따르고** 사각/타원 형태로 버튼 뒤·아래에 떠 보였기 때문.
    - 조치(2차): `::after` 블롭 제거. 대신 버튼에 **`filter:drop-shadow` 다중 레이어**를 적용 — drop-shadow는 티켓 PNG의 alpha(실루엣)를 따라 halo를 그려 자연스러움. filter는 등장(enterUp)/펄스(theartbeat)가 안 건드리는 속성이라 상시 유지됨(btnStart는 `.enter`가 `.blink`를 덮어 tblink가 애초에 실행 안 됨도 확인). hover엔 조금 더 강한 glow.
  - 2026-07-09: (후속) "조금 움직이는 효과를 줘" — 정적 글로우에 은은한 모션 요청.
    - 조치(3차): `ctaFloat` 애니메이션(transform translateY/scale + filter glow 맥동) 추가로 부드럽게 떠오르며 글로우가 숨쉬는 모션. **주의:** 처음엔 `animation:enterUp(opacity 0→1)+ctaFloat`로 합쳤더니 버튼이 아예 사라짐(opacity 애니메이션 조합 문제) → **opacity는 정적 1로 두고 ctaFloat은 transform/filter만** 애니메이션하도록 수정(등장 슬라이드는 포기, 가시성·모션 확보). `#btnToTutorial`은 `.dlg-cta.on`의 opacity:1 정적값 유지 + ctaFloat.
- 규칙화 메모: 아직 1회(+ 후속 자연스러움 교정). 반복되면 "(a) 글로우 등 분위기 이펙트는 `:hover`가 아니라 상시로. (b) **alpha 실루엣 asset(티켓/캐릭터 등) 위 글로우는 `::after` 사각/radial 블롭이 아니라 `filter:drop-shadow`로 실루엣을 따라 그린다.**" 규칙을 builder_system.md에 제안 후보.

### [spec-fx-color-mismatch] 스펙이 지정한 오답 강조 색/연출을 임의 색으로 바꿔 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-a` `.choice.correct-reveal`, `#s-b` 오답 로직)
- 분류 태그: spec-fx-color-mismatch
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 스펙(활동 2 Scene 1)은 "3회 오답 시 정답 시계가 붉은색으로 깜박인 후 강제 전환"인데, 유형 A 구현이 의도적으로 금색(`goldReveal`, 주석 "gold reveal, not red")으로 바꿔 스펙과 어긋남. 유형 B는 3회 오답 강제 전환/붉은 깜박 자체가 없었음.
    - 조치: 유형 A 3회 오답 리빌을 금색 → `wrong-reveal`(붉은 깜박, `redReveal`)로 변경. 유형 B에 `bWrong` 카운터 + 3회 오답 시 정답 리빌(붉은 깜박 `.kb-blank.reveal`) 후 강제 전환 추가(유형 A와 동일 로직).
  - 2026-07-10: 튜토리얼(#s-tut) 오답 시 (a)꼬마 사서가 슬퍼하지 않고(캐릭터 표정 미변경) (b)빈칸 카드 피드백(흔들림/빨강)도 안 나옴. 원인: `.blank.bad`(흔들림+빨강)이 있지만 더 높은 명시도의 `#s-tut #tutBlank:not(.filled)`(slotPulse 애니메이션 + border-color:wood-deep)이 덮어 shake/빨강이 죽음. 캐릭터는 유형 A와 달리 오답 시 `kid_librarian_confused` 교체 로직이 없었음.
    - 조치: `#s-tut #tutBlank.bad` 규칙(shake .4s + 빨강 border/box-shadow + 연분홍 배경)을 slotPulse 뒤에 배치해 명시도·소스순서로 이기게 함. 튜토리얼 꼬마 사서에 `id="tutKid"` 부여 후 오답 시 `kid_librarian_confused.png`(+tilt)→1.3초 뒤 explaining 복귀, 정답 시 `kid_librarian_success.png`(+cheer) 반응 추가.
- 규칙화 메모: 2회. 교훈: 스펙 오답 연출을 임의 색으로 바꾸지 말 것 + **정답/오답 피드백은 씬마다 일관되게(카드 흔들림·빨강 + 캐릭터 표정 변화)**. 또 **더 높은 명시도의 scoped 규칙(`#s-x #id:not(...)`)이 범용 `.bad` 상태 피드백을 조용히 덮을 수 있으니, 상태 피드백은 동일 명시도+소스순서 뒤 또는 더 높은 명시도로 보장**한다. builder_system.md에 제안 후보.

### [spec-mixed-answer-format-flattening] 스펙의 문제별 혼합 정답 형식을 유형별 단일 형식으로 획일화

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-a` `A_DATA`, `loadA`/`pickA`)
- 분류 태그: spec-mixed-answer-format-flattening
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 원본 스펙(`_no_img.md` 활동 2)은 유형 A 안에서도 문제 1·3은 "몇 분 전 텍스트 → 시계 고르기", 문제 2·4는 "시계 제시 → 문자열 보기 고르기"로 혼합 형식이었는데, 빌드는 4문제 모두 시계 고르기로 획일화했음. (초기엔 사용자도 단일 형식으로 가자고 했다가) 사용자가 2·4번을 스펙대로 "전광판에 시계 + 문자열 보기 카드"로 되돌리도록 요청.
- 조치: `A_DATA`에 `mode`('clock'|'text') 도입. 2·4번을 `mode:'text'`(`clock:[h,m]` 제시 + 문자열 `choices`/`answer`)로 변경. `loadA`가 mode별로 렌더(text 모드: 전광판 plaque에 `buildClock` + '이 시계와 같은 시각은?' + 문자열 보기는 넓은 티켓 카드 `.choice.choice-text`). `aIsCorrect(ch,q)`로 정오답 판정 통합, 3회 오답 리빌도 mode 무관 동작.
- 규칙화 메모: 아직 1회. 반복되면 "스토리보드가 문제별로 정답 형식(객관식 시계/문자열/키패드/드래그)을 다르게 지정하면 유형 단위로 획일화하지 말고 문제 단위 형식을 보존" 규칙을 builder_system.md에 제안 후보.

### [action-control-on-art-surface] 조작 버튼(확인/제출)이 아트 표면 안에 박혀 있어 밖으로 빼야 함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b #bSubmit`)
- 분류 태그: action-control-on-art-surface
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B의 "확인하기" 버튼이 코르크 보드(`bContent`) 안에 status-tag 이미지 표면으로 박혀 있어 답답함. 보드 아래로 빼달라고 요청.
- 조치: `bSubmit`을 `bContent`의 innerHTML(동적 생성)에서 분리해 `.center-col` 안 보드-스테이지 아래 정적 버튼(`.btn`)으로 이동. per-load로 붙던 click 리스너를 1회 바인딩으로 변경. `#s-b #bSubmit` 이미지(status-tag) 오버라이드 CSS 제거.
- 규칙화 메모: 아직 1회. 반복되면 "학습 조작 버튼(확인/제출/다음)은 문제 아트 표면 안이 아니라 표면 밖(아래) 표준 버튼으로 배치" 규칙을 builder_system.md에 제안 후보. (표면에 텍스트/컨트롤을 억지로 넣지 말라는 `[dialogue-as-speech-bubble]`·`[redundant-surface-label-text]`와 같은 계열)

### [weak-input-affordance] 탭 입력 칸(?박스)이 선택 가능함을 알리는 상시 어포던스가 없음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b .kb-blank`)
- 분류 태그: weak-input-affordance
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B의 정답 입력 `?`칸(`.kb-blank`)이 눌러서 선택하는 요소인데, 활성(`.active`) 전에는 아무 시각 신호가 없어 선택 가능한지 알기 어려움. 글로우/하이라이트로 선택 가능함을 알려야 함.
- 조치: `#s-b .kb-blank:not(.filled):not(.active)`에 상시 골드 글로우 펄스(`kbInvite`) 추가. 활성/입력완료 시에는 애니메이션이 멈추고 각각 `.active` 글로우/`.filled` 상태로 전환. (튜토리얼 빈 슬롯 `slotPulse`와 같은 상시 pulse 어포던스 계열)
- 규칙화 메모: 아직 1회. `[weak-drag-affordance]`(드래그 소스/타깃 유도)와 묶어 "탭·드래그 등 상호작용 대상은 유휴 상태에서도 상시 pulse/glow로 조작 가능함을 알린다" 규칙으로 발전 가능. 반복되면 builder_system.md에 제안 후보.

### [spec-success-feedback-missing] 스펙이 지정한 성공 연출/메시지를 누락하거나 축소해 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-c` `checkC`/`loadC`)
- 분류 태그: spec-success-feedback-missing
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 C 정답 완료 시 스펙(md Scene 3 항목 5)은 "모니터 화면이 밝아지며 [시스템 재부팅 완료!] 메시지 출력"인데, 구현은 mon-status 한 줄 텍스트만 `q.done`으로 바꾸고 문제를 그대로 둔 채 넘어감. 또 진행중 표시(재부팅 중 `…`)가 정적이라 진행감이 없음.
- 조치: `checkC`를 "화면(`.mon-screen.rebooted` glow)이 밝아지며 문제/트레이를 지우고 `✅ 시스템 재부팅 완료!` 메시지만 2초 출력 후 다음 문제"로 변경. 마지막 문제는 `nextC`에서 중복 메시지 제거하고 곧장 수리 아웃트로로. 상태문구 끝 점을 `. / .. / ...` 반복(`startMonLoading`/`stopMonLoading` + `.mon-status .dots` 고정폭)으로 진행중 연출 추가.
- 규칙화 메모: 아직 1회. 반복되면 "스토리보드가 정답/성공 시 화면 상태 변화(밝아짐·메시지·문제 제거 등)를 명시하면 텍스트 한 줄 치환으로 축소하지 말고 명시된 연출을 그대로 구현" 규칙을 builder_system.md에 제안 후보. (`[spec-fx-color-mismatch]`와 같은 '스펙 연출 임의 축소/변경' 계열)
