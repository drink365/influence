# pages/Tools_AssetMap.py
# 家族資產地圖（英文檔名＋中文頁面；單位：萬元 TWD）
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from legacy_tools.modules.pdf_generator import generate_pdf

# ---------- 小工具 ----------
def fmt_wan(n: float) -> str:
    try:
        return f"{float(n):,.0f} 萬"
    except Exception:
        return "—"

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

# ---------- 介面設定 ----------
st.set_page_config(page_title="家族資產地圖", layout="wide")

st.markdown("## 🗺️ 家族資產地圖")
st.caption("把專業變成家人的安心：**3 分鐘看懂家族資產版圖**，協助您規劃現金流與傳承節奏。")
st.caption("所有金額單位：**萬元（TWD）**。請以「萬元」輸入（例：500 代表 NT$5,000,000）。")

with st.form("asset_form"):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 資產（萬元）")
        cash = st.number_input("現金 / 活存", min_value=0.0, value=100.0, step=10.0)
        deposit = st.number_input("定存 / 外幣存款（折合新台幣）", min_value=0.0, value=200.0, step=10.0)
        securities = st.number_input("股票 / 基金 / ETF", min_value=0.0, value=300.0, step=10.0)
        insurance_cv = st.number_input("保單現金價值", min_value=0.0, value=150.0, step=10.0)
        real_estate = st.number_input("不動產（淨值）", min_value=0.0, value=800.0, step=10.0)
        business_equity = st.number_input("企業股權（估值）", min_value=0.0, value=500.0, step=10.0)
        crypto = st.number_input("加密資產", min_value=0.0, value=0.0, step=10.0)
        other_assets = st.number_input("其他資產", min_value=0.0, value=0.0, step=10.0)

    with c2:
        st.markdown("### 負債（萬元）")
        mortgage = st.number_input("房貸餘額", min_value=0.0, value=400.0, step=10.0)
        loans = st.number_input("信貸 / 車貸", min_value=0.0, value=50.0, step=10.0)
        biz_loans = st.number_input("企業貸款", min_value=0.0, value=0.0, step=10.0)
        tax_reserve = st.number_input("稅務準備（未繳之預估稅金）", min_value=0.0, value=0.0, step=10.0)
        other_liab = st.number_input("其他負債", min_value=0.0, value=0.0, step=10.0)

    submitted = st.form_submit_button("產生資產地圖")

if not submitted:
    st.info("請輸入上方數據並按下「產生資產地圖」。")
    st.stop()

# ---------- 計算 ----------
asset_items = {
    "現金 / 活存": cash,
    "定存 / 外幣存款（折合新台幣）": deposit,
    "股票 / 基金 / ETF": securities,
    "保單現金價值": insurance_cv,
    "不動產（淨值）": real_estate,
    "企業股權（估值）": business_equity,
    "加密資產": crypto,
    "其他資產": other_assets,
}
liab_items = {
    "房貸餘額": mortgage,
    "信貸 / 車貸": loans,
    "企業貸款": biz_loans,
    "稅務準備": tax_reserve,
    "其他負債": other_liab,
}

df_assets = pd.DataFrame(
    [{"項目": k, "金額（萬元）": float(v)} for k, v in asset_items.items()]
).sort_values("金額（萬元）", ascending=False)
df_liab = pd.DataFrame(
    [{"項目": k, "金額（萬元）": float(v)} for k, v in liab_items.items()]
).sort_values("金額（萬元）", ascending=False)

total_assets = float(df_assets["金額（萬元）"].sum())
total_liab = float(df_liab["金額（萬元）"].sum())
net_worth = total_assets - total_liab

# ---------- 指標摘要 ----------
m1, m2, m3 = st.columns(3)
m1.metric("總資產（萬元）", fmt_wan(total_assets))
m2.metric("總負債（萬元）", fmt_wan(total_liab))
m3.metric("家族淨值（萬元）", fmt_wan(net_worth))

st.markdown("---")

# ---------- 配置圖與表 ----------
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown("### 資產配置（萬元）")
    df_assets_nonzero = df_assets[df_assets["金額（萬元）"] > 0].copy()
    if df_assets_nonzero.empty:
        st.info("目前資產全為 0，請輸入數值後再產生圖表。")
    else:
        fig = px.pie(
            df_assets_nonzero,
            names="項目",
            values="金額（萬元）",
            hole=0.35,
            title="家族資產配置比例（單位：萬元）"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=480, margin=dict(t=80, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 明細表")
    with st.expander("資產明細（萬元）", expanded=True):
        st.dataframe(df_assets, use_container_width=True)
        st.download_button(
            "下載資產 CSV（萬元）",
            data=df_to_csv_bytes(df_assets),
            file_name="資產明細_萬元.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with st.expander("負債明細（萬元）", expanded=True):
        st.dataframe(df_liab, use_container_width=True)
        st.download_button(
            "下載負債 CSV（萬元）",
            data=df_to_csv_bytes(df_liab),
            file_name="負債明細_萬元.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.markdown("---")

# ---------- 下載 PDF 摘要（萬元） ----------
def build_pdf_bytes() -> bytes:
    lines = []
    lines += [
        "家族資產地圖（摘要）",
        "",
        f"總資產（萬元）：{total_assets:,.0f}",
        f"總負債（萬元）：{total_liab:,.0f}",
        f"家族淨值（萬元）：{net_worth:,.0f}",
        "",
        "— 資產明細（萬元） —",
    ]
    for _, r in df_assets.iterrows():
        lines.append(f"{r['項目']}: {r['金額（萬元）']:,.0f}")
    lines += ["", "— 負債明細（萬元） —"]
    for _, r in df_liab.iterrows():
        lines.append(f"{r['項目']}: {r['金額（萬元）']:,.0f}")

    pdf_buf = generate_pdf(
        content="\n".join(lines),
        title="家族資產地圖",
        logo_path="logo.png",
        footer_text="永傳家族辦公室｜www.gracefo.com｜123@gracefo.com",
    )
    return pdf_buf.getvalue()

cA, cB = st.columns([1, 1])
with cA:
    st.download_button(
        "下載 PDF 摘要（萬元）",
        data=build_pdf_bytes(),
        file_name="家族資產地圖_摘要_萬元.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with cB:
    df_all = pd.concat(
        [df_assets.assign(類別="資產"), df_liab.assign(類別="負債")],
        ignore_index=True,
    )
    st.download_button(
        "下載總表 CSV（萬元）",
        data=df_to_csv_bytes(df_all[["類別", "項目", "金額（萬元）"]]),
        file_name="資產地圖_總表_萬元.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption("＊本報告為即時生成之規劃建議，僅供參考")
st.caption("說明：本頁所有數值皆以 **萬元（TWD）** 為單位；外幣請先折合新台幣後再填入。")
