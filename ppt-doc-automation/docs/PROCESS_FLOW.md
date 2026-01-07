# PPT 문서 자동화 시스템 - 프로세스 흐름도

## 전체 프로세스 다이어그램

```mermaid
flowchart TB
    subgraph Input ["📥 입력 단계"]
        A[/"마크다운 문서 (.md)"/]
        B[/"PPT 템플릿 (.pptx)"/]
    end

    subgraph Frontend ["🖥️ 프론트엔드 (Vue.js)"]
        C[웹 애플리케이션]
        C1[템플릿 관리]
        C2[마크다운 업로드]
        C3[생성 이력 조회]
    end

    subgraph Backend ["⚙️ 백엔드 (FastAPI)"]
        D[API 서버]
        
        subgraph Pipeline ["🔄 PPT 생성 파이프라인"]
            E[MarkdownParser<br/>구조 분석]
            F{스마트 모드?}
            G[ContentSummarizer<br/>핵심 내용 요약]
            H[PPTDesigner<br/>레이아웃/스타일 결정]
            I[TemplateAnalyzer<br/>템플릿 분석]
            J[PPTGenerator<br/>PPTX 생성]
        end
    end

    subgraph Storage ["💾 저장소"]
        K[(SQLite DB)]
        L[파일 스토리지]
    end

    subgraph Output ["📤 출력 단계"]
        M[/"생성된 PPT (.pptx)"/]
        N[다운로드 URL]
    end

    A --> C2
    B --> C1
    C --> D
    
    D --> E
    E --> F
    F -->|Yes| G
    F -->|No| J
    G --> H
    H --> I
    I --> J
    
    J --> L
    J --> K
    L --> M
    K --> N
    N --> C3
    M --> C3
```

---

## 📋 프로세스 설명

| 단계 | 컴포넌트 | 역할 |
|------|----------|------|
| **1. 입력** | 사용자 | 마크다운 문서와 PPT 템플릿을 업로드 |
| **2. 파싱** | `MarkdownParser` | 마크다운을 구조화된 슬라이드 데이터로 변환 |
| **3. 요약** | `ContentSummarizer` | 긴 텍스트를 슬라이드에 적합하게 요약 |
| **4. 디자인** | `PPTDesigner` | 각 슬라이드의 레이아웃과 스타일 결정 |
| **5. 템플릿 분석** | `TemplateAnalyzer` | 템플릿의 플레이스홀더 위치 파악 |
| **6. 생성** | `PPTGenerator` | 최종 PPTX 파일 렌더링 |
| **7. 출력** | 시스템 | DB 기록 후 다운로드 URL 제공 |

---

*생성일: 2026-01-06*
