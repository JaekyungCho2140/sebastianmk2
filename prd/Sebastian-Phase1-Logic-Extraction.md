# Sebastian Phase 1: Logic Extraction Guide

**버전**: 1.0.0
**작성일**: 2025-12-19
**Phase 목표**: 레거시 코드에서 순수 로직만 추출하여 `sebastian/core/` 구축

---

## 📋 Phase 1 개요

### 목표

레거시 3개 도구(M4/GL, NC/GL, LY/GL)의 핵심 로직을 UI와 분리하여 재사용 가능한 모듈로 추출합니다.

### 핵심 원칙

1. **복사 우선**: 재작성하지 않고 복사
2. **최소 변경**: UI 의존성 제거를 위한 최소한의 변경만
3. **로직 보존**: 알고리즘, 데이터 처리, 서식 지정 등 한 줄도 변경 금지
4. **검증 필수**: diff로 변경사항 확인 후 다음 단계

### 산출물

```
sebastian/core/
├── m4gl/
│   ├── __init__.py
│   ├── dialogue.py      # run_merge() 복사본
│   └── string.py        # run_merge_string() 복사본
├── ncgl/
│   ├── __init__.py
│   └── merger.py        # process_files() 복사본
└── lygl/                # LY/GL 전체 복사
    ├── __init__.py
    ├── merge.py
    ├── split.py
    ├── batch_merger.py
    ├── legacy_diff.py
    ├── excel_format.py
    ├── validator.py
    └── error_messages.py
```

---

## 🎯 우선순위 순서

### 1. LY/GL (가장 쉬움 ⭐⭐☆☆☆)

**이유**: 이미 UI와 로직이 분리되어 있음

**작업**: 그대로 복사 + customtkinter 의존성 제거

**예상 시간**: 2-3일

### 2. M4/GL (중간 ⭐⭐⭐☆☆)

**이유**: 로직 추출 필요하지만 단순한 구조

**작업**: 함수 추출 + tkinter 의존성 제거

**예상 시간**: 3-5일

### 3. NC/GL (복잡 ⭐⭐⭐⭐☆)

**이유**: ProcessPoolExecutor + xlsxwriter 유지 필요

**작업**: 함수 추출 + 병렬 처리 로직 보존

**예상 시간**: 4-6일

---

## 📦 Task 1: LY/GL 로직 복사

### 1.1 디렉터리 구조 생성

**Claude Code 지시**:
```
"sebastian/core/lygl/ 디렉터리를 생성하고, __init__.py 파일을 만들어줘."
```

**검증**:
```bash
ls -la sebastian/core/lygl/
# __init__.py 파일 확인
```

### 1.2 핵심 모듈 복사

**소스**: `legacy/LY/src/*.py`
**타겟**: `sebastian/core/lygl/*.py`

**Claude Code 지시**:
```
"다음 파일들을 정확히 복사해줘:
1. legacy/LY/src/merge.py → sebastian/core/lygl/merge.py
2. legacy/LY/src/split.py → sebastian/core/lygl/split.py
3. legacy/LY/src/batch_merger.py → sebastian/core/lygl/batch_merger.py
4. legacy/LY/src/legacy_diff.py → sebastian/core/lygl/legacy_diff.py
5. legacy/LY/src/excel_format.py → sebastian/core/lygl/excel_format.py
6. legacy/LY/src/validator.py → sebastian/core/lygl/validator.py
7. legacy/LY/src/error_messages.py → sebastian/core/lygl/error_messages.py

한 줄도 변경하지 말고 그대로 복사만 해줘."
```

**검증**:
```bash
diff legacy/LY/src/merge.py sebastian/core/lygl/merge.py
# 차이 없음 확인

diff legacy/LY/src/split.py sebastian/core/lygl/split.py
# 차이 없음 확인

# ... 나머지 파일들도 동일하게 확인
```

### 1.3 customtkinter 의존성 확인

**Claude Code 지시**:
```
"sebastian/core/lygl/*.py 파일들에서 customtkinter 임포트를 찾아줘.
발견되면 해당 파일과 라인 번호를 알려줘."
```

**예상 결과**:
- merge.py, split.py, batch_merger.py, legacy_diff.py에는 customtkinter 없음
- ui.py만 customtkinter 사용 (이 파일은 복사하지 않음)

### 1.4 __init__.py 작성

**Claude Code 지시**:
```
"sebastian/core/lygl/__init__.py에 다음 내용을 작성해줘:

'''
LY/GL 현지화 테이블 병합/분할 로직

레거시 소스: legacy/LY/src/
'''

from .merge import merge_language_files
from .split import split_all_file
from .batch_merger import merge_batches
from .legacy_diff import compare_folders

__all__ = [
    'merge_language_files',
    'split_all_file',
    'merge_batches',
    'compare_folders',
]
"
```

### 1.5 단위 테스트 확인

**소스**: `legacy/LY/src/test_*.py` (37개 테스트)

**Claude Code 지시**:
```
"legacy/LY/ 디렉터리에서 test_로 시작하는 파일들을 찾아서 리스트로 보여줘."
```

**참고**: 테스트 마이그레이션은 Phase 3에서 수행 (지금은 확인만)

### 1.6 LY/GL 완료 체크리스트

- [ ] `sebastian/core/lygl/` 디렉터리 생성
- [ ] `merge.py` 복사 및 diff 확인
- [ ] `split.py` 복사 및 diff 확인
- [ ] `batch_merger.py` 복사 및 diff 확인
- [ ] `legacy_diff.py` 복사 및 diff 확인
- [ ] `excel_format.py` 복사 및 diff 확인
- [ ] `validator.py` 복사 및 diff 확인
- [ ] `error_messages.py` 복사 및 diff 확인
- [ ] `__init__.py` 작성
- [ ] customtkinter 의존성 없음 확인
- [ ] 37개 단위 테스트 위치 확인

---

## 📦 Task 2: M4/GL 로직 추출

### 2.1 디렉터리 구조 생성

**Claude Code 지시**:
```
"sebastian/core/m4gl/ 디렉터리를 생성하고, __init__.py 파일을 만들어줘."
```

### 2.2 DIALOGUE 병합 로직 추출

**소스**: `legacy/M4/Merged_M4.py` (74-266행)
**타겟**: `sebastian/core/m4gl/dialogue.py`

**Claude Code 지시**:
```
"legacy/M4/Merged_M4.py의 74-266행(run_merge 함수)을
sebastian/core/m4gl/dialogue.py로 복사해줘.

다음 변경사항만 적용:
1. 함수명 변경: run_merge() → merge_dialogue(folder_path, progress_queue)
2. 함수 시그니처:
   def merge_dialogue(folder_path: str, progress_queue) -> None:
3. progress_queue 사용 (레거시와 동일하게 queue.put() 호출)
4. 나머지 로직은 한 줄도 변경하지 마

특히 다음 항목은 절대 변경 금지:
- read_excel_file() 호출 파라미터 (sheet_name, header_row, skip_rows)
- language_mapping 딕셔너리 (컬럼 인덱스)
- NPC 매핑 로직 (iloc[:, 7], iloc[:, 9])
- 서식 지정 (Font, PatternFill, Border 색상 코드)
- 파일 권한 설정 (os.chmod)
"
```

**검증**:
```bash
# diff 실행 (변경사항 확인)
diff legacy/M4/Merged_M4.py sebastian/core/m4gl/dialogue.py

# 예상 diff:
# - def run_merge(progress_queue, folder_path, start_time):
# + def merge_dialogue(folder_path: str, progress_queue) -> None:
# + start_time = time.time()
```

**수동 검증**:
```python
# sebastian/core/m4gl/dialogue.py 열어서 확인

# 1. 파일 읽기 파라미터 확인
cinematic_data = read_excel_file(cinematic_path, sheet_name=1, header_row=1, skip_rows=9)
# ✅ sheet_name=1, header_row=1, skip_rows=9 (변경 없음)

# 2. 컬럼 매핑 확인
language_mapping = {
    'KO (M)': (11, 12),
    'KO (F)': (12, 13),
    # ...
}
# ✅ 인덱스 (11, 12) 등 (변경 없음)

# 3. NPC 매핑 확인
npc_map = dict(zip(npc_data.iloc[:, 7], npc_data.iloc[:, 9]))
# ✅ iloc[:, 7], iloc[:, 9] (변경 없음)

# 4. 서식 확인
header_font = Font(name='맑은 고딕', size=12, bold=True, color='9C5700')
# ✅ color='9C5700' (변경 없음)

# 5. 파일 권한 확인
os.chmod(output_file, stat.S_IREAD)
# ✅ stat.S_IREAD (변경 없음)
```

### 2.3 STRING 병합 로직 추출

**소스**: `legacy/M4/Merged_M4.py` (268-422행)
**타겟**: `sebastian/core/m4gl/string.py`

**Claude Code 지시**:
```
"legacy/M4/Merged_M4.py의 268-422행(run_merge_string 함수)을
sebastian/core/m4gl/string.py로 복사해줘.

다음 변경사항만 적용:
1. 함수명 변경: run_merge_string() → merge_string(folder_path, progress_queue)
2. 함수 시그니처:
   def merge_string(folder_path: str, progress_queue) -> None:
3. 나머지 로직은 한 줄도 변경하지 마

특히 다음 항목은 절대 변경 금지:
- file_list (8개 파일명)
- header_rows 딕셔너리
- start_rows 딕셔너리
- matching_columns 딕셔너리 (컬럼 인덱스)
- 서식 지정 로직
"
```

**검증**:
```bash
diff legacy/M4/Merged_M4.py sebastian/core/m4gl/string.py

# 예상 diff:
# - def run_merge_string(progress_queue, folder_path, start_time):
# + def merge_string(folder_path: str, progress_queue) -> None:
# + start_time = time.time()
```

**수동 검증**:
```python
# sebastian/core/m4gl/string.py 열어서 확인

# 1. 파일 리스트 확인
file_list = [
    "SEQUENCE_DIALOGUE.xlsm",
    "STRING_BUILTIN.xlsm",
    # ...
]
# ✅ 8개 파일 (변경 없음)

# 2. header_rows 확인
header_rows = {
    "SEQUENCE_DIALOGUE.xlsm": 2,
    "STRING_BUILTIN.xlsm": 2,
    # ...
}
# ✅ 각 파일별 header_row (변경 없음)

# 3. matching_columns 확인
matching_columns = {
    "SEQUENCE_DIALOGUE.xlsm": [7, None, 10, 11, 12, 13, 14, 15, 16, 17, None, None],
    # ...
}
# ✅ 컬럼 인덱스 (변경 없음)
```

### 2.4 read_excel_file 헬퍼 함수 추출

**소스**: `legacy/M4/Merged_M4.py` (66-71행)

**Claude Code 지시**:
```
"legacy/M4/Merged_M4.py의 66-71행(read_excel_file 함수)을
sebastian/core/m4gl/dialogue.py와 sebastian/core/m4gl/string.py의
상단에 복사해줘. (두 파일 모두에 포함)"
```

### 2.5 __init__.py 작성

**Claude Code 지시**:
```
"sebastian/core/m4gl/__init__.py에 다음 내용을 작성해줘:

'''
M4/GL 현지화 테이블 병합 로직

레거시 소스: legacy/M4/Merged_M4.py
'''

from .dialogue import merge_dialogue
from .string import merge_string

__all__ = [
    'merge_dialogue',
    'merge_string',
]
"
```

### 2.6 M4/GL 완료 체크리스트

- [ ] `sebastian/core/m4gl/` 디렉터리 생성
- [ ] `dialogue.py` 생성 및 run_merge() 복사
- [ ] 함수명 변경: `merge_dialogue()`
- [ ] diff 확인: 함수명, 인자 외 변경 없음
- [ ] 수동 검증: 파일 읽기 파라미터
- [ ] 수동 검증: language_mapping
- [ ] 수동 검증: NPC 매핑
- [ ] 수동 검증: 서식 지정
- [ ] 수동 검증: 파일 권한
- [ ] `string.py` 생성 및 run_merge_string() 복사
- [ ] 함수명 변경: `merge_string()`
- [ ] diff 확인
- [ ] 수동 검증: file_list, header_rows, start_rows, matching_columns
- [ ] `read_excel_file` 헬퍼 함수 복사
- [ ] `__init__.py` 작성
- [ ] tkinter 의존성 제거 확인

---

## 📦 Task 3: NC/GL 로직 추출

### 3.1 디렉터리 구조 생성

**Claude Code 지시**:
```
"sebastian/core/ncgl/ 디렉터리를 생성하고, __init__.py 파일을 만들어줘."
```

### 3.2 병합 로직 추출

**소스**: `legacy/NC/Merged_NC.py` (147-272행)
**타겟**: `sebastian/core/ncgl/merger.py`

**Claude Code 지시**:
```
"legacy/NC/Merged_NC.py의 147-272행(process_files 함수)을
sebastian/core/ncgl/merger.py로 복사해줘.

다음 변경사항만 적용:
1. 함수명 변경: process_files() → merge_ncgl(folder_path, date, milestone, progress_queue)
2. 함수 시그니처:
   def merge_ncgl(folder_path: str, date: str, milestone: str, progress_queue) -> None:
3. start_time = time.time() 함수 내부에 추가
4. 나머지 로직은 한 줄도 변경하지 마

특히 다음 항목은 절대 변경 금지:
- ProcessPoolExecutor 사용 (병렬 처리)
- read_excel_file 글로벌 함수 (6-8행도 함께 복사)
- file_names 리스트 (8개 파일)
- xlsxwriter 사용 (openpyxl 아님)
- 텍스트 서식 설정 (num_format: '@')
- NaN 처리 (replace([np.nan, np.inf, -np.inf], ''))
"
```

**검증**:
```bash
diff legacy/NC/Merged_NC.py sebastian/core/ncgl/merger.py

# 예상 diff:
# - def process_files(self, folder_path, date, milestone):
# + def merge_ncgl(folder_path: str, date: str, milestone: str, progress_queue) -> None:
# + start_time = time.time()
```

**수동 검증**:
```python
# sebastian/core/ncgl/merger.py 열어서 확인

# 1. ProcessPoolExecutor 확인
with ProcessPoolExecutor() as executor:
    file_paths = [os.path.join(folder_path, f) for f in file_names]
    results = list(executor.map(read_excel_file, file_paths))
# ✅ ProcessPoolExecutor (변경 없음)

# 2. file_names 확인
file_names = [
    "StringEnglish.xlsx", "StringTraditionalChinese.xlsx",
    # ...
]
# ✅ 8개 파일 (변경 없음)

# 3. xlsxwriter 확인
import xlsxwriter
workbook = xlsxwriter.Workbook(output_path)
# ✅ xlsxwriter 사용 (변경 없음)

# 4. 텍스트 서식 확인
cell_format = workbook.add_format({
    'num_format': '@'  # 텍스트 서식
})
# ✅ num_format: '@' (변경 없음)

# 5. NaN 처리 확인
result_df = result_df.replace([np.nan, np.inf, -np.inf], '', regex=False)
# ✅ NaN 처리 (변경 없음)
```

### 3.3 read_excel_file 글로벌 함수 추가

**소스**: `legacy/NC/Merged_NC.py` (6-8행)

**Claude Code 지시**:
```
"legacy/NC/Merged_NC.py의 6-8행(read_excel_file 글로벌 함수)을
sebastian/core/ncgl/merger.py의 상단에 복사해줘.

# ProcessPoolExecutor에서 사용할 함수는 반드시 글로벌로 정의해야 함

def read_excel_file(file_path):
    import pandas as pd
    return pd.read_excel(file_path)
"
```

### 3.4 __init__.py 작성

**Claude Code 지시**:
```
"sebastian/core/ncgl/__init__.py에 다음 내용을 작성해줘:

'''
NC/GL 현지화 테이블 병합 로직

레거시 소스: legacy/NC/Merged_NC.py
'''

from .merger import merge_ncgl

__all__ = [
    'merge_ncgl',
]
"
```

### 3.5 NC/GL 완료 체크리스트

- [ ] `sebastian/core/ncgl/` 디렉터리 생성
- [ ] `merger.py` 생성 및 process_files() 복사
- [ ] 함수명 변경: `merge_ncgl()`
- [ ] diff 확인: 함수명, 인자 외 변경 없음
- [ ] 수동 검증: ProcessPoolExecutor
- [ ] 수동 검증: file_names
- [ ] 수동 검증: xlsxwriter 사용
- [ ] 수동 검증: 텍스트 서식 (@)
- [ ] 수동 검증: NaN 처리
- [ ] `read_excel_file` 글로벌 함수 복사
- [ ] `__init__.py` 작성
- [ ] tkinter 의존성 제거 확인

---

## 🧪 Phase 1 전체 검증

### 검증 1: 디렉터리 구조

**Claude Code 지시**:
```
"sebastian/core/ 디렉터리 구조를 tree 형식으로 보여줘."
```

**예상 결과**:
```
sebastian/core/
├── __init__.py
├── m4gl/
│   ├── __init__.py
│   ├── dialogue.py
│   └── string.py
├── ncgl/
│   ├── __init__.py
│   └── merger.py
└── lygl/
    ├── __init__.py
    ├── merge.py
    ├── split.py
    ├── batch_merger.py
    ├── legacy_diff.py
    ├── excel_format.py
    ├── validator.py
    └── error_messages.py
```

### 검증 2: 임포트 테스트

**Claude Code 지시**:
```
"sebastian/core/__init__.py를 작성해줘:

'''
Sebastian Core Engine

레거시 로직 통합 모듈
'''

# M4/GL
from .m4gl import merge_dialogue, merge_string

# NC/GL
from .ncgl import merge_ncgl

# LY/GL
from .lygl import (
    merge_language_files,
    split_all_file,
    merge_batches,
    compare_folders,
)

__all__ = [
    # M4/GL
    'merge_dialogue',
    'merge_string',
    # NC/GL
    'merge_ncgl',
    # LY/GL
    'merge_language_files',
    'split_all_file',
    'merge_batches',
    'compare_folders',
]
"
```

**테스트**:
```python
# sebastian/ 디렉터리에서 Python 실행
python

>>> from core import merge_dialogue, merge_string
>>> from core import merge_ncgl
>>> from core import merge_language_files, split_all_file

# 에러 없이 임포트되면 성공
```

### 검증 3: 의존성 확인

**Claude Code 지시**:
```
"sebastian/core/ 디렉터리의 모든 .py 파일에서 import 구문을 찾아서
사용된 외부 라이브러리 리스트를 만들어줘."
```

**예상 결과**:
```
pandas
openpyxl
xlsxwriter
numpy
```

**requirements.txt 업데이트**:
```
"sebastian/requirements.txt에 다음 내용을 추가해줘:

# Core dependencies (레거시 유지)
pandas>=1.3.0
openpyxl>=3.0.0
xlsxwriter>=3.0.0
numpy>=1.21.0
"
```

### 검증 4: UI 의존성 제거 확인

**Claude Code 지시**:
```
"sebastian/core/ 디렉터리의 모든 .py 파일에서
tkinter, customtkinter를 임포트하는 라인이 있는지 찾아줘.
있으면 파일명과 라인 번호를 알려줘."
```

**예상 결과**:
```
검색 결과 없음 (UI 의존성 완전 제거됨)
```

---

## 📊 Phase 1 완료 체크리스트

### 전체 작업
- [ ] LY/GL 로직 복사 완료
- [ ] M4/GL 로직 추출 완료
- [ ] NC/GL 로직 추출 완료
- [ ] 디렉터리 구조 검증
- [ ] 임포트 테스트 통과
- [ ] 의존성 확인 및 requirements.txt 업데이트
- [ ] UI 의존성 제거 확인

### 문서 업데이트
- [ ] 변경 이력 기록
- [ ] 발견된 이슈 문서화
- [ ] Phase 2 진행 준비

---

## 🚨 주의사항

### 절대 하지 말 것

1. ❌ 로직 재작성: "더 나은 방법이 있어도" 레거시 그대로 유지
2. ❌ 최적화: "성능 개선" 시도 금지 (Phase 5에서 수행)
3. ❌ 리팩토링: "코드 정리" 금지
4. ❌ 타입 힌트 과도 추가: 함수 시그니처만 추가
5. ❌ 주석 추가: 레거시에 없던 주석 추가 금지

### 허용되는 변경

1. ✅ 함수명 변경 (run_merge → merge_dialogue)
2. ✅ 함수 시그니처 변경 (인자 순서, 타입 힌트)
3. ✅ UI 의존성 제거 (tkinter, customtkinter import 제거)
4. ✅ progress_queue 사용 (레거시 인터페이스 유지)
5. ✅ __init__.py 작성 (모듈화)

---

## 🐛 트러블슈팅

### 문제 1: diff에서 예상치 못한 변경 발견

**증상**: diff 결과에 함수명, 인자 외 다른 변경사항 표시

**해결**:
```
1. 변경사항 확인
2. 레거시 코드 다시 복사
3. 함수명, 인자만 변경
4. diff 재확인
```

### 문제 2: 임포트 에러

**증상**: `ModuleNotFoundError: No module named 'sebastian.core'`

**해결**:
```
1. sebastian/__init__.py 존재 확인
2. sebastian/core/__init__.py 존재 확인
3. PYTHONPATH 설정 확인
4. 가상환경 활성화 확인
```

### 문제 3: 의존성 충돌

**증상**: `ImportError: cannot import name '...' from 'openpyxl'`

**해결**:
```
1. requirements.txt 버전 확인
2. pip install -r requirements.txt --upgrade
3. 가상환경 재생성
```

---

## 📅 다음 단계

Phase 1 완료 후:

1. **Phase 2 시작**: [Sebastian-Phase2-UI-Development.md](Sebastian-Phase2-UI-Development.md)
2. **Implementation PRD 참조**: 각 게임별 상세 구현 가이드
3. **진행 상황 업데이트**: Migration Guide의 진행률 체크리스트 업데이트

---

## 📚 참고 자료

- [Sebastian-Migration-Guide.md](Sebastian-Migration-Guide.md) - 전체 마이그레이션 개요
- [Sebastian-Claude-Code-Protocol.md](Sebastian-Claude-Code-Protocol.md) - Claude Code 작업 규칙
- 레거시 코드:
  - `legacy/M4/Merged_M4.py`
  - `legacy/NC/Merged_NC.py`
  - `legacy/LY/src/*.py`
