# CSV 복원 기능 엣지 케이스 분석

**분석일**: 2025-12-26
**분석 파일**: `legacy\.csv test\251216_lygl-ymir_cup_EXTRA0_*.csv`

---

## 📊 발견된 패턴 분류

### 패턴 1: 필드 따옴표 누락/추가

| key-name | 언어 | Original | Exported | 복원 목표 |
|----------|------|----------|----------|-----------|
| key-name7 | ko | `"서버의 명예&#44;..."` | `서버의 명예&#44;...` | `"서버의 명예&#44;..."` |
| key-name3 | ko | `텍스트` | `"텍스트"` | `텍스트` |
| key-name3 | en | `"Quoted Text"` | `Quoted Text` | `"Quoted Text"` |

**분석**:
- memoQ가 필드 따옴표를 임의로 추가/제거함
- 원본의 따옴표 **유무**를 정확히 파악하여 복원 필요

---

### 패턴 2: HTML 태그 내 따옴표 Escape

| key-name | 언어 | Original | Exported | 복원 목표 |
|----------|------|----------|----------|-----------|
| key-name46 | ko | `...&#39;<span class="green">레이저</span>&#39;...` | `"...'<span class=""green"">레이저</span>'..."` | `...'<span class="green">레이저</span>'...` |
| key-name67 | pt | `&#39;이그드라실 컵&#39;` | `"""Copa de Yggdrasil"" concedida..."` | `"Copa de Yggdrasil" concedida...` |

**분석**:
- memoQ가 HTML 태그 내 따옴표를 RFC 4180 규격에 맞게 escape (`"` → `""`)
- 원본처럼 단일 따옴표(`"`)로 복원 필요
- **필드 레벨 따옴표**도 함께 복원 (key-name46은 없었음, key-name67 pt는 있었음)

---

### 패턴 3: 작은따옴표 (Single Quote)

| key-name | 언어 | Original | Exported | 복원 목표 |
|----------|------|----------|----------|-----------|
| key-name20 | ko | `&#39;누가 전장을...&#39;` | `&#39;누가 전장을...&#39;` | `&#39;누가 전장을...&#39;` |
| key-name34 | ko | `&#39;최후의 서버...&#39;` | `&#39;최후의 서버...&#39;` | `&#39;최후의 서버...&#39;` |

**분석**:
- 작은따옴표(`'`)는 CSV 특수문자가 아니므로 memoQ가 건드리지 않음
- 복원 불필요 (그대로 유지)

---

### 패턴 4: 괄호 필드

| key-name | 언어 | Original | Exported | 복원 목표 |
|----------|------|----------|----------|-----------|
| key-name48 | ko | `(2025. 12. 26 ~ 2026. 01. 23)` | `(2025. 12. 26 ~ 2026. 01. 23)` | `(2025. 12. 26 ~ 2026. 01. 23)` |
| key-name77 | ko | `(오프라인 대회...)` | `(오프라인 대회...)` | `(오프라인 대회...)` |

**분석**:
- 괄호는 CSV 특수문자가 아니므로 변경 없음
- 복원 불필요

---

### 패턴 5: 쉼표 포함 필드 (&#44; HTML Entity)

| key-name | 언어 | Original | Exported | 복원 목표 |
|----------|------|----------|----------|-----------|
| key-name7 | ko | `"서버의 명예&#44; 클랜의 전략&#44;..."` | `서버의 명예&#44; 클랜의 전략&#44;...` | `"서버의 명예&#44; 클랜의 전략&#44;..."` |
| key-name5 | ko | `명예를 향한 전쟁의 시작&#44;` | `명예를 향한 전쟁의 시작&#44;` | `명예를 향한 전쟁의 시작&#44;` |

**분석**:
- `&#44;`는 HTML entity (쉼표 escape)이므로 CSV 파싱에 영향 없음
- 실제 쉼표(`,`)가 아니므로 따옴표 불필요
- **원본에 따옴표가 있었는지 여부**만 복원

---

### 패턴 6: 복합 패턴 (필드 따옴표 + 내부 escape)

**가장 복잡한 케이스**: key-name46 ko 필드

**Original** (raw text):
```
각 지역의 대표 서버들이 세계적인 게이밍 브랜드 '<span class="green">레이저(Razer)</span>'의 싱가포르 글로벌 HQ에서 최후의 왕관을 두고 세계 최강의 자리를 가립니다.
```
- 필드 따옴표: **없음**
- HTML 내 따옴표: `class="green"` (1개)

**Exported** (raw text):
```
"각 지역의 대표 서버들이 세계적인 게이밍 브랜드 '<span class=""green"">레이저(Razer)</span>'의 싱가포르 글로벌 HQ에서 최후의 왕관을 두고 세계 최강의 자리를 가립니다."
```
- 필드 따옴표: **있음** (memoQ가 추가)
- HTML 내 따옴표: `class=""green""` (2개로 escape)

**Restored** (목표):
```
각 지역의 대표 서버들이 세계적인 게이밍 브랜드 '<span class="green">레이저(Razer)</span>'의 싱가포르 글로벌 HQ에서 최후의 왕관을 두고 세계 최강의 자리를 가립니다.
```
- 필드 따옴표: **없음** (원본 패턴)
- HTML 내 따옴표: `class="green"` (1개로 복원)

**복원 로직**:
1. 원본에서 필드 따옴표 없음 확인
2. Export에서 데이터 읽기 (pandas가 자동으로 `""` → `"` unescape)
3. Restored에 필드 따옴표 없이 저장

---

## 🔍 Raw Text 파싱 필요성

### CSV Reader의 한계

**Python csv.reader 사용 시**:
```python
import csv
with open('original.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row[0])  # 이미 파싱된 값, 따옴표 정보 손실
```

- ✅ 편리함, 안전함
- ❌ 원본에 따옴표가 있었는지 알 수 없음
- ❌ `"필드"` vs `필드` 구분 불가

### Raw Text 파싱 시**:
```python
with open('original.csv') as f:
    line = f.readline().strip()
    # "field1",field2,"field3"
    # ↑ 따옴표 유무 직접 파악 가능
```

- ✅ 정확한 따옴표 정보 획득
- ❌ 복잡한 케이스 처리 어려움 (줄바꿈, nested quotes)
- ❌ 수동 구현 필요

---

## 🎯 핵심 요구사항 정리

### 요구사항 1: 필드 레벨 따옴표 복원

**입력**:
- Original: `"필드"` (따옴표 있음)
- Export: `필드` (memoQ가 제거)

**출력**:
- Restored: `"필드"` (원본 패턴 복원)

### 요구사항 2: 필드 내부 이중 따옴표 Unescape

**입력**:
- Original: `<span class="green">` (따옴표 1개)
- Export: `<span class=""green"">` (따옴표 2개로 escape)

**출력**:
- Restored: `<span class="green">` (따옴표 1개로 복원)

### 요구사항 3: 복합 케이스

**입력**:
- Original: `각 지역의... '<span class="green">...'` (필드 따옴표 X, 내부 따옴표 1개)
- Export: `"각 지역의... '<span class=""green"">..."'` (필드 따옴표 O, 내부 따옴표 2개)

**출력**:
- Restored: `각 지역의... '<span class="green">...'` (필드 따옴표 X, 내부 따옴표 1개)

---

## 🧩 Raw CSV 파싱 알고리즘 설계

### 상태 머신 기반 파서

```python
def _parse_csv_line_raw(line: str) -> List[Tuple[str, bool]]:
    """CSV 라인을 수동 파싱 (상태 머신)

    상태:
        - FIELD_START: 필드 시작
        - IN_QUOTED_FIELD: 따옴표로 감싼 필드 내부
        - IN_UNQUOTED_FIELD: 따옴표 없는 필드 내부
        - AFTER_QUOTE: 따옴표 닫힌 직후 (다음 문자 확인 필요)

    Returns:
        [(field_value, has_quotes), ...]
        - field_value: unescape된 필드 값 ("" → ")
        - has_quotes: 필드에 따옴표가 있었는지 여부
    """
    STATE_FIELD_START = 'field_start'
    STATE_IN_QUOTED = 'in_quoted'
    STATE_IN_UNQUOTED = 'in_unquoted'
    STATE_AFTER_QUOTE = 'after_quote'

    fields = []
    current_field = []
    has_quotes = False
    state = STATE_FIELD_START

    i = 0
    while i < len(line):
        char = line[i]

        if state == STATE_FIELD_START:
            if char == '"':
                # 따옴표로 시작하는 필드
                has_quotes = True
                state = STATE_IN_QUOTED
            elif char == ',':
                # 빈 필드
                fields.append(('', False))
            else:
                # 일반 필드
                current_field.append(char)
                state = STATE_IN_UNQUOTED

        elif state == STATE_IN_QUOTED:
            if char == '"':
                # 따옴표 발견 - escape인지 닫는 따옴표인지 확인
                if i + 1 < len(line) and line[i + 1] == '"':
                    # Escape된 따옴표 ("")
                    current_field.append('"')
                    i += 1  # 다음 " 건너뛰기
                else:
                    # 필드 닫는 따옴표
                    state = STATE_AFTER_QUOTE
            else:
                current_field.append(char)

        elif state == STATE_IN_UNQUOTED:
            if char == ',':
                # 필드 종료
                fields.append((''.join(current_field), has_quotes))
                current_field = []
                has_quotes = False
                state = STATE_FIELD_START
            else:
                current_field.append(char)

        elif state == STATE_AFTER_QUOTE:
            if char == ',':
                # 필드 종료
                fields.append((''.join(current_field), has_quotes))
                current_field = []
                has_quotes = False
                state = STATE_FIELD_START
            else:
                # 예상치 못한 문자 (에러)
                raise ValueError(f"따옴표 닫힌 후 예상치 못한 문자: {char}")

        i += 1

    # 마지막 필드
    if state != STATE_FIELD_START:
        fields.append((''.join(current_field), has_quotes))

    return fields
```

---

## 🧪 테스트 케이스 설계

### 테스트 1: 단순 따옴표 복원

**Input**:
```csv
key-name,ko,en
key1,"텍스트",Text
```

**Expected**:
- `(0, 'ko')`: `('텍스트', True)` - 따옴표 있음
- `(0, 'en')`: `('Text', False)` - 따옴표 없음

### 테스트 2: 이중 따옴표 Escape

**Input**:
```csv
key-name,ko
key1,"<span class=""green"">텍스트</span>"
```

**Expected**:
- `(0, 'ko')`: `('<span class="green">텍스트</span>', True)`
- Unescape: `""` → `"`

### 테스트 3: 복합 패턴

**Input**:
```csv
key-name,ko
key1,각 지역의... '<span class="green">레이저</span>'
```

**Expected**:
- `(0, 'ko')`: `('각 지역의... \'<span class="green">레이저</span>\'', False)`
- 필드 따옴표: 없음
- 내부 작은따옴표, HTML 따옴표: 그대로 유지

### 테스트 4: 빈 필드

**Input**:
```csv
key-name,ko,en
key1,,Text
key2,"",Text2
```

**Expected**:
- `(0, 'ko')`: `('', False)` - 빈 필드, 따옴표 없음
- `(1, 'ko')`: `('', True)` - 빈 필드, 따옴표 있음

### 테스트 5: 줄바꿈 포함 필드

**Input**:
```csv
key-name,ko
key1,"첫 줄
두 번째 줄"
```

**Expected**:
- `(0, 'ko')`: `('첫 줄\n두 번째 줄', True)`
- 따옴표 있음, 줄바꿈 포함

---

## 🔧 복원 저장 알고리즘 설계

### 저장 로직 (Manual CSV Writing)

```python
def _save_csv_with_original_pattern(
    df: pd.DataFrame,
    output_path: str,
    original_pattern: Dict
) -> None:
    """DataFrame을 원본 패턴으로 CSV 저장

    Args:
        df: 저장할 DataFrame (export 데이터)
        output_path: 출력 경로
        original_pattern: {(row_idx, col): {'has_field_quotes': bool}}
    """
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        # 헤더 작성 (따옴표 없이)
        f.write(','.join(df.columns) + '\n')

        # 데이터 작성
        for row_idx, row in df.iterrows():
            row_parts = []

            for col in df.columns:
                field_value = str(row[col])
                pattern = original_pattern.get((row_idx, col), {})
                has_quotes = pattern.get('has_field_quotes', False)

                if has_quotes:
                    # 따옴표로 감싸기
                    # 필드 내부 따옴표는 escape (" → "")
                    escaped = field_value.replace('"', '""')
                    formatted = f'"{escaped}"'
                else:
                    # 따옴표 없이
                    formatted = field_value

                row_parts.append(formatted)

            f.write(','.join(row_parts) + '\n')
```

**주의사항**:
- Export 데이터는 **pandas로 읽으므로 이미 unescape됨** (`""` → `"`)
- 원본 패턴대로 저장 시 **다시 escape 필요** (`"` → `""`) - **필드 따옴표가 있을 때만**

---

## ⚠️ 엣지 케이스 및 대응

### 엣지 케이스 1: 필드 내부 줄바꿈

**예시**:
```csv
key-name,ko
key1,"첫 줄
두 번째 줄"
```

**대응**:
- 상태 머신에서 `STATE_IN_QUOTED` 상태일 때 줄바꿈도 필드 내용으로 처리
- 여러 줄을 읽어야 할 수 있음

### 엣지 케이스 2: 필드 끝 공백

**예시**:
```csv
key-name,ko
key1,"텍스트  ",Text
```

**대응**:
- 공백도 데이터의 일부이므로 보존
- strip() 사용 금지

### 엣지 케이스 3: 특수문자 (유니코드)

**예시**:
```csv
key-name,ko,th
key1,한글,ภาษาไทย
```

**대응**:
- UTF-8 인코딩 사용 (`encoding='utf-8-sig'`)
- BOM 처리 (`utf-8-sig`)

### 엣지 케이스 4: 빈 라인

**예시**:
```csv
key-name,ko

key1,텍스트
```

**대응**:
- 빈 라인은 무시 (데이터 행으로 처리하지 않음)

---

## 📐 알고리즘 복잡도 분석

### 시간 복잡도

**파싱**:
- `O(n * m * L)` - n개 행, m개 컬럼, L은 평균 필드 길이
- 실제: 10,000행 × 9컬럼 × 100자 ≈ 9M 문자 처리
- 예상 시간: < 2초

**복원**:
- `O(n * m)` - 각 필드마다 패턴 조회 및 포맷팅
- 예상 시간: < 1초

**총 예상 시간**: < 5초 (목표 달성 가능)

### 공간 복잡도

- `original_pattern` 딕셔너리: `O(n * m)` - 10,000 × 9 = 90,000개 항목
- 메모리: 약 10MB (충분히 작음)

---

## 🛠️ 구현 계획 수정

### Phase 1: Raw CSV 파서 구현

**파일**: `core/common/csv_parser.py` (새 파일)

**함수**:
1. `parse_csv_line_raw(line: str) -> List[Tuple[str, bool]]` - 상태 머신 파서
2. `analyze_csv_pattern(csv_path: str) -> Dict` - 전체 파일 분석
3. `save_csv_with_pattern(df, output_path, pattern)` - 패턴 기반 저장

### Phase 2: csv_restore.py 수정

**변경 사항**:
1. `_analyze_quote_pattern()` → `analyze_csv_pattern()` 사용
2. `_save_csv_with_quotes()` → `save_csv_with_pattern()` 사용
3. 복원 로직 단순화 (export 데이터 + 원본 패턴)

### Phase 3: 테스트 강화

**추가 테스트**:
1. HTML 태그 내 따옴표 escape
2. 복합 패턴 (필드 따옴표 + 내부 escape)
3. 줄바꿈 포함 필드
4. 빈 필드 (따옴표 있음 vs 없음)

---

## 🎯 구현 우선순위

### Priority 1: 상태 머신 파서 (핵심)
- `csv_parser.py` 구현
- 단위 테스트 작성 (10개 이상)

### Priority 2: 복원 로직 수정
- `csv_restore.py` 재구현
- 패턴 기반 저장 로직

### Priority 3: 통합 테스트
- 실제 파일로 검증 (251216_lygl-ymir_cup_EXTRA0_*)
- 원본 vs 복원 비교 (100% 일치 목표)

---

## ✅ 다음 단계

상세 분석이 완료되었습니다. 이제 구현을 시작하시겠습니까?

**구현 예상 시간**: 2-3시간
**복잡도**: 중상
**성공 확률**: 높음 (알고리즘 명확함)
