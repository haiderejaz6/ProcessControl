#!/usr/bin/env python3
"""Build the Lecture 10 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-10_Derivations.ipynb")
d = Deck()
d.title("Lecture 10 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 18", date=False)
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
""")

d.part("A", "The Reaction Curve of $1/(s+1)^4$",
       "Coughanowr & LeBlanc, Ch. 18, Sec. 18.2", "coughanowr-ch18")
d.sub("""
### Step response and its inflection point

$C(s) = \\frac{1}{s(s+1)^4}$. Partial fractions (or Table 2.1):
$c(t) = 1 - e^{-t}(1 + t + t^2/2 + t^3/6)$. Differentiate: every term
cancels except $c'(t) = t^3e^{-t}/6$ -- the impulse response of
$1/(s+1)^4$. Then $c''(t) = e^{-t}t^2(3 - t)/6 = 0$ at $t = 3$.

$S = c'(3) = 27e^{-3}/6 = 0.2240$; $c(3) = 1 - 13e^{-3} = 0.3528$.
Tangent: $c = 0.3528 + 0.2240(t - 3)$ meets $c = 0$ at $T_d = 1.425$;
$T = 1/S = 4.463$.

### Why Cohen-Coon fails here

Table 18.2 was derived for a true FOPDT. Here it gives
$K_c = 2.91$, 73% of $K_{cu} = 4$, together with fast integral action
($\tau_I = 2.86 < P_u/2$). The PI's extra phase lag at the crossover
lowers the usable gain below $K_{cu}$, so the loop is unstable. The
least-squares fit sees the whole curve, gives a smaller $T/T_d$, and
a stable $K_c$.
""")
d.code("Check -- the inflection point symbolically", [
    "Differentiate and solve with sympy",
], """
t = sp.symbols("t", positive=True)
c = 1 - sp.exp(-t) * (1 + t + t**2/2 + t**3/6)
c1 = sp.simplify(sp.diff(c, t))
ti = sp.solve(sp.diff(c1, t), t)
S, c3 = c1.subs(t, 3), c.subs(t, 3)
print(c1, ti, float(S), float(c3), float(3 - c3/S), float(1/S))
""", """
Prints t**3*exp(-t)/6, the inflection [3], S = 0.2240,
c(3) = 0.3528, Td = 1.425 and T = 4.463: the values Code 1/4 found
numerically from the sampled curve.
""")

d.part("B", "Least Squares in Closed Form",
       "Coughanowr & LeBlanc, Ch. 18, Sec. 18.3", "coughanowr-ch18")
d.sub("""
### The normal equations

$J(\\theta) = (y - \\Phi\\theta)^T(y - \\Phi\\theta) = y^Ty -
2\\theta^T\\Phi^Ty + \\theta^T\\Phi^T\\Phi\\theta$.
$\\nabla J = -2\\Phi^Ty + 2\\Phi^T\\Phi\\theta = 0
\\Rightarrow \\Phi^T\\Phi\\theta = \\Phi^Ty$.
$\\Phi^T\\Phi$ is positive definite when the columns of $\\Phi$ are
independent, i.e. when the input *excites* the process; a constant
input makes $y_{k-1}$ and $u_{k-1-d}$ proportional at steady state
and the matrix singular.

### Discrete FOPDT (zero-order hold)

Over one sample with $u$ held: $y(t_k) = e^{-\\Delta t/T}y(t_{k-1}) +
K_p(1 - e^{-\\Delta t/T})u$ -- the exact solution of the first-order
ODE with constant forcing, so no Euler approximation is involved.
""")
d.code("Check -- a constant input makes $\\Phi^T\\Phi$ singular", [
    "Steady data: both columns proportional",
], """
y = np.full(50, 2.0); u = np.full(50, 1.0)       # at steady state
Phi = np.column_stack([y[:-1], u[:-1]])
print(np.linalg.matrix_rank(Phi.T @ Phi), np.linalg.cond(Phi.T @ Phi))
""", """
Prints rank 1 and a condition number around 1e16 (or inf): with no
excitation the data cannot separate a from b. Identification tests
must move the input.
""")

d.part("C", "Gain of the Gravity-Drained Tank",
       "Coughanowr & LeBlanc, Ch. 18, Sec. 18.3", "coughanowr-ch18")
d.sub("""
### Linearization

$A\\,dh/dt = q - c\\sqrt h$. Steady state $h_s = (q_s/c)^2$. Linearize:
$\\sqrt h \\approx \\sqrt{h_s} + (h - h_s)/(2\\sqrt{h_s})$, so
$A\\,dh'/dt = q' - \\frac{c}{2\\sqrt{h_s}}h'$: gain
$K = 2\\sqrt{h_s}/c = 2q_s/c^2$, time constant $\\tau = 2A\\sqrt{h_s}/c$.

With $A = 2$, $c = 0.5$: at $q_s = 1$, $K = 8$, $\\tau = 16$ min; at
$q_s = 1.4$, $K = 11.2$, $\\tau = 22.4$ min. The linear model of Part D
learned a gain near the low-flow value: its final level for the
1.0 -> 1.4 step, 6.80, implies $(6.80 - 4)/0.4 = 7.0$, while the true
plant needs $(7.84 - 4)/0.4 = 9.6$ on average over that step.
""")
d.code("Check -- local gains along the step", [
    "Linearized gain $2q/c^2$ and the average over 1.0 -> 1.4",
], """
c = 0.5
for q in [1.0, 1.2, 1.4]:
    print(f"q = {q}: local gain {2*q/c**2:.1f}")
print("average 1.0->1.4:", round(((1.4/c)**2 - (1/c)**2) / 0.4, 1))
""", """
Prints local gains 8.0, 9.6 and 11.2, and an average gain of 9.6 over
the step (the secant of h = (q/c)^2). The linear model's 7.0 is below
even the low-flow local gain: fitted with one set of coefficients
across the whole training range, it compromises.
""")

d.write(OUT)
