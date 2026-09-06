# Prediction Branch — Polymarket & Kalshi Ecosystem Scan

**Date:** 2026-09-07 · **Branch of:** Agentic Universe (self-improving agentic systems)
**Sources:** GitHub Search API (live, 2026-09-06/07), arXiv, ecosystem directories. Star counts are snapshot values.

## Purpose

A curated implementation map for a self-improving forecasting and prediction-market branch. The branch treats resolved markets as a grounded feedback channel: forecast, record evidence and probability, score after resolution, recalibrate by domain, and evolve the research and trading policy.

## Official infrastructure

| Component | Status | Recommended use |
|---|---|---|
| Polymarket/agent-skills | Active official skill pack | Primary agent-facing integration layer for market research, orders, positions, streaming, bridging, and gasless operations. |
| Polymarket/polymarket-cli | Active official Rust CLI, JSON API mode | Script/agent control plane and terminal workflow. |
| Polymarket/agents | Archived 2026-05-11 | Reference architecture only; do not use as a greenfield dependency. |
| Polymarket/py-clob-client | Archived | Legacy reference only. |
| Kalshi API v2 | Active REST/WebSocket API | Use the demo sandbox first; production uses RSA-key authentication. |

## High-priority GitHub projects

### Data and cross-venue infrastructure

| Repository | Why it matters |
|---|---|
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | Polymarket + Kalshi data-analysis framework and large public historical dataset; foundation for replay, calibration, and market mapping. |
| [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt) | CCXT-like unified TypeScript API for Polymarket, Kalshi, and other venues; preferred integration boundary. |
| [warproxxx/poly_data](https://github.com/warproxxx/poly_data) | Polymarket market, trade, and order-event collection. |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | High-adoption multi-source research skill across web, Reddit, X, HN, YouTube, and Polymarket; candidate evidence-ingestion component. |
| [aarora4/Awesome-Prediction-Market-Tools](https://github.com/aarora4/Awesome-Prediction-Market-Tools) | Living directory for agent, API, data, copy-trading, alerting, and analysis tools; rescan monthly. |

### Agentic and self-improvement patterns

| Repository | Pattern to extract |
|---|---|
| [bennyjo/phil](https://github.com/bennyjo/phil) | Self-improving prediction trader: rewrites strategy after settled bets; paper-first and capped live stakes. |
| [zhongdaweiai/clio](https://github.com/zhongdaweiai/clio) | Multi-agent, Pareto-scored, time-evolving backtests; explicit autoresearch framing. |
| [thierrypdamiba/teeth](https://github.com/thierrypdamiba/teeth) | Live prediction markets as ungameable evaluation surface for agents. |
| [SpartanLabsXyz/simmer-sdk](https://github.com/SpartanLabsXyz/simmer-sdk) | Skills, MCP server, and Python SDK across Polymarket/Kalshi; paper-to-live graduation and outcome-learning loops. |
| [artvandelay/polymarket-agents](https://github.com/artvandelay/polymarket-agents) | Research MCP server surface—odds, order book, spread, and history—plus autonomous paper-trading loop and SQLite persistence. |
| [OctagonAI/kalshi-trading-bot-cli](https://github.com/OctagonAI/kalshi-trading-bot-cli) | Deep-research to probability-estimate to edge analysis, with Kelly sizing and a multi-gate risk pattern. |
| [666ghj/MiroFish](https://github.com/666ghj/MiroFish) | Swarm simulation alternative for long-horizon scenario forecasting; use as an experimental forecasting specialist, not an execution engine. |
| [alsk1992/CloddsBot](https://github.com/alsk1992/CloddsBot) | Multi-venue autonomous-agent architecture including prediction markets, useful for execution-boundary design. |

### Quant and execution references

| Repository | Pattern to extract |
|---|---|
| [YichengYang-Ethan/oracle3](https://github.com/YichengYang-Ethan/oracle3) | Quantitative engine: historical-contract calibration, Wang Transform pricing, constraint-based arbitrage, Kelly execution, and strong test coverage. |
| [taetaehoho/poly-kalshi-arb](https://github.com/taetaehoho/poly-kalshi-arb) | Cross-platform market matching and order-book delta handling in Rust. |
| [ImMike/polymarket-arbitrage](https://github.com/ImMike/polymarket-arbitrage) | Broad cross-platform inefficiency scanning. |
| [evan-kolberg/prediction-market-backtesting](https://github.com/evan-kolberg/prediction-market-backtesting) | Nautilus Trader-based backtesting route. |
| [warproxxx/poly-maker](https://github.com/warproxxx/poly-maker) | Market-making mechanics and two-sided order management. |
| [sterlingcrispin/nothing-ever-happens](https://github.com/sterlingcrispin/nothing-ever-happens) | Simple buy-NO baseline that the branch should outperform on matched markets. |

### Domain-edge references

| Repository | Pattern to extract |
|---|---|
| [suislanchez/polymarket-kalshi-weather-bot](https://github.com/suislanchez/polymarket-kalshi-weather-bot) | Narrow-domain ensemble forecasts, explicit edge threshold, Kelly sizing, and dashboarding. |
| [livetennisapi/polymarket-tennis](https://github.com/livetennisapi/polymarket-tennis) | Market-to-live-event mapping and observe-only data layer. |
| [Novals83/5min-btc-polymarket](https://github.com/Novals83/5min-btc-polymarket) | Short-horizon momentum workflow with configurable risk controls. |

## Literature map

| Work | arXiv | Branch implication |
|---|---|---|
| Approaching Human-Level Forecasting with Language Models | [2402.18563](https://arxiv.org/abs/2402.18563) | Retrieval-augmented forecast pipeline and forecast-crowd ensemble are baseline designs. |
| ForecastBench | [2409.19839](https://arxiv.org/abs/2409.19839) | Dynamic, contamination-resistant Brier-scored external evaluation target. |
| LLM-as-a-Prophet / Prophet Arena | [2510.17638](https://arxiv.org/abs/2510.17638) | Models may be calibrated yet aggregate fresh information slower than markets near resolution; require freshness-aware strategy constraints. |
| Going All-In on LLM Accuracy | [2512.05998](https://arxiv.org/abs/2512.05998) | Wager-size framing can expose a more useful confidence signal than raw binary outputs. |
| TruthTensor | [2601.13545](https://arxiv.org/abs/2601.13545) | Score calibration, drift, and risk sensitivity separately from directional accuracy. |
| PredictionMarketBench | [2602.00133](https://arxiv.org/abs/2602.00133) | Deterministic limit-order-book replay, transaction costs, and settlement risk must be regression gates before execution. |
| Domain-Specific Calibration Dynamics | [2602.19520](https://arxiv.org/abs/2602.19520) | Maintain domain-specific calibration tables rather than global probability correction. |
| PolyBench | [2604.14199](https://arxiv.org/abs/2604.14199) | Live Polymarket benchmark; warns that raw frontier LLM forecasts are generally overconfident and most models were not profitable. |
| Bayesian Language Forecaster | [2604.18576](https://arxiv.org/abs/2604.18576) | Store and update a linguistic belief state: probability plus concise evidence rationale. |
| Replaying Prediction Markets to Evaluate LLM Forecasters | [2607.14051](https://arxiv.org/html/2607.14051v1) | Use point-in-time evidence snapshots for leakage-free hindcasts. |
| AQuA: Recursively Self-Improving Quantitative Trading | [2608.12841](https://arxiv.org/html/2608.12841v2) | Direct conceptual input for an evidence-driven recursive research/evolution loop. |

## Branch architecture

```text
1. INGEST
   pmxt unified API; Polymarket Gamma/CLOB; Kalshi v2 demo; historical datasets;
   evidence capture through a multi-source research skill.

2. FORECAST
   Retrieval-augmented forecaster; explicit belief-state JSON; independent-model
   ensemble; optional swarm-simulation specialist for scenario questions.

3. MEMORY AND CALIBRATION
   Persist {timestamp, market, forecast probability, market price, rationale,
   evidence hashes, confidence, resolution}; calculate Brier/log score and
   domain-specific reliability curves when markets settle.

4. EVALUATION
   Replay harness first, external benchmark second, live paper portfolio last.
   Track Brier, log loss, calibration slope/intercept, CWR, drawdown, and coverage.

5. EXECUTION
   Paper trading only by default; execution gate needs independent estimate, edge
   after fees/slippage, liquidity threshold, risk budget, and human approval.

6. EVOLUTION
   Create candidate policy changes from outcome analyses; backtest against frozen
   episodes; Pareto-select for calibration, return, turnover, and robustness;
   promote only through staged paper evaluation.
```

## Minimal viable loop

1. Connect `pmxt` or read-only venue APIs and ingest active/resolved markets into SQLite or DuckDB.
2. Generate one independent forecast per selected market with a structured belief state.
3. Store retrieval timestamp and source URLs/hashes to prevent hindsight leakage.
4. Resolve daily; calculate Brier and log score against both final resolution and contemporaneous market probability.
5. Build reliability curves by domain and time-to-resolution.
6. Do not enable orders until at least 100 resolved forecasts demonstrate calibration and replayed returns remain positive after realistic costs.

## Data contract

```json
{
  "forecast_id": "uuid",
  "created_at": "ISO-8601",
  "venue": "polymarket|kalshi",
  "market_id": "string",
  "question": "string",
  "horizon_hours": 0,
  "market_mid": 0.0,
  "agent_probability": 0.0,
  "confidence": 0.0,
  "belief_state": {
    "thesis": "string",
    "supporting_evidence": ["source-id"],
    "disconfirming_evidence": ["source-id"],
    "key_uncertainties": ["string"]
  },
  "model_and_prompt_version": "string",
  "policy_version": "string",
  "decision": "observe|paper_yes|paper_no|live_yes|live_no",
  "resolution": null,
  "brier_score": null,
  "log_score": null
}
```

## Operating safeguards

- Keep venue credentials outside repos and never supply them to unreviewed trading repositories.
- Treat unsupported profit claims, opaque binaries, and mass-forked arbitrage bots as untrusted until manually audited.
- Start in read-only or sandbox mode; then paper trade; require explicit human approval for each new live-capital regime.
- Price in fees, spread, queue position, slippage, settlement/oracle risk, and venue-specific eligibility before calling an opportunity an edge.
- Preserve point-in-time evidence and immutable execution logs so the system can diagnose false confidence rather than merely optimize PnL.

## Initial KPIs

- Forecast count and settlement coverage by market domain.
- Brier score and log score, globally and per domain.
- Reliability slope/intercept and expected calibration error.
- Performance versus contemporaneous market price and simple baselines.
- Paper CWR/PnL after realistic fees and slippage.
- Drawdown, turnover, and decision-to-resolution latency.
- Promotion/reversion history for every policy version.

## Near-term implementation order

1. Adopt `pmxt` behind a venue adapter interface.
2. Import a resolved-market corpus from `prediction-market-analysis`.
3. Build the immutable forecast ledger and calibration dashboard before any trade executor.
4. Reproduce a small `PredictionMarketBench`-style replay suite.
5. Add the belief-state forecaster and evaluation reports.
6. Evaluate vertical specialists starting with weather, where public exogenous data and crisp resolution provide clean testing.
7. Only then prototype a bounded, human-approved paper-execution gate.
