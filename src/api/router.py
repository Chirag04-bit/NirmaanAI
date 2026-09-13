"""
NirmaanAI Main API Router
Mounts all 16 subsystem routers under /api/v1.
"""

from fastapi import APIRouter

from src.api.routes.health import router as health_router
from src.api.routes.factories import router as factories_router
from src.api.routes.machines import router as machines_router
from src.api.routes.sensors import router as sensors_router
from src.api.routes.production import router as production_router
from src.api.routes.maintenance import router as maintenance_router
from src.api.routes.inventory import router as inventory_router
from src.api.routes.predictive_maintenance import router as pdm_router
from src.api.routes.anomalies import router as anomalies_router
from src.api.routes.bottlenecks import router as bottlenecks_router
from src.api.routes.forecasting import router as forecasting_router
from src.api.routes.shap import router as shap_router
from src.api.routes.rca import router as rca_router
from src.api.routes.health_scores import router as health_scores_router
from src.api.routes.finance import router as finance_router
from src.api.routes.recommendations import router as recommendations_router
from src.api.routes.simulations import router as simulations_router
from src.copilot.router import router as copilot_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount routes under /api/v1
api_v1_router.include_router(factories_router)
api_v1_router.include_router(machines_router)
api_v1_router.include_router(sensors_router)
api_v1_router.include_router(production_router)
api_v1_router.include_router(maintenance_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(pdm_router)
api_v1_router.include_router(anomalies_router)
api_v1_router.include_router(bottlenecks_router)
api_v1_router.include_router(forecasting_router)
api_v1_router.include_router(shap_router)
api_v1_router.include_router(rca_router)
api_v1_router.include_router(health_scores_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(simulations_router)
api_v1_router.include_router(copilot_router)
