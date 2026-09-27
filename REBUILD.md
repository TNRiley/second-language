# Rebuilding Second Language

Enough to reproduce this project from scratch with a shell, Python 3 and no other context.

---

## 1. What is being built

A single self-contained HTML page about the answer vocabulary of the New York Times
crossword, 1942 to 2025.

The finding it exists to show: **the Times replaced almost its entire distinctive
crossword vocabulary within about a year of the 1993 editor handover, and the letter
distribution did not move at all.**

Concretely, three claims, each with its own section:

1. **The swap.** 56 answers were printed at least 50 times in 1942–1979 and not once in
   2000–2025 (`ASOR`, `ENARE`, `OSAR`, `PROA`, `IRADE` — lakes, coins, boats, gazetteer
   entries). 161 answers were never printed before 1980 and are now used at least 50 times
   (`SNL`, `SSN`, `EDU`, `TSA`, `IMAC`, `IKEA` — acronyms, brands, television).
2. **The hinge.** The median retired word was last printed in **1993**; the median invented
   word first appeared in **1994**. Eugene Maleska died in August 1993 and Will Shortz's
   first puzzle ran 21 November 1993. Fourteen of the 56 were last seen in 1993 itself; 22
   of the 161 arrived in 1994, the largest single year.
3. **The constraint.** The letter profile of the Farrar era correlates with the Shortz era
   at **r = 0.997**, while each correlates with English at only 0.96–0.97. Crossword answers
   are 40.7%–42.7% vowels in every year on record; English is 37.1%.

A fourth, smaller finding: the share of answers that are ordinary English words was flat at
66–68% from 1942 to 1993, then fell to 53% by 2011 and has recovered only to 57%.

---

## 2. Data sources

### xd corpus — the only source that matters

<https://xd.saul.pw/data>

* `xd-clues.zip` — **93 MB**, expands to `xd/clues.tsv` at 268 MB.
  Columns: `pubid  year  answer  clue`, tab-separated, 8,019,346 rows, UTF-8.
* `xd-metadata.zip` — 2.8 MB. Not needed for the page; useful for sanity checks.

Quirks that will bite:

* **46 publications, not one.** Filter `pubid == "nyt"` or every figure is wrong. The NYT
  rows are 2,457,203 of the 8,019,346; the other 5,562,121 belong to 45 other papers.
* **`year` is sometimes `0`.** Several publications carry rows with year `0`; drop any row
  whose year is not a four-digit number in range.
* **Answers are bare uppercase strings with no spaces.** `E COLI` is `ECOLI`. Strip to
  `A–Z` and upper-case before comparing. Punctuation appears in a handful of rows.
* **1942–1950 is Sundays only** — about 8,000 answers a year, against 31,000 from 1951.
  The Times had no daily puzzle before September 1950. Use shares, never raw counts.
* **The corpus is a reconstruction, not the paper.** 1978 has 23,900 rows where a full year
  is ~31,400. 2012–2014 have *more* rows than a year of puzzles contains (2013: 42,187).
  Shares absorb both; counts do not.
* **The archives are regenerated periodically.** This build used the 28 April 2026
  generation. Later generations will shift the verification numbers below by a little.

### ENABLE lexicon

<https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt> — 172,823 words,
public domain. Used only as a membership test: is this answer an ordinary English word?
It contains no proper nouns, no abbreviations and no phrases, which is exactly what is
wanted.

### Norvig word counts

<https://norvig.com/ngrams/count_1w.txt> — 333,333 words, 588 billion tokens, from the
Google Web Trillion Word Corpus. Used **only** for the English letter and vowel baseline.

> **Do not use its tail.** The list stops at 333,333 words and its last entries are OCR
> noise (`gooblle`, `golgw`, all at the 12,711 floor). Genuinely rare real words —
> `esne`, `anoa` — are *absent*, while nonsense is present. It cannot tell you how rare a
> crossword word is in English. It can tell you what the letters of ordinary English look
> like in bulk, because a frequency-weighted mean is dominated by the head.

---

## 3. Processing decisions, and why

**Restrict everything to the New York Times.** It is the only publication in the corpus
with continuous coverage under a single editorial lineage. Pooling publications smears the
1993 handover into nothing.

**Symmetric windows with a gap.** Retired = ≥50 uses in 1942–1979 **and** 0 uses in
2000–2025. Invented = 0 uses in 1942–1979 **and** ≥50 uses in 2000–2025. The 20 years
between are left unjudged deliberately: with a single cut point, any list you produce is
partly an artefact of where you put it. With a gap, the interesting question — *where
inside those 20 years does each word actually land?* — is not something the definition
decided for you. It lands on 1993/1994.

**Report the all-time total on each card, and sort by it**, not by the window count that
defined the list. Two different numbers on one card invites misreading.

**Letters and vowels are taken over answers of three letters or more**, matching the cut
applied to the English baseline. This drops 279 of 2,457,203 NYT answers.

**Editor eras run start-year to the year before the next start**, so no year is counted
twice: Farrar 1942–1968, Weng 1969–1976, Maleska 1977–1992, Shortz 1993–2025. The real
handovers were mid-year, which makes the 1993 column a blend of two editors and the hinge
slightly *blunter* than the truth, not sharper.

**Payload encoding.** Each answer's 84 yearly counts become an 84-character string, one
byte per year, indexed into a 75-character JSON-safe alphabet (printable ASCII 48–126 minus
`"` and `\`). The largest single-year count in the corpus is 45, so one byte is ample, and a
string of mostly-zero characters compresses to almost nothing over the wire. 20,000 answers
ship this way — 76.5% of all NYT usages, every answer used at least 21 times.

---

## 4. The page

Newsprint palette (`--paper:#F7F3E9`, ink `#15120C`), amber `--old` for the retired
vocabulary and blue `--new` for the invented one, both validated in light and dark. Fraunces
for display, IBM Plex Sans and Mono for everything else — the house Quick Projects stack.

The motif is a strip of crossword cells that swaps one four-letter word for another every
2.6 seconds (`ESNE`/`EDU`/`OLEO`/`IMAC`), suppressed under `prefers-reduced-motion`.

Six sections:

1. **The swap** — 217 word cards, each rendered as crossword squares with its all-time
   count, year span, per-year sparkline and one dated clue. Filter by list, sort by uses /
   year / alphabetically. *With both lists showing, interleave them rather than
   concatenating* — the invented words are used far more often, so a single sort buries
   every retired card below the fold and destroys the comparison.
2. **One year** — the hinge. A double histogram, one block per word: invented words'
   first year above the line, retired words' last year below, with the four editors banded
   along the axis and a dashed marker at November 1993. *Size the canvas from the data* —
   the 1994 column is 22 blocks tall and a fixed height clips it.
3. **The letters never moved** — 26 letter rows, bars for the selected era with a red tick
   for English and the signed difference at the right. Era toggle recomputes the
   correlations in the caption.
4. **Is it even a word?** — the ENABLE share, 1942–2025.
5. **Look up any answer** — type any of the 20,000, get its eighty-four-year bar chart,
   total, first and last year, busiest year and rank.
6. **How this was made** — method and limits, including the trap below.

All charts sit in `.scrollx` containers with a 660px minimum SVG width: on a phone the
chart scrolls inside its own figure rather than shrinking an 84-year axis to four pixels a
year, and the page itself never scrolls sideways.

---

## 5. Verification table

Rebuild against the 28 April 2026 xd generation and these should come back exactly.

### Corpus shape

| quantity | value |
|---|---|
| rows in `clues.tsv` | 8,019,346 |
| NYT rows, 1942–2025 | 2,457,203 |
| distinct NYT answers | 205,829 |
| other publications | 45 (5,562,121 rows) |
| NYT usages in 1942 / 1950 / 1951 | 8,085 / 15,412 / 31,490 |
| NYT usages in 1978 / 2013 | 23,900 / 42,187 |

### The two lists

| quantity | value |
|---|---|
| retired words (≥50 in 1942–79, 0 in 2000–25) | **56**, 3,780 uses in window |
| invented words (0 in 1942–79, ≥50 in 2000–25) | **161**, 14,055 uses in window |
| median year a retired word was last printed | **1993** |
| median year an invented word first appeared | **1994** |
| retired words last seen in 1992 / 1993 | 9 / 14 |
| invented words first seen in 1994 | 22 |
| retired words still in use after 1999 | 0 |
| top retired, by window count | `ASOR` 112, `ARAR` 110, `EVOE` 101, `UNAL` 99, `ENARE` 97 |
| top invented, by window count | `SNL` 261, `SSN` 233, `ELO` 212, `ATARI` 194, `EDU` 188 |

### Individual answers — the fastest parse check

| answer | all-time NYT uses | first | last | busiest year | rank |
|---|---|---|---|---|---|
| `ERA` | 1639 | 1942 | 2025 | 2015 (×36) | #1 |
| `AREA` | 1608 | 1942 | 2025 | 1973 (×35) | #2 |
| `ERIE` | 1444 | 1942 | 2025 | 1980 (×34) | #4 |
| `OLEO` | 884 | 1942 | 2025 | 1985 (×23) | #53 |
| `ESNE` | 410 | 1943 | 2015 | 1984 (×20) | #566 |
| `ETUI` | 373 | 1943 | 2025 | 1987 (×11) | #708 |
| `SNL` | 273 | 1995 | 2025 | 2014 (×19) | #1305 |
| `EDU` | 197 | 1995 | 2025 | 2018 (×14) | #2246 |
| `ANOA` | 166 | 1943 | 2004 | 1951 (×8) | #2853 |
| `ACAI` | 127 | 2010 | 2025 | 2021 (×21) | #4078 |
| `ENARE` | 109 | 1942 | 1991 | 1953 (×7) | #4817 |

### Eras

| editor | years | usages | distinct | most-used answer |
|---|---|---|---|---|
| Margaret Farrar | 1942–1968 | 641,995 | 92,800 | `ONE` |
| Will Weng | 1969–1976 | 253,294 | 60,003 | `AREA` |
| Eugene T. Maleska | 1977–1992 | 494,076 | 77,267 | `AREA` |
| Will Shortz | 1993–2025 | 1,067,838 | 131,739 | `ERA` |

### Letters and vowels

| quantity | value |
|---|---|
| vowel share of answers, 1942 / 1993 / 2025 | 42.07% / 42.52% / 40.73% |
| vowel share, English (≥3 letters, freq-weighted) | 37.15% |
| letter r, Farrar vs Shortz | **0.9970** |
| letter r, Farrar vs English | 0.9635 |
| letter r, Shortz vs English | 0.9686 |
| `E` share, English / Shortz era | 12.26% / 13.49% |
| `A` share, English / Shortz era | 8.12% / 11.36% |
| `H` share, English / Shortz era | 3.75% / 2.34% |
| ENABLE-word share, 1942 / 1993 / 2011 / 2025 | 69.6% / 65.2% / 53.2% / 56.5% |

---

## 6. The trap — do not repeat this

**The first version of this analysis measured the rise of abbreviations from the clues, and
got a false answer.**

American crossword convention requires an abbreviated answer to be signalled in its clue, so
counting clues containing `: Abbr.`, `for short`, `briefly` or `in brief` looks like a clean
way to measure how abbreviation-heavy the puzzle became. Run per decade, it gives:

| decade | 1940s | 1950s | 1960s | 1970s | **1980s** | 1990s | 2000s | 2010s |
|---|---|---|---|---|---|---|---|---|
| clues with an abbreviation marker | 0.43% | 1.65% | 2.59% | 2.22% | **0.77%** | 1.21% | 2.49% | 2.81% |

The 1980s collapse is not real. **Maleska flagged abbreviations by abbreviating the clue
itself** — `Drivers' org.`, `Motoring gp.` — rather than appending a marker. The marker
count measures house style, not content.

Nothing on the published page is derived from clue formatting. The only clue-shaped fact
kept is one that is independently visible and unambiguous: the share of NYT clues ending in
a full stop runs 96–98% through 1967, then 86% in 1968, 75% in 1969, and **5.6% in 1970** —
the Times dropped terminal periods from its clues as Will Weng took over.

Two further limits worth stating on the page:

* Any statistic split by year inherits the corpus's uneven coverage. Only shares are safe.
* One clue per featured word is quoted, dated. The clue file belongs to the papers that
  printed it; do not republish it wholesale.

---

## 7. Running it

```bash
cd projects/second-language/src
python fetch.py            # ~96 MB into src/raw/, skips anything already there
python build_payload.py    # src/raw/ -> src/payload.json  (~2 MB, about a minute)
python inject.py           # payload + template.html -> ../index.html, wrapped and linked
```

`inject.py` runs `wrap_for_pages.py` and `add_catalog_link.py` as its last two steps.
Regenerating the page without them silently drops the standalone document wrapper and the
breadcrumb back to the catalog.

`src/raw/` is git-ignored: the clue archive is 93 MB and `fetch.py` refetches it.
