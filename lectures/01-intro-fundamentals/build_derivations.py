#!/usr/bin/env python3
"""Build the Lecture 1 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-01_Derivations.ipynb")
d = Deck()
d.title("Lecture 1 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 1; Cecil Smith, Intro and Sec. 1.1-1.2",
        date=False)
d.slide("""
## How to use this notebook

Same Part order as the lecture. Each Part gives the complete algebra
that the lecture works on the board, then a code cell that checks it.
Your Turn answers are worked in full at the end of each Part.
""")
d.setup(["Imports used below"], """
import numpy as np
import sympy as sp
from scipy.stats import norm
""")

# ---------------------------------------------------------------- A
d.part("A", "Hot Water Tank under On/Off Control",
       "Coughanowr & LeBlanc, Ch. 1, Example 1.1", "coughanowr-ch1")
d.sub("""
### Heat-up time and duty cycle

Model: $\\tau\\,dT/dt = (T_i - T) + Kq$, with $\\tau = 30$ min,
$K = 90$ F, $T_i = 60$ F.

**Heat-up** with the burner fully on ($q = 1$) from $T(0) = 100$ F: the
steady value is $T_i + K = 150$ F, so
$T(t) = 150 - 50\\,e^{-t/30}$. Setting $T = 130$:
$e^{-t/30} = 0.4$, $t = 30\\ln 2.5 = 27.5$ min.

**Duty cycle** at 130 F: the average heat input must equal the
steady requirement, $\\bar q = (130 - T_i)/K$: 0.778 at $T_i = 60$ F,
0.889 at $T_i = 50$ F (Your Turn 1).
""")
d.code("Check -- heat-up time with SymPy", [
    "`dsolve` with the initial condition, then solve for 130 F",
], """
t = sp.symbols("t", positive=True)
T = sp.Function("T")
ode = sp.Eq(30 * T(t).diff(t), (60 - T(t)) + 90)   # q = 1
sol = sp.dsolve(ode, T(t), ics={T(0): 100}).rhs
t130 = sp.solve(sp.Eq(sol, 130), t)[0]
print(sol)
print(sp.simplify(t130 - 30 * sp.log(sp.Rational(5, 2))))
print(f"{float(t130):.2f} min")
""", """
`dsolve` solves the first-order ODE with T(0) = 100; the solution is
150 - 50 exp(-t/30). `sp.solve(sp.Eq(sol, 130), t)` inverts it. SymPy writes the answer as
the log of a large fraction, so the second print subtracts 30 ln 2.5
and simplifies: 0, i.e. the two are equal. The third print gives 27.49
min, the 27.4 min seen in the lecture's sampled loop (the loop reports
the first 0.1-min sample at or above 130 F).
""")
d.sub("""
### Your Turn A, worked

1. $\\bar q = (130 - 50)/90 = 0.889$: on 89% of the time.
2. `thermostat(131.0, T_set=132.0)`: $e = 1.0 > 0$, prints `1.0`;
   `thermostat(129.9, T_set=132.0)`: $e = 2.1 > 0$, prints `1.0`.
""")

# ---------------------------------------------------------------- B
d.part("B", "Offset under P Control; Why PI Removes It",
       "Coughanowr & LeBlanc, Ch. 1", "coughanowr-ch1")
d.sub("""
### P control, full algebra

Steady state: $0 = (T_i - T) + K[q_s + K_c(T_{set} - T)]$.
At the design point $0 = (60 - 130) + Kq_s$. Subtract, with
$T' = T - 130$ and $T_i' = T_i - 60$:

$$0 = T_i' - T' - KK_cT' \\;\\Rightarrow\\; T' = \\frac{T_i'}{1 + KK_c},
\\qquad e_{ss} = -T' = \\frac{-T_i'}{1 + KK_c}$$

With $T_i' = -10$ F, $K = 90$ F: $e_{ss} = 10/(1 + 90K_c)$.
""")
d.sub("""
### PI control: why the offset must vanish

$q = q_s + K_c\\left(e + \\frac{1}{\\tau_I}\\int_0^t e\\,dt'\\right)$.
At a steady state every signal is constant, so $q$ is constant. If
$e \\ne 0$ the integral grows linearly in time and $q$ cannot be
constant. Therefore any steady state has $e = 0$: no offset, whatever
$K_c$ and $\\tau_I$ -- provided the loop settles (Part C).
""")
d.code("Check -- offset formula against the simulated P loop", [
    "Re-run the lecture's loop for several gains; compare",
], """
def final_T(Kc, dt=0.1, t_end=300.0):
    T = 130.0
    for k in range(int(t_end / dt)):
        Ti = 60.0 if k * dt < 10 else 50.0
        q = np.clip(70/90 + Kc * (130.0 - T), 0, 1)
        T += dt * ((Ti - T) + 90 * q) / 30
    return T
for Kc in [0.01, 0.05, 0.2]:
    print(Kc, round(130 - final_T(Kc), 3), round(10/(1+90*Kc), 3))
""", """
`final_T` is the lecture's P loop, run long enough (300 min) to settle.
Each line prints the gain, the simulated offset and the formula. They
agree to three decimals: 5.263, 1.818, 0.526 F. Kc = 0.2 is Your Turn
B1 (0.53 F).
""")
d.sub("""
### Your Turn B, worked

1. $e_{ss} = 10/(1 + 18) = 0.53$ F.
2. `run(0.0)[-1]`: no feedback, $q$ stays $70/90$. The tank obeys
   $30\\,dT/dt = 50 - T + 70$ from $T = 130$ at $t = 10$ min:
   $T = 120 + 10e^{-(t-10)/30}$; at $t = 150$, $120.09$ F, printed as
   120.1 to one decimal.
""")

# ---------------------------------------------------------------- C
d.part("C", "The Gain Limit with Measurement and Burner Lags",
       "Coughanowr & LeBlanc, Ch. 1 (made exact in Ch. 13)",
       "coughanowr-ch1")
d.sub("""
### Characteristic equation (a preview of Lecture 6)

Three first-order lags in the loop -- tank (30 min), burner (3 min),
sensor (2 min) -- and a P controller with loop gain $KK_c$. The closed
loop is stable when every root of

$$(30s+1)(3s+1)(2s+1) + KK_c = 180s^3 + 156s^2 + 35s + (1 + KK_c) = 0$$

has a negative real part. For a cubic $a_3s^3 + a_2s^2 + a_1s + a_0$
(all positive) the Routh condition is $a_2a_1 > a_3a_0$:
$156 \\times 35 > 180(1 + KK_c)$, so $KK_c < 29.33$,
$K_c < 0.326$ /F.
""")
d.code("Check -- the boundary from the roots", [
    "`np.roots` for gains either side of 0.326 /F",
    "Positive real part = unstable",
], """
for Kc in [0.25, 0.32, 0.33, 0.40]:
    r = np.roots([180, 156, 35, 1 + 90 * Kc])
    print(f"Kc = {Kc}: max Re = {r.real.max():+.4f}")
Kcu = (156 * 35 / 180 - 1) / 90
print(f"Routh: Kc,u = {Kcu:.4f} /F")
""", """
`np.roots` takes polynomial coefficients from the highest power and
returns all roots. The largest real part changes sign between 0.32 and
0.33 /F, and the Routh formula gives 0.3259 /F. This matches the
lecture's simulation: 0.25 oscillated and decayed, 0.4 grew until the
burner saturated.
""")
d.sub("""
### Your Turn C, worked

1. True error $130 - 128 = 2.0$ F; apparent $130 - 129 = 1.0$ F.
2. Only $K_c = 0.4$ hits the 0/1 limits (about 30% of the time).
   Saturation caps the growth, giving a constant-amplitude limit cycle.
""")

# ---------------------------------------------------------------- D
d.part("D", "Variance, Target and Block Arithmetic",
       "Cecil Smith, Introduction and Sec. 1.1-1.2", "cecil-intro-1.1-1.2")
d.sub("""
### Violation rate and the target shift

For $y \\sim N(\\mu, \\sigma^2)$ and target $\\mu = L - z\\sigma$:
$P(y > L) = P(Z > z) = 1 - \\Phi(z)$, independent of $\\sigma$. With
$z = 2$, $1 - \\Phi(2) = 2.28\\%$. Narrowing from $\\sigma_1$ to
$\\sigma_2$ at fixed risk moves the target by $z(\\sigma_1 - \\sigma_2)$.

### Lag of a moving average on a ramp

Input $x_k = a + bkT_s$. The average of the last $N$ samples is
$a + bT_s(k - \\frac{N-1}{2})$, so it trails by $\\frac{N-1}{2}T_s$ in
time, $b\\frac{N-1}{2}T_s$ in value: $0.02 \\times 9.5 \\times 0.5 =
0.095$ F for the lecture's numbers.
""")
d.code("Check -- the two formulas", [
    "`norm.sf(z)` is $1 - \\Phi(z)$, the upper-tail probability",
], """
print(f"P(y > L) for z = 2: {norm.sf(2):.4f}")
N, Ts, b = 20, 0.5, 0.02
print(f"ramp lag: {b * (N - 1) / 2 * Ts:.3f} F")
""", """
`norm.sf` is the survival function of the standard normal: 0.0228, the
2.3% quoted in the lecture (the simulation gave 2.2% from 10,000
random samples). The ramp lag prints 0.095 F, the value the lecture's
moving-average cell measured.
""")
d.sub("""
### Your Turn D, worked

1. $\\Delta = 2(0.8 - 0.4) = 0.8$.
2. `summer(50, 20, k0=5, k1=0.5, k2=2)` $= 5 + 25 + 40 = 70.0$;
   `flow_from_valve(60.0)` $= 70 \\times 0.6 = 42.0$ gpm.
""")

d.write(OUT)
