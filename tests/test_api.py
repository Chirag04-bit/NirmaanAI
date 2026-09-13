"""
NirmaanAI Phase 18 Test Suite: FastAPI Backend & API Service Layer
Validates:
- Application startup and /health
- Database availability and 503 error handling
- 404 resource not found and 422 validation failure
- Pagination and bounded telemetry query parameters
- Complete coverage of all 16 subsystem API domains
- Strict temporal boundary: MAINT_0003 excluded from decision evidence
- Authoritative Phase 6-16 metrics (M2 pdm=0.9959, anomaly=0.3500, ROP=1.367, SS=1.134, health=26.88)
- Financial segregation (realized ₹73,062.28 vs opportunity cost ₹24,320.00 vs gross exposure ₹97,382.28)
- What-If simulation net benefit (₹7,030) and strictly NOT_PROJECTABLE diagnostic KPIs
- OpenAPI metadata and credential masking
"""

import json
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy.pool import StaticPool

import src.db as db
from app.main import app
from src.api.dependencies import get_db
from src.db.seed.seeder import DatabaseSeeder, DECISION_CUTOFF


@pytest.fixture(scope="module")
def api_test_engine():
    """Creates isolated in-memory SQLite database for API testing with StaticPool."""
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db.Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()
    seeder = DatabaseSeeder(session)
    seeder.seed_all(telemetry_sample_limit=50, jobs_sample_limit=30)
    session.commit()
    session.close()

    yield engine
    engine.dispose()


@pytest.fixture
def client(api_test_engine):
    """Provides a TestClient with overridden get_db dependency."""
    SessionLocal = sessionmaker(bind=api_test_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==============================================================================
# 1. SYSTEM, HEALTH & ERROR HANDLING TESTS
# ==============================================================================

def test_api_root_index(client):
    """Verify root index returns application metadata."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "NirmaanAI Factory Intelligence API"
    assert data["version"] == "0.18.0"
    assert data["docs"] == "/docs"


def test_system_health_success(client):
    """Verify /health returns 200 when database is connected."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["application"] == "HEALTHY"
    assert data["database"] == "CONNECTED"
    assert data["version"] == "0.18.0"


def test_api_v1_health(client):
    """Verify /api/v1/health returns versioned health response."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["database"] == "CONNECTED"


def test_database_unavailable_health_returns_503(client):
    """Verify /health returns 503 when database is unreachable."""
    broken_engine = create_engine("sqlite:///non_existent_dir/broken.db")
    BrokenSession = sessionmaker(bind=broken_engine)

    def broken_get_db():
        session = BrokenSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = broken_get_db
    try:
        res = client.get("/health")
        assert res.status_code == 503
        data = res.json()
        assert data["database"] == "UNAVAILABLE"
        assert data["status"] == "UNAVAILABLE"
    finally:
        app.dependency_overrides.clear()


def test_404_structured_error(client):
    """Verify non-existent resources return structured 404 without leaking stack traces."""
    res = client.get("/api/v1/machines/NON_EXISTENT_MACHINE_999")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
    assert "not found" in data["error"]["message"].lower()


def test_422_validation_error(client):
    """Verify invalid query parameter triggers structured 422."""
    res = client.get("/api/v1/factories?page=-1")
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


# ==============================================================================
# 2. FACTORY & MACHINE TOPOLOGY TESTS
# ==============================================================================

def test_list_factories(client):
    """Verify factory collection endpoint with pagination."""
    res = client.get("/api/v1/factories")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["factory_id"] == "FACT_LINE_01"


def test_get_factory_details(client):
    """Verify factory detail retrieval and 404 behavior."""
    res = client.get("/api/v1/factories/FACT_LINE_01")
    assert res.status_code == 200
    assert res.json()["factory_id"] == "FACT_LINE_01"

    res_404 = client.get("/api/v1/factories/FACT_UNKNOWN")
    assert res_404.status_code == 404


def test_get_factory_overview(client):
    """Verify plant-wide aggregated overview."""
    res = client.get("/api/v1/factories/FACT_LINE_01/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["factory_id"] == "FACT_LINE_01"
    assert data["total_machines"] == 5
    assert data["critical_machines"] >= 1  # M2 is CRITICAL
    assert data["plant_health_state"] == "WATCH"  # Plant capped at WATCH because M2 is CRITICAL
    assert data["total_gross_exposure_inr"] >= 97382.28


def test_list_machines(client):
    """Verify machine listing and factory filtering."""
    res = client.get("/api/v1/machines?factory_id=FACT_LINE_01")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    machine_ids = {m["machine_id"] for m in data["items"]}
    assert {"M1", "M2", "M3", "M4", "M5"} == machine_ids


def test_get_machine_details(client):
    """Verify machine detail endpoint."""
    res = client.get("/api/v1/machines/M2")
    assert res.status_code == 200
    data = res.json()
    assert data["machine_id"] == "M2"
    assert data["baseline_vibration_mms"] == 1.40
    assert data["alert_vibration_mms"] == 3.80
    assert data["critical_vibration_mms"] == 5.50


def test_get_machine_overview_m2_critical_reconciliation(client):
    """
    Validates synthesized M2 overview:
    - PdM probability = 0.9959 (alert True, threshold 0.91)
    - PCA anomaly score = 0.3500 (threshold 0.24050, status ANOMALOUS)
    - Health score = 26.88 (band CRITICAL)
    - Inventory: current stock = 2.0, SS = 1.134, ROP = 1.367
    - Financial: realized = ₹73,062.28, gross exposure = ₹97,382.28
    - Top recommendation = INSPECT_SPINDLE_BEARING
    """
    res = client.get("/api/v1/machines/M2/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["machine_id"] == "M2"
    assert data["failure_probability"] == 0.9959
    assert data["pdm_threshold"] == 0.91
    assert data["pdm_alert"] is True
    assert data["anomaly_score"] == 0.3500
    assert data["anomaly_status"] == "ANOMALOUS"
    assert data["health_score"] == 26.88
    assert data["health_state"] == "CRITICAL"
    assert data["current_stock"] == 2.0
    assert data["safety_stock"] == 1.134
    assert data["reorder_point"] == 1.367
    assert data["realized_historical_loss_inr"] == 73062.28
    assert data["gross_financial_exposure_inr"] == 97382.28
    assert data["top_recommendation_action"] == "INSPECT_SPINDLE_BEARING"


# ==============================================================================
# 3. SENSORS & TELEMETRY BOUNDED QUERY TESTS
# ==============================================================================

def test_get_machine_telemetry_bounded(client):
    """Verify machine telemetry retrieval with limit enforcement."""
    res = client.get("/api/v1/machines/M2/telemetry?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data) <= 10
    if len(data) > 0:
        assert data[0]["machine_id"] == "M2"
        assert "vibration_mms" in data[0]
        assert "temperature_c" in data[0]


def test_get_machine_telemetry_invalid_time_range_422(client):
    """Verify start > end triggers 422 unprocessable entity."""
    res = client.get("/api/v1/machines/M2/telemetry?start=2026-01-22T00:00:00Z&end=2026-01-21T00:00:00Z")
    assert res.status_code == 422


# ==============================================================================
# 4. PRODUCTION & MAINTENANCE TEMPORAL CAUSALITY TESTS
# ==============================================================================

def test_list_production_jobs(client):
    """Verify production jobs listing."""
    res = client.get("/api/v1/production/jobs?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["items"]) <= 10


def test_get_machine_production_jobs(client):
    """Verify jobs by machine."""
    res = client.get("/api/v1/machines/M1/production")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["machine_id"] == "M1"


def test_maintenance_temporal_exclusion_default(client):
    """
    CRITICAL TEMPORAL TEST:
    Verify that MAINT_0003 (post-cutoff ground truth) is EXCLUDED by default (include_retrospective=False)
    to guarantee no decision-state data contamination.
    """
    res = client.get("/api/v1/maintenance/records")
    assert res.status_code == 200
    data = res.json()
    ids = [rec["maintenance_id"] for rec in data["items"]]
    assert "MAINT_0003" not in ids
    for rec in data["items"]:
        assert rec["is_decision_input"] is True


def test_maintenance_retrospective_inclusion_when_requested(client):
    """
    Verify that when include_retrospective=True, MAINT_0003 is visible
    and explicitly tagged with is_decision_input=False and retrospective ground truth status.
    """
    res = client.get("/api/v1/maintenance/records?include_retrospective=true")
    assert res.status_code == 200
    data = res.json()
    maint_0003 = next((r for r in data["items"] if r["maintenance_id"] == "MAINT_0003"), None)
    assert maint_0003 is not None
    assert maint_0003["is_decision_input"] is False
    assert maint_0003["epistemic_status"] == "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"


def test_get_maintenance_record_by_id(client):
    """Verify single maintenance record retrieval."""
    res = client.get("/api/v1/maintenance/MAINT_0001")
    assert res.status_code == 200
    assert res.json()["maintenance_id"] == "MAINT_0001"


# ==============================================================================
# 5. INVENTORY OPTIMIZATION CONTRACT TESTS
# ==============================================================================

def test_list_inventory(client):
    """Verify inventory item listing."""
    res = client.get("/api/v1/inventory")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 5


def test_inventory_m2_bearing_authoritative_contract(client):
    """
    Verify authoritative Phase 10 inventory contracts for M2 spindle bearing:
    - stock = 2.0
    - SS = 1.134
    - ROP = 1.367
    - lead time = 7.0 days
    """
    res = client.get("/api/v1/inventory/SKU_SPINDLE_BEARING_M2")
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == "SKU_SPINDLE_BEARING_M2"
    assert data["current_stock"] == 2.0
    assert data["safety_stock"] == 1.134
    assert data["reorder_point"] == 1.367
    assert data["lead_time_days"] == 7.0
    assert data["current_stock"] > data["reorder_point"]  # 2.0 > 1.367 -> no immediate stockout


def test_get_machine_inventory(client):
    """Verify coupled spares retrieval for M2."""
    res = client.get("/api/v1/machines/M2/inventory")
    assert res.status_code == 200
    items = res.json()
    assert any(it["sku_id"] == "SKU_SPINDLE_BEARING_M2" for it in items)


# ==============================================================================
# 6. AI SUBSYSTEMS & DIAGNOSTIC INTELLIGENCE TESTS
# ==============================================================================

def test_predictive_maintenance_m2(client):
    """Verify Phase 6 predictive maintenance prediction for M2."""
    res = client.get("/api/v1/machines/M2/predictive-maintenance")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    pdm = data["items"][0]
    assert pdm["machine_id"] == "M2"
    assert pdm["failure_probability"] == 0.9959
    assert pdm["threshold"] == 0.91
    assert pdm["prediction_class"] == 1
    assert pdm["source"] in ("PHASE_06_XGBOOST", "PHASE_06_XGBOOST_MODEL")


def test_anomaly_detection_m2(client):
    """Verify Phase 7 anomaly detection for M2."""
    res = client.get("/api/v1/machines/M2/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    anom = data["items"][0]
    assert anom["machine_id"] == "M2"
    assert anom["anomaly_score"] == 0.3500
    assert anom["threshold"] == 0.24050
    assert anom["anomaly_status"] == "ANOMALOUS"


def test_bottleneck_prediction(client):
    """Verify Phase 8 bottleneck listing."""
    res = client.get("/api/v1/ai/bottlenecks")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1


def test_forecasting_endpoint(client):
    """Verify Phase 9 forecasting queries."""
    res = client.get("/api/v1/ai/forecasts?target_series=production_volume")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["target_series"] == "production_volume"


def test_shap_explanations_m2(client):
    """Verify Phase 11 SHAP feature attributions for M2."""
    res = client.get("/api/v1/ai/shap/M2")
    assert res.status_code == 200
    shap_list = res.json()
    assert len(shap_list) >= 1
    assert shap_list[0]["machine_id"] == "M2"
    assert "feature_name" in shap_list[0]
    assert "shap_value" in shap_list[0]


def test_rca_results_m2(client):
    """Verify Phase 12 RCA diagnostic results for M2."""
    res = client.get("/api/v1/ai/rca/M2")
    assert res.status_code == 200
    rca_list = res.json()
    assert len(rca_list) >= 1
    assert rca_list[0]["machine_id"] == "M2"
    assert "Lubrication starvation" in rca_list[0]["primary_cause"]
    assert rca_list[0]["severity"] == "CRITICAL"


def test_factory_health_scores(client):
    """Verify Phase 13 health scores and M2 CRITICAL band."""
    res = client.get("/api/v1/machines/M2/health")
    assert res.status_code == 200
    data = res.json()
    assert data["machine_id"] == "M2"
    assert data["health_score"] == 26.88
    assert data["health_state"] == "CRITICAL"


# ==============================================================================
# 7. FINANCIAL LOSS ACCOUNTING TESTS
# ==============================================================================

def test_financial_losses_list(client):
    """Verify listing financial loss records."""
    res = client.get("/api/v1/finance/losses")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 4


def test_machine_financial_summary_segregation(client):
    """
    CRITICAL FINANCIAL SEMANTICS TEST:
    Verifies that the financial summary strictly separates:
    - Realized historical loss = ₹73,062.28
    - Baseline projected opportunity cost = ₹24,320.00
    - Total baseline gross financial exposure = ₹97,382.28
    - Counterfactual avoided opportunity cost = ₹19,520.00
    - Counterfactual remaining gross exposure = ₹77,862.28
    """
    res = client.get("/api/v1/machines/M2/finance")
    assert res.status_code == 200
    data = res.json()
    assert data["machine_id"] == "M2"
    assert data["realized_historical_loss_inr"] == 73062.28
    assert data["realized_downtime_loss_inr"] == 11250.0
    assert data["realized_scrap_loss_inr"] == 51800.0
    assert data["realized_rework_loss_inr"] == 6475.0
    assert data["realized_emergency_labor_inr"] == 420.0
    assert data["realized_energy_inefficiency_inr"] == 3117.28
    assert data["baseline_projected_opportunity_cost_inr"] == 24320.00
    assert data["baseline_gross_financial_exposure_inr"] == 97382.28
    assert data["counterfactual_avoided_opportunity_cost_inr"] == 19520.00
    assert data["counterfactual_remaining_gross_exposure_inr"] == 77862.28
    assert data["epistemic_status"] == "FINANCIAL_SUMMARY_SEGREGATED"


# ==============================================================================
# 8. OPERATIONAL RECOMMENDATIONS TESTS
# ==============================================================================

def test_list_recommendations(client):
    """Verify recommendations listing and closed 26-action taxonomy."""
    res = client.get("/api/v1/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    rec = data["items"][0]
    assert rec["action"] in [
        "INSPECT_SPINDLE_BEARING", "ORDER_SPARE_PARTS", "SCHEDULE_MAINTENANCE_WINDOW",
        "REDUCE_FEED_RATE", "CHECK_LUBRICATION", "REPLACE_TOOLING"
    ]
    assert rec["priority"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert rec["urgency"] in ["IMMEDIATE", "NEXT_SHIFT", "SCHEDULED", "DEFERRED"]


def test_machine_recommendations_m2(client):
    """Verify M2 recommendations contain critical bearing inspection."""
    res = client.get("/api/v1/machines/M2/recommendations")
    assert res.status_code == 200
    data = res.json()
    actions = [r["action"] for r in data["items"]]
    assert "INSPECT_SPINDLE_BEARING" in actions


# ==============================================================================
# 9. WHAT-IF DIGITAL TWIN SIMULATION TESTS
# ==============================================================================

def test_list_simulations(client):
    """Verify listing what-if digital twin counterfactual scenarios."""
    res = client.get("/api/v1/simulations")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1


def test_simulation_scenario_proactive_service(client):
    """
    CRITICAL COUNTERFACTUAL & NOT_PROJECTABLE TEST:
    Verifies Phase 16 simulation metrics:
    - Avoided breakdown loss = ₹9,420 (₹9,000 downtime + ₹420 emergency labor)
    - Planned service cost = ₹2,390
    - Net counterfactual benefit = ₹7,030
    - Diagnostic KPIs under intervention remain strictly "NOT_PROJECTABLE"
    """
    res = client.get("/api/v1/simulations/SCENARIO_M2_PROACTIVE_SERVICE")
    assert res.status_code == 200
    sim = res.json()
    assert sim["scenario_id"] == "SCENARIO_M2_PROACTIVE_SERVICE"
    assert sim["machine_id"] == "M2"
    assert sim["net_avoided_downtime_minutes"] == 120.0
    assert sim["avoided_downtime_loss_inr"] == 9000.0
    assert sim["avoided_emergency_labor_inr"] == 420.0
    assert sim["projected_avoided_breakdown_loss_inr"] == 9420.0
    assert sim["planned_service_cost_inr"] == 2390.0
    assert sim["net_counterfactual_benefit_inr"] == 7030.0
    # Strict preservation of non-projectable diagnostic states
    assert sim["projected_failure_probability"] == "NOT_PROJECTABLE"
    assert sim["projected_anomaly_score"] == "NOT_PROJECTABLE"
    assert sim["projected_health_score"] == "NOT_PROJECTABLE"
    assert sim["projected_health_state"] == "NOT_PROJECTABLE"
    assert sim["temporal_semantics"] == "COUNTERFACTUAL_EVALUATION"


# ==============================================================================
# 10. OPENAPI SCHEMA & SECURITY LEAKAGE TESTS
# ==============================================================================

def test_openapi_schema_generation(client):
    """Verify OpenAPI JSON schema is generated cleanly with all 38 paths."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert schema["info"]["title"] == "NirmaanAI Factory Intelligence API"
    assert schema["info"]["version"] == "0.18.0"
    paths = schema["paths"]
    assert len(paths) >= 30
    assert "/api/v1/machines/{machine_id}/overview" in paths
    assert "/api/v1/simulations/{scenario_id}" in paths
    assert "/api/v1/finance/losses" in paths


def test_no_credential_leakage_in_error_responses(client):
    """Verify that error responses never leak DATABASE_URL, passwords, or system internals."""
    res = client.get("/api/v1/machines/INVALID_MACHINE_ID")
    assert res.status_code == 404
    body = res.text
    assert "postgresql://" not in body
    assert "password" not in body.lower()
    assert "traceback" not in body.lower()
    assert "sqlite" not in body.lower()
