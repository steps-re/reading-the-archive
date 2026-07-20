# Reading the Archive

**Verifying machine-transcribed historical mathematics — without knowing the answer in advance.**

Most of the past has been scanned and almost none of it transcribed. Vision-language models can now read many historical pages, but a plausible transcription is worthless to a scholar if there is no way to know which words are solid and which are invented. This repo is the part that fixes that for mathematics: a small, dependency-light verification stack that turns a transcription into a *checked* transcription.

Mathematics is the rare content you can verify without knowing the answer beforehand. Four checks:

1. **Render** — does the LaTeX render back to something that matches the source image?
2. **Symbolic** — is the equality *true*? A reading of `cos(pi) = 1` is rejected because it is false, however cleanly it renders.
3. **Numeric** — if symbolic proof fails (true identities often can't be reduced), does it hold at random test points? "Cannot prove" is never treated as "false."
4. **Triage** — sort the flagged equalities into *approximations verified against the printed decimals*, *definitions*, *the author's own conventions*, *numerically-verified identities*, and the *genuine anomalies* a human should see.

`mathverify.py` is self-contained (only `sympy` + `matplotlib`), no credentials, no network. The transcription step (image → LaTeX) is pluggable.

## The finding this produced

Run over all 356 leaves of **Euler's *Introductio in analysin infinitorum* (1748)**, the pipeline transcribed 4,397 mathematical expressions and flagged 60. Triaged honestly, 55 were Euler being Euler (decimals verified to 23 digits, definitions, his division-by-zero and infinite-*i* conventions, and true identities SymPy could not prove). **Five were genuine anomalies** — see [`euler_introductio_errata.json`](euler_introductio_errata.json).

The headline: we transcribed the value of π Euler printed, 127 digits. **112 were correct, and the pipeline flagged the 113th** (page reads `7`, π is `8`). That is not an OCR error. It is **de Lagny's mistake**, computed by hand in 1719, uncaught until Vega in 1794, and reproduced by Euler in 1748. The tool transcribed faithfully and the validator pointed straight at a 250-year-old error. A second candidate, in Euler's printed `1/π`, is flagged but not confirmed.

## What's here

- `mathverify.py` — the verification stack (render / symbolic / numeric / triage). Run `python mathverify.py` for a demo.
- `euler_introductio_errata.json` — the reproducible errata: every flagged relation, its category, and the five anomalies.
- `PAPER.md` — the methods write-up, "Reading the Archive."
- `HANDWRITTEN_MATH_TRAINING.md` — the plan for extending this to handwritten mathematics.

## Honest limits

These are machine transcriptions. The de Lagny finding is confirmed against known history; the transcriptions themselves rest on the checks above, not peer review. The method reads printed and clean-hand material well and cannot yet read difficult or non-Latin hands, or handwritten mathematics, without dedicated work. Every failure is labeled rather than hidden. A tool a scholar can trust is not one that is usually right. It is one that tells you, every time, how it knows.

---
By [Steps Ventures](https://stepsventures.com). MIT License. Contributions and corrections welcome.
