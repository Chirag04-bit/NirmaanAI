# 01_AI4I_2020 Predictive Maintenance Dataset

## Overview
Synthetic predictive maintenance dataset reflecting real milling machine operations.
Published by Stephan Matzka (2020) in UCI Machine Learning Repository.

## Files
- 
aw/ai4i2020.csv (10,000 rows, 14 columns)

## Primary Target
- Machine failure: Binary (0 = No Failure [96.61%], 1 = Failure [3.39%])

## Root Cause Failure Modes
- TWF: Tool Wear Failure (46 instances)
- HDF: Heat Dissipation Failure (115 instances)
- PWF: Power Failure (95 instances)
- OSF: Overstrain Failure (98 instances)
- RNF: Random Failure (19 instances)

## Critical Leakage Guardrail
Do NOT include TWF, HDF, PWF, OSF, RNF as features when predicting Machine failure. Drop UDI index.
