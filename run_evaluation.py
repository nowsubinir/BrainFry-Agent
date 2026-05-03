
from pathlib import Path
import pandas as pd
from brainfry_agent import baseline_recommendation, agent_recommendation, detect_budget, heuristic_evaluate
ROOT=Path(__file__).parent
df=pd.read_csv(ROOT/'data/products.csv')
scenarios=pd.read_csv(ROOT/'evaluation/scenarios_20.csv')
rows=[]; outputs=[]
for _,s in scenarios.iterrows():
    sid=s['scenario_id']; cat=s['category']; inp=s['user_scenario']; budget=detect_budget(inp)
    pairs=[('Baseline LLM', baseline_recommendation(inp,df,cat,budget)),('BrainFry Agent', agent_recommendation(inp,df,cat)['text'])]
    for system,text in pairs:
        score=heuristic_evaluate(system,text)
        rows.append({'scenario_id':sid,'category':cat,'expected_type':s['expected_type'],'system':system,**score})
        outputs.append({'scenario_id':sid,'system':system,'user_input':inp,'output':text})
results=pd.DataFrame(rows); outputs_df=pd.DataFrame(outputs)
metrics=['decision_ease','satisfaction','confidence','cognitive_load_reduction','explanation_quality','personalization','purchase_intention']
summary=results.groupby('system')[metrics].mean().round(2).reset_index()
b=summary[summary['system']=='Baseline LLM'].iloc[0]; a=summary[summary['system']=='BrainFry Agent'].iloc[0]
diff={'system':'Difference (Agent - Baseline)'}
for m in metrics: diff[m]=round(a[m]-b[m],2)
summary=pd.concat([summary,pd.DataFrame([diff])],ignore_index=True)
(ROOT/'outputs').mkdir(exist_ok=True)
results.to_csv(ROOT/'outputs/evaluation_scores.csv',index=False,encoding='utf-8-sig')
outputs_df.to_csv(ROOT/'outputs/system_outputs.csv',index=False,encoding='utf-8-sig')
summary.to_csv(ROOT/'outputs/summary_metrics.csv',index=False,encoding='utf-8-sig')
print(summary.to_string(index=False))
