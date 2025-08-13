# app.py
# 主應用入口：包含「響應式 Logo」顯示（桌機約 220px，手機自動縮小）
from __future__ import annotations

import base64
from pathlib import Path
import json
import streamlit as st

# -------------------------
# 讀取品牌設定（可選）
# -------------------------
def load_brand():
    """
    讀取 brand.json（若有），回傳 dict：
    {
        "app_title": "influence",
        "app_subtitle": "家族傳承與保單策略助手",
        "logo_paths": ["logo.png", "assets/logo.png", "static/logo.png"]
    }
    """
    defaults = {
        "app_title": "influence",
        "app_subtitle": "家族傳承與保單策略助手",
        "logo_paths": ["logo.png", "assets/logo.png", "static/logo.png", "images/logo.png"],
    }
    for p in [Path("brand.json"), Path("config/brand.json"), Path("assets/brand.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                # 合併預設
                for k, v in defaults.items():
                    data.setdefault(k, v)
                return data
            except Exception:
                return defaults
    return defaults

BRAND = load_brand()

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title=f"{BRAND.get('app_title','influence')}",
    page_icon="🧭",
    layout="wide",
)

# -------------------------
# 找出 Logo 並轉成 base64
# -------------------------
def find_logo_bytes(paths) -> bytes | None:
    for p in paths:
        fp = Path(p)
        if fp.exists() and fp.is_file():
            try:
                return fp.read_bytes()
            except Exception:
                continue
    return None

def to_base64_src(img_bytes: bytes) -> str:
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"

logo_bytes = find_logo_bytes(BRAND.get("logo_paths", []))
logo_src = to_base64_src(logo_bytes) if logo_bytes else None

# -------------------------
# 版頭：左 logo、右標題
# -------------------------
HEADER_CSS = """
<style>
.app-header { display:flex; align-items:center; gap: 16px; margin-bottom: 12px; }
.app-logo img { display:block; width: 220px; height: auto; }           /* 桌機 */
@media (max-width: 1024px) {
  .app-logo img { width: 180px; }                                      /* 平板 */
}
@media (max-width: 640px) {
  .app-logo img { width: 140px; }                                      /* 手機 */
}
.app-title { line-height:1.2; }
.app-title h1 { margin: 0; font-size: 1.8rem; }
.app-title p  { margin: 4px 0 0 0; color: #666; }
hr.hr-thin { border: none; border-top: 1px solid #eee; margin: 8px 0 20px 0; }
</style>
"""

st.markdown(HEADER_CSS, unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 5], gap="small")
with col_logo:
    if logo_src:
        st.markdown(f"<div class='app-logo'><img src='{logo_src}' alt='logo'></div>", unsafe_allow_html=True)
    else:
        # 找不到 logo 時不報錯，只顯示預設 emoji
        st.markdown("<div class='app-logo'>🏷️</div>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        f"""
        <div class='app-title'>
          <h1>{BRAND.get('app_title','influence')}</h1>
          <p>{BRAND.get('app_subtitle','家族傳承與保單策略助手')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr class='hr-thin' />", unsafe_allow_html=True)

# -------------------------
# 導覽（可依你現有的多頁設計調整）
# -------------------------
st.write("歡迎使用。請從左側選單進入各工具頁（如：AI Copilot Pro、保單策略建議、遺產稅試算…）。")
st.caption("提示：Logo 尺寸已自動響應式調整。若需更小，請在 app.py 中修改 CSS 的寬度。")
