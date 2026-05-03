# Experiment Protocol

## Goal
Compare BrainFry Agent with a single-call Baseline LLM on 20 consumer shopping scenarios.

## Data
- File: `evaluation/scenarios_20.csv`
- 20 cases
- Each case includes product category, user scenario, and expected consumer type.

## Systems
- Baseline LLM: returns multiple options and asks user to compare.
- BrainFry Agent: detects BrainFry, classifies consumer type, filters product DB, simplifies options, and runs critic review.

## Metrics
All metrics are 1–5: decision ease, satisfaction, confidence, cognitive load reduction, explanation quality, personalization, purchase intention.

## Reproducible Run
```bash
python run_evaluation.py
```
