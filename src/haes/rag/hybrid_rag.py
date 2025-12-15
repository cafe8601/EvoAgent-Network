"""
Hybrid RAG - 공용 + 개인용 통합 RAG 시스템

두 가지 RAG 시스템 통합:
- 공용 RAG (Google Gemini File Search): 팀 공유 문서
- 개인용 RAG (ChromaDB): 개인 로컬 문서

검색 시 두 시스템을 모두 조회하고 결과를 통합 정렬
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from haes.rag.personal_rag import PersonalRAG, SearchResult as PersonalResult
from haes.rag.shared_rag import SharedRAG, SharedSearchResult


class RAGType(Enum):
    """RAG 유형"""
    PERSONAL = "personal"  # ChromaDB
    SHARED = "shared"      # Google Gemini File Search
    HYBRID = "hybrid"      # 둘 다


@dataclass
class HybridSearchResult:
    """하이브리드 검색 결과"""
    content: str
    score: float
    source: str  # "personal" or "shared"
    metadata: Dict[str, Any]
    doc_id: Optional[str] = None
    file_name: Optional[str] = None


class HybridRAG:
    """
    하이브리드 RAG 시스템
    
    공용(Google Gemini) + 개인용(ChromaDB) RAG 통합
    
    사용 예시:
        rag = HybridRAG(
            personal_persist_dir="./my_rag",
            google_api_key="your-api-key"
        )
        
        # 개인 문서 추가
        rag.add_personal_document("My notes about ML", metadata={"topic": "ml"})
        
        # 공용 파일 업로드
        rag.upload_shared_file("./team_docs.pdf")
        
        # 하이브리드 검색 (두 시스템 모두 검색)
        results = rag.search("machine learning", rag_type=RAGType.HYBRID)
        
        # 개인용만 검색
        personal_results = rag.search("my notes", rag_type=RAGType.PERSONAL)
    """
    
    def __init__(
        self,
        personal_persist_dir: str = "./personal_rag_db",
        google_api_key: Optional[str] = None,
        enable_personal: bool = True,
        enable_shared: bool = True,
        personal_weight: float = 0.5,  # 개인용 결과 가중치 (0~1)
    ):
        """
        Args:
            personal_persist_dir: 개인용 RAG 저장 경로
            google_api_key: Google API Key
            enable_personal: 개인용 RAG 활성화
            enable_shared: 공용 RAG 활성화
            personal_weight: 결과 합산 시 개인용 가중치
        """
        self.enable_personal = enable_personal
        self.enable_shared = enable_shared
        self.personal_weight = personal_weight
        
        # 개인용 RAG (ChromaDB)
        self._personal_rag: Optional[PersonalRAG] = None
        if enable_personal:
            try:
                self._personal_rag = PersonalRAG(persist_dir=personal_persist_dir)
                logger.info("Personal RAG (ChromaDB) enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Personal RAG: {e}")
                self.enable_personal = False
        
        # 공용 RAG (Google Gemini)
        self._shared_rag: Optional[SharedRAG] = None
        if enable_shared and google_api_key:
            try:
                self._shared_rag = SharedRAG(api_key=google_api_key)
                logger.info("Shared RAG (Google Gemini) enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Shared RAG: {e}")
                self.enable_shared = False
        elif enable_shared:
            logger.warning("Shared RAG disabled: Google API key not provided")
            self.enable_shared = False
        
        logger.info(f"HybridRAG initialized: personal={self.enable_personal}, shared={self.enable_shared}")
    
    # =====================
    # 개인용 RAG 메서드
    # =====================
    
    def add_personal_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> Optional[str]:
        """개인 문서 추가"""
        if not self._personal_rag:
            logger.warning("Personal RAG not available")
            return None
        
        return self._personal_rag.add_text(content, metadata, doc_id)
    
    def add_personal_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> int:
        """개인 문서 다수 추가"""
        if not self._personal_rag:
            logger.warning("Personal RAG not available")
            return 0
        
        return self._personal_rag.add_documents(documents)
    
    def delete_personal_document(self, doc_id: str) -> bool:
        """개인 문서 삭제"""
        if not self._personal_rag:
            return False
        return self._personal_rag.delete_document(doc_id)
    
    def list_personal_documents(
        self,
        where: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """개인 문서 목록"""
        if not self._personal_rag:
            return []
        
        docs = self._personal_rag.list_documents(where, limit)
        return [{"id": d.id, "content": d.content, "metadata": d.metadata} for d in docs]
    
    # =====================
    # 공용 RAG 메서드
    # =====================
    
    def upload_shared_file(
        self,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        wait_for_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """공용 파일 업로드"""
        if not self._shared_rag:
            logger.warning("Shared RAG not available")
            return None
        
        doc = self._shared_rag.upload_file(file_path, display_name, metadata)
        
        if wait_for_active:
            self._shared_rag.wait_for_processing(doc.id)
        
        return {
            "id": doc.id,
            "name": doc.name,
            "uri": doc.uri,
            "state": doc.state,
        }
    
    def delete_shared_file(self, file_id: str) -> bool:
        """공용 파일 삭제"""
        if not self._shared_rag:
            return False
        return self._shared_rag.delete_file(file_id)
    
    def list_shared_files(self) -> List[Dict[str, Any]]:
        """공용 파일 목록"""
        if not self._shared_rag:
            return []
        
        files = self._shared_rag.list_files()
        return [
            {"id": f.id, "name": f.name, "state": f.state, "size": f.size_bytes}
            for f in files
        ]
    
    # =====================
    # 하이브리드 검색
    # =====================
    
    def search(
        self,
        query: str,
        k: int = 10,
        rag_type: RAGType = RAGType.HYBRID,
        personal_filter: Optional[Dict[str, Any]] = None,
        shared_file_ids: Optional[List[str]] = None,
    ) -> List[HybridSearchResult]:
        """
        하이브리드 검색
        
        Args:
            query: 검색 쿼리
            k: 반환할 결과 수
            rag_type: RAG 유형 (PERSONAL, SHARED, HYBRID)
            personal_filter: 개인용 RAG 필터
            shared_file_ids: 공용 RAG에서 검색할 파일 ID
        
        Returns:
            통합 검색 결과 (점수순 정렬)
        """
        results: List[HybridSearchResult] = []
        
        # 개인용 RAG 검색
        if rag_type in (RAGType.PERSONAL, RAGType.HYBRID) and self._personal_rag:
            try:
                personal_results = self._personal_rag.search(
                    query=query,
                    k=k,
                    where=personal_filter,
                )
                
                for r in personal_results:
                    # 개인용 결과에 가중치 적용
                    adjusted_score = r.score * self.personal_weight
                    
                    results.append(HybridSearchResult(
                        content=r.content,
                        score=adjusted_score,
                        source="personal",
                        metadata=r.metadata,
                        doc_id=r.id,
                    ))
            except Exception as e:
                logger.error(f"Personal RAG search failed: {e}")
        
        # 공용 RAG 검색
        if rag_type in (RAGType.SHARED, RAGType.HYBRID) and self._shared_rag:
            try:
                shared_results = self._shared_rag.rag_search(
                    query=query,
                    file_ids=shared_file_ids,
                    k=k,
                )
                
                for r in shared_results:
                    # 공용 결과에 (1-가중치) 적용
                    adjusted_score = r.relevance_score * (1 - self.personal_weight)
                    
                    results.append(HybridSearchResult(
                        content=r.content,
                        score=adjusted_score,
                        source="shared",
                        metadata={"file_name": r.file_name},
                        file_name=r.file_name,
                    ))
            except Exception as e:
                logger.error(f"Shared RAG search failed: {e}")
        
        # 점수순 정렬
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:k]
    
    def search_personal(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[HybridSearchResult]:
        """개인용 RAG만 검색"""
        return self.search(
            query=query,
            k=k,
            rag_type=RAGType.PERSONAL,
            personal_filter=where,
        )
    
    def search_shared(
        self,
        query: str,
        k: int = 5,
        file_ids: Optional[List[str]] = None,
    ) -> List[HybridSearchResult]:
        """공용 RAG만 검색"""
        return self.search(
            query=query,
            k=k,
            rag_type=RAGType.SHARED,
            shared_file_ids=file_ids,
        )
    
    # =====================
    # 유틸리티
    # =====================
    
    def get_context(
        self,
        query: str,
        k: int = 5,
        rag_type: RAGType = RAGType.HYBRID,
        max_tokens: int = 4000,
    ) -> str:
        """
        LLM 컨텍스트용 검색 결과 생성
        
        검색 결과를 LLM 프롬프트에 삽입할 수 있는 형식으로 반환
        
        Args:
            query: 검색 쿼리
            k: 검색할 문서 수
            rag_type: RAG 유형
            max_tokens: 최대 토큰 수 (대략적 추정)
        
        Returns:
            컨텍스트 문자열
        """
        results = self.search(query, k, rag_type)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # 토큰 추정 (1 토큰 ≈ 4 문자)
        
        for i, r in enumerate(results, 1):
            source_label = f"[{r.source.upper()}]"
            if r.file_name:
                source_label += f" ({r.file_name})"
            elif r.doc_id:
                source_label += f" (doc:{r.doc_id[:8]})"
            
            part = f"--- Document {i} {source_label} (score: {r.score:.2f}) ---\n{r.content}\n"
            
            if total_chars + len(part) > max_chars:
                break
            
            context_parts.append(part)
            total_chars += len(part)
        
        return "\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """RAG 시스템 통계"""
        stats = {
            "type": "hybrid",
            "personal_enabled": self.enable_personal,
            "shared_enabled": self.enable_shared,
            "personal_weight": self.personal_weight,
        }
        
        if self._personal_rag:
            stats["personal"] = self._personal_rag.get_stats()
        
        if self._shared_rag:
            stats["shared"] = self._shared_rag.get_stats()
        
        return stats
    
    @property
    def personal(self) -> Optional[PersonalRAG]:
        """개인용 RAG 접근"""
        return self._personal_rag
    
    @property
    def shared(self) -> Optional[SharedRAG]:
        """공용 RAG 접근"""
        return self._shared_rag


# 전역 하이브리드 RAG
_hybrid_rag: Optional[HybridRAG] = None


def get_hybrid_rag(
    personal_persist_dir: str = "./personal_rag_db",
    google_api_key: Optional[str] = None,
) -> HybridRAG:
    """전역 하이브리드 RAG 반환"""
    global _hybrid_rag
    if _hybrid_rag is None:
        _hybrid_rag = HybridRAG(
            personal_persist_dir=personal_persist_dir,
            google_api_key=google_api_key,
        )
    return _hybrid_rag
