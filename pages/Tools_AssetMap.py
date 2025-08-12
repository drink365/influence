# pages/Tools_AssetMap.py
# 🗺️ 傳承地圖｜完整版（六大資產＋現金流＋PDF 匯出）
# 特色：
# 1) 六大資產分類（公司股權、不動產、金融資產、保單、海外資產、其他資產）
# 2) 輸入各類金額與預估年化現金流率 → 自動計算年現金流
# 3) 圓餅圖＋現金流總表＋集中度/流動性偵測與建議
# 4) 一鍵匯出 PDF（含圖與表），方便提案

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io, os
from datetime import date
from math import isfinite

# ---- UI 基本設定 ----
st.set_page_config(page_title="傳承地圖｜完整版", page_icon="🗺️", layout="wide")
st.title("🗺️ 傳承地圖｜完整版")
st.caption("輸入六大資產分布與預估現金流率，系統自動生成圓餅圖、現金流表與重點建議，並可一鍵匯出 PDF。")

# ---- 中文字型（若有 NotoSansTC-Regular.ttf 就用；沒有則忽略） ----
try:
    import matplotlib
    font_path = os.path.join(os.path.dirname(__file__), "..", "NotoSansTC-Regular.ttf")
    if os.path.exists(font_path):
        matplotlib.font_manager.fontManager.addfont(font_path)
        plt.rcParams["font.sans-serif"] = ["Noto Sans TC"]
        plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass  # 沒字型也不影響功能

# ---- 六大資產分類（依你既定標準）----
ASSET_CATEGORIES = [
    {"key": "equity", "label": "公司股權", "default_rate": 2.0},     # 預設以股利/分紅估 2%
    {"key": "realty", "label": "不動產", "default_rate": 2.0},     # 淨租金率估 2%
    {"key": "financial", "label": "金融資產", "default_rate": 3.0},# 配息/利息估 3%
    {"key": "policy", "label": "保單", "default_rate": 2.5},       # 現金價值增長或分紅估 2.5%
    {"key": "overseas", "label": "海外資產", "default_rate": 2.0}, # 保守估
    {"key": "others", "label": "其他資產", "default_rate": 0.5},   # 謹慎估
]

# ---- 資料輸入 ----
st.subheader("① 請輸入資產分布與現金流假設")
c1, c2 = st.columns([2,1])

with c1:
    st.markdown("**資產金額（TWD）**")
with c2:
    st.markdown("**預估年化現金流率（%）**")

inputs = []
cols_amt = st.columns(3)
cols_rate = st.columns(3)
for i, cat in enumerate(ASSET_CATEGORIES):
    with cols_amt[i % 3]:
        amt = st.number_input(cat["label"], min_value=0, value=0, step=100000, key=f"amt_{cat['key']}")
    with cols_rate[i % 3]:
        rate = st.number_input(f"{cat['label']} 現金流率(%)", min_value=0.0, value=float(cat["default_rate"]), step=0.1, key=f"rate_{cat['key']}")
    cash = round(amt * rate / 100.0)
    inputs.append({"資產類別": cat["label"], "金額": amt, "現金流率(%)": rate, "年現金流": cash})

df = pd.DataFrame(inputs)

total_amt = int(df["金額"].sum())
total_cash = int(df["年現金流"].sum())

st.markdown("---")
st.subheader("② 視覺化總覽")

# ---- 畫圓餅圖 ----
if total_amt == 0:
    st.info("請先輸入各資產類別的金額數值。")
else:
    fig, ax = plt.subplots(figsize=(5,5))
    labels = df["資產類別"].tolist()
    values = df["金額"].tolist()
    autopct_fmt = lambda p: f"{p:.1f}%" if p > 0 else ""
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct=autopct_fmt, startangle=90)
    ax.axis("equal")
    st.pyplot(fig, use_container_width=False)

    st.markdown(f"**總資產**：NT$ {total_amt:,.0f}　｜　**預估年現金流**：NT$ {total_cash:,.0f}")

    st.markdown("### 現金流明細")
    df_show = df.copy()
    df_show["占比(%)"] = (df_show["金額"] / total_amt * 100).round(1)
    st.dataframe(df_show, use_container_width=True)

# ---- 風險偵測與建議 ----
st.markdown("---")
st.subheader("③ 風險偵測與建議（自動）")

def risk_checks(df: pd.DataFrame):
    tips = []
    if df["金額"].sum() <= 0:
        return ["尚未輸入資產金額。"]

    # 1) 集中度
    df_sorted = df.sort_values("金額", ascending=False)
    top1 = df_sorted.iloc[0]
    if top1["金額"] / df["金額"].sum() >= 0.5:
        tips.append(f"「{top1['資產類別']}」占比超過 50%，集中風險較高，建議規劃流動性備援。")

    # 2) 流動性（假設：不動產＋公司股權較不易變現）
    illiq = df.set_index("資產類別").loc[["不動產", "公司股權"], "金額"].sum()
    if illiq / df["金額"].sum() >= 0.5:
        tips.append("不動產＋公司股權超過 50%，可能影響稅源與緊急現金流，建議配置保單流動性或分散。")

    # 3) 現金流率過低
    low_flow = df["年現金流"].sum() / (df["金額"].sum() + 1e-9)
    if low_flow < 0.01:
        tips.append("整體年化現金流率 < 1%，在通膨環境下恐不足以支撐家族現金流需求，可再優化收益/結構。")

    # 4) 海外資產占比提醒
    try:
        over = df.set_index("資產類別").loc["海外資產", "金額"]
        if over / df["金額"].sum() >= 0.3:
            tips.append("海外資產占比 ≥ 30%，留意跨境稅務與申報（含匯回、受益人與信託安排）。")
    except Exception:
        pass

    if not tips:
        tips.append("目前未見明顯集中或流動性風險，後續可進一步做稅源預留與保單配置模擬。")
    return tips

if total_amt > 0:
    advices = risk_checks(df)
    for t in advices:
        st.markdown(f"✅ {t}")
else:
    st.info("輸入金額後，系統會自動產生建議。")

# ---- 產出 PDF ----
st.markdown("---")
st.subheader("④ 匯出 PDF（含圖＋表）")

def make_pdf(df: pd.DataFrame, total_amt: int, total_cash: int, pie_fig):
    """以 reportlab 動態產生 PDF（含圓餅圖與表格）。"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.2*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = []

    # 標題
    story.append(Paragraph("傳承地圖（概覽報告）", styles["Title"]))
    story.append(Paragraph(f"產出日期：{date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # 總覽數字
    story.append(Paragraph(f"<b>總資產：</b> NT$ {total_amt:,.0f}　｜　<b>預估年現金流：</b> NT$ {total_cash:,.0f}", styles["Heading3"]))
    story.append(Spacer(1, 0.3*cm))

    # 圓餅圖存成圖片插入
    img_buf = io.BytesIO()
    pie_fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=200)
    img_buf.seek(0)
    story.append(Image(img_buf, width=12*cm, height=12*cm))
    story.append(Spacer(1, 0.3*cm))

    # 表格
    tbl_data = [["資產類別", "金額", "占比(%)", "現金流率(%)", "年現金流"]]
    df_tab = df.copy()
    df_tab["占比(%)"] = (df_tab["金額"] / (total_amt or 1) * 100).round(1)
    for _, r in df_tab.iterrows():
        tbl_data.append([r["資產類別"], f"{int(r['金額']):,}", f"{r['占比(%)']:.1f}", f"{r['現金流率(%)']:.2f}", f"{int(r['年現金流']):,}"])

    tbl = Table(tbl_data, hAlign="LEFT", colWidths=[3.5*cm, 3.2*cm, 2.5*cm, 3.0*cm, 3.2*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # 建議
    tips = risk_checks(df)
    story.append(Paragraph("<b>系統建議：</b>", styles["Heading3"]))
    for t in tips:
        story.append(Paragraph(f"• {t}", styles["Normal"]))

    doc.build(story)
    pdf_data = buf.getvalue()
    buf.close()
    return pdf_data

# 重新繪製乾淨的圓餅圖給 PDF 用（避免上面的渲染造成 DPI 或邊界問題）
def draw_pie_for_pdf(df: pd.DataFrame):
    fig2, ax2 = plt.subplots(figsize=(5,5))
    labels2 = df["資產類別"].tolist()
    values2 = df["金額"].tolist()
    autopct_fmt2 = lambda p: f"{p:.1f}%" if p > 0 else ""
    ax2.pie(values2, labels=labels2, autopct=autopct_fmt2, startangle=90)
    ax2.axis("equal")
    return fig2

if total_amt > 0:
    pdf_fig = draw_pie_for_pdf(df)
    pdf_bytes = make_pdf(df, total_amt, total_cash, pdf_fig)
    st.download_button(
        "⬇️ 下載 PDF 報告",
        data=pdf_bytes,
        file_name=f"傳承地圖_{date.today().isoformat()}.pdf",
        mime="application/pdf",
    )
else:
    st.warning("請先輸入資產金額，再匯出 PDF。")
