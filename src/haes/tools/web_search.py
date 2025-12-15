"""
Web Search Tool - 웹 검색 도구

DuckDuckGo (무료) 또는 Tavily (유료, 고품질) 검색
"""

import os
import asyncio
import httpx
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class SearchResult:
    """검색 결과"""
    title: str
    url: str
    snippet: str
    source: str = ""


class WebSearchTool:
    """
    웹 검색 도구
    
    - DuckDuckGo: 무료, API 키 불필요
    - Tavily: 유료 ($5/1000쿼리), AI 최적화
    """
    
    def __init__(
        self,
        provider: str = "duckduckgo",
        tavily_api_key: Optional[str] = None,
    ):
        """
        초기화
        
        Args:
            provider: 검색 제공자 ("duckduckgo" 또는 "tavily")
            tavily_api_key: Tavily API 키 (선택)
        """
        self.provider = provider
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        
        logger.info(f"WebSearchTool initialized: provider={provider}")
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[SearchResult]:
        """
        웹 검색 실행
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            
        Returns:
            검색 결과 리스트
        """
        if self.provider == "tavily" and self.tavily_api_key:
            return await self._search_tavily(query, max_results)
        else:
            return await self._search_duckduckgo(query, max_results)
    
    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[SearchResult]:
        """DuckDuckGo 검색 (무료)"""
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            results = []
            
            # Abstract (요약)
            if data.get("Abstract"):
                results.append(SearchResult(
                    title=data.get("Heading", query),
                    url=data.get("AbstractURL", ""),
                    snippet=data.get("Abstract", ""),
                    source=data.get("AbstractSource", ""),
                ))
            
            # Related Topics
            for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(SearchResult(
                        title=topic.get("Text", "")[:100],
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        source="DuckDuckGo",
                    ))
            
            # 결과가 없으면 HTML 검색 시도
            if not results:
                results = await self._search_duckduckgo_html(query, max_results)
            
            logger.debug(f"DuckDuckGo search: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    async def _search_duckduckgo_html(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[SearchResult]:
        """DuckDuckGo HTML 검색 (백업)"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                html = response.text
            
            # 간단한 파싱
            results = []
            import re
            
            # 결과 링크 추출
            pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>'
            matches = re.findall(pattern, html)
            
            for url, title in matches[:max_results]:
                # HTML 태그 제거
                title = re.sub(r'<[^>]+>', '', title)
                results.append(SearchResult(
                    title=title,
                    url=url,
                    snippet="",
                    source="DuckDuckGo",
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo HTML search error: {e}")
            return []
    
    async def _search_tavily(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[SearchResult]:
        """Tavily 검색 (유료, AI 최적화)"""
        try:
            url = "https://api.tavily.com/search"
            headers = {
                "Content-Type": "application/json",
            }
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": True,
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                data = response.json()
            
            results = []
            
            # AI 요약 답변
            if data.get("answer"):
                results.append(SearchResult(
                    title="AI 요약",
                    url="",
                    snippet=data["answer"],
                    source="Tavily AI",
                ))
            
            # 검색 결과
            for item in data.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    source=item.get("source", ""),
                ))
            
            logger.debug(f"Tavily search: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    def format_results(self, results: List[SearchResult]) -> str:
        """
        검색 결과를 포맷팅
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            포맷된 문자열
        """
        if not results:
            return "검색 결과가 없습니다."
        
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"""
### {i}. {r.title}
{r.snippet}
- 출처: {r.source}
- URL: {r.url}
""")
        
        return "\n".join(formatted)


# 싱글톤 인스턴스
_search_tool: Optional[WebSearchTool] = None

def get_search_tool() -> WebSearchTool:
    """검색 도구 싱글톤 반환"""
    global _search_tool
    if _search_tool is None:
        _search_tool = WebSearchTool()
    return _search_tool
