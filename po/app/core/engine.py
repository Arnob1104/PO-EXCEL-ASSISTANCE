import pandas as pd
from openai import OpenAI

from app.config import settings
from app.db import supabase

# OrcaRouter exposes an OpenAI-compatible API, so we use the openai SDK
# pointed at their base_url instead of a dedicated client.
_llm_client = OpenAI(
    base_url="https://api.orcarouter.ai/v1",
    api_key=settings.orcarouter_api_key,
)

# Using OrcaRouter's hosted Qwen3.8-27B (free tier), 65K context window.
LLM_MODEL = "qwen/qwen3.8-27b-free"

SYSTEM_PROMPT = """You are a data assistant answering questions about purchase \
orders using ONLY the table data provided. If the answer requires data not in \
the table, say "I don't have that information." Give precise numbers, not \
approximations, when the data supports it."""


def load_po_dataframe(org_id: str) -> pd.DataFrame:
    """
    Pulls this org's purchase order rows from Supabase and returns them as a
    DataFrame, in the same shape the original script expected from the xlsx.
    """
    result = (
        supabase.table("purchase_orders")
        .select("order_ref, buyer, style, order_qty, ship_date, status")
        .eq("org_id", org_id)
        .execute()
    )
    return pd.DataFrame(result.data)


def answer_question(df: pd.DataFrame, question: str) -> str:
    if df.empty:
        return "I don't have that information. No purchase order data is loaded yet."

    table_text = df.to_string(index=False)
    prompt = f"""Purchase order data:
{table_text}

Question: {question}"""

    response = _llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content