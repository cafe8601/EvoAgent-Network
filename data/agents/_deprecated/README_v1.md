# Claude Code Subagent Repository

**Comprehensive collection of 169 production-ready Claude Code subagents, optimized and categorized for efficient AI-assisted development.**

## 📊 Overview

This repository contains meticulously organized subagent definitions following Claude Code best practices and operational workflow patterns. Each subagent is designed for specific development tasks with integrated MCP tool support and structured communication protocols.

### Statistics

- **Total Agents**: 169
- **Categories**: 10 specialized domains
- **Format**: Operational workflow with MCP integration
- **Status**: Production-ready

## 🎯 What Are Subagents?

Subagents are specialized AI assistants that enhance Claude Code's capabilities through:

- **Isolated Context Windows**: Independent operation preventing cross-contamination
- **Domain-Specific Intelligence**: Expertly crafted instructions for specialized tasks
- **MCP Tool Integration**: Direct access to Model Context Protocol tools
- **Structured Workflows**: Clear communication protocols and development phases
- **Cross-Agent Collaboration**: Coordinated multi-agent operations

## 📁 Category Structure

### [01. Core Development](01-core-development/) (11 agents)
Essential development subagents for everyday coding tasks.

**Key Agents**:
- **api-designer** - REST and GraphQL API architecture
- **backend-developer** - Server-side scalable systems
- **frontend-developer** - UI/UX React/Vue/Angular specialist
- **fullstack-developer** - End-to-end feature development
- **microservices-architect** - Distributed systems design
- **mobile-developer** - Cross-platform mobile apps
- **websocket-engineer** - Real-time communication
- **wordpress-master** - WordPress development & optimization

### [02. Language Specialists](02-language-specialists/) (33 agents)
Language-specific experts with deep framework knowledge.

**Popular Languages**:
- **Python**: python-pro, django-pro, fastapi-pro
- **JavaScript/TypeScript**: javascript-pro, typescript-pro, nextjs-developer, react-specialist, vue-expert, angular-architect
- **Java/JVM**: java-pro, kotlin-specialist, scala-pro, spring-boot-engineer
- **Systems**: rust-pro, golang-pro, cpp-pro, c-pro
- **Mobile**: swift-expert, flutter-expert
- **Web**: php-pro, laravel-specialist, rails-expert, elixir-pro

### [03. Infrastructure](03-infrastructure/) (19 agents)
DevOps, cloud, and deployment specialists.

**Key Areas**:
- **Cloud**: cloud-architect, hybrid-cloud-architect
- **Containers**: kubernetes-architect, kubernetes-specialist
- **IaC**: terraform-specialist, terraform-engineer
- **DevOps**: devops-engineer, devops-incident-responder, devops-troubleshooter
- **Reliability**: sre-engineer, incident-responder
- **Database**: database-admin, database-administrator
- **Monitoring**: observability-engineer, platform-engineer

### [04. Quality & Security](04-quality-security/) (20 agents)
Testing, security, and code quality experts.

**Specializations**:
- **Testing**: qa-expert, test-automator, accessibility-tester, chaos-engineer
- **Security**: backend-security-coder, frontend-security-coder, mobile-security-coder, security-auditor, penetration-tester
- **Review**: code-reviewer, architect-review, architect-reviewer
- **Compliance**: compliance-auditor, security-engineer
- **Quality**: debugger, error-detective, performance-engineer, tdd-orchestrator

### [05. Data & AI](05-data-ai/) (13 agents)
Data engineering, ML, and AI specialists.

**Focus Areas**:
- **AI/ML**: ai-engineer, ml-engineer, mlops-engineer, machine-learning-engineer
- **LLM**: llm-architect, prompt-engineer, nlp-engineer
- **Data**: data-engineer, data-scientist, data-analyst
- **Database**: database-optimizer, postgres-pro

### [06. Developer Experience](06-developer-experience/) (15 agents)
Tooling and developer productivity experts.

**Capabilities**:
- **Documentation**: documentation-engineer, docs-architect, reference-builder, tutorial-engineer
- **Tools**: build-engineer, cli-developer, tooling-engineer, mcp-developer
- **Workflow**: git-workflow-manager, dependency-manager, dx-optimizer
- **Refactoring**: refactoring-specialist, legacy-modernizer
- **Visualization**: mermaid-expert

### [07. Specialized Domains](07-specialized-domains/) (27 agents)
Domain-specific technology experts.

**Domains**:
- **Blockchain**: blockchain-developer
- **Finance**: fintech-engineer, payment-integration, quant-analyst
- **Gaming**: game-developer, unity-developer, minecraft-bukkit-pro
- **Mobile**: mobile-app-developer, ios-developer
- **IoT/Embedded**: iot-engineer, embedded-systems
- **SEO** (10 agents): seo-specialist, seo-content-writer, seo-meta-optimizer, seo-keyword-strategist, seo-content-auditor, seo-structure-architect, seo-authority-builder, seo-cannibalization-detector, seo-content-refresher, seo-snippet-hunter
- **Support**: customer-support, api-documenter

### [08. Business & Product](08-business-product/) (15 agents)
Product management and business analysis.

**Roles**:
- **Product**: product-manager, project-manager, scrum-master
- **Analysis**: business-analyst, ux-researcher
- **Documentation**: technical-writer
- **Customer**: customer-success-manager
- **Sales**: sales-engineer, sales-automator
- **Legal/HR**: legal-advisor, hr-pro
- **Marketing**: content-marketer
- **Design**: ui-ux-designer, ui-designer, ui-visual-validator

### [09. Meta & Orchestration](09-meta-orchestration/) (9 agents)
Agent coordination and meta-programming.

**Coordination**:
- **Orchestration**: multi-agent-coordinator, workflow-orchestrator, agent-organizer
- **Management**: task-distributor, context-manager, performance-monitor
- **Intelligence**: knowledge-synthesizer, error-coordinator

### [10. Research & Analysis](10-research-analysis/) (7 agents)
Research, search, and analysis specialists.

**Capabilities**:
- **Research**: research-analyst, data-researcher
- **Market**: market-researcher, competitive-analyst, trend-analyst
- **Search**: search-specialist

## 🛠️ Usage Guide

### Setting Up Subagents

**Global Installation** (available across all projects):
```bash
cp -r /home/cafe99/agent-categories/* ~/.claude/agents/
```

**Project-Specific Installation**:
```bash
cp -r /home/cafe99/agent-categories/* /path/to/project/.claude/agents/
```

### Invoking Subagents

**Automatic Invocation** (Claude decides):
```
> Optimize the authentication system for security
# Claude automatically invokes backend-security-coder
```

**Manual Invocation**:
```
> Ask the cloud-architect agent to review our infrastructure
> Have code-reviewer analyze the latest pull request
```

**Command-Line Access**:
```bash
/agents  # Open agent manager in Claude Code
```

## 📖 Subagent Structure

All agents follow the **operational workflow format**:

```yaml
---
name: agent-name
description: Comprehensive capability description with use cases
tools: MCP tool integrations (Read, Write, Bash, etc.)
---

Role definition and expertise overview

When invoked:
1. Context gathering steps
2. Analysis procedures
3. Implementation approach
4. Quality validation

## MCP Tool Suite
Detailed tool descriptions and usage patterns

## Communication Protocol
Inter-agent communication specifications with JSON examples

## Development Workflow
Structured phases with checklists and progress tracking

Integration with other agents:
Cross-agent collaboration patterns
```

## 🎯 Format Advantages

**Why Operational Workflow Format?**

✅ **MCP Integration**: Direct tool access specifications
✅ **Structured Communication**: JSON-based inter-agent protocols
✅ **Clear Workflows**: Phase-based development processes
✅ **Context Awareness**: Context manager integration
✅ **Collaboration**: Explicit cross-agent coordination
✅ **Production-Ready**: Comprehensive checklists and validation

**Compared to Basic Format**:
- 95% more content on average
- Structured workflow phases vs. freeform descriptions
- MCP tool specifications vs. generic capabilities
- Communication protocols vs. basic interactions
- ~280 lines vs. ~165 lines average

## 🔍 Finding the Right Agent

**By Task Type**:
- Building APIs → api-designer, backend-developer, graphql-architect
- Frontend work → frontend-developer, react-specialist, vue-expert
- Security review → backend/frontend/mobile-security-coder, security-auditor
- Performance → performance-engineer, database-optimizer
- Testing → qa-expert, test-automator, accessibility-tester
- DevOps → devops-engineer, sre-engineer, kubernetes-specialist
- AI/ML → ai-engineer, ml-engineer, llm-architect
- Documentation → technical-writer, documentation-engineer, api-documenter

**By Language**:
- Python → python-pro, django-developer, fastapi-pro
- JavaScript/TypeScript → javascript-pro, typescript-pro, nextjs-developer
- Java → java-architect, spring-boot-engineer
- Go → golang-pro
- Rust → rust-engineer, rust-pro
- And 20+ more language specialists

**By Platform**:
- Cloud → cloud-architect, hybrid-cloud-architect
- Mobile → mobile-developer, ios-developer, flutter-expert
- Web → wordpress-master, django-developer, rails-expert
- Desktop → electron-pro
- Gaming → unity-developer, game-developer

## 🤝 Agent Collaboration

Many agents are designed to work together:

**Example Workflows**:

**Full-Stack Feature**:
1. architect-review → System design
2. backend-developer → API implementation
3. frontend-developer → UI implementation
4. qa-expert → Testing strategy
5. devops-engineer → Deployment

**Security Audit**:
1. security-auditor → Vulnerability assessment
2. backend-security-coder → Server-side fixes
3. frontend-security-coder → Client-side fixes
4. penetration-tester → Validation
5. compliance-auditor → Compliance verification

**Cloud Migration**:
1. cloud-architect → Architecture design
2. terraform-engineer → Infrastructure as Code
3. kubernetes-specialist → Container orchestration
4. database-administrator → Data migration
5. sre-engineer → Reliability setup

## 📊 Quality Standards

All agents meet these criteria:

✅ **Production-Ready**: Tested in real-world scenarios
✅ **Best Practices**: Following industry standards
✅ **MCP Integrated**: Leveraging Model Context Protocol
✅ **Well-Documented**: Clear descriptions and workflows
✅ **Context-Aware**: Integration with context manager
✅ **Collaborative**: Cross-agent coordination support

## 🔧 Customization

You can customize agents for your needs:

1. **Edit System Prompts**: Press `e` in agent manager
2. **Modify Tool Access**: Adjust tools list in YAML frontmatter
3. **Add Custom Workflows**: Extend development workflow sections
4. **Configure Integrations**: Customize communication protocols

## 📝 Contributing

To add or improve agents:

1. Follow the operational workflow format
2. Include comprehensive MCP tool specifications
3. Add structured communication protocols
4. Document development workflow phases
5. Specify integration with related agents
6. Test in production scenarios

## 🔗 Related Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [VoltAgent Framework](https://github.com/voltagent/voltagent)

## 📄 License

MIT License - Open for commercial and personal use

---

<div align="center">

**169 Production-Ready Subagents** | **10 Specialized Categories** | **MCP Integrated** | **Claude Code Optimized**

*Maintained for professional AI-assisted development*

</div>
