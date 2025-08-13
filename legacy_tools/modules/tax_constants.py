# legacy_tools/modules/tax_constants.py
# 來源：依照使用者在 estate-tax repo 的設定整理
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple
import math

# ---- 你的原始級距（上限、稅率）----
# 單位：萬元
DEFAULT_TAX_BRACKETS: List[Tuple[float, float]] = [
    (5621, 0.10),          # 0 ～ 5,621 萬 → 10%
    (11242, 0.15),         # 5,621 ～ 11,242 萬 → 15%
    (math.inf, 0.20),      # 11,242 萬以上 → 20%
]

# ---- 相容我們現有計算器使用的格式（下限、上限、稅率）----
DEFAULT_INHERITANCE_TAX_BRACKETS: List[Tuple[float, float, float]] = [
    (0, 5621, 0.10),
    (5621, 11242, 0.15),
    (11242, math.inf, 0.20),
]

@dataclass
class TaxConstants:
    """遺產稅相關常數（單位皆為「萬元」）"""

    # 免稅額與各項扣除額
    EXEMPT_AMOUNT: float = 1333               # 免稅額
    FUNERAL_EXPENSE: float = 138              # 喪葬費扣除額
    SPOUSE_DEDUCTION_VALUE: float = 553       # 配偶扣除額
    ADULT_CHILD_DEDUCTION: float = 56         # 每位子女扣除額
    PARENTS_DEDUCTION: float = 138            # 父母扣除額
    DISABLED_DEDUCTION: float = 693           # 重度身心障礙扣除額
    OTHER_DEPENDENTS_DEDUCTION: float = 56    # 其他撫養扣除額

    # 稅率級距（同時提供兩種結構，確保相容）
    TAX_BRACKETS: List[Tuple[float, float]] = field(
        default_factory=lambda: DEFAULT_TAX_BRACKETS.copy()
    )
    INHERITANCE_TAX_BRACKETS: List[Tuple[float, float, float]] = field(
        default_factory=lambda: DEFAULT_INHERITANCE_TAX_BRACKETS.copy()
    )
