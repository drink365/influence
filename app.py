import streamlit as st

st.set_page_config(page_title="influence｜數位傳承顧問", page_icon="✨", layout="wide")

st.title("✨ influence｜數位傳承顧問")
st.write(
    """
歡迎回來！請從左側選單或下方卡片進入功能頁：

- **顧問工具庫**：遺產稅試算、傳承地圖、保單策略
- **AI 行銷助手 Pro**：快速產出 FB/LINE/演講開場（讀取 brand.json，支援 PDF）
- **預約**（選用）：若已設定 Secrets 可啟用寄信/排程
"""
)

# 快速入口
from nav_shim import goto
c1, c2, c3 = st.columns(3)
with c1:
    st.header("🧰 顧問工具庫")
    st.write("遺產稅試算｜傳承地圖｜保單策略")
    if st.button("打開"):
        goto(st, "pages/0_Tools.py")

with c2:
    st.header("🪄 AI 行銷助手 Pro")
    st.write("讀 brand.json｜PDF 匯出")
    if st.button("進入 AI 助手"):
        goto(st, "pages/0_AI_Copilot_Pro.py")

with c3:
    st.header("📅 預約（選用）")
    st.write("若未設定 Secrets，功能會停用但不影響其他頁面")
    if st.button("開啟預約頁"):
        goto(st, "pages/4_Booking.py")

st.caption("提示：PDF 會自動套用 brand.json 的品牌抬頭與 NotoSansTC 中文字型。")
