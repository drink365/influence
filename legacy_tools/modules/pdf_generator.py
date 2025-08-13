# legacy_tools/modules/pdf_generator.py
# 統一 PDF 引擎（品牌抬頭 + Noto 中文字型 + Logo/QRCode）
# ✅ 新增：emoji 安全轉換（避免 PDF 顯示方框）
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
import os, json, re

# --------------------
# 讀取品牌設定 / 字型 / 圖檔
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
    # 支援你的檔名 'logo-橫式彩色.png' 與常見檔名
    return _find_image_by_names(["logo-橫式彩色.png", "logo.png", "logo.jpg", "logo.jpeg"])

def _find_qrcode():
    return _find_image_by_names(["qrcode.png", "qrcode.jpg", "qrcode.jpeg"])

# --------------------
# Emoji 安全轉換（避免 PDF 缺字）
# --------------------
_EMOJI_MAP = {
    "💡": "(重點)",
    "👉": "→",
    "🌱": "(一起前進)",
    "🧮": "(遺產稅)",
    "🗺️": "(傳承地圖)",
    "📦": "(策略)",
    "🪄": "(小幫手)",
    "📅": "(預約)",
    "📝": "(筆記)",
    "✨": "",
    "❤️": "",
    "👍": "",
    "🔒": "",
    "💼": "",
    "🧭": "",
}

# 粗略抓取 emoji 的範圍（如遇未知 emoji，就移除）
_EMOJI_RE = re.compile(
    "["                     # 以下為常見 emoji 區段
    "\U0001F300-\U0001F6FF" # pictographs, transport, etc.
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002700-\U000027BF" # Dingbats
    "\U00002600-\U000026FF" # Misc symbols
    "]",
    flags=re.UNICODE
)

def _sanitize_emoji(text: str) -> str:
    if not text:
        return text
    # 先做常用替換
    for k, v in _EMOJI_MAP.items():
        if k in text:
            text = text.replace(k, v)
    # 再移除其餘無對應的 emoji，避免 PDF 出現方框
    text = _EMOJI_RE.sub("", text)
    return text

# --------------------
# 樣式 & 品牌抬頭
# --------------------
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
    brand_name = _sanitize_emoji(brand.get("brand_name", "永傳家族辦公室"))
    slogan = _sanitize_emoji(brand.get("slogan", "傳承您的影響力"))
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
# 1) 通用 PDF（AI 助手 / 任意文字）
#   - 向下相容：若未傳 content，會從 st.session_state 組「探索紀錄」
# --------------------
def generate_pdf(content: str = None, title: str = "報告", filename: str = "output.pdf"):
    try:
        import streamlit as st
    except Exception:
        st = None

    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)

    # 情境 A：傳入 content（AI 助手）
    if content is not None:
        story.append(Paragraph(_sanitize_emoji(title or "報告"), styleH))
        story.append(Spacer(1, 6))
        for para in (content or "").split("\n"):
            para = _sanitize_emoji(para)
            if para.strip() == "":
                story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(para, styleN))
        doc.build(story)
        buf.seek(0)
        return buf

    # 情境 B：未傳 content → 從 session_state 組「探索紀錄」（舊頁相容）
    story.append(Paragraph("探索紀錄摘要", styleH))
    story.append(Spacer(1, 6))
    if st is not None and "legacy_style_result" in st.session_state:
        txt = st.session_state.legacy_style_result
        txt = _sanitize_emoji(txt)
        story.append(Paragraph("您的傳承風格：", styleH))
        story.append(Paragraph(txt, styleN))
        story.append(Spacer(1, 6))

    if st is not None and "key_issues" in st.session_state:
        story.append(Paragraph("模組二：您最在意的重點", styleH))
        for issue in st.session_state.key_issues:
            story.append(Paragraph(_sanitize_emoji(f"• {issue}"), styleN))
        if st.session_state.get("reason"):
            story.append(Paragraph(_sanitize_emoji(f"原因：{st.session_state.reason}"), styleN))
        story.append(Spacer(1, 6))

    if st is not None and "directions" in st.session_state:
        story.append(Paragraph("模組三：您期望的未來方向", styleH))
        for d in st.session_state.directions:
            story.append(Paragraph(_sanitize_emoji(f"• {d}"), styleN))
        if st.session_state.get("custom_direction"):
            story.append(Paragraph(_sanitize_emoji(f"補充：{st.session_state.custom_direction}"), styleN))
        story.append(Spacer(1, 6))

    for line in [
        "1. 如果我今天退休，最擔心的事情是什麼？",
        "2. 我希望未來家人如何記得我？",
        "3. 有沒有什麼，是我現在就可以決定、啟動的？",
    ]:
        story.append(Paragraph(_sanitize_emoji(line), styleN))

    story.append(Spacer(1, 12))
    story.append(Paragraph(_sanitize_emoji("下一步：若這份紀錄讓您浮現了願景，邀請您預約對談，一起為未來鋪路。"), styleN))
    story.append(Paragraph(_sanitize_emoji("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com"), styleC))

    doc.build(story)
    buf.seek(0)
    return buf

# --------------------
# 2) 傳承地圖 PDF（雙介面相容）
#   A. generate_asset_map_pdf(labels, values, suggestions, chart_image_bytes)
#   B. generate_asset_map_pdf(asset_data=dict, chart_path=str, table_data=list)
# --------------------
def generate_asset_map_pdf(*args, **kwargs):
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)
    story.append(Paragraph("傳承地圖", styleH))

    # 介面 B：以命名參數傳入
    asset_data = kwargs.get("asset_data")
    chart_path = kwargs.get("chart_path")
    table_data = kwargs.get("table_data")
    if asset_data is not None or chart_path is not None or table_data is not None:
        if chart_path and os.path.exists(chart_path):
            img = Image(chart_path, width=14*cm, height=10*cm); img.hAlign = "CENTER"
            story.append(img); story.append(Spacer(1, 6))
        if table_data:
            # 先做 emoji 安全處理
            safe_table = [[_sanitize_emoji(str(c)) for c in row] for row in table_data]
            t = Table(safe_table)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), styleN.fontName),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            story.append(t)
        doc.build(story); buf.seek(0); return buf

    # 介面 A：舊介面（labels, values, suggestions, chart_image_bytes）
    labels, values, suggestions, chart_image_bytes = None, None, None, None
    if len(args) >= 2:
        labels, values = args[0], args[1]
    if len(args) >= 3:
        suggestions = args[2]
    if len(args) >= 4:
        chart_image_bytes = args[3]

    # 表格
    if labels and values:
        total = sum(values) if values else 0
        data = [["資產類別", "金額（萬元）", "佔比"]]
        for label, val in zip(labels, values):
            pct = f"{(val / total * 100):.1f}%" if total > 0 else "0.0%"
            data.append([_sanitize_emoji(str(label)), f"{val:,.0f}", pct])
        if total > 0:
            data.append(["總資產", f"{total:,.0f}", "100.0%"])
        t = Table(data, colWidths=[60*mm, 50*mm, 30*mm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0,0), (-1,-1), styleN.fontName),
            ("FONTSIZE", (0,0), (-1,-1), 12),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ]))
        story.append(t); story.append(Spacer(1, 10))

    # 圖
    if chart_image_bytes:
        story.append(Paragraph("資產結構圖", styleH))
        img = Image(chart_image_bytes, width=150*mm, height=150*mm)
        img.hAlign = "CENTER"
        story.append(img); story.append(Spacer(1, 10))

    # 建議
    if suggestions:
        story.append(Paragraph("系統建議摘要", styleH))
        for s in suggestions:
            s_clean = _sanitize_emoji(str(s))
            story.append(Paragraph(f"• {s_clean}", styleN))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_sanitize_emoji("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com"), styleC))

    doc.build(story)
    buf.seek(0)
    return buf

# --------------------
# 3) 保單策略 PDF（雙介面相容）
#   A. generate_insurance_strategy_pdf(age, gender, budget, currency, pay_years, goals, strategies)
#   B. generate_insurance_strategy_pdf(strategy_text=str, chart_path=str)
# --------------------
def generate_insurance_strategy_pdf(*args, **kwargs):
    styleN, styleH, styleC, styleTitle, styleSlogan = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=30)
    story = []
    _brand_header(story, styleTitle, styleSlogan, styleC)
    story.append(Paragraph("保單策略建議", styleH))

    # 介面 B：strategy_text / chart_path
    strategy_text = kwargs.get("strategy_text")
    chart_path = kwargs.get("chart_path")
    if strategy_text is not None or chart_path is not None:
        if chart_path and os.path.exists(chart_path):
            img = Image(chart_path, width=14*cm, height=10*cm)
            img.hAlign = "CENTER"
            story.append(img); story.append(Spacer(1, 6))
        for para in (strategy_text or "").split("\n"):
            para = _sanitize_emoji(para)
            if para.strip() == "":
                story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(para, styleN))
        doc.build(story); buf.seek(0); return buf

    # 介面 A：結構化欄位
    if len(args) >= 6:
        age, gender, budget, currency, pay_years, goals = args[:6]
    else:
        age = gender = budget = currency = pay_years = goals = None

    strategies = args[6] if len(args) >= 7 else None

    if age is not None:
        head = f"年齡：{age}　性別：{gender}　預算：{currency}{budget:,}　繳費年期：{pay_years} 年"
        story.append(Paragraph(_sanitize_emoji(head), styleN))

    if goals:
        story.append(Spacer(1, 4))
        story.append(Paragraph("目標：", styleH))
        for g in goals:
            story.append(Paragraph(_sanitize_emoji(f"• {g}"), styleN))

    if strategies:
        story.append(Spacer(1, 6))
        story.append(Paragraph("初步策略建議：", styleH))
        for s in strategies:
            name = s.get("name", "策略")
            why = s.get("why", "")
            fit = ", ".join(s.get("fit", []))
            desc = s.get("description", "")
            story.append(Paragraph(_sanitize_emoji(f"【{name}】"), styleN))
            if why:  story.append(Paragraph(_sanitize_emoji(f"理由：{why}"), styleN))
            if fit:  story.append(Paragraph(_sanitize_emoji(f"適合對象：{fit}"), styleN))
            if desc: story.append(Paragraph(_sanitize_emoji(f"結構說明：{desc}"), styleN))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_sanitize_emoji("下一步：若這份策略讓您浮現了想法，歡迎預約對談，讓保單成為資產任務的助手。"), styleN))
    story.append(Paragraph(_sanitize_emoji("《影響力》傳承策略平台｜永傳家族辦公室 https://gracefo.com"), styleC))

    doc.build(story)
    buf.seek(0)
    return buf
