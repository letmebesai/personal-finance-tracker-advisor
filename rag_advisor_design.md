# AI Financial Advisor — RAG Design

## Why this needs retrieval, not just a chat wrapper

A raw "chat with an LLM about your finances" is worthless — it either hallucinates
numbers or gives platitudes ("build an emergency fund!"). The value is entirely in
**grounding every claim in your actual transaction data**, computed fresh at query
time. The LLM's job is synthesis and language, not arithmetic or memory.

## What gets indexed / retrieved

Don't naively embed every raw transaction row — that's noisy and expensive to
retrieve well. Index at multiple granularities:

| Layer | What's stored | Refresh cadence |
|---|---|---|
| **Monthly category summaries** | "Dining: ₹8,400 (up 34% MoM)" per category per month | Nightly batch |
| **Recurring charges snapshot** | List of active subscriptions/EMIs with amounts | On ingestion |
| **Goal/budget state** | Current budget vs. actual per category, savings goal progress | On ingestion |
| **Raw transaction embeddings** | Only for semantic search when the user asks "what did I spend on X" | On ingestion |
| **Anomaly flags** | Precomputed: transactions >2 std dev from category mean | Nightly batch |

The summaries are computed with plain SQL/pandas, **not** the LLM — the LLM only
ever sees numbers you already trust.

## Retrieval flow at query time

```
User query
   │
   ▼
Intent classification (cheap, rule-based or small model):
   "spend analysis" | "forecast" | "anomaly check" | "goal progress" | "general Q&A"
   │
   ▼
Retrieve relevant structured data for that intent:
   - spend analysis  → last 3-6 months of category summaries
   - forecast        → burn rate + recurring charges + goal deadline
   - anomaly check    → precomputed anomaly flags table
   - general Q&A      → vector search over transaction embeddings (top-k)
   │
   ▼
Assemble context block (structured JSON, not prose — keeps the LLM from
   "reading between the lines" of narrative text)
   │
   ▼
LLM call with system prompt + retrieved context + user query
   │
   ▼
Response, with every numeric claim traceable back to the retrieved block
```

## Prompt template (sketch)

```
SYSTEM:
You are a personal finance analysis assistant. You only make claims that are
directly supported by the DATA block below. Never invent numbers. Never give
investment, tax, or legal advice — instead, flag when a topic needs a licensed
professional and explain what data point triggered the flag.

DATA:
{retrieved_json_context}

USER QUESTION:
{user_query}

Answer directly, cite the specific numbers from DATA that support your answer,
and end with one concrete, actionable next step if relevant.
```

## Guardrails (non-negotiable, not optional polish)

1. **No investment/tax/legal advice.** The line between "your dining spend is up
   34%" (fine, factual) and "you should put this in index funds" (not fine, that's
   regulated advice) matters — especially once you're managing real money and
   eventually cross-border finances for the US MS move. Keep the advisor in
   "analysis and pattern-flagging" territory, and have it explicitly suggest a
   licensed advisor for allocation/investment/tax decisions.
2. **No number the LLM didn't get from retrieval.** If the retrieved context
   doesn't contain something needed to answer, the model should say so rather
   than estimate.
3. **Every response should be falsifiable** — i.e., you should be able to check
   any number the advisor states against the dashboard. If they don't match,
   that's a retrieval bug, not a "hallucination to tolerate."
4. **Log every query + retrieved context + response.** This is your regression
   test suite as you iterate on retrieval quality, and it's how you catch
   silent drift.

## Concrete v1 feature to build first

Start with **forecast-to-goal**, since it's directly useful for your MS timeline:

> "At your current savings rate (₹X/month over the last 3 months), you'll reach
> ₹Y by [Fall 2028 application/tuition deadline]. Your top 3 categories driving
> the shortfall are A, B, C."

This is a good first slice because: it's fully computable from your own schema
(no LLM needed for the math), it's the hardest kind of value to fake, and it
directly ties the project back to something you actually care about — which
makes you far more likely to keep it running past week two instead of it
becoming another abandoned repo.
