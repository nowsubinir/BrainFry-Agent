# BrainFry Agent

BrainFry Agent is an AI-assisted purchase decision support system for consumers experiencing information overload and decision fatigue in online shopping environments.

## Problem
Online consumers often compare too many reviews, advertisements, prices, and product options. Instead of making the decision easier, this can produce confusion, decision fatigue, regret avoidance, and delayed purchase. We call this state **BrainFry**.

## Agent Architecture
1. User Intent Agent
2. BrainFry Detector Agent
3. Psychology Agent
4. Product Search / Tool Use Agent
5. Decision Simplifier Agent
6. Critic Agent

This is not a single-call recommender; it is a staged agent pipeline.

## Run Live Demo
```bash
pip install -r requirements.txt
streamlit run app.py
```

Demo input:
```text
무선 이어폰 사고 싶은데 유튜브 리뷰만 2시간 넘게 봤어요. 예산은 15만 원 정도이고, 착용감이랑 통화 품질이 중요해요. 그런데 보면 볼수록 뭐가 좋은지 모르겠어요.
```

## Run Evaluation
```bash
python run_evaluation.py
```

Generated files:
- outputs/system_outputs.csv
- outputs/evaluation_scores.csv
- outputs/summary_metrics.csv

## Evaluation Benchmark
The benchmark uses 20 self-constructed shopping scenarios in `evaluation/scenarios_20.csv`. It compares a Baseline LLM with BrainFry Agent using decision ease, satisfaction, confidence, cognitive load reduction, explanation quality, personalization, and purchase intention.

## Important Note
The included evaluation is a reproducible automated pilot benchmark. For final submission, human evaluation scores can replace or supplement these automated scores using `evaluation/human_eval_rubric.csv`.

## Repository Structure
```text
BrainFry-Agent-Final/
├── app.py
├── brainfry_agent.py
├── run_evaluation.py
├── requirements.txt
├── README.md
├── data/products.csv
├── prompts/
├── evaluation/
├── outputs/
├── docs/
└── references/paper_list.md
```
