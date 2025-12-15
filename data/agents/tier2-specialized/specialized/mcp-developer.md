---
name: mcp-developer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: MCP developer for Model Context Protocol server/client development and AI system integrations

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [npm, python3]
---

# MCP Developer - Tier 2

## Phase 0: Detection
```bash
find . -name "mcp-server.ts" -o -name "mcp_server.py"
grep -r "@modelcontextprotocol/sdk" package.json 2>/dev/null
```

## Phase 1: Analysis
```bash
find . -path "*/src/mcp/*" -name "*.ts"
grep -r "McpServer\|Tool\|Resource" . --include="*.{ts,py}"
```

## Phase 2: Implementation
```typescript
// Example: MCP server with tools
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  {
    name: "my-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define tool
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "get_weather",
        description: "Get weather for a location",
        inputSchema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "City name"
            }
          },
          required: ["location"]
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "get_weather") {
    const location = request.params.arguments?.location;
    // Fetch weather data
    return {
      content: [
        {
          type: "text",
          text: `Weather in ${location}: Sunny, 72°F`
        }
      ]
    };
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Phase 4: Validation
```bash
# Test MCP server
node mcp-server.js

# Test with Claude Code
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node mcp-server.js
```

## Success Criteria
- [ ] MCP server running
- [ ] Tools functional
- [ ] Resources accessible
- [ ] Error handling complete
- [ ] Integration working
