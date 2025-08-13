# legacy_tools/modules/pdf_generator.py
# 簡潔穩定的 PDF 產生器（繁中字型、Logo、頁首單位註記＋生成日期）
from __future__ import annotations

import io
import os
import re
from typing import Optional, Tuple
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

# 預設字型設定
_DEFAULT_FONT_NAME = "Helvetica"          # fallback
_CJK_FONT_NAME = "NotoSansTC"             # 目標字型名稱
_CJK_FONT_FILE = "NotoSansTC-Regular.ttf" # 建議放在 repo 根目錄或 pages/ 或 assets/

# 文字樣式
_TITLE_FONT_SIZE = 18
_BODY_FONT_SIZE = 12
_UNIT_FONT_SIZE = 9
_META_FONT_SIZE = 9         # 生成日期等小字
_FOOTER_FONT_SIZE = 8

# 版面設定
_PAGE_MARGIN_LR = 48    # 左右邊界
_PAGE_MARGIN_T = 56     # 上邊界
_PAGE_MARGIN_B = 56     # 下邊界
_LINE_HEIGHT = 18       # 文字行距（對應 12pt 字體）
_MAX_LOGO_WIDTH = 140   # Logo 最大寬度（pt）

# 預設頁首註記
_DEFAULT_UNIT_NOTE = "本報告所有金額單位：萬元（TWD）"
_DEFAULT_DATE_LABEL = "生成日期"           # 友善用語（取代「出具日期」）


def _register_cjk_font() -> str:
    """
    嘗試註冊 NotoSansTC；找不到就使用內建 Helvetica。
    回傳可用的 fontName。
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    search_paths = [
        _CJK_FONT_FILE,
        os.path.join("pages", _CJK_FONT_FILE),
        os.path.join("assets", _CJK_FONT_FILE),
        os.path.join("static", _CJK_FONT_FILE),
        os.path.join("fonts", _CJK_FONT_FILE),
    ]
    for p in search_paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(_CJK_FONT_NAME, p))
                return _CJK_FONT_NAME
            except Exception:
                continue
    return _DEFAULT_FONT_NAME


def _sanitize_text(s: str) -> str:
    """
    移除常見會造成嵌字失敗的字元（包含多數 emoji、控制字元），避免 PDF 出現方框或錯位。
    - 移除 BMP 以外的字元（大多數 emoji）
    - 移除控制字元（除了常用換行）
    """
    if not s:
        return ""
    # 移除非 BMP（\U00010000 以上）
    s = re.sub(r"[\U00010000-\U0010FFFF]", "", s)
    # 移除控制字元（保留 \n、\r、\t）
    s = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", s)
    return s


def _wrap_text(text: str, max_width: float, canvas_obj: canvas.Canvas, font_name: str, font_size: int) -> list:
    """
    簡單斷行：依據字串測寬度在 max_width 內換行。
    備註：針對中文以字元為單位斷行，英文以空白為界會更好，不過此處以穩定簡化為主。
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth

    lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.rstrip()
        if not line:
            lines.append("")
            continue

        # 嘗試以空白切，兼顧中英文；不夠再用字元切
        parts = re.split(r"(\s+)", line)  # 保留空白做黏回
        buf = ""
        for part in parts:
            test = buf + part
            if stringWidth(test, font_name, font_size) <= max_width:
                buf = test
            else:
                if buf:
                    lines.append(buf)
                # part 自己太長時，改以字元切
                if stringWidth(part, font_name, font_size) > max_width:
                    chunk = ""
                    for ch in part:
                        if stringWidth(chunk + ch, font_name, font_size) <= max_width:
                            chunk += ch
                        else:
                            lines.append(chunk)
                            chunk = ch
                    buf = chunk
                else:
                    buf = part
        if buf:
            lines.append(buf)
    return lines


def _draw_logo(c: canvas.Canvas, logo_path: Optional[str], x: float, y: float) -> Optional[Tuple[float, float]]:
    """
    繪製 Logo，回傳 (實際寬, 實際高)。若失敗回傳 None。
    """
    if not logo_path:
        return None
    try:
        img = ImageReader(logo_path)
        iw, ih = img.getSize()
        # 等比縮放
        if iw > _MAX_LOGO_WIDTH:
            scale = _MAX_LOGO_WIDTH / float(iw)
            dw = _MAX_LOGO_WIDTH
            dh = ih * scale
        else:
            dw, dh = iw, ih
        c.drawImage(img, x, y - dh, width=dw, height=dh, preserveAspectRatio=True, mask='auto')
        return (dw, dh)
    except Exception:
        return None


def generate_pdf(
    content: str,
    title: str = "報告",
    logo_path: Optional[str] = None,
    unit_note: Optional[str] = _DEFAULT_UNIT_NOTE,
    footer_text: Optional[str] = None,
    page_size=A4,
    # 新增：生成日期（可關閉或自訂）
    show_date: bool = True,
    date_label: str = _DEFAULT_DATE_LABEL,
    date_value: Optional[str] = None,     # None 則自動使用今日
    date_format: str = "%Y-%m-%d",
) -> io.BytesIO:
    """
    產生 PDF：
    - content：多行文字，將依頁寬斷行
    - title：頁首標題
    - logo_path：品牌 Logo（可省略）
    - unit_note：頁首右側的單位註記；預設顯示「本報告所有金額單位：萬元（TWD）」
                 若傳入 None 或空字串，則不顯示
    - footer_text：頁尾小字（可省略）
    - show_date / date_label / date_value / date_format：右上角以溫和語氣顯示「生成日期」
    - 回傳 BytesIO
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page_size)
    width, height = page_size

    # 字型
    font_name = _register_cjk_font()
    c.setTitle(_sanitize_text(title))

    # 頁首：Logo + Title + 右上角（單位註記／生成日期）
    x = _PAGE_MARGIN_LR
    y = height - _PAGE_MARGIN_T

    # Logo（左上）
    logo_drawn = _draw_logo(c, logo_path, x, y)
    if logo_drawn:
        lw, lh = logo_drawn
        title_y = y - (lh + 8)  # Logo 下方 8pt 顯示標題
    else:
        title_y = y

    # Title
    c.setFont(font_name, _TITLE_FONT_SIZE)
    c.setFillColor(colors.black)
    c.drawString(x, title_y, _sanitize_text(title))

    # 右上角：單位註記（第一行）＋ 生成日期（第二行）
    right_x = width - _PAGE_MARGIN_LR
    meta_y = title_y
    if unit_note:
        c.setFont(font_name, _UNIT_FONT_SIZE)
        c.setFillColor(colors.HexColor("#6b7280"))  # slate-500 類似
        unit_text = _sanitize_text(str(unit_note))
        utw = c.stringWidth(unit_text, font_name, _UNIT_FONT_SIZE)
        c.drawString(right_x - utw, meta_y, unit_text)
        meta_y -= (_UNIT_FONT_SIZE + 3)  # 下一行往下

    if show_date:
        c.setFont(font_name, _META_FONT_SIZE)
        c.setFillColor(colors.HexColor("#6b7280"))
        date_str = date_value or datetime.now().strftime(date_format)
        date_text = f"{date_label}：{date_str}"
        date_text = _sanitize_text(date_text)
        dtw = c.stringWidth(date_text, font_name, _META_FONT_SIZE)
        c.drawString(right_x - dtw, meta_y, date_text)

    # 內容起始 Y（標題下一行再留 16pt）
    cur_y = min(meta_y, title_y) - 16

    # 內容框寬度
    content_max_w = width - _PAGE_MARGIN_LR * 2

    # 內容文字
    c.setFont(font_name, _BODY_FONT_SIZE)
    c.setFillColor(colors.black)

    lines = _wrap_text(_sanitize_text(content or ""), content_max_w, c, font_name, _BODY_FONT_SIZE)
    for line in lines:
        if cur_y < _PAGE_MARGIN_B + _LINE_HEIGHT:
            # 換頁
            c.showPage()
            c.setFont(font_name, _BODY_FONT_SIZE)
            cur_y = height - _PAGE_MARGIN_T
        c.drawString(_PAGE_MARGIN_LR, cur_y, line)
        cur_y -= _LINE_HEIGHT

    # 頁尾（可選）
    if footer_text:
        c.setFont(font_name, _FOOTER_FONT_SIZE)
        c.setFillColor(colors.HexColor("#9ca3af"))  # 淺灰
        ft = _sanitize_text(footer_text)
        c.drawString(_PAGE_MARGIN_LR, _PAGE_MARGIN_B - 10, ft)

    c.save()
    buf.seek(0)
    return buf
