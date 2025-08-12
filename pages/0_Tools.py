import streamlit as st
from src.utils.nav import goto

st.set_page_config(page_title="顧問工具庫｜influence9", page_icon="🧰", layout="wide")
st.title("🧰 顧問工具庫")
st.caption("把專業變成成交力：遺產稅試算、傳承地圖、保單策略。")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🧮 遺產稅試算")
    st.write("快速估算遺產稅與扣除項，支援 PDF 匯出。")
    if st.button("打開｜遺產稅試算"):
        goto(st, "pages/Tools_EstateTax.py")
with col2:
    st.subheader("🗺️ 傳承地圖")
    st.write("用圖像化方式盤點資產，建立家族現金流視圖。")
    if st.button("打開｜傳承地圖"):
        goto(st, "pages/Tools_AssetMap.py")
with col3:
    st.subheader("📦 保單策略建議")
    st.write("依需求與預算產出保單配置建議，輔助提案。")
    if st.button("打開｜保單策略建議"):
        goto(st, "pages/Tools_InsuranceStrategy.py")

st.markdown("---")
st.caption("提示：以上工具來自 legacy 專案，已整合至 influence9，方便顧問端一站式使用。")