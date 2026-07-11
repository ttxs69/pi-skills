# Context-Window Management in Long-Horizon LLM Agent Frameworks

**Scope:** LangChain, LlamaIndex, OpenAI Assistants API, Anthropic Agent SDK, AutoGen, CrewAI
**Window of interest:** roughly mid-2024 → early 2026
**Method:** Single-pass synthesis from training-time knowledge (cutoff Jan 2026). Live web verification was not available in this run — citations point at the public docs/announcements I recall; treat specifics as plausible rather than authoritative and re-verify before relying on them.

---

## 1. Executive summary

Across the six frameworks surveyed, context-window management for long-horizon agents has converged on a small toolkit of primitives, even though each framework packages them differently:

- **Sliding-window / trim-by-token** is universal; every framework ships some form of "keep the last N messages or last K tokens."
- **Compaction via summarization** is the dominant mid-session strategy, with two variants: rolling summary chains (LangChain, LlamaIndex) and model-driven context editing (Anthropic).
- **Tiered memory** (short-term working memory + long-term episodic/semantic memory) has become the explicit design in CrewAI and AutoGen v0.4+, and is the de facto pattern in LangGraph.
- **Server-side truncation** is the OpenAI Assistants approach: the runtime truncates older thread messages automatically rather than asking the application to do it.
- **RAG-over-past-turns** (vector-store-backed memory of prior exchanges) is now treated as a first-class context strategy in LlamaIndex, LangChain, AutoGen, and CrewAI.

What is *not* solved well in this window: principled heuristics for *when* to compact vs. trim, transparent cost attribution across memory tiers, and graceful degradation when the long-term store diverges from the working set.

---

## 2. Per-framework notes

### 2.1 LangChain / LangGraph
- **Memory primitives** (LCEL era): `ConversationBufferMemory`, `ConversationBufferWindowMemory` (keep last K turns), `ConversationSummaryMemory`, `ConversationTokenBufferMemory` (trim by token count against the model's context window), and `ConversationSummaryBufferMemory` (hybrid: summarize older turns, keep recent turns verbatim).
- **Trim utility:** `trim_messages` in `langchain-core` accepts a strategy (`"last"`, `"first"`) plus token-count and stop criteria; this is the canonical sliding-window helper.
- **LangGraph** (the graph-runtime extension): state is a typed `State` object; nodes can read/write it explicitly. Long-horizon patterns published in the LangGraph docs include a `MessagesState` with a `RemoveMessage` reducer plus a summarization node, which together implement compaction-as-graph-step.
- **Long-term memory:** LangGraph ships `InMemoryStore`, `PostgresStore`, and an `index`-style memory API for cross-thread recall; the 2024 "LangGraph long-term memory" guide described three scopes — profile, semantic (facts), and episodic (prior sessions).
- **Known limitation:** Default checkpointers are in-process; persistence across multi-day sessions requires an explicit checkpointer backend.

### 2.2 LlamaIndex
- **Chat memory classes** under `llama_index.core.memory`:
  - `ChatMemoryBuffer` — token-bounded ring buffer of chat messages.
  - `TokenAwareMemory` — same idea with explicit max-token input.
  - `SimpleComposableMemory` / `ComposableMemory` — stacks multiple memory backends (e.g., buffer + vector memory).
- **Memory blocks** (2024 redesign): typed blocks (`StaticBlock`, `ChatMemoryBlock`, `VectorMemoryBlock`, `FactExtractionMemoryBlock`) composed into a single context per turn. This is LlamaIndex's explicit answer to memory hierarchies.
- **Compaction:** `CondensePlusContextChatEngine` and `ContextChatEngine` provide rolling summarization; the newer memory-block API replaces ad-hoc summarization chains with declarative blocks.
- **Long-term recall:** `VectorMemoryBlock` writes past turns to a vector index and retrieves top-k per query, framing long-horizon memory as RAG over the conversation itself.

### 2.3 OpenAI Assistants API
- **Threads are server-managed.** The application appends messages; the runtime assembles the prompt for each `run`.
- **Truncation:** the Threads API exposes a `truncation_strategy` (either `auto` — drop the oldest messages to fit — or explicit `last_messages` count). This is the framework's primary context-management lever.
- **Token budgets:** `max_prompt_tokens` and `max_completion_tokens` per run; the server surfaces `usage` metadata so callers can observe when truncation happened.
- **File search / code interpreter tools** keep large corpora *outside* the prompt; this is the official escape hatch for long-horizon tasks with reference material.
- **Limitations in the window:** no first-class summarization step; no client-controlled compaction callback. If `auto` truncation isn't acceptable, callers typically pre-summarize before appending.

### 2.4 Anthropic Agent SDK (Claude API features consumed by the SDK)
- **Context window:** 200K tokens on current Claude models; prompt caching reduces re-billing of stable prefixes.
- **Context editing (beta, announced mid-2024, expanded through 2025):** a server-side feature that automatically clears or summarizes tool results and stale turns when approaching a configurable token threshold. This is the closest thing in the surveyed frameworks to first-class, model-aware compaction.
- **Skills system:** pre-defined instruction bundles injected on demand — used as a form of compressed, on-call context rather than always-on system prompt content.
- **Agent SDK long-horizon patterns:** documented patterns include writing intermediate state to local files, periodic `compact` operations that summarize the transcript into a structured note, and re-injecting that note at the top of subsequent turns. The SDK ships reference implementations of these patterns.
- **Prompt caching** is the implicit memory tier: stable system prompts and tool definitions are cached and don't count against the active context budget in the same way as fresh turns.

### 2.5 AutoGen (Microsoft)
- **AutoGen v0.4 (2024)** reorganized the runtime around an actor model; each actor has its own message stream and can apply its own context-trimming policy.
- **Memory modules** (v0.4+): `ListMemory`, ` ChromaDB`-backed `VectorMemory`, and `RAGMemory`. Agents can be configured with a memory backend and a `MemoryController` that decides what to recall per turn.
- **Context compression:** the `contextual` package (or `compression` in some releases) provides summarization-based compaction; agents can be wired to call it before context overflow.
- **GroupChatManager:** long group chats use a manager that decides which prior messages to forward to which agent — an implicit sliding-window per recipient.
- **Notable gap:** the canonical tutorials still favor single-session agents; multi-day persistence requires wiring your own store on top of the memory backend.

### 2.6 CrewAI
- **Three explicit memory tiers**, the cleanest in this set:
  - **Short-term memory** — current crew execution context (in-memory).
  - **Long-term memory** — persisted across runs (typically SQLite or a vector store).
  - **Entity memory** — extracted entities (people, projects, concepts) with their own store.
- **Sliding-window behavior** is implicit in short-term memory: older crew steps age out unless promoted to long-term or entity memory.
- **Compaction** happens via task-completion summaries being written into long-term memory; there's no explicit summarization node as in LangGraph.
- **RAG-backed recall** is the default for long-term and entity memory; the framework ships with ChromaDB integrations out of the box.

---

## 3. Comparison

| Framework | Trim / sliding window | Summarization compaction | Memory hierarchy | Server-side truncation | Notes |
|---|---|---|---|---|---|
| LangChain / LangGraph | `trim_messages`, `BufferWindow` | `SummaryMemory`, graph summarization node | Profile + semantic + episodic via LangGraph store | No | Most flexible; most wiring required |
| LlamaIndex | `ChatMemoryBuffer` | Memory blocks (`FactExtractionBlock`) | Composable memory blocks | No | Strong RAG-of-past-turns story |
| OpenAI Assistants | Implicit | None first-class | None (threads only) | Yes (`auto`) | Easiest; least controllable |
| Anthropic Agent SDK | Manual | Server-side context editing | Skills + cached system prompt | Partial (context editing) | Best model-aware compaction |
| AutoGen v0.4+ | Per-actor policy | `compression`/`contextual` package | `VectorMemory` / `RAGMemory` | No | Strong actor isolation |
| CrewAI | Implicit (short-term aging) | Implicit (task-summary writeback) | Short / long / entity | No | Cleanest tiering taxonomy |

---

## 4. Patterns that recur

1. **Trim-first, summarize-second.** Almost every framework implements trim-by-token as the cheap baseline and summarization as the upgrade path when the buffer isn't enough.
2. **Vectorize the past.** Five of the six frameworks (all except OpenAI Assistants) treat RAG-over-prior-turns as a memory tier rather than as a separate concern.
3. **Compaction as an explicit step.** LangGraph and the Anthropic SDK both publish compaction-as-a-node patterns; this is becoming the canonical shape rather than ad-hoc summarization chains.
4. **Memory tiers are the new abstraction.** Where 2023-era agents had "a memory," 2024–2025 agents have 2–3 named tiers with different persistence and retrieval characteristics.

---

## 5. What I could not verify

Live web access was unavailable for this run. The following items are areas where I'd want to re-check the official docs before citing the specifics:

- Exact API surface and parameter names for OpenAI's `truncation_strategy` and Anthropic's context-editing beta in their current forms.
- Whether LangGraph's `RemoveMessage` reducer and the three-scope memory guide have been renamed or restructured in recent releases.
- AutoGen v0.4's current memory-package names (the `MemoryController` / `ListMemory` / `VectorMemory` naming shifted across preview releases).
- CrewAI's current default long-term store backend (it has changed at least once).
- Whether any framework now ships a published "when to compact" heuristic (vs. leaving it to the developer).

## 6. Open questions for follow-up

- How do frameworks expose *cost* (tokens used / tokens saved) of compaction decisions to the developer?
- Are there benchmarks published in this window comparing sliding-window vs. summarization vs. RAG-of-past-turns on identical long-horizon tasks? (Anthropic published internal numbers for context editing; I'd want to verify whether independent reproductions exist.)
- How do frameworks handle *contradiction* between a compacted summary and the underlying transcript? (None of the surveyed designs surface this.)
- Multi-day *handoff* — passing a session between two frameworks or two model providers — is essentially unsolved.