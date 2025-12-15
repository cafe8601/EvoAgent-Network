# AI Research Skills 확장 예시 북 (Extended Cookbook)

> 현실적인 프로젝트 시나리오와 상세 구현 가이드

---

## 📚 목차

### Part A: 연구 & 학습 파이프라인
- [A1. 도메인 특화 LLM 개발 (의료/법률/금융)](#a1-도메인-특화-llm-개발)
- [A2. 연속 학습 시스템](#a2-연속-학습-시스템)
- [A3. 모델 경량화 파이프라인](#a3-모델-경량화-파이프라인)
- [A4. 합성 데이터 생성](#a4-합성-데이터-생성)

### Part B: 프로덕션 시스템
- [B1. 엔터프라이즈 RAG 시스템](#b1-엔터프라이즈-rag-시스템)
- [B2. 실시간 채팅 서비스](#b2-실시간-채팅-서비스)
- [B3. 문서 자동화 시스템](#b3-문서-자동화-시스템)
- [B4. 콘텐츠 생성 플랫폼](#b4-콘텐츠-생성-플랫폼)

### Part C: 멀티에이전트 시스템
- [C1. 소프트웨어 개발 자동화](#c1-소프트웨어-개발-자동화)
- [C2. 데이터 분석 파이프라인](#c2-데이터-분석-파이프라인)
- [C3. 콘텐츠 모더레이션](#c3-콘텐츠-모더레이션)
- [C4. 연구 논문 분석](#c4-연구-논문-분석)

### Part D: 한국 시장 트레이딩 심화
- [D1. 옵션 스프레드 전략](#d1-옵션-스프레드-전략)
- [D2. 뉴스 기반 트레이딩](#d2-뉴스-기반-트레이딩)
- [D3. 포트폴리오 최적화](#d3-포트폴리오-최적화)

### Part E: DevOps & 인프라
- [E1. MLOps 파이프라인](#e1-mlops-파이프라인)
- [E2. 서버리스 AI 배포](#e2-서버리스-ai-배포)

---

# Part A: 연구 & 학습 파이프라인

## A1. 도메인 특화 LLM 개발

### 시나리오: 금융 도메인 LLM

**목표**: 금융 보고서 분석, 투자 리서치 요약, 재무제표 해석에 특화된 LLM 개발

**사용 스킬**: `02`, `03`, `05`, `06`, `11`, `15`

#### Step 1: 금융 코퍼스 수집 및 정제

```python
# 05-data-processing/ray-data
import ray
from ray.data import read_json

# 데이터 소스
sources = [
    "sec_filings/",      # SEC 공시 자료
    "earnings_calls/",   # 실적 발표 전사본
    "analyst_reports/",  # 애널리스트 리포트
    "financial_news/"    # 금융 뉴스
]

@ray.remote
def process_financial_doc(doc):
    # 1. 금융 용어 표준화
    doc = standardize_financial_terms(doc)
    
    # 2. 숫자/통화 정규화
    doc = normalize_numbers(doc)
    
    # 3. 테이블 추출 및 구조화
    tables = extract_tables(doc)
    
    # 4. 품질 점수 계산
    quality_score = compute_quality(doc)
    
    return {
        "text": doc,
        "tables": tables,
        "quality_score": quality_score,
        "source": doc["source"]
    }

# 분산 처리
ds = ray.data.read_json(sources)
processed = ds.map(process_financial_doc)
processed.filter(lambda x: x["quality_score"] > 0.7).write_parquet("financial_corpus/")
```

#### Step 2: 금융 토크나이저 확장

```python
# 02-tokenization
from transformers import AutoTokenizer

base_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")

# 금융 특수 토큰 추가
financial_tokens = [
    # 통화
    "₩", "€", "£", "¥",
    # 금융 용어
    "EBITDA", "P/E", "EPS", "ROE", "ROA", "WACC",
    "M&A", "IPO", "ETF", "SPAC",
    # 숫자 표현
    "1Q", "2Q", "3Q", "4Q",
    "YoY", "QoQ", "MoM",
    # 등급
    "AAA", "AA+", "AA", "AA-", "A+", "A", "A-",
]

base_tokenizer.add_tokens(financial_tokens)
base_tokenizer.save_pretrained("./financial_tokenizer")
```

#### Step 3: 도메인 SFT

```yaml
# axolotl_financial_sft.yaml
base_model: meta-llama/Meta-Llama-3-8B
tokenizer_type: LlamaTokenizer
load_in_4bit: true

datasets:
  - path: ./financial_instructions.jsonl
    type: alpaca
  - path: ./earnings_qa.jsonl
    type: alpaca
  - path: ./report_summary.jsonl
    type: alpaca

output_dir: ./financial_llm_sft
sequence_len: 4096

adapter: lora
lora_r: 64
lora_alpha: 128
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj

learning_rate: 2e-5
num_epochs: 3
micro_batch_size: 2
gradient_accumulation_steps: 8

wandb_project: financial-llm
```

#### Step 4: 금융 RAG 통합

```python
# 15-rag + 14-agents
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 금융 문서 벡터 DB
financial_db = Chroma(
    persist_directory="./financial_vectordb",
    embedding_function=HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
)

# 금융 특화 프롬프트
FINANCIAL_PROMPT = """
당신은 금융 분석 전문가입니다. 제공된 문서를 기반으로 질문에 답변하세요.

규칙:
1. 수치 데이터는 정확하게 인용하세요
2. 출처(문서명, 날짜)를 명시하세요
3. 불확실한 정보는 명확히 표시하세요
4. 투자 조언이 아님을 명시하세요

문서:
{context}

질문: {question}

답변:
"""

llm = ChatOpenAI(model="./financial_llm_sft", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=financial_db.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": FINANCIAL_PROMPT}
)
```

---

## A2. 연속 학습 시스템

### 시나리오: 뉴스 코퍼스로 지속적 모델 업데이트

**목표**: 새로운 지식을 지속적으로 학습하면서 기존 지식 유지

**사용 스킬**: `03`, `05`, `11`, `13`

#### 아키텍처

```
[새 데이터 스트림] → [품질 필터] → [망각 평가] 
                                      ↓
                              [점진적 학습]
                                      ↓
                              [성능 검증]
                                      ↓
                    [Pass] → [모델 업데이트] → [배포]
                    [Fail] → [롤백]
```

#### 구현

```python
class ContinualLearningPipeline:
    def __init__(self, base_model_path: str):
        self.model = AutoModelForCausalLM.from_pretrained(base_model_path)
        self.replay_buffer = ReplayBuffer(max_size=10000)
        self.evaluator = BenchmarkEvaluator(["mmlu", "hellaswag"])
        self.baseline_scores = self.evaluator.evaluate(self.model)
        
    def update(self, new_data: Dataset):
        # 1. 새 데이터 품질 검증
        filtered_data = self.quality_filter(new_data)
        
        # 2. 리플레이 버퍼에서 기존 데이터 샘플링 (망각 방지)
        replay_data = self.replay_buffer.sample(len(filtered_data) // 2)
        combined_data = concatenate_datasets([filtered_data, replay_data])
        
        # 3. 점진적 학습 (작은 learning rate)
        trainer = Trainer(
            model=self.model,
            train_dataset=combined_data,
            args=TrainingArguments(
                learning_rate=1e-6,  # 낮은 LR
                num_train_epochs=1,
                per_device_train_batch_size=4,
                output_dir="./continual_checkpoints"
            )
        )
        trainer.train()
        
        # 4. 성능 검증 (망각 체크)
        new_scores = self.evaluator.evaluate(self.model)
        
        forgetting_rate = self._calculate_forgetting(
            self.baseline_scores, new_scores
        )
        
        if forgetting_rate > 0.05:  # 5% 이상 성능 저하
            print(f"⚠️ 망각 감지: {forgetting_rate:.1%} 성능 저하")
            self._rollback()
            return False
        
        # 5. 리플레이 버퍼 업데이트
        self.replay_buffer.add(filtered_data)
        
        # 6. 체크포인트 저장
        self.model.save_pretrained(f"./model_v{self.version}")
        self.version += 1
        
        return True
    
    def _calculate_forgetting(self, old_scores, new_scores):
        """각 태스크별 망각률 계산"""
        forgetting = {}
        for task in old_scores:
            if old_scores[task] > 0:
                drop = (old_scores[task] - new_scores[task]) / old_scores[task]
                forgetting[task] = max(0, drop)
        return sum(forgetting.values()) / len(forgetting)
```

---

## A3. 모델 경량화 파이프라인

### 시나리오: 70B 모델을 모바일에서 실행

**목표**: 프로덕션 모델을 엣지 디바이스용으로 경량화

**사용 스킬**: `10`, `19`, `12`

#### 경량화 전략

```
[원본 70B 모델]
      ↓
[Knowledge Distillation] → [7B 학생 모델]
      ↓
[Pruning] → 30% 파라미터 제거
      ↓
[Quantization] → 4-bit GGUF
      ↓
[벤치마크] → 정확도 95% 유지 확인
      ↓
[배포] → llama.cpp / iOS / Android
```

#### Step 1: 지식 증류

```python
# 19-emerging-techniques/knowledge-distillation
from transformers import AutoModelForCausalLM
import torch

class DistillationTrainer:
    def __init__(self, teacher_model, student_model, temperature=2.0):
        self.teacher = teacher_model
        self.teacher.eval()
        self.student = student_model
        self.temperature = temperature
        
    def distillation_loss(self, student_logits, teacher_logits, labels):
        # Soft target loss (KL Divergence)
        soft_teacher = F.softmax(teacher_logits / self.temperature, dim=-1)
        soft_student = F.log_softmax(student_logits / self.temperature, dim=-1)
        soft_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean')
        
        # Hard target loss (Cross Entropy)
        hard_loss = F.cross_entropy(student_logits, labels)
        
        # Combined loss
        return 0.7 * soft_loss * (self.temperature ** 2) + 0.3 * hard_loss
    
    def train_step(self, batch):
        with torch.no_grad():
            teacher_outputs = self.teacher(**batch)
            teacher_logits = teacher_outputs.logits
        
        student_outputs = self.student(**batch)
        student_logits = student_outputs.logits
        
        loss = self.distillation_loss(
            student_logits, 
            teacher_logits, 
            batch["labels"]
        )
        
        return loss
```

#### Step 2: 양자화

```bash
# GGUF 변환 (llama.cpp)
python convert.py ./distilled_7b --outtype f16 --outfile distilled_7b.f16.gguf

# 4-bit 양자화
./quantize distilled_7b.f16.gguf distilled_7b.Q4_K_M.gguf Q4_K_M

# 크기 확인
# 원본 70B: ~140GB
# 증류 7B: ~14GB  
# 4-bit: ~4GB
```

#### Step 3: 모바일 배포

```swift
// iOS (llama.cpp Swift binding)
import LlamaCpp

class MobileLLM {
    private var context: LlamaContext?
    
    func load(modelPath: String) {
        let params = LlamaContextParams.default()
        params.n_ctx = 2048
        params.n_threads = 4  // 모바일 최적화
        
        context = LlamaContext(path: modelPath, params: params)
    }
    
    func generate(prompt: String) async -> String {
        guard let ctx = context else { return "" }
        
        let tokens = ctx.tokenize(prompt)
        var output = ""
        
        for _ in 0..<256 { // max tokens
            let nextToken = ctx.sample()
            if nextToken == ctx.eosToken { break }
            output += ctx.detokenize([nextToken])
        }
        
        return output
    }
}
```

---

## A4. 합성 데이터 생성

### 시나리오: 개인정보 없는 학습 데이터 생성

**목표**: 프라이버시 보호하면서 학습용 데이터 생성

**사용 스킬**: `03`, `07`, `11`

```python
class SyntheticDataGenerator:
    """개인정보 제거된 합성 데이터 생성"""
    
    def __init__(self, generator_model, validator_model):
        self.generator = generator_model
        self.validator = validator_model
        self.pii_detector = PIIDetector()
        
    def generate_batch(self, template: str, n_samples: int) -> List[Dict]:
        samples = []
        
        for _ in range(n_samples):
            # 1. 합성 데이터 생성
            generated = self.generator.generate(template)
            
            # 2. PII 검출
            pii_found = self.pii_detector.detect(generated)
            if pii_found:
                # PII 제거/대체
                generated = self.pii_detector.anonymize(generated)
            
            # 3. 품질 검증
            quality_score = self.validator.score(generated)
            
            if quality_score > 0.8:
                samples.append({
                    "text": generated,
                    "quality": quality_score,
                    "pii_clean": not pii_found
                })
        
        return samples
    
    def generate_instruction_dataset(self, categories: List[str], per_category: int):
        """지시사항 데이터셋 생성"""
        
        dataset = []
        
        for category in categories:
            template = CATEGORY_TEMPLATES[category]
            
            for i in range(per_category):
                # 다양한 복잡도
                complexity = ["simple", "medium", "complex"][i % 3]
                
                instruction = self.generator.generate(
                    f"Generate a {complexity} {category} instruction"
                )
                
                response = self.generator.generate(
                    f"Instruction: {instruction}\nResponse:"
                )
                
                # 품질 검증
                if self.validator.validate(instruction, response):
                    dataset.append({
                        "instruction": instruction,
                        "input": "",
                        "output": response,
                        "category": category,
                        "complexity": complexity
                    })
        
        return dataset

# 사용 예시
generator = SyntheticDataGenerator(
    generator_model=load_model("gpt-4o"),
    validator_model=load_model("claude-3-opus")
)

# 10,000개 합성 데이터 생성
synthetic_data = generator.generate_instruction_dataset(
    categories=["coding", "math", "writing", "reasoning"],
    per_category=2500
)
```

---

# Part B: 프로덕션 시스템

## B1. 엔터프라이즈 RAG 시스템

### 시나리오: 대기업 사내 문서 검색 시스템

**목표**: 10만+ 문서, 1000+ 동시 사용자 지원

**사용 스킬**: `15`, `14`, `12`, `17`, `07`

#### 아키텍처

```
[사용자] → [API Gateway] → [Load Balancer]
                                 ↓
                    [RAG Service Cluster]
                    /         |         \
            [vLLM 1]    [vLLM 2]    [vLLM 3]
                    \         |         /
                     [Vector DB Cluster]
                     (Qdrant / Milvus)
                              ↓
                    [Document Store]
                    (PostgreSQL + S3)
```

#### 구현

```python
# FastAPI + 비동기 RAG
from fastapi import FastAPI, BackgroundTasks
from qdrant_client import QdrantClient
from openai import AsyncOpenAI
import asyncio

app = FastAPI()
qdrant = QdrantClient(host="qdrant-cluster", port=6333)
llm_client = AsyncOpenAI(base_url="http://vllm-cluster:8000/v1")

class EnterpriseRAG:
    def __init__(self):
        self.cache = RedisCache()
        self.rate_limiter = RateLimiter(requests_per_minute=100)
        
    async def search(self, query: str, user_id: str, department: str):
        # 1. 캐시 확인
        cache_key = f"rag:{hash(query)}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # 2. ACL 기반 필터링
        access_filter = self.build_access_filter(user_id, department)
        
        # 3. 하이브리드 검색 (Semantic + Keyword)
        semantic_results = await self.semantic_search(query, access_filter)
        keyword_results = await self.keyword_search(query, access_filter)
        
        # 4. Reciprocal Rank Fusion
        merged = self.rrf_merge(semantic_results, keyword_results)
        
        # 5. LLM 생성
        context = self.format_context(merged[:5])
        response = await self.generate_response(query, context)
        
        # 6. 캐시 저장
        await self.cache.set(cache_key, response, ttl=3600)
        
        return response
    
    async def semantic_search(self, query: str, filter: dict):
        embedding = await self.embed(query)
        
        results = await qdrant.search(
            collection_name="enterprise_docs",
            query_vector=embedding,
            query_filter=filter,
            limit=10
        )
        
        return results
    
    async def generate_response(self, query: str, context: str):
        messages = [
            {"role": "system", "content": ENTERPRISE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        response = await llm_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            messages=messages,
            temperature=0.1,
            max_tokens=1024
        )
        
        return response.choices[0].message.content

@app.post("/api/v1/search")
async def search_endpoint(request: SearchRequest, background_tasks: BackgroundTasks):
    rag = EnterpriseRAG()
    
    # Rate limiting
    if not rag.rate_limiter.allow(request.user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    response = await rag.search(
        query=request.query,
        user_id=request.user_id,
        department=request.department
    )
    
    # 백그라운드로 로깅
    background_tasks.add_task(log_query, request, response)
    
    return {"answer": response, "sources": response.sources}
```

---

## B2. 실시간 채팅 서비스

### 시나리오: 스트리밍 응답 + 대화 기록 관리

**사용 스킬**: `12`, `14`, `17`

```python
# WebSocket 기반 스트리밍 채팅
from fastapi import FastAPI, WebSocket
from openai import AsyncOpenAI
import json

app = FastAPI()
client = AsyncOpenAI(base_url="http://vllm:8000/v1")

class ChatSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        self.redis = Redis()
        
    async def load(self):
        """세션 복원"""
        data = await self.redis.get(f"chat:{self.session_id}")
        if data:
            self.messages = json.loads(data)
    
    async def save(self):
        """세션 저장"""
        await self.redis.setex(
            f"chat:{self.session_id}",
            3600 * 24,  # 24시간 유지
            json.dumps(self.messages)
        )
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        
        # 컨텍스트 윈도우 관리 (최근 20개만)
        if len(self.messages) > 20:
            # 시스템 메시지 유지 + 최근 19개
            self.messages = self.messages[:1] + self.messages[-19:]

@app.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    session = ChatSession(session_id)
    await session.load()
    
    # 시스템 프롬프트 설정
    if not session.messages:
        session.add_message("system", "당신은 도움이 되는 AI 어시스턴트입니다.")
    
    try:
        while True:
            # 사용자 메시지 수신
            user_message = await websocket.receive_text()
            session.add_message("user", user_message)
            
            # 스트리밍 응답 생성
            stream = await client.chat.completions.create(
                model="meta-llama/Meta-Llama-3-8B-Instruct",
                messages=session.messages,
                stream=True,
                max_tokens=1024
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    
                    # 실시간 토큰 전송
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })
            
            # 완료 신호
            await websocket.send_json({
                "type": "complete",
                "content": full_response
            })
            
            session.add_message("assistant", full_response)
            await session.save()
            
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
```

---

## B3. 문서 자동화 시스템

### 시나리오: 계약서/보고서 자동 생성

**사용 스킬**: `16`, `15`, `07`

```python
from pydantic import BaseModel
from instructor import from_openai
from openai import OpenAI

# 구조화된 출력 (16-prompt-engineering/instructor)
client = from_openai(OpenAI())

class ContractSection(BaseModel):
    title: str
    content: str
    legal_references: List[str]

class Contract(BaseModel):
    parties: List[str]
    effective_date: str
    sections: List[ContractSection]
    signatures: List[str]

class ContractGenerator:
    def __init__(self):
        self.template_db = ContractTemplateDB()
        self.legal_rag = LegalRAG()
        
    def generate(self, contract_type: str, params: dict) -> Contract:
        # 1. 템플릿 로드
        template = self.template_db.get(contract_type)
        
        # 2. 관련 법률 조항 검색
        legal_context = self.legal_rag.search(
            f"{contract_type} 관련 법률 조항"
        )
        
        # 3. 구조화된 계약서 생성
        contract = client.chat.completions.create(
            model="gpt-4o",
            response_model=Contract,
            messages=[
                {"role": "system", "content": f"""
                    당신은 법률 문서 작성 전문가입니다.
                    다음 템플릿과 법률 조항을 참고하여 계약서를 작성하세요.
                    
                    템플릿: {template}
                    관련 법률: {legal_context}
                """},
                {"role": "user", "content": f"""
                    계약 유형: {contract_type}
                    당사자: {params['parties']}
                    계약 조건: {params['terms']}
                """}
            ]
        )
        
        # 4. 검증
        self.validate(contract)
        
        return contract
    
    def validate(self, contract: Contract):
        """계약서 유효성 검증"""
        # 필수 조항 존재 확인
        required_sections = ["목적", "기간", "대금", "해지"]
        for req in required_sections:
            if not any(req in s.title for s in contract.sections):
                raise ValueError(f"필수 조항 누락: {req}")
```

---

## B4. 콘텐츠 생성 플랫폼

### 시나리오: 마케팅 콘텐츠 자동 생성

**사용 스킬**: `14`, `16`, `18`

```python
class ContentGenerationPlatform:
    """멀티채널 마케팅 콘텐츠 생성"""
    
    def __init__(self):
        self.text_llm = ChatOpenAI(model="gpt-4o")
        self.image_gen = DallE3()
        self.voice_gen = ElevenLabs()
        
    async def generate_campaign(self, brief: str, channels: List[str]):
        """캠페인별 콘텐츠 생성"""
        
        results = {}
        
        for channel in channels:
            if channel == "instagram":
                results["instagram"] = await self.generate_instagram(brief)
            elif channel == "blog":
                results["blog"] = await self.generate_blog(brief)
            elif channel == "email":
                results["email"] = await self.generate_email(brief)
            elif channel == "video_script":
                results["video"] = await self.generate_video_script(brief)
        
        return results
    
    async def generate_instagram(self, brief: str):
        # 캡션 생성
        caption = await self.text_llm.ainvoke(f"""
            다음 브리프를 기반으로 인스타그램 캡션을 작성하세요.
            - 150자 이내
            - 이모지 활용
            - 해시태그 5개 포함
            
            브리프: {brief}
        """)
        
        # 이미지 생성
        image_prompt = await self.text_llm.ainvoke(f"""
            다음 캡션에 어울리는 이미지를 DALL-E로 생성하기 위한 
            영어 프롬프트를 작성하세요.
            
            캡션: {caption}
        """)
        
        image_url = await self.image_gen.generate(image_prompt)
        
        return {
            "caption": caption,
            "image_url": image_url,
            "suggested_posting_time": self.get_best_posting_time("instagram")
        }
    
    async def generate_blog(self, brief: str):
        # SEO 최적화된 블로그 글
        outline = await self.text_llm.ainvoke(f"""
            다음 주제로 SEO 최적화된 블로그 글 개요를 작성하세요.
            - H1, H2, H3 구조
            - 타겟 키워드 제안
            - 메타 설명 포함
            
            주제: {brief}
        """)
        
        full_content = await self.text_llm.ainvoke(f"""
            다음 개요를 바탕으로 2000자 분량의 블로그 글을 작성하세요.
            
            개요: {outline}
        """)
        
        return {
            "title": outline["title"],
            "content": full_content,
            "meta_description": outline["meta"],
            "keywords": outline["keywords"]
        }
```

---

# Part C: 멀티에이전트 시스템

## C1. 소프트웨어 개발 자동화

### 시나리오: 요구사항 → 코드 → 테스트 → 배포

**사용 스킬**: `21`, `24`, `14`

```python
class SoftwareDevTeam:
    """AI 소프트웨어 개발 팀"""
    
    def __init__(self):
        self.agents = {
            "pm": ProjectManagerAgent(),
            "architect": ArchitectAgent(),
            "developer": DeveloperAgent(),
            "reviewer": CodeReviewerAgent(),
            "tester": TesterAgent(),
            "devops": DevOpsAgent()
        }
        self.memory = SharedMemory()
        
    async def develop_feature(self, requirement: str):
        """기능 개발 전체 파이프라인"""
        
        # 1. PM: 요구사항 분석 및 태스크 분해
        tasks = await self.agents["pm"].analyze(requirement)
        self.memory.set("tasks", tasks)
        
        # 2. Architect: 기술 설계
        design = await self.agents["architect"].design(
            requirement, 
            tasks,
            existing_code=self.memory.get("codebase")
        )
        self.memory.set("design", design)
        
        # 3. Developer: 코드 구현 (TDD)
        for task in tasks:
            # 테스트 먼저 작성
            tests = await self.agents["tester"].write_tests(task, design)
            
            # 코드 구현
            code = await self.agents["developer"].implement(
                task, 
                design, 
                tests
            )
            
            # 코드 리뷰
            review = await self.agents["reviewer"].review(code, tests)
            
            if review.issues:
                # 리뷰 반영
                code = await self.agents["developer"].fix(code, review.issues)
            
            self.memory.append("implemented", {"task": task, "code": code})
        
        # 4. 통합 테스트
        integration_results = await self.agents["tester"].integration_test(
            self.memory.get("implemented")
        )
        
        if not integration_results.passed:
            # 문제 해결
            fixes = await self.agents["developer"].fix_integration(
                integration_results.failures
            )
        
        # 5. 배포 준비
        deployment = await self.agents["devops"].prepare_deployment(
            self.memory.get("implemented")
        )
        
        return {
            "tasks_completed": len(tasks),
            "code": self.memory.get("implemented"),
            "tests": integration_results,
            "deployment_ready": deployment
        }
```

---

## C2. 데이터 분석 파이프라인

### 시나리오: 자연어 → SQL → 인사이트

**사용 스킬**: `21`, `16`, `14`

```python
class DataAnalystTeam:
    """데이터 분석 멀티에이전트"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.agents = {
            "interpreter": QueryInterpreterAgent(),
            "sql_writer": SQLWriterAgent(db_schema=self.get_schema()),
            "executor": QueryExecutorAgent(db_connection),
            "analyst": InsightAnalystAgent(),
            "visualizer": VisualizerAgent()
        }
    
    async def analyze(self, question: str) -> AnalysisResult:
        # 1. 자연어 해석
        intent = await self.agents["interpreter"].interpret(question)
        
        # 2. SQL 생성
        sql = await self.agents["sql_writer"].generate(intent)
        
        # 3. SQL 검증 및 실행
        if await self.validate_sql(sql):
            results = await self.agents["executor"].execute(sql)
        else:
            # SQL 수정 요청
            sql = await self.agents["sql_writer"].fix(sql, validation_errors)
            results = await self.agents["executor"].execute(sql)
        
        # 4. 인사이트 추출
        insights = await self.agents["analyst"].extract_insights(
            question=question,
            data=results,
            context=self.get_business_context()
        )
        
        # 5. 시각화 생성
        charts = await self.agents["visualizer"].create_charts(
            data=results,
            insights=insights
        )
        
        return AnalysisResult(
            query=sql,
            data=results,
            insights=insights,
            visualizations=charts
        )
    
    async def validate_sql(self, sql: str) -> bool:
        """SQL 안전성 검증"""
        # EXPLAIN으로 실행 계획 확인
        # 위험한 패턴 감지 (DROP, TRUNCATE 등)
        # 성능 예측
        pass
```

---

## C3. 콘텐츠 모더레이션

### 시나리오: 사용자 콘텐츠 실시간 검수

**사용 스킬**: `21`, `07`, `18`

```python
class ContentModerationPipeline:
    """콘텐츠 모더레이션 파이프라인"""
    
    def __init__(self):
        self.agents = {
            "text": TextModerationAgent(),
            "image": ImageModerationAgent(),
            "spam": SpamDetectionAgent(),
            "context": ContextAnalyzerAgent(),
            "appeals": AppealsHandlerAgent()
        }
        self.policy = CommunityPolicy.load("./policies/community_guidelines.yaml")
        
    async def moderate(self, content: UserContent) -> ModerationResult:
        # 병렬 검사
        checks = await asyncio.gather(
            self.agents["text"].check(content.text) if content.text else None,
            self.agents["image"].check(content.images) if content.images else None,
            self.agents["spam"].check(content),
            return_exceptions=True
        )
        
        text_result, image_result, spam_result = checks
        
        # 결과 취합
        violations = []
        
        if text_result and text_result.violations:
            violations.extend(text_result.violations)
        
        if image_result and image_result.violations:
            violations.extend(image_result.violations)
        
        if spam_result and spam_result.is_spam:
            violations.append(Violation(type="spam", confidence=spam_result.confidence))
        
        # 컨텍스트 분석 (풍자, 인용 등)
        if violations:
            context_check = await self.agents["context"].analyze(
                content=content,
                violations=violations
            )
            
            # 컨텍스트로 해제 가능한 위반 필터링
            violations = [v for v in violations if not context_check.is_exception(v)]
        
        # 최종 판정
        if not violations:
            return ModerationResult(action="approve")
        
        severity = max(v.severity for v in violations)
        
        if severity >= 0.9:
            return ModerationResult(action="remove", violations=violations)
        elif severity >= 0.7:
            return ModerationResult(action="review", violations=violations)
        else:
            return ModerationResult(action="warn", violations=violations)
```

---

## C4. 연구 논문 분석

### 시나리오: 논문 자동 리뷰 및 인사이트 추출

**사용 스킬**: `21`, `15`, `18`

```python
class ResearchPaperAnalyzer:
    """연구 논문 분석 시스템"""
    
    def __init__(self):
        self.agents = {
            "parser": PaperParserAgent(),
            "methodology": MethodologyReviewerAgent(),
            "stats": StatisticalReviewerAgent(),
            "literature": LiteratureLinkerAgent(),
            "summarizer": SummarizerAgent(),
            "critic": CriticAgent()
        }
        self.arxiv_db = ArxivVectorDB()
        
    async def analyze_paper(self, pdf_bytes: bytes) -> PaperAnalysis:
        # 1. 논문 파싱
        paper = await self.agents["parser"].parse(pdf_bytes)
        
        # 2. 병렬 분석
        results = await asyncio.gather(
            self.agents["methodology"].review(paper.methodology),
            self.agents["stats"].review(paper.results, paper.tables),
            self.agents["literature"].find_related(paper.abstract, self.arxiv_db),
            self.agents["critic"].critique(paper)
        )
        
        methodology_review, stats_review, related_papers, critique = results
        
        # 3. 종합 요약
        summary = await self.agents["summarizer"].summarize(
            paper=paper,
            reviews={
                "methodology": methodology_review,
                "statistics": stats_review,
                "critique": critique
            },
            related=related_papers
        )
        
        return PaperAnalysis(
            title=paper.title,
            tldr=summary.tldr,  # 1문장 요약
            key_contributions=summary.contributions,
            methodology_assessment=methodology_review,
            statistical_validity=stats_review,
            limitations=critique.limitations,
            related_work=related_papers[:5],
            recommended_for=self.classify_audience(paper)
        )
```

---

# Part D: 한국 시장 트레이딩 심화

## D1. 옵션 스프레드 전략

### 시나리오: 아이언 콘도르 자동매매

```python
class IronCondorStrategy:
    """아이언 콘도르 자동매매 전략"""
    
    def __init__(self, api):
        self.api = api
        self.config = {
            "wing_width": 2,      # 행사가 간격 (ATM 기준)
            "target_delta": 0.15, # 타겟 델타
            "profit_target": 0.5, # 50% 익절
            "stop_loss": 2.0,     # 최대 손실 2x 프리미엄
            "dte_range": (7, 21)  # 잔존일 7-21일
        }
        
    def find_strikes(self, chain: OptionChain):
        """적정 행사가 탐색"""
        atm = chain.get_atm_strike()
        
        # 델타 기준으로 OTM 행사가 선택
        short_call = chain.find_strike_by_delta(0.15, "call")
        short_put = chain.find_strike_by_delta(-0.15, "put")
        
        long_call = short_call + self.config["wing_width"] * chain.strike_interval
        long_put = short_put - self.config["wing_width"] * chain.strike_interval
        
        return {
            "short_call": short_call,
            "long_call": long_call,
            "short_put": short_put,
            "long_put": long_put
        }
    
    def calculate_greeks(self, strikes, chain):
        """포지션 그릭스 계산"""
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        
        # Short Call Spread
        total_delta -= chain.get_option(strikes["short_call"], "call").delta
        total_delta += chain.get_option(strikes["long_call"], "call").delta
        
        # Short Put Spread
        total_delta -= chain.get_option(strikes["short_put"], "put").delta
        total_delta += chain.get_option(strikes["long_put"], "put").delta
        
        # Gamma, Theta, Vega 유사하게 계산
        # ...
        
        return {
            "delta": total_delta,
            "gamma": total_gamma,
            "theta": total_theta,
            "vega": total_vega
        }
    
    def entry_signal(self, market_data):
        """진입 시그널"""
        # IV가 높을 때 진입 (IV Rank > 50)
        iv_rank = self.calculate_iv_rank(market_data)
        
        if iv_rank < 50:
            return False
        
        # 횡보장 확인 (ADX < 25)
        adx = self.calculate_adx(market_data, period=14)
        
        if adx > 25:
            return False
        
        return True
    
    def manage_position(self, position):
        """포지션 관리"""
        current_pnl = position.unrealized_pnl
        max_profit = position.initial_credit
        
        # 50% 익절
        if current_pnl >= max_profit * 0.5:
            return {"action": "close", "reason": "profit_target"}
        
        # 스톱로스
        if current_pnl <= -max_profit * 2:
            return {"action": "close", "reason": "stop_loss"}
        
        # 잔존일 3일 이하: 청산
        if position.dte <= 3:
            return {"action": "close", "reason": "expiration"}
        
        # 델타 이탈 시 조정
        greeks = self.calculate_greeks(position.strikes, position.chain)
        if abs(greeks["delta"]) > 0.2:
            return {"action": "adjust", "reason": "delta_breach"}
        
        return {"action": "hold"}
```

---

## D2. 뉴스 기반 트레이딩

### 시나리오: 실시간 뉴스 분석 → 트레이딩 시그널

```python
class NewsBasedTrading:
    """뉴스 기반 트레이딩 시스템"""
    
    def __init__(self):
        self.news_stream = NaverNewsStream()
        self.sentiment_model = load_model("./finance_sentiment_ko")
        self.entity_extractor = FinanceNER()
        self.position_manager = PositionManager()
        
    async def process_news(self, news: NewsArticle):
        # 1. 관련 종목 추출
        entities = self.entity_extractor.extract(news.content)
        stocks = [e for e in entities if e.type == "STOCK"]
        
        if not stocks:
            return
        
        # 2. 감성 분석
        sentiment = self.sentiment_model.predict(news.content)
        
        # 3. 뉴스 중요도 판단
        importance = self.calculate_importance(news)
        
        # 4. 시그널 생성
        for stock in stocks:
            signal = self.generate_signal(stock, sentiment, importance)
            
            if signal.strength >= 0.7:
                await self.execute_signal(stock, signal)
    
    def calculate_importance(self, news: NewsArticle):
        """뉴스 중요도 계산"""
        factors = {
            "source_credibility": self.get_source_score(news.source),
            "breaking": 1.5 if "속보" in news.title else 1.0,
            "market_hours": 1.2 if self.is_market_hours() else 0.8,
            "first_report": 1.3 if not self.is_duplicate(news) else 0.5
        }
        
        return sum(factors.values()) / len(factors)
    
    def generate_signal(self, stock, sentiment, importance):
        # 긍정 뉴스 + 높은 중요도 = 매수
        if sentiment.label == "positive" and importance > 0.8:
            return Signal(
                direction="buy",
                strength=sentiment.confidence * importance,
                holding_period="short"  # 단기
            )
        
        # 부정 뉴스 = 매도/공매도
        if sentiment.label == "negative" and importance > 0.8:
            return Signal(
                direction="sell",
                strength=sentiment.confidence * importance,
                holding_period="short"
            )
        
        return Signal(direction="hold", strength=0)
```

---

## D3. 포트폴리오 최적화

### 시나리오: AI 기반 자산 배분

```python
class PortfolioOptimizer:
    """AI 기반 포트폴리오 최적화"""
    
    def __init__(self):
        self.return_predictor = ReturnPredictionModel()
        self.risk_model = RiskModel()
        
    def optimize(self, assets: List[str], constraints: dict):
        # 1. 수익률 예측
        expected_returns = self.return_predictor.predict(assets)
        
        # 2. 공분산 행렬 추정
        cov_matrix = self.risk_model.estimate_covariance(assets)
        
        # 3. 최적화 (Mean-Variance + Constraints)
        from scipy.optimize import minimize
        
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Sharpe Ratio 최대화
            return -portfolio_return / portfolio_risk
        
        # 제약조건
        cons = [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # 합 = 1
        ]
        
        # 자산별 비중 제한
        bounds = [(constraints.get("min_weight", 0), 
                   constraints.get("max_weight", 0.3)) for _ in assets]
        
        result = minimize(
            objective,
            x0=np.ones(len(assets)) / len(assets),
            method="SLSQP",
            bounds=bounds,
            constraints=cons
        )
        
        return {
            "weights": dict(zip(assets, result.x)),
            "expected_return": np.dot(result.x, expected_returns),
            "expected_risk": np.sqrt(np.dot(result.x.T, np.dot(cov_matrix, result.x))),
            "sharpe_ratio": -result.fun
        }
```

---

# Part E: DevOps & 인프라

## E1. MLOps 파이프라인

### 시나리오: 자동화된 모델 학습-평가-배포

**사용 스킬**: `13`, `11`, `12`

```yaml
# .github/workflows/mlops.yml
name: MLOps Pipeline

on:
  push:
    paths:
      - 'training/**'
      - 'data/**'

jobs:
  train:
    runs-on: [self-hosted, gpu]
    steps:
      - uses: actions/checkout@v4
      
      - name: Train Model
        run: |
          python training/train.py \
            --config training/config.yaml \
            --output models/
        env:
          WANDB_API_KEY: ${{ secrets.WANDB_KEY }}
      
      - name: Evaluate
        run: |
          python evaluation/evaluate.py \
            --model models/latest \
            --benchmarks mmlu,hellaswag
      
      - name: Check Performance
        run: |
          python scripts/check_metrics.py \
            --threshold 0.75 \
            --metric accuracy
      
      - name: Build Container
        if: success()
        run: |
          docker build -t llm-service:${{ github.sha }} .
          docker push registry/llm-service:${{ github.sha }}
      
      - name: Deploy to Staging
        if: success()
        run: |
          kubectl set image deployment/llm-staging \
            llm=registry/llm-service:${{ github.sha }}
      
      - name: Run E2E Tests
        run: |
          pytest tests/e2e/ --staging-url $STAGING_URL
      
      - name: Deploy to Production
        if: github.ref == 'refs/heads/main'
        run: |
          kubectl set image deployment/llm-prod \
            llm=registry/llm-service:${{ github.sha }}
```

---

## E2. 서버리스 AI 배포

### 시나리오: Modal로 온디맨드 GPU 서빙

**사용 스킬**: `09`, `12`

```python
# 09-infrastructure/modal
import modal

app = modal.App("llm-service")

# GPU 이미지 정의
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("vllm", "torch", "transformers")
    .run_commands("apt-get update && apt-get install -y git")
)

# 모델 볼륨
model_volume = modal.Volume.from_name("llm-models", create_if_missing=True)

@app.cls(
    gpu=modal.gpu.A100(count=2),
    image=image,
    volumes={"/models": model_volume},
    container_idle_timeout=300,  # 5분 유휴 후 종료
    concurrency_limit=10
)
class LLMService:
    @modal.enter()
    def load_model(self):
        from vllm import LLM
        
        self.llm = LLM(
            model="/models/Meta-Llama-3-70B-Instruct-AWQ",
            tensor_parallel_size=2,
            quantization="awq",
            max_model_len=8192
        )
    
    @modal.method()
    def generate(self, prompt: str, max_tokens: int = 1024):
        from vllm import SamplingParams
        
        params = SamplingParams(
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        outputs = self.llm.generate([prompt], params)
        return outputs[0].outputs[0].text

@app.function(schedule=modal.Cron("0 * * * *"))  # 매시간
def warmup():
    """콜드 스타트 방지를 위한 워밍업"""
    service = LLMService()
    service.generate.remote("Hello", max_tokens=10)

# 로컬 테스트
if __name__ == "__main__":
    with app.run():
        service = LLMService()
        result = service.generate.remote("안녕하세요, 자기소개 부탁드립니다.")
        print(result)
```

---

## 부록: 문제 해결 가이드

### GPU 메모리 부족 (OOM)

| 문제 | 해결책 |
|------|--------|
| 학습 시 OOM | `gradient_checkpointing`, `batch_size` 감소 |
| 추론 시 OOM | `quantization` (4-bit), `max_model_len` 감소 |
| vLLM OOM | `gpu_memory_utilization` 조정 (0.9 → 0.8) |

### 느린 추론 속도

| 문제 | 해결책 |
|------|--------|
| 첫 토큰 느림 | KV 캐시 워밍업, 프리필 최적화 |
| 전체 느림 | `tensor_parallel_size` 증가, Flash Attention |
| 배치 비효율 | `continuous_batching` 활성화 |

### 학습 불안정

| 문제 | 해결책 |
|------|--------|
| Loss 발산 | `learning_rate` 감소, `gradient_clipping` |
| Loss 정체 | `learning_rate` 조정, 데이터 품질 확인 |
| 과적합 | `dropout` 증가, 데이터 증강, 조기 종료 |

---

**버전**: 1.0
**최종 수정**: 2025-12-08
**유지관리**: Orchestra Research
