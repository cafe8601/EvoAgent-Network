# Agent Classification Guide v2.0

**Purpose:** Clear mapping from old structure (01-10 categories) to new structure (tier1/2/3)

---

## 🎯 Tier System Overview

### Tier 1: Core Agents (20) ✅ COMPLETE
**Status:** Production-ready, fully validated, 100% standalone
**Location:** `tier1-core/`
**Quality:** v2.0 with full validation

**List:**
1. backend-developer
2. frontend-developer
3. python-pro
4. typescript-pro
5. javascript-pro
6. devops-engineer
7. kubernetes-architect
8. cloud-architect
9. qa-expert
10. code-reviewer
11. security-auditor
12. data-engineer
13. ml-engineer
14. fullstack-developer
15. dx-optimizer
16. build-engineer
17. product-manager
18. technical-writer
19. multi-agent-coordinator
20. agent-organizer

---

### Tier 2: Specialized Agents (~100)
**Status:** Functional, may use v1.0 or simplified v2.0
**Location:** `tier2-specialized/{category}/`
**Quality:** Use as-is or convert with tier2-template.md

**Categories:**

#### `tier2-specialized/languages/`
**From:** 02-language-specialists (minus Tier 1 agents)

**Agents (~25):**
- rust-pro, rust-engineer
- golang-pro
- java-pro, java-architect
- c-pro, cpp-pro
- kotlin-specialist
- scala-pro
- elixir-pro
- ruby-pro
- swift-expert
- php-pro
- sql-pro
- csharp-pro, csharp-developer
- dotnet-framework-4.8-expert
- dotnet-core-expert

**Characteristics:**
- Language-specific expertise
- Compiler/runtime knowledge
- Ecosystem tools
- Testing frameworks

---

#### `tier2-specialized/frameworks/`
**From:** 02-language-specialists (framework-specific)

**Agents (~15):**
- nextjs-developer
- react-specialist
- vue-expert
- angular-architect
- django-pro, django-developer
- rails-expert
- laravel-specialist
- fastapi-pro
- spring-boot-engineer
- flutter-expert

**Characteristics:**
- Framework-specific patterns
- Best practices
- Ecosystem integration

---

#### `tier2-specialized/infrastructure/`
**From:** 03-infrastructure (minus Tier 1 agents)

**Agents (~12):**
- terraform-specialist
- observability-engineer
- sre-engineer
- platform-engineer
- network-engineer
- deployment-engineer
- incident-responder
- database-admin
- terraform-engineer
- kubernetes-specialist (if not consolidated)
- hybrid-cloud-architect
- devops-troubleshooter (if not consolidated)

**Characteristics:**
- Infrastructure tooling
- Platform engineering
- Reliability engineering

---

#### `tier2-specialized/quality/`
**From:** 04-quality-security (quality subset)

**Agents (~8):**
- performance-engineer
- accessibility-tester
- test-automator
- debugger
- refactoring-specialist
- legacy-modernizer
- chaos-engineer
- dependency-manager

**Characteristics:**
- Quality improvement
- Performance optimization
- Testing automation

---

#### `tier2-specialized/security/`
**From:** 04-quality-security (security subset)

**Agents (~6):**
- security-engineer
- penetration-tester
- compliance-auditor
- backend-security-coder
- frontend-security-coder
- mobile-security-coder

**Characteristics:**
- Security implementation
- Vulnerability testing
- Compliance validation

---

#### `tier2-specialized/data-ai/`
**From:** 05-data-ai (minus Tier 1 agents)

**Agents (~8):**
- ai-engineer
- mlops-engineer
- data-scientist
- data-analyst
- nlp-engineer
- llm-architect
- prompt-engineer
- database-optimizer

**Characteristics:**
- AI/ML specialization
- Data processing
- Analytics

---

#### `tier2-specialized/devtools/`
**From:** 06-developer-experience (minus Tier 1 agents)

**Agents (~10):**
- tooling-engineer
- documentation-engineer
- reference-builder
- tutorial-engineer
- docs-architect
- cli-developer
- git-workflow-manager
- mermaid-expert
- ui-visual-validator

**Characteristics:**
- Developer tooling
- Documentation
- Workflow optimization

---

#### `tier2-specialized/specialized/`
**From:** 07-specialized-domains

**Agents (~20):**
- mobile-developer
- mobile-app-developer
- ios-developer
- electron-pro
- websocket-engineer
- graphql-architect
- api-designer
- microservices-architect
- iot-engineer
- embedded-systems
- seo-specialist
- competitive-analyst
- trend-analyst
- search-specialist
- data-researcher
- market-researcher
- research-analyst
- payment-integration
- risk-manager
- customer-support

**Characteristics:**
- Domain-specific expertise
- Specialized technologies
- Niche applications

---

#### `tier2-specialized/business/`
**From:** 08-business-product (minus Tier 1 agents)

**Agents (~10):**
- business-analyst
- project-manager
- ux-researcher
- ui-ux-designer
- ui-designer
- scrum-master
- customer-success-manager
- sales-engineer
- sales-automator
- hr-pro
- legal-advisor

**Characteristics:**
- Business operations
- Product management
- Design

---

#### `tier2-specialized/orchestration/`
**From:** 09-meta-orchestration (minus Tier 1 agents)

**Agents (~4):**
- context-manager
- task-distributor
- workflow-orchestrator
- performance-monitor
- error-coordinator
- knowledge-synthesizer

**Characteristics:**
- Meta-system coordination
- Workflow management
- Knowledge synthesis

---

#### `tier2-specialized/research/`
**From:** 10-research-analysis

**Agents (~6):**
- All agents from 10-research-analysis
- (May overlap with specialized/)

---

### Tier 3: Experimental Agents (~40)
**Status:** Experimental, use with caution
**Location:** `tier3-experimental/{category}/`
**Quality:** v1.0, not validated

**Categories:**

#### `tier3-experimental/blockchain/`
- blockchain-developer
- fintech-engineer
- quant-analyst

#### `tier3-experimental/gaming/`
- game-developer
- unity-developer
- minecraft-bukkit-pro

#### `tier3-experimental/emerging-tech/`
- quantum-computing (if exists)
- edge-computing
- web3-specialist

#### `tier3-experimental/niche/`
- seo-* variants (multiple SEO specialists)
- wordpress-master
- Other highly specialized agents

---

## 📋 Classification Decision Tree

**How to classify an agent:**

```python
def classify_agent(agent):
    # Tier 1: Already decided (20 agents)
    if agent in TIER_1_LIST:
        return "tier1-core/"

    # Tier 3: Experimental criteria
    if is_experimental(agent) or is_niche(agent):
        category = determine_experimental_category(agent)
        return f"tier3-experimental/{category}/"

    # Tier 2: Everything else
    category = determine_category(agent)
    return f"tier2-specialized/{category}/"

def is_experimental(agent):
    keywords = ["blockchain", "quantum", "crypto", "web3", "gaming"]
    return any(kw in agent.lower() for kw in keywords)

def is_niche(agent):
    # Very specialized, limited use cases
    niche_agents = [
        "minecraft-bukkit-pro",
        "wordpress-master",
        "seo-*",  # Multiple SEO variants
    ]
    return agent in niche_agents

def determine_category(agent):
    # Language specialists
    if agent.endswith("-pro") or "language" in description:
        return "languages"

    # Framework specialists
    if any(fw in agent for fw in ["nextjs", "django", "rails", "vue", "angular"]):
        return "frameworks"

    # Infrastructure
    if any(kw in agent for kw in ["terraform", "ansible", "sre", "platform"]):
        return "infrastructure"

    # Quality
    if any(kw in agent for kw in ["performance", "accessibility", "test", "debug"]):
        return "quality"

    # Security
    if any(kw in agent for kw in ["security", "penetration", "compliance"]):
        return "security"

    # Data/AI
    if any(kw in agent for kw in ["data", "ml", "ai", "analytics"]):
        return "data-ai"

    # DevTools
    if any(kw in agent for kw in ["tool", "cli", "git", "documentation"]):
        return "devtools"

    # Business
    if any(kw in agent for kw in ["product", "business", "sales", "ux"]):
        return "business"

    # Orchestration
    if any(kw in agent for kw in ["coordinator", "orchestrator", "workflow"]):
        return "orchestration"

    # Default
    return "specialized"
```

---

## 🗂️ Migration Mapping

### From Old Structure to New

**Old:** `01-core-development/backend-developer.md`
**New:** `tier1-core/backend-developer.md` ✅

**Old:** `02-language-specialists/rust-pro.md`
**New:** `tier2-specialized/languages/rust-pro.md`

**Old:** `03-infrastructure/terraform-specialist.md`
**New:** `tier2-specialized/infrastructure/terraform-specialist.md`

**Old:** `04-quality-security/penetration-tester.md`
**New:** `tier2-specialized/security/penetration-tester.md`

**Old:** `07-specialized-domains/blockchain-developer.md`
**New:** `tier3-experimental/blockchain/blockchain-developer.md`

---

## 🎯 Why This Structure?

### Benefits of New Structure

**1. Clear Quality Tiers**
- **Tier 1:** Validated, production-ready, use with confidence
- **Tier 2:** Functional, use as-is or with simplified template
- **Tier 3:** Experimental, use with caution

**2. Preserved Categories**
- Still organized by function (languages, infrastructure, etc.)
- Easy to browse and discover
- Logical grouping maintained

**3. No Confusion**
- Single source of truth
- Clear version (v1.0 in deprecated, v2.0 in tiers)
- Obvious usage guidance

### vs Old Structure

**Old (Confusing):**
```
01-core-development/backend-developer.md  (v1.0, broken)
tier1-core/backend-developer.md  (v2.0, working)
→ Which one to use??? 🤔
```

**New (Clear):**
```
tier1-core/backend-developer.md  (v2.0, ✅ validated)
_deprecated/01-core-development/backend-developer.md  (v1.0, archived)
→ Use tier1-core! ✅
```

---

## 📖 Usage Guide

### Finding the Right Agent

**By Quality Need:**
1. **Need production-ready?** → Check `tier1-core/` first
2. **Need specialized?** → Check `tier2-specialized/{category}/`
3. **Experimental OK?** → Check `tier3-experimental/`

**By Functional Area:**
1. **Language expertise?** → `tier2-specialized/languages/`
2. **Framework specific?** → `tier2-specialized/frameworks/`
3. **Infrastructure?** → `tier1-core/` or `tier2-specialized/infrastructure/`
4. **Quality/Security?** → `tier1-core/` or `tier2-specialized/quality|security/`

**Example:**
```
Need: Python development
→ tier1-core/python-pro.md (BEST CHOICE - validated)

Need: Rust development
→ tier2-specialized/languages/rust-pro.md (functional, v1.0)

Need: Blockchain development
→ tier3-experimental/blockchain/blockchain-developer.md (experimental)
```

---

## 🔄 Migration Process for Remaining 139 Agents

### Automated Classification Script

```bash
#!/bin/bash
# classify_agents.sh

DEPRECATED="_deprecated"

# For each old category
for old_cat in "$DEPRECATED"/0*/; do
  cat_name=$(basename "$old_cat")

  for agent in "$old_cat"/*.md; do
    [ "$(basename "$agent")" = "README.md" ] && continue

    agent_name=$(basename "$agent" .md)

    # Check if in Tier 1 (skip)
    if [ -f "tier1-core/$agent_name.md" ]; then
      echo "Skip: $agent_name (in Tier 1)"
      continue
    fi

    # Classify to Tier 2 or 3
    if is_experimental "$agent_name"; then
      dest="tier3-experimental"
    else
      dest="tier2-specialized"
    fi

    # Determine subcategory
    subcat=$(determine_subcategory "$agent_name" "$cat_name")

    # Copy to new location
    cp "$agent" "$dest/$subcat/$agent_name.md"
    echo "✅ $agent_name → $dest/$subcat/"
  done
done
```

### Manual Classification Priorities

**High Priority (Do First):**
- Language specialists (rust, go, java) → tier2/languages/
- Framework specialists (nextjs, django) → tier2/frameworks/
- Infrastructure tools (terraform, ansible) → tier2/infrastructure/

**Medium Priority:**
- Quality tools → tier2/quality/
- Security tools → tier2/security/
- Data/AI tools → tier2/data-ai/

**Low Priority:**
- Everything else → appropriate tier2 subcategory
- Highly experimental → tier3

---

## 🎯 Recommended Approach

### Option 1: Use As-Is (Simplest)

**Current state:**
- Tier 1: 20 agents ✅ (validated, ready)
- Tier 2/3: Empty but organized
- Old agents: In _deprecated/ (accessible if needed)

**Usage:**
- Use Tier 1 for 91% of cases
- Reference _deprecated/ if need specific agent
- Gradually migrate to Tier 2/3 on-demand

**Effort:** 0 hours

---

### Option 2: Classify All (Comprehensive)

**Action:** Move 139 agents from _deprecated/ to tier2/tier3

**Process:**
1. Run classification script
2. Manual review of placements
3. Add README to each subcategory

**Effort:** 4-6 hours

---

### Option 3: On-Demand (Practical - RECOMMENDED)

**Action:** Migrate agents as needed

**Process:**
1. User requests agent (e.g., "rust-pro")
2. Check tier1-core/ first
3. If not found, check _deprecated/
4. Classify and move to tier2/languages/
5. Apply tier2-template if time permits

**Effort:** Minimal, distributed over time

---

## 📊 Category → Tier Mapping

| Old Category | New Tier 2 Location | Agent Count |
|-------------|---------------------|-------------|
| 01-core-development | tier1-core/ (moved) | 10 → Tier 1 |
| 02-language-specialists | tier2/languages/ + tier2/frameworks/ | 32 |
| 03-infrastructure | tier2/infrastructure/ + tier1 (some) | 18 |
| 04-quality-security | tier2/quality/ + tier2/security/ + tier1 (some) | 19 |
| 05-data-ai | tier2/data-ai/ + tier1 (some) | 12 |
| 06-developer-experience | tier2/devtools/ + tier1 (some) | 14 |
| 07-specialized-domains | tier2/specialized/ + tier3/blockchain/ + tier3/gaming/ | 26 |
| 08-business-product | tier2/business/ + tier1 (some) | 14 |
| 09-meta-orchestration | tier2/orchestration/ + tier1 (some) | 8 |
| 10-research-analysis | tier2/research/ | 6 |

---

## 🗺️ Final Directory Structure

```
~/.claude/agents/
│
├── tier1-core/                    [20 agents - v2.0 validated]
│   ├── backend-developer.md
│   ├── frontend-developer.md
│   └── ... (18 more)
│
├── tier2-specialized/             [~100 agents - functional]
│   ├── languages/                [rust, go, java, etc.]
│   ├── frameworks/               [nextjs, django, rails, etc.]
│   ├── infrastructure/           [terraform, sre, etc.]
│   ├── quality/                  [performance, accessibility, etc.]
│   ├── security/                 [penetration, compliance, etc.]
│   ├── data-ai/                  [ai, mlops, data-science, etc.]
│   ├── devtools/                 [tooling, docs, cli, etc.]
│   ├── specialized/              [mobile, iot, seo, etc.]
│   ├── business/                 [analyst, project-manager, etc.]
│   ├── orchestration/            [workflow, task-distributor, etc.]
│   └── research/                 [research-analyst, etc.]
│
├── tier3-experimental/            [~40 agents - experimental]
│   ├── blockchain/               [blockchain-developer, fintech, etc.]
│   ├── gaming/                   [game-developer, unity, minecraft, etc.]
│   ├── emerging-tech/            [quantum, edge, web3, etc.]
│   └── niche/                    [wordpress, seo variants, etc.]
│
├── _templates/                    [Agent creation templates]
│   ├── tier1-template.md
│   ├── tier2-template.md
│   └── validate-agent.sh
│
├── _deprecated/                   [v1.0 backup - 159 agents]
│   ├── 01-core-development/
│   ├── 02-language-specialists/
│   └── ... (10 categories)
│
└── [Documentation]
    ├── README.md
    ├── MIGRATION_GUIDE.md
    ├── AGENT_CLASSIFICATION_GUIDE.md (this file)
    ├── CONVERSION_STATUS.md
    ├── COMPLETION_REPORT.md
    └── FINAL_SUMMARY.md
```

---

## ✅ Key Improvements

**Before (Confusing):**
```
01-core-development/backend-developer.md  (v1.0)
tier1-core/backend-developer.md           (v2.0)
_deprecated/01-core-development/...       (backup)
→ 3 copies, which to use? 😵
```

**After (Clear):**
```
tier1-core/backend-developer.md           (v2.0 ✅)
_deprecated/01-core-development/...       (archived)
→ Single source of truth! 😊
```

---

## 🎯 Summary

**Old Structure:** Functional categories (01-10)
- ✅ Good: Organized by purpose
- ❌ Bad: No quality indication

**New Structure:** Tier + Categories
- ✅ Tier 1: Quality guarantee (validated)
- ✅ Tier 2: Functional + categorized
- ✅ Tier 3: Experimental + categorized
- ✅ Categories preserved in tier2/tier3 subdirectories

**Result:** Best of both worlds - quality tiers + functional categories

---

**Recommendation:** Use **Option 3 (On-Demand)** - Keep current clean structure, migrate agents from _deprecated/ to tier2/3 as needed.

**Status:** Structure ready, agents available in _deprecated/, tier1 complete.
