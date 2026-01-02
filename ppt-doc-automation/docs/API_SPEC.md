# API 명세서

## 개요
- **Base URL**: `http://localhost:8000/api`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)

---

## 인증
현재 버전에서는 인증이 구현되어 있지 않습니다.

---

## 엔드포인트

### 📋 Templates (템플릿)

#### 템플릿 목록 조회
```http
GET /api/templates
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | N | 페이지 번호 (기본값: 1) |
| page_size | int | N | 페이지 크기 (기본값: 10, 최대: 100) |
| is_active | bool | N | 활성 상태 필터 |

**Response**
```json
{
  "items": [
    {
      "id": 1,
      "name": "기본 템플릿",
      "description": "깔끔한 기본 템플릿",
      "file_path": "/templates/default/template.pptx",
      "is_default": true,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

#### 템플릿 상세 조회
```http
GET /api/templates/{template_id}
```

#### 템플릿 생성
```http
POST /api/templates
```

**Request Body**
```json
{
  "name": "새 템플릿",
  "description": "템플릿 설명",
  "file_path": "/templates/new/template.pptx",
  "is_default": false
}
```

#### 템플릿 수정
```http
PUT /api/templates/{template_id}
```

#### 템플릿 삭제
```http
DELETE /api/templates/{template_id}
```

---

### 📄 Documents (문서)

#### 문서 목록 조회
```http
GET /api/documents
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | N | 페이지 번호 |
| page_size | int | N | 페이지 크기 |
| status | str | N | 상태 필터 (pending, processing, completed, failed) |

#### 문서 상세 조회
```http
GET /api/documents/{document_id}
```

#### 문서 다운로드
```http
GET /api/documents/{document_id}/download
```

**Response**: PPTX 파일 바이너리

#### 문서 삭제
```http
DELETE /api/documents/{document_id}
```

---

### ⚡ Generate (PPT 생성)

#### 텍스트로 PPT 생성
```http
POST /api/generate/from-text
```

**Request Body**
```json
{
  "md_content": "# 제목\n\n## 슬라이드 1\n- 내용",
  "template_id": 1,
  "options": {}
}
```

**Response**
```json
{
  "document_id": 1,
  "status": "completed",
  "message": "PPT가 성공적으로 생성되었습니다",
  "download_url": "/api/documents/1/download"
}
```

#### 파일로 PPT 생성
```http
POST /api/generate/from-file
```

**Request**: `multipart/form-data`
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | File | Y | .md 파일 |
| template_id | int | N | 템플릿 ID |

---

## 오류 응답

**형식**
```json
{
  "detail": "오류 메시지"
}
```

**HTTP 상태 코드**
| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 |
| 404 | 리소스 없음 |
| 500 | 서버 오류 |
