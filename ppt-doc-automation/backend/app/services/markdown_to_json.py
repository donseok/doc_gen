"""
마크다운 → JSON 변환기 (프로젝트 수행계획서 특화)

마크다운 문서를 컴포넌트 기반 PPT 생성에 적합한 JSON 형식으로 변환합니다.

주요 기능:
- YAML 프론트매터 파싱
- 섹션 구조 분석
- 표 데이터 추출
- 불릿 포인트 추출
- 슬라이드 타입 자동 결정
"""

import re
import yaml
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class SlideType(Enum):
    """슬라이드 타입"""
    TITLE = "title"
    TOC = "toc"
    SECTION = "section"
    CONTENT = "content"


@dataclass
class TableData:
    """표 데이터"""
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    style: str = "header_highlight"


@dataclass
class BulletItem:
    """불릿 아이템"""
    text: str
    level: int = 0
    sub_items: List['BulletItem'] = field(default_factory=list)


@dataclass
class SlideData:
    """슬라이드 데이터"""
    slide_type: str
    main_title: str = ""
    action_title: str = ""
    title: str = ""
    subtitle: str = ""
    body: List[Dict] = field(default_factory=list)
    visual_elements: List[Dict] = field(default_factory=list)
    use_action_title: bool = True
    section_number: str = ""
    items: List[Dict] = field(default_factory=list)  # TOC용


@dataclass
class PresentationData:
    """프레젠테이션 전체 데이터"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    slides: List[Dict] = field(default_factory=list)


class MarkdownToJsonConverter:
    """마크다운 → JSON 변환기
    
    프로젝트 수행계획서 형식의 마크다운을 PPT 생성용 JSON으로 변환합니다.
    
    Usage:
        converter = MarkdownToJsonConverter()
        json_data = converter.convert(markdown_content)
    """
    
    # 정규식 패턴
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    H1_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    H2_PATTERN = re.compile(r'^##\s+(.+)$', re.MULTILINE)
    H3_PATTERN = re.compile(r'^###\s+(.+)$', re.MULTILINE)
    TABLE_PATTERN = re.compile(r'^\|(.+)\|$', re.MULTILINE)
    BULLET_PATTERN = re.compile(r'^(\s*)-\s+(.+)$', re.MULTILINE)
    NUMBERED_PATTERN = re.compile(r'^(\s*)\d+\.\s+(.+)$', re.MULTILINE)
    
    # 섹션 키워드 매핑 (KPI 추출용)
    KPI_KEYWORDS = ['효율', '향상', '달성', '절감', '증가', '감소', '%']
    
    def __init__(self, max_slides: int = 20):
        """초기화
        
        Args:
            max_slides: 최대 슬라이드 수
        """
        self.max_slides = max_slides
        self.section_counter = 0
    
    def convert(self, markdown_content: str) -> Dict[str, Any]:
        """마크다운을 JSON으로 변환
        
        Args:
            markdown_content: 마크다운 텍스트
            
        Returns:
            PPT 생성용 JSON 딕셔너리
        """
        self.section_counter = 0
        
        # 1. 프론트매터 추출
        metadata = self._extract_frontmatter(markdown_content)
        content = self._remove_frontmatter(markdown_content)
        
        # 2. 문서 제목 추출
        doc_title = self._extract_title(content)
        
        # 3. 섹션 분할
        sections = self._split_sections(content)
        
        # 4. 슬라이드 생성
        slides = []
        
        # 표지 슬라이드
        title_slide = self._create_title_slide(doc_title, metadata)
        slides.append(asdict(title_slide) if hasattr(title_slide, '__dataclass_fields__') else title_slide)
        
        # 목차 슬라이드
        toc_slide = self._create_toc_slide(sections)
        slides.append(toc_slide)
        
        # 본문 슬라이드들
        for section in sections:
            section_slides = self._process_section(section)
            slides.extend(section_slides)
            
            if len(slides) >= self.max_slides:
                break
        
        return {
            "metadata": metadata,
            "slides": slides[:self.max_slides]
        }
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """YAML 프론트매터 추출"""
        match = self.FRONTMATTER_PATTERN.match(content)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                pass
        return {}
    
    def _remove_frontmatter(self, content: str) -> str:
        """프론트매터 제거"""
        return self.FRONTMATTER_PATTERN.sub('', content)
    
    def _extract_title(self, content: str) -> str:
        """H1 제목 추출"""
        match = self.H1_PATTERN.search(content)
        return match.group(1).strip() if match else "프레젠테이션"
    
    def _split_sections(self, content: str) -> List[Dict[str, Any]]:
        """H2로 섹션 분할"""
        sections = []
        
        # H2로 분할
        parts = re.split(r'\n(?=##\s+)', content)
        
        for part in parts:
            if not part.strip():
                continue
            
            h2_match = self.H2_PATTERN.match(part)
            if h2_match:
                section_title = h2_match.group(1).strip()
                section_content = part[h2_match.end():].strip()
                
                sections.append({
                    "title": section_title,
                    "content": section_content
                })
        
        return sections
    
    def _create_title_slide(self, title: str, metadata: Dict) -> Dict[str, Any]:
        """표지 슬라이드 생성"""
        return {
            "slide_type": "title",
            "title": title,
            "subtitle": metadata.get('project', ''),
            "author": metadata.get('author', ''),
            "date": metadata.get('date', ''),
            "department": ""
        }
    
    def _create_toc_slide(self, sections: List[Dict]) -> Dict[str, Any]:
        """목차 슬라이드 생성"""
        items = []
        
        for i, section in enumerate(sections[:5]):  # 최대 5개
            # 섹션 제목에서 번호 추출
            title = section["title"]
            number_match = re.match(r'^(\d+)\.\s*(.+)$', title)
            
            if number_match:
                num = number_match.group(1)
                clean_title = number_match.group(2)
            else:
                num = f"{i+1:02d}"
                clean_title = title
            
            items.append({
                "number": num if len(num) > 1 else f"0{num}",
                "title": clean_title,
                "page_range": f"{(i+1)*2+1:02d}-{(i+1)*2+3:02d}"
            })
        
        return {
            "slide_type": "toc",
            "title": "Contents",
            "items": items
        }
    
    def _process_section(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """섹션 처리하여 슬라이드들 생성"""
        slides = []
        title = section["title"]
        content = section["content"]
        
        # 섹션 번호 추출
        self.section_counter += 1
        number_match = re.match(r'^(\d+)\.\s*(.+)$', title)
        if number_match:
            section_number = f"{int(number_match.group(1)):02d}"
            section_title = number_match.group(2)
        else:
            section_number = f"{self.section_counter:02d}"
            section_title = title
        
        # 섹션 구분 슬라이드
        section_slide = {
            "slide_type": "section",
            "section_number": section_number,
            "title": section_title
        }
        slides.append(section_slide)
        
        # H3 하위 섹션 처리
        subsections = self._split_subsections(content)
        
        for subsection in subsections:
            subsection_slides = self._create_content_slides(subsection, section_title)
            slides.extend(subsection_slides)
        
        # H3가 없는 경우 전체 내용을 하나의 슬라이드로
        if not subsections and content.strip():
            content_slide = self._create_simple_content_slide(section_title, content)
            if content_slide:
                slides.append(content_slide)
        
        return slides
    
    def _split_subsections(self, content: str) -> List[Dict[str, Any]]:
        """H3로 하위 섹션 분할"""
        subsections = []
        
        parts = re.split(r'\n(?=###\s+)', content)
        
        for part in parts:
            if not part.strip():
                continue
            
            h3_match = self.H3_PATTERN.match(part)
            if h3_match:
                subsection_title = h3_match.group(1).strip()
                subsection_content = part[h3_match.end():].strip()
                
                subsections.append({
                    "title": subsection_title,
                    "content": subsection_content
                })
        
        return subsections
    
    def _create_content_slides(
        self, 
        subsection: Dict[str, Any], 
        parent_title: str
    ) -> List[Dict[str, Any]]:
        """하위 섹션에서 콘텐츠 슬라이드 생성"""
        slides = []
        
        title = subsection["title"]
        content = subsection["content"]
        
        # 표 추출
        tables = self._extract_tables(content)
        
        # 불릿 추출
        bullets = self._extract_bullets(content)
        
        # KPI 추출 (숫자 + %)
        kpis = self._extract_kpis(content)
        
        # 슬라이드 생성
        visual_elements = []
        
        # 표가 있으면 표 슬라이드
        if tables:
            for table in tables:
                visual_elements.append({
                    "type": "table",
                    "data": {
                        "headers": table["headers"],
                        "rows": table["rows"],
                        "style": "header_highlight"
                    }
                })
        
        # KPI가 있으면 big_numbers
        if kpis and len(kpis) >= 2:
            visual_elements.append({
                "type": "big_numbers",
                "data": {
                    "items": kpis[:4],
                    "columns": min(len(kpis), 4)
                }
            })
        
        # 불릿이 있으면 body에 추가
        body = []
        if bullets:
            for bullet in bullets[:5]:  # 최대 5개
                body.append({
                    "text": bullet["text"],
                    "level": bullet["level"]
                })
        
        # 슬라이드 구성
        if visual_elements or body:
            slide = {
                "slide_type": "content",
                "main_title": parent_title,
                "action_title": title,
                "use_action_title": True,
                "body": body if not visual_elements else [],
                "visual_elements": visual_elements,
                "footer_text": ""
            }
            slides.append(slide)
        
        return slides
    
    def _create_simple_content_slide(
        self, 
        title: str, 
        content: str
    ) -> Optional[Dict[str, Any]]:
        """간단한 콘텐츠 슬라이드 생성"""
        # 표 추출
        tables = self._extract_tables(content)
        bullets = self._extract_bullets(content)
        
        visual_elements = []
        body = []
        
        if tables:
            for table in tables[:1]:  # 첫 번째 표만
                visual_elements.append({
                    "type": "table",
                    "data": {
                        "headers": table["headers"],
                        "rows": table["rows"][:8],  # 최대 8행
                        "style": "header_highlight"
                    }
                })
        
        if bullets:
            for bullet in bullets[:5]:
                body.append({
                    "text": bullet["text"],
                    "level": bullet["level"]
                })
        
        if not visual_elements and not body:
            return None
        
        # 첫 문장을 action_title로
        first_line = content.split('\n')[0].strip()
        action_title = first_line[:80] if len(first_line) > 80 else first_line
        
        return {
            "slide_type": "content",
            "main_title": title,
            "action_title": action_title if not action_title.startswith('|') else "",
            "use_action_title": bool(action_title and not action_title.startswith('|')),
            "body": body if not visual_elements else [],
            "visual_elements": visual_elements,
            "footer_text": ""
        }
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """마크다운 표 추출"""
        tables = []
        
        # 표 블록 찾기
        lines = content.split('\n')
        in_table = False
        current_table_lines = []
        
        for line in lines:
            if line.strip().startswith('|') and line.strip().endswith('|'):
                in_table = True
                current_table_lines.append(line.strip())
            else:
                if in_table and current_table_lines:
                    table = self._parse_table(current_table_lines)
                    if table:
                        tables.append(table)
                    current_table_lines = []
                in_table = False
        
        # 마지막 표 처리
        if current_table_lines:
            table = self._parse_table(current_table_lines)
            if table:
                tables.append(table)
        
        return tables
    
    def _parse_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """표 라인들을 파싱"""
        if len(lines) < 2:
            return None
        
        # 헤더
        header_line = lines[0]
        headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # 구분선 건너뛰기 (|---|---|)
        start_idx = 1
        if len(lines) > 1 and re.match(r'^\|[\s\-:]+\|$', lines[1]):
            start_idx = 2
        
        # 데이터 행
        rows = []
        for line in lines[start_idx:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                rows.append(cells)
        
        if not headers or not rows:
            return None
        
        return {
            "headers": headers,
            "rows": rows
        }
    
    def _extract_bullets(self, content: str) -> List[Dict[str, Any]]:
        """불릿 포인트 추출"""
        bullets = []
        
        for match in self.BULLET_PATTERN.finditer(content):
            indent = len(match.group(1))
            text = match.group(2).strip()
            
            # **강조** 제거
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            
            level = indent // 2  # 2칸 들여쓰기 = 1레벨
            bullets.append({
                "text": text,
                "level": min(level, 2)
            })
        
        # 번호 목록도 처리
        for match in self.NUMBERED_PATTERN.finditer(content):
            indent = len(match.group(1))
            text = match.group(2).strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            
            level = indent // 2
            bullets.append({
                "text": text,
                "level": min(level, 2)
            })
        
        return bullets
    
    def _extract_kpis(self, content: str) -> List[Dict[str, Any]]:
        """KPI/지표 추출 (숫자 + %)"""
        kpis = []
        
        # 숫자% 패턴 (예: 30% 향상, 99.5% 달성)
        kpi_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*%\s*(\S+)')
        
        for match in kpi_pattern.finditer(content):
            value = match.group(1)
            label_hint = match.group(2)
            
            # 컨텍스트에서 라벨 추출
            start = max(0, match.start() - 30)
            context = content[start:match.end() + 10]
            
            # 라벨 결정
            if '향상' in context or '증가' in context:
                label = label_hint if label_hint != '향상' else '효율 향상'
                change = f"+{value}%"
            elif '절감' in context or '감소' in context:
                label = label_hint if label_hint != '절감' else '비용 절감'
                change = f"-{value}%"
            elif '달성' in context:
                label = label_hint if label_hint != '달성' else '목표 달성'
                change = ""
            else:
                label = label_hint
                change = ""
            
            kpis.append({
                "value": f"{value}%",
                "label": label,
                "change": change
            })
        
        return kpis


def convert_markdown_to_json(markdown_content: str) -> Dict[str, Any]:
    """편의 함수: 마크다운을 JSON으로 변환
    
    Args:
        markdown_content: 마크다운 텍스트
        
    Returns:
        PPT 생성용 JSON 딕셔너리
    """
    converter = MarkdownToJsonConverter()
    return converter.convert(markdown_content)


def convert_file(input_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """파일 변환 함수
    
    Args:
        input_path: 입력 마크다운 파일 경로
        output_path: 출력 JSON 파일 경로 (선택적)
        
    Returns:
        변환된 JSON 데이터
    """
    import json
    
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    json_data = convert_markdown_to_json(markdown_content)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return json_data
