# 03_UCI_SECOM Semiconductor Manufacturing Process

## Overview
Complex semiconductor wafer fabrication yield monitoring dataset containing 590 sensor signals across 1,567 manufacturing runs.

## Target
- Pass/Fail: -1 (Pass: 1,463 [93.36%]), 1 (Fail: 104 [6.64%])

## Preprocessing Requirements
- Handle 41,951 missing values across 538 feature columns.
- Imputation and low-variance feature filtering must be fitted exclusively on training folds.
