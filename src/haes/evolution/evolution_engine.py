"""
EvolutionEngine - 피드백 기반 학습 및 진화

사용자 피드백을 수집하고 라우팅 패턴을 학습
영속성 지원: JSON/YAML 파일로 패턴 저장 및 로드
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from loguru import logger

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from haes.models.execution import ExecutionResult
from haes.models.feedback import Feedback, LearnedPattern


class EvolutionEngine:
    """
    진화 엔진 - 피드백 기반 학습
    
    - 피드백 수집 및 저장
    - 라우팅 통계 업데이트
    - 성공 패턴 학습
    - 라우팅 힌트 제공
    """

    # 학습 임계값
    LEARNING_THRESHOLD = 5  # 최소 5회 성공 필요
    SUCCESS_SCORE = 4  # 4점 이상이 성공
    HIGH_CONFIDENCE = 0.8  # 높은 신뢰도

    # 기본 파일 경로
    DEFAULT_PERSIST_DIR = "./evolution_data"

    def __init__(self, persist_dir: Optional[str] = None, auto_load: bool = True):
        """
        EvolutionEngine 초기화

        Args:
            persist_dir: 데이터 저장 디렉토리 경로
            auto_load: 초기화 시 자동으로 저장된 데이터 로드 여부
        """
        # 영속성 경로 설정
        self.persist_dir = Path(persist_dir) if persist_dir else Path(self.DEFAULT_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 피드백 데이터베이스
        self.feedback_db: List[Dict[str, Any]] = []

        # SKILL별 라우팅 통계
        self.routing_stats: Dict[str, Dict[str, Any]] = {}

        # 학습된 패턴
        self.learned_patterns: List[Dict[str, Any]] = []

        # 쿼리 패턴 캐시 (유사도 매칭용)
        self._query_patterns: Dict[str, List[str]] = {}

        # 자동 저장 플래그
        self._auto_save = True
        self._dirty = False  # 변경 추적

        # 자동 로드
        if auto_load:
            self.load()

        logger.info(f"EvolutionEngine initialized (persist_dir={self.persist_dir})")

    def record_feedback(
        self,
        result: ExecutionResult,
        feedback: str,
        score: int,
    ) -> Optional[Dict[str, Any]]:
        """
        피드백 기록 및 학습 트리거

        Args:
            result: 실행 결과
            feedback: 피드백 텍스트
            score: 평가 점수 (1-5)

        Returns:
            개선 제안 (낮은 점수 시) 또는 None
        """
        # 피드백 기록
        record = {
            "timestamp": datetime.now().isoformat(),
            "query": result.query,
            "mode": result.mode,
            "skills_used": result.skills_used,
            "agents_used": result.agents_used,
            "feedback": feedback,
            "score": score,
        }
        self.feedback_db.append(record)

        # 라우팅 통계 업데이트
        self._update_routing_stats(record)

        # 성공 패턴 학습
        if score >= self.SUCCESS_SCORE:
            self._learn_success_pattern(record)

        # 낮은 점수 시 개선 제안
        if score <= 2:
            return self._trigger_improvement(record)

        logger.debug(f"Feedback recorded: score={score}, skills={result.skills_used}")

        # 변경 사항 추적 및 자동 저장
        self._dirty = True
        if self._auto_save:
            self.save()

        return None

    def _update_routing_stats(self, record: Dict[str, Any]) -> None:
        """라우팅 통계 업데이트"""
        is_success = record["score"] >= self.SUCCESS_SCORE

        for skill_id in record["skills_used"]:
            if skill_id not in self.routing_stats:
                self.routing_stats[skill_id] = {
                    "total": 0,
                    "success": 0,
                    "scores": [],
                    "modes": {},
                }

            stats = self.routing_stats[skill_id]
            stats["total"] += 1
            stats["scores"].append(record["score"])

            if is_success:
                stats["success"] += 1

            # 모드별 카운트
            mode = record["mode"]
            stats["modes"][mode] = stats["modes"].get(mode, 0) + 1

    def _learn_success_pattern(self, record: Dict[str, Any]) -> None:
        """성공 패턴 학습"""
        query = record["query"]
        skills = record["skills_used"]
        mode = record["mode"]

        # 쿼리 정규화 (키워드 추출)
        query_keywords = self._extract_keywords(query)
        pattern_key = "|".join(sorted(skills))

        # 기존 패턴 검색
        existing_pattern = None
        for pattern in self.learned_patterns:
            if pattern["pattern_key"] == pattern_key:
                existing_pattern = pattern
                break

        if existing_pattern:
            # 기존 패턴 업데이트
            existing_pattern["sample_count"] += 1
            existing_pattern["query_keywords"].update(query_keywords)
            existing_pattern["success_scores"].append(record["score"])
        else:
            # 새 패턴 후보
            if pattern_key not in self._query_patterns:
                self._query_patterns[pattern_key] = []

            self._query_patterns[pattern_key].append({
                "query": query,
                "keywords": query_keywords,
                "score": record["score"],
                "mode": mode,
                "agents": record["agents_used"],
            })

            # 임계값 도달 시 패턴 학습
            if len(self._query_patterns[pattern_key]) >= self.LEARNING_THRESHOLD:
                self._create_learned_pattern(pattern_key, skills, mode)

    def _create_learned_pattern(
        self,
        pattern_key: str,
        skills: List[str],
        mode: str,
    ) -> None:
        """학습된 패턴 생성"""
        samples = self._query_patterns[pattern_key]

        # 키워드 통합
        all_keywords = set()
        all_scores = []
        agents = []

        for sample in samples:
            all_keywords.update(sample["keywords"])
            all_scores.append(sample["score"])
            if sample["agents"]:
                agents.extend(sample["agents"])

        # 성공률 계산
        success_count = sum(1 for s in all_scores if s >= self.SUCCESS_SCORE)
        success_rate = success_count / len(all_scores)

        if success_rate >= 0.8:  # 80% 이상 성공률만 학습
            pattern = {
                "pattern_key": pattern_key,
                "skills": skills,
                "mode": mode,
                "agents": list(set(agents)),
                "query_keywords": all_keywords,
                "sample_count": len(samples),
                "success_rate": success_rate,
                "success_scores": all_scores,
                "learned_at": datetime.now().isoformat(),
            }
            self.learned_patterns.append(pattern)
            logger.info(f"Learned pattern: {pattern_key}, success_rate={success_rate:.2f}")

    def _trigger_improvement(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """낮은 점수 시 개선 트리거"""
        return {
            "action": "review",
            "needs_review": True,
            "query": record["query"],
            "skills_used": record["skills_used"],
            "score": record["score"],
            "suggestion": "Consider reviewing SKILL content or routing logic",
        }

    def _extract_keywords(self, query: str) -> set:
        """쿼리에서 키워드 추출"""
        # 간단한 키워드 추출 (단어 분리)
        words = re.findall(r'\w+', query.lower())
        # 불용어 제거
        stopwords = {"을", "를", "이", "가", "은", "는", "에", "의", "로", "해", "해줘", "알려줘", "방법", "뭐"}
        keywords = {w for w in words if len(w) > 1 and w not in stopwords}
        return keywords

    def get_routing_hints(self, query: str) -> Dict[str, Any]:
        """
        쿼리에 대한 라우팅 힌트 반환

        Args:
            query: 사용자 쿼리

        Returns:
            힌트 딕셔너리 (confidence, suggested_skills, suggested_mode)
        """
        if not self.learned_patterns:
            return {
                "confidence": 0.0,
                "suggested_skills": [],
                "suggested_mode": None,
                "suggested_agents": [],
            }

        query_keywords = self._extract_keywords(query)

        best_match = None
        best_score = 0.0

        for pattern in self.learned_patterns:
            # 키워드 유사도 계산
            pattern_keywords = pattern["query_keywords"]
            if not pattern_keywords:
                continue

            common = query_keywords & pattern_keywords
            if not common:
                continue

            # Jaccard 유사도
            similarity = len(common) / len(query_keywords | pattern_keywords)

            # 성공률 가중치
            weighted_score = similarity * pattern["success_rate"]

            if weighted_score > best_score:
                best_score = weighted_score
                best_match = pattern

        if best_match and best_score > 0.3:
            confidence = min(best_score * 1.5, 0.95)  # 스케일 조정
            return {
                "confidence": confidence,
                "suggested_skills": best_match["skills"],
                "suggested_mode": best_match["mode"],
                "suggested_agents": best_match.get("agents", []),
                "matched_pattern": best_match["pattern_key"],
            }

        return {
            "confidence": 0.0,
            "suggested_skills": [],
            "suggested_mode": None,
            "suggested_agents": [],
        }

    def get_skill_performance(self, skill_id: str) -> Dict[str, Any]:
        """
        SKILL별 성능 조회

        Args:
            skill_id: SKILL ID

        Returns:
            성능 통계
        """
        if skill_id not in self.routing_stats:
            return {
                "total": 0,
                "success": 0,
                "average_score": 0.0,
                "success_rate": 0.0,
            }

        stats = self.routing_stats[skill_id]
        total = stats["total"]
        scores = stats["scores"]

        return {
            "total": total,
            "success": stats["success"],
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "success_rate": stats["success"] / total if total > 0 else 0.0,
            "modes": stats["modes"],
        }

    def get_stats(self) -> Dict[str, Any]:
        """전체 통계 조회"""
        total = len(self.feedback_db)
        positive = sum(1 for f in self.feedback_db if f["score"] >= self.SUCCESS_SCORE)
        negative = sum(1 for f in self.feedback_db if f["score"] <= 2)

        return {
            "total_feedbacks": total,
            "positive_feedbacks": positive,
            "negative_feedbacks": negative,
            "average_score": (
                sum(f["score"] for f in self.feedback_db) / total
                if total > 0 else 0.0
            ),
            "learned_patterns_count": len(self.learned_patterns),
            "skills_tracked": len(self.routing_stats),
        }

    def clear(self) -> None:
        """모든 데이터 클리어"""
        self.feedback_db.clear()
        self.routing_stats.clear()
        self.learned_patterns.clear()
        self._query_patterns.clear()
        logger.info("EvolutionEngine data cleared")

    def get_top_performing_skills(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        상위 성능 SKILL 반환

        Args:
            n: 반환할 개수

        Returns:
            상위 SKILL 목록
        """
        performances = []
        for skill_id, stats in self.routing_stats.items():
            if stats["total"] >= 3:  # 최소 3회 이상
                performances.append({
                    "skill_id": skill_id,
                    "success_rate": stats["success"] / stats["total"],
                    "total": stats["total"],
                })

        performances.sort(key=lambda x: x["success_rate"], reverse=True)
        return performances[:n]

    def export_patterns(self) -> List[Dict[str, Any]]:
        """학습된 패턴 내보내기"""
        return [
            {
                "skills": p["skills"],
                "mode": p["mode"],
                "keywords": list(p["query_keywords"]),
                "success_rate": p["success_rate"],
                "sample_count": p["sample_count"],
            }
            for p in self.learned_patterns
        ]

    # =========================================================================
    # 영속성 메서드 (Persistence Methods)
    # =========================================================================

    def save(self, filepath: Optional[Union[str, Path]] = None) -> bool:
        """
        학습된 데이터를 파일에 저장

        Args:
            filepath: 저장 파일 경로 (None이면 기본 경로 사용)

        Returns:
            저장 성공 여부
        """
        if filepath:
            save_path = Path(filepath)
        else:
            save_path = self.persist_dir / "evolution_state.json"

        try:
            # 저장할 데이터 구성
            data = self._serialize_state()

            # 파일 형식 결정 (확장자 기반)
            if save_path.suffix.lower() in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    logger.warning("YAML not available, falling back to JSON")
                    save_path = save_path.with_suffix(".json")
                    self._save_json(save_path, data)
                else:
                    self._save_yaml(save_path, data)
            else:
                self._save_json(save_path, data)

            self._dirty = False
            logger.info(f"EvolutionEngine state saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save evolution state: {e}")
            return False

    def load(self, filepath: Optional[Union[str, Path]] = None) -> bool:
        """
        저장된 데이터를 파일에서 로드

        Args:
            filepath: 로드할 파일 경로 (None이면 기본 경로 사용)

        Returns:
            로드 성공 여부
        """
        if filepath:
            load_path = Path(filepath)
        else:
            # 기본 경로에서 JSON 또는 YAML 파일 찾기
            json_path = self.persist_dir / "evolution_state.json"
            yaml_path = self.persist_dir / "evolution_state.yaml"

            if json_path.exists():
                load_path = json_path
            elif yaml_path.exists():
                load_path = yaml_path
            else:
                logger.debug("No existing evolution state file found")
                return False

        if not load_path.exists():
            logger.debug(f"Evolution state file not found: {load_path}")
            return False

        try:
            # 파일 형식에 따라 로드
            if load_path.suffix.lower() in [".yaml", ".yml"]:
                data = self._load_yaml(load_path)
            else:
                data = self._load_json(load_path)

            # 상태 복원
            self._deserialize_state(data)

            logger.info(f"EvolutionEngine state loaded from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load evolution state: {e}")
            return False

    def _serialize_state(self) -> Dict[str, Any]:
        """현재 상태를 직렬화 가능한 딕셔너리로 변환"""
        # learned_patterns의 set을 list로 변환
        serialized_patterns = []
        for pattern in self.learned_patterns:
            p = pattern.copy()
            if "query_keywords" in p and isinstance(p["query_keywords"], set):
                p["query_keywords"] = list(p["query_keywords"])
            if "success_scores" in p:
                p["success_scores"] = list(p["success_scores"])
            serialized_patterns.append(p)

        # query_patterns의 set을 list로 변환
        serialized_query_patterns = {}
        for key, samples in self._query_patterns.items():
            serialized_samples = []
            for sample in samples:
                s = sample.copy()
                if "keywords" in s and isinstance(s["keywords"], set):
                    s["keywords"] = list(s["keywords"])
                serialized_samples.append(s)
            serialized_query_patterns[key] = serialized_samples

        return {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "feedback_db": self.feedback_db,
            "routing_stats": self.routing_stats,
            "learned_patterns": serialized_patterns,
            "query_patterns": serialized_query_patterns,
            "stats": {
                "total_feedbacks": len(self.feedback_db),
                "learned_patterns_count": len(self.learned_patterns),
                "skills_tracked": len(self.routing_stats),
            },
        }

    def _deserialize_state(self, data: Dict[str, Any]) -> None:
        """직렬화된 데이터에서 상태 복원"""
        # 버전 확인
        version = data.get("version", "1.0")
        if version != "1.0":
            logger.warning(f"Loading data from different version: {version}")

        # 피드백 DB 복원
        self.feedback_db = data.get("feedback_db", [])

        # 라우팅 통계 복원
        self.routing_stats = data.get("routing_stats", {})

        # 학습된 패턴 복원 (list를 set으로 변환)
        self.learned_patterns = []
        for pattern in data.get("learned_patterns", []):
            p = pattern.copy()
            if "query_keywords" in p and isinstance(p["query_keywords"], list):
                p["query_keywords"] = set(p["query_keywords"])
            self.learned_patterns.append(p)

        # 쿼리 패턴 캐시 복원
        self._query_patterns = {}
        for key, samples in data.get("query_patterns", {}).items():
            self._query_patterns[key] = []
            for sample in samples:
                s = sample.copy()
                if "keywords" in s and isinstance(s["keywords"], list):
                    s["keywords"] = set(s["keywords"])
                self._query_patterns[key].append(s)

        self._dirty = False

    def _save_json(self, filepath: Path, data: Dict[str, Any]) -> None:
        """JSON 형식으로 저장"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """JSON 파일에서 로드"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_yaml(self, filepath: Path, data: Dict[str, Any]) -> None:
        """YAML 형식으로 저장"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support")
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """YAML 파일에서 로드"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support")
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def set_auto_save(self, enabled: bool) -> None:
        """
        자동 저장 기능 활성화/비활성화

        Args:
            enabled: 활성화 여부
        """
        self._auto_save = enabled
        logger.debug(f"Auto-save {'enabled' if enabled else 'disabled'}")

    def is_dirty(self) -> bool:
        """저장되지 않은 변경 사항 존재 여부"""
        return self._dirty

    def backup(self, backup_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """
        현재 상태를 타임스탬프 포함 백업 파일로 저장

        Args:
            backup_dir: 백업 디렉토리 (None이면 기본 경로/backups 사용)

        Returns:
            백업 파일 경로 또는 실패 시 None
        """
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = self.persist_dir / "backups"

        backup_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"evolution_state_{timestamp}.json"

        if self.save(backup_file):
            logger.info(f"Backup created: {backup_file}")
            return backup_file
        return None

    def restore_from_backup(self, backup_file: Union[str, Path]) -> bool:
        """
        백업 파일에서 상태 복원

        Args:
            backup_file: 백업 파일 경로

        Returns:
            복원 성공 여부
        """
        return self.load(backup_file)
