# pages/Tools_EstateTax.py
# 家族遺產稅試算（英文檔名＋中文頁面；單位：萬元 TWD）
from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Tuple, List
from dataclasses import dataclass, field

from legacy_tools.modules.pdf_generator import generate_pdf

# ===============================
# 常數（單位：萬元）
# ===============================
@dataclass
class TaxConstants:
    EXEMPT_AMOUNT: float = 1333   # 免稅額
    FUNERAL_EXPENSE: float = 138  # 喪葬費
    SPOUSE_DEDUCTION_VALUE: float = 553
    ADULT_CHILD_DEDUCTION: float = 56
    PARENTS_DEDUCTION: float = 138
    DISABLED_DEDUCTION: float = 693
    OTHER_DEPENDENTS_DEDUCTION: float = 56
    TAX_BRACKETS: List[tuple] = field(default_factory=lambda: [
        (5621, 0.10), (11242, 0.15), (float('inf'), 0.20)
    ])

# ===============================
# 計算邏輯（單位：萬元）
# ===============================
class EstateTaxCalculator:
    def __init__(self, constants: TaxConstants):
        self.constants = constants

    def compute_deductions(
        self, spouse: bool, adult_children: int, other_dependents: int,
        disabled_people: int, parents: int
    ) -> float:
        spouse_deduction = self.constants.SPOUSE_DEDUCTION_VALUE if spouse else 0
        return (
            spouse_deduction +
            self.constants.FUNERAL_EXPENSE +
            disabled_people * self.constants.DISABLED_DEDUCTION +
            adult_children * self.constants.ADULT_CHILD_DEDUCTION +
            other_dependents * self.constants.OTHER_DEPENDENTS_DEDUCTION +
            parents * self.constants.PARENTS_DEDUCTION
        )

    @st.cache_data
    def calculate_estate_tax(
        _self, total_assets: float, spouse: bool, adult_children: int,
        other_dependents: int, disabled_people: int, parents: int
    ) -> Tuple[float, float, float]:
        deductions = _self.compute_deductions(
            spouse, adult_children, other_dependents, disabled_people, parents
        )
        if total_assets < _self.constants.EXEMPT_AMOUNT + deductions:
            return 0, 0, deductions
        taxable_amount = max(0, total_assets - _self.constants.EXEMPT_AMOUNT - deductions)
        tax_due = 0.0
        prev = 0.0
        for bracket, rate in _self.constants.TAX_BRACKETS:
            if taxable_amount > prev:
                taxed = min(taxable_amount, bracket) - prev
                tax_due += taxed * rate
                prev = bracket
        return taxable_amount, round(tax_due, 0), deductions

# ===============================
# 介面（中文）
# ===============================
def main():
    st.set_page_config(page_title="家族遺產稅試算", layout="wide")

    st.markdown("## 🧮 家族遺產稅試算")
    st.caption("用清楚的試算，**提早預留稅源**，讓傳承更從容。所有金額單位：**萬元（TWD）**。")

    st.markdown("### 請輸入資產與家庭資訊")
    total_assets_input = st.number_input("總資產（萬元）", min_value=1000, max_value=100000, value=5000, step=100)

    st.markdown("---")
    st.markdown("### 家庭成員")
    has_spouse = st.checkbox("是否有配偶（扣除額 553 萬元）", value=False)
    adult_children_input = st.number_input("直系血親卑親屬數（每人 56 萬元）", min_value=0, max_value=10, value=0)
    parents_input = st.number_input("父母數（每人 138 萬元，最多 2 人）", min_value=0, max_value=2, value=0)
    max_disabled = (1 if has_spouse else 0) + adult_children_input + parents_input
    disabled_people_input = st.number_input("重度以上身心障礙者數（每人 693 萬元）", min_value=0, max_value=max_disabled, value=0)
    other_dependents_input = st.number_input("受撫養之兄弟姊妹、祖父母數（每人 56 萬元）", min_value=0, max_value=5, value=0)

    calculator = EstateTaxCalculator(TaxConstants())
    taxable_amount, tax_due, total_deductions = calculator.calculate_estate_tax(
        total_assets_input, has_spouse, adult_children_input,
        other_dependents_input, disabled_people_input, parents_input
    )

    st.markdown(f"## 預估遺產稅：{tax_due:,.0f} 萬元")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**資產概況**")
        st.table(pd.DataFrame({"項目": ["總資產"], "金額（萬元）": [int(total_assets_input)]}))

    with col2:
        st.markdown("**扣除項目**")
        df_deductions = pd.DataFrame({
            "項目": [
                "免稅額", "喪葬費扣除額", "配偶扣除額",
                "直系血親卑親屬扣除額", "父母扣除額",
                "重度身心障礙扣除額", "其他撫養扣除額"
            ],
            "金額（萬元）": [
                TaxConstants.EXEMPT_AMOUNT,
                TaxConstants.FUNERAL_EXPENSE,
                TaxConstants.SPOUSE_DEDUCTION_VALUE if has_spouse else 0,
                adult_children_input * TaxConstants.ADULT_CHILD_DEDUCTION,
                parents_input * TaxConstants.PARENTS_DEDUCTION,
                disabled_people_input * TaxConstants.DISABLED_DEDUCTION,
                other_dependents_input * TaxConstants.OTHER_DEPENDENTS_DEDUCTION
            ]
        }).astype({"金額（萬元）": int})
        st.table(df_deductions)

    with col3:
        st.markdown("**稅務計算**")
        st.table(pd.DataFrame({
            "項目": ["課稅遺產淨額", "預估遺產稅"],
            "金額（萬元）": [int(taxable_amount), int(tax_due)]
        }))

    # 下載 PDF
    st.markdown("---")

    def _build_pdf_bytes() -> bytes:
        lines = [
            "家族遺產稅試算（摘要）",
            "",
            f"總資產（萬元）：{total_assets_input:,.0f}",
            f"扣除總額（萬元）：{total_deductions:,.0f}",
            f"課稅遺產淨額（萬元）：{taxable_amount:,.0f}",
            f"預估遺產稅（萬元）：{tax_due:,.0f}",
            "",
            "— 扣除項目（萬元） —",
        ]
        for _, r in df_deductions.iterrows():
            lines.append(f"{r['項目']}: {r['金額（萬元）']:,d}")

        pdf_buf = generate_pdf(
            content="\n".join(lines),
            title="家族遺產稅試算",
            logo_path="logo.png",
            footer_text="永傳家族辦公室｜www.gracefo.com｜123@gracefo.com",
        )
        return pdf_buf.getvalue()

    st.download_button(
        "下載 PDF 摘要（萬元）",
        data=_build_pdf_bytes(),
        file_name="家族遺產稅試算_摘要_萬元.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.caption("＊本報告為即時生成之規劃建議，僅供參考")

if __name__ == "__main__":
    main()
