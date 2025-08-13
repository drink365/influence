# pages/Booking.py
# 預約洽談：必填驗證 + 偏好時間下拉 + Email 通知（支援 TLS/SSL）
# ------------------------------------------------------------
# st.secrets 設定範例（請放在部署環境的 Secrets）：
# [smtp]
# host = "smtp.gmail.com"
# port = 587
# username = "your_account@gmail.com"
# password = "your_app_password"
# to = "123@gracefo.com"
# use_tls = true
# # 可選：from = "your_account@gmail.com"   # 預設等於 username
# ------------------------------------------------------------

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from datetime import datetime, date
from typing import Optional, Tuple, Dict, Any

import streamlit as st

st.set_page_config(page_title="預約洽談｜永傳家族辦公室", layout="wide", initial_sidebar_state="collapsed")

# ---------- 樣式 ----------
st.markdown("""
<style>
  .card {background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;}
  .ok-badge {display:inline-block;background:#059669;color:white;padding:2px 8px;border-radius:999px;font-size:12px;}
  .warn-badge {display:inline-block;background:#b45309;color:white;padding:2px 8px;border-radius:999px;font-size:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <h2 style="margin:0 0 .5rem 0;">預約洽談</h2>
  <p style="margin:0;color:#334155">
    請留下您的聯絡資訊與想諮詢的重點，我們將於一個工作日內回覆。<br>
    ※ 個資僅用於聯繫與提供服務，不另作其他用途。
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- 讀取 SMTP 設定 ----------
def get_smtp() -> Optional[Dict[str, Any]]:
    """
    需提供 st.secrets["smtp"]，欄位：host, port, username, password, to
    可選：use_tls（預設 True）、from
    """
    smtp_cfg = st.secrets.get("smtp")
    if not smtp_cfg:
        return None
    required = ["host", "port", "username", "password", "to"]
    if any(k not in smtp_cfg for k in required):
        return None
    return smtp_cfg

SMTP_CFG = get_smtp()

if not SMTP_CFG:
    st.markdown(
        '<span class="warn-badge">提醒</span> 未設定通知信箱（SMTP）。'
        ' 仍可送出並在畫面顯示備份，但不會自動寄信。請於部署環境設定 <code>st.secrets["smtp"]</code>。',
        unsafe_allow_html=True
    )

# ---------- 表單 ----------
with st.form("booking_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("您的姓名 *", value="")
        email = st.text_input("Email（聯絡其一即可）", value="")
        phone = st.text_input("電話（聯絡其一即可）", value="")
    with col2:
        meet_date: date = st.date_input("偏好日期", value=date.today())
        time_pref = st.selectbox(
            "偏好時間（下拉）",
            ["不限", "上午（09:00–12:00）", "下午（13:00–17:00）", "晚上（19:00–21:00）"],
            index=0
        )
        channel = st.selectbox("會談方式", ["視訊（Google Meet）", "電話", "當面會談（會議室）"], index=0)

    focus = st.text_area(
        "想諮詢的重點（必填，至少 5 個字） *",
        height=140,
        placeholder="例：家族股權與遺產稅源預留，想先釐清保單與信託搭配…"
    )
    note = st.text_area("補充說明（選填）", height=100, placeholder="可提供方便聯絡時段、特殊需求等")
    agree = st.checkbox("我已閱讀並同意僅用於聯繫與服務之資料使用說明")

    submitted = st.form_submit_button("送出預約", type="primary", use_container_width=True)

# ---------- 驗證 ----------
def validate() -> Optional[str]:
    if not name.strip():
        return "請填寫姓名。"
    if not (email.strip() or phone.strip()):
        return "請至少提供 Email 或電話其中一項聯絡方式。"
    if len(focus.strip()) < 5:
        return "「想諮詢的重點」需至少 5 個字，請再多補充一些內容。"
    if not agree:
        return "請勾選同意資料使用說明。"
    return None

# ---------- 寄信（支援 TLS/SSL，自動 Reply-To） ----------
def send_mail(payload: Dict[str, Any]) -> Tuple[bool, str]:
    if not SMTP_CFG:
        return False, "未設定 SMTP（st.secrets['smtp'] 缺少必要欄位）"

    host = str(SMTP_CFG["host"])
    port = int(SMTP_CFG["port"])
    username = str(SMTP_CFG["username"])
    password = str(SMTP_CFG["password"])
    to_addr = str(SMTP_CFG["to"])
    use_tls = SMTP_CFG.get("use_tls", True)

    # From 建議使用與 SMTP 帳號相同的信箱，降低被擋風險
    from_addr = SMTP_CFG.get("from", username)

    msg = EmailMessage()
    msg["Subject"] = f"【新預約】{payload['name']}｜{payload['meet_date']}｜{payload['time_pref']}"
    msg["From"] = from_addr
    msg["To"] = to_addr

    # 使用者的 Email（若有）設為 Reply-To，方便一鍵回覆
    if payload.get("email"):
        msg["Reply-To"] = payload["email"]

    body = (
        "永傳家族辦公室：收到一筆新的預約。\n\n"
        f"【姓名】{payload['name']}\n"
        f"【Email】{payload['email'] or '-'}\n"
        f"【電話】{payload['phone'] or '-'}\n"
        f"【偏好日期】{payload['meet_date']}\n"
        f"【偏好時間】{payload['time_pref']}\n"
        f"【會談方式】{payload['channel']}\n"
        f"【想諮詢的重點】\n{payload['focus']}\n\n"
        f"【補充說明】\n{payload['note'] or '-'}\n\n"
        f"提交時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    msg.set_content(body)

    try:
        if port == 465 or (use_tls is False and port == 465):
            # SSL 直連
            with smtplib.SMTP_SSL(host, port, timeout=20) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            # 一般 + STARTTLS（常見：587）
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(username, password)
                server.send_message(msg)

        return True, f"已從 {from_addr} 寄至 {to_addr}"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"認證失敗：請檢查帳密或應用程式密碼（{e}）"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"收件人被拒絕：{e}"
    except smtplib.SMTPException as e:
        return False, f"SMTP 例外：{e}"
    except Exception as e:
        return False, f"未知錯誤：{e}"

# ---------- 提交處理 ----------
if submitted:
    err = validate()
    if err:
        st.error(err)
    else:
        data = {
            "name": name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "meet_date": meet_date.strftime("%Y-%m-%d"),
            "time_pref": time_pref,
            "channel": channel,
            "focus": focus.strip(),
            "note": note.strip(),
        }

        mailed, mail_msg = send_mail(data)

        st.success("✅ 我們已收到您的預約，將於一個工作日內與您聯繫。")
        if mailed:
            st.markdown(f'<span class="ok-badge">通知</span> {mail_msg}', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="warn-badge">通知</span> {mail_msg}', unsafe_allow_html=True)

        # 螢幕備份（避免未設 SMTP 時遺漏）
        with st.expander("查看本次提交內容（可複製備份）", expanded=False):
            st.json(data)

        st.markdown("---")
        st.markdown("如需立即聯繫，歡迎直接來信 123@gracefo.com 或前往官網 www.gracefo.com 。")
