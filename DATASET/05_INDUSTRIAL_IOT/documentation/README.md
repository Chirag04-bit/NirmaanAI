# 05_INDUSTRIAL_IOT Factory Sensor Simulator 2040

## Overview
Multi-machine industrial IoT telemetry dataset containing 500,000 records across vibration, temperature, acoustic, and fluid levels.

## Targets
- Binary: Failure_Within_7_Days (6.0% failure rate)
- Continuous: Remaining_Useful_Life_days

## Critical Leakage Guardrail
Exclude Remaining_Useful_Life_days when training classification models for Failure_Within_7_Days.
