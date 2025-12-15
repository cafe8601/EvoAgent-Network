# 🌌 AI Research Skills: The Ultimate Guidebook v3.0

> **"Systematic Mastery of AI: From Research to Production & Autonomous Agents"**
>
> 이 가이드북은 **26개 카테고리**, **60+ 전문 스킬**, **61+ 상세 워크플로우 예시**를 주제별로 체계적으로 정리한 **멀티 파일 에디션**입니다.

---

## 🧭 가이드북 네비게이션

각 링크를 클릭하여 해당 주제의 상세 가이드로 이동하세요.

### [🏗️ Part 1: AI 모델링 기초 (Foundations)](./GUIDEBOOK_01_FOUNDATIONS.md)
*   LLM의 뼈대가 되는 아키텍처, 토큰화, 데이터 처리를 다룹니다.
*   **포함 스킬**: 01-Model Architecture, 02-Tokenization, 05-Data Processing

### [🏋️ Part 2: 학습 파이프라인 (Training)](./GUIDEBOOK_02_TRAINING.md)
*   모델을 학습시키고 성능을 평가하는 핵심 기술입니다.
*   **포함 스킬**: 03-Fine-tuning, 06-Post-training, 08-Distributed Training, 10-Optimization, 11-Evaluation

### [🚀 Part 3: 배포 및 운영 (Deployment & Ops)](./GUIDEBOOK_03_DEPLOYMENT_OPS.md)
*   모델을 서비스로 배포하고 안정적으로 운영하는 방법입니다.
*   **포함 스킬**: 09-Infrastructure, 12-Inference Serving, 13-MLOps, 17-Observability

### [🧩 Part 4: 애플리케이션 응용 (Applications)](./GUIDEBOOK_04_APPLICATIONS.md)
*   LLM을 활용해 실제 애플리케이션을 만드는 기술입니다.
*   **포함 스킬**: 07-Safety & Alignment, 14-Agents, 15-RAG, 16-Prompt Engineering, 18-Multimodal, 19-Emerging Techniques

### [🤖 Part 5: 도메인 스페셜리스트 (Specialists)](./GUIDEBOOK_05_SPECIALISTS.md)
*   금융, 블록체인, 개발(FE/BE), 멀티에이전트 등 특정 도메인에 특화된 고급 스킬입니다.
*   **포함 스킬**: 20-Trading, 21-Multi-Agent System, 22-Blockchain Security, 23-Frontend Architect, 24-Spec-Driven Planner, 25-Backend Architect, **26-Investment Trading Systems**

### [🔧 Part 6: 통합 워크플로우 (Workflows)](./GUIDEBOOK_06_WORKFLOWS.md)
*   모든 스킬을 조합하여 해결하는 **51가지의 상세 시나리오** 모음집입니다.
*   **포함 예시**: 한국어 LLM 구축, 알고리즘 트레이딩 봇, 사내 RAG 시스템 등

### [🤖 Part 7: 학습 기반 멀티에이전트 코딩 (Multi-Agent Coding)](./GUIDEBOOK_07_MULTIAGENT_CODING.md)
*   비용/속도/실용성 중심의 **AI 에이전트 팀 기반 소프트웨어 개발** 워크플로우입니다.
*   **포함 예시**: Big Three 풀스택 개발, 레거시 마이그레이션, 버그 조사, 코드 리뷰 자동화, CI/CD 통합 등 **10가지 실전 시나리오**

---

## 📊 카테고리 요약표

| 번호 | 카테고리 | 핵심 기능 | 대표 도구 | 난이도 |
|:----:|----------|-----------|-----------|:------:|
| 01 | Model Architecture | 모델 구조 설계 | NanoGPT, Mamba, LitGPT | ⭐⭐⭐ |
| 02 | Tokenization | 텍스트 토큰화 | HuggingFace Tokenizers | ⭐⭐ |
| 03 | Fine-tuning | 모델 미세조정 | Unsloth, Axolotl | ⭐⭐ |
| 05 | Data Processing | 데이터 전처리 | NeMo Curator, Ray Data | ⭐⭐ |
| 06 | Post-training | RLHF/DPO 학습 | TRL, GRPO, OpenRLHF | ⭐⭐⭐ |
| 07 | Safety Alignment | 안전성 정렬 | NeMo Guardrails | ⭐⭐ |
| 08 | Distributed Training | 분산 학습 | DeepSpeed, FSDP | ⭐⭐⭐ |
| 09 | Infrastructure | 인프라 관리 | Modal | ⭐⭐ |
| 10 | Optimization | 성능 최적화 | Flash Attention | ⭐⭐⭐ |
| 11 | Evaluation | 모델 평가 | lm-evaluation-harness | ⭐⭐ |
| 12 | Inference Serving | 추론 서빙 | vLLM, TensorRT-LLM | ⭐⭐ |
| 13 | MLOps | 실험 관리 | Weights & Biases | ⭐⭐ |
| 14 | Agents | AI 에이전트 | LangChain, LlamaIndex | ⭐⭐ |
| 15 | RAG | 검색 증강 생성 | Chroma, FAISS | ⭐⭐ |
| 16 | Prompt Engineering | 프롬프트 최적화 | DSPy, Instructor | ⭐⭐ |
| 17 | Observability | 모니터링 | LangSmith | ⭐⭐ |
| 18 | Multimodal | 멀티모달 처리 | Whisper, CLIP | ⭐⭐ |
| 19 | Emerging Techniques | 신기술 | Model Merging, MoE | ⭐⭐⭐ |
| 20 | Trading | 알고리즘 트레이딩 | Backtrader, CCXT | ⭐⭐⭐ |
| 21 | Multi-Agent Learning | 멀티에이전트 시스템 | Agent Pool, Memory System | ⭐⭐⭐ |
| 22 | Blockchain Security | 블록체인 보안 | ZK Proofs, Smart Contracts | ⭐⭐⭐⭐ |
| 23 | Frontend Architect | 프론트엔드 설계 | Design Tokens, Atomic Design | ⭐⭐ |
| 24 | Spec-Driven Planner | 명세 주도 개발 | GitHub Spec Kit, TDD | ⭐⭐ |
| 25 | Backend Architect | 백엔드 설계 | Clean Architecture, OWASP | ⭐⭐⭐ |
| 26 | Investment Systems | 종합 투자 시스템 | NautilusTrader, FinRL | ⭐⭐⭐⭐ |

---

## 🧭 스킬 선택 가이드

### "나는 지금 무엇을 해야 하는가?"

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 목표가 무엇인가요?                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📚 LLM을 이해하고 싶다                                          │
│  └→ [Part 1: 기초](./GUIDEBOOK_01_FOUNDATIONS.md)              │
│                                                                 │
│  🔧 내 데이터로 모델을 맞춤화하고 싶다                            │
│  └→ [Part 2: 학습](./GUIDEBOOK_02_TRAINING.md)                 │
│                                                                 │
│  🚀 모델을 서비스로 배포하고 싶다                                 │
│  └→ [Part 3: 배포/운영](./GUIDEBOOK_03_DEPLOYMENT_OPS.md)      │
│                                                                 │
│  🤖 LLM이 도구를 사용하게 하고 싶다                               │
│  └→ [Part 4: 응용](./GUIDEBOOK_04_APPLICATIONS.md)             │
│                                                                 │
│  💰 트레이딩 봇을 만들고 싶다                                     │
│  └→ [Part 5: 스페셜리스트](./GUIDEBOOK_05_SPECIALISTS.md)      │
│      (20. Trading, 26. Investment Systems)                      │
│                                                                 │
│  🧬 여러 AI가 협력하는 시스템을 만들고 싶다                        │
│  └→ [Part 5: 스페셜리스트](./GUIDEBOOK_05_SPECIALISTS.md)      │
│      (21. Multi-Agent System)                                   │
│                                                                 │
│  🔐 블록체인으로 에이전트를 인증하고 싶다                          │
│  └→ [Part 5: 스페셜리스트](./GUIDEBOOK_05_SPECIALISTS.md)      │
│                                                                 │
│  💻 웹/앱 서비스를 체계적으로 개발하고 싶다                         │
│  └→ [Part 5: 스페셜리스트](./GUIDEBOOK_05_SPECIALISTS.md)      │
│      (23. Frontend, 24. Spec-Planner, 25. Backend)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
