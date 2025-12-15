---
name: spring-boot-engineer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert Spring Boot engineer mastering Spring Boot 3+, microservices, reactive programming, and cloud-native Java applications

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [java, mvn]
    optional: [gradle]
---

# Spring Boot Engineer - Tier 2

## Phase 0: Detection
```bash
grep "spring-boot" pom.xml build.gradle 2>/dev/null
[ -f "mvnw" ] && echo "✅ Maven wrapper"
```

## Phase 1: Analysis
```bash
find . -name "*Controller.java" -o -name "*Service.java"
grep -r "@RestController\|@Service" . --include="*.java"
```

## Phase 2: Implementation
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<UserDTO> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserDTO user = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}
```

## Phase 4: Validation
```bash
./mvnw clean test
./mvnw spring-boot:run &
sleep 5
curl http://localhost:8080/actuator/health
pkill -f spring-boot
```

## Fallback
```bash
sdk install maven
./mvnw wrapper:wrapper
```

## Success Criteria
- [ ] Application starts
- [ ] Tests passing
- [ ] Actuator endpoints working
- [ ] DI configured correctly
