#!/usr/bin/env python3
"""Build Lecture 3 (Coughanowr & LeBlanc, Ch. 4-6).

Converted from the hand-authored notebook (2026-09-28 reference version);
every code cell now carries a walkthrough, and the Your Turn checks are
code-reading tasks (no laptops in class).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

NB = "PSE-823_Lecture-03_First-Order-Systems.ipynb"
d = Deck()

WALK = {
1: """
`sp.symbols(..., positive=True)` creates the symbols and tells SymPy
they are positive, which lets it simplify later. `sp.Function` declares
X and Y as unknown functions of time (deviation variables). `sp.Eq` builds
the equation of Derive 1/4-2/4: hA(X - Y) = mC dY/dt, where
`Y(t).diff(t)` is dY/dt. The last line displays the equation as typeset
math, so it can be checked against the board.
""",
2: """
`sp.laplace_transform(expr, t, s, noconds=True)` transforms each side of
the balance separately. The left side is linear, so it becomes
hA(L{X} - L{Y}). The right side becomes mC(s L{Y} - Y(0)): SymPy applied
the derivative rule of Eq. 2.6 itself. Displaying `rhs` shows the -Y(0)
term -- the one deviation variables are about to remove.
""",
3: """
The transformed expressions contain objects such as
LaplaceTransform(Y(t), t, s); `rename` maps them to plain symbols X_s and
Y_s, and also sets Y(0) = 0 (deviation variables start at zero).
`.subs(rename)` applies all three replacements at once. The result,
hA(X_s - Y_s) = mC s Y_s, is Derive 3/4 on the board.
""",
4: """
`sp.solve(eq_s, Ys)[0]` isolates Y_s; dividing by X_s gives the transfer
function. The first print shows A h/(A h + C m s). The second line
substitutes m = tau hA/C (the definition of tau rearranged) and
simplifies: 1/(tau s + 1), Derive 4/4. This is the whole derivation, done
by the computer in four cells -- point at each cell and the matching
board step.
""",
5: """
`A` is redefined as the step size. Y(s) = X(s) G(s) with X(s) = A/s.
`sp.apart(Y_s, s)` splits it into partial fractions in s: A/s -
A tau/(tau s + 1), the cover-up result of Derive 1/3.
""",
6: """
`inverse_laplace_transform` returns A(1 - exp(-t/tau)), Eq. 4.15. The
loop then evaluates the fraction complete, y/A, at t = n tau by
substitution: 0.632, 0.865, 0.950, 0.982, 0.993. These are the rules
worth memorising: 63.2% at one tau, 95% at three, 99.3% at five.
""",
7: """
`sp.lambdify((t, tau, A), y_step, "numpy")` converts the symbolic formula
into a fast NumPy function of three arguments. `tt` is a grid of 601
times from 0 to 0.6 min; the reading is 90 F plus the deviation for
tau = 0.1 min and a 10 F step. `np.argmax(reading >= 98)` returns the
first index where the condition is True. Prints 98 F at t = 0.161 min,
the hand answer of Example 4.2.
""",
8: """
The minimal plot: create a figure of 4:3 proportions, draw one curve,
label the axes, show it. The curve is the thermometer reading rising
from 90 F toward 100 F.
""",
9: """
Same curve plus four guide lines. `axvline(0.1)` marks t = tau and
`axhline(96.32)` marks 63.2% of the 10 F change; they cross on the
curve. The dotted pair marks 98 F and the time found in Code 3/3; they
also cross on the curve. The plot verifies both derived numbers.
""",
10: """
The `for` loop draws one curve per time constant, each with a `label`,
and `ax.legend` builds the key. Smaller tau rises faster; every curve
reaches 63.2% of the step at its own tau (cf. Fig. 4-13).
""",
11: """
`ct.tf([1], [0.1, 1])` builds 1/(0.1 s + 1) from coefficient lists,
highest power of s first. `ct.poles` prints -10: the pole sits at
-1/tau. `ct.step_response(10 * G_th, tt)` simulates a 10 F step with no
algebra at all; `.outputs` is the response array. The largest gap to
the derived formula is printed: below 1e-13 F, i.e. round-off. From here
on python-control does the inversion for us.
""",
12: """
`w = 20` rad/min. Y(s) = A w/((s^2 + w^2)(tau s + 1)) with A = 2 F and
tau = 1/10 as an exact fraction, so SymPy keeps exact numbers. `apart`
prints three terms: one for the real pole at -10 and two for the
complex pair +/- 20j. The inverse is a decaying exponential plus a sine
and a cosine at the bath frequency.
""",
13: """
`lambdify` the inverse, evaluate on a fine grid (2001 points over one
minute, enough for a 20 rad/min sine), and plot bath and thermometer
together. Left of the dotted line (about 3 tau) the transient is still
visible; to the right only the ultimate response remains: same
frequency, amplitude 2 x 0.894 = 1.79 F, lagging the bath (cf. Fig.
4-18).
""",
14: """
`np.logspace(-1, 3, 200)` gives 200 frequencies spaced evenly on a log
scale from 0.1 to 1000 rad/min. Eq. 4.28 is evaluated for all of them
in one vectorized line. `loglog` uses log axes on both sides. The curve
is flat at 1 for slow baths and falls like 1/(omega tau) for fast ones;
the corner is at omega = 1/tau = 10 rad/min. A first-order system is a
low-pass filter: this is Ch. 15 (Lecture 7) in miniature.
""",
15: """
The two arrays are the Prob. 4.6 table: time in seconds and reading in
F. `frac` normalizes every reading in one line: (y - 75)/325 = Y/A. The
loop prints the eight fractions, from 0.000 to 0.954 -- every reading
becomes "fraction of the way to the oil temperature".
""",
16: """
`np.interp(x, xp, fp)` interpolates linearly: it finds where the
increasing `frac` array reaches 0.632 and returns the matching time,
exactly as one would read a table by hand. Prints (a) tau = 9.9 s
(0.632 falls just below the t = 10 s reading of 0.637).
""",
17: """
`np.log(1 - frac)` turns every fraction into z = -t/tau (Derive 2/3b).
The slope k is the least-squares formula of Derive 3/3, written with
two `np.sum` calls. Prints (b) tau = 9.9 s. Note `np.log(1 - 1.0)` would
be -inf: a reading equal to the bath temperature cannot be used.
""",
18: """
Dots are the eight z values; the line is z = -k t through the origin.
If the system were not first order the dots would curve away from any
straight line. The last point (t = 30 s, Y/A = 0.954) dominates a
no-intercept fit on the log scale, and the log inflates noise near
Y/A = 1 -- one reason to fit the raw curve directly, next.
""",
19: """
`model(t, tau)` is the derived step response in F. `curve_fit(model, x,
y, p0=[5.0])` adjusts tau, starting from 5 s, to minimize the sum of
squared residuals; it returns the best value (`popt`) and its covariance
(`pcov`), whose square-root diagonal is the standard error. Prints
tau = 10.19 +/- 0.19 s, then the residuals: a few F, alternating in
sign, no trend.
""",
20: """
The fitted model evaluated on a fine grid (line) over the book's data
(dots), with the 400 F oil temperature as a dotted line. All eight
points are used at once -- the fit is a compromise among them.
""",
21: """
`qo` is the nonlinear outflow C sqrt(h). `sp.diff(qo, h)` is the slope;
`.subs(h, hs)` evaluates it at the operating point. The tangent line is
value + slope x (h - h_s): the first two Taylor terms of Derive 1/3.
""",
22: """
R1 is the reciprocal of the slope. `sp.simplify` gives 2 sqrt(h_s)/C_v,
the book's linearized resistance.
""",
23: """
`vals` substitutes the book's numbers (C = 8, h_s = 4 ft) with a
dictionary. R1 = 0.5 ft/cfm and tau = A R1 = 1.5 min. `ct.tf([R1], [tau,
1])` builds R1/(tau s + 1); printing a transfer function shows it as a
fraction.
""",
24: """
`tank(t, h, q)` returns dh/dt for the nonlinear model; `h` arrives as an
array, so `h[0]` is the level. `solve_ivp` integrates from h = 4 ft with
the inflow raised to 20 cfm (`args=(20.0,)`); `.y[0]` is the level
history. The linear model's response is 4 ft plus the step response of
4 x G_lin (a 4-cfm step). Prints nonlinear 6.24 ft (heading for
(20/8)^2 = 6.25) versus linear 6.00 ft (4 + 0.5 x 4).
""",
25: """
Two curves on one axis, the linearized one dashed. Both start at 4 ft
with the same initial slope -- the tangent is exact at the operating
point -- and separate as the level moves away from h_s (cf. Fig. 5-9).
""",
26: """
`q` is a grid of 281 candidate inflows. For each, the true steady level
(q/C)^2 and the tangent's level h_s + R1(q - q_s) are computed in one
line each; `err` is the percentage error. `ok` is a boolean array (True
where |err| < 5%); `q[ok].min()` and `.max()` give the window edges.
Prints 13.1 to 20.6 cfm.
""",
27: """
The nonlinear steady-state curve, its tangent at q_s = 16 cfm (dashed),
the operating point (black dot) and, shaded with `axvspan`, the inflows
where the tangent is within 5%. Outside the band the linear model
drifts away.
""",
28: """
Q, Q1, Q2, H1, H2 are the five Laplace-domain unknowns; A1, A2, R1, R2
the parameters. `eqs` is the list of the four board equations, typed as
written (Eqs. 6.20-6.23). `sp.solve(eqs, [Q1, Q2, H1, H2], dict=True)`
eliminates everything except Q; `[0]` takes the solution dictionary.
`sol[H2] / Q` is the transfer function. The display shows
R2/(A1 A2 R1 R2 s^2 + (A1 R1 + A1 R2 + A2 R2)s + 1): Eq. 6.24 with
tau1 = A1 R1 and tau2 = A2 R2.
""",
29: """
`eqs[2] = ...` replaces only the valve equation (index 2, the third
item) with the noninteracting law R1 Q1 = H1, and the same `solve` runs
again. `sp.factor` writes the result as R2/((A1 R1 s + 1)(A2 R2 s + 1)):
the product of two first-order blocks, Eq. 6.7. One changed equation,
one changed physical arrangement.
""",
30: """
`one` sets every parameter to 1. For each derived transfer function:
`sp.together` puts it over one denominator, `sp.fraction` splits it
into numerator and denominator, `sp.Poly(den, s).all_coeffs()` lists the
denominator coefficients (highest power first) -- the format `ct.tf`
wants. Prints non [1, 2, 1] with poles -1, -1 and int [1, 3, 1] with
poles -2.618, -0.382. The slow pole at -0.382 (time constant 2.618) is
why the interacting system is slower.
""",
31: """
`two_tanks` is the four equations in the time domain with A = R = 1 and
a unit inflow. The flag `interacting` chooses the valve law with a
conditional expression. The loop runs `solve_ivp` twice, from empty
tanks, and stores h2 for each mode in a dictionary keyed by the flag.
Two coupled states integrated together: a state-space model (Lecture 12).
""",
32: """
Thick lines: the ODE simulations. Dotted lines: step responses of the
two transfer functions built from SymPy's results. They coincide: board
algebra, SymPy elimination and direct simulation agree. The interacting
curve rises more slowly -- rising h2 throttles q1 (the second tank
loads the first).
""",
33: """
`G` starts as 1 and is multiplied by 1/(s + 1) once per pass: after n
passes it is n identical noninteracting lags in series (Eq. 6.12).
Each response is plotted with its n. As n grows the start of the curve
flattens -- transfer lag -- and the curve starts to look like a delay
followed by a single lag: the FOPDT idea of Lecture 4.
""",
}

d.slide("""
# PSE-823: Advanced Process Dynamics and Control
## Lecture 3 -- First-Order Systems: Derive, then Code
### (Coughanowr & LeBlanc, Ch. 4-6)

Date: __________
""")

d.slide("""
## How today works

- Each idea is **introduced**, then **derived** on the board.
- Then the **code repeats the derivation**, step for step.
- Then the code goes **further** than hand algebra can.
- Full worked derivations: the companion `Derivations` notebook.
""")

d.notes("""
The order is: board first, code second. Every code cell on a
"Code it" slide has the same step number as the board step it mirrors,
so students can lay their notes next to the screen. The derivations are
examinable; the code is how we check them and extend them.
""")

d.slide("""
## Agenda

**Part A** -- The thermometer: first-order transfer function (Ch. 4)

**Part B** -- Reading $\\tau$ from data (Ch. 4, Prob. 4.6)

**Part C** -- The nonlinear tank and linearization (Ch. 5)

**Part D** -- Tanks in series: interaction and transfer lag (Ch. 6)

Tools: `sympy` mirrors the algebra; `numpy`, `scipy`,
`python-control` and `matplotlib` build on it.
""")

d.sub("""
### Setup (run once)


- Every library from the Python Primer, imported once
- In Colab, uncomment the first line
""")
d._code("""
# !pip install control          # Colab only
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ct
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
plt.rcParams.update({"font.size": 15})
""", "-", ["setup"])

d.slide("""
## Part A
### The Thermometer: a First-Order Transfer Function

(Coughanowr & LeBlanc, Ch. 4)
<!-- source: coughanowr-ch4 -->
""")

d.sub("""
### Introduce -- the mercury thermometer (Sec. 4.1)

- Bulb at temperature $y(t)$, sitting in a bath at $x(t)$.
- The bath changes. **How does the reading follow it?**
- Assumptions: all resistance in the film ($h$), bulb uniform,
  glass holds no heat, no expansion.

*Textbook figure: Coughanowr Fig. 4-1a (cross-section of thermometer bulb).*
""")

d.notes("""
Motivate: a sensor is a process too. Whatever a controller "sees" has
already been filtered by the sensor's own dynamics. Emphasise the
assumptions: they are what make the model first order.
""")

d.sub("""
### Derive 1/4 -- unsteady-state energy balance

Rate in $-$ rate out $=$ rate of accumulation:
""")

d.frag("""
$$hA\\,(x-y) \\;-\\; 0 \\;=\\; mC\\,\\frac{dy}{dt}$$

$A$: bulb surface area, $m$: mass of mercury, $C$: heat capacity.
""")

d.sub("""
### Derive 2/4 -- deviation variables

Before $t=0$ the bulb is at steady state: $hA(x_s-y_s)=0$.
""")

d.frag("""
Subtract, and define $X = x-x_s$, $\\;Y = y-y_s$:

$$hA\\,(X-Y) = mC\\,\\frac{dY}{dt}, \\qquad Y(0)=0$$
""")

d.notes("""
Why deviation variables: they make the initial condition zero, so the
Laplace transform of dY/dt is just sY(s). That is what lets a clean
ratio Y(s)/X(s) exist at all.
""")

d.sub("""
### Derive 3/4 -- Laplace transform

Transform both sides, using $\\mathcal{L}\\{dY/dt\\} = sY(s) - Y(0)$:
""")

d.frag("""
$$hA\\,[X(s)-Y(s)] = mC\\,s\\,Y(s)$$
""")

d.sub("""
### Derive 4/4 -- the transfer function

Collect $Y(s)$ and divide by $X(s)$:
""")

d.frag("""
$$\\frac{Y(s)}{X(s)} = \\frac{1}{\\tau s+1}, \\qquad \\tau = \\frac{mC}{hA}$$

General form: $K_p/(\\tau s+1)$, gain $K_p$, time constant $\\tau$.
""")

d.notes("""
Five-step recipe (Sec. 4.1): balance -> linearize if needed ->
deviation variables -> Laplace -> ratio output/input.
Ex. 4.1: Y/X = 2/(s + 1/3) = 6/(3s + 1), so tau = 3 and Kp = 6.
Always rearrange to a 1 in the denominator before reading off tau.
""")

d.sub("""
### Code it -- the same four steps in SymPy

- SymPy does algebra with **symbols**, as on the board
- Each cell below carries the **step number** it mirrors
- Nothing new is derived; the computer checks our algebra
""")

d.code_md("""
### Code 1-2/4 -- the balance, in deviation variables


- `sp.Function` declares an unknown function of $t$
- `sp.Eq(left, right)` is an **equation**, not an assignment
""", """
t, s = sp.symbols("t s", positive=True)
h, A, m, C = sp.symbols("h A m C", positive=True)
X, Y = sp.Function("X"), sp.Function("Y")   # deviation vars

# hA (X - Y) = mC dY/dt
balance = sp.Eq(h*A*(X(t) - Y(t)), m*C*Y(t).diff(t))
balance
""",
          WALK[1])

d.code_md("""
### Code 3/4 -- Laplace transform of each side


- `sp.laplace_transform` knows the derivative rule
- Look for the $-Y(0)$ term in the output
""", """
lhs = sp.laplace_transform(balance.lhs, t, s, noconds=True)
rhs = sp.laplace_transform(balance.rhs, t, s, noconds=True)
rhs                          # C m (s L{Y} - Y(0))
""",
          WALK[2])

d.code_md("""
### Code 3/4 (cont.) -- tidy up: $Y(0)=0$


- Rename the transforms to plain symbols $X_s$, $Y_s$
- Set $Y(0)=0$, exactly as deviation variables promised
""", """
Xs, Ys = sp.symbols("X_s Y_s")
rename = {sp.LaplaceTransform(X(t), t, s): Xs,
          sp.LaplaceTransform(Y(t), t, s): Ys,
          Y(0): 0}                         # deviation variable
eq_s = sp.Eq(lhs.subs(rename), rhs.subs(rename))
eq_s                                       # hA (Xs - Ys) = mC s Ys
""",
          WALK[3])

d.code_md("""
### Code 4/4 -- solve for $Y_s/X_s$


- `sp.solve(eq, Ys)` isolates $Y_s$; divide by $X_s$
- Then substitute $mC = \\tau hA$ to reach standard form
""", """
G = sp.solve(eq_s, Ys)[0] / Xs     # Y(s) / X(s)
print(sp.simplify(G))              # A h / (A h + C m s)

tau = sp.symbols("tau", positive=True)
sp.simplify(G.subs(m, tau*h*A/C))  # 1 / (tau s + 1)
""",
          WALK[4])

d.sub("""
### Introduce -- the step response

- Now **use** the transfer function: plunge the thermometer into a
  hotter bath.
- A step of size $A$ in the bath temperature: $X(s) = A/s$.
- **Example 4.2:** $\\tau = 0.1$ min, reading 90 F, bath at 100 F.
  When does it read **98 F**?
""")

d.sub("""
### Derive 1/3 -- output in the $s$-domain

Multiply the input by the transfer function:
""")

d.frag("""
$$Y(s) = \\frac{A}{s}\\cdot\\frac{1}{\\tau s+1}
= \\frac{A}{s} - \\frac{A\\tau}{\\tau s+1}$$

(partial fractions, cover-up rule)
""")

d.sub("""
### Derive 2/3 -- invert

Each term is in the table:
""")

d.frag("""
$$Y(t) = A\\left(1 - e^{-t/\\tau}\\right) \\qquad \\text{(Eq. 4.15)}$$

At $t=\\tau$: $Y/A = 1-e^{-1} = 0.632$.
""")

d.sub("""
### Derive 3/3 -- Example 4.2 by hand

$A = 10$ F, $\\tau = 0.1$ min, want $Y = 98-90 = 8$ F:
""")

d.frag("""
$$8 = 10\\left(1-e^{-t/0.1}\\right) \\;\\Rightarrow\\;
t = 0.1\\ln 5 = 0.161 \\text{ min}$$
""")

d.code_md("""
### Code 1/3 -- $Y(s)$ and partial fractions


- Build $Y(s) = X(s)\\,G(s)$ with the step $X(s) = A/s$
- `sp.apart` does the partial fractions
""", """
A = sp.symbols("A", positive=True)   # now: step size
Y_s = (A / s) / (tau*s + 1)          # X(s) G(s)
sp.apart(Y_s, s)                     # A/s - A tau/(tau s + 1)
""",
          WALK[5])

d.code_md("""
### Code 2/3 -- invert to the time domain


- `sp.inverse_laplace_transform` replaces the table
- Then ask the formula for the fraction complete at $t = n\\tau$
""", """
y_step = sp.inverse_laplace_transform(Y_s, s, t)
print(y_step)                        # A (1 - exp(-t/tau))

for n in [1, 2, 3, 4, 5]:
    frac = (y_step / A).subs(t, n*tau)
    print(f"t = {n} tau: {float(frac):.3f} of final value")
""",
          WALK[6])

d.code_md("""
### Code 3/3 -- Example 4.2 with numbers


- `sp.lambdify` turns the formula into a NumPy function
- Evaluate on a time grid; find the first time above 98 F
""", """
y_num = sp.lambdify((t, tau, A), y_step, "numpy")

tt = np.linspace(0, 0.6, 601)          # min
reading = 90 + y_num(tt, 0.1, 10)      # 90 F + deviation
i98 = np.argmax(reading >= 98)         # first index at 98 F
print(f"98 F at t = {tt[i98]:.3f} min  (hand: 0.161)")
""",
          WALK[7])

d.sub("""
### Build on it -- plotting the response, one piece at a time

- The derivation is done. Now we **draw** it.
- Same recipe as the Primer: curve, then labels, then guides.
""")

d.code_md("""
### Plot 1/3 -- the curve


- `fig, ax = plt.subplots(...)` gives a figure we can control
- `ax.plot(x, y)` draws one curve
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(tt, reading)                  # thermometer reading
ax.set_xlabel("t (min)")
ax.set_ylabel("reading (F)")
plt.show()
""",
          WALK[8])

d.code_md("""
### Plot 2/3 -- mark the numbers we derived


- `axhline` / `axvline`: horizontal and vertical guides
- 63.2% of the change at $t = \\tau$; 98 F at $t = 0.161$ min
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(tt, reading)
ax.axvline(0.1, ls="--", c="gray")      # t = tau
ax.axhline(90 + 6.32, ls="--", c="gray") # 63.2% of 10 F
ax.axhline(98, ls=":", c="k")           # target reading
ax.axvline(tt[i98], ls=":", c="k")      # time to reach it
ax.set(xlabel="t (min)", ylabel="reading (F)")
plt.show()
""",
          WALK[9])

d.code_md("""
### Plot 3/3 -- effect of $\\tau$ (cf. Fig. 4-13)


- Loop over three values of $\\tau$; one call per curve
- `label=` plus `ax.legend()` gives the key
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
for tau_i in [0.05, 0.1, 0.2]:               # min
    ax.plot(tt, 90 + y_num(tt, tau_i, 10),
            label=f"tau = {tau_i} min")
ax.axhline(98, ls=":", c="k")
ax.set(xlabel="t (min)", ylabel="reading (F)")
ax.legend(loc="lower right")
plt.show()
""",
          WALK[10])

d.code_md("""
### Build on it -- the same model in `python-control`


- `ct.tf(num, den)`: coefficients, highest power of $s$ first
- `step_response` needs **no** algebra -- and matches ours
""", """
G_th = ct.tf([1], [0.1, 1])              # 1 / (0.1 s + 1)
print("pole:", ct.poles(G_th))           # -1/tau = -10

resp = ct.step_response(10 * G_th, tt)   # 10 F step
gap = np.abs(90 + resp.outputs - reading).max()
print(f"max |python-control - formula| = {gap:.1e} F")
""",
          WALK[11])

d.sub("""
### Introduce -- a sinusoidal bath (Example 4.3)

- Same thermometer, $\\tau = 0.1$ min.
- Bath oscillates $\\pm 2$ F about 100 F at $\\omega = 20$ rad/min.
- Does the reading show the **full** swing? Is it **in step**?
""")

d.sub("""
### Derive 1/2 -- transform and split

$X(t) = A\\sin\\omega t \\;\\Rightarrow\\; X(s) = A\\omega/(s^2+\\omega^2)$:
""")

d.frag("""
$$Y(s) = \\frac{A\\omega}{(s^2+\\omega^2)(\\tau s+1)}$$

Partial fractions: one real pole, one complex pair.
""")

d.sub("""
### Derive 2/2 -- the ultimate (long-time) response

The $e^{-t/\\tau}$ term dies out, leaving (Eq. 4.28):
""")

d.frag("""
$$Y(t) \\to \\frac{A}{\\sqrt{1+\\omega^2\\tau^2}}\\sin(\\omega t+\\phi),
\\quad \\phi = -\\tan^{-1}(\\omega\\tau)$$

Here: amplitude ratio $0.894$, $\\phi = -63.4^\\circ$.
""")

d.notes("""
Full partial-fraction algebra (Eqs. 4.24-4.27) is in the Derivations
notebook. The two facts to take away: same frequency, smaller
amplitude, lagging phase. The book rounds to 0.896 and 63.5 deg.
""")

d.code_md("""
### Code 1/2 -- partial fractions and inverse


- Same two calls as the step: `apart`, then invert
- Exact numbers: `sp.Rational(1, 10)` keeps $\\tau$ as a fraction
""", """
w = 20                                      # rad/min
Y_sin = 2*w / ((s**2 + w**2) * (sp.Rational(1, 10)*s + 1))
print(sp.apart(Y_sin, s))                   # three terms

y_sin = sp.inverse_laplace_transform(Y_sin, s, t)
y_sin                                       # decay + sine + cosine
""",
          WALK[12])

d.code_md("""
### Code 2/2 -- bath versus thermometer (cf. Fig. 4-18)


- `lambdify` again, then plot input and output together
- Left of the dotted line: transient. Right: the ultimate response
""", """
f_sin = sp.lambdify(t, y_sin, "numpy")
tt = np.linspace(0, 1.0, 2001)                # min
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(tt, 100 + 2*np.sin(20*tt), label="bath")
ax.plot(tt, 100 + f_sin(tt), label="thermometer")
ax.axvline(0.3, ls=":", c="gray")             # ~3 tau
ax.set(xlabel="t (min)", ylabel="T (F)", ylim=(97.5, 103))
ax.legend(loc="upper center", ncol=2)
plt.show()
""",
          WALK[13])

d.code_md("""
### Build on it -- sweep the frequency


- Amplitude ratio for **every** $\\omega$ at once: one NumPy line
- Log axes: a preview of the **Bode plot** (Ch. 15)
""", """
w = np.logspace(-1, 3, 200)                # rad/min
AR = 1 / np.sqrt(1 + (w * 0.1)**2)         # Eq. 4.28
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.loglog(w, AR)
ax.axvline(20, ls=":", c="k")              # Example 4.3
ax.set(xlabel="omega (rad/min)", ylabel="amplitude ratio")
plt.show()
""",
          WALK[14])

d.sub("""
### Your Turn (10 min)

**Probs. 4.9-4.10.** Thermometer, $\\tau = 1$ min, reads 50 C.
At $t=0$ it goes into a 100 C bath; at $t=1.5$ min it is moved
to a 75 C bath.

1. By hand: the reading at $t=1.2$ min.
2. By hand: the **maximum** reading, and the reading at $t=20$ min.
3. Read the code: what does `50 + y_num(1.2, 1.0, 50)` print?
""")

d.answer("""
(1) y = 100 - 50 e^{-1.2} = 84.94 C.
(2) At t = 1.5: y = 100 - 50 e^{-1.5} = 88.84 C. After the move the
    reading decays toward 75: y = 75 + 13.84 e^{-(t-1.5)}. So the maximum
    is 88.84 C, at the moment of transfer; at t = 20 min, y = 75.00 C.
(3) Prints 84.94... -- the same as (1): y_num evaluates
    A(1 - e^(-t/tau)) with t = 1.2, tau = 1, A = 50.
Common slip: thinking the reading keeps rising after the move (it was
below 100, above 75 -> falls immediately). Full piecewise simulation
with forced_response is in the Derivations notebook.
""")

d.sub("""
### Check -- cold-call

In Example 4.3, **halve** $\\tau$.

Does the lag *in minutes* between bath and thermometer peaks
go up or down? Answer from the formula -- then rerun the sweep.
""")

d.answer("""
phi = atan(w tau) = atan(1) = 45 deg; lag = phi/w = 0.785/20 = 0.039 min,
down from 0.055 min. Smaller tau = faster sensor = less attenuation and
less lag. Change 0.1 -> 0.05 in the sweep cell: the corner moves right.
""")

d.slide("""
## Part B
### Reading $\\tau$ from Data

(Coughanowr & LeBlanc, Ch. 4, Prob. 4.6)
<!-- source: coughanowr-ch4 -->
""")

d.sub("""
### Introduce -- $h$ is never known

- $\\tau = mC/hA$, but in practice $h$ is **unknown**.
- So: **measure** the response, and infer $\\tau$ from it.
- **Prob. 4.6.** Thermometer at 75 F plunged into a 400 F oil bath;
  readings taken over 30 s.
- First time in this course a model is **learned from data**.
""")

d.sub("""
### Derive 1/3 -- normalize the data

From Part A, with a step of $A = 400-75 = 325$ F:
""")

d.frag("""
$$\\frac{Y}{A} = \\frac{y-75}{325} = 1 - e^{-t/\\tau}$$

Every reading becomes a fraction between 0 and 1.
""")

d.sub("""
### Derive 2/3 -- two ways to read $\\tau$

**(a)** At $t=\\tau$, $Y/A = 0.632$: interpolate the table.
""")

d.frag("""
**(b)** Take logs -- a straight line through the origin:

$$z \\equiv \\ln\\!\\left(1-\\frac{Y}{A}\\right) = -\\frac{t}{\\tau}$$
""")

d.sub("""
### Derive 3/3 -- least squares on the line

Minimize $\\sum_i (z_i + k\\,t_i)^2$ over $k = 1/\\tau$:
""")

d.frag("""
$$\\frac{d}{dk}\\sum_i (z_i + k t_i)^2 = 0 \\;\\Rightarrow\\;
k = -\\frac{\\sum_i t_i z_i}{\\sum_i t_i^2}$$
""")

d.notes("""
One-parameter least squares with no intercept, done by hand: expand,
differentiate, set to zero. This is the same normal equation as linear
regression, with one feature and no bias term.
""")

d.code_md("""
### Code 1/3 -- the data, normalized


- Two arrays straight from the book's table
- One vectorized line per derivation step
""", """
t_d = np.array([0, 1, 2.5, 5, 8, 10, 15, 30])            # s
y_d = np.array([75, 107, 140, 205, 244, 282, 328, 385])  # F
frac = (y_d - 75) / 325                   # Y/A
for ti, f in zip(t_d, frac):
    print(f"t = {ti:5.1f} s    Y/A = {f:.3f}")
""",
          WALK[15])

d.code_md("""
### Code 2/3 -- (a) interpolate the 63.2% crossing


- `np.interp(x, xp, fp)`: linear interpolation, as by hand
- Here we ask: at what $t$ does $Y/A$ reach 0.632?
""", """
tau_a = np.interp(0.632, frac, t_d)       # frac is increasing
print(f"(a) tau = {tau_a:.1f} s")
""",
          WALK[16])

d.code_md("""
### Code 3/3 -- (b) the log line, and its slope


- `np.log` on the whole array: every $z_i$ at once
- Slope from the formula we just derived
""", """
z = np.log(1 - frac)                       # z = -t / tau
k = -np.sum(t_d * z) / np.sum(t_d**2)      # least-squares slope
print(f"(b) tau = {1/k:.1f} s")
""",
          WALK[17])

d.code_md("""
### Plot -- is the log line really straight?


- If the model is first order, the dots fall on one line
- Curvature would mean the model form is wrong
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(t_d, z, "o", ms=9, label="data")
ax.plot(t_d, -k * t_d, label=f"slope -1/{1/k:.1f}")
ax.set(xlabel="t (s)", ylabel="ln(1 - Y/A)")
ax.legend(loc="lower left")
plt.show()
""",
          WALK[18])

d.code_md("""
### Build on it -- fit the raw curve with `curve_fit`


- Fit $y = 75 + 325(1-e^{-t/\\tau})$ directly: no log trick
- `curve_fit` also returns an **uncertainty** for $\\tau$
""", """
def model(t, tau):
    return 75 + 325 * (1 - np.exp(-t / tau))

popt, pcov = curve_fit(model, t_d, y_d, p0=[5.0])
tau_fit, tau_se = popt[0], np.sqrt(pcov[0, 0])
print(f"tau = {tau_fit:.2f} +/- {tau_se:.2f} s")
print("residuals (F):", np.round(y_d - model(t_d, tau_fit), 1))
""",
          WALK[19])

d.code_md("""
### Plot -- data and fitted model


- Dots: the book's measurements. Line: the fitted model
- All eight points used at once
""", """
tt = np.linspace(0, 32, 300)
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(t_d, y_d, "o", ms=9, label="Prob. 4.6 data")
ax.plot(tt, model(tt, tau_fit), label=f"fit, tau = {tau_fit:.1f} s")
ax.axhline(400, ls=":", c="gray")
ax.set(xlabel="t (s)", ylabel="reading (F)")
ax.legend(loc="lower right")
plt.show()
""",
          WALK[20])

d.sub("""
### Read the output

`curve_fit` minimizes $\\sum_i (y_i-\\hat y_i)^2$ --
the **same objective** as regression in machine learning.

- Physics fixes the model's **form**; only $\\tau$ is learned.
- Small residuals, no trend: first order is adequate.
- The $\\pm$ uncertainty is something no hand estimate gives.
""")

d.notes("""
Expect tau = 10.19 +/- 0.19 s. Residuals within about +/- 8 F and
alternating in sign -- no systematic curvature, so no evidence for a
second lag. Framing: ML is this same move with a far more flexible model
form, which buys fit and costs interpretability and extrapolation.
Returns at scale in Ch. 18 (process identification) and L10-L11.
""")

d.sub("""
### Your Turn (8 min)

1. By hand: use only the points at $t=5$ and $t=15$ s to get the
   slope of the log line, and so $\\tau$.
2. Read the code: what is `1 / k2` (to one decimal)?

```python
k2 = -np.sum(t_d[[3, 6]] * z[[3, 6]]) / np.sum(t_d[[3, 6]]**2)
```

Does a two-point estimate agree with the full fit?
""")

d.answer("""
z(5) = ln(1-0.400) = -0.511 ; z(15) = ln(1-0.778) = -1.504.
Two-point slope through the two points = (-1.504 + 0.511)/10 = -0.0993/s
-> tau = 10.1 s. (2) The code's no-intercept formula on those two points
prints 9.9 (seconds), the same as the full log fit. Pointwise, each data point implies a
different tau (9.6 to 11.2 s): that scatter is measurement noise, which
is why the full fit with an error bar is the better answer.
""")

d.sub("""
### Check -- think-pair-share

The fit gives $\\tau \\approx 10$ s **in oil**.

Would you use $\\tau = 10$ s for the same thermometer **in air**?
What does your answer say about *any* model fitted from data?
""")

d.answer("""
No. tau = mC/hA and h in air is far lower (Prob. 4.8 takes
h_air = h_oil/5, so tau_air ~ 50 s). A fitted model is only valid for
conditions represented in the data -- the extrapolation problem that
returns, much sharper, with ML models in L10-L11.
""")

d.slide("""
## Part C
### The Nonlinear Tank and Linearization

(Coughanowr & LeBlanc, Ch. 5)
<!-- source: coughanowr-ch5 -->
""")

d.sub("""
### Introduce -- one transfer function, many processes (Sec. 5.1)

Tank with a **linear** outlet $q_o = h/R$:

$$A\\frac{dh}{dt} = q - \\frac{h}{R} \\;\\Rightarrow\\;
\\frac{H(s)}{Q(s)} = \\frac{R}{\\tau s+1}, \\quad \\tau = AR$$

Thermometer, tank, mixing tank: **same form**, same code.

*Textbook figure: Coughanowr Fig. 5-1 (liquid-level system).*
""")

d.sub("""
### Introduce -- but a real valve is not linear (Sec. 5.2)

- Turbulent outlet: $q_o = C\\sqrt{h}$.
- $\\sqrt{h}$ has no Laplace transform rule: **no transfer function**.
- Fix: replace the curve by its **tangent** at the operating point.

Book example: $A=3$ ft$^2$, $h_s=4$ ft, $q_s=16$ cfm $\\Rightarrow C=8$.

*Textbook figure: Coughanowr Fig. 5-8 (nonlinear resistance and tangent line).*
""")

d.sub("""
### Derive 1/3 -- Taylor series about $h_s$

Keep the first two terms of $q_o(h) = C\\sqrt{h}$:
""")

d.frag("""
$$q_o \\approx C\\sqrt{h_s} + \\frac{C}{2\\sqrt{h_s}}(h-h_s)
= q_s + \\frac{h-h_s}{R_1}, \\qquad R_1 = \\frac{2\\sqrt{h_s}}{C}$$
""")

d.sub("""
### Derive 2/3 -- deviation variables

Put the tangent into $A\\,dh/dt = q - q_o$; subtract steady state:
""")

d.frag("""
$$A\\frac{dH}{dt} = Q - \\frac{H}{R_1}, \\qquad H = h-h_s,\\; Q = q-q_s$$

Linear again -- the same form as the linear tank.
""")

d.sub("""
### Derive 3/3 -- transfer function and numbers

Laplace transform, as in Part A:
""")

d.frag("""
$$\\frac{H(s)}{Q(s)} = \\frac{R_1}{\\tau s+1}, \\quad \\tau = AR_1$$

Book numbers: $R_1 = 2(2)/8 = 0.5$ ft/cfm, $\\tau = 1.5$ min.
""")

d.notes("""
R1 is the slope of h versus q_o at the operating point -- a local
resistance. It depends on h_s: the process has a different tau at every
operating level (Your Turn).
""")

d.code_md("""
### Code 1/3 -- the tangent line, symbolically


- `sp.diff` gives the slope $dq_o/dh$; `.subs` evaluates it at $h_s$
- Tangent = value + slope $\\times$ distance
""", """
h, hs, Cv = sp.symbols("h h_s C_v", positive=True)
qo = Cv * sp.sqrt(h)                     # nonlinear outflow
slope = sp.diff(qo, h).subs(h, hs)       # dq_o/dh at h_s
tangent = qo.subs(h, hs) + slope * (h - hs)
tangent                                  # Taylor, first order
""",
          WALK[21])

d.code_md("""
### Code 2/3 -- the linearized resistance $R_1$


- $R_1$ is one over the slope
- SymPy simplifies to the book's form
""", """
R1 = sp.simplify(1 / slope)
R1                                       # 2 sqrt(h_s) / C_v
""",
          WALK[22])

d.code_md("""
### Code 3/3 -- numbers, and the transfer function


- Substitute the book's values with a dictionary
- Build $R_1/(\\tau s+1)$ as a `python-control` object
""", """
vals = {Cv: 8, hs: 4}                   # Sec. 5.2 example
R1_val = float(R1.subs(vals))           # ft/cfm
tau_val = 3 * R1_val                    # tau = A R1, A = 3 ft^2
G_lin = ct.tf([R1_val], [tau_val, 1])
print(f"R1 = {R1_val} ft/cfm, tau = {tau_val} min")
print(G_lin)
""",
          WALK[23])

d.code_md("""
### Build on it -- simulate the **real** tank


- The nonlinear ODE has no transfer function -- but `solve_ivp`
  does not need one
- Step the inflow 16 to 20 cfm; compare with the linear model
""", """
def tank(t, h, q):
    # A dh/dt = q - C sqrt(h), with A = 3, C = 8
    return [(q - 8 * np.sqrt(h[0])) / 3]

tt = np.linspace(0, 10, 500)                # min
h_nl = solve_ivp(tank, [0, 10], [4.0], args=(20.0,),
                 t_eval=tt).y[0]
h_lin = 4 + ct.step_response(4 * G_lin, tt).outputs
print(f"final h: nonlinear {h_nl[-1]:.2f} ft, "
      f"linear {h_lin[-1]:.2f} ft")
""",
          WALK[24])

d.code_md("""
### Plot -- nonlinear versus linearized (cf. Fig. 5-9)


- Same start, same initial slope
- They part as $h$ moves away from $h_s$
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(tt, h_nl, label="nonlinear, C sqrt(h)")
ax.plot(tt, h_lin, "--", label="linearized, tau = 1.5 min")
ax.set(xlabel="t (min)", ylabel="h (ft)")
ax.legend(loc="lower right")
plt.show()
""",
          WALK[25])

d.code_md("""
### Build on it -- where is the tangent good enough?


- Steady state: true $h = (q/C)^2$; tangent $h = h_s + R_1(q-q_s)$
- Find the inflows where they differ by less than 5%
""", """
q = np.linspace(4, 32, 281)            # candidate inflows, cfm
h_true = (q / 8) ** 2                  # nonlinear steady state
h_tan = 4 + R1_val * (q - 16)          # the tangent line
err = 100 * (h_tan - h_true) / h_true  # percent error
ok = np.abs(err) < 5
print(f"within 5%: q from {q[ok].min():.1f} "
      f"to {q[ok].max():.1f} cfm")
""",
          WALK[26])

d.code_md("""
### Plot -- the curve, its tangent, and the validity window


- Shaded: error under 5%
- Outside it, the linear model drifts
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(q, h_true, label="nonlinear h = (q/C)^2")
ax.plot(q, h_tan, "--", label="tangent at q_s = 16")
ax.axvspan(q[ok].min(), q[ok].max(), color="gray", alpha=0.2)
ax.plot(16, 4, "ko")                    # operating point
ax.set(xlabel="q (cfm)", ylabel="steady h (ft)", ylim=(0, 16))
ax.legend(loc="upper left")
plt.show()
""",
          WALK[27])

d.sub("""
### Read the output

- Exact at $h_s$, good nearby, wrong far away: a **validity window**.
- Adequate when a controller holds $h$ near $h_s$ (Sec. 5.2).
- Every model -- transfer function, regression, neural net --
  has a window. **Do you know where its edges are?**
""")

d.notes("""
Window algebra (Derivations notebook): with x = q/qs, relative error
= -(x-1)^2/x^2, so |err| < 5% for x in [0.817, 1.288], i.e. q in
[13.1, 20.6] cfm. The book's own +4 cfm step (to 20) sits right at the
edge -- which is why Fig. 5-9 shows a visible but modest gap.
Bridge: this is the same question we will ask of ML surrogates in L11.
""")

d.sub("""
### Your Turn (8 min)

**Prob. 5.2.** Tank with $A = 3$ ft$^2$ and valve $q = 8\\sqrt{h}$.

1. By hand: $\\tau$ at an operating level of (a) 3 ft, (b) 9 ft.
2. Read the code: what does this print?

```python
print(3 * float(R1.subs({Cv: 8, hs: 9})))
```
""")

d.answer("""
tau = R1 A = 2 A sqrt(h_s)/C.
(a) 2(3)(1.732)/8 = 1.30 min.  (b) 2(3)(3)/8 = 2.25 min.
(2) Prints 2.25: R1 at h_s = 9 ft is 0.75 ft/cfm, times A = 3 ft^2.
Same tank, same valve, different tau: the dynamics depend on where you
operate. A controller tuned at 3 ft is tuned for a different process
than the one at 9 ft (gain scheduling). Slip: using C = 8 with h
instead of sqrt(h).
""")

d.sub("""
### Check -- poll

Now step the inflow **down**, 16 to 12 cfm.
The linear model's final level is:

**A)** too high  **B)** too low  **C)** exactly right
""")

d.answer("""
B, too low: linear gives 4 - 0.5(4) = 2.00 ft; true (12/8)^2 = 2.25 ft.
Same side as the +4 step (6.00 vs 6.25). Reason: h = (q/C)^2 is convex,
so the tangent lies below the curve everywhere. Rerun the simulation cell
with args=(12.0,) and 4 * G_lin -> -4 * G_lin to show it.
""")

d.slide("""
## Part D
### Tanks in Series: Interaction and Transfer Lag

(Coughanowr & LeBlanc, Ch. 6)
<!-- source: coughanowr-ch6 -->
""")

d.sub("""
### Introduce -- two tanks, two ways to connect them

- **Noninteracting:** tank 1 drains freely, $q_1 = h_1/R_1$.
- **Interacting:** tank 1 drains *into* tank 2, $q_1 = (h_1-h_2)/R_1$.
- One term differs. **Does it change the dynamics?**

*Textbook figure: Coughanowr Fig. 6-1 ((a) noninteracting, (b) interacting tanks).*
""")

d.sub("""
### Derive 1/3 -- the four equations, in $s$

Two balances, two valves (deviation variables, Eqs. 6.20-6.23):
""")

d.frag("""
$$Q - Q_1 = A_1 s H_1, \\qquad Q_1 - Q_2 = A_2 s H_2$$
$$R_1 Q_1 = H_1 - H_2, \\qquad R_2 Q_2 = H_2$$

Noninteracting: the third equation is $R_1 Q_1 = H_1$ instead.
""")

d.sub("""
### Derive 2/3 -- noninteracting: the blocks multiply

Each tank sees only what flows in (Eq. 6.7):
""")

d.frag("""
$$\\frac{H_2}{Q} = \\frac{1}{\\tau_1 s+1}\\cdot\\frac{R_2}{\\tau_2 s+1},
\\qquad \\tau_i = A_i R_i$$
""")

d.sub("""
### Derive 3/3 -- interacting: eliminate $H_1, Q_1, Q_2$

Tank 1 now feels $H_2$; the result does **not** factor (Eq. 6.24):
""")

d.frag("""
$$\\frac{H_2}{Q} = \\frac{R_2}{\\tau_1\\tau_2 s^2
+ (\\tau_1+\\tau_2+A_1R_2)\\,s + 1}$$

The extra $A_1R_2$ is the interaction.
""")

d.notes("""
The elimination is three lines of substitution; the full version is in
the Derivations notebook. Do it on the board only as far as students
need to see where A1 R2 comes from: it enters through H1 = H2 + R1 Q1.
""")

d.code_md("""
### Code 1/2 -- four equations, solved at once


- The four board equations, typed as written
- `sp.solve` eliminates $H_1, Q_1, Q_2$ in one call
""", """
Q, Q1, Q2, H1, H2 = sp.symbols("Q Q1 Q2 H1 H2")
A1, A2, R1, R2 = sp.symbols("A1 A2 R1 R2", positive=True)
eqs = [sp.Eq(Q - Q1, A1*s*H1),       # tank 1 balance
       sp.Eq(Q1 - Q2, A2*s*H2),      # tank 2 balance
       sp.Eq(R1*Q1, H1 - H2),        # interacting valve
       sp.Eq(R2*Q2, H2)]             # outlet valve
sol = sp.solve(eqs, [Q1, Q2, H1, H2], dict=True)[0]
G_int = sp.simplify(sol[H2] / Q)
G_int
""",
          WALK[28])

d.code_md("""
### Code 2/2 -- change one line: noninteracting


- Replace the valve equation by $R_1Q_1 = H_1$
- `sp.factor` shows the product of two first-order blocks
""", """
eqs[2] = sp.Eq(R1*Q1, H1)            # noninteracting valve
sol = sp.solve(eqs, [Q1, Q2, H1, H2], dict=True)[0]
G_non = sp.factor(sol[H2] / Q)
G_non                                # R2 / ((A1R1 s+1)(A2R2 s+1))
""",
          WALK[29])

d.sub("""
### Build on it -- which one responds faster?

- Identical tanks: $A_1=A_2=R_1=R_2=1$, so $\\tau_1=\\tau_2=1$.
- Plug in, get **numbers**, compare poles and step responses.
""")

d.code_md("""
### Poles from the derived transfer functions


- `.subs` puts in the numbers; `sp.fraction` splits num / den
- `sp.Poly(...).all_coeffs()` gives the list `ct.tf` wants
""", """
one = {A1: 1, A2: 1, R1: 1, R2: 1}
tfs = {}
for name, G in [("non", G_non), ("int", G_int)]:
    num, den = sp.fraction(sp.together(G.subs(one)))
    c = [float(v) for v in sp.Poly(den, s).all_coeffs()]
    tfs[name] = ct.tf([float(num)], c)
    print(name, c, "poles:", np.round(ct.poles(tfs[name]).real, 3))
""",
          WALK[30])

d.code_md("""
### Simulate the tanks directly, as ODEs


- One function, both arrangements: a flag picks the valve law
- Two coupled states in one `solve_ivp`: a **state-space** model
""", """
def two_tanks(t, h, interacting):
    h1, h2 = h
    q1 = (h1 - h2) if interacting else h1   # R1 = 1
    return [1.0 - q1, q1 - h2]              # A = R2 = 1, q = 1

tt = np.linspace(0, 10, 400)
h2 = {}
for mode in (False, True):
    h2[mode] = solve_ivp(two_tanks, [0, 10], [0, 0],
                         args=(mode,), t_eval=tt).y[1]
""",
          WALK[31])

d.code_md("""
### Plot -- ODE versus derived transfer functions (cf. Fig. 6-7)


- Thick: ODE simulation. Dotted: the transfer functions we derived
- The ODE never saw a transfer function, yet matches both
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(tt, h2[False], lw=3, label="noninteracting (ODE)")
ax.plot(tt, h2[True], lw=3, label="interacting (ODE)")
for G in tfs.values():
    ax.plot(tt, ct.step_response(G, tt).outputs, "k:")
ax.set(xlabel="t / tau", ylabel="H2")
ax.legend(loc="lower right")
plt.show()
""",
          WALK[32])

d.code_md("""
### Build on it -- more tanks in series (cf. Figs. 6-5, 6-6)


- Noninteracting: just keep multiplying blocks
- Watch the start of the curve flatten: **transfer lag**
""", """
fig, ax = plt.subplots(figsize=(7, 5.25))
G = ct.tf([1], [1])
for n in range(1, 5):
    G = G * ct.tf([1], [1, 1])        # add one tank, tau = 1
    ax.plot(tt, ct.step_response(G, tt).outputs, label=f"n = {n}")
ax.set(xlabel="t", ylabel="Y(t)")
ax.legend(loc="lower right")
plt.show()
""",
          WALK[33])

d.sub("""
### Your Turn (8 min)

Interacting tanks with $\\tau_1=\\tau_2=\\tau$ and $A_1=A_2$
(so $A_1R_2=\\tau$).

1. By hand: show the denominator of Eq. 6.24 becomes
   $\\tau^2 s^2 + 3\\tau s + 1$.
2. By hand: its roots, and the two effective time constants.
3. Read the code: what do these print?

```python
print(np.roots([1, 3, 1]))
print(-1 / np.roots([1, 3, 1]))
```
""")

d.answer("""
(1) tau1 tau2 = tau^2 ; tau1 + tau2 + A1 R2 = tau + tau + tau = 3 tau.
(2) s = (-3 +/- sqrt(5)) / (2 tau) = -0.382/tau, -2.618/tau.
    Effective time constants = -1/root = 2.618 tau and 0.382 tau
    (product tau^2, sum 3 tau). Eq. 6.28.
(3) [-2.618 -0.382] and [0.382 2.618]: the roots, and the
    effective time constants as -1/root.
Aside: 2.618 = phi^2, 0.382 = 1/phi^2 (golden ratio).
""")

d.sub("""
### Check -- cold-call

Four tanks in series. You only have the **measured** $h_4(t)$.

What is the simplest model you would fit -- and what would
its parameters mean physically?
""")

d.answer("""
First-order-plus-dead-time (FOPDT), K e^{-theta s}/(tau s + 1):
theta absorbs the transfer lag of the upstream tanks, tau the dominant
lag, K the gain. It is Part B's curve_fit with one more parameter.
Sets up Ch. 7 (transportation lag, next lecture) and Ch. 18.
""")

d.slide("""
### Wrap-up

**Derived, then coded:** thermometer transfer function and its step and
sinusoidal responses (Ch. 4); $\\tau$ from data by least squares
(Prob. 4.6); linearization and its validity window (Ch. 5);
interacting versus noninteracting tanks (Ch. 6).

**Tools:** `sp.laplace_transform`, `sp.apart`, `sp.solve`, `lambdify`,
`ct.tf`, `step_response`, `solve_ivp`, `curve_fit`

**Next:** Ch. 7 -- transportation lag and second-order systems.
""")

d.notes("""
Optional practice (ungraded): Prob. 5.7 gives steady-state level versus
inflow for a real tank. Fit q = K h^n with curve_fit, then linearize the
fitted valve at 300 and 400 gal/min and compare tau. Part B + Part C on
real data -- a good warm-up for Assignment 1.
""")


d.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), NB))
