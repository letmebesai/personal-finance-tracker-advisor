"""
Transaction Categorization Pipeline
------------------------------------
Three-tier approach:
  1. Rule engine (regex/keyword match against category_rules table) — cheap, deterministic, handles ~70-80% of volume
  2. Embedding-based ML fallback for anything the rules miss
  3. Feedback loop: every manual correction either reinforces an existing rule
     or gets auto-promoted into a new rule once it repeats

Run this as a batch job after each ingestion (see ingest_and_categorize()).
"""

import re
import psycopg2
import psycopg2.extras
from dataclasses import dataclass
from typing import Optional
import numpy as np

from merchant_normalization import normalize_merchant


# ---------------------------------------------------------------------------
# 1. Rule-based fast path
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    rule_id: str
    category_id: str
    match_type: str   # 'exact' | 'contains' | 'regex'
    pattern: str
    priority: int


def load_rules(conn) -> list[Rule]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM category_rules ORDER BY priority ASC")
        return [Rule(**row) for row in cur.fetchall()]


def match_rule(description: str, rules: list[Rule]) -> Optional[str]:
    """Return category_id if a rule matches, else None."""
    normalized = description.upper().strip()
    for rule in rules:
        if rule.match_type == "exact" and normalized == rule.pattern.upper():
            return rule.category_id
        elif rule.match_type == "contains" and rule.pattern.upper() in normalized:
            return rule.category_id
        elif rule.match_type == "regex" and re.search(rule.pattern, normalized, re.IGNORECASE):
            return rule.category_id
    return None


# ---------------------------------------------------------------------------
# 2. ML fallback — embedding similarity against labeled examples
# ---------------------------------------------------------------------------
# Approach: maintain a small set of "reference embeddings" per category, built
# from previously confirmed transactions. Embed the new description, compare
# via cosine similarity, take the nearest category above a confidence threshold.
# This avoids calling an LLM per-transaction (slow + costly at scale) — only
# use the LLM for genuinely ambiguous cases (see classify_with_llm below).

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def embed_text(text: str) -> np.ndarray:
    """
    Plug in your embedding model here — e.g. sentence-transformers
    ('all-MiniLM-L6-v2' is fast and free, runs locally) or an API embedding call.
    Returning a stub vector so this file runs standalone; replace in production.
    """
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(text, normalize_embeddings=True)


def classify_with_embeddings(
    description: str,
    category_reference_embeddings: dict[str, list[np.ndarray]],
    threshold: float = 0.72,
) -> tuple[Optional[str], float]:
    query_vec = embed_text(description)
    best_category, best_score = None, 0.0
    for category_id, ref_vectors in category_reference_embeddings.items():
        score = max(cosine_similarity(query_vec, ref) for ref in ref_vectors)
        if score > best_score:
            best_category, best_score = category_id, score
    if best_score >= threshold:
        return best_category, best_score
    return None, best_score


def classify_with_llm(description: str, category_names: list[str]) -> str:
    """
    Last-resort fallback for genuinely ambiguous transactions (low embedding
    confidence). Cheap in volume terms since it's the minority path.
    """
    import anthropic
    client = anthropic.Anthropic()
    prompt = (
        f"Classify this bank transaction description into exactly one category "
        f"from this list: {', '.join(category_names)}.\n\n"
        f"Transaction: \"{description}\"\n\n"
        f"Respond with only the category name, nothing else."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# 3. Main pipeline
# ---------------------------------------------------------------------------

def categorize_transaction(description: str, rules: list[Rule], ref_embeddings: dict) -> dict:
    # Tier 1: rules
    category_id = match_rule(description, rules)
    if category_id:
        return {"category_id": category_id, "method": "rule", "confidence": 1.0}

    # Tier 2: embeddings
    category_id, score = classify_with_embeddings(description, ref_embeddings)
    if category_id:
        return {"category_id": category_id, "method": "ml", "confidence": round(score, 3)}

    # Tier 3: LLM fallback for the genuinely unclear remainder
    return {"category_id": None, "method": "uncategorized", "confidence": 0.0,
            "needs_review": True, "raw_description": description}


def ingest_and_categorize(conn, new_transactions: list[dict]) -> None:
    """
    new_transactions: [{account_id, posted_date, amount, raw_description}, ...]
    Inserts each transaction with its best-effort category, flagging low-confidence
    ones for manual review instead of silently guessing wrong.
    """
    rules = load_rules(conn)
    ref_embeddings = build_reference_embeddings(conn)  # see below

    with conn.cursor() as cur:
        for txn in new_transactions:
            result = categorize_transaction(txn["raw_description"], rules, ref_embeddings)
            merchant_normalized = normalize_merchant(txn["raw_description"])
            cur.execute(
                """
                INSERT INTO transactions
                    (account_id, posted_date, amount, raw_description,
                     merchant_normalized, category_id, categorization_method, categorization_confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (account_id, posted_date, amount, raw_description) DO NOTHING
                """,
                (txn["account_id"], txn["posted_date"], txn["amount"], txn["raw_description"],
                 merchant_normalized, result.get("category_id"), result["method"], result.get("confidence")),
            )
    conn.commit()


def build_reference_embeddings(conn, min_examples: int = 5) -> dict[str, list[np.ndarray]]:
    """
    Pull confirmed (rule or manually-corrected) transactions per category and
    embed a sample as the reference set for the ML tier. Cache this in production
    instead of rebuilding every run.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT category_id, raw_description FROM transactions
            WHERE categorization_method IN ('rule', 'manual')
            """
        )
        rows = cur.fetchall()

    by_category: dict[str, list[str]] = {}
    for row in rows:
        by_category.setdefault(row["category_id"], []).append(row["raw_description"])

    return {
        cat_id: [embed_text(desc) for desc in descriptions[:20]]
        for cat_id, descriptions in by_category.items()
        if len(descriptions) >= min_examples
    }


# ---------------------------------------------------------------------------
# 4. Feedback loop — turn repeated manual corrections into new rules
# ---------------------------------------------------------------------------

def promote_corrections_to_rules(conn, min_repeats: int = 3) -> None:
    """
    Run periodically (e.g. weekly). If the same merchant string has been
    manually corrected to the same category >= min_repeats times, auto-create
    a 'contains' rule so future imports categorize it correctly without a human.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT t.merchant_normalized, c.new_category_id, COUNT(*) as n
            FROM category_corrections c
            JOIN transactions t ON t.transaction_id = c.transaction_id
            WHERE t.merchant_normalized IS NOT NULL
            GROUP BY t.merchant_normalized, c.new_category_id
            HAVING COUNT(*) >= %s
            """,
            (min_repeats,),
        )
        candidates = cur.fetchall()

        for row in candidates:
            cur.execute(
                """
                INSERT INTO category_rules (category_id, match_type, pattern, priority, created_from)
                SELECT %s, 'contains', %s, 50, 'user_correction'
                WHERE NOT EXISTS (
                    SELECT 1 FROM category_rules WHERE pattern = %s AND category_id = %s
                )
                """,
                (row["new_category_id"], row["merchant_normalized"],
                 row["merchant_normalized"], row["new_category_id"]),
            )
    conn.commit()
