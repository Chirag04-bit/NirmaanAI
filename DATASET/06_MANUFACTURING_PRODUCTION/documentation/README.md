# 06_MANUFACTURING_PRODUCTION Hybrid Manufacturing Categorical

## Overview
Job dispatching, cycle times, and machine availability for manufacturing scheduling analysis (1,000 jobs).

## Targets
- Job_Status: Completed (673), Delayed (198), Failed (129)
- Optimization_Category

## Critical Leakage Guardrail
Exclude Actual_End at scheduling inference time.
