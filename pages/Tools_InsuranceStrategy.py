# pages/Tools_InsuranceStrategy.py
# 家族保單策略建議（英文檔名＋中文頁面；畫面統一以『萬元（TWD）』，USD 顯示等值）
from __future__ import annotations

import streamlit as st
from typing import List, Dict

from legacy_tools.modules.insurance_logic import (
    recommend_strategies,
    FX_USD_TWD,
)
from legacy_tools.modules.pdf_generator import generate_pdf

# ---------- 小工具 ----------
def _tier_label(budget_wan: float, currency: str) -> str:
    """以等值萬 TWD 判斷分級（顯示用）。"""
    twd_wan = budget_wan * (FX_USD_TWD if currency == "USD" else 1.0)
    if twd_wan >= 1000:
        return "高端預算"
    if twd_wan >= 300:
        return "進階預算"
    if twd_wan >= 100:
        return "標準預算"
    return "入門預算"

def _fmt_money_wan_twd(amount_wan: float) -> str:
    return f"{amount_wan:,.0f} 萬元"

def _fmt_budget_display(budget_wan: float, currency: str) -> str:
    """主畫面一律以『萬元（TWD）』顯示；USD 額外顯示原幣參考。"""
    if currency == "USD":
        twd_equiv = budget_wan * FX_USD_TWD
        return f"{_fmt_money_wan_twd(twd_equiv)}（約 US${budget_wan:,.0f} 萬）"
    return _fmt_money_wan_twd(budget_wan)

def _pdf_from_results(
    age: int,
    gender: str,
    budget_wan: float,
    currency: str,
    pay_years: int,
    goals: List[str],
    strategies: List[Dict],
) -> bytes:
    """輸出 PDF（以萬元 TWD 為主，含 logo／生成日期／頁尾）。"""
    tier = _tier_label(budget_wan, currency)
    main_budget_text = _fmt_budget_display(budget_wan, currency)
    lines: List[str] = []
    lines += [
        "家族保單策略建議（摘要）",
        "",
        f"年齡：{age}",
        f"性別：{gender}",
        f"總預算（統一顯示）：{main_budget_text}",
        f"繳費年期：{pay_years} 年",
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

    pdf_buf = generate_pdf(
        content="\n".join(lines),
        title="家族保單策略建議",
        logo_path="logo.png",
        footer_text="永傳家族辦公室｜www.gracefo.com｜123@gracefo.com",
    )
    return pdf_buf.getvalue()

# ---------- 介面 ----------
st.set_page_config(page_title="家族保單策略建議", page_icon="📦", layout="wide")

st.markdown("## 📦 家族保單策略建議")
st.caption("依您的家庭目標與預算，**即時產出專屬策略與說明**，協助預留稅源、守護家族現金流。")
st.caption("畫面一律以 **『萬元（TWD）』** 顯示；若選 USD，會同時顯示等值新台幣。")

with st.form("ins_form"):
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        age = st.number_input("年齡", min_value=18, max_value=85, value=45, step=1, format="%d")
        gender = st.selectbox("性別", ["不分", "女性", "男性"], index=0)

    with c2:
        currency = st.radio("幣別（可選 USD；畫面將統一顯示為萬元）", options=["TWD", "USD"], index=0, horizontal=True)
        helper = "請輸入單位：『萬元』（例：100 = 1,000,000）"
        budget_default = 300.0 if currency == "TWD" else 10.0
        budget = st.number_input(
            "總預算（以『萬元』輸入）",
            min_value=1.0, value=budget_default, step=1.0, help=helper
        )

    with c3:
        pay_years = st.number_input(
            "繳費年期（年）",
            min_value=1, max_value=30, value=10, step=1, format="%d",
            help="預設 10 年；最少 1 年、最多 30 年。"
        )
        goals = st.multiselect(
            "家庭目標（可複選 1–3 項）",
            ["傳承", "退休", "醫療", "長照", "教育", "資產配置", "稅源", "企業主"],
            default=["傳承"],
        )

    submitted = st.form_submit_button("✨ 產生建議")

if not submitted:
    st.info("請先輸入條件並按下「✨ 產生建議」。")
    st.stop()

# 基本驗證
if budget <= 0:
    st.error("請輸入有效的總預算（萬元）。")
    st.stop()
if not goals:
    st.warning("請至少選擇 1 個目標，才會有具體建議。")
    st.stop()

# 引擎呼叫（注意使用複數參數名 goals）
recs = recommend_strategies(
    age=int(age),
    gender=gender,
    budget=float(budget),
    currency=currency,      # 'TWD' / 'USD'
    pay_years=int(pay_years),
    goals=goals,            # ✅ 正確參數名稱
)

# 分級與顯示
tier_text = _tier_label(float(budget), currency)
main_budget_text = _fmt_budget_display(float(budget), currency)

st.markdown(
    f"### 📌 分級：**{tier_text}**　｜　總預算：**{main_budget_text}**　｜　年期：**{int(pay_years)} 年**"
)

# 策略清單
if not recs:
    st.info("目前條件下尚無明確策略，請調整目標或預算。")
else:
    for i, s in enumerate(recs, 1):
        with st.expander(f"{i}. {s.get('name','（未命名策略）')}"):
            st.markdown(f"**適用對象：** {'、'.join(s.get('fit', []) or [])}")
            st.markdown(f"**策略觀念：** {s.get('why','')}")
            st.markdown(f"**實作作法：** {s.get('description','')}")

# 下載區（TXT / PDF）
st.markdown("---")
colA, colB = st.columns(2)

# .txt 內容
txt_lines = [
    f"# 家族保單策略建議（{tier_text}）",
    "",
    f"- 年齡：{int(age)}",
    f"- 性別：{gender}",
    f"- 總預算（統一顯示）：{main_budget_text}",
    f"- 繳費年期：{int(pay_years)} 年",
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
        "下載 .txt（萬元）",
        data=txt_content,
        file_name="家族保單策略建議_萬元.txt",
        mime="text/plain",
    )

with colB:
    pdf_bytes = _pdf_from_results(
        int(age), gender, float(budget), currency, int(pay_years), goals, recs
    )
    st.download_button(
        "下載 PDF（萬元）",
        data=pdf_bytes,
        file_name="家族保單策略建議_萬元.pdf",
        mime="application/pdf",
    )

st.caption("＊本報告為即時生成之規劃建議，僅供參考")
