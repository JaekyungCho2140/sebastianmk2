# Sebastian PRD - NC/GL 병합 기능

**문서 유형**: Feature
**게임**: 나이트크로우 글로벌 (Nightcrow Global)
**버전**: 0.1.0 (초안)
**작성일**: 2025-12-10

---

## 📋 문서 참조

**공통 요소**: [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md)를 참조하세요.

---

## 🎯 기능 개요

나이트크로우 글로벌 게임의 **8개 언어별 번역 파일을 하나의 통합 Excel 파일로 병합**.

**핵심 특징**:
- **병렬 처리**: QThreadPool로 8개 파일 동시 읽기 → 약 3-4배 속도 향상
- **고속 저장**: xlsxwriter 사용 → openpyxl 대비 5-10배 빠름
- **실시간 검증**: 날짜/마일스톤 입력 시 즉시 유효성 체크

---

## Import 구문
```python
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSignal, QObject, Qt
from queue import Queue
import os
from datetime import datetime
import xlsxwriter
```

## 📥 입력

### 8개 언어별 Excel 파일

**파일 위치**: 사용자가 폴더 선택

**필수 파일 목록**:
```
{선택한 폴더}/
├── StringEnglish.xlsx          (EN)
├── StringTraditionalChinese.xlsx (CT)
├── StringSimplifiedChinese.xlsx  (CS)
├── StringJapanese.xlsx          (JA)
├── StringThai.xlsx              (TH)
├── StringSpanish.xlsx           (ES)
├── StringPortuguese.xlsx        (PT)
└── StringRussian.xlsx           (RU)
```

**각 파일 구조** (공통):
```
Key | Source | Target | Comment | TableName | Status
```

**파일 크기 제한**: [Sebastian-PRD-Shared.md#공통-검증-함수](Sebastian-PRD-Shared.md#공통-검증-함수) 참조 (최대 50MB)

### 사용자 입력

**날짜 (YYMMDD)**:
- 형식: 정확히 6자리 숫자
- 예시: `250512` (2025년 5월 12일)
- 검증: `date.isdigit() and len(date) == 6`

**마일스톤 차수**:
- 형식: 1~3자리 숫자
- 예시: `15` → M15
- 검증: `milestone.isdigit() and len(milestone) <= 3`

---

## 📤 출력

**파일명**: `{YYMMDD}_M{마일스톤}_StringALL.xlsx`
- 예시: `250512_M15_StringALL.xlsx`

**구조** (13개 컬럼):
```
Key | Source | Target_EN | Target_CT | Target_CS | Target_JA |
Target_TH | Target_ES | Target_PT | Target_RU | Comment | TableName | Status
```

**서식**:
- 헤더: 맑은 고딕 12pt Bold, 가운데 정렬, #DAE9F8 배경
- 본문: 맑은 고딕 10pt, 왼쪽 정렬, 텍스트 서식(@)
- 컬럼 너비: 24

### 저장 위치

- **기본 동작**: 입력 파일과 동일한 폴더에 자동 저장
- **저장 위치 선택 UI**: 제공하지 않음
- **파일 덮어쓰기**: 동일 파일명 존재 시 자동으로 `_1`, `_2` 추가 (M4GL과 통일)

---

## ⚙️ 처리 로직

### 1단계: 파일 검증

**필수 파일 존재 확인**:
```python
REQUIRED_FILES = [
    'StringEnglish.xlsx',
    'StringTraditionalChinese.xlsx',
    'StringSimplifiedChinese.xlsx',
    'StringJapanese.xlsx',
    'StringThai.xlsx',
    'StringSpanish.xlsx',
    'StringPortuguese.xlsx',
    'StringRussian.xlsx'
]

missing_files = []
for filename in REQUIRED_FILES:
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        missing_files.append(filename)

if missing_files:
    raise FileValidationError(
        f"필수 파일이 없습니다:\n"
        f"- 누락된 파일: {', '.join(missing_files)}\n"
        f"- 선택한 폴더: {folder_path}\n\n"
        f"8개 필수 파일이 모두 존재하는지 확인하세요."
    )
```

**에러 메시지**: 구체적으로 어떤 파일이 누락되었는지, 어떤 폴더를 선택했는지 표시

### 2단계: 병렬 파일 읽기 (QThreadPool)

**구현 방식** (Round 2 결정):

```python
import pandas as pd
from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSignal, QObject
from queue import Queue
import os

class FileReaderSignals(QObject):
    """파일 읽기 결과 signal"""
    finished = pyqtSignal(str, object)  # (file_path, DataFrame)
    error = pyqtSignal(str, str)        # (file_path, error_message)


class FileReaderRunnable(QRunnable):
    """단일 파일 읽기 작업"""

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.signals = FileReaderSignals()

    def run(self):
        """파일 읽기 실행"""
        try:
            df = pd.read_excel(self.file_path)
            self.signals.finished.emit(self.file_path, df)
        except Exception as e:
            self.signals.error.emit(self.file_path, str(e))


# NCGLMergeWorker에서 사용
class NCGLMergeWorker(BaseWorker):
    def __init__(self, folder_path, date, milestone):
        super().__init__()
        self.folder_path = folder_path
        self.date = date
        self.milestone = milestone

    def run(self):
        try:
            # 파일 순서 명시적 정의 (중요!)
            FILE_ORDER = [
                'StringEnglish.xlsx',
                'StringTraditionalChinese.xlsx',
                'StringSimplifiedChinese.xlsx',
                'StringJapanese.xlsx',
                'StringThai.xlsx',
                'StringSpanish.xlsx',
                'StringPortuguese.xlsx',
                'StringRussian.xlsx'
            ]
            file_paths = [os.path.join(self.folder_path, f) for f in FILE_ORDER]

            # QThreadPool 생성
            thread_pool = QThreadPool()

            # 결과 저장 (thread-safe Queue 사용)
            result_queue = Queue()
            error_queue = Queue()

            # 각 파일마다 Runnable 생성 및 실행
            for file_path in file_paths:
                runnable = FileReaderRunnable(file_path)

                # Signal 연결 (람다 클로저 문제 해결)
                runnable.signals.finished.connect(
                    lambda p, d, fp=file_path: result_queue.put((fp, d))
                )
                runnable.signals.error.connect(
                    lambda p, e, fp=file_path: error_queue.put(f"{fp}: {e}")
                )

                # 스레드 풀에 제출
                thread_pool.start(runnable)

            # 모든 작업 완료 대기
            thread_pool.waitForDone()

            # 에러 확인
            errors = list(error_queue.queue)
            if errors:
                raise ExcelProcessingError("\n".join(errors))

            # 파일 순서 보장 메커니즘
            # 주의: QThreadPool의 병렬 처리는 완료 순서를 보장하지 않습니다.
            #       Queue에서 결과를 꺼낼 때 순서가 뒤섞일 수 있으므로,
            #       딕셔너리에 수집한 후 FILE_ORDER로 재정렬해야 합니다.
            #
            # Claude Code 구현 시: 이 패턴을 반드시 따라야 합니다.
            # 병렬 처리의 성능 이점을 유지하면서도 데이터 순서의 정확성을 보장합니다.
            results = {}
            while not result_queue.empty():
                path, df = result_queue.get()
                results[path] = df

            # FILE_ORDER 순서대로 DataFrame 리스트 생성
            # 이렇게 해야 Target_EN, Target_CT, Target_CS, ... 순서가 보장됨
            dfs = [results[path] for path in file_paths]

            # 이후 병합 로직 계속...

        except Exception as e:
            self.signals.error_occurred.emit(str(e))
```

**수정 사항** (Opus 지적 반영):
1. ✅ **파일 순서 명시적 정의** (FILE_ORDER) - 데이터 뒤섞임 방지
2. ✅ **람다 클로저 문제 해결** - 기본값 캡처 `fp=file_path`
3. ✅ **thread-safe Queue 사용** - race condition 방지
4. ✅ **변수 초기화** - `__init__`에 folder_path, date, milestone

**성능 특징**:
- QThreadPool은 기본적으로 CPU 코어 수만큼 스레드 생성
- 8개 파일, 4코어 CPU → 2번에 나눠서 처리
- 예상 시간: ~2-3초 (레거시 ~1.5초 대비 약간 느림, 허용 범위)

### 3단계: 데이터 병합

**기본 컬럼 추출** (EN 파일에서):
```python
# 첫 번째 파일(English)에서 기본 메타데이터 컬럼 추출
result_df = dfs[0][['Key', 'Source', 'Comment', 'TableName', 'Status']]
```

**언어별 Target 컬럼 병합**:
```python
lang_codes = ['EN', 'CT', 'CS', 'JA', 'TH', 'ES', 'PT', 'RU']

# 각 언어의 Target 컬럼을 Target_EN, Target_JA 등으로 리네임
target_dfs = [
    dfs[i][['Target']].rename(columns={'Target': f'Target_{lang_codes[i]}'})
    for i in range(len(dfs))
]

# 가로 방향(axis=1)으로 병합
result_df = pd.concat([result_df] + target_dfs, axis=1)
```

**최종 컬럼 순서 재정렬**:
```python
result_df = result_df[[
    'Key', 'Source',
    'Target_EN', 'Target_CT', 'Target_CS', 'Target_JA',
    'Target_TH', 'Target_ES', 'Target_PT', 'Target_RU',
    'Comment', 'TableName', 'Status'
]]
```

**레거시 참조**: `Merged_NC.py` 라인 186-208

### 4단계: 데이터 정제

**NaN/inf 처리**:
```python
import numpy as np

# inf 처리만 (NaN은 그대로)
result_df = result_df.replace([np.inf, -np.inf], '', regex=False)

# NaN → 'None' 변환 하지 않음!
# xlsxwriter가 NaN을 빈 셀로 자동 처리
```

**변경 사유** (레거시와 다름):
- Comment 컬럼이 대부분 빈 값
- 'None' 문자열 표시 시 사용자 혼동
- Excel에서 빈 셀이 더 자연스러움
- xlsxwriter가 NaN을 빈 문자열로 자동 변환

**레거시와의 차이**:
- **레거시**: Comment 제외, NaN → 'None' 변환
- **Sebastian**: 모든 컬럼 NaN 그대로 (xlsxwriter 처리 위임)

### 5단계: xlsxwriter 저장

**출력 파일 생성**:
```python
output_file = f"{date}_M{milestone}_StringALL.xlsx"
output_path = os.path.join(folder_path, output_file)

workbook = xlsxwriter.Workbook(output_path)
worksheet = workbook.add_worksheet('Sheet1')
```

**서식 정의**:
```python
# 헤더 서식 (가운데 정렬, 파란 배경)
header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'vcenter',
    'align': 'center',
    'fg_color': '#DAE9F8',
    'font_name': '맑은 고딕',
    'font_size': 10,
    'border': 1
})

# 데이터 셀 서식 (왼쪽 정렬, 텍스트 서식)
cell_format = workbook.add_format({
    'font_name': '맑은 고딕',
    'font_size': 10,
    'align': 'left',
    'valign': 'vcenter',
    'num_format': '@'  # 텍스트 서식 (숫자 자동 변환 방지)
})
```

**헤더 행 작성**:
```python
for col_num, value in enumerate(result_df.columns.values):
    worksheet.write(0, col_num, value, header_format)
    worksheet.set_column(col_num, col_num, 24, cell_format)  # 컬럼 너비 24
```

**데이터 행 작성** (셀별, NaN 처리):
```python
import pandas as pd

for row_num in range(len(result_df)):
    for col_num in range(len(result_df.columns)):
        value = result_df.iloc[row_num, col_num]

        # NaN 처리 (빈 셀로)
        if pd.isna(value):
            worksheet.write_blank(row_num + 1, col_num, None, cell_format)
        else:
            # 텍스트 강제 (숫자 자동 변환 방지)
            worksheet.write_string(row_num + 1, col_num, str(value), cell_format)
```

**중요**: `str(NaN)` = `'nan'` 문자열이 되므로, **반드시 pd.isna() 체크** 후 write_blank 사용

**파일 닫기**:
```python
workbook.close()
```

**레거시 참조**: `Merged_NC.py` 라인 221-253

**선택**: 셀별 write_string (레거시 동작 유지)
- 장점: 텍스트 서식 확실히 적용
- 단점: 행 단위 write_row보다 느림 (하지만 xlsxwriter 자체가 빨라서 문제 없음)
- 성능: 개발 완료 후 실제 측정하여 성능 목표(<5초) 충족 여부 확인

---

## 🎨 UI 설계

**상세 UI 와이어프레임**: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md#-ncgl-탭-ui)

### 개요

**레이아웃**: 실시간 검증 입력 필드 (날짜, 마일스톤) + 폴더 선택 + 실행 버튼

**핵심 기능**: 입력 중 실시간 유효성 검증 및 시각적 피드백 (✓/✗)

**동작 흐름**:
1. 사용자: 날짜 입력 (YYMMDD, 6자리) → 실시간 검증 → ✓/✗ 표시
2. 사용자: 마일스톤 입력 (1-3자리 숫자) → 실시간 검증 → ✓/✗ 표시
3. 사용자: [폴더 선택] → 8개 필수 파일 확인
4. 모든 입력 유효 → [실행] 버튼 활성화
5. [실행] 클릭 → NCGLMergeWorker 실행 + ProgressDialog 표시

**구현 참조**:
- 입력 필드 스타일: [Sebastian-UI-Wireframes.md#입력-필드-스타일](Sebastian-UI-Wireframes.md#입력-필드-스타일)
- 검증 아이콘: [Sebastian-UI-Wireframes.md#검증-아이콘-영역](Sebastian-UI-Wireframes.md#검증-아이콘-영역)
- 실행 버튼: [Sebastian-UI-Wireframes.md#실행-버튼-1](Sebastian-UI-Wireframes.md#실행-버튼-1)
- ProgressDialog: [Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog](Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog)

---

## ⚠️ 특이사항

1. **NaN 처리**: 모든 컬럼 NaN 그대로 유지 (xlsxwriter가 빈 셀 처리)
2. **텍스트 서식 강제**: `num_format: '@'` → 자동 형식 추론 생략
3. **레거시와 차이**: Comment만 아닌 전체 NaN 허용 (더 자연스러움)

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 0.1.0 | 2025-12-10 | 초안 작성 | 재경 |
| 0.1.1 | 2025-12-11 | 병렬 읽기 순서 보장 로직 주석 보강 (Claude Code 대상 명시) | 재경 |
| 0.2.0 | 2025-12-11 | 파일 검증 에러 메시지 구체화 (누락 파일 목록 표시) | 재경 |
| 0.3.0 | 2025-12-11 | 날짜 검증 미래 날짜 허용 명시, xlsxwriter 성능 측정 계획 추가 | 재경 |
| 0.4.0 | 2025-12-11 | 검수 반영: 저장 위치 설정 명시 (입력 폴더 자동 저장, 덮어쓰기 규칙), 파일 크기 제한 참조 추가 | 재경 |
| 0.5.0 | 2025-12-12 | UI 설계 섹션 와이어프레임 참조로 변경, 구현 코드 제거 | 재경 |
