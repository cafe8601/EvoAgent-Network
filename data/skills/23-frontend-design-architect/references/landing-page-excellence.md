# Landing Page Excellence: AI가 구축하지 않은 것처럼 보이게

## Overview

이 참조 문서는 **AI가 생성한 것처럼 보이지 않는** 고전환 프리미엄 랜딩 페이지를 구축하기 위한 완전한 가이드입니다. 전환율 최적화와 브랜드 기억력을 동시에 달성합니다.

**핵심 목표:**
1. 프리미엄하고 전문적으로 디자인된 것처럼 보이게 (AI 생성이 아닌)
2. 방문자를 고객으로 전환 (검증된 심리학 사용)
3. 일반 템플릿에서 벗어나기 (의도적이고 정교한 디자인)
4. 인간이 만든 느낌 (세심한 디테일과 절제)

---

## Part 1: AI 디자인의 10가지 치명적 신호 (Dead Giveaways)

### 1. The Gradient Epidemic (그라디언트 남용)

**AI가 하는 것:**
- 모든 곳에 그라디언트 배경
- 한 페이지에 여러 개의 경쟁하는 그라디언트
- 밝고 채도 높은 그라디언트 메시
- 보라색-파란색 그라디언트 (AI의 최애)

**프리미엄 디자인이 하는 것:**
- 솔리드 색상 또는 미세한 단일 그라디언트를 액센트로만
- 모노크롬 배경 (off-white, light gray)
- hero에 하나의 미세한 그라디언트, 있다면
- 백드롭 블러와 투명 오버레이 선호

**수정 방법:**
```css
/* ❌ 회피 */
.ai-style { background: linear-gradient(to-br, purple-500, pink-500, orange-500); }

/* ✅ 사용 */
.premium-style { background-color: #FAFAF9; } /* stone-50 */
.premium-subtle { background: linear-gradient(to-br, #EFF6FF, #EEF2FF); } /* 매우 미세 */
```

### 2. The Everything-Centered Syndrome (모두 가운데 정렬)

**AI가 하는 것:**
- 모든 섹션 가운데 정렬
- 모든 텍스트 가운데 정렬
- 가운데에 떠 있는 CTA
- 전체적으로 대칭 레이아웃

**프리미엄 디자인이 하는 것:**
- 비대칭 hero (60/40 분할)
- 좌측 정렬 텍스트 블록
- 오른쪽 정렬 이미지 오프셋
- 가운데 정렬은 전략적으로 드물게 사용

```tsx
// ❌ 회피
<div className="text-center mx-auto">모든 것 가운데</div>

// ✅ 사용
<div className="grid lg:grid-cols-2 gap-12">
  <div className="text-left">좌측 정렬 콘텐츠</div>
  <div className="lg:pl-8">오른쪽 시각 요소</div>
</div>
```

### 3. The Rainbow Catastrophe (레인보우 색상)

**AI가 하는 것:**
- 각 섹션마다 다른 밝은 색상
- 한 페이지에 파랑, 보라, 초록, 주황, 분홍 모두
- 각 카드가 다른 색상
- "다채로움" = "전문적" (틀림)

**프리미엄 디자인이 하는 것:**
- 1 브랜드 색상 + 1 액센트 색상 최대
- 80% 중립색 (회색, off-white)
- CTA에만 전략적 색상 포인트
- 모노크롬 정교함

```css
/* ❌ 회피 */
.section-1 { background: blue-500; }
.section-2 { background: purple-500; }
.section-3 { background: green-500; }

/* ✅ 사용 */
.section-1 { background: white; }
.section-2 { background: #F8FAFC; } /* slate-50 */
.section-3 { background: #0F172A; } /* slate-900, 대비용 */
/* CTA만 채도 높은 색상 */
```

### 4. The Stock Photo Disaster (스톡 사진)

**AI가 하는 것:**
- 사무실에서 하이파이브하는 다양한 팀
- 노트북을 가리키며 웃는 사람
- 회사 악수 사진
- 명백히 연출된 "캔디드" 샷

**프리미엄 디자인이 하는 것:**
- 실제 제품 스크린샷
- 실제 고객 사진 (해당되는 경우)
- 커스텀 일러스트 또는 추상 도형
- 고품질, 진정성 있는 사진
- 또는 사진 없이 훌륭한 타이포그래피만

### 5. The Feature-Dumping Problem (기능 나열)

**AI가 하는 것:**
- 20개+ 기능을 그리드에 나열
- 각 기능 = 아이콘 + 제목 + 단락
- 모든 것이 동일한 강조
- 명확한 계층이나 흐름 없음

**프리미엄 디자인이 하는 것:**
- 3-6개 핵심 기능 최대
- 주요 기능에 더 많은 공간
- 기능이 아닌 혜택
- 명확한 시각적 계층

```tsx
// ❌ 회피: 20개 작은 기능 카드의 4x5 그리드
// ✅ 사용: 실제 혜택이 있는 3개 대형 기능 블록
// 또는: 1개 메인 기능 + 4개 지원 기능 (비대칭 그리드)
```

### 6. The Pill Button Plague (pill 버튼)

**AI가 하는 것:**
- 모든 버튼: `rounded-full` (pill 모양)
- 경쟁하는 여러 pill 버튼
- 그라디언트 pill 버튼
- 모든 곳에 떠 있는 pill 버튼

**프리미엄 디자인이 하는 것:**
- `rounded-lg` (8-12px) 최대
- 미세한 라운딩의 직사각형
- 전체적으로 일관된 버튼 스타일
- 전략적 버튼 배치

```tsx
// ❌ 회피
<button className="rounded-full px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500">

// ✅ 사용
<button className="rounded-lg px-6 py-3 bg-blue-600 hover:bg-blue-700">
```

### 7. The Busy Background Nightmare (바쁜 배경)

**AI가 하는 것:**
- 모든 곳에 기하학적 패턴
- 날아다니는 애니메이션 도형
- 콘텐츠와 경쟁하는 그리드 패턴
- 배경으로 그라디언트 메시

**프리미엄 디자인이 하는 것:**
- 깨끗하고 미니멀한 배경
- 미세한 그리드 또는 도트 패턴 (있다면)
- 단일 액센트 도형 (전략적 위치)
- 디자인 요소로서 여백

### 8. The Typography Chaos (타이포 혼란)

**AI가 하는 것:**
- 3개+ 다른 폰트
- 일관성 없는 크기
- 모든 곳에 대문자
- 가운데 정렬 단락 (읽기 어려움)
- 작은 본문 텍스트 (14px 이하)

**프리미엄 디자인이 하는 것:**
- 1-2개 폰트 최대
- 명확한 크기 계층
- 문장형 대소문자 (대문자 아님)
- 좌측 정렬 본문 텍스트
- 18-20px 본문 텍스트 (읽기 쉬움)

### 9. The CTA Apocalypse (CTA 과다)

**AI가 하는 것:**
- 스크롤 전에 5개+ CTA
- 각 CTA마다 다른 색상
- "Learn More"가 primary CTA
- 모호한 카피의 CTA

**프리미엄 디자인이 하는 것:**
- 1 primary + 1 secondary CTA 최대
- 페이지 전체에 동일한 primary CTA
- CTA 카피에 구체적 행동
- 명확한 시각적 계층

### 10. The Shadow Overload (그림자 과다)

**AI가 하는 것:**
- 모든 곳에 heavy drop shadow
- 여러 그림자 방향
- 네온 글로우 그림자
- 과도한 그림자로 떠 있는 카드

**프리미엄 디자인이 하는 것:**
- 미세한 그림자 (shadow-sm, shadow-md)
- 일관된 그림자 방향
- 최소한의 그림자, 전략적 사용
- 종종 그림자 없이 테두리만

---

## Part 2: 프리미엄 디자인 원칙

### 2.1 8pt 그리드 스페이싱

```
Base unit: 8px
All spacing: 8, 16, 24, 32, 40, 48, 64, 80, 96, 128px
Section padding: 최소 80-128px 수직
Element spacing: 24-48px 주요 요소 사이
Micro-spacing: 8-16px 관련 항목
```

**Tailwind 클래스:**
```
p-2 (8px), p-4 (16px), p-6 (24px), p-8 (32px)
p-10 (40px), p-12 (48px), p-16 (64px), p-20 (80px)
p-24 (96px), p-32 (128px)
```

### 2.2 타이포그래피 계층

**크기 (Desktop):**
| 요소 | 크기 | 예시 |
|------|------|------|
| Hero Headline | 64-80px | text-7xl ~ text-8xl |
| Section Titles | 48-56px | text-5xl ~ text-6xl |
| Subsection Titles | 32-40px | text-4xl ~ text-5xl |
| Body | 18-20px | text-lg ~ text-xl |
| Small Text | 14-16px | text-sm ~ text-base |

**폰트 페어링:**
```
1. 대비 페어: 굵은 Display 폰트 + 우아한 Serif Body
2. 모던 프로: 전체 Sans-serif with weight 대비
3. 에디토리얼: Serif Display + Sans Body
```

**규칙:**
- Line height: 헤드라인 1.2, 본문 1.6-1.7
- Letter spacing: 대형 헤드라인에 -0.02em ~ -0.04em
- 단락 최대 너비: 65-75자 (약 700px)
- 절대 2개 초과 폰트 패밀리 사용 금지

### 2.3 색상 전략

**프리미엄 팔레트 공식:**
```
Background: stone-50 (#FAFAF9) 또는 slate-50 (#F8FAFC)
Text Primary: slate-900 (#0F172A) 또는 zinc-900
Text Secondary: slate-600 (#475569)
Primary Brand: 단일 브랜드 색상
CTA: 고대비 보색 (브랜드가 파란색이면 amber/orange 사용)
Borders: slate-200 (#E2E8F0)
```

**피해야 할 것:**
- 순백색 (#FFFFFF) - warm off-white 사용
- 순흑색 (#000000) - slate-900 사용
- 밝고 채도 높은 레인보우 팔레트
- 모든 곳에 그라디언트

### 2.4 비대칭과 시각적 관심

```
- 텍스트 블록: 60% 너비, 좌측 또는 우측 배치
- 이미지: 가운데에서 오프셋, 컨테이너 밖으로 확장
- 그리드 레이아웃: 2컬럼 with 하나가 더 넓음 (60/40 또는 70/30)
- 카드 크기: 시각적 관심을 위해 크기 다양화
```

---

## Part 3: 전환 심리학

### 3.1 AIDA 프레임워크

**Attention (Hero 섹션):**
- 헤드라인: 제품이 아닌 변환을 명시
- 공식: "[원하는 결과] Without [공통 고충]"
- 예: "Scale Your Agency to $50K/month Without Hiring More People"

**Interest (문제/솔루션):**
- 고충을 자극 (2-3개 구체적 문제)
- 솔루션을 다리로 제시
- 일반화가 아닌 구체적 사용

**Desire (기능/혜택 + 사회적 증거):**
- 달성할 것을 보여줌
- 효과를 증명 (후기, 데이터, 사례)
- 미래 상태의 그림을 그림

**Action (CTA 섹션):**
- 명확하고 구체적인 요청
- 마찰 제거
- 정직하게 긴급성 생성

### 3.2 사회적 증거 계층

1. **구체적 숫자**: "2,847 active users"
2. **인식 가능한 브랜드**: 알려진 회사 로고 스트립
3. **결과가 있는 후기**: "Made $50K in first month"
4. **권위 추천**: 업계 전문가 인용
5. **인증/수상**: 진짜이고 인식되는 경우

### 3.3 헤드라인 공식

**변환 약속:**
```
"[Desired Outcome] Without [Common Pain Point]"
예: "Scale Your Agency Without Hiring"
```

**구체적 결과:**
```
"How [Target Audience] [Achieved Result] in [Timeframe]"
예: "How 247 Coaches Built 6-Figure Businesses in 90 Days"
```

**직접적 혜택:**
```
"[Biggest Benefit] in [Timeframe/Context]"
예: "Triple Your Close Rate in Your Next 10 Sales Calls"
```

### 3.4 CTA 카피 공식

**회피:**
- "Submit", "Click Here", "Learn More", "Get Started"

**사용:**
- "Get My Free Analysis"
- "Start Building My Landing Page"
- "Show Me How to 3X My Revenue"
- "Yes, I Want to Save 15 Hours/Week"

---

## Part 4: 컴포넌트 패턴

### 4.1 Hero 섹션 (비대칭)

```tsx
export default function Hero() {
  return (
    <section className="relative bg-stone-50 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* 좌측: 콘텐츠 */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-full mb-6">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              New: AI-Powered Analytics
            </div>
            
            <h1 className="text-5xl lg:text-6xl xl:text-7xl font-bold text-slate-900 leading-tight mb-6 tracking-tight">
              Scale Your Agency to{' '}
              <span className="text-blue-600">$50K/month</span> Without Hiring
            </h1>
            
            <p className="text-lg lg:text-xl text-slate-600 mb-8 max-w-xl leading-relaxed">
              Automate client reporting, lead generation, and follow-ups. 
              Join 2,847 agencies saving 20+ hours per week.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 shadow-sm transition-all duration-150">
                Start Your Free Trial
              </button>
              <button className="px-8 py-4 border-2 border-slate-300 text-slate-700 font-semibold rounded-lg hover:border-slate-400 transition-all duration-150">
                Watch 2-Min Demo →
              </button>
            </div>
            
            {/* Social Proof */}
            <div className="mt-8 flex items-center gap-6">
              <div className="flex -space-x-2">
                {[1,2,3,4].map(i => (
                  <div key={i} className="w-10 h-10 rounded-full bg-slate-300 border-2 border-white" />
                ))}
              </div>
              <div className="text-sm">
                <div className="font-semibold text-slate-900">2,847+ agencies</div>
                <div className="text-slate-600">switched this month</div>
              </div>
            </div>
          </div>
          
          {/* 우측: 시각 요소 */}
          <div className="relative lg:pl-8">
            <div className="relative rounded-xl overflow-hidden shadow-2xl border border-slate-200">
              <div className="aspect-[4/3] bg-slate-100"></div>
            </div>
            {/* 플로팅 메트릭 카드 */}
            <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-lg shadow-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">Revenue Growth</div>
              <div className="text-2xl font-bold text-green-600">+127%</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

### 4.2 Feature 섹션 (3컬럼)

```tsx
import { Zap, Shield, BarChart3 } from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: "Automated Lead Qualification",
    description: "Stop wasting time on unqualified leads. Our AI scores every lead and prioritizes the ones ready to buy."
  },
  {
    icon: Shield,
    title: "Bank-Level Security",
    description: "Enterprise-grade encryption and compliance. Your data is protected by the same security used by Fortune 500 companies."
  },
  {
    icon: BarChart3,
    title: "Real-Time Analytics",
    description: "See exactly what's working. Track conversions, ROI, and pipeline in one beautiful dashboard."
  }
];

export default function Features() {
  return (
    <section className="py-24 lg:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
            Everything you need to scale
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Built for agencies who refuse to compromise on quality
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-12">
          {features.map((feature, i) => (
            <div key={i} className="group">
              <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-6 group-hover:bg-blue-100 transition-colors">
                <feature.icon className="w-6 h-6 text-blue-600" />
              </div>
              
              <h3 className="text-2xl font-bold text-slate-900 mb-3">
                {feature.title}
              </h3>
              
              <p className="text-slate-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### 4.3 Testimonial 섹션 (정적 그리드, 캐러셀 아님!)

```tsx
const testimonials = [
  {
    quote: "We closed $240K in new business in our first 60 days. The automated lead qualification alone saved us 25 hours per week.",
    author: "Sarah Chen",
    role: "Founder, GrowthLab Agency",
    rating: 5
  },
  // ... 더 많은 후기
];

export default function Testimonials() {
  return (
    <section className="py-24 bg-slate-900">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">
            Loved by 2,847+ agencies
          </h2>
          <p className="text-xl text-slate-400">
            Real results from real businesses
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial, i) => (
            <div key={i} className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              {/* Star rating */}
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              
              <p className="text-slate-300 mb-6 leading-relaxed">
                "{testimonial.quote}"
              </p>
              
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-slate-700" />
                <div>
                  <div className="font-semibold text-white">{testimonial.author}</div>
                  <div className="text-sm text-slate-400">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### 4.4 Final CTA (리스크 역전 포함)

```tsx
export default function FinalCTA() {
  return (
    <section className="py-24 lg:py-32 bg-gradient-to-br from-blue-600 to-blue-700">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
          Ready to scale your agency?
        </h2>
        
        <p className="text-xl text-blue-100 mb-10">
          Join 2,847 agencies using our platform to close more deals, 
          faster, with less manual work.
        </p>
        
        <button className="px-10 py-5 bg-white text-blue-600 text-lg font-semibold rounded-lg hover:bg-blue-50 transition-colors shadow-xl mb-6">
          Start Your 14-Day Free Trial
        </button>
        
        {/* 리스크 역전 */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-blue-100">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            No credit card required
          </div>
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            14-day money-back guarantee
          </div>
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Setup in under 10 minutes
          </div>
        </div>
      </div>
    </section>
  );
}
```

### 4.5 FAQ 섹션 (아코디언)

```tsx
'use client';
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const faqs = [
  {
    q: "How is this different from [competitor]?",
    a: "Unlike generic CRMs, we're built specifically for agencies. Our automation handles the entire lead qualification process, not just data storage."
  },
  // ... 더 많은 FAQ
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  
  return (
    <section className="py-24 bg-white">
      <div className="max-w-3xl mx-auto px-6">
        <h2 className="text-4xl font-bold text-slate-900 text-center mb-16">
          Frequently asked questions
        </h2>
        
        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div key={i} className="border border-slate-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full px-6 py-5 text-left flex items-center justify-between hover:bg-slate-50 transition-colors"
              >
                <span className="font-semibold text-slate-900 pr-4">
                  {faq.q}
                </span>
                <ChevronDown 
                  className={`w-5 h-5 text-slate-600 transition-transform flex-shrink-0 ${
                    open === i ? 'rotate-180' : ''
                  }`}
                />
              </button>
              
              {open === i && (
                <div className="px-6 pb-5 text-slate-600 leading-relaxed">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## Part 5: 애니메이션과 마이크로인터랙션

### 5.1 페이지 로드 애니메이션 (스태거드)

```css
@keyframes fadeSlideIn {
  from {
    opacity: 0.01; /* 0이 아님 - 깜빡임 방지 */
    transform: translateY(20px);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

.animate-fade-in {
  animation: fadeSlideIn 0.6s ease-out both;
}

/* 스태거 자식 요소 */
.stagger > *:nth-child(1) { animation-delay: 0.1s; }
.stagger > *:nth-child(2) { animation-delay: 0.2s; }
.stagger > *:nth-child(3) { animation-delay: 0.3s; }
.stagger > *:nth-child(4) { animation-delay: 0.4s; }
.stagger > *:nth-child(5) { animation-delay: 0.5s; }
```

### 5.2 호버 상태

```css
/* 버튼 */
.btn-premium {
  transition: all 150ms ease-in-out;
}
.btn-premium:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 카드 */
.card-premium {
  transition: all 200ms ease-in-out;
}
.card-premium:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

/* 링크 */
.link-underline {
  position: relative;
}
.link-underline::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: currentColor;
  transition: width 200ms, left 200ms;
}
.link-underline:hover::after {
  width: 100%;
  left: 0;
}
```

### 5.3 Reduced Motion 지원

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Part 6: 품질 체크리스트

### 배포 전 체크

**시각 디자인:**
- [ ] 1-2개 폰트 최대
- [ ] 일관된 8pt 스페이싱 스케일
- [ ] 넉넉한 여백 (80-128px 섹션 패딩)
- [ ] 모노크롬 또는 미니멀 컬러 팔레트
- [ ] 그라디언트 없음 (또는 하나의 미세한 액센트)
- [ ] 스톡 사진 없음 (또는 고품질 커스텀만)
- [ ] 미세한 그림자 (shadow-sm/md) 또는 없음
- [ ] 프로페셔널 타이포그래피 (18-20px 본문, 64-80px hero)
- [ ] 비대칭 레이아웃 (모두 가운데 아님)

**전환 요소:**
- [ ] 구체적, 변환 중심 헤드라인
- [ ] 스크롤 전 명확한 가치 제안
- [ ] 스크롤 전 1 primary + 1 secondary CTA 최대
- [ ] 구체적 숫자의 사회적 증거
- [ ] 3-6 기능 (혜택 중심, 20개 목록 아님)
- [ ] 실명과 결과가 있는 후기
- [ ] 주요 이의를 다루는 FAQ

**카피 품질:**
- [ ] AI 클리셰 없음 ("unlock", "revolutionize", "next level")
- [ ] 전체에 구체적 숫자와 기간
- [ ] 행동 중심 CTA 카피 ("Learn More" 아님)
- [ ] "You" 언어 (독자에게 직접)
- [ ] 기능보다 혜택
- [ ] 2-3개 주요 이의 해소

**기술 구현:**
- [ ] 모바일 반응형 (테스트됨)
- [ ] 빠른 로딩 (<3s)
- [ ] 시맨틱 HTML
- [ ] 일관된 컴포넌트 패턴
- [ ] 부드러운 트랜지션 (150-200ms)
- [ ] 콘솔 에러 없음
- [ ] 접근성 (alt 텍스트, 적절한 대비)

---

## Part 7: AI vs 프리미엄 빠른 참조

| 요소 | AI 기본값 | 프리미엄 접근 |
|------|----------|--------------|
| 배경 | 그라디언트 메시 | 솔리드 off-white |
| Hero 레이아웃 | 가운데 | 비대칭 60/40 |
| 타이포그래피 | 3+ 폰트 | 1-2 폰트 최대 |
| 색상 | 레인보우 | 모노크롬 + 1 액센트 |
| 버튼 | Pill 모양 | 미세 radius (8-12px) |
| 기능 | 12+ 그리드 | 3-6 전략적 배치 |
| 사진 | 스톡 일반 | 실제 제품 또는 없음 |
| 그림자 | 모든 곳에 Heavy | 미세하고 전략적 |
| 스페이싱 | 랜덤 | 일관된 8pt 스케일 |
| CTA 카피 | "Learn More" | 구체적 행동 |
| 후기 | 캐러셀 | 정적 그리드 |
| 여백 | 최소 | 넉넉함 |

---

**기억하세요:** 프리미엄 디자인은 **절제, 의도, 정교함**입니다. AI 디자인은 **최대주의, 안전, 템플릿**입니다. 더 많은 색상, 폰트, 효과가 더 나은 디자인을 만들지 않습니다. 최고의 랜딩 페이지는 1-2개 폰트, 1개 primary 색상 + 1개 액센트, 그리고 넉넉한 여백을 사용합니다.
