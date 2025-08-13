import sys, os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from legacy_tools.modules.insurance_logic import recommend_strategies

st.set_page_config(page_title="保單策略建議｜influence9", page_icon="📦", layout="wide")

st.title("📦 保單策略建議（簡版）")
st.caption("依照目標與預算，產出初步的策略建議，作為與客戶討論的起點。")

goal = st.selectbox("主要目標", ["稅源預留", "資產放大", "醫療長照", "外幣配置", "傳承金流"])
budget = st.number_input("預算（年繳，TWD）", min_value=0, step=10000, value=300000)
horizon = st.slider("規劃年期（年）", 5, 30, 15)

if st.button("產出建議"):
    recs = recommend_strategies(goal=goal, budget=budget, years=horizon)
    for r in recs:
        st.markdown(f"### ✅ {r['name']}")
        st.write(r['why'])
        st.write(f"**適合對象**：{', '.join(r['fit'])}")
        st.markdown("---")