"""
JSON v2 형식을 PPTX로 변환하는 생성기

프로젝트_수행계획서_PPT_v2.json 형식의 구조화된 JSON을
고품질 PPTX 프레젠테이션으로 변환합니다.
"""
import json
import os
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData


@dataclass
class DongkukTheme:
    """동국제강 브랜드 색상 테마"""
    dk1: RGBColor = None  # 어두운 텍스트 기본색
    lt1: RGBColor = None  # 밝은 배경색 (흰색)
    dk2: RGBColor = None  # 동국제강 네이비 (브랜드 컬러)
    lt2: RGBColor = None  # 밝은 회색
    accent1: RGBColor = None  # 회색 강조
    accent2: RGBColor = None  # 청회색
    accent3: RGBColor = None  # 연한 청록색
    accent4: RGBColor = None  # 동국제강 레드 (브랜드 컬러)
    accent5: RGBColor = None  # 주황-빨강
    accent6: RGBColor = None  # 금색/황토색

    def __post_init__(self):
        self.dk1 = RGBColor(0x26, 0x26, 0x26)
        self.lt1 = RGBColor(0xFF, 0xFF, 0xFF)
        self.dk2 = RGBColor(0x00, 0x24, 0x52)  # 네이비
        self.lt2 = RGBColor(0xB6, 0xB6, 0xB6)
        self.accent1 = RGBColor(0x75, 0x75, 0x75)
        self.accent2 = RGBColor(0x4B, 0x65, 0x80)
        self.accent3 = RGBColor(0xB7, 0xD0, 0xD4)
        self.accent4 = RGBColor(0xC5, 0x1F, 0x2A)  # 레드
        self.accent5 = RGBColor(0xD5, 0x56, 0x33)
        self.accent6 = RGBColor(0xE9, 0xB8, 0x6E)


def hex_to_rgb(hex_color: str) -> RGBColor:
    """HEX 색상을 RGBColor로 변환"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return RGBColor(r, g, b)


class JsonToPptGenerator:
    """
    JSON v2 형식을 PPTX로 변환하는 생성기
    """

    # 슬라이드 크기 (A4 가로, 4:3에 가까움)
    SLIDE_WIDTH = Emu(9906000)   # 약 27.52cm
    SLIDE_HEIGHT = Emu(6858000)  # 약 19.05cm

    # 여백 (EMU)
    MARGIN_LEFT = Emu(270064)    # 약 0.75cm
    MARGIN_TOP = Emu(171278)     # 약 0.48cm

    # 콘텐츠 영역
    CONTENT_WIDTH = Emu(9360550)

    # 폰트
    FONT_TITLE = "본고딕"
    FONT_BODY = "본고딕"
    FONT_ENGLISH = "Segoe UI"

    def __init__(self, template_path: Optional[str] = None):
        """
        Args:
            template_path: PPT기본양식.pptx 템플릿 경로 (선택적)
        """
        self.template_path = template_path
        self.theme = DongkukTheme()
        self.prs = None

    def generate(self, json_data: Dict) -> Presentation:
        """
        JSON 데이터를 PPTX로 변환

        Args:
            json_data: 구조화된 프레젠테이션 JSON

        Returns:
            Presentation 객체
        """
        # 프레젠테이션 생성
        if self.template_path and os.path.exists(self.template_path):
            self.prs = Presentation(self.template_path)
        else:
            self.prs = Presentation()
            self.prs.slide_width = self.SLIDE_WIDTH
            self.prs.slide_height = self.SLIDE_HEIGHT

        presentation = json_data.get("presentation", {})
        slides = presentation.get("slides", [])

        for slide_data in slides:
            self._add_slide(slide_data)

        return self.prs

    def generate_from_file(self, json_path: str, output_path: str) -> str:
        """
        JSON 파일에서 PPTX 생성

        Args:
            json_path: JSON 파일 경로
            output_path: 출력 PPTX 경로

        Returns:
            생성된 파일 경로
        """
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        prs = self.generate(json_data)

        # 출력 디렉토리 확인
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        prs.save(output_path)
        return output_path

    def _add_slide(self, slide_data: Dict):
        """슬라이드 추가"""
        layout_id = slide_data.get("layout_id", 4)
        slide_type = slide_data.get("slide_type", "content")

        # Blank 레이아웃 사용 (커스텀 디자인)
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)

        # 레이아웃별 처리
        if layout_id == 1:  # 표지
            self._design_title_slide(slide, slide_data)
        elif layout_id == 2:  # 목차
            self._design_toc_slide(slide, slide_data)
        else:  # 본문 슬라이드
            self._design_content_slide(slide, slide_data)

    def _design_title_slide(self, slide, data: Dict):
        """표지 슬라이드 디자인"""
        placeholders = data.get("placeholders", {})

        # 상단 그라데이션 바 (빨강→네이비)
        gradient_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Emu(0), Emu(0),
            self.SLIDE_WIDTH, Emu(36000)
        )
        gradient_bar.fill.solid()
        gradient_bar.fill.fore_color.rgb = self.theme.accent4
        gradient_bar.line.fill.background()

        # 제목
        title_text = placeholders.get("title", "프레젠테이션")
        title_box = slide.shapes.add_textbox(
            Cm(1.5), Cm(7),
            Cm(18), Cm(4)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text.replace("\\n", "\n")
        p.font.name = self.FONT_TITLE
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self.theme.dk2
        p.alignment = PP_ALIGN.LEFT

        # 부제목
        subtitle_text = placeholders.get("subtitle", "")
        if subtitle_text:
            subtitle_box = slide.shapes.add_textbox(
                Cm(1.5), Cm(12),
                Cm(15), Cm(1)
            )
            tf = subtitle_box.text_frame
            p = tf.paragraphs[0]
            p.text = subtitle_text
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = self.theme.accent2
            p.alignment = PP_ALIGN.LEFT

    def _design_toc_slide(self, slide, data: Dict):
        """목차 슬라이드 디자인"""
        placeholders = data.get("placeholders", {})
        toc_items = placeholders.get("toc_items", [])

        # 상단 바
        self._add_header_bar(slide)

        # Contents 제목
        title_box = slide.shapes.add_textbox(
            Cm(2.5), Cm(4.5),
            Cm(8), Cm(1.2)
        )
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = "Contents"
        p.font.name = self.FONT_TITLE
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = self.theme.dk2

        # 목차 항목들
        y_start = Cm(6.5)
        for i, item in enumerate(toc_items):
            y = y_start + Cm(i * 1.8)

            # 번호
            num_box = slide.shapes.add_textbox(
                Cm(2.5), y,
                Cm(1.5), Cm(1)
            )
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("number", f"0{i+1}")
            p.font.name = self.FONT_TITLE
            p.font.size = Pt(16)
            p.font.color.rgb = self.theme.dk2
            p.alignment = PP_ALIGN.RIGHT

            # 제목
            title_box = slide.shapes.add_textbox(
                Cm(4.5), y,
                Cm(12), Cm(1)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(16)
            p.font.color.rgb = self.theme.dk1

            # 페이지
            page_box = slide.shapes.add_textbox(
                Cm(18), y,
                Cm(3), Cm(1)
            )
            tf = page_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("pages", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = self.theme.lt2
            p.alignment = PP_ALIGN.RIGHT

    def _design_content_slide(self, slide, data: Dict):
        """본문 슬라이드 디자인"""
        placeholders = data.get("placeholders", {})
        custom_elements = data.get("custom_elements", [])
        slide_type = data.get("slide_type", "content")

        # 상단 바
        self._add_header_bar(slide)

        # 구분선
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            self.MARGIN_LEFT, Emu(540000),
            self.CONTENT_WIDTH, Emu(6350)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(0xE0, 0xE0, 0xE0)
        line.line.fill.background()

        # Main Title
        main_title = placeholders.get("main_title", "")
        if main_title:
            title_box = slide.shapes.add_textbox(
                self.MARGIN_LEFT, Emu(171278),
                Emu(6172693), Emu(369332)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = main_title
            p.font.name = self.FONT_TITLE
            p.font.size = Pt(19)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk2

        # Action Title
        action_title = placeholders.get("action_title", "")
        if action_title:
            action_box = slide.shapes.add_textbox(
                self.MARGIN_LEFT, Emu(576000),
                self.CONTENT_WIDTH, Emu(708943)
            )
            tf = action_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = action_title
            p.font.name = self.FONT_BODY
            p.font.size = Pt(17)
            p.font.color.rgb = self.theme.dk1
            p.line_spacing = 1.3

        # Custom Elements 처리
        if custom_elements:
            self._render_custom_elements(slide, custom_elements, slide_type)
        elif placeholders.get("body"):
            self._render_body_bullets(slide, placeholders.get("body", []))

    def _render_custom_elements(self, slide, elements: List[Dict], slide_type: str):
        """커스텀 요소 렌더링"""
        content_top = Emu(1431130)  # Action Title 아래 시작

        for element in elements:
            element_type = element.get("type", "")
            data = element.get("data", {})

            if element_type == "big_number_display":
                self._render_big_numbers(slide, data, content_top)
            elif element_type == "pain_point_cards":
                self._render_pain_points(slide, data, content_top)
            elif element_type == "comparison_bar_chart":
                self._render_comparison_chart(slide, data, content_top)
            elif element_type in ["icon_card_grid", "icon_box_grid"]:
                self._render_icon_cards(slide, data, content_top)
            elif element_type in ["feature_cards", "numbered_step_cards"]:
                self._render_feature_cards(slide, data, content_top)
            elif element_type == "horizontal_process_flow":
                self._render_process_flow(slide, data, content_top)
            elif element_type == "tech_stack_grid":
                self._render_tech_stack(slide, data, content_top)
            elif element_type == "organization_cards":
                self._render_organization(slide, data, content_top)
            elif element_type == "donut_chart_with_table":
                self._render_donut_with_table(slide, data, content_top)
            elif element_type == "gantt_timeline":
                self._render_timeline(slide, data, content_top)
            elif element_type == "milestone_cards_grid":
                self._render_milestones(slide, data, content_top)
            elif element_type == "two_column_icon_list":
                self._render_two_column_list(slide, data, content_top)
            elif element_type == "risk_matrix_cards":
                self._render_risk_matrix(slide, data, content_top)
            elif element_type == "checklist_cards":
                self._render_checklist_cards(slide, data, content_top)
            elif element_type == "table":
                self._render_table(slide, data, content_top)

    def _render_big_numbers(self, slide, data: Dict, top: Emu):
        """Big Number Display 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 3)

        card_width_cm = 7
        card_height_cm = 5
        gap_cm = 1

        total_width_cm = card_width_cm * columns + gap_cm * (columns - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        card_width = Cm(card_width_cm)
        card_height = Cm(card_height_cm)
        gap = Cm(gap_cm)

        for i, item in enumerate(items[:columns]):
            x = start_x + i * (card_width + gap)
            y = top + Cm(0.5)

            # 카드 배경
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xF8, 0xF9, 0xFA)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 하단 액센트 바
            accent_color = hex_to_rgb(item.get("accent_color", "#002452"))
            accent_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y + card_height - Cm(0.3),
                card_width, Cm(0.3)
            )
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = accent_color
            accent_bar.line.fill.background()

            # 숫자 값
            value_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(0.8),
                card_width - Cm(1), Cm(2)
            )
            tf = value_box.text_frame
            p = tf.paragraphs[0]
            p.text = f"{item.get('value', '')}{item.get('unit', '')}"
            p.font.name = self.FONT_ENGLISH
            p.font.size = Pt(48)
            p.font.bold = True
            p.font.color.rgb = accent_color
            p.alignment = PP_ALIGN.CENTER

            # 라벨
            label_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(3),
                card_width - Cm(1), Cm(0.8)
            )
            tf = label_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("label", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1
            p.alignment = PP_ALIGN.CENTER

            # 부가 정보
            sub_label = item.get("sub_label", "")
            if sub_label:
                sub_box = slide.shapes.add_textbox(
                    x + Cm(0.5), y + Cm(3.8),
                    card_width - Cm(1), Cm(0.6)
                )
                tf = sub_box.text_frame
                p = tf.paragraphs[0]
                p.text = sub_label
                p.font.name = self.FONT_BODY
                p.font.size = Pt(11)
                p.font.color.rgb = self.theme.lt2
                p.alignment = PP_ALIGN.CENTER

    def _render_pain_points(self, slide, data: Dict, top: Emu):
        """Pain Point Cards 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 3)

        card_width_cm = 7
        card_height_cm = 5.5
        gap_cm = 0.8

        total_width_cm = card_width_cm * columns + gap_cm * (columns - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        card_width = Cm(card_width_cm)
        card_height = Cm(card_height_cm)
        gap = Cm(gap_cm)

        severity_colors = {
            "critical": RGBColor(0xC5, 0x1F, 0x2A),
            "high": RGBColor(0xFF, 0x6B, 0x6B),
            "medium": RGBColor(0xFF, 0xB3, 0x47)
        }

        for i, item in enumerate(items[:columns]):
            x = start_x + i * (card_width + gap)
            y = top + Cm(0.5)

            severity = item.get("severity", "high")
            border_color = severity_colors.get(severity, severity_colors["high"])

            # 카드 배경
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xF5, 0xF5)
            card.line.color.rgb = RGBColor(0xFF, 0xE0, 0xE0)

            # 좌측 액센트 바
            accent_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                Cm(0.25), card_height
            )
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = border_color
            accent_bar.line.fill.background()

            # 제목
            title_box = slide.shapes.add_textbox(
                x + Cm(0.6), y + Cm(0.5),
                card_width - Cm(1), Cm(1)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 설명
            desc_box = slide.shapes.add_textbox(
                x + Cm(0.6), y + Cm(1.6),
                card_width - Cm(1), Cm(2.5)
            )
            tf = desc_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = item.get("description", "").replace("\\n", "\n")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = self.theme.accent1
            p.line_spacing = 1.3

            # 영향도
            impact = item.get("impact", "")
            if impact:
                impact_box = slide.shapes.add_textbox(
                    x + Cm(0.6), y + Cm(4.3),
                    card_width - Cm(1), Cm(0.8)
                )
                tf = impact_box.text_frame
                p = tf.paragraphs[0]
                p.text = impact
                p.font.name = self.FONT_BODY
                p.font.size = Pt(10)
                p.font.bold = True
                p.font.color.rgb = border_color

    def _render_comparison_chart(self, slide, data: Dict, top: Emu):
        """Before/After 비교 차트 렌더링 (간소화된 바 차트)"""
        categories = data.get("categories", [])
        series_data = data.get("series", [])
        change_badges = data.get("change_badges", [])

        if not categories or not series_data:
            return

        # 차트 영역
        chart_left = Cm(2)
        chart_width = Cm(22)
        bar_height = Cm(1)
        group_gap = Cm(1.5)

        for i, category in enumerate(categories):
            y_base = top + Cm(0.5) + i * (bar_height * 2 + group_gap)

            # 카테고리 레이블
            cat_box = slide.shapes.add_textbox(
                chart_left, y_base,
                Cm(5), Cm(0.8)
            )
            tf = cat_box.text_frame
            p = tf.paragraphs[0]
            p.text = category
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # As-Is 바
            as_is_value = series_data[0]["values"][i] if len(series_data) > 0 else 0
            as_is_width = Cm(as_is_value / 100 * 12)
            as_is_bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                chart_left + Cm(5.5), y_base,
                as_is_width, bar_height
            )
            as_is_bar.fill.solid()
            as_is_bar.fill.fore_color.rgb = hex_to_rgb(series_data[0].get("color", "#B6B6B6"))
            as_is_bar.line.fill.background()

            # To-Be 바
            to_be_value = series_data[1]["values"][i] if len(series_data) > 1 else 0
            to_be_width = Cm(to_be_value / 100 * 12)
            to_be_bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                chart_left + Cm(5.5), y_base + bar_height + Cm(0.1),
                to_be_width, bar_height
            )
            to_be_bar.fill.solid()
            to_be_bar.fill.fore_color.rgb = hex_to_rgb(series_data[1].get("color", "#002452"))
            to_be_bar.line.fill.background()

            # 변화율 뱃지
            if i < len(change_badges):
                badge = change_badges[i]
                badge_box = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    chart_left + Cm(18.5), y_base + Cm(0.3),
                    Cm(2.5), Cm(1)
                )
                badge_box.fill.solid()
                badge_box.fill.fore_color.rgb = RGBColor(0xE8, 0xF5, 0xE9)
                badge_box.line.color.rgb = hex_to_rgb(badge.get("color", "#2E7D32"))

                # 뱃지 텍스트
                badge_box.text_frame.paragraphs[0].text = badge.get("label", "")
                badge_box.text_frame.paragraphs[0].font.size = Pt(12)
                badge_box.text_frame.paragraphs[0].font.bold = True
                badge_box.text_frame.paragraphs[0].font.color.rgb = hex_to_rgb(badge.get("color", "#2E7D32"))
                badge_box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # 범례
        legend_y = top + Cm(0.5) + len(categories) * (bar_height * 2 + group_gap)
        for j, s in enumerate(series_data):
            legend_box = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                chart_left + Cm(5.5) + j * Cm(4), legend_y,
                Cm(0.5), Cm(0.5)
            )
            legend_box.fill.solid()
            legend_box.fill.fore_color.rgb = hex_to_rgb(s.get("color", "#000000"))
            legend_box.line.fill.background()

            legend_text = slide.shapes.add_textbox(
                chart_left + Cm(6.2) + j * Cm(4), legend_y,
                Cm(3), Cm(0.5)
            )
            tf = legend_text.text_frame
            p = tf.paragraphs[0]
            p.text = s.get("name", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = self.theme.dk1

    def _render_icon_cards(self, slide, data: Dict, top: Emu):
        """아이콘 카드 그리드 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 4)

        card_width_cm = 5.5
        card_height_cm = 5
        gap_cm = 0.5

        total_width_cm = card_width_cm * columns + gap_cm * (columns - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        card_width = Cm(card_width_cm)
        card_height = Cm(card_height_cm)
        gap = Cm(gap_cm)

        for i, item in enumerate(items[:columns]):
            x = start_x + i * (card_width + gap)
            y = top + Cm(0.3)

            accent_color = hex_to_rgb(item.get("accent_color", "#002452"))

            # 카드 배경
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 좌측 액센트 바
            accent_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                Cm(0.2), card_height
            )
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = accent_color
            accent_bar.line.fill.background()

            # 제목 (시스템명)
            title_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(0.5),
                card_width - Cm(0.8), Cm(1)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = accent_color

            # 부제목
            subtitle = item.get("subtitle", "")
            if subtitle:
                sub_box = slide.shapes.add_textbox(
                    x + Cm(0.5), y + Cm(1.4),
                    card_width - Cm(0.8), Cm(0.6)
                )
                tf = sub_box.text_frame
                p = tf.paragraphs[0]
                p.text = subtitle
                p.font.name = self.FONT_BODY
                p.font.size = Pt(10)
                p.font.color.rgb = self.theme.lt2

            # 기능 목록
            features = item.get("features", [])
            for j, feature in enumerate(features[:3]):
                feat_box = slide.shapes.add_textbox(
                    x + Cm(0.5), y + Cm(2.2) + j * Cm(0.7),
                    card_width - Cm(0.8), Cm(0.6)
                )
                tf = feat_box.text_frame
                p = tf.paragraphs[0]
                p.text = f"• {feature}"
                p.font.name = self.FONT_BODY
                p.font.size = Pt(10)
                p.font.color.rgb = self.theme.dk1

    def _render_feature_cards(self, slide, data: Dict, top: Emu):
        """Feature Cards / Numbered Step Cards 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 3)

        card_width_cm = 7
        card_height_cm = 5.5
        gap_cm = 0.8

        total_width_cm = card_width_cm * columns + gap_cm * (columns - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        card_width = Cm(card_width_cm)
        card_height = Cm(card_height_cm)
        gap = Cm(gap_cm)

        for i, item in enumerate(items[:columns]):
            x = start_x + i * (card_width + gap)
            y = top + Cm(0.5)

            accent_color = hex_to_rgb(item.get("accent_color", item.get("color", "#002452")))

            # 카드 배경
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 상단 액센트 바
            accent_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                card_width, Cm(0.25)
            )
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = accent_color
            accent_bar.line.fill.background()

            # 번호
            number = item.get("number", str(i + 1))
            num_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(0.5),
                Cm(1.5), Cm(1.2)
            )
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = number
            p.font.name = self.FONT_ENGLISH
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 제목
            title_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(1.8),
                card_width - Cm(1), Cm(0.8)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 설명
            desc_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(2.8),
                card_width - Cm(1), Cm(2)
            )
            tf = desc_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = item.get("description", "").replace("\\n", "\n")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = self.theme.accent1
            p.line_spacing = 1.3

    def _render_process_flow(self, slide, data: Dict, top: Emu):
        """Horizontal Process Flow 렌더링"""
        nodes = data.get("nodes", [])

        node_width_cm = 5
        node_height_cm = 4
        gap_cm = 1.5

        total_width_cm = node_width_cm * len(nodes) + gap_cm * (len(nodes) - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        node_width = Cm(node_width_cm)
        node_height = Cm(node_height_cm)
        gap = Cm(gap_cm)

        for i, node in enumerate(nodes):
            x = start_x + i * (node_width + gap)
            y = top + Cm(0.5)

            node_color = hex_to_rgb(node.get("color", "#002452"))

            # 노드 박스
            box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                node_width, node_height
            )
            # 배경색 (연한 버전)
            box.fill.solid()
            box.fill.fore_color.rgb = RGBColor(
                min(255, node_color[0] + 200),
                min(255, node_color[1] + 200),
                min(255, node_color[2] + 200)
            )
            box.line.color.rgb = node_color
            box.line.width = Pt(2)

            # 상단 바
            top_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                node_width, Cm(0.2)
            )
            top_bar.fill.solid()
            top_bar.fill.fore_color.rgb = node_color
            top_bar.line.fill.background()

            # Phase 이름
            phase_box = slide.shapes.add_textbox(
                x + Cm(0.3), y + Cm(0.5),
                node_width - Cm(0.6), Cm(0.8)
            )
            tf = phase_box.text_frame
            p = tf.paragraphs[0]
            p.text = node.get("phase", node.get("title", ""))
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = node_color
            p.alignment = PP_ALIGN.CENTER

            # 기간
            duration = node.get("duration", "")
            if duration:
                dur_box = slide.shapes.add_textbox(
                    x + Cm(0.3), y + Cm(1.3),
                    node_width - Cm(0.6), Cm(0.5)
                )
                tf = dur_box.text_frame
                p = tf.paragraphs[0]
                p.text = duration
                p.font.name = self.FONT_BODY
                p.font.size = Pt(10)
                p.font.color.rgb = node_color
                p.alignment = PP_ALIGN.CENTER

            # 활동 내용
            activities = node.get("activities", [])
            for j, activity in enumerate(activities[:2]):
                act_box = slide.shapes.add_textbox(
                    x + Cm(0.3), y + Cm(2) + j * Cm(0.6),
                    node_width - Cm(0.6), Cm(0.5)
                )
                tf = act_box.text_frame
                p = tf.paragraphs[0]
                p.text = f"• {activity}"
                p.font.name = self.FONT_BODY
                p.font.size = Pt(9)
                p.font.color.rgb = self.theme.dk1
                p.alignment = PP_ALIGN.CENTER

            # 화살표 (마지막 노드 제외)
            if i < len(nodes) - 1:
                arrow = slide.shapes.add_shape(
                    MSO_SHAPE.RIGHT_ARROW,
                    x + node_width + Cm(0.2), y + node_height / 2 - Cm(0.3),
                    gap - Cm(0.4), Cm(0.6)
                )
                arrow.fill.solid()
                arrow.fill.fore_color.rgb = self.theme.lt2
                arrow.line.fill.background()

    def _render_tech_stack(self, slide, data: Dict, top: Emu):
        """기술 스택 렌더링"""
        layers = data.get("layers", [])

        layer_height = Cm(1.2)
        layer_gap = Cm(0.3)
        start_x = Cm(2)
        layer_width = Cm(22)

        for i, layer in enumerate(layers):
            y = top + Cm(0.3) + i * (layer_height + layer_gap)
            layer_color = hex_to_rgb(layer.get("color", "#002452"))

            # 레이어 배경
            bg = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                start_x, y,
                layer_width, layer_height
            )
            bg.fill.solid()
            bg.fill.fore_color.rgb = RGBColor(
                min(255, layer_color[0] + 220),
                min(255, layer_color[1] + 220),
                min(255, layer_color[2] + 220)
            )
            bg.line.fill.background()

            # 좌측 바
            left_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                start_x, y,
                Cm(0.2), layer_height
            )
            left_bar.fill.solid()
            left_bar.fill.fore_color.rgb = layer_color
            left_bar.line.fill.background()

            # 레이어 이름
            name_box = slide.shapes.add_textbox(
                start_x + Cm(0.5), y + Cm(0.3),
                Cm(3), Cm(0.6)
            )
            tf = name_box.text_frame
            p = tf.paragraphs[0]
            p.text = layer.get("name", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = layer_color

            # 기술 뱃지들
            techs = layer.get("techs", [])
            badge_x = start_x + Cm(4)
            for tech in techs:
                tech_name = tech.get("name", "")
                version = tech.get("version", "")
                badge_text = f"{tech_name} {version}".strip()

                badge = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    badge_x, y + Cm(0.25),
                    Cm(3.5), Cm(0.7)
                )
                badge.fill.solid()
                badge.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                badge.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

                badge.text_frame.paragraphs[0].text = badge_text
                badge.text_frame.paragraphs[0].font.size = Pt(9)
                badge.text_frame.paragraphs[0].font.name = self.FONT_BODY
                badge.text_frame.paragraphs[0].font.color.rgb = self.theme.dk1
                badge.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

                badge_x += Cm(3.8)

    def _render_organization(self, slide, data: Dict, top: Emu):
        """조직도 렌더링"""
        left_data = data.get("left", {})
        right_data = data.get("right", {})

        col_width = Cm(10)
        col_gap = Cm(1)
        start_x = Cm(2)

        # 좌측 (발주기관)
        self._render_org_column(slide, left_data, start_x, top, col_width)

        # 우측 (수행사)
        self._render_org_column(slide, right_data, start_x + col_width + col_gap, top, col_width)

    def _render_org_column(self, slide, data: Dict, x, top: Emu, width):
        """조직도 컬럼 렌더링"""
        title = data.get("title", "")
        color = hex_to_rgb(data.get("left_color", data.get("right_color", "#002452")))
        items = data.get("items", data.get("left_items", data.get("right_items", [])))

        y = top + Cm(0.3)

        # 헤더
        header = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            x, y,
            width, Cm(1)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = color
        header.line.fill.background()

        header.text_frame.paragraphs[0].text = title
        header.text_frame.paragraphs[0].font.size = Pt(12)
        header.text_frame.paragraphs[0].font.bold = True
        header.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        header.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # 항목들
        item_y = y + Cm(1.3)
        for item in items:
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, item_y,
                width, Cm(1.5)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xF8, 0xF9, 0xFA)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 역할
            role_box = slide.shapes.add_textbox(
                x + Cm(0.3), item_y + Cm(0.2),
                Cm(3), Cm(0.5)
            )
            tf = role_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("role", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = color

            # 이름
            name_box = slide.shapes.add_textbox(
                x + Cm(3.5), item_y + Cm(0.2),
                Cm(3), Cm(0.5)
            )
            tf = name_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("name", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = self.theme.dk1

            # 책임
            resp_box = slide.shapes.add_textbox(
                x + Cm(0.3), item_y + Cm(0.8),
                width - Cm(0.6), Cm(0.5)
            )
            tf = resp_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("responsibility", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(9)
            p.font.color.rgb = self.theme.accent1

            item_y += Cm(1.7)

    def _render_donut_with_table(self, slide, data: Dict, top: Emu):
        """도넛 차트 + 테이블 렌더링 (간소화된 버전)"""
        chart_data = data.get("chart", {})
        table_data = data.get("table", {})

        # 도넛 차트 (원형으로 대체)
        segments = chart_data.get("segments", [])
        center_label = chart_data.get("center_label", "")
        center_sublabel = chart_data.get("center_sublabel", "")

        # 중앙 텍스트 박스
        center_box = slide.shapes.add_textbox(
            Cm(3), top + Cm(2),
            Cm(6), Cm(2)
        )
        tf = center_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"{center_label}\n{center_sublabel}"
        p.font.name = self.FONT_BODY
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = self.theme.dk2
        p.alignment = PP_ALIGN.CENTER

        # 범례
        legend_y = top + Cm(0.5)
        for i, seg in enumerate(segments[:5]):
            legend_box = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Cm(1), legend_y + i * Cm(0.8),
                Cm(0.5), Cm(0.5)
            )
            legend_box.fill.solid()
            legend_box.fill.fore_color.rgb = hex_to_rgb(seg.get("color", "#002452"))
            legend_box.line.fill.background()

            label_box = slide.shapes.add_textbox(
                Cm(1.7), legend_y + i * Cm(0.8),
                Cm(5), Cm(0.5)
            )
            tf = label_box.text_frame
            p = tf.paragraphs[0]
            p.text = f"{seg.get('label', '')} ({seg.get('value', 0)}MM)"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = self.theme.dk1

        # 테이블
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if headers and rows:
            table = slide.shapes.add_table(
                len(rows) + 1, len(headers),
                Cm(10), top + Cm(0.3),
                Cm(14), Cm(5)
            ).table

            # 헤더
            for i, h in enumerate(headers):
                cell = table.cell(0, i)
                cell.text = h
                cell.fill.solid()
                cell.fill.fore_color.rgb = self.theme.dk2
                cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                cell.text_frame.paragraphs[0].font.size = Pt(10)
                cell.text_frame.paragraphs[0].font.bold = True
                cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # 데이터
            for ri, row in enumerate(rows):
                for ci, cell_val in enumerate(row):
                    cell = table.cell(ri + 1, ci)
                    cell.text = str(cell_val)
                    cell.text_frame.paragraphs[0].font.size = Pt(9)
                    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    def _render_timeline(self, slide, data: Dict, top: Emu):
        """Gantt 타임라인 렌더링"""
        phases = data.get("phases", [])

        timeline_left = Cm(2.5)
        timeline_width = Cm(21)
        bar_height = Cm(0.8)
        bar_gap = Cm(0.2)

        # 월 헤더
        months = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
        month_width = timeline_width / 12

        for i, month in enumerate(months):
            month_box = slide.shapes.add_textbox(
                timeline_left + month_width * i, top,
                month_width, Cm(0.6)
            )
            tf = month_box.text_frame
            p = tf.paragraphs[0]
            p.text = month
            p.font.name = self.FONT_BODY
            p.font.size = Pt(8)
            p.font.color.rgb = self.theme.lt2
            p.alignment = PP_ALIGN.CENTER

        # Phase 바
        for i, phase in enumerate(phases):
            y = top + Cm(0.8) + i * (bar_height + bar_gap)

            start_month = int(phase.get("start", "01").split("-")[0]) - 1
            end_month_str = phase.get("end", "01")
            end_month = int(end_month_str.split("-")[0]) - 1

            bar_x = timeline_left + month_width * start_month
            bar_w = month_width * (end_month - start_month + 1)

            bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                bar_x, y,
                bar_w, bar_height
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb(phase.get("color", "#002452"))
            bar.line.fill.background()

            bar.text_frame.paragraphs[0].text = phase.get("name", "")
            bar.text_frame.paragraphs[0].font.size = Pt(9)
            bar.text_frame.paragraphs[0].font.bold = True
            bar.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            bar.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    def _render_milestones(self, slide, data: Dict, top: Emu):
        """마일스톤 카드 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 3)

        card_width_cm = 7
        card_height_cm = 2.5
        gap_x_cm = 0.8
        gap_y_cm = 0.5

        total_width_cm = card_width_cm * columns + gap_x_cm * (columns - 1)
        start_x = (self.SLIDE_WIDTH - Cm(total_width_cm)) // 2

        card_width = Cm(card_width_cm)
        card_height = Cm(card_height_cm)
        gap_x = Cm(gap_x_cm)
        gap_y = Cm(gap_y_cm)

        for i, item in enumerate(items):
            col = i % columns
            row = i // columns

            x = start_x + col * (card_width + gap_x)
            y = top + Cm(0.3) + row * (card_height + gap_y)

            color = hex_to_rgb(item.get("color", "#002452"))

            # 카드
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 좌측 바
            left_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                Cm(0.25), card_height
            )
            left_bar.fill.solid()
            left_bar.fill.fore_color.rgb = color
            left_bar.line.fill.background()

            # ID 뱃지
            badge = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                x + Cm(0.5), y + Cm(0.3),
                Cm(1), Cm(1)
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = color
            badge.line.fill.background()
            badge.text_frame.paragraphs[0].text = item.get("id", "")
            badge.text_frame.paragraphs[0].font.size = Pt(11)
            badge.text_frame.paragraphs[0].font.bold = True
            badge.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            badge.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # 제목
            title_box = slide.shapes.add_textbox(
                x + Cm(1.8), y + Cm(0.3),
                card_width - Cm(2.2), Cm(0.6)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 날짜
            date_box = slide.shapes.add_textbox(
                x + Cm(1.8), y + Cm(1),
                card_width - Cm(2.2), Cm(0.5)
            )
            tf = date_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("date", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = color

            # 산출물
            deliv_box = slide.shapes.add_textbox(
                x + Cm(1.8), y + Cm(1.6),
                card_width - Cm(2.2), Cm(0.6)
            )
            tf = deliv_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("deliverable", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(9)
            p.font.color.rgb = self.theme.lt2

    def _render_two_column_list(self, slide, data: Dict, top: Emu):
        """2열 아이콘 리스트 렌더링"""
        left = data.get("left", {})
        right = data.get("right", {})

        col_width = Cm(10.5)
        start_x = Cm(1.5)
        gap = Cm(1)

        self._render_icon_list_column(slide, left, start_x, top, col_width)
        self._render_icon_list_column(slide, right, start_x + col_width + gap, top, col_width)

    def _render_icon_list_column(self, slide, data: Dict, x, top: Emu, width):
        """아이콘 리스트 컬럼 렌더링"""
        title = data.get("title", "")
        accent_color = hex_to_rgb(data.get("accent_color", "#002452"))
        items = data.get("items", [])

        y = top + Cm(0.3)

        # 헤더
        header_bg = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            x, y,
            width, Cm(1)
        )
        header_bg.fill.solid()
        header_bg.fill.fore_color.rgb = RGBColor(
            min(255, accent_color[0] + 220),
            min(255, accent_color[1] + 220),
            min(255, accent_color[2] + 220)
        )
        header_bg.line.fill.background()

        header_box = slide.shapes.add_textbox(
            x + Cm(0.5), y + Cm(0.2),
            width - Cm(1), Cm(0.6)
        )
        tf = header_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = self.FONT_BODY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = accent_color

        # 항목들
        item_y = y + Cm(1.3)
        for item in items:
            # 제목
            title_box = slide.shapes.add_textbox(
                x + Cm(0.3), item_y,
                width - Cm(0.6), Cm(0.5)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 설명
            desc_box = slide.shapes.add_textbox(
                x + Cm(0.3), item_y + Cm(0.5),
                width - Cm(0.6), Cm(0.5)
            )
            tf = desc_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("desc", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = self.theme.lt2

            item_y += Cm(1.2)

    def _render_risk_matrix(self, slide, data: Dict, top: Emu):
        """위험 매트릭스 렌더링"""
        risks = data.get("risks", [])
        level_colors = data.get("level_colors", {
            "critical": "#C51F2A",
            "high": "#FF6B6B",
            "medium": "#FFB347",
            "low": "#4CAF50"
        })

        card_width = Cm(22)
        card_height = Cm(1.5)
        gap = Cm(0.3)
        start_x = Cm(1.5)

        for i, risk in enumerate(risks):
            y = top + Cm(0.3) + i * (card_height + gap)
            level = risk.get("level", "medium")
            level_color = hex_to_rgb(level_colors.get(level, "#FFB347"))

            # 카드 배경
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                start_x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 좌측 바
            left_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                start_x, y,
                Cm(0.3), card_height
            )
            left_bar.fill.solid()
            left_bar.fill.fore_color.rgb = level_color
            left_bar.line.fill.background()

            # 위험 이름
            risk_box = slide.shapes.add_textbox(
                start_x + Cm(0.6), y + Cm(0.3),
                Cm(5), Cm(0.5)
            )
            tf = risk_box.text_frame
            p = tf.paragraphs[0]
            p.text = risk.get("risk", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 대응 방안
            resp_box = slide.shapes.add_textbox(
                start_x + Cm(6), y + Cm(0.3),
                Cm(12), Cm(0.9)
            )
            tf = resp_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = risk.get("response", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = self.theme.accent1

            # 담당자
            owner_box = slide.shapes.add_textbox(
                start_x + Cm(19), y + Cm(0.5),
                Cm(2.5), Cm(0.5)
            )
            tf = owner_box.text_frame
            p = tf.paragraphs[0]
            p.text = risk.get("owner", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = level_color
            p.alignment = PP_ALIGN.RIGHT

    def _render_checklist_cards(self, slide, data: Dict, top: Emu):
        """체크리스트 카드 렌더링"""
        items = data.get("items", [])
        columns = data.get("columns", 2)

        card_width = Cm(10.5)
        card_height = Cm(4)
        gap_x = Cm(1)
        gap_y = Cm(0.5)

        start_x = Cm(1.5)

        for i, item in enumerate(items):
            col = i % columns
            row = i // columns

            x = start_x + col * (card_width + gap_x)
            y = top + Cm(0.3) + row * (card_height + gap_y)

            color = hex_to_rgb(item.get("color", "#002452"))

            # 카드
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x, y,
                card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

            # 좌측 바
            left_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x, y,
                Cm(0.25), card_height
            )
            left_bar.fill.solid()
            left_bar.fill.fore_color.rgb = color
            left_bar.line.fill.background()

            # 카테고리 뱃지
            cat_badge = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                x + Cm(0.5), y + Cm(0.3),
                Cm(2), Cm(0.6)
            )
            cat_badge.fill.solid()
            cat_badge.fill.fore_color.rgb = RGBColor(
                min(255, color[0] + 220),
                min(255, color[1] + 220),
                min(255, color[2] + 220)
            )
            cat_badge.line.fill.background()
            cat_badge.text_frame.paragraphs[0].text = item.get("category", "")
            cat_badge.text_frame.paragraphs[0].font.size = Pt(9)
            cat_badge.text_frame.paragraphs[0].font.color.rgb = color
            cat_badge.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # 제목
            title_box = slide.shapes.add_textbox(
                x + Cm(0.5), y + Cm(1.1),
                card_width - Cm(1), Cm(0.6)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = item.get("title", "")
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = self.theme.dk1

            # 체크리스트
            checklist = item.get("checklist", [])
            for j, check_item in enumerate(checklist[:3]):
                check_box = slide.shapes.add_textbox(
                    x + Cm(0.5), y + Cm(1.9) + j * Cm(0.55),
                    card_width - Cm(1), Cm(0.5)
                )
                tf = check_box.text_frame
                p = tf.paragraphs[0]
                p.text = f"☐ {check_item}"
                p.font.name = self.FONT_BODY
                p.font.size = Pt(10)
                p.font.color.rgb = self.theme.accent1

    def _render_table(self, slide, data: Dict, top: Emu):
        """테이블 렌더링"""
        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not headers:
            return

        table = slide.shapes.add_table(
            len(rows) + 1, len(headers),
            Cm(1.5), top + Cm(0.3),
            Cm(22), Cm(5)
        ).table

        # 헤더
        for i, h in enumerate(headers):
            cell = table.cell(0, i)
            cell.text = str(h)
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.theme.dk2
            cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell.text_frame.paragraphs[0].font.size = Pt(10)
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # 데이터
        for ri, row in enumerate(rows):
            for ci, cell_val in enumerate(row):
                if ci < len(headers):
                    cell = table.cell(ri + 1, ci)
                    cell.text = str(cell_val) if cell_val else ""
                    if ri % 2 == 1:
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor(0xF8, 0xF9, 0xFA)
                    cell.text_frame.paragraphs[0].font.size = Pt(9)
                    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    def _render_body_bullets(self, slide, body: List[Dict]):
        """본문 불릿 포인트 렌더링"""
        y = Emu(1431130) + Cm(0.3)

        for item in body:
            level = item.get("level", 1)
            text = item.get("text", "")

            indent = Cm((level - 1) * 0.8)
            bullet = "▐" if level == 1 else ("•" if level == 2 else "–")

            text_box = slide.shapes.add_textbox(
                self.MARGIN_LEFT + indent, y,
                self.CONTENT_WIDTH - indent, Cm(0.8)
            )
            tf = text_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = f"{bullet} {text}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14 if level == 1 else 12)
            p.font.bold = level == 1
            p.font.color.rgb = self.theme.dk2 if level == 1 else self.theme.dk1

            y += Cm(0.9 if level == 1 else 0.7)

    def _add_header_bar(self, slide):
        """상단 헤더 바 추가"""
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Emu(0), Emu(0),
            self.SLIDE_WIDTH, Emu(36000)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = self.theme.dk2
        bar.line.fill.background()


def generate_ppt_from_json(json_path: str, output_dir: str) -> str:
    """
    JSON 파일에서 PPTX 생성 (편의 함수)

    Args:
        json_path: JSON 파일 경로
        output_dir: 출력 디렉토리

    Returns:
        생성된 PPTX 파일 경로
    """
    # JSON 파일 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 파일명 생성
    presentation = json_data.get("presentation", {})
    title = presentation.get("title", "presentation")
    # 파일명에 사용할 수 없는 문자 제거
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
    safe_title = safe_title[:50]  # 길이 제한

    output_filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pptx"
    output_path = os.path.join(output_dir, output_filename)

    # PPT 생성
    generator = JsonToPptGenerator()
    generator.generate_from_file(json_path, output_path)

    return output_path


if __name__ == "__main__":
    # 테스트 실행
    import sys

    if len(sys.argv) < 2:
        print("Usage: python json_to_ppt_generator.py <json_path> [output_dir]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(json_path)

    result = generate_ppt_from_json(json_path, output_dir)
    print(f"Generated: {result}")
