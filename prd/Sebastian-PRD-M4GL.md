# Sebastian PRD - M4/GL 병합 기능

**문서 유형**: Feature
**게임**: 미르4 글로벌 (MIR4 Global)
**버전**: 0.1.0 (초안)
**작성일**: 2025-12-10

---

## 📋 문서 참조

**공통 요소**: [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md)를 참조하세요.
- 기술 스택
- 공통 UI 컴포넌트 (ProgressDialog, FileSelectionDialog 등)
- 공통 데이터 구조
- 용어집

---

## 🎯 기능 개요

미르4 글로벌 게임의 인게임 현지화 테이블 병합 기능. **2가지 독립적인 병합 작업**을 수행합니다:

1. **DIALOGUE 병합**: 캐릭터 대화 데이터 통합 (3개 파일 → 1개)
2. **STRING 병합**: UI 문자열 데이터 통합 (8개 파일 → 1개)

---

## 🔀 DIALOGUE 병합

### Import 구문
```python
import pandas as pd
import os
import stat
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side
import logging
```

### 입력

**3개의 Excel 파일** (사용자가 폴더 선택):
```
{선택한 폴더}/
├── CINEMATIC_DIALOGUE.xlsm   # 시네마틱(컷씬) 대화
├── SMALLTALK_DIALOGUE.xlsm    # 일반 대화
└── NPC.xlsm                   # NPC 정보 (매핑용)
```

**파일 구조**:
- CINEMATIC_DIALOGUE: 시트2, 헤더 2행, 데이터 10행부터
- SMALLTALK_DIALOGUE: 시트2, 헤더 2행, 데이터 5행부터
- NPC: 'NPC' 시트, 헤더 2행

**파일 크기 제한**: [Sebastian-PRD-Shared.md#공통-검증-함수](Sebastian-PRD-Shared.md#공통-검증-함수) 참조 (최대 50MB)

### 출력

**파일명**: `{MMDD}_MIR4_MASTER_DIALOGUE.xlsx`
- 예시: `1210_MIR4_MASTER_DIALOGUE.xlsx` (12월 10일)
- 중복 시: `{MMDD}_MIR4_MASTER_DIALOGUE_{N}.xlsx` (N은 1부터 시작: _1, _2, _3...)

**파일명 중복 처리** (레거시 동작):
```python
output_file = f'{mmdd}_MIR4_MASTER_DIALOGUE.xlsx'
counter = 1
while os.path.exists(output_file):
    output_file = f'{mmdd}_MIR4_MASTER_DIALOGUE_{counter}.xlsx'
    counter += 1
```

**구조** (23개 컬럼):
```
# | Table Name | String ID | Table/ID | NPC ID | Speaker Name |
KO (M) | KO (F) | EN (M) | EN (F) | CT (M) | CT (F) | ... | NOTE
```

**특징**:
- 읽기 전용으로 저장
- 서식 지정: 헤더(맑은 고딕 12pt Bold, #FFEB9C 배경), 본문(맑은 고딕 10pt)
- 틀 고정: 1행

### 처리 로직

#### 1단계: 파일 읽기

**CINEMATIC_DIALOGUE.xlsm**:
```python
cinematic_data = pd.read_excel(
    cinematic_path,
    sheet_name=1,      # 시트 인덱스 1 (0부터 시작, 두 번째 시트)
    header=1,          # 헤더 행 인덱스 1 (0부터 시작, 2번째 행)
    skiprows=range(9)  # 0~8행 건너뛰기 (9행부터 데이터)
)
```

**SMALLTALK_DIALOGUE.xlsm**:
```python
smalltalk_data = pd.read_excel(
    smalltalk_path,
    sheet_name=1,
    header=1,
    skiprows=range(4)  # 0~3행 건너뛰기 (4행부터 데이터)
)
```

**NPC.xlsm**:
```python
npc_data = pd.read_excel(
    npc_path,
    sheet_name='NPC',  # 시트명 'NPC'
    header=1           # 헤더 행 인덱스 1 (2번째 행)
)
# 중복 제거: H열(인덱스 7) 기준
npc_data = npc_data.drop_duplicates(subset=npc_data.columns[7], keep='first')
```

#### 2단계: 언어 컬럼 매핑

**매핑 규칙** (레거시 `language_mapping` 딕셔너리):

| 결과 컬럼 | CINEMATIC 열 | SMALLTALK 열 |
|-----------|--------------|--------------|
| String ID | 8열 (인덱스 7) | 8열 (인덱스 7) |
| NPC ID | 9열 (인덱스 8) | 9열 (인덱스 8) |
| KO (M) | 12열 (인덱스 11) | 13열 (인덱스 12) |
| KO (F) | 13열 (인덱스 12) | 14열 (인덱스 13) |
| EN (M) | 14열 (인덱스 13) | 15열 (인덱스 14) |
| EN (F) | 15열 (인덱스 14) | 16열 (인덱스 15) |
| CT (M) | 16열 (인덱스 15) | 17열 (인덱스 16) |
| CT (F) | 17열 (인덱스 16) | 18열 (인덱스 17) |
| CS (M) | 18열 (인덱스 17) | 19열 (인덱스 18) |
| CS (F) | 19열 (인덱스 18) | 20열 (인덱스 19) |
| JA (M) | 20열 (인덱스 19) | 21열 (인덱스 20) |
| JA (F) | 21열 (인덱스 20) | 22열 (인덱스 21) |
| TH (M) | 22열 (인덱스 21) | 23열 (인덱스 22) |
| TH (F) | 23열 (인덱스 22) | 24열 (인덱스 23) |
| ES-LATAM (M) | 24열 (인덱스 23) | 25열 (인덱스 24) |
| ES-LATAM (F) | 25열 (인덱스 24) | 26열 (인덱스 25) |
| PT-BR (M) | 26열 (인덱스 25) | 27열 (인덱스 26) |
| PT-BR (F) | 27열 (인덱스 26) | 28열 (인덱스 27) |
| NOTE | 30열 (인덱스 29) | 31열 (인덱스 30) |

**구현 방식**: 위 매핑을 코드에 딕셔너리로 하드코딩

```python
language_mapping = {
    'KO (M)': (11, 12),
    'KO (F)': (12, 13),
    'EN (M)': (13, 14),
    'EN (F)': (14, 15),
    'CT (M)': (15, 16),
    'CT (F)': (16, 17),
    'CS (M)': (17, 18),
    'CS (F)': (18, 19),
    'JA (M)': (19, 20),
    'JA (F)': (20, 21),
    'TH (M)': (21, 22),
    'TH (F)': (22, 23),
    'ES-LATAM (M)': (23, 24),
    'ES-LATAM (F)': (24, 25),
    'PT-BR (M)': (25, 26),
    'PT-BR (F)': (26, 27),
    'NOTE': (29, 30)
}
```

**language_mapping 사용하여 데이터 병합**:
```python
# 결과 DataFrame 생성
total_rows = len(cinematic_data) + len(smalltalk_data)
result_df = pd.DataFrame(index=range(total_rows), columns=headers)

# 변수 정의 (열 개수, 행 개수)
cinematic_cols = len(cinematic_data.columns)
smalltalk_cols = len(smalltalk_data.columns)
cin_len = len(cinematic_data)
small_len = len(smalltalk_data)

# 기본 컬럼 채우기
result_df['#'] = range(1, total_rows + 1)
result_df.loc[:cin_len-1, 'Table Name'] = 'CINEMATIC_DIALOGUE'
result_df.loc[cin_len:, 'Table Name'] = 'SMALLTALK_DIALOGUE'

# String ID, NPC ID 채우기
if 7 < cinematic_cols:
    result_df.loc[:cin_len-1, 'String ID'] = cinematic_data.iloc[:, 7].values
if 7 < smalltalk_cols:
    result_df.loc[cin_len:, 'String ID'] = smalltalk_data.iloc[:, 7].values

if 8 < cinematic_cols:
    result_df.loc[:cin_len-1, 'NPC ID'] = cinematic_data.iloc[:, 8].values
if 8 < smalltalk_cols:
    result_df.loc[cin_len:, 'NPC ID'] = smalltalk_data.iloc[:, 8].values

# Table/ID 생성 (필터링 전에 생성 - 레거시 동작)
# 주의: String ID가 NaN이면 .astype(str)이 'nan' 문자열로 변환됨
# 하지만 필터링 단계에서 EN (M) 기준으로 제거되므로 문제 없음
result_df['Table/ID'] = result_df['Table Name'] + '/' + result_df['String ID'].astype(str)

# language_mapping 사용하여 언어 데이터 채우기
for col_name, (cin_idx, small_idx) in language_mapping.items():
    # CINEMATIC 데이터 채우기
    if cin_idx < cinematic_cols:
        result_df.loc[:cin_len-1, col_name] = cinematic_data.iloc[:, cin_idx].values

    # SMALLTALK 데이터 채우기
    if small_idx < smalltalk_cols:
        result_df.loc[cin_len:, col_name] = smalltalk_data.iloc[:, small_idx].values
```

**레거시 참조**: `Merged_M4.py` 라인 120-178

#### 3단계: NPC 이름 매핑

**NPC.xlsm 구조**:
- H열 (인덱스 7): NPC ID (유니크 키)
- J열 (인덱스 9): NPC 이름 (표시명)

**매핑 로직**:
```python
# 1. NPC 데이터 중복 제거
npc_data = npc_data.drop_duplicates(subset=npc_data.columns[7])

# 2. Dictionary 매핑 생성
npc_map = dict(zip(
    npc_data.iloc[:, 7],  # H열: NPC ID
    npc_data.iloc[:, 9]   # J열: NPC 이름
))

# 3. Speaker Name 매핑 (매핑 실패 시 NPC ID 유지)
result_df['Speaker Name'] = result_df['NPC ID'].map(npc_map).fillna(result_df['NPC ID'])
```

**에러 처리**:
```python
import logging

# 로거 설정
logger = logging.getLogger(__name__)

try:
    npc_map = dict(zip(...))
    result_df['Speaker Name'] = ...

    # 매핑 실패 로깅 (조용히 처리)
    failed_mappings = result_df[result_df['Speaker Name'] == result_df['NPC ID']]
    if len(failed_mappings) > 0:
        logger.warning(f"NPC 매핑 실패: {len(failed_mappings)}개 행")
        logger.debug(f"실패한 NPC ID: {failed_mappings['NPC ID'].unique()}")
    # 사용자 알림 없음 (로그만)

except Exception as e:
    raise ExcelProcessingError(f"NPC 이름 매핑 중 오류 발생: {str(e)}")
```

**매핑 실패 처리**:
- **일부 매핑 실패** (fillna): NPC ID 유지 (조용히 처리)
  - fillna로 매핑되지 않은 NPC ID는 원래 값 유지
  - 로그 파일에만 기록, 사용자 알림 없음
- **심각한 오류** (Exception): 에러 메시지 표시 및 작업 중단
  - NPC.xlsm 파일을 읽을 수 없을 때
  - 딕셔너리 생성 중 오류 발생 시
  - 구현:
    ```python
    try:
        npc_map = dict(zip(...))
        result_df['Speaker Name'] = result_df['NPC ID'].map(npc_map).fillna(result_df['NPC ID'])
    except Exception as e:
        raise ExcelProcessingError(f"NPC 이름 매핑 중 오류 발생: {str(e)}")
    ```

**레거시 동작**: Exception 발생 시 에러 표시 및 작업 중단 (레거시 유지)

#### 4단계: 필터링

**제거 조건** (EN (M) 컬럼 기준):
```python
# 다음 행 제거
# 1. EN (M) 컬럼이 NaN (빈 셀)
# 2. EN (M) 컬럼이 0 (정수)
# 3. EN (M) 컬럼이 '미사용' (문자열)

# pandas 구현
result_df = result_df[~(
    pd.isna(result_df['EN (M)']) |
    result_df['EN (M)'].isin([0, '미사용'])
)]
```

**참고**: 0은 정수형, '미사용'은 문자열

#### 5단계: 인덱스 재생성 및 저장

```python
# '#' 컬럼을 1부터 자동 증가
result_df['#'] = range(1, len(result_df) + 1)

# Excel 저장 및 서식 지정
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side
import stat

# DataFrame을 Excel로 저장
result_df.to_excel(output_file, index=False)

# 서식 지정
wb = load_workbook(output_file)
ws = wb.active

# 폰트 및 서식 설정
header_font = Font(name='맑은 고딕', size=12, bold=True, color='9C5700')
default_font = Font(name='맑은 고딕', size=10)
header_fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
border_style = Side(border_style='thin', color='000000')
full_border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)

# 헤더 행 서식 (1행)
for cell in ws[1]:
    cell.font = header_font
    cell.fill = header_fill
    cell.border = full_border

# 데이터 행 서식 (2행부터)
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.font = default_font
        cell.border = full_border

# 틀 고정 (1행)
ws.freeze_panes = 'A2'

# 저장 및 읽기 전용 설정
wb.save(output_file)
os.chmod(output_file, stat.S_IREAD)
```

**레거시 참조**: `Merged_M4.py` 라인 227-256

### 에러 처리

**파일 존재 확인**:
```python
missing_files = []
for path in [cinematic_path, smalltalk_path, npc_path]:
    if not os.path.isfile(path):
        missing_files.append(f"파일을 찾을 수 없습니다: {path}")
if missing_files:
    raise FileNotFoundError("\n".join(missing_files))
```

---

## 📝 STRING 병합

### 입력

**8개의 Excel 파일** (사용자가 폴더 선택):
```
{선택한 폴더}/
├── SEQUENCE_DIALOGUE.xlsm
├── STRING_BUILTIN.xlsm
├── STRING_MAIL.xlsm
├── STRING_MESSAGE.xlsm
├── STRING_NPC.xlsm
├── STRING_QUESTTEMPLATE.xlsm
├── STRING_TEMPLATE.xlsm
└── STRING_TOOLTIP.xlsm
```

### 출력

**파일명**: `{MMDD}_MIR4_MASTER_STRING.xlsx`
- 예시: `1210_MIR4_MASTER_STRING.xlsx`
- 중복 시: `{MMDD}_MIR4_MASTER_STRING_{N}.xlsx` (N은 1부터 시작: _1, _2, _3...)

**파일명 중복 처리** (DIALOGUE와 동일):
```python
output_file = f'{mmdd}_MIR4_MASTER_STRING.xlsx'
counter = 1
while os.path.exists(output_file):
    output_file = f'{mmdd}_MIR4_MASTER_STRING_{counter}.xlsx'
    counter += 1
```

**구조** (15개 컬럼):
```
# | Table Name | String ID | Table/ID | NOTE |
KO | EN | CT | CS | JA | TH | ES-LATAM | PT-BR |
NPC 이름 | 비고
```

### 처리 로직

#### 1단계: 파일별 헤더/시작 행 설정

**헤더 행** (모든 파일 공통):
```python
header_rows = {
    "SEQUENCE_DIALOGUE.xlsm": 2,
    "STRING_BUILTIN.xlsm": 2,
    "STRING_MAIL.xlsm": 2,
    "STRING_MESSAGE.xlsm": 2,
    "STRING_NPC.xlsm": 2,
    "STRING_QUESTTEMPLATE.xlsm": 2,
    "STRING_TEMPLATE.xlsm": 2,
    "STRING_TOOLTIP.xlsm": 2
}
```

**참고**: 모든 파일의 헤더가 2번째 행이지만, 헤더 위의 메타데이터 행 수는 파일마다 다릅니다.
이로 인해 데이터 시작 행이 파일마다 다릅니다 (4행, 7행, 9행 등).

**데이터 시작 행**:
```python
start_rows = {
    "SEQUENCE_DIALOGUE.xlsm": 9,      # 10행부터 데이터
    "STRING_QUESTTEMPLATE.xlsm": 7,   # 8행부터 데이터
    "STRING_BUILTIN.xlsm": 4,         # 5행부터 데이터
    "STRING_MAIL.xlsm": 4,
    "STRING_MESSAGE.xlsm": 4,
    "STRING_NPC.xlsm": 4,
    "STRING_TEMPLATE.xlsm": 4,
    "STRING_TOOLTIP.xlsm": 4
}
```

#### 2단계: 파일별 열 매핑

**매핑 규칙** (레거시 `matching_columns`):

각 리스트는 결과 컬럼 순서를 의미합니다: `[String ID, NOTE, KO, EN, CT, CS, JA, TH, ES-LATAM, PT-BR, NPC이름, 비고]`

`None` = 해당 컬럼 없음 (빈 값으로 채움)

| 파일명 | String ID | NOTE | KO | EN | CT | CS | JA | TH | ES | PT | NPC이름 | 비고 |
|--------|-----------|------|----|----|----|----|----|----|----|----|---------|------|
| SEQUENCE_DIALOGUE | 7 | - | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | - | - |
| STRING_BUILTIN | 7 | 21 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | - | - |
| STRING_MAIL | 7 | - | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | - | - |
| STRING_MESSAGE | 7 | 21 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | - | - |
| STRING_NPC | 7 | 20 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 18 | 19 |
| STRING_QUESTTEMPLATE | 7 | 0 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | - | - |
| STRING_TEMPLATE | 7 | 19 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | - | 18 |
| STRING_TOOLTIP | 7 | 8 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | - | - |

**구현 방식**: 위 매핑을 코드에 딕셔너리로 하드코딩

```python
matching_columns = {
    "SEQUENCE_DIALOGUE.xlsm": [7, None, 10, 11, 12, 13, 14, 15, 16, 17, None, None],
    "STRING_BUILTIN.xlsm": [7, 21, 8, 9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_MAIL.xlsm": [7, None, 8, 9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_MESSAGE.xlsm": [7, 21, 8, 9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_NPC.xlsm": [7, 20, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19],
    "STRING_QUESTTEMPLATE.xlsm": [7, 0, 12, 13, 14, 15, 16, 17, 18, 19, None, None],
    "STRING_TEMPLATE.xlsm": [7, 19, 8, 9, 10, 11, 12, 13, 14, 15, None, 18],
    "STRING_TOOLTIP.xlsm": [7, 8, 11, 12, 13, 14, 15, 16, 17, 18, None, None]
}
```

#### 3단계: 데이터 병합

**각 파일 순회하며 DataFrame 생성**:
```python
for file in file_list:
    data = read_excel_file(file_path, sheet_name=1,
                          header_row=header_rows[file],
                          skip_rows=start_rows[file])

    # matching_columns 규칙에 따라 temp_df 생성
    temp_df = pd.DataFrame({
        'Table Name': file.replace(".xlsm", ""),
        'String ID': data.iloc[:, matching_columns[file][0]] if matching_columns[file][0] is not None else '',
        'NOTE': data.iloc[:, matching_columns[file][1]] if matching_columns[file][1] is not None else '',
        'KO': data.iloc[:, matching_columns[file][2]] if matching_columns[file][2] is not None else '',
        'EN': data.iloc[:, matching_columns[file][3]] if matching_columns[file][3] is not None else '',
        'CT': data.iloc[:, matching_columns[file][4]] if matching_columns[file][4] is not None else '',
        'CS': data.iloc[:, matching_columns[file][5]] if matching_columns[file][5] is not None else '',
        'JA': data.iloc[:, matching_columns[file][6]] if matching_columns[file][6] is not None else '',
        'TH': data.iloc[:, matching_columns[file][7]] if matching_columns[file][7] is not None else '',
        'ES-LATAM': data.iloc[:, matching_columns[file][8]] if matching_columns[file][8] is not None else '',
        'PT-BR': data.iloc[:, matching_columns[file][9]] if matching_columns[file][9] is not None else '',
        'NPC 이름': data.iloc[:, matching_columns[file][10]] if matching_columns[file][10] is not None else '',
        '비고': data.iloc[:, matching_columns[file][11]] if matching_columns[file][11] is not None else ''
    })

    result_df = pd.concat([result_df, temp_df], ignore_index=True)
```

#### 4단계: 필터링

**제거 조건** (EN 컬럼, 7번째 컬럼 인덱스 6 기준):
```python
# 다음 행 제거
1. EN 컬럼이 NaN (빈 셀)
2. EN 컬럼이 0
3. EN 컬럼이 '미사용'

# pandas 구현
result_df = result_df[~(
    pd.isna(result_df.iloc[:, 6]) |
    result_df.iloc[:, 6].isin([0, '미사용'])
)]
```

#### 5단계: 인덱스 재생성 및 저장

```python
# '#' 컬럼을 1부터 자동 증가
result_df['#'] = range(1, len(result_df) + 1)

# Excel 저장 (서식 지정)
# 읽기 전용 설정
os.chmod(output_file, stat.S_IREAD)
```

---

## 🎨 UI 설계

**상세 UI 와이어프레임**: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md#-m4gl-탭-ui)

### 개요

**레이아웃**: 2개 큰 버튼 (DIALOGUE, STRING) + 폴더 선택 + 실행 버튼

**동작 흐름**:
1. 사용자: DIALOGUE 또는 STRING 버튼 클릭 → 선택 표시
2. [폴더 선택] 버튼 활성화 → QFileDialog로 폴더 선택
3. 폴더 경로 표시, [실행] 버튼 활성화
4. [실행] 클릭 → 해당 워커 실행 + ProgressDialog 표시

**구현 참조**:
- 버튼 스타일 및 색상: [Sebastian-UI-Wireframes.md#기능-버튼-스타일](Sebastian-UI-Wireframes.md#기능-버튼-스타일)
- 폴더 선택 UI: [Sebastian-UI-Wireframes.md#폴더-선택-ui](Sebastian-UI-Wireframes.md#폴더-선택-ui)
- 실행 버튼: [Sebastian-UI-Wireframes.md#실행-버튼](Sebastian-UI-Wireframes.md#실행-버튼)
- ProgressDialog: [Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog](Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog)

---

## ⚠️ 특이사항

1. **성별 구분**: DIALOGUE는 언어별 남/여 컬럼 분리, STRING은 통합
2. **NPC 매핑**: DIALOGUE에만 필요, STRING은 일부 파일에 이미 포함
3. **읽기 전용**: 결과 파일 `os.chmod(stat.S_IREAD)` 설정

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 0.1.0 | 2025-12-10 | 초안 작성 | 재경 |
| 0.2.0 | 2025-12-11 | NPC 매핑 실패 처리 명확화, Table/ID 생성 시점 명시, 파일명 중복 처리 로직 추가 (counter 1부터) | 재경 |
| 0.3.0 | 2025-12-11 | STRING 파일별 헤더 구조 차이 설명 추가 | 재경 |
| 0.4.0 | 2025-12-11 | 검수 반영: 파일 크기 제한 참조 추가 | 재경 |
| 0.5.0 | 2025-12-12 | UI 설계 섹션 와이어프레임 참조로 변경, 아스키 UI 제거 | 재경 |
