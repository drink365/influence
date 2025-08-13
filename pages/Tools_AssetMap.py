# pages/Tools_AssetMap.py
# 🗺️ 傳承地圖｜完整版（六大資產＋現金流＋PDF 匯出）
# 本版升級：PDF 自動讀取 brand.json（brand_name / slogan），顯示品牌抬頭

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io, os, json
from datetime import date

st.set_page_config(page_title="傳承地圖｜完整版", page_icon="🗺️", layout="wide")
st.title("🗺️ 傳承地圖｜完整版")
st.caption("輸入六大資產分布與現金流率，系統生成圓餅圖、現金流表與建議，並可一鍵匯出 PDF（含品牌抬頭）。")

# ---------- 讀取 brand.json（根目錄） ----------
def load_brand():
    try_paths = []
    this_dir = os.path.dirname(__file__)
    try_paths.append(os.path.abspath(os.path.join(this_dir, "..", "brand.json")))
    try_paths.append(os.path.abspath(os.path.join(this_dir, "..", "..", "brand.json")))
    try_paths.append(os.path.abspath(os.path.join(os.getcwd(), "brand.json")))
    for p in try_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {"brand_name": "永傳家族辦公室", "slogan": "傳承您的影響力"}

BRAND = load_brand()

# ---------- 中文字型（有 NotoSansTC-Regular.ttf 就啟用；沒有也可用） ----------
try:
    import matplotlib
    font_path = os.path.join(os.path.dirname(__file__), "..", "NotoSansTC-Regular.ttf")
    if os.path.exists(font_path):
        matplotlib.font_manager.fontManager.addfont(font_path)
        plt.rcParams["font.sans-serif"] = ["Noto Sans TC"]
        plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass

# ---------- 六大資產分類 ----------
ASSET_CATEGORIES = [
    {"key": "equity", "label": "公司股權", "default_rate": 2.0},
    {"key": "realty", "label": "不動產", "default_rate": 2.0},
    {"key": "financial", "label": "金融資產", "default_rate": 3.0},
    {"key": "policy", "label": "保單", "default_rate": 2.5},
    {"key": "overseas", "label": "海外資產", "default_rate": 2.0},
    {"key": "others", "label": "其他資產", "default_rate": 0.5},
]

# ---------- 輸入區 ----------
st.subheader("① 請輸入資產分布與現金流假設")
cols_amt = st.columns(3)
cols_rate = st.columns(3)
rows = []
for i, cat in enumerate(ASSET_CATEGORIES):
    with cols_amt[i % 3]:
        amt = st.number_input(cat["label"], min_value=0, value=0, step=100000, key=f"amt_{cat['key']}")
    with cols_rate[i % 3]:
        rate = st.number_input(f"{cat['label']} 現金流率(%)", min_value=0.0, value=float(cat["default_rate"]), step=0.1, key=f"rate_{cat['key']}")
    cash = round(amt * rate / 100.0)
    rows.append({"資產類別": cat["label"], "金額": amt, "現金流率(%)": rate, "年現金流": cash})

df = pd.DataFrame(rows)
total_amt = int(df["金額"].sum())
total_cash = int(df["年現金流"].sum())

st.markdown("---")
st.subheader("② 視覺化總覽")

# ---------- 圓餅圖 ----------
if total_amt == 0:
    st.info("請先輸入各資產類別的金額數值。")
else:
    fig, ax = plt.subplots(figsize=(5,5))
    labels = df["資產類別"].tolist()
    values = df["金額"].tolist()
    autopct_fmt = lambda p: f"{p:.1f}%" if p > 0 else ""
    ax.pie(values, labels=labels, autopct=autopct_fmt, startangle=90)
    ax.axis("equal")
    st.pyplot(fig, use_container_width=False)

    st.markdown(f"**總資產**：NT$ {total_amt:,.0f}　｜　**預估年現金流**：NT$ {total_cash:,.0f}")

    st.markdown("### 現金流明細")
    df_show = df.copy()
    df_show["占比(%)"] = (df_show["金額"] / total_amt * 100).round(1)
    st.dataframe(df_show, use_container_width=True)

# ---------- 風險偵測與建議 ----------
st.markdown("---")
st.subheader("③ 風險偵測與建議（自動）")

def risk_checks(df: pd.DataFrame):
    tips = []
    if df["金額"].sum() <= 0:
        return ["尚未輸入資產金額。"]

    # 集中度（單一類別 >=50%）
    df_sorted = df.sort_values("金額", ascending=False)
    top1 = df_sorted.iloc[0]
    if top1["金額"] / df["金額"].sum() >= 0.5:
        tips.append(f"「{top1['資產類別']}」占比超過 50%，集中風險較高，建議規劃流動性備援。")

    # 流動性（不動產＋公司股權 >=50%）
    illiq = df.set_index("資產類別").loc[["不動產", "公司股權"], "金額"].sum()
    if illiq / df["金額"].sum() >= 0.5:
        tips.append("不動產＋公司股權占比 ≥ 50%，可能影響稅源與緊急現金流，建議配置保單流動性或分散。")

    # 整體現金流率 <1%
    low_flow = df["年現金流"].sum() / (df["金額"].sum() + 1e-9)
    if low_flow < 0.01:
        tips.append("整體年化現金流率 < 1%，在通膨環境下恐不足以支撐需求，可再優化收益/結構。")

    # 海外資產提醒
    if "海外資產" in df["資產類別"].values:
        over = df.set_index("資產類別").loc["海外資產", "金額"]
        if over / df["金額"].sum() >= 0.3:
            tips.append("海外資產占比 ≥ 30%，留意跨境稅務與申報（含匯回、受益人與信託安排）。")

    if not tips:
        tips.append("目前未見明顯集中或流動性風險，後續可進一步做稅源預留與保單配置模擬。")
    return tips

if total_amt > 0:
    for t in risk_checks(df):
        st.markdown(f"✅ {t}")
else:
    st.info("輸入金額後，系統會自動產生建議。")

# ---------- PDF 匯出（含品牌抬頭） ----------
st.markdown("---")
st.subheader("④ 匯出 PDF（含圖＋表＋品牌抬頭）")

def draw_pie_for_pdf(df: pd.DataFrame):
    fig2, ax2 = plt.subplots(figsize=(5,5))
    labels2 = df["資產類別"].tolist()
    values2 = df["金額"].tolist()
    autopct_fmt2 = lambda p: f"{p:.1f}%" if p > 0 else ""
    ax2.pie(values2, labels=labels2, autopct=autopct_fmt2, startangle=90)
    ax2.axis("equal")
    return fig2

def make_pdf(df: pd.DataFrame, total_amt: int, total_cash: int, pie_fig, brand: dict):
    """以 reportlab 產生 PDF（含品牌抬頭、圓餅圖與表格）"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.2*cm, leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    styles = getSampleStyleSheet()

    # 標題樣式
    brand_style = ParagraphStyle(
        "BrandHead", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=4
    )
    slogan_style = ParagraphStyle(
        "Slogan", parent=styles["Normal"], fontName="Helvetica", fontSize=11, textColor=colors.grey, spaceAfter=10
    )

    story = []
    brand_name = brand.get("brand_name", "永傳家族辦公室")
    slogan = brand.get("slogan", "傳承您的影響力")

    story.append(Paragraph(brand_name, brand_style))
    story.append(Paragraph(slogan, slogan_style))
    story.append(Paragraph("傳承地圖（概覽報告）", styles["Title"]))
    story.append(Paragraph(f"產出日期：{date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # 總覽數字
    story.append(Paragraph(f"<b>總資產：</b> NT$ {total_amt:,.0f}　｜　<b>預估年現金流：</b> NT$ {total_cash:,.0f}", styles["Heading3"]))
    story.append(Spacer(1, 0.3*cm))

    # 圓餅圖存為圖片插入
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
        tbl_data.append([
            r["資產類別"],
            f"{int(r['金額']):,}",
            f"{r['占比(%)']:.1f}",
            f"{r['現金流率(%)']:.2f}",
            f"{int(r['年現金流']):,}"
        ])
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
    tips = []
    # 重用畫面上的邏輯（簡化重寫）
    df_tmp = df.copy()
    if df_tmp["金額"].sum() > 0:
        df_sorted = df_tmp.sort_values("金額", ascending=False)
        top1 = df_sorted.iloc[0]
        if top1["金額"] / df_tmp["金額"].sum() >= 0.5:
            tips.append(f"「{top1['資產類別']}」占比超過 50%，集中風險較高，建議規劃流動性備援。")
        illiq = df_tmp.set_index("資產類別").loc[["不動產", "公司股權"], "金額"].sum()
        if illiq / df_tmp["金額"].sum() >= 0.5:
            tips.append("不動產＋公司股權占比 ≥ 50%，可能影響稅源與緊急現金流，建議配置保單流動性或分散。")
        low_flow = df_tmp["年現金流"].sum() / (df_tmp["金額"].sum() + 1e-9)
        if low_flow < 0.01:
            tips.append("整體年化現金流率 < 1%，在通膨環境下恐不足以支撐需求，可再優化收益/結構。")
        if "海外資產" in df_tmp["資產類別"].values:
            over = df_tmp.set_index("資產類別").loc["海外資產", "金額"]
            if over / df_tmp["金額"].sum() >= 0.3:
                tips.append("海外資產占比 ≥ 30%，留意跨境稅務與申報（含匯回、受益人與信託安排）。")
    if not tips:
        tips.append("目前未見明顯集中或流動性風險，後續可進一步做稅源預留與保單配置模擬。")

    from reportlab.platypus import Paragraph
    story.append(Paragraph("<b>系統建議：</b>", styles["Heading3"]))
    for t in tips:
        story.append(Paragraph(f"• {t}", styles["Normal"]))

    doc.build(story)
    pdf_data = buf.getvalue()
    buf.close()
    return pdf_data

if total_amt > 0:
    fig_pdf = draw_pie_for_pdf(df)
    pdf_bytes = make_pdf(df, total_amt, total_cash, fig_pdf, BRAND)
    st.download_button(
        "⬇️ 下載 PDF 報告（含品牌抬頭）",
        data=pdf_bytes,
        file_name=f"傳承地圖_{date.today().isoformat()}.pdf",
        mime="application/pdf",
    )
else:
    st.warning("請先輸入資產金額，再匯出 PDF。")
