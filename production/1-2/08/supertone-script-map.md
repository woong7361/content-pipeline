# 1-2/08 음성 스크립트 (Supertone Play 임포트용)

`supertone-script.txt`를 Supertone Play의 **프로젝트 → 스크립트 가져오기**로 넣으면 한 줄이 한 블록이 된다.
아래 표는 그 순서 그대로이며, 내보낸 오디오를 `assets/audio/script/<키>.mp3`로 저장하면 `index.html` 수정 없이 교체된다.

**배역이 4종이다.** 한 파일을 통째로 넣으면 전부 같은 보이스가 되므로, 배역별로 나눈 `supertone-script/`를 쓴다 — 아래 [배역별 파일](#배역별-파일) 참고.

- 기준: `index.html` (2026-08-04 현재 상태). 원문 `…723 음성 스크립트.md`가 아니라 **실제 화면에 붙어 있는 대사**를 옮겼다.
- **효과음(SFX)은 제외**했다. `…723 효과음 스크립트.md` / `assets/audio/sfx/` 및 완료 화면 `3차시 수리 완료!`(효과음 처리)는 이 파일에 없다.
- TTS가 읽지 못하는 `● ■ ▲` 기호는 `동그라미 / 네모 / 세모`로 풀어 썼다. 화면 텍스트는 기호 그대로다.
- 문제 대사에서 화면에만 있는 제목줄(`덧셈과 뺄셈`)과 식(`7 + 3 = (   )`)은 읽는 대상이 아니라서 뺐다.

| # | 키 (파일명) | 씬 | 화자 | 대사 |
| --- | --- | --- | --- | --- |
| 1 | `intro-1-apology` | 도입 | 작업자 | 공사 중에 실수로 담장을 무너뜨렸어요. 죄송합니다! |
| 2 | `intro-2-wall-fixed` | 도입 | 작업자 | 휴, 담장은 다 고쳤어요. |
| 3 | `intro-3-need-help` | 도입 | 작업자 | 그런데, 벽화는 못 그리겠어요. 누가 도와줘요! |
| 4 | `intro-4-volunteer` | 도입 | 주인공 | 저희가 도와드릴게요! |
| 5 | `shape-open-1-how-to-draw` | 모양 찾기 | 주인공 | 벽화를 어떻게 그려야 되지? |
| 6 | `shape-open-2-various-shapes` | 모양 찾기 | 교사 | 여러 가지 모양으로 그리면 좋겠어요. |
| 7 | `shape-open-3-find-together` | 모양 찾기 | 교사 | 저와 학교에서 모양을 찾아 보아요. |
| 8 | `shape-open-4-yes` | 모양 찾기 | 주인공 | 네! |
| 9 | `search-square` | 모양 찾기 | 내레이션 | 네모 모양 2개를 찾아 봅시다. |
| 10 | `search-tutorial-square` | 모양 찾기 | 내레이션 | 네모 모양을 클릭해보세요. |
| 11 | `search-circle` | 모양 찾기 | 내레이션 | 동그라미 모양 2개를 찾아 봅시다. |
| 12 | `search-triangle` | 모양 찾기 | 내레이션 | 세모 모양 2개를 찾아 봅시다. |
| 13 | `correct-1` | 공통 | 내레이션 | 정답입니다. |
| 14 | `praise-well-found` | 모양 찾기 | 교사 | 잘 찾았어요! |
| 15 | `paint-color-shape` | 모양 찾기 | 교사 | 페인트 색깔마다 모양이 달라요. |
| 16 | `paint-shape-circle` | 모양 찾기 | 교사 | 동그라미 모양 |
| 17 | `paint-shape-square` | 모양 찾기 | 교사 | 네모 모양 |
| 18 | `paint-shape-triangle` | 모양 찾기 | 교사 | 세모 모양 |
| 19 | `count-circle` | 모양 세기 | 내레이션 | 동그라미 모양은 몇 개인가요? |
| 20 | `count-triangle` | 모양 세기 | 내레이션 | 세모 모양은 몇 개인가요? |
| 21 | `count-square` | 모양 세기 | 내레이션 | 네모 모양은 몇 개인가요? |
| 22 | `shape-outro-1-praise` | 모양 찾기 | 교사 | 잘했어요. 이제 벽화를 색칠해봐요! |
| 23 | `shape-outro-2-request` | 모양 찾기 | 교사 | 페인트 소개를 부탁해요! |
| 24 | `arith-intro-1-we-will` | 산술 튜토리얼 | 주인공 | 페인트 소개는 저희가 할게요. |
| 25 | `arith-intro-2-this-is-paint` | 산술 튜토리얼 | 주인공 | 이것을 페인트라고 해요. 초록색부터 알려드릴게요. |
| 26 | `arith-intro-3-ten-per-can` | 산술 튜토리얼 | 주인공 | 1통에 모양을 10개씩 그릴 수 있어요! |
| 27 | `arith-q-total-ten` | 산술 튜토리얼 | 내레이션 | 모양은 모두 몇 개인가요? |
| 28 | `arith-q-add-7-3` | 산술 튜토리얼 | 내레이션 | 7개에서 3개를 더 색칠하면 몇 개일까요? |
| 29 | `arith-beat-can-empty` | 산술 튜토리얼 | 주인공 | 페인트 1통을 다 썼어요. |
| 30 | `arith-beat-can-ready` | 산술 튜토리얼 | 작업자 | 1통을 더 준비했어요. |
| 31 | `arith-beat-paint-2-more` | 산술 튜토리얼 | 작업자 | 2개를 더 색칠해주세요. |
| 32 | `arith-beat-yes` | 산술 튜토리얼 | 주인공 | 네. |
| 33 | `correct-2` | 산술 튜토리얼 | 내레이션 | 정답입니다. |
| 34 | `arith-beat-thanks` | 산술 튜토리얼 | 작업자 | 고마워요! 다른 담장으로 가요. |
| 35 | `arith-beat-yes-2` | 산술 튜토리얼 | 주인공 | 네! |
| 36 | `arith-beat-erase-2` | 산술 튜토리얼 | 작업자 | 잘못 그린 2개를 지워주세요! |
| 37 | `arith-q-subtract-12-2` | 산술 튜토리얼 | 내레이션 | 모양 12개에서 2개를 지우면 몇 개일까요? |
| 38 | `arith-beat-erase-3-more` | 산술 튜토리얼 | 작업자 | 3개를 더 지우고 싶어요. 지워주세요. |
| 39 | `arith-q-subtract-10-3` | 산술 튜토리얼 | 내레이션 | 모양 10개에서 3개를 더 지우면 몇 개일까요? |
| 40 | `correct-3` | 산술 튜토리얼 | 내레이션 | 정답입니다. |
| 41 | `arith-outro-1-well-done` | 산술 튜토리얼 | 작업자 | 잘했어요! |
| 42 | `arith-outro-2-more-walls` | 산술 튜토리얼 | 작업자 | 더 많은 담장을 색칠해야해요! |
| 43 | `arith-outro-3-yes` | 산술 튜토리얼 | 주인공 | 네! |
| 44 | `random-a-find-ten` | 무작위 문제 | 내레이션 | 10이 되는 덧셈식을 찾아 보세요. |
| 45 | `random-b-subtract-from-ten` | 무작위 문제 | 내레이션 | 10에서 빼어 보세요. |
| 46 | `random-c-add-three` | 무작위 문제 | 내레이션 | 세 수의 덧셈을 해 보세요. |
| 47 | `random-d-subtract-three` | 무작위 문제 | 내레이션 | 세 수의 뺄셈을 해 보세요. |
| 48 | `drawing-1-almost-done` | 자유 그리기 | 교사 | 담장 색칠이 끝나가요! |
| 49 | `drawing-2-free-draw` | 자유 그리기 | 교사 | 마지막 담장은 자유롭게 그려주세요. |
| 50 | `drawing-3-finished-question` | 자유 그리기 | 내레이션 | 그림을 완성했나요? |
| 51 | `story-intro-seen-shapes` | 수리 이야기 | 내레이션 | 모양을 길에서 본 적이 있나요? |
| 52 | `story-what-sign` | 수리 이야기 | 내레이션 | 무슨 표지판일까요? |
| 53 | `story-circle-question` | 수리 이야기 | 내레이션 | 동그라미 모양 표지판은 어떤 것이 있을까요? |
| 54 | `story-circle-answer` | 수리 이야기 | 내레이션 | 자동차 전용 도로 표지판입니다. 자동차만 다닐 수 있으니, 사람은 다니지 않아요. |
| 55 | `story-square-question` | 수리 이야기 | 내레이션 | 네모 모양 표지판은 어떤 것이 있을까요? |
| 56 | `story-square-answer` | 수리 이야기 | 내레이션 | 주차 표지판입니다. 자동차가 많으니 주차장에서 놀지 않아요. 안전히 인도로 다녀야 해요. |
| 57 | `story-triangle-question` | 수리 이야기 | 내레이션 | 세모 모양 표지판은 어떤 것이 있을까요? |
| 58 | `story-triangle-answer` | 수리 이야기 | 내레이션 | 공사 표지판입니다. 주변에 공사를 하고 있으니 가까이 가지 않아야 해요. |
| 59 | `story-outro-safe` | 수리 이야기 | 내레이션 | 앞으로 표지판을 보며 안전하게 다녀요. |

## 배역별 파일

`supertone-script/`에 배역별로 나눠 뒀다. **프로젝트를 4개 만들거나 한 프로젝트에서 파일을 하나씩 임포트하면서 보이스를 바꿔 지정**하면 된다. 각 파일 안의 줄 순서 = 아래 키 순서다.

| 파일 | 배역 | 줄 수 | 키 순서 |
| --- | --- | --- | --- |
| `01-worker.txt` | 공사 작업자 (성인 남성) | 10 | `intro-1-apology` · `intro-2-wall-fixed` · `intro-3-need-help` · `arith-beat-can-ready` · `arith-beat-paint-2-more` · `arith-beat-thanks` · `arith-beat-erase-2` · `arith-beat-erase-3-more` · `arith-outro-1-well-done` · `arith-outro-2-more-walls` |
| `02-child.txt` | 주인공 어린이 | 10 | `intro-4-volunteer` · `shape-open-1-how-to-draw` · `shape-open-4-yes` · `arith-intro-1-we-will` · `arith-intro-2-this-is-paint` · `arith-intro-3-ten-per-can` · `arith-beat-can-empty` · `arith-beat-yes` · `arith-beat-yes-2` · `arith-outro-3-yes` |
| `03-teacher.txt` | 여 교사 | 11 | `shape-open-2-various-shapes` · `shape-open-3-find-together` · `praise-well-found` · `paint-color-shape` · `paint-shape-circle` · `paint-shape-square` · `paint-shape-triangle` · `shape-outro-1-praise` · `shape-outro-2-request` · `drawing-1-almost-done` · `drawing-2-free-draw` |
| `04-narration.txt` | 내레이션 | 28 | `search-square` · `search-tutorial-square` · `search-circle` · `search-triangle` · `correct-1` · `count-circle` · `count-triangle` · `count-square` · `arith-q-total-ten` · `arith-q-add-7-3` · `correct-2` · `arith-q-subtract-12-2` · `arith-q-subtract-10-3` · `correct-3` · `random-a-find-ten` · `random-b-subtract-from-ten` · `random-c-add-three` · `random-d-subtract-three` · `drawing-3-finished-question` · `story-intro-seen-shapes` · `story-what-sign` · `story-circle-question` · `story-circle-answer` · `story-square-question` · `story-square-answer` · `story-triangle-question` · `story-triangle-answer` · `story-outro-safe` |

`supertone-script/00-with-speaker-labels.txt`는 `배역: 대사` 형태로 접두어를 붙인 전체본이다. **Play가 이 형식을 화자로 파싱할 때만** 쓴다 — 파싱하지 못하면 "작업자 콜론"까지 그대로 읽으므로, 한 줄 넣어 보고 접두어가 사라지는지 확인한 뒤에 쓴다.

주인공 어린이의 `네!`(3본: `shape-open-4-yes` / `arith-beat-yes-2` / `arith-outro-3-yes`)와 `네.`(`arith-beat-yes`)는 문구가 거의 같다. Play에서 같은 결과가 나오면 한 본만 뽑아 4개로 복사해도 된다.

## 납품 현황

| 배역 | 파일 | 상태 |
| --- | --- | --- |
| 공사 작업자 | `01-worker.txt` (10줄) | **2026-08-04 재녹음 완료.** `assets/add_audio/Take{1~10}` → 같은 키 mp3로 교체(complete.md 97번) |
| 주인공 어린이 | `02-child.txt` (10줄) | **3/10 교체**(2026-08-04, 98번) — `arith-intro-1-we-will` · `-2-this-is-paint` · `-3-ten-per-can`. 나머지 7본은 2026-08-03 녹음 |
| 여 교사 | `03-teacher.txt` (11줄) | 미납. 2026-08-03 녹음이 그대로 |
| 내레이션 | `04-narration.txt` (28줄) | **1/28 교체**(2026-08-04, 98번) — `arith-q-add-7-3`(배역 확인 필요, 98번 주의). 나머지는 2026-08-03 녹음. `search-tutorial-square` 1본은 **아직 파일 자체가 없다** |

## 현재 오디오와 다른 점

- **10번 `search-tutorial-square`는 아직 파일이 없다.** 코드(`SEARCH_TUTORIAL.voice`)가 참조만 하고 `assets/audio/script/`에 실물이 없어 지금은 무음이다. 이번에 반드시 만들어야 하는 한 본이다.
- **9·11·12번(찾기 3문항)**: 기존 녹음은 "네모 모양을 찾아봅시다"로 개수가 없다. 화면 배너는 "2개"를 표시하므로 여기서는 화면 문구에 맞춰 "2개"를 넣었다. 기존 녹음과 맞추려면 "2개를"을 빼고 읽히면 된다.
- **13·33·40번 `정답입니다.`** 는 문구가 같고 파일만 3본으로 나뉜다(재생 위치가 달라 톤을 달리 잡은 자리다). 같은 소리를 써도 되면 1본만 만들어 3개로 복사하면 된다.
- **52번 `story-what-sign`** 은 표지판 카드 3장이 돌려 쓴다(1본).
- `search-prompt.mp3`(옛 "모양을 찾아 봅시다")는 현재 코드에서 **참조가 0**이라 뺐다.
- 현재 파일은 `assets/audio/script/*.mp3` 59본이다. 위 표의 59줄과 개수는 같지만 구성이 다르다 — 표에는 `search-tutorial-square`가 들어가고 `search-prompt`가 빠졌다.
