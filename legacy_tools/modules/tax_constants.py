from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class TaxConstants:
    """遺產稅相關常數（以台灣 2025 年制為主）"""
    EXEMPT_AMOUNT: float = 1333  # 免稅額
    FUNERAL_EXPENSE: float = 138  # 喪葬費扣除額
    SPOUSE_DEDUCTION_VALUE: float = 553  # 配偶扣除額
    ADULT_CHILD_DEDUCTION: float = 56  # 每位子女扣除額
    PARENTS_DEDUCTION: float = 138  # 每位父母扣除額（最多2人）
    DISABLED_DEDUCTION: float = 693  # 重度身心障礙扣除額
    OTHER_DEPENDENTS_DEDUCTION: float = 56  # 其他撫養親屬扣除額
    TAX_BRACKETS: List[Tuple[float, float]] = field(default_factory=lambda: [
        (5621, 0.1),
        (11242, 0.15),
        (float('inf'), 0.2)
    ])
