"""
서비스 패키지
"""
from app.services.md_parser import MarkdownParser

# PPTGenerator는 사용 시 lazy import (python-pptx Python 3.13 호환성 이슈)
def get_ppt_generator():
    from app.services.ppt_generator import PPTGenerator
    return PPTGenerator

__all__ = ["MarkdownParser", "get_ppt_generator"]
