#!/usr/bin/env python3
"""Build the Lecture 7 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-07_Derivations.ipynb")
d = Deck()
d.title("Lecture 7 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 15", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
""")

d.part("A", "Why the Substitution Rule Works",
       "Coughanowr & LeBlanc, Ch. 15, Sec. 15.3", "coughanowr-ch15")
d.sub("""
### Sketch of the general proof (Sec. 15.3)

For $\\sum a_k Y^{(k)} = A\\sin\\omega t$ the particular solution is
$Y_p = D_1\\sin(\\omega t + D_2)$. Write both sines as complex
exponentials; matching the $e^{j\\omega t}$ terms gives
$D_1e^{jD_2}\\sum a_k(j\\omega)^k = A$, i.e.
$D_1/A = |1/\\sum a_k(j\\omega)^k| = |G(j\\omega)|$ and
$D_2 = \\angle G(j\\omega)$. If the system is stable the
complementary solution decays, so $Y_p$ is what remains.

### Ex. 15.4 in full

$\\tau_1 = \\rho V/w = 60.8(15/7.48)/600 = 0.203$ min;
$\\tau_2 = L/v = 2/[600/(60.8 \\times 0.196)] = 0.0397$ min.
At $\\omega = 46$: tank $AR = 1/\\sqrt{1 + 9.34^2} = 0.107$,
$\\phi_1 = -83.9^\\circ$; pipe $\\phi_2 = -1.826$ rad $= -104.6^\\circ$.
$T_m = 170 + 0.53\\sin(46t - 188.5^\\circ)$.
""")
d.code("Check -- Ex. 15.4 numbers", ["Tank, pipe and total"], """
w = 46.0
tank = 1 / (1 + 1j * w * 0.203); pipe = np.exp(-1j * w * 0.0397)
for name, g in [("tank", tank), ("pipe", pipe), ("total", tank*pipe)]:
    ph = np.degrees(np.angle(g))
    print(f"{name}: AR {abs(g):.3f}, phase {ph:.1f} deg")
print("unwrapped total phase:",
      round(np.degrees(np.angle(tank)) - np.degrees(w * 0.0397), 1))
""", """
The two factors are evaluated separately at omega = 46. The pipe's
-104.6 deg is shown as is; the total's angle, -188.5 deg, is wrapped by
`np.angle` to +171.5 deg. Adding the individual phases (last line)
avoids the wrap and gives -188.5 deg.
""")

d.part("B", "Bode Asymptotes and Corner Errors",
       "Coughanowr & LeBlanc, Ch. 15, Sec. 15.2", "coughanowr-ch15")
d.sub("""
### First-order corner error

At $\\omega = 1/\\tau$ the asymptotes give $AR = 1$ but the true
$AR = 1/\\sqrt2 = 0.707$: an error of $-3$ dB, the largest anywhere. One
octave away ($\\omega\\tau = 0.5$ or 2) the error is about $-1$ dB.

### Prob. 15.1(a)

$G = 100/[(10s+1)(s+1)]$: corners at 0.1 and 1 rad/time. At
$\\omega = 10$: $10\\omega = 100$, so $|10j\\omega + 1| = \\sqrt{10001}
= 100.0$ and $|j\\omega + 1| = \\sqrt{101} = 10.05$: $AR = 0.0995$,
phase $= -(89.4 + 84.3) = -173.7^\\circ$.
""")
d.code("Check -- Prob. 15.1(a) at $\\omega = 10$", ["Direct evaluation"], """
s = 10j
G = 100 / ((10 * s + 1) * (s + 1))
print(f"AR = {abs(G):.4f}, phase = {np.degrees(np.angle(G)):.1f} deg")
""", """
Prints AR = 0.0995 and phase = -173.7 deg, the hand values.
""")

d.part("C", "PI, PD and Dead Time",
       "Coughanowr & LeBlanc, Ch. 15, Sec. 15.2", "coughanowr-ch15")
d.sub("""
### PI controller

$K_c(1 + 1/j\\omega\\tau_I) = K_c(1 - j/\\omega\\tau_I)$:
$AR = K_c\\sqrt{1 + 1/(\\omega\\tau_I)^2}$,
$\\phi = \\tan^{-1}(-1/\\omega\\tau_I)$: $-90^\\circ$ at low frequency,
$0^\\circ$ at high, $-45^\\circ$ at the corner $\\omega = 1/\\tau_I$.

### Prob. 15.2 by hand

At high frequency the lag of B behind A tends to
$90 - 90 = 0$; the maximum lag (29.8 deg near 1 cycle/min) occurs where
$\\frac{d}{d\\omega}[\\tan^{-1}\\omega\\tau_B - \\tan^{-1}0.1\\omega] = 0$,
i.e. $\\omega^2 = 1/(0.1\\tau_B)$. With $\\omega = 2\\pi(1.0)$:
$\\tau_B = 1/(0.1 \\times 39.5) = 0.25$ min, close to the least-squares
0.29 min.
""")
d.code("Check -- the maximum-lag estimate", ["Compare with the fitted value"], """
w_peak = 2 * np.pi * 1.0
print(f"tau_B from the peak: {1 / (0.1 * w_peak**2):.3f} min")
""", """
Prints 0.253 min. The peak in the data is not sharply located (29.8 deg
at 1.0 cycle/min, 28.2 at 0.8), so the one-point estimate is rougher
than the 0.290 min least-squares fit, which uses all nine points.
""")

d.write(OUT)
