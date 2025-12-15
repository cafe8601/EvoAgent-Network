# Pydantic 모델 최적화 with DSPy

DSPy를 사용하여 Pydantic 모델의 Field Description을 자동 최적화하는 방법.

---

## 개요

LLM에서 구조화된 데이터를 추출할 때, Pydantic Field의 `description`이 추출 정확도에 큰 영향을 미침. DSPy의 최적화 알고리즘을 활용하면 이 description을 자동으로 개선할 수 있음.

**목표**: 수동 튜닝 없이 20-40% 정확도 향상

---

## 방법 1: DSPydantic 라이브러리 (간편)

**GitHub**: https://github.com/davidberenstein1957/dspydantic (40+ stars)

DSPy + Pydantic 통합 래퍼 라이브러리.

### 설치

```bash
pip install dspydantic
```

### 기본 사용법

```python
from pydantic import BaseModel, Field
from dspydantic import PydanticOptimizer, Example, create_optimized_model

# 1. Pydantic 모델 정의
class User(BaseModel):
    name: str = Field(description="User name")
    age: int = Field(description="User age")
    email: str = Field(description="Email address")

# 2. 학습 예제 준비
examples = [
    Example(
        text="John Doe, 30 years old, john@example.com",
        expected_output=User(name="John Doe", age=30, email="john@example.com")
    ),
    Example(
        text="Jane Smith, 25, jane.smith@email.com",
        expected_output=User(name="Jane Smith", age=25, email="jane.smith@email.com")
    ),
]

# 3. 최적화 실행
optimizer = PydanticOptimizer(
    model=User,
    examples=examples,
    evaluate_fn="exact",
    model_id="gpt-4o"
)
result = optimizer.optimize()

# 4. 최적화된 모델 생성
OptimizedUser = create_optimized_model(User, result.optimized_descriptions)

# 5. 최적화된 description 확인
print("Optimized descriptions:")
for field, description in result.optimized_descriptions.items():
    print(f"  {field}: {description}")
```

### 이미지/PDF 입력

```python
# 이미지 입력
Example(
    image_path="document.png",
    expected_output=Invoice(...)
)

# PDF 입력
Example(
    pdf_path="invoice.pdf",
    pdf_dpi=300,
    expected_output=Invoice(...)
)
```

### LLM Judge (Ground Truth 없이 평가)

```python
import dspy

# Ground truth 없이 LLM이 품질 평가
examples = [
    Example(text="John Doe, 30 years old", expected_output=None),
]

judge_lm = dspy.LM("gpt-4o", api_key="...")

optimizer = PydanticOptimizer(
    model=User,
    examples=examples,
    evaluate_fn=judge_lm,  # LLM as judge
    model_id="gpt-4o"
)
```

### Optimizer 선택

```python
# 자동 선택 (데이터셋 크기 기반)
# < 20 예제: BootstrapFewShot
# >= 20 예제: BootstrapFewShotWithRandomSearch

# 수동 선택
optimizer = PydanticOptimizer(
    model=User,
    examples=examples,
    optimizer="miprov2",  # 또는 "gepa", "copro", "simba"
    model_id="gpt-4o"
)
```

---

## 방법 2: DSPy 직접 사용 (유연)

DSPydantic 없이 DSPy의 `TypedPredictor`로 직접 구현.

### 기본 구조

```python
import dspy
from pydantic import BaseModel, Field

# LM 설정
lm = dspy.OpenAI(model="gpt-4o")
dspy.settings.configure(lm=lm)

# Pydantic 모델
class Invoice(BaseModel):
    invoice_number: str = Field(description="Invoice ID")
    total_amount: float = Field(description="Total amount")
    date: str = Field(description="Invoice date")

# DSPy Signature with Pydantic
class ExtractInvoice(dspy.Signature):
    """Extract invoice information from text."""
    text = dspy.InputField()
    invoice: Invoice = dspy.OutputField()

# TypedPredictor 사용
extractor = dspy.TypedPredictor(ExtractInvoice)
result = extractor(text="Invoice INV-2024-001, Total: $1,234.56, Date: 2024-01-15")
print(result.invoice.invoice_number)  # "INV-2024-001"
```

### 최적화 적용

```python
from dspy.teleprompt import BootstrapFewShot

# 학습 데이터
trainset = [
    dspy.Example(
        text="Invoice INV-001, $500.00, 2024-01-01",
        invoice=Invoice(invoice_number="INV-001", total_amount=500.0, date="2024-01-01")
    ).with_inputs("text"),
    # 더 많은 예제...
]

# 평가 함수
def validate_invoice(example, pred, trace=None):
    return (
        example.invoice.invoice_number == pred.invoice.invoice_number and
        example.invoice.total_amount == pred.invoice.total_amount
    )

# 최적화
optimizer = BootstrapFewShot(metric=validate_invoice, max_bootstrapped_demos=3)
optimized_extractor = optimizer.compile(extractor, trainset=trainset)

# 저장/로드
optimized_extractor.save("models/invoice_extractor.json")
```

### Chain of Thought + Pydantic

```python
class ReasonedExtraction(dspy.Signature):
    """Extract invoice with reasoning."""
    text = dspy.InputField()
    invoice: Invoice = dspy.OutputField()

# ChainOfThought로 추론 과정 추가
cot_extractor = dspy.ChainOfThought(ReasonedExtraction)
result = cot_extractor(text="...")
print(result.rationale)  # 추론 과정
print(result.invoice)    # 추출 결과
```

---

## 방법 3: Instructor + DSPy 조합 (고급)

Instructor로 추출, DSPy로 최적화.

```python
import instructor
import dspy
from openai import OpenAI
from pydantic import BaseModel, Field

# Instructor 클라이언트
client = instructor.from_openai(OpenAI())

class User(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")

# Instructor로 추출 함수 정의
def extract_user(text: str, description_override: dict = None) -> User:
    model = User
    if description_override:
        # 동적으로 description 수정
        model = create_model_with_descriptions(User, description_override)

    return client.chat.completions.create(
        model="gpt-4o",
        response_model=model,
        messages=[{"role": "user", "content": f"Extract: {text}"}]
    )

# DSPy로 최적화할 description 탐색
# (BootstrapFewShot 또는 MIPRO 사용)
```

---

## 비교: 어떤 방법을 선택할까?

| 방법 | 장점 | 단점 | 적합한 경우 |
|------|------|------|------------|
| **DSPydantic** | 간편, 올인원 | 초기 라이브러리, 기능 제한 | 빠른 프로토타이핑 |
| **DSPy 직접** | 유연, 커스터마이징 | 설정 복잡 | 복잡한 파이프라인 |
| **Instructor+DSPy** | 최고 품질 | 구현 복잡 | 프로덕션 시스템 |

### 권장 흐름

```
1. 프로토타입 → DSPydantic으로 빠르게 테스트
2. 검증 후 → DSPy TypedPredictor로 직접 구현
3. 프로덕션 → Instructor 통합으로 안정화
```

---

## 실전 예제: 영수증 데이터 추출

### 모델 정의

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    KRW = "KRW"

class LineItem(BaseModel):
    description: str = Field(description="Item description")
    quantity: int = Field(description="Quantity purchased", ge=1)
    unit_price: float = Field(description="Price per unit")

class Receipt(BaseModel):
    store_name: str = Field(description="Name of the store")
    date: str = Field(description="Purchase date in YYYY-MM-DD format")
    items: list[LineItem] = Field(description="List of purchased items")
    subtotal: float = Field(description="Subtotal before tax")
    tax: float = Field(description="Tax amount")
    total: float = Field(description="Total amount paid")
    currency: Currency = Field(description="Currency code")
    payment_method: Optional[str] = Field(default=None, description="Payment method used")
```

### DSPydantic으로 최적화

```python
from dspydantic import PydanticOptimizer, Example, create_optimized_model

examples = [
    Example(
        text="""
        WALMART
        Date: 2024-01-15

        Apple (3) @ $1.50 each = $4.50
        Milk (2) @ $3.00 each = $6.00

        Subtotal: $10.50
        Tax: $0.84
        Total: $11.34

        Paid with Credit Card
        """,
        expected_output=Receipt(
            store_name="WALMART",
            date="2024-01-15",
            items=[
                LineItem(description="Apple", quantity=3, unit_price=1.50),
                LineItem(description="Milk", quantity=2, unit_price=3.00),
            ],
            subtotal=10.50,
            tax=0.84,
            total=11.34,
            currency=Currency.USD,
            payment_method="Credit Card"
        )
    ),
    # 더 많은 예제 추가...
]

optimizer = PydanticOptimizer(
    model=Receipt,
    examples=examples,
    evaluate_fn="exact",
    model_id="gpt-4o",
    verbose=True
)

result = optimizer.optimize()

# 최적화된 모델 생성
OptimizedReceipt = create_optimized_model(Receipt, result.optimized_descriptions)

# OpenAI Structured Outputs와 함께 사용
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": result.optimized_system_prompt or "Extract receipt data."},
        {"role": "user", "content": receipt_text}
    ],
    response_format=OptimizedReceipt
)

receipt = OptimizedReceipt.model_validate_json(response.choices[0].message.content)
```

---

## 성능 팁

### 1. 다양한 예제 제공

```python
# 다양한 포맷과 엣지 케이스 포함
examples = [
    Example(text="정상 케이스", ...),
    Example(text="누락된 필드", ...),
    Example(text="이상한 포맷", ...),
    Example(text="다국어 입력", ...),
]
```

### 2. 적절한 Optimizer 선택

```python
# 예제 수에 따른 권장 optimizer
# 5-10개: BootstrapFewShot
# 10-50개: BootstrapFewShotWithRandomSearch
# 50개+: MIPROv2
```

### 3. 검증 함수 신중하게 작성

```python
def validate_receipt(example, pred, trace=None):
    # 핵심 필드만 검증 (모든 필드 exact match 피함)
    return (
        abs(example.receipt.total - pred.receipt.total) < 0.01 and
        example.receipt.store_name.lower() == pred.receipt.store_name.lower()
    )
```

### 4. 최적화 결과 저장

```python
# 최적화된 description을 파일로 저장
import json

with open("optimized_descriptions.json", "w") as f:
    json.dump(result.optimized_descriptions, f, indent=2)

# 나중에 로드
with open("optimized_descriptions.json") as f:
    descriptions = json.load(f)

OptimizedModel = create_optimized_model(OriginalModel, descriptions)
```

---

## 참고 자료

- **DSPydantic**: https://github.com/davidberenstein1957/dspydantic
- **DSPy TypedPredictor**: https://dspy.ai/learn/typed_predictors
- **Instructor**: https://python.useinstructor.com
- **PyTorch KR 소개글**: https://discuss.pytorch.kr/t/dspydantic-dspy-pydantic/8388
