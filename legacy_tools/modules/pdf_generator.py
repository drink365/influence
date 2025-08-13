# legacy_tools/modules/pdf_generator.py
from __future__ import annotations
import io, os, re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 字型：優先 NotoSansTC
_FONT_MAIN = "NotoSansTC"
_FONT_CANDIDATES = [
    os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
    os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf"),
]
def _register_fonts() -> str:
    for p in _FONT_CANDIDATES:
        if os.path.isfile(p):
            try:
                pdfmetrics.registerFont(TTFont(_FONT_MAIN, p))
                return _FONT_MAIN
            except Exception:
                pass
    return "Helvetica"
_FONT_NAME = _register_fonts()

# 去除 emoji
_EMOJI = re.compile("[" "\U0001F300-\U0001F5FF" "\U0001F600-\U0001F64F" "\U0001F680-\U0001F6FF"
                    "\U0001F700-\U0001F77F" "\U0001F780-\U0001F7FF" "\U0001F800-\U0001F8FF"
                    "\U0001F900-\U0001F9FF" "\U0001FA00-\U0001FA6F" "\U00002700-\U000027BF"
                    "\U00002600-\U000026FF" "]+", flags=re.UNICODE)
def _sanitize(s: str) -> str:
    return "" if not s else _EMOJI.sub("", s)

def _wrap(text: str, font: str, size: float, maxw: float) -> list[str]:
    out = []
    for raw in (text or "").splitlines():
        line = raw.rstrip("\n")
        if not line:
            out.append(""); continue
        buf = ""
        for ch in line:
            t = buf + ch
            if pdfmetrics.stringWidth(t, font, size) <= maxw:
                buf = t
            else:
                if buf: out.append(buf)
                buf = ch
        if buf or line == "":
            out.append(buf)
    return out

def generate_pdf(content: str, title: str = "報告", logo_path: str | None = None, footer_text: str = "") -> io.BytesIO:
    # 自動帶入根目錄 logo.png
    if not logo_path:
        default_logo = os.path.join(os.getcwd(), "logo.png")
        if os.path.isfile(default_logo):
            logo_path = default_logo

    PAGE_W, PAGE_H = A4
    M_L, M_R, M_T, M_B = 20*mm, 20*mm, 18*mm, 18*mm
    LOGO_MAX_W, LOGO_MAX_H = 36*mm, 18*mm
    META_FONT_SIZE, TITLE_SIZE = 9, 18
    TITLE_GAP, BODY_GAP = 5*mm, 6*mm
    BODY_FONT, BODY_SIZE, BODY_LINE = _FONT_NAME, 12, 16

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)

    header_top = PAGE_H - M_T
    header_bottom = header_top - LOGO_MAX_H

    # 左：Logo
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            scale = min(LOGO_MAX_W/iw, LOGO_MAX_H/ih)
            c.drawImage(img, M_L, header_top - ih*scale, width=iw*scale, height=ih*scale, mask="auto")
        except Exception:
            pass

    # 右：單位＋日期
    c.setFont(BODY_FONT, META_FONT_SIZE)
    right_x = PAGE_W - M_R
    c.drawRightString(right_x, header_top - 0, _sanitize("本報告所有金額單位：萬元（TWD）"))
    c.drawRightString(right_x, header_top - 12, _sanitize(f"生成日期：{datetime.now().strftime('%Y-%m-%d')}"))

    # 置中標題
    c.setFont(_FONT_NAME, TITLE_SIZE)
    title_y = header_bottom - TITLE_GAP
    c.drawCentredString(PAGE_W/2, title_y, _sanitize(title or "報告"))

    # 正文
    body_start_y = title_y - BODY_GAP
    c.setFont(BODY_FONT, BODY_SIZE)
    lines = _wrap(_sanitize(content or ""), BODY_FONT, BODY_SIZE, PAGE_W - M_L - M_R)
    y = body_start_y
    for line in lines:
        if y <= M_B + BODY_LINE: break
        c.drawString(M_L, y, line); y -= BODY_LINE

    # 頁尾
    if footer_text:
        c.setFont(BODY_FONT, 10)
        c.drawCentredString(PAGE_W/2, M_B - 6, _sanitize(footer_text))

    c.showPage(); c.save(); buf.seek(0)
    return buf
