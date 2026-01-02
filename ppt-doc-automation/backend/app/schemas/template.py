"""
템플릿 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    """템플릿 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=255, description="템플릿 이름")
    description: Optional[str] = Field(None, description="템플릿 설명")


class TemplateCreate(TemplateBase):
    """템플릿 생성 스키마"""
    file_path: str = Field(..., description="템플릿 파일 경로")
    is_default: bool = Field(False, description="기본 템플릿 여부")


class TemplateUpdate(BaseModel):
    """템플릿 수정 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """템플릿 응답 스키마"""
    id: int
    file_path: str
    thumbnail_path: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """템플릿 목록 응답 스키마"""
    items: List[TemplateResponse]
    total: int
    page: int
    page_size: int
