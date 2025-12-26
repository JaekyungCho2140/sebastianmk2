"""
데이터 검증 모듈

PRD 섹션 2.2 "Core Functionalities"에 정의된 데이터 무결성 규칙을 검증합니다.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path


# 언어 코드 매핑 (PRD 섹션 2.1.3)
LANGUAGE_MAPPING = {
    "EN": {"file_name": "EN.xlsx", "column_name": "Target_EN", "full_name": "English"},
    "CT": {
        "file_name": "CT.xlsx",
        "column_name": "Target_CT",
        "full_name": "Chinese Traditional",
    },
    "CS": {
        "file_name": "CS.xlsx",
        "column_name": "Target_CS",
        "full_name": "Chinese Simplified",
    },
    "JA": {"file_name": "JA.xlsx", "column_name": "Target_JA", "full_name": "Japanese"},
    "TH": {"file_name": "TH.xlsx", "column_name": "Target_TH", "full_name": "Thai"},
    "PT-BR": {
        "file_name": "PT-BR.xlsx",
        "column_name": "Target_PT",
        "full_name": "Portuguese (Brazil)",
    },
    "RU": {"file_name": "RU.xlsx", "column_name": "Target_RU", "full_name": "Russian"},
}

LANGUAGE_ORDER = ["EN", "CT", "CS", "JA", "TH", "PT-BR", "RU"]

# 파일명 패턴 (PRD 섹션 2.3.2)
FILE_PATTERNS = {
    "merged": re.compile(r"^\d{6}_LYGL_StringALL\.xlsx$"),
    "language": re.compile(r"^\d{6}_(EN|CT|CS|JA|TH|PT-BR|RU)\.xlsx$"),
}


class ValidationError(Exception):
    """데이터 검증 에러"""

    def __init__(self, message: str, error_code: str = None, **kwargs):
        super().__init__(message)
        self.error_code = error_code
        self.params = kwargs


def validate_file_name(file_path: Path, file_type: str) -> bool:
    """
    파일명 형식 검증

    Args:
        file_path: 검증할 파일 경로
        file_type: 'merged' 또는 'language'

    Returns:
        True if valid, False otherwise
    """
    pattern = FILE_PATTERNS[file_type]
    return pattern.match(file_path.name) is not None


def extract_language_code(file_path: Path) -> Optional[str]:
    """
    언어별 파일에서 언어 코드 추출

    Args:
        file_path: 언어별 파일 경로

    Returns:
        언어 코드 (예: 'EN', 'CT') 또는 None

    Example:
        extract_language_code(Path('251104_EN.xlsx')) → 'EN'
    """
    match = re.match(r"^\d{6}_(.+)\.xlsx$", file_path.name)
    return match.group(1) if match else None


def extract_date(file_path: Path) -> Optional[str]:
    """
    파일에서 날짜 추출

    Args:
        file_path: 파일 경로

    Returns:
        날짜 문자열 (YYMMDD 형식), 없으면 None

    Example:
        extract_date(Path('251104_LYGL_StringALL.xlsx')) → '251104'
        extract_date(Path('251104_EN.xlsx')) → '251104'
    """
    match = re.match(r"^(\d{6})_", file_path.name)
    return match.group(1) if match else None


def validate_language_files(file_paths: List[Path]) -> Tuple[bool, Optional[str]]:
    """
    언어 파일 목록 검증

    Args:
        file_paths: 언어 파일 경로 목록

    Returns:
        (검증 성공 여부, 에러 메시지)

    Raises:
        ValidationError: 검증 실패 시
    """
    # 1. 파일 수 검증 (정확히 7개)
    if len(file_paths) != 7:
        raise ValidationError(f"Expected 7 language files, got {len(file_paths)}")

    # 2. 언어 코드 추출 및 검증
    found_languages = set()
    dates = set()

    for file_path in file_paths:
        # 파일명 형식 검증
        if not validate_file_name(file_path, "language"):
            raise ValidationError(f"Invalid file name format: {file_path.name}")

        # 언어 코드 추출
        lang_code = extract_language_code(file_path)
        if not lang_code:
            raise ValidationError(
                f"Cannot extract language code from: {file_path.name}"
            )

        # 날짜 추출
        date = extract_date(file_path)
        if date:
            dates.add(date)

        found_languages.add(lang_code)

    # 3. 필수 언어 검증
    required_langs = set(LANGUAGE_ORDER)
    if found_languages != required_langs:
        missing = required_langs - found_languages
        extra = found_languages - required_langs
        raise ValidationError(f"Language mismatch. Missing: {missing}, Extra: {extra}")

    # 4. 날짜 일치 검증
    if len(dates) > 1:
        raise ValidationError(
            f"Date mismatch: Found files with different dates ({', '.join(sorted(dates))})"
        )

    return True, None


def validate_headers(
    headers: List[str], expected_headers: List[str], file_name: str = ""
) -> None:
    """
    헤더 검증

    Args:
        headers: 실제 헤더 목록
        expected_headers: 예상 헤더 목록
        file_name: 파일명 (에러 메시지용)

    Raises:
        ValidationError: 헤더 불일치 시
    """
    # Date 컬럼 누락 허용 (하위 호환성)
    if len(headers) == len(expected_headers) - 1 and "Date" in expected_headers:
        # Date 컬럼 없는 구버전 파일
        headers_without_date = [h for h in expected_headers if h != "Date"]
        if headers != headers_without_date:
            raise ValidationError(
                f"Invalid headers in {file_name}. "
                f"Expected {expected_headers} or {headers_without_date}, got {headers}"
            )
    elif headers != expected_headers:
        raise ValidationError(
            f"Invalid headers in {file_name}. "
            f"Expected {expected_headers}, got {headers}"
        )


def validate_key(key, row_num: int = 0, file_name: str = "") -> None:
    """
    KEY 컬럼 값 검증

    Args:
        key: KEY 값
        row_num: 행 번호 (에러 메시지용)
        file_name: 파일명 (에러 메시지용)

    Raises:
        ValidationError: KEY가 비어있거나 유효하지 않을 시
    """
    if not key or str(key).strip() == "":
        raise ValidationError(f"Empty KEY found in {file_name} at row {row_num}")


def validate_row_match(
    key: str,
    en_row: Dict,
    lang_row: Dict,
    lang_code: str,
    check_fields: Optional[List[str]] = None,
) -> None:
    """
    두 행의 공통 필드 일치 여부 검증

    Args:
        key: KEY 값
        en_row: EN(마스터) 행 데이터
        lang_row: 다른 언어 행 데이터
        lang_code: 언어 코드 (에러 메시지용)
        check_fields: 검증할 필드 목록 (기본: Table, Source, Status, NOTE, Date)

    Raises:
        ValidationError: 필드 불일치 시
    """
    if check_fields is None:
        check_fields = ["Table", "Source", "Status", "NOTE", "Date"]

    for field in check_fields:
        en_value = en_row.get(field)
        lang_value = lang_row.get(field)

        # NOTE, Date 필드는 빈 값 정규화 (None과 '' 동일 처리)
        if field in ["NOTE", "Date"]:
            en_value = en_value if en_value else ""
            lang_value = lang_value if lang_value else ""

        if en_value != lang_value:
            raise ValidationError(
                f"{field} mismatch for KEY '{key}': "
                f"EN={en_value}, {lang_code}={lang_value}"
            )


def normalize_empty_value(value) -> str:
    """
    빈 값 정규화 (None → '')

    중요: 공백을 보존하기 위해 strip() 사용하지 않음
    Excel 셀의 좌우 공백은 원본 그대로 유지됨

    Args:
        value: 원본 값

    Returns:
        정규화된 문자열 (None은 '', 나머지는 문자열 변환)
    """
    if value is None:
        return ""

    return str(value)
