"""
SkillStore Unit Tests

TDD: RED Phase - Write tests first
"""

import pytest
from pathlib import Path
from typing import List

from haes.models.skill import Skill


class TestSkillStore:
    """SkillStore 단위 테스트"""

    def test_init_creates_cache(self, tmp_path: Path):
        """초기화 시 캐시가 생성되어야 함"""
        from haes.stores.skill_store import SkillStore

        skills_path = tmp_path / "skills"
        skills_path.mkdir()

        store = SkillStore(
            skills_path=str(skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )

        assert store.cache == {}
        assert store.skills_path == skills_path

    def test_parse_skill_file_extracts_metadata(self, sample_skills_path: Path):
        """SKILL 파일에서 메타데이터를 올바르게 추출해야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(sample_skills_path.parent / "vectordb"),
        )

        # sample-fine-tuning 폴더의 SKILL.md 파싱
        skill_file = sample_skills_path / "sample-fine-tuning" / "SKILL.md"
        skill = store._parse_skill_file(skill_file)

        assert skill.name == "sample-fine-tuning"
        assert "Fine-Tuning" in skill.tags
        assert "LoRA" in skill.tags
        assert skill.version == "1.0.0"
        assert skill.author == "Test Author"

    def test_parse_skill_file_extracts_content(self, sample_skills_path: Path):
        """SKILL 파일 전체 내용을 가져와야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(sample_skills_path.parent / "vectordb"),
        )

        skill_file = sample_skills_path / "sample-fine-tuning" / "SKILL.md"
        skill = store._parse_skill_file(skill_file)

        assert "Quick Start" in skill.content
        assert "LoRA Fine-tuning" in skill.content

    def test_index_all_skills_returns_count(self, sample_skills_path: Path, tmp_path: Path):
        """모든 SKILL 인덱싱 후 개수를 반환해야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )

        count = store.index_all_skills()

        # 3개의 샘플 SKILL이 있음
        assert count == 3

    def test_load_returns_skill_content(self, sample_skills_path: Path, tmp_path: Path):
        """SKILL ID로 내용을 로드해야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        content = store.load(["sample-fine-tuning"])

        assert "LoRA" in content or "Fine-Tuning" in content

    def test_load_multiple_skills_concatenates(self, sample_skills_path: Path, tmp_path: Path):
        """여러 SKILL 로드 시 내용이 연결되어야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        content = store.load(["sample-fine-tuning", "sample-rag"])

        assert "LoRA" in content or "Fine-Tuning" in content
        assert "RAG" in content or "Vector" in content

    def test_load_uses_cache(self, sample_skills_path: Path, tmp_path: Path):
        """두 번째 로드는 캐시를 사용해야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        # 첫 번째 로드
        store.load(["sample-fine-tuning"])
        assert "sample-fine-tuning" in store.cache

        # 두 번째 로드 - 캐시 사용 확인
        cached_content = store.cache["sample-fine-tuning"]
        content = store.load(["sample-fine-tuning"])
        assert content == cached_content

    def test_get_compressed_index_returns_string(self, sample_skills_path: Path, tmp_path: Path):
        """압축 인덱스가 문자열로 반환되어야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        index = store.get_compressed_index()

        assert isinstance(index, str)
        assert "sample-fine-tuning" in index
        assert "sample-rag" in index

    def test_get_compressed_index_format(self, sample_skills_path: Path, tmp_path: Path):
        """압축 인덱스가 올바른 형식이어야 함 (ID|키워드|설명)"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        index = store.get_compressed_index()
        lines = index.strip().split("\n")

        # 헤더 확인
        assert "ID" in lines[0]
        # 데이터 라인 확인
        assert len(lines) >= 4  # 헤더 + 3개 SKILL

    def test_search_returns_relevant_skills(self, sample_skills_path: Path, tmp_path: Path):
        """검색어에 관련된 SKILL이 반환되어야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        results = store.search("fine-tuning LoRA", k=3)

        assert len(results) > 0
        # fine-tuning 관련 SKILL이 상위에 있어야 함
        skill_ids = [r.skill_id for r in results]
        assert "sample-fine-tuning" in skill_ids

    def test_search_respects_k_limit(self, sample_skills_path: Path, tmp_path: Path):
        """검색 결과가 k개로 제한되어야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        results = store.search("test query", k=2)

        assert len(results) <= 2

    def test_get_skill_by_id(self, sample_skills_path: Path, tmp_path: Path):
        """ID로 특정 SKILL을 가져와야 함"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        skill = store.get_by_id("sample-fine-tuning")

        assert skill is not None
        assert skill.skill_id == "sample-fine-tuning"

    def test_get_skill_by_id_returns_none_for_unknown(
        self, sample_skills_path: Path, tmp_path: Path
    ):
        """없는 SKILL은 None 반환"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        skill = store.get_by_id("nonexistent-skill")

        assert skill is None

    def test_list_all_skills(self, sample_skills_path: Path, tmp_path: Path):
        """모든 SKILL 목록 반환"""
        from haes.stores.skill_store import SkillStore

        store = SkillStore(
            skills_path=str(sample_skills_path),
            persist_dir=str(tmp_path / "vectordb"),
        )
        store.index_all_skills()

        skills = store.list_all()

        assert len(skills) == 3
        skill_ids = [s.skill_id for s in skills]
        assert "sample-fine-tuning" in skill_ids
        assert "sample-rag" in skill_ids
        assert "sample-inference" in skill_ids
