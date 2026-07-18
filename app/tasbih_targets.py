"""Multiple named tasbih targets (e.g. "সুবহানাল্লাহ: ৩৩ বার"), run in
sequence: the active targets are counted one after another, and each turns
"completed" once its count reaches its target."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field

from app.paths import user_data_dir

TASBIH_FILE = user_data_dir() / "tasbih_targets.json"


@dataclass
class TasbihTarget:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    target: int = 33
    count: int = 0
    active: bool = True

    @property
    def completed(self) -> bool:
        return self.count >= self.target


_DEFAULTS = [
    TasbihTarget(name="সুবহানাল্লাহ", target=33),
    TasbihTarget(name="আলহামদুলিল্লাহ", target=33),
    TasbihTarget(name="আল্লাহু আকবার", target=34),
]


def load_targets() -> list[TasbihTarget]:
    if not TASBIH_FILE.exists():
        save_targets(_DEFAULTS)
        return [TasbihTarget(**asdict(t)) for t in _DEFAULTS]
    try:
        raw = json.loads(TASBIH_FILE.read_text(encoding="utf-8"))
        return [TasbihTarget(**t) for t in raw]
    except Exception:
        return []


def save_targets(targets: list[TasbihTarget]) -> None:
    TASBIH_FILE.write_text(
        json.dumps([asdict(t) for t in targets], ensure_ascii=False, indent=2), encoding="utf-8"
    )
