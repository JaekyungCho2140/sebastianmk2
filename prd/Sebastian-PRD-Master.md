# Sebastian PRD - Master Document

**프로젝트명**: Sebastian
**버전**: 1.0.0
**작성일**: 2025-12-10
**작성자**: 재경 (L10n Team Localization Project Manager)
**상태**: Draft

---

## 📋 문서 구조

이 PRD는 모듈화된 구조로 작성되었습니다:

| 문서 | 역할 | 링크 |
|------|------|------|
| **Master** (이 문서) | 프로젝트 전체 조율 | - |
| **Shared** | 공통 요소 집중 | [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md) |
| **UI Wireframes** | UI 디자인 스펙 | [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md) |
| **M4GL** | M4/GL 병합 기능 | [Sebastian-PRD-M4GL.md](Sebastian-PRD-M4GL.md) |
| **NCGL** | NC/GL 병합 기능 | [Sebastian-PRD-NCGL.md](Sebastian-PRD-NCGL.md) |
| **LYGL** | LY/GL 병합/분할/Diff | [Sebastian-PRD-LYGL.md](Sebastian-PRD-LYGL.md) |

---

## 🎯 프로젝트 목적

**핵심 목적**: 게임 퍼블리셔 L10n(Localization)팀에서 실무에 사용하는 **3개 게임의 현지화 테이블 관리 도구를 단일 통합 프로그램으로 통합**

**해결하려는 문제**:
1. **도구 분산**: 3개 게임 각각의 독립 Python 스크립트 실행 → 번거로움
2. **기술 스택 불일치**: tkinter/customtkinter 혼재 → 사용자 경험 비일관성
3. **중복 코드**: 진행도 표시, 파일 선택, 검증 로직 중복 → 유지보수 부담
4. **확장성 부족**: 새 게임 추가 시 새로운 독립 도구 개발 필요

**목표 달성 기준**:
- ✅ 단일 실행 파일(.exe)로 3개 게임 기능 제공
- ✅ 통합된 PyQt6 기반 UI/UX
- ✅ 레거시 기능 100% 동작 보장 (Round-trip 무결성 포함)
- ✅ 공통 컴포넌트 재사용으로 중복 코드 제거

---

## 🏗️ 전체 아키텍처

### 계층 구조

```
Sebastian.exe
│
├── Main Window (PyQt6)
│   ├── 프로젝트 선택 탭
│   │   ├── M4/GL
│   │   ├── NC/GL
│   │   └── LY/GL
│   │
│   └── 공통 UI 컴포넌트
│       ├── 진행도 Dialog
│       ├── 파일 선택 Dialog
│       └── 에러/로그 뷰어
│
├── Core Engine
│   ├── M4GL 병합 로직
│   ├── NCGL 병합 로직
│   └── LYGL 테이블 처리 로직
│
└── Shared Components
    ├── Excel 처리 (pandas + openpyxl)
    ├── 데이터 검증
    ├── 설정 관리
    └── 에러 처리
```

### UI 구조

**상세 UI 와이어프레임**: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md)

**개요**:
- **메인 창**: 탭 기반 레이아웃 (M4/GL, NC/GL, LY/GL)
- **메뉴바**: 파일(F), 도움말(H)
- **로그 뷰어**: 하단 영역, 접기/펴기 가능 (로그/에러/경고 탭)
- **상태바**: 현재 작업 상태 표시

**탭별 UI**:
- **M4/GL**: 2개 큰 버튼 (DIALOGUE, STRING) + 폴더 선택
- **NC/GL**: 실시간 검증 입력 필드 (날짜, 마일스톤) + 폴더 선택
- **LY/GL**: 4개 큰 버튼 (Merge, Split, Batches, Diff) → 위저드 Dialog

**공통 컴포넌트**:
- **ProgressDialog**: 모달 진행도 표시 (양방향 Signal/Slot)
- **LogViewer**: 로그/에러/경고 실시간 표시
- **FileSelectionDialog**: 파일/폴더 선택 헬퍼

**참조**:
- UI 상세 디자인: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md)
- 공통 컴포넌트 구현: [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md)
- 각 탭별 UI: Feature 문서 (M4GL, NCGL, LYGL)

### 메뉴바 (Round 3 결정 - 최소화)

**파일(F) 메뉴**:
```
파일(F)
  ├─ 로그 저장...          (현재 로그를 .txt로 저장)
  ├─ ──────────────
  └─ 종료                 (Ctrl+Q)
```

**도움말(H) 메뉴**:
```
도움말(H)
  ├─ 사용자 가이드          (README.md)
  ├─ ──────────────
  └─ Sebastian 정보        (버전, 개발자, 라이선스)
```

**사용자 가이드 동작**:
- **위치**: 실행 파일(.exe)과 같은 폴더의 `README.md`
- **실행**: 기본 텍스트 에디터로 열기 (Windows: notepad.exe)
- **파일 없을 때**: "사용자 가이드를 찾을 수 없습니다" 메시지 표시
- **작성 담당**: 개발자 (개발 완료 후 작성)

**제거된 항목** (불필요):
- ~~최근 폴더 열기~~: QFileDialog가 자동으로 최근 위치 기억
- ~~설정 메뉴 전체~~: 간단한 도구, 설정 불필요
- ~~키보드 단축키~~: 메뉴가 간단해서 불필요
- ~~레거시 도구 위치~~: 개발자용 정보

### 기술 스택

**상세 내용**: [Sebastian-PRD-Shared.md#기술-스택](Sebastian-PRD-Shared.md#기술-스택)

**요약**:
- **GUI 프레임워크**: PyQt6
- **Excel 처리**: pandas, openpyxl, xlsxwriter
- **비동기 처리**: QThread (레거시의 threading/ProcessPoolExecutor 대체)
- **배포**: PyInstaller

---

## 📦 기능 목록

### 우선순위 1: 핵심 테이블 병합 기능

| 기능 | 설명 | 상태 | 문서 링크 |
|------|------|------|-----------|
| **M4/GL DIALOGUE 병합** | 3개 파일 → 1개 통합 (23개 컬럼) | ✅ 상세 분석 완료 | [Sebastian-PRD-M4GL.md#dialogue](Sebastian-PRD-M4GL.md#dialogue-병합) |
| **M4/GL STRING 병합** | 8개 파일 → 1개 통합 (15개 컬럼) | ✅ 상세 분석 완료 | [Sebastian-PRD-M4GL.md#string](Sebastian-PRD-M4GL.md#string-병합) |
| **NC/GL 병합** | 8개 언어 → 1개 통합 (병렬 처리) | ✅ 상세 분석 완료 | [Sebastian-PRD-NCGL.md](Sebastian-PRD-NCGL.md) |
| **LY/GL Merge** | 7개 언어 → 1개 통합 | ✅ 상세 분석 완료 | [Sebastian-PRD-LYGL.md#merge](Sebastian-PRD-LYGL.md#merge) |
| **LY/GL Split** | 1개 통합 → 7개 언어 | ✅ 상세 분석 완료 | [Sebastian-PRD-LYGL.md#split](Sebastian-PRD-LYGL.md#split) |

### 우선순위 2: 고급 기능

| 기능 | 설명 | 상태 | 문서 링크 |
|------|------|------|-----------|
| **LY/GL Merge Batches** | 배치 병합 + 중복 제거 | ✅ 상세 분석 완료 | [Sebastian-PRD-LYGL.md#merge-batches](Sebastian-PRD-LYGL.md#merge-batches) |
| **LY/GL Legacy Diff** | 두 버전 비교 → 변경 추적 | ✅ 상세 분석 완료 | [Sebastian-PRD-LYGL.md#legacy-diff](Sebastian-PRD-LYGL.md#legacy-diff) |

---

## 🚀 개발 로드맵

### Phase 1: 기반 아키텍처 (우선순위: Critical)
**목표**: PyQt6 기반 구조 및 공통 컴포넌트 개발

- [ ] PyQt6 Main Window 설계
- [ ] 프로젝트 탭 구조 구현 (M4GL, NCGL, LYGL)
- [ ] 공통 진행도 Dialog (QProgressDialog)
- [ ] 공통 파일 선택 Dialog (QFileDialog)
- [ ] 공통 에러/로그 뷰어 (QPlainTextEdit)
- [ ] 설정 관리 (QSettings)

### Phase 2: M4/GL 기능 마이그레이션 (우선순위: High)
**목표**: DIALOGUE/STRING 병합 기능 구현

- [ ] DIALOGUE 병합 로직 포팅
- [ ] STRING 병합 로직 포팅
- [ ] 이미지 버튼 → QPushButton 변환
- [ ] NPC 매핑 기능 구현
- [ ] 결과 파일 서식 지정
- [ ] 통합 테스트 (레거시 결과와 100% 일치)

### Phase 3: NC/GL 기능 마이그레이션 (우선순위: High)
**목표**: 8개 언어 병합 + 병렬 처리

- [ ] 병렬 파일 읽기 (QThreadPool)
- [ ] 날짜/마일스톤 입력 UI
- [ ] xlsxwriter 통합
- [ ] 통합 테스트

### Phase 4: LY/GL 기능 마이그레이션 (우선순위: High)
**목표**: Merge/Split/Batch/Diff 전체 기능

- [ ] Merge 로직 포팅
- [ ] Split 로직 포팅
- [ ] Merge Batches 구현
- [ ] Legacy Diff 구현
- [ ] Round-trip 무결성 테스트
- [ ] 37개 단위 테스트 마이그레이션

### Phase 5: 최적화 및 배포 (우선순위: Medium)
**목표**: 성능 개선 및 사용자 경험 향상

- [ ] 대용량 파일 처리 최적화 (49,600행+)
- [ ] UI/UX 개선 (다크 모드, 접근성)
- [ ] PyInstaller 빌드 설정
- [ ] 사용자 문서 작성
- [ ] 배포 패키지 생성

---

## ⚠️ 제외 사항 (Out of Scope)

**이번 개발 사이클에서 구현하지 않는 기능**:

1. ❌ **Folder Creator** - 폴더 자동 생성 기능 (향후 고려)
2. ❌ **Bulk Jira Task Creator** - JIRA 일감 생성 (향후 고려)
3. ❌ **웹 기반 인터페이스** - 데스크톱 앱만 구현
4. ❌ **자동 업데이트 기능** - 수동 배포
5. ❌ **다국어 UI** - 한국어만 지원

---

## 🔧 기술적 제약사항

### 필수 요구사항

1. **OS**: Windows 10 이상
2. **Python**: 3.8+ (개발 환경)
3. **Excel**: 결과 파일 열람용 (Microsoft Excel 2016+)

### 성능 목표

| 항목 | 목표 | 근거 |
|------|------|------|
| **대용량 처리** | ~50,000행 처리 | LY/GL 실제 데이터 기준 |
| **병합 시간** | < 5초 (병렬 처리) | NC/GL 8개 파일 기준 |
| **메모리 사용** | < 500MB | 일반 사무용 PC 고려 |
| **EXE 크기** | < 100MB | 배포 편의성 |

### 레거시 호환성

**100% 동작 보장**:
- ✅ 입력 파일 형식 동일
- ✅ 출력 파일 내용 동일 (Round-trip 무결성)
- ✅ 서식 지정 규칙 동일
- ✅ 에러 메시지 동일

**개선 허용**:
- ✅ UI/UX 디자인 변경 (PyQt6 네이티브)
- ✅ 성능 최적화
- ✅ 에러 처리 강화

---

## 📝 용어 정리

**상세 용어집**: [Sebastian-PRD-Shared.md#용어집](Sebastian-PRD-Shared.md#용어집)

**핵심 용어**:
- **M4/GL**: 미르4 글로벌 (게임)
- **NC/GL**: 나이트크로우 글로벌 (게임)
- **LY/GL**: 레전드 오브 이미르 글로벌 (게임)
- **L10n**: Localization (현지화)
- **병합(Merge)**: 여러 파일을 하나로 통합
- **분할(Split)**: 하나의 파일을 여러 파일로 분리
- **Round-trip**: 병합 → 분할 → 원본 동일성 보장

---

## 📊 성공 지표 (Success Metrics)

### 기능 완성도

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **기능 동작률** | 100% | 모든 레거시 기능 정상 동작 |
| **Round-trip 무결성** | 100% | LY/GL 병합→분할 원본 일치 |
| **테스트 통과율** | 100% | 37개 단위 테스트 전부 통과 |

### 사용자 경험

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **작업 시간 단축** | 50% | 도구 실행부터 결과까지 |
| **에러 발생률** | < 1% | 정상 입력 시 성공률 |
| **사용자 만족도** | > 4/5 | L10n팀 비공식 피드백 (개발 완료 후) |

### 코드 품질

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **코드 중복률** | < 5% | 공통 컴포넌트 재사용 |
| **테스트 커버리지** | > 80% | pytest-cov |
| **문서화 완성도** | 100% | 모든 공개 함수 docstring |

---

## 🔐 보안 및 데이터 관리

### 데이터 보안

1. **민감 정보 처리**: 게임 번역 데이터는 내부 자료 → 외부 유출 금지
2. **임시 파일 관리**: 처리 중 임시 파일 생성 시 작업 완료 후 자동 삭제
3. **결과 파일 권한**: 읽기 전용 설정 (M4/GL 레거시 동작 유지)

### 에러 로그

1. **로그 파일 위치**: 실행 파일과 동일 디렉터리 (`sebastian.log`)
2. **로그 레벨**: INFO (일반), DEBUG (개발 중)
3. **개인정보**: 파일 경로만 저장, 파일 내용 비저장

---

## 📚 참고 문서

### 레거시 코드 분석

- [LY/GL 상세 분석](../claudedocs/LY_Table_레거시_코드_분석.md)
- [M4/GL 상세 분석](../claudedocs/M4GL-legacy-code-analysis.md)
- [NC/GL 상세 분석](../claudedocs/NCGL-legacy-code-analysis.md)
- [전체 요약](../drafts/Sebastian-Analysis-Summary.md)

### 레거시 코드 위치

- `legacy/Merged_M4/` - M4/GL 소스 코드
- `legacy/Merged_NC/` - NC/GL 소스 코드
- `legacy/LY_Table/` - LY/GL 소스 코드

---

## 📅 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0.0 | 2025-12-10 | 초안 작성 (Phase 0 완료) | 재경 |
| 1.0.1 | 2025-12-11 | 사용자 가이드 위치 명확화 (README.md) | 재경 |
| 1.0.2 | 2025-12-11 | 사용자 만족도 측정 방법 명시 (비공식 피드백) | 재경 |
| 1.1.0 | 2025-12-12 | UI 와이어프레임 문서 추가, UI 섹션 와이어프레임 참조로 변경 | 재경 |
| 1.2.0 | 2025-12-12 | 와이어프레임 문서 v2.0 전면 재작성 (미니멀 디자인, PyQt6 구현 가이드) | 재경 |

---

**다음 단계**: 이 Master 문서를 검토하신 후, Shared 및 Feature 문서 작성을 진행하겠습니다.
