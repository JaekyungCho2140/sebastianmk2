# Sebastian PRD - LY/GL 테이블 처리 기능

**문서 유형**: Feature
**게임**: 레전드 오브 이미르 글로벌 (Legend of YMIR Global)
**버전**: 0.1.0 (초안)
**작성일**: 2025-12-10

---

## 📋 문서 참조

**공통 요소**: [Sebastian-PRD-Shared.md](Sebastian-PRD-Shared.md)를 참조하세요.

---

## Import 구문
```python
import pandas as pd
import os
import re
from typing import Dict, List, Tuple
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QDialog, QFileDialog,
    QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
```

## 🎯 기능 개요

레전드 오브 이미르 글로벌 게임의 다국어 번역 테이블 관리 도구. **4가지 독립 기능**을 제공합니다:

1. **Merge**: 7개 언어별 파일 → 1개 통합 파일 (번역 검수용)
2. **Split**: 1개 통합 파일 → 7개 언어별 파일 (게임 적용용)
3. **Merge Batches**: 여러 배치 병합 + 중복 KEY 자동 제거
4. **Legacy Diff**: 두 버전 비교 → Status="기존" 행의 변경 추적

**핵심 특징**:
- **Round-trip 무결성**: Merge → Split → 원본 100% 일치
- **37개 단위 테스트**: 모든 시나리오 커버
- **~49,600행 처리**: 실제 운영 데이터 기준

---

## 🔀 Merge (병합)

### 입력

**7개 언어별 파일** (사용자가 복수 선택):
```
251128_EN.xlsx
251128_CT.xlsx
251128_CS.xlsx
251128_JA.xlsx
251128_TH.xlsx
251128_PT-BR.xlsx
251128_RU.xlsx
```

**각 파일 구조** (7개 컬럼):
```
Table | KEY | Source | Target | Status | NOTE | Date
```

**Date 컬럼 형식**: `YYYY-MM-DD HH:MM` (예: `2025-11-28 14:30`)
- **목적**: 최신 데이터 선별 (Merge Batches에서 중복 KEY 발생 시 최신 행 유지)
- **참고**: 파일명 날짜(`YYMMDD`)는 작명 목적으로 다른 형식 사용

**파일 크기 제한**: [Sebastian-PRD-Shared.md#공통-검증-함수](Sebastian-PRD-Shared.md#공통-검증-함수) 참조 (최대 50MB)

### 파일 선택 방식

**방식**: 복수 파일 직접 선택
1. QFileDialog.getOpenFileNames()로 7개 파일 선택
2. 파일명에서 언어 코드 추출하여 매핑 (`251128_EN.xlsx` → `EN`)
3. 7개 미만/초과 선택 시 오류 표시
4. 파일명 날짜(YYMMDD) 일치 여부 검증

**레거시 참조**: `LY_Table/src/ui.py` 라인 200-204

### 출력

**파일명**: `{YYMMDD}_LYGL_StringALL.xlsx`

**구조** (13개 컬럼):
```
Table | KEY | Source | Target_EN | Target_CT | Target_CS |
Target_JA | Target_TH | Target_PT | Target_RU | Status | NOTE | Date
```

### 데이터 무결성 규칙

**검증 항목**:

#### 1. KEY 일치 검증
**규칙**: 모든 7개 언어 파일의 KEY가 완전히 동일해야 함

**검증 로직**:
```python
# 대소문자 구분 검증 (Python set은 기본적으로 대소문자 구분)
en_keys = set(en_df['KEY'])
for lang in ['CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']:
    lang_keys = set(lang_df['KEY'])
    if en_keys != lang_keys:
        # 차이 분석
        only_in_en = en_keys - lang_keys
        only_in_lang = lang_keys - en_keys
        raise DataIntegrityError(
            f"KEY가 일치하지 않습니다:\n"
            f"  EN에만 있음: {sorted(only_in_en)}\n"
            f"  {lang}에만 있음: {sorted(only_in_lang)}"
        )
```

**실패 시 동작**: ❌ **즉시 오류, 작업 중단**

#### 2. EN 마스터 기준
**규칙**: EN 파일의 KEY 순서가 기준, 다른 파일들은 EN 순서로 정렬

```python
# EN 파일 KEY 순서 추출
en_key_order = en_df['KEY'].tolist()

# 다른 언어 파일을 EN 순서로 정렬 (딕셔너리 사용)
lang_dfs = {
    'CT': ct_df,
    'CS': cs_df,
    'JA': ja_df,
    'TH': th_df,
    'PT-BR': pt_df,
    'RU': ru_df
}

for lang, lang_df in lang_dfs.items():
    sorted_df = lang_df.set_index('KEY').reindex(en_key_order).reset_index()
    lang_dfs[lang] = sorted_df  # 정렬된 DataFrame으로 교체
```

#### 3. 필드 일치 검증
**규칙**: Table, Source, Status, NOTE, Date가 모든 파일에서 동일해야 함

**검증 로직**:
```python
for key in en_keys:
    en_row = en_df[en_df['KEY'] == key].iloc[0]
    for lang, lang_df in langs.items():
        lang_row = lang_df[lang_df['KEY'] == key].iloc[0]

        for field in ['Table', 'Source', 'Status', 'NOTE', 'Date']:
            if en_row[field] != lang_row[field]:
                raise DataIntegrityError(
                    f"KEY '{key}'의 필드 불일치:\n"
                    f"  {field} (EN={en_row[field]}, {lang}={lang_row[field]})"
                )
```

**실패 시 동작**: ❌ **즉시 오류, 작업 중단**

#### 4. 파일명 날짜 일치 검증
**규칙**: 모든 7개 파일의 파일명 날짜(YYMMDD)가 동일해야 함

**검증 순서**: 파일 개수 검증 → 날짜 일치 검증 (논리적 순서)

**검증 로직**:
```python
import re
from collections import Counter

dates = []
for filename in selected_files:
    match = re.match(r"(\d{6})_([A-Z\-]+)\.xlsx", os.path.basename(filename))
    if match:
        dates.append(match.group(1))

date_counts = Counter(dates)
if len(date_counts) > 1:
    raise FileValidationError(
        f"파일명 날짜가 일치하지 않습니다:\n" +
        "\n".join([f"  {date} ({count}개 파일)" for date, count in date_counts.items()])
    )
```

**실패 시 동작**: ❌ **즉시 오류, 작업 중단**

---

## 🔗 Split (분할)

### 입력

**1개 통합 파일**: `{YYMMDD}_LYGL_StringALL.xlsx` (13개 컬럼)

### 출력

**7개 언어별 파일**:
```
{YYMMDD}_EN.xlsx
{YYMMDD}_CT.xlsx
{YYMMDD}_CS.xlsx
{YYMMDD}_JA.xlsx
{YYMMDD}_TH.xlsx
{YYMMDD}_PT-BR.xlsx
{YYMMDD}_RU.xlsx
```

### 처리 로직

**분할 알고리즘**:
```python
def split_merged_file(merged_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """통합 파일(13개 컬럼)을 7개 언어별 파일(7개 컬럼)로 분할

    Args:
        merged_df: DataFrame with columns:
            Table | KEY | Source | Target_EN | Target_CT | Target_CS |
            Target_JA | Target_TH | Target_PT | Target_RU | Status | NOTE | Date

    Returns:
        Dict[str, pd.DataFrame]: {'EN': df, 'CT': df, 'CS': df, 'JA': df,
                                  'TH': df, 'PT-BR': df, 'RU': df}
        각 DataFrame 구조: Table | KEY | Source | Target | Status | NOTE | Date
    """
    LANG_COLUMNS = ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']
    result = {}

    for lang in LANG_COLUMNS:
        # 7개 컬럼 구조로 변환
        lang_df = pd.DataFrame({
            'Table': merged_df['Table'],
            'KEY': merged_df['KEY'],
            'Source': merged_df['Source'],
            'Target': merged_df[f'Target_{lang}'],  # 언어별 Target 추출
            'Status': merged_df['Status'],
            'NOTE': merged_df['NOTE'],
            'Date': merged_df['Date'] if 'Date' in merged_df.columns else ''  # 하위 호환
        })

        result[lang] = lang_df

    return result
```

**파일 저장**:
```python
# 날짜 추출 (입력 파일명에서)
import re
match = re.match(r'(\d{6})_LYGL_StringALL\.xlsx', os.path.basename(merged_file_path))
if match:
    yymmdd = match.group(1)
else:
    raise ValueError(
        f"파일명에서 날짜를 추출할 수 없습니다.\n"
        f"현재 파일명: {os.path.basename(merged_file_path)}\n"
        f"예상 형식: YYMMDD_LYGL_StringALL.xlsx\n"
        f"예시: 251210_LYGL_StringALL.xlsx"
    )

# 7개 언어별 파일 저장
for lang, df in split_dfs.items():
    output_file = os.path.join(output_folder, f"{yymmdd}_{lang}.xlsx")
    df.to_excel(output_file, index=False, sheet_name='Sheet1')
```

**레거시 참조**: `LY_Table/src/split.py`

### Round-trip 무결성

**보장 사항**:
- Merge → Split → 원본 파일과 100% 동일
- KEY 순서 유지
- 공백 보존 (strip() 사용 안 함)

**검증 방식**: **TDD 방식**으로 개발, pytest 자동화 테스트

**개발 방법론**:
- **TDD (Test-Driven Development)**: 테스트를 먼저 작성하고, 테스트를 통과하는 코드를 구현
- **pytest 자동화**: 개발자가 로컬에서 실행하여 품질 검증
- **CI/CD 통합 없음**: 개발자 책임 하에 테스트 실행 (자동화된 파이프라인 불필요)
- **테스트 데이터**: 실제 작업 데이터 사용 (사용자가 제공 예정)

**pytest 단위 테스트**:
```python
# tests/test_roundtrip.py
def test_merge_split_roundtrip():
    """Merge → Split → 원본 일치 검증

    실제 작업 데이터를 사용하여 Round-trip 무결성을 검증합니다.
    """
    # 실제 작업 데이터 로드 (사용자 제공)
    original_files = load_original_files()

    # Merge
    merged_file = merge(original_files)

    # Split
    split_files = split(merged_file)

    # 원본과 비교 (100% 일치해야 함)
    for lang in ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']:
        assert split_files[lang].equals(original_files[lang])
```

**테스트 항목** (TDD 방식으로 필요한 만큼 추가):
- Merge → Split → 원본 동일성
- 공백 보존 검증
- KEY 순서 유지 검증
- Date 컬럼 형식 검증 (`YYYY-MM-DD HH:MM`)
- 대용량 데이터 (49,600행) 검증

**테스트 수**: TDD 방식으로 개발하면서 자연스럽게 증가 (37개는 참고값)

**사용자 사용 시**: 자동 검증 없음 (개발 테스트로 품질 보장)

**개발 워크플로우**:
1. 기능 요구사항 분석
2. pytest 테스트 작성 (TDD)
3. 테스트가 실패하는 코드 작성
4. 테스트가 통과하도록 코드 수정
5. 리팩토링 및 최적화
6. 모든 테스트 통과 확인

---

## 📦 Merge Batches (배치 병합)

### 입력

**여러 배치 폴더** (사용자가 복수 선택):
```
251126_REGULAR/ (7개 파일)
251201_EXTRA1/ (7개 파일)
251205_EXTRA2/ (7개 파일)
```

### 배치 폴더명 규칙

**패턴**: `{YYMMDD}_{배치타입}`
- 예시: `251126_REGULAR`, `251201_EXTRA1`, `251205_EXTRA2`
- EXTRA 번호 범위: 0~20
- 정규식: `^(\d{6})_(REGULAR|EXTRA(\d{1,2}))$`

**레거시 참조**: `LY_Table/src/batch_merger.py` 라인 22

### 배치 파일명 규칙

**패턴**: `{YYMMDD}_{언어코드}_{배치타입}.xlsx`
- 예시: `251126_EN_REGULAR.xlsx`, `251201_CT_EXTRA1.xlsx`
- 정규식: `^(\d{6})_(EN|CT|CS|JA|TH|PT-BR|RU)_(.+)\.xlsx$`

**검증 규칙**:
1. 날짜(YYMMDD)는 폴더명의 날짜와 일치해야 함
2. 언어 코드는 7개 중 하나 (EN, CT, CS, JA, TH, PT-BR, RU)
3. 배치타입은 폴더명의 배치타입과 일치해야 함

**레거시 참조**: `LY_Table/src/batch_merger.py` 라인 25

### 기준 배치 (Base Batch)

**개념**: 병합의 기준이 되는 배치. 다른 배치들은 기준 배치에 추가되는 형태로 병합됩니다.

**역할**:
1. **병합 순서의 첫 번째**: 기준 배치가 항상 병합 순서의 첫 번째가 됩니다
2. **필드 우선순위**: Table, Source, Status, NOTE 등 메타데이터 필드는 기준 배치의 값을 우선 사용
3. **사용자 선택**: UI에서 라디오 버튼으로 어떤 배치를 기준으로 할지 선택 가능

**기본값**: `REGULAR` 배치가 있으면 자동 선택, 없으면 첫 번째 배치

**구현**:
```python
def sort_batches_with_base(batch_names: List[str], base_batch: str) -> List[str]:
    """배치명 정렬 (기준 배치 우선)

    Args:
        batch_names: 배치명 리스트
        base_batch: 기준 배치명

    Returns:
        정렬된 배치명 리스트 (base_batch가 첫 번째)
    """
    # 기준 배치 제외
    other_batches = [b for b in batch_names if b != base_batch]

    # 나머지 배치 정렬 (REGULAR 우선, EXTRA는 번호순)
    sorted_others = sorted(other_batches, key=lambda x: (
        0 if x == 'REGULAR' else 1,  # REGULAR가 먼저
        int(x.replace('EXTRA', '')) if x.startswith('EXTRA') else 0
    ))

    # 기준 배치를 첫 번째로
    return [base_batch] + sorted_others
```

**레거시 참조**: `LY_Table/src/batch_merger.py` 라인 172-206, `LY_Table/src/batch_ui.py` 라인 40-66

### 처리 규칙

**중복 제거 알고리즘**:

```python
def merge_batches_with_dedup(batch_dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """여러 배치 병합 및 중복 제거

    Args:
        batch_dfs: 배치별 DataFrame 리스트 (순서대로 적재, 최신이 마지막)

    Returns:
        중복 제거된 통합 DataFrame

    Raises:
        DataIntegrityError: 배치 내 중복 또는 Date 동일한 중복 발견 시
    """
    # 1. 배치 내 중복 검사
    for i, df in enumerate(batch_dfs):
        duplicates = df[df.duplicated(subset='KEY', keep=False)]
        if len(duplicates) > 0:
            dup_keys = duplicates['KEY'].unique().tolist()
            raise DataIntegrityError(
                f"배치 {i+1}에 중복 KEY 발견: {dup_keys}\n"
                f"수동으로 중복을 제거한 후 다시 시도하세요."
            )

    # 2. 전체 병합
    all_data = pd.concat(batch_dfs, ignore_index=True)

    # 3. 배치 간 중복 검사 및 처리
    duplicated_keys = all_data[all_data.duplicated(subset='KEY', keep=False)]['KEY'].unique()

    for key in duplicated_keys:
        rows = all_data[all_data['KEY'] == key]

        # Date 누락 검사
        if rows['Date'].isna().any():
            raise DataIntegrityError(
                f"KEY '{key}'의 일부 행에 Date가 누락되었습니다.\n"
                f"모든 행에 Date를 입력하세요."
            )

        dates = rows['Date'].unique()

        # Date 동일 검사
        if len(dates) == 1:
            raise DataIntegrityError(
                f"KEY '{key}'가 여러 배치에서 동일한 Date({dates[0]})로 존재합니다.\n"
                f"Date가 다른 경우에만 자동 병합됩니다.\n"
                f"수동으로 중복을 제거하세요."
            )

    # 4. Date 기준 최신 행만 유지
    # Date 컬럼: YYYY-MM-DD HH:MM 형식 문자열 (예: '2025-11-28 14:30')
    # 주의: 파일명의 날짜(YYMMDD)는 작명 목적, Date 컬럼(YYYY-MM-DD HH:MM)은 최신 데이터 선별 목적
    # datetime 비교로 정확한 정렬 (문자열 사전순도 정확하지만 명시적으로 datetime 사용 권장)
    all_data = all_data.sort_values('Date', ascending=False)  # 최신 먼저
    all_data = all_data.drop_duplicates(subset='KEY', keep='first')  # 첫 번째(최신) 유지
    all_data = all_data.sort_values('KEY')  # KEY 순서 복원

    return all_data.reset_index(drop=True)
```

**처리 규칙 설명**:
1. **배치 내 중복**: ❌ 오류 발생 → 사용자 수동 제거 필요
   - 예: Batch1에 KEY_A가 2번 존재 → 오류
2. **배치 간 중복 + Date 다름**: ✅ 최신 유지
   - 예: Batch1(Date=2025-11-28 14:30)에 KEY_A, Batch2(Date=2025-12-10 15:00)에 KEY_A → 2025-12-10 15:00 유지
3. **배치 간 중복 + Date 동일**: ❌ 오류 발생
   - 예: Batch1(Date=2025-11-28 14:30)에 KEY_A, Batch2(Date=2025-11-28 14:30)에 KEY_A → 오류
4. **Date 누락**: ❌ 오류 발생

**레거시 참조**: `LY_Table/src/batch_merger.py` 라인 70-132

**Status 자동 완료**:

**규칙**: 최종 병합된 데이터의 Status를 조건부로 변경

```python
STATUS_MAPPING = {
    "번역필요": "완료",
    "수정": "완료"
}

# Status 컬럼 (5번째, 인덱스 4) 값이 매핑에 있으면 변경
for row in final_data:
    if row[4] in STATUS_MAPPING:
        row[4] = STATUS_MAPPING[row[4]]
```

**변경 대상**:
- Status = "번역필요" → "완료"로 변경
- Status = "수정" → "완료"로 변경

**유지 대상**:
- Status = "기존" → 유지
- Status = "신규" → 유지
- 기타 다른 Status 값 → 유지

**처리 시퀀스** (적용 시점 명확화):
1. 각 배치 읽기 (7개 언어 파일씩)
2. 기준 배치를 첫 번째로 순차 적재 (`sort_batches_with_base()` 사용)
3. 배치 내 중복 검증
4. 배치 간 중복 검증 (Date 확인)
5. Date 기준 최신 행만 유지 (중복 제거)
6. **Status 자동 완료 적용** ← 여기! (`apply_status_completion()` 함수)
7. 파일 저장

**레거시 참조**: `legacy/LY_Table/src/batch_merger.py` 라인 135-169 `apply_status_completion()` 함수, 라인 1032-1036 호출 시점

### 출력

**기본 저장 위치**: 루트 폴더 내 `Output/` 하위 폴더
- 예: `D:\Work\LYGL\Output\`
- Output 폴더가 없으면 자동 생성
- 루트 폴더: 배치 폴더들의 부모 폴더

**파일명 규칙**: `{오늘날짜YYMMDD}_{언어코드}.xlsx`
- 예: `251211_EN.xlsx`, `251211_CT.xlsx`, `251211_CS.xlsx`, `251211_JA.xlsx`, `251211_TH.xlsx`, `251211_PT-BR.xlsx`, `251211_RU.xlsx`
- 7개 언어별 파일 생성

**내용**: 중복 제거 + Status 자동 완료된 전체 데이터

**레거시 참조**: `LY_Table/src/batch_merger.py` 라인 1057

---

## 🔍 Legacy Diff (레거시 비교)

### 입력

**2개 버전** (각 7개 파일):
```
비교1 폴더/ (이전 버전)
  ├── 251128_EN.xlsx
  └── ...

비교2 폴더/ (현재 버전)
  ├── 251210_EN.xlsx
  └── ...
```

### 처리 로직

**비교 알고리즘**:
```python
def generate_diff(old_dfs: Dict[str, pd.DataFrame],
                  new_dfs: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """두 버전 비교하여 변경 추적

    Args:
        old_dfs: 이전 버전 언어별 DataFrame {'EN': df, 'CT': df, ...}
        new_dfs: 현재 버전 언어별 DataFrame {'EN': df, 'CT': df, ...}

    Returns:
        Tuple[overview_df, detail_dfs]
        - overview_df: Overview 시트 (# | KEY | EN | CT | CS | JA | TH | PT-BR | RU)
        - detail_dfs: 언어별 상세 시트 {'EN': df, ...}
    """
    LANGS = ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']

    # 1. EN 기준 Status='기존'인 KEY만 추출
    en_old = old_dfs['EN']
    existing_keys = en_old[en_old['Status'] == '기존']['KEY'].tolist()

    # 2. Overview 시트 생성 (KEY 알파벳 순서로 정렬)
    # 레거시 동작: KEY 알파벳 순서로 정렬하여 예측 가능한 순서 제공
    existing_keys_sorted = sorted(existing_keys)

    overview_data = []
    detail_data = {lang: [] for lang in LANGS}

    for key in existing_keys_sorted:
        row = {'KEY': key}
        key_has_changes = False

        for lang in LANGS:
            # KEY 기준 매칭
            old_row = old_dfs[lang][old_dfs[lang]['KEY'] == key]
            new_row = new_dfs[lang][new_dfs[lang]['KEY'] == key]

            if len(old_row) == 0 or len(new_row) == 0:
                row[lang] = 'X'  # KEY 없음
                continue

            old_target = old_row['Target'].iloc[0]
            new_target = new_row['Target'].iloc[0]

            # Target 비교 (변경 여부)
            if old_target != new_target:
                row[lang] = 'O'  # 변경됨
                key_has_changes = True

                # 상세 시트에 추가
                detail_data[lang].append({
                    'Overview Index': len(overview_data) + 1,
                    'KEY': key,
                    'Source': new_row['Source'].iloc[0],
                    '이전 Target': old_target,
                    '현재 Target': new_target
                })
            else:
                row[lang] = 'X'  # 변경 안됨

        # 하나라도 변경된 경우만 Overview에 포함
        if key_has_changes:
            overview_data.append(row)

    # 3. Overview DataFrame 생성
    overview_df = pd.DataFrame(overview_data)
    overview_df.insert(0, '#', range(1, len(overview_df) + 1))

    # 4. 언어별 상세 DataFrame 생성
    detail_dfs = {}
    for lang in LANGS:
        if detail_data[lang]:
            detail_dfs[lang] = pd.DataFrame(detail_data[lang])
        else:
            # 변경 없으면 빈 DataFrame
            detail_dfs[lang] = pd.DataFrame(columns=['Overview Index', 'KEY', 'Source', '이전 Target', '현재 Target'])

    return overview_df, detail_dfs
```

**파일 저장**:
```python
from datetime import datetime

# 파일명 생성 (타임스탬프)
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
output_file = f"{timestamp}_DIFF.xlsx"

# Excel 파일에 다중 시트 저장
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Overview 시트
    overview_df.to_excel(writer, sheet_name='Overview', index=False)

    # 언어별 상세 시트
    for lang, detail_df in detail_dfs.items():
        detail_df.to_excel(writer, sheet_name=lang, index=False)
```

**레거시 참조**: `LY_Table/src/legacy_diff.py`

### 출력

**파일명**: `{YYYYMMDDHHMMSS}_DIFF.xlsx`
- 예시: `20251210180539_DIFF.xlsx` (2025년 12월 10일 18시 05분 39초)

**Excel 파일 구조** (다중 시트):

#### Overview 시트 (9개 컬럼)

```
# | KEY | EN | CT | CS | JA | TH | PT-BR | RU
```

**컬럼 설명**:
- **#**: 행 번호 (1부터 자동 증가)
- **KEY**: 문자열 고유 식별자
- **언어 컬럼** (EN, CT, CS, JA, TH, PT-BR, RU):
  - `O` (알파벳 O): 해당 언어에서 Target 변경됨
  - `X` (알파벳 X): 해당 언어에서 Target 변경 안됨

**예시 데이터**:
```
# | KEY                                    | EN | CT | CS | JA | TH | PT-BR | RU
1 | StringEssentialContent_DuplicateLogin  | O  | X  | X  | X  | X  | X     | X
2 | StringTemplate_ShortcutKey_Equals      | O  | O  | O  | O  | O  | O     | O
```

**의미**:
- Row 1: 영어만 변경됨
- Row 2: 모든 언어에서 변경됨

#### 언어별 상세 시트 (5개 컬럼)

**시트명**: EN, CT, CS, JA, TH, PT-BR, RU (7개 시트)

**컬럼 구조**:
```
Overview Index | KEY | Source | 이전 Target | 현재 Target
```

**컬럼 설명**:
- **Overview Index**: Overview 시트의 행 번호 (참조용)
- **KEY**: 문자열 고유 식별자
- **Source**: 원문 (한국어)
- **이전 Target**: 비교1 폴더(이전 버전)의 번역문
- **현재 Target**: 비교2 폴더(현재 버전)의 번역문

**특징**:
- 해당 언어에서 **변경된 행만** 표시 (Overview에서 O인 행만)
- 변경 안 된 행(X)은 포함하지 않음

**예시 데이터** (EN 시트):
```
Overview Index | KEY                                    | Source | 이전 Target | 현재 Target
1              | StringEssentialContent_DuplicateLogin  | 없음   |             | None
7              | StringTemplate_ShortcutKey_Equals      | =      |             | =
```

**레거시 참조**: `legacy/20251210180539_DIFF.xlsx` 실제 출력 파일

### 예외 처리

**변경사항 없음**:
- **조건**: 모든 '기존' Status 항목의 Target이 동일
- **메시지**: "변경된 항목이 없습니다. 모든 '기존' 상태 항목의 Target이 동일합니다."
- **동작**: 오류 표시, 파일 생성 안 함

**레거시 참조**: `LY_Table/src/legacy_diff.py` 라인 448-453

---

## 🎨 UI 설계

**상세 UI 와이어프레임**: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md#-lygl-탭-ui)

### 개요

**레이아웃**: 4개 큰 버튼 (Merge, Split, Batches, Diff) → 위저드 Dialog 시작

**동작 흐름**:
1. 사용자: 4개 버튼 중 하나 클릭
2. 해당 기능의 위저드 Dialog 표시
3. 위저드에서 파일/폴더/옵션 선택
4. [실행] 클릭 → 위저드 닫힘 → 워커 실행 + ProgressDialog 표시

### 위저드 Dialog 종류

| 위저드 | 기능 | 와이어프레임 링크 |
|--------|------|-------------------|
| **Merge** | 7개 언어 파일 선택 + 저장 위치 | [Merge 위저드](Sebastian-UI-Wireframes.md#위저드-dialog-lygl-merge) |
| **Split** | 통합 파일 선택 + 저장 폴더 | [Split 위저드](Sebastian-UI-Wireframes.md) |
| **Merge Batches** | 배치 폴더 목록 + 순서 조정 + 기준 배치 선택 | [Merge Batches 위저드](Sebastian-UI-Wireframes.md#위저드-dialog-lygl-merge-batches) |
| **Legacy Diff** | 2개 비교 폴더 선택 + 저장 위치 | [Legacy Diff 위저드](Sebastian-UI-Wireframes.md) |

**구현 참조**:
- 기능 버튼: [Sebastian-UI-Wireframes.md#기능-버튼-스타일-1](Sebastian-UI-Wireframes.md#기능-버튼-스타일-1)
- 위저드 Dialog: [Sebastian-UI-Wireframes.md#-위저드-dialog-lygl-merge](Sebastian-UI-Wireframes.md#-위저드-dialog-lygl-merge)
- 배치 목록 관리: [Sebastian-UI-Wireframes.md#배치-목록-항목](Sebastian-UI-Wireframes.md#배치-목록-항목)
- ProgressDialog: [Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog](Sebastian-PRD-Shared.md#1-진행도-dialog-progressdialog)

---

## ⚠️ 특이사항

1. **Date 컬럼 하위 호환**: 없어도 처리 가능 (빈 값)
2. **공백 보존**: strip() 사용 안 함 → Round-trip 무결성
3. **시트명 통일**: 모든 출력 파일 'Sheet1'

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 0.1.0 | 2025-12-10 | 초안 작성 | 재경 |
| 0.2.0 | 2025-12-11 | Date 형식 명확화 (YYYY-MM-DD HH:MM), 기준 배치 개념 추가, Round-trip 검증 방식 명시 (TDD) | 재경 |
| 0.3.0 | 2025-12-11 | KEY 대소문자 구분 명시, Legacy Diff Overview 정렬 순서 명시 (알파벳순), Status 자동 완료 시퀀스 명확화 | 재경 |
| 1.0.0 | 2025-12-11 | 배치 순서 병합 영향 명시, Split 에러 메시지 개선, 파일 개수 검증 순서 추가, 버튼 크기 일관성 주석 - 정제 완료 | 재경 |
| 1.1.0 | 2025-12-11 | 검수 반영: 배치 폴더/파일명 패턴 추가, Merge 파일 선택 방식 명시, Legacy Diff 예외 처리 추가, Merge Batches 출력 폴더 명시, 파일 크기 제한 참조 추가 | 재경 |
| 1.2.0 | 2025-12-12 | UI 설계 섹션 와이어프레임 참조로 변경, 위저드 아스키 UI 및 구현 코드 제거 | 재경 |
