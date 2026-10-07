"""pytest 共享：把仓库根加入 sys.path，使 tests 可导入 contracts/orchestrator。"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
