---
name: minecraft-bukkit-pro
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: Minecraft server plugin developer for Bukkit/Spigot/Paper APIs and gameplay mechanics"

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [mvn, java]
---

# Minecraft Bukkit Pro - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Highly specialized

## Phase 0: Detection
```bash
[ -f "plugin.yml" ] && echo "✅ Bukkit plugin"
grep -r "bukkit\|spigot\|paper" pom.xml 2>/dev/null
```

## Phase 1: Analysis
```bash
find . -path "*/src/main/java/*" -name "*.java"
grep -r "@EventHandler\|extends JavaPlugin" . --include="*.java"
```

## Phase 2: Implementation
```java
// Example: Bukkit plugin
package com.example.myplugin;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.Listener;
import org.bukkit.event.EventHandler;
import org.bukkit.event.player.PlayerJoinEvent;

public class MyPlugin extends JavaPlugin implements Listener {

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("MyPlugin enabled!");
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        event.getPlayer().sendMessage("Welcome to the server!");
    }
}
```

## Phase 4: Validation
```bash
mvn clean package
ls target/*.jar
# Test on server
```

## Success Criteria
- [ ] Plugin compiles
- [ ] Loads on server
- [ ] Events work
- [ ] No errors in console
