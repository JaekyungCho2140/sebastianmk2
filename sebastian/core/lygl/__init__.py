"""
LY/GL 현지화 테이블 병합/분할 로직

레거시 소스: legacy/LY/src/
"""

from .merge import merge, merge_files
from .split import split, split_file
from .batch_merger import (
    validate_batch_folder_name,
    extract_language_from_filename,
    sort_batches,
    apply_status_completion,
    sort_batches_with_base,
)
from .legacy_diff import (
    scan_language_files,
    validate_diff_folders,
    compare_language_files,
    create_overview_sheet,
    create_language_sheet,
)

__all__ = [
    # Merge
    'merge',
    'merge_files',
    # Split
    'split',
    'split_file',
    # Batch
    'validate_batch_folder_name',
    'extract_language_from_filename',
    'sort_batches',
    'apply_status_completion',
    'sort_batches_with_base',
    # Diff
    'scan_language_files',
    'validate_diff_folders',
    'compare_language_files',
    'create_overview_sheet',
    'create_language_sheet',
]
