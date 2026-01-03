"""
콘텐츠 요약 에이전트

마크다운 문서에서 PPT에 적합한 핵심 내용만 추출하는 에이전트
- 섹션별 핵심 포인트 추출
- 표 데이터 요약
- 불필요한 상세 내용 제거
- PPT 슬라이드에 적합한 분량으로 조절
"""
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SlideContent:
    """단일 슬라이드 콘텐츠"""
    title: str
    subtitle: Optional[str] = None
    bullets: List[str] = field(default_factory=list)
    key_metrics: List[Dict[str, str]] = field(default_factory=list)  # {"label": "", "value": ""}
    table_data: Optional[Dict[str, Any]] = None  # {"headers": [], "rows": []}
    layout_hint: str = "bullet"  # bullet, metrics, table, title_only, two_column
    importance: int = 1  # 1-3, 높을수록 중요


@dataclass
class PresentationContent:
    """전체 프레젠테이션 콘텐츠"""
    title: str
    subtitle: Optional[str] = None
    slides: List[SlideContent] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class ContentSummarizer:
    """
    콘텐츠 요약 에이전트

    마크다운 문서를 분석하여 PPT에 적합한 핵심 콘텐츠만 추출
    """

    # 슬라이드당 최대 불릿 포인트 수
    MAX_BULLETS_PER_SLIDE = 5
    # 불릿 포인트 최대 길이 (자)
    MAX_BULLET_LENGTH = 60
    # 표 최대 행 수
    MAX_TABLE_ROWS = 6

    # 중요 키워드 (우선순위 높음)
    IMPORTANT_KEYWORDS = [
        '목표', '목적', '전략', '핵심', '주요', '중요', '필수',
        '일정', '마일스톤', '예산', '비용', '금액',
        '위험', '리스크', '이슈', '문제',
        '성과', '효과', '기대', 'KPI',
        '조직', '인력', '담당', 'PM', 'PL',
    ]

    # 제외할 섹션 (상세 내용)
    SKIP_SECTIONS = [
        '부록', '문서 개정 이력', '참고', '별첨',
    ]

    def __init__(self):
        self.parsed_content = None

    def summarize(self, parsed_data: Dict[str, Any]) -> PresentationContent:
        """
        파싱된 마크다운 데이터를 요약하여 프레젠테이션 콘텐츠로 변환

        Args:
            parsed_data: MarkdownParser에서 파싱된 데이터

        Returns:
            요약된 프레젠테이션 콘텐츠
        """
        self.parsed_content = parsed_data

        presentation = PresentationContent(
            title=parsed_data.get("title", "프레젠테이션"),
            metadata=parsed_data.get("metadata", {}),
        )

        # 메타데이터에서 부제목 추출
        if "author" in presentation.metadata:
            presentation.subtitle = f"작성자: {presentation.metadata['author']}"
        if "date" in presentation.metadata:
            presentation.subtitle = presentation.metadata.get("date", "")

        # 각 슬라이드 처리
        for slide_data in parsed_data.get("slides", []):
            summarized_slides = self._summarize_slide(slide_data)
            presentation.slides.extend(summarized_slides)

        # 중요도 기반 정렬 및 필터링
        presentation.slides = self._prioritize_slides(presentation.slides)

        return presentation

    def _summarize_slide(self, slide_data: Dict[str, Any]) -> List[SlideContent]:
        """
        단일 슬라이드 데이터를 요약
        필요시 여러 슬라이드로 분할
        """
        title = slide_data.get("title") or ""

        # 제외할 섹션 체크
        for skip in self.SKIP_SECTIONS:
            if skip in title:
                return []

        content_items = slide_data.get("content", [])
        parsed_tables = slide_data.get("tables", [])  # 파서에서 이미 파싱된 테이블

        # 콘텐츠 분류
        bullets = []
        metrics = []

        for item in content_items:
            item_type = item.get("type", "")
            text = item.get("text", "")

            if item_type in ("bullet", "numbered"):
                # 핵심 불릿만 추출
                summarized = self._summarize_bullet(text)
                if summarized:
                    bullets.append(summarized)
            elif item_type == "text":
                # 텍스트에서 핵심 정보 추출
                extracted = self._extract_key_info(text)
                if extracted:
                    if isinstance(extracted, dict):
                        metrics.append(extracted)
                    else:
                        bullets.append(extracted)

        # 표 데이터 처리 - 파서에서 이미 파싱된 테이블 우선 사용
        table_data = None
        if parsed_tables:
            # 첫 번째 테이블 사용 (행 수 제한)
            table_data = parsed_tables[0]
            if table_data and table_data.get("rows"):
                table_data = {
                    "headers": table_data["headers"],
                    "rows": table_data["rows"][:self.MAX_TABLE_ROWS]
                }
        else:
            # 레거시: 콘텐츠에서 테이블 패턴 추출
            table_data = self._extract_table_from_content(content_items)

        # 슬라이드 분할 (내용이 많은 경우)
        slides = []

        # 중요도 계산
        importance = self._calculate_importance(title, bullets)

        # 표가 있는 경우 별도 슬라이드
        if table_data:
            slides.append(SlideContent(
                title=title,
                table_data=table_data,
                layout_hint="table",
                importance=importance,
            ))
            # 표와 불릿을 분리
            if bullets:
                slides.append(SlideContent(
                    title=f"{title} - 주요 내용",
                    bullets=bullets[:self.MAX_BULLETS_PER_SLIDE],
                    layout_hint="bullet",
                    importance=importance,
                ))
        elif metrics:
            # 메트릭이 있는 경우
            slides.append(SlideContent(
                title=title,
                key_metrics=metrics[:4],  # 최대 4개
                bullets=bullets[:3] if bullets else [],
                layout_hint="metrics",
                importance=importance,
            ))
        elif bullets:
            # 불릿이 많으면 분할
            for i in range(0, len(bullets), self.MAX_BULLETS_PER_SLIDE):
                chunk = bullets[i:i + self.MAX_BULLETS_PER_SLIDE]
                suffix = f" ({i // self.MAX_BULLETS_PER_SLIDE + 1})" if len(bullets) > self.MAX_BULLETS_PER_SLIDE else ""
                slides.append(SlideContent(
                    title=f"{title}{suffix}",
                    bullets=chunk,
                    layout_hint="bullet",
                    importance=importance,
                ))
        else:
            # 내용이 없으면 제목만
            slides.append(SlideContent(
                title=title,
                layout_hint="title_only",
                importance=importance,
            ))

        return slides

    def _summarize_bullet(self, text: str) -> Optional[str]:
        """불릿 포인트 요약"""
        if not text:
            return None

        # 불필요한 마크다운 제거
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # code

        # 너무 긴 경우 요약
        if len(text) > self.MAX_BULLET_LENGTH:
            # 핵심 부분 추출 (콜론 앞부분 우선)
            if ':' in text:
                parts = text.split(':', 1)
                if len(parts[0]) <= self.MAX_BULLET_LENGTH:
                    return parts[0].strip()
            # 그냥 자르기
            return text[:self.MAX_BULLET_LENGTH - 3] + "..."

        return text.strip()

    def _extract_key_info(self, text: str) -> Optional[Any]:
        """텍스트에서 핵심 정보 추출"""
        if not text:
            return None

        # 금액 패턴
        money_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:억|만|원|백만)', text)
        if money_match:
            # 레이블 추출 시도
            label_match = re.search(r'([가-힣]+(?:금액|비용|예산|계약))', text)
            if label_match:
                return {
                    "label": label_match.group(1),
                    "value": money_match.group(0),
                }

        # 기간 패턴
        period_match = re.search(r'(\d+)\s*(?:개월|주|일)', text)
        if period_match and any(kw in text for kw in ['기간', '일정', '계약']):
            return {
                "label": "프로젝트 기간",
                "value": period_match.group(0),
            }

        # 인원 패턴
        people_match = re.search(r'(\d+)\s*(?:명|인)', text)
        if people_match and any(kw in text for kw in ['인력', '인원', '팀']):
            return {
                "label": "투입 인력",
                "value": people_match.group(0),
            }

        # 일반 텍스트 (짧은 경우만)
        if len(text) <= self.MAX_BULLET_LENGTH:
            return text.strip()

        return None

    def _extract_table_from_content(self, content_items: List[Dict]) -> Optional[Dict[str, Any]]:
        """콘텐츠에서 표 형식 데이터 추출 및 요약"""
        # 현재는 파서가 표를 별도로 처리하지 않으므로
        # 텍스트에서 표 패턴을 찾아 추출

        table_texts = []
        for item in content_items:
            text = item.get("text", "")
            if "|" in text and "---" not in text:
                table_texts.append(text)

        if not table_texts:
            return None

        # 표 파싱
        headers = []
        rows = []

        for i, text in enumerate(table_texts):
            cells = [c.strip() for c in text.split("|") if c.strip()]
            if i == 0:
                headers = cells
            else:
                if len(cells) == len(headers):
                    rows.append(cells)

        if not headers or not rows:
            return None

        # 행 수 제한
        rows = rows[:self.MAX_TABLE_ROWS]

        return {
            "headers": headers,
            "rows": rows,
        }

    def _calculate_importance(self, title: str, bullets: List[str]) -> int:
        """슬라이드 중요도 계산 (1-3)"""
        score = 1

        # 제목에 중요 키워드 포함
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in title:
                score = max(score, 2)
                break

        # 특별히 중요한 섹션
        very_important = ['개요', '목표', '전략', '일정', '조직', '위험']
        for keyword in very_important:
            if keyword in title:
                score = 3
                break

        return score

    def _prioritize_slides(self, slides: List[SlideContent]) -> List[SlideContent]:
        """슬라이드 우선순위 정렬 및 필터링"""
        # 중요도가 낮은 슬라이드 중 일부 제거 (너무 많은 경우)
        MAX_SLIDES = 15

        if len(slides) <= MAX_SLIDES:
            return slides

        # 중요도순 정렬 후 상위 슬라이드 선택
        sorted_slides = sorted(slides, key=lambda s: s.importance, reverse=True)
        return sorted_slides[:MAX_SLIDES]


def summarize_for_ppt(parsed_data: Dict[str, Any]) -> PresentationContent:
    """
    편의 함수: 파싱된 데이터를 PPT용으로 요약
    """
    summarizer = ContentSummarizer()
    return summarizer.summarize(parsed_data)
