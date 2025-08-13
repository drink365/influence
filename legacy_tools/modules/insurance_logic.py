# legacy_tools/modules/insurance_logic.py
# 保單策略引擎（新版專用，已統一用語：定期壽險；前期加保文案依年期自動調整，且保留逗號）
# API：
#   recommend_strategies(age, gender, budget, currency, pay_years, goals)
#   導出 FX_USD_TWD（供頁面顯示分級換算一致）

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

__all__ = ["recommend_strategies", "FX_USD_TWD"]

# === 匯率設定（可改為讀 secrets；此處提供預設）===
FX_USD_TWD: float = 31.0  # 1 萬 USD ≈ 31 萬 TWD（分級判斷用）

# === 幫手：幣別正規化 ===
def _normalize_currency(cur: str | None) -> Tuple[str, str, float]:
    """
    回傳 (code, symbol, to_twd_multiplier)
    輸入 budget 單位是「萬 <currency>」，轉換成「萬 TWD」用 multiplier：
      - TWD: 1.0
      - USD: FX_USD_TWD
    """
    c = (cur or "TWD").upper()
    if c == "USD":
        return "USD", "US$", FX_USD_TWD
    return "TWD", "NT$", 1.0

@dataclass
class Profile:
    age: int
    gender: str
    total_budget_wan: float     # 總預算（萬，依 currency）
    currency: str               # 'TWD' / 'USD'
    currency_symbol: str        # 'NT$' / 'US$'
    to_twd_multiplier: float    # 轉換到「萬TWD」的倍率
    pay_years: int
    goals: List[str]

# === 分級（門檻以「萬TWD」為基準）===
def _tier(total_budget_wan_in_twd: float) -> str:
    """
    門檻（單位：萬 TWD）
      - 高端：≥ 1000 萬
      - 進階：300–999 萬
      - 標準：100–299 萬
      - 入門：< 100 萬
    """
    if total_budget_wan_in_twd >= 1000:
        return "高端"
    if total_budget_wan_in_twd >= 300:
        return "進階"
    if total_budget_wan_in_twd >= 100:
        return "標準"
    return "入門"

def _has(goal_keys: List[str], *needles: str) -> bool:
    g = "｜".join(goal_keys or [])
    return any(n in g for n in needles)

def _age_band(age: int) -> str:
    if age < 35:
        return "年輕族"
    if age <= 55:
        return "壯年族"
    if age <= 70:
        return "熟年族"
    return "高齡族"

def _fmt_amt_wan(amount_wan: float, symbol: str) -> str:
    return f"{symbol}{amount_wan:,.0f}萬"

def _accum_phrase(pay_years: int) -> str:
    """
    依繳費年期生成「前期加保」文案：
      - 1 年：不顯示
      - >= 2 年：『前期視資金狀況加保；』
    """
    if pay_years >= 2:
        return "前期視資金狀況加保；"
    return ""  # 1 年不顯示

# === 基礎模組 ===
def _base_set(p: Profile) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    # 醫療/長照
    if _has(p.goals, "醫療", "長照", "保障"):
        items.append({
            "name": "醫療/長照保障模組",
            "why": "重大醫療與長照是家庭現金流風險的來源，先把底層保障補齊。",
            "fit": [p.gender, _age_band(p.age), "風險敏感族"],
            "description": (
                "以實支實付醫療＋長照日額為主；預算較高可加重大疾病或失能扶助。"
                f" 建議先預留 {_fmt_amt_wan(min(p.total_budget_wan, 100), p.currency_symbol)} 於保障模組。"
            )
        })
    # 基礎壽險（用語統一：定期壽險）
    if _has(p.goals, "保障", "家庭保障", "稅源", "傳承"):
        items.append({
            "name": "基礎壽險模組（定期壽險 / 終身壽險）",
            "why": "以有效率的方式建立『萬一』保額，守住家庭與企業的基本盤。",
            "fit": [_age_band(p.age), "家庭責任族"],
            "description": (
                "年輕/負債期以定期壽險放大保額；資產型客戶以終身壽險作為傳承底層。"
                f" 繳費期 {p.pay_years} 年；保額依現金流及負債動態規劃。"
            )
        })
    return items

# === 引擎 ===
def _engine(p: Profile) -> List[Dict[str, Any]]:
    res: List[Dict[str, Any]] = []
    budget_in_twd_wan = p.total_budget_wan * p.to_twd_multiplier  # 以「萬TWD」計算分級
    tier = _tier(budget_in_twd_wan)

    # 1) 積累/傳承
    if _has(p.goals, "傳承", "資產配置", "現金流", "稅源", "企業主", "家族"):
        if tier in ("進階", "高端"):
            # 依年期調整前期加保句子（1 年不顯示；>=2 年顯示）
            accum = _accum_phrase(p.pay_years)
            desc = (
                f"建議以 {p.pay_years} 年繳設計增額結構，"
                f"{accum}"
                "後期可利用保單借款做資金調度或作為稅源預留。"
            )
            res.append({
                "name": "增額終身壽險（高現金價值型）",
                "why": "穩定累積保單現金價值，提供保單借款與傳承效率；可作為稅源或企業傳承準備。",
                "fit": [p.gender, _age_band(p.age), f"{tier}預算"],
                "description": desc
            })
        else:
            res.append({
                "name": "分紅型終身壽險（穩健型）",
                "why": "兼顧保障與分紅，保費壓力較低，適合入門或逐步加碼。",
                "fit": [_age_band(p.age), f"{tier}預算"],
                "description": f"{p.pay_years} 年繳為主；預算成長後可追加繳或加保。"
            })

    # 2) 退休/年金現金流
    if _has(p.goals, "退休", "年金", "現金流"):
        bucket = max(p.total_budget_wan - 100, 0)  # 示意切分
        res.append({
            "name": "年金確定收入（退休現金流）",
            "why": "把一次資金換成長期現金流，降低長壽風險與市場波動壓力。",
            "fit": [_age_band(p.age), "現金流導向"],
            "description": (
                "以保證年金＋紅利機制為基礎；若可承受波動，可搭配投資連結型年金提高上限。"
                f" 建議預留 {_fmt_amt_wan(bucket, p.currency_symbol)} 作年金桶。"
            )
        })

    # 3) 資產保全/企業主
    if _has(p.goals, "企業", "股權", "房地產", "稅源", "債務"):
        res.append({
            "name": "保單融資／資產保全（企業主專用）",
            "why": "以保單現金價值作為備援資金；遇短期流動性或稅務缺口，可低成本借款避免被動賣資產。",
            "fit": ["企業主", f"{tier}預算"],
            "description": (
                "設計保單現金價值曲線，預留稅源；視銀行融資條件規劃 LTV 與利率，"
                "必要時搭配信託或保單質借機制。"
            )
        })

    # 4) 教育
    if _has(p.goals, "教育", "子女", "學費"):
        res.append({
            "name": "教育金保單（含增額/年金）",
            "why": "把未來的大額學費變成可預期的現金流。",
            "fit": ["父母族", _age_band(p.age)],
            "description": "以增額終身或年金型做時間分層，設定領取節點與金額；保額與保費隨學齡滾動調整。"
        })

    # 5) 入門／標準預算
    if tier in ("入門", "標準"):
        res.append({
            "name": "短年期定期壽險＋醫療附約（入門組合）",
            "why": "有限預算下，先以最低成本完成基本保障，之後再升級。",
            "fit": [_age_band(p.age), f"{tier}預算"],
            "description": f"定期壽險 {p.pay_years} 年繳；醫療以實支實付為主。未來預算增加再轉增額終身。"
        })

    # 6) 高齡或長照需求
    if p.age >= 60 or _has(p.goals, "長照"):
        res.append({
            "name": "長照/失能收入保障",
            "why": "針對高齡風險與照護費用，提供長期現金流補位。",
            "fit": ["熟年族/高齡族"],
            "description": "長照日額＋失能扶助（含豁免），與退休年金搭配提高抗風險能力。"
        })

    # 7) 基礎模組補位
    base = _base_set(p)
    existing = {x["name"] for x in res}
    for item in base:
        if item["name"] not in existing:
            res.append(item)

    if not res:
        res.append({
            "name": "基礎保障＋增額入門",
            "why": "從基礎保障開始，同步建立小額增額終身作為資產桶。",
            "fit": [_age_band(p.age)],
            "description": (
                f"建議預算 {_fmt_amt_wan(p.total_budget_wan, p.currency_symbol)}；"
                "先 70% 基礎保障、30% 增額終身。"
            )
        })
    return res

# === 公開 API（新版）===
def recommend_strategies(age: int,
                         gender: str,
                         budget: float,
                         currency: str,
                         pay_years: int,
                         goals: List[str]) -> List[Dict[str, Any]]:
    """
    參數：
      - age: 年齡（int）
      - gender: 性別（字串，自由填：男/女/不分…）
      - budget: 總預算「萬 <currency>」，例：100 代表該幣別 100 萬
      - currency: 'TWD' 或 'USD'
      - pay_years: 繳費年期（年）
      - goals: 目標關鍵字列表（中文），例：["傳承", "退休", "醫療"]

    回傳：策略清單（每筆含 name/why/fit/description）
    """
    code, symbol, to_twd = _normalize_currency(currency)
    p = Profile(
        age=int(age),
        gender=str(gender),
        total_budget_wan=float(budget),
        currency=code,
        currency_symbol=symbol,
        to_twd_multiplier=float(to_twd),
        pay_years=int(pay_years),
        goals=[str(g) for g in (goals or [])],
    )
    return _engine(p)
