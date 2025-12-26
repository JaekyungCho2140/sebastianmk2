# Sebastian PRD - NC/GL (NC Global)

**게임**: NC Global
**기능**: 8개 언어 병합
**버전**: v0.1.1
**상태**: Production

---

## 목차

1. [개요](#개요)
2. [기능 명세](#기능-명세)
3. [UI 디자인](#ui-디자인)
4. [병렬 처리](#병렬-처리)
5. [구현 세부사항](#구현-세부사항)

---

## 개요

### 목적

NC Global 게임의 현지화 테이블을 병합하는 기능입니다.

- **8개 언어 파일 → 1개 통합 파일**
- **병렬 처리**로 성능 최적화 (ProcessPoolExecutor)
- **xlsxwriter** 기반 고속 저장

### 입력/출력

**입력**:
- 폴더 경로 (8개 언어 파일이 위치한 폴더)
- 날짜 (YYMMDD 형식, 6자리)
- 마일스톤 차수 (1-3자리 숫자)

**출력**:
- `{date}_M{milestone}_StringALL.xlsx`
- 예: `250512_M15_StringALL.xlsx`

---

## 기능 명세

### 입력 파일 (8개)

| 파일명 | 언어 | 언어 코드 |
|--------|------|-----------|
| `StringEnglish.xlsx` | English | EN |
| `StringTraditionalChinese.xlsx` | Traditional Chinese | CT |
| `StringSimplifiedChinese.xlsx` | Simplified Chinese | CS |
| `StringJapanese.xlsx` | Japanese | JA |
| `StringThai.xlsx` | Thai | TH |
| `StringSpanish.xlsx` | Spanish (Latin America) | ES |
| `StringPortuguese.xlsx` | Portuguese (Brazil) | PT |
| `StringRussian.xlsx` | Russian | RU |

**파일 구조** (모든 파일 동일):
- Sheet: Sheet1 (기본)
- 헤더: Key, Source, Target, Comment, TableName, Status

### 출력 파일

**컬럼 구조** (13개 컬럼):

| # | 컬럼명 | 설명 | 데이터 소스 |
|---|--------|------|-------------|
| 1 | Key | 문자열 KEY | 첫 번째 파일 (EN) |
| 2 | Source | 원문 (한국어) | 첫 번째 파일 (EN) |
| 3-10 | Target_EN, Target_CT, ..., Target_RU | 언어별 번역문 | 각 언어 파일의 Target 컬럼 |
| 11 | Comment | 코멘트 | 첫 번째 파일 (EN) |
| 12 | TableName | 테이블 이름 | 첫 번째 파일 (EN) |
| 13 | Status | 상태 | 첫 번째 파일 (EN) |

**컬럼 순서**:
```
Key, Source, Target_EN, Target_CT, Target_CS, Target_JA, Target_TH,
Target_ES, Target_PT, Target_RU, Comment, TableName, Status
```

### 병합 알고리즘

```
1. 입력 검증
   - 날짜: 6자리 숫자 (YYMMDD)
   - 마일스톤: 1-3자리 숫자
   - 폴더 경로: 8개 파일 모두 존재 확인

2. 병렬 파일 읽기 (ProcessPoolExecutor)
   - 8개 파일 동시 읽기
   - pandas.read_excel() 사용
   - 약 3배 속도 향상

3. DataFrame 병합
   - EN 파일의 Key, Source, Comment, TableName, Status 컬럼
   - 각 언어 파일의 Target 컬럼 → Target_{언어코드}로 rename
   - pandas.concat()으로 수평 병합

4. 데이터 정규화
   - NaN, inf, -inf → 빈 문자열
   - pandas.isna() → 'None' 문자열
   - Comment 컬럼은 예외 (None 유지)

5. xlsxwriter로 저장
   - 셀 서식: 맑은 고딕 10pt, 텍스트 형식
   - 헤더 서식: Bold, 가운데 정렬, 연한 파란색 배경
   - 컬럼 너비 자동 조정
   - 행 높이: 25px

6. 진행 상황 업데이트
   - 각 파일 읽기: 12.5% × 8 = 100%
   - 병합: +10%
   - 저장: +10%
```

### Excel 서식 (xlsxwriter)

**헤더 서식**:
```python
header_format = {
    'bold': True,
    'text_wrap': True,
    'valign': 'vcenter',
    'align': 'center',
    'fg_color': '#DAE9F8',
    'font_name': '맑은 고딕',
    'font_size': 10,
    'border': 1
}
```

**셀 서식**:
```python
cell_format = {
    'font_name': '맑은 고딕',
    'font_size': 10,
    'align': 'left',
    'valign': 'vcenter',
    'num_format': '@',  # 텍스트 형식
    'border': 1
}
```

**컬럼 너비**:
- Key: 15
- Source, Target_*: 30
- Comment: 20
- TableName: 15
- Status: 10

---

## UI 디자인

### NC/GL 탭 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│    날짜 (YYMMDD)                                        │
│    ┌──────────────────────────────┐  [✓]              │
│    │  250512                      │                    │
│    └──────────────────────────────┘                    │
│    6자리 숫자 (예: 250512)                             │
│                                                         │
│    마일스톤 차수                                        │
│    ┌──────────────────────────────┐  [✓]              │
│    │  15                          │                    │
│    └──────────────────────────────┘                    │
│    1-3자리 숫자 (예: 15 → M15)                         │
│                                                         │
│    선택한 폴더                                          │
│    ┌──────────────────────────────┐  ┌─────────┐      │
│    │  (경로 표시)                 │  │ 폴더    │      │
│    └──────────────────────────────┘  │ 선택    │      │
│                                      └─────────┘      │
│                                                         │
│                              ┌───────────────┐         │
│                              │ 실행 (Enter) │         │
│                              └───────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 입력 필드 (실시간 검증)

**날짜 입력**:
- Placeholder: "250512"
- MaxLength: 6
- 검증: 6자리 숫자
- 유효: 초록색 체크 (✓)
- 무효: 빨간색 X (✗)

**마일스톤 입력**:
- Placeholder: "15"
- MaxLength: 3
- 검증: 1-3자리 숫자
- 유효: 초록색 체크 (✓)
- 무효: 빨간색 X (✗)

**검증 아이콘 스타일**:

유효 상태:
```python
icon_label.setText("✓")
icon_label.setStyleSheet(f"""
    background-color: {BG_SECONDARY};
    color: {SUCCESS};  # #10B981
    font-size: 24px;
""")
```

무효 상태:
```python
icon_label.setText("✗")
icon_label.setStyleSheet(f"""
    background-color: {BG_SECONDARY};
    color: {ERROR};  # #EF4444
    font-size: 24px;
""")
```

**입력 필드 테두리 색상**:
- 기본: `#E5E7EB`
- 유효: `#10B981` (초록색)
- 무효: `#EF4444` (빨간색)

### 실행 버튼

**활성화 조건**:
- 날짜: 6자리 숫자
- 마일스톤: 1-3자리 숫자
- 폴더 경로: 선택됨

**비활성 상태**:
- Background: `#F3F4F6`
- Text Color: `#9CA3AF`

---

## 병렬 처리

### ProcessPoolExecutor

**목적**: 8개 파일을 동시에 읽어 속도 향상

**구현**:

```python
from concurrent.futures import ProcessPoolExecutor

def read_excel_file(file_path):
    import pandas as pd
    return pd.read_excel(file_path)

def merge_ncgl(folder_path: str, date: str, milestone: str, progress_queue):
    file_names = [
        "StringEnglish.xlsx",
        "StringTraditionalChinese.xlsx",
        # ...
    ]

    dfs = []
    with ProcessPoolExecutor() as executor:
        file_paths = [os.path.join(folder_path, f) for f in file_names]
        results = list(executor.map(read_excel_file, file_paths))
        dfs.extend(results)

        for idx, file_name in enumerate(file_names):
            progress_queue.put(f"파일:{file_name}")
            progress_queue.put(int((idx + 1) / len(file_names) * 80))
```

**성능**:
- 순차 처리: ~24초 (8개 × 3초)
- 병렬 처리: ~8초 (약 3배 향상)

### 주의사항

**Worker 함수는 글로벌로 정의**:
- ProcessPoolExecutor는 pickle 직렬화 사용
- 로컬 함수나 lambda는 사용 불가
- `read_excel_file()`을 모듈 레벨에 정의

---

## 구현 세부사항

### Core 로직

**파일 경로**: `sebastian/core/ncgl/merger.py`

**함수 시그니처**:

```python
def merge_ncgl(
    folder_path: str,
    date: str,
    milestone: str,
    progress_queue: queue.Queue
) -> None:
    """
    NC/GL 8개 언어 파일 병합

    Args:
        folder_path: 폴더 경로
        date: 날짜 (YYMMDD, 6자리)
        milestone: 마일스톤 차수 (1-3자리)
        progress_queue: 진행 상황 Queue

    Raises:
        FileNotFoundError: 파일 미존재 시
        ValidationError: 데이터 검증 실패 시
        IOError: 파일 읽기/쓰기 실패 시
    """
    pass
```

### Worker

**파일 경로**: `sebastian/workers/ncgl_worker.py`

**Signals**:

```python
class NCGLWorker(QThread):
    progress_updated = pyqtSignal(int)         # 0-100 진행률
    step_updated = pyqtSignal(str)             # 단계 정보
    file_updated = pyqtSignal(str)             # 처리 중인 파일명
    files_count_updated = pyqtSignal(int)      # 처리된 파일 수
    completed = pyqtSignal(str)                # 완료 메시지
    error_occurred = pyqtSignal(str)           # 에러 메시지
```

### UI 탭

**파일 경로**: `sebastian/ui/ncgl_tab.py`

**실시간 검증**:

```python
def _validate_date(self, text: str):
    """날짜 검증 (6자리 숫자)"""
    is_valid = text.isdigit() and len(text) == 6
    self._update_validation_icon(self.date_icon, is_valid)
    self._update_input_style(self.date_input, is_valid if text else None)
    self._check_execute_enabled()

def _validate_milestone(self, text: str):
    """마일스톤 검증 (1-3자리 숫자)"""
    is_valid = text.isdigit() and 1 <= len(text) <= 3
    self._update_validation_icon(self.milestone_icon, is_valid)
    self._update_input_style(self.milestone_input, is_valid if text else None)
    self._check_execute_enabled()
```

---

## 테스트

### 검증 항목

1. **입력 검증**
   - 날짜: 6자리 숫자 정확히 입력
   - 마일스톤: 1-3자리 숫자
   - 실시간 검증 아이콘 정확히 표시

2. **파일 존재 확인**
   - 8개 파일 모두 존재
   - FileNotFoundError 처리

3. **병렬 읽기**
   - ProcessPoolExecutor 정상 동작
   - 8개 DataFrame 생성

4. **DataFrame 병합**
   - 컬럼 순서 정확
   - Target_{언어코드} rename 정확

5. **Excel 저장**
   - 파일명: {date}_M{milestone}_StringALL.xlsx
   - xlsxwriter 서식 정확히 적용

6. **레거시 출력 비교**
   - 레거시 스크립트 출력과 100% 일치

### 테스트 데이터

**위치**: `legacy/NC/` (레거시 스크립트 및 샘플 데이터)

**실행**:
```bash
# 레거시 스크립트
python legacy/NC/NC 파일 통합.py

# Sebastian
python sebastian/main.py
# → NC/GL 탭 → 날짜/마일스톤 입력 → 실행

# 출력 비교
diff 250512_M15_StringALL.xlsx legacy_output/250512_M15_StringALL.xlsx
```

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-12-24
