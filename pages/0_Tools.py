# pages/0_Tools.py
# 🧰 顧問工具庫（穩定跳頁）
import streamlit as st
from nav_shim import goto  # 根目錄 shim，內部會優先用 src.utils.nav

st.set_page_config(page_title="顧問工具庫｜influence", page_icon="🧰", layout="wide")
st.title("🧰 顧問工具庫")
st.caption("把專業變成成交力：遺產稅試算、傳承地圖、保單策略。")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🧮 遺產稅試算")
    st.write("快速估算遺產稅與扣除項，支援 PDF 匯出。")
    if st.button("打開｜遺產稅試算"):
        goto(st, "pages/Tools_EstateTax.py")
with col2:
    st.subheader("🗺️ 傳承地圖（完整版）")
    st.write("輸入六大資產，生成圓餅圖＋現金流表＋PDF。")
    if st.button("打開｜傳承地圖"):
        goto(st, "pages/Tools_AssetMap.py")
with col3:
    st.subheader("📦 保單策略建議")
    st.write("依目標與預算產出策略建議，輔助提案。")
    if st.button("打開｜保單策略建議"):
        goto(st, "pages/Tools_InsuranceStrategy.py")

st.markdown("---")
st.caption("提示：以上工具來自 legacy 專案，已整合至 influence，方便顧問端一站式使用。")
