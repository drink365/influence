# pages/Tools.py
# 顧問工具庫（清楚導覽；名稱依你的偏好調整）
from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="顧問工具庫", layout="wide")

st.markdown("""
<h2 style="margin-bottom:.5rem;color:#0f172a;">顧問工具庫｜3 分鐘看懂、5 分鐘拿到摘要</h2>
<p style="color:#334155;margin:0 0 1rem 0;">
  遺產稅試算、資產地圖、保單策略，一次完成、一次帶走。金額單位皆為 <b>萬元（TWD）</b>。
</p>
""", unsafe_allow_html=True)

st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/Tools_AssetMap.py", label="🗺️ 家族資產地圖",
                 help="輸入資產與負債（萬元），生成家族版圖與摘要 PDF")
with c2:
    st.page_link("pages/Tools_EstateTax.py", label="🧮 遺產稅試算",
                 help="以萬元估稅、列出扣除項，協助預留稅源")
with c3:
    st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 保單策略建議",
                 help="依目標與預算產出策略，附 TXT/PDF 下載")

st.markdown("---")
st.caption("建議流程：先用『家族資產地圖』建立共識 → 再做『遺產稅試算』與『保單策略建議』。")
