
import pandas as pd
import streamlit as st
from brainfry_agent import detect_budget, detect_priorities, brainfry_detector, classify_consumer_type, score_products, agent_recommendation

st.set_page_config(page_title='BrainFry Agent Demo', page_icon='🧠', layout='wide')
st.title('🧠 BrainFry Agent Demo')
st.caption('정보과부하 소비자를 위한 AI 구매 의사결정 에이전트 MVP')
df = pd.read_csv('data/products.csv')
default_text='무선 이어폰 사고 싶은데 유튜브 리뷰만 2시간 넘게 봤어요. 예산은 15만 원 정도이고, 착용감이랑 통화 품질이 중요해요. 그런데 보면 볼수록 뭐가 좋은지 모르겠어요.'
with st.sidebar:
    st.header('Demo Settings')
    cats=sorted(df['category'].unique())
    category=st.selectbox('Product category', cats, index=cats.index('wireless earbuds'))
user_input=st.text_area('User Input', value=default_text, height=130)
if st.button('Run BrainFry Agent', type='primary'):
    budget=detect_budget(user_input); priorities=detect_priorities(user_input); brainfry=brainfry_detector(user_input); ctype,strategy=classify_consumer_type(user_input,brainfry); ranked=score_products(df,category,budget,priorities)
    col1,col2=st.columns(2)
    with col1:
        st.subheader('1. Agent Diagnostics')
        st.write(f'**BrainFry Level:** {brainfry.level}')
        st.write(f"**Detected Signals:** {', '.join(brainfry.signals) if brainfry.signals else 'None'}")
        st.write(f'**Consumer Type:** {ctype}')
        st.write(f'**Support Strategy:** {strategy}')
    with col2:
        st.subheader('2. Product Search / Tool Use')
        st.dataframe(ranked[['name','price','comfort','call_quality','battery','noise_canceling','score']].head(5), use_container_width=True)
    st.subheader('3. Final Recommendation')
    st.text(agent_recommendation(user_input, df, category)['text'])
else:
    st.info('발표 중에는 기본 입력문을 보여준 뒤, 버튼을 눌러 Agent가 어떻게 판단하는지 설명하세요.')
