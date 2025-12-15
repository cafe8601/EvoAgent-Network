"""
KeywordMatcher - 키워드 기반 SKILL 매칭

빠른 키워드 기반 SKILL 매칭 (Vector DB 없이)
"""

import re
from typing import List, Tuple, Dict
from loguru import logger


class KeywordMatcher:
    """키워드 기반 SKILL 매칭기"""

    # SKILL-키워드 매핑 (전체 63+ SKILLs)
    KEYWORD_MAP: Dict[str, List[str]] = {
        # Model Architecture
        "01-model-architecture": [
            "transformer", "llama", "mamba", "ssm", "attention", "architecture",
            "모델", "아키텍처", "트랜스포머"
        ],
        
        # Tokenization
        "02-tokenization": [
            "tokenizer", "bpe", "sentencepiece", "vocabulary", "토크나이저", "토큰"
        ],
        
        # Fine-tuning
        "03-fine-tuning": [
            "fine-tuning", "finetune", "lora", "qlora", "peft", "axolotl",
            "adapter", "instruction", "sft", "파인튜닝", "미세조정", "학습"
        ],
        
        # Data Processing
        "05-data-processing": [
            "data", "dataset", "dedup", "filtering", "ray", "preprocessing",
            "데이터", "전처리", "정제"
        ],
        
        # Post-training
        "06-post-training": [
            "dpo", "rlhf", "grpo", "ppo", "rloo", "preference", "reward",
            "포스트트레이닝", "강화학습", "선호도"
        ],
        
        # Safety & Alignment
        "07-safety-alignment": [
            "guardrails", "redteaming", "safety", "alignment", "jailbreak",
            "안전", "정렬", "가드레일"
        ],
        
        # Distributed Training
        "08-distributed-training": [
            "deepspeed", "fsdp", "ddp", "distributed", "multi-gpu", "multi-node",
            "분산학습", "분산", "멀티gpu"
        ],
        
        # Optimization
        "10-optimization": [
            "quantization", "pruning", "distillation", "compression", "4bit", "8bit",
            "양자화", "최적화", "경량화"
        ],
        
        # Evaluation
        "11-evaluation": [
            "lm-eval", "benchmark", "evaluation", "metrics", "harness",
            "평가", "벤치마크", "성능측정"
        ],
        
        # Inference & Serving
        "12-inference-serving": [
            "vllm", "tgi", "triton", "inference", "serving", "deploy",
            "추론", "서빙", "배포", "deployment"
        ],
        
        # MLOps
        "13-mlops": [
            "wandb", "mlflow", "experiment", "tracking", "logging",
            "mlops", "실험관리"
        ],
        
        # Agents
        "14-agents": [
            "agent", "langchain", "crewai", "autogen", "tool", "function",
            "에이전트", "도구"
        ],
        
        # RAG
        "15-rag": [
            "rag", "retrieval", "vector", "embedding", "chroma", "faiss", "pinecone",
            "검색", "벡터", "임베딩", "지식베이스"
        ],
        
        # Prompt Engineering
        "16-prompt-engineering": [
            "prompt", "dspy", "instructor", "structured", "few-shot",
            "프롬프트", "엔지니어링"
        ],
        
        # Observability
        "17-observability": [
            "observability", "logging", "tracing", "monitoring", "langsmith",
            "관측성", "모니터링", "로깅"
        ],
        
        # Multimodal
        "18-multimodal": [
            "multimodal", "clip", "whisper", "llava", "vision", "audio",
            "멀티모달", "비전", "음성"
        ],
        
        # Emerging Techniques
        "19-emerging-techniques": [
            "moe", "mixture", "ssm", "state-space", "emerging",
            "신기술", "최신기술"
        ],
        
        # Trading
        "20-trading": [
            "trading", "ta-lib", "vectorbt", "backtest", "quant", "finance",
            "트레이딩", "퀀트", "금융", "주식"
        ],
        
        # Frontend Design
        "23-frontend-design-architect": [
            "frontend", "ui", "ux", "react", "design", "component",
            "프론트엔드", "디자인", "ui/ux"
        ],
        
        # Spec-Driven Planner
        "24-spec-driven-planner": [
            "spec", "specification", "planning", "task", "requirement",
            "스펙", "기획", "요구사항", "계획"
        ],
    }

    def __init__(self):
        """KeywordMatcher 초기화"""
        # 키워드 → SKILL ID 역방향 인덱스 구축
        self._reverse_index: Dict[str, List[str]] = {}
        for skill_id, keywords in self.KEYWORD_MAP.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self._reverse_index:
                    self._reverse_index[keyword_lower] = []
                self._reverse_index[keyword_lower].append(skill_id)

        logger.info(f"KeywordMatcher initialized with {len(self.KEYWORD_MAP)} skills")

    def match(self, query: str, max_results: int = 3) -> List[Tuple[str, float]]:
        """
        쿼리에 맞는 SKILL 매칭

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수

        Returns:
            (skill_id, score) 튜플 리스트 (점수 내림차순)
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        # SKILL별 점수 계산
        skill_scores: Dict[str, float] = {}

        for skill_id, keywords in self.KEYWORD_MAP.items():
            score = 0.0

            for keyword in keywords:
                keyword_lower = keyword.lower()

                # 완전 매칭 (높은 점수)
                if keyword_lower in query_lower:
                    score += 10.0
                    continue

                # 단어 매칭
                keyword_words = set(re.findall(r'\w+', keyword_lower))
                common_words = query_words & keyword_words
                if common_words:
                    score += len(common_words) * 3.0

            if score > 0:
                skill_scores[skill_id] = score

        # 점수순 정렬
        sorted_skills = sorted(
            skill_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_skills[:max_results]

    def match_skill_ids(self, query: str, max_results: int = 3) -> List[str]:
        """
        매칭된 SKILL ID만 반환

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수

        Returns:
            skill_id 리스트
        """
        matches = self.match(query, max_results)
        return [skill_id for skill_id, _ in matches]

    def get_all_keywords(self) -> Dict[str, List[str]]:
        """
        전체 키워드 맵 반환

        Returns:
            SKILL ID → 키워드 리스트 딕셔너리
        """
        return self.KEYWORD_MAP.copy()

    def get_skills_for_keyword(self, keyword: str) -> List[str]:
        """
        특정 키워드에 해당하는 SKILL 반환

        Args:
            keyword: 검색할 키워드

        Returns:
            SKILL ID 리스트
        """
        keyword_lower = keyword.lower()
        return self._reverse_index.get(keyword_lower, [])
