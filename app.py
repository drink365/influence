import os
import streamlit as st
from nav_shim import goto

st.set_page_config(page_title="influence｜數位傳承顧問", page_icon="✨", layout="wide")

# ---- 找 Logo（支援多檔名）----
def find_logo():
    candidates = [
        "logo.png", "logo.jpg", "logo.jpeg",
        "logo-橫式彩色.png",
        os.path.join("pages", "logo.png"), os.path.join("pages", "logo.jpg")
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

logo = find_logo()

# ---- 樣式 ----
st.markdown(
    """
    <style>
    .hero {
        padding: 18px 20px 8px 20px;
        border-radius: 18px;
        background: #fff;
        border: 1px solid #eee;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }
    .cards {display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 18px; margin-top: 12px;}
    .card {
        padding: 18px; border-radius: 16px;
        border: 1px solid #eee; background: #ffffff;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        transition: transform .08s ease, box-shadow .08s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,0.08);}
    .card h3 { margin: 0 0 6px 0; font-size: 1.15rem;}
    .muted { color: #666; font-size: 0.95rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Hero 區塊（Logo + 說明）----
if logo:
    st.image(logo, use_container_width=True)
else:
    st.title("✨ influence｜數位傳承顧問")

st.markdown('<div class="hero">', unsafe_allow_html=True)
st.write(
    """
**歡迎回來！** 請從下方卡片或左側選單進入功能頁：

- **顧問工具庫**：遺產稅試算、傳承地圖、保單策略  
- **AI 行銷助手 Pro**：讀取 brand.json 的金句與 Hashtag，並可匯出 PDF  
- **預約**（選用）：若未設定 Secrets，寄信功能會停用但不影響其他頁面
"""
)
st.markdown('</div>', unsafe_allow_html=True)

# ---- 快速卡片 ----
st.markdown('<div class="cards">', unsafe_allow_html=True)

# 卡 1：顧問工具庫
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🧰 顧問工具庫")
st.write("遺產稅試算｜傳承地圖｜保單策略。將專業轉化為清楚的成交素材。")
if st.button("打開工具庫"):
    goto(st, "pages/0_Tools.py")
st.markdown('</div>', unsafe_allow_html=True)

# 卡 2：AI 行銷助手 Pro
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🪄 AI 行銷助手 Pro")
st.write("讀 brand.json｜可輸出 PDF。快速產出 FB/LINE/演講開場文案。")
if st.button("進入 AI 助手"):
    goto(st, "pages/0_AI_Copilot_Pro.py")
st.markdown('</div>', unsafe_allow_html=True)

# 卡 3：預約（選用）
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📅 預約（選用）")
st.write("未設定 Secrets 時，頁面可開但寄信會停用。")
if st.button("開啟預約頁"):
    goto(st, "pages/4_Booking.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.caption("提示：PDF 會自動套用 brand.json 的品牌抬頭與 NotoSansTC 中文字型（若根目錄有 logo / qrcode 也會加入）。")
