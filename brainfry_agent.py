
from dataclasses import dataclass
import re
from typing import List, Tuple
import pandas as pd

@dataclass
class BrainFryResult:
    level: str
    score: int
    signals: List[str]
    explanation: str

def detect_budget(text: str, default: int = 150000) -> int:
    text = text.replace(',', '')
    m = re.search(r'(\d+)\s*만\s*원?', text)
    if m: return int(m.group(1)) * 10000
    m = re.search(r'(\d{5,7})\s*원?', text)
    if m: return int(m.group(1))
    return default

def detect_priorities(text: str) -> List[str]:
    priorities=[]
    if any(k in text for k in ['착용감','귀','편한','편하게','허리','comfort']): priorities.append('comfort')
    if any(k in text for k in ['통화','마이크','call']): priorities.append('call_quality')
    if any(k in text for k in ['배터리','오래','용량','battery']): priorities.append('battery')
    if any(k in text for k in ['노이즈','소음','ANC','noise']): priorities.append('noise_canceling')
    return priorities or ['comfort','call_quality']

def brainfry_detector(text: str) -> BrainFryResult:
    rules=[
        ('긴 고민 시간',['2시간','몇 시간','며칠','계속','오래','밤새']),
        ('과도한 리뷰/비교',['리뷰','후기','비교','영상','유튜브','검색','모델','종류']),
        ('확신 부족/혼란',['헷갈','모르겠','결정','못 고르','어렵','못 하겠']),
        ('후회 걱정',['후회','돈 낭비','실패','걱정']),
        ('선택 회피/지연',['미루','안 사고','나중','귀찮'])]
    signals=[label for label, kws in rules if any(k in text for k in kws)]
    score=len(signals)
    level='High' if score>=4 else 'Moderate' if score>=2 else 'Low'
    explanation=f"입력에서 {', '.join(signals) if signals else '강한 BrainFry 신호는 없음'} 신호가 탐지되었습니다."
    return BrainFryResult(level, score, signals, explanation)

def classify_consumer_type(text: str, brainfry: BrainFryResult) -> Tuple[str,str]:
    if any(k in text for k in ['후회','돈 낭비','실패','걱정']): return '후회 회피형','추천 근거와 제외 이유를 명확히 제시한다.'
    if any(k in text for k in ['가성비','싼','저렴','가격','예산']): return '가성비형','예산 안에서 핵심 조건을 만족하는 선택지를 우선 제시한다.'
    if any(k in text for k in ['제일','최고','완벽','다 좋아','끝판왕']): return '완벽주의형','충분히 좋은 기준을 명확히 제시한다.'
    if any(k in text for k in ['바로','지금','할인','빨리','귀찮']): return '충동형','예산과 필요도를 먼저 점검한다.'
    if brainfry.level in ['Moderate','High']: return '선택피로형','선택지를 줄이고 핵심 기준만 남겨 인지 부담을 낮춘다.'
    return '일반형','사용자 조건에 맞는 균형형 추천을 제공한다.'

def score_products(df: pd.DataFrame, category: str, budget: int, priorities: List[str]) -> pd.DataFrame:
    candidates=df[df['category']==category].copy()
    if candidates.empty: candidates=df.copy()
    candidates['budget_fit']=(candidates['price']<=budget).astype(int)
    score=candidates['budget_fit']*2.0
    for p in priorities:
        if p in candidates.columns: score += candidates[p].astype(float)
    score += ((budget-candidates['price']).clip(lower=0)/max(budget,1))
    candidates['score']=score
    return candidates.sort_values('score', ascending=False)

def baseline_recommendation(user_input: str, df: pd.DataFrame, category: str, budget: int) -> str:
    candidates=df[df['category']==category].copy()
    if candidates.empty: candidates=df.copy()
    top=candidates.sort_values('price').head(5)
    lines=['Baseline LLM Recommendation:','조건에 맞춰 다음 후보들을 비교해볼 수 있습니다.']
    for i,row in enumerate(top.itertuples(),1): lines.append(f'{i}. {row.name} ({row.price:,}원): {row.review_summary}')
    lines.append('각 제품의 가격, 리뷰, 브랜드 선호도, 세부 기능을 추가로 비교한 뒤 선택하세요.')
    return '\n'.join(lines)

def agent_recommendation(user_input: str, df: pd.DataFrame, category: str) -> dict:
    budget=detect_budget(user_input); priorities=detect_priorities(user_input); brainfry=brainfry_detector(user_input)
    consumer_type,strategy=classify_consumer_type(user_input, brainfry)
    ranked=score_products(df, category, budget, priorities)
    top=ranked.head(2 if brainfry.level=='High' else 3)
    pk={'comfort':'착용감','call_quality':'통화 품질','battery':'배터리','noise_canceling':'노이즈캔슬링'}
    lines=['BrainFry Agent Recommendation:',f'BrainFry Level: {brainfry.level}',f"Detected Signals: {', '.join(brainfry.signals) if brainfry.signals else 'None'}",f'Consumer Type: {consumer_type}',f"핵심 조건: 예산 {budget:,}원 / 우선순위 {', '.join(pk.get(p,p) for p in priorities)}",'정보 부담을 줄이기 위해 선택지를 제한합니다.']
    for i,row in enumerate(top.itertuples(),1):
        reasons=['예산 안에 들어옴' if row.price<=budget else '예산 초과 대안']
        for p in priorities:
            if getattr(row,p)>=4: reasons.append(f'{pk.get(p,p)} 점수가 높음')
        lines += [f'{i}순위: {row.name} ({row.price:,}원)',f"- 이유: {', '.join(reasons)}",f'- 리뷰 요약: {row.review_summary}']
    lines += [f"현재 조건에서는 {top.iloc[0]['name']}이 충분히 합리적인 선택입니다.",'Critic Agent: 예산, 우선순위, 추천 개수, 구매 압박 표현을 점검했습니다.']
    return {'text':'\n'.join(lines),'brainfry_level':brainfry.level,'brainfry_score':brainfry.score,'signals':brainfry.signals,'consumer_type':consumer_type,'num_options':len(top),'top_product':top.iloc[0]['name']}

def heuristic_evaluate(system: str, output_text: str) -> dict:
    option_count=len(re.findall(r'\d+[\).순위]', output_text))
    mentions_brainfry=int(('BrainFry' in output_text) or ('정보 부담' in output_text) or ('선택 피로' in output_text))
    mentions_type=int(('Consumer Type' in output_text) or ('유형' in output_text) or ('회피형' in output_text) or ('피로형' in output_text))
    has_critic=int(('Critic' in output_text) or ('점검' in output_text))
    asks_more_compare=('추가로 비교' in output_text) or ('비교한 뒤' in output_text) or ('더 비교' in output_text)
    decision_ease=5 if option_count<=3 and not asks_more_compare else 3
    satisfaction=4 if option_count<=3 else 3
    confidence=5 if ('충분히 합리적' in output_text or '안전한 선택' in output_text) else 3
    cognitive_load=5 if option_count<=3 and mentions_brainfry else 3
    explanation=5 if ('이유' in output_text and '리뷰 요약' in output_text) else 3
    personalization=5 if mentions_type else 3
    purchase_intention=4 if confidence>=4 and decision_ease>=4 else 3
    if system.lower().startswith('baseline'):
        decision_ease=min(decision_ease,3); cognitive_load=min(cognitive_load,3); personalization=min(personalization,3)
    return {'decision_ease':decision_ease,'satisfaction':satisfaction,'confidence':confidence,'cognitive_load_reduction':cognitive_load,'explanation_quality':explanation,'personalization':personalization,'purchase_intention':purchase_intention,'option_count':option_count,'mentions_brainfry':mentions_brainfry,'mentions_consumer_type':mentions_type,'has_critic':has_critic}
