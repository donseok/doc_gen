# Templates 디렉토리

PPT 문서 자동화 시스템의 템플릿을 관리하는 폴더입니다.

## 디렉토리 구조

```
templates/
├── markdown/           # 마크다운 문서 템플릿 (.md)
│   ├── group/          # 그룹사 공통 표준 템플릿
│   │   ├── 프로젝트_수행계획서.md
│   │   ├── 주간업무보고서.md
│   │   └── 킥오프_보고서.md
│   └── customer/       # 고객사별 맞춤 템플릿
│       ├── {고객사명}/
│       └── ...
│
├── pptx/               # PPT 마스터 템플릿 (.pptx)
│   ├── group/          # 그룹사 공통 PPT 양식
│   │   └── PPT기본양식.pptx
│   └── customer/       # 고객사별 PPT 양식
│       ├── {고객사명}/
│       └── ...
│
└── README.md           # 이 파일
```

## 템플릿 분류 기준

### 그룹사 공통 (group/)
- 내부 표준 문서 양식
- 회사 CI/BI 반영
- 전사 공통 사용 가능
- 버전 관리 필수

### 고객사별 (customer/)
- 프로젝트별 맞춤 양식
- 고객사 브랜드 가이드 반영
- 고객사명 폴더로 구분
- 프로젝트 종료 후 아카이브

## 마크다운 템플릿 명명 규칙

```
{문서유형}_{용도}.md

예시:
- 프로젝트_수행계획서.md
- 주간업무보고서.md
- 킥오프_보고서.md
- 시스템_설계서.md
```

## PPT 템플릿 명명 규칙

```
{회사명}_PPT양식_{버전}.pptx

예시:
- 동국제강_PPT양식_v1.0.pptx
- 고객사A_PPT양식_v1.0.pptx
```

## 사용 방법

### 1. 마크다운 템플릿 사용
```bash
# 템플릿 복사 후 내용 작성
cp templates/markdown/group/프로젝트_수행계획서.md docs/my_project.md
```

### 2. PPT 템플릿 적용
```python
from app.services.json_to_ppt_generator import JsonToPptGenerator

generator = JsonToPptGenerator(
    template_path='templates/pptx/group/PPT기본양식.pptx'
)
```

## 템플릿 추가 시 체크리스트

- [ ] 적절한 분류 폴더에 배치
- [ ] 명명 규칙 준수
- [ ] 필수 섹션 포함 여부 확인
- [ ] 테스트 생성 수행
- [ ] README 업데이트 (필요 시)
