#!/usr/bin/env python3
"""Build the Lecture 13 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-13_Derivations.ipynb")
d = Deck()
d.title("Lecture 13 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 23; Cecil, Ch. 7-8", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
s = sp.symbols("s")
""")

d.part("A", "Ex. 23.1 by Hand",
       "Coughanowr & LeBlanc, Ch. 23, Sec. 23.1", "coughanowr-ch23")
d.sub("""
### From the balances to Eq. 23.21

Eq. 23.16 with $A_1 = 1$, $R_1 = 1/2$, $R_3 = 1$:
$\\dot c_1 = m_1 - 2(c_1 - c_2) - c_1 = m_1 - 3c_1 + 2c_2$.
Eq. 23.17 with $A_2 = 1/2$, $R_2 = 2$:
$\\tfrac12\\dot c_2 = m_2 + 2(c_1 - c_2) - c_2/2$, i.e.
$\\dot c_2 = 2m_2 + 4c_1 - 5c_2$.

$sI - A = \\begin{bmatrix} s + 3 & -2\\\\ -4 & s + 5\\end{bmatrix}$,
$\\det = s^2 + 8s + 7 = (s+1)(s+7)$,
$(sI - A)^{-1} = \\frac{1}{(s+1)(s+7)}\\begin{bmatrix} s + 5 & 2\\\\ 4 &
s + 3\\end{bmatrix}$; times $B = \\mathrm{diag}(1, 2)$ doubles the
second column: Eq. 23.21.
""")
d.code("Check -- eigenvalues are the poles", ["`np.linalg.eigvals`"], """
print(np.linalg.eigvals(np.array([[-3.0, 2.0], [4.0, -5.0]])))
""", """
Prints -1 and -7 (in some order): the roots of (s + 1)(s + 7).
""")

d.part("B", "Why Rows and Columns of the RGA Sum to One",
       "Cecil, Ch. 7, Sec. 7.4", "cecil-ch07")
d.sub("""
For 2 x 2, with $\\Delta = K_{11}K_{22} - K_{12}K_{21}$:
$(K^{-1})^T = \\frac1\\Delta\\begin{bmatrix} K_{22} & -K_{21}\\\\ -K_{12}
& K_{11}\\end{bmatrix}$, so
$\\lambda_{11} = K_{11}K_{22}/\\Delta$,
$\\lambda_{12} = -K_{12}K_{21}/\\Delta$ and
$\\lambda_{11} + \\lambda_{12} = \\Delta/\\Delta = 1$. In general,
$\\sum_j K_{ij}(K^{-1})_{ji} = (KK^{-1})_{ii} = 1$.

### Cecil's process test (Fig. 7.13)

$K_{11} = (57.2 - 60.0)/5 = -0.56$ psig/%,
$K'_{11} = (40.1 - 60.0)/5 = -3.98$ psig/%, $\\lambda_{11} = 0.14$
(the steady-state model gives 0.10; the dynamic simulation is more
detailed).
""")
d.code("Check -- symbolic RGA of a 2 x 2", ["Sum the first row"], """
K = sp.Matrix(2, 2, sp.symbols("K11 K12 K21 K22"))
L = sp.matrix_multiply_elementwise(K, K.inv().T)
print(sp.simplify(L[0, 0]), "|", sp.simplify(L[0, 0] + L[0, 1]))
""", """
`sp.matrix_multiply_elementwise` is the symbolic version of numpy's
`*`. lambda_11 prints as K11*K22/(K11*K22 - K12*K21) and the row sum
simplifies to 1.
""")

d.part("C", "Ex. 23.2 with PI Primary Controllers",
       "Coughanowr & LeBlanc, Ch. 23, Sec. 23.1", "coughanowr-ch23")
d.sub("""
With $G_{c11} = K_1(1 + 1/s)$, $G_{c22} = K_2(1 + 1/s)$, Eqs.
23.14-23.15 give $G_{c12} = \\frac{-4K_2(s + 1)}{s(s + 5)}$ and
$G_{c21} = \\frac{-2K_1(s + 1)}{s(s + 3)}$ (the book's PI case,
Fig. 23-17). The decoupled loop is
$G_{o11} = \\frac{K_1(s + 1)}{s(s + 3)}$: integral action, no offset.
""")
d.code("Check -- the PI cross-controllers", ["Same formula, PI primaries"], """
K1, K2 = sp.symbols("K1 K2", positive=True)
D = (s + 1) * (s + 7)
G11, G12, G21, G22 = (s + 5)/D, 4/D, 4/D, 2*(s + 3)/D
pi1, pi2 = K1*(1 + 1/s), K2*(1 + 1/s)
print(sp.factor(-G12*pi2/G11), "|", sp.factor(-G21*pi1/G22))
print(sp.factor(G11*pi1 + G12*sp.factor(-G21*pi1/G22)))
""", """
Prints -4K2(s + 1)/(s(s + 5)) and -2K1(s + 1)/(s(s + 3)), and the
decoupled loop K1(s + 1)/(s(s + 3)).
""")

d.part("D", "Ex. 23.4: Routh on the Reduced Polynomial",
       "Coughanowr & LeBlanc, Ch. 23, Sec. 23.2", "coughanowr-ch23")
d.sub("""
$|I + G_pG_c| = \\frac{[(s+1)(s+7) + K_1(s+5)][(s+1)(s+7) + 2K_2(s+3)]
- 16K_1K_2}{[(s+1)(s+7)]^2}$. The numerator is the book's quartic;
it equals $(s+1)(s+7)\\,[s^2 + (8 + K_1 + 2K_2)s + 7 + 5K_1 + 6K_2 +
2K_1K_2]$. The factor $(s+1)(s+7)$ cancels with the denominator --
those are open-loop poles, not closed-loop ones. Stability:
$K_1 + 2K_2 > -8$ and $(2K_1 + 6)(K_2 + 2.5) > 8$.
""")
d.code("Check -- the quartic factors", ["Expand and factor"], """
K1, K2 = sp.symbols("K1 K2")
q = ((s+1)*(s+7) + K1*(s+5)) * ((s+1)*(s+7) + 2*K2*(s+3)) - 16*K1*K2
print(sp.factor(sp.expand(q)))
""", """
Prints (s + 1)(s + 7)(2K1K2 + K1 s + 5K1 + 2K2 s + 6K2 + s^2 + 8s + 7):
the quartic of Eq. 23.34 contains the open-loop factor (s + 1)(s + 7).
""")

d.write(OUT)
