---
name: game-developer
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: Expert game developer specializing in game engines, graphics, multiplayer, and cross-platform game development"

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [unity, godot, npm]
---

# Game Developer - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Game development is highly specialized

## Phase 0: Detection
```bash
find . -name "*.unity" -o -name "project.godot" -o -name "package.json"
find . -name "*.cs" -path "*/Assets/Scripts/*"
```

## Phase 1: Analysis
```bash
# Find game scripts
find . -name "*.cs" -o -name "*.gd" -o -name "*.js" | grep -E "game|player|enemy"

# Check game engine
[ -d "Assets" ] && echo "Unity project"
[ -f "project.godot" ] && echo "Godot project"
```

## Phase 2: Implementation
```csharp
// Example: Unity game controller
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;

    private Rigidbody2D rb;
    private bool isGrounded;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    void Update()
    {
        // Movement
        float moveX = Input.GetAxis("Horizontal");
        rb.velocity = new Vector2(moveX * moveSpeed, rb.velocity.y);

        // Jump
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse);
        }
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
    }

    void OnCollisionExit2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = false;
        }
    }
}
```

## Phase 4: Validation
```bash
# Unity (GUI required)
# Godot
godot --export "Linux/X11" game.x86_64 2>/dev/null
```

## ⚠️ Limitations
- Most game engines require GUI
- Asset creation needs specialized tools
- Performance testing needs target hardware

## Success Criteria
- [ ] Game runs
- [ ] Gameplay mechanics working
- [ ] Frame rate stable (60fps)
- [ ] Build successful
