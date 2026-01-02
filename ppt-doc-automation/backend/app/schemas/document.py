"""
문서 스키마
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """문서 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=255, description="문서 제목")


class DocumentCreate(DocumentBase):
    """문서 생성 스키마"""
    original_filename: str = Field(..., description="원본 파일명")
    md_content: Optional[str] = Field(None, description="마크다운 내용")
    template_id: Optional[int] = Field(None, description="사용할 템플릿 ID")


class DocumentResponse(DocumentBase):
    """문서 응답 스키마"""
    id: int
    original_filename: str
    output_path: Optional[str]
    template_id: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """문서 목록 응답 스키마"""
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class GenerateRequest(BaseModel):
    """PPT 생성 요청 스키마"""
    md_content: Optional[str] = Field(None, description="마크다운 내용 (직접 입력)")
    template_id: Optional[int] = Field(None, description="사용할 템플릿 ID")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="생성 옵션 (슬라이드 크기, 테마 등)"
    )


class GenerateResponse(BaseModel):
    """PPT 생성 응답 스키마"""
    document_id: int
    status: str
    message: str
    download_url: Optional[str] = None
