"""
HAES Configuration Module

환경 변수 및 설정 관리
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


def get_base_dir() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent.parent.parent


class Config(BaseSettings):
    """HAES 시스템 설정"""

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Paths - 우선순위: 내부 → 외부 → 환경변수
    # 내부 경로 (독립 실행용)
    skills_path: Path = Path("./data/skills")
    agents_path: Path = Path("./data/agents")
    persist_dir: Path = Path("./skill_vectordb")
    
    # 외부 경로 (개발용 폴백)
    _external_skills: Path = Path("../AI-research-SKILLs")
    _external_agents: Path = Path("../.claude/agents")

    # Models
    routing_model: str = "claude-3-5-haiku-latest"
    main_model: str = "claude-3-5-sonnet-latest"
    embedding_model: str = "text-embedding-3-small"


    # System Settings
    max_skills_per_query: int = 3
    enable_evolution: bool = True
    cache_enabled: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def resolve_paths(self) -> "Config":
        """
        경로 해결 (내부 → 외부 폴백)
        
        우선순위:
        1. 내부 경로 (./data/skills, ./data/agents)
        2. 외부 경로 (../AI-research-SKILLs, ../.claude/agents)
        3. 환경 변수
        """
        # Skills 경로 해결
        if not self.skills_path.exists():
            if self._external_skills.exists():
                self.skills_path = self._external_skills
        
        # Agents 경로 해결
        if not self.agents_path.exists():
            if self._external_agents.exists():
                self.agents_path = self._external_agents
        
        return self

    def validate_paths(self) -> bool:
        """경로 유효성 검사"""
        # 먼저 경로 해결 시도
        self.resolve_paths()
        
        if not self.skills_path.exists():
            raise ValueError(f"Skills path not found: {self.skills_path}")
        if not self.agents_path.exists():
            raise ValueError(f"Agents path not found: {self.agents_path}")
        return True

    def validate_api_keys(self) -> bool:
        """API 키 유효성 검사"""
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError("At least one API key is required (OpenAI or Anthropic)")
        return True
    
    def get_info(self) -> dict:
        """설정 정보 반환 (디버깅용)"""
        self.resolve_paths()
        return {
            "skills_path": str(self.skills_path.absolute()),
            "agents_path": str(self.agents_path.absolute()),
            "skills_exists": self.skills_path.exists(),
            "agents_exists": self.agents_path.exists(),
            "routing_model": self.routing_model,
            "main_model": self.main_model,
        }


def get_config() -> Config:
    """설정 인스턴스 반환 (경로 자동 해결)"""
    config = Config()
    config.resolve_paths()
    return config

