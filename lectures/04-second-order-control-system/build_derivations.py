#!/usr/bin/env python3
"""Build the Lecture 4 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-04_Derivations.ipynb")
d = Deck()
d.title("Lecture 4 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 7-8", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
import control as ct
t, s = sp.symbols("t s", positive=True)
""")

d.part("A", "Manometer: Eq. 7.4 and the Three Cases",
       "Coughanowr & LeBlanc, Ch. 7, Sec. 7.1", "coughanowr-ch7")
d.sub("""
### From Eq. 7.3 to Eq. 7.4

Divide Eq. 7.3 by $\\rho g\\pi D^2/4$. Inertia term:
$\\frac{\\rho\\pi D^2L/4\\cdot(4/3)(1/2)}{\\rho g\\pi D^2/4} = \\frac{2L}{3g}$.
Friction term: $\\frac{(8\\mu/D)(1/2)\\pi DL}{\\rho g\\pi D^2/4} =
\\frac{16\\mu L}{\\rho D^2g}$. Hence Eq. 7.4, and with
$\\tau^2 = 2L/3g$: $\\zeta = \\frac{16\\mu L}{2\\tau\\rho D^2g} =
\\frac{8\\mu}{\\rho D^2}\\sqrt{\\frac{3L}{2g}}$.

Numbers: $\\tau = \\sqrt{400/2940} = 0.369$ s;
$\\zeta = \\frac{0.08}{D^2}\\sqrt{600/1960} = 0.0443/D^2$.
""")
d.code("Check -- the overdamped case is two lags in series", [
    "Eqs. 7.23-7.24 for $\\zeta = 3.66$, $\\tau = 0.369$ s",
], """
tau, z = 0.369, 3.66
t1 = (z + np.sqrt(z**2 - 1)) * tau
t2 = (z - np.sqrt(z**2 - 1)) * tau
print(f"tau1 = {t1:.3f} s, tau2 = {t2:.4f} s")
print("product", round(t1 * t2, 4), "= tau^2", round(tau**2, 4))
""", """
Eqs. 7.23 and 7.24 split the overdamped quadratic into (tau1 s + 1)
(tau2 s + 1): tau1 = 2.65 s and tau2 = 0.051 s. Their product equals
tau^2 = 0.136 s^2 and their sum equals 2 zeta tau, which is how the
factors were found. The slow lag dominates: the thin-tube manometer
behaves almost like a first-order system with tau = 2.65 s.
""")

d.part("B", "Underdamped Response: Eq. 7.18 and the Characteristics",
       "Coughanowr & LeBlanc, Ch. 7, Sec. 7.1", "coughanowr-ch7")
d.sub("""
### Eq. 7.18 by partial fractions

$Y(s) = \\frac{1}{s(\\tau^2s^2 + 2\\zeta\\tau s + 1)} = \\frac1s -
\\frac{\\tau^2s + 2\\zeta\\tau}{\\tau^2s^2 + 2\\zeta\\tau s + 1}$.
Complete the square: $\\tau^2[(s + \\zeta/\\tau)^2 + \\omega^2]$ with
$\\omega = \\sqrt{1-\\zeta^2}/\\tau$. Inverting gives
$1 - e^{-\\zeta t/\\tau}[\\cos\\omega t + \\frac{\\zeta}{\\sqrt{1-\\zeta^2}}
\\sin\\omega t]$, which the identity $a\\cos x + b\\sin x =
\\sqrt{a^2+b^2}\\sin(x + \\tan^{-1}(a/b))$ turns into Eq. 7.18.

### Prob. 7.1 in full

$\\tau = 0.5$, $\\zeta = 0.4$, ultimate $= 2.5 \\times 4 = 10$;
overshoot $e^{-0.4\\pi/0.9165} = 0.254$ (25.4%); maximum 12.54;
period $2\\pi(0.5)/0.9165 = 3.43$; peak at $T/2 = 1.71$. Rise time
(first reaching 10): solve $\\sin(\\omega t + \\phi) = 0$ for the first
$t$: $t_r = (\\pi - \\phi)/\\omega$ with $\\phi = \\tan^{-1}(0.9165/0.4)
= 1.159$: $t_r = 1.08$.
""")
d.code("Check -- Prob. 7.1 rise time from the simulation", [
    "First time the response reaches its final value"], """
tt = np.linspace(0, 6, 60001)
y = ct.step_response(4 * ct.tf([10], [1, 1.6, 4]), tt).outputs
print(f"t_r = {tt[np.argmax(y >= 10)]:.3f}")
print(f"peak {y.max():.2f} at t = {tt[y.argmax()]:.3f}")
""", """
A fine grid (0.0001 time units) makes the threshold crossing precise.
`np.argmax(y >= 10)` finds the first sample at or above the final value:
t_r = 1.08, as derived. The peak prints 12.54 at t = 1.71 = T/2.
""")

d.part("C", "Transportation Lag: Where Pade Comes From",
       "Coughanowr & LeBlanc, Ch. 7, Sec. 7.2", "coughanowr-ch7")
d.sub("""
### First-order Pade

$e^{-\\tau s} = e^{-\\tau s/2}/e^{\\tau s/2} \\approx
(1 - \\tau s/2)/(1 + \\tau s/2)$, keeping first-order terms of each
series. Expanding the quotient:
$1 - \\tau s + \\tau^2s^2/2 - \\tau^3s^3/4 + \\dots$ against
$e^{-\\tau s} = 1 - \\tau s + \\tau^2s^2/2 - \\tau^3s^3/6 + \\dots$:
the error is $-\\tau^3s^3/12$ -- three terms match, versus two for
$1/(1+\\tau s)$.

### Your Turn C

$\\tau = 2/0.5 = 4$ s; $(1 - 2s)/(1 + 2s)$; `ct.pade(4, 1)` returns
num $[-1, 0.5]$, den $[1, 0.5]$.
""")
d.code("Check -- `ct.pade(4, 1)`", ["Confirms the Your Turn answer"], """
print(ct.pade(4.0, 1))
""", """
Prints ([-1.0, 0.5], [1.0, 0.5]): (-s + 0.5)/(s + 0.5), which equals
(1 - 2s)/(1 + 2s) after dividing numerator and denominator by 0.5.
""")

d.part("D", "The Stirred-Tank Heater Loop",
       "Coughanowr & LeBlanc, Ch. 8", "coughanowr-ch8")
d.sub("""
### Example 8.1 in full

$wC = 200\\ \\text{kg/min} \\times 4.184\\ \\text{kJ/(kg C)}/60 =
13.95$ kW/C, so $1/wC \\approx 1/14$ C/kW;
$q_s = 13.95 \\times 20 = 279$ kW (book: 280).

### Example 8.4 closed loop (preview of Ch. 11)

Forward path $G = K_c\\frac{1/14}{5s+1}$, feedback $H = \\frac{1}{0.33s+1}$:
$\\frac{T'}{T_R'} = \\frac{G}{1 + GH}$. At $s = 0$:
$\\frac{20/14}{1 + 20/14} = \\frac{20}{34} = 0.588$; a 5 C step gives
2.94 C. Characteristic equation $(5s+1)(0.33s+1) + 20/14 = 0$:
$1.65s^2 + 5.33s + 2.43 = 0$, roots $-2.68$ and $-0.55$ (real: no
overshoot).
""")
d.code("Check -- the closed-loop poles", ["`np.roots` of the characteristic polynomial"], """
print(np.roots([5 * 0.33, 5 + 0.33, 1 + 20 / 14]))
""", """
The characteristic polynomial (5s + 1)(0.33s + 1) + 20/14 expanded has
coefficients 1.65, 5.33 and 2.43. The roots -2.68 and -0.55 are real
and negative: a stable loop without oscillation at this gain. Raising
Kc moves them together and then apart as a complex pair -- the root
locus of Lecture 6.
""")

d.write(OUT)
