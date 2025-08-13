# pages/0_AI_Copilot_Pro.py
# AI Copilot Pro：雙模式（品牌草擬/免費 + 專家模式/用戶自備API）
from __future__ import annotations

import os
import glob
import re
from datetime import datetime
from typing import List, Tuple

import streamlit as st
from legacy_tools.modules.pdf_generator import generate_pdf

# -------------------------------------------------
# 頁面設定
# -------------------------------------------------
st.set_page_config(
    page_title="AI Copilot Pro｜永傳家族辦公室",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 工具：讀檔＆簡易檢索（免外部套件）
# -------------------------------------------------
def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def load_knowledge_cards() -> List[Tuple[str, str]]:
    """
    回傳 [(filename, content), ...]，搜尋 knowledge/*.md
    """
    cards: List[Tuple[str, str]] = []
    for p in sorted(glob.glob(os.path.join("knowledge", "*.md"))):
        cards.append((os.path.basename(p), read_text(p)))
    return cards

def keywordize(s: str) -> List[str]:
    s = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", " ", s)
    return [w for w in s.lower().split() if w]

def score_overlap(query: str, doc: str) -> int:
    """
    超輕量檢索：以關鍵詞交集數量作為分數
    """
    qset = set(keywordize(query))
    dset = set(keywordize(doc))
    return len(qset & dset)

def retrieve(query: str, docs: List[Tuple[str, str]], k: int = 3) -> List[Tuple[str, str]]:
    scored = [(fn, tx, score_overlap(query, tx)) for fn, tx in docs]
    scored.sort(key=lambda x: x[2], reverse=True)
    return [(fn, tx) for fn, tx, _ in scored[:k] if _ > 0]

def load_template(kind: str) -> str:
    """
    從 prompts/ 載入模板；kind 例如 'email', 'summary', 'slides', 'generic'
    """
    path = os.path.join("prompts", f"{kind}.md")
    text = read_text(path)
    if not text.strip():
        # 後備：通用模板
        return (
            "【目的】{purpose}\n"
            "【受眾】{audience}\n"
            "【語氣】{tone}\n"
            "【格式】{fmt}\n\n"
            "=== 知識重點 ===\n{knowledge}\n\n"
            "=== 內容草擬 ===\n"
            "{body}\n\n"
            "{brand_signature}"
        )
    return text

def format_free_brand_output(
    tone: str, audience: str, purpose: str, fmt: str, length: str,
    must: str, avoid: str, body: str, knowledge_snippets: List[str], add_brand: bool
) -> str:
    want_len = {"短":"約 80–150 字", "中":"約 150–300 字", "長":"約 300–600 字"}[length]
    fmt_desc = "條列重點" if fmt == "條列重點" else "段落敘述"
    brand_signature = "—\n永傳家族辦公室｜www.gracefo.com｜123@gracefo.com" if add_brand else ""

    # 選模板
    kind = "slides" if fmt == "條列重點" and purpose in ["簡報大綱"] else "generic"
    if purpose in ["Email 正文"]:
        kind = "email"
    elif purpose in ["企劃摘要", "諮詢回覆"]:
        kind = "summary"

    tpl = load_template(kind)

    # 組合知識摘要
    kn_text = "\n---\n".join(knowledge_snippets) if knowledge_snippets else "（無特定知識命中；以下為品牌草擬稿）"

    # 產出
    out = tpl.format(
        purpose=purpose,
        audience=audience,
        tone=tone,
        fmt=fmt_desc + f"；篇幅：{want_len}",
        must=("必含關鍵詞：" + must) if must.strip() else "",
        avoid=("避免：" + avoid) if avoid.strip() else "",
        knowledge=kn_text,
        body=body.strip() or "（請在上方輸入你的情境或需求）",
        brand_signature=brand_signature
    )
    return out.strip()

# -------------------------------------------------
# 專家模式：OpenAI + 知識檢索（RAG）
# -------------------------------------------------
def build_system_prompt(tone: str, audience: str, purpose: str, fmt: str, length: str, add_brand: bool) -> str:
    tone_map = {
        "溫暖專業": "溫暖、具同理心，用字精確且有專業感；避免誇張與行話",
        "精準中性": "中性冷靜、直達重點；先結論後理由",
        "權威簡潔": "權威、簡潔、結構化",
        "故事引導": "短故事切入，帶出問題與解法",
        "簡報要點": "每點 10–20 字，像投影片要點",
    }
    want_len = {"短":"約 80–150 字","中":"約 150–300 字","長":"約 300–600 字"}[length]
    fmt_hint = "條列重點；短句、每點一行" if fmt == "條列重點" else "段落敘述，段落短而清楚"
    brand_sig = "結尾附：永傳家族辦公室｜www.gracefo.com｜123@gracefo.com。" if add_brand else "結尾不需品牌簽名。"
    return (
        "你是「永傳家族辦公室」的資深顧問，服務高資產家族，整合保險、法律與稅務，重視合規與風險控管。\n"
        "台灣脈絡與原則（非精算承諾）：\n"
        "- 遺產稅常見：免稅額 1,333 萬、喪葬費 138 萬、配偶 553 萬、子女/祖父母/兄弟姊妹 56 萬、父母 138 萬、重度身心障礙 693 萬；稅率級距常見 10%/15%/20%。\n"
        "- 保單策略：定期/終身壽險、TWD/USD 幣別配置、合理前期加保；避免保證與誇大。\n"
        "- 單位以「萬元（TWD）」表達；外幣請說明匯率風險。\n"
        "回覆原則：合規、透明、可落地；先重點，再作法，最後下一步行動（CTA）。避免不當承諾。\n\n"
        f"受眾：{audience}。目的：{purpose}。語氣：{tone_map.get(tone, tone)}。\n"
        f"格式：{fmt_hint}；篇幅：{want_len}。{brand_sig}\n"
        "請使用繁體中文，讓非專業者也能看懂。必要時用簡單例子輔助。"
    )

def llm_generate_with_rag(
    api_key: str,
    user_prompt: str,
    system_prompt: str,
    retrieved_snippets: List[str],
    mode: str = "normal"
) -> str:
    """
    使用者自備 API Key；若失敗回傳友善訊息。
    """
    try:
        import openai  # type: ignore
        openai.api_key = api_key

        instruction = {
            "normal": "依系統指示與提供的知識內容，產出最佳版本。",
            "shorter": "改寫為更精簡版本（約 60–120 字）。",
            "longer": "擴寫為更完整版本（約 250–500 字），補足背景與行動建議。",
            "slide": "轉為『簡報大綱』：每點一行、精煉可上投影片。",
        }[mode]

        context = "\n\n--- 已知識卡重點 ---\n" + "\n\n---\n".join(retrieved_snippets) if retrieved_snippets else ""

        msgs = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{instruction}\n{context}\n\n使用者內容：\n{user_prompt}"},
        ]

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=0.6 if mode != "slide" else 0.3,
            max_tokens=1400,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return (
            "目前未能成功連線到模型或 API Key 無效。\n"
            "你可以：\n"
            "1) 檢查 OpenAI API Key 是否正確/有額度，\n"
            "2) 先切換到「品牌草擬（免費）」模式使用不連網版本，\n"
            "3) 稍後再試。"
        )

# -------------------------------------------------
# Header（品牌定位）
# -------------------------------------------------
st.markdown("""
<div style="background:#f5f8ff;padding:1.1rem 1.25rem;border-radius:12px;border:1px solid #e2e8f0;">
  <h2 style="margin:0 0 .4rem 0;color:#0f172a;">你的專屬 AI 規劃助理，讓傳承更清楚、更從容</h2>
  <p style="margin:0;color:#334155;">
    把法律、稅務與保險的複雜度變簡單。用對話，就能快速產出藍圖、簡報摘要與下一步建議。
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# 模式切換 + 控制選項（頁面上方）
# -------------------------------------------------
st.markdown("### ✍️ 寫作控制")

m1, m2 = st.columns([1, 2])
with m1:
    mode = st.selectbox("模式", ["品牌草擬（免費）", "專家模式（用戶 API）"], index=0)

with m2:
    # 專家模式：使用者 API Key（存在 session，不落地）
    user_api_key = st.text_input(
        "OpenAI API Key（僅在本次會話記憶，不會儲存）" if mode == "專家模式（用戶 API）" else "（專家模式可輸入 API Key）",
        value=st.session_state.get("user_api_key", "") if mode == "專家模式（用戶 API）" else "",
        type="password",
        help="若輸入，生成將使用你的 Key 連線模型，費用算在你的帳號；不輸入則建議用『品牌草擬（免費）』模式。"
    )
    if mode == "專家模式（用戶 API）":
        st.session_state["user_api_key"] = user_api_key

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1:
    tone = st.selectbox("語氣", ["溫暖專業", "精準中性", "權威簡潔", "故事引導", "簡報要點"], index=0)
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
    add_brand = st.checkbox("加入品牌簽名（永傳家族辦公室）", value=True)
with c7:
    st.caption("金額單位以 **萬元（TWD）** 為主；可把工具試算/地圖的結果貼到下方再重寫。")

c8, c9 = st.columns([1, 1])
with c8:
    must = st.text_input("必含關鍵詞（逗號分隔）", value="")
with c9:
    avoid = st.text_input("避免詞（逗號分隔）", value="")

st.markdown("---")

# -------------------------------------------------
# 主區：輸入 / 產出
# -------------------------------------------------
col_in, col_out = st.columns([1, 1.2], gap="large")

with col_in:
    st.markdown("#### 📝 你的情境或指示")
    user_prompt = st.text_area(
        "請描述你要產出的內容（可貼上工具結果、客戶背景、限制條件）",
        height=220,
        placeholder="範例：幫我寫一段簡報開場，說明為何要預留稅源，語氣溫暖專業，200 字內…"
    )
    generate_btn = st.button("✨ 產出內容", type="primary", use_container_width=True)

    st.markdown("##### 快捷重寫")
    ca, cb, cc = st.columns(3)
    with ca: shorter_btn = st.button("更精簡")
    with cb: longer_btn  = st.button("更完整")
    with cc: slide_btn   = st.button("轉成簡報大綱")

# 狀態
if "copilot_output" not in st.session_state:
    st.session_state.copilot_output = ""

# 載入知識卡（免費模式/專家模式都會用）
cards = load_knowledge_cards()

with col_out:
    st.markdown("#### 🧾 產出結果")

    # 產出主流程
    if generate_btn and not user_prompt.strip():
        st.warning("請先輸入內容或情境，再按「產出內容」。")

    if generate_btn and user_prompt.strip():
        # 檢索命中知識
        top_docs = retrieve(user_prompt, cards, k=3)
        snippets = [tx[:800] for _, tx in top_docs]  # 取片段（避免過長）

        if mode == "品牌草擬（免費）":
            st.session_state.copilot_output = format_free_brand_output(
                tone, audience, purpose, fmt, length, must, avoid, user_prompt, snippets, add_brand
            )
        else:
            # 專家模式：需要 API Key
            api_key = st.session_state.get("user_api_key", "").strip()
            if not api_key:
                st.warning("請輸入 OpenAI API Key，或改用『品牌草擬（免費）』模式。")
                st.session_state.copilot_output = format_free_brand_output(
                    tone, audience, purpose, fmt, length, must, avoid, user_prompt, snippets, add_brand
                )
            else:
                system = build_system_prompt(tone, audience, purpose, fmt, length, add_brand)
                st.session_state.copilot_output = llm_generate_with_rag(
                    api_key=api_key,
                    user_prompt=user_prompt,
                    system_prompt=system,
                    retrieved_snippets=snippets,
                    mode="normal"
                )

    # 快捷重寫
    if st.session_state.copilot_output and shorter_btn:
        if mode == "專家模式（用戶 API）" and st.session_state.get("user_api_key"):
            system = build_system_prompt(tone, audience, purpose, fmt, length, add_brand)
            st.session_state.copilot_output = llm_generate_with_rag(
                api_key=st.session_state["user_api_key"],
                user_prompt=st.session_state.copilot_output,
                system_prompt=system,
                retrieved_snippets=[],
                mode="shorter"
            )
        else:
            st.session_state.copilot_output = st.session_state.copilot_output[:800]  # 超簡單精簡

    if st.session_state.copilot_output and longer_btn:
        if mode == "專家模式（用戶 API）" and st.session_state.get("user_api_key"):
            system = build_system_prompt(tone, audience, purpose, fmt, length, add_brand)
            st.session_state.copilot_output = llm_generate_with_rag(
                api_key=st.session_state["user_api_key"],
                user_prompt=st.session_state.copilot_output,
                system_prompt=system,
                retrieved_snippets=[],
                mode="longer"
            )
        else:
            st.session_state.copilot_output = st.session_state.copilot_output + "\n\n（已擴充：請於專家模式獲得更佳品質）"

    if st.session_state.copilot_output and slide_btn:
        if mode == "專家模式（用戶 API）" and st.session_state.get("user_api_key"):
            system = build_system_prompt(tone, audience, purpose, "條列重點", length, add_brand)
            st.session_state.copilot_output = llm_generate_with_rag(
                api_key=st.session_state["user_api_key"],
                user_prompt=st.session_state.copilot_output,
                system_prompt=system,
                retrieved_snippets=[],
                mode="slide"
            )
        else:
            # 簡易轉大綱
            bullets = [f"• {l.strip()}" for l in st.session_state.copilot_output.splitlines() if l.strip()]
            st.session_state.copilot_output = "\n".join(bullets[:15])

    # 顯示結果
    result = st.text_area("", value=st.session_state.copilot_output, height=420)

    # 下載
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "下載 .txt",
            data=(result or "").encode("utf-8"),
            file_name=f"AI_Copilot_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not result.strip()
        )
    with d2:
        if st.button("下載 PDF", use_container_width=True, disabled=not result.strip()):
            pdf_bytes = generate_pdf(
                content=result,
                title=f"{purpose}",
                logo_path=None,  # pdf_generator 會自動抓根目錄 logo.png
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
# 導覽
n1, n2, n3 = st.columns(3)
with n1: st.page_link("pages/Tools_AssetMap.py", label="🗺️ 家族資產地圖")
with n2: st.page_link("pages/Tools_EstateTax.py", label="🧮 遺產稅試算")
with n3: st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 保單策略建議")
