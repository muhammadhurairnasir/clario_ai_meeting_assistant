"""
fix_unicode.py
--------------
Replace emoji/Unicode characters in print() calls that break on Windows cp1252.
Run once: python fix_unicode.py
"""

import os
import re

FILES = [
    "models/database.py",
    "services/pipeline.py",
    "services/transcription.py",
    "services/summarization.py",
    "services/task_detection.py",
    "utils/visualization.py",
    "utils/helpers.py",
]

# Broad emoji + common symbols that cp1252 cannot encode
EMOJI = re.compile(
    "["
    "\U0001F000-\U0001FFFF"   # supplemental symbols
    "\U00002600-\U000027BF"   # misc symbols / dingbats
    "\U00002300-\U000023FF"   # technical symbols
    "\u2705\u274C\u26A0\u2764\u2B50\u2714\u2716"
    "]+",
    flags=re.UNICODE,
)

for path in FILES:
    if not os.path.exists(path):
        print(f"SKIP (not found): {path}")
        continue

    original = open(path, encoding="utf-8").read()
    cleaned  = EMOJI.sub("", original)

    if cleaned != original:
        open(path, "w", encoding="utf-8").write(cleaned)
        print(f"Fixed: {path}")
    else:
        print(f"OK (no changes): {path}")

print("Done.")
