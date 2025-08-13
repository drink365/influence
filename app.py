import streamlit as st

st.set_page_config(
    page_title="influence",
    page_icon="logo.png",
    layout="wide"
)

# 頁首 Logo
st.image("logo.png", width=180)
st.markdown("### 家族傳承與保單策略助手")

st.markdown("---")

# 行銷文案區塊
st.markdown(
    """
    <div style="background-color: #f5f8ff; padding: 2rem; border-radius: 10px;">
        <h1 style="color: #0f172a; font-weight: bold;">專屬傳承藍圖，讓家族未來更穩健</h1>
        <p style="font-size: 1.2rem; color: #334155;">
            結合法律、稅務與保險的整合式規劃，3 分鐘產出專屬藍圖與簡報，協助您守護家族資產、延續價值與使命。
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem;">
            <span style="background-color: white; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid #cbd5e1;">
                高端客製：以人為本，量身訂製最佳解決方案
            </span>
            <span style="background-color: white; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid #cbd5e1;">
                一站整合：律師、會計師、財稅專家跨域協作
            </span>
            <span style="background-color: white; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid #cbd5e1;">
                AI 驅動：即時產出藍圖與簡報，讓傳承規劃更精準
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# 呼叫其他功能或導頁
st.markdown("👉 [立即產生保單策略](./Tools_InsuranceStrategy)")
st.markdown("👉 [立即試算遺產稅](./Tools_EstateTax)")

# 頁尾
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.9rem; color: #64748b;">
        © 2025 永傳家族辦公室 | Email: <a href="mailto:123@gracefo.com">123@gracefo.com</a> | 
        <a href="https://www.gracefo.com" target="_blank">www.gracefo.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
