"""
AgentPool - 에이전트 풀 관리

다중 Tier 구조의 에이전트 로드 및 관리
"""

import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from haes.models.agent import Agent


class AgentPool:
    """에이전트 풀 - 159개 전문 에이전트 관리"""

    # 지원하는 Tier
    TIERS = ["tier1-core", "tier2-specialized", "tier3-experimental"]

    def __init__(self, agents_path: str):
        """
        AgentPool 초기화

        Args:
            agents_path: 에이전트 파일들이 있는 디렉토리 경로
        """
        self.agents_path = Path(agents_path)
        self.agents: Dict[str, Agent] = {}

        logger.info(f"AgentPool initialized: {self.agents_path}")

    def load_all_agents(self) -> int:
        """
        모든 에이전트 로드

        Returns:
            로드된 에이전트 수
        """
        count = 0
        self.agents.clear()

        # 각 Tier 디렉토리에서 로드
        for tier in self.TIERS:
            tier_path = self.agents_path / tier
            if tier_path.exists():
                count += self._load_from_tier(tier_path, tier)

        # 루트 디렉토리의 에이전트도 로드 (있다면)
        count += self._load_from_tier(self.agents_path, "root")

        logger.info(f"Loaded {count} agents")
        return count

    def _load_from_tier(self, tier_path: Path, tier_name: str) -> int:
        """
        특정 Tier에서 에이전트 로드

        Args:
            tier_path: Tier 디렉토리 경로
            tier_name: Tier 이름

        Returns:
            로드된 에이전트 수
        """
        count = 0

        # .md 파일 찾기 (하위 디렉토리 포함)
        for agent_file in tier_path.rglob("*.md"):
            # 대문자로 시작하는 파일 제외 (README.md 등)
            if agent_file.name[0].isupper():
                continue

            # 상위 폴더가 tier인지 확인
            relative_path = agent_file.relative_to(tier_path)
            if len(relative_path.parts) > 1:
                # 하위 디렉토리의 파일
                actual_tier = f"{tier_name}/{relative_path.parts[0]}"
            else:
                actual_tier = tier_name

            try:
                agent = self._parse_agent_file(agent_file, actual_tier)
                self.agents[agent.agent_id] = agent
                count += 1
                logger.debug(f"Loaded agent: {agent.agent_id} ({actual_tier})")

            except Exception as e:
                logger.error(f"Error loading {agent_file}: {e}")

        return count

    def _parse_agent_file(self, file_path: Path, tier: str) -> Agent:
        """
        에이전트 파일 파싱

        Args:
            file_path: 에이전트 .md 파일 경로
            tier: Tier 이름

        Returns:
            Agent 객체
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

        # 에이전트 ID는 파일 이름 (확장자 제외)
        agent_id = file_path.stem

        # tools 파싱
        tools = []
        if "tools" in metadata:
            if isinstance(metadata["tools"], dict):
                # native, mcp_optional 등
                for tool_type, tool_list in metadata["tools"].items():
                    if isinstance(tool_list, list):
                        tools.extend(tool_list)
            elif isinstance(metadata["tools"], list):
                tools = metadata["tools"]

        # tier 결정 (메타데이터 우선)
        resolved_tier = tier
        if "tier" in metadata:
            tier_value = metadata["tier"]
            if isinstance(tier_value, int):
                resolved_tier = f"tier{tier_value}-core" if tier_value == 1 else f"tier{tier_value}-specialized"

        return Agent(
            agent_id=agent_id,
            tier=resolved_tier,
            name=metadata.get("name", agent_id),
            description=metadata.get("description", ""),
            system_prompt=body_content.strip(),
            version=str(metadata.get("version", "1.0")),
            standalone=metadata.get("standalone", True),
            tools=tools,
        )

    def get(self, agent_id: str) -> Optional[Agent]:
        """
        ID로 에이전트 조회

        Args:
            agent_id: 에이전트 ID

        Returns:
            Agent 객체 또는 None
        """
        return self.agents.get(agent_id)

    def list_all(self) -> List[Agent]:
        """
        모든 에이전트 목록 반환

        Returns:
            전체 에이전트 목록
        """
        return list(self.agents.values())

    def list_by_tier(self, tier: str) -> List[Agent]:
        """
        Tier별 에이전트 목록 반환

        Args:
            tier: Tier 이름 (예: "tier1-core")

        Returns:
            해당 Tier의 에이전트 목록
        """
        return [
            agent for agent in self.agents.values()
            if agent.tier == tier or agent.tier.startswith(tier)
        ]

    def get_count(self) -> int:
        """
        전체 에이전트 수 반환

        Returns:
            에이전트 총 개수
        """
        return len(self.agents)

    def select_for_task(self, task_description: str) -> Optional[str]:
        """
        작업에 적합한 에이전트 선택

        Args:
            task_description: 작업 설명

        Returns:
            선택된 에이전트 ID 또는 None
        """
        task_lower = task_description.lower()

        # 키워드 기반 매칭
        keyword_map = {
            "backend": ["backend", "api", "server", "database"],
            "frontend": ["frontend", "ui", "react", "vue", "css"],
            "qa": ["test", "quality", "qa", "testing"],
            "security": ["security", "auth", "vulnerability"],
            "devops": ["devops", "deploy", "ci/cd", "docker", "kubernetes"],
            "data": ["data", "ml", "ai", "machine learning"],
        }

        best_match = None
        best_score = 0

        for agent in self.agents.values():
            score = 0

            # 에이전트 설명 + 이름과 매칭
            agent_text = f"{agent.name} {agent.description} {agent.system_prompt}".lower()

            for _, keywords in keyword_map.items():
                task_matches = sum(1 for kw in keywords if kw in task_lower)
                agent_matches = sum(1 for kw in keywords if kw in agent_text)

                if task_matches > 0 and agent_matches > 0:
                    score += task_matches * agent_matches

            # Tier 1 가점
            if agent.tier == "tier1-core":
                score += 2

            if score > best_score:
                best_score = score
                best_match = agent.agent_id

        return best_match

    def get_stats(self) -> Dict[str, Any]:
        """저장소 통계 반환"""
        tier_counts = {}
        for agent in self.agents.values():
            tier_counts[agent.tier] = tier_counts.get(agent.tier, 0) + 1

        return {
            "total_agents": len(self.agents),
            "by_tier": tier_counts,
            "agents_path": str(self.agents_path),
        }
