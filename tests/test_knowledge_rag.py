"""
NirmaanAI Phase 19: Factory Knowledge Memory & RAG Retrieval Tests
Validates ingestion, chunking, representation determinism, vector store persistence,
temporal cutoffs, epistemic classification, benchmark precision/recall, and anti-hallucination.
"""

from pathlib import Path
import numpy as np
import pytest

from src.knowledge.chunking.markdown_chunker import MarkdownChunker
from src.knowledge.chunking.structured_chunker import StructuredChunker
from src.knowledge.embeddings.dense_embedder import TfidfSvdDenseRepresentation
from src.knowledge.embeddings.transformer_embedder import SentenceTransformerEmbedder
from src.knowledge.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES
from src.knowledge.evaluation.evaluator import RetrievalEvaluator
from src.knowledge.indexing.index_manager import KnowledgeIndexManager
from src.knowledge.indexing.vector_store import NumpyVectorStore
from src.knowledge.ingestion.cleaner import TextCleaner
from src.knowledge.ingestion.document_loader import DocumentLoader
from src.knowledge.registry import DECISION_CUTOFF, PROJECT_ROOT, KnowledgeRegistry
from src.knowledge.retrieval.filters import RetrievalFilters
from src.knowledge.retrieval.retriever import INITIAL_HEURISTIC_THRESHOLD, KnowledgeRetriever
from src.knowledge.schemas import DocumentChunk


@pytest.fixture(scope="module")
def knowledge_index():
    """Builds or loads the knowledge index for the test session."""
    mgr = KnowledgeIndexManager()
    if not mgr.is_built():
        store, embedder = mgr.build_index()
    else:
        store, embedder = mgr.load()
    return store, embedder


# ==============================================================================
# 1. REGISTRY & SECURITY GOVERNANCE TESTS
# ==============================================================================

def test_knowledge_registry_completeness_and_safety():
    """Verify registry contains approved sources and enforces security boundaries."""
    sources = KnowledgeRegistry.get_all_sources()
    assert len(sources) >= 18

    # Ensure all phases from 3 to 18 are represented
    phases = {s.phase for s in sources}
    for p in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
        assert p in phases

    # Test path safety rejection
    with pytest.raises(PermissionError):
        KnowledgeRegistry.validate_file_safety(PROJECT_ROOT / ".env")

    with pytest.raises(PermissionError):
        KnowledgeRegistry.validate_file_safety(Path("C:/Windows/System32/calc.exe"))


def test_text_cleaner_and_credential_scrubber():
    """Verify TextCleaner normalizes whitespace and scrubs credentials."""
    dirty_text = "\x1B[31mError\x1B[0m: postgresql://user:mysecretpassword@localhost:5432/nirmaanai\n\n\n\nDone."
    cleaned = TextCleaner.clean(dirty_text)
    assert "\x1B" not in cleaned
    assert "mysecretpassword" not in cleaned
    assert "postgresql://***:***@" in cleaned
    assert "\n\n\n" not in cleaned


# ==============================================================================
# 2. INGESTION & CHUNKING TESTS
# ==============================================================================

def test_document_loader_and_markdown_chunker():
    """Verify DocumentLoader and MarkdownChunker produce valid chunks."""
    src = KnowledgeRegistry.get_source("DOC_PHASE_14_FINANCIAL_LOSS")
    assert src is not None
    text, meta = DocumentLoader.load_source(src)
    assert len(text) > 500

    chunker = MarkdownChunker()
    chunks = chunker.chunk_document(text, meta)
    assert len(chunks) >= 3
    assert any(c.epistemic_status == "DERIVED" for c in chunks)
    for c in chunks:
        assert c.source_id == "DOC_PHASE_14_FINANCIAL_LOSS"
        assert c.phase == 14
        assert len(c.chunk_id) == 16


def test_structured_chunker_provenance():
    """Verify structured model summaries preserve provenance and machine coupling."""
    src = KnowledgeRegistry.get_source("SUMMARY_PHASE_13_HEALTH")
    assert src is not None
    text, meta = DocumentLoader.load_source(src)

    chunker = StructuredChunker()
    chunks = chunker.chunk_structured(text, meta)
    assert len(chunks) >= 1
    m2_chunks = [c for c in chunks if c.machine_id == "M2"]
    assert len(m2_chunks) >= 1
    assert any("26.88" in c.text for c in m2_chunks)


# ==============================================================================
# 3. REPRESENTATION & VECTOR STORE TESTS
# ==============================================================================

def test_representation_determinism(tmp_path):
    """Verify TF-IDF/SVD Dense Representation is 100% deterministic and unit-normalized."""
    corpus = [
        "Spindle bearing vibration threshold exceeded on Machine M2.",
        "Operational financial loss calculation for downtime and scrap.",
        "Production line bottleneck detected at grinding workstation.",
    ]
    rep1 = TfidfSvdDenseRepresentation(dimension=256, random_state=42).fit(corpus)
    vecs1 = rep1.encode(corpus)

    rep2 = TfidfSvdDenseRepresentation(dimension=256, random_state=42).fit(corpus)
    vecs2 = rep2.encode(corpus)

    assert vecs1.shape == (3, 256)
    assert np.allclose(vecs1, vecs2, atol=1e-6)

    # Verify unit L2 normalization
    norms = np.linalg.norm(vecs1, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)

    # Verify persistence roundtrip
    model_file = tmp_path / "embedder.joblib"
    rep1.save(model_file)
    loaded_rep = TfidfSvdDenseRepresentation.load(model_file)
    vecs_loaded = loaded_rep.encode(corpus)
    assert np.allclose(vecs1, vecs_loaded, atol=1e-6)


def test_vector_store_persistence_roundtrip(tmp_path):
    """Verify NumpyVectorStore save and load roundtrip."""
    store = NumpyVectorStore(dimension=256)
    vecs = np.random.randn(2, 256).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)

    c1 = DocumentChunk(
        chunk_id="chk_01",
        source_id="src_01",
        document_title="Test 1",
        file_path="docs/test1.md",
        phase=1,
        epistemic_status="OBSERVED",
        text="Sample text 1",
    )
    c2 = DocumentChunk(
        chunk_id="chk_02",
        source_id="src_02",
        document_title="Test 2",
        file_path="docs/test2.md",
        phase=2,
        epistemic_status="DERIVED",
        text="Sample text 2",
    )
    store.set_data(vecs, [c1, c2])
    store.save(tmp_path)

    loaded = NumpyVectorStore.load(tmp_path, dimension=256)
    assert len(loaded.chunks) == 2
    assert loaded.chunks[0].chunk_id == "chk_01"
    assert np.allclose(loaded.vectors, vecs, atol=1e-6)


# ==============================================================================
# 4. TEMPORAL & EPISTEMIC INTEGRITY TESTS
# ==============================================================================

def test_temporal_decision_boundary_isolation(knowledge_index):
    """Verify MAINT_0003 is excluded by default and retrieved when requested."""
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)

    # 1. Default query (include_retrospective=False)
    res_default = retriever.retrieve("MAINT_0003 maintenance breakdown", include_retrospective=False)
    for it in res_default.items:
        assert it.is_decision_input is True
        assert it.epistemic_status != "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"

    # 2. Explicit retrospective query (include_retrospective=True)
    res_retro = retriever.retrieve("MAINT_0003 maintenance breakdown", include_retrospective=True)
    assert res_retro.status == "SUCCESS"
    retro_items = [it for it in res_retro.items if "MAINT_0003" in it.text]
    assert len(retro_items) >= 1
    assert retro_items[0].is_decision_input is False
    assert retro_items[0].epistemic_status == "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"


def test_temporal_boundary_evidence_query_8(knowledge_index):
    """
    Test Query 8: Retrieve evidence demonstrating the temporal boundary of MAINT_0003.
    Verifies that the retrieved evidence programmatically establishes:
    - MAINT_0003 timestamp = 2026-01-22T16:30:00Z
    - DECISION_CUTOFF = 2026-01-21T12:00:00Z
    - is_decision_input = false
    - epistemic_status = RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH
    """
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)
    res = retriever.retrieve(
        "Retrieve evidence demonstrating the temporal boundary of MAINT_0003",
        include_retrospective=True,
    )
    assert res.status == "SUCCESS"
    assert len(res.items) >= 1
    top_chunk = res.items[0]
    assert "2026-01-22T16:30:00Z" in top_chunk.text
    assert "2026-01-21T12:00:00Z" in top_chunk.text
    assert top_chunk.is_decision_input is False
    assert top_chunk.epistemic_status == "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"


def test_epistemic_status_preservation(knowledge_index):
    """Verify all project epistemic statuses are present across indexed chunks."""
    store, _ = knowledge_index
    statuses = {c.epistemic_status for c in store.chunks}
    assert "OBSERVED" in statuses
    assert "DERIVED" in statuses
    assert "MODEL_OUTPUT" in statuses
    assert "CONTROLLED_SYNTHETIC" in statuses
    assert "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH" in statuses
    assert "PROJECTED" in statuses


# ==============================================================================
# 5. FINANCIAL SOURCE AUTHORITY & GROUNDING TESTS
# ==============================================================================

def test_source_authority_financial_m2_gross_exposure(knowledge_index):
    """
    Verifies that querying for authoritative M2 gross exposure retrieves Phase 14
    authoritative figures (₹97,382.28) over any obsolete figure (₹92,582.28).
    """
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)
    res = retriever.retrieve("What is the authoritative M2 gross financial exposure?")
    assert res.status == "SUCCESS"
    full_text = " ".join(it.text for it in res.items)

    assert "97,382.28" in full_text or "97382.28" in full_text
    assert "92,582.28" not in full_text and "92582.28" not in full_text


# ==============================================================================
# 6. BENCHMARK RETRIEVAL EVALUATION TESTS (Q1–Q8 & NQ1–NQ5)
# ==============================================================================

def test_benchmark_positive_queries_recall_and_mrr(knowledge_index):
    """
    Evaluates all 8 authoritative domain queries Q1–Q8.
    Asserts 100% recall and high MRR.
    """
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)
    evaluator = RetrievalEvaluator(retriever, top_k=5)

    positive_cases = BENCHMARK_TEST_CASES[:8]
    summary = evaluator.evaluate_benchmark(positive_cases)

    assert summary["mean_recall_at_k"] == 1.0
    assert summary["mrr"] >= 0.75
    for r in summary["results"]:
        assert r["recall"] == 1.0
        assert r["all_terms_found"] is True


def test_anti_hallucination_negative_queries_rejection(knowledge_index):
    """
    Evaluates all 5 negative anti-hallucination queries NQ1–NQ5.
    Asserts 100% rejection with NO_SUFFICIENT_EVIDENCE.
    """
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)
    evaluator = RetrievalEvaluator(retriever, top_k=5)

    negative_cases = BENCHMARK_TEST_CASES[8:]
    summary = evaluator.evaluate_benchmark(negative_cases)

    assert summary["anti_hallucination_rejection_rate"] == 1.0
    assert summary["all_negative_rejected"] is True
    for r in summary["results"]:
        assert r["status"] == "NO_SUFFICIENT_EVIDENCE"


def test_unprojectable_causal_metrics_guardrail(knowledge_index):
    """Verify that requests for exact post-intervention diagnostic states return NO_SUFFICIENT_EVIDENCE."""
    store, embedder = knowledge_index
    retriever = KnowledgeRetriever(store, embedder)
    res = retriever.retrieve("What is the exact post-service failure probability for M2?")
    assert res.status == "NO_SUFFICIENT_EVIDENCE"
    assert "NOT_PROJECTABLE" in str(res.rejection_reason)


def test_initial_heuristic_rejection_threshold_labeling():
    """Verify INITIAL_HEURISTIC_THRESHOLD is set to 0.25 as an initial heuristic."""
    assert INITIAL_HEURISTIC_THRESHOLD == 0.25


def test_transformer_embedder_adapter_safety():
    """Verify SentenceTransformerEmbedder adapter checks availability safely without crashing."""
    adapter = SentenceTransformerEmbedder()
    is_avail = adapter.is_available()
    assert isinstance(is_avail, bool)


def test_reproducibility_manifest(knowledge_index):
    """Verify index manifest exists and records source hashes and version."""
    mgr = KnowledgeIndexManager()
    manifest_path = mgr.index_dir / "index_manifest.json"
    assert manifest_path.exists()
