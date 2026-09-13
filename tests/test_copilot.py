"""
NirmaanAI Phase 20: AI Factory Copilot Test Suite
Validates intent classification, entity extraction, temporal governance,
epistemic tracking, authoritative financial protection, and anti-hallucination guardrails.
"""

import pytest

from src.copilot.copilot_service import FactoryCopilotService
from src.copilot.entities import EntityExtractor
from src.copilot.evaluation.benchmark import run_copilot_evaluation
from src.copilot.intent import IntentClassifier
from src.copilot.schemas import (
    CopilotContext,
    CopilotIntent,
    CopilotResponse,
    CopilotStatus,
)
from src.copilot.temporal import TemporalInterpreter
from src.knowledge.indexing.index_manager import KnowledgeIndexManager
from src.knowledge.retrieval.retriever import KnowledgeRetriever
from src.knowledge.schemas import EpistemicStatus


@pytest.fixture(scope="module")
def copilot_service():
    """Builds or loads the KnowledgeRetriever and initializes FactoryCopilotService."""
    manager = KnowledgeIndexManager()
    if not manager.is_built():
        vector_store, embedder = manager.build_index()
    else:
        vector_store, embedder = manager.load()
    retriever = KnowledgeRetriever(vector_store, embedder)
    return FactoryCopilotService(retriever=retriever)


# ==============================================================================
# 1. INTENT CLASSIFICATION TESTS
# ==============================================================================

def test_intent_classification():
    """Verifies deterministic classification across operational intents."""
    assert IntentClassifier.classify("What is the current health of machine M2?") == CopilotIntent.MACHINE_HEALTH
    assert IntentClassifier.classify("Why is M2 degrading?") == CopilotIntent.ROOT_CAUSE
    assert IntentClassifier.classify("What maintenance action is recommended for M2?") == CopilotIntent.RECOMMENDATION
    assert IntentClassifier.classify("What is the M2 bearing inventory status?") == CopilotIntent.INVENTORY_STATUS
    assert IntentClassifier.classify("What is M2's realized financial loss?") == CopilotIntent.FINANCIAL_IMPACT
    assert IntentClassifier.classify("What bottleneck risk does M2 have?") == CopilotIntent.BOTTLENECK_STATUS
    assert IntentClassifier.classify("What happened during the retrospective M2 event?") == CopilotIntent.TEMPORAL_HISTORY
    assert IntentClassifier.classify("What if we reduce machine feed rate in Scenario D?") == CopilotIntent.WHAT_IF
    assert IntentClassifier.classify("What is the failure probability for M1?") == CopilotIntent.PREDICTIVE_MAINTENANCE
    assert IntentClassifier.classify("What is the anomaly score on M2?") == CopilotIntent.ANOMALY_STATUS
    assert IntentClassifier.classify("What is the weather outside the plant?") == CopilotIntent.UNSUPPORTED_QUERY
    assert IntentClassifier.classify("What is the approved 2027 expansion budget?") == CopilotIntent.UNSUPPORTED_QUERY


# ==============================================================================
# 2. ENTITY EXTRACTION & VALIDATION TESTS
# ==============================================================================

def test_entity_extraction_valid():
    """Extracts known machines, factories, metrics, and phases."""
    extracted = EntityExtractor.extract_all("Check health score and failure probability on machine M2 in factory FAC_01 for Phase 13")
    assert "M2" in extracted["valid_machines"]
    assert "FAC_01" in extracted["valid_factories"]
    assert "health_score" in extracted["metrics"]
    assert "failure_probability" in extracted["metrics"]
    assert 13 in extracted["phases"]
    assert extracted["has_invalid_entities"] is False


def test_entity_extraction_invalid_rejection(copilot_service):
    """Rejects uncataloged machines (e.g. M99) and uncataloged factories (e.g. FAC_99)."""
    # M99 rejection
    resp_m99 = copilot_service.ask("What is the health status of machine M99?")
    assert resp_m99.status == CopilotStatus.NO_SUFFICIENT_EVIDENCE
    assert resp_m99.confidence == "NO_EVIDENCE"
    assert "M99" in str(resp_m99.rejection_reason)

    # FAC_99 rejection
    resp_fac99 = copilot_service.ask("Retrieve maintenance history for factory FAC_99")
    assert resp_fac99.status == CopilotStatus.NO_SUFFICIENT_EVIDENCE
    assert "FAC_99" in str(resp_fac99.rejection_reason)


# ==============================================================================
# 3. PHASE 19 RETRIEVAL & PROVENANCE INTEGRATION TESTS
# ==============================================================================

def test_phase19_retrieval_and_provenance(copilot_service):
    """Verifies that Copilot queries retrieve Phase 19 evidence and retain provenance."""
    resp = copilot_service.ask("What is the health of M2?")
    assert resp.status == CopilotStatus.SUCCESS
    assert resp.evidence_count >= 1
    assert len(resp.provenance) >= 1

    first_prov = resp.provenance[0]
    assert "source_id" in first_prov
    assert "phase" in first_prov
    assert "file_path" in first_prov
    assert "epistemic_status" in first_prov


# ==============================================================================
# 4. TEMPORAL BOUNDARY & RETROSPECTIVE ISOLATION TESTS
# ==============================================================================

def test_prospective_temporal_boundary_isolation(copilot_service):
    """Default prospective queries must NOT include post-cutoff retrospective event MAINT_0003."""
    resp = copilot_service.ask("What maintenance actions have occurred on M2?")
    assert resp.status == CopilotStatus.SUCCESS
    for item in resp.evidence:
        assert item.is_decision_input is True
        assert item.source_id != "EVENT_MAINT_0003_RETROSPECTIVE"


def test_retrospective_event_access(copilot_service):
    """Retrospective queries access MAINT_0003 and clearly label it."""
    resp = copilot_service.ask("What evidence exists about the M2 retrospective event?")
    assert resp.status == CopilotStatus.SUCCESS
    assert resp.retrospective is True
    assert resp.epistemic_status == EpistemicStatus.RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.value
    assert "MAINT_0003" in resp.answer
    assert "150" in resp.answer


def test_temporal_boundary_query_tq1(copilot_service):
    """TQ1: Verifies response to 'Was MAINT_0003 part of the prospective decision evidence?'"""
    resp = copilot_service.ask("Was MAINT_0003 part of the prospective decision evidence?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "No" in resp.answer
    assert "post-cutoff" in resp.answer.lower()
    assert "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH" in resp.answer


# ==============================================================================
# 5. EPISTEMIC FIDELITY & FINANCIAL GOVERNANCE TESTS
# ==============================================================================

def test_epistemic_status_preservation(copilot_service):
    """Asserts that model predictions are tagged MODEL_OUTPUT, not OBSERVED."""
    resp = copilot_service.ask("What is the health of M2?")
    assert resp.epistemic_status == EpistemicStatus.MODEL_OUTPUT.value
    assert resp.epistemic_status != EpistemicStatus.OBSERVED.value


def test_superseded_financial_protection(copilot_service):
    """
    Verifies that authoritative Phase 14 financial exposure (₹97,382.28) is returned
    and the superseded preliminary draft figure (₹92,582.28) is excluded.
    """
    resp = copilot_service.ask("What is M2's gross financial exposure?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "97,382.28" in resp.answer
    assert "73,062.28" in resp.answer
    assert "24,320.00" in resp.answer
    assert "92,582.28" not in resp.answer


def test_realized_loss_accuracy(copilot_service):
    """Verifies that realized loss returns ₹73,062.28 without combining opportunity cost."""
    resp = copilot_service.ask("What is M2's realized financial loss?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "73,062.28" in resp.answer


# ==============================================================================
# 6. DOMAIN GROUNDING TESTS (RECOMMENDATION, RCA, INVENTORY, BOTTLENECK)
# ==============================================================================

def test_recommendation_grounding(copilot_service):
    """Verifies that M2 recommendation returns approved action INSPECT_SPINDLE_BEARING."""
    resp = copilot_service.ask("What maintenance action is recommended for M2?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "INSPECT_SPINDLE_BEARING" in resp.answer
    assert "CRITICAL" in resp.answer
    assert "IMMEDIATE" in resp.answer


def test_rca_grounding(copilot_service):
    """Verifies that M2 root cause analysis returns MECHANICAL_LOAD."""
    resp = copilot_service.ask("Why is M2 degrading?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "MECHANICAL_LOAD" in resp.answer
    assert "Phase 12" in resp.answer or "Root Cause" in resp.answer


def test_inventory_grounding(copilot_service):
    """Verifies that M2 bearing stock returns 2.0 on hand, 1.134 safety stock, 1.0 post-action."""
    resp = copilot_service.ask("What is the M2 bearing inventory status?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "2.0" in resp.answer
    assert "1.134" in resp.answer
    assert "1.0" in resp.answer
    assert "SKU_SPINDLE_BEARING_M2" in resp.answer


def test_bottleneck_grounding(copilot_service):
    """Verifies that M2 bottleneck query returns cycle ratio 1.38 and 76 delayed units."""
    resp = copilot_service.ask("What bottleneck risk does M2 have?")
    assert resp.status == CopilotStatus.SUCCESS
    assert "1.38" in resp.answer
    assert "76" in resp.answer
    assert "bottleneck" in resp.answer.lower()


# ==============================================================================
# 7. ANTI-HALLUCINATION & GUARDRAILS TESTS
# ==============================================================================

def test_unprojectable_causal_metrics_guardrail(copilot_service):
    """Refuses queries requesting unprojectable post-service metrics."""
    resp = copilot_service.ask("What is the exact post-service failure probability?")
    assert resp.status == CopilotStatus.NO_SUFFICIENT_EVIDENCE
    assert "NOT_PROJECTABLE" in resp.answer
    assert resp.confidence == "NO_EVIDENCE"


def test_negative_queries_rejection(copilot_service):
    """Verifies rejection of unsupported out-of-scope or non-existent entity queries."""
    negative_queries = [
        "What is the health of M99?",
        "What happened during the coolant explosion?",
        "What is the approved 2027 expansion budget?",
        "What is the exact post-service failure probability?",
        "Tell me something unrelated to the factory that is not in the knowledge base.",
    ]
    for q in negative_queries:
        resp = copilot_service.ask(q)
        assert resp.status == CopilotStatus.NO_SUFFICIENT_EVIDENCE
        assert resp.evidence_count == 0


def test_deterministic_reproducibility(copilot_service):
    """Verifies that querying identical questions returns byte-for-byte deterministic answers."""
    resp1 = copilot_service.ask("What is the health of M2?")
    resp2 = copilot_service.ask("What is the health of M2?")
    assert resp1.answer == resp2.answer
    assert resp1.epistemic_status == resp2.epistemic_status
    assert resp1.status == resp2.status


def test_benchmark_suite_evaluation(copilot_service):
    """Runs the complete 14-case benchmark and validates 100% accuracy."""
    summary = run_copilot_evaluation(copilot_service)
    assert summary["positive_accuracy"] == 1.0
    assert summary["negative_rejection_rate"] == 1.0
    assert summary["overall_accuracy"] == 1.0


def test_copilot_fastapi_endpoints():
    """Verifies that FastAPI properly exposes /api/v1/copilot/ask and /health."""
    from fastapi.testclient import TestClient
    from app.main import create_app

    app = create_app()
    client = TestClient(app)

    # Health check
    health_res = client.get("/api/v1/copilot/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "healthy"
    assert health_data["subsystem"] == "AI Factory Copilot (Phase 20)"

    # Ask endpoint
    ask_res = client.post(
        "/api/v1/copilot/ask",
        json={
            "query": "What is the health of M2?",
            "context": {
                "user_role": "OPERATOR",
                "factory_id": "FAC_01",
                "machine_id": "M2",
            },
        },
    )
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert ask_data["status"] == "SUCCESS"
    assert "26.88" in ask_data["answer"]
    assert ask_data["intent"] == "MACHINE_HEALTH"
    assert ask_data["evidence_count"] >= 1

