# NirmaanAI — Phase 19 Implementation Report
## Factory Knowledge Memory / RAG Engine

**Date:** 2026-09-13  
**Status:** COMPLETED & VERIFIED  
**Version:** v0.19.0  
**Authors:** NirmaanAI Systems Engineering  

---

### 1. Executive Summary
Phase 19 establishes the **Factory Knowledge Memory and Grounded Retrieval-Augmented Generation (RAG) Engine** for NirmaanAI. This engine acts as the authoritative single source of truth across all 18 preceding project phases, indexing operational documentation, machine architecture specifications, predictive maintenance analytics, root cause analyses, financial calculations, simulation outcomes, and API endpoint contracts.

The engine provides deterministic, provenance-tracked, epistemically classified, and temporally bounded retrieval. It guarantees that any future intelligence layer (such as the Phase 20 Factory Copilot) operates strictly on validated facts with exact source traceability, preventing hallucinations, obsolete data retrieval, and temporal data leakage.

---

### 2. Exact Objective & Scope
- **Objective**: Construct an offline, fully deterministic, production-grade knowledge retrieval engine grounded in NirmaanAI's cross-phase artifacts.
- **In Scope**:
  - Ingestion and sanitization of cross-phase markdown reports and structured model summaries.
  - Header-aware and entity-specific chunking pipelines.
  - Deterministic unit-normalized TF-IDF/SVD 256-dimensional dense retrieval representation.
  - Exact cosine vector storage and indexing with dual `.npy` and `.json` persistence.
  - Hybrid lexical-dense retrieval scoring with source authority weighting.
  - Strict temporal boundary enforcement (`DECISION_CUTOFF = 2026-01-21T12:00:00Z`).
  - Epistemic status tracking and superseded-figure governance.
  - Multi-tier anti-hallucination guardrails (entity verification, topical keyword anchors, unprojectable causal query rejection).
  - 13-query benchmark evaluation suite and 16 unit/integration tests.
- **Explicitly Out of Scope**:
  - Conversational chat endpoints or conversational session state.
  - LLM prompt orchestration or generative completions (reserved for Phase 20).
  - React/Vite dashboard integration (reserved for Phase 21).
  - External network downloads or neural dependency installations (`sentence-transformers`, `torch`, `faiss`).
  - Modifications to Phases 0–18 code or data.

---

### 3. Directory & File Manifest
```
src/knowledge/
├── __init__.py                                 # Package root and public API export
├── schemas.py                                  # Pydantic v2 domain schemas and enums
├── registry.py                                 # Catalog of 18+ knowledge sources & security validators
├── ingestion/
│   ├── __init__.py
│   ├── cleaner.py                              # Unicode normalization and credential scrubber
│   └── document_loader.py                      # Markdown & structured JSON model loaders
├── chunking/
│   ├── __init__.py
│   ├── markdown_chunker.py                     # Header-aware section chunker with table preservation
│   └── structured_chunker.py                   # Model metadata & asset parameter chunker
├── embeddings/
│   ├── __init__.py
│   ├── base.py                                 # BaseRepresentationModel abstract interface
│   ├── dense_embedder.py                       # TfidfSvdDenseRepresentation (256-dim deterministic baseline)
│   └── transformer_embedder.py                 # Pluggable SentenceTransformer adapter
├── indexing/
│   ├── __init__.py
│   ├── vector_store.py                         # NumpyVectorStore with exact cosine similarity
│   └── index_manager.py                        # KnowledgeIndexManager pipeline coordinator
├── retrieval/
│   ├── __init__.py
│   ├── filters.py                              # RetrievalFilters (temporal, machine, phase, epistemic)
│   └── retriever.py                            # KnowledgeRetriever with hybrid scoring and guardrails
└── evaluation/
    ├── __init__.py
    ├── benchmark_dataset.py                    # 13 benchmark test queries (Q1–Q8, NQ1–NQ5)
    └── evaluator.py                            # RetrievalEvaluator (Precision, Recall@K, MRR, Rejection Rate)

models/knowledge/
├── chunks_metadata.json                        # 278 indexed chunks with full provenance
├── tfidf_svd_model.joblib                      # Fitted TF-IDF vectorizer and TruncatedSVD pipeline
├── vector_embeddings.npy                       # Unit-normalized dense representation array (278, 256)
└── manifest.json                               # Reproducibility manifest with SHA-256 hashes

tests/
└── test_knowledge_rag.py                       # 16 comprehensive Phase 19 verification tests
```

---

### 4. Ingestion Architecture & Text Cleaning
The ingestion pipeline (`src/knowledge/ingestion/`) sanitizes raw text before chunking:
- **Unicode Normalization**: Canonical decomposition and recomposition (`NFKC`) strips zero-width spaces, control characters, and byte order marks.
- **Whitespace Sanitization**: Collapses repeated blank lines while preserving Markdown structural indentation and tabular layout.
- **Credential & Secret Scrubbing**: Regex filters automatically scrub API keys, tokens (`Bearer [a-zA-Z0-9_\-\.]+`), database connection URIs (`postgres://...`), and private IPs (`10.x.x.x`, `192.168.x.x`).
- **Path Security**: All source documents are verified to reside strictly within `C:\NIRMAAN AI`, rejecting symlinks, directory traversals, and unauthorized files.

---

### 5. Document Loader & Registered Knowledge Sources
The registry (`src/knowledge/registry.py`) catalogs 18 approved cross-phase knowledge sources:
1. `DOC_PHASE_03_RAW_DATA`: Phase 3 Raw Data Extraction and Signal Mapping.
2. `DOC_PHASE_04_CLEANING`: Phase 4 Signal Cleaning and Imputation Strategy.
3. `DOC_PHASE_05_EDA`: Phase 5 Exploratory Data Analysis & Sensor Statistics.
4. `DOC_PHASE_06_FEATURE_ENG`: Phase 6 Feature Engineering & Rolling Window Metrics.
5. `DOC_PHASE_07_ANOMALY`: Phase 7 Unsupervised Anomaly Detection & Degradation Tracking.
6. `DOC_PHASE_08_BOTTLENECK`: Phase 8 Bottleneck Identification & Throughput Analysis.
7. `DOC_PHASE_09_REMAINING_USEFUL_LIFE`: Phase 9 Predictive Maintenance RUL Estimation.
8. `DOC_PHASE_10_INVENTORY`: Phase 10 Spare Parts Inventory Optimization.
9. `DOC_PHASE_11_SHAP`: Phase 11 SHAP Feature Importance & Interpretability.
10. `DOC_PHASE_12_RCA`: Phase 12 Root Cause Analysis & Fault Tree Diagnosis.
11. `DOC_PHASE_13_HEALTH`: Phase 13 Machine Health Scoring & Degradation Index.
12. `DOC_PHASE_14_FINANCIAL_LOSS`: Phase 14 Financial Cost Quantization & Loss Modeling.
13. `DOC_PHASE_15_RULES`: Phase 15 Decision Engine & Rule Optimization.
14. `DOC_PHASE_16_SIMULATION`: Phase 16 Monte Carlo Simulation & Stress Testing.
15. `DOC_PHASE_17_DATABASE`: Phase 17 PostgreSQL Schema & Persistence Architecture.
16. `DOC_PHASE_18_API`: Phase 18 FastAPI Backend Service Layer.
17. `MODELS_STRUCTURED_SUMMARIES`: Machine learning model metrics and runtime parameters.
18. `EVENT_MAINT_0003_RETROSPECTIVE`: Controlled post-cutoff synthetic ground truth event.

---

### 6. Chunking Strategies
- **MarkdownChunker**: Header-aware hierarchical chunking (`#`, `##`, `###`). Chunks retain their structural path (`H1 > H2 > H3`) in chunk headers for semantic context. Markdown tables are preserved intact without mid-row splitting.
- **StructuredChunker**: Converts JSON model artifacts and tabular metadata into clean domain cards with machine-level tagging (`machine_ids=["M1", "M2", ...]`) and epistemic status tagging.
- **Total Corpus Output**: Exactly 278 chunks generated, validated, and indexed.

---

### 7. Metadata & Provenance Schema
Every chunk adheres to the immutable `DocumentChunk` schema (`src/knowledge/schemas.py`):
```python
class DocumentChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    phase: int
    content: str
    source_path: str
    heading_path: List[str]
    epistemic_status: EpistemicStatus
    timestamp: datetime
    is_decision_input: bool
    is_superseded: bool
    superseded_by: Optional[str]
    authority_weight: float
    machine_ids: List[str]
    factory_ids: List[str]
    token_count: int
    checksum: str
```

---

### 8. Epistemic-Status Architecture
To guarantee evidence validity, knowledge chunks carry explicit epistemic classifications:
1. `OBSERVED_HISTORICAL_FACT`: Empirical facts recorded during telemetry (e.g., historical sensor logs, real maintenance events). Authority: `1.0`.
2. `DETERMINISTIC_CALCULATION`: Direct mathematical or financial computations (e.g., Phase 14 realized financial loss of ₹73,062.28). Authority: `1.0`.
3. `STATISTICAL_INFERENCE`: Machine learning model predictions, RUL estimates, and degradation indices. Authority: `0.90`.
4. `SIMULATION_PROJECTION`: Monte Carlo or stress-test projections. Authority: `0.85`.
5. `PRESCRIPTIVE_POLICY`: Rule-based maintenance prescriptions and inventory recommendations. Authority: `0.95`.
6. `HISTORICAL_SUPERSEDED`: Outdated drafts or preliminary estimates (e.g., ₹92,582.28 preliminary loss). Authority: `0.50` (`is_superseded=True`). Excluded from authoritative queries by default.
7. `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Controlled post-cutoff validation records (e.g., `MAINT_0003`). Authority: `1.0` (`is_decision_input=False`). Excluded by default; accessible only with `include_retrospective=True`.

---

### 9. Temporal Cutoff & Boundary Governance
- **Cutoff Timestamp**: `2026-01-21T12:00:00Z` (Locked Decision Boundary).
- **Enforcement**:
  - Chunks created after the cutoff have `is_decision_input=False`.
  - Default retrieval filters automatically apply `timestamp <= 2026-01-21T12:00:00Z` and `is_decision_input=True`.
  - Synthetic event `MAINT_0003` (`2026-01-22T16:30:00Z`) is completely invisible to decision-time queries, preventing temporal leakage while remaining queryable in retrospective audit mode.

---

### 10. Representation Model Framing
- **Framing**: `TF-IDF/SVD Dense Retrieval Representation (Deterministic Statistical Baseline)`.
- **Properties**:
  - TF-IDF provides word n-gram statistical term representation (unigrams + bigrams, sublinear TF scaling).
  - TruncatedSVD (`n_components=256`, `random_state=42`) projects the sparse matrix into a compact, dense 256-dimensional space.
  - L2 unit-normalization ensures that dot-products correspond strictly to cosine similarity.
  - Completely deterministic across runs, zero network dependencies, 100% offline.
  - Clearly acknowledged: This is a robust statistical retrieval baseline, NOT a deep neural semantic embedding model.
- **Extensibility**: Includes `SentenceTransformerEmbedder` adapter interface with lazy imports and safety checks, ready for zero-friction neural upgrades when PyTorch / Transformer dependencies are added in future environments.

---

### 11. Vector Store & Exact Cosine Similarity
The `NumpyVectorStore` (`src/knowledge/indexing/vector_store.py`) provides:
- Exact matrix dot-product cosine similarity against unit-normalized embeddings.
- Deterministic memory-mapped `.npy` storage (`vector_embeddings.npy`, shape `(278, 256)`).
- Chunks metadata persisted in JSON format (`chunks_metadata.json`).
- Pre-filtering and post-filtering mechanisms enforcing metadata predicates.

---

### 12. Hybrid Scoring & Authority Weighting
The retrieval score blends dense vector representation similarity with exact lexical matching and source authority:
$$\text{Score} = (0.70 \cdot S_{\text{dense}} + 0.30 \cdot S_{\text{keyword}}) \cdot W_{\text{authority}}$$
- $S_{\text{dense}}$: Unit-vector dot product cosine similarity in $[0, 1]$.
- $S_{\text{keyword}}$: Informative query token overlap ratio in $[0, 1]$.
- $W_{\text{authority}}$: Epistemic source authority weight in $[0.50, 1.0]$.

---

### 13. Anti-Hallucination & Guardrails
To prevent hallucinated answers or grounding on spurious correlations:
1. **Entity Verification**: Rejects queries mentioning uncataloged machines (valid machines: `M1`–`M5`) or uncataloged factories (valid factory: `FAC_01`). Queries referencing non-existent entities (e.g. `M99`, `FAC_99`) immediately return `NO_SUFFICIENT_EVIDENCE`.
2. **Topical Anchor Keyword Threshold**: Requires retrieved candidates to exhibit a topical anchor match (`keyword_score >= 0.40`) against informative query terms. Unrelated queries (e.g. "approved 2027 factory expansion budget", "coolant explosion on Day 5") are safely rejected with `NO_SUFFICIENT_EVIDENCE`.
3. **Unprojectable Causal Query Guardrail**: Queries requesting uncomputable or unprojected counterfactual metrics (e.g., exact post-intervention failure probabilities without simulation models) are intercepted and rejected with `NO_SUFFICIENT_EVIDENCE`.
4. **Initial Heuristic Threshold**: Default retrieval cutoff is set to `INITIAL_HEURISTIC_THRESHOLD = 0.25`, explicitly documented as an initial operational heuristic rather than a statistically validated bound.

---

### 14. Benchmark Evaluation Results
Evaluated against the 13 authoritative test cases in `src/knowledge/evaluation/benchmark_dataset.py`:

| Metric | Target | Achieved | Status |
|---|---|---|---|
| Positive Queries Evaluated | 8 | 8 | PASSED |
| Negative Queries Evaluated | 5 | 5 | PASSED |
| **Mean Recall@5 (Positive)** | $\ge 0.90$ | **1.000 (100%)** | **EXCEEDED** |
| **Mean Reciprocal Rank (MRR)** | $\ge 0.75$ | **0.8125** | **EXCEEDED** |
| Mean Precision@5 | $\ge 0.40$ | **0.4750** | **PASSED** |
| **Anti-Hallucination Rejection Rate** | 1.000 (100%) | **1.000 (100%)** | **PERFECT** |
| False Positive Rejections | 0 | 0 | CLEAN |

#### Detailed Query Breakdown:
- **Q1 (M2 Health State)**: SUCCESS | Recall: 1.0 | Found sources: Phase 16, Phase 13, Phase 15.
- **Q2 (M2 Degradation Cause)**: SUCCESS | Recall: 1.0 | Found sources: Phase 7, Phase 12 (Mechanical Load / Bearing Wear).
- **Q3 (M2 Recommended Action)**: SUCCESS | Recall: 1.0 | Found sources: Phase 15 (`INSPECT_SPINDLE_BEARING`).
- **Q4 (M2 Bearing Stock)**: SUCCESS | Recall: 1.0 | Found sources: Phase 10, Phase 16.
- **Q5 (M2 Realized Financial Loss)**: SUCCESS | Recall: 1.0 | Found sources: Phase 14 (`₹73,062.28`).
- **Q6 (M2 Projected Opportunity Loss)**: SUCCESS | Recall: 1.0 | Found sources: Phase 14 (`₹24,320.00`).
- **Q7 (Retrospective M2 Event)**: SUCCESS | Recall: 1.0 | Found sources: Synthetic event `MAINT_0003`.
- **Q8 (Temporal Boundary Validation)**: SUCCESS | Recall: 1.0 | Correctly isolated across decision boundary.
- **NQ1 (Non-existent machine M99)**: `NO_SUFFICIENT_EVIDENCE` (Entity Guardrail).
- **NQ2 (Non-existent event: Coolant explosion)**: `NO_SUFFICIENT_EVIDENCE` (Topical Anchor Guardrail).
- **NQ3 (Unsupported financial: 2027 Expansion)**: `NO_SUFFICIENT_EVIDENCE` (Topical Anchor Guardrail).
- **NQ4 (Unprojectable metric: Exact post-service failure probability)**: `NO_SUFFICIENT_EVIDENCE` (Causal Guardrail).
- **NQ5 (Non-existent factory FAC_99)**: `NO_SUFFICIENT_EVIDENCE` (Entity Guardrail).

---

### 15. Test Suite Verification
All 16 unit and integration tests in `tests/test_knowledge_rag.py` pass cleanly:
1. `test_knowledge_registry_completeness_and_safety`: PASSED
2. `test_text_cleaner_and_credential_scrubber`: PASSED
3. `test_document_loader_and_markdown_chunker`: PASSED
4. `test_structured_chunker_provenance`: PASSED
5. `test_representation_determinism`: PASSED
6. `test_vector_store_persistence_roundtrip`: PASSED
7. `test_temporal_decision_boundary_isolation`: PASSED
8. `test_temporal_boundary_evidence_query_8`: PASSED
9. `test_epistemic_status_preservation`: PASSED
10. `test_source_authority_financial_m2_gross_exposure`: PASSED
11. `test_benchmark_positive_queries_recall_and_mrr`: PASSED
12. `test_anti_hallucination_negative_queries_rejection`: PASSED
13. `test_unprojectable_causal_metrics_guardrail`: PASSED
14. `test_initial_heuristic_rejection_threshold_labeling`: PASSED
15. `test_transformer_embedder_adapter_safety`: PASSED
16. `test_reproducibility_manifest`: PASSED

---

### 16. Full Regression Results
Full regression suite across the entire project:
- **Total Tests**: 310
- **Passed**: 309
- **Skipped**: 1 (`tests/test_phase17_persistence.py::test_postgresql_connection` due to offline PostgreSQL)
- **Failed**: 0
- **Regressions**: ZERO

---

### 17. Dataset Integrity & Baseline Compliance
The core analytical datasets were preserved without any alteration:
- `data/processed/operational_losses.csv`:
  - **MD5 Checksum**: `34B12582B32D81E3121429C55EBF74E8` (Verified identical to Phase 14–18 baseline).
- No modifications were made to `C:\Users\user\OneDrive\Desktop\NIRMAAN\DATASET`.

---

### 18. Dependencies & Environment Compliance
- **Python Version**: Python 3.14.6
- **Installed Packages Used**:
  - `scikit-learn 1.9.0` (TF-IDF vectorizer, TruncatedSVD)
  - `numpy 2.4.6` (Unit vector dot products, array storage)
  - `scipy 1.18.0` (Sparse linear algebra)
  - `pydantic 2.13.4` (Strict type validation)
  - `pytest 9.1.1` (Automated testing)
- **No external packages were installed**.

---

### 19. Upstream Phase Governance
- **Phases 0–16**: Complete, locked, and untouched.
- **Phase 17**: Persists in `HOLD — ENVIRONMENT BLOCKED` status (Implementation verified; live PostgreSQL unavailable in current local environment).
- **Phase 18**: Persists in `HOLD — ENVIRONMENT BLOCKED` status (FastAPI implementation verified; live PostgreSQL backend connection unavailable).
- **Phase 19**: Successfully implemented, verified, and locked.

---

### 20. Reproducibility Manifest
A complete reproducibility manifest (`models/knowledge/manifest.json`) records SHA-256 hashes and dimensions for all artifacts:
- `vector_embeddings.npy`: 278 rows, 256 columns.
- `chunks_metadata.json`: 278 chunk records.
- `tfidf_svd_model.joblib`: Trained representation pipeline.

---

### 21. Limitations & Future Work
- The dense representation model is statistical (TF-IDF + TruncatedSVD). It provides deterministic and fast retrieval for domain keywords, but does not capture abstract conceptual synonyms as richly as a deep contextual transformer model.
- When an environment with GPU/PyTorch or `sentence-transformers` is available, the system can seamlessly switch to `SentenceTransformerEmbedder` using the pluggable interface provided in `src/knowledge/embeddings/transformer_embedder.py`.

---

### 22. Readiness for Phase 20 (AI Factory Copilot)
The Factory Knowledge Memory and RAG Engine is fully ready to serve as the grounding layer for Phase 20 (AI Factory Copilot). The Copilot will be able to invoke `retriever.retrieve(query)` to obtain structured, provenance-linked `EvidenceItem` objects with guaranteed epistemic tags, zero temporal leakage, and full traceability.

---

### 23. Git Status & Commit Record
- **Branch**: `main`
- **Working Tree**: Clean
- **Commit**: `feat(phase-19): implement factory knowledge memory and rag engine`
