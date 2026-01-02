# PPT 문서 자동화 시스템 요구사항

## 프로젝트 개요
- 목적: 개발자는 .md로 작업, 고객에게는 예쁜 PPT 제공
- 핵심 타겟: 고객 대면 보고서류 (SI 프로젝트)

## 지원 문서 유형 (1단계)
1. 프로젝트 수행계획서 (최우선)
2. 주간보고서
3. 월간보고서
4. 착수보고서
5. 중간보고서
6. 완료보고서

## 입력 방식
- .md 파일 업로드 (Front Matter + 마크다운)
- 웹 폼 직접 입력
- 엑셀 업로드 (테이블 데이터)

## 다국어 지원
- 한국어 (ko) - 기본
- 영어 (en)
- 베트남어 (vi)

## 권한 체계
- admin: 시스템 관리자
- pm: 프로젝트 관리자 (PM/PL)
- member: 일반 사용자

## 기술 스택
- Frontend: Vue.js 3 + vue-i18n + Pinia
- Backend: Python 3.11 + FastAPI
- PPT 생성: python-pptx
- MD 파싱: python-frontmatter + markdown
- DB: SQLite