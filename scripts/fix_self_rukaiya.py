"""One-off: fix self_rukaiya.json data issues:
1. Entry 14 (index 13)'s full procedural text was stored in the unused
   "untitled" field (never rendered by the app) instead of a displayed
   field -- move it to "bangla_translation".
2. Add missing repetition counts to entries the user identified as lacking
   them (indices 0, 1, 4, 5, 6, 14), matching the counts they specified.
"""
import json
from pathlib import Path

PATH = Path(r"C:\Claude\MuslimDesk\assets\data\self_rukaiya.json")
data = json.loads(PATH.read_text(encoding="utf-8"))

# 1. Move entry 14 (index 13)'s content out of "untitled" into "bangla_translation".
e13 = data[13]
assert e13["title"].startswith("১৪"), e13["title"]
if e13["untitled"] and not e13["bangla_translation"]:
    e13["bangla_translation"] = e13["untitled"]
    e13["untitled"] = ""

# 2. Add missing counts.
count_additions = {
    0: "যেকোনো রোগের জন্য সূরা ফাতিহা: ১, ৩ অথবা ৭ বার পড়া যায়।",
    1: "রোগীর সুস্থ হওয়ার দোয়া: ৭ বার পড়তে হবে।",
    4: "ফোঁড়া, গোটা ইত্যাদির জন্য দোয়াটি ৩ বার পড়তে হবে।",
    5: "অসুস্থ ব্যক্তির শরীরে ডান হাত রেখে দোয়াটি ৩ বার পড়তে হবে।",
    6: "অসুস্থ ব্যক্তিকে দেখতে গিয়ে এই দোয়াটি ৩ বার পড়া।",
    14: "প্রতিটি আয়াত ৩ বার করে পড়তে হবে। পড়ার পূর্বে সূরা ফাতেহা পড়ে নেওয়া উত্তম।",
}
for idx, new_rules in count_additions.items():
    title = data[idx]["title"]
    data[idx]["rules"] = new_rules
    print(f"Updated index {idx} ({title.strip()}): {new_rules}")

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Saved.")
