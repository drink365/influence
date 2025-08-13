# legacy_tools/modules/pdf_generator.py
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
import os, json

# --------------------
# 輔助函式
# --------------------
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
    # 支援多檔名（含你的 logo-橫式彩色.png）
    return _find_image_by_names(["logo-橫式彩色.png", "logo.png", "logo.jpg", "logo.jpeg"])

def _find_qrcode():
    return _find_image_by_names(["qrcode.png", "qrcode.jpg", "qrcode.jpeg"])

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

def _brand_header(story, styleTitle, styleSlogan, styleC):
    brand = _load_brand()
    brand_name = brand.get("brand_name", "永傳家族辦公室")
    slogan = brand.get("slogan", "傳承您的影響力")
    logo = _find_logo()
    qrcode = _find_qrcode()

    if logo:
        img = Image(logo, width=80*mm, height=20*mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 6))
    story.append(Paragraph(brand_name, styleTitle))
    story.append(Paragraph(slogan, styleSlogan))
    story.append(Paragraph(f"產出日期：{date.today().isoformat()}", styleC))
    story.append(Spacer(1, 6))
    if qrcode:
        qr = Image(qrcode, width=28*mm, height=28*mm)
        qr.hAlign = "RIGHT"
        story.append(qr)
        story.append(Paragraph("掃描 QR 預約諮詢", styleC))
    story.append(Spacer(1, 6))

# --------------------
# 1) 通用 PDF（例如 AI 行銷助手）
# --------------------
def generate_pdf(content: str, title: str = "報告", filename: str = "output.pdf"):
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)
    story.append(Paragraph(title, styleH))
    story.append(Spacer(1, 6))
    for para in content.split("\n"):
        if para.strip() == "":
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(para, styleN))
    doc.build(story)
    buf.seek(0)
    return buf

# --------------------
# 2) 傳承地圖 PDF
# --------------------
def generate_asset_map_pdf(asset_data: dict, chart_path: str = None, table_data: list = None, filename: str = "asset_map.pdf"):
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)
    story.append(Paragraph("傳承地圖", styleH))

    # 資產餅圖
    if chart_path and os.path.exists(chart_path):
        img = Image(chart_path, width=14*cm, height=10*cm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 6))

    # 資產表格
    if table_data:
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), styleN.fontName),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(t)

    doc.build(story)
    buf.seek(0)
    return buf

# --------------------
# 3) 保單策略 PDF
# --------------------
def generate_insurance_strategy_pdf(strategy_text: str, chart_path: str = None, filename: str = "insurance_strategy.pdf"):
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)
    story.append(Paragraph("保單策略建議", styleH))

    # 圖表
    if chart_path and os.path.exists(chart_path):
        img = Image(chart_path, width=14*cm, height=10*cm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 6))

    # 策略文字
    for para in strategy_text.split("\n"):
        if para.strip() == "":
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(para, styleN))

    doc.build(story)
    buf.seek(0)
    return buf
