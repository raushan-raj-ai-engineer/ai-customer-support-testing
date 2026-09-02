from __future__ import annotations

from app.rag.chunker import (
    chunk_document,
    chunk_documents,
    split_into_sentences,
)
from app.rag.document_loader import (
    load_knowledge_documents,
)

# =========================================================
# DOCUMENT LOADING
# =========================================================


def test_loads_three_policy_documents() -> None:
    """
    Verify that all three support policy documents
    are loaded successfully.
    """

    documents = load_knowledge_documents()

    assert len(documents) == 3

    policy_ids = {document.policy_id for document in documents}

    assert policy_ids == {
        "REFUND_POLICY",
        "SHIPPING_POLICY",
        "PASSWORD_POLICY",
    }


# =========================================================
# SENTENCE SPLITTING
# =========================================================


def test_policy_is_split_into_complete_sentences() -> None:
    """
    Verify that policy content is split into
    complete sentences instead of arbitrary
    word-count fragments.
    """

    documents = load_knowledge_documents()

    document = documents[0]

    sentences = split_into_sentences(document.content)

    assert sentences

    assert len(sentences) >= 2

    assert all(sentence.strip() for sentence in sentences)

    assert all(sentence.endswith((".", "!", "?")) for sentence in sentences)


# =========================================================
# SINGLE DOCUMENT CHUNKING
# =========================================================


def test_document_is_split_into_chunks() -> None:
    """
    Verify that a single knowledge document
    produces sentence-level chunks.
    """

    documents = load_knowledge_documents()

    document = documents[0]

    chunks = chunk_document(document)

    assert chunks

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.policy_id == document.policy_id

        assert chunk.title == document.title

        assert chunk.source == document.source

        assert chunk.content.strip()


# =========================================================
# CHUNK ID
# =========================================================


def test_chunk_ids_are_unique() -> None:
    """
    Every chunk must have its own unique ID.
    """

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


# =========================================================
# CHUNK INDEX
# =========================================================


def test_chunk_indexes_start_from_zero() -> None:
    """
    Chunk indexes should start at zero for
    each individual policy document.
    """

    documents = load_knowledge_documents()

    for document in documents:
        chunks = chunk_document(document)

        indexes = [chunk.chunk_index for chunk in chunks]

        assert indexes == list(range(len(chunks)))


# =========================================================
# MARKDOWN HEADINGS
# =========================================================


def test_markdown_heading_is_not_chunked() -> None:
    """
    Markdown headings such as:

        # Shipping Policy

    should not be part of the embedding text because
    title/policy metadata already exists separately.
    """

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    assert chunks

    for chunk in chunks:
        assert not (chunk.content.lstrip().startswith("#"))


# =========================================================
# COMPLETE SENTENCES
# =========================================================


def test_chunks_are_complete_sentences() -> None:
    """
    This test protects us from the previous bug:

        "Customers receive a tracking"

        "The password reset"

    Every chunk should now be a complete sentence.
    """

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    assert chunks

    assert all(chunk.content.endswith((".", "!", "?")) for chunk in chunks)


# =========================================================
# NO EMPTY CHUNKS
# =========================================================


def test_no_empty_chunks_are_created() -> None:
    """
    Ensure whitespace or blank lines never
    create empty chunks.
    """

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    assert chunks

    assert all(chunk.content.strip() for chunk in chunks)


# =========================================================
# ALL POLICY DOCUMENTS
# =========================================================


def test_all_documents_generate_chunks() -> None:
    """
    Verify that every knowledge-base document
    contributes chunks.
    """

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    generated_policy_ids = {chunk.policy_id for chunk in chunks}

    expected_policy_ids = {document.policy_id for document in documents}

    assert generated_policy_ids == expected_policy_ids


# =========================================================
# REFUND POLICY FACT
# =========================================================


def test_refund_policy_contains_atomic_return_window_chunk() -> None:
    """
    Important regression test.

    The return-window fact should exist as its
    own sentence-level chunk.
    """

    documents = load_knowledge_documents()

    refund_document = next(
        document for document in documents if document.policy_id == "REFUND_POLICY"
    )

    chunks = chunk_document(refund_document)

    matching_chunks = [
        chunk.content for chunk in chunks if ("30 days" in chunk.content)
    ]

    assert matching_chunks

    assert any("return" in content.lower() for content in matching_chunks)


# =========================================================
# SHIPPING POLICY FACT
# =========================================================


def test_shipping_policy_contains_atomic_shipping_time_chunk() -> None:
    """
    Standard shipping duration should be
    available in a focused chunk.
    """

    documents = load_knowledge_documents()

    shipping_document = next(
        document for document in documents if document.policy_id == "SHIPPING_POLICY"
    )

    chunks = chunk_document(shipping_document)

    matching_chunks = [
        chunk.content for chunk in chunks if ("3 to 5 business days" in chunk.content)
    ]

    assert matching_chunks

    assert any(("standard shipping" in content.lower()) for content in matching_chunks)


# =========================================================
# TRACKING FACT
# =========================================================


def test_shipping_policy_contains_atomic_tracking_chunk() -> None:
    """
    Tracking-number rule should not be mixed with
    unrelated delivery/refund content.
    """

    documents = load_knowledge_documents()

    shipping_document = next(
        document for document in documents if document.policy_id == "SHIPPING_POLICY"
    )

    chunks = chunk_document(shipping_document)

    matching_chunks = [
        chunk.content
        for chunk in chunks
        if ("tracking number" in chunk.content.lower())
    ]

    assert matching_chunks

    assert any(
        ("after the order has been shipped" in content.lower())
        for content in matching_chunks
    )


# =========================================================
# PASSWORD EXPIRY FACT
# =========================================================


def test_password_policy_contains_atomic_expiry_chunk() -> None:
    """
    Password reset expiry should be represented
    as a dedicated sentence-level chunk.
    """

    documents = load_knowledge_documents()

    password_document = next(
        document for document in documents if document.policy_id == "PASSWORD_POLICY"
    )

    chunks = chunk_document(password_document)

    matching_chunks = [
        chunk.content for chunk in chunks if ("15 minutes" in chunk.content)
    ]

    assert matching_chunks

    assert any(
        ("password reset link" in content.lower()) for content in matching_chunks
    )


# =========================================================
# FORGOT PASSWORD FACT
# =========================================================


def test_password_policy_contains_atomic_reset_instruction_chunk() -> None:
    """
    Forgot-password guidance should exist
    as an independent retrievable chunk.
    """

    documents = load_knowledge_documents()

    password_document = next(
        document for document in documents if document.policy_id == "PASSWORD_POLICY"
    )

    chunks = chunk_document(password_document)

    matching_chunks = [
        chunk.content
        for chunk in chunks
        if ("account login page" in chunk.content.lower())
    ]

    assert matching_chunks

    assert any(
        ("password reset link" in content.lower()) for content in matching_chunks
    )
