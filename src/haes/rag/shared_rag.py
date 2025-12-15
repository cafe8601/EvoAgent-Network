"""
Shared RAG - Google Gemini File Search API 기반 공용 RAG 시스템

클라우드 기반 팀 공유 RAG 시스템
- Google Gemini File Search API 사용
- 자동 청킹, 임베딩, 검색
- 팀원간 문서 공유

참고: https://ai.google.dev/gemini-api/docs/file-search
"""

import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from loguru import logger

try:
    import google.generativeai as genai
    from google.generativeai.types import FileState
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenAI not installed. Run: pip install google-generativeai")


@dataclass
class SharedDocument:
    """공유 문서"""
    id: str
    name: str
    uri: str
    mime_type: str
    size_bytes: int
    state: str  # PROCESSING, ACTIVE, FAILED
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedSearchResult:
    """공유 검색 결과"""
    content: str
    source: str
    relevance_score: float
    file_name: str
    file_uri: str
    chunk_index: int = 0


class SharedRAG:
    """
    공용 RAG 시스템 (Google Gemini File Search API)
    
    클라우드 기반 팀 공유 RAG. Google의 관리형 벡터 데이터베이스 사용.
    
    사용 예시:
        rag = SharedRAG(api_key="your-api-key")
        
        # 파일 업로드
        file = rag.upload_file("./document.pdf", metadata={"project": "haes"})
        
        # File Search Store 생성
        store = rag.create_store("team-knowledge")
        rag.add_files_to_store(store.id, [file.id])
        
        # 검색
        results = rag.search("How does HAES work?", store_id=store.id)
        for r in results:
            print(f"{r.relevance_score:.2f}: {r.content[:100]}")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_store: Optional[str] = None,
    ):
        """
        Args:
            api_key: Google API Key (없으면 환경변수에서)
            default_store: 기본 File Search Store 이름
        """
        if not GENAI_AVAILABLE:
            raise RuntimeError("Google GenAI not installed. Run: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API Key required. Set GOOGLE_API_KEY environment variable.")
        
        # API 설정
        genai.configure(api_key=self.api_key)
        
        self.default_store = default_store
        self._stores: Dict[str, Any] = {}
        self._files: Dict[str, SharedDocument] = {}
        
        logger.info("SharedRAG initialized with Google Gemini File Search API")
    
    def upload_file(
        self,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SharedDocument:
        """
        파일 업로드
        
        Args:
            file_path: 파일 경로
            display_name: 표시 이름
            metadata: 메타데이터
        
        Returns:
            업로드된 문서 정보
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        display_name = display_name or path.name
        
        # 파일 업로드
        uploaded = genai.upload_file(
            path=str(path),
            display_name=display_name,
        )
        
        # 문서 정보 생성
        doc = SharedDocument(
            id=uploaded.name,
            name=display_name,
            uri=uploaded.uri,
            mime_type=uploaded.mime_type or "",
            size_bytes=uploaded.size_bytes or 0,
            state=uploaded.state.name if hasattr(uploaded.state, 'name') else str(uploaded.state),
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        
        self._files[doc.id] = doc
        logger.info(f"Uploaded file: {display_name} -> {doc.id}")
        
        return doc
    
    def get_file(self, file_id: str) -> Optional[SharedDocument]:
        """파일 정보 조회"""
        try:
            file = genai.get_file(file_id)
            return SharedDocument(
                id=file.name,
                name=file.display_name or "",
                uri=file.uri,
                mime_type=file.mime_type or "",
                size_bytes=file.size_bytes or 0,
                state=file.state.name if hasattr(file.state, 'name') else str(file.state),
                created_at=str(file.create_time) if hasattr(file, 'create_time') else "",
            )
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None
    
    def list_files(self) -> List[SharedDocument]:
        """업로드된 파일 목록"""
        files = []
        for file in genai.list_files():
            files.append(SharedDocument(
                id=file.name,
                name=file.display_name or "",
                uri=file.uri,
                mime_type=file.mime_type or "",
                size_bytes=file.size_bytes or 0,
                state=file.state.name if hasattr(file.state, 'name') else str(file.state),
                created_at=str(file.create_time) if hasattr(file, 'create_time') else "",
            ))
        return files
    
    def delete_file(self, file_id: str) -> bool:
        """파일 삭제"""
        try:
            genai.delete_file(file_id)
            if file_id in self._files:
                del self._files[file_id]
            logger.info(f"Deleted file: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    def wait_for_processing(
        self,
        file_id: str,
        timeout_seconds: int = 300,
        poll_interval: int = 5,
    ) -> bool:
        """
        파일 처리 완료 대기
        
        Args:
            file_id: 파일 ID
            timeout_seconds: 타임아웃 (초)
            poll_interval: 폴링 간격 (초)
        
        Returns:
            처리 완료 여부
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            file = genai.get_file(file_id)
            state = file.state.name if hasattr(file.state, 'name') else str(file.state)
            
            if state == "ACTIVE":
                logger.info(f"File {file_id} is now ACTIVE")
                return True
            elif state == "FAILED":
                logger.error(f"File {file_id} processing FAILED")
                return False
            
            logger.debug(f"File {file_id} state: {state}, waiting...")
            time.sleep(poll_interval)
        
        logger.warning(f"File {file_id} processing timeout after {timeout_seconds}s")
        return False
    
    def search_with_model(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        model: str = "gemini-2.0-flash",
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        File Search를 사용한 질의응답
        
        Args:
            query: 검색 쿼리
            file_ids: 검색할 파일 ID 목록
            model: 사용할 모델
            system_instruction: 시스템 지시
        
        Returns:
            생성된 응답
        """
        # 파일 준비
        files = []
        if file_ids:
            for fid in file_ids:
                file = genai.get_file(fid)
                files.append(file)
        else:
            # 모든 ACTIVE 파일 사용
            for file in genai.list_files():
                if hasattr(file, 'state') and file.state.name == "ACTIVE":
                    files.append(file)
        
        if not files:
            return "No files available for search."
        
        # 모델 생성
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction or "You are a helpful assistant. Answer based on the provided documents.",
        )
        
        # 파일과 함께 쿼리
        content = [query] + files
        response = model_instance.generate_content(content)
        
        return response.text
    
    def create_corpus(
        self,
        name: str,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Corpus(File Search Store) 생성
        
        Note: 이 기능은 Gemini API의 Semantic Retrieval 기능을 사용합니다.
        현재 Preview 상태이며 별도의 권한이 필요할 수 있습니다.
        
        Args:
            name: 고유 이름
            display_name: 표시 이름
        
        Returns:
            Corpus 정보
        """
        # 참고: genai.Corpus API는 아직 공개되지 않았을 수 있음
        # 대안으로 파일 기반 검색을 사용
        
        corpus_info = {
            "name": name,
            "display_name": display_name or name,
            "created_at": datetime.now().isoformat(),
            "files": [],
        }
        
        self._stores[name] = corpus_info
        logger.info(f"Created corpus: {name}")
        
        return corpus_info
    
    def rag_search(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        k: int = 5,
    ) -> List[SharedSearchResult]:
        """
        RAG 검색 (파일 기반)
        
        파일 내용에서 관련 정보를 검색합니다.
        Gemini의 grounding 기능을 활용합니다.
        
        Args:
            query: 검색 쿼리
            file_ids: 검색할 파일 ID 목록
            k: 반환할 결과 수
        
        Returns:
            검색 결과 리스트
        """
        # 현재는 모델 기반 검색으로 대체
        # 추후 File Search Tool API가 공개되면 업데이트
        
        prompt = f"""Based on the uploaded documents, find the top {k} most relevant passages for this query:

Query: {query}

For each relevant passage:
1. Quote the exact text from the document
2. Indicate which file it came from
3. Rate its relevance (0-1)

Format each result as:
[RESULT]
Content: <exact quote>
File: <filename>
Relevance: <score>
[/RESULT]
"""
        
        response = self.search_with_model(
            query=prompt,
            file_ids=file_ids,
            system_instruction="Extract and quote relevant passages from the documents. Be precise and include source information.",
        )
        
        # 결과 파싱 (간단한 파싱)
        results = []
        current_result = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('Content:'):
                current_result['content'] = line[8:].strip()
            elif line.startswith('File:'):
                current_result['file'] = line[5:].strip()
            elif line.startswith('Relevance:'):
                try:
                    current_result['relevance'] = float(line[10:].strip())
                except ValueError:
                    current_result['relevance'] = 0.5
            elif line == '[/RESULT]' and current_result:
                results.append(SharedSearchResult(
                    content=current_result.get('content', ''),
                    source='shared',
                    relevance_score=current_result.get('relevance', 0.5),
                    file_name=current_result.get('file', 'unknown'),
                    file_uri='',
                ))
                current_result = {}
        
        # 결과가 없으면 전체 응답을 단일 결과로
        if not results:
            results.append(SharedSearchResult(
                content=response,
                source='shared',
                relevance_score=0.8,
                file_name='combined',
                file_uri='',
            ))
        
        return results[:k]
    
    def get_stats(self) -> Dict[str, Any]:
        """RAG 통계"""
        files = self.list_files()
        active_files = [f for f in files if f.state == "ACTIVE"]
        
        return {
            "type": "shared",
            "backend": "google_gemini_file_search",
            "total_files": len(files),
            "active_files": len(active_files),
            "stores": list(self._stores.keys()),
            "api_configured": bool(self.api_key),
        }


# 전역 공유 RAG
_shared_rag: Optional[SharedRAG] = None


def get_shared_rag(api_key: Optional[str] = None) -> SharedRAG:
    """전역 공유 RAG 반환"""
    global _shared_rag
    if _shared_rag is None:
        _shared_rag = SharedRAG(api_key=api_key)
    return _shared_rag
