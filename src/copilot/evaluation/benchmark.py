"""
NirmaanAI Phase 20: Copilot Benchmark Evaluation Suite
Evaluates positive domain queries, negative guardrail queries, and temporal boundary inquiries.
"""

from pathlib import Path
import json
import time
from typing import Any, Dict, List

from src.copilot.copilot_service import FactoryCopilotService
from src.copilot.schemas import CopilotContext, CopilotStatus

COPILOT_BENCHMARK_CASES = [
    # Positive Queries
    {
        "query_id": "Q1",
        "query": "What is the health of M2?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["26.88", "CRITICAL", "0.9959"],
        "is_negative": False,
    },
    {
        "query_id": "Q2",
        "query": "Why is M2 degrading?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["MECHANICAL_LOAD", "spindle", "bearing"],
        "is_negative": False,
    },
    {
        "query_id": "Q3",
        "query": "What maintenance action is recommended for M2?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["INSPECT_SPINDLE_BEARING", "EXPEDITE_CRITICAL_SPARE"],
        "is_negative": False,
    },
    {
        "query_id": "Q4",
        "query": "What is the M2 bearing inventory status?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["2.0", "1.134", "1.0", "SKU_SPINDLE_BEARING_M2"],
        "is_negative": False,
    },
    {
        "query_id": "Q5",
        "query": "What is M2's realized financial loss?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["73,062.28"],
        "forbidden_terms": ["92,582.28"],
        "is_negative": False,
    },
    {
        "query_id": "Q6",
        "query": "What is M2's gross financial exposure?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["97,382.28", "73,062.28", "24,320.00"],
        "forbidden_terms": ["92,582.28"],
        "is_negative": False,
    },
    {
        "query_id": "Q7",
        "query": "What bottleneck risk does M2 have?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["bottleneck", "1.38", "76"],
        "is_negative": False,
    },
    {
        "query_id": "Q8",
        "query": "What evidence exists about the M2 retrospective event?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["MAINT_0003", "150", "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"],
        "is_negative": False,
    },
    # Negative Queries
    {
        "query_id": "NQ1",
        "query": "What is the health of M99?",
        "expected_status": CopilotStatus.NO_SUFFICIENT_EVIDENCE,
        "is_negative": True,
    },
    {
        "query_id": "NQ2",
        "query": "What happened during the coolant explosion?",
        "expected_status": CopilotStatus.NO_SUFFICIENT_EVIDENCE,
        "is_negative": True,
    },
    {
        "query_id": "NQ3",
        "query": "What is the approved 2027 expansion budget?",
        "expected_status": CopilotStatus.NO_SUFFICIENT_EVIDENCE,
        "is_negative": True,
    },
    {
        "query_id": "NQ4",
        "query": "What is the exact post-service failure probability?",
        "expected_status": CopilotStatus.NO_SUFFICIENT_EVIDENCE,
        "is_negative": True,
    },
    {
        "query_id": "NQ5",
        "query": "Tell me something unrelated to the factory that is not in the knowledge base.",
        "expected_status": CopilotStatus.NO_SUFFICIENT_EVIDENCE,
        "is_negative": True,
    },
    # Temporal Boundary Query
    {
        "query_id": "TQ1",
        "query": "Was MAINT_0003 part of the prospective decision evidence?",
        "expected_status": CopilotStatus.SUCCESS,
        "expected_terms": ["No", "post-cutoff", "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"],
        "is_negative": False,
    },
]


def run_copilot_evaluation(service: FactoryCopilotService) -> Dict[str, Any]:
    """Runs all benchmark test cases and computes performance metrics."""
    results: List[Dict[str, Any]] = []
    positive_count = 0
    positive_passed = 0
    negative_count = 0
    negative_rejected = 0

    for case in COPILOT_BENCHMARK_CASES:
        start_t = time.perf_counter()
        resp = service.ask(case["query"])
        latency_ms = (time.perf_counter() - start_t) * 1000

        is_neg = case["is_negative"]
        status_match = resp.status == case["expected_status"]

        terms_passed = True
        if not is_neg and "expected_terms" in case:
            for term in case["expected_terms"]:
                if term.lower() not in resp.answer.lower():
                    terms_passed = False
                    break

        forbidden_passed = True
        if "forbidden_terms" in case:
            for term in case["forbidden_terms"]:
                if term in resp.answer:
                    forbidden_passed = False
                    break

        passed = status_match and terms_passed and forbidden_passed

        if is_neg:
            negative_count += 1
            if passed:
                negative_rejected += 1
        else:
            positive_count += 1
            if passed:
                positive_passed += 1

        results.append({
            "query_id": case["query_id"],
            "query": case["query"],
            "is_negative": is_neg,
            "status": resp.status.value,
            "expected_status": case["expected_status"].value,
            "passed": passed,
            "latency_ms": round(latency_ms, 2),
            "evidence_count": resp.evidence_count,
            "epistemic_status": resp.epistemic_status,
            "confidence": resp.confidence,
            "answer_preview": resp.answer[:150] + "...",
        })

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_evaluated": len(COPILOT_BENCHMARK_CASES),
        "positive_evaluated": positive_count,
        "positive_passed": positive_passed,
        "positive_accuracy": positive_passed / positive_count if positive_count else 0.0,
        "negative_evaluated": negative_count,
        "negative_rejected": negative_rejected,
        "negative_rejection_rate": negative_rejected / negative_count if negative_count else 0.0,
        "overall_passed": positive_passed + negative_rejected,
        "overall_accuracy": (positive_passed + negative_rejected) / len(COPILOT_BENCHMARK_CASES),
        "detailed_results": results,
    }

    # Save to models/copilot/copilot_evaluation.json
    out_dir = Path("models/copilot")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "copilot_evaluation.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
