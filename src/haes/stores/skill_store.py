"""
SkillStore - SKILL 저장 및 검색

Vector DB를 사용한 SKILL.md 파일 인덱싱 및 검색
"""

import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from haes.models.skill import Skill


class SkillStore:
    """SKILL 저장소 - Vector DB 기반 검색 지원"""

    def __init__(
        self,
        skills_path: str,
        persist_dir: str = "./skill_vectordb",
        use_vector_db: bool = False,  # 기본은 로컬 검색, Vector DB는 선택적
    ):
        """
        SkillStore 초기화

        Args:
            skills_path: SKILL 파일들이 있는 디렉토리 경로
            persist_dir: Vector DB 저장 경로
            use_vector_db: Vector DB 사용 여부 (False면 키워드 기반 검색)
        """
        self.skills_path = Path(skills_path)
        self.persist_dir = Path(persist_dir)
        self.use_vector_db = use_vector_db

        # 캐시
        self.cache: Dict[str, str] = {}

        # 인덱싱된 SKILL 저장
        self.skills: Dict[str, Skill] = {}

        # 압축 인덱스
        self._compressed_index: Optional[str] = None

        # Vector DB 초기화 (선택적)
        self.collection = None
        if use_vector_db:
            self._init_vector_db()

        logger.info(f"SkillStore initialized: {self.skills_path}")

    def _init_vector_db(self) -> None:
        """Vector DB 초기화 (ChromaDB)"""
        try:
            import chromadb
            from chromadb.config import Settings

            self.persist_dir.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )

            self.collection = self.client.get_or_create_collection(
                name="skills",
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(f"Vector DB initialized at {self.persist_dir}")

        except ImportError:
            logger.warning("ChromaDB not installed. Using local search only.")
            self.use_vector_db = False

    def _parse_skill_file(self, file_path: Path) -> Skill:
        """
        SKILL.md 파일 파싱

        Args:
            file_path: SKILL.md 파일 경로

        Returns:
            Skill 객체
        """
        content = file_path.read_text(encoding="utf-8")

        # YAML frontmatter 추출
        yaml_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            body_content = yaml_match.group(2)

            try:
                metadata = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                logger.warning(f"YAML parse error in {file_path}: {e}")
                metadata = {}
        else:
            metadata = {}
            body_content = content

        # SKILL ID는 부모 폴더 이름
        skill_id = file_path.parent.name

        return Skill(
            skill_id=skill_id,
            name=metadata.get("name", skill_id),
            description=metadata.get("description", ""),
            tags=metadata.get("tags", []),
            content=content,  # 전체 내용 (YAML 포함)
            path=str(file_path),
            version=metadata.get("version", "1.0.0"),
            author=metadata.get("author", "Unknown"),
            dependencies=metadata.get("dependencies", []),
        )

    def index_all_skills(self) -> int:
        """
        모든 SKILL 인덱싱

        Returns:
            인덱싱된 SKILL 수
        """
        count = 0
        self.skills.clear()
        self._compressed_index = None

        # 모든 SKILL.md 파일 찾기
        for skill_file in self.skills_path.rglob("SKILL.md"):
            try:
                skill = self._parse_skill_file(skill_file)
                self.skills[skill.skill_id] = skill

                # Vector DB에 추가
                if self.use_vector_db and self.collection:
                    self.collection.upsert(
                        ids=[skill.skill_id],
                        documents=[skill.description + " " + " ".join(skill.tags)],
                        metadatas=[{"path": skill.path, "name": skill.name}],
                    )

                count += 1
                logger.debug(f"Indexed skill: {skill.skill_id}")

            except Exception as e:
                logger.error(f"Error indexing {skill_file}: {e}")

        logger.info(f"Indexed {count} skills")
        return count

    def search(self, query: str, k: int = 3) -> List[Skill]:
        """
        SKILL 검색

        Args:
            query: 검색 쿼리
            k: 반환할 최대 결과 수

        Returns:
            관련 SKILL 목록
        """
        if self.use_vector_db and self.collection:
            return self._search_vector(query, k)
        else:
            return self._search_keyword(query, k)

    def _search_vector(self, query: str, k: int) -> List[Skill]:
        """Vector DB 기반 검색"""
        if not self.collection:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(k, len(self.skills)),
        )

        skills = []
        if results and results["ids"] and results["ids"][0]:
            for skill_id in results["ids"][0]:
                if skill_id in self.skills:
                    skills.append(self.skills[skill_id])

        return skills

    def _search_keyword(self, query: str, k: int) -> List[Skill]:
        """키워드 기반 검색 (Vector DB 없이)"""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_skills = []

        for skill_id, skill in self.skills.items():
            score = 0

            # SKILL ID 매칭
            if query_lower in skill_id.lower():
                score += 10

            # 이름 매칭
            if query_lower in skill.name.lower():
                score += 8

            # 태그 매칭
            for tag in skill.tags:
                tag_lower = tag.lower()
                if tag_lower in query_lower or query_lower in tag_lower:
                    score += 5
                for word in query_words:
                    if word in tag_lower:
                        score += 2

            # 설명 매칭
            desc_lower = skill.description.lower()
            for word in query_words:
                if word in desc_lower:
                    score += 1

            if score > 0:
                scored_skills.append((score, skill))

        # 점수순 정렬
        scored_skills.sort(key=lambda x: x[0], reverse=True)

        return [skill for _, skill in scored_skills[:k]]

    def load(self, skill_ids: List[str]) -> str:
        """
        SKILL 내용 로드 (캐싱 적용)

        Args:
            skill_ids: 로드할 SKILL ID 목록

        Returns:
            SKILL 내용 (여러 개면 구분자로 연결)
        """
        contents = []

        for skill_id in skill_ids:
            # 캐시 확인
            if skill_id in self.cache:
                contents.append(self.cache[skill_id])
                continue

            # 인덱스에서 가져오기
            if skill_id in self.skills:
                content = self.skills[skill_id].content
                self.cache[skill_id] = content
                contents.append(content)
            else:
                logger.warning(f"Skill not found: {skill_id}")

        return "\n\n---\n\n".join(contents)

    def get_by_id(self, skill_id: str) -> Optional[Skill]:
        """
        ID로 SKILL 조회

        Args:
            skill_id: SKILL ID

        Returns:
            Skill 객체 또는 None
        """
        return self.skills.get(skill_id)

    def list_all(self) -> List[Skill]:
        """
        모든 SKILL 목록 반환

        Returns:
            전체 SKILL 목록
        """
        return list(self.skills.values())

    def get_compressed_index(self) -> str:
        """
        라우팅용 압축 인덱스 반환

        Format: ID|키워드|설명

        Returns:
            압축된 인덱스 문자열 (~2000 토큰)
        """
        if self._compressed_index:
            return self._compressed_index

        lines = ["ID|키워드|설명"]

        for skill_id, skill in self.skills.items():
            # 태그 최대 5개
            tags_str = ",".join(skill.tags[:5])
            # 설명 최대 100자
            desc_short = skill.description[:100].replace("|", " ")

            line = f"{skill_id}|{tags_str}|{desc_short}"
            lines.append(line)

        self._compressed_index = "\n".join(lines)
        return self._compressed_index

    def clear_cache(self) -> None:
        """캐시 클리어"""
        self.cache.clear()
        self._compressed_index = None
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """저장소 통계 반환"""
        return {
            "total_skills": len(self.skills),
            "cached_skills": len(self.cache),
            "use_vector_db": self.use_vector_db,
            "skills_path": str(self.skills_path),
        }
