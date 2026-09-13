"""
NirmaanAI Phase 19: Benchmark Evaluation Dataset
Defines the 13 curated source/chunk level evaluation queries:
- 8 authoritative factory domain queries (Q1–Q8)
- 5 anti-hallucination negative queries (NQ1–NQ5)
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class BenchmarkTestCase(BaseModel):
    query_id: str
    query: str
    is_negative: bool = False
    expected_status: str = "SUCCESS"
    target_phases: List[int] = Field(default_factory=list)
    target_sources: List[str] = Field(default_factory=list)
    expected_terms: List[str] = Field(default_factory=list)
    include_retrospective: bool = False
    description: str = ""


BENCHMARK_TEST_CASES: List[BenchmarkTestCase] = [
    # Q1: M2 Current Health
    BenchmarkTestCase(
        query_id="Q1_M2_HEALTH",
        query="What is the current health state of M2?",
        target_phases=[13],
        target_sources=["DOC_PHASE_13_HEALTH", "SUMMARY_PHASE_13_HEALTH"],
        expected_terms=["26.88", "CRITICAL"],
        description="Retrieves Phase 13 health report evidence establishing M2 score 26.88 and CRITICAL band.",
    ),
    # Q2: M2 Degradation Cause
    BenchmarkTestCase(
        query_id="Q2_M2_DEGRADATION",
        query="What caused the M2 degradation?",
        target_phases=[7, 8, 12],
        target_sources=["DOC_PHASE_12_RCA", "SUMMARY_PHASE_12_RCA", "DOC_PHASE_07_ANOMALY"],
        expected_terms=["bearing", "mechanical", "vibration"],
        description="Retrieves Phase 12 RCA diagnostic evaluation and Phase 7 anomaly evidence.",
    ),
    # Q3: M2 Recommendation
    BenchmarkTestCase(
        query_id="Q3_M2_RECOMMENDATION",
        query="What maintenance action was recommended for M2?",
        target_phases=[15],
        target_sources=["DOC_PHASE_15_RECOMMENDATIONS", "DOC_PHASE_15_RULES", "SUMMARY_PHASE_15_RECOMMENDATIONS"],
        expected_terms=["INSPECT_SPINDLE_BEARING"],
        description="Retrieves Phase 15 operational recommendations evidence for M2.",
    ),
    # Q4: M2 Bearing Inventory
    BenchmarkTestCase(
        query_id="Q4_M2_INVENTORY",
        query="What is the M2 bearing stock?",
        target_phases=[10],
        target_sources=["DOC_PHASE_10_INVENTORY"],
        expected_terms=["2.0", "1.134", "1.367"],
        description="Retrieves Phase 10 inventory contracts evidence (Stock 2.0, SS 1.134, ROP 1.367).",
    ),
    # Q5: M2 Realized Loss
    BenchmarkTestCase(
        query_id="Q5_M2_REALIZED_LOSS",
        query="What was the realized M2 loss?",
        target_phases=[14],
        target_sources=["DOC_PHASE_14_FINANCIAL_LOSS", "SUMMARY_PHASE_14_LOSS"],
        expected_terms=["73,062.28", "73062.28"],
        description="Retrieves Phase 14 realized historical loss evidence (₹73,062.28).",
    ),
    # Q6: M2 Projected Opportunity Cost
    BenchmarkTestCase(
        query_id="Q6_M2_PROJECTED_OPPORTUNITY",
        query="What is the projected opportunity?",
        target_phases=[14],
        target_sources=["DOC_PHASE_14_FINANCIAL_LOSS"],
        expected_terms=["24,320", "24320"],
        description="Retrieves Phase 14 baseline projected opportunity cost evidence (₹24,320.00).",
    ),
    # Q7: Retrospective Ground Truth Event
    BenchmarkTestCase(
        query_id="Q7_RETROSPECTIVE_EVENT",
        query="What happened during the retrospective M2 event?",
        target_phases=[5],
        target_sources=["EVENT_MAINT_0003_RETROSPECTIVE"],
        expected_terms=["MAINT_0003", "seizure", "2026-01-22"],
        include_retrospective=True,
        description="Explicitly retrieves MAINT_0003 retrospective ground truth when requested.",
    ),
    # Q8: Temporal Boundary Evidence
    BenchmarkTestCase(
        query_id="Q8_TEMPORAL_BOUNDARY",
        query="Retrieve evidence demonstrating the temporal boundary of MAINT_0003",
        target_phases=[5],
        target_sources=["EVENT_MAINT_0003_RETROSPECTIVE"],
        expected_terms=["2026-01-22T16:30:00Z", "2026-01-21T12:00:00Z", "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"],
        include_retrospective=True,
        description="Retrieves evidence establishing MAINT_0003 occurred after DECISION_CUTOFF.",
    ),
    # NQ1: Nonexistent Machine
    BenchmarkTestCase(
        query_id="NQ1_NONEXISTENT_MACHINE",
        query="What is the current health status of machine M99?",
        is_negative=True,
        expected_status="NO_SUFFICIENT_EVIDENCE",
        description="Negative test asserting rejection for nonexistent machine M99.",
    ),
    # NQ2: Nonexistent Failure Event
    BenchmarkTestCase(
        query_id="NQ2_NONEXISTENT_EVENT",
        query="What happened during the coolant explosion on Day 5?",
        is_negative=True,
        expected_status="NO_SUFFICIENT_EVIDENCE",
        description="Negative test asserting rejection for ungrounded catastrophic event.",
    ),
    # NQ3: Unsupported Financial Budget
    BenchmarkTestCase(
        query_id="NQ3_UNSUPPORTED_FINANCIAL",
        query="What is the approved 2027 factory expansion budget?",
        is_negative=True,
        expected_status="NO_SUFFICIENT_EVIDENCE",
        description="Negative test asserting rejection for unsupported corporate financial metrics.",
    ),
    # NQ4: Unprojectable Metric Query
    BenchmarkTestCase(
        query_id="NQ4_UNPROJECTABLE_METRIC",
        query="What is the exact post-service failure probability?",
        is_negative=True,
        expected_status="NO_SUFFICIENT_EVIDENCE",
        description="Negative test asserting rejection for unsupported causal post-intervention states.",
    ),
    # NQ5: Nonexistent Factory
    BenchmarkTestCase(
        query_id="NQ5_NONEXISTENT_FACTORY",
        query="Retrieve historical maintenance records for factory FAC_99",
        is_negative=True,
        expected_status="NO_SUFFICIENT_EVIDENCE",
        description="Negative test asserting rejection for out-of-scope factory plant.",
    ),
]
