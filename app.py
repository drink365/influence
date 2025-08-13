# app.py
import streamlit as st

st.set_page_config(
    page_title="influence｜家族傳承與保單策略助手",
    page_icon="logo.png",
    layout="wide"
)

# --- 頁首（Logo + 次標） ---
st.image("logo.png", width=180)
st.markdown("### 家族傳承與保單策略助手")

st.markdown(
    """
    <div style="background-color:#f5f8ff; padding: 2rem; border-radius: 12px; border:1px solid #e2e8f0;">
        <h1 style="color:#0f172a; font-weight:700; margin-bottom:0.5rem;">專屬傳承藍圖，讓家族未來更穩健</h1>
        <p style="font-size:1.15rem; color:#334155; margin:0;">
            結合法律、稅務與保險的整合式規劃，3 分鐘產出專屬藍圖與簡報，協助您守護家族資產、延續價值與使命。
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:1rem;">
            <span style="background:#ffffff; padding:0.5rem 1rem; border-radius:999px; border:1px solid #cbd5e1;">高端客製：以人為本，量身訂製最佳解決方案</span>
            <span style="background:#ffffff; padding:0.5rem 1rem; border-radius:999px; border:1px solid #cbd5e1;">一站整合：律師、會計師、財稅專家跨域協作</span>
            <span style="background:#ffffff; padding:0.5rem 1rem; border-radius:999px; border:1px solid #cbd5e1;">AI 驅動：即時產出藍圖與簡報，讓傳承規劃更精準</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# --- 導覽按鈕（直達各工具頁） ---
st.markdown("#### 立即開始")
c1, c2, c3 = st.columns(3)

with c1:
    st.page_link(
        "pages/Tools_AssetMap.py",
        label="🗺️ 前往：家族資產地圖",
        help="輸入資產與負債，一鍵生成家族資產版圖與摘要 PDF"
    )

with c2:
    st.page_link(
        "pages/Tools_EstateTax.py",
        label="🧮 前往：家族遺產稅試算",
        help="以萬元（TWD）為單位，快速試算並產出摘要 PDF"
    )

with c3:
    st.page_link(
        "pages/Tools_InsuranceStrategy.py",
        label="📦 前往：家族保單策略建議",
        help="依目標與預算，產出實務可行的保單策略與摘要 PDF"
    )

st.markdown("---")

# --- 服務亮點（家族客戶視角） ---
st.markdown("#### 我們如何協助您的家族")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("**確定性傳承**  \n以保單與信託機制，強化現金流與資產分配的確定性。")
with col_b:
    st.markdown("**稅源預留**  \n提早預估並準備稅金，避免影響家族營運與生活品質。")
with col_c:
    st.markdown("**簡報就緒**  \n即時產出摘要與 PDF，方便與家人或專業團隊溝通。")

# --- 頁尾（品牌與聯繫） ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:0.95rem; color:#64748b;">
        © 2025 永傳家族辦公室 ｜ Email：<a href="mailto:123@gracefo.com">123@gracefo.com</a> ｜ 
        <a href="https://www.gracefo.com" target="_blank">www.gracefo.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
