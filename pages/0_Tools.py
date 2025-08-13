# pages/0_Tools.py
# 🧰 顧問工具庫（含 AI 助手卡片＋品牌小 Logo）
import os
import streamlit as st
from nav_shim import goto

st.set_page_config(page_title="顧問工具庫｜influence", page_icon="🧰", layout="wide")

def find_logo():
    for p in ["logo-橫式彩色.png", "logo.png", "logo.jpg", "logo.jpeg", os.path.join("pages","logo.png")]:
        if os.path.exists(p):
            return p
    return None

logo = find_logo()

st.markdown(
    """
    <style>
    .grid {display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:16px;}
    .card {padding:16px;border-radius:16px;border:1px solid #eee;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.06);}
    .card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(0,0,0,.08);}
    .card h4{margin:0 0 6px 0;}
    .topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
    .logo-small{height:32px;opacity:.9}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="topbar">', unsafe_allow_html=True)
st.markdown("<h2>🧰 顧問工具庫</h2>", unsafe_allow_html=True)
if logo:
    st.markdown(f'<img class="logo-small" src="{logo}">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.caption("把專業變成成交力：遺產稅試算、傳承地圖、保單策略、AI 行銷助手。")

st.markdown('<div class="grid">', unsafe_allow_html=True)

# 1 遺產稅
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### 🧮 遺產稅試算")
st.write("快速估算遺產稅與扣除項，支援 PDF 匯出。")
if st.button("打開｜遺產稅試算"):
    goto(st, "pages/Tools_EstateTax.py")
st.markdown('</div>', unsafe_allow_html=True)

# 2 傳承地圖
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### 🗺️ 傳承地圖（完整版）")
st.write("輸入六大資產，生成圓餅圖＋現金流表＋PDF。")
if st.button("打開｜傳承地圖"):
    goto(st, "pages/Tools_AssetMap.py")
st.markdown('</div>', unsafe_allow_html=True)

# 3 保單策略
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### 📦 保單策略建議")
st.write("依目標與預算產出策略建議，輔助提案。")
if st.button("打開｜保單策略建議"):
    goto(st, "pages/Tools_InsuranceStrategy.py")
st.markdown('</div>', unsafe_allow_html=True)

# 4 AI 助手
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### 🪄 AI 行銷助手 Pro")
st.write("讀 brand.json｜金句/Hashtag｜PDF 匯出。")
if st.button("打開｜AI 行銷助手"):
    goto(st, "pages/0_AI_Copilot_Pro.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")
st.caption("PDF 風格已統一，品牌抬頭與字型由 brand.json / NotoSansTC 控制。若根目錄有 logo / qrcode 也會自動加入 PDF。")
