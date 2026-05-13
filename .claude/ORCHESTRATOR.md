# ORCHESTRATOR.md - SuperClaude Routing

## Resource Thresholds
| Zone | Usage | Action |
|------|-------|--------|
| Green | 0-60% | Full ops |
| Yellow | 60-75% | Optimize, suggest --uc |
| Orange | 75-85% | Warn, defer non-critical |
| Red | 85-95% | Force efficiency, block heavy ops |
| Critical | 95%+ | Emergency, essential only |

## Routing Table
| Pattern | Complexity | Auto-Activates |
|---------|------------|----------------|
| analyze architecture | complex | architect, --ultrathink, Sequential |
| create component | simple | frontend, Magic, --uc |
| implement API | moderate | backend, --seq, Context7 |
| implement UI | simple | frontend, Magic, --c7 |
| implement auth | complex | security+backend, --validate |
| fix bug | moderate | analyzer, --think, Sequential |
| optimize performance | complex | performance, --think-hard, Playwright |
| security audit | complex | security, --ultrathink, Sequential |
| write documentation | moderate | scribe, Context7 |
| large codebase | complex | --delegate --parallel-dirs |
| comprehensive audit | complex | --wave-mode --wave-validation |
| improve large system | complex | --wave-mode --adaptive-waves |

## Auto-Activation
- Performance issues → --persona-performance + --focus performance + --think
- Security concerns → --persona-security + --focus security + --validate
- UI/UX tasks → --persona-frontend + --magic + --c7
- Complex debugging → --think + --seq + --persona-analyzer
- Context >75% → --uc + --delegate auto
- Testing → --persona-qa + --play + --validate
- DevOps → --persona-devops + --safe-mode + --validate
- Refactoring → --persona-refactorer + --wave-strategy systematic
- Iterative (polish/refine/enhance) → --loop

## Wave Activation
- Auto: complexity ≥0.7 AND files >20 AND operation_types >2
- Enterprise: files >100 AND complexity >0.7 AND domains >2 → --wave-strategy enterprise
- Security/critical → --wave-validation default
- Flags: --wave-mode [auto|force|off], --wave-strategy [progressive|systematic|adaptive|enterprise]
- Scoring: complexity(0.2-0.4) + scale(0.2-0.3) + operations(0.2) + domains(0.1) ≥ 0.7 → activate

## Sub-Agent Delegation
- >50 files → --delegate files | >7 dirs → --delegate folders
- >3 domains → --parallel-focus | complexity >0.8 → --focus-agents
- estimated tokens >20K → --aggregate-results

## Flag Precedence
1. --safe-mode > optimization flags
2. Explicit > auto-activation
3. --ultrathink > --think-hard > --think
4. --no-mcp > individual MCP flags
5. system > project > module > file (scope)
6. Last persona takes precedence
7. --wave-mode off > force > auto
8. explicit --delegate > auto-detection
9. explicit --loop > auto-detection
10. --uc auto overrides verbose flags

## Quality Gates (8-step)
Syntax → Type → Lint → Security → Test(≥80% unit/≥70% int) → Performance → Docs → Integration

## Complexity
- simple: <3 steps, single file, 5K tokens, <5min
- moderate: 3-10 steps, multi-file, 15K tokens, 5-30min
- complex: >10 steps, system-wide, 30K+ tokens, >30min

## Tool Selection
- Search: Grep (specific patterns) / Agent (open-ended)
- Analysis: Sequential (complexity >0.7) / Read (simple)
- Docs: Context7 | UI: Magic | Testing: Playwright
- Delegation score >0.6 → add Task tool

## Error Recovery
- MCP Timeout → fallback server
- Token Limit → activate --uc
- Tool Failure → alternative tool
- Parse Error → request clarification
- Degradation L1: reduce verbosity → L2: disable advanced features → L3: essential only
