# pages/0_Tools.py
# 🧰 顧問工具庫（含 AI 助手快捷卡）
import streamlit as st
from nav_shim import goto

st.set_page_config(page_title="顧問工具庫｜influence", page_icon="🧰", layout="wide")
st.title("🧰 顧問工具庫")
st.caption("把專業變成成交力：遺產稅試算、傳承地圖、保單策略、AI 行銷助手。")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("🧮 遺產稅試算")
    st.write("快速估算遺產稅與扣除項，支援 PDF 匯出。")
    if st.button("打開｜遺產稅試算"):
        goto(st, "pages/Tools_EstateTax.py")

with c2:
    st.subheader("🗺️ 傳承地圖（完整版）")
    st.write("輸入六大資產，生成圓餅圖＋現金流表＋PDF。")
    if st.button("打開｜傳承地圖"):
        goto(st, "pages/Tools_AssetMap.py")

with c3:
    st.subheader("📦 保單策略建議")
    st.write("依目標與預算產出策略建議，輔助提案。")
    if st.button("打開｜保單策略建議"):
        goto(st, "pages/Tools_InsuranceStrategy.py")

with c4:
    st.subheader("🪄 AI 行銷助手 Pro")
    st.write("讀 brand.json｜金句/Hashtag｜PDF 匯出。")
    if st.button("打開｜AI 行銷助手"):
        goto(st, "pages/0_AI_Copilot_Pro.py")

st.markdown("---")
st.caption("提示：以上工具與 PDF 風格已統一，品牌抬頭與字型由 brand.json / NotoSansTC 控制。")
