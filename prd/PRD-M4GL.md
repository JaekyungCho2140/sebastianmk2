# Sebastian PRD - M4/GL (MIR4 Global)

**게임**: MIR4 Global
**기능**: DIALOGUE/STRING 병합
**버전**: v0.1.1
**상태**: Production

---

## 목차

1. [개요](#개요)
2. [DIALOGUE 병합](#dialogue-병합)
3. [STRING 병합](#string-병합)
4. [UI 디자인](#ui-디자인)
5. [구현 세부사항](#구현-세부사항)

---

## 개요

### 목적

MIR4 Global 게임의 현지화 테이블을 병합하는 기능입니다.

- **DIALOGUE**: 대화 데이터 (3개 파일 → 1개)
- **STRING**: 문자열 데이터 (8개 파일 → 1개)

### 핵심 기능

1. **다중 파일 병합**: 여러 Excel 파일을 1개로 통합
2. **NPC 매핑**: NPC ID → Speaker Name 자동 매핑 (DIALOGUE)
3. **Excel 서식**: 폰트, 색상, 테두리 자동 지정
4. **진행 상황 표시**: 실시간 진행도 및 파일명 표시

### 입력/출력

**입력**:
- 폴더 경로 (Excel 파일들이 위치한 폴더)
- 모드 선택 (DIALOGUE 또는 STRING)

**출력**:
- `MERGED_DIALOGUE.xlsx` (DIALOGUE 모드)
- `MERGED_STRING.xlsx` (STRING 모드)

---

## DIALOGUE 병합

### 입력 파일 (3개)

| 파일명 | 설명 | 시트 | 헤더 행 | 데이터 시작 행 |
|--------|------|------|---------|---------------|
| `CINEMATIC_DIALOGUE.xlsm` | 시네마틱 대화 | Sheet2 | 2 | 10 |
| `SMALLTALK_DIALOGUE.xlsm` | 일반 대화 | Sheet2 | 2 | 5 |
| `NPC.xlsm` | NPC 정보 | Sheet2 | 2 | 5 |

### 출력 파일

**파일명**: `MERGED_DIALOGUE.xlsx`

**컬럼 구조** (23개 컬럼):

| # | 컬럼명 | 설명 | 데이터 소스 |
|---|--------|------|-------------|
| 1 | # | 행 번호 (1부터 시작) | 자동 생성 |
| 2 | Table Name | 테이블 이름 | CINEMATIC_DIALOGUE / SMALLTALK_DIALOGUE |
| 3 | String ID | 문자열 ID | 원본 파일 인덱스 7 |
| 4 | Table/ID | 테이블/ID 조합 | 자동 생성 (Table Name + String ID) |
| 5 | NPC ID | NPC ID | 원본 파일 인덱스 8 |
| 6 | Speaker Name | 화자 이름 | NPC.xlsm에서 매핑 |
| 7-22 | KO (M/F), EN (M/F), ... | 언어별 남/여 텍스트 | 원본 파일 인덱스 9-24 |
| 23 | NOTE | 비고 | 원본 파일 인덱스 25 |

**지원 언어** (8개, 각 M/F):
- KO (Korean)
- EN (English)
- CT (Traditional Chinese)
- CS (Simplified Chinese)
- JA (Japanese)
- TH (Thai)
- ES-LATAM (Spanish Latin America)
- PT-BR (Portuguese Brazil)

### NPC 매핑 로직

**목적**: NPC ID → Speaker Name 자동 채우기

**입력**:
- NPC.xlsm 파일 (Sheet2, 헤더 행 2, 데이터 시작 행 5)
- 컬럼 구조: [인덱스 0: NPC ID, 인덱스 1: KO 이름]

**매핑 과정**:

```python
# 1. NPC.xlsm 읽기
npc_data = pd.read_excel("NPC.xlsm", sheet_name=1, header=1, skiprows=4)

# 2. NPC ID → Speaker Name 딕셔너리 생성
npc_mapping = {}
for idx, row in npc_data.iterrows():
    npc_id = row.iloc[0]      # NPC ID
    speaker_name = row.iloc[1]  # KO 이름
    npc_mapping[npc_id] = speaker_name

# 3. DIALOGUE 데이터에 매핑 적용
for idx, row in dialogue_data.iterrows():
    npc_id = row['NPC ID']
    speaker_name = npc_mapping.get(npc_id, "")
    result_df.loc[idx, 'Speaker Name'] = speaker_name
```

### Excel 서식

**헤더 행 (행 1)**:
- Font: `맑은 고딕`, 10pt, Bold
- Fill: `#DAE9F8` (연한 파란색)
- Border: 전체 테두리 (얇은 선)
- Alignment: 가운데 정렬, 세로 가운데

**데이터 행 (행 2~)**:
- Font: `맑은 고딕`, 10pt
- Alignment: 왼쪽 정렬, 세로 가운데
- Border: 전체 테두리 (얇은 선)

**특정 컬럼 색상**:
- `Table Name` (B열): 노란색 배경 (`#FFFF00`)

**컬럼 너비 자동 조정**:
```python
for column in worksheet.columns:
    max_length = max(len(str(cell.value)) for cell in column)
    adjusted_width = min(max_length + 2, 50)
    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
```

### 알고리즘

```
1. 파일 존재 확인
   - CINEMATIC_DIALOGUE.xlsm, SMALLTALK_DIALOGUE.xlsm, NPC.xlsm
   - FileNotFoundError 발생 시 에러 메시지

2. NPC 매핑 테이블 생성
   - NPC.xlsm 읽기
   - {NPC ID: Speaker Name} 딕셔너리 생성

3. CINEMATIC_DIALOGUE.xlsm 읽기
   - Sheet2, 헤더 행 2, 데이터 시작 행 10
   - 인덱스 7-25 컬럼 추출
   - NPC ID → Speaker Name 매핑
   - Table Name = "CINEMATIC_DIALOGUE"

4. SMALLTALK_DIALOGUE.xlsm 읽기
   - Sheet2, 헤더 행 2, 데이터 시작 행 5
   - 인덱스 7-25 컬럼 추출
   - NPC ID → Speaker Name 매핑
   - Table Name = "SMALLTALK_DIALOGUE"

5. 데이터 병합
   - CINEMATIC_DIALOGUE + SMALLTALK_DIALOGUE
   - 행 번호 (#) 자동 생성 (1부터)
   - Table/ID = Table Name + String ID

6. Excel 파일 저장
   - MERGED_DIALOGUE.xlsx
   - openpyxl로 서식 지정

7. 진행 상황 업데이트
   - 0%: 시작
   - 20%: CINEMATIC_DIALOGUE 읽기 완료
   - 40%: SMALLTALK_DIALOGUE 읽기 완료
   - 60%: NPC 매핑 완료
   - 80%: 데이터 병합 완료
   - 100%: Excel 저장 완료
```

---

## STRING 병합

### 입력 파일 (8개)

| 파일명 | 헤더 행 | 데이터 시작 행 | 특징 |
|--------|---------|---------------|------|
| `SEQUENCE_DIALOGUE.xlsm` | 2 | 10 | 시퀀스 대화 |
| `STRING_BUILTIN.xlsm` | 2 | 5 | 내장 문자열 |
| `STRING_MAIL.xlsm` | 2 | 5 | 메일 문자열 |
| `STRING_MESSAGE.xlsm` | 2 | 5 | 메시지 문자열 |
| `STRING_NPC.xlsm` | 2 | 5 | NPC 문자열 (NPC 이름/비고 포함) |
| `STRING_QUESTTEMPLATE.xlsm` | 2 | 8 | 퀘스트 템플릿 |
| `STRING_TEMPLATE.xlsm` | 2 | 5 | 템플릿 문자열 |
| `STRING_TOOLTIP.xlsm` | 2 | 5 | 툴팁 문자열 |

### 출력 파일

**파일명**: `MERGED_STRING.xlsx`

**컬럼 구조** (15개 컬럼):

| # | 컬럼명 | 설명 | 데이터 소스 |
|---|--------|------|-------------|
| 1 | # | 행 번호 (1부터 시작) | 자동 생성 |
| 2 | Table Name | 테이블 이름 | 파일명 (확장자 제외) |
| 3 | String ID | 문자열 ID | 원본 파일 인덱스 7 |
| 4 | Table/ID | 테이블/ID 조합 | 자동 생성 |
| 5 | NOTE | 비고 | 파일별 매핑 인덱스 |
| 6-13 | KO, EN, CT, CS, JA, TH, ES-LATAM, PT-BR | 언어별 텍스트 | 파일별 매핑 인덱스 |
| 14 | NPC 이름 | NPC 이름 (STRING_NPC만) | STRING_NPC 인덱스 18 |
| 15 | 비고 | 비고 (STRING_NPC만) | STRING_NPC 인덱스 19 |

### 컬럼 매핑 테이블

각 파일마다 컬럼 인덱스가 다르므로 매핑 테이블 사용:

```python
matching_columns = {
    "SEQUENCE_DIALOGUE.xlsm":     [7, None, 10, 11, 12, 13, 14, 15, 16, 17, None, None],
    "STRING_BUILTIN.xlsm":        [7,   21,  8,  9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_MAIL.xlsm":           [7, None,  8,  9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_MESSAGE.xlsm":        [7,   21,  8,  9, 10, 11, 12, 13, 14, 15, None, None],
    "STRING_NPC.xlsm":            [7,   20,  9, 10, 11, 12, 13, 14, 15, 16,   18,   19],
    "STRING_QUESTTEMPLATE.xlsm":  [7,    0, 12, 13, 14, 15, 16, 17, 18, 19, None, None],
    "STRING_TEMPLATE.xlsm":       [7,   19,  8,  9, 10, 11, 12, 13, 14, 15, None,   18],
    "STRING_TOOLTIP.xlsm":        [7,    8, 11, 12, 13, 14, 15, 16, 17, 18, None, None],
}
```

**매핑 순서**:
```
[String ID, NOTE, KO, EN, CT, CS, JA, TH, ES-LATAM, PT-BR, NPC 이름, 비고]
```

**None 처리**:
- `None`이면 빈 문자열 (`""`) 입력

### Excel 서식

**DIALOGUE와 동일**:
- 헤더: 맑은 고딕 10pt Bold, 연한 파란색 배경
- 데이터: 맑은 고딕 10pt, 왼쪽 정렬
- Table Name 컬럼: 노란색 배경

### 알고리즘

```
1. 파일 존재 확인
   - 8개 파일 모두 존재 확인
   - FileNotFoundError 발생 시 에러 메시지

2. 각 파일 순차 읽기
   FOR EACH file IN file_list:
       - Excel 읽기 (sheet_name, header_row, skip_rows)
       - matching_columns 적용하여 컬럼 추출
       - Table Name = 파일명 (확장자 제외)
       - result_df에 추가

3. 행 번호 (#) 자동 생성
   - 1부터 총 행 수까지

4. Table/ID 생성
   - Table Name + String ID

5. Excel 파일 저장
   - MERGED_STRING.xlsx
   - openpyxl로 서식 지정

6. 진행 상황 업데이트
   - 각 파일 읽기마다 진행률 업데이트
   - 0%, 12.5%, 25%, 37.5%, 50%, 62.5%, 75%, 87.5%, 100%
```

---

## UI 디자인

### M4/GL 탭 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│    ┌────────────────┐      ┌────────────────┐          │
│    │                │      │                │          │
│    │   DIALOGUE     │      │    STRING      │          │
│    │                │      │                │          │
│    │     병합       │      │     병합       │          │
│    │                │      │                │          │
│    │   대화 데이터  │      │  문자열 데이터 │          │
│    │   3개 파일     │      │   8개 파일     │          │
│    │                │      │                │          │
│    └────────────────┘      └────────────────┘          │
│                                                         │
│    폴더 선택                                            │
│    ┌──────────────────────────────────┐  ┌─────────┐  │
│    │  (경로 표시)                     │  │ 📁 폴더 │  │
│    └──────────────────────────────────┘  │  선택   │  │
│                                          └─────────┘  │
│                                                         │
│                              ┌───────────────┐         │
│                              │ 실행 (Enter) │         │
│                              └───────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 카드 버튼 (DIALOGUE/STRING)

**크기**: 240 × 200px

**구조**:
```
┌──────────────────┐
│                  │
│    DIALOGUE      │  ← 제목 (18pt Bold)
│                  │
│      병합        │  ← 부제목 (15pt)
│                  │
│   대화 데이터    │  ← 설명 1 (13pt)
│   3개 파일       │  ← 설명 2 (13pt)
│                  │
└──────────────────┘
```

**기본 상태**:
- Background: `#FFFFFF`
- Border: `2px solid #E5E7EB`
- Border Radius: `12px`

**Hover**:
- Border Color: `#5E35B1`

**선택 상태**:
- Background: `#EDE7F6` (Primary Surface)
- Border: `3px solid #5E35B1`

### 폴더 선택

**입력 필드**:
- Read-only
- Placeholder: "(경로 표시)"
- Height: 40px
- Background: `#FAFAFA` (비활성)

**폴더 선택 버튼**:
- Text: "📁 폴더 선택"
- Style: Secondary Button
- Size: 120 × 40px

### 실행 버튼

**크기**: 160 × 48px
**텍스트**: "실행 (Enter)"
**활성화 조건**:
- 모드 선택 (DIALOGUE 또는 STRING)
- 폴더 경로 입력

**비활성 상태**:
- Background: `#F3F4F6`
- Text Color: `#9CA3AF`

**활성 상태**:
- Background: `#5E35B1`
- Text Color: `#FFFFFF`

---

## 구현 세부사항

### Core 로직

**파일 경로**:
- `sebastian/core/m4gl/dialogue.py`
- `sebastian/core/m4gl/string.py`

**함수 시그니처**:

```python
def merge_dialogue(folder_path: str, progress_queue: queue.Queue) -> None:
    """
    M4/GL DIALOGUE 3개 파일 병합

    Args:
        folder_path: 폴더 경로
        progress_queue: 진행 상황 Queue

    Raises:
        FileNotFoundError: 파일 미존재 시
        ValidationError: 데이터 검증 실패 시
        IOError: 파일 읽기/쓰기 실패 시
    """
    pass

def merge_string(folder_path: str, progress_queue: queue.Queue) -> None:
    """
    M4/GL STRING 8개 파일 병합

    Args:
        folder_path: 폴더 경로
        progress_queue: 진행 상황 Queue

    Raises:
        FileNotFoundError: 파일 미존재 시
        ValidationError: 데이터 검증 실패 시
        IOError: 파일 읽기/쓰기 실패 시
    """
    pass
```

### Worker

**파일 경로**: `sebastian/workers/m4gl_worker.py`

**Signals**:

```python
class M4GLWorker(QThread):
    progress_updated = pyqtSignal(int)         # 0-100 진행률
    step_updated = pyqtSignal(str)             # 단계 정보 (예: "1/3")
    file_updated = pyqtSignal(str)             # 처리 중인 파일명
    files_count_updated = pyqtSignal(int)      # 처리된 파일 수
    completed = pyqtSignal(str)                # 완료 메시지
    error_occurred = pyqtSignal(str)           # 에러 메시지
```

**실행 흐름**:

```python
def run(self):
    # 별도 스레드에서 Core 로직 실행
    work_thread = threading.Thread(target=self._do_work)
    work_thread.start()

    # Queue 폴링 (100ms)
    while work_thread.is_alive():
        self._process_queue()
        time.sleep(0.1)

    # 마지막 Queue 처리
    self._process_queue()

def _do_work(self):
    try:
        if self.mode == 'dialogue':
            merge_dialogue(self.folder_path, self.progress_queue)
        else:
            merge_string(self.folder_path, self.progress_queue)

        self.completed.emit(f"M4/GL {self.mode.upper()} 병합 완료")
    except Exception as e:
        self.error_occurred.emit(f"실패: {e}")
```

### UI 탭

**파일 경로**: `sebastian/ui/m4gl_tab.py`

**Signal 연결**:

```python
def _execute(self):
    # Worker 생성
    self.worker = M4GLWorker(self.selected_mode, self.folder_path)

    # ProgressDialog 생성
    title = "M4/GL DIALOGUE 병합" if self.selected_mode == 'dialogue' else "M4/GL STRING 병합"
    self.progress_dialog = ProgressDialog(self, title, M4GL_COLOR)

    # Signal 연결
    self.worker.progress_updated.connect(self.progress_dialog.update_progress)
    self.worker.step_updated.connect(self.progress_dialog.update_step)
    self.worker.file_updated.connect(self.progress_dialog.update_file)
    self.worker.completed.connect(self._on_completed)
    self.worker.error_occurred.connect(self._on_error)

    # Worker 시작
    self.worker.start()
    self.progress_dialog.exec()
```

---

## 테스트

### 검증 항목

1. **파일 존재 확인**
   - 3개/8개 파일 모두 존재
   - FileNotFoundError 처리

2. **데이터 읽기**
   - 정확한 sheet_name, header_row, skip_rows
   - pandas DataFrame 생성 성공

3. **NPC 매핑** (DIALOGUE만)
   - NPC ID → Speaker Name 정확히 매핑
   - 존재하지 않는 NPC ID → 빈 문자열

4. **컬럼 매핑** (STRING)
   - matching_columns 정확히 적용
   - None → 빈 문자열

5. **Excel 저장**
   - MERGED_DIALOGUE.xlsx / MERGED_STRING.xlsx 생성
   - 서식 정확히 적용

6. **레거시 출력 비교**
   - 레거시 스크립트 출력과 100% 일치
   - 셀 값, 서식 모두 동일

### 테스트 데이터

**위치**: `legacy/M4/` (레거시 스크립트 및 샘플 데이터)

**실행**:
```bash
# 레거시 스크립트
python legacy/M4/Merged_M4.py

# Sebastian
python sebastian/main.py
# → M4/GL 탭 → DIALOGUE/STRING 선택 → 실행

# 출력 비교
diff MERGED_DIALOGUE.xlsx legacy_output/MERGED_DIALOGUE.xlsx
```

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-12-24
