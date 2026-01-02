# 데이터베이스 스키마

## 테이블 목록
1. users - 사용자
2. roles - 역할/권한
3. customers - 고객사
4. projects - 프로젝트
5. project_members - 프로젝트 참여자
6. project_staff - 투입 인력
7. milestones - 마일스톤
8. templates - PPT 템플릿
9. documents - 생성된 문서
10. issues - 이슈/위험

## 상세 스키마

### users
- id: INTEGER PRIMARY KEY
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- name: VARCHAR(100) NOT NULL
- name_en: VARCHAR(100)
- name_vi: VARCHAR(100)
- role_id: INTEGER FK -> roles
- language: VARCHAR(10) DEFAULT 'ko'
- is_active: BOOLEAN DEFAULT TRUE
- created_at: DATETIME
- updated_at: DATETIME

### projects
- id: INTEGER PRIMARY KEY
- code: VARCHAR(50) UNIQUE NOT NULL
- name: VARCHAR(300) NOT NULL
- name_en: VARCHAR(300)
- name_vi: VARCHAR(300)
- customer_id: INTEGER FK -> customers
- description: TEXT
- objectives: TEXT
- scope: TEXT
- start_date: DATE NOT NULL
- end_date: DATE NOT NULL
- pm_name: VARCHAR(100)
- pl_name: VARCHAR(100)
- status: VARCHAR(20) DEFAULT 'active'
- language: VARCHAR(10) DEFAULT 'ko'
- created_by: INTEGER FK -> users
- created_at: DATETIME
- updated_at: DATETIME

### templates
- id: INTEGER PRIMARY KEY
- project_id: INTEGER FK (nullable)
- customer_id: INTEGER FK (nullable)
- doc_type: VARCHAR(50) NOT NULL
- name: VARCHAR(200) NOT NULL
- file_path: VARCHAR(500) NOT NULL
- is_default: BOOLEAN DEFAULT FALSE
- variables: TEXT (JSON)
- language: VARCHAR(10) DEFAULT 'ko'
- created_by: INTEGER FK -> users
- created_at: DATETIME

### documents
- id: INTEGER PRIMARY KEY
- project_id: INTEGER FK NOT NULL
- template_id: INTEGER FK
- doc_type: VARCHAR(50) NOT NULL
- title: VARCHAR(300) NOT NULL
- version: VARCHAR(20) DEFAULT 'v1.0'
- content: TEXT (JSON)
- source_md_path: VARCHAR(500)
- output_path: VARCHAR(500)
- report_date: DATE
- period_start: DATE
- period_end: DATE
- week_number: INTEGER
- created_by: INTEGER FK NOT NULL
- created_at: DATETIME