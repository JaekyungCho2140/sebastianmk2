# LY/GL 현지화 테이블 병합/분할 도구

**버전**: 1.3.0
**게임**: Legend of YMIR MMORPG
**목적**: 다국어 번역 테이블 관리 자동화

---

## 📋 개요

Legend of YMIR의 게임 문자열 다국어 번역 관리를 위한 Excel 파일 처리 도구입니다.

### 지원 언어 (7개국)
- 🇬🇧 영어 (EN)
- 🇹🇼 중국어 번체 (CT)
- 🇨🇳 중국어 간체 (CS)
- 🇯🇵 일본어 (JA)
- 🇹🇭 태국어 (TH)
- 🇧🇷 포르투갈어 브라질 (PT-BR)
- 🇷🇺 러시아어 (RU)

### 주요 기능
- **🔀 Merge**: 7개 언어별 파일 → 1개 통합 파일 (번역 검수용)
- **🔗 Split**: 1개 통합 파일 → 7개 언어별 파일 (게임 적용용)
- **📦 Merge Batches**: 여러 배치 병합 + 중복 제거 (신규 v1.3.0)

---

## 🚀 빠른 시작

### 방법 1: 실행 파일 사용 (권장)
1. `LY_Table_Tool.exe` 다운로드
2. 더블클릭으로 실행
3. **Merge** 또는 **Split** 버튼 클릭
4. 파일 선택 후 작업 완료

### 방법 2: Python 직접 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 프로그램 실행
python src/main.py
```

---

## 📖 사용 방법

### 🔀 Merge (병합)
**언어별 파일 7개를 하나의 통합 파일로 병합**

#### 입력 파일
- `251128_EN.xlsx`
- `251128_CT.xlsx`
- `251128_CS.xlsx`
- `251128_JA.xlsx`
- `251128_TH.xlsx`
- `251128_PT-BR.xlsx`
- `251128_RU.xlsx`

각 파일 구조 (7개 컬럼):
```
Table | KEY | Source | Target | Status | NOTE | Date
```

#### 출력 파일
- `251128_LYGL_StringALL.xlsx`

통합 파일 구조 (13개 컬럼):
```
Table | KEY | Source | Target_EN | Target_CT | Target_CS |
Target_JA | Target_TH | Target_PT | Target_RU | Status | NOTE | Date
```

#### 사용 순서
1. **Merge** 버튼 클릭
2. 7개 언어 파일 모두 선택 (Ctrl+클릭)
3. 저장할 위치와 파일명 지정
4. 완료 메시지 확인

---

### 🔗 Split (분할)
**하나의 통합 파일을 7개 언어별 파일로 분할**

#### 입력 파일
- `251128_LYGL_StringALL.xlsx` (13개 컬럼)

#### 출력 파일
- `251128_EN.xlsx`
- `251128_CT.xlsx`
- `251128_CS.xlsx`
- `251128_JA.xlsx`
- `251128_TH.xlsx`
- `251128_PT-BR.xlsx`
- `251128_RU.xlsx`

각 파일 구조 (7개 컬럼):
```
Table | KEY | Source | Target | Status | NOTE | Date
```

#### 사용 순서
1. **Split** 버튼 클릭
2. 통합 파일 선택
3. 저장할 디렉토리 선택
4. 7개 파일 생성 확인

---

## ⚠️ 중요 사항

### 파일명 규칙
```
YYMMDD_언어코드.xlsx        (언어별 파일)
YYMMDD_LYGL_StringALL.xlsx  (통합 파일)
```

예시:
- ✅ `251128_EN.xlsx` (올바름)
- ❌ `EN.xlsx` (잘못됨 - 날짜 누락)

### 데이터 무결성 규칙
1. **KEY 기준 매칭**: 모든 언어 파일의 KEY가 일치해야 함
2. **EN = 마스터**: EN 파일이 기준, 다른 파일은 EN의 KEY를 따름
3. **필드 일치**: Table, Source, Status, NOTE, Date는 모든 언어에서 동일
4. **공백 보존**: 텍스트 좌우 공백은 원본 그대로 유지

### 검증 에러
다음 경우 에러가 발생합니다:
- ❌ 파일 수가 7개가 아닐 때
- ❌ KEY가 일치하지 않을 때
- ❌ Table/Source/Status/NOTE/Date가 불일치할 때
- ❌ 날짜가 파일마다 다를 때

---

## 🎯 실전 활용 사례

### Case 1: 번역 검수
```
언어별 파일 7개 → [Merge] → 통합 파일 1개
→ Excel에서 모든 언어 동시 확인/수정
→ [Split] → 언어별 파일 7개
→ 게임에 적용
```

### Case 2: 새 번역 추가
```
통합 파일 열기
→ 새 행 추가 (모든 Target 컬럼 작성)
→ [Split] → 언어별 파일 생성
→ 게임에 적용
```

### Case 3: 번역 수정
```
언어별 파일에서 수정
→ [Merge] → 통합 파일 생성
→ 전체 검토
→ [Split] → 최종 파일 생성
```

---

## 📊 처리 성능

| 항목 | 성능 |
|------|------|
| 처리 행 수 | ~49,600행 |
| Merge 시간 | 약 2-3초 |
| Split 시간 | 약 2-3초 |
| 파일 크기 | 언어별 ~3MB, 통합 ~20MB |

---

## 🔧 기술 스펙

### 시스템 요구사항
- **OS**: Windows 10 이상
- **Python**: 3.8+ (실행 파일 사용 시 불필요)
- **Excel**: Microsoft Excel 2016 이상 (파일 열람용)

### 의존성
```
openpyxl >= 3.1.2      # Excel 파일 처리
customtkinter >= 5.2.0 # GUI 인터페이스
```

### 파일 구조
```
LY_Table/
├── src/
│   ├── main.py          # 진입점
│   ├── merge.py         # 병합 로직
│   ├── split.py         # 분할 로직
│   ├── validator.py     # 데이터 검증
│   ├── excel_format.py  # Excel 서식
│   └── ui.py            # GUI
├── tests/               # 테스트 코드 (37개)
├── requirements.txt     # 의존성 목록
├── setup.py            # 패키지 설정
├── ly_table.spec       # PyInstaller 빌드 설정
└── README.md           # 본 문서
```

---

## 🧪 테스트

### 전체 테스트 실행
```bash
pytest tests/ -v
```

### 테스트 커버리지
- **37개 테스트** 모두 통과
- 단위 테스트: 병합, 분할, 검증 로직
- 통합 테스트: Round-trip 무결성 검증
- 실제 데이터: 49,600행 처리 검증

---

## 📝 버전 히스토리

### v1.3.0 (2025-12-02)
- ✨ **Merge Batches 기능 추가** (배치별 병합 + 중복 KEY 제거)
- 💬 **사용자 친화적 오류 메시지** (28개 메시지 개선)
- 🧪 54개 테스트 모두 통과
- 📋 순차 적재 순서 유지 중복 제거 알고리즘

### v1.2.0 (2025-11-28)
- ✨ Date 컬럼 추가 (언어별 G열, 통합 M열)
- ✅ 하위 호환성 지원
- 🎨 시트명 'Sheet1' 통일

---

## 🆘 문제 해결

### Q: "파일 수가 7개가 아닙니다" 에러
**A**: Merge 시 정확히 7개 언어 파일을 모두 선택해야 합니다.

### Q: "KEY가 일치하지 않습니다" 에러
**A**: 모든 언어 파일의 KEY 목록이 동일해야 합니다. EN 파일을 기준으로 확인하세요.

### Q: "날짜가 일치하지 않습니다" 에러
**A**: 모든 언어 파일의 파일명 날짜가 동일해야 합니다 (예: 모두 251128).

### Q: Date 컬럼이 없는 구버전 파일을 사용할 수 있나요?
**A**: 네, v1.3.0부터 Date 컬럼이 없는 파일도 처리 가능합니다 (빈 값으로 처리).

### Q: 빈 Target 값이 있어도 되나요?
**A**: 네, Target, NOTE, Date 컬럼은 빈 값(공백) 허용됩니다.

---

## 📄 라이선스

MIT License

---

## 👥 개발팀

**LY/GL Team**
Legend of YMIR MMORPG 현지화팀

---

## 📮 문의

프로젝트 관련 문의사항은 GitHub Issues를 통해 남겨주세요.

---

**Last Updated**: 2025-12-02
**Document Version**: 1.3.0
