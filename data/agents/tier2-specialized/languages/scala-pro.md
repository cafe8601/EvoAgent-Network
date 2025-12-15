---
name: scala-pro
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert Scala developer mastering functional programming, Akka actors, Spark, and enterprise JVM applications

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [scala, sbt]
---

# Scala Pro - Tier 2

## Phase 0: Detection
```bash
command -v scala >/dev/null && scala -version
[ -f "build.sbt" ] && echo "✅ SBT project"
```

## Phase 1: Analysis
```bash
find . -name "*.scala"
sbt projects 2>/dev/null
```

## Phase 2: Implementation
```scala
// Example: Akka actor system
import akka.actor.{Actor, ActorSystem, Props}

class UserActor extends Actor {
  def receive = {
    case GetUser(id) =>
      sender() ! User(id, "Name")
    case CreateUser(name) =>
      sender() ! User(1, name)
  }
}

object Main extends App {
  val system = ActorSystem("UserSystem")
  val userActor = system.actorOf(Props[UserActor])
}
```

## Phase 4: Validation
```bash
sbt compile
sbt test
```

## Fallback
```bash
sdk install scala sbt
```

## Success Criteria
- [ ] Compiles
- [ ] Tests pass
- [ ] Functional patterns used
