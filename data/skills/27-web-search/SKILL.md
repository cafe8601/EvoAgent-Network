---
name: Web Search
description: 실시간 웹 검색으로 최신 정보 조회
version: 1.0.0
category: tools
keywords:
  - 검색
  - search
  - 최신
  - latest
  - 뉴스
  - news
  - 현재
  - current
  - 오늘
  - today
  - 2024
  - 2025
  - 트렌드
  - trend
---

# Web Search SKILL

실시간 웹 검색을 통해 최신 정보를 조회합니다.

## 언제 사용하나요?

- 최신 뉴스나 트렌드 조회
- 현재 시점의 정보가 필요할 때
- 특정 제품/서비스의 현재 상태 확인
- "오늘", "최신", "현재" 등의 키워드가 포함된 쿼리

## 사용 방법

### Python 코드

```python
from haes.tools import get_search_tool

# 검색 도구 가져오기
search = get_search_tool()

# 검색 실행
results = await search.search("GPT-5 최신 뉴스")

# 결과 포맷팅
formatted = search.format_results(results)
print(formatted)
```

### 검색 결과 구조

```python
@dataclass
class SearchResult:
    title: str      # 제목
    url: str        # URL
    snippet: str    # 내용 요약
    source: str     # 출처
```

## 지원 검색 엔진

| 엔진 | 비용 | API 키 | 특징 |
|------|------|--------|------|
| DuckDuckGo | 무료 | 불필요 | 기본 검색 |
| Tavily | $5/1000쿼리 | 필요 | AI 최적화, 요약 제공 |

## 설정

### DuckDuckGo (기본)

별도 설정 불필요.

### Tavily (고품질)

```bash
export TAVILY_API_KEY=tvly-xxxxx
```

## 예시 쿼리

- "GPT-5 출시일"
- "2024년 AI 트렌드"
- "테슬라 주가 최신"
- "한국 경제 뉴스 오늘"

## 한계

- DuckDuckGo는 실시간 검색 결과가 제한적일 수 있음
- 일부 최신 정보는 인덱싱 지연이 있을 수 있음
- 복잡한 쿼리는 Tavily 권장
