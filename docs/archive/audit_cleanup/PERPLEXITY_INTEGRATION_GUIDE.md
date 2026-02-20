# Perplexity Pro Integration Guide

## Setup

Your BROski Pantheon is now configured to use **Perplexity Pro** as the primary LLM.

### Environment

Make sure your `.env` has:

```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-xxx  # Optional fallback
```

### Model Comparison

| Feature | Perplexity Pro | Claude 3.5 | Local (smollm2) |
|---------|---|---|---|
| Context | 200K tokens | 8K tokens | 4K tokens |
| Speed | Fast | Fast | Very Fast (local) |
| Cost | $0.002/$0.01 | $0.003/$0.015 | Free (local) |
| Real-time web | ✅ Yes | ❌ No | ❌ No |
| Reasoning | ✅ Strong | ✅ Very Strong | ⚠️ Limited |
| Best for | Research, web-aware | Coding, complex tasks | Fast iteration |

---

## Why Perplexity for Your Agents

### BROski Orchestrator
- **Benefit:** Can search web for current best practices
- **Use case:** Planning feature additions, researching patterns
- **Cost:** ~$0.005 per task

### Language Specialist (HyperCode)
- **Benefit:** Large context (200K) for full codebase analysis
- **Use case:** Understanding HyperCode paradigm shifts
- **Cost:** ~$0.01 per analysis

### Frontend Specialist
- **Benefit:** Up-to-date with latest React/Next.js patterns
- **Use case:** Finding new UI component libraries
- **Cost:** ~$0.008 per task

### Backend Specialist
- **Benefit:** Latest API design patterns
- **Use case:** Optimizing database queries, API architecture
- **Cost:** ~$0.01 per task

### Security Specialist
- **Benefit:** Real-time CVE database access
- **Use case:** Checking for latest vulnerabilities
- **Cost:** ~$0.01 per audit

### QA Specialist
- **Benefit:** Can research testing frameworks
- **Use case:** Staying current with testing best practices
- **Cost:** ~$0.008 per task

### Observability Specialist
- **Benefit:** Latest monitoring tools + patterns
- **Use case:** Setting up Prometheus/Grafana best practices
- **Cost:** ~$0.01 per task

---

## Cost Calculation

**Per agent per task:** ~$0.005-0.015  
**7 agents, 10 tasks each:** ~$0.35-1.05 per session  
**Daily (5 sessions):** ~$1.75-5.25  
**Monthly:** ~$50-150

**Compare to:**
- Claude only: $150-300/month
- Anthropic Pro: $20 + overage
- Your Perplexity Pro: $20/month unlimited

✅ **You get best-in-class + unlimited for $20/month**

---

## Hybrid Strategy (Recommended)

Use Perplexity for most tasks, fall back to local models when:

```yaml
# In cagent-pantheon.yaml

agents:
  language-specialist:
    # Primary: Perplexity (research, web-aware, large context)
    model: "perplexity-pro"
    
    # Fallback: Local model if Perplexity is down
    fallback_model: "smollm2"
    
    # Cost-aware: Use local for simple validation
    routing:
      parse_hypercode: "smollm2"  # Simple parsing → fast local
      validate_hypercode: "smollm2"  # Validation → fast local
      complex_analysis: "perplexity-pro"  # Research → web-aware
```

---

## Testing Your Setup

### Test 1: Perplexity is working

```bash
export PERPLEXITY_API_KEY=pplx-xxx
docker run -v $(pwd):/app \
  -e PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY \
  docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml
```

Give BROski a task:
```
"Research the best practices for building DSLs. Summarize in 3 points."
```

Expected: BROski searches web, returns current best practices.

### Test 2: Local fallback works

```bash
docker model pull smollm2
```

Then give BROski:
```
"Check this HyperCode syntax: print('hello')"
```

Expected: Uses local model (instant, no API call).

### Test 3: Cost tracking

BROski should report:
```
Cost this session: $0.02
Tokens used: 1200 in / 800 out
Remaining budget: $19.98/month
```

---

## Monitoring Perplexity Usage

Add to your observability dashboard:

```yaml
# monitoring/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'perplexity-usage'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/perplexity'
```

Track:
- API calls per agent
- Cost per task
- Fallback usage (when local model is used)
- Error rates

---

## Troubleshooting

### "Invalid API Key"
```bash
# Check your key is set
echo $PERPLEXITY_API_KEY

# Make sure it starts with 'pplx-'
# Get from: https://www.perplexity.ai/account/api
```

### "Rate limited"
```bash
# Perplexity Pro allows ~1000 requests/day
# If hitting limit, use local model for non-critical tasks

# Or space out requests:
# Add delay: sleep 1 between agent calls
```

### "Context too long"
```bash
# Perplexity has 200K token limit
# If agent fails:
# 1. Summarize input first
# 2. Use smaller files
# 3. Fall back to smollm2 for this task
```

---

## Advanced: Model Router

Automatically choose best model per task:

```yaml
# In cagent-pantheon.yaml

model_router:
  rules:
    - task: "parse_*"
      model: "smollm2"  # Fast, local
      reason: "Simple parsing doesn't need web access"
    
    - task: "research_*"
      model: "perplexity-pro"  # Web-aware
      reason: "Research needs current web info"
    
    - task: "validate_*"
      model: "smollm2"  # Fast, local
      reason: "Validation is deterministic"
    
    - task: "*"
      model: "perplexity-pro"  # Default
      reason: "Use Pro for complex tasks"

cost_tracking:
  monthly_budget: 20.0  # Your Perplexity Pro plan
  warn_at: 18.0  # Warn when using 90%
  cutoff_at: 19.5  # Fall back to local only
```

---

## Your Setup Now

```
┌─────────────────────────────┐
│ BROski Pantheon 2.0         │
│ with Perplexity Pro         │
└────────────┬────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    v                 v
┌─────────────┐  ┌──────────────┐
│ Perplexity  │  │ Local Models │
│ Pro         │  │ (smollm2)    │
│ $20/month   │  │ Free         │
│ 200K ctx    │  │ 4K ctx       │
│ Web-aware   │  │ Instant      │
└─────────────┘  └──────────────┘
```

Agents route tasks to best model automatically.

---

## Next Steps

1. ✅ Set `PERPLEXITY_API_KEY` in `.env`
2. ✅ Pull local model: `docker model pull smollm2`
3. ✅ Test with: `docker run ... docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml`
4. ✅ Monitor costs (should be $20/month or less)
5. ✅ Celebrate: You now have cutting-edge agents for less than a coffee ☕

---

**Your agents are now powered by Perplexity Pro + local models.**

Questions? Let me know!
