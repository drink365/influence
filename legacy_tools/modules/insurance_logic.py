# legacy_tools/modules/insurance_logic.py
# 保單策略引擎（純規則版）
# 供 pages/Tools_InsuranceStrategy.py 匯入：from legacy_tools.modules.insurance_logic import recommend_strategies

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Profile:
    age: int
    gender: str
    budget: float          # 預算（萬元）
    currency: str          # 幣別字串（顯示用途）
    pay_years: int         # 繳費年期（年）
    goals: List[str]       # 目標（中文關鍵字）


def _tier(budget_wan: float) -> str:
    """預算分級（萬元）"""
    if budget_wan >= 1000:
        return "超高"
    if budget_wan >= 300:
        return "高"
    if budget_wan >= 100:
        return "中"
    return "入門"


def _has(goal_keys: List[str], *needles: str) -> bool:
    g = "｜".join(goal_keys)
    return any(n in g for n in needles)


def _age_band(age: int) -> str:
    if age < 35:
        return "年輕族"
    if age <= 55:
        return "壯年族"
    if age <= 70:
        return "熟年族"
    return "高齡族"


def _fmt_amt(budget_wan: float, currency: str) -> str:
    # 僅做展示，實際保額由公司試算
    return f"{currency}{budget_wan:,.0f}萬（預算）"


def _base_set(profile: Profile) -> List[Dict]:
    """所有人通用的基礎組合（醫療/長照 + 基礎壽險）。"""
    items: List[Dict] = []

    # 醫療/長照
    if _has(profile.goals, "醫療", "長照", "保障"):
        items.append({
            "name": "醫療/長照保障模組",
            "why": "重大醫療與長照是家庭現金流風險的主要來源，先把底層保障補齊。",
            "fit": [profile.gender, _age_band(profile.age), "風險敏感族"],
            "description": (
                "以實支實付醫療＋長照日額為主；預算較高者可加重大疾病或失能扶助。"
                f" 建議先預留 {_fmt_amt(min(profile.budget, 100), profile.currency)} 於保障模組。"
            )
        })

    # 基礎壽險
    if _has(profile.goals, "保障", "家庭保障", "稅源", "傳承"):
        items.append({
            "name": "基礎壽險模組（定壽/終身壽險）",
            "why": "以最有效率的方式建立『萬一』保額，守住家庭與企業的基本盤。",
            "fit": [_age_band(profile.age), "家庭責任族"],
            "description": (
                "年輕/負債期以定期壽險放大保額；資產型客戶以終身壽險作為傳承底層。"
                f" 繳費期 {profile.pay_years} 年；保額依現金流及負債做動態規劃。"
            )
        })

    return items


def recommend_strategies(age: int, gender: str, budget: float, currency: str,
                         pay_years: int, goals: List[str]) -> List[Dict]:
    """
    輸入：年齡、性別、預算（萬元）、幣別字串、繳費年期、目標關鍵字（中文）
    輸出：策略清單（每筆含 name/why/fit/description）
    """
    p = Profile(age=age, gender=gender, budget=budget, currency=currency, pay_years=pay_years, goals=goals or [])
    res: List[Dict] = []

    tier = _tier(p.budget)

    # 1) 積累/傳承：增額終身壽險 / 分紅 / IUL 類
    if _has(p.goals, "傳承", "資產配置", "現金流", "稅源", "企業主", "家族"):
        if tier in ("高", "超高"):
            res.append({
                "name": "增額終身壽險（高現金價值型）",
                "why": "穩定累積保單現金價值，提供保單借款與傳承效率；可作為稅源或企業傳承準備。",
                "fit": [p.gender, _age_band(p.age), f"預算{tier}"],
                "description": (
                    f"建議以 {p.pay_years} 年繳設計增額結構，前3–5年加保；"
                    "後期可利用保單借款做資金調度或作為稅源預留。"
                )
            })
        else:
            res.append({
                "name": "分紅型終身壽險（穩健型）",
                "why": "兼顧保障與分紅，保費壓力較低，適合入門或逐步加碼。",
                "fit": [_age_band(p.age), f"預算{tier}"],
                "description": (
                    f"{p.pay_years} 年繳為主；預算成長後可追加繳或加保。"
                )
            })

    # 2) 退休/年金現金流
    if _has(p.goals, "退休", "年金", "現金流"):
        res.append({
            "name": "年金/變額年金（退休現金流）",
            "why": "把『一次資金』換成『一輩子現金流』，降低長壽風險與市場波動壓力。",
            "fit": [_age_band(p.age), "現金流導向"],
            "description": (
                "以保證年金＋紅利機制為基礎；若可承受波動，可搭配投資連結型年金提高上限。"
                f" 建議先預留 {_fmt_amt(min(max(p.budget-100, 0), p.budget), p.currency)} 作年金桶。"
            )
        })

    # 3) 資產保全/企業主
    if _has(p.goals, "企業", "股權", "房地產", "稅源", "債務"):
        res.append({
            "name": "保單融資／資產保全（企業主專用）",
            "why": "以保單現金價值作為備援資金；遇到稅務或短期流動性缺口，可低成本借款避免被動賣資產。",
            "fit": ["企業主", "高資產", f"預算{tier}"],
            "description": (
                "設計保單現金價值曲線，預留稅源；視銀行融資條件規劃 LTV 與利率區間，"
                "必要時搭配信託或保單質借機制。"
            )
        })

    # 4) 教育/定期目標
    if _has(p.goals, "教育", "子女", "學費"):
        res.append({
            "name": "教育金保單（含增額/年金）",
            "why": "把未來的大額支出（學費/留學）變成可預期的現金流。",
            "fit": ["父母族", _age_band(p.age)],
            "description": (
                "以增額終身或年金型做時間分層，設定領取節點與金額；保額與保費隨學齡滾動調整。"
            )
        })

    # 5) 入門或短年期預算
    if tier in ("入門", "中"):
        res.append({
            "name": "短年期定壽＋醫療附約（入門組合）",
            "why": "有限預算下，先以最低成本完成基本保障，逐步升級。",
            "fit": [_age_band(p.age), f"預算{tier}"],
            "description": (
                f"定期壽險 {p.pay_years} 年繳；醫療以實支實付為主。未來預算增加再轉增額終身。"
            )
        })

    # 6) 高齡或健康考量
    if p.age >= 60 or _has(p.goals, "長照"):
        res.append({
            "name": "長照/失能收入保障",
            "why": "針對高齡風險與照護費用，提供長期現金流補位。",
            "fit": ["熟年族/高齡族"],
            "description": "長照日額＋失能扶助（含豁免），與退休年金搭配提高抗風險能力。"
        })

    # 7) 最後：基礎組合（若尚未涵蓋）
    base = _base_set(p)
    # 去重（以名稱去重）
    existing = {x["name"] for x in res}
    for item in base:
        if item["name"] not in existing:
            res.append(item)

    # 若完全沒有辨識到任何目標，至少給入門建議
    if not res:
        res.append({
            "name": "基礎保障＋增額入門",
            "why": "從基礎保障開始，同步建立小額增額終身作為資產桶。",
            "fit": [_age_band(p.age)],
            "description": f"預算 { _fmt_amt(p.budget, p.currency) }；先 70% 基礎保障、30% 增額終身。"
        })

    return res
