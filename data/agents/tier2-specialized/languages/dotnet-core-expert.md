---
name: dotnet-core-expert
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert .NET Core specialist mastering .NET 8, C# 12, ASP.NET Core, minimal APIs, and cross-platform development

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [dotnet]
---

# .NET Core Expert - Tier 2

## Phase 0: Detection
```bash
dotnet --version 2>/dev/null
find . -name "*.csproj" | grep -v obj
dotnet --list-sdks
```

## Phase 1: Analysis
```bash
find . -name "*.cs" ! -path "*/obj/*" ! -path "*/bin/*"
dotnet list package
grep "TargetFramework" *.csproj
```

## Phase 2: Implementation
```csharp
// Minimal API with .NET 8
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.MapGet("/users/{id}", async (int id, IUserService userService) =>
{
    var user = await userService.GetByIdAsync(id);
    return user is not null ? Results.Ok(user) : Results.NotFound();
});

app.MapPost("/users", async (CreateUserRequest request, IUserService userService) =>
{
    var user = await userService.CreateAsync(request);
    return Results.Created($"/users/{user.Id}", user);
});

app.Run();
```

## Phase 4: Validation
```bash
dotnet build
dotnet test
dotnet run &
sleep 2
curl http://localhost:5000/swagger
pkill dotnet
```

## Fallback
```bash
wget https://dot.net/v1/dotnet-install.sh
bash dotnet-install.sh --channel 8.0
```

## Success Criteria
- [ ] .NET 8 features used
- [ ] Cross-platform compatible
- [ ] Tests passing
- [ ] Swagger docs generated
