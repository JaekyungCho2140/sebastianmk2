"""
M4/GL 현지화 테이블 병합 로직

레거시 소스: legacy/M4/Merged_M4.py
"""

from .dialogue import merge_dialogue
from .string import merge_string

__all__ = [
    'merge_dialogue',
    'merge_string',
]
