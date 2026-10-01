#!/usr/bin/env python3
"""Build the Lecture 8 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-08_Derivations.ipynb")
d = Deck()
d.title("Lecture 8 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 16", date=False)
d.setup(["Imports used below"], """
import numpy as np
from scipy.optimize import brentq
""")

d.part("A", "Bode Criterion: the Tank with Dead Time",
       "Coughanowr & LeBlanc, Ch. 16, Sec. 16.1-16.2", "coughanowr-ch16")
d.sub("""
### Exact crossover for Eq. 16.1

$\\tan^{-1}(0.203\\omega) + 0.0396\\omega = \\pi$. At $\\omega = 42.6$:
$\\tan^{-1}(8.65) = 1.456$ and $0.0396 \\times 42.6 = 1.687$; sum
$3.142$. $AR/(K_c/600) = 1/\\sqrt{1 + 8.65^2} = 0.115$, so
$K_{c,u} = 5220$ Btu/(min F). The book's 5000 comes from reading
0.12 off Fig. 16-2.

### Ex. 16.3

$\\tan^{-1}\\omega + 1.02\\omega = \\pi \\Rightarrow \\omega_{co} = 1.995$;
$K_{c,u} = \\sqrt{1 + \\omega_{co}^2} = 2.23$; Z-N PI: $K_c = 1.00$,
$\\tau_I = (2\\pi/1.995)/1.2 = 2.62$ min.
""")
d.code("Check -- both crossovers", ["`brentq` on each phase equation"], """
w1 = brentq(lambda w: np.arctan(0.203*w) + 0.0396*w - np.pi, 1, 100)
w3 = brentq(lambda w: np.arctan(w) + 1.02*w - np.pi, 0.5, 5)
print(f"Eq. 16.1: w_co = {w1:.2f}, Kc,u = "
      f"{600*np.sqrt(1 + (0.203*w1)**2):.0f}")
print(f"Ex. 16.3: w_co = {w3:.3f}, Kc,u = {np.sqrt(1 + w3**2):.3f}")
""", """
Both equations are written as "total phase lag minus pi = 0" and solved
with `brentq`. Prints 42.58 rad/min with Kc,u = 5220, and 1.995 rad/min
with Kc,u = 2.232.
""")

d.part("B", "Margins: Ex. 16.1 and Ex. 16.2",
       "Coughanowr & LeBlanc, Ch. 16, Sec. 16.3", "coughanowr-ch16")
d.sub("""
### Ex. 16.1: PM against $\\zeta_2$ in closed form

$G = K_c/(s+1)^2$. Gain crossover $\\omega_g$: $K_c = 1 + \\omega_g^2$.
$PM = 180^\\circ - 2\\tan^{-1}\\omega_g$. Closed loop (Eq. 12.17 with
$\\tau = \\tau_m = 1$): $\\zeta_2 = 1/\\sqrt{1 + K_c} = 1/\\sqrt{2 + \\omega_g^2}$.
Eliminate $\\omega_g = \\tan(90^\\circ - PM/2)$:
$\\zeta_2 = 1/\\sqrt{2 + \\cot^2(PM/2)}$. At $PM = 30^\\circ$:
$\\cot 15^\\circ = 3.73$, $\\zeta_2 = 0.26$; $K_c = 1 + 3.73^2 = 14.9$.

### Ex. 16.2 summary

PD: $\\omega_{180} = 8.62$, $K_u = 22.5$; $\\omega_{150} = 5.53$,
$K_{PM} = 12.3$; GM at 12.3: 1.83. P: $\\omega_{180} = 3.14$,
$K_u = 11.35$; $\\omega_{150} = 2.01$, $K_{PM} = 5.14$; GM 2.21.
""")
d.code("Check -- the closed-form PM relation at 30 deg", ["Evaluate the formula"], """
pm = np.radians(30)
cot = 1 / np.tan(pm / 2)
print(f"zeta2 = {1/np.sqrt(2 + cot**2):.3f}, Kc = {1 + cot**2:.1f}")
""", """
Prints zeta2 = 0.259 and Kc = 14.9: the book's "PM > 30 deg requires
zeta2 > 0.26, hence Kc < 14".
""")

d.part("C", "Ziegler-Nichols for the Two-Tank Reactor",
       "Coughanowr & LeBlanc, Ch. 16, Sec. 16.4", "coughanowr-ch16")
d.sub("""
### Exact versus graphical

$\\tan^{-1}\\omega + \\tan^{-1}2\\omega + 0.5\\omega = \\pi$ gives
$\\omega_{co} = 1.665$ (book 1.56); $K_u = \\sqrt{(1+2.77)(1+11.09)} =
6.75$ (book 6.9); $P_u = 3.77$ min (book 4.0). With $K = 0.09$ (Ch. 10)
the actual controller gain is $K_c = K_1/0.09$, e.g. PID
$K_c = 4.05/0.09 = 45$.

### Why $\\tau_I = 4\\tau_D$ makes a double zero

$K_c\\frac{\\tau_D\\tau_Is^2 + \\tau_Is + 1}{\\tau_Is}$ with $\\tau_I = 4\\tau_D$:
numerator $4\\tau_D^2s^2 + 4\\tau_Ds + 1 = (2\\tau_Ds + 1)^2$ (Eq. 16.6):
two identical PD factors, corner at $1/2\\tau_D$.
""")
d.code("Check -- the double zero", ["Roots of the Z-N PID numerator"], """
tD = 0.47
print(np.roots([4 * tD**2, 4 * tD, 1]), "-> -1/(2 tD) =",
      round(-1 / (2 * tD), 3))
""", """
The numerator 4 tD^2 s^2 + 4 tD s + 1 has a repeated root at
-1/(2 tD) = -1.064 for tD = 0.47 min: the two PD corners coincide, as
Eq. 16.6 states.
""")

d.write(OUT)
