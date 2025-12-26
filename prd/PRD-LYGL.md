# Sebastian PRD - LY/GL (LY Table)

**게임**: LY Table
**기능**: Merge/Split/Batches/Diff/StatusCheck
**버전**: v0.1.1
**상태**: Production

---

## 목차

1. [개요](#개요)
2. [Merge (병합)](#merge-병합)
3. [Split (분리)](#split-분리)
4. [Batches (배치 병합)](#batches-배치-병합)
5. [Diff (버전 비교)](#diff-버전-비교)
6. [Status Check (상태 검증)](#status-check-상태-검증)
7. [UI 디자인](#ui-디자인)
8. [데이터 검증](#데이터-검증)
9. [Round-trip 무결성](#round-trip-무결성)

---

## 개요

### 목적

LY Table 게임의 현지화 테이블을 관리하는 종합 도구입니다.

**5개 주요 기능**:
1. **Merge**: 7개 언어 파일 → 1개 통합 파일
2. **Split**: 1개 통합 파일 → 7개 언어 파일
3. **Batches**: 배치 병합 + Status 자동 완료 처리
4. **Diff**: 두 버전 비교 → 변경 사항 추적
5. **Status Check**: 언어별 Status 일치 검증

### 지원 언어 (7개)

| 언어 코드 | 언어 | 파일명 예시 |
|-----------|------|-------------|
| EN | English | EN.xlsx |
| CT | Traditional Chinese | CT.xlsx |
| CS | Simplified Chinese | CS.xlsx |
| JA | Japanese | JA.xlsx |
| TH | Thai | TH.xlsx |
| PT-BR | Portuguese (Brazil) | PT-BR.xlsx |
| RU | Russian | RU.xlsx |

### 파일 구조 (공통)

**언어별 파일** (Split 형식):
```
| Table | KEY | Source | Target | Status | NOTE | Date |
```

**통합 파일** (Merge 형식):
```
| Table | KEY | Source | Target_EN | Target_CT | ... | Target_RU | Status | NOTE | Date |
```

---

## Merge (병합)

### 기능

**7개 언어 파일 → 1개 통합 파일**

### 입력

- 7개 언어 파일 (EN, CT, CS, JA, TH, PT-BR, RU)
- 각 파일: `{언어코드}.xlsx`

### 출력

- 통합 파일: 사용자 지정 경로
- 예: `merged_lygl.xlsx`

### 알고리즘

```
1. 파일 검증
   - 정확히 7개 파일 (EN, CT, CS, JA, TH, PT-BR, RU)
   - 파일 존재 확인
   - 헤더 검증: [Table, KEY, Source, Target, Status, NOTE, Date]

2. EN 파일 (마스터) 로드
   - KEY, Table, Source, Status, NOTE, Date 추출
   - {KEY: {Table, Source, Status, NOTE, Date}} 딕셔너리 생성

3. 나머지 언어 파일 처리
   FOR EACH lang IN [CT, CS, JA, TH, PT-BR, RU]:
       - 파일 로드
       - KEY 일치 확인 (EN과 동일해야 함)
       - Table, Source 일치 확인
       - Target → Target_{lang} 저장

4. 통합 Workbook 생성
   - 컬럼: Table, KEY, Source, Target_EN, Target_CT, ..., Target_RU, Status, NOTE, Date
   - EN 데이터 기준으로 행 생성
   - 각 언어의 Target 값 채우기

5. Excel 서식 적용
   - 헤더: Bold, 연한 파란색 배경
   - 데이터: 왼쪽 정렬
   - 빈 값: "" (빈 문자열)

6. 파일 저장
   - openpyxl로 저장
```

### 데이터 검증

**KEY 일치**:
```python
if key in en_data:
    # Table, Source 일치 확인
    if en_data[key]['Table'] != table:
        raise ValidationError(f"Table 불일치: {key}")
    if en_data[key]['Source'] != source:
        raise ValidationError(f"Source 불일치: {key}")
else:
    raise ValidationError(f"KEY 불일치: {key} (EN에 없음)")
```

---

## Split (분리)

### 기능

**1개 통합 파일 → 7개 언어 파일**

### 입력

- 통합 파일 (Merge 형식)

### 출력

- 7개 언어 파일: `{언어코드}.xlsx`
- 출력 폴더: 사용자 지정

### 알고리즘

```
1. 통합 파일 로드
   - 헤더 검증: Table, KEY, Source, Target_EN, ..., Target_RU, Status, NOTE, Date
   - 데이터 수집

2. 각 언어별 파일 생성
   FOR EACH lang IN [EN, CT, CS, JA, TH, PT-BR, RU]:
       - Workbook 생성
       - 컬럼: Table, KEY, Source, Target, Status, NOTE, Date
       - Target = Target_{lang} 값
       - 빈 값: "" (빈 문자열)
       - Excel 서식 적용
       - 파일 저장: {lang}.xlsx
```

### Round-trip 보장

**Merge → Split → Merge 무결성 검증**:

```python
# 1. 원본 7개 언어 파일 → 병합
merged_wb = merge(language_files)

# 2. 병합 파일 → 7개 분리
split_files = split(merged_wb, output_folder)

# 3. 분리된 7개 → 재병합
remerged_wb = merge(split_files)

# 4. 원본 병합과 재병합 비교
assert merged_wb == remerged_wb  # 100% 일치
```

---

## Batches (배치 병합)

### 기능

**여러 배치 파일 병합 + Status 자동 완료 처리**

### 배치 구조

```
Root Folder/
├── Batch 1/
│   ├── EN.xlsx
│   ├── CT.xlsx
│   └── ...
├── Batch 2/
│   ├── EN.xlsx
│   └── ...
└── Batch 3/
    └── ...
```

### 입력

- Root Folder (배치 폴더들이 위치)
- 선택한 배치 리스트 (예: [Batch 1, Batch 2])
- Base Batch (기준 배치, 예: Batch 1)
- Auto Complete 옵션 (Status 자동 완료 처리)

### 출력

- 병합된 통합 파일: `merged_batches.xlsx`

### 알고리즘

```
1. 배치 스캔
   - Root Folder 내 모든 하위 폴더 확인
   - 7개 언어 파일이 있는 폴더만 배치로 인식
   - 배치 정보 수집: {배치명: {언어코드: 파일 수}}

2. Base Batch 병합
   - Base Batch의 7개 언어 파일 → 통합 병합
   - {KEY: {Table, Source, Target_*, Status, NOTE, Date}} 딕셔너리

3. 나머지 배치 처리
   FOR EACH batch IN selected_batches:
       IF batch == base_batch:
           SKIP

       - 배치의 7개 언어 파일 → 통합 병합
       - Base와 KEY 비교:
           - 새 KEY: 추가
           - 기존 KEY: Target 값 업데이트 (빈 값만)

4. Status 자동 완료 (Auto Complete = True)
   - 모든 Target_{언어} 값이 채워진 KEY → Status = "완료"

5. 중복 제거
   - 동일한 KEY는 마지막 배치 우선

6. Excel 저장
   - 통합 형식으로 저장
```

### Auto Complete 로직

```python
def apply_auto_complete(merged_data):
    """모든 Target 값이 있으면 Status = '완료'"""
    for key, data in merged_data.items():
        all_filled = all(
            data.get(f'Target_{lang}', '').strip() != ''
            for lang in ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']
        )

        if all_filled:
            merged_data[key]['Status'] = '완료'
```

---

## Diff (버전 비교)

### 기능

**두 버전의 폴더 비교 → 변경 사항 추적**

### 입력

- 폴더 1 (이전 버전, 7개 언어 파일)
- 폴더 2 (현재 버전, 7개 언어 파일)

### 출력

- Diff 파일: `diff_report.xlsx`
- 변경 사항 요약

### Diff 유형

| 유형 | 설명 | 색상 |
|------|------|------|
| **Added** | 새로 추가된 KEY | 초록색 |
| **Deleted** | 삭제된 KEY | 빨간색 |
| **Modified** | 값이 변경된 KEY | 노란색 |
| **Unchanged** | 변경 없음 | 기본 |

### 알고리즘

```
1. 폴더 1, 2 각각 Merge
   - 7개 언어 파일 → 통합 병합
   - merged1, merged2

2. KEY 비교
   keys1 = set(merged1.keys())
   keys2 = set(merged2.keys())

   added_keys = keys2 - keys1      # 새로 추가
   deleted_keys = keys1 - keys2    # 삭제됨
   common_keys = keys1 & keys2     # 공통

3. 공통 KEY 값 비교
   FOR EACH key IN common_keys:
       IF merged1[key] != merged2[key]:
           modified_keys.add(key)

4. Diff 리포트 생성
   - Added Keys: 초록색 배경
   - Deleted Keys: 빨간색 배경
   - Modified Keys: 노란색 배경
   - 변경 전/후 값 비교

5. Excel 저장
   - Sheet1: Added
   - Sheet2: Deleted
   - Sheet3: Modified
   - Sheet4: Summary (통계)
```

### 출력 형식

**Sheet1: Added**:
```
| Table | KEY | Source | Target_EN | ... | Status |
```

**Sheet3: Modified**:
```
| Table | KEY | Field | Before | After |
| ...   | ... | Target_EN | "Hello" | "Hi" |
| ...   | ... | Status | "번역필요" | "완료" |
```

---

## Status Check (상태 검증)

### 기능

**7개 언어 파일의 Status 일치 검증**

### 입력

- 7개 언어 파일 (EN, CT, CS, JA, TH, PT-BR, RU)

### 출력

- Status Check 리포트: `status_check_report.xlsx`
- 불일치 KEY 목록

### 알고리즘

```
1. 7개 언어 파일 로드
   FOR EACH lang IN [EN, CT, CS, JA, TH, PT-BR, RU]:
       - 파일 읽기
       - {KEY: Status} 매핑 수집

2. EN 기준 비교
   FOR EACH key IN en_keys:
       en_status = en_data[key]

       FOR EACH lang IN [CT, CS, JA, TH, PT-BR, RU]:
           lang_status = lang_data.get(key, None)

           IF lang_status != en_status:
               # 불일치 발견
               mismatch_list.append({
                   'KEY': key,
                   'EN_Status': en_status,
                   f'{lang}_Status': lang_status
               })

3. 통계 계산
   - 전체 KEY 수
   - 일치 KEY 수
   - 불일치 KEY 수
   - 언어별 Status 분포

4. Excel 리포트 생성
   - Sheet1: Mismatches (불일치 KEY 목록)
   - Sheet2: Statistics (통계)
   - Sheet3: Language Summary (언어별 요약)
```

### 출력 형식

**Sheet1: Mismatches**:
```
| KEY | Table | EN_Status | CT_Status | CS_Status | ... | RU_Status |
| key1 | Table1 | 완료 | 번역필요 | 완료 | ... | 완료 |
```

**Sheet2: Statistics**:
```
| 항목 | 값 |
| 전체 KEY 수 | 1000 |
| 일치 KEY 수 | 950 |
| 불일치 KEY 수 | 50 |
| 일치율 | 95% |
```

---

## UI 디자인

### LY/GL 탭 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Merge                        7 → 1           →  │   │
│  │ 언어별 파일 → 통합 생성                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Split                        1 → 7           →  │   │
│  │ 통합 파일 → 언어별 분리                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Batches                      배치 병합        →  │   │
│  │ Status 자동 완료 처리                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Diff                         버전 비교        →  │   │
│  │ 변경 사항 추적                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Status Check                 Status 통일 검증 →  │   │
│  │ 언어별 Status 일치 확인                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 리스트 버튼 (수직 레이아웃)

**크기**: 최소 높이 64px

**구조**:
```
┌──────────────────────────────────────────┐
│ Merge                          7 → 1  →  │
│ 언어별 파일 → 통합 생성                   │
└──────────────────────────────────────────┘
```

**스타일**:
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border Radius: `8px`
- Padding: `10px 16px`

**Hover**:
- Background: `#F8F9FA`
- Border Color: `#5E35B1`

### Wizard Dialog

**모든 기능은 Wizard 형식**:

1. **MergeWizard**: 7개 파일 선택 + 출력 경로
2. **SplitWizard**: 통합 파일 선택 + 출력 폴더
3. **BatchWizard**: Root 폴더 + 배치 선택 + Auto Complete
4. **DiffWizard**: 폴더 1, 2 선택 + 출력 경로
5. **StatusCheckWizard**: 7개 파일 선택 + 출력 경로

**공통 구조**:
```python
class SomeWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self._setup_ui()

    def get_data(self) -> Dict[str, Any]:
        """사용자가 선택한 데이터 반환"""
        return {
            'input_files': self.selected_files,
            'output_path': self.output_path,
            # ...
        }
```

---

## 데이터 검증

### 공통 검증 규칙

**validator.py**:

```python
def validate_language_files(files: List[Path]):
    """7개 언어 파일 검증"""
    if len(files) != 7:
        raise ValidationError(f"7개 파일 필요 (현재: {len(files)}개)")

    lang_codes = set()
    for file in files:
        lang = extract_language_code(file.name)
        if lang not in VALID_LANGUAGES:
            raise ValidationError(f"잘못된 언어 코드: {lang}")
        lang_codes.add(lang)

    if lang_codes != set(VALID_LANGUAGES):
        raise ValidationError("EN, CT, CS, JA, TH, PT-BR, RU 모두 필요")

def validate_headers(actual: List[str], expected: List[str], file_name: str):
    """헤더 검증 (대소문자 구분)"""
    if actual != expected:
        raise ValidationError(
            f"헤더 불일치:\n파일: {file_name}\n"
            f"기대: {expected}\n실제: {actual}"
        )

def validate_key(key: Any, row: int, file_name: str):
    """KEY 검증 (None/빈 값 체크)"""
    if not key or str(key).strip() == "":
        raise ValidationError(f"빈 KEY:\n파일: {file_name}\n행: {row}")
```

### 에러 메시지

**error_messages.py**:

```python
def get_user_friendly_message(error_type: str, **kwargs) -> str:
    """사용자 친화적 에러 메시지"""
    messages = {
        'FILE_NOT_FOUND': "파일을 찾을 수 없습니다:\n{path}",
        'INVALID_HEADER': "엑셀 헤더가 올바르지 않습니다:\n기대: {expected}\n실제: {actual}",
        'KEY_MISMATCH': "KEY가 일치하지 않습니다:\n파일: {file}\nKEY: {key}",
        'TABLE_MISMATCH': "Table 값이 일치하지 않습니다:\nKEY: {key}\nEN: {en_table}\n{lang}: {lang_table}",
        'SOURCE_MISMATCH': "Source 값이 일치하지 않습니다:\nKEY: {key}\nEN: {en_source}\n{lang}: {lang_source}",
    }
    return messages.get(error_type, "알 수 없는 에러").format(**kwargs)
```

---

## Round-trip 무결성

### 테스트 (37개)

**tests/test_lygl_roundtrip.py**:

```python
@pytest.mark.parametrize("test_case", [
    "basic_7files",
    "empty_target",
    "special_chars",
    "unicode",
    "large_dataset",
    # ... 37개 케이스
])
def test_roundtrip(test_case):
    """Merge → Split → Merge 무결성 검증"""
    # 1. 원본 파일 로드
    original_files = load_test_case(test_case)

    # 2. Merge
    merged_wb = merge(original_files)
    merged_data = extract_data(merged_wb)

    # 3. Split
    split_folder = tempfile.mkdtemp()
    split(merged_wb, split_folder)
    split_files = [Path(split_folder) / f"{lang}.xlsx" for lang in VALID_LANGUAGES]

    # 4. Re-Merge
    remerged_wb = merge(split_files)
    remerged_data = extract_data(remerged_wb)

    # 5. 비교
    assert merged_data == remerged_data, f"Round-trip 실패: {test_case}"
```

**결과**: 37개 테스트 모두 통과 ✅

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-12-24
