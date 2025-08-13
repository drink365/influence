# legacy_tools/modules/estate_tax_ui.py
"""
遺產稅試算頁面的 UI 與邏輯
- 改用相對匯入，避免 ModuleNotFoundError
- 使用共用 PDF 引擎 generate_pdf()（自動處理字型與 emoji）
"""

import streamlit as st
from .tax_calculator import TaxCalculator  # 相對匯入
from .tax_constants import TaxConstants   # 如果要顯示級距
from .pdf_generator import generate_pdf   # 共用 PDF 引擎


def _fmt_money(x: float) -> str:
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "0"


def render_estate_tax_page():
    st.set_page_config(page_title="遺產稅試算｜influence", page_icon="🧮", layout="wide")
    st.markdown("## 🧮 遺產稅試算")
    st.caption("快速估算遺產稅與扣除項，並可下載 PDF。")

    with st.form("estate_tax_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            total_assets = st.number_input("總資產（萬元）", min_value=0.0, value=5000.0, step=100.0)
        with c2:
            debts = st.number_input("債務/列舉扣除（萬元）", min_value=0.0, value=500.0, step=50.0)
        with c3:
            exemptions = st.number_input("免稅額（萬元）", min_value=0.0, value=1220.0, step=20.0)

        show_brackets = st.toggle("顯示稅率級距", value=True)
        submitted = st.form_submit_button("計算")

    if submitted:
        tax = TaxCalculator.calculate_inheritance_tax(
            total_assets * 10000,  # 轉為元計算也行；此處僅顯示用，實際倍數不影響比率
            debts * 10000,
            exemptions * 10000,
        )

        # 因為 TaxCalculator 回傳的是金額單位與輸入一致，為了展示簡潔，以下仍以「萬元」表示
        # 這裡簡化：直接以萬元計算（不轉元）
        tax_wan = TaxCalculator.calculate_inheritance_tax(total_assets, debts, exemptions)

        st.markdown("### 📊 試算結果")
        colA, colB, colC, colD = st.columns(4)
        with colA:
            st.metric("總資產（萬元）", _fmt_money(total_assets))
        with colB:
            st.metric("扣除（萬元）", _fmt_money(debts + exemptions))
        with colC:
            taxable_base = max(total_assets - debts - exemptions, 0)
            st.metric("應稅基（萬元）", _fmt_money(taxable_base))
        with colD:
            st.metric("估算稅額（萬元）", _fmt_money(tax_wan))

        if show_brackets:
            st.markdown("#### 稅率級距（參考）")
            st.table({
                "下限（萬元）": [b[0] for b in TaxConstants.INHERITANCE_TAX_BRACKETS],
                "上限（萬元）": [b[1] for b in TaxConstants.INHERITANCE_TAX_BRACKETS],
                "稅率": [f"{int(b[2]*100)}%" for b in TaxConstants.INHERITANCE_TAX_BRACKETS],
            })

        # --- PDF 下載 ---
        # 組 PDF 文字（以「萬元」單位呈現）
        lines = [
            "遺產稅試算",
            "",
            f"總資產：{_fmt_money(total_assets)} 萬元",
            f"債務/列舉扣除：{_fmt_money(debts)} 萬元",
            f"免稅額：{_fmt_money(exemptions)} 萬元",
            f"應稅基：{_fmt_money(taxable_base)} 萬元",
            f"估算稅額：{_fmt_money(tax_wan)} 萬元",
            "",
            "備註：以上為試算結果，實際以主管機關規定及申報資料為準。",
        ]
        pdf_buf = generate_pdf(content="\n".join(lines), title="遺產稅試算")

        st.download_button(
            "下載 PDF",
            data=pdf_buf.getvalue(),
            file_name="遺產稅試算.pdf",
            mime="application/pdf",
        )
