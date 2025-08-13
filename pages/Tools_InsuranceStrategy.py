# pages/Tools_InsuranceStrategy.py
# 保單策略建議（新版介面）
# - 幣別：TWD / USD
# - 預算：總預算（單位：萬 <幣別>）
# - 繳費年期：預設 10 年、最少 1、最多 30（整數）
# - 分級：以「萬TWD」換算後套用 高端/進階/標準/入門
# - 產出：策略清單 + PDF 摘要可下載

from __future__ import annotations

import streamlit as st
from typing import List, Dict

from legacy_tools.modules.insurance_logic import (
    recommend_strategies,
    FX_USD_TWD,  # 與引擎一致的換算
)
from legacy_tools.modules.pdf_generator import generate_pdf


# ---------- 小工具 ----------
def _tier_label(budget_wan: float, currency: str) -> str:
    """以等值萬TWD 判斷分級，回傳顯示文字。"""
    budget_in_twd_wan = budget_wan * (FX_USD_TWD if currency == "USD" else 1.0)
    if budget_in_twd_wan >= 1000:
        return "高端預算"
    if budget_in_twd_wan >= 300:
        return "進階預算"
    if budget_in_twd_wan >= 100:
        return "標準預算"
    return "入門預算"


def _fmt_money_wan(amount_wan: float, currency: str) -> str:
    symbol = "NT$" if currency == "TWD" else "US$"
    return f"{symbol}{amount_wan:,.0f}萬"


def _pdf_from_results(
    age: int,
    gender: str,
    budget_wan: float,
    currency: str,
    pay_years: int,
    goals: List[str],
    strategies: List[Dict],
) -> bytes:
    """把摘要與策略清單組成 PDF 文字，呼叫共用引擎."""
    tier = _tier_label(budget_wan, currency)
    lines: List[str] = []
    lines += [
        "保單策略建議摘要",
        "",
        f"年齡：{age}",
        f"性別：{gender}",
        f"總預算：{_fmt_money_wan(budget_wan, currency)}",
        f"繳費年期：{pay_years} 年",
        f"幣別：{currency}",
        f"分級：{tier}",
        f"目標：{('、'.join(goals)) if goals else '（未填）'}",
        "",
        "—— 策略清單 ——",
        "",
    ]
    for i, s in enumerate(strategies, 1):
        name = s.get("name", "")
        why = s.get("why", "")
        fit = "、".join(s.get("fit", []) or [])
        desc = s.get("description", "")
        lines += [
            f"{i}. {name}",
            f"   適用：{fit}" if fit else "   適用：",
            f"   觀念：{why}",
            f"   作法：{desc}",
            "",
        ]

    pdf_buf = generate_pdf(content="\n".join(lines), title="保單策略建議")
    return pdf_buf.getvalue()


# ---------- 介面 ----------
st.set_page_config(page_title="保單策略建議｜influence", page_icon="📦", layout="wide")
st.markdown("## 📦 保單策略建議")
st.caption("輸入基本條件與目標，系統依預算分級（高端/進階/標準/入門）提供策略方向。")

with st.form("ins_form"):
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        age = st.number_input("年齡", min_value=18, max_value=85, value=45, step=1, format="%d")
        gender = st.selectbox("性別", ["不分", "女性", "男性"], index=0)

    with c2:
        currency = st.radio("幣別", options=["TWD", "USD"], index=0, horizontal=True)
        helper = "例：100 = NT$1,000,000" if currency == "TWD" else "例：10 = US$100,000"
        budget_default = 300.0 if currency == "TWD" else 10.0
        budget = st.number_input(
            "總預算（萬）",
            min_value=1.0,
            value=budget_default,
            step=1.0,
            help=helper,
        )

    with c3:
        # 強制整數 + 允許 1~30 年
        pay_years = st.number_input(
            "繳費年期（年）",
            min_value=1,
            max_value=30,
            value=10,
            step=1,
            format="%d",
            help="預設 10 年；最少 1 年、最多 30 年。",
        )
        goals = st.multiselect(
            "目標（可複選 1–3 項）",
            ["傳承", "退休", "醫療", "長照", "教育", "資產配置", "稅源", "企業主"],
            default=["傳承"],
            help="建議先選 1–2 個最重要的目標。",
        )

    submitted = st.form_submit_button("✨ 產生建議")

if not submitted:
    st.info("請先輸入條件並按下「✨ 產生建議」。")
    st.stop()

# 基本驗證
if budget <= 0:
    st.error("請輸入有效的總預算（萬）。")
    st.stop()
if not goals:
    st.warning("請至少選擇 1 個目標，才會有具體建議。")
    st.stop()

# ✅ 新版 API 呼叫（不再使用舊的 goal/years 參數）
recs = recommend_strategies(
    age=int(age),
    gender=gender,
    budget=float(budget),         # 總預算（萬 <currency>）
    currency=currency,            # 'TWD' / 'USD'
    pay_years=int(pay_years),
    goals=goals,
)

# 分級標籤
tier_text = _tier_label(float(budget), currency)
st.markdown(
    f"### 📌 分級：**{tier_text}**　｜　總預算：**{_fmt_money_wan(float(budget), currency)}**　｜　年期：**{int(pay_years)} 年**"
)

# 顯示策略清單
if not recs:
    st.info("目前條件下尚無明確策略，請調整目標或提高預算。")
else:
    for i, s in enumerate(recs, 1):
        with st.expander(f"{i}. {s.get('name','（未命名策略）')}"):
            st.markdown(f"**適用對象：** {'、'.join(s.get('fit', []) or [])}")
            st.markdown(f"**策略觀念：** {s.get('why','')}")
            st.markdown(f"**實作作法：** {s.get('description','')}")

# 下載區（TXT / PDF）
st.markdown("---")
colA, colB = st.columns(2)

# TXT
txt_lines = [f"# 保單策略建議（{tier_text}）", ""]
txt_lines += [
    f"- 年齡：{int(age)}",
    f"- 性別：{gender}",
    f"- 總預算：{_fmt_money_wan(float(budget), currency)}",
    f"- 繳費年期：{int(pay_years)} 年",
    f"- 幣別：{currency}",
    f"- 目標：{('、'.join(goals)) if goals else '（未填）'}",
    "",
    "## 策略清單",
    "",
]
for i, s in enumerate(recs, 1):
    txt_lines += [
        f"{i}. {s.get('name','')}",
        f"   適用：{'、'.join(s.get('fit', []) or [])}",
        f"   觀念：{s.get('why','')}",
        f"   作法：{s.get('description','')}",
        "",
    ]
txt_content = "\n".join(txt_lines)

with colA:
    st.download_button(
        "下載 .txt",
        data=txt_content,
        file_name="保單策略建議.txt",
        mime="text/plain",
    )

# PDF
pdf_bytes = _pdf_from_results(
    int(age), gender, float(budget), currency, int(pay_years), goals, recs
)
with colB:
    st.download_button(
        "下載 PDF",
        data=pdf_bytes,
        file_name="保單策略建議.pdf",
        mime="application/pdf",
    )

st.caption("提示：分級以等值新台幣門檻計算（USD 依引擎匯率換算）；PDF 已套用共用品牌樣式。")
