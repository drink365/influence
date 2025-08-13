# pages/0_AI_Copilot_Pro.py
# AI Copilot Pro：互動式內容/簡報產生器（單頁控制，無側邊欄）
from __future__ import annotations

import streamlit as st
from typing import List
from datetime import datetime

from legacy_tools.modules.pdf_generator import generate_pdf

st.set_page_config(page_title="AI Copilot Pro｜規劃與簡報助理", layout="wide")

# =========================
# Header：客戶視角說明
# =========================
st.markdown("""
<div style="background:#f5f8ff;padding:1.25rem 1.25rem;border-radius:12px;border:1px solid #e2e8f0;">
  <h2 style="margin:0 0 .5rem 0;color:#0f172a;">你的專屬 AI 規劃助理，讓傳承更清楚、更從容</h2>
  <p style="margin:0;color:#334155;">
    把法律、稅務與保險的複雜度變簡單。用對話，就能快速產出家族藍圖、簡報摘要與下一步建議。
  </p>
  <ul style="margin:1rem 0 0 1.25rem;color:#334155;">
    <li><b>一問即答：</b>以你的情境為核心，回覆清楚、少行話。</li>
    <li><b>專業可追溯：</b>依據常見實務與合規方向，標註注意事項。</li>
    <li><b>立即可用：</b>一鍵轉成簡報大綱／條列重點／Email 版，並可下載 PDF。</li>
  </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# 寫作控制（放在頁面上方）
# =========================
with st.container():
    st.markdown("### ✍️ 寫作控制")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

    with c1:
        tone = st.selectbox(
            "語氣",
            ["溫暖專業", "精準中性", "權威簡潔", "故事引導", "簡報要點"],
            index=0
        )
    with c2:
        audience = st.selectbox("受眾", ["家族客戶", "企業主", "專業夥伴", "一般大眾"], index=0)
    with c3:
        purpose = st.selectbox("目的", ["諮詢回覆", "企劃摘要", "簡報大綱", "社群貼文", "Email 正文"], index=1)
    with c4:
        fmt = st.radio("格式", ["條列重點", "段落敘述"], index=0, horizontal=True)

    c5, c6, c7 = st.columns([1, 1, 1])
    with c5:
        length = st.select_slider("長度", options=["短", "中", "長"], value="中")
    with c6:
        add_brand = st.checkbox("加入品牌簽名", value=True, help="結尾加上：永傳家族辦公室｜www.gracefo.com｜123@gracefo.com")
    with c7:
        st.caption("金額單位以 **萬元（TWD）** 為主；可在下方貼上工具結果再重寫。")

    c8, c9 = st.columns([1, 1])
    with c8:
        keywords = st.text_input("必含關鍵詞（逗號分隔）", value="")
    with c9:
        avoid = st.text_input("避免詞（逗號分隔）", value="")

# =========================
# 主區：輸入／產出
# =========================
col_in, col_out = st.columns([1, 1.2], gap="large")

with col_in:
    st.markdown("#### 📝 你的情境或指示")
    user_prompt = st.text_area(
        "請描述你要產出的內容（可貼上工具結果、客戶背景、限制條件）",
        height=220,
        placeholder="範例：幫我寫一段給家族客戶的簡報開場，說明為何要預留稅源，語氣溫暖專業，200 字內…"
    )
    generate_btn = st.button("✨ 產出內容", type="primary", use_container_width=True)

    st.markdown("##### 快捷重寫")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        shorter_btn = st.button("更精簡")
    with col_b:
        longer_btn = st.button("更完整")
    with col_c:
        slide_btn = st.button("轉成簡報大綱")

def _sys_prompt(tone: str, audience: str, purpose: str, fmt: str, length: str,
                keywords: str, avoid: str, add_brand: bool) -> str:
    want_len = {"短": "約 80–150 字", "中": "約 150–300 字", "長": "約 300–600 字"}[length]
    fmt_hint = "請用條列格式（短句、每點 1 行）" if fmt == "條列重點" else "請用流暢段落敘述"
    brand = "結尾加上『永傳家族辦公室｜www.gracefo.com｜123@gracefo.com』" if add_brand else "不需要品牌簽名"
    kw = f"必須包含關鍵詞：{keywords}。" if keywords.strip() else ""
    ban = f"避免出現：{avoid}。" if avoid.strip() else ""
    tone_map = {
        "溫暖專業": "溫暖、具同理心、但保持專業與精確用字",
        "精準中性": "中性冷靜、重點明確、避免形容詞",
        "權威簡潔": "權威、精煉、直達重點",
        "故事引導": "用簡短故事切入，帶出問題與解法",
        "簡報要點": "每點 10–20 字內，像投影片要點",
    }
    return (
        f"你是家族財富傳承顧問的寫作助理，受眾是「{audience}」。"
        f"目的為「{purpose}」。語氣採用「{tone_map.get(tone, tone)}」。"
        f"{fmt_hint}，篇幅 {want_len}。{kw}{ban} {brand}。"
        "請使用繁體中文，避免過度行話，讓客戶易懂。"
    )

def _llm_generate(prompt: str, system: str, mode: str = "normal") -> str:
    # mode: normal/shorter/longer/slide
    try:
        import openai  # type: ignore
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            instr = {
                "normal": "請依系統要求與使用者內容產出最佳版本。",
                "shorter": "請在保留關鍵資訊下，改寫為更精簡版本（約 60–120 字或更少）。",
                "longer": "請擴寫為更完整版本，補足背景與行動建議（約 250–500 字）。",
                "slide": "請轉換為『簡報大綱』：每點一行、用詞精煉、避免冗句與標點裝飾。",
            }[mode]
            msgs = [
                {"role": "system", "content": system},
                {"role": "user", "content": f"{instr}\n\n使用者內容：\n{prompt}"},
            ]
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=msgs,
                temperature=0.7 if mode != "slide" else 0.3,
                max_tokens=1200,
            )
            return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    # Fallback（無金鑰/錯誤時）
    tag = {"normal": "建議稿", "shorter": "精簡稿", "longer": "擴寫稿", "slide": "簡報大綱"}[mode]
    bullet = "• " if "條列格式" in system else ""
    lines = [
        f"【{tag}】（離線草稿；上線後會改用模型生成）",
        "",
        f"目的：{purpose}｜受眾：{audience}｜語氣：{tone}",
        "",
    ]
    if mode == "slide":
        lines += [
            f"{bullet}問題/情境：{(st.session_state.get('last_topic') or '—')}",
            f"{bullet}核心觀念：預留稅源、確定性傳承",
            f"{bullet}可執行步驟：條列 3–5 點",
            f"{bullet}下一步：預約諮詢或下載工具 PDF",
        ]
    else:
        lines += [
            "重點：",
            f"{bullet}聚焦客戶情境，避免行話",
            f"{bullet}說明做法與下一步",
            "",
            "內容草稿：",
            (st.session_state.get("last_topic") or "（尚未輸入內容）"),
        ]
    if add_brand:
        lines += ["", "—", "永傳家族辦公室｜www.gracefo.com｜123@gracefo.com"]
    return "\n".join(lines)

# 狀態
if "copilot_output" not in st.session_state:
    st.session_state.copilot_output = ""
if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

system_prompt = _sys_prompt(tone, audience, purpose, fmt, length, keywords, avoid, add_brand)

with col_out:
    st.markdown("#### 🧾 產出結果")
    if generate_btn and not user_prompt.strip():
        st.warning("請先輸入內容或情境，再按「產出內容」。")
    if generate_btn and user_prompt.strip():
        st.session_state.last_topic = user_prompt.strip()[:60]
        st.session_state.copilot_output = _llm_generate(user_prompt, system_prompt, mode="normal")

    # 快捷重寫
    if st.session_state.copilot_output and 'shorter_btn' in locals() and shorter_btn:
        st.session_state.copilot_output = _llm_generate(
            st.session_state.copilot_output, system_prompt, mode="shorter"
        )
    if st.session_state.copilot_output and 'longer_btn' in locals() and longer_btn:
        st.session_state.copilot_output = _llm_generate(
            st.session_state.copilot_output, system_prompt, mode="longer"
        )
    if st.session_state.copilot_output and 'slide_btn' in locals() and slide_btn:
        st.session_state.copilot_output = _llm_generate(
            st.session_state.copilot_output, system_prompt, mode="slide"
        )

    result = st.text_area("", value=st.session_state.copilot_output, height=420)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "下載 .txt",
            data=(result or "").encode("utf-8"),
            file_name=f"AI_Copilot_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not result.strip()
        )
    with col_dl2:
        if st.button("下載 PDF", use_container_width=True, disabled=not result.strip()):
            pdf_bytes = generate_pdf(
                content=result,
                title=f"{purpose}",
                logo_path=None,  # 自動抓根目錄 logo.png
                footer_text="永傳家族辦公室｜www.gracefo.com｜123@gracefo.com",
            ).getvalue()
            st.download_button(
                "點此下載 PDF",
                data=pdf_bytes,
                file_name=f"AI_Copilot_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

st.markdown("---")
# 導覽（名稱依你的偏好：資產地圖保留「家族」，其餘不加）
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    st.page_link("pages/Tools_AssetMap.py", label="🗺️ 家族資產地圖")
with col_nav2:
    st.page_link("pages/Tools_EstateTax.py", label="🧮 遺產稅試算")
with col_nav3:
    st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 保單策略建議")
