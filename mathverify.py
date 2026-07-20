#!/usr/bin/env python3
"""mathverify — verify machine-transcribed mathematics without knowing the answer.

Given LaTeX (from any OCR/VLM transcriber) this module applies the checks that make a
transcription trustworthy:

  render(latex)      -> does it render at all (compilability)
  sympy_true(eq)     -> is the equality a true identity (symbolic)
  numeric_true(eq)   -> if symbolic proof fails, does it hold at random test points
  triage(eqs)        -> sort flagged equalities into: approximation (verified against the
                        printed decimals), definition, 18c-convention (div-by-zero, complex
                        roots, Euler's infinite i), numerically-verified, or genuine anomaly

No credentials and no network. Depends only on sympy and matplotlib. The transcription step
(image -> LaTeX) is pluggable; this is the part that turns a guess into a checked fact.

MIT License. Steps Ventures, 2026.  https://github.com/steps-re/reading-the-archive
"""
import re
import signal
import sympy as sp

LOC = {"pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "e": sp.E,
       "log": sp.log, "sqrt": sp.sqrt, "a": sp.Symbol("a", positive=True)}

# Period typography that is faithful transcription but breaks matplotlib mathtext.
# Normalized ONLY for the render probe; the transcription itself is never altered.
_PERIOD_LATEX = [
    (re.compile(r"\\&c\.?"), r"\\ldots"),   # Euler's "&c." (et cetera)
    (re.compile(r"(?<!\\)&c\.?"), r"\\ldots"),
]


def _normalize_for_render(latex):
    for pat, rep in _PERIOD_LATEX:
        latex = pat.sub(rep, latex)
    return latex


class _Timeout(Exception):
    pass


def _guarded(fn, seconds=5, default=None):
    """Run fn() with a wall-clock guard (POSIX main thread; degrades to a plain try elsewhere).
    sympy.simplify can hang on adversarial expressions; a verifier must not."""
    def _alarm(sig, frm): raise _Timeout()
    try:
        old = signal.signal(signal.SIGALRM, _alarm); signal.alarm(seconds)
    except ValueError:                      # not in the main thread
        try: return fn()
        except Exception: return default
    try:
        return fn()
    except (_Timeout, Exception):
        return default
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)


def render(latex):
    """True if the LaTeX renders (matplotlib mathtext). A reading that will not render is wrong.
    Known period idioms (e.g. Euler's '&c.') are normalized first so faithful transcription
    of 18th-century typography is not misreported as a failure."""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        fig = plt.figure(figsize=(4, 1))
        fig.text(0.01, 0.5, f"${_normalize_for_render(latex.strip().strip('$'))}$", fontsize=16)
        fig.canvas.draw(); plt.close(fig); return True
    except Exception:
        plt.close("all"); return False


def sympy_true(eq):
    """True/False/None for an equality string 'lhs = rhs' (None = could not parse/decide).
    Guarded: simplify is given a few seconds, then we fall back to undecided."""
    if "=" not in eq: return None
    L, R = eq.split("=", 1)
    def _check():
        return sp.simplify(sp.sympify(L, locals=LOC) - sp.sympify(R, locals=LOC)) == 0
    return _guarded(_check, seconds=5, default=None)


def numeric_true(eq, points=(0.317, 0.733, 1.171, 0.529), tol=1e-7):
    """True if the equality holds numerically at several substituted points. Distinguishes a
    true identity SymPy cannot prove (e.g. trig product formulas) from a false one."""
    if "=" not in eq: return None
    L, R = eq.split("=", 1)
    try:
        expr = sp.sympify(L, locals=LOC) - sp.sympify(R, locals=LOC)
        syms = sorted(expr.free_symbols, key=str)
        if not syms: return sympy_true(eq)
        trials = good = 0
        for base in points:
            sub = {s: sp.Float(base + 0.211 * k) for k, s in enumerate(syms)}
            try:
                v = complex(expr.subs(sub).evalf()); trials += 1; good += abs(v) < tol
            except Exception:
                pass
        return trials >= 2 and good == trials
    except Exception:
        return None


def _is_decimal(s): return bool(re.fullmatch(r"-?\d+\.\d+", s.strip()))


def triage(eq):
    """Classify a flagged equality. Returns (category, note). Categories:
    approximation | definition | 18c-convention | numerically-verified | anomaly | unparsed."""
    if "=" not in eq: return "unparsed", ""
    L, R = [x.strip() for x in eq.split("=", 1)]
    if re.fullmatch(r"[A-Za-z]\w*", L) and not _is_decimal(R):
        return "definition", f"{L} defined"
    dec, expr = (R, L) if _is_decimal(R) else ((L, R) if _is_decimal(L) else (None, None))
    if dec is not None:
        try:
            val = sp.sympify(expr, locals=LOC).evalf(30); ndp = len(dec.split(".")[1])
            ev = f"{float(val):.{ndp + 2}f}"
            if abs(val - sp.Float(dec)) < sp.Float(10) ** (-(ndp - 1)):
                return "approximation", f"exact {ev} matches printed {dec}"
            return "anomaly", f"printed {dec}, exact {ev}"
        except Exception:
            return "18c-convention", "numeric / undefined"
    if numeric_true(eq) is True:
        return "numerically-verified", "holds at all test points (SymPy could not reduce)"
    if re.search(r"1/0|0\*\*-|0\*\*\(-|/0\b|zoo|oo", eq):
        return "18c-convention", "division by zero / infinity"
    if re.search(r"\bi\b", eq):
        try:
            ii = sp.Symbol("i", positive=True); loc = dict(LOC); loc["i"] = ii
            if sp.limit(sp.sympify(L, locals=loc) - sp.sympify(R, locals=loc), ii, sp.oo) == 0:
                return "18c-convention", "holds as i -> infinity (Euler's infinite number)"
        except Exception:
            pass
    if re.search(r"\(-\d+\)\*\*\(1/", eq):
        return "18c-convention", "real-vs-complex root branch"
    # differential relations / derivations (dx, dy, ds, dt, dp..., derivatives, integrals) are
    # NOT universal identities; the identity-checker does not apply. Common in the calculus of
    # variations. Flag as such rather than calling a valid differential relation an error.
    if re.search(r"d[a-zA-Z](?![A-Za-z0-9])|Derivative|Integral", eq):
        return "differential-relation", "contains differentials/derivatives; not a universal identity"
    return "anomaly", "unverified as a universal identity (may be context-dependent)"


def verify(eq):
    """The one-call cascade. Returns (verdict, note).

    Order matters: symbolic proof first (the strongest verdict), then the triage
    explanations for everything symbolic proof cannot settle. Verdicts:
      verified-identity | approximation | numerically-verified | definition |
      18c-convention | differential-relation | anomaly | unparsed
    """
    if "=" not in eq:
        return "unparsed", "no equality to check"
    if sympy_true(eq) is True:
        return "verified-identity", "symbolically proven"
    return triage(eq)


if __name__ == "__main__":
    demo = ["cos(pi) = -1", "cos(pi) = 1", "sqrt(10) = 3.162277", "alpha = 1/2",
            "1/0**3 = 1/0", "(i-1)/(2*i) = 1/2", "sin(5*z) = 16*sin(z)*sin(pi/5-z)*sin(pi/5+z)*sin(2*pi/5-z)*sin(2*pi/5+z)"]
    for eq in demo:
        c, n = verify(eq); print(f"{eq[:44]:44} -> {c:20} {n}")
    print("\nrender('A+Bz+Cz^2+\\\\&c.') =", render(r"A+Bz+Cz^2+\&c."), " (period '&c.' idiom, normalized)")
