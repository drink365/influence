# pages/0_AI_Copilot_Pro.py
# AI Copilot Pro（家族客戶視角文案＋相容你既有 UI）
from __future__ import annotations

import streamlit as st

# 若你的 Copilot UI 是獨立模組，這裡相容呼叫；沒有也不會報錯
def _try_render_existing_ui():
    try:
        # 你既有的 Copilot 介面（若存在）
        from legacy_tools.modules.ai_copilot_ui import render_copilot
        render_copilot()
        return True
    except Exception:
        return False

st.set_page_config(page_title="AI Copilot Pro｜家族傳承助手", layout="wide")

# --- 文案區（家族客戶視角） ---
st.markdown("""
<div style="background:#f5f8ff;padding:1.5rem;border-radius:12px;border:1px solid #e2e8f0;">
  <h2 style="margin:0 0 .5rem 0;color:#0f172a;">你的專屬 AI 規劃助理，讓傳承更清楚、更從容</h2>
  <p style="margin:0;color:#334155;">
    把法律、稅務與保險的複雜度變簡單。用對話，就能快速產出家族藍圖、簡報摘要與下一步建議。
  </p>
  <ul style="margin:1rem 0 0 1.25rem;color:#334155;">
    <li><b>一問即答：</b>以你的情境為核心，回覆清楚、少行話。</li>
    <li><b>專業可追溯：</b>依據台灣法規與常見實務，給予合規方向與注意事項。</li>
    <li><b>立即可用：</b>自動整理成簡報式摘要與 PDF，方便和家人或專家團隊討論。</li>
  </ul>
</div>
<p style="color:#64748b;font-size:.95rem;margin-top:.5rem;">
  貼心提醒：AI 回覆為即時建議，<b>不構成法律或稅務意見</b>；重要決策前請與我們或你的顧問確認。
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 嘗試渲染你原本的 Copilot 介面 ---
rendered = _try_render_existing_ui()
if not rendered:
    st.info("（提示）偵測不到既有的 Copilot 介面模組，先顯示文案區與導覽。若你本來就有互動介面，這段提示不會出現。")

# --- 快速導覽 ---
c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/Tools_AssetMap.py", label="🗺️ 家族資產地圖")
with c2:
    st.page_link("pages/Tools_EstateTax.py", label="🧮 家族遺產稅試算")
with c3:
    st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 家族保單策略建議")
