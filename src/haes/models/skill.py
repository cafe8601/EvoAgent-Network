"""
Skill Data Model

AI Research SKILL을 표현하는 데이터 모델
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Skill:
    """AI Research SKILL 표현"""

    skill_id: str
    """SKILL 고유 식별자 (예: "03-fine-tuning")"""

    name: str
    """SKILL 이름 (예: "axolotl-fine-tuning")"""

    description: str
    """SKILL 설명 (YAML frontmatter에서 추출)"""

    tags: List[str]
    """검색용 태그 목록"""

    content: str
    """SKILL.md 전체 내용"""

    path: str
    """파일 시스템 경로"""

    version: str = "1.0.0"
    """SKILL 버전"""

    author: str = "Unknown"
    """작성자"""

    dependencies: List[str] = field(default_factory=list)
    """의존성 목록"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "content": self.content,
            "path": self.path,
            "version": self.version,
            "author": self.author,
            "dependencies": self.dependencies,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        """딕셔너리에서 생성"""
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            description=data["description"],
            tags=data.get("tags", []),
            content=data["content"],
            path=data["path"],
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            dependencies=data.get("dependencies", []),
        )

    def get_summary(self, max_length: int = 200) -> str:
        """SKILL 요약 반환"""
        summary = f"{self.skill_id}|{','.join(self.tags[:5])}|{self.description[:max_length]}"
        return summary
