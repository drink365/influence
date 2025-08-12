import sys, os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from legacy_tools.modules.strategy_module import ASSET_CATEGORIES

st.set_page_config(page_title="傳承地圖｜influence9", page_icon="🗺️", layout="wide")

st.title("🗺️ 傳承地圖（簡版）")
st.caption("輸入資產分布，快速生成圓餅圖與現金流概覽。")

labels = [c["label"] for c in ASSET_CATEGORIES]
vals = []
cols = st.columns(3)
for i, lab in enumerate(labels):
    with cols[i % 3]:
        vals.append(st.number_input(lab, min_value=0, value=0, step=100, key=f"v_{i}"))

if sum(vals) == 0:
    st.info("請先輸入各資產類別的金額數值。")
else:
    fig, ax = plt.subplots()
    ax.pie(vals, labels=labels, autopct=lambda p: f"{p:.1f}%" if p > 0 else "")
    ax.axis("equal")
    st.pyplot(fig)

    df = pd.DataFrame({"資產類別": labels, "金額": vals})
    st.dataframe(df, use_container_width=True)