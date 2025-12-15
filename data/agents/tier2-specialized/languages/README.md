# Tier 2: Language Specialists

Expert developers for specific programming languages beyond Tier 1 coverage.

## Available Agents

### Completed ✅
- **rust-pro.md** - Systems programming, memory safety, zero-cost abstractions
- **golang-pro.md** - Concurrent systems, microservices, cloud-native
- **java-pro.md** - Enterprise Java, Spring Boot, virtual threads

### To Be Added (On-Demand)
- **csharp-pro.md** - .NET, C# 12+, async/await
- **kotlin-specialist.md** - Kotlin, coroutines, multiplatform
- **scala-pro.md** - Functional programming, Akka, Spark
- **ruby-pro.md** - Ruby, Rails, metaprogramming
- **php-pro.md** - Modern PHP 8.3+, Laravel, Symfony
- **swift-expert.md** - iOS/macOS development
- **c-pro.md** - Systems programming, embedded
- **cpp-pro.md** - Modern C++20/23, performance
- **elixir-pro.md** - Elixir, OTP, Phoenix
- **sql-pro.md** - Advanced SQL, query optimization

## Usage

```bash
# Use existing
invoke_agent("tier2-specialized/languages/rust-pro")

# Request missing
"I need C++ development" → Will create cpp-pro.md on-demand
```

## Creating New Language Agent

```bash
cp ../../_templates/tier2-template.md ./new-language-pro.md
# Fill in language-specific details
# Validate if promoting to Tier 1
```
