# Training path for handwritten mathematics

Goal: be able to read 18th-c. handwritten mathematics (Leibniz, Euler, Bernoulli manuscripts)
LATER, without spending GPU budget NOW. The strategy is to assemble the training data cheaply
(inference + CPU, no GPU) so a fine-tune is a small, de-risked job whenever we choose to run it.
The verification stack (render + SymPy + numeric) already works on any LaTeX, so quality is gated
the same way no matter which model produced it.

## The bridge insight: our printed output IS training data
Every printed page we transcribe AND verify is a clean `image -> verified-LaTeX` pair. The Euler
Introductio (356 leaves) + Methodus inveniendi (343 leaves) already yield thousands of verified
math expressions. Scaling printed math (Tier 1) is therefore also how we grow the labeled corpus.
This trains a printed-math model directly and seeds handwritten via transfer + the bootstrap below.

## Existing handwritten-math datasets (pull + stage now, free)
- **CROHME** — 8,836 training formulae, InkML online strokes; the field benchmark.
- **HME100K** — 74,502 offline handwritten-formula images, 249 symbol classes; real-world.
- **MathWriting** (Google, 2024) — largest online handwritten-math dataset.
- **im2latex-100k** — 100k printed image/LaTeX pairs (Zenodo/Kaggle); the printed base for transfer.
These are standard, downloadable. Staging them = the base training set. Modern handwriting, so they
teach general HMER but not the 18th-c. hands, which the bootstrap supplies.

## The bootstrap (the clever, cheap part): manuscript-to-print alignment
Many printed math texts survive as MANUSCRIPT originals (Euler's Nachlass, the Bernoulli-Euler
papers, Leibniz). Where a manuscript has a known printed edition:
1. Transcribe + verify the PRINTED version (proven, ~free on inference).
2. Align that verified LaTeX to the MANUSCRIPT page images (layout match; the render-verify loop
   doubles as the aligner — a rendered equation that matches a manuscript region locates the pair).
3. Result: `handwritten-image -> verified-LaTeX` pairs, generated AUTOMATICALLY, no human labelling,
   no GPU. This produces exactly the period-specific handwritten training data that CROHME/HME100K
   lack. This is the genuine innovation and it uses only inference credits.

Plus standard synthetic augmentation: render LaTeX in handwriting-like fonts with perturbations to
expand coverage (cheap, CPU).

## Training approach, cheapest-first
- **Phase 1 (now, free):** grow verified printed pairs (Tier-1 runs) + stage CROHME/HME100K/
  MathWriting/im2latex + prototype the manuscript-print bootstrap on ONE case to prove pair quality.
- **Phase 2 (when ready, cheap):** Gemini supervised fine-tuning on the assembled pairs, if the GfS
  credit covers Vertex tuning jobs (verify terms). On-platform, no GPU procurement.
- **Phase 3 (only if Phase 2 underperforms):** fine-tune a dedicated HMER model (TAMER / ICAL /
  Uni-MuMER base) on GPUs. This needs a real GPU budget the Gemini credits will not cover.

## Why this respects "not worth it now"
We are NOT spending GPU budget to produce drafts an expert must recheck. We are cheaply banking the
training data (a durable asset) so that IF the economics change, a fine-tune is a small run, not a
cold-start project. Meanwhile the printed work ships real value today and the corpus keeps growing.

## Immediate no-GPU actions
1. Keep running Tier-1 printed math (in progress: Methodus inveniendi) -> verified pairs.
2. Pull + stage CROHME, HME100K, MathWriting, im2latex-100k into a `mathtrain/` corpus.
3. Prototype the manuscript-print bootstrap on one Euler manuscript with a known printed edition;
   measure how many good handwritten pairs it yields per page.
4. Verify whether the GfS credit covers Vertex Gemini tuning (decides Phase 2 cost).
