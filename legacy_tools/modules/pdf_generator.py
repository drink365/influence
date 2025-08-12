from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib import colors
import streamlit as st

def generate_pdf():
    buffer = BytesIO()
    logo_path = "logo.png"
    font_path = "NotoSansTC-Regular.ttf"

    pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
    styleN = ParagraphStyle(name='Normal', fontName='NotoSansTC', fontSize=12)
    styleH = ParagraphStyle(name='Heading2', fontName='NotoSansTC', fontSize=14, spaceAfter=10)
    styleC = ParagraphStyle(name='Center', fontName='NotoSansTC', fontSize=10, alignment=TA_CENTER)

    story = []
    logo = Image(logo_path, width=80 * mm, height=20 * mm)
    logo.hAlign = 'CENTER'
    story.append(logo)
    story.append(Spacer(1, 6))
    story.append(Paragraph("傳承您的影響力", styleC))
    story.append(Paragraph("每一位家族的掌舵者，都是家族傳承的種子。", styleC))
    story.append(Paragraph("我們陪您，讓這份影響力持續茁壯。", styleC))
    story.append(Spacer(1, 24))

    story.append(Paragraph("探索紀錄摘要", styleH))
    story.append(Spacer(1, 20))

    if "legacy_style_result" in st.session_state:
        story.append(Paragraph("您的傳承風格：", styleH))
        story.append(Paragraph(st.session_state.legacy_style_result.replace("❤️", "").replace("💼", "").replace("🧭", ""), styleN))
        story.append(Spacer(1, 12))

    if "key_issues" in st.session_state:
        story.append(Paragraph("模組二：您最在意的重點", styleH))
        for issue in st.session_state.key_issues:
            story.append(Paragraph(f"• {issue}", styleN))
        if st.session_state.get("reason"):
            story.append(Paragraph(f"原因：{st.session_state.reason}", styleN))
        story.append(Spacer(1, 12))

    if "directions" in st.session_state:
        story.append(Paragraph("模組三：您期望的未來方向", styleH))
        for d in st.session_state.directions:
            story.append(Paragraph(f"• {d}", styleN))
        if st.session_state.get("custom_direction"):
            story.append(Paragraph(f"補充：{st.session_state.custom_direction}", styleN))
        story.append(Spacer(1, 12))

    story.append(Paragraph("對談前的思考引導", styleH))
    story.append(Paragraph("這三個問題，邀請您在心中停留片刻：", styleN))
    story.append(Paragraph("1. 如果我今天退休，最擔心的事情是什麼？", styleN))
    story.append(Paragraph("2. 我希望未來家人如何記得我？", styleN))
    story.append(Paragraph("3. 有沒有什麼，是我現在就可以決定、啟動的？", styleN))
    story.append(Spacer(1, 20))

    story.append(Paragraph("下一步，我們可以一起完成", styleH))
    story.append(Paragraph("如果這份紀錄讓您浮現了願景，我們誠摯邀請您預約對談，一起為未來鋪路。", styleN))
    story.append(Spacer(1, 12))
    story.append(Spacer(1, 6))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))
    story.append(Paragraph("聯絡信箱：123@gracefo.com", styleC))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_asset_map_pdf(labels, values, suggestions, chart_image_bytes):
    buffer = BytesIO()
    logo_path = "logo.png"
    font_path = "NotoSansTC-Regular.ttf"

    pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
    styleN = ParagraphStyle(name='Normal', fontName='NotoSansTC', fontSize=12)
    styleH = ParagraphStyle(name='Heading2', fontName='NotoSansTC', fontSize=14, spaceAfter=10)
    styleC = ParagraphStyle(name='Center', fontName='NotoSansTC', fontSize=10, alignment=TA_CENTER)

    total = sum(values)
    data = [["資產類別", "金額（萬元）", "佔比"]]
    for label, val in zip(labels, values):
        pct = f"{(val / total * 100):.1f}%" if total > 0 else "0.0%"
        data.append([label, f"{val:,.0f}", pct])
    data.append(["總資產", f"{total:,.0f}", "100.0%"])

    table = Table(data, colWidths=[60 * mm, 50 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "NotoSansTC"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
    ]))

    story = []
    story.append(Image(logo_path, width=80 * mm, height=20 * mm))
    story.append(Spacer(1, 12))
    story.append(Paragraph("《影響力》傳承策略平台｜資產結構與風險建議報告", styleC))
    story.append(Spacer(1, 18))
    story.append(Paragraph("資產分布明細", styleH))
    story.append(table)
    story.append(Spacer(1, 18))

    if any(val > 0 for val in values):
        story.append(Paragraph("資產結構圖", styleH))
        chart = Image(chart_image_bytes, width=150 * mm, height=150 * mm)
        chart.hAlign = "CENTER"
        story.append(chart)
        story.append(Spacer(1, 18))

    story.append(Paragraph("系統建議摘要", styleH))
    if suggestions:
        for s in suggestions:
            s_clean = s.translate({ord(c): None for c in "📌🏢🏠💵🌐🔒👍"}).strip()
            story.append(Paragraph(f"• {s_clean}", styleN))
    else:
        story.append(Paragraph("目前資產結構整體平衡，仍建議定期檢視傳承架構與稅源預備狀況。", styleN))

    story.append(Spacer(1, 20))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))
    story.append(Paragraph("聯絡信箱：123@gracefo.com", styleC))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_insurance_strategy_pdf(age, gender, budget, currency, pay_years, goals, strategies):
    buffer = BytesIO()
    logo_path = "logo.png"
    font_path = "NotoSansTC-Regular.ttf"

    pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
    styleN = ParagraphStyle(name='Normal', fontName='NotoSansTC', fontSize=12)
    styleH = ParagraphStyle(name='Heading2', fontName='NotoSansTC', fontSize=14, spaceAfter=10)
    styleC = ParagraphStyle(name='Center', fontName='NotoSansTC', fontSize=10, alignment=TA_CENTER)

    story = []
    story.append(Image(logo_path, width=80 * mm, height=20 * mm))
    story.append(Spacer(1, 12))
    story.append(Paragraph("《影響力》傳承策略平台｜保單策略建議摘要", styleC))
    story.append(Spacer(1, 18))

    story.append(Paragraph("基本資料", styleH))
    story.append(Paragraph(f"年齡：{age} 歲　性別：{gender}　預算：約 {budget:,} 萬元（{currency}）　繳費年期：{pay_years}", styleN))
    story.append(Paragraph(f"規劃目標：{'、'.join(goals)}", styleN))
    story.append(Spacer(1, 18))

    story.append(Paragraph("建議策略組合", styleH))
    for s in strategies:
        story.append(Paragraph(f"策略名稱：{s['name']}", styleN))
        story.append(Paragraph(f"適合目標：{'、'.join(s['matched_goals'])}", styleN))
        story.append(Paragraph(f"結構說明：{s['description']}", styleN))
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 18))
    story.append(Paragraph("下一步，我們可以一起完成", styleH))
    story.append(Paragraph("如果這份策略讓您浮現了想法，我們誠摯邀請您預約對談，讓保單成為資產任務的最佳助手。", styleN))
    story.append(Spacer(1, 12))
    story.append(Paragraph("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com", styleC))
    story.append(Paragraph("聯絡信箱：123@gracefo.com", styleC))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build(story)
    buffer.seek(0)
    return buffer
