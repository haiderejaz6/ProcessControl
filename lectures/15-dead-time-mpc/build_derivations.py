#!/usr/bin/env python3
"""Build the Lecture 15 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-15_Derivations.ipynb")
d = Deck()
d.title("Lecture 15 Companion", "Full Derivations and Worked Answers",
        "Cecil, Ch. 8, Sec. 8.2-8.3", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
from scipy.linalg import toeplitz
""")

d.part("A", "Why the Smith Predictor Removes the Dead Time",
       "Cecil, Ch. 8, Sec. 8.2", "cecil-ch08")
d.sub("""
Process $G(s)e^{-\\theta s}$, model $\\hat G(s)e^{-\\hat\\theta s}$,
controller $G_c$. The PV is $C + \\hat GM - \\hat Ge^{-\\hat\\theta s}M$;
with $M = G_c(R - PV)$ and a perfect model ($\\hat G = G$,
$\\hat\\theta = \\theta$) the $e^{-\\theta s}$ terms cancel in the loop:

$$\\frac{C}{R} = \\frac{G_cG}{1 + G_cG}\\,e^{-\\theta s}$$

The characteristic equation $1 + G_cG = 0$ has no dead time: the
controller can be tuned for $G$ alone. The response is delayed by
$\\theta$ but not destabilized by it. For a load entering at the
process input, the correction still needs one dead time to show, so
the best possible recovery takes about two dead times (Sec. 8.2).
""")
d.code("Check -- the closed loop with a perfect predictor", [
    "Symbolic: substitute the PV and solve for $C/R$",
], """
s, th = sp.symbols("s theta", positive=True)
Gc, G, R, C, M = sp.symbols("G_c G R C M")
pv = C + G*M - G*sp.exp(-th*s)*M
sol = sp.solve([sp.Eq(M, Gc*(R - pv)), sp.Eq(C, G*sp.exp(-th*s)*M)],
               [C, M])
print(sp.simplify(sol[C] / R))
""", """
Prints G*G_c*exp(-s*theta)/(G*G_c + 1): the dead time multiplies the
loop from outside; it no longer appears in the denominator.
""")

d.part("B", "QDMC: the Least-Squares Moves",
       "Cecil, Ch. 8, Sec. 8.3", "cecil-ch08")
d.sub("""
$\\Phi = (\\hat{\\mathbf e} - A\\Delta\\mathbf m)^T(\\hat{\\mathbf e} -
A\\Delta\\mathbf m) + k^2\\Delta\\mathbf m^T\\Delta\\mathbf m$.
$\\nabla\\Phi = -2A^T(\\hat{\\mathbf e} - A\\Delta\\mathbf m) +
2k^2\\Delta\\mathbf m = 0 \\Rightarrow (A^TA + k^2I)\\Delta\\mathbf m =
A^T\\hat{\\mathbf e}$.

Same algebra as the normal equations of Lecture 10 and ridge
regression: the moves are the "parameters", the predicted errors the
"data".

Cecil's numbers ($R = 4$, $L = 2$): $A^TA = \\begin{bmatrix} 0.04965 &
0.03538\\\\ 0.03538 & 0.02715\\end{bmatrix}$ (Cecil prints one sign
wrong), inverse $\\begin{bmatrix} 281.0 & -366.2\\\\ -366.2 &
513.9\\end{bmatrix}$.
""")
d.code("Check -- $A^TA$ and its inverse", ["From Table 8.3"], """
s4 = np.array([0, -0.05, -0.095, -0.125, -0.15])
A = toeplitz(s4[1:5], [0, 0])
print((A.T @ A).round(5)); print(np.linalg.inv(A.T @ A).round(1))
""", """
Prints [[0.04965 0.03538] [0.03538 0.02715]] -- both off-diagonal
entries positive (A^T A is symmetric) -- and the inverse
[[281.0 -366.2] [-366.2 513.9]], Cecil's values.
""")

d.part("C", "Answers for the Lecture's Your Turns",
       "Cecil, Ch. 8, Sec. 8.2-8.3", "cecil-ch08")
d.sub("""
- Lambda with $\\tau_{CL} = 2\\theta$: $K_C = 0.17/(3.6 \\times 0.67) =
  0.070$.
- Square DMC: $\\Delta m = \\hat e(1)/s(1) = 5/(-0.05) = -100$ lb/min.
  At $\\Delta t = 5$ min, $s(1) = -0.0147$ and the move is $-340$
  (Cecil's table); at 1 min, $s(1) = 0$.
- Steady-state move for +5 F: $5/(-0.225) = -22.2$ lb/min.
- QDMC feasibility with dead time: $R > \\mathrm{int}(\\theta/\\Delta t) +
  L$.
""")
d.code("Check -- the square-DMC first move against the sampling time", [
    "$s(1)$ from the fitted FOPDT at 15, 5 and 1 min",
], """
K, T, th = -0.2312, 55.49, 1.353
for dt in [15.0, 5.0, 1.0]:
    s1 = K * (1 - np.exp(-max(dt - th, 0) / T))
    print(f"dt = {dt:4}: s(1) = {s1:.4f}, move = "
          f"{5 / s1 if s1 else float('inf'):.0f} lb/min")
""", """
Prints s(1) = -0.0504 (Cecil's raw data: -0.050), -0.0147 and 0
(shown as -0.0000); moves -99, -340 and inf. Shorter sampling makes the square DMC
controller more aggressive, then impossible.
""")

d.write(OUT)
