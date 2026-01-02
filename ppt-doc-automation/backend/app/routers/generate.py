"""
PPT 생성 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import GenerateRequest, GenerateResponse
from app.services.md_parser import MarkdownParser

router = APIRouter()


@router.post("/from-text", response_model=GenerateResponse)
async def generate_from_text(
    request: GenerateRequest,
    db: Session = Depends(get_db),
):
    """
    텍스트(마크다운)로부터 PPT 생성
    """
    if not request.md_content:
        raise HTTPException(status_code=400, detail="마크다운 내용이 필요합니다")
    
    # 문서 레코드 생성
    document = Document(
        title="Untitled",
        original_filename="text_input.md",
        md_content=request.md_content,
        template_id=request.template_id,
        status=DocumentStatus.PROCESSING.value,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    try:
        # 마크다운 파싱
        parser = MarkdownParser()
        parsed_data = parser.parse(request.md_content)
        
        # 제목 업데이트
        if parsed_data.get("title"):
            document.title = parsed_data["title"]
        
        # PPT 생성 (lazy import for Python 3.13 compatibility)
        from app.services.ppt_generator import PPTGenerator
        generator = PPTGenerator()
        output_path = generator.generate(
            parsed_data,
            template_id=request.template_id,
            options=request.options or {},
        )
        
        # 성공 상태 업데이트
        document.output_path = output_path
        document.status = DocumentStatus.COMPLETED.value
        db.commit()
        
        return GenerateResponse(
            document_id=document.id,
            status="completed",
            message="PPT가 성공적으로 생성되었습니다",
            download_url=f"/api/documents/{document.id}/download",
        )
        
    except Exception as e:
        # 실패 상태 업데이트
        document.status = DocumentStatus.FAILED.value
        document.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"PPT 생성 실패: {str(e)}")


@router.post("/from-file", response_model=GenerateResponse)
async def generate_from_file(
    file: UploadFile = File(...),
    template_id: int = None,
    db: Session = Depends(get_db),
):
    """
    마크다운 파일로부터 PPT 생성
    """
    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="마크다운(.md) 파일만 업로드 가능합니다")
    
    # 파일 내용 읽기
    content = await file.read()
    md_content = content.decode("utf-8")
    
    # 문서 레코드 생성
    document = Document(
        title=file.filename.replace(".md", ""),
        original_filename=file.filename,
        md_content=md_content,
        template_id=template_id,
        status=DocumentStatus.PROCESSING.value,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    try:
        # 마크다운 파싱
        parser = MarkdownParser()
        parsed_data = parser.parse(md_content)
        
        # 제목 업데이트
        if parsed_data.get("title"):
            document.title = parsed_data["title"]
        
        # PPT 생성 (lazy import for Python 3.13 compatibility)
        from app.services.ppt_generator import PPTGenerator
        generator = PPTGenerator()
        output_path = generator.generate(
            parsed_data,
            template_id=template_id,
            options={},
        )
        
        # 성공 상태 업데이트
        document.output_path = output_path
        document.status = DocumentStatus.COMPLETED.value
        db.commit()
        
        return GenerateResponse(
            document_id=document.id,
            status="completed",
            message="PPT가 성공적으로 생성되었습니다",
            download_url=f"/api/documents/{document.id}/download",
        )
        
    except Exception as e:
        # 실패 상태 업데이트
        document.status = DocumentStatus.FAILED.value
        document.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"PPT 생성 실패: {str(e)}")
