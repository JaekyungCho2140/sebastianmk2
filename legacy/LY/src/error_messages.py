"""
사용자 친화적 오류 메시지 모듈

PRD v1.3.0 섹션 1.2 "오류 메시지 매핑표"에 정의된 메시지를 제공합니다.
"""

# 오류 메시지 템플릿
ERROR_MESSAGES = {
    "FILE_COUNT_MISMATCH": (
        "7개의 언어 파일이 필요합니다만, 현재 {count}개만 선택되었습니다.\n\n"
        "필수 파일:\n"
        "- EN (영어)\n"
        "- CT (중국어 번체)\n"
        "- CS (중국어 간체)\n"
        "- JA (일본어)\n"
        "- TH (태국어)\n"
        "- PT-BR (포르투갈어 브라질)\n"
        "- RU (러시아어)\n\n"
        "모든 언어 파일을 선택해주세요."
    ),
    "INVALID_FILENAME_FORMAT": (
        "파일명 형식이 올바르지 않습니다.\n\n"
        "문제 파일: {filename}\n\n"
        "올바른 형식: YYMMDD_언어코드.xlsx\n"
        "예시: 251128_EN.xlsx, 251128_PT-BR.xlsx\n\n"
        "파일명을 확인해주세요."
    ),
    "LANG_CODE_EXTRACT_FAIL": (
        "파일명에서 언어 코드를 찾을 수 없습니다.\n\n"
        "문제 파일: {filename}\n\n"
        "파일명은 '날짜_언어코드.xlsx' 형식이어야 합니다.\n"
        "(예: 251128_EN.xlsx)\n\n"
        "파일명을 수정해주세요."
    ),
    "LANGUAGE_MISMATCH": (
        "언어 파일이 올바르지 않습니다.\n\n"
        "{missing_msg}{extra_msg}"
        "필수 언어: EN, CT, CS, JA, TH, PT-BR, RU\n\n"
        "누락되거나 불필요한 파일을 확인해주세요."
    ),
    "DATE_MISMATCH": (
        "파일들의 날짜가 일치하지 않습니다.\n\n"
        "발견된 날짜: {dates}\n\n"
        "모든 언어 파일은 동일한 날짜로 시작해야 합니다.\n"
        "(예: 모두 251128_로 시작)\n\n"
        "파일 날짜를 확인해주세요."
    ),
    "INVALID_HEADERS": (
        "파일의 컬럼 구조가 올바르지 않습니다.\n\n"
        "문제 파일: {file}\n\n"
        "필요한 컬럼: {expected}\n"
        "현재 컬럼: {actual}\n\n"
        "파일 구조를 확인해주세요."
    ),
    "EMPTY_KEY": (
        "빈 KEY가 발견되었습니다.\n\n"
        "파일: {file}\n"
        "위치: {row}번째 행\n\n"
        "KEY 컬럼(B열)은 반드시 값이 있어야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "DUPLICATE_KEY_EN": (
        "영어(EN) 파일에 중복된 KEY가 있습니다.\n\n"
        "중복 KEY: {key}\n\n"
        "EN 파일에서 중복을 제거한 후 다시 시도해주세요."
    ),
    "KEY_NOT_IN_MASTER": (
        "{lang} 파일의 KEY가 영어(EN) 파일에 없습니다.\n\n"
        "문제 KEY: {key}\n"
        "문제 파일: {lang}\n\n"
        "EN 파일이 기준입니다. 모든 언어 파일은 EN과 동일한 KEY를 가져야 합니다.\n\n"
        "EN 파일에 KEY를 추가하거나, {lang} 파일에서 해당 KEY를 제거해주세요."
    ),
    "TABLE_MISMATCH": (
        "Table 값이 일치하지 않습니다.\n\n"
        "KEY: {key}\n"
        "EN 파일: {en_val}\n"
        "{lang} 파일: {lang_val}\n\n"
        "모든 언어 파일의 Table 값은 EN과 동일해야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "SOURCE_MISMATCH": (
        "원문(Source)이 일치하지 않습니다.\n\n"
        "KEY: {key}\n"
        "EN 파일: {en_val}\n"
        "{lang} 파일: {lang_val}\n\n"
        "모든 언어 파일의 원문은 EN과 동일해야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "STATUS_MISMATCH": (
        "상태(Status)가 일치하지 않습니다.\n\n"
        "KEY: {key}\n"
        "EN 파일: {en_val}\n"
        "{lang} 파일: {lang_val}\n\n"
        "모든 언어 파일의 Status는 EN과 동일해야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "NOTE_MISMATCH": (
        "비고(NOTE)가 일치하지 않습니다.\n\n"
        "KEY: {key}\n"
        "EN 파일: {en_val}\n"
        "{lang} 파일: {lang_val}\n\n"
        "모든 언어 파일의 NOTE는 EN과 동일해야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "DATE_FIELD_MISMATCH": (
        "날짜(Date)가 일치하지 않습니다.\n\n"
        "KEY: {key}\n"
        "EN 파일: {en_val}\n"
        "{lang} 파일: {lang_val}\n\n"
        "모든 언어 파일의 Date는 EN과 동일해야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "FILE_NOT_FOUND": (
        "파일을 찾을 수 없습니다.\n\n"
        "경로: {path}\n\n"
        "파일이 존재하는지 확인해주세요."
    ),
    "FILE_READ_ERROR": (
        "파일을 읽을 수 없습니다.\n\n"
        "파일: {file}\n"
        "오류: {error}\n\n"
        "파일이 열려있거나 손상되었을 수 있습니다.\n"
        "파일을 닫고 다시 시도해주세요."
    ),
    "FILE_WRITE_ERROR": (
        "파일을 저장할 수 없습니다.\n\n"
        "오류: {error}\n\n"
        "디스크 공간이 부족하거나 쓰기 권한이 없을 수 있습니다.\n"
        "확인 후 다시 시도해주세요."
    ),
    "DIR_CREATE_ERROR": (
        "출력 폴더를 생성할 수 없습니다.\n\n"
        "오류: {error}\n\n"
        "쓰기 권한을 확인해주세요."
    ),
    "INCOMPLETE_ROW": (
        "불완전한 행이 발견되었습니다.\n\n"
        "위치: {row}번째 행\n\n"
        "모든 필수 컬럼(Table, KEY, Source 등)에 값이 있어야 합니다.\n"
        "파일을 확인하고 수정해주세요."
    ),
    "EN_MASTER_MISSING": (
        "영어(EN) 파일이 없습니다.\n\n"
        "EN 파일은 필수입니다. EN 파일이 기준이 되어 다른 언어 파일을 검증합니다.\n\n"
        "EN 파일을 추가해주세요."
    ),
    # Merge Batches 전용 오류
    "BATCH_FOLDER_INVALID": (
        "'{folder}' 폴더는 배치 폴더가 아닙니다.\n\n"
        "배치 폴더 형식: YYMMDD_REGULAR 또는 YYMMDD_EXTRA0~20\n"
        "예시: 251128_REGULAR, 251128_EXTRA1\n\n"
        "다른 폴더를 선택해주세요."
    ),
    "BATCH_REGULAR_MISSING": (
        "REGULAR 배치가 필요합니다.\n\n"
        "REGULAR 배치는 필수입니다.\n"
        "폴더를 확인하고 다시 선택해주세요."
    ),
    "BATCH_INCOMPLETE": (
        "{batch} 배치에 일부 언어 파일이 없습니다.\n\n"
        "누락된 언어: {missing}\n\n"
        "모든 언어 파일(7개)이 필요합니다.\n"
        "파일을 확인하고 다시 시도해주세요."
    ),
    "BATCH_FILE_DUPLICATE": (
        "{batch} 배치에 동일한 언어 파일이 여러 개 있습니다.\n\n"
        "중복 언어: {lang}\n"
        "발견된 파일:\n{files}\n\n"
        "각 언어는 1개 파일만 있어야 합니다.\n"
        "중복 파일을 제거해주세요."
    ),
    "BATCH_INTERNAL_DUPLICATE": (
        "'{batch}' 배치 내에 중복 KEY가 있습니다.\n\n"
        "중복 KEY:\n{keys}\n\n"
        "각 배치 파일 내에서 중복을 제거한 후 다시 시도해주세요."
    ),
    "DUPLICATE_DATE_SAME": (
        "중복 KEY에 동일한 Date가 있습니다.\n\n"
        "KEY: {key}\n"
        "동일 Date: {date}\n\n"
        "중복 KEY는 Date로 구분됩니다.\n"
        "Date를 수정하거나 중복을 수동으로 제거해주세요."
    ),
    "DATE_EMPTY_IN_DUPLICATE": (
        "중복 KEY에 빈 Date가 있습니다.\n\n"
        "KEY: {key}\n"
        "행 번호: {row}\n\n"
        "중복된 KEY를 비교하려면 모든 행에 Date가 필요합니다.\n"
        "Date를 입력하거나 중복을 제거해주세요."
    ),
    "DATE_FORMAT_INVALID": (
        "Date 형식이 올바르지 않습니다.\n\n"
        "KEY: {key}\n"
        "행 번호: {row}\n"
        "현재 Date: {date}\n\n"
        "올바른 형식: YYYY-MM-DD HH:MM\n"
        "(예: 2025-11-28 14:41)\n\n"
        "Date를 수정해주세요."
    ),
    "LANGUAGE_ROW_COUNT_MISMATCH": (
        "언어별 행 수가 일치하지 않습니다.\n\n"
        "EN: {en_count}행\n"
        "{lang}: {lang_count}행\n\n"
        "모든 언어는 동일한 KEY를 가져야 합니다."
    ),
    "SELECTION_TOO_FEW": (
        "최소 2개 이상의 배치를 선택해야 합니다.\n\n"
        "현재: {count}개 선택"
    ),
    "SELECTION_REGULAR_MISSING": (
        "REGULAR 배치는 필수입니다.\n\n"
        "REGULAR를 포함하여 선택해주세요."
    ),
}


def get_user_friendly_message(error_code: str, **kwargs) -> str:
    """
    사용자 친화적 오류 메시지 반환

    Args:
        error_code: 오류 코드
        **kwargs: 메시지 템플릿 변수

    Returns:
        포맷팅된 오류 메시지

    Example:
        >>> get_user_friendly_message("FILE_COUNT_MISMATCH", count=5)
        "7개의 언어 파일이 필요합니다만, 현재 5개만 선택되었습니다..."
    """
    template = ERROR_MESSAGES.get(error_code, "오류가 발생했습니다.\n\n오류 코드: {error_code}")

    # 특수 처리: LANGUAGE_MISMATCH
    if error_code == "LANGUAGE_MISMATCH":
        missing = kwargs.get("missing", set())
        extra = kwargs.get("extra", set())

        missing_msg = ""
        if missing:
            missing_msg = f"누락된 언어: {', '.join(sorted(missing))}\n"

        extra_msg = ""
        if extra:
            extra_msg = f"불필요한 파일: {', '.join(sorted(extra))}\n"

        kwargs["missing_msg"] = missing_msg
        kwargs["extra_msg"] = extra_msg

    try:
        return template.format(**kwargs)
    except KeyError as e:
        # 파라미터 누락 시 기본 메시지
        return f"오류가 발생했습니다.\n\n오류 코드: {error_code}\n누락된 파라미터: {e}"


def format_batch_duplicates(batch_duplicates: dict) -> str:
    """
    배치 내 중복 KEY를 포맷팅

    Args:
        batch_duplicates: {배치명: [KEY1, KEY2, ...]}

    Returns:
        포맷팅된 문자열
    """
    lines = []
    for batch, keys in batch_duplicates.items():
        lines.append(f"{batch} 배치:")
        for key in keys[:10]:  # 최대 10개만 표시
            lines.append(f"  - {key}")
        if len(keys) > 10:
            lines.append(f"  ... 외 {len(keys) - 10}개")

    return "\n".join(lines)
