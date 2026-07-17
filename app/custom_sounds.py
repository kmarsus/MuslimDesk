"""User-uploaded custom sounds (for azan or alarm), stored alongside the
bundled voices so they show up in the same picker. Files are copied into
the user's local app-data folder so they survive even if the original file
is later moved or deleted."""
from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from app.paths import user_data_dir

CUSTOM_SOUNDS_DIR = user_data_dir() / "custom_sounds"
CUSTOM_SOUNDS_FILE = user_data_dir() / "custom_sounds.json"

UPLOAD_SENTINEL = "__upload__"


@dataclass(frozen=True)
class CustomSound:
    id: str
    label: str
    file_name: str

    @property
    def path(self) -> str:
        return str(CUSTOM_SOUNDS_DIR / self.file_name)


def load_custom_sounds() -> list[CustomSound]:
    if not CUSTOM_SOUNDS_FILE.exists():
        return []
    try:
        raw = json.loads(CUSTOM_SOUNDS_FILE.read_text(encoding="utf-8"))
        return [CustomSound(**s) for s in raw]
    except Exception:
        return []


def _save(sounds: list[CustomSound]) -> None:
    CUSTOM_SOUNDS_FILE.write_text(
        json.dumps([asdict(s) for s in sounds], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_custom_sound(source_path: str) -> CustomSound:
    CUSTOM_SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    src = Path(source_path)
    sound_id = uuid.uuid4().hex[:8]
    dest_name = f"{sound_id}{src.suffix.lower()}"
    shutil.copyfile(src, CUSTOM_SOUNDS_DIR / dest_name)
    sound = CustomSound(id=f"custom:{sound_id}", label=src.stem, file_name=dest_name)
    sounds = load_custom_sounds()
    sounds.append(sound)
    _save(sounds)
    return sound


def remove_custom_sound(sound_id: str) -> None:
    sounds = load_custom_sounds()
    remaining = []
    for s in sounds:
        if s.id == sound_id:
            try:
                (CUSTOM_SOUNDS_DIR / s.file_name).unlink(missing_ok=True)
            except Exception:
                pass
        else:
            remaining.append(s)
    _save(remaining)


def find_custom_sound(sound_id: str) -> CustomSound | None:
    for s in load_custom_sounds():
        if s.id == sound_id:
            return s
    return None
