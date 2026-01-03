"""
템플릿 API 라우터
"""
import os
import uuid
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.template import Template
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
)
from app.config import settings
from app.services.template_analyzer import analyze_template

router = APIRouter()


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    db: Session = Depends(get_db),
):
    """
    템플릿 목록 조회
    """
    query = db.query(Template)
    
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return TemplateListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """
    템플릿 상세 조회
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    return template


@router.post("", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
):
    """
    새 템플릿 생성
    """
    template = Template(**template_data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
):
    """
    템플릿 수정
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """
    템플릿 삭제
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    db.delete(template)
    db.commit()
    return {"message": "템플릿이 삭제되었습니다"}


@router.post("/upload")
async def upload_template(
    file: UploadFile = File(...),
    name: str = Form(..., description="템플릿 이름"),
    description: Optional[str] = Form(None, description="템플릿 설명"),
    is_default: bool = Form(False, description="기본 템플릿 여부"),
    db: Session = Depends(get_db),
):
    """
    템플릿 파일 업로드 및 분석

    업로드된 PPTX 파일을 분석하여 디자인 요소를 추출하고 저장합니다.
    """
    if not file.filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="PPTX 파일만 업로드 가능합니다")

    # 파일 크기 확인
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다. 최대 {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB까지 가능합니다."
        )

    # 고유 파일명 생성
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{unique_id}_{file.filename}"
    file_path = os.path.join(settings.TEMPLATES_DIR, safe_filename)

    # 파일 저장
    os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)

    # 템플릿 분석
    try:
        style_info = analyze_template(file_path)
    except Exception as e:
        # 분석 실패 시 파일 삭제
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"템플릿 분석 실패: {str(e)}")

    # 스타일 정보를 JSON 파일로 저장
    style_file_path = file_path.replace(".pptx", "_style.json")
    with open(style_file_path, "w", encoding="utf-8") as f:
        json.dump(style_info, f, ensure_ascii=False, indent=2)

    # 기본 템플릿으로 설정 시 기존 기본 템플릿 해제
    if is_default:
        db.query(Template).filter(Template.is_default == True).update({"is_default": False})

    # DB에 템플릿 저장
    template = Template(
        name=name,
        description=description,
        file_path=file_path,
        is_default=is_default,
        is_active=True,
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    return {
        "message": "템플릿이 업로드되었습니다",
        "template_id": template.id,
        "name": template.name,
        "file_path": file_path,
        "style_info": style_info,
    }


@router.get("/{template_id}/style")
async def get_template_style(
    template_id: int,
    db: Session = Depends(get_db),
):
    """
    템플릿의 스타일 정보 조회
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 스타일 JSON 파일 경로
    style_file_path = template.file_path.replace(".pptx", "_style.json")

    if not os.path.exists(style_file_path):
        # 스타일 파일이 없으면 다시 분석
        try:
            style_info = analyze_template(template.file_path)
            with open(style_file_path, "w", encoding="utf-8") as f:
                json.dump(style_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"스타일 분석 실패: {str(e)}")
    else:
        with open(style_file_path, "r", encoding="utf-8") as f:
            style_info = json.load(f)

    return style_info
