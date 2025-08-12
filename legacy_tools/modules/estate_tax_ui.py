import streamlit as st
import pandas as pd
from modules.tax_constants import TaxConstants
from modules.tax_calculator import EstateTaxCalculator


def render_estate_tax_ui(calculator: EstateTaxCalculator):
    constants = calculator.constants

    st.markdown("## 🧾 請輸入基本資訊")

    col1, col2 = st.columns(2)
    with col1:
        total_assets_input = st.number_input(
            "總資產（萬）",
            min_value=0,
            value=3000,
            step=100,
            help="請輸入遺產總額"
        )
        has_spouse = st.checkbox("是否有配偶", value=False)
        adult_children_input = st.number_input("成年子女人數", min_value=0, value=0)

    with col2:
        parents_input = st.number_input("父母人數", min_value=0, max_value=2, value=0)
        disabled_people_input = st.number_input("重度身心障礙者人數", min_value=0, value=0)
        other_dependents_input = st.number_input("其他受扶養親屬人數", min_value=0, value=0)

    # 自動即時計算遺產稅
    try:
        taxable_amount, tax_due, total_deductions = calculator.calculate_estate_tax(
            total_assets_input,
            has_spouse,
            adult_children_input,
            other_dependents_input,
            disabled_people_input,
            parents_input
        )
    except Exception as e:
        st.error(f"計算遺產稅時發生錯誤：{e}")
        return

    st.markdown("---")
    st.subheader("💡 預估遺產稅結果")
    st.markdown(f"**課稅遺產淨額：** {taxable_amount:,.0f} 萬元")
    st.markdown(f"**預估遺產稅：** {tax_due:,.0f} 萬元")

    st.markdown("### 📌 各項扣除額明細")
    deduction_data = [
        ("免稅額", constants.EXEMPT_AMOUNT),
        ("喪葬費扣除額", constants.FUNERAL_EXPENSE),
        ("配偶扣除額", constants.SPOUSE_DEDUCTION_VALUE if has_spouse else 0),
        ("子女扣除額", adult_children_input * constants.ADULT_CHILD_DEDUCTION),
        ("父母扣除額", parents_input * constants.PARENTS_DEDUCTION),
        ("重度身障扣除額", disabled_people_input * constants.DISABLED_DEDUCTION),
        ("其他撫養扣除額", other_dependents_input * constants.OTHER_DEPENDENTS_DEDUCTION),
    ]

    deductions_df = pd.DataFrame(deduction_data, columns=["項目", "扣除金額（萬）"])
    deductions_df["扣除金額（萬）"] = deductions_df["扣除金額（萬）"].astype(int)
    st.table(deductions_df)

    st.markdown("---")
    st.markdown("### 📍 提醒您：")
    st.markdown("""
    - 本工具僅供初步估算參考，實際遺產稅額仍需依個案情況與稅務規定而定。
    - 若您希望規劃保險、贈與、信託等策略，我們可提供一對一諮詢協助。
    """)
