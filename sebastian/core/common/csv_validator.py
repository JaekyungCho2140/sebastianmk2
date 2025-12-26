"""CSV 파일 구조 검증 모듈

memoQ export CSV 파일과 원본 CSV 파일의 구조를 검증합니다.
"""

from typing import Tuple, List
import pandas as pd
from pathlib import Path


class CSVValidationError(Exception):
    """CSV 검증 에러

    CSV 파일의 구조가 올바르지 않을 때 발생합니다.
    """

    pass


def validate_csv_structure(
    original_path: str, export_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """CSV 파일 구조 검증

    원본 CSV 파일과 memoQ export CSV 파일의 구조를 검증합니다.
    다음 항목을 검증합니다:
    1. 파일 존재 여부
    2. CSV 파싱 가능 여부
    3. 컬럼 수 일치 (필수)
    4. 헤더 일치 (권장)
    5. key-name 컬럼 존재 (필수)
    6. key-name 값 일치 (권장)

    Args:
        original_path: 원본 CSV 파일 경로
        export_path: memoQ export CSV 파일 경로

    Returns:
        (원본 DataFrame, export DataFrame, 경고 메시지 리스트)
        경고 메시지는 헤더 불일치, key-name 불일치 등을 포함합니다.

    Raises:
        CSVValidationError: 검증 실패 시
            - 파일이 존재하지 않음
            - CSV 파싱 실패
            - 컬럼 수 불일치
            - key-name 컬럼 없음
            - key-name 값 불일치 (export에만 있거나 원본에만 있음)

    Examples:
        >>> original_df, export_df, warnings = validate_csv_structure(
        ...     "original.csv", "export.csv"
        ... )
        >>> if warnings:
        ...     print("경고:", warnings)
    """
    warnings: List[str] = []

    # 1. 파일 존재 여부 확인
    original_file = Path(original_path)
    export_file = Path(export_path)

    if not original_file.exists():
        raise CSVValidationError(f"원본 파일이 존재하지 않습니다: {original_path}")

    if not export_file.exists():
        raise CSVValidationError(f"Export 파일이 존재하지 않습니다: {export_path}")

    # 2. CSV 파싱
    try:
        original_df = pd.read_csv(original_path, dtype=str, keep_default_na=False)
    except Exception as e:
        raise CSVValidationError(f"원본 파일 파싱 실패: {e}")

    try:
        export_df = pd.read_csv(export_path, dtype=str, keep_default_na=False)
    except Exception as e:
        raise CSVValidationError(f"Export 파일 파싱 실패: {e}")

    # 3. 컬럼 수 일치 확인 (필수)
    if len(original_df.columns) != len(export_df.columns):
        raise CSVValidationError(
            f"컬럼 수 불일치: 원본 {len(original_df.columns)}개, "
            f"export {len(export_df.columns)}개"
        )

    # 4. 헤더 일치 확인 (권장)
    if not original_df.columns.equals(export_df.columns):
        header_diff = set(original_df.columns) ^ set(export_df.columns)
        warning_msg = f"헤더 불일치: {header_diff}"
        warnings.append(warning_msg)
        raise CSVValidationError(warning_msg)

    # 5. key-name 컬럼 존재 확인 (첫 번째 컬럼)
    if len(original_df.columns) == 0:
        raise CSVValidationError("컬럼이 없습니다")

    key_column = original_df.columns[0]

    # 6. key-name 값 일치 확인 (권장)
    original_keys = set(original_df[key_column].values)
    export_keys = set(export_df[key_column].values)

    # export에만 있는 key-name
    only_in_export = export_keys - original_keys
    if only_in_export:
        warning_msg = f"Export에만 있는 key-name: {only_in_export}"
        warnings.append(warning_msg)
        raise CSVValidationError(warning_msg)

    # 원본에만 있는 key-name
    only_in_original = original_keys - export_keys
    if only_in_original:
        warning_msg = f"원본에만 있는 key-name: {only_in_original}"
        warnings.append(warning_msg)
        raise CSVValidationError(warning_msg)

    return original_df, export_df, warnings
