#!/usr/bin/env python3
"""Build the Lecture 2 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-02_Derivations.ipynb")
d = Deck()
d.title("Lecture 2 Companion", "Full Derivations and Worked Answers",
        "Coughanowr & LeBlanc, Ch. 2-3", date=False)
d.setup(["Imports used below"], """
import sympy as sp
t, s = sp.symbols("t s", positive=True)
""")

# ---------------------------------------------------------------- A
d.part("A", "Mixing Scenario: Separation of Variables and Prob. 2.9",
       "Coughanowr & LeBlanc, Ch. 2, Sec. 2.1", "coughanowr-ch2")
d.sub("""
### Eq. 2.2 by separation

$5\\,dC_a/dt = 2 - C_a$. Separate: $\\frac{dC_a}{2 - C_a} = \\frac{dt}{5}$.
Integrate from $(0, 3)$: $-\\ln(2 - C_a)\\big|_3^{C_a} = t/5$, so
$\\ln\\frac{2 - C_a}{2 - 3} = -t/5$, i.e. $C_a - 2 = e^{-t/5}$.

### Prob. 2.9 (stream 1 raised to 20 L/min)

$v_3 = 40$ L/min, $C_{a3} = (20 + 80)/40 = 2.5$ g/L,
$\\tau = 150/40 = 3.75$ min. With $C_a(0) = 3$:
$3.75\\,dC_a/dt + C_a = 2.5$, so $C_a = 2.5 + 0.5e^{-t/3.75}$.
""")
d.code("Check -- Prob. 2.9 by dsolve", [
    "The same ODE with the new $\\tau$ and inlet",
], """
C = sp.Function("C")
ode = sp.Eq(sp.Rational(15, 4) * C(t).diff(t) + C(t),
            sp.Rational(5, 2))
print(sp.dsolve(ode, C(t), ics={C(0): 3}).rhs)
""", """
Rational numbers keep the result exact: 15/4 = 3.75 and 5/2 = 2.5.
`dsolve` returns 5/2 + exp(-4 t/15)/2, i.e. 2.5 + 0.5 e^(-t/3.75).
""")

# ---------------------------------------------------------------- B
d.part("B", "Energy Balance: Where the Reference Temperature Goes",
       "Coughanowr & LeBlanc, Ch. 2, Sec. 2.1", "coughanowr-ch2")
d.sub("""
### Tee

$\\rho v_1C_p(T_1 - T_{ref}) + \\rho v_2C_p(T_2 - T_{ref}) =
\\rho v_3C_p(T_3 - T_{ref})$. Since $v_1 + v_2 = v_3$, the $T_{ref}$
terms cancel: $v_1T_1 + v_2T_2 = v_3T_3$.

### Vessel

$\\rho v_3C_p(T_3 - T_{ref}) - \\rho v_3C_p(T - T_{ref}) + Q =
\\frac{d}{dt}[\\rho VC_p(T - T_{ref})]$. Constant $\\rho, V, C_p$:
divide by $\\rho v_3C_p$ to get Eq. 2.3,
$\\tau\\,dT/dt + T = T_3 + Q/(\\rho v_3C_p)$, $\\tau = V/v_3$.

### Prob. 2.9, energy part

$T_3 = (500 + 1100)/40 = 40$ C, $\\tau = 3.75$ min,
$Q/(\\rho v_3C_p) = 1.05\\times10^6/40000 = 26.25$ C, final $T = 66.25$ C,
$T(t) = 66.25 + 13.75\\,e^{-t/3.75}$.
""")
d.code("Check -- the reference temperature drops out", [
    "Keep $T_{ref}$ symbolic and simplify",
], """
v1, v2, T1, T2, T3, Tr = sp.symbols("v1 v2 T1 T2 T3 T_ref")
tee = sp.Eq(v1*(T1 - Tr) + v2*(T2 - Tr), (v1 + v2)*(T3 - Tr))
print(sp.solve(tee, T3)[0])
""", """
The tee balance is typed with T_ref everywhere and v3 = v1 + v2. Solving
for T3 gives (T1 v1 + T2 v2)/(v1 + v2): T_ref has vanished, as the book
states.
""")

# ---------------------------------------------------------------- C
d.part("C", "The Derivative Rule, Proved",
       "Coughanowr & LeBlanc, Ch. 2, Sec. 2.2", "coughanowr-ch2")
d.sub("""
### Eq. 2.6 by parts

$\\int_0^\\infty f'(t)e^{-st}dt$ with $u = e^{-st}$, $dv = f'dt$,
$du = -se^{-st}dt$, $v = f$:
$= [fe^{-st}]_0^\\infty + s\\int_0^\\infty fe^{-st}dt = -f(0) + sF(s)$.
Applied twice: $\\mathcal{L}\\{f''\\} = s^2F - sf(0) - f'(0)$.

### Ex. 2.4

$sx - 2 + 3x = 0 \\Rightarrow x(s) = 2/(s+3) \\Rightarrow x(t) = 2e^{-3t}$.
""")
d.code("Check -- second-derivative rule", [
    "Same test as in the lecture, one order higher",
], """
f = sp.cos(3 * t) + t**2
F = sp.laplace_transform(f, t, s, noconds=True)
lhs = sp.laplace_transform(f.diff(t, 2), t, s, noconds=True)
rhs = s**2*F - s*f.subs(t, 0) - f.diff(t).subs(t, 0)
print(sp.simplify(lhs - rhs))
""", """
f(0) = 1 and f'(0) = 0 for this test function; the difference between
the direct transform of f'' and s^2 F - s f(0) - f'(0) simplifies to 0.
""")

# ---------------------------------------------------------------- D
d.part("D", "Partial Fractions in Full",
       "Coughanowr & LeBlanc, Ch. 3, Sec. 3.1", "coughanowr-ch3")
d.sub("""
### Ex. 3.3 cover-up table

$x(s) = \\frac{s^4 - 6s^2 + 9s - 8}{s(s-2)(s+1)(s+2)(s-1)}$.
Cover each factor and set $s$ to its root:
$A = \\frac{-8}{(-2)(1)(2)(-1)} = -2$,
$B = \\frac{16 - 24 + 18 - 8}{(2)(3)(4)(1)} = \\frac{1}{12}$,
$C = \\frac{1 - 6 - 9 - 8}{(-1)(-3)(1)(-2)} = \\frac{11}{3}$,
$D = \\frac{16 - 24 - 18 - 8}{(-2)(-4)(-1)(-3)} = -\\frac{17}{12}$,
$E = \\frac{1 - 6 + 9 - 8}{(1)(-1)(2)(3)} = \\frac{2}{3}$.

### Ex. 3.5 coefficient matching

With $A = 1$, $B = -1$: $1 = (1 + D)s^3 + (3 + C + 2D)s^2 +
(2 + C + D)s + 1$, so $D = -1$, $C = -1$.
""")
d.code("Check -- cover-up as a limit", [
    "Cover-up = multiply by the factor, then let $s$ go to the root",
], """
X3 = (s**4 - 6*s**2 + 9*s - 8) / (s*(s-2)*(s+1)*(s+2)*(s-1))
for root in [0, 2, -1, -2, 1]:
    print(root, sp.limit(X3 * (s - root), s, root))
""", """
Multiplying by (s - root) cancels that factor; the limit evaluates the
rest at the root -- the cover-up rule written as calculus. Prints -2,
1/12, 11/3, -17/12, 2/3, the five coefficients in the book.
""")
d.sub("""
### Prob. 2.9 inverted (Lecture Your Turn D)

$3.75s + 1 = 3.75(s + 0.2667)$. First term:
$\\frac{2.5/3.75}{s(s + 0.2667)} = \\frac{2.5}{s} - \\frac{2.5}{s + 0.2667}$.
Second term: $\\frac{11.25/3.75}{s + 0.2667} = \\frac{3}{s + 0.2667}$.
Sum $\\frac{2.5}{s} + \\frac{0.5}{s + 0.2667}$, so
$C_a(t) = 2.5 + 0.5e^{-t/3.75}$, matching Part A.
""")

d.write(OUT)
