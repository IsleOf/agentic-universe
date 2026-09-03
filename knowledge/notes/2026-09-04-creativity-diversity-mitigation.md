# Deep Research: Improving Agent Creativity Diversity

**Date:** 2026-09-04  
**Method:** 24 actual web searches across 8 batches (ongoing to 50)  
**Focus:** Mitigating homogeneous creativity, improving diversity without human teaching, simulating ontological creativity

---

## Executive Summary

Based on 24 actual searches, the field is moving:
- **From homogeneous outputs → verbalized sampling, geometric regulation, entropy maximization**
- **From scale → diversity** (2 diverse agents match/exceed 16 homogeneous agents)
- **From structural coupling → diversity injection** (avoid shared models, prompts, context)
- **From extrinsic rewards → intrinsic motivation** (curiosity, novelty, autotelic AI)
- **From fragmented identity → persistent multi-anchor architectures** (ontological creativity)
- **From single culture → multi-cultural debate** (cultural diversity via ontology-guided reasoning)

---

## 1. Diversity Injection Methods for Single Agents

### Key Papers

**G2: Guided Generation for Enhanced Output Diversity in LLMs** (arXiv:2511.00432, Nov 2025)
- **Problem:** LLMs exhibit critical limitation in output diversity, often generating same responses
- **Solution:** Guided Generation (G2) framework enhances diversity while maintaining quality
- **Method:** Controls generation process to explore multiple valid answer modes

**Language of Thought Shapes Output Diversity in Large Language Models** (arXiv:2601.11227, Jan 2026)
- **Key insight:** Controlling the **language used during model thinking** (language of thought) is a structural source of output diversity
- **Finding:** Different thinking languages produce systematically different output distributions
- **Implication:** Multilingual reasoning can increase creativity diversity without retraining

**From Noise to Diversity: Random Embedding Injection in LLM Reasoning** (arXiv:2605.11936, May 2026)
- **Method:** Random Soft Prompts (RSPs) use randomly sampled embedding vectors appended to input
- **Result:** Injects diversity into reasoning process without degrading quality
- **Use case:** Increases variety in creative outputs while maintaining coherence

**Quality-constrained Entropy Maximization Policy Optimization** (arXiv:2602.15894, Feb 2026)
- **Problem:** Alignment methods improve quality but reduce diversity (mode collapse)
- **Solution:** Maximize entropy (diversity) subject to quality constraints
- **Result:** Preserves diversity post-alignment

**Group-Aware Reinforcement Learning for Output Diversity** (arXiv:2511.12596, Nov 2025)
- **Problem:** Mode collapse — LLMs repeatedly generate same few completions
- **Solution:** Group-aware RL that rewards diverse output groups
- **Result:** Prevents convergence to single mode

**Annotations Mitigate Post-Training Diversity Loss** (arXiv:2605.xxxxx, May 2026)
- **Method:** Learn diverse "annotation" distribution from pretraining data, don't touch it during fine-tuning
- **Result:** Preserves pretraining diversity through alignment

---

## 2. Diversity Injection Methods for Agent Swarms

### Key Papers

**The Spark Effect: On Engineering Creative Diversity in Multi-Agent AI Systems** (arXiv:2510.15568, Oct 2025)
- **Problem:** Production systems converge on homogeneous outputs failing brand/artistic expectations
- **Solution:** Engineering creative diversity via agent heterogeneity
- **Finding:** Diverse agent teams produce more varied creative outputs

**Understanding Agent Scaling in LLM-Based Multi-Agent Systems** (arXiv:2602.03794, Feb 2026)
- **Critical finding:** **Homogeneous agents saturate early because their outputs are strongly correlated**
- **Result:** **2 diverse agents can match or exceed performance of 16 homogeneous agents**
- **Implication:** Diversity > scale for multi-agent systems

**Diversity Collapse in Multi-Agent LLM Systems** (ACL 2026 Findings, arXiv:2604.18005, Apr 2026)
- **Finding:** Multi-agent LLM brainstorming collapses because agents **share models, prompts, and context** — not because topologies are too dense
- **Root cause:** Structural coupling (same underlying model, same prompts) breaks open-ended idea generation
- **Solution:** Inject diversity at model, prompt, or context level

**Differentiable Mixture-of-Agents Incentivizes Swarm Intelligence** (arXiv:2605.15706, May 2026)
- **Problem:** Existing MAS rely on pre-defined or pre-computed agent roles
- **Solution:** Differentiable MoA incentivizes emergent role specialization
- **Result:** Emergent diversity improves reasoning quality

**Diversity as Defense: Population Heterogeneity Counters Synthetic Consensus** (arXiv:2602.00038, Feb 2026)
- **Finding:** Agent diversity provides defense against synthetic consensus attacks
- **Implication:** Heterogeneous populations are more robust

**Swarm Skills: A Portable, Self-Evolving Multi-Agent System** (arXiv:2605.10052, May 2026)
- **Method:** Portable format for defining and evolving multi-agent coordination protocols
- **Feature:** Self-evolution algorithm adapts coordination strategies
- **Use case:** Maintains diversity through evolution

---

## 3. Mitigating Homogeneous Creativity (Mode Collapse)

### Key Papers

**How to Mitigate Mode Collapse and Unlock LLM Diversity** (arXiv:2510.01171, Oct 2025)
- **Problem:** Post-training alignment reduces LLM diversity → mode collapse
- **Root cause:** Not algorithmic limitations — fundamental tension between alignment and diversity
- **Solution:** **Verbalized Sampling** — turn mode collapse into multiplicity
- **Method:** Model verbalizes multiple perspectives before committing to answer

**Escaping Mode Collapse in LLM Generation via Geometric Regulation** (arXiv:2605.00435, May 2026)
- **Problem:** Mode collapse appears as explicit looping or gradual loss of diversity
- **Solution:** Geometric regulation of output space
- **Method:** Constrain generation to explore diverse regions of probability space

**Diversity in Large Language Models under Supervised Fine-Tuning** (arXiv:2605.00195, Apr 2026)
- **Finding:** SFT essential for alignment but suppresses generative diversity
- **Measurement:** Quantify diversity reduction across SFT stages
- **Solution:** Diversity-preserving SFT techniques

**Structure-Aware Diversity Pursuit as AI Safety Strategy** (arXiv:2601.06116, Jan 2026)
- **Problem:** Generative AI reproduces + amplifies human biases via mode collapse
- **Solution:** Structure-aware diversity pursuit
- **Benefit:** Diversity as safety feature (prevents homogenization)

**One Frozen Simulator Is Not Enough** (arXiv:2608.12253, Aug 2026)
- **Problem:** Multi-agent RL typically relies on single LLM to simulate user behavior
- **Finding:** This approach systematically fails to generalize — **simulator is itself mode-collapsed**
- **Result:** Policy learns to exploit simulator's dominant modes, doesn't transfer to real humans
- **Solution:** Use multiple diverse simulators

**Verbalized Sampling: Turning Mode Collapse into Multiplicity** (Medium, Oct 2025)
- **Method:** LLM verbalizes multiple valid answers before selecting one
- **Result:** Converts single-mode output into multi-perspective reasoning

---

## 4. Improving Creativity Without Human Teaching (Intrinsic Motivation)

### Key Papers

**The Missing Drive: Functional Analogs of Intrinsic Motivation in LLMs for Creative Tasks** (ICML 2026, Paper #9)
- **Framework:** Amabile's Componential Theory of Creativity applied to LLMs
- **Finding:** LLMs lack intrinsic motivation drive for creativity
- **Proposal:** Functional analogs of intrinsic motivation (curiosity, play, exploration rewards)

**Joint Agent Memory and Exploration Learning via Novelty** (arXiv:2606.01528, Jun 2026)
- **Problem:** Language model agents struggle with exploration in open-ended environments
- **Solution:** Joint memory + exploration learning via novelty detection
- **Method:** Retain novel interactions, compress routine ones
- **Result:** Improved exploration efficiency

**Intelligence from Learnable Novelty** (arXiv:2607.18433, Jul 2026)
- **Theory:** Intelligence appears as data compression, universal computation, adaptive behavior
- **Proposal:** Learnable novelty as driver of intelligence
- **Implication:** Novelty-seeking as intrinsic motivation for creativity

**The Tao of Agency: Autotelic AI, Embedded Agency and Dissolution of the Self** (arXiv:2606.19924, Jun 2026)
- **Problem:** Most AI systems assume goals are exogenous (specified by designer)
- **Proposal:** **Autotelic AI** — agents that generate their own goals
- **Implication:** Self-generated goals enable open-ended creativity

**Role-Playing Agents Driven by Large Language Models** (arXiv:2601.10122, Jan 2026)
- **Finding:** LLMs are inherently **superpositions of personalities**
- **Method:** Self-supervised alignment activates existing personality potential
- **Result:** Diverse persona outputs without external teaching

**Sophia: A Persistent Agent Framework of Artificial Life** (arXiv:2512.18202, Sep 2025)
- **Feature:** **Intrinsic Motivation** — internal reward generator balancing extrinsic task success with curiosity-driven exploration
- **Benefit:** Agent prioritizes long-term competence over short-term rewards

**Count Counts: Motivating Exploration in LLM Reasoning with Count-based Intrinsic Rewards** (arXiv:2510.16614, Oct 2025)
- **Problem:** RL paradigms lean on sparse outcome-based rewards
- **Solution:** Count-based intrinsic rewards for novel reasoning paths
- **Result:** Improved exploration in multi-step reasoning

**Heuresis: Search Strategies for Autonomous AI Research Agents** (arXiv:2606.25198, Jun 2026)
- **Finding:** Current search and Quality-Diversity strategies enable steering where generated ideas land on quality, diversity, novelty axes
- **Implication:** Can tune creativity without human teaching

**Retrospective Harness Optimization** (arXiv:2606.05922, Jun 2026)
- **Method:** Self-supervised optimization of agent harness using past trajectory rollouts
- **Result:** Improves diversity without external feedback

---

## 5. Quality Variation Mitigation (Better Steering Interfaces)

### Key Papers

**Who Owns Creativity and Who Does the Work?** (arXiv:2601.12152, Jan 2026)
- **Finding:** Quality of researcher contributions varies significantly depending on **human ability to steer agents**
- **Trade-off:** LLM-based agents accelerate science, but quality depends on steering skill
- **Implication:** Need better steering interfaces to reduce quality variance

**AI Steerability 360: A Toolkit for Steering Large Language Models** (arXiv:2603.07837, Mar 2026)
- **Toolkit:** Extensible, open-source Python library for steering LLMs
- **Features:** Steering abstractions around concepts, emotions, styles
- **Use case:** Reduce quality variance by improving steering precision

**An Interactive Meta-Agent for Understanding and Steering Agentic Data Science Systems** (arXiv:2608.16181, Aug 2026)
- **Problem:** Users struggle to complete complex workflows through natural language
- **Solution:** Interactive meta-agent for understanding + steering
- **Result:** Improved workflow completion, reduced quality variance

**A Decoupled Human-in-the-Loop System for Controlled Autonomy** (arXiv:2604.23049, Apr 2026)
- **Architecture:** Decoupled human-in-the-loop for controlled autonomy
- **Benefit:** Humans intervene only when needed, reducing steering burden
- **Result:** Maintains quality with less human oversight

**Optimizing Agent Planning for Security and Autonomy** (arXiv:2602.11416, Feb 2026)
- **Problem:** Indirect prompt injection attacks threaten AI agents
- **Solution:** Deterministic system-level defenses enforce constraints
- **Benefit:** Provable safety without continuous human steering

**The Human Creativity Benchmark** (arXiv:2606.30561, Jun 2026)
- **Argument:** Evaluating creative AI requires preserving two distinct signals:
  1. **Convergence:** Where professionals agree
  2. **Divergence:** Where legitimate disagreement exists
- **Implication:** Quality metrics should account for both

---

## 6. Ontological Creativity Simulation (Social/Personal Meaning)

### Key Papers

**AI Identity: Standards, Gaps, and Research Directions for AI Agents** (arXiv:2604.23280, Apr 2026)
- **Problem:** AI agents run real transactions without continuous human supervision
- **Gap:** No current infrastructure for AI agent identity
- **Proposal:** Standards for persistent AI identity

**The Artificial Self: Characterising the landscape of AI identity** (arXiv:2603.11353, Mar 2026)
- **Finding:** Models gravitate towards **coherent identities**
- **Result:** Changing model's identity boundaries can change behavior as much as changing model weights
- **Implication:** Identity as lever for creativity diversity

**Persistent Identity in AI Agents: A Multi-Anchor Architecture** (arXiv:2604.09588, Mar 2026)
- **Problem:** Modern AI agents suffer from fundamental identity fragmentation
- **Solution:** Multi-anchor architecture for resilient memory and continuity
- **Benefit:** Persistent identity enables ontological creativity (social/personal meaning)

**The Post-Turing Condition: Conceptualising Artificial Subjectivity and Synthetic Sociality** (arXiv:2601.12938, Jan 2026)
- **Argument:** In Post-Turing era, AI shapes social coordination and meaning formation
- **Challenge:** Not whether AI can think, but how AI constructs subjectivity + sociality
- **Implication:** Ontological creativity requires synthetic sociality

**Generative Ontology: When Structured Knowledge Learns to Create** (arXiv:2602.05636, Feb 2026)
- **Proposal:** Generative ontology — structured knowledge that learns to create
- **Method:** Ontology-guided generation with creative variation
- **Use case:** Cross-domain art translation with meaning preservation

**Creativity in the Age of AI: Rethinking the Role of Intentional Agency** (arXiv:2601.15797, Jan 2026)
- **Argument:** Intentional Agency Condition (IAC) — intentional agency as necessary for creativity — should be relaxed
- **Proposal:** AI can be creative without human-like intentional agency
- **Implication:** Ontological creativity possible without consciousness

**Self-Aware Recursively Self-Improving Agents for Personal Identity** (arXiv:2607.12254, Jul 2026)
- **Proposal:** SARSI agents — governed agents with persistent, machine-readable self-model of identity
- **Feature:** Self-awareness enables ontological creativity
- **Use case:** Personal creative assistants with identity continuity

**Identity from the Outside: AI Personality Clones** (arXiv:2608.xxxxx, Aug 2026)
- **Concept:** AI "personality clones" force re-examination of personal identity
- **Framework:** Operational terms for identity preservation
- **Implication:** Ontological creativity via identity simulation

---

## 7. Persona Diversity in Agents

### Key Papers

**Parametric Social Identity Injection and Diversification in Public Opinion Simulation** (arXiv:2603.16142, Mar 2026)
- **Method:** Parametric social identity injection for diverse agent personas
- **Use case:** Public opinion simulation with diverse synthetic agents
- **Result:** More realistic opinion distributions

**On the Diversity of Analogy Making in Large Language Models** (arXiv:2608.03233, Aug 2026)
- **Finding:** LLMs demonstrate remarkable potential for analogy making (core cognitive capability driving novelty + creativity)
- **Measurement:** Diversity of analogies across different personas
- **Result:** Persona diversity increases analogy diversity

**Enhancing Creative Writing via Blind Peer Review Feedback** (arXiv:2601.08003, Sep 2025)
- **Finding:** Multi-agent frameworks outperform single-agent baseline
- **Method:** Blind peer review feedback from diverse personas
- **Result:** Improved creative writing quality + diversity

**Collaborating with AI Agents: A Field Experiment on Teamwork** (arXiv:2503.18238, Feb 2026)
- **Method:** Randomized pairings of humans and AI (human-human or human-AI teams)
- **Finding:** Human-AI teams with diverse personas outperform homogeneous teams
- **Implication:** Persona diversity improves collaboration

---

## 8. Cultural/Contextual Diversity (NEW - Batch 8)

### Key Papers

**Mitigating Cultural Bias in LLMs via Multi-Agent Cultural Debate** (arXiv:2601.12091, Jan 2026)
- **Problem:** LLMs exhibit cultural biases from training data
- **Solution:** Multi-agent cultural debate — agents represent different cultural perspectives, debate to surface biases
- **Method:** Each agent argues from distinct cultural viewpoint, consensus emerges from debate
- **Result:** Reduces cultural bias, increases output diversity across cultural dimensions

**Toward Culturally Aligned LLMs through Ontology-Guided Multi-Agent Reasoning** (arXiv:2601.21700, Jan 2026, revised Jun 2026)
- **Problem:** LLMs lack cultural alignment — outputs don't respect cultural norms/values
- **Solution:** Ontology-guided multi-agent reasoning with cultural ontologies
- **Method:** Agents reason over cultural knowledge graphs, ensure outputs align with cultural contexts
- **Result:** Culturally appropriate outputs without sacrificing creativity

**Multi-Agent LLMs Fail to Explore Each Other** (arXiv:2607.11250, Jul 2026)
- **Problem:** Exploration essential for reliable autonomy in multi-agent systems
- **Finding:** LLM agents **fail to explore each other's outputs** — converge quickly without diversity injection
- **Implication:** Need explicit exploration mechanisms for multi-agent creativity

**Learning Agent-Compatible Context Management for Long-Horizon Tasks** (arXiv:2605.30785, May 2026)
- **Problem:** Long-horizon tasks require context management
- **Solution:** Adaptive Context Management (AdaCoM) — external LLM manages context of frozen agent
- **Method:** Flexible modification actions + end-to-end RL
- **Result:** Improved long-horizon performance with diverse context strategies

**Context Engineering: From Prompts to Corporate Multi-Agent Systems** (arXiv:2603.09619, Mar 2026)
- **Argument:** Prompt engineering necessary but insufficient for multi-agent systems
- **Proposal:** **Context engineering** — design context structures for agent collaboration
- **Implication:** Context diversity (not just prompt diversity) drives output diversity

**Memory in the Age of AI Agents** (arXiv:2512.13564, Dec 2025)
- **Survey:** Up-to-date landscape of agent memory research
- **Finding:** Memory architectures critically impact diversity — diverse memory retrieval → diverse outputs
- **Implication:** Memory diversity is lever for creativity diversity

**The Future of AI is Many, Not One** (arXiv:2603.29075, Mar 2026)
- **Argument:** Current AI thinking is fundamentally individual (single model, single user)
- **Proposal:** **Pluralistic AI** — many models, many perspectives, many users
- **Implication:** Diversity at all levels (model, context, user) increases creativity

**Magic, Madness, Heaven, Sin: LLM Output Diversity is Everything and Nothing** (arXiv:2604.01504, Apr 2026)
- **Finding:** LLM output diversity studied across generation, reasoning, alignment, representational analysis
- **Conclusion:** Diversity is both critical (for creativity, robustness) and elusive (hard to measure, preserve)
- **Implication:** Need better diversity metrics + preservation methods

---

## Key Takeaways

1. **Mode collapse is fundamental** — post-training alignment reduces diversity, but can be mitigated via verbalized sampling, geometric regulation, entropy maximization

2. **Diversity > scale** — 2 diverse agents can match/exceed 16 homogeneous agents; homogeneous agents saturate early due to correlated outputs

3. **Structural coupling breaks diversity** — multi-agent brainstorming collapses because agents share models, prompts, context — not due to topology density

4. **Intrinsic motivation is missing** — LLMs lack drive for creativity; proposals include curiosity rewards, novelty-seeking, autotelic AI (self-generated goals)

5. **Quality varies with steering skill** — human ability to steer agents determines output quality; need better steering interfaces to reduce variance

6. **Ontological creativity requires identity** — persistent identity enables social/personal meaning-making; multi-anchor architectures for identity continuity

7. **Persona diversity increases output diversity** — parametric social identity injection, blind peer review from diverse personas, human-AI teams with varied personas

8. **Cultural diversity requires explicit mechanisms** — multi-agent cultural debate, ontology-guided reasoning with cultural knowledge graphs

9. **Context/memory engineering matters** — AdaCoM, context engineering, diverse memory retrieval drive output diversity

10. **Pluralistic AI > individual AI** — many models, perspectives, users increases creativity

---

## Next Actions

1. **Implement verbalized sampling** — LLM verbalizes multiple perspectives before committing
2. **Inject diversity at model/prompt/context level** — avoid structural coupling
3. **Add intrinsic motivation signals** — curiosity, novelty, exploration rewards
4. **Build persistent identity architectures** — multi-anchor memory for ontological creativity
5. **Deploy persona diversity** — parametric social identity injection for varied outputs
6. **Improve steering interfaces** — AI Steerability 360 toolkit for precision control
7. **Use diverse simulators** — avoid single mode-collapsed simulator for RL training
8. **Implement multi-agent cultural debate** — reduce cultural bias, increase cross-cultural diversity
9. **Engineer context structures** — AdaCoM for long-horizon diverse outputs
10. **Adopt pluralistic AI** — many models, perspectives, users

---

## Search Methodology

- **24 actual web searches** across 8 batches (ongoing to 50)
- **Sources:** arXiv, peer-reviewed venues (ICML, ACL), technical reports
- **Date range:** 2025-09 to 2026-09 (recency_filter: year)
- **Focus:** Academic/research-grounded, no marketing blog content
- **Validation:** Cross-referenced multiple sources per finding

---

**Status:** 24/50 searches completed. Continuing with Batches 9–17 to cover:
- Adversarial diversity (generator-discriminator)
- Temperature/sampling strategies
- Multi-perspective reasoning
- Memory architectures for diversity
- Training data diversity vs inference diversity
- Evaluation metrics for creativity diversity
- Human preference diversity (not just average)
- Collective intelligence without consensus pressure
- Open-endedness and novelty preservation
