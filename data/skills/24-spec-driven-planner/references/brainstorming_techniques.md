# Brainstorming Techniques for Spec-Driven Development

This document provides comprehensive guidance on facilitation techniques for product discovery and feature ideation.

---

## Table of Contents

1. [Story Mapping](#1-story-mapping)
2. [Event Storming](#2-event-storming)
3. [Impact Mapping](#3-impact-mapping)
4. [Prioritization Frameworks](#4-prioritization-frameworks)
5. [Ideation Techniques](#5-ideation-techniques)
6. [Workshop Formats](#6-workshop-formats)
7. [Output Templates](#7-output-templates)

---

## 1. Story Mapping

### Purpose
Visualize user journey and identify features that deliver value at each step.

### Process

```
Step 1: Define User Activities (horizontal backbone)
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Discover     │ Browse       │ Purchase     │ Receive      │
│ Products     │ & Compare    │ & Checkout   │ & Review     │
└──────────────┴──────────────┴──────────────┴──────────────┘

Step 2: Break down into User Tasks (vertical slices)

Discover Products:
├─ Search by keyword
├─ Filter by category
├─ View trending products
└─ Get personalized recommendations

Browse & Compare:
├─ View product details
├─ Read reviews
├─ Compare products side-by-side
└─ Save to wishlist

Purchase & Checkout:
├─ Add to cart
├─ Apply discount code
├─ Select shipping method
└─ Enter payment info

Step 3: Prioritize by Walking Skeleton (MVP = top row)
┌────────────────────────────────────────────────────────┐
│ MVP (Release 1): Walking Skeleton                      │
├────────────────────────────────────────────────────────┤
│ Search → View Details → Add to Cart → Checkout        │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Release 2: Enhanced Discovery                          │
├────────────────────────────────────────────────────────┤
│ Filters, Trending, Recommendations, Reviews            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Release 3: Advanced Features                           │
├────────────────────────────────────────────────────────┤
│ Wishlist, Compare, Discount Codes, Saved Payments     │
└────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Activities First**: Start with user goals (horizontal axis)
2. **Tasks Second**: Break down into specific tasks (vertical axis)
3. **Walking Skeleton**: MVP includes one path through each activity
4. **Incremental Value**: Each release adds complete vertical slices

### Output
Prioritized backlog aligned with user journey.

---

## 2. Event Storming

### Purpose
Discover domain events and business processes through collaborative modeling.

### Color Coding

| Color | Element | Example |
|-------|---------|---------|
| 🟠 Orange | Domain Events | OrderPlaced, PaymentProcessed |
| 🔵 Blue | Commands | PlaceOrder, ProcessPayment |
| 🟡 Yellow | Aggregates | Order, Payment, Shipment |
| 🩷 Pink | External Systems | PaymentGateway, ShippingProvider |
| 🟣 Purple | Policies | WHEN X THEN Y |

### Process

```markdown
## Event Storming Workflow

### Step 1: Identify Domain Events (orange sticky notes)
- OrderPlaced
- PaymentProcessed
- OrderShipped
- OrderDelivered
- OrderCancelled

### Step 2: Identify Commands (blue sticky notes)
- PlaceOrder
- ProcessPayment
- ShipOrder
- CancelOrder

### Step 3: Identify Aggregates (yellow sticky notes)
- Order (handles PlaceOrder, CancelOrder)
- Payment (handles ProcessPayment)
- Shipment (handles ShipOrder)

### Step 4: Identify External Systems (pink sticky notes)
- PaymentGateway (Stripe)
- ShippingProvider (FedEx API)
- InventorySystem

### Step 5: Identify Policies (purple sticky notes)
- WHEN OrderPlaced THEN ProcessPayment
- WHEN PaymentProcessed THEN ReserveInventory
- WHEN InventoryReserved THEN ShipOrder
- WHEN OrderCancelled AND PaymentProcessed THEN RefundPayment
```

### Output
Visual map of business processes and bounded contexts.

---

## 3. Impact Mapping

### Purpose
Connect business goals to features through user impact.

### Structure

```
GOAL: Increase revenue by 20% in Q2

WHY? (Impact)
├─ Increase conversion rate (5% → 8%)
│  ├─ WHO? (Actors)
│  │  ├─ New visitors
│  │  └─ Returning customers
│  ├─ HOW? (Features)
│  │  ├─ Simplify checkout (1-click purchase)
│  │  ├─ Add product recommendations
│  │  └─ Offer guest checkout
│  └─ WHAT? (Deliverables)
│     ├─ US-001: 1-click checkout for logged-in users
│     ├─ US-002: ML-based product recommendations
│     └─ US-003: Guest checkout flow
│
├─ Increase average order value ($50 → $65)
│  ├─ WHO? (Actors)
│  │  └─ Existing customers
│  ├─ HOW? (Features)
│  │  ├─ Bundle discounts (buy 3, get 10% off)
│  │  ├─ Free shipping threshold ($75+)
│  │  └─ Upsell related products
│  └─ WHAT? (Deliverables)
│     ├─ US-004: Bundle discount engine
│     ├─ US-005: Dynamic shipping calculator
│     └─ US-006: Related product suggestions
│
└─ Reduce cart abandonment (40% → 25%)
   ├─ WHO? (Actors)
   │  └─ Users with items in cart
   ├─ HOW? (Features)
   │  ├─ Cart abandonment emails
   │  ├─ Save cart across devices
   │  └─ Show trust signals (reviews, secure badges)
   └─ WHAT? (Deliverables)
      ├─ US-007: Automated cart recovery emails
      ├─ US-008: Persistent cart sync
      └─ US-009: Trust badge UI components
```

### Output
Features directly linked to business outcomes.

---

## 4. Prioritization Frameworks

### 4.1 MoSCoW Method

| Category | Definition | Criteria |
|----------|------------|----------|
| **Must Have** | Critical for launch | System won't work without it |
| **Should Have** | Important but not critical | Can launch without, but hurts UX |
| **Could Have** | Nice to have | Improves experience but optional |
| **Won't Have** | Explicitly deferred | Out of scope for this release |

#### Example

```markdown
## Feature Prioritization: E-commerce MVP

### MUST Have (Critical for Launch)
- [ ] User registration & login
- [ ] Product catalog with search
- [ ] Shopping cart
- [ ] Checkout with payment processing
- [ ] Order confirmation email

**Rationale**: Core transactional flow, no sales without these.

### SHOULD Have (Important but not critical)
- [ ] Product reviews and ratings
- [ ] Wishlist/Save for Later
- [ ] Order history
- [ ] Basic analytics dashboard (admin)

**Rationale**: Enhance UX and trust, but MVP can ship without.

### COULD Have (Nice to have if time allows)
- [ ] Product recommendations
- [ ] Social login (Google, Facebook)
- [ ] Advanced filtering (price range, brand)
- [ ] Guest checkout

**Rationale**: Competitive features, but not required for MVP.

### WON'T Have (Explicitly deferred)
- [ ] Mobile app (web-first)
- [ ] Multi-currency support
- [ ] Subscription billing
- [ ] Loyalty program

**Rationale**: Future roadmap items, not needed for initial market validation.
```

### 4.2 RICE Score

**Formula**: `RICE = (Reach × Impact × Confidence) / Effort`

| Component | Scale | Description |
|-----------|-------|-------------|
| **Reach** | Number | Users affected in time period |
| **Impact** | 0.25-3 | Massive(3), High(2), Medium(1), Low(0.5), Minimal(0.25) |
| **Confidence** | 0-100% | How sure you are about estimates |
| **Effort** | Person-weeks | Development time required |

#### Example

```markdown
## RICE Scoring

### Feature A: 1-Click Checkout
- Reach: 5000 users/month
- Impact: High (3/3)
- Confidence: 80%
- Effort: 4 person-weeks

**RICE Score** = (5000 × 3 × 0.8) / 4 = **3000**

### Feature B: Product Recommendations
- Reach: 8000 users/month
- Impact: Medium (2/3)
- Confidence: 50%
- Effort: 8 person-weeks

**RICE Score** = (8000 × 2 × 0.5) / 8 = **1000**

### Feature C: Guest Checkout
- Reach: 2000 users/month
- Impact: High (3/3)
- Confidence: 90%
- Effort: 2 person-weeks

**RICE Score** = (2000 × 3 × 0.9) / 2 = **2700**

### Priority Order
1. 1-Click Checkout (RICE: 3000)
2. Guest Checkout (RICE: 2700)
3. Product Recommendations (RICE: 1000)
```

### 4.3 Kano Model

| Category | Description | Strategy |
|----------|-------------|----------|
| **Basic (Must-Be)** | Expected, absence causes dissatisfaction | Must implement, won't differentiate |
| **Performance (Linear)** | More is better, linear correlation | Invest based on competition |
| **Excitement (Delighters)** | Unexpected, presence creates joy | Focus on 1-2 for differentiation |
| **Indifferent** | Users don't care | Deprioritize or skip |
| **Reverse** | Causes dissatisfaction | Avoid completely |

#### Example

```markdown
## Kano Analysis: Email Client

### Basic Needs (Hygiene Factors)
- Send and receive email (expected)
- Attachment support (expected)
- Spam filtering (expected)

**Action**: Must implement, won't differentiate.

### Performance Needs (Satisfiers)
- Search speed (faster = better)
- Storage quota (more = better)
- Mobile app performance

**Action**: Invest based on competitive benchmarks.

### Excitement Needs (Delighters)
- AI-powered email summarization
- Smart reply suggestions
- Scheduled send with timezone awareness
- Undo send (5-second window)

**Action**: Focus on 1-2 for differentiation.

### Indifferent Features (Low Priority)
- Custom email signatures
- Theme customization

**Action**: Deprioritize or skip.

### Reverse Features (Causes Dissatisfaction)
- Intrusive ads in inbox
- Forced social features

**Action**: Avoid completely.
```

---

## 5. Ideation Techniques

### 5.1 Crazy 8s (Rapid Ideation)

**Process**: 8 sketches in 8 minutes (1 minute per idea)

```markdown
## Crazy 8s Session: Improve Checkout Flow

### Ideas Generated (8 minutes)
1. **1-Click Purchase** - Saved payment + address
2. **Progressive Disclosure** - Multi-step wizard
3. **Guest Checkout** - No account required
4. **Cart Abandonment Recovery** - Email + discount
5. **Payment Link Sharing** - Send checkout link to others
6. **Buy Now Pay Later** - Installment payments
7. **Voice Checkout** - "Alexa, complete my order"
8. **AR Try-On** - Virtual fitting before checkout

### Voting (Dot Voting)
- 1-Click Purchase: ●●●●● (5 votes)
- Guest Checkout: ●●●● (4 votes)
- BNPL Integration: ●●● (3 votes)
- Progressive Disclosure: ●● (2 votes)

### Top 3 for Deeper Exploration
1. 1-Click Purchase (quick win, high impact)
2. Guest Checkout (reduce friction)
3. BNPL Integration (competitive parity)
```

### 5.2 Six Thinking Hats (De Bono)

| Hat | Focus | Questions |
|-----|-------|-----------|
| ⚪ White | Facts & Data | What do we know? What data exists? |
| ❤️ Red | Emotions & Intuition | How do I feel about this? |
| 💛 Yellow | Optimism & Benefits | What are the positives? |
| ⬛ Black | Risks & Caution | What could go wrong? |
| 💚 Green | Creativity & Alternatives | What are other possibilities? |
| 🔵 Blue | Process & Conclusion | What's the next step? |

#### Example

```markdown
## Six Hats Analysis: AI-Powered Email Summarization

### White Hat (Facts & Data)
- Average email length: 200 words
- Users spend 3 minutes reading complex emails
- 40% of emails are > 500 words
- Competitor Y launched similar feature (20% adoption)

### Red Hat (Emotions & Intuition)
- "This feels like a gimmick"
- "Love this! Saves time on long threads"
- "Worried about missing critical details"

### Yellow Hat (Optimism & Benefits)
- Saves 2 minutes per long email → 20 min/day
- Reduces cognitive load
- Differentiator from competitors

### Black Hat (Risks & Caution)
- AI hallucination risk
- Privacy concerns
- High development cost
- May annoy some users

### Green Hat (Creativity & Alternatives)
- Alternative 1: Highlight key sentences only
- Alternative 2: TL;DR generated by sender
- Alternative 3: Voice-to-summary

### Blue Hat (Process & Conclusion)
**Decision**: Proceed with limited MVP
- Build: Highlight key sentences (lower risk)
- Test: 10% of users
- Iterate: If successful, full AI summarization
```

### 5.3 How Might We (HMW) Questions

**Purpose**: Reframe problems as opportunities.

```markdown
## Problem Statement
Users abandon checkout because the form is too long (12 fields).

### HMW Questions

**HMW reduce the number of required fields?**
- Use address autocomplete (Google Places API)
- Prefill from previous orders

**HMW make the form feel shorter?**
- Multi-step wizard (psychological chunking)
- Progress bar showing "80% complete"

**HMW eliminate the form entirely?**
- 1-click checkout for returning users
- Voice input for address/payment

**HMW make filling the form more enjoyable?**
- Gamify with rewards
- Show real-time savings

**HMW help users trust the checkout process?**
- Show trust badges (SSL, money-back guarantee)
- Live chat support during checkout
```

---

## 6. Workshop Formats

### 6.1 Remote Brainstorming (90 minutes)

```
00:00 - 00:10  Introduction & Problem Statement
00:10 - 00:25  Individual Ideation (silent brainstorming)
00:25 - 00:45  Group Sharing (2 min per person)
00:45 - 01:00  Affinity Grouping (cluster similar ideas)
01:00 - 01:15  Dot Voting (3 votes per person)
01:15 - 01:30  Discussion & Action Items
```

**Tools**: Miro, FigJam, Mural

### 6.2 Design Sprint (5-Day Format)

| Day | Activity | Output |
|-----|----------|--------|
| **Day 1** | Map | User journey, pain points, sprint goal |
| **Day 2** | Sketch | Crazy 8s, solution sketches |
| **Day 3** | Decide | Dot voting, storyboard, prototype plan |
| **Day 4** | Prototype | High-fidelity mockup, interactive prototype |
| **Day 5** | Test | 5 user interviews, findings, decision |

---

## 7. Output Templates

### Brainstorming Session Summary

```markdown
# Brainstorming Session: [Topic]

**Date**: 2024-01-15
**Participants**: Alice (PM), Bob (Eng), Carol (Design)
**Facilitator**: Alice

## Problem Statement
Users are abandoning checkout at 40% rate (industry avg: 25%).

## Ideas Generated (22 total)

### High Priority (Top 5 by voting)
1. **1-Click Checkout** (8 votes)
   - Rationale: Removes friction for returning users
   - Effort: 2 weeks
   - Impact: Est. 10% reduction in abandonment

2. **Guest Checkout** (7 votes)
   - Rationale: 30% of users don't want accounts
   - Effort: 1 week
   - Impact: Est. 8% reduction

3. **Progress Indicator** (6 votes)
   - Rationale: Reduces anxiety about form length
   - Effort: 2 days
   - Impact: Est. 3% reduction

4. **Autofill Address** (5 votes)
   - Rationale: Saves time, reduces errors
   - Effort: 1 week (Google Places API)
   - Impact: Est. 5% reduction

5. **Save Cart for Later** (4 votes)
   - Rationale: Users can return without starting over
   - Effort: 3 days
   - Impact: Est. 4% recovery

### Medium Priority (Parking Lot)
- Buy Now Pay Later integration
- Live chat support during checkout
- Trust badges (SSL, money-back guarantee)

### Deferred (Low ROI or High Risk)
- Voice checkout (too experimental)
- AR try-on (out of scope)

## Action Items
- [ ] Alice: Create specs for Top 3
- [ ] Bob: Technical feasibility assessment (3 days)
- [ ] Carol: Mockups for guest checkout flow (5 days)
- [ ] Team: Review specs on Friday standup

## Next Session
- Date: 2024-01-22
- Topic: Refine top 3 ideas into user stories
```

---

## Best Practices

### 1. Timebox Everything
- Ideation: 10-15 minutes max
- Discussion: 5 minutes per idea
- Voting: 2 minutes

### 2. Diverge Before Converging
- Generate quantity first (no criticism)
- Evaluate quality later (structured voting)

### 3. Make It Visual
- Sketches > Text
- Whiteboards > Documents
- Prototypes > Specs

### 4. Include Diverse Perspectives
- Engineering (feasibility)
- Design (usability)
- Product (business value)
- Support (user pain points)

### 5. Document Decisions
- Why did we choose X over Y?
- What assumptions are we making?
- What will we measure?

---

## Resources

- [User Story Mapping - Jeff Patton](https://www.jpattonassociates.com/user-story-mapping/)
- [Impact Mapping - Gojko Adzic](https://www.impactmapping.org/)
- [Design Sprint - Google Ventures](https://www.gv.com/sprint/)
- [Kano Model Analysis](https://en.wikipedia.org/wiki/Kano_model)
- [Event Storming](https://www.eventstorming.com/)
