# legacy_tools/modules/pdf_generator.py
# 升級版：統一品牌抬頭 + 中文字型（讀 brand.json & NotoSansTC）+ 可選 logo 與 QR Code
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

# ---- 讀取品牌設定 ----
def _load_brand():
    for p in [
        os.path.join(os.getcwd(), "brand.json"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "brand.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "brand.json")),
    ]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {"brand_name": "永傳家族辦公室", "slogan": "傳承您的影響力"}

# ---- 找字型/Logo/QRCode ----
def _find_font():
    for p in [
        os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
        os.path.join(os.getcwd(), "pages", "NotoSansTC-Regular.ttf"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "NotoSansTC-Regular.ttf")),
        "NotoSansTC-Regular.ttf",
    ]:
        if os.path.exists(p):
            return p
    return None

def _find_image_by_names(names):
    for name in names:
        p = os.path.join(os.getcwd(), name)
        if os.path.exists(p):
            return p
    return None

def _find_logo():
    return _find_image_by_names(["logo.png", "logo.jpg", "logo.jpeg"])

def _find_qrcode():
    return _find_image_by_names(["qrcode.png", "qrcode.jpg", "qrcode.jpeg"])

# ---- 樣式 ----
def _styles():
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

# ---- 公用：品牌抬頭（含可選 logo 與 QRCode）----
def _brand_header(story, styleTitle, styleSlogan, styleC):
    brand = _load_brand()
    brand_name = brand.get("brand_name", "永傳家族辦公室")
    slogan = brand.get("slogan", "傳承您的影響力")
    logo = _find_logo()
    qrcode = _find_qrcode()

    if logo:
        img = Image(logo, width=80*mm, height=20*mm)
        img.hAlign = "CENTER"; story.append(img); story.append(Spacer(1, 6))
    story.append(Paragraph(brand_name, styleTitle))
    story.append(Paragraph(slogan, styleSlogan))
    story.append(Paragraph(f"產出日期：{date.today().isoformat()}", styleC))
    story.append(Spacer(1, 6))

    # 如果有 QRCode（例如預約連結），附在抬頭下方右側
    if qrcode:
        qr = Image(qrcode, width=28*mm, height=28*mm)
        qr.hAlign = "RIGHT"; story.append(qr)
        story.append(Paragraph("掃描 QR 預約諮詢", styleC))
    story.append(Spacer(1, 6))

# =========================
# 1) 探索紀錄 PDF（沿用 generate_pdf）
# =========================
def generate_pdf():
    buf = BytesIO()
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    story.append(Paragraph("探索紀錄摘要", styleH))
    story.append(Spacer(1, 6))

    # 依現有 session_state 欄位輸出（若無則跳過）
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

# =========================
# 2) 資產地圖 PDF
# =========================
def generate_asset_map_pdf(labels, values, suggestions, chart_image_bytes):
    buf = BytesIO()
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    total = sum(values) if values else 0
    data = [["資產類別", "金額（萬元）", "佔比"]]
    for label, val in zip(labels, values):
        pct = f"{(val / total * 100):.1f}%" if total > 0 else "0.0%"
        data.append([label, f"{val:,.0f}", pct])
    if total > 0:
        data.append(["總資產", f"{total:,.0f}", "100.0%"])

    table = Table(data, colWidths=[60*mm, 50*mm, 30*mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "NotoSansTC" if _find_font() else "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 12),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    story.append(Paragraph("資產分布明細", styleH))
    story.append(table)
    story.append(Spacer(1, 10))

    if chart_image_bytes:
        story.append(Paragraph("資產結構圖", styleH))
        chart = Image(chart_image_bytes, width=150*mm, height=150*mm)
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

# =========================
# 3) 保單策略 PDF
# =========================
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
            name = s.get("name", "策略")
            why = s.get("why", "")
            fit = ", ".join(s.get("fit", []))
            desc = s.get("description", "")
            story.append(Paragraph(f"【{name}】", styleN))
            if why:  story.append(Paragraph(f"理由：{why}", styleN))
            if fit:  story.append(Paragraph(f"適合對象：{fit}", styleN))
            if desc: story.append(Paragraph(f"結構說明：{desc}", styleN))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))
    story.append(Paragraph("下一步：若這份策略讓您浮現了想法，歡迎預約對談，讓保單成為資產任務的助手。", styleN))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))

    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buf.seek(0)
    return buf
