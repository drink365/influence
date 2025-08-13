# pages/Tools.py
# 顧問工具庫（家族客戶視角文案）
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="顧問工具庫", layout="wide")

st.markdown("""
<h2 style="margin-bottom:.5rem;color:#0f172a;">顧問工具庫｜3 分鐘看懂、5 分鐘拿到摘要</h2>
<p style="color:#334155;margin:0 0 1rem 0;">
  把專業變成家人的安心：遺產稅試算、資產地圖、保單策略，一次完成、一次帶走。
</p>
<div style="display:flex;flex-wrap:wrap;gap:.75rem;">
  <span style="background:#fff;border:1px solid #cbd5e1;border-radius:999px;padding:.4rem .9rem;">
    家族資產地圖：輸入資產與負債（單位：萬元），立即看見家族版圖與重點比例
  </span>
  <span style="background:#fff;border:1px solid #cbd5e1;border-radius:999px;padding:.4rem .9rem;">
    遺產稅試算：用萬元估稅、列出扣除項、預留稅源更從容
  </span>
  <span style="background:#fff;border:1px solid #cbd5e1;border-radius:999px;padding:.4rem .9rem;">
    保單策略建議：依目標與預算產出策略，附可下載的 TXT／PDF 摘要
  </span>
</div>
<p style="margin-top:1rem;color:#0f172a;"><b>建議流程：</b>從「家族資產地圖」開始 → 釐清版圖與重點 → 進一步做稅務試算與保單策略。</p>
""", unsafe_allow_html=True)

st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/Tools_AssetMap.py", label="🗺️ 前往：家族資產地圖")
with c2:
    st.page_link("pages/Tools_EstateTax.py", label="🧮 前往：遺產稅試算")
with c3:
    st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 前往：保單策略建議")
