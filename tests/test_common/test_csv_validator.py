"""CSV Validator 테스트"""

import pytest
from pathlib import Path
from sebastian.core.common.csv_validator import validate_csv_structure, CSVValidationError


@pytest.fixture
def sample_data_dir():
    """샘플 데이터 디렉토리 경로"""
    return Path(__file__).parent / "sample_data"


class TestCSVValidator:
    """CSV 검증 테스트"""

    def test_valid_files(self, sample_data_dir):
        """정상 파일 검증"""
        original = sample_data_dir / "original_normal.csv"
        export = sample_data_dir / "export_normal.csv"

        original_df, export_df, warnings = validate_csv_structure(
            str(original), str(export)
        )

        assert len(warnings) == 0
        assert len(original_df) == 7  # 7개 행
        assert len(export_df) == 7
        assert len(original_df.columns) == 9  # 9개 컬럼
        assert original_df.columns[0] == "key-name"

    def test_column_count_mismatch(self, sample_data_dir):
        """컬럼 수 불일치 테스트"""
        original = sample_data_dir / "error_column_mismatch_original.csv"
        export = sample_data_dir / "error_column_mismatch_export.csv"

        with pytest.raises(CSVValidationError, match="컬럼 수 불일치"):
            validate_csv_structure(str(original), str(export))

    def test_keyname_mismatch(self, sample_data_dir):
        """key-name 불일치 테스트"""
        original = sample_data_dir / "error_keyname_mismatch_original.csv"
        export = sample_data_dir / "error_keyname_mismatch_export.csv"

        with pytest.raises(CSVValidationError, match="key-name"):
            validate_csv_structure(str(original), str(export))

    def test_file_not_exists(self):
        """파일이 존재하지 않을 때"""
        with pytest.raises(CSVValidationError, match="존재하지 않습니다"):
            validate_csv_structure("nonexistent.csv", "nonexistent2.csv")

    def test_invalid_csv_format(self, tmp_path):
        """잘못된 CSV 형식"""
        # 잘못된 CSV 파일 생성
        invalid_csv = tmp_path / "invalid.csv"
        invalid_csv.write_text("key-name\n\nvalue\n\n", encoding="utf-8")

        original = tmp_path / "original.csv"
        original.write_text("key-name,ko\nkey1,텍스트", encoding="utf-8")

        # 파싱은 성공하지만 컬럼 수 불일치로 에러
        with pytest.raises(CSVValidationError):
            validate_csv_structure(str(original), str(invalid_csv))
