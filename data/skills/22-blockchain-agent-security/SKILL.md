---
name: blockchain-agent-security
description: Provides comprehensive guidance for implementing secure blockchain-based identity, reputation, and credential systems for AI agents. Covers ZK proofs (Circom circuits), cross-chain identity (LayerZero), smart contract security patterns, and incident response. Use when building decentralized agent identity, implementing on-chain reputation systems, verifying agent credentials with ZK proofs, or deploying multi-chain agent infrastructure.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Blockchain, Security, ZK-Proofs, Smart-Contracts, Multi-Agent, Cross-Chain, Identity]
dependencies: [snarkjs>=0.7.0, circomlibjs>=0.1.0, ethers>=6.0.0, hardhat>=2.19.0]
---

# Blockchain Agent Security

## Overview

Enterprise-grade security infrastructure for AI agent systems on blockchain. Provides on-chain identity verification, ZK-proof based credentials, cross-chain reputation sync, and production-hardened security patterns.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BLOCKCHAIN AGENT SECURITY STACK                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Identity Layer    →  2. Credential Layer  →  3. Reputation Layer        │
│     Agent Registry        ZK Proofs (Circom)      On-chain Scoring          │
│                                                                              │
│  4. Cross-Chain       →  5. Security           →  6. Incident Response      │
│     LayerZero Bridge      Circuit Breakers         Automated Recovery        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use This Skill

**Trigger this skill when:**
- Building decentralized AI agent identity systems
- Implementing on-chain agent reputation and staking
- Creating ZK proofs for agent credential verification
- Deploying multi-chain agent infrastructure
- Designing security patterns for agent smart contracts
- Setting up monitoring and incident response for agent systems
- Integrating blockchain identity with multi-agent orchestrators

## Core Concepts (~50 tokens)

### Agent Identity Architecture
- **On-chain Registry**: Solidity contracts for agent registration
- **Key Management**: Owner keys, operator keys, recovery addresses
- **Trust Tiers**: Graduated trust levels (0-4) based on reputation
- **Metadata Hashing**: Off-chain metadata with on-chain commitment

### Zero-Knowledge Proofs
- **Circom Circuits**: Privacy-preserving credential verification
- **Capability Proofs**: Prove agent has capability without revealing details
- **Reputation Range**: Prove score is within range without exact value
- **Nullifiers**: Prevent double-use of credentials

### Security Patterns
- **Circuit Breaker**: Automatic pause on anomaly detection
- **Time-locked Upgrades**: Multi-sig with delay for critical changes
- **Rate Limiting**: Per-block and per-hour operation limits
- **Emergency Mode**: Global pause with 24-hour auto-recovery

→ Load L2 for ZK circuit implementations and cross-chain patterns
→ Load L3 for production deployment and incident response

## Quick Start

### 1. Deploy Agent Identity Registry

```solidity
// Simplified AgentIdentityRegistry
contract AgentIdentityRegistry {
    struct Agent {
        address owner;
        address operatorKey;
        bytes32 metadataHash;
        uint256 createdAt;
        bool isActive;
        uint8 trustTier;
    }

    mapping(bytes32 => Agent) public agents;

    function registerAgent(
        bytes32 agentId,
        bytes32 metadataHash,
        address[] calldata recoveryAddresses
    ) external {
        require(!agents[agentId].isActive, "Already registered");
        agents[agentId] = Agent({
            owner: msg.sender,
            operatorKey: msg.sender,
            metadataHash: metadataHash,
            createdAt: block.timestamp,
            isActive: true,
            trustTier: 0
        });
    }
}
```

### 2. ZK Capability Proof (Circom)

```circom
template AgentCapabilityProof() {
    signal input nullifier;           // Public: prevents double-use
    signal input capabilityCommitment; // Public: commitment to capability
    signal input minTrustLevel;        // Public: required trust level

    signal input agentId;              // Private
    signal input trustLevel;           // Private
    signal input credentialSecret;     // Private

    // Verify commitment
    component hash = Poseidon(3);
    hash.inputs[0] <== agentId;
    hash.inputs[1] <== capabilityType;
    hash.inputs[2] <== credentialSecret;
    hash.out === capabilityCommitment;

    // Verify trust level meets minimum
    component check = GreaterEqThan(8);
    check.in[0] <== trustLevel;
    check.in[1] <== minTrustLevel;
    check.out === 1;
}
```

### 3. Reputation System with Staking

```solidity
contract AgentReputationSystem {
    struct Reputation {
        uint256 totalScore;
        uint256 stakedAmount;
        uint256 successfulTasks;
        uint256 failedTasks;
    }

    mapping(bytes32 => Reputation) public reputations;

    function stake(bytes32 agentId) external payable {
        reputations[agentId].stakedAmount += msg.value;
    }

    function slash(bytes32 agentId, uint256 severity) external {
        uint256 penalty = (reputations[agentId].stakedAmount * severity) / 100;
        reputations[agentId].stakedAmount -= penalty;
        reputations[agentId].totalScore =
            reputations[agentId].totalScore > penalty ?
            reputations[agentId].totalScore - penalty : 0;
    }
}
```

## Security Checklist

### Smart Contract Security
- [ ] Reentrancy guards on all external calls
- [ ] Access control on admin functions
- [ ] Rate limiting on sensitive operations
- [ ] Emergency pause capability
- [ ] Timelock on upgrades (min 48h)

### ZK Circuit Security
- [ ] Nullifier prevents double-use
- [ ] Commitment scheme is binding
- [ ] Range proofs properly constrained
- [ ] No information leakage

### Operational Security
- [ ] Multi-sig for admin operations
- [ ] Monitoring and alerting active
- [ ] Incident response playbooks ready
- [ ] Regular security audits scheduled

## Integration with Multi-Agent Systems

```typescript
// Hook for multi-agent orchestrator
const blockchainHook = new BlockchainAgentHook();

orchestrator.on("agent:spawn", async (agent) => {
    await blockchainHook.registerAgent(agent);
});

orchestrator.on("task:complete", async (agentId, result) => {
    await blockchainHook.updateReputation(agentId, result);
});

// Verify credentials before sensitive operations
orchestrator.addMiddleware("sensitive", async (ctx, next) => {
    const verified = await blockchainHook.verifyCredentials(ctx.agentId);
    if (!verified) throw new Error("Credentials verification failed");
    return next();
});
```

## References

→ [`levels/L2.md`](levels/L2.md) - ZK circuits, cross-chain identity, advanced patterns
→ [`levels/L3.md`](levels/L3.md) - Production deployment, monitoring, incident response

**Related Skills:**
- `21-multiagent-learning-system` - Multi-agent orchestration integration
- `14-agents/langchain` - Agent framework integration

---

**Version:** 1.0.0
**Complexity:** Advanced
**Output:** Secure blockchain infrastructure for AI agent systems
