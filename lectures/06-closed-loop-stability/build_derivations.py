#!/usr/bin/env python3
"""Build the Lecture 6 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-06_Derivations.ipynb")
d = Deck()
d.title("Lecture 6 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 12-14", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
s = sp.symbols("s")
""")

d.part("A", "P Control: Eqs. 12.1-12.7",
       "Coughanowr & LeBlanc, Ch. 12", "coughanowr-ch12")
d.sub("""
### Servo

$\\frac{T'}{T_R'} = \\frac{K_cA/(\\tau s+1)}{1 + K_cA/(\\tau s+1)} =
\\frac{K_cA}{\\tau s + 1 + K_cA}$. Divide by $1 + K_cA$:
$\\frac{A_1}{\\tau_1 s + 1}$ with $A_1 = \\frac{K_cA}{1+K_cA}$,
$\\tau_1 = \\frac{\\tau}{1 + K_cA}$. Final value theorem for a unit step:
$\\lim_{s\\to0} s\\cdot\\frac1s\\cdot\\frac{A_1}{\\tau_1s+1} = A_1$.
Offset $= 1 - A_1 = 1/(1 + K_cA)$.

### Regulator

$\\frac{T'}{T_i'} = \\frac{1/(\\tau s+1)}{1 + K_cA/(\\tau s+1)} =
\\frac{1}{\\tau s + 1 + K_cA}$; final value $1/(1 + K_cA)$; offset
$-1/(1 + K_cA)$. Ex. 12.2 ($K_c = 20$, 5 C): $T'(\\infty) = 2.059$ C.
""")

d.part("B", "PI Control and Measurement Lag",
       "Coughanowr & LeBlanc, Ch. 12, Sec. 12.3-12.5", "coughanowr-ch12")
d.sub("""
### Eq. 12.9

$\\frac{T'}{T_i'} = \\frac{1/(\\tau s+1)}{1 + K_c(1 + 1/\\tau_Is)A/(\\tau s+1)}$.
Multiply numerator and denominator by $\\tau_Is(\\tau s+1)$:
$\\frac{\\tau_Is}{\\tau\\tau_Is^2 + \\tau_I(1 + K_cA)s + K_cA}$. Divide by
$K_cA$: $\\tau_1^2 = \\tau\\tau_I/K_cA$, $2\\zeta\\tau_1 =
\\tau_I(1 + K_cA)/K_cA$, which gives the book's $\\zeta$.

### Eq. 12.17 (P with measurement lag)

$\\frac{T'}{T_R'} = \\frac{K_cA/(\\tau s+1)}{1 + K_cA/[(\\tau s+1)(\\tau_ms+1)]}
= \\frac{K_cA(\\tau_ms+1)}{(\\tau s+1)(\\tau_ms+1) + K_cA}$. Divide by
$1 + K_cA$: $\\tau_2^2 = \\frac{\\tau\\tau_m}{1+K_cA}$,
$2\\zeta_2\\tau_2 = \\frac{\\tau + \\tau_m}{1 + K_cA}$.
""")
d.code("Check -- $\\zeta_2$ from the expanded denominator", [
    "Symbolic check of Eq. 12.17's damping factor",
], """
tau, tm, KA = sp.symbols("tau tau_m KA", positive=True)
den = sp.Poly(sp.expand((tau*s + 1)*(tm*s + 1) + KA), s).all_coeffs()
t2 = sp.sqrt(den[0] / den[2])
z2 = sp.simplify(den[1] / den[2] / (2 * t2))
print(z2)
""", """
The denominator coefficients [tau tau_m, tau + tau_m, KA + 1] are put in
standard form as in the lecture. The damping factor prints as
(tau + tau_m)/(2 sqrt(tau) sqrt(tau_m) sqrt(KA + 1)): Eq. 12.17.
""")

d.part("C", "The Routh Test in Full",
       "Coughanowr & LeBlanc, Ch. 13", "coughanowr-ch13")
d.sub("""
### Example 13.2

$s^4 + 3s^3 + 5s^2 + 4s + 2$. Row 3: $b_1 = (3\\cdot5 - 1\\cdot4)/3 =
11/3$, $b_2 = (3\\cdot2 - 0)/3 = 2$. Row 4: $c_1 = (\\frac{11}{3}\\cdot4 -
3\\cdot2)/\\frac{11}{3} = 26/11$. Row 5: $2$. No sign change: stable.

### Prob. 13.11 (Your Turn)

Rows $[1, 6, 1+K]$, $[4, 4]$, $[5, 1+K]$, $[(20 - 4 - 4K)/5]$, $[1+K]$:
$K < 4$. At $K = 4$: $5s^2 + 5 = 0$, $s = \\pm j$; the other two roots
from $s^4 + 4s^3 + 6s^2 + 4s + 5 = (s^2 + 1)(s^2 + 4s + 5)$:
$-2 \\pm j$.
""")
d.code("Check -- the factorization at $K = 4$", ["`sp.factor` splits the quartic"], """
print(sp.factor(s**4 + 4*s**3 + 6*s**2 + 4*s + 5))
""", """
Prints (s**2 + 1)*(s**2 + 4*s + 5): roots +/- j on the axis and
-2 +/- j in the left half-plane, as derived.
""")

d.part("D", "Root Locus: Example 14.1 Exactly",
       "Coughanowr & LeBlanc, Ch. 14", "coughanowr-ch14")
d.sub("""
### The quartic and its Hurwitz condition

$3s(20s+1)(10s+1)(0.5s+1) + K_c(2s^2 + 3s + 1) = 0$, i.e.
$300s^4 + 645s^3 + (91.5 + 2K_c)s^2 + 3(1 + K_c)s + K_c = 0$.
For a quartic $a_0s^4 + \\dots + a_4$ with positive coefficients the
Routh first column is positive iff $a_1a_2a_3 - a_0a_3^2 - a_1^2a_4 > 0$.
""")
d.code("Check -- solve the boundary condition", [
    "The two gains where the condition is zero",
], """
Kc = sp.symbols("K_c", positive=True)
a0, a1, a2, a3, a4 = sp.Poly(sp.expand(
    3*s*(20*s + 1)*(10*s + 1)*(s/2 + 1) + Kc*(2*s**2 + 3*s + 1)),
    s).all_coeffs()
cond = sp.factor(a1*a2*a3 - a0*a3**2 - a1**2*a4)
print(cond, [round(float(r), 3) for r in sp.solve(cond, Kc)])
""", """
`all_coeffs` unpacks the five coefficients. The Hurwitz expression
factors as 45(52 K_c^2 - 10689 K_c + 7749)/2, a quadratic in K_c whose
roots are 0.728 and 204.830: the exact stability boundaries. The book's
0.6 and 360 (with omega = 0.1 and 1.1) are graphical estimates; the
exact crossing frequencies are 0.090 and 0.979 rad/time.
""")

d.write(OUT)
