# .md 파일 규격

## Front Matter (YAML)

### 공통 필드
- type: 문서 유형 (필수)
- project: 프로젝트 코드 (필수)
- version: 문서 버전
- date: 작성일
- author: 작성자

### 문서 유형 코드
- project-plan: 프로젝트 수행계획서
- kickoff-report: 착수보고서
- weekly-report: 주간보고서
- monthly-report: 월간보고서
- interim-report: 중간보고서
- final-report: 완료보고서

## 예시: 주간보고서

\`\`\`markdown
---
type: weekly-report
project: PRJ-2025-001
week: 3
period_start: 2025-01-13
period_end: 2025-01-17
author: 홍길동
---

# 주간보고서

## 진척 현황
| 구분 | 계획 | 실적 | 차이 |
|------|:----:|:----:|:----:|
| 전체 | 8% | 8% | 0% |

## 금주 실적
- 업무 현황 분석 완료
- 현행 시스템 분석 진행 중

## 차주 계획
- 요구사항 초안 작성

## 이슈 및 위험
| ID | 내용 | 상태 | 담당 |
|----|------|------|------|
| I-001 | 서버 접근 권한 | 진행 | 김철수 |
\`\`\`
```

---

## 🤖 4단계: Antigravity Agent에게 개발 요청

Antigravity는 전체 작업을 이해하고 여러 단계를 자동으로 처리하는 AI 도구입니다. 'DB 연결이 있는 로그인 폼을 만들어줘'라고 말하면, HTML, 백엔드 코드, 유효성 검사, 테스트를 만들고 버그도 수정합니다. 

### 🎯 첫 번째 태스크: 백엔드 기본 구조

Agent Manager에서 새 태스크 생성:
```
PPT 문서 자동화 시스템의 백엔드를 구축해줘.

참고 문서:
- docs/REQUIREMENTS.md
- docs/DB_SCHEMA.md

요구사항:
1. FastAPI 프로젝트 구조 생성
2. SQLite 데이터베이스 연결 (SQLAlchemy)
3. DB 스키마에 따른 모델 생성 (users, projects, templates, documents 등)
4. 기본 CRUD API 엔드포인트 생성
5. JWT 기반 인증 구현
6. 다국어 지원을 위한 구조 (Accept-Language 헤더 처리)

기술:
- Python 3.11
- FastAPI
- SQLAlchemy
- python-jose (JWT)
- passlib (비밀번호 해시)
```

### 🎯 두 번째 태스크: .md 파서 구현
```
.md 파일을 파싱하는 서비스를 구현해줘.

참고 문서:
- docs/MD_FORMAT.md

요구사항:
1. Front Matter (YAML) 추출
2. 본문 섹션별 파싱 (H2, H3 레벨)
3. 마크다운 테이블 → 딕셔너리 변환
4. 리스트 항목 추출
5. 문서 유형별 필수 필드 검증

사용 라이브러리:
- python-frontmatter
- markdown
- PyYAML
```

### 🎯 세 번째 태스크: PPT 생성기 구현
```
PPT 자동 생성 서비스를 구현해줘.

요구사항:
1. 템플릿 PPT 파일 로드
2. {{변수명}} 플레이스홀더 치환
3. 테이블 데이터 삽입
4. 한글 처리 (UTF-8)
5. 생성된 PPT 파일 저장

사용 라이브러리:
- python-pptx

입력:
- 템플릿 PPT 파일 경로
- 변수 데이터 (딕셔너리)
- 출력 파일 경로

출력:
- 완성된 PPT 파일
```

### 🎯 네 번째 태스크: 프론트엔드 구축
```
Vue.js 3 프론트엔드를 구축해줘.

요구사항:
1. Vue 3 + Vite 프로젝트 생성
2. Vue Router 설정
3. Pinia 상태 관리
4. vue-i18n 다국어 설정 (ko, en, vi)
5. Axios API 클라이언트

페이지:
- 로그인
- 대시보드
- 프로젝트 목록/등록/수정
- 문서 생성 (유형선택 → 입력 → 미리보기 → 생성)
- 템플릿 관리

컴포넌트:
- 사이드바 메뉴
- 헤더 (언어 선택, 사용자 정보)
- 프로젝트 카드
- 문서 유형 선택 카드
- 데이터 입력 폼
- 테이블 에디터
```

---

## 📋 5단계: 작업 순서 체크리스트

Antigravity의 에이전트들은 Artifacts를 생성합니다—태스크 목록, 구현 계획, 스크린샷, 브라우저 녹화 같은 tangible한 결과물입니다. 이 Artifacts를 통해 에이전트의 로직을 한눈에 확인할 수 있습니다. 
```
[ ] 1. 프로젝트 폴더 구조 생성
[ ] 2. docs/ 폴더에 요구사항 문서 작성
[ ] 3. 백엔드 기본 구조 (FastAPI)
[ ] 4. DB 모델 생성 (SQLAlchemy)
[ ] 5. 기본 API 엔드포인트 (CRUD)
[ ] 6. 인증 시스템 (JWT)
[ ] 7. .md 파서 서비스
[ ] 8. PPT 생성기 서비스
[ ] 9. 프론트엔드 기본 구조 (Vue.js)
[ ] 10. 페이지 및 컴포넌트 개발
[ ] 11. API 연동
[ ] 12. 테스트 및 디버깅
[ ] 13. Docker 설정
[ ] 14. 샘플 템플릿 PPT 제작