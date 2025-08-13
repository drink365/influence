# legacy_tools/modules/__init__.py
"""
Lightweight package init for legacy_tools.modules.

- 不在初始化時做任何副作用匯入（避免循環依賴 / ModuleNotFoundError）
- 提供相容別名：允許舊程式碼用 `from modules.xxx import yyy`
"""

import sys as _sys

# 相容舊寫法：把目前套件暱稱成 "modules"
# 這樣 `from modules.tax_constants import TaxConstants` 仍然可以運作
if __name__ != "modules":
    _sys.modules["modules"] = _sys.modules[__name__]

# 不主動匯入任何子模組，避免在 import 階段拉到未就緒的依賴
__all__ = []
