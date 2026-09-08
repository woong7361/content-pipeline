# Character Asset QA

## Accepted

- `output/assets/child_idle.webp`: 같은 기준 인물, 양갈래·남색 리본·분홍 가디건·노란 단추·남색 치마·흰 양말·남색 운동화가 명세와 일치한다. 정면 중립 대기 자세, 전신 여백, 실제 알파 투명 배경을 확인했다.
- `output/assets/child_speaking.webp`: idle과 얼굴·헤어·의상·팔레트·비율·조명이 일치한다. 화면 오른쪽을 보는 시선과 한 손을 든 말하기 동작, 전신 여백, 실제 알파 투명 배경을 확인했다.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|

## Integration Notes

- 두 PNG는 모두 1024×1536 `Format32bppArgb`이며 모서리 알파 값이 0이다.
- 말하기 포즈는 오른쪽 말풍선과 연결되는 시선·손 방향을 유지한다.
- 생성기가 투명 배경을 체크무늬로 굽는 문제를 보여, 이미지 생성본의 캐릭터 형태는 유지하고 연결된 중성 체크무늬 픽셀만 알파로 후처리했다.
