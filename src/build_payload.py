#!/usr/bin/env python
"""Turn the xd corpus into payload.json for Second Language.

Reads src/raw/ (see fetch.py), writes src/payload.json. Pure stdlib.

Everything on the page is New York Times only: it is the one publication in
the corpus with continuous coverage from 1942 to 2025 under a single editorial
lineage, which is what makes the 1993 handover legible. The other 45
publications are counted once, for the coverage note, and otherwise unused.
"""
import os, io, json, zipfile, collections, statistics, re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "payload.json")

Y0, Y1 = 1942, 2025                      # NYT coverage in the corpus
YEARS = list(range(Y0, Y1 + 1))
VOWELS = set("AEIOU")

# Letter and vowel shares are taken over answers of three letters or more, the
# same cut as the English baseline. It discards 279 of 2,457,203 NYT answers.
MINLEN = 3
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The four editors of the New York Times crossword. These dates are the
# published record, not something the corpus knows: Farrar edited the first
# puzzle on 15 Feb 1942 and retired in 1969; Weng followed until 1977;
# Maleska from 1977 until his death in August 1993; Shortz's first puzzle
# ran 21 November 1993.
EDITORS = [
    {"name": "Margaret Farrar", "from": 1942, "to": 1969},
    {"name": "Will Weng", "from": 1969, "to": 1977},
    {"name": "Eugene T. Maleska", "from": 1977, "to": 1993},
    {"name": "Will Shortz", "from": 1993, "to": 2025},
]

# The two windows that define the retired and invented vocabularies. They are
# deliberately symmetric and leave 1980-1999 as an unjudged gap, so neither
# list can be an artefact of where a single boundary was drawn.
OLD_A, OLD_B = 1942, 1979
NEW_A, NEW_B = 2000, 2025
MIN_USES = 50

EXPLORER_N = 20000        # answers shipped to the lookup tool

# 75 JSON-safe printable characters, excluding the double quote and the
# backslash, used to encode one year's usage count in a single byte. The
# largest single-year count anywhere in the corpus is 45.
ALPHA = "".join(chr(c) for c in range(48, 127)
                if chr(c) not in ('"', chr(92)))[:75]


def norm(ans):
    """The corpus answer field, upper-cased and stripped to A-Z."""
    return re.sub(r"[^A-Z]", "", ans.strip().upper())


def read_clues():
    """Yield (year, answer, clue) for every NYT usage; count the rest."""
    zc = zipfile.ZipFile(os.path.join(RAW, "xd-clues.zip"))
    other_rows = 0
    other_pubs = set()
    with zc.open("xd/clues.tsv") as fh:
        t = io.TextIOWrapper(fh, encoding="utf-8", errors="replace")
        next(t)
        for line in t:
            p = line.rstrip("\n").split("\t", 3)
            if len(p) < 4:
                continue
            pub, yr, ans, clue = p
            if pub != "nyt":
                other_rows += 1
                other_pubs.add(pub)
                continue
            if not yr.isdigit():
                continue
            y = int(yr)
            if not (Y0 <= y <= Y1):
                continue
            w = norm(ans)
            if w:
                yield y, w, clue
    read_clues.other = (other_rows, len(other_pubs))


def english_baseline():
    """Letter and vowel profiles of English, from Norvig's web-corpus counts.

    Weighted by token frequency and restricted to alphabetic tokens of three
    letters or more - the same cut applied to the crossword side, where it
    removes 279 answers out of 2.46 million - so the two are comparable. The
    list's tail is unusable: it stops at 333,333 words and its last entries
    are OCR noise. Its head, which is all a frequency-weighted mean depends
    on, is sound.
    """
    lt, tot = collections.Counter(), 0
    vw, nw = 0.0, 0
    with open(os.path.join(RAW, "count_1w.txt"), encoding="utf-8") as f:
        for line in f:
            w, c = line.rstrip("\n").split("\t")
            if not w.isalpha() or len(w) < MINLEN:
                continue
            c = int(c)
            W = w.upper()
            for ch in W:
                lt[ch] += c
            tot += len(W) * c
            nw += c
            vw += sum(ch in VOWELS for ch in W) / len(W) * c
    letters = [round(lt[ch] / tot * 100, 4) for ch in AZ]
    return letters, round(vw / nw * 100, 3)


def letter_profile(counter):
    lt, tot = collections.Counter(), 0
    for w, k in counter.items():
        if len(w) < MINLEN:
            continue
        for ch in w:
            lt[ch] += k
        tot += len(w) * k
    return [round(lt[ch] / tot * 100, 4) for ch in AZ]


def encode(series):
    """84 per-year counts -> an 84-character string, one byte per year."""
    return "".join(ALPHA[min(v, len(ALPHA) - 1)] for v in series)


def main():
    by_year = collections.defaultdict(collections.Counter)

    for y, w, _clue in read_clues():
        by_year[y][w] += 1
    other_rows, other_pubs = read_clues.other

    totals = collections.Counter()
    first, last = {}, {}
    for y in YEARS:
        for w, k in by_year[y].items():
            totals[w] += k
            first.setdefault(w, y)
            last[w] = y

    def window(a, b):
        c = collections.Counter()
        for y in range(a, b + 1):
            c.update(by_year[y])
        return c

    old, new = window(OLD_A, OLD_B), window(NEW_A, NEW_B)

    retired = sorted(((w, n) for w, n in old.items()
                      if n >= MIN_USES and new[w] == 0), key=lambda t: -t[1])
    invented = sorted(((w, n) for w, n in new.items()
                       if n >= MIN_USES and old[w] == 0), key=lambda t: -t[1])

    # second pass: keep one clue per featured word
    featured = set(w for w, _ in retired) | set(w for w, _ in invented)
    clue_of = collections.defaultdict(list)
    for y, w, clue in read_clues():
        if w in featured:
            clue_of[w].append((y, clue.strip()))

    def pick_clue(w):
        """The earliest clue of usable length.

        Earliest, because for the retired words that means the 1940s and 50s,
        when the Times still wrote its clues as complete sentences - and
        because the pre-1964 puzzles are the part of the corpus whose
        copyright was never renewed. One clue per word, dated, as
        illustration.
        """
        cs = sorted(clue_of.get(w, []))
        for y, c in cs:
            if 18 <= len(c) <= 95:
                return {"y": y, "c": c}
        return {"y": cs[0][0], "c": cs[0][1]} if cs else None

    def series_of(w):
        return [by_year[y].get(w, 0) for y in YEARS]

    def entry(w, n):
        return {"w": w, "n": n, "tot": totals[w], "f": first[w], "l": last[w],
                "s": encode(series_of(w)), "q": pick_clue(w)}

    retired_e = [entry(w, n) for w, n in retired]
    invented_e = [entry(w, n) for w, n in invented]

    # per-year series
    enable = set()
    with open(os.path.join(RAW, "enable1.txt"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                enable.add(line.strip().upper())

    usages, distinct, vowel, enshare, meanlen = [], [], [], [], []
    for y in YEARS:
        c = by_year[y]
        tot = sum(c.values())
        usages.append(tot)
        distinct.append(len(c))
        vn = sum(k for w, k in c.items() if len(w) >= MINLEN)
        vowel.append(round(sum(sum(ch in VOWELS for ch in w) / len(w) * k
                               for w, k in c.items() if len(w) >= MINLEN)
                           / vn * 100, 3))
        enshare.append(round(sum(k for w, k in c.items() if w in enable)
                             / tot * 100, 3))
        meanlen.append(round(sum(len(w) * k for w, k in c.items()) / tot, 3))

    eng_letters, eng_vowel = english_baseline()

    eras = {}
    for e in EDITORS:
        # An era runs from its start year through the year before the next
        # editor's start, so handover years are never double counted.
        nxt = [x["from"] for x in EDITORS if x["from"] > e["from"]]
        end = (nxt[0] - 1) if nxt else Y1
        c = window(e["from"], end)
        eras[e["name"]] = {"from": e["from"], "to": end,
                           "letters": letter_profile(c),
                           "usages": sum(c.values()), "distinct": len(c),
                           "top": [w for w, _ in c.most_common(24)]}

    top = totals.most_common(EXPLORER_N)
    ex_words = [w for w, _ in top]
    ex_series = [encode(series_of(w)) for w in ex_words]

    ret_last = sorted(last[w] for w, _ in retired)
    inv_first = sorted(first[w] for w, _ in invented)

    payload = {
        "built": "2026-09-27",
        "years": YEARS,
        "editors": EDITORS,
        "alpha": ALPHA,
        "coverage": {"usages": usages, "distinct": distinct,
                     "meanlen": meanlen, "totalUsages": sum(usages),
                     "totalDistinct": len(totals),
                     "otherRows": other_rows, "otherPubs": other_pubs},
        "vowel": {"series": vowel, "english": eng_vowel},
        "enable": {"series": enshare, "n": len(enable)},
        "letters": {"english": eng_letters,
                    "eras": dict((k, v["letters"]) for k, v in eras.items())},
        "eras": eras,
        "windows": {"oldFrom": OLD_A, "oldTo": OLD_B, "newFrom": NEW_A,
                    "newTo": NEW_B, "minUses": MIN_USES},
        "retired": retired_e,
        "invented": invented_e,
        "hinge": {
            "retiredMedianLast": statistics.median(ret_last),
            "inventedMedianFirst": statistics.median(inv_first),
            "retiredLastHist": dict(collections.Counter(ret_last)),
            "inventedFirstHist": dict(collections.Counter(inv_first)),
        },
        "explorer": {"words": ex_words, "series": ex_series, "n": EXPLORER_N,
                     "covers": round(sum(n for _, n in top)
                                     / sum(totals.values()) * 100, 2),
                     "minUses": top[-1][1]},
    }

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)

    print("retired      %4d words, %6d uses"
          % (len(retired_e), sum(e["n"] for e in retired_e)))
    print("invented     %4d words, %6d uses"
          % (len(invented_e), sum(e["n"] for e in invented_e)))
    print("hinge        retired median last %s / invented median first %s"
          % (payload["hinge"]["retiredMedianLast"],
             payload["hinge"]["inventedMedianFirst"]))
    print("explorer     %d answers, %.1f%% of usages, min %d uses"
          % (EXPLORER_N, payload["explorer"]["covers"],
             payload["explorer"]["minUses"]))
    print("payload.json %.2f MB" % (os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()
