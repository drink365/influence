# app.py
# 行銷導向首頁（Hero + 品牌價值 + CTA）
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
        "logo_paths": ["logo.png", "assets/logo.png", "static/logo.png", "images/logo.png"],
        "booking_url": "https://www.gracefo.com/booking",
        "contact_line": "@yourlineid",
        "contact_email": "service@gracefo.com",
        "hero_headline": "以專業，讓傳承更簡單。",
        "hero_subhead": "結合法律、稅務與保險的整合式規劃，打造家族永續現金流。",
        "bullets": [
            "高端客製：以人為本，量身訂製最佳解決方案",
            "一站整合：律師、會計師、財稅專家跨域協作",
            "AI 驅動：快速產出策略與專業簡報，提高成交效率"
        ]
    }
    """
    defaults = {
        "app_title": "influence",
        "app_subtitle": "家族傳承與保單策略助手",
        "logo_paths": ["logo.png", "assets/logo.png", "static/logo.png", "images/logo.png"],
        "booking_url": "",
        "contact_line": "",
        "contact_email": "",
        "hero_headline": "以專業，讓傳承更簡單。",
        "hero_subhead": "結合法律、稅務與保險的整合式規劃，打造家族永續現金流。",
        "bullets": [
            "高端客製：以人為本，量身訂製最佳解決方案",
            "一站整合：律師、會計師、財稅專家跨域協作",
            "AI 驅動：快速產出策略與專業簡報，提高成交效率",
        ],
    }
    for p in [Path("brand.json"), Path("config/brand.json"), Path("assets/brand.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
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
    page_icon="🏛️",
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
# 樣式（Hero / 品牌區塊）
# -------------------------
CSS = """
<style>
/* 版頭 */
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

/* Hero Banner */
.hero {
  border-radius: 18px;
  padding: 28px 28px 24px 28px;
  background: linear-gradient(135deg, #f7f8ff 0%, #eef3ff 100%);
  border: 1px solid #e8ecff;
  box-shadow: 0 4px 18px rgba(30, 60, 120, 0.06);
  margin: 8px 0 18px 0;
}
.hero h2 {
  margin: 0 0 6px 0;
  font-size: 2rem;
  line-height: 1.25;
  color: #1e2a45;
}
.hero p.sub {
  margin: 0 0 12px 0;
  font-size: 1.05rem;
  color: #3b4963;
}
.badges { display:flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
.badge {
  border-radius: 999px;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid #e2e8ff;
  color: #334155;
  font-size: 0.92rem;
}
.cta-row { display:flex; gap: 12px; flex-wrap: wrap; margin-top: 14px; }
.cta a, .cta button {
  display:inline-block; border-radius: 10px; padding: 10px 16px; border: 1px solid #2b59ff;
  background:#2b59ff; color:#fff; text-decoration:none; font-weight:600;
}
.cta-outline {
  background:#fff; color:#2b59ff; border:1px solid #2b59ff;
}
.hr-thin { border: none; border-top: 1px solid #eee; margin: 8px 0 6px 0; }

/* 三大價值 */
.value-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 10px; }
.value-card {
  border-radius: 16px; padding: 16px; background:#fff; border:1px solid #eef1f7;
  box-shadow: 0 2px 10px rgba(30, 60, 120, 0.05);
}
.value-card h3 { margin: 0 0 6px 0; font-size: 1.05rem; color:#0f172a; }
.value-card p { margin: 0; color:#475569; }
@media (max-width: 900px) {
  .value-grid { grid-template-columns: 1fr; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -------------------------
# 版頭（Logo + 標題）
# -------------------------
col_logo, col_title = st.columns([1, 5], gap="small")
with col_logo:
    if logo_src:
        st.markdown(f"<div class='app-logo'><img src='{logo_src}' alt='logo'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='app-logo'>🏛️</div>", unsafe_allow_html=True)

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
# Hero 行銷文案＋ CTA
# -------------------------
hero_headline = BRAND.get("hero_headline")
hero_subhead = BRAND.get("hero_subhead")
bullets = BRAND.get("bullets", [])

st.markdown(
    f"""
    <div class="hero">
      <h2>{hero_headline}</h2>
      <p class="sub">{hero_subhead}</p>
      <div class="badges">
        {''.join([f"<span class='badge'>{b}</span>" for b in bullets[:4]])}
      </div>
      <div class="cta-row">
        <span class="cta"><a href="#" id="to-ins" onclick="return false;">立即產生保單策略</a></span>
        {"<span class='cta'><a class='cta-outline' href='"+BRAND.get("booking_url","")+"' target='_blank'>預約 30 分鐘諮詢</a></span>" if BRAND.get("booking_url") else ""}
        {"<span class='cta'><a class='cta-outline' href='https://line.me/R/ti/p/"+BRAND.get("contact_line","")+"' target='_blank'>加入 LINE 洽詢</a></span>" if BRAND.get("contact_line") else ""}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 讓「立即產生保單策略」導向 Tools_InsuranceStrategy（盡量相容不同版本 Streamlit）
clicked = st.button("👉 立即產生保單策略", key="cta_fallback_button")
if clicked:
    # 1) 新版 Streamlit（支援 switch_page）
    try:
        from streamlit_extras.switch_page_button import switch_page  # 若有外掛
        switch_page("Tools_InsuranceStrategy")
    except Exception:
        try:
            st.switch_page("pages/Tools_InsuranceStrategy.py")  # 官方 API（較新版本）
        except Exception:
            # 2) 若不支援，顯示引導：請從左側選單點選
            st.info("請從左側選單進入「Tools_InsuranceStrategy」頁面。")

# -------------------------
# 三大價值（可再加深）
# -------------------------
v1, v2, v3 = st.columns(3, gap="small")
with v1:
    st.markdown(
        """
        <div class="value-card">
          <h3>法律 × 稅務 × 保險 一站整合</h3>
          <p>跨域專家協同，將信託、股權與保單策略化繁為簡，避免戲劇化接班。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with v2:
    st.markdown(
        """
        <div class="value-card">
          <h3>高效成交工具，現場就能用</h3>
          <p>AI 立即生成策略與 PDF 簡報，清楚展示傳承與稅源預留效果，縮短決策時間。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with v3:
    st.markdown(
        """
        <div class="value-card">
          <h3>品牌一致、客製輸出</h3>
          <p>套用專屬 Logo 與版面，生成可分享的策略摘要，兼顧專業形象與實務可行性。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# 次 CTA（頁面底部）
# -------------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("下一步")
    st.markdown("- 前往 **保單策略建議**，輸入預算與目標，立即產出專屬建議。")
    st.markdown("- 需要完整家族傳承規劃？可預約顧問 1 對 1 諮詢。")

with col2:
    if st.button("前往保單策略建議", key="cta_bottom"):
        try:
            from streamlit_extras.switch_page_button import switch_page
            switch_page("Tools_InsuranceStrategy")
        except Exception:
            try:
                st.switch_page("pages/Tools_InsuranceStrategy.py")
            except Exception:
                st.info("請從左側選單進入「Tools_InsuranceStrategy」頁面。")

# 底部品牌資訊（若有設定）
contact_email = BRAND.get("contact_email")
contact_line = BRAND.get("contact_line")
booking_url = BRAND.get("booking_url")
footer_bits = []
if booking_url:
    footer_bits.append(f"[預約諮詢]({booking_url})")
if contact_line:
    footer_bits.append(f"[LINE]({'https://line.me/R/ti/p/'+contact_line})")
if contact_email:
    footer_bits.append(f"聯絡信箱：{contact_email}")

if footer_bits:
    st.markdown("---")
    st.caption("　｜　".join(footer_bits))
