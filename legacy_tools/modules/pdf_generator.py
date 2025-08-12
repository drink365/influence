# legacy_tools/modules/pdf_generator.py
# 升級版：統一品牌抬頭 + 中文字型（讀取根目錄 brand.json & NotoSansTC-Regular.ttf）
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from datetime import date
import streamlit as st
import os, json

# -----------------------------
# 設定：尋找品牌設定與字型/Logo
# -----------------------------
def _load_brand():
    try_paths = []
    # 頁面子資料夾 → 專案根目錄 brand.json
    base = os.getcwd()
    try_paths += [
        os.path.join(base, "brand.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "brand.json"),
        os.path.join(os.path.dirname(__file__), "..", "brand.json"),
    ]
    for p in try_paths:
        p = os.path.abspath(p)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {"brand_name": "永傳家族辦公室", "slogan": "傳承您的影響力"}

def _find_font():
    # 優先找 repo 根目錄與 pages/ 下的 NotoSansTC-Regular.ttf
    candidates = [
        os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
        os.path.join(os.getcwd(), "pages", "NotoSansTC-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "..", "NotoSansTC-Regular.ttf"),
        "NotoSansTC-Regular.ttf",
    ]
    for p in candidates:
        p = os.path.abspath(p)
        if os.path.exists(p):
            return p
    return None

def _find_logo():
    # 可選的 logo（若沒上傳就忽略）
    for name in ["logo.png", "logo.jpg", "logo.jpeg"]:
        p = os.path.join(os.getcwd(), name)
        if os.path.exists(p):
            return p
    return None

def _styles():
    # 註冊字型（若找不到則 fallback）
    font_path = _find_font()
    font_name = "Helvetica"
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("NotoSansTC", font_path))
            font_name = "NotoSansTC"
        except Exception:
            pass

    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(name="NormalTC", parent=styles["Normal"], fontName=font_name, fontSize=12, leading=16)
    styleH = ParagraphStyle(name="HeadingTC", parent=styles["Heading2"], fontName=font_name, fontSize=14, leading=18, spaceAfter=10)
    styleC = ParagraphStyle(name="CenterTC", parent=styles["Normal"], fontName=font_name, fontSize=10, alignment=TA_CENTER)
    styleTitle = ParagraphStyle(name="BrandTitle", parent=styles["Title"], fontName=font_name, fontSize=20, leading=24, spaceAfter=4)
    styleSlogan = ParagraphStyle(name="BrandSlogan", parent=styles["Normal"], fontName=font_name, fontSize=11, textColor=colors.grey)
    return styleN, styleH, styleC, styleTitle, styleSlogan

def _brand_header(story, styleTitle, styleSlogan, styleC):
    brand = _load_brand()
    brand_name = brand.get("brand_name", "永傳家族辦公室")
    slogan = brand.get("slogan", "傳承您的影響力")
    logo = _find_logo()
    if logo:
        img = Image(logo, width=80 * mm, height=20 * mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 6))
    story.append(Paragraph(brand_name, styleTitle))
    story.append(Paragraph(slogan, styleSlogan))
    story.append(Paragraph(f"產出日期：{date.today().isoformat()}", styleC))
    story.append(Spacer(1, 10))

# -----------------------------
# 1) 《探索紀錄》PDF（原 generate_pdf）
# 依賴 st.session_state 的多段內容
# -----------------------------
def generate_pdf():
    buf = BytesIO()
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()

    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    story.append(Paragraph("探索紀錄摘要", styleH))
    story.append(Spacer(1, 6))

    # 以下保持原本 st.session_state 欄位名稱不變（若沒有則略過顯示）
    if "legacy_style_result" in st.session_state:
        txt = st.session_state.legacy_style_result
        txt = txt.replace("❤️", "").replace("💼", "").replace("🧭", "")
        story.append(Paragraph("您的傳承風格：", styleH))
        story.append(Paragraph(txt, styleN))
        story.append(Spacer(1, 6))

    if "key_issues" in st.session_state:
        story.append(Paragraph("模組二：您最在意的重點", styleH))
        for issue in st.session_state.key_issues:
            story.append(Paragraph(f"• {issue}", styleN))
        if st.session_state.get("reason"):
            story.append(Paragraph(f"原因：{st.session_state.reason}", styleN))
        story.append(Spacer(1, 6))

    if "directions" in st.session_state:
        story.append(Paragraph("模組三：您期望的未來方向", styleH))
        for d in st.session_state.directions:
            story.append(Paragraph(f"• {d}", styleN))
        if st.session_state.get("custom_direction"):
            story.append(Paragraph(f"補充：{st.session_state.custom_direction}", styleN))
        story.append(Spacer(1, 6))

    story.append(Paragraph("對談前的思考引導", styleH))
    for line in [
        "1. 如果我今天退休，最擔心的事情是什麼？",
        "2. 我希望未來家人如何記得我？",
        "3. 有沒有什麼，是我現在就可以決定、啟動的？",
    ]:
        story.append(Paragraph(line, styleN))

    story.append(Spacer(1, 12))
    story.append(Paragraph("下一步：若這份紀錄讓您浮現了願景，邀請您預約對談，一起為未來鋪路。", styleN))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))

    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buf.seek(0)
    return buf

# -----------------------------
# 2) 資產地圖 PDF（原 generate_asset_map_pdf）
# -----------------------------
def generate_asset_map_pdf(labels, values, suggestions, chart_image_bytes):
    buf = BytesIO()
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()

    total = sum(values) if values else 0
    data = [["資產類別", "金額（萬元）", "佔比"]]
    for label, val in zip(labels, values):
        pct = f"{(val / total * 100):.1f}%" if total > 0 else "0.0%"
        data.append([label, f"{val:,.0f}", pct])
    if total > 0:
        data.append(["總資產", f"{total:,.0f}", "100.0%"])

    table = Table(data, colWidths=[60 * mm, 50 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), styleN.fontName),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    story.append(Paragraph("資產分布明細", styleH))
    story.append(table)
    story.append(Spacer(1, 10))

    if chart_image_bytes:
        story.append(Paragraph("資產結構圖", styleH))
        chart = Image(chart_image_bytes, width=150 * mm, height=150 * mm)
        chart.hAlign = "CENTER"
        story.append(chart)
        story.append(Spacer(1, 10))

    story.append(Paragraph("系統建議摘要", styleH))
    if suggestions:
        for s in suggestions:
            s_clean = s.translate({ord(c): None for c in "📌🏢🏠💵🌐🔒👍"}).strip()
            story.append(Paragraph(f"• {s_clean}", styleN))
    else:
        story.append(Paragraph("目前資產結構整體平衡，仍建議定期檢視傳承架構與稅源預備狀況。", styleN))

    story.append(Spacer(1, 8))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))

    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buf.seek(0)
    return buf

# -----------------------------
# 3) 保單策略 PDF（原 generate_insurance_strategy_pdf）
# -----------------------------
def generate_insurance_strategy_pdf(age, gender, budget, currency, pay_years, goals, strategies):
    buf = BytesIO()
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()

    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    story.append(Paragraph("保單策略建議（概要）", styleH))
    story.append(Paragraph(f"年齡：{age}　性別：{gender}　預算：{currency}{budget:,}　繳費年期：{pay_years} 年", styleN))

    if goals:
        story.append(Spacer(1, 4))
        story.append(Paragraph("目標：", styleH))
        for g in goals:
            story.append(Paragraph(f"• {g}", styleN))

    if strategies:
        story.append(Spacer(1, 6))
        story.append(Paragraph("初步策略建議：", styleH))
        for s in strategies:
            # 預期結構：{"name":..., "why":..., "fit":[...], "description":...}
            name = s.get("name", "策略")
            why = s.get("why", "")
            fit = ", ".join(s.get("fit", []))
            desc = s.get("description", "")
            story.append(Paragraph(f"【{name}】", styleN))
            if why:  story.append(Paragraph(f"理由：{why}", styleN))
            if fit:  story.append(Paragraph(f"適合對象：{fit}", styleN))
            if desc: story.append(Paragraph(f"結構說明：{desc}", styleN))
            st
