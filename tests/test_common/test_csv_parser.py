"""CSV Parser 테스트"""

import pytest
from sebastian.core.common.csv_parser import (
    parse_csv_line_raw,
    analyze_csv_pattern,
    save_csv_with_pattern,
    CSVParseError,
)
from pathlib import Path
import pandas as pd


class TestParseCSVLineRaw:
    """CSV 라인 파싱 테스트"""

    def test_simple_fields(self):
        """단순 필드 파싱"""
        line = 'field1,field2,field3'
        result = parse_csv_line_raw(line)

        assert len(result) == 3
        assert result[0] == ('field1', False, 'field1')
        assert result[1] == ('field2', False, 'field2')
        assert result[2] == ('field3', False, 'field3')

    def test_quoted_fields(self):
        """따옴표 있는 필드 파싱"""
        line = '"field1",field2,"field3"'
        result = parse_csv_line_raw(line)

        assert len(result) == 3
        assert result[0] == ('field1', True, '"field1"')
        assert result[1] == ('field2', False, 'field2')
        assert result[2] == ('field3', True, '"field3"')

    def test_escaped_quotes(self):
        """이중 따옴표 escape 파싱"""
        line = 'text,"<span class=""green"">Test</span>"'
        result = parse_csv_line_raw(line)

        assert len(result) == 2
        assert result[0] == ('text', False, 'text')
        # "" → " 변환 확인, raw text는 escape 포함
        assert result[1] == ('<span class="green">Test</span>', True, '"<span class=""green"">Test</span>"')

    def test_comma_in_quoted_field(self):
        """따옴표 필드 내 쉼표"""
        line = '"Hello, World",Test'
        result = parse_csv_line_raw(line)

        assert len(result) == 2
        assert result[0] == ('Hello, World', True, '"Hello, World"')
        assert result[1] == ('Test', False, 'Test')

    def test_empty_fields(self):
        """빈 필드"""
        line = 'field1,,field3'
        result = parse_csv_line_raw(line)

        assert len(result) == 3
        assert result[0] == ('field1', False, 'field1')
        assert result[1] == ('', False, '')  # 빈 필드, 따옴표 없음
        assert result[2] == ('field3', False, 'field3')

    def test_empty_quoted_field(self):
        """빈 필드 (따옴표 있음)"""
        line = 'field1,"",field3'
        result = parse_csv_line_raw(line)

        assert len(result) == 3
        assert result[0] == ('field1', False, 'field1')
        assert result[1] == ('', True, '""')  # 빈 필드, 따옴표 있음
        assert result[2] == ('field3', False, 'field3')

    def test_complex_html(self):
        """복잡한 HTML 태그"""
        line = '''key1,각 지역의... '<span class="green">레이저(Razer)</span>'의...'''
        result = parse_csv_line_raw(line)

        assert len(result) == 2
        assert result[0] == ('key1', False, 'key1')
        # 따옴표 없는 필드, HTML 내 따옴표는 그대로
        assert result[1][0] == '각 지역의... \'<span class="green">레이저(Razer)</span>\'의...'
        assert result[1][1] == False

    def test_triple_quotes_case(self):
        """삼중 따옴표 케이스 (memoQ 특수 케이스)"""
        # memoQ가 생성: """Copa de Yggdrasil"" concedida..."
        line = '"""Copa de Yggdrasil"" concedida..."'
        result = parse_csv_line_raw(line)

        assert len(result) == 1
        # "" → " 변환, 필드 따옴표 있음
        assert result[0][0] == '"Copa de Yggdrasil" concedida...'
        assert result[0][1] == True

    def test_unquoted_field_with_html_entity(self):
        """HTML entity 포함 필드 (따옴표 없음)"""
        line = 'key1,서버의 명예&#44; 클랜의 전략&#44; 전사의 실력...'
        result = parse_csv_line_raw(line)

        assert len(result) == 2
        assert result[0] == ('key1', False, 'key1')
        assert result[1][0] == '서버의 명예&#44; 클랜의 전략&#44; 전사의 실력...'
        assert result[1][1] == False

    def test_quoted_field_with_html_entity(self):
        """HTML entity 포함 필드 (따옴표 있음)"""
        line = 'key1,"서버의 명예&#44; 클랜의 전략&#44; 전사의 실력..."'
        result = parse_csv_line_raw(line)

        assert len(result) == 2
        assert result[0] == ('key1', False, 'key1')
        assert result[1][0] == '서버의 명예&#44; 클랜의 전략&#44; 전사의 실력...'
        assert result[1][1] == True


class TestAnalyzeCSVPattern:
    """CSV 패턴 분석 테스트"""

    def test_analyze_simple_csv(self, tmp_path):
        """단순 CSV 패턴 분석"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            'key-name,ko,en\n'
            'key1,"텍스트",Text\n'
            'key2,일반,"Quoted"\n',
            encoding='utf-8-sig'
        )

        pattern = analyze_csv_pattern(str(csv_file))

        # key1
        assert pattern[(0, 'ko')]['has_field_quotes'] == True
        assert pattern[(0, 'ko')]['original_value'] == '텍스트'
        assert pattern[(0, 'en')]['has_field_quotes'] == False
        assert pattern[(0, 'en')]['original_value'] == 'Text'

        # key2
        assert pattern[(1, 'ko')]['has_field_quotes'] == False
        assert pattern[(1, 'en')]['has_field_quotes'] == True


class TestSaveCSVWithPattern:
    """패턴 기반 CSV 저장 테스트"""

    def test_save_with_pattern(self, tmp_path):
        """원본 패턴으로 저장"""
        # 원본 패턴
        pattern = {
            (0, 'ko'): {
                'has_field_quotes': True,
                'original_value': '텍스트',
                'raw_field_text': '"텍스트"'
            },
            (0, 'en'): {
                'has_field_quotes': False,
                'original_value': 'Text',
                'raw_field_text': 'Text'
            },
        }

        # DataFrame (export와 original 동일한 경우)
        df = pd.DataFrame({
            'key-name': ['key1'],
            'ko': ['텍스트'],
            'en': ['Text']
        })

        output_file = tmp_path / "output.csv"
        save_csv_with_pattern(df, str(output_file), pattern)

        # 저장된 파일 확인
        content = output_file.read_text(encoding='utf-8-sig')
        lines = content.strip().split('\n')

        assert lines[0] == 'key-name,ko,en'  # 헤더
        # 내용 동일하므로 원본 raw 그대로
        assert lines[1] == 'key1,"텍스트",Text'

    def test_save_with_html_quotes(self, tmp_path):
        """HTML 따옴표 복원"""
        # 원본 패턴 (따옴표 없음)
        pattern = {
            (0, 'ko'): {
                'has_field_quotes': False,
                'original_value': '각 지역의... \'<span class="green">레이저</span>\'...',
                'raw_field_text': '각 지역의... \'<span class="green">레이저</span>\'...'
            },
        }

        # DataFrame (export - 내용 동일)
        df = pd.DataFrame({
            'key-name': ['key46'],
            'ko': ['각 지역의... \'<span class="green">레이저</span>\'...']
        })

        output_file = tmp_path / "output.csv"
        save_csv_with_pattern(df, str(output_file), pattern)

        # 저장된 파일 확인
        content = output_file.read_text(encoding='utf-8-sig')
        lines = content.strip().split('\n')

        # 내용 동일하므로 원본 raw 그대로
        assert '각 지역의... \'<span class="green">레이저</span>\'...' in lines[1]
