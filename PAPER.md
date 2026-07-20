# Reading the Archive

### A verification-first pipeline for machine transcription of historical documents

*Steps Ventures, Historical AI. Draft, July 2026.*

---

## The problem is not the images. It is the words.

For twenty years the world's archives have photographed their holdings. National libraries, university collections, and museums have put hundreds of millions of manuscript pages online. Almost none of them are transcribed. A page scan that no one can search is a locked book with the lights on, and the backlog of un-transcribed material is where most of the unread past now sits: letters, ledgers, court records, notebooks, and diagrams that no one can find because no one can read them at scale.

Large vision-language models can now read many of these pages. The obstacle to using them is not capability. It is trust. A model that transcribes a 1748 page and hands back plausible text is worthless to a historian if there is no way to know which words are solid and which are invented. This note describes a pipeline built around a single principle: a transcription is a guess until it survives checks that do not depend on trusting the model, and every reading must carry its own confidence.

## Transcription with a measured doubt

Each page is transcribed independently more than once. Where the passes agree and match the image, the reading is treated as reliable. Where they disagree, the page is flagged rather than published. Inter-pass agreement, measured as an edit distance over the token stream, becomes a confidence score attached to every page.

Language and script are detected per page, because a French secretary hand and an Armenian mercantile hand cannot be read the same way. This matters most where the model fails. On a corpus of captured-ship documents we transcribed 644 pages across English, French, and Armenian. The English prize-court records and the French East India Company papers came back at high confidence, near 0.8. The eighteenth-century New Julfa Armenian merchant letters came back near 0.2, with the two passes barely agreeing. A second, higher-resolution pass lifted the English and French readings and barely moved the Armenian, from 0.21 to 0.25. That is the honest result. The model cannot reliably read the Julfa hand, so we do not pretend it can. Those letters were located, imaged, machine-drafted with a clear unverified label, and offered to the scholar who owns that world, rather than presented as finished transcriptions.

Refusing to launder a guess is the whole design. A confidence score that is sometimes low is what makes the high scores worth anything.

## Mathematics is verifiable without knowing the answer

Prose can be checked for internal agreement and against the image, and no further. Mathematics is different. It is the rare kind of content you can verify without knowing the answer in advance, and that opens a verification stack that ordinary transcription cannot reach. We apply four layers.

**One, read.** The model transcribes the page, prose and formulae, into text with mathematics rendered as LaTeX. Two independent passes make disagreement measurable.

**Two, render.** The LaTeX is rendered back to an image and compared to the source. Garbled output cannot hide, because it will not render to the same marks. On clean typeset equations this alone gives a pixel-level match.

**Three, validate.** A symbolic engine evaluates each equality. A reading of cos(pi) = 1 is rejected on the spot because it is false, no matter how cleanly it renders. Where an identity is true but the symbolic engine cannot prove it, as with product formulas for sin(5z), the claim is tested numerically at several points before any verdict is reached. Cannot prove is never treated as false.

**Four, contextualize.** The equation is compared against what the surrounding prose claims it should be. A formula that contradicts its own caption is flagged for a human.

A reading that passes all four is not a guess. It is a fact that has survived four ways of being wrong.

## A worked case: Euler, *Introductio in analysin infinitorum*, 1748

We ran the full pipeline over all 356 leaves of the first volume of Euler's *Introductio*, transcribing 4,397 mathematical expressions and validating every equality. Sixty relations were flagged by validation. The value of the method is in what happened next, because a crude tool would report sixty errors. Triaged honestly, they were:

- **Eighteen printed approximations, verified.** Euler's decimals, recomputed and confirmed to the digits he printed, including the values of pi-squared over 24, pi-to-the-fourth over 1440, and pi-to-the-sixth over 60480, each matching to twenty-three digits.
- **Seventeen definitions**, such as the recurrence C = B + A, which assign symbols rather than assert identities.
- **Six of Euler's own eighteenth-century conventions**, including division by zero, complex root branches, and his use of the letter i for an infinite number. The last of these the validator now confirms by taking the limit as i tends to infinity, so that (i-1)/(2i) = 1/2 is recognized as true in Euler's own sense.
- **Fourteen true identities the symbolic engine could not reduce**, confirmed numerically.
- **Five genuine anomalies for a human.**

Two of those five are worth stating. First, we asked the pipeline to read the value of pi that Euler printed. It returned 127 digits. Compared against the true value, 112 leading digits were correct, and the pipeline flagged the 113th, where the page reads 7 and pi is 8. This is not a transcription error. It is de Lagny's mistake, computed by hand in 1719, uncaught until Vega corrected it in 1794, and reproduced faithfully by Euler in 1748. The tool transcribed exactly what was printed, and the validation layer pointed straight at a 250-year-old error.

Second, Euler's printed value of 1 over pi was flagged as diverging from the true value near the sixteenth decimal. This one we report as a candidate, not a confirmed finding. It could be an error in the 1748 print or a digit the model misread on a long string. The point is that the pipeline surfaced it for a human to check, which is the whole function of the layer.

## What this is, and what it is not

Across two corpora and roughly ninety dollars of compute, the pipeline produced a confidence-labeled transcription of 644 pages of eighteenth-century correspondence and a validated edition of a 356-leaf mathematics text, complete with a machine-generated errata that distinguishes the author's approximations, his conventions, and his genuine errors. The errata is the kind of artifact ordinary OCR cannot produce. It is the tool doing scholarship rather than typing.

The honest limits matter as much as the results. None of this has yet been validated by a subject expert. The de Lagny finding is confirmed against known history, but the transcriptions themselves rest on the pipeline's own checks, not peer review. The method reads printed and clean-hand material well, struggles with difficult and non-Latin hands, and cannot yet read handwritten mathematics or non-Latin scripts without dedicated training. Each of those failures is labeled rather than hidden. That is the point. A tool a historian can trust is not one that is usually right. It is one that tells you, every time, exactly how it knows.

## Availability

The Euler edition, its errata, and the Prize Papers transcriptions are published with per-item confidence and provenance, source images left with their holding archives. The method and the corpora are catalogued at the project's site.

*Correspondence: mike@stepsventures.com*
