# legacy_tools/modules/pdf_generator.py
# 雙欄抬頭 PDF 生成器：
# 左 Logo、右上報告資訊；下一行置中主標題；正文自動換行；頁尾置中。
from __future__ import annotations

import io
import os
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -----------------------------
# 字型註冊：優先使用 NotoSansTC-Regular.ttf（根目錄或與本檔同層）
# -----------------------------
_FONT_MAIN = "NotoSansTC"
_FONT_CANDIDATES = [
    os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
    os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf"),
]

def _register_fonts() -> str:
    for path in _FONT_CANDIDATES:
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont(_FONT_MAIN, path))
                return _FONT_MAIN
            except Exception:
                pass
    # 回退英文字型（CJK 可能缺字；我們已移除 emoji 以避免方框）
    return "Helvetica"

_FONT_NAME = _register_fonts()

# -----------------------------
# 移除 emoji（避免 PDF 方框亂碼）
# -----------------------------
_EMOJI_PATTERN = re.compile(
    "["  # 常見 emoji 區段
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)

def _sanitize(s: str) -> str:
    if not s:
        return ""
    return _EMOJI_PATTERN.sub("", s)

# -----------------------------
# 簡易自動換行（保留原本換行）
# -----------------------------
def _wrap_text(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip("\n")
        if not line:
            out.append("")
            continue
        buf = ""
        for ch in line:
            t = buf + ch
            w = pdfmetrics.stringWidth(t, font_name, font_size)
            if w <= max_width:
                buf = t
            else:
                if buf:
                    out.append(buf)
                buf = ch
        if buf or line == "":
            out.append(buf)
    return out

# -----------------------------
# 生成 PDF（單頁）
# -----------------------------
def generate_pdf(
    content: str,
    title: str = "報告",
    logo_path: str | None = None,
    footer_text: str = "",
) -> io.BytesIO:
    """
    產生單頁 A4 PDF，抬頭使用【左 Logo、右上資訊；下一行置中標題】版式。
    參數：
      - content: 內文（自動換行）
      - title: 主標題（置中）
      - logo_path: 左上 Logo 圖（可為 None）
      - footer_text: 頁尾置中文字
    回傳：BytesIO
    """
    # --- 版面參數 ---
    PAGE_W, PAGE_H = A4  # 595 x 842 pt
    M_L, M_R, M_T, M_B = 20*mm, 20*mm, 18*mm, 18*mm

    # Header（雙欄）與標題、正文間距
    LOGO_MAX_W = 36 * mm
    LOGO_MAX_H = 18 * mm
    META_FONT_SIZE = 9
    TITLE_SIZE = 18
    TITLE_GAP = 5 * mm         # Header 與「置中標題」之間距
    BODY_GAP = 6 * mm          # 標題與正文之間距

    BODY_FONT = _FONT_NAME
    BODY_SIZE = 12
    BODY_LINE = 16             # 行高

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)

    # ---------- Header：左 Logo、右上資訊 ----------
    header_top = PAGE_H - M_T
    header_bottom = header_top - LOGO_MAX_H

    # Left: Logo
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            scale = min(LOGO_MAX_W / iw, LOGO_MAX_H / ih)
            dw, dh = iw * scale, ih * scale
            c.drawImage(img, M_L, header_top - dh, width=dw, height=dh, mask="auto")
        except Exception:
            pass

    # Right: 單位＋日期（兩行、右對齊）
    c.setFont(BODY_FONT, META_FONT_SIZE)
    unit_text = _sanitize("本報告所有金額單位：萬元（TWD）")
    date_text = _sanitize(f"生成日期：{datetime.now().strftime('%Y-%m-%d')}")
    right_x = PAGE_W - M_R
    c.drawRightString(right_x, header_top - 0, unit_text)
    c.drawRightString(right_x, header_top - 12, date_text)

    # ---------- 置中標題（在 header 下方、整頁置中對齊） ----------
    safe_title = _sanitize(title or "報告")
    c.setFont(_FONT_NAME, TITLE_SIZE)
    title_y = header_bottom - TITLE_GAP
    c.drawCentredString(PAGE_W / 2, title_y, safe_title)

    # ---------- 正文（自動換行） ----------
    body_start_y = title_y - BODY_GAP
    c.setFont(BODY_FONT, BODY_SIZE)
    safe_content = _sanitize(content or "")
    max_width = PAGE_W - M_L - M_R
    lines = _wrap_text(safe_content, BODY_FONT, BODY_SIZE, max_width)

    y = body_start_y
    for line in lines:
        if y <= M_B + BODY_LINE:
            break  # 單頁版式：若超出頁面則截斷（如需多頁，可延伸此處）
        c.drawString(M_L, y, line)
        y -= BODY_LINE

    # ---------- 頁尾 ----------
    if footer_text:
        c.setFont(BODY_FONT, 10)
        c.drawCentredString(PAGE_W / 2, M_B - 6, _sanitize(footer_text))

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
