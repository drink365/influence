# pages/AI_Copilot.py
# 🪄 AI 行銷助手（免 API）：輸入重點 → 一鍵產生 FB 貼文 / LINE 私訊 / 演講開場
import streamlit as st
from datetime import date

st.set_page_config(page_title="AI 行銷助手（免 API）", page_icon="🪄", layout="wide")

st.title("🪄 AI 行銷助手（免 API）")
st.caption("適合壯世代與傳統業務員：把重點輸入，就能產出可用文案。支援 Facebook 貼文、LINE 私訊與演講開場。")

with st.form("mk"):
    c1, c2 = st.columns(2)
    with c1:
        audience = st.selectbox("目標受眾", ["企業主", "高資產家庭", "年輕上班族", "一般家庭"], index=0)
        channel = st.selectbox("產出格式", ["Facebook 貼文", "LINE 私訊", "演講開場"], index=0)
        tone = st.selectbox("語氣風格", ["溫暖專業", "簡潔有力", "穩重可信", "親切口語"], index=0)
    with c2:
        topic = st.text_input("主題 / 服務（例：傳承規劃、遺產稅試算、壯世代轉型）", "傳承規劃")
        key_points = st.text_area("關鍵重點（每行一點）", "1. 有數據與圖像化工具\n2. 可先做風險盤點\n3. 提供預約諮詢")
        cta = st.text_input("CTA 呼籲動作", "私訊我預約 30 分鐘諮詢")
        brand = st.text_input("品牌簽名（可留空）", "永傳家族辦公室｜影響力傳承計畫")
    submit = st.form_submit_button("產生內容")

def bullets(text: str):
    return [s.strip(" 　-•\t1234567890.).、") for s in text.splitlines() if s.strip()]

def style_wrap(text: str, tone: str) -> str:
    if tone == "簡潔有力":
        return text.replace("，", "，").replace("。", "。")
    if tone == "穩重可信":
        return text
    if tone == "親切口語":
        # 輕量口語化
        t = text.replace("我們", "我").replace("提供", "可以幫你").replace("將", "會")
        return t
    return text  # 溫暖專業（預設）

def gen_fb(aud, topic, pts, cta, brand):
    title = f"【{topic}｜{aud}必修】"
    head = f"你是否也在想：{pts[0] if pts else '如何更有效把傳承做對？'}"
    lines = [title, head, ""]
    lines += [f"・{p}" for p in pts]
    lines += ["", f"👉 {cta}"]
    if brand:
        hash_tag = "#" + " #".join([s for s in brand.replace("｜", " ").split() if s.strip()])
        lines += ["", hash_tag]
    return "\n".join(lines)

def gen_line(aud, topic, pts, cta):
    lines = [f"{aud}您好，我是 Grace。剛整理了「{topic}」要點："]
    lines += [f"• {p}" for p in pts]
    lines += ["", f"如果方便，我可以用 15–30 分鐘跟您快速說明重點。{cta}"]
    return "\n".join(lines)

def gen_opening(aud, topic, pts):
    lines = [f"各位好，今天想跟大家談「{topic}」。"]
    lines += [f"多數{aud}常遇到以下情況："]
    for i, p in enumerate(pts[:3] if pts else ["缺少清楚方法", "資訊分散難比較", "不知道從哪一步開始"], 1):
        lines += [f"{i}. {p}"]
    lines += ["今天我會用真實案例與工具，讓大家帶得走、做得到。"]
    return "\n".join(lines)

if submit:
    pts = bullets(key_points)
    if channel == "Facebook 貼文":
        out = gen_fb(audience, topic, pts, cta, brand)
    elif channel == "LINE 私訊":
        out = gen_line(audience, topic, pts, cta)
    else:
        out = gen_opening(audience, topic, pts)

    out = style_wrap(out, tone)
    st.markdown("### ✍️ 產出結果")
    st.code(out, language="markdown")
    st.download_button("下載為 .txt", data=out, file_name=f"mk_{date.today()}.txt")

st.markdown("---")
st.caption("小提醒：若要更進一步（如自動套入你品牌語調、案例庫、保單名稱），之後可接上自家模板或 OpenAI API。")
