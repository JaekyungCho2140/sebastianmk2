# Sebastian - Claude Code 작업 프로토콜

**버전**: 1.0.0
**작성일**: 2025-12-19
**목적**: Claude Code와 효과적으로 협업하기 위한 작업 규칙

---

## 🎯 핵심 원칙

### 1. 명확한 지시

**❌ 추상적 지시 (실패)**:
```
"M4/GL 병합 기능 구현해줘"
```
→ Claude가 해석하여 재구현 → 레거시와 다른 결과

**✅ 구체적 지시 (성공)**:
```
"legacy/M4/Merged_M4.py의 74-266행을 sebastian/core/m4gl/dialogue.py로
복사하고, 함수명을 merge_dialogue()로 변경해줘.
progress_queue 인자를 추가하고 나머지는 변경하지 마."
```
→ Claude가 정확히 복사 → 레거시와 동일한 결과

### 2. 단계별 진행

**한 번에 하나의 Task만 지시**:
```
1. Phase 1 완료 → 검증
2. Phase 2 완료 → 검증
3. Phase 3 완료 → 검증
```

**❌ 잘못된 방식**:
```
"Phase 1, 2, 3 전부 구현해줘"
```

### 3. 검증 필수

**각 Task 완료 후 즉시 검증**:
```
Task 완료 → diff 확인 → 다음 Task
```

**❌ 검증 없이 진행**:
```
Task 1 → Task 2 → Task 3 → 마지막에 검증 (❌ 에러 발견 시 되돌리기 어려움)
```

### 4. 변경 금지 항목 명시

**"변경하지 마" 명시 필요**:
```
"다음 항목은 절대 변경하지 마:
- language_mapping 딕셔너리 (컬럼 인덱스)
- NPC 매핑 로직 (iloc[:, 7], iloc[:, 9])
- 서식 지정 (Font, PatternFill, Border 색상 코드)"
```

---

## 📝 작업 지시 템플릿

### Template 1: 파일 복사

```
"[소스 파일 경로]:[시작행]-[종료행]을
[타겟 파일 경로]로 복사해줘.

다음 변경사항만 적용:
1. [변경 항목 1]
2. [변경 항목 2]

나머지는 한 줄도 변경하지 마.

특히 다음 항목은 절대 변경 금지:
- [보존 항목 1]
- [보존 항목 2]"
```

**예시**:
```
"legacy/M4/Merged_M4.py:74-266을
sebastian/core/m4gl/dialogue.py로 복사해줘.

다음 변경사항만 적용:
1. 함수명: run_merge() → merge_dialogue()
2. 인자: progress_queue 추가

나머지는 한 줄도 변경하지 마.

특히 다음 항목은 절대 변경 금지:
- read_excel_file() 호출 파라미터
- language_mapping 딕셔너리
- NPC 매핑 로직"
```

### Template 2: UI 구현

```
"[UI 파일 경로]를 작성해줘.
wireframe의 '[섹션명]' 섹션을 참조하세요.

요구사항:
1. [요구사항 1]
2. [요구사항 2]
...

스타일:
- [스타일 속성 1]
- [스타일 속성 2]"
```

**예시**:
```
"sebastian/ui/m4gl_tab.py를 작성해줘.
wireframe의 'M4/GL 탭' 섹션을 참조하세요.

요구사항:
1. QWidget 상속
2. 2개 버튼 (DIALOGUE, STRING)
3. 폴더 선택 필드
4. 실행 버튼

스타일:
- DIALOGUE 배경: linear-gradient(135deg, #E8F5E9, #C8E6C9)
- STRING 배경: linear-gradient(135deg, #E3F2FD, #BBDEFB)"
```

### Template 3: 검증

```
"[검증 대상]을(를) 검증해줘.

방법:
1. [검증 방법 1]
2. [검증 방법 2]

예상 결과:
- [예상 결과 1]
- [예상 결과 2]"
```

**예시**:
```
"sebastian/core/m4gl/dialogue.py와 legacy/M4/Merged_M4.py를 diff로 비교해줘.

예상 결과:
- 함수명 변경: run_merge → merge_dialogue
- 인자 추가: progress_queue
- 나머지: 변경 없음"
```

---

## 🔄 작업 흐름

### Phase 1: 로직 추출

```
1. "sebastian/core/m4gl/ 디렉터리 생성"
   ↓
2. "legacy/M4/Merged_M4.py:74-266을 sebastian/core/m4gl/dialogue.py로 복사"
   ↓
3. "함수명을 merge_dialogue()로 변경"
   ↓
4. "diff로 변경사항 확인"
   ↓
5. "수동 검증: language_mapping 확인"
   ↓
6. 다음 Task
```

### Phase 2: UI 개발

```
1. "sebastian/ui/common/progress_dialog.py 작성 (wireframe 참조)"
   ↓
2. "ProgressDialog 테스트 코드 실행"
   ↓
3. "sebastian/ui/main_window.py 작성"
   ↓
4. "메인 창 실행 및 확인"
   ↓
5. 다음 Task
```

### Phase 3: 통합

```
1. "sebastian/workers/m4gl_worker.py 작성"
   ↓
2. "sebastian/ui/m4gl_tab.py에 Worker 연결"
   ↓
3. "실제 데이터로 테스트 실행"
   ↓
4. "출력 파일 비교 (레거시 vs 신규)"
   ↓
5. 100% 일치 확인
```

---

## ✅ 검증 체크리스트

### 로직 추출 검증

**각 함수 복사 후**:
- [ ] diff 실행: 함수명, 인자 외 변경 없음
- [ ] 수동 확인: 파일 읽기 파라미터
- [ ] 수동 확인: 컬럼 매핑 딕셔너리
- [ ] 수동 확인: 서식 지정 코드
- [ ] 임포트 테스트: from core.m4gl import merge_dialogue

### UI 개발 검증

**각 UI 컴포넌트 작성 후**:
- [ ] wireframe 디자인 100% 준수
- [ ] 색상 코드 정확히 일치
- [ ] 폰트, 크기, 간격 일치
- [ ] 실행 테스트: UI 표시 확인

### 통합 검증

**각 기능 연결 후**:
- [ ] Worker 정상 실행
- [ ] ProgressDialog 업데이트
- [ ] 출력 파일 생성
- [ ] 레거시와 100% 일치

---

## 🚨 주의사항

### 절대 하지 말 것

1. **❌ 로직 재작성**: "더 나은 방법" 제안 금지
2. **❌ 최적화**: "성능 개선" 시도 금지
3. **❌ 리팩토링**: "코드 정리" 금지
4. **❌ 추측**: 불확실한 부분은 질문 필수
5. **❌ 일괄 작업**: 한 번에 여러 Task 수행 금지

### 허용되는 작업

1. **✅ 정확한 복사**: 지시된 범위만 복사
2. **✅ 최소 변경**: 명시된 변경사항만 적용
3. **✅ 검증**: 각 단계마다 검증
4. **✅ 질문**: 불명확한 부분은 즉시 질문
5. **✅ 리포트**: 작업 결과 상세히 보고

---

## 💬 질문 유형

### 질문 1: 불명확한 지시

**상황**: 지시사항이 모호하거나 불명확
**질문 예시**:
```
"함수명 변경 시 타입 힌트도 추가해야 할까요?
지시사항에는 명시되지 않았습니다."
```

### 질문 2: 예상치 못한 상황

**상황**: 레거시 코드 구조가 예상과 다름
**질문 예시**:
```
"legacy/M4/Merged_M4.py:74-266에는 run_merge() 함수가 없고
run_merge_dialogue() 함수가 있습니다.
이 함수를 복사해야 할까요?"
```

### 질문 3: 검증 실패

**상황**: 검증 결과가 예상과 다름
**질문 예시**:
```
"diff 결과, 함수명과 인자 외에도 import 구문이 변경되었습니다.
이것이 의도된 것인가요?"
```

---

## 📊 작업 진행 리포트 형식

### 각 Task 완료 시 보고

```markdown
## Task 완료 리포트

**Task**: [Task 이름]
**완료 시간**: [날짜/시간]

### 수행 작업
1. [작업 1]
2. [작업 2]
...

### 변경 사항
- [변경 사항 1]
- [변경 사항 2]

### 검증 결과
- [x] diff 확인: 예상대로 변경됨
- [x] 수동 확인: language_mapping 보존됨
- [ ] 임포트 테스트: 실패 (원인: ...)

### 다음 단계
[다음 Task 이름]
```

---

## 🐛 트러블슈팅 프로토콜

### 문제 발생 시

1. **즉시 중단**: 다음 Task 진행하지 않음
2. **현상 보고**: 에러 메시지, 예상 vs 실제
3. **원인 분석**: 가능한 원인 제시
4. **해결 방안 제안**: 2-3가지 옵션
5. **사용자 결정 대기**: 임의 수정 금지

### 보고 예시

```markdown
## 문제 발생

**Task**: sebastian/core/m4gl/dialogue.py 복사

**에러**:
```
ModuleNotFoundError: No module named 'progress_window'
```

**원인 분석**:
레거시 코드가 progress_window 모듈을 임포트하는데,
신규 코드에는 이 모듈이 없습니다.

**해결 방안**:
1. progress_window import 제거 (권장)
2. progress_window 모듈도 함께 복사
3. mock 객체로 대체

**권장**: 옵션 1 (progress_queue로 대체)
```

---

## 📅 작업 스케줄 관리

### 일일 작업 계획

```markdown
## 2025-12-19 작업 계획

### 오전 (Phase 1)
- [x] LY/GL 로직 복사 (2시간)
- [x] 검증 (30분)

### 오후 (Phase 1)
- [ ] M4GL DIALOGUE 로직 추출 (2시간)
- [ ] 검증 (30분)
- [ ] M4GL STRING 로직 추출 (2시간)

### 진행 상황
- Phase 1: 40% 완료
- 예상 완료: 2025-12-20
```

---

## 📚 참고 문서 활용

### 작업 시 참조 순서

1. **Phase 가이드**: 현재 Phase의 상세 가이드
2. **wireframe**: UI 작업 시 필수
3. **레거시 코드**: 로직 추출 시 원본 확인
4. **Migration Guide**: 전체 맥락 파악

### 문서 간 연결

```
Migration Guide (전체)
  ↓
Phase 1 Guide (현재 작업)
  ↓
Claude Code 지시 (구체적 작업)
  ↓
검증 (결과 확인)
```

---

## ✨ 모범 사례

### 예시 1: 성공적인 로직 추출

```
사용자: "legacy/M4/Merged_M4.py:74-266을 sebastian/core/m4gl/dialogue.py로
        복사하고, 함수명을 merge_dialogue()로 변경해줘.
        progress_queue 인자를 추가하고 나머지는 변경하지 마."

Claude:
  1. 파일 읽기
  2. 74-266행 복사
  3. 함수명 변경
  4. 인자 추가
  5. diff 실행

  "✅ 복사 완료. diff 결과:
  - 함수명: run_merge → merge_dialogue
  - 인자: progress_queue 추가
  - 나머지: 변경 없음

  다음 단계를 진행하시겠습니까?"

사용자: "좋아, 다음은 STRING 로직도 동일하게 복사해줘."
```

### 예시 2: 검증 실패 시 대처

```
Claude: "diff 결과, 예상과 다른 변경사항이 발견되었습니다:
        - import 구문 추가: from typing import Queue

        이것이 의도된 것인가요?
        아니면 제거해야 할까요?"

사용자: "타입 힌트는 추가해도 돼. 계속 진행해."

Claude: "✅ 확인했습니다. 계속 진행하겠습니다."
```

---

## 🎓 학습 및 개선

### 작업 후 회고

**각 Phase 완료 후**:
```markdown
## Phase 1 회고

### 잘된 점
- LY/GL은 이미 분리되어 있어 빠르게 완료
- diff 검증으로 변경사항 조기 발견

### 어려웠던 점
- M4GL matching_columns 딕셔너리 복잡도
- NC/GL ProcessPoolExecutor 이해

### 개선 사항
- 다음 Phase부터는 더 세밀한 단계 분할
- 검증 자동화 스크립트 작성

### 다음 Phase 전략
- UI 작업은 wireframe 철저히 참조
- 공통 컴포넌트 먼저 완성
```

---

이 프로토콜을 따르면 Claude Code와의 협업이 훨씬 효율적이고 정확해집니다.
각 Phase 가이드를 참조하면서 단계별로 진행하시면 됩니다.
