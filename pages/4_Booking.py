# pages/Booking.py
# 預約諮詢頁（家族客戶視角文案）
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="預約諮詢", layout="wide")

st.markdown("""
<div style="background:#f8fafc;padding:1.25rem 1.5rem;border-radius:12px;border:1px solid #e2e8f0;">
  <h2 style="margin:0 0 .5rem 0;color:#0f172a;">預約 30 分鐘初談｜讓我們先了解你的目標</h2>
  <p style="margin:0;color:#334155;">
    線上／現場皆可。會前我們會先準備你的資產地圖或試算摘要，讓討論更有效率。
  </p>
  <ol style="margin:.9rem 0 0 1.25rem;color:#334155;">
    <li>填寫基本資料與需求（傳承、退休、稅源、企業主等）。</li>
    <li>上傳（選填）相關資料或先用我們的工具產出 PDF。</li>
    <li>工作日 24 小時內回覆，安排合適時段與方式。</li>
  </ol>
  <p style="margin:.9rem 0 0 0;color:#0f172a;"><b>你會獲得：</b>會議重點摘要（PDF）、可行策略方向、下一步清單。</p>
</div>
<p style="color:#64748b;font-size:.95rem;margin-top:.5rem;">
  我們重視你的隱私，所有資料將以最高標準保密；若涉及法律或稅務意見，將由合作專家提供正式意見。
</p>
""", unsafe_allow_html=True)

st.markdown("---")

with st.form("booking_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名")
        email = st.text_input("Email")
        topic = st.selectbox("主要需求", ["傳承", "退休", "稅源", "醫療/長照", "教育", "資產配置", "企業主", "其他"], index=0)
    with col2:
        mode = st.selectbox("會談方式", ["線上", "現場"], index=0)
        preferred_time = st.text_input("偏好時段（例如：週三下午、週五上午）")
        note = st.text_area("想先告訴我們的重點（選填）", height=100)

    submitted = st.form_submit_button("送出預約")
    if submitted:
        if not name or not email:
            st.error("請填寫姓名與 Email，方便我們回覆您。")
        else:
            st.success("已收到您的預約！我們會在工作日 24 小時內回覆您，謝謝。")

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:0.95rem; color:#64748b;">
        © 永傳家族辦公室 ｜ Email：<a href="mailto:123@gracefo.com">123@gracefo.com</a> ｜ 
        <a href="https://www.gracefo.com" target="_blank">www.gracefo.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
