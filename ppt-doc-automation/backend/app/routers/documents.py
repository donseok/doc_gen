"""
문서 API 라우터
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    status: Optional[str] = Query(None, description="상태 필터"),
    db: Session = Depends(get_db),
):
    """
    문서 목록 조회
    """
    query = db.query(Document).order_by(Document.created_at.desc())
    
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    문서 상세 조회
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    문서 다운로드
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    
    if not document.output_path or not os.path.exists(document.output_path):
        raise HTTPException(status_code=404, detail="생성된 파일이 없습니다")
    
    return FileResponse(
        path=document.output_path,
        filename=f"{document.title}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    문서 삭제
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    
    # 생성된 파일 삭제
    if document.output_path and os.path.exists(document.output_path):
        os.remove(document.output_path)
    
    db.delete(document)
    db.commit()
    return {"message": "문서가 삭제되었습니다"}
