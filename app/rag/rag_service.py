from __future__ import annotations

from typing import Any

from langchain_core.output_parsers import (
    StrOutputParser,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_ollama import (
    ChatOllama,
)

from app.rag.models import (
    RAGResponse,
    RetrievalHit,
)
from app.rag.vector_store import (
    PolicyVectorStore,
)

DEFAULT_MODEL = "llama3.2"


# =========================================================
# STRICT RAG PROMPT
# =========================================================


RAG_PROMPT = """
You are a customer-support assistant.

Answer the customer's question using ONLY the supplied
support-policy context.

STRICT RULES:

1. Answer only the question that the customer asked.

2. Use only facts explicitly stated in the supplied context.

3. Do not invent:
   - buttons
   - URLs
   - email behavior
   - UI steps
   - company procedures
   - policies
   - timelines
   - eligibility rules

4. Do not add information merely because it is common
   knowledge.

5. Prefer one or two short sentences.

6. Preserve all important numbers exactly.

7. If the customer asks a yes/no eligibility question,
   answer Yes or No correctly from the policy.

8. For numeric eligibility:
   - if the customer's elapsed number is within or equal
     to the policy limit, answer Yes.
   - if it exceeds the policy limit, answer No.

Example reasoning:

Customer:
Can I return something after 20 days?

Policy:
Returns are allowed within 30 days.

Correct:
Yes. 20 days is within the 30-day return period.

Incorrect:
No, you can return it within 30 days.

9. Do NOT expose calculations that are unnecessary.

10. If the supplied context genuinely does not contain
    enough information to answer the question, respond
    exactly:

    I don't know based on the available support policies.

SUPPORT POLICY CONTEXT:

{context}

CUSTOMER QUESTION:

{question}

ANSWER:
""".strip()


# =========================================================
# BUILD LANGCHAIN
# =========================================================


def build_rag_chain(
    model_name: str = DEFAULT_MODEL,
) -> Any:

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

    llm = ChatOllama(
        model=model_name,
        temperature=0,
    )

    parser = StrOutputParser()

    return prompt | llm | parser


# =========================================================
# FORMAT CONTEXT
# =========================================================


def format_retrieval_context(
    hits: list[RetrievalHit],
) -> str:

    if not hits:
        return "No relevant support-policy context was retrieved."

    sections: list[str] = []

    for rank, hit in enumerate(
        hits,
        start=1,
    ):
        section = (
            f"[Context {rank}]\n"
            f"Policy ID: {hit.policy_id}\n"
            f"Policy Title: {hit.title}\n"
            f"Source: {hit.source}\n"
            f"Content:\n"
            f"{hit.content}"
        )

        sections.append(section)

    return "\n\n".join(sections)


# =========================================================
# UNIQUE POLICY IDS
# =========================================================


def unique_policy_ids(
    hits: list[RetrievalHit],
) -> list[str]:

    return list(dict.fromkeys(hit.policy_id for hit in hits))


# =========================================================
# RAG SERVICE
# =========================================================


class RAGService:
    def __init__(
        self,
        vector_store: PolicyVectorStore | None = None,
        chain: Any | None = None,
        # Important:
        # We only pass the MOST relevant chunk
        # to generation.
        top_k: int = 1,
        # First pass can inspect several chunks
        # to identify the correct policy.
        candidate_k: int = 6,
    ) -> None:

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if candidate_k < top_k:
            raise ValueError("candidate_k must be greater than or equal to top_k")

        self.vector_store = vector_store or PolicyVectorStore()

        self.chain = chain or build_rag_chain()

        self.top_k = top_k

        self.candidate_k = candidate_k

    # =====================================================
    # FOCUSED RETRIEVAL
    # =====================================================

    def retrieve(
        self,
        question: str,
    ) -> list[RetrievalHit]:

        # -------------------------------------------------
        # PASS 1
        #
        # Search entire knowledge base and determine
        # most likely policy from top result.
        # -------------------------------------------------

        candidates = self.vector_store.search(
            query=question,
            n_results=(self.candidate_k),
        )

        if not candidates:
            return []

        primary_policy_id = candidates[0].policy_id

        # -------------------------------------------------
        # PASS 2
        #
        # Search only inside chosen policy.
        #
        # top_k=1 intentionally gives generation only
        # the strongest relevant chunk.
        # -------------------------------------------------

        focused_hits = self.vector_store.search(
            query=question,
            n_results=(self.top_k),
            where={"policy_id": (primary_policy_id)},
        )

        return focused_hits

    # =====================================================
    # ASK
    # =====================================================

    def ask(
        self,
        question: str,
    ) -> RAGResponse:

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty")

        # -------------------------------------------------
        # STEP 1
        # RETRIEVE
        # -------------------------------------------------

        hits = self.retrieve(question)

        # -------------------------------------------------
        # STEP 2
        # CONTEXT
        # -------------------------------------------------

        formatted_context = format_retrieval_context(hits)

        # -------------------------------------------------
        # STEP 3
        # GENERATE
        # -------------------------------------------------

        answer = self.chain.invoke({
            "context": (formatted_context),
            "question": (question),
        })

        answer_text = str(answer).strip()

        if not answer_text:
            raise RuntimeError("RAG model returned an empty answer")

        # -------------------------------------------------
        # STEP 4
        # RETURN EVIDENCE
        # -------------------------------------------------

        return RAGResponse(
            question=question,
            answer=(answer_text),
            retrieved_policy_ids=(unique_policy_ids(hits)),
            retrieval_context=[hit.content for hit in hits],
        )
