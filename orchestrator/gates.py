"""owner_gate —— interrupt 式人环原语（6 步②④）。

程序挂起，等 owner 一句话 resume（0 token）。owner 的拍板写入 decision_record 契约。
生产实现应把 wait() 接到 owner 可见的通道（控制台 / 消息 / 回调）；测试注入假决策。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class OwnerGate:
    """人环闸门：挂起 → 等 owner 一句话 → resume。"""

    notify: Callable[[str], None] = lambda msg: print(f"[owner_gate] {msg}")
    _pending: dict | None = None
    _decided_at: str | None = None

    def wait(self, question: str) -> dict:
        """挂起等 owner 拍板。返回 decision_record 内容。"""
        self.notify(question)
        # 生产：此处阻塞等外部 resume()；测试通过注入决策提前返回。
        if self._pending is None:
            raise RuntimeError("owner_gate: 未收到 owner 决策（生产环境由外部 resume() 注入）")
        decision = self._pending
        self._pending = None
        decision["decided_at"] = decision.get("decided_at") or time.strftime("%Y-%m-%dT%H:%M:%S%z")
        return decision

    def resume(self, decision: dict) -> None:
        """owner 一句话拍板。decision 需含 decision / options / rationale / owner。"""
        self._pending = decision
        self._decided_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
