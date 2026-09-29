# 명세·추적·DAG 캐시 구조

## 단일 명세

`spec/lesson-spec.json`은 인터뷰가 끝난 뒤 생성되며 이후 비주얼 설계와 개발의 단일 진실 공급원이다.

- `requirements`: 원본 요구사항과 출처, 구현 대상, 검증 방식
- `scenes`: 안정적인 `SCN-*` ID를 가진 장면
- `questions`: 안정적인 `Q-*` ID를 가진 문항
- `assets`: 안정적인 `AST-*` ID와 실제 경로
- `decisions`: 인터뷰 결정과 미확정 상태

스키마는 `schemas/lesson_spec.schema.json`이다. 열린 결정, 끊어진 요구사항 ID, 존재하지 않는 장면·문항·자산 연결은 다음 단계로 넘어가기 전에 거부한다.

## 요구사항 추적과 테스트

개발 산출물이 생기면 `verify_spec.py`가 다음 파일을 만든다.

```text
tests/functional-test-plan.json
tests/spec-verification.json
```

장면마다 도달 가능성 테스트, 문항마다 정답·재시도 테스트를 생성한다. 정적 검증기는 명세의 장면·문항 ID와 문구, 자산 경로가 `lesson.json`에 보존됐는지 확인하며, 테스트가 없는 `static`·`functional` 요구사항을 거부한다.

독립 실행:

```powershell
python -B ./verify_spec.py runs/<run-id>
```

## DAG

DAG는 Directed Acyclic Graph, 즉 방향이 있고 순환하지 않는 의존 관계 그래프다. 단순한 작업 목록과 달리 무엇이 무엇을 기다리는지를 표현한다.

```text
senior_planner
├─ senior_designer
│  └─ interview_brief
│     └─ lesson_spec
│        └─ visual_design
│           ├─ senior_developer
│           └─ asset_render
```

`senior_developer`와 `asset_render`는 서로를 기다리지 않고 둘 다 `visual_design`만 의존한다. 따라서 동시에 실행할 수 있다.

그래프 확인:

```powershell
python -B ./produce_lesson.py runs/<run-id> --check-only --explain-dag
```

## 캐시

캐시는 각 단계의 입력 파일, 상위 단계 출력, 프롬프트, 모델, 인터뷰 답변을 SHA-256으로 요약해 `runs/<run-id>/.pipeline/cache.json`에 저장한다.

- fingerprint가 같고 출력 파일이 있으면 단계를 건너뛴다.
- 상위 단계 출력이 달라지면 하위 단계 fingerprint도 달라진다.
- 특정 단계부터 다시 만들고 싶으면 그 단계와 모든 하위 캐시만 무효화한다.

```powershell
python -B ./produce_lesson.py runs/<run-id> --invalidate lesson_spec
python -B ./produce_lesson.py runs/<run-id> --no-cache
```

첫 명령은 `lesson_spec`, `visual_design`, `senior_developer`, `asset_render`만 다시 실행 대상으로 만든다. 두 번째 명령은 선택한 전체 범위에서 캐시를 사용하지 않는다.
