---
name: csharp-developer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: C# developer for general .NET development, Windows applications, and enterprise solutions

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [dotnet]
---

# C# Developer - Tier 2

## Phase 0: Detection
```bash
find . -name "*.cs" ! -path "*/obj/*" ! -path "*/bin/*"
dotnet --version 2>/dev/null
```

## Phase 1: Analysis
```bash
grep -r "class \|interface \|namespace " . --include="*.cs" | head -20
dotnet list package 2>/dev/null
```

## Phase 2: Implementation
```csharp
// Example: Console application
using System;
using System.Threading.Tasks;

namespace MyApp
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("Starting application...");

            try
            {
                await RunApplicationAsync();
                Console.WriteLine("Completed successfully");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static async Task RunApplicationAsync()
        {
            // Application logic
            await Task.Delay(1000);
        }
    }
}
```

## Phase 4: Validation
```bash
dotnet build
dotnet run
dotnet test
```

## Success Criteria
- [ ] Builds successfully
- [ ] Runs without errors
- [ ] Tests passing
- [ ] C# conventions followed
