# legacy_tools/modules/estate_tax_ui.py
# 遺產稅試算（完整版：家庭扣除 + 2025 新級距）＋ PDF 匯出
# 依賴：tax_constants.TaxConstants、pdf_generator.generate_pdf
from __future__ import annotations

import math
import pandas as pd
import streamlit as st

from .tax_constants import TaxConstants
from .pdf_generator import generate_pdf


# -----------------------
# 計算核心（依你原 repo）
# -----------------------
def compute_deductions(constants: TaxConstants,
                       spouse: bool,
                       adult_children: int,
                       other_dependents: int,
                       disabled_people: int,
                       parents: int) -> float:
    """合計所有扣除額（單位：萬元）"""
    spouse_deduction = constants.SPOUSE_DEDUCTION_VALUE if spouse else 0
    total = (
        spouse_deduction
        + constants.FUNERAL_EXPENSE
        + disabled_people * constants.DISABLED_DEDUCTION
        + adult_children * constants.ADULT_CHILD_DEDUCTION
        + other_dependents * constants.OTHER_DEPENDENTS_DEDUCTION
        + parents * constants.PARENTS_DEDUCTION
    )
    return total


def calculate_estate_tax(constants: TaxConstants,
                         total_assets: float,
                         spouse: bool,
                         adult_children: int,
                         other_dependents: int,
                         disabled_people: int,
                         parents: int) -> tuple[float, float, float]:
    """
    回傳： (課稅遺產淨額, 預估稅額, 扣除額合計) ；單位皆為「萬元」
    級距算法依你原始邏輯：TAX_BRACKETS = [(上限, 稅率), ...]
    """
    deductions = compute_deductions(constants, spouse, adult_children, other_dependents, disabled_people, parents)

    # 未達免稅額 + 扣除額
    threshold = constants.EXEMPT_AMOUNT + deductions
    if total_assets < threshold:
        return 0.0, 0.0, deductions

    taxable_amount = max(0.0, total_assets - constants.EXEMPT_AMOUNT - deductions)

    # 依級距逐段計算（previous_bracket 為前一段上限）
    tax_due = 0.0
    previous_bracket = 0.0
    for upper, rate in constants.TAX_BRACKETS:
        if taxable_amount > previous_bracket:
            amount_at_rate = min(taxable_amount, upper) - previous_bracket
            tax_due += amount_at_rate * rate
            previous_bracket = upper
        else:
            break

    return taxable_amount, round(tax_due, 0), deductions


# -----------------------
# UI
# -----------------------
def _fmt(x: float) -> str:
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "0"


def render_estate_tax_page():
    st.set_page_config(page_title="遺產稅試算（2025 版）", page_icon="🧮", layout="wide")
    st.markdown("## 🧮 遺產稅試算（2025 版）")
    st.caption("輸入家庭成員與資產，系統依 2025 級距與扣除額試算稅額，並可下載 PDF。")

    C = TaxConstants()  # 你的常數（單位：萬元）

    with st.form("estate_form"):
        c1, c2 = st.columns([1, 1])
        with c1:
            total_assets = st.number_input("總資產（萬元）", min_value=0.0, value=5000.0, step=100.0)
            spouse = st.checkbox(f"是否有配偶（扣除 {C.SPOUSE_DEDUCTION_VALUE:.0f} 萬）", value=False)

            adult_children = st.number_input(
                f"直系血親卑親屬人數（每人 {C.ADULT_CHILD_DEDUCTION:.0f} 萬）",
                min_value=0, max_value=20, value=0
            )
            parents = st.number_input(
                f"父母人數（每人 {C.PARENTS_DEDUCTION:.0f} 萬，最多 2 人）",
                min_value=0, max_value=2, value=0
            )
        with c2:
            # 身心障礙最大人數不超過家庭總人數（簡單限制）
            max_disabled = (1 if spouse else 0) + adult_children + parents
            disabled_people = st.number_input(
                f"重度以上身心障礙人數（每人 {C.DISABLED_DEDUCTION:.0f} 萬）",
                min_value=0, max_value=max_disabled, value=0
            )
            other_dependents = st.number_input(
                f"其他受撫養（兄弟姊妹、祖父母）（每人 {C.OTHER_DEPENDENTS_DEDUCTION:.0f} 萬）",
                min_value=0, max_value=10, value=0
            )

            st.write("---")
            st.write("**制度參數（參考）**")
            st.write(
                f"- 免稅額：{_fmt(C.EXEMPT_AMOUNT)} 萬｜喪葬費扣除：{_fmt(C.FUNERAL_EXPENSE)} 萬  \n"
                f"- 稅率級距：0–5,621 萬（10%）、5,621–11,242 萬（15%）、11,242 萬以上（20%）"
            )

        submitted = st.form_submit_button("計算")

    if not submitted:
        return

    taxable, tax, deductions = calculate_estate_tax(
        C, total_assets, spouse, adult_children, other_dependents, disabled_people, parents
    )

    st.markdown("### 📊 試算結果")
    a, b, c, d = st.columns(4)
    with a:
        st.metric("總資產（萬）", _fmt(total_assets))
    with b:
        st.metric("扣除合計（萬）", _fmt(deductions + C.EXEMPT_AMOUNT))  #（扣除 + 免稅額）
    with c:
        st.metric("課稅遺產淨額（萬）", _fmt(taxable))
    with d:
        st.metric("預估遺產稅（萬）", _fmt(tax))

    # 明細表
    st.markdown("#### 扣除明細（萬元）")
    rows = [
        ("免稅額", C.EXEMPT_AMOUNT),
        ("喪葬費扣除額", C.FUNERAL_EXPENSE),
        ("配偶扣除額", C.SPOUSE_DEDUCTION_VALUE if spouse else 0),
        ("直系血親卑親屬扣除額", adult_children * C.ADULT_CHILD_DEDUCTION),
        ("父母扣除額", parents * C.PARENTS_DEDUCTION),
        ("重度身心障礙扣除額", disabled_people * C.DISABLED_DEDUCTION),
        ("其他受撫養扣除額", other_dependents * C.OTHER_DEPENDENTS_DEDUCTION),
    ]
    df = pd.DataFrame(rows, columns=["項目", "金額（萬）"])
    df["金額（萬）」"] = df["金額（萬）"] if "金額（萬）" not in df else df["金額（萬）"]
    st.table(df)

    # -------- PDF 匯出（共用引擎）--------
    lines = [
        "遺產稅試算（2025 版）",
        "",
        f"總資產：{_fmt(total_assets)} 萬元",
        "",
        "扣除明細：",
        f"．免稅額：{_fmt(C.EXEMPT_AMOUNT)} 萬",
        f"．喪葬費扣除額：{_fmt(C.FUNERAL_EXPENSE)} 萬",
        f"．配偶扣除額：{_fmt(C.SPOUSE_DEDUCTION_VALUE if spouse else 0)} 萬",
        f"．直系血親卑親屬扣除額：{_fmt(adult_children * C.ADULT_CHILD_DEDUCTION)} 萬（人數 {adult_children}）",
        f"．父母扣除額：{_fmt(parents * C.PARENTS_DEDUCTION)} 萬（人數 {parents}）",
        f"．重度身心障礙扣除額：{_fmt(disabled_people * C.DISABLED_DEDUCTION)} 萬（人數 {disabled_people}）",
        f"．其他受撫養扣除額：{_fmt(other_dependents * C.OTHER_DEPENDENTS_DEDUCTION)} 萬（人數 {other_dependents}）",
        "",
        f"課稅遺產淨額：{_fmt(taxable)} 萬元",
        f"預估遺產稅：{_fmt(tax)} 萬元",
        "",
        "備註：本結果為試算，實際以主管機關規定與申報資料為準。",
    ]
    pdf_buf = generate_pdf(content="\n".join(lines), title="遺產稅試算（2025 版）")
    st.download_button(
        "下載 PDF",
        data=pdf_buf.getvalue(),
        file_name="遺產稅試算_2025.pdf",
        mime="application/pdf",
    )
