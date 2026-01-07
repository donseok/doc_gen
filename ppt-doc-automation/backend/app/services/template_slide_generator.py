"""
템플릿 기반 슬라이드 생성기

기존 그룹 공통 PPT템플릿.pptx의 마스터 레이아웃을 활용하여
고품질 슬라이드를 생성합니다.

주요 개선점:
- Blank 레이아웃 대신 적절한 마스터 레이아웃 사용
- 플레이스홀더에 직접 텍스트 삽입 (디자인 요소 유지)
- 커스텀 요소는 기존 렌더러와 통합
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from pptx import Presentation
from pptx.slide import Slide
from pptx.util import Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


@dataclass
class LayoutConfig:
    """레이아웃 설정"""
    index: int
    name: str
    placeholders: Dict[str, int]  # placeholder_name -> idx


class TemplateSlideGenerator:
    """
    템플릿 기반 슬라이드 생성기.
    
    기존 그룹 공통 PPT템플릿.pptx의 5개 마스터 레이아웃을 활용합니다:
    - Layout 0: White_Big K 버전 (표지)
    - Layout 1: 간지 1 (목차)
    - Layout 2: 내지 - Action title 사용 (본문 + Action Title + Body)
    - Layout 3: 내지 - Action title, Body삭제 (본문 + Action Title, 자유 배치)
    - Layout 4: 내지 - Action Title 미사용 (본문 + 넓은 Body)
    """
    
    # 레이아웃 매핑 (PPT기본양식_분석보고서.md 기준)
    LAYOUTS = {
        "title": LayoutConfig(
            index=0, 
            name="White_Big K 버전",
            placeholders={"title": 15, "subtitle": 27}
        ),
        "toc": LayoutConfig(
            index=1, 
            name="간지 1",
            placeholders={"toc_numbers": 22, "toc_titles": 20, "toc_pages": 17}
        ),
        "content_action": LayoutConfig(
            index=2, 
            name="내지 (Action title 사용)",
            placeholders={"main_title": 17, "action_title": 16, "body": 15}
        ),
        "content_free": LayoutConfig(
            index=3, 
            name="내지 (Action title, Body삭제)",
            placeholders={"main_title": 17, "action_title": 16}
        ),
        "content_simple": LayoutConfig(
            index=4, 
            name="내지 (Action Title 미사용)",
            placeholders={"main_title": 17, "body": 14}
        ),
    }
    
    # JSON layout_id → 내부 레이아웃 타입 매핑
    LAYOUT_ID_MAP = {
        1: "title",
        2: "toc",
        3: "content_action",
        4: "content_free",
        5: "content_simple",
    }
    
    def __init__(self, template_path: str):
        """
        Args:
            template_path: 그룹 공통 PPT템플릿.pptx 경로
        """
        self.template_path = template_path
        self._validate_template()
        
    def _validate_template(self):
        """템플릿 파일 존재 확인"""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {self.template_path}")
    
    def create_presentation(self) -> Presentation:
        """템플릿 기반으로 새 프레젠테이션 생성"""
        return Presentation(self.template_path)
    
    def add_slide(self, prs: Presentation, layout_id: int, data: Dict) -> Slide:
        """
        적절한 레이아웃으로 슬라이드 추가 후 데이터 채우기
        
        Args:
            prs: Presentation 객체
            layout_id: JSON의 layout_id (1~5)
            data: 슬라이드 데이터 (placeholders, custom_elements 등)
            
        Returns:
            생성된 Slide 객체
        """
        layout_type = self.LAYOUT_ID_MAP.get(layout_id, "content_free")
        layout_config = self.LAYOUTS[layout_type]
        
        # 적절한 마스터 레이아웃 선택
        try:
            slide_layout = prs.slide_layouts[layout_config.index]
        except IndexError:
            # 폴백: Blank 레이아웃 (인덱스 6)
            print(f"[WARNING] 레이아웃 {layout_config.index} 없음, Blank 사용")
            slide_layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[-1]
        
        slide = prs.slides.add_slide(slide_layout)
        
        # 플레이스홀더에 데이터 채우기
        self._fill_placeholders(slide, layout_type, data)
        
        return slide
    
    def _fill_placeholders(self, slide: Slide, layout_type: str, data: Dict):
        """
        슬라이드의 플레이스홀더에 데이터 채우기
        
        Args:
            slide: 슬라이드 객체
            layout_type: 레이아웃 타입 (title, toc, content_action 등)
            data: 슬라이드 데이터
        """
        placeholders = data.get("placeholders", {})
        
        if layout_type == "title":
            self._fill_title_slide(slide, placeholders)
        elif layout_type == "toc":
            self._fill_toc_slide(slide, placeholders)
        else:
            self._fill_content_slide(slide, placeholders, layout_type)
    
    def _fill_title_slide(self, slide: Slide, placeholders: Dict):
        """표지 슬라이드 플레이스홀더 채우기"""
        title = placeholders.get("title", "")
        subtitle = placeholders.get("subtitle", "")
        
        for shape in slide.shapes:
            if shape.has_text_frame:
                # 제목 플레이스홀더 찾기
                if hasattr(shape, 'placeholder_format') and shape.placeholder_format:
                    idx = shape.placeholder_format.idx
                    if idx == 15 or idx == 0:  # title placeholder
                        self._set_text_frame(shape.text_frame, title)
                    elif idx == 27 or idx == 13:  # subtitle placeholder
                        self._set_text_frame(shape.text_frame, subtitle)
                elif shape.name and "제목" in shape.name:
                    self._set_text_frame(shape.text_frame, title)
                elif shape.name and ("부제" in shape.name or "텍스트" in shape.name):
                    if subtitle:
                        self._set_text_frame(shape.text_frame, subtitle)
    
    def _fill_toc_slide(self, slide: Slide, placeholders: Dict):
        """목차 슬라이드 플레이스홀더 채우기"""
        toc_items = placeholders.get("toc_items", [])
        
        # 목차 항목들을 텍스트로 변환
        numbers_text = "\n".join([item.get("number", f"0{i+1}") for i, item in enumerate(toc_items)])
        titles_text = "\n".join([item.get("title", "") for item in toc_items])
        pages_text = "\n".join([item.get("pages", "") for item in toc_items])
        
        for shape in slide.shapes:
            if shape.has_text_frame and hasattr(shape, 'placeholder_format') and shape.placeholder_format:
                idx = shape.placeholder_format.idx
                if idx == 22 or idx == 17:  # 번호 열
                    self._set_text_frame(shape.text_frame, numbers_text)
                elif idx == 20 or idx == 13:  # 제목 열
                    self._set_text_frame(shape.text_frame, titles_text)
                elif idx == 17 or idx == 14:  # 페이지 열
                    if pages_text:
                        self._set_text_frame(shape.text_frame, pages_text)
    
    def _fill_content_slide(self, slide: Slide, placeholders: Dict, layout_type: str):
        """본문 슬라이드 플레이스홀더 채우기"""
        main_title = placeholders.get("main_title", "")
        action_title = placeholders.get("action_title", "")
        body = placeholders.get("body", [])
        
        # body가 리스트인 경우 텍스트로 변환
        if isinstance(body, list):
            body_text = self._format_body_list(body)
        else:
            body_text = str(body) if body else ""
        
        for shape in slide.shapes:
            if shape.has_text_frame:
                if hasattr(shape, 'placeholder_format') and shape.placeholder_format:
                    idx = shape.placeholder_format.idx
                    # Main Title (idx=19 또는 17)
                    if idx in [19, 17]:
                        if "Main" in shape.name or "12" in shape.name:
                            self._set_text_frame(shape.text_frame, main_title)
                    # Action Title (idx=16 또는 title type)
                    elif idx == 16 or idx == 0:
                        if action_title and layout_type in ["content_action", "content_free"]:
                            self._set_text_frame(shape.text_frame, action_title)
                    # Body (idx=18 또는 15 또는 14)
                    elif idx in [18, 15, 14]:
                        if body_text and layout_type in ["content_action", "content_simple"]:
                            self._set_text_frame(shape.text_frame, body_text)
                elif shape.name:
                    # 이름 기반 매칭 (폴백)
                    name_lower = shape.name.lower()
                    if "main" in name_lower or "12" in shape.name:
                        self._set_text_frame(shape.text_frame, main_title)
                    elif "action" in name_lower or "제목" in shape.name:
                        if action_title:
                            self._set_text_frame(shape.text_frame, action_title)
    
    def _format_body_list(self, body_items: List) -> str:
        """body 리스트를 텍스트로 변환"""
        lines = []
        for item in body_items:
            if isinstance(item, dict):
                level = item.get("level", 1)
                text = item.get("text", "")
                indent = "  " * (level - 1)
                bullet = "▐" if level == 1 else ("•" if level == 2 else "–")
                lines.append(f"{indent}{bullet} {text}")
            else:
                lines.append(f"▐ {item}")
        return "\n".join(lines)
    
    def _set_text_frame(self, text_frame, text: str):
        """텍스트 프레임에 텍스트 설정"""
        if not text:
            return
        
        # 개행 문자 처리
        text = text.replace("\\n", "\n")
        
        # 첫 번째 paragraph 사용
        if text_frame.paragraphs:
            text_frame.paragraphs[0].text = text
        else:
            p = text_frame.paragraphs.add_paragraph()
            p.text = text


# 편의 함수
def create_presentation_from_json(template_path: str, json_data: Dict) -> Presentation:
    """
    JSON 데이터로부터 템플릿 기반 프레젠테이션 생성
    
    Args:
        template_path: 템플릿 파일 경로
        json_data: 슬라이드 JSON 데이터
        
    Returns:
        Presentation 객체
    """
    generator = TemplateSlideGenerator(template_path)
    prs = generator.create_presentation()
    
    # 기존 슬라이드 삭제 (템플릿의 샘플 슬라이드들)
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]
    
    presentation = json_data.get("presentation", {})
    slides_data = presentation.get("slides", [])
    
    for slide_data in slides_data:
        layout_id = slide_data.get("layout_id", 4)
        generator.add_slide(prs, layout_id, slide_data)
    
    return prs
