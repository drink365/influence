# pages/Tools_EstateTax.py
# 遺產稅試算（全站統一單位：萬元）
from __future__ import annotations
import streamlit as st
import pandas as pd
import math
import plotly.express as px
from typing import Tuple, Dict, Any, List
from datetime import datetime
import time
from dataclasses import dataclass, field

# ===============================
# 1. 常數與設定（單位：萬元）
# ===============================
@dataclass
class TaxConstants:
    EXEMPT_AMOUNT: float = 1333    # 免稅額（萬元）
    FUNERAL_EXPENSE: float = 138   # 喪葬費（萬元）
    SPOUSE_DEDUCTION_VALUE: float = 553
    ADULT_CHILD_DEDUCTION: float = 56
    PARENTS_DEDUCTION: float = 138
    DISABLED_DEDUCTION: float = 693
    OTHER_DEPENDENTS_DEDUCTION: float = 56
    TAX_BRACKETS: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (5621, 0.1),
            (11242, 0.15),
            (float('inf'), 0.2)
        ]
    )

# ===============================
# 2. 稅務計算邏輯（單位：萬元）
# ===============================
class EstateTaxCalculator:
    def __init__(self, constants: TaxConstants):
        self.constants = constants

    def compute_deductions(self, spouse: bool, adult_children: int, other_dependents: int,
                           disabled_people: int, parents: int) -> float:
        spouse_deduction = self.constants.SPOUSE_DEDUCTION_VALUE if spouse else 0
        total_deductions = (
            spouse_deduction +
            self.constants.FUNERAL_EXPENSE +
            (disabled_people * self.constants.DISABLED_DEDUCTION) +
            (adult_children * self.constants.ADULT_CHILD_DEDUCTION) +
            (other_dependents * self.constants.OTHER_DEPENDENTS_DEDUCTION) +
            (parents * self.constants.PARENTS_DEDUCTION)
        )
        return total_deductions

    @st.cache_data
    def calculate_estate_tax(_self, total_assets: float, spouse: bool, adult_children: int,
                             other_dependents: int, disabled_people: int, parents: int) -> Tuple[float, float, float]:
        deductions = _self.compute_deductions(spouse, adult_children, other_dependents, disabled_people, parents)
        if total_assets < _self.constants.EXEMPT_AMOUNT + deductions:
            return 0, 0, deductions
        taxable_amount = max(0, total_assets - _self.constants.EXEMPT_AMOUNT - deductions)
        tax_due = 0.0
        previous_bracket = 0
        for bracket, rate in _self.constants.TAX_BRACKETS:
            if taxable_amount > previous_bracket:
                taxable_at_rate = min(taxable_amount, bracket) - previous_bracket
                tax_due += taxable_at_rate * rate
                previous_bracket = bracket
        return taxable_amount, round(tax_due, 0), deductions

# ===============================
# 3. 模擬試算邏輯（單位：萬元）
# ===============================
class EstateTaxSimulator:
    def __init__(self, calculator: EstateTaxCalculator):
        self.calculator = calculator

    def simulate_insurance_strategy(self, total_assets: float, spouse: bool, adult_children: int,
                                    other_dependents: int, disabled_people: int, parents: int,
                                    premium_ratio: float, premium: float) -> Dict[str, Any]:
        _, tax_no_insurance, _ = self.calculator.calculate_estate_tax(
            total_assets, spouse, adult_children, other_dependents, disabled_people, parents
        )
        net_no_insurance = total_assets - tax_no_insurance
        claim_amount = round(premium * premium_ratio, 0)
        new_total_assets = total_assets - premium
        _, tax_new, _ = self.calculator.calculate_estate_tax(
            new_total_assets, spouse, adult_children, other_dependents, disabled_people, parents
        )
        net_not_taxed = round(new_total_assets - tax_new + claim_amount, 0)
        effect_not_taxed = net_not_taxed - net_no_insurance
        effective_estate = total_assets - premium + claim_amount
        _, tax_effective, _ = self.calculator.calculate_estate_tax(
            effective_estate, spouse, adult_children, other_dependents, disabled_people, parents
        )
        net_taxed = round(effective_estate - tax_effective, 0)
        effect_taxed = net_taxed - net_no_insurance
        return {
            "沒有規劃": {
                "總資產（萬元）": int(total_assets),
                "預估遺產稅（萬元）": int(tax_no_insurance),
                "家人總共取得（萬元）": int(net_no_insurance)
            },
            "有規劃保單": {
                "預估遺產稅（萬元）": int(tax_new),
                "家人總共取得（萬元）": int(net_not_taxed),
                "規劃效果（萬元）": int(effect_not_taxed)
            },
            "有規劃保單 (被實質課稅)": {
                "預估遺產稅（萬元）": int(tax_effective),
                "家人總共取得（萬元）": int(net_taxed),
                "規劃效果（萬元）": int(effect_taxed)
            }
        }

# ===============================
# 4. 介面（單位：萬元）
# ===============================
def main():
    st.set_page_config(page_title="AI 秒算遺產稅（萬元）", layout="wide")
    st.markdown("<h1 class='main-header'>AI 秒算遺產稅</h1>", unsafe_allow_html=True)
    st.caption("所有金額單位：**萬元（TWD）**")

    with st.container():
        st.markdown("## 請輸入資產及家庭資訊")
        total_assets_input = st.number_input(
            "總資產（萬元）", min_value=1000, max_value=100000,
            value=5000, step=100, help="請輸入您的總資產（單位：萬元）"
        )
        st.markdown("---")
        st.markdown("### 請輸入家庭成員數")
        has_spouse = st.checkbox("是否有配偶（扣除額 553 萬元）", value=False)
        adult_children_input = st.number_input(
            "直系血親卑親屬數（每人 56 萬元）", min_value=0, max_value=10, value=0
        )
        parents_input = st.number_input(
            "父母數（每人 138 萬元，最多 2 人）", min_value=0, max_value=2, value=0
        )
        max_disabled = (1 if has_spouse else 0) + adult_children_input + parents_input
        disabled_people_input = st.number_input(
            "重度以上身心障礙者數（每人 693 萬元）", min_value=0, max_value=max_disabled, value=0
        )
        other_dependents_input = st.number_input(
            "受撫養之兄弟姊妹、祖父母數（每人 56 萬元）", min_value=0, max_value=5, value=0
        )

    calculator = EstateTaxCalculator(TaxConstants())
    try:
        taxable_amount, tax_due, total_deductions = calculator.calculate_estate_tax(
            total_assets_input, has_spouse, adult_children_input,
            other_dependents_input, disabled_people_input, parents_input
        )
    except Exception as e:
        st.error(f"計算遺產稅時發生錯誤：{e}")
        return

    st.markdown(f"## 預估遺產稅：{tax_due:,.0f} 萬元")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**資產概況**")
        df_assets = pd.DataFrame({"項目": ["總資產"], "金額（萬元）": [int(total_assets_input)]})
        st.table(df_assets)
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
        df_tax = pd.DataFrame({
            "項目": ["課稅遺產淨額", "預估遺產稅"],
            "金額（萬元）": [int(taxable_amount), int(tax_due)]
        })
        st.table(df_tax)

    st.markdown("---")
    st.markdown("## 家族傳承策略建議（方向）")
    st.markdown(
        """
        1. 規劃保單：透過保險預留稅源。  
        2. 提前贈與：利用免稅贈與逐年轉移財富。  
        3. 分散配置：透過合理資產配置降低稅負。
        """
    )

if __name__ == "__main__":
    main()
