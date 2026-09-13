"""
NirmaanAI Phase 19: Knowledge Source Registry
Strictly defines the approved, locked knowledge sources for ingestion.
Rejects unauthorized external paths, credentials, and virtual environment files.
"""

from pathlib import Path
from typing import Dict, List, Optional
from src.knowledge.schemas import EpistemicStatus, KnowledgeSource, KnowledgeSourceType

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Decision cutoff constant
DECISION_CUTOFF = "2026-01-21T12:00:00Z"

# Approved Knowledge Sources Catalog
APPROVED_SOURCES: Dict[str, KnowledgeSource] = {
    # Phase 3: EDA
    "DOC_PHASE_03_EDA": KnowledgeSource(
        source_id="DOC_PHASE_03_EDA",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 3 Exploratory Data Analysis & Sensor Profiling",
        file_path="docs/eda/eda_summary_report.md",
        phase=3,
        default_epistemic_status=EpistemicStatus.OBSERVED,
        authority_weight=0.90,
    ),
    # Phase 4: Schema
    "DOC_PHASE_04_SCHEMA": KnowledgeSource(
        source_id="DOC_PHASE_04_SCHEMA",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 4 Unified Manufacturing Plant Data Schema",
        file_path="docs/schema/unified_factory_schema.md",
        phase=4,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=0.90,
    ),
    # Phase 5: Synthetic Factory
    "DOC_PHASE_05_SYNTHETIC": KnowledgeSource(
        source_id="DOC_PHASE_05_SYNTHETIC",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 5 Synthetic Factory Specification & Physics Degradation",
        file_path="docs/data/synthetic_data_specification.md",
        phase=5,
        default_epistemic_status=EpistemicStatus.CONTROLLED_SYNTHETIC,
        authority_weight=0.90,
    ),
    # Phase 6: Predictive Maintenance
    "DOC_PHASE_06_PDM": KnowledgeSource(
        source_id="DOC_PHASE_06_PDM",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 6 Predictive Maintenance XGBoost Classification & RUL",
        file_path="docs/models/predictive_maintenance_report.md",
        phase=6,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 7: Anomaly Detection
    "DOC_PHASE_07_ANOMALY": KnowledgeSource(
        source_id="DOC_PHASE_07_ANOMALY",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 7 Multi-Detector Vibration & Physics Anomaly Detection",
        file_path="docs/models/anomaly_detection_report.md",
        phase=7,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 8: Bottleneck Prediction
    "DOC_PHASE_08_BOTTLENECK": KnowledgeSource(
        source_id="DOC_PHASE_08_BOTTLENECK",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 8 Production Line Bottleneck Detection & Heuristic Cutoff",
        file_path="docs/models/bottleneck_prediction_report.md",
        phase=8,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 9: Forecasting
    "DOC_PHASE_09_FORECASTING": KnowledgeSource(
        source_id="DOC_PHASE_09_FORECASTING",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 9 Production Volume & Sensor Telemetry Forecasting",
        file_path="docs/models/forecasting_report.md",
        phase=9,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 10: Inventory
    "DOC_PHASE_10_INVENTORY": KnowledgeSource(
        source_id="DOC_PHASE_10_INVENTORY",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 10 Inventory Intelligence & Critical Spare Parts Optimization",
        file_path="docs/models/inventory_intelligence_report.md",
        phase=10,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=0.95,
    ),
    # Phase 11: SHAP
    "DOC_PHASE_11_SHAP": KnowledgeSource(
        source_id="DOC_PHASE_11_SHAP",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 11 Model Explainability & SHAP Feature Attributions",
        file_path="docs/explainability/shap_report.md",
        phase=11,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 12: RCA
    "DOC_PHASE_12_RCA": KnowledgeSource(
        source_id="DOC_PHASE_12_RCA",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 12 Root Cause Analysis Diagnostic Evaluation",
        file_path="docs/rca/root_cause_analysis_report.md",
        phase=12,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 13: Health Scores
    "DOC_PHASE_13_HEALTH": KnowledgeSource(
        source_id="DOC_PHASE_13_HEALTH",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 13 Machine Health Scoring & Locked Health Bands",
        file_path="docs/health/factory_health_score_report.md",
        phase=13,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
    ),
    # Phase 14: Financial Loss
    "DOC_PHASE_14_FINANCIAL_LOSS": KnowledgeSource(
        source_id="DOC_PHASE_14_FINANCIAL_LOSS",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 14 Operational Loss Accounting & Opportunity Cost Segregation",
        file_path="docs/loss/operational_loss_report.md",
        phase=14,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
    ),
    # Phase 15: Recommendations
    "DOC_PHASE_15_RECOMMENDATIONS": KnowledgeSource(
        source_id="DOC_PHASE_15_RECOMMENDATIONS",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 15 Operational Recommendation Engine & 26-Action Taxonomy",
        file_path="docs/recommendations/recommendation_engine.md",
        phase=15,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
    ),
    "DOC_PHASE_15_RULES": KnowledgeSource(
        source_id="DOC_PHASE_15_RULES",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 15 Recommendation Decision Rules Catalog",
        file_path="docs/recommendations/recommendation_rules.md",
        phase=15,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
    ),
    # Phase 16: Simulation
    "DOC_PHASE_16_SIMULATION": KnowledgeSource(
        source_id="DOC_PHASE_16_SIMULATION",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 16 Digital-Twin What-If Simulation Engine & Scenario Catalog",
        file_path="docs/simulation/simulation_engine.md",
        phase=16,
        default_epistemic_status=EpistemicStatus.PROJECTED,
        authority_weight=1.00,
    ),
    "DOC_PHASE_16_SCENARIOS": KnowledgeSource(
        source_id="DOC_PHASE_16_SCENARIOS",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 16 Counterfactual Scenario Catalog & Avoided Opportunity Costs",
        file_path="docs/simulation/scenario_catalog.md",
        phase=16,
        default_epistemic_status=EpistemicStatus.PROJECTED,
        authority_weight=1.00,
    ),
    # Phase 17: Database
    "DOC_PHASE_17_DATABASE": KnowledgeSource(
        source_id="DOC_PHASE_17_DATABASE",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 17 PostgreSQL Persistence Layer & Production Data Models",
        file_path="docs/database/architecture.md",
        phase=17,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
    ),
    # Phase 18: API
    "DOC_PHASE_18_API": KnowledgeSource(
        source_id="DOC_PHASE_18_API",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        title="Phase 18 FastAPI Production Backend Architecture & Endpoints",
        file_path="docs/api/architecture.md",
        phase=18,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
    ),
    # Model Summaries
    "SUMMARY_PHASE_13_HEALTH": KnowledgeSource(
        source_id="SUMMARY_PHASE_13_HEALTH",
        source_type=KnowledgeSourceType.MODEL_SUMMARY,
        title="Authoritative Machine & Factory Health Summary",
        file_path="models/health/health_summary.json",
        phase=13,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
        machine_id="M2",
    ),
    "SUMMARY_PHASE_14_LOSS": KnowledgeSource(
        source_id="SUMMARY_PHASE_14_LOSS",
        source_type=KnowledgeSourceType.MODEL_SUMMARY,
        title="Authoritative Operational Loss Summary",
        file_path="models/loss/loss_summary.json",
        phase=14,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
        machine_id="M2",
    ),
    "SUMMARY_PHASE_12_RCA": KnowledgeSource(
        source_id="SUMMARY_PHASE_12_RCA",
        source_type=KnowledgeSourceType.MODEL_SUMMARY,
        title="Authoritative Root Cause Analysis Summary",
        file_path="models/rca/rca_summary.json",
        phase=12,
        default_epistemic_status=EpistemicStatus.MODEL_OUTPUT,
        authority_weight=0.95,
        machine_id="M2",
    ),
    "SUMMARY_PHASE_15_RECOMMENDATIONS": KnowledgeSource(
        source_id="SUMMARY_PHASE_15_RECOMMENDATIONS",
        source_type=KnowledgeSourceType.MODEL_SUMMARY,
        title="Authoritative Operational Recommendations Summary",
        file_path="models/recommendations/recommendation_summary.json",
        phase=15,
        default_epistemic_status=EpistemicStatus.DERIVED,
        authority_weight=1.00,
        machine_id="M2",
    ),
    "SUMMARY_PHASE_16_SIMULATION": KnowledgeSource(
        source_id="SUMMARY_PHASE_16_SIMULATION",
        source_type=KnowledgeSourceType.MODEL_SUMMARY,
        title="Authoritative What-If Simulation Scenarios Summary",
        file_path="models/simulation/simulation_summary.json",
        phase=16,
        default_epistemic_status=EpistemicStatus.PROJECTED,
        authority_weight=1.00,
        machine_id="M2",
    ),
    # Controlled Retrospective Ground Truth Event
    "EVENT_MAINT_0003_RETROSPECTIVE": KnowledgeSource(
        source_id="EVENT_MAINT_0003_RETROSPECTIVE",
        source_type=KnowledgeSourceType.GROUND_TRUTH_EVENT,
        title="Controlled Retrospective Ground Truth Event MAINT_0003",
        file_path="docs/data/synthetic_data_specification.md",
        phase=5,
        default_epistemic_status=EpistemicStatus.RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH,
        authority_weight=1.00,
        machine_id="M2",
    ),
}


class KnowledgeRegistry:
    """Manages approved knowledge sources and enforces path boundary restrictions."""

    @staticmethod
    def get_all_sources() -> List[KnowledgeSource]:
        """Returns all registered knowledge sources."""
        return list(APPROVED_SOURCES.values())

    @staticmethod
    def get_source(source_id: str) -> Optional[KnowledgeSource]:
        """Retrieves a source by its ID."""
        return APPROVED_SOURCES.get(source_id)

    @staticmethod
    def is_approved_path(rel_path: str) -> bool:
        """Verifies if a relative path is approved for knowledge ingestion."""
        norm_path = rel_path.replace("\\", "/").lstrip("./")
        return any(s.file_path.replace("\\", "/") == norm_path for s in APPROVED_SOURCES.values())

    @staticmethod
    def validate_file_safety(file_path: Path) -> None:
        """
        Guarantees security boundaries:
        - Must reside inside project root.
        - Must not be a secret/.env file.
        - Must not access external Desktop dataset directory.
        """
        resolved = file_path.resolve()
        # Security: Prevent path traversal outside project root
        try:
            resolved.relative_to(PROJECT_ROOT)
        except ValueError:
            raise PermissionError(f"Access denied: Path {file_path} is outside project root.")

        # Security: Block sensitive files
        forbidden_patterns = [".env", "password", "secret", "credentials", ".git", "__pycache__", "venv"]
        name_lower = resolved.name.lower()
        if any(pat in name_lower for pat in forbidden_patterns):
            raise PermissionError(f"Access denied: Sensitive or forbidden file pattern in {file_path}.")
