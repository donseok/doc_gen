"""
PPT 생성 API 라우터

개선 사항:
- 요약 에이전트 (ContentSummarizer) 통합
- 디자인 에이전트 (PPTDesigner) 통합
- 스마트 PPT 생성 파이프라인
"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import GenerateRequest, GenerateResponse
from app.services.md_parser import MarkdownParser
from app.config import settings

router = APIRouter()


def generate_smart_ppt(
    md_content: str,
    template_id: int = None,
    theme: str = "modern_blue",
    use_smart_mode: bool = True,
    db: Session = None,
) -> str:
    """
    스마트 PPT 생성 파이프라인

    1. 마크다운 파싱
    2. 콘텐츠 요약 (핵심 내용 추출)
    3. PPT 디자인 적용 (템플릿 스타일 또는 테마)
    4. 파일 저장

    Args:
        md_content: 마크다운 문자열
        template_id: 템플릿 ID (업로드된 템플릿 스타일 적용)
        theme: 디자인 테마 (modern_blue, corporate, dark, minimal)
        use_smart_mode: True면 스마트 모드 (요약+디자인), False면 기존 방식
        db: 데이터베이스 세션 (템플릿 조회용)

    Returns:
        생성된 PPT 파일 경로
    """
    import uuid
    import json

    # 1. 마크다운 파싱
    parser = MarkdownParser()
    parsed_data = parser.parse(md_content)

    if use_smart_mode:
        # 2. 콘텐츠 요약 (스마트 모드)
        from app.services.content_summarizer import ContentSummarizer
        summarizer = ContentSummarizer()
        presentation_content = summarizer.summarize(parsed_data)

        # 3. 템플릿 스타일 로드 (있는 경우)
        template_style = None
        if template_id and db:
            from app.models.template import Template
            template = db.query(Template).filter(Template.id == template_id).first()
            if template and template.file_path:
                style_file_path = template.file_path.replace(".pptx", "_style.json")
                if os.path.exists(style_file_path):
                    with open(style_file_path, "r", encoding="utf-8") as f:
                        template_style = json.load(f)

        # 4. PPT 디자인 적용
        from app.services.ppt_designer import PPTDesigner
        designer = PPTDesigner(theme=theme, template_style=template_style)
        prs = designer.design(presentation_content)

        # 5. 파일 저장
        title = presentation_content.title or "presentation"
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50] if safe_title else "presentation"
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{safe_title}_{unique_id}.pptx"

        output_path = os.path.join(settings.OUTPUT_DIR, filename)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        prs.save(output_path)

        return output_path

    else:
        # 기존 방식 (레거시 호환)
        from app.services.ppt_generator import PPTGenerator
        generator = PPTGenerator()
        return generator.generate(parsed_data, template_id=template_id)


@router.post("/from-text", response_model=GenerateResponse)
async def generate_from_text(
    request: GenerateRequest,
    db: Session = Depends(get_db),
):
    """
    텍스트(마크다운)로부터 PPT 생성

    스마트 모드가 활성화되면:
    - 핵심 내용만 자동 추출
    - 모던한 디자인 자동 적용
    - 텍스트 오버플로우 자동 방지
    """
    if not request.md_content:
        raise HTTPException(status_code=400, detail="마크다운 내용이 필요합니다")

    # 옵션에서 설정 추출
    options = request.options or {}
    theme = options.get("theme", "modern_blue")
    use_smart_mode = options.get("smart_mode", True)  # 기본값: 스마트 모드 활성화

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
        # 마크다운 파싱 (제목 추출용)
        parser = MarkdownParser()
        parsed_data = parser.parse(request.md_content)

        # 제목 업데이트
        if parsed_data.get("title"):
            document.title = parsed_data["title"]

        # 스마트 PPT 생성
        output_path = generate_smart_ppt(
            md_content=request.md_content,
            template_id=request.template_id,
            theme=theme,
            use_smart_mode=use_smart_mode,
            db=db,
        )

        # 성공 상태 업데이트
        document.output_path = output_path
        document.status = DocumentStatus.COMPLETED.value
        db.commit()

        return GenerateResponse(
            document_id=document.id,
            status="completed",
            message="PPT가 성공적으로 생성되었습니다" + (" (스마트 모드)" if use_smart_mode else ""),
            download_url=f"/api/documents/{document.id}/download",
        )

    except Exception as e:
        # 실패 상태 업데이트
        logger.error(f"PPT generation failed: {str(e)}")

        document.status = DocumentStatus.FAILED.value
        document.error_message = str(e)
        db.commit()

        raise HTTPException(status_code=500, detail=f"PPT 생성 실패: {str(e)}")


@router.post("/from-file", response_model=GenerateResponse)
async def generate_from_file(
    file: UploadFile = File(...),
    template_id: int = None,
    theme: str = Query(default="modern_blue", description="디자인 테마"),
    smart_mode: bool = Query(default=True, description="스마트 모드 사용 여부"),
    db: Session = Depends(get_db),
):
    """
    마크다운 파일로부터 PPT 생성

    Parameters:
    - file: 마크다운 파일 (.md)
    - template_id: 템플릿 ID (선택)
    - theme: 디자인 테마 (modern_blue, corporate, dark, minimal)
    - smart_mode: True면 스마트 모드 (요약+디자인)
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
        # 마크다운 파싱 (제목 추출용)
        parser = MarkdownParser()
        parsed_data = parser.parse(md_content)

        # 제목 업데이트
        if parsed_data.get("title"):
            document.title = parsed_data["title"]

        # 스마트 PPT 생성
        output_path = generate_smart_ppt(
            md_content=md_content,
            template_id=template_id,
            theme=theme,
            use_smart_mode=smart_mode,
            db=db,
        )

        # 성공 상태 업데이트
        document.output_path = output_path
        document.status = DocumentStatus.COMPLETED.value
        db.commit()

        return GenerateResponse(
            document_id=document.id,
            status="completed",
            message="PPT가 성공적으로 생성되었습니다" + (" (스마트 모드)" if smart_mode else ""),
            download_url=f"/api/documents/{document.id}/download",
        )

    except Exception as e:
        # 실패 상태 업데이트
        document.status = DocumentStatus.FAILED.value
        document.error_message = str(e)
        db.commit()

        raise HTTPException(status_code=500, detail=f"PPT 생성 실패: {str(e)}")


@router.get("/themes")
async def get_available_themes():
    """
    사용 가능한 디자인 테마 목록
    """
    return {
        "themes": [
            {
                "id": "modern_blue",
                "name": "모던 블루",
                "description": "깔끔하고 전문적인 파란색 테마",
                "primary_color": "#0070C0",
            },
            {
                "id": "corporate",
                "name": "기업용",
                "description": "격식있는 네이비 기반 테마",
                "primary_color": "#003366",
            },
            {
                "id": "dark",
                "name": "다크 모드",
                "description": "어두운 배경의 현대적 테마",
                "primary_color": "#00BCD4",
            },
            {
                "id": "minimal",
                "name": "미니멀",
                "description": "깔끔하고 단순한 테마",
                "primary_color": "#333333",
            },
        ]
    }
