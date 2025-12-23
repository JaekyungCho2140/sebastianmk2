# Sebastian Migration Guide

**버전**: 1.0.0
**작성일**: 2025-12-19
**목적**: 레거시 도구를 Sebastian 통합 프로그램으로 안전하게 마이그레이션

---

## 📚 문서 구조

이 마이그레이션 가이드는 다음 문서들로 구성됩니다:

| 문서 | 역할 | 대상 |
|------|------|------|
| **Migration Guide** (이 문서) | 전체 프로세스 조율 | PM, 개발자 |
| **Phase 1: Logic Extraction** | 레거시 로직 추출 가이드 | 개발자, Claude Code |
| **Phase 2: UI Development** | PyQt6 UI 개발 가이드 | 개발자, Claude Code |
| **Phase 3: Integration** | 통합 및 검증 가이드 | 개발자, Claude Code |
| **Claude Code Protocol** | Claude Code 작업 규칙 | 개발자 |

---

## 🎯 마이그레이션 원칙

### 핵심 원칙

1. **로직 재구현 금지**: 레거시 코드를 복사만 하고 재작성하지 않음
2. **최소 변경**: UI 의존성 제거를 위한 최소한의 변경만 허용
3. **100% 동작 보장**: 출력 결과가 레거시와 완전히 일치해야 함
4. **단계별 검증**: 각 Phase마다 검증 후 다음 단계 진행

### 성공 기준

| 항목 | 기준 | 측정 방법 |
|------|------|-----------|
| **기능 동작률** | 100% | 모든 레거시 기능 정상 동작 |
| **출력 파일 일치** | 100% | pandas.DataFrame.equals() |
| **Round-trip 무결성** | 100% | LY/GL 병합→분할→원본 일치 |
| **테스트 통과율** | 100% | LY/GL 37개 단위 테스트 |

---

## 🗺️ 전체 로드맵

### Phase 1: 로직 추출 (1-2주)

**목표**: 레거시 코드에서 순수 로직만 추출하여 `sebastian/core/` 구축

**작업 내용**:
- M4/GL: `run_merge()`, `run_merge_string()` 함수 추출
- NC/GL: `process_files()` 함수 추출
- LY/GL: 이미 분리된 모듈 그대로 복사

**산출물**:
```
sebastian/core/
├── m4gl/
│   ├── dialogue.py      # run_merge() 복사본
│   └── string.py        # run_merge_string() 복사본
├── ncgl/
│   └── merger.py        # process_files() 복사본
└── lygl/                # LY/GL 전체 복사
    ├── merge.py
    ├── split.py
    ├── batch_merger.py
    └── legacy_diff.py
```

**검증**:
- [ ] diff로 변경사항 확인 (함수명, 인자 외 변경 없음)
- [ ] 의존성 확인 (pandas, openpyxl, xlsxwriter)
- [ ] 단위 테스트 작성 (가능한 경우)

**상세**: [Sebastian-Phase1-Logic-Extraction.md](Sebastian-Phase1-Logic-Extraction.md)

---

### Phase 2: UI 개발 (2-3주)

**목표**: PyQt6 기반 통합 UI 구축 (wireframe 기반)

**작업 내용**:
- 메인 창 + 탭 구조
- 공통 컴포넌트 (ProgressDialog, LogViewer)
- 각 게임별 탭 (M4GL, NCGL, LYGL)

**산출물**:
```
sebastian/ui/
├── main_window.py       # 메인 창 + 탭
├── m4gl_tab.py          # M4/GL 탭
├── ncgl_tab.py          # NC/GL 탭
├── lygl_tab.py          # LY/GL 탭
└── common/
    ├── progress_dialog.py
    └── log_viewer.py
```

**검증**:
- [ ] wireframe 디자인 100% 구현
- [ ] 모든 버튼 클릭 → 해당 core 함수 호출
- [ ] ProgressDialog 동작 확인

**상세**: [Sebastian-Phase2-UI-Development.md](Sebastian-Phase2-UI-Development.md)

---

### Phase 3: 통합 및 검증 (1-2주)

**목표**: UI와 로직 연결 및 레거시와의 동작 일치 검증

**작업 내용**:
- QThread로 비동기 처리
- Signal/Slot 연결
- 레거시 출력 파일과 비교 검증

**산출물**:
- 완성된 sebastian.exe
- 검증 리포트

**검증**:
- [ ] M4/GL DIALOGUE: 출력 파일 100% 일치
- [ ] M4/GL STRING: 출력 파일 100% 일치
- [ ] NC/GL: 출력 파일 100% 일치
- [ ] LY/GL Merge: 출력 파일 100% 일치
- [ ] LY/GL Split: 출력 파일 100% 일치
- [ ] LY/GL Round-trip: 원본 복원 100%
- [ ] LY/GL 37개 단위 테스트 통과

**상세**: [Sebastian-Phase3-Integration.md](Sebastian-Phase3-Integration.md)

---

## 📋 Phase별 체크리스트

### Phase 1: 로직 추출

#### LY/GL (우선순위 1 - 가장 쉬움)
- [ ] `legacy/LY/src/merge.py` → `sebastian/core/lygl/merge.py` 복사
- [ ] `legacy/LY/src/split.py` → `sebastian/core/lygl/split.py` 복사
- [ ] `legacy/LY/src/batch_merger.py` → `sebastian/core/lygl/batch_merger.py` 복사
- [ ] `legacy/LY/src/legacy_diff.py` → `sebastian/core/lygl/legacy_diff.py` 복사
- [ ] `legacy/LY/src/excel_format.py` → `sebastian/core/lygl/excel_format.py` 복사
- [ ] `legacy/LY/src/validator.py` → `sebastian/core/lygl/validator.py` 복사
- [ ] `legacy/LY/src/error_messages.py` → `sebastian/core/lygl/error_messages.py` 복사
- [ ] customtkinter 의존성 제거 (ui.py 제외)
- [ ] 37개 단위 테스트 복사 및 통과 확인

#### M4/GL (우선순위 2)
- [ ] `sebastian/core/m4gl/dialogue.py` 생성
- [ ] `legacy/M4/Merged_M4.py:74-266` (run_merge) 복사
- [ ] 함수명 변경: `run_merge()` → `merge_dialogue(folder_path, progress_queue)`
- [ ] tkinter 의존성 제거
- [ ] diff 확인: 함수명, 인자 외 변경 없음
- [ ] `sebastian/core/m4gl/string.py` 생성
- [ ] `legacy/M4/Merged_M4.py:268-422` (run_merge_string) 복사
- [ ] 함수명 변경: `run_merge_string()` → `merge_string(folder_path, progress_queue)`
- [ ] diff 확인

#### NC/GL (우선순위 3)
- [ ] `sebastian/core/ncgl/merger.py` 생성
- [ ] `legacy/NC/Merged_NC.py:147-272` (process_files) 복사
- [ ] 함수명 변경: `process_files()` → `merge_ncgl(folder_path, date, milestone, progress_queue)`
- [ ] tkinter 의존성 제거
- [ ] ProcessPoolExecutor 로직 유지
- [ ] xlsxwriter 사용 유지
- [ ] diff 확인

### Phase 2: UI 개발

#### 공통 컴포넌트
- [ ] `sebastian/ui/common/progress_dialog.py` 작성
  - [ ] QDialog + QProgressBar
  - [ ] Signal: progress_updated(int), status_updated(str)
  - [ ] Slot: update_progress(int), update_status(str)
- [ ] `sebastian/ui/common/log_viewer.py` 작성
  - [ ] QPlainTextEdit 기반
  - [ ] 접기/펴기 기능
  - [ ] 로그/에러/경고 탭

#### 메인 창
- [ ] `sebastian/ui/main_window.py` 작성
  - [ ] QMainWindow + QTabWidget
  - [ ] 메뉴바 (파일, 도움말)
  - [ ] 상태바
  - [ ] LogViewer 통합

#### 게임별 탭
- [ ] `sebastian/ui/m4gl_tab.py` 작성 (wireframe 참조)
  - [ ] DIALOGUE/STRING QPushButton (280x200)
  - [ ] 폴더 선택 (QLineEdit + QPushButton)
  - [ ] 실행 버튼 (160x48)
- [ ] `sebastian/ui/ncgl_tab.py` 작성
  - [ ] 날짜 입력 (QLineEdit + 검증)
  - [ ] 마일스톤 입력 (QLineEdit + 검증)
  - [ ] 폴더 선택
  - [ ] 실행 버튼
- [ ] `sebastian/ui/lygl_tab.py` 작성
  - [ ] 4개 버튼 그리드 (Merge, Split, Batches, Diff)
  - [ ] 각 버튼 클릭 → 위저드 Dialog

### Phase 3: 통합 및 검증

#### 비동기 처리
- [ ] M4/GL QThread Worker 작성
  - [ ] DIALOGUE Worker
  - [ ] STRING Worker
- [ ] NC/GL QThread Worker 작성
- [ ] LY/GL QThread Worker 작성 (4개 기능별)

#### Signal/Slot 연결
- [ ] ProgressDialog ↔ Worker 연결
- [ ] LogViewer ↔ Worker 연결
- [ ] 상태바 업데이트

#### 출력 파일 검증
- [ ] M4/GL DIALOGUE: 레거시 vs 신규 비교
- [ ] M4/GL STRING: 레거시 vs 신규 비교
- [ ] NC/GL: 레거시 vs 신규 비교
- [ ] LY/GL Merge: 레거시 vs 신규 비교
- [ ] LY/GL Split: 레거시 vs 신규 비교
- [ ] LY/GL Batches: 동작 확인
- [ ] LY/GL Diff: 동작 확인

#### Round-trip 무결성
- [ ] LY/GL: Merge → Split → 원본 일치 확인

#### 단위 테스트
- [ ] LY/GL 37개 테스트 통과

---

## 🤝 Claude Code 작업 프로토콜

**상세**: [Sebastian-Claude-Code-Protocol.md](Sebastian-Claude-Code-Protocol.md)

**핵심 규칙**:

1. **명확한 지시**: "구현해줘" ❌ → "복사해줘" ✅
2. **단계별 진행**: 한 번에 하나의 Task만
3. **검증 필수**: 각 Task 완료 후 diff/테스트
4. **변경 금지**: 레거시 로직은 함수명, 인자 외 변경 금지

**지시 예시**:
```
❌ "M4/GL DIALOGUE 병합 기능 구현해줘"
✅ "legacy/M4/Merged_M4.py:74-266을 sebastian/core/m4gl/dialogue.py로
   복사하고, 함수명을 merge_dialogue()로 변경해줘.
   progress_queue 인자를 추가하고 나머지는 변경하지 마."
```

---

## 📊 진행 상황 추적

### 전체 진행률

- [ ] Phase 1: 로직 추출 (0%)
  - [ ] LY/GL (0%)
  - [ ] M4/GL (0%)
  - [ ] NC/GL (0%)
- [ ] Phase 2: UI 개발 (0%)
  - [ ] 공통 컴포넌트 (0%)
  - [ ] 메인 창 (0%)
  - [ ] 게임별 탭 (0%)
- [ ] Phase 3: 통합 및 검증 (0%)
  - [ ] 비동기 처리 (0%)
  - [ ] 출력 파일 검증 (0%)
  - [ ] 단위 테스트 (0%)

### 예상 일정

| Phase | 기간 | 완료 예정 |
|-------|------|-----------|
| Phase 1 | 1-2주 | - |
| Phase 2 | 2-3주 | - |
| Phase 3 | 1-2주 | - |
| **전체** | **4-7주** | - |

---

## 🚨 리스크 및 대응

### 리스크 1: 레거시 코드 재구현

**문제**: Claude Code가 로직을 재작성하여 결과 불일치

**대응**:
- Implementation PRD에 "변경 금지" 명시
- diff로 변경사항 검증
- 출력 파일 비교로 즉시 확인

### 리스크 2: 의존성 충돌

**문제**: openpyxl vs xlsxwriter, pandas 버전 등

**대응**:
- 각 core 모듈은 레거시 의존성 그대로 유지
- requirements.txt에 모든 의존성 명시
- 가상환경에서 테스트

### 리스크 3: 비동기 처리 오류

**문제**: QThread 처리 중 데이터 손실, UI 프리징

**대응**:
- Queue 기반 통신 (레거시와 동일)
- Signal/Slot으로 안전한 UI 업데이트
- 에러 핸들링 강화

### 리스크 4: 검증 불가능

**문제**: 레거시 출력 파일이 없거나 접근 불가

**대응**:
- 마이그레이션 전 레거시 실행하여 기준 파일 생성
- 테스트 데이터셋 준비
- LY/GL 단위 테스트 활용

---

## 📚 참고 문서

### 프로젝트 문서
- [Sebastian-PRD-Master.md](Sebastian-PRD-Master.md) - 전체 프로젝트 개요
- [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md) - UI 디자인 스펙
- [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md) - 공통 요소

### 레거시 코드
- `legacy/M4/Merged_M4.py` - M4/GL 소스 코드
- `legacy/NC/Merged_NC.py` - NC/GL 소스 코드
- `legacy/LY/src/*.py` - LY/GL 소스 코드

---

## 📅 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0.0 | 2025-12-19 | 초안 작성 (Option C 선택) | Claude + 재경 |

---

**다음 단계**: Phase 1 가이드 문서 작성 시작
