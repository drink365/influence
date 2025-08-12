# pages/Tools_EstateTax.py
# 🧮 遺產稅試算（整合新版 PDF 抬頭＋繁中字型）
import streamlit as st
import os
import matplotlib.pyplot as plt

# 字型設定（找到你已上傳的 NotoSansTC-Regular.ttf 就套用，沒有也能跑）
try:
    import matplotlib
    candidates = [
        os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
        os.path.join(os.getcwd(), "pages", "NotoSansTC-Regular.ttf"),
    ]
    for fp in candidates:
        if os.path.exists(fp):
            matplotlib.font_manager.fontManager.addfont(fp)
            plt.rcParams["font.sans-serif"] = ["Noto Sans TC"]
            plt.rcParams["axes.unicode_minus"] = False
            break
except Exception:
    pass

st.set_page_config(page_title="遺產稅試算", page_icon="🧮", layout="wide")
st.title("🧮 遺產稅試算")

# === 你的既有 UI（沿用 legacy 的頁面函式） ===
from legacy_tools.modules.estate_tax_ui import render_estate_tax_page
render_estate_tax_page()

st.markdown("---")
st.subheader("🧾 匯出 PDF（含品牌抬頭＋繁中字型）")

# 匯出：呼叫新版共用引擎（會讀取 brand.json 與字型）
from legacy_tools.modules.pdf_generator import generate_pdf

if st.button("⬇️ 匯出《探索紀錄》PDF"):
    pdf_buf = generate_pdf()
    st.download_button(
        "下載 PDF",
        data=pdf_buf.getvalue(),
        file_name="遺產稅探索紀錄.pdf",
        mime="application/pdf",
    )
