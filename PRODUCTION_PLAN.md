# Community LLM - Production Plan

## Executive Summary

Build a production-ready community LLM platform where:
- **Contributors** run agents, get paid credits for compute
- **Users** pay credits to query the LLM  
- **Operator** covers costs + profit

---

## 1. Hardware Assessment

**Current Resources:**
- Storage: 374GB available (plenty for model checkpoints)
- No GPU currently detected in this environment

**Requirements:**
- GPU server (8x A100 or equivalent) for inference serving
- Estimated cost: $500-2000/month for cloud GPU
- Alternative: Use user's own GPUs via the agent network

---

## 2. Tokenomics & Pricing

### Credit System
| Metric | Value |
|--------|-------|
| **1 credit** | $0.01 USD |
| **Query cost** | 10 credits (10¢) for 100 tokens |
| **Agent reward** | 5-50 credits/task (based on compute) |

### Profit Calculation
```
Monthly Costs (cloud GPU):
- 1x A100 (80GB): ~$800/month
- Bandwidth: ~$50/month
- Infrastructure: ~$100/month
- Total: ~$950/month

Revenue Needed:
- Break-even: 95,000 queries/month (3,167/day)
- Profit (20%): 114,000 queries/month (3,800/day)

Pricing Tiers:
- Pay-per-query: 10¢/100 tokens
- Subscription: $9.99/month (unlimited 10k tokens)
- API access: $49/month (100k tokens)
```

### Agent Rewards
| Task Type | Credits | Cost to Operator |
|-----------|---------|------------------|
| Simple inference | 1-5 | $0.01-0.05 |
| Training step | 20-100 | $0.20-1.00 |
| Data contribution | 10-50 | $0.10-0.50 |

---

## 3. Technical Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                         │
│  (Website, API, Telegram Bot, Discord Bot)               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY                            │
│  (FastAPI + Authentication + Rate Limiting)              │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   INFERENCE ENGINE     │    │   COORDINATOR         │
│   (vLLM + Qwen)       │    │   (Task Queue)        │
│                       │    │                       │
│   - Serve model       │    │   - Agent registry    │
│   - Track usage      │    │   - Task distribution│
│   - Bill users       │    │   - Credit ledger    │
└─────────────────────────┘    └─────────────────────────┘
              ▲                             ▲
              │                             │
              └──────────────┬──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT NETWORK                          │
│  (Contributors running training/p inference tasks)        │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    credits INTEGER DEFAULT 100,
    total_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP
);

-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    pubkey TEXT UNIQUE,
    total_earned INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    reputation_score REAL DEFAULT 1.0,
    status TEXT DEFAULT 'active'
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID,
    agent_id UUID,
    type TEXT, -- 'query', 'reward', 'withdrawal'
    credits INTEGER,
    tx_hash TEXT,
    created_at TIMESTAMP
);
```

---

## 4. Smart Contract (Base Network)

### Token: `COMMUNITY_LLM`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract CommunityLLM is ERC20 {
    mapping(address => uint256) public earnedCredits;
    mapping(address => uint256) public burnedCredits;
    
    uint256 public constant MIN_WITHDRAWAL = 100e18; // 100 tokens
    
    event TaskCompleted(address indexed agent, uint256 credits);
    event QueryMade(address indexed user, uint256 credits);
    
    function mintForTask(address agent, uint256 amount) external onlyOwner {
        _mint(agent, amount);
        earnedCredits[agent] += amount;
        emit TaskCompleted(agent, amount);
    }
    
    function burnForQuery(address user, uint256 amount) external onlyOwner {
        _burn(user, amount);
        burnedCredits[user] += amount;
        emit QueryMade(user, amount);
    }
}
```

---

## 5. Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
| Day | Task |
|-----|------|
| 1 | Deploy coordinator API with real database (PostgreSQL) |
| 2 | Set up vLLM with Qwen2.5-2B for inference |
| 3 | Build user registration + credit system |
| 4 | Create agent registration with cryptographic keys |
| 5 | Implement basic query flow (user → credits → inference) |

### Phase 2: Agent Network (Week 2)
| Day | Task |
|-----|------|
| 1 | Build agent Docker image with LoRA training capability |
| 2 | Implement task distribution (coordinator → agents) |
| 3 | Create credit reward system for completed tasks |
| 4 | Add agent reputation tracking |
| 5 | Deploy test agents (3-5 contributors) |

### Phase 3: Payments & Tokens (Week 3)
| Day | Task |
|-----|------|
| 1 | Deploy ERC-20 token on Base |
| 2 | Integrate x402 for fiat payments |
| 3 | Build withdrawal system (credits → token → fiat/crypto) |
| 4 | Add subscription tiers |
| 5 | Test full payment flow |

### Phase 4: Governance (Week 4)
| Day | Task |
|-----|------|
| 1 | Implement governance token |
| 2 | Create proposal system |
| 3 | Build voting mechanism |
| 4 | Add contributor rewards (bonus credits for governance) |
| 5 | Launch public beta |

### Phase 5: Scale (Ongoing)
- Add more GPU capacity
- Optimize token economics
- Marketing & user acquisition
- Partnership integrations

---

## 6. Cost Analysis

### Monthly Operating Costs
| Item | Cost |
|------|------|
| GPU Inference (cloud) | $800 |
| Database | $50 |
| Domain/API | $25 |
| Bandwidth | $50 |
| Monitoring | $25 |
| **Total** | **$950** |

### Revenue Projections
| Scenario | Queries/Day | Monthly Revenue | Profit |
|----------|-------------|-----------------|--------|
| Conservative | 1,000 | $300 | -$650 |
| Moderate | 5,000 | $1,500 | $550 |
| Target | 10,000 | $3,000 | $2,050 |
| Optimistic | 50,000 | $15,000 | $14,050 |

---

## 7. Key Metrics to Track

- **Daily Active Users (DAU)**
- **Daily Active Agents**
- **Average Query Cost** 
- **Agent Earnings Rate**
- **User Retention**
- **Net Promoter Score (NPS)**

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Low user adoption | High | High | Marketing, influencer partnerships |
| GPU costs too high | Medium | High | Use community GPU network |
| Token volatility | Medium | Medium | Stablecoin-backed credits |
| Regulatory | Low | High | Legal counsel, KYC/AML |

---

## 9. Immediate Next Steps

1. **Get GPU server** - Rent cloud GPU or use existing hardware
2. **Deploy vLLM** - Get Qwen2.5-2B running for inference
3. **Build API** - User auth, credits, query endpoint
4. **Test internally** - Run 100 queries, verify flow
5. **Launch beta** - Invite 10 users, 5 agents
6. **Iterate** - Fix issues, optimize pricing

---

## Summary

| Metric | Value |
|--------|-------|
| **Target users** | 10,000 daily |
| **Target agents** | 100 active |
| **Query price** | 10¢ / 100 tokens |
| **Break-even** | 3,200 queries/day |
| **Profit margin** | ~70% after costs |

This is a viable business. The key is getting the flywheel spinning: users → revenue → more agents → better model → more users.

---

Want me to start building Phase 1?
