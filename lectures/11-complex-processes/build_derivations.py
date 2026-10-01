#!/usr/bin/env python3
"""Build the Lecture 11 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-11_Derivations.ipynb")
d = Deck()
d.title("Lecture 11 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 20", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
from scipy.special import erfc
""")

d.part("A", "Kettle: from Eq. 20.1 to Eq. 20.9",
       "Coughanowr & LeBlanc, Ch. 20, Sec. 20.1", "coughanowr-ch20")
d.sub("""
### Linearized water balance

Substituting Eqs. 20.4-20.5 into Eq. 20.1:
$C[(T_{is} - T_{os})(w - w_s) + w_s(T_i - T_o)] + UA(T_v - T_o) =
mC\\,dT_o/dt$. Subtract the steady state (Eq. 20.7) and transform:
$(mCs + UA + w_sC)T_o' = w_sCT_i' + UAT_v' - C(T_{os} - T_{is})W'$.
Divide by $UA + w_sC$: Eq. 20.9.

### Water flow to temperature in the closed kettle

With $G_2 = K_2/(\\tau_ws + 1)$, $G_4 = 1/(\\tau_vs + 1)$ and
$G_c = K_c$, $H = 1$, Eq. 20.21 reduces to the second-order Eq. 20.22
with $D_1 = 1 + K_5/R_v + K_cK_vK_2K_5 - K_2 > 0$ because $K_2 < 1$.
""")
d.code("Check -- the steady state is the linear model's fixed point", [
    "Exact steady state against $T_{os} + K_2T_v'$ for a steam change",
], """
To = lambda w, Tv: (w * 60 + 750 * Tv) / (w + 750)
K2 = 750 / (750 + 250)
print(To(250, 260) - To(250, 250), K2 * 10)
""", """
Both print 7.5: Tv enters Eq. 20.1 linearly, so its gain K2 is exact
at fixed w. Only the products wTi and wTo needed approximation.
""")

d.part("B", "Absorber: Eliminating $X_1$",
       "Coughanowr & LeBlanc, Ch. 20, Sec. 20.2", "coughanowr-ch20")
d.sub("""
From $sX_2 = cX_1 - aX_2$: $X_1 = (s + a)X_2/c$. Into the first:
$(s + a)^2X_2/c = bX_2 + cX_0$, so
$X_2/X_0 = c^2/[(s + a)^2 - bc]$. Divide by $a^2 - bc$: Eq. 20.34.
$\\zeta^2 = a^2/(a^2 - bc)$; with $a = b + c$:
$\\zeta^{-2} = 1 - \\frac{bc}{(b + c)^2} = 1 - \\frac{r}{(1 + r)^2}$,
$r = Vm/L$. Since $0 < r/(1 + r)^2 \\le 1/4$ (maximum at $r = 1$),
$1 < \\zeta \\le 2/\\sqrt3 = 1.155$: always overdamped, never far
from critical, and most damped at $Vm = L$.
""")
d.code("Check -- the range of the damping ratio", ["Scan $r = Vm/L$"], """
r = np.logspace(-2, 2, 2001)
zeta = 1 / np.sqrt(1 - r / (1 + r)**2)
print(round(zeta.min(), 4), round(zeta.max(), 4), r[zeta.argmax()])
""", """
Prints a minimum of 1.0049 (at the ends of the scan, r = 0.01 and
100) and a maximum of 1.1547 = 2/sqrt 3 at r = 1.0. The two-plate
absorber is overdamped for every flow ratio. The lecture's L/H = 1,
Vm/H = 1.5 give r = 1.5, r/(1 + r)^2 = 0.24 and zeta = 1.147.
""")

d.part("C", "Conduction into a Solid and the Exchanger",
       "Coughanowr & LeBlanc, Ch. 20, Sec. 20.3", "coughanowr-ch20")
d.sub("""
### The slab (Eqs. 20.39-20.53)

$\\alpha T_{xx} = T_t$; Laplace in $t$: $\\alpha\\bar T'' = s\\bar T$, so
$\\bar T = A_1e^{-\\sqrt{s/\\alpha}x}$ (bounded as $x \\to \\infty$).
$\\bar T(L,s)/\\bar T(0,s) = e^{-\\sqrt{s/\\alpha}L}$; step:
$T(L,t) = \\mathrm{erfc}[L/\\sqrt{4\\alpha t}]$. With $s = j\\omega$:
$AR = e^{-\\sqrt{\\omega/2\\alpha}L}$, phase $-\\sqrt{\\omega/2\\alpha}L$
-- unbounded.

### The exchanger (Eqs. 20.61-20.65)

$dT'/dx + \\frac{s + 1/\\tau}{v}T' = \\frac{1}{\\tau v}T_v'$ with
$T'(0,s)$ given: integrating factor $e^{(s + 1/\\tau)x/v}$ gives
Eq. 20.63; at $x = L$, $e^{-(\\tau s + 1)L/\\tau v} = Ke^{-\\tau_ds}$.
""")
d.code("Check -- the slab step response", [
    "$\\mathrm{erfc}$ at a few values of $\\alpha t/L^2$",
], """
for z in [0.05, 0.1, 0.5, 1.0, 5.0]:
    print(f"alpha t / L^2 = {z}: T(L,t) = {erfc(0.5 / np.sqrt(z)):.3f}")
""", """
Prints 0.002, 0.025, 0.317, 0.480, 0.752: Fig. 20-7. The response is
slow to finish (0.75 at a dimensionless time of 5) -- the long tail of
a distributed system.
""")
d.code("Check -- Ex. 20.1 numbers", ["Velocity, tau, td, K"], """
Ai = np.pi * (0.584 / 12)**2 / 4
v = 2 / 7.48 / Ai / 60
inv_tau = np.pi * (0.584 / 12) * 100 / (Ai * 62.4) / 3600
print(f"Ai = {Ai:.5f} ft2, v = {v:.2f} ft/s, tau = {1/inv_tau:.1f} s, "
      f"td = {40/v:.1f} s, K = {np.exp(-40/v*inv_tau):.3f}")
""", """
Prints Ai = 0.00186 ft2, v = 2.40 ft/s, tau = 27.3 s, td = 16.7 s and
K = 0.543. U is per hour, hence the /3600.
""")

d.write(OUT)
