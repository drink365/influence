# legacy_tools/modules/__init__.py
from .pdf_generator import generate_pdf
from .insurance_logic import recommend_strategies, FX_USD_TWD

__all__ = [
    "generate_pdf",
    "recommend_strategies",
    "FX_USD_TWD",
]
