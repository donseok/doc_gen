"""
마크다운 파서 서비스 (AST 기반 - mistune 활용)

개선 사항 (제미나이 분석서 반영):
- 정규표현식 기반 → AST(Abstract Syntax Tree) 기반 파서로 전환
- 복잡한 중첩 구조 및 변칙적인 마크다운 문법 지원 강화
- 더 안정적인 문법 해석 제공
"""
import re
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from mistune import create_markdown
from mistune.core import BaseRenderer


class SlideRenderer(BaseRenderer):
    """
    마크다운 AST를 슬라이드 데이터 구조로 변환하는 커스텀 렌더러
    """
    NAME = 'slide'

    def __init__(self):
        super().__init__()
        self.slides = []
        self.current_slide = None
        self.presentation_title = None

    def _ensure_slide(self):
        """현재 슬라이드가 없으면 생성"""
        if self.current_slide is None:
            self.current_slide = {
                "title": None,
                "content": [],
                "images": [],
                "code_blocks": [],
                "layout": "title_content",
            }

    def heading(self, text: str, level: int, **attrs) -> str:
        """헤딩 처리"""
        if level == 1:
            # # H1 → 프레젠테이션 제목
            self.presentation_title = text
        elif level == 2:
            # ## H2 → 새 슬라이드 시작
            if self.current_slide is not None:
                self._finalize_slide()
            self.current_slide = {
                "title": text,
                "content": [],
                "images": [],
                "code_blocks": [],
                "layout": "title_content",
            }
        elif level == 3:
            # ### H3 → 슬라이드 내 서브헤딩
            self._ensure_slide()
            self.current_slide["content"].append({
                "type": "subheading",
                "text": text,
            })
        return ''

    def paragraph(self, text: str, **attrs) -> str:
        """일반 문단 처리"""
        self._ensure_slide()
        if text.strip():
            self.current_slide["content"].append({
                "type": "text",
                "text": text.strip(),
            })
        return ''

    def list(self, text: str, ordered: bool, **attrs) -> str:
        """리스트는 개별 아이템에서 처리"""
        return text

    def list_item(self, text: str, **attrs) -> str:
        """리스트 아이템 처리"""
        self._ensure_slide()
        # 중첩된 태그 제거 및 텍스트 정리
        clean_text = self._strip_tags(text).strip()
        if clean_text:
            self.current_slide["content"].append({
                "type": "bullet",
                "text": clean_text,
            })
        return ''

    def block_code(self, code: str, info: Optional[str] = None, **attrs) -> str:
        """코드 블록 처리"""
        self._ensure_slide()
        self.current_slide["code_blocks"].append({
            "language": info or "text",
            "code": code.strip(),
        })
        return ''

    def image(self, text: str, url: str, title: Optional[str] = None, **attrs) -> str:
        """이미지 처리"""
        self._ensure_slide()
        self.current_slide["images"].append({
            "alt": text or title or "",
            "src": url,
        })
        return ''

    def codespan(self, text: str, **attrs) -> str:
        """인라인 코드 - 백틱으로 감싸서 반환"""
        return f"`{text}`"

    def emphasis(self, text: str, **attrs) -> str:
        """강조 (이탤릭)"""
        return text

    def strong(self, text: str, **attrs) -> str:
        """굵게"""
        return text

    def link(self, text: str, url: str, title: Optional[str] = None, **attrs) -> str:
        """링크 - 텍스트만 반환"""
        return text

    def text(self, text: str, **attrs) -> str:
        """일반 텍스트"""
        return text

    def linebreak(self, *args, **attrs) -> str:
        """줄바꿈"""
        return '\n'

    def softbreak(self, *args, **attrs) -> str:
        """소프트 줄바꿈"""
        return ' '

    def blank_line(self, *args, **attrs) -> str:
        """빈 줄"""
        return ''

    def thematic_break(self, *args, **attrs) -> str:
        """수평선"""
        return ''

    def block_quote(self, text: str, **attrs) -> str:
        """인용문 처리"""
        self._ensure_slide()
        clean_text = self._strip_tags(text).strip()
        if clean_text:
            self.current_slide["content"].append({
                "type": "quote",
                "text": clean_text,
            })
        return ''

    def block_html(self, html: str, **attrs) -> str:
        """HTML 블록 - 무시"""
        return ''

    def inline_html(self, html: str, **attrs) -> str:
        """인라인 HTML - 무시"""
        return ''

    def _strip_tags(self, text: str) -> str:
        """HTML/마크다운 태그 제거"""
        # 간단한 태그 제거
        clean = re.sub(r'<[^>]+>', '', text)
        return clean

    def _finalize_slide(self):
        """현재 슬라이드 완료 처리"""
        if self.current_slide:
            # 레이아웃 결정
            if self.current_slide["images"] and not self.current_slide["content"]:
                self.current_slide["layout"] = "image_only"
            elif self.current_slide["images"]:
                self.current_slide["layout"] = "image_content"
            elif self.current_slide["code_blocks"]:
                self.current_slide["layout"] = "code"

            self.slides.append(self.current_slide)

    def finalize(self) -> Dict[str, Any]:
        """파싱 완료 후 결과 반환"""
        if self.current_slide is not None:
            self._finalize_slide()

        return {
            "title": self.presentation_title,
            "slides": self.slides,
            "metadata": {},
        }


class MarkdownParserStrategy(ABC):
    """마크다운 파서 전략 인터페이스 (확장성을 위한 추상화)"""

    @abstractmethod
    def parse(self, md_content: str) -> Dict[str, Any]:
        """마크다운 파싱"""
        pass

    @abstractmethod
    def extract_metadata(self, md_content: str) -> Dict[str, str]:
        """메타데이터 추출"""
        pass


class MistuneParser(MarkdownParserStrategy):
    """
    Mistune AST 기반 마크다운 파서

    장점:
    - 표준 CommonMark 호환
    - 복잡한 중첩 구조 안정적 처리
    - 확장 가능한 플러그인 시스템
    """

    def __init__(self):
        self.renderer = SlideRenderer()
        self.markdown = create_markdown(renderer=self.renderer)

    def parse(self, md_content: str) -> Dict[str, Any]:
        """
        마크다운 내용을 파싱하여 슬라이드 데이터로 변환

        Args:
            md_content: 마크다운 문자열

        Returns:
            파싱된 슬라이드 구조 데이터
        """
        # 프론트매터 분리
        content, metadata = self._separate_frontmatter(md_content)

        # 렌더러 초기화
        self.renderer = SlideRenderer()
        self.markdown = create_markdown(renderer=self.renderer)

        # 마크다운 파싱 (AST 기반)
        self.markdown(content)

        # 결과 생성
        result = self.renderer.finalize()
        result["metadata"] = metadata

        return result

    def extract_metadata(self, md_content: str) -> Dict[str, str]:
        """YAML 프론트매터 추출"""
        _, metadata = self._separate_frontmatter(md_content)
        return metadata

    def _separate_frontmatter(self, md_content: str) -> tuple:
        """프론트매터와 본문 분리"""
        metadata = {}
        content = md_content

        if md_content.startswith('---'):
            end = md_content.find('---', 3)
            if end > 0:
                frontmatter = md_content[3:end].strip()
                content = md_content[end + 3:].strip()

                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return content, metadata


class RegexParser(MarkdownParserStrategy):
    """
    레거시 정규표현식 기반 파서 (하위 호환성 유지)

    참고: 복잡한 구조에서는 MistuneParser 사용 권장
    """

    def __init__(self):
        self.title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self.h2_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)
        self.h3_pattern = re.compile(r'^###\s+(.+)$', re.MULTILINE)
        self.bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)
        self.numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
        # 테이블 행 패턴: | 로 시작하고 끝나는 라인
        self.table_row_pattern = re.compile(r'^\|(.+)\|$', re.MULTILINE)
        # 테이블 구분선 패턴: |---|---|
        self.table_separator_pattern = re.compile(r'^\|[\s\-:]+\|$', re.MULTILINE)

    def parse(self, md_content: str) -> Dict[str, Any]:
        result = {
            "title": None,
            "slides": [],
            "metadata": {},
        }

        title_match = self.title_pattern.search(md_content)
        if title_match:
            result["title"] = title_match.group(1).strip()

        sections = self._split_by_h2(md_content)

        for section in sections:
            slide = self._parse_section(section)
            if slide:
                result["slides"].append(slide)

        return result

    def extract_metadata(self, md_content: str) -> Dict[str, str]:
        metadata = {}

        if md_content.startswith('---'):
            end = md_content.find('---', 3)
            if end > 0:
                frontmatter = md_content[3:end].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def _split_by_h2(self, content: str) -> List[str]:
        matches = list(self.h2_pattern.finditer(content))

        if not matches:
            return [content] if content.strip() else []

        sections = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section = content[start:end].strip()
            if section:
                sections.append(section)

        return sections

    def _parse_section(self, section: str) -> Optional[Dict[str, Any]]:
        slide = {
            "title": None,
            "content": [],
            "images": [],
            "code_blocks": [],
            "tables": [],  # 테이블 데이터 추가
            "layout": "title_content",
        }

        lines = section.split('\n')

        if lines and lines[0].startswith('## '):
            slide["title"] = lines[0][3:].strip()
            lines = lines[1:]

        # 테이블 파싱을 위한 상태 관리
        table_buffer = []
        in_table = False

        for line in lines:
            line = line.strip()

            if not line:
                # 테이블이 끝났으면 저장
                if in_table and table_buffer:
                    table_data = self._parse_table(table_buffer)
                    if table_data:
                        slide["tables"].append(table_data)
                    table_buffer = []
                    in_table = False
                continue

            # 테이블 행 감지 (| 로 시작하고 끝나는 라인)
            if line.startswith('|') and line.endswith('|'):
                in_table = True
                table_buffer.append(line)
                continue

            # 테이블이 끝났으면 저장
            if in_table and table_buffer:
                table_data = self._parse_table(table_buffer)
                if table_data:
                    slide["tables"].append(table_data)
                table_buffer = []
                in_table = False

            img_match = self.image_pattern.search(line)
            if img_match:
                slide["images"].append({
                    "alt": img_match.group(1),
                    "src": img_match.group(2),
                })
                continue

            bullet_match = self.bullet_pattern.match(line)
            if bullet_match:
                slide["content"].append({
                    "type": "bullet",
                    "text": bullet_match.group(1),
                })
                continue

            numbered_match = self.numbered_pattern.match(line)
            if numbered_match:
                slide["content"].append({
                    "type": "numbered",
                    "text": numbered_match.group(1),
                })
                continue

            if line.startswith('### '):
                slide["content"].append({
                    "type": "subheading",
                    "text": line[4:],
                })
                continue

            # 수평선 (---) 무시
            if line.startswith('---'):
                continue

            slide["content"].append({
                "type": "text",
                "text": line,
            })

        # 섹션 끝에서 남은 테이블 처리
        if table_buffer:
            table_data = self._parse_table(table_buffer)
            if table_data:
                slide["tables"].append(table_data)

        code_matches = self.code_block_pattern.findall(section)
        for lang, code in code_matches:
            slide["code_blocks"].append({
                "language": lang or "text",
                "code": code.strip(),
            })

        if slide["images"] and not slide["content"]:
            slide["layout"] = "image_only"
        elif slide["images"]:
            slide["layout"] = "image_content"
        elif slide["code_blocks"]:
            slide["layout"] = "code"
        elif slide["tables"]:
            slide["layout"] = "table"

        return slide if slide["title"] or slide["content"] or slide["tables"] else None

    def _parse_table(self, table_lines: List[str]) -> Optional[Dict[str, Any]]:
        """
        마크다운 테이블을 파싱하여 구조화된 데이터로 변환

        Args:
            table_lines: 테이블 행 목록 (| col1 | col2 | 형식)

        Returns:
            {"headers": [...], "rows": [[...], [...]]} 형식의 딕셔너리
        """
        if len(table_lines) < 2:
            return None

        headers = []
        rows = []

        for i, line in enumerate(table_lines):
            # | 로 분리하고 빈 셀 제거
            cells = [cell.strip() for cell in line.split('|')]
            # 앞뒤 빈 문자열 제거 (| col | col | 형식에서 발생)
            cells = [c for c in cells if c]

            # 구분선 (|---|---| 형식) 스킵
            if cells and all(set(c.replace('-', '').replace(':', '').strip()) == set() for c in cells):
                continue

            if i == 0:
                # 첫 번째 행은 헤더
                # ** 볼드 마크다운 제거
                headers = [self._clean_cell_text(c) for c in cells]
            else:
                # 나머지는 데이터 행
                if cells and len(cells) > 0:
                    rows.append([self._clean_cell_text(c) for c in cells])

        if not headers:
            return None

        return {
            "headers": headers,
            "rows": rows,
        }

    def _clean_cell_text(self, text: str) -> str:
        """셀 텍스트에서 마크다운 서식 제거"""
        # ** 볼드 제거
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # * 이탤릭 제거
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # ` 코드 제거
        text = re.sub(r'`([^`]+)`', r'\1', text)
        return text.strip()


class MarkdownParser:
    """
    마크다운 파서 팩토리 (하위 호환성 유지)

    기본적으로 AST 기반 MistuneParser를 사용하며,
    필요시 레거시 RegexParser로 전환 가능
    """

    def __init__(self, use_legacy: bool = True):
        """
        Args:
            use_legacy: True면 레거시 정규식 파서 사용 (기본값: True - mistune 3.x 호환성 이슈로)
        """
        if use_legacy:
            self._parser = RegexParser()
        else:
            self._parser = MistuneParser()

    def parse(self, md_content: str) -> Dict[str, Any]:
        """
        마크다운 내용을 파싱하여 슬라이드 데이터로 변환

        Args:
            md_content: 마크다운 문자열

        Returns:
            파싱된 슬라이드 구조 데이터
        """
        return self._parser.parse(md_content)

    def extract_metadata(self, md_content: str) -> Dict[str, str]:
        """YAML 프론트매터 추출"""
        return self._parser.extract_metadata(md_content)
