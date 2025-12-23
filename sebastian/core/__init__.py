"""
Sebastian Core Engine

레거시 로직 통합 모듈
"""

# M4/GL
from .m4gl import merge_dialogue, merge_string

# NC/GL
from .ncgl import merge_ncgl

# LY/GL
from .lygl import (
    merge,
    merge_files,
    split,
    split_file,
)

__all__ = [
    # M4/GL
    'merge_dialogue',
    'merge_string',
    # NC/GL
    'merge_ncgl',
    # LY/GL
    'merge',
    'merge_files',
    'split',
    'split_file',
]
