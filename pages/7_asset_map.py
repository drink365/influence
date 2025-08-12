import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
from io import BytesIO
from modules.pdf_generator import generate_asset_map_pdf
from modules.config import setup_page

# 頁面設定
setup_page("《影響力》資產結構、風險與現金流模擬")

# 中文字型設定
font_path = "NotoSansTC-Regular.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()

# 標題
st.markdown(
    "<div style='text-align:center;'>"
    "<h2 style='font-size:28px;'>《影響力》資產結構、風險與現金流模擬</h2>"
    "</div>", unsafe_allow_html=True
)

# 側邊欄輸入
st.sidebar.header("🔧 輸入參數")
st.sidebar.markdown("請輸入各類資產金額（萬元）及年化現金流率（%）：")
labels = ["公司股權","不動產","金融資產","保單","海外資產","其他"]
values, yields = [], []
for asset in labels:
    # 資產名稱加大字體
    st.sidebar.markdown(f"<span style='font-size:16px; font-weight:bold;'>{asset}</span>", unsafe_allow_html=True)
    val = st.sidebar.number_input(f"{asset} 金額 (萬元)", min_value=0, value=0, step=100)
    rate = st.sidebar.number_input(f"{asset} 年化現金流率 (%)", min_value=0.0, value=3.0, step=0.1)
    values.append(val)
    yields.append(rate)

total_assets = sum(values)

# 計算現金流
df_cash = pd.DataFrame({
    "資產類別": labels,
    "金額(萬)": values,
    "現金流率(%)": yields
})
df_cash["年現金流(萬)"] = df_cash["金額(萬)"] * df_cash["現金流率(%)"] / 100

total_flow = df_cash["年現金流(萬)"].sum()

# 建議摘要
def generate_suggestions(df: pd.DataFrame, total_assets: float, total_flow: float):
    suggestions = []
    # 保單
    idx_ins = df.index[df["資產類別"] == "保單"][0]
    if df.loc[idx_ins, "年現金流(萬)"] < 0.02 * total_assets:
        suggestions.append("保單現金流率偏低，建議增加高收益產品以提升固定現金流。")
    # 金融資產
    idx_fin = df.index[df["資產類別"] == "金融資產"][0]
    if df.loc[idx_fin, "年現金流(萬)"] < 0.03 * total_assets:
        suggestions.append("金融資產現金流不足，建議調整至更高收益工具。")
    # 不動產
    idx_re = df.index[df["資產類別"] == "不動產"][0]
    if df.loc[idx_re, "金額(萬)"] > 0.4 * total_assets:
        suggestions.append("不動產比例過高，租金波動可能影響現金流穩定性。")
    # 整體
    if total_flow / total_assets < 0.03:
        suggestions.append("整體現金流率低於3%，建議優化組合提高現金流覆蓋率。")
    if not suggestions:
        suggestions.append("現金流結構良好，請持續監控並定期調整組合。")
    return suggestions

suggestions = generate_suggestions(df_cash, total_assets, total_flow)

# 首屏儀表板
col1, col2, col3 = st.columns(3)
col1.metric("總資產 (萬元)", f"{total_assets:,.0f}")
col2.metric("總年現金流 (萬元)", f"{total_flow:,.1f}")
avg_yield = (total_flow / total_assets * 100) if total_assets else 0
col3.metric("平均現金流率 (%)", f"{avg_yield:.2f}")

# 主要圖表區
if total_assets > 0:
    filtered = df_cash[df_cash["金額(萬)"] > 0]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    # 圓餅圖
    ax1.pie(
        filtered["金額(萬)"],
        labels=filtered["資產類別"],
        autopct="%1.1f%%",
        startangle=140,
        textprops={"fontproperties": font_prop, "fontsize": 10}
    )
    ax1.set_title("資產結構分佈", fontproperties=font_prop)
    ax1.axis('equal')
    # 長條圖
    ax2.bar(
        filtered["資產類別"],
        filtered["年現金流(萬)"],
        color="#8BC34A"
    )
    ax2.set_title("年現金流 (萬元)", fontproperties=font_prop)
    ax2.set_ylabel("年現金流 (萬元)", fontproperties=font_prop)
    for tick in ax2.get_xticklabels():
        tick.set_fontproperties(font_prop)
        tick.set_rotation(45)
        tick.set_ha('right')
    fig.tight_layout()
    st.pyplot(fig)
else:
    st.info("尚未輸入任何資產，請於側邊欄輸入後查看圖表。")

# 展開區：明細與建議
with st.expander("🔍 查看現金流明細與建議"):
    if total_assets > 0:
        st.subheader("資產與現金流明細表")
        st.dataframe(
            df_cash.style.format({
                "金額(萬)": "{:,}",
                "現金流率(%)": "{:.1f}",
                "年現金流(萬)": "{:.1f}"
            }), use_container_width=True
        )
        st.subheader("建議摘要")
        for s in suggestions:
            st.info(s)
    else:
        st.info("請先輸入資產並完成分析後，才能查看明細與建議。")

# 展開區：報告下載與下一步
with st.expander("📄 下載報告與下一步"):
    if total_assets > 0:
        fig_report, (r1, r2) = plt.subplots(1, 2, figsize=(10, 5))
        r1.pie(
            filtered["金額(萬)"],
            labels=filtered["資產類別"],
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontproperties": font_prop, "fontsize": 10}
        )
        r1.set_title("資產結構分佈", fontproperties=font_prop)
        r1.axis('equal')
        r2.bar(
            filtered["資產類別"],
            filtered["年現金流(萬)"],
            color="#8BC34A"
        )
        r2.set_title("年現金流 (萬元)", fontproperties=font_prop)
        r2.set_ylabel("年現金流 (萬元)", fontproperties=font_prop)
        for tick in r2.get_xticklabels():
            tick.set_fontproperties(font_prop)
            tick.set_rotation(45)
            tick.set_ha('right')
        fig_report.tight_layout()
        buf = BytesIO()
        fig_report.savefig(buf, format='png')
        buf.seek(0)
        pdf_file = generate_asset_map_pdf(labels, values, suggestions, buf)
        st.download_button(
            label="📄 下載資產及現金流報告",
            data=pdf_file,
            file_name="asset_cashflow_report.pdf",
            mime="application/pdf"
        )
        plt.close(fig_report)
    else:
        st.info("報告需先輸入資產並完成分析。")
    st.markdown("---")
    st.markdown("如需深入遺產稅影響分析：")
    if st.button("🧮 AI 秒算遺產稅"):
        st.switch_page("pages/5_estate_tax.py")

# 聯絡資訊
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px;'>"
    "<a href='/' style='color:#006666; text-decoration:underline;'>《影響力》傳承策略平台</a> | "
    "<a href='https://gracefo.com' target='_blank'>永傳家族辦公室</a> | "
    "<a href='mailto:123@gracefo.com'>123@gracefo.com</a>"
    "</div>", unsafe_allow_html=True
)
