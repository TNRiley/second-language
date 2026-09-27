#!/usr/bin/env python
"""Download every input Second Language needs, into src/raw/.

Nothing here is committed - .gitignore excludes raw/ - because the xd clue
archive alone is 93 MB. Re-run this and build_payload.py to rebuild the page
from scratch. All four sources are stable public URLs; the xd archives are
regenerated periodically, so figures may drift by a puzzle or two.
"""
import os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(HERE, "raw")

SOURCES = [
    # the corpus: 8.0M answer/clue usages across 46 publications, 1917-2026
    ("xd-clues.zip",   "https://xd.saul.pw/xd-clues.zip"),
    # puzzle-level metadata: date, size, author, editor, copyright
    ("xd-metadata.zip","https://xd.saul.pw/xd-metadata.zip"),
    # ENABLE: the public-domain word-game lexicon, 172,823 entries.
    # Used only as a yes/no test of "is this an ordinary English word".
    ("enable1.txt",    "https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt"),
    # Norvig's word counts from the Google Web Trillion Word Corpus:
    # 333,333 words, 588 billion tokens. Used for the English letter and
    # vowel baseline only - see REBUILD.md for why its tail is unusable.
    ("count_1w.txt",   "https://norvig.com/ngrams/count_1w.txt"),
]

def main():
    os.makedirs(RAW, exist_ok=True)
    for name, url in SOURCES:
        dest = os.path.join(RAW, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print("have   %-18s %10d bytes" % (name, os.path.getsize(dest)))
            continue
        print("get    %-18s %s" % (name, url))
        req = urllib.request.Request(url, headers={"User-Agent": "second-language/1.0"})
        with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        print("       %-18s %10d bytes" % (name, os.path.getsize(dest)))

if __name__ == "__main__":
    sys.exit(main())
