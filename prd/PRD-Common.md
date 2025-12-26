# PRD - 공통 도구 (Common Tools)

**버전**: 1.0
**작성일**: 2025-12-26
**대상**: 공통 탭 기능 명세

---

## 📋 목차

1. [개요](#개요)
2. [CSV 따옴표 복원 기능](#csv-따옴표-복원-기능)
3. [아키텍처](#아키텍처)
4. [기술 명세](#기술-명세)
5. [UI/UX 명세](#uiux-명세)
6. [향후 확장](#향후-확장)

---

## 개요

### 목적

여러 게임에 공통으로 사용할 수 있는 도구 모음을 제공합니다.

### 범위

**현재 기능**:
- CSV 따옴표 복원 (memoQ export 파일 처리)

**향후 추가 예정**:
- CSV 병합
- CSV 분할
- CSV 형식 변환 (UTF-8 ↔ EUC-KR)

---

## CSV 따옴표 복원 기능

### 배경

L10n 팀에서 사용하는 memoQ 도구는 RFC 4180 규격에 맞지 않는 CSV 파일을 자동으로 정규화(Truncate)하는 기능이 있으며, 이 기능을 비활성화할 수 없습니다.

**발생하는 문제**:
1. **필드 따옴표 추가/제거**: 원본에 없던 따옴표 추가 또는 있던 따옴표 제거
2. **이중 따옴표 escape**: HTML 태그 내 `class="green"` → `class=""green""`

### 기능 목표

memoQ에서 export한 CSV 파일을 원본 파일과 비교하여, 원본의 따옴표 패턴을 그대로 복원합니다.

**핵심 원칙**:
- ✅ **원본 raw text 완벽 재현** (RFC 4180 위반 포함)
- ✅ **번역 변경 사항 반영** (export data 사용)
- ❌ RFC 4180 준수 **무시**

---

## 아키텍처

### 3계층 구조

```
┌─────────────────────────────────────────┐
│         UI Layer (PyQt6 v2)              │
│  - CommonTab                             │
│  - RestoreCSVWizard                      │
└──────────────┬──────────────────────────┘
               │ Signal/Slot
               ▼
┌─────────────────────────────────────────┐
│      Worker Layer (QThread)              │
│  - CommonWorker                          │
│    - restore_csv operation               │
└──────────────┬──────────────────────────┘
               │ progress_queue
               ▼
┌─────────────────────────────────────────┐
│       Core Layer (Business Logic)        │
│  - csv_validator.py (구조 검증)          │
│  - csv_parser.py (상태 머신 파서)        │
│  - csv_restore.py (복원 + 보고서)        │
└─────────────────────────────────────────┘
```

### 파일 구조

```
sebastian/
├── core/common/
│   ├── __init__.py
│   ├── csv_validator.py     # CSV 구조 검증
│   ├── csv_parser.py         # Raw CSV 파서
│   └── csv_restore.py        # 복원 로직
├── workers/
│   └── common_worker.py      # 비동기 작업
├── ui/
│   ├── common_tab.py         # 공통 탭
│   └── wizards/
│       └── restore_csv_wizard.py  # Wizard
tests/test_common/
├── test_csv_validator.py     # 5개 테스트
├── test_csv_parser.py        # 13개 테스트
├── test_csv_restore.py       # 4개 테스트
└── test_real_files.py        # 2개 테스트
```

---

## 기술 명세

### CSV 파서 (상태 머신)

#### 상태 정의

```
FIELD_START     : 필드 시작
IN_QUOTED       : 따옴표 필드 내부
IN_UNQUOTED     : 일반 필드 내부
AFTER_QUOTE     : 따옴표 닫힌 직후
```

#### 상태 전이

```
FIELD_START → IN_QUOTED      (문자 = ")
FIELD_START → IN_UNQUOTED    (문자 = 일반)
FIELD_START → FIELD_START    (문자 = ,, 빈 필드)

IN_QUOTED → IN_QUOTED        (문자 = 일반)
IN_QUOTED → IN_QUOTED        ("" = escape)
IN_QUOTED → AFTER_QUOTE      (문자 = ", 닫기)

IN_UNQUOTED → FIELD_START    (문자 = ,)
IN_UNQUOTED → IN_UNQUOTED    (문자 = 일반)
IN_UNQUOTED → IN_UNQUOTED    (문자 = ", RFC 위반 허용)

AFTER_QUOTE → FIELD_START    (문자 = ,)
AFTER_QUOTE → AFTER_QUOTE    (RFC 위반 허용)
```

#### 출력

```python
[
    (field_value, has_quotes, raw_field_text),
    ...
]
```

**예시**:
```python
parse_csv_line_raw('"field1",field2,"field3"')
# → [('field1', True, '"field1"'),
#     ('field2', False, 'field2'),
#     ('field3', True, '"field3"')]

parse_csv_line_raw('text,"<span class=""green"">Test</span>"')
# → [('text', False, 'text'),
#     ('<span class="green">Test</span>', True, '"<span class=""green"">Test</span>"')]
```

### 복원 알고리즘

#### Step 1: 패턴 분석

```python
original_pattern = analyze_csv_pattern(original_path)
export_pattern = analyze_csv_pattern(export_path)

# {(row_idx, col): {'has_field_quotes': bool,
#                   'original_value': str,
#                   'raw_field_text': str}}
```

#### Step 2: 검증

```python
validate_csv_structure(original_path, export_path)
```

**검증 항목**:
- ✅ 파일 존재 여부
- ✅ CSV 파싱 가능 여부
- ✅ 컬럼 수 일치 (필수)
- ✅ 헤더 일치 (권장, 불일치 시 예외)
- ✅ key-name 값 일치 (불일치 시 예외)

#### Step 3: key-name 기준 매칭

```python
key_column = df.columns[0]  # 첫 번째 컬럼
original_key_map = {key: idx for idx, key in enumerate(original_df[key_column])}
export_key_map = {key: idx for idx, key in enumerate(export_df[key_column])}
```

#### Step 4: 필드별 복원

```python
for row_idx, col in all_fields:
    export_value = export_df.iloc[row_idx][col]
    original_value = original_pattern[(row_idx, col)]['original_value']
    original_raw = original_pattern[(row_idx, col)]['raw_field_text']

    if export_value == original_value:
        # 내용 동일 → 원본 raw text 그대로
        restored_field = original_raw
    else:
        # 내용 변경 → Export 값 사용
        restored_field = export_value

    # CSV에 직접 쓰기 (RFC 4180 무시!)
    f.write(restored_field)
```

#### Step 5: 보고서 생성

```python
for row_idx, col in all_fields:
    export_raw = export_pattern[(row_idx, col)]['raw_field_text']
    restored_raw = restored_pattern[(row_idx, col)]

    if export_raw != restored_raw:
        # 복원 발생! 보고서에 기록
        report.add({
            'key-name': key_value,
            'Column': col,
            'Original': original_raw,
            'Export': export_raw,
            'Restored': restored_raw,
            'Status': '✅ 따옴표 복원'
        })
```

### 보고서 형식

**Excel 파일 구조** (`{filename}_diff_report.xlsx`):

**Sheet 1: Summary**
| 항목 | 값 |
|------|-----|
| 총 행 수 | 84 |
| 총 필드 수 | 756 |
| 따옴표 복원된 필드 수 | 14 |
| 경고 수 | 0 |
| 오류 수 | 0 |

**Sheet 2: Restored Fields**
| key-name | Column | Original | Export | Restored | Status |
|----------|--------|----------|--------|----------|--------|
| key-name7 | ko | `"서버의..."` | `서버의...` | `"서버의..."` | ✅ 따옴표 복원 |
| key-name46 | ko | `각 지역의... '<span class="green">...` | `"각 지역의... '<span class=""green"">..."` | `각 지역의... '<span class="green">...` | ✅ 따옴표 복원 |

**Sheet 3: Warnings**
| Type | key-name | Message |
|------|----------|---------|
| - | - | 검증 통과 (경고 없음) |

---

## UI/UX 명세

### 공통 탭 (CommonTab)

**레이아웃**: LY/GL과 동일한 수직 리스트

**구성 요소**:
- 제목: "공통 도구" (24px, bold, Primary 색상)
- 설명: 2줄 텍스트 (Secondary 색상)
- 기능 버튼 리스트:
  - 높이: 64px
  - 간격: 12px
  - objectName: `listItemButton`
  - 텍스트: 타이틀 + 설명 (왼쪽 정렬)
  - 화살표 아이콘: `→` (오른쪽)

**현재 기능**:
1. CSV 따옴표 복원
   - 타이틀: "CSV 따옴표 복원"
   - 설명: "memoQ export 파일의 따옴표를 원본 파일과 비교하여 복원합니다"

### RestoreCSVWizard

**타입**: 단일 페이지 QDialog

**크기**: 700 x 350px

**구성 요소**:

1. **제목**: "CSV 따옴표 복원" (20px, bold)
2. **설명**: 기능 안내 문구 (2줄)
3. **파일 선택 섹션** (3개):
   - 원본 파일 선택 (QLineEdit + "📁 찾아보기" 버튼)
   - memoQ Export 파일 선택
   - 출력 폴더 선택
4. **하단 버튼**:
   - "취소" (secondaryButton)
   - "복원 시작" (primaryButton, 모든 필드 입력 시 활성화)

**동작**:
- 파일 선택 시 경로를 QLineEdit에 표시
- 모든 필드 입력 완료 시 "복원 시작" 버튼 활성화
- Accept 시 `get_data()` 반환: `{original_path, export_path, output_dir}`

### Signal/Slot

**CommonTab Signals**:
```python
restore_csv_requested = pyqtSignal()
```

**CommonWorker Signals**:
```python
progress_updated = pyqtSignal(int)        # 0-100
status_updated = pyqtSignal(str)          # 상태 메시지
completed = pyqtSignal(str)               # 완료 메시지
error_occurred = pyqtSignal(str)          # 에러 메시지
```

**MainWindow 연결**:
```python
self.common_tab.restore_csv_requested.connect(self._on_restore_csv_requested)
```

---

## 성능 요구사항

| 항목 | 목표 | 현재 달성 |
|------|------|----------|
| 10,000행 처리 시간 | < 5초 | ~2초 ✅ |
| 메모리 사용량 | < 500MB | ~40MB ✅ |
| UI 반응성 | 블로킹 없음 | 비동기 ✅ |

---

## 검증 및 에러 처리

### 검증 규칙

| 검증 항목 | 조건 | 실패 시 동작 |
|----------|------|-------------|
| 파일 존재 | 원본, export 파일 존재 | 예외 발생, 작업 중단 |
| CSV 파싱 | 정상 파싱 가능 | 예외 발생, 작업 중단 |
| 컬럼 수 | 원본 == export | 예외 발생, 작업 중단 |
| 헤더 | 원본 == export | 경고 + 예외 발생 |
| key-name 값 | 원본 == export | 경고 + 예외 발생 |

### 에러 메시지

```python
CSVValidationError("컬럼 수 불일치: 원본 9개, export 6개")
CSVValidationError("헤더 불일치: {'ko', 'en'}")
CSVValidationError("Export에만 있는 key-name: {'key4'}")
CSVValidationError("원본 파일이 존재하지 않습니다: path")
```

---

## 특수 케이스 처리

### RFC 4180 위반 파일

**케이스 1**: 필드 따옴표 미완성
```csv
"Copa de Yggdrasil" concedida...
```
- 필드가 `"Copa..."`로 시작했지만 중간에 닫고 계속
- pandas: 관대하게 파싱 → 전체를 하나의 필드로 인식
- 복원: 원본 raw text 그대로 저장 ✅

**케이스 2**: 필드 내부 따옴표 미escape
```csv
각 지역의... '<span class="green">레이저</span>'
```
- 따옴표 없는 필드 내부에 `"` 문자
- RFC 4180 위반이지만 실제 파일에서 발생
- 파서: 경고 로그 후 계속 파싱 ✅

**케이스 3**: HTML entity
```csv
서버의 명예&#44; 클랜의 전략&#44;...
```
- `&#44;`는 HTML entity (쉼표 escape)
- CSV 파싱에 영향 없음
- 원본 패턴대로 복원 ✅

---

## 향후 확장

### Phase 2: 추가 기능

1. **CSV 병합**
   - 여러 CSV 파일 → 1개 통합
   - key-name 기준 매칭

2. **CSV 분할**
   - 1개 CSV → 언어별 분할
   - 컬럼 선택 기능

3. **CSV 형식 변환**
   - UTF-8 ↔ EUC-KR
   - Excel ↔ CSV

### Phase 3: 도구 확장

1. **다양한 CAT 도구 지원**
   - SDL Trados
   - Smartling
   - Crowdin

2. **자동화**
   - 배치 처리
   - 스크립트 생성

---

## 참고 문서

- **구현 계획**: `claudedocs/CSV_Restore_Feature_Plan.md`
- **엣지 케이스 분석**: `claudedocs/CSV_Restore_Edge_Cases_Analysis.md`
- **테스트 파일**: `tests/test_common/`
- **샘플 데이터**: `tests/test_common/sample_data/`
- **실제 파일**: `legacy/.csv test/`

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-26
