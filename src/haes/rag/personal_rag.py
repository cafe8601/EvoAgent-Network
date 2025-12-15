"""
Personal RAG - ChromaDB 기반 개인용 RAG 시스템

15-rag/chroma SKILL 기반
로컬 저장, 개인 문서 관리, 빠른 검색

Features:
- 로컬 ChromaDB 저장
- Sentence Transformers 임베딩
- 메타데이터 필터링
- 컬렉션별 문서 관리
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not installed. Run: pip install chromadb")


@dataclass
class Document:
    """문서 데이터"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """검색 결과"""
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float  # 유사도 점수 (0~1, 높을수록 유사)
    source: str = "personal"  # "personal" or "shared"


class PersonalRAG:
    """
    개인용 RAG 시스템 (ChromaDB 기반)
    
    로컬에 문서를 저장하고 검색하는 개인용 RAG
    
    사용 예시:
        rag = PersonalRAG(persist_dir="./my_rag")
        
        # 문서 추가
        rag.add_documents([
            {"content": "Python is a programming language", "metadata": {"source": "docs"}},
            {"content": "Machine learning uses algorithms", "metadata": {"source": "notes"}},
        ])
        
        # 검색
        results = rag.search("What is Python?", k=3)
        for r in results:
            print(f"{r.score:.2f}: {r.content[:100]}")
    """
    
    def __init__(
        self,
        persist_dir: str = "./personal_rag_db",
        collection_name: str = "personal_docs",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Args:
            persist_dir: ChromaDB 저장 경로
            collection_name: 컬렉션 이름
            embedding_model: Sentence Transformers 모델명
        """
        if not CHROMA_AVAILABLE:
            raise RuntimeError("ChromaDB not installed. Run: pip install chromadb")
        
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # ChromaDB 클라이언트 초기화
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # 컬렉션 가져오기 또는 생성
        self._collection = self._get_or_create_collection()
        
        logger.info(f"PersonalRAG initialized: {self.persist_dir} / {self.collection_name}")
    
    def _get_or_create_collection(self):
        """컬렉션 가져오기 또는 생성"""
        try:
            # Sentence Transformers 임베딩 함수 사용
            from chromadb.utils import embedding_functions
            
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )
            
            return self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},  # 코사인 유사도 사용
            )
        except Exception as e:
            logger.warning(f"Sentence Transformers 로드 실패, 기본 임베딩 사용: {e}")
            return self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        collection_name: Optional[str] = None,
    ) -> int:
        """
        문서 추가
        
        Args:
            documents: 문서 리스트 [{"content": str, "metadata": dict}, ...]
            collection_name: 컬렉션 이름 (None이면 기본 컬렉션)
        
        Returns:
            추가된 문서 수
        """
        if collection_name:
            collection = self.client.get_or_create_collection(collection_name)
        else:
            collection = self._collection
        
        ids = []
        contents = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{datetime.now().timestamp()}_{i}")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # 기본 메타데이터 추가
            metadata.setdefault("created_at", datetime.now().isoformat())
            metadata.setdefault("source", "personal")
            
            ids.append(doc_id)
            contents.append(content)
            metadatas.append(metadata)
        
        if contents:
            collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(contents)} documents to {collection.name}")
        
        return len(contents)
    
    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        단일 텍스트 추가
        
        Args:
            text: 텍스트 내용
            metadata: 메타데이터
            doc_id: 문서 ID (없으면 자동 생성)
        
        Returns:
            문서 ID
        """
        doc_id = doc_id or f"doc_{datetime.now().timestamp()}"
        
        self.add_documents([{
            "id": doc_id,
            "content": text,
            "metadata": metadata or {},
        }])
        
        return doc_id
    
    def search(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        문서 검색
        
        Args:
            query: 검색 쿼리
            k: 반환할 결과 수
            where: 메타데이터 필터
            collection_name: 컬렉션 이름
        
        Returns:
            검색 결과 리스트
        """
        if collection_name:
            collection = self.client.get_or_create_collection(collection_name)
        else:
            collection = self._collection
        
        # 쿼리 실행
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        
        # 결과 변환
        search_results = []
        
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # distance를 similarity로 변환 (코사인 거리 -> 유사도)
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance  # 코사인 거리를 유사도로 변환
                
                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    score=max(0, min(1, similarity)),
                    source="personal",
                ))
        
        return search_results
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """문서 조회"""
        results = self._collection.get(ids=[doc_id])
        
        if results["ids"]:
            return Document(
                id=results["ids"][0],
                content=results["documents"][0] if results["documents"] else "",
                metadata=results["metadatas"][0] if results["metadatas"] else {},
            )
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """문서 삭제"""
        try:
            self._collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """문서 업데이트"""
        try:
            update_args = {"ids": [doc_id]}
            if content:
                update_args["documents"] = [content]
            if metadata:
                update_args["metadatas"] = [metadata]
            
            self._collection.update(**update_args)
            logger.info(f"Updated document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def list_documents(
        self,
        where: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Document]:
        """문서 목록 조회"""
        results = self._collection.get(
            where=where,
            limit=limit,
            include=["documents", "metadatas"],
        )
        
        documents = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append(Document(
                id=doc_id,
                content=results["documents"][i] if results["documents"] else "",
                metadata=results["metadatas"][i] if results["metadatas"] else {},
            ))
        
        return documents
    
    def create_collection(self, name: str) -> bool:
        """새 컬렉션 생성"""
        try:
            self.client.create_collection(name)
            logger.info(f"Created collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def delete_collection(self, name: str) -> bool:
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(name)
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """컬렉션 목록"""
        collections = self.client.list_collections()
        return [c.name for c in collections]
    
    def get_stats(self) -> Dict[str, Any]:
        """RAG 통계"""
        return {
            "type": "personal",
            "backend": "chromadb",
            "persist_dir": str(self.persist_dir),
            "collection": self.collection_name,
            "document_count": self._collection.count(),
            "embedding_model": self.embedding_model,
            "collections": self.list_collections(),
        }
    
    def clear(self) -> None:
        """모든 문서 삭제"""
        # 컬렉션 재생성으로 초기화
        self.client.delete_collection(self.collection_name)
        self._collection = self._get_or_create_collection()
        logger.info(f"Cleared collection: {self.collection_name}")


# 전역 개인 RAG
_personal_rag: Optional[PersonalRAG] = None


def get_personal_rag(persist_dir: str = "./personal_rag_db") -> PersonalRAG:
    """전역 개인 RAG 반환"""
    global _personal_rag
    if _personal_rag is None:
        _personal_rag = PersonalRAG(persist_dir=persist_dir)
    return _personal_rag
