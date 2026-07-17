"""One-off: convert the Dart daily_azkar.dart list literal into JSON.

The Dart list literal is already JSON-shaped (double-quoted keys/values,
\\n escape sequences) -- we just need to slice out the `[ ... ]` and let
json.loads parse it, with a couple of textual repairs for Dart-only syntax
(trailing commas, escaped single quotes) if json.loads first fails.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(r"C:\Claude\app-IOM-Daily-Azkar\lib\features\iom_daily_azkar\data\daily_azkar.dart")

text = SRC.read_text(encoding="utf-8")


def extract_list(marker: str) -> list:
    start = text.index(marker) + len(marker) - 1  # index of '['
    depth = 0
    i = start
    in_string = False
    escape = False
    end = None
    while i < len(text):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        i += 1

    if end is None:
        print(f"Could not find matching bracket for {marker}", file=sys.stderr)
        sys.exit(1)

    raw = text[start:end + 1]
    raw = re.sub(r",\s*([\]}])", r"\1", raw)  # Dart allows trailing commas; JSON doesn't.

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Parse failed for {marker}: {e}", file=sys.stderr)
        ctx = raw[max(0, e.pos - 120):e.pos + 120]
        print("Context:\n", ctx, file=sys.stderr)
        sys.exit(1)


daily_azkar = extract_list("dailyAzkarRawData = [")
self_rukaiya = extract_list("selfRukaiyaRawData = [")

print(f"Parsed {len(daily_azkar)} daily azkar entries, {len(self_rukaiya)} self-rukaiya entries")

out_dir = Path(r"C:\Claude\MuslimDesk\assets\data")
(out_dir / "daily_azkar.json").write_text(
    json.dumps(daily_azkar, ensure_ascii=False, indent=2), encoding="utf-8"
)
(out_dir / "self_rukaiya.json").write_text(
    json.dumps(self_rukaiya, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Wrote daily_azkar.json and self_rukaiya.json")
