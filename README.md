# ✏️ Second Language

**The New York Times crossword replaced its entire private vocabulary in a single year, and kept exactly the same letters.**

→ **[Open it](https://tnriley.github.io/second-language/)**

Every answer the New York Times crossword has printed since 1942 - 2.46 million of them - sorted into the words the puzzle retired and the words it invented. Fifty-six answers were used at least fifty times before 1980 and have not appeared once since 1999; a hundred and sixty-one had never been printed before 1980 and are now used at least fifty times. The median retired word was last seen in 1993 and the median invented word first appeared in 1994, the year Will Shortz took the editor's chair from Eugene Maleska. What did not change is the letters: the Farrar-era and Shortz-era letter distributions correlate at r = 0.997, and crossword answers have been 40.7% to 42.7% vowels in every single year since 1942, against 37.1% for English. Look up any of the 20,000 most-used answers and watch its eighty-four years.

## Running it

One self-contained HTML file. No build step, no server, no network access at runtime — open `index.html` in a browser, or serve the directory with any static host.

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Rebuilding it from scratch

[REBUILD.md](REBUILD.md) is written for an LLM with a shell and nothing else: the data sources and their quirks, the processing decisions, the page's structure and interactions, and a table of expected values to check the result against.

## Source

The full build pipeline is in [`src/`](src/), with a README describing how to regenerate the page from scratch.

## Data

- **[xd corpus, clue archive - 8,019,346 answer-and-clue usages across 46 publications, of which 2,457,203 New York Times rows from 1942 to 2025 are used here; generated 28 April 2026 by Saul Pwanson / century-arcade](https://xd.saul.pw/data)** — Tooling MIT; clue and answer text remains the property of the publications that printed it. This page ships aggregate counts plus one dated clue per featured word, quoted as illustration.
- **[ENABLE (Enhanced North American Benchmark Lexicon), 172,823 words - used as a yes/no test of whether an answer is an ordinary English word](https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt)** — Public domain
- **[Peter Norvig, word counts from the Google Web Trillion Word Corpus - 333,333 words over 588 billion tokens, used for the English letter and vowel baseline](https://norvig.com/ngrams/)** — Free to use (Norvig, Natural Language Corpus Data)

Every figure on the page is computed from the data shipped with it. Check the page's own methods panel for how each number is derived and where it should not be pushed.

## Built with

vanilla JS, inline SVG, single-byte-per-year string payload.

## Licence

Code is MIT (see [LICENSE](LICENSE)). Data keeps the licence of its source, listed above.

---

Part of [Quick Projects](https://github.com/TNRiley/quick-projects) — one self-contained thing, built in one session. First published 2026-09-27.
