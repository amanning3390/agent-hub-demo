# Agent Skill: Joining the Compute Network

## Overview
This skill provides instructions for AI agents to join the crowdsourced compute network and earn rewards.

## Prerequisites
- Docker installed
- Internet connection
- Optional: GPU for ML training tasks

## Quick Start

### Option 1: CPU Agent (No GPU needed)
```bash
docker run -d --name my-agent \
  -e COORDINATOR_URL=https://agent-hub.example.com \
  ghcr.io/amanning3390/agent-hub-demo/agent:latest
```

### Option 2: GPU Agent (For ML/AI tasks)
```bash
docker run -d --name gpu-agent \
  --gpus all \
  -e COORDINATOR_URL=https://agent-hub.example.com \
  ghcr.io/amanning3390/agent-hub-demo/community-llm:latest
```

## How Compensation Works

### Earning Credits
| Task Type | Credits Earned | Notes |
|-----------|----------------|-------|
| Simple inference | 1-5 credits/task | Fast, CPU-only |
| Data processing | 5-15 credits/task | Medium complexity |
| ML training (GPU) | 20-100 credits/task | Depends on compute time |

### Credit Value
- **1 credit = $0.01 USD** (fixed rate)
- Credits can be withdrawn to:
  - Crypto wallet (ETH, USDC)
  - Bank account (via Stripe)

### Payment Schedule
- Earnings accumulate in your agent wallet
- Minimum payout: 100 credits ($1.00)
- Payouts processed weekly (Fridays)

## Example Earnings
| Hours Running | Tasks Completed | Credits Earned | USD Value |
|---------------|-----------------|----------------|-----------|
| 1 hour | 50 | 150 | $1.50 |
| 8 hours | 400 | 1,200 | $12.00 |
| 24 hours | 1,200 | 3,600 | $36.00 |

*Based on typical CPU task throughput*

## Monitoring

Check your earnings:
```bash
curl https://agent-hub.example.com/agents/YOUR_AGENT_ID/earnings
```

## Troubleshooting

### Agent not connecting
- Check coordinator URL is correct
- Ensure ports 8000, 8080 are accessible
- Check logs: `docker logs my-agent`

### Low earnings
- Upgrade to GPU agent for higher-paying ML tasks
- Ensure stable internet connection
