# legacy_tools/modules/pdf_generator.py
# 專業抬頭版式 PDF 生成器（左 Logo、右標題；避免重疊）
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
# 字型註冊：優先使用 NotoSansTC-Regular.ttf（根目錄或當前資料夾）
# -----------------------------
_FONT_MAIN = "NotoSansTC"
_FONT_PATH_CANDIDATES = [
    os.path.join(os.getcwd(), "NotoSansTC-Regular.ttf"),
    os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf"),
]

def _register_fonts():
    for p in _FONT_PATH_CANDIDATES:
        if os.path.isfile(p):
            try:
                pdfmetrics.registerFont(TTFont(_FONT_MAIN, p))
                return _FONT_MAIN
            except Exception:
                pass
    # 回退（英文/數字正常，CJK 會缺字；但我們會移除 emoji 以避免方框）
    return "Helvetica"

_FONT_NAME = _register_fonts()

# -----------------------------
# 文字處理（移除 emoji，避免方框亂碼）
# -----------------------------
_EMOJI_PATTERN = re.compile(
    "["                         # 常見 emoji 區段
    "\U0001F300-\U0001F5FF"     # Symbols & Pictographs
    "\U0001F600-\U0001F64F"     # Emoticons
    "\U0001F680-\U0001F6FF"     # Transport & Map
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U00002700-\U000027BF"     # Dingbats
    "\U00002600-\U000026FF"     # Misc symbols
    "]+",
    flags=re.UNICODE,
)

def _sanitize_text(s: str) -> str:
    if not s:
        return ""
    # 移除 emoji；不顯示「已移除 emoji」等字樣，避免打擾
    return _EMOJI_PATTERN.sub("", s)

# -----------------------------
# 文本換行
# -----------------------------
def _wrap_text(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    """
    依據字寬在 max_width 內做簡單換行（保留原始換行）。
    """
    lines_out: list[str] = []
    for raw_line in (text or "").splitlines():
        line = raw_line.rstrip("\n")
        if not line:
            lines_out.append("")
            continue
        # 逐字累積
        buf = ""
        for ch in line:
            test = buf + ch
            w = pdfmetrics.stringWidth(test, font_name, font_size)
            if w <= max_width:
                buf = test
            else:
                if buf:
                    lines_out.append(buf)
                buf = ch
        if buf or line == "":
            lines_out.append(buf)
    return lines_out

# -----------------------------
# 核心：產生 PDF
# -----------------------------
def generate_pdf(
    content: str,
    title: str = "報告",
    logo_path: str | None = None,
    footer_text: str = "",
) -> io.BytesIO:
    """
    產生單頁 A4 PDF，抬頭為「左 Logo、右標題」，避免與標題重疊。
    參數：
      - content: 主要文字內容（會自動換行）
      - title: 主標題（顯示於右上）
      - logo_path: 左上 Logo 圖檔路徑（可為 None）
      - footer_text: 頁尾置中文字
    回傳：BytesIO（可直接給 Streamlit download_button）
    """
    # 頁面與邊界
    PAGE_W, PAGE_H = A4  # 595 x 842 pt
    M_L = 20 * mm
    M_R = 20 * mm
    M_T = 18 * mm
    M_B = 18 * mm

    # Header 內部參數
    LOGO_MAX_W = 34 * mm      # Logo 最大寬
    LOGO_MAX_H = 16 * mm      # Logo 最大高（抬頭高度）
    TITLE_FONT = _FONT_NAME
    TITLE_SIZE = 16
    META_FONT_SIZE = 9
    HEADER_GAP_Y = 6 * mm     # Header 與正文間距

    # 正文字級
    BODY_FONT = _FONT_NAME
    BODY_SIZE = 12
    BODY_LINE_SP = 16          # 行高（pt）

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)

    # ----------------- Header：左 Logo、右標題 -----------------
    # Header 區域基準線（上邊界往下）
    header_top_y = PAGE_H - M_T
    header_bottom_y = header_top_y - LOGO_MAX_H
    header_height = LOGO_MAX_H

    # 1) Logo（靠左，維持等比）
    logo_drawn_h = 0
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            # 依比例縮放到 LOGO_MAX_W x LOGO_MAX_H 內
            scale = min(LOGO_MAX_W / iw, LOGO_MAX_H / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            x = M_L
            y = header_top_y - draw_h  # 靠上對齊
            c.drawImage(img, x, y, width=draw_w, height=draw_h, mask='auto')
            logo_drawn_h = draw_h
        except Exception:
            logo_drawn_h = 0

    # 2) 右側標題區（標題＋右上角小字）
    c.setFont(TITLE_FONT, TITLE_SIZE)
    safe_title = _sanitize_text(title or "報告")

    # 右上角 meta（單位與日期）
    meta_right_x = PAGE_W - M_R
    meta_start_y = header_top_y
    c.setFont(BODY_FONT, META_FONT_SIZE)
    unit_text = "本報告所有金額單位：萬元（TWD）"
    date_text = f"生成日期：{datetime.now().strftime('%Y-%m-%d')}"
    # 右對齊小字
    c.drawRightString(meta_right_x, meta_start_y - 0, _sanitize_text(unit_text))
    c.drawRightString(meta_right_x, meta_start_y - 12, _sanitize_text(date_text))

    # 標題：放在右側，避免與 logo 重疊（標題 baseline 設在 header 中線略下）
    title_x = PAGE_W - M_R
    title_y = header_bottom_y + (header_height * 0.45)  # 視覺置中略下
    c.setFont(TITLE_FONT, TITLE_SIZE)
    c.drawRightString(title_x, title_y, safe_title)

    # 計算正文起始 Y：取 Header 及 Logo/標題區之下，再加安全間距
    body_start_y = min(header_bottom_y, title_y - 4) - HEADER_GAP_Y

    # ----------------- 正文 -----------------
    c.setFont(BODY_FONT, BODY_SIZE)
    safe_content = _sanitize_text(content or "")
    max_text_width = PAGE_W - M_L - M_R
    lines = _wrap_text(safe_content, BODY_FONT, BODY_SIZE, max_text_width)

    cursor_y = body_start_y
    for line in lines:
        # 頁底保護：若超出頁面，暫時用單頁報告，超出則截斷（可擴充成多頁）
        if cursor_y <= M_B + BODY_LINE_SP:
            break
        c.drawString(M_L, cursor_y, line)
        cursor_y -= BODY_LINE_SP

    # ----------------- 頁尾 -----------------
    if footer_text:
        c.setFont(BODY_FONT, 10)
        safe_footer = _sanitize_text(footer_text)
        c.drawCentredString(PAGE_W / 2, M_B - 6, safe_footer)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
