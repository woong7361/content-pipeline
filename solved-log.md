# solved-log.md

`problem.md`에서 `규칙화됨`이 된 항목의 **문제 + 해결 전문**을 옮겨 보존하는 지식 로그다.
운영 규칙은 `problem.md` 상단 "사용 규칙 > 규칙화됨 항목 보관과 재발 처리"와 최상단 `AGENTS.md`의 "피드백 → problem.md → rule 루프" 섹션을 따른다.

## 목적

- 규칙화되어 `problem.md`에서 스텁으로 축소된 항목의 상세(어떤 문제였고 어떻게 해결했는가)를 잃지 않는다.
- `problem.md`에는 스텁만 남겨 중복 감지·재발 카운트를 유지하고, 상세 지식은 여기서 참조한다.
- 재발 시 그 재발 사례를 해당 항목 아래에 덧붙여 "rule 있는데도 또 터진" 이력을 남긴다.

## 항목 형식

```markdown
### [분류태그] 한 줄 요약   <!-- problem.md 스텁의 solved-log#앵커가 이 제목을 가리킨다 -->

- 대상: content-harness-pipeline/... (구체 경로 또는 index.html)
- 분류 태그: <problem.md 스텁과 동일>
- 최종 발생 횟수: N
- 규칙화일: YYYY-MM-DD
- 반영한 rule 위치: (AGENTS.md 경로/섹션)
- 사례:
  - YYYY-MM-DD: <지적 내용 요약>
- 조치: <어떻게 해결했는지 전문>
- rule 문구: <실제 승격된 rule 요약>
- 재발 이력:
  - <없으면 "없음". 재발 시 YYYY-MM-DD와 대응 추가>
```

## 로그

<!-- 규칙화된 항목의 전문을 이 아래에 추가한다. -->

### [dialogue-as-speech-bubble] 대사·피드백을 표면 텍스트로 넣고 말풍선을 매번 새로 만듦 (channel 렌더링 계약으로 통합)

- 대상: content-harness-pipeline/prompts/builder_system.md (산출: runs/2026-07-08_ch802d08/output/index.html 전반)
- 분류 태그: dialogue-as-speech-bubble · feedback-as-character-bubble · sequential-scene-choreography **3개 태그를 하나의 규칙으로 통합**
- 최종 발생 횟수: 16 (dialogue 8 + feedback 5 + sequential 3)
- 규칙화일: 2026-07-15
- 반영한 rule 위치: `prompts/builder_system.md`의 "channel 렌더링 계약" 절
- 사례:
  - **dialogue-as-speech-bubble (8회)** — 튜토리얼 대사를 작업대 보드 빈 공간(`.wb-note`)에 끼워 넣음 / 말풍선을 상단 코너에 고정해 캐릭터와 떨어져 "붕 떠 보임" / 유형 A·B·C 안내 대사가 전광판·보드·모니터의 표면 텍스트로 들어감 / 퀴즈 정답 대사가 다른 씬과 **다른 `.bubble` 컴포넌트**로 떠 있음 / 인증서 마무리 대사가 인증서 종이 안 `.cert-caption`에 박힘 / 이야기 대사가 책 지면 `.cap` 캡션에 박힘.
  - **feedback-as-character-bubble (5회)** — 정오답 피드백이 3:1 좁은 `.status-tag`에서 세로로 깨짐 / 스펙이 요구한 중앙 말풍선 팝업 미적용 / 피드백을 전용 도장 이미지로 요청 / 캐릭터 옆 짧은 대사를 모든 문제에 요청했는데 **새 말풍선을 만들어 "기존 것을 재사용하라"고 재지적** / 오답 시 confused pose가 idle로 복귀하지 않아 고민 표정이 고착됨.
  - **sequential-scene-choreography (3회)** — 문제 인트로가 모든 요소를 한 번에 띄우는 단일 장면 / 복구 씬이 두 캐릭터 대사를 하나의 plaque banner에 통째로 담음 / 인증서 씬도 마무리 대사가 캡션으로 박힌 단일 장면.
- 조치(전문):
  - **근본 원인.** planner는 `elements[].channel`로 각 줄의 역할(`dialogue`, `feedback`, ...)을 **이미 태깅하고 있었는데**, builder에는 그 channel을 어떻게 렌더할지에 대한 계약이 없었다. 그래서 builder가 매번 자기 판단으로 표면을 골랐고, 대사가 plaque·board·monitor·인증서·책 지면 등 그때그때 다른 곳에 들어갔다. 말풍선도 계약이 없으니 씬마다 새로 만들어져 `.speech`와 `.bubble`과 `.kid-say`가 혼재했다.
  - **수정.** `builder_system.md`에 "channel 렌더링 계약" 절 신설. `dialogue`는 반드시 기존 speech_bubble asset 재사용 + 화자 머리 옆(head-height) 배치, 표면 텍스트·자막 카드 금지, 한 section에 여러 줄이면 순차 beat 전개. `feedback`은 캐릭터 표정 전환 + 캐릭터 옆 말풍선(dialogue와 같은 에셋) + 중앙 도장의 3층 동시 구현, 오답 pose는 말풍선 종료 시 idle 복귀(취소 가능 타이머).
  - **왜 이 위치인가.** design_review의 creative_direction(제안)이 아니라 builder의 계약(예방)에 넣었다. 검출만 두면 builder가 계속 틀리고 iteration을 낭비한다. 그리고 `channel`이 planner 스키마의 실제 필드이므로 "태깅은 스키마가, 렌더는 계약이" 맡는 반(半)구조적 형태가 된다.
- rule 문구: "`elements[].channel`이 `dialogue`면 기존 speech_bubble 에셋 말풍선으로 화자 머리 옆에 렌더하고 표면 텍스트로 넣지 않는다. 말풍선은 새로 만들지 말고 재사용한다. 여러 줄이면 순차 beat로 전개한다. `feedback`이면 표정 전환 + 캐릭터 말풍선 + 중앙 도장을 함께 구현하고, 오답 pose는 말풍선 종료 시 idle로 되돌린다."
- 검증: **미검증.** 프롬프트 계약이라 builder 산출 HTML을 실제로 확인해야 한다. 2026-07-15 full run(ch8a0715)이 돌긴 했으나 이 계약을 넣기 **전**의 프롬프트로 실행된 것이라 검증에 쓸 수 없다. 검증 방법은 명확하다 — 새 run의 HTML에서 `channel: dialogue` 요소가 speech_bubble asset 위에 렌더됐는지, 씬마다 다른 말풍선 컴포넌트가 섞이지 않았는지 확인한다.
- 한계: 스키마로 강제할 수 없는 프롬프트 규칙이다. 다만 "dialogue 요소가 `.speech` 안에 렌더됐는가"는 사후 검증이 가능하므로, 재발하면 design_review 체크나 코드 검증으로 승격할 여지가 있다.
- 재발 이력:
  - 없음 (2026-07-15 기준).

### [planner-storyboard-detail-loss] 스토리보드 세부(문항·보기·정답·대사·연출)가 하류로 가며 사라짐

- 대상: content-harness-pipeline/prompts/senior_planner_system.md · prompts/interview_brief_system.md · produce_lesson.py(`STAGES[].depends_on`) · stages/planner.py · schemas/planner_output.schema.json
- 분류 태그: planner-storyboard-detail-loss
- 최종 발생 횟수: 5
- 규칙화일: 2026-09-11
- 반영한 rule 위치: `content-harness-pipeline/CLAUDE.md` > "실패에서 배운 것" > "스토리보드 세부는 어느 단계에서도 요약하지 않는다"
- rule 문구: 스토리보드 세부는 어느 단계에서도 요약하지 않는다. 각 단계는 옮긴 항목에 **원본 출처**(쪽·표 번호·예시화면 여부)를 함께 적고, 옮기지 못한 것은 `unmapped`에 사유와 함께 보고한다. 하류 단계는 요약본이 아니라 **원본 문서를 직접 읽을 수 있어야** 한다 — `depends_on`에 원본을 넣는다.
- **손실 지점이 매번 달랐다는 것이 이 항목의 핵심이다.** 한 군데를 막으면 다음은 다른 데서 샌다.

| 회차 | 날짜 | 손실 지점 |
|---|---|---|
| 1 | 2026-07-13 | planner가 문항·보기·정답을 `content_outline` 한 줄로 압축 |
| 2 | 2026-07-31 | planner 산출에서 정답 공란·판정 불가 자연어·asset group 중복 |
| 3 | 2026-08-14 | 기존 검사층은 전부 PASS인데 노출 시점 불일치·출제 규칙 소실 |
| 4 | 2026-09-11 | `content-plan.md` → `production-guide.md` 요약 (개발 단계가 원본을 안 읽는 구조) |
| 5 | 2026-09-11 | PDF → 전사 `.md` (설명 표만 옮기고 **예시화면 그림 속 말풍선**을 버림) |

- 재발 이력:
  - **2026-09-11 (규칙화 당일 재발, 6회차).** 새로 만든 화면 대조 단계(`diff_screens.py`)가 잡았다 — 사람 눈이 아니라 파이프라인이 처음으로 잡은 회차다.
    원문 `storyboard.md:174` 는 "대사가 모두 종료되면 화면 중앙에 **퀘스트 알림창이 크게 팝업**됨 / 알림창 하단에 노란 `[ 수락하기 ]` 버튼 활성화(펄스)" 라고 못박았다.
    전사본에도 그대로 남아 있었으므로 **요약 손실이 아니다.** `senior_developer` 가 그것을 base 원자(말풍선 + `ctaText`)로 **근사**했다 — 원문에 있는 UI 형태를 런타임이 이미 가진 것으로 바꿔치기한 것이다.
    현재 rule 문구("어느 단계에서도 요약하지 않는다")는 **이 축을 안 덮는다.** 요약이 아니라 치환이기 때문이다.
    제안하는 보강: "**원문이 UI 형태를 지정했으면 그 형태로 만든다.** base 원자에 비슷한 것이 있다는 이유로 바꿔치기하지 않는다. 원자로 안 되면 `player-ext` 로 만들고, 그것도 안 되면 `unmapped` 에 올린다." (승인 대기)

---

#### 규칙화 이전 전문 (problem.md 원본)

### [planner-storyboard-detail-loss] planner.json이 storyboard 세부(문제 보기·대사·오디오·모션·효과)를 압축/누락함

- 대상: content-harness-pipeline/stages/planner.py, schemas/planner_output.schema.json, prompts/planner_system.md (산출: runs/2026-07-08_ch802d08/ch802d08_planner.json)
- 분류 태그: planner-storyboard-detail-loss
- 상태: 제안됨 (**5회 도달 — rule 승격 제안, 승인 대기**)
- 발생 횟수: 5
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-09-11
- 사례:
  - 2026-07-13: `2학년_8차시(시간)_임상현.md`(storyboard)와 `ch802d08_planner.json`을 비교하니 차이가 큼. storyboard가 요구한 요소(이미지, 대사, 문제 문구, 보기(distractor), 캐릭터 포즈, 효과, 애니메이션, 오디오/SFX)가 요약되거나 생략됨. 특히 활동2 12문제의 정확한 문제 문구·보기 3개·정답이 planner에서는 content_outline 한 줄로 압축되어 정답만 남고 오답 보기가 사라짐. 사용자가 schema가 너무 정적이거나 prompt 문제로 추정하고, storyboard를 온전히 담을 수정 방향을 요청.
  - 2026-07-31: `runs/2026-07-31_dfbc1027/dfbc1027_planner.json` 검토 후 전체 수정 요청. schema는 PASS하지만 도형 세기 문항 2개의 `answer`가 비어 있고, 도형 찾기 정답 대상이 기계적으로 판정할 수 없는 자연어로만 표현됨. 원문의 `다음 차시 이동`이 완료 섹션에서 누락되고, 무작위 문제 생성 규칙과 고정 예시 문항의 역할이 모호하며, 동일 asset이 두 batch group에 중복되어 runner의 first-consume 로직상 뒤 그룹의 일관성 목적이 무효화됨. 사용자는 전체 보정 후 planner schema 통과를 요구.
  - 2026-08-14: 사용자가 "planner 생성에 오류가 있는 것 같다"며 eval/critique/refine 3-stage와 test 명세 생성은 비용 때문에 못 붙인다는 제약과 함께 대안을 요청. 최신 산출(`runs/2026-08-14_dfbc1027/dfbc1027_planner.json`)을 실측하니 **schema PASS · 참조 무결성 0건 · 파생기 underivable 0건 · 스토리보드 문구 recall 90개 중 89개**로 기존 검사층은 전부 통과하는데, 두 가지가 남아 있었다. ① 캐러셀로 계획된 화면에서 문항 4개가 요소 하나에 `refs=[a,b,c,d] / reveal=scene_enter`로 묶여, 파생된 케이스가 페이지를 넘기지 않고 바로 조작한다(같은 화면의 문구는 `on_page`로 파생되어 **한 화면에 대해 문구와 문항의 노출 시점이 서로 다르게** 파생됨 → 실행 시 가짜 실패 → content_refine이 멀쩡한 HTML을 고치러 감). 같은 스키마로 문항마다 요소를 쪼개 `on_page/0..3`을 준 과거 산출(`2026-08-12_65126dad-v3`)이 있으므로 **표현할 자리가 없어서가 아니라 같은 사실을 두 방식으로 적은 것**이다. ② 무작위 출제 생성 규칙이 계획의 규칙 자리가 아니라 `channel: generation_rule` 요소 5줄(모두 `rendered_text: []`)로만 남고, 문항은 스토리보드의 예시값 4개로 굳음 — **2026-07-31 사례에서 이미 지적된 것과 같은 손실의 재발**.
  - 2026-09-11: `runs/2026-09-10_g3l05-postoffice` (3학년 5차시 우체국). 사용자가 두 가지를 지적했다. ① "Scene2에서 배경이 바뀌면서 셈이와 수리의 위치가 오른쪽에 있어야 하는데 스토리보드 반영이 안 됐다." ② "효과 같은 부분이 다 빠져 있다 — 편지를 클릭하라든지, 화면이 밝아지면서 장면이 전환된다든지."
    **검증 결과 — 손실 지점은 planner가 아니라 `content-plan.md` → `production-guide.md` 핸드오프였다.** 스토리보드 104·152행이 장면별 인물 위치를 못박았고, `senior_planner`는 그것을 `planning/content-plan.md`에 표로 정확히 옮겼다. 그런데 `senior_developer`의 `depends_on`은 `('planning/production-guide.md', 'design/visual-design.md', 'design/asset-plan.md')`뿐이라 **`content-plan.md`를 아예 읽지 않는다.** `interview_brief`가 만든 `production-guide.md`에는 그 표가 없었다. 즉 상류가 제대로 받아적어도 중간 단계가 요약하면서 떨어뜨리면 개발 단계는 존재 자체를 모른다.
    ②도 같은 구조다. 연출 지시가 `steps[].stageDirections[].action`의 **산문**으로만 남았고(`"편지를 클릭하면 화면이 밝아지며 전환"`), 런타임이 읽는 필드(`backgroundRef`·`motion`·`sound`·`layer`·`characterEmotion`)는 비어 있었다. 배포된 차시(`lessons/1-1/04` 등)는 같은 내용을 전부 필드로 들고 있다. **산문은 어떤 게이트도 못 읽고 런타임도 못 읽는다** — schema PASS·lesson_check PASS·빌드 성공을 다 통과한 뒤 사람 눈에만 보였다.
    - 조치(2026-09-11): (a) 14개 intro 컷과 5개 outro 컷에 `characterPosition`을 명시하고 `cast.postmaster.position`을 `left`로 정정 — 화면 실측으로 좌/우 전환 확인. (b) 스토리보드와 대조해 배경 전환 자리를 바로잡았다. Scene 2는 우체국 **앞 골목**(storyboard.md:149)인데 컷9가 이미 **내부 작업대**로 바꾸고 있었고, 정작 내부로 바뀌어야 할 Scene 3(storyboard.md:193)에는 배경 필드가 아예 없어 산문에만 남아 있었다 — 컷9의 잘못된 `backgroundRef`를 빼고 `step-2`에 부여했다. (c) **게이트를 새로 넣었다** — 아래 "규칙화 메모" 참조. (d) 구조 수정: `senior_developer.depends_on`에 `planning/content-plan.md` 추가, `senior_developer_system.md`에 "두 파일이 다르면 `content-plan.md`가 원본" 명시, `interview_brief_system.md`에 "장면별 인물 배치·연출 지시" 절을 만들고 그 표는 요약 금지로 못박음, `lesson_contract.md`에 `characterPosition` 행과 "원문에 이런 말이 나오면 이 필드를 채운다" 대응표 추가.
  - 2026-09-11 (같은 날 2건째): 사용자가 "말풍선이 누락된 게 있다. content-plan.md부터 누락됐다"며 Scene 1의 대사 순서를 제시했다 — `"안녕, 나는 수리!"` → `"나는 셈이야!"` → `"우와, '198X년'이라고 적힌~"` → `"어디 보자... 어?~"`.
    **검증 결과 — 앞의 자기소개 대사 2개는 스토리보드 설명 표에 아예 없다.** 원본 PDF 5쪽의 **예시화면 그림 안 말풍선**에만 있다(수리 좌측 `"안녕, 나는 수리!"` / 셈이 우측 `"나는 셈이야!"`). 설명 표 5번 "대사 및 연출(편지 발견)"은 대사를 셋만 싣는다. 파이프라인 입력으로 쓴 `storyboard.md`(PDF 전사본)도 설명 표만 옮겼기 때문에, `senior_planner`는 그 대사를 **볼 수 있는 경로가 없었다.**
    즉 손실 지점이 또 달랐다. 앞 사례는 `content-plan.md` → `production-guide.md` 핸드오프였고, 이번은 **PDF → 전사 `.md`** 구간이다. 스토리보드에서 대사는 두 곳에 나뉘어 있다 — 설명 표와 예시화면 그림. 표만 읽으면 그림 속 대사가 통째로 사라진다.
    - 조치(2026-09-11): `prompts/senior_planner_system.md`에 "대사는 설명 표에만 있지 않다 — 예시화면 그림 안 말풍선도 대사다. 둘을 합쳐야 전체다. 입력이 전사본이라 그림을 볼 수 없으면 `unmapped`에 보고한다"를 넣었다. Scene 1 대사 2개를 lesson.json에 복원.
- 조치: 2026-07-13 분석 결과를 반영해 현재 schema/prompt에 `sections[].elements`, `questions`, `rendered_text` 구조가 도입됨. 2026-07-31 산출 planner에서 잔존한 의미적 누락을 수정함: 도형별 정답·클릭 target ID·다음 차시 interaction을 명시하고, 무작위 template/예시의 역할을 interaction에 고정하며, asset group 중복과 사용 참조 불일치를 정리함. 공식 planner schema PASS, 중복 ID·누락 참조·빈 정답·group 중복 검사도 PASS.
  2026-08-14: 산출물을 매번 손으로 보정하는 대신 **`planner_refine` stage(LLM 1회)** 를 신설. 앞뒤로 LLM 0회 층을 붙여 critique/eval 역할은 코드가 맡는다 — 앞은 참조 무결성·시점 정합을 확정하는 `stages/scripts/planner_check.py`, 뒤는 화면·문항·문구가 줄면 REJECT하고 원본을 되살리는 회귀 검사(`design_refine`이 HTML을 통째로 다시 써 앞선 수정을 지우던 것과 같은 위험이라 필수). 점수도 게이트도 만들지 않으므로 남은 문제는 고친 결과를 기계 검사에 다시 통과시켜 안다.
- 규칙화 메모(2026-09-11 추가): 4회. 구조 조치는 위 조치 (d)로 반영했다. 문서 규칙만으로는 막히지 않는다 — 읽히지 않는 파일에 적힌 규칙은 없는 규칙이다.
  **게이트 시도와 결과.** 먼저 `action` 산문의 키워드로 빠진 필드를 추론하는 게이트를 만들어 배포 차시에 돌렸더니 **거짓 양성 3건**이 나왔다(오디오 전용 컷의 표정 지시 / 같은 배경 안의 서사적 "장면 전환" / base가 이미 하는 CTA 페이드인). 산문 추론은 0 거짓 양성이 안 되므로 **넣지 않았다.**
  대신 필드 존재 여부만 세었더니 갈리는 신호가 나왔다 — 배포 17개 차시의 컷 **606개 전부**가 `source`와 `layer`를 들고 있고(예외 0건), 우리 차시만 39개 중 0개였다. `timing`·`motion`·`sound`는 차시별 편차가 커서 못 쓴다. `characterPosition`은 배포 어디에도 없다(전부 `cast[].position`으로 처리). 그래서 `check_stage_direction`에 `cut_source`·`cut_layer` 두 검사를 추가했다 — 배포 차시 606컷에서 0건, 우리 차시에서 78건 적발. `source`가 있어야 "스토리보드의 어떤 지시가 통째로 빠졌는가"를 기계적으로 물을 수 있다.
- 규칙화 메모: 3회. 이 항목은 상위 원인(메타)에 가까움 — 하류 [typeB-problem-text-mismatch-spec], [typeA-prompt-text-small-terse], [spec-success-feedback-missing], [type-per-problem-answer-format] 계열이 "builder가 spec대로 안 만든다"로 반복되는데, 실은 planner가 spec을 온전히 안 넘긴 것이 상류 원인. 5회 이상 반복되면 "planner는 storyboard의 문제 문구·보기·정답·대사·전환/성공 메시지를 원문 그대로 보존하고, 자유문자열로 압축하지 말고 typed 슬롯(questions/dialogue/audio/feedback)에 담는다" 규칙을 planner_system.md에 제안 후보.

---

### [character-asset-identity-alpha] 캐릭터 에셋이 포즈마다 다른 인물로 생성됨 (정체성 부분)

- 대상: content-harness-pipeline (planner/design_review/asset_generator 경로 전반), 산출 예: runs/2026-07-08_ch802d08/output/assets/teacher_*.png, kid_librarian_*.png
- 분류 태그: character-asset-identity-alpha
- 최종 발생 횟수: 9 (원 항목 17회 중 정체성 관련 9회. 알파/프린지 8회는 [character-asset-alpha-fringe]로 분리되어 problem.md에 열린 상태로 남음)
- 규칙화일: 2026-07-15
- 반영한 rule 위치: **AGENTS.md 문서 규칙이 아니라 파이프라인 구조로 강제함.** `schemas/planner_output.schema.json`(characters 엔티티 + asset_plan.character_id), `prompts/planner_system.md`, `stages/design_review.py`(compact_planner_context), `runner.py`(apply_asset_regeneration_patch, attach_identity_context), `prompts/design_review_system.md`, `prompts/asset_generator_system.md`, `schemas/asset_generator_output.schema.json`, `schemas/design_review_{model_,}output.schema.json`
- 사례:
  - 2026-07-09: 꼬마 사서가 원래 필요한 캐릭터가 아니라 다른 학생으로 생성됨.
  - 2026-07-09: 꼬마 사서를 기존 에셋과 무관한 새 캐릭터로 설계하도록 요청. 기존 에셋은 실패 사례 참고로만 취급.
  - 2026-07-10: output/assets의 꼬마 사서가 포즈마다 성별이 바뀜 — idle/success/confused는 남자아이, explaining만 여자아이.
  - 2026-07-10: `teacher_happy`/`teacher_pointing`이 `teacher_worried`와 색상·디자인이 달라 같은 인물로 안 보임. worried 기준으로 통일 요청.
  - 2026-07-10: 재생성한 `teacher_happy` 얼굴에 기준보다 강한 홍조.
  - 2026-07-13: `kid_librarian_idle`만 다른 포즈보다 전체 색감이 붉음.
  - 2026-07-13: `teacher_happy`가 다른 teacher 포즈와 통일성이 어색.
  - 2026-07-13: 재생성 시안 얼굴에 얼룩처럼 불균일한 피부 명암.
  - 2026-07-13: 로컬 보정으로 해결 안 돼 새 기준 이미지를 첨부하고 전체 재생성 요청. 이후에도 조건 없이 재생성 재요청.
- 조치(전문):
  - **근본 원인 규명(2026-07-15, 코드 확인).** 원인은 이미지 생성 품질이 아니라 **재생성 경로의 구조**였다.
    - **D1 — 눈 감고 덮어쓰기.** `design_review.py`의 `compact_planner_context()`가 allowlist라 asset의 `style_constraints`를 design_review에 **전달하지 않는데**, `assetRegenerationRequest` 스키마는 `style_constraints`를 required로 **출력하라고** 요구했고, `runner.py`가 그 값으로 원본을 **통째로 대입**했다. 즉 원본을 본 적 없는 stage가 정체성이 살던 유일한 자리를 재작성했다.
    - **D2 — 형제 포즈 제거.** `build_batch_planner_output()`이 재생성 대상만 남기고 asset_plan을 좁혀, `teacher_happy` 하나만 재생성하면 `teacher_worried`/`teacher_pointing` 스펙이 payload에서 사라졌다. `asset_generator_system.md`는 "batch 안의 asset끼리 캐릭터를 강하게 맞춘다"고 지시하지만 **batch에 혼자면 맞출 대상이 없다.**
    - **D3 — 정체성 소유자 부재.** 정체성이 `art_direction.character_rules`(모든 캐릭터를 한 문자열에) + asset마다의 `style_constraints` 자유문자열에 흩어져 있었다. ch802d08 planner를 실제로 열어보니 `style_constraints`가 `"teacher_worried와 동일 캐릭터"`, `"반복 캐릭터 규칙 유지"` 같은 **참조 사슬**이었다 — 그런데 D2가 그 참조 대상을 batch에서 잘라냈다. 맞출 기준이 payload에 없으니 drift는 필연이었다.
  - **수정(구조로 강제).**
    - planner에 `characters[]` 1급 엔티티 신설 — `identity`(face/hair/outfit/palette/proportions/distinctive_features) + `reference_asset_id`(기준 포즈 = source of truth). `asset_plan`에 `character_id` 참조 추가. `style_constraints`는 그 컷의 포즈·표정·소품·시선만 담도록 축소하고, `art_direction.character_rules`는 공통 그리기 규칙만 담도록 축소.
    - `compact_planner_context`에 `characters`·`character_id`·`style_constraints`·`composition_notes`·`negative_prompt` 전달 추가(D1 차단). 겸사겸사 죽어 있던 필드 수정: `interaction_summary`(planner에 없는 키 → 항상 "")→`interactions`, `section.interaction`(항상 None)→`interaction_ids`, `notes`(스키마에 없음)→`alt_text`+`status`.
    - `apply_asset_regeneration_patch()` 도입 — wholesale 대입 → **patch merge**. 빈 문자열/빈 배열 = "원본 유지". `character_id`는 patch 대상에서 제외해 캐릭터 소속 변조 자체를 불가능하게 함(D1 차단).
    - `attach_identity_context()` 도입 — asset_plan을 좁히기 **전에** 캐릭터 identity + 형제 포즈 + 기준 포즈 이미지 경로를 붙여, `build_batch_planner_output`의 `.copy()`로 배치까지 전파. **`asset_plan`에는 넣지 않아** 형제가 재생성되지 않게 함(D2 차단).
    - `asset_generator_output`에 `character_id` 기록(정체성 추적).
    - 스키마/프롬프트 모순 해소: `assetRegenerationRequest`의 `minLength:1`이 빈 문자열 patch 정책을 금지하고 있어 제거. `design_review_output`의 `newAssetRequest`에 `character_id`가 없어 `additionalProperties:false`로 최종 출력이 REJECT 날 상태였던 것을 model 스키마와 거울로 맞춤. `reason`/`impact` 등 근거 필드는 `minLength:1` 유지해 근거 없는 재생성 요청은 계속 차단.
  - **검증.** codex `--output-schema` 3개(planner/asset_generator/design_review_model) 전부 수락, 산출물도 스키마 통과. 실제 스토리보드로 planner-only run 실행(`runs/2026-07-15_ch802d14`, PASS, 196s) → 캐릭터 2명·포즈 7개가 나왔고 **7개 전부 `style_constraints`에 정체성 재서술 0건**(포즈·표정·시선만). 단일 포즈 재생성 시뮬레이션에서 batch에 asset 1개만 남아도 identity + 기준 포즈 + 형제 목록이 따라오는 것 확인.
  - **full run 검증(2026-07-15).** 위에 "codex에 이미지 생성 도구가 없어 전체 run 불가"라고 적었던 것은 **틀린 판단이었다**(MCP 목록만 보고 problem.md의 7/10 기록을 검증 없이 믿음 — 실제로는 이미지 생성이 정상 동작). ch8_input.json으로 full run 2회 실행 결과:
    - **정체성은 run 안에서 완벽히 유지됐다.** 두 캐릭터 × 3포즈가 모두 같은 인물이고 identity 명세와 일치.
    - **그러나 이 수정의 타깃 시나리오는 발생하지 않았다.** design_review의 재생성 요청 13건이 전부 소품·표면이라 캐릭터가 하나도 재생성되지 않았고, 각 캐릭터의 포즈가 한 batch에 묶여 생성돼 기존 "batch 안에서 맞춘다" 방식만으로도 성립하는 상황이었다. **즉 D1/D2가 막는 상황이 안 왔으므로 이 수정의 효과는 여전히 미검증이다.**
    - 검증에 필요한 조건: design_review가 **캐릭터 asset**의 재생성을 요청하고, 그 포즈가 형제와 분리된 batch로 가는 경우. 재현하려면 캐릭터 하나를 의도적으로 `--asset-generator-missing-only`로 단독 재생성해 보는 것이 가장 빠르다.
- rule 문구: "캐릭터 정체성은 planner의 `characters`가 단일 소유자다. asset은 `character_id`로 참조만 하고 정체성을 재서술하지 않는다. 정체성 판단이 갈리면 `reference_asset_id`의 기준 포즈가 source of truth다. 재생성 요청은 덮어쓰기가 아니라 patch이며(빈 값 = 원본 유지), 원본을 보지 못한 stage는 그 필드를 재작성하지 않는다. 포즈를 하나만 재생성하더라도 identity와 기준 포즈가 batch까지 따라간다." — 문서 규칙이 아니라 schema/runner/prompt로 강제됨.
- 재발 이력:
  - 없음 (2026-07-15 기준). 재발 시 problem.md 스텁의 횟수를 +1 하고 여기에 사례를 덧붙인다.
