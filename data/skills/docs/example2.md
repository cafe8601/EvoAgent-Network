# AI Research Skills 확장 예시 북 2 (Creative Cookbook)

> 창의적이고 고도화된 AI 응용 시나리오 및 구현 가이드

---

## 📚 목차

### Part F: 창의적 멀티모달 응용
- [F1. AI 딥다이브 팟캐스트 생성기](#f1-ai-딥다이브-팟캐스트-생성기)
- [F2. UX/UI 자동 진단 및 개선 에이전트](#f2-uxui-자동-진단-및-개선-에이전트)

### Part G: 하이퍼 오토메이션 (Hyper-Automation)
- [G1. "The Midnight Coder" 자율 리팩토링](#g1-the-midnight-coder-자율-리팩토링)
- [G2. 실시간 위기 대응 상황실](#g2-실시간-위기-대응-상황실)

### Part H: 데이터 사이언스 & 분석 심화
- [H1. 인과 추론 (Causal Inference) 마케팅 분석기](#h1-인과-추론-마케팅-분석기)
- [H2. "Auto-Kaggle" 모델링 파이프라인](#h2-auto-kaggle-모델링-파이프라인)

### Part I: 틈새 도메인 특화
- [I1. 특허 침해 가능성 분석기](#i1-특허-침해-가능성-분석기)
- [I2. 개인화된 "Second Brain" 지식 그래프](#i2-개인화된-second-brain-지식-그래프)

---

# Part F: 창의적 멀티모달 응용

## F1. AI 딥다이브 팟캐스트 생성기

### 시나리오: "논문 읽어주는 두 친구"

**목표**: 기술 논문(PDF)이나 복잡한 문서를 입력하면, 두 명의 AI 호스트(진행자 & 전문가)가 쉽고 재미있게 대화하는 10분 분량의 오디오 콘텐츠 생성. (Google NotebookLM 스타일)

**사용 스킬**: `18-multimodal`, `16-prompt-engineering`, `14-agents`

#### 구현 파이프라인

1.  **PDF 파싱**: 논문 텍스트 및 구조 추출
2.  **대본 작성 (Script Writer)**: 두 페르소나의 대화 생성 (유머, 비유 포함)
3.  **음성 합성 (TTS)**: 각 화자별 다른 목소리로 오디오 생성
4.  **오디오 믹싱**: 배경음악 및 효과음 삽입

```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
# 가상 TTS 라이브러리 (OpenAI TTS or ElevenLabs)
from tts_provider import generate_speech, mix_audio

class PodcastProducer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        
    async def produce_episode(self, pdf_path: str, output_file: str):
        # 1. 문서 분석
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        content = "\n".join([d.page_content for d in docs[:5]]) # 앞부분만 예시
        
        # 2. 대본 생성 (페르소나 정의 중요)
        script = await self.generate_script(content)
        
        # 3. 음성 합성 (병렬 처리)
        audio_segments = []
        for line in script:
            voice_id = "alloy" if line["speaker"] == "Host" else "onyx"
            audio = await generate_speech(
                text=line["text"], 
                voice=voice_id,
                emotion=line.get("emotion", "neutral")
            )
            audio_segments.append(audio)
            
        # 4. 믹싱 (Intro/Outro BGM 추가)
        final_audio = mix_audio(
            segments=audio_segments,
            bgm="lofi_beat.mp3",
            bgm_volume=0.1
        )
        final_audio.export(output_file, format="mp3")
        
    async def generate_script(self, content: str):
        """DSPy 스타일 프롬프팅으로 자연스러운 대화 생성"""
        prompt = f"""
        당신은 인기 테크 팟캐스트의 PD입니다. 
        주어진 기술 문서를 바탕으로 두 진행자(Alex, Jamie)의 대본을 작성하세요.
        
        [페르소나]
        - **Alex (진행자)**: 호기심 많고 에너지가 넘침. 질문을 던지고 청취자의 눈높이에서 비유를 사용함.
        - **Jamie (전문가)**: 차분하고 지적임. 핵심 원리를 명쾌하게 설명하고 깊이 있는 통찰을 제공함.
        
        [규칙]
        1. "안녕하세요" 같은 뻔한 인사는 생략하고 바로 본론의 흥미로운 점으로 시작할 것.
        2. 중간에 가벼운 농담이나 감탄사("와, 진짜요?", "잠깐만요!")를 넣어 자연스럽게 만들 것.
        3. 문어체가 아닌 구어체를 사용할 것.
        4. JSON 형식으로 출력할 것: {{"speaker": "Alex", "text": "...", "emotion": "excited"}}
        
        문서 내용: {content[:3000]}...
        """
        # (구현 생략: LLM 호출 및 JSON 파싱)
        return parsed_script_json
```

---

## F2. UX/UI 자동 진단 및 개선 에이전트

### 시나리오: "디자인 닥터"

**목표**: 웹사이트 URL이나 스크린샷을 입력하면, 사용성 문제(Usability)와 시각적 결함(Visual Glitch)을 진단하고, 개선된 CSS/React 코드를 제안.

**사용 스킬**: `18-multimodal` (Vision), `23-frontend-design-architect`

#### 구현

```python
from langchain_core.messages import HumanMessage
import base64

class DesignDoctor:
    def __init__(self):
        self.vision_model = ChatOpenAI(model="gpt-4o", max_tokens=2048)
        
    async def diagnose(self, image_path: str):
        # 이미지 인코딩
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
            
        # 비전 모델 분석
        msg = HumanMessage(content=[
            {"type": "text", "text": """
            당신은 시니어 UX/UI 디자이너입니다. 이 웹사이트 스크린샷을 분석하고 다음을 수행하세요:
            
            1. **휴리스틱 평가**: 닐슨의 10가지 휴리스틱 원칙에 위배되는 점 찾기 (예: 가시성 부족, 일관성 결여).
            2. **시각적 계층 구조**: 타이포그래피, 대비, 여백이 정보 전달에 효과적인지 분석.
            3. **접근성(a11y)**: 색상 대비가 충분한지, 터치 타겟이 적절한지 추정.
            4. **개선 제안**: Tailwind CSS를 사용한 구체적인 개선 코드 제안.
            """},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        
        response = await self.vision_model.ainvoke([msg])
        return response.content

    def generate_report(self, diagnosis: str):
        # 분석 결과를 마크다운 리포트로 변환
        # 개선 전/후 비교 코드 블록 강조
        pass
```

---

# Part G: 하이퍼 오토메이션 (Hyper-Automation)

## G1. "The Midnight Coder" 자율 리팩토링

### 시나리오: 밤샘 자율 리팩토링

**목표**: 개발자가 퇴근한 후(Midnight), CI 파이프라인이 실행되어 레거시 코드(Python 2.7 스타일, 비효율적 Pandas 등)를 탐지하고, 모던 Python(Type Hinting, Pydantic)으로 변환하여 PR을 올리는 시스템.

**사용 스킬**: `14-agents`, `07-safety-alignment`, `Github API`

#### 아키텍처

```
[Cron Job: 02:00 AM]
      ↓
[Code Scanner] → (Static Analysis: SonarQube/Ruff)
      ↓
[Refactoring Agent] ←→ [Unit Test Runner]
      ↓                 (수정 후 테스트 통과 필수)
[PR Creator] → "refactor/auto-fix-metadata" 브랜치 생성
```

#### 에이전트 루프 구현

```python
class RefactoringAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        
    async def refactor_file(self, file_path: str, issues: list):
        original_code = read_file(file_path)
        
        # 1. 리팩토링 제안
        prompt = f"""
        다음 Python 코드를 최신 표준으로 리팩토링하세요.
        이슈: {issues}
        
        [요구사항]
        - Type Hinting 추가
        - Docstring (Google Style) 추가
        - Pydantic BaseModel 사용하여 데이터 구조화
        - 비효율적인 루프를 List Comprehension 또는 Vectorization으로 변경
        """
        
        new_code = await self.llm.invoke(prompt)
        
        # 2. 검증 (Self-Correction Loop)
        for attempt in range(3):
            write_file(file_path, new_code)
            
            # 테스트 실행
            test_result = run_pytest(file_path)
            
            if test_result.passed:
                return new_code
            
            # 실패 시 수정
            new_code = await self.fix_code(
                original_code, new_code, test_result.error_log
            )
            
        # 3회 실패 시 롤백
        write_file(file_path, original_code)
        return None
```

## G2. 실시간 위기 대응 상황실

### 시나리오: 브랜드 평판 방어 시스템

**목표**: 트위터, 커뮤니티, 뉴스를 실시간 모니터링하다가 브랜드에 대한 부정적 여론이 급증하면(Viral Spike), 원인을 분석하고 공식 입장문 초안과 대응 시나리오를 경영진에게 Push 알림으로 전송.

**사용 스킬**: `20-trading` (시계열 이상탐지 응용), `21-multiagent`

#### 워크플로우

1.  **Monitor Agent**: 키워드 언급량 및 감성지수 실시간 추적 (Trading의 RSI/볼린저 밴드 지표 응용).
2.  **Alert Trigger**: 감성지수가 -2.0 SD(표준편차) 급락 시 "위기" 경보 발령.
3.  **Analyst Agent**: 급락 원인이 된 상위 게시글 크롤링 및 팩트 체크.
4.  **PR Agent**: 위기 유형(제품 결함, 임원 리스크, 오보 등)에 따른 사과문/해명문 초안 작성.
5.  **Notification**: Slack으로 "🚨 위기 감지 리포트" 발송.

```python
class CrisisWarRoom:
    async def monitor_stream(self):
        # 실시간 데이터 스트림 (Kafka 등)
        async for data in self.social_stream:
            metrics = self.calculate_sentiment_metrics(data)
            
            # 이상 탐지 (Z-score)
            if metrics['z_score'] < -3.0:
                await self.activate_protocol(data, metrics)
    
    async def activate_protocol(self, trigger_data, metrics):
        # 원인 분석
        top_posts = await self.analyst.find_viral_posts(hours=1)
        root_cause = await self.analyst.summarize_issue(top_posts)
        
        # 대응 전략 수립
        strategy = await self.pr_agent.draft_strategy(
            issue=root_cause,
            severity="CRITICAL"
        )
        
        # 슬랙 알림 전송
        await self.notifier.send_alert(
            title="🔴 브랜드 위기 경보 발령",
            fields=[
                {"title": "급락 지수", "value": f"{metrics['z_score']:.2f} sigma"},
                {"title": "핵심 이슈", "value": root_cause},
                {"title": "제안 대응", "value": strategy['action_plan']},
                {"title": "입장문 초안", "value": strategy['draft_text']}
            ]
        )
```

---

# Part H: 데이터 사이언스 & 분석 심화

## H1. 인과 추론 마케팅 분석기

### 시나리오: "상관관계는 인과관계가 아니다"

**목표**: 단순히 "광고비가 늘어서 매출이 올랐다"가 아니라, "광고비를 100만원 늘렸을 때, 외부 요인(계절성, 경쟁사 가격)을 통제하고 순수하게 매출이 얼마나 오르는가(Causal Lift)"를 분석.

**사용 스킬**: `DoWhy`, `CausalML`, `21-multiagent`

#### 에이전트 구성

1.  **Graph Agent**: 도메인 지식을 바탕으로 인과 그래프(Causal Graph) 초안 생성 (ex: 가격 → 구매, 날씨 → 구매).
2.  **Estimation Agent**: Double Machine Learning 등으로 인과 효과(ATE) 추정.
3.  **Refutation Agent**: 추정된 인과 효과가 통계적으로 유의미한지 반박(Refutation) 테스트 수행.

```python
# 가상의 Causal Library 사용
import dowhy
from dowhy import CausalModel

class CausalAnalyst:
    def analyze_marketing_roi(self, df):
        # 1. 인과 그래프 정의 (LLM 도움)
        causal_graph = """
        digraph {
            Ads -> Sales;
            Seasonality -> Sales;
            Seasonality -> Ads;
            CompetitorPrice -> Sales;
        }
        """
        
        # 2. 모델링
        model = CausalModel(
            data=df,
            treatment='Ads',
            outcome='Sales',
            graph=causal_graph
        )
        
        # 3. 식별 (Identification)
        identified_estimand = model.identify_effect()
        
        # 4. 추정 (Estimation)
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.linear_regression"
        )
        
        # 5. 검증 (Refutation) - 중요!
        refute = model.refute_estimate(
            identified_estimand,
            estimate,
            method_name="random_common_cause"
        )
        
        return {
            "causal_effect": estimate.value, # 순수 광고 효과
            "robustness": refute.is_robust
        }
```

## H2. "Auto-Kaggle" 모델링 파이프라인

### 시나리오: 데이터셋만 던져주면 베이스라인 정복

**목표**: `train.csv`, `test.csv`만 입력하면 EDA부터 전처리, 피처 엔지니어링, 복수의 모델 학습(LGBM, XGBoost, CatBoost), 앙상블, 그리고 결과 제출 파일까지 생성.

**사용 스킬**: `13-mlops`, `05-data-processing`, `Optuna`

#### 구현

```python
class AutoKaggler:
    def __init__(self, target_col):
        self.target = target_col
        
    def run_pipeline(self, train_path, test_path):
        # 1. 자동 EDA 및 타입 추론
        df_train = pd.read_csv(train_path)
        col_types = self.infer_column_types(df_train)
        
        # 2. LLM 기반 피처 아이디어 생성
        feature_ideas = self.brain.brainstorm_features(df_train.columns)
        # ex: "TransactionDate에서 '주말 여부', '공휴일 여부' 파생 변수 생성 추천"
        
        # 3. 전처리 및 피처 생성 코드 실행
        X_train, y_train = self.preprocessor.transform(df_train, feature_ideas)
        
        # 4. 모델 선택 및 HPO (Optuna)
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: self.objective(trial, X_train, y_train), n_trials=50)
        
        # 5. Stacking Ensemble
        best_models = self.get_top_k_models(study, k=3)
        stacker = StackingClassifier(estimators=best_models, final_estimator=LogisticRegression())
        stacker.fit(X_train, y_train)
        
        # 6. 리포트 생성
        return TrainingReport(
            cv_score=stacker.score,
            feature_importance=stacker.feature_importances_,
            submission_file="submission.csv"
        )
```

---

# Part I: 틈새 도메인 특화

## I1. 특허 침해 가능성 분석기

### 시나리오: 기술(Tech) + 법률(Legal) 하이브리드

**목표**: 개발 중인 제품의 기술 명세서(Spec)와 경쟁사의 특허 문서를 비교하여 침해 가능성(Risk Score)을 산출하고 회피 설계(Design-around) 방안 제안.

**사용 스킬**: `15-rag` (특허 DB), `03-fine-tuning` (법률 용어 학습), `21-multiagent`

#### 프로세스

1.  **Claim Parser**: 특허의 권리 범위인 '청구항(Claims)'을 구성요소별로 분해 (Element-by-element analysis).
2.  **Product Mapper**: 우리 제품의 기능을 청구항 구성요소와 매핑.
3.  **Risk Scorer**: 각 구성요소의 일치 여부(All-elements rule) 판단. 하나라도 불일치하면 비침해.
4.  **Advisor**: 침해 소지가 있는 구성요소를 대체할 기술적 대안 제안.

```python
class PatentRiskAnalyzer:
    async def check_infringement(self, product_spec: str, patent_id: str):
        # 특허 청구항 로드
        claims = await self.patent_db.get_claims(patent_id)
        
        # 구성요소 분해 (LLM)
        elements = await self.llm.invoke(f"다음 청구항을 독립된 구성요소로 분해해:\n{claims}")
        
        report = []
        infringement_flag = True
        
        for element in elements:
            # 구성요소 매칭
            match = await self.compare(element, product_spec)
            report.append(match)
            
            if match.status == "NOT_FOUND":
                infringement_flag = False # 구성요소 완비 원칙에 의해 비침해
        
        if infringement_flag:
            return {
                "risk": "HIGH", 
                "advice": await self.suggest_workaround(report)
            }
        else:
            return {"risk": "LOW"}
```

## I2. 개인화된 "Second Brain" 지식 그래프

### 시나리오: 로컬 지식 관리 시스템 (Obsidian/Notion 연동)

**목표**: 사용자의 메모, 북마크, 일기를 벡터화하여 저장만 하는 것이 아니라, **지식 그래프(Knowledge Graph)**로 연결하여 "이 아이디어는 작년의 저 생각과 연결됩니다"라고 제안.

**사용 스킬**: `15-rag`, `NetworkX` (그래프), `Local LLM` (프라이버시)

```python
class SecondBrain:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.vectordb = Chroma()
        
    def add_note(self, note: Note):
        # 1. 키워드 및 엔티티 추출
        entities = self.extract_entities(note.content)
        
        # 2. 벡터 임베딩 저장
        self.vectordb.add(note)
        
        # 3. 그래프 노드/엣지 생성
        self.graph.add_node(note.id, type="Note")
        for entity in entities:
             self.graph.add_node(entity, type="Concept")
             self.graph.add_edge(note.id, entity, relation="mentions")
             
        # 4. 연결 발견 (Serendipity)
        related_notes = self.find_hidden_connections(note.id)
        return related_notes
    
    def find_hidden_connections(self, note_id):
        # 그래프 탐색: 2-hop neighbor 중 관련성 높은 것 추천
        # A(새 메모) -> Concept X -> B(과거 메모)
        pass
```

---

**버전**: 1.0
**최종 수정**: 2025-12-08
**유지관리**: Orchestra Research
