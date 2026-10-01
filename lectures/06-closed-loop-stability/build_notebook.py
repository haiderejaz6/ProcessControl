#!/usr/bin/env python3
"""Build Lecture 6 (Coughanowr & LeBlanc, Ch. 12-14)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from lecture_kit import Deck, STANDARD_SETUP  # noqa: E402

NB = "PSE-823_Lecture-06_Closed-Loop-Stability.ipynb"
d = Deck()

d.title("Lecture 6", "Closed-Loop Response, Stability and Root Locus",
        "Coughanowr & LeBlanc, Ch. 12-14")

d.slide("""
## Agenda

**Part A** -- Proportional control: servo, regulator and offset
(Sec. 12.1-12.2)

**Part B** -- PI control and measurement lag (Sec. 12.3-12.5)

**Part C** -- Stability and the Routh test (Ch. 13)

**Part D** -- Root locus (Ch. 14)
""")
d.notes("""
Closed-loop transfer functions (Ch. 11) are stated, not derived, in
Part A: C/R = G1 G2/(1 + G1 G2 H) and C/U = G2/(1 + G1 G2 H) for the
single loop of Fig. 13-3. Lecture 5's full treatment of Ch. 9-11 is
scheduled once its chapter files are in place.
""")

d.setup(["The standard imports, as in Lectures 3-4"], STANDARD_SETUP)

# ===================================================================== A
d.part("A", "Proportional Control: Servo, Regulator and Offset",
       "Coughanowr & LeBlanc, Ch. 12, Sec. 12.1-12.2", "coughanowr-ch12")

d.sub("""
### Introduce -- the stirred-tank heater, closed (Fig. 12-1e)

- Lecture 4's tank: $\\tau = 5$ min, $A = 1/wC = 1/14$ C/kW.
- Unity feedback (fast thermocouple), valve gain 1, P controller $K_c$.
- Single loop (Ch. 11): $\\dfrac{C}{R} = \\dfrac{G_1G_2}{1 + G_1G_2H}$,
  $\\;\\dfrac{C}{U} = \\dfrac{G_2}{1 + G_1G_2H}$.
- Lecture 4 found 2.94 C for a 5 C set-point step with $K_c = 20$.
  **Why not 5?**
""")

d.derive("Derive 1/3 -- servo: still first order (Eq. 12.2)",
         "$G_1 = K_c$, $G_2 = A/(\\tau s + 1)$, $H = 1$:",
         """
$$\\frac{T'}{T_R'} = \\frac{K_cA}{\\tau s + 1 + K_cA}
= \\frac{A_1}{\\tau_1 s + 1},\\quad
\\tau_1 = \\frac{\\tau}{1 + K_cA},\\quad A_1 = \\frac{K_cA}{1 + K_cA}$$

Feedback makes the response **faster** ($\\tau_1 < \\tau$).
""")

d.derive("Derive 2/3 -- offset",
         "Final value for a unit step, minus the request:",
         """
$$\\text{Offset} = 1 - A_1 = \\frac{1}{1 + K_cA} \\qquad (12.4)$$

Ex. 12.1 (5 C step): $K_c = 5, 10, 20, 100$ give offsets
$3.69, 2.92, 2.06, 0.614$ C.
""")

d.derive("Derive 3/3 -- regulator: the same lag, the same offset",
         "Load $T_i$ with $T_R' = 0$ (Eq. 12.5-12.7):",
         """
$$\\frac{T'}{T_i'} = \\frac{1}{\\tau s + 1 + K_cA}
= \\frac{1/(1+K_cA)}{\\tau_1 s + 1},\\qquad
\\text{Offset} = -\\frac{1}{1 + K_cA}$$
""")

d.code("Code 1/3 -- block algebra, symbolically", [
    "Mirrors Derive 1/3: the single-loop formula, simplified",
    "`sp.solve` reads $\\tau_1$ and $A_1$ off the standard form",
], """
s, Kc, A, tau = sp.symbols("s K_c A tau", positive=True)
G1, G2, H = Kc, A / (tau*s + 1), 1
servo = sp.simplify(G1*G2 / (1 + G1*G2*H))
load = sp.simplify(G2 / (1 + G1*G2*H) * (tau*s + 1) / A)
print(servo, "|", sp.simplify(load / (tau*s + 1)))
tau1, A1 = sp.symbols("tau_1 A_1")
print(sp.solve([sp.Eq(tau1, tau/(1 + Kc*A)),
                sp.Eq(A1, servo.subs(s, 0))], [tau1, A1]))
""", """
G1, G2 and H are the three blocks of Fig. 12-1e. `servo` is the single-
loop formula; SymPy simplifies it to A K_c/(A K_c + s tau + 1), Eq. 12.1.
For the load the process block from T_i is 1/(tau s + 1), i.e. G2 with A
removed -- hence the factor (tau s + 1)/A; the second print shows
1/(A K_c + s tau + 1), Eq. 12.5. The last print states tau_1 and A_1
explicitly: A_1 = A K_c/(A K_c + 1) is just the servo function at s = 0.
""")

d.code("Code 2/3 -- Example 12.1's offset table", [
    "Mirrors Derive 2/3: offset $= 5/(1 + K_cA)$ for a 5 C step",
], """
A_v = 1 / 14                                # C per kW
for kc in [5, 10, 20, 100]:
    off = 5 / (1 + kc * A_v)
    tau1_v = 5 / (1 + kc * A_v)
    print(f"Kc = {kc:3}: offset {off:.3f} C, tau1 {tau1_v:.2f} min")
""", """
For each gain the offset and the closed-loop time constant are printed.
Offsets 3.684, 2.917, 2.059, 0.614 C: the book's table. The time
constants fall from 3.68 to 0.61 min (open loop: 5 min). They are the
same numbers because a 5 C step and a 5 min tau happen to share the
factor 5/(1 + K_c A). Bigger gain: smaller offset, faster response.
""")

d.code("Code 3/3 -- simulate both problems (Figs. 12-5, 12-8)", [
    "`ct.feedback` for the servo; the load path is $G_2/(1+G_1G_2)$",
], """
tt = np.linspace(0, 15, 300)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7, 5.25), sharey=True)
for kc in [5, 10, 20, 100]:
    Gp = ct.tf([1/14], [5, 1])
    sv = ct.feedback(kc * Gp, 1)
    ld = ct.feedback(ct.tf([1], [5, 1]), kc * ct.tf([1/14], [1]))
    a1.plot(tt, ct.step_response(5 * sv, tt).outputs)
    a2.plot(tt, ct.step_response(5 * ld, tt).outputs, label=kc)
a1.set(title="set point +5 C", xlabel="t (min)", ylabel="T' (C)")
a2.set(title="T_i +5 C", xlabel="t (min)"); a2.legend(title="Kc")
plt.show()
""", """
Left: `ct.feedback(kc * Gp, 1)` is the servo loop with unity feedback.
Right: the load loop is written as feedback of the load block 1/(5s + 1)
with the rest of the loop (controller times heater gain) in the feedback
path -- the same denominator 1 + G1 G2. Read the plots: set-point curves
end short of 5 C by the offsets of Code 2/3; load curves end above 0 C
by the same amounts. Larger Kc is faster and closer, but never exact.
""")

d.your_turn(8, """
**Ex. 12.2.** $T_i$ rises 5 C with the set point fixed, $K_c = 20$.

1. By hand: the final $T'$ and the offset.
2. Read the code: what does this print, to three decimals?

```python
print(ct.dcgain(ct.feedback(20 * ct.tf([1/14], [5, 1]), 1)))
```
""", """
(1) T'(inf) = 5/(1 + 20/14) = 2.059 C; offset = 0 - 2.059 = -2.059 C.
(2) 0.588: the servo loop's steady-state gain A_1 = (20/14)/(1 + 20/14)
= 20/34. Times 5 C it is the 2.94 C of Lecture 4.
""")

d.check("cold-call", """
Feedback made the closed-loop time constant **smaller** than the
tank's own $\\tau = 5$ min. The tank did not change. Where does the
speed come from?
""", """
From the controller: when the error is large it drives the heater much
harder than the steady requirement, so the temperature moves faster than
the tank would on its own. The price is a larger heater swing -- and,
with lags, the risk of instability (Part C).
""")

# ===================================================================== B
d.part("B", "PI Control and Measurement Lag",
       "Coughanowr & LeBlanc, Ch. 12, Sec. 12.3-12.5", "coughanowr-ch12")

d.sub("""
### Introduce -- removing offset, and the price

- PI: $G_c = K_c(1 + 1/\\tau_I s)$. Integral action keeps pushing
  until the error is zero.
- The closed loop becomes **second order**, so it can oscillate.
- A lag in the measuring element does the same even with P only
  (Sec. 12.5).
""")

d.derive("Derive 1/3 -- PI, load change (Eq. 12.9)",
         "Insert $G_c$ in $G_2/(1 + G_cG_2)$ and rearrange:",
         """
$$\\frac{T'}{T_i'} = \\frac{A_1s}{\\tau_1^2s^2 + 2\\zeta\\tau_1s + 1},\\;
\\tau_1 = \\sqrt{\\frac{\\tau\\tau_I}{K_cA}},\\;
\\zeta = \\frac12\\sqrt{\\frac{\\tau_I}{\\tau}}\\frac{1 + K_cA}{\\sqrt{K_cA}}$$

The $s$ in the numerator: a step in $T_i$ gives **zero** offset.
""")

d.derive("Derive 2/3 -- Example 12.3 numbers",
         "$K_c = 20$, $\\tau_I = 2$ min, $\\tau = 5$ min, $A = 1/14$:",
         """
$K_cA = 1.429$, $\\;\\tau_1 = \\sqrt{10/1.429} = 2.65$ min,
$\\;\\zeta = \\frac12\\sqrt{0.4}\\,\\frac{2.429}{1.195} = 0.64$.

Table: $K_c\\uparrow \\Rightarrow \\zeta\\uparrow$; $\\;\\tau_I\\downarrow
\\Rightarrow \\zeta\\downarrow$ (more oscillation, smaller peak).
""")

d.derive("Derive 3/3 -- P control with measurement lag (Eq. 12.17)",
         "$H = 1/(\\tau_ms + 1)$ makes the denominator quadratic:",
         """
$$\\frac{T'}{T_R'} = \\frac{A_1(\\tau_ms+1)}{\\tau_2^2s^2 + 2\\zeta_2\\tau_2s+1},
\\quad
\\zeta_2 = \\frac{\\tau + \\tau_m}{2\\sqrt{\\tau\\tau_m}}\\frac{1}{\\sqrt{1 + K_cA}}$$

$\\zeta_2$ falls as $K_c$ or $\\tau_m$ grows: more oscillation.
""")

d.code("Code 1/3 -- Eq. 12.9 by SymPy", [
    "Mirrors Derive 1/3: PI in the load loop, then match the standard form",
], """
tI = sp.symbols("tau_I", positive=True)
Gc = Kc * (1 + 1 / (tI * s))
pi_load = sp.cancel(1 / (tau*s + 1) / (1 + Gc * A / (tau*s + 1)))
num, den = sp.fraction(pi_load)
den = sp.Poly(den, s).all_coeffs()            # [a2, a1, a0]
t1 = sp.sqrt(den[0] / den[2])
z = sp.simplify(den[1] / den[2] / (2 * t1))
print(num, "|", den); print("tau1 =", t1, " zeta =", z)
""", """
`sp.cancel` clears the nested fractions into one ratio of polynomials.
`sp.fraction` splits it; the numerator is s tau_I (the zero at the
origin that kills the offset). The denominator coefficients
[tau tau_I, tau_I(A K_c + 1), A K_c] are divided by the constant term to
reach standard form: tau_1 = sqrt(tau tau_I/(A K_c)) and zeta =
tau_I(A K_c + 1)/(2 sqrt(...)), which simplifies to the book's
(1/2) sqrt(tau_I/tau)(1 + K_c A)/sqrt(K_c A).
""")

d.code("Code 2/3 -- Example 12.3, both sweeps (Figs. 12-12, 12-13)", [
    "Left: $\\tau_I = 2$, vary $K_c$. Right: $K_c = 20$, vary $\\tau_I$",
], """
tt = np.linspace(0, 30, 400); load = ct.tf([1], [5, 1])
def pi_ctrl(kc, ti): return ct.tf([kc * ti, kc], [ti, 0])
def resp(kc, ti):                           # T_i +5 C, PI loop
    L = ct.feedback(load, pi_ctrl(kc, ti) * ct.tf([1/14], [1]))
    return ct.step_response(5 * L, tt).outputs
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7, 5.25), sharey=True)
for kc in [5, 10, 20, 100]: a1.plot(tt, resp(kc, 2), label=kc)
for ti in [1, 2, 5, 10]: a2.plot(tt, resp(20, ti), label=ti)
a1.legend(title="Kc"); a2.legend(title="tau_I")
a1.set(xlabel="t (min)", ylabel="T' (C)"); a2.set(xlabel="t (min)")
plt.show()
""", """
`pi_ctrl` builds K_c(tau_I s + 1)/(tau_I s), the PI transfer function,
from coefficient lists. `resp` returns the load response to a 5 C step
in T_i, with the PI controller and heater gain in the feedback path;
the two one-line loops call it for each K_c and each tau_I. Every curve returns to
0: no offset. Left: higher K_c, smaller peak and less ringing (zeta
rises). Right: smaller tau_I, smaller peak but more oscillation (zeta
falls) -- the book's summary table, read off the plot.
""")

d.code("Code 3/3 -- measurement lag hurts (Example 12.5)", [
    "PI with $K_c = 20$, $\\tau_I = 2$; thermocouple lag $\\tau_m$ grows",
], """
tt = np.linspace(0, 40, 500)
fig, ax = plt.subplots(figsize=(7, 5.25))
for tm in [0.33, 1.0, 2.0, 5.0]:
    fwd = pi_ctrl(20, 2) * ct.tf([1/14], [5, 1])
    L = ct.feedback(fwd, ct.tf([1], [tm, 1]))
    ax.plot(tt, ct.step_response(5 * L, tt).outputs, label=tm)
ax.axhline(5, ls="--", c="gray")
ax.set(xlabel="t (min)", ylabel="T' (C)")
ax.legend(title="tau_m (min)"); plt.show()
""", """
The forward path is PI controller times heater; the thermocouple
1/(tau_m s + 1) sits in the feedback path. A 5 C set-point step. With
tau_m = 0.33 min (Lecture 4's thermocouple) the response is crisp; at
5 min it overshoots heavily and rings for half an hour. The controller
acts on old news (Lecture 1, Part C). Rule from Sec. 12.5: the measuring
element must respond quickly.
""")

d.your_turn(8, """
1. By hand: $\\zeta$ of Eq. 12.9 for $K_c = 100$, $\\tau_I = 2$ min.
2. Read the code: in Code 3/3, which value of `tm` gives the largest
   overshoot, and does any curve settle away from 5 C?
""", """
(1) K_c A = 7.14; zeta = 0.5 sqrt(0.4)(8.14)/sqrt(7.14) = 0.5(0.632)
(8.14)/(2.67) = 0.96: nearly critically damped.
(2) tm = 5.0 overshoots most. None settles away from 5 C: PI leaves no
offset whatever the sensor lag, as long as the loop is stable.
""")

d.check("poll", """
You need **less oscillation** in a PI load response without changing
$\\tau_I$. You should:

**A)** raise $K_c$  **B)** lower $K_c$  **C)** slow the thermocouple
""", """
A. zeta grows with K_c for fixed tau_I (Eq. 12.9). C makes it worse
(Code 3/3). The answer reverses once more lags are present -- then high
K_c destabilizes (Part C).
""")

# ===================================================================== C
d.part("C", "Stability and the Routh Test",
       "Coughanowr & LeBlanc, Ch. 13", "coughanowr-ch13")

d.sub("""
### Introduce -- three lags and a P controller (Fig. 13-1)

- Lags $\\tau_1 = 1$, $\\tau_2 = 1/2$, $\\tau_3 = 1/3$ (the last in the
  measurement); P controller $K_c$.
- Fig. 13-2: beyond some $K_c$ the oscillations **grow**.
- Stable: every root of $1 + G(s) = 0$ in the left half-plane
  (BIBO; imaginary axis counts as unstable).
""")

d.derive("Derive 1/3 -- the characteristic equation (Eq. 13.11)",
         "$1 + K_c/[(s+1)(s/2+1)(s/3+1)] = 0$, multiply out by 6:",
         """
$$s^3 + 6s^2 + 11s + 6(1 + K_c) = 0$$
""")

d.derive("Derive 2/3 -- the Routh array (Ex. 13.3)",
         "Rows from the coefficients; third row "
         "$b_1 = (a_1a_2 - a_0a_3)/a_1$:",
         """
| row | | |
|---|---|---|
| 1 | 1 | 11 |
| 2 | 6 | $6(1+K_c)$ |
| 3 | $10 - K_c$ | |
| 4 | $6(1+K_c)$ | |

All positive (Theorem 13.1) $\\Rightarrow$ stable for $K_c < 10$.
""")

d.derive("Derive 3/3 -- on the boundary (Theorem 13.3)",
         "At $K_c = 10$ row 3 vanishes; row 2 gives the imaginary pair:",
         """
$$6s^2 + 66 = 0 \\Rightarrow s = \\pm j\\sqrt{11} = \\pm 3.317j,
\\qquad s_3 = -6$$
""")

d.code("Code 1/3 -- a Routh array in nine lines", [
    "Mirrors Derive 2/3: each new row from the two rows above it",
    "Works for numbers **and** symbols ($K_c$)",
], """
def routh(c):
    c = [sp.nsimplify(x) for x in c]
    n, cols = len(c), (len(c) + 1) // 2
    R = [c[0::2] + [0]*(cols - len(c[0::2])),
         c[1::2] + [0]*(cols - len(c[1::2]))]
    for i in range(2, n):
        a, b = R[i - 2], R[i - 1]
        R.append([sp.simplify((b[0]*a[j+1] - a[0]*b[j+1]) / b[0])
                  for j in range(cols - 1)] + [0])
    return [r[0] for r in R]              # the first column
""", """
`c[0::2]` takes every other coefficient starting at the first (row 1:
a0, a2, ...); `c[1::2]` starts at the second (row 2: a1, a3, ...); rows
are padded with zeros to equal length. Each new row applies the book's
formula b_j = (b0 a_{j+1} - a0 b_{j+1})/b0, i.e.
(a1 a2 - a0 a3)/a1 for the first entry, using the two rows above. The
function returns the first column, which is all Theorems 13.1-13.2
need. `sp.nsimplify` turns decimals into exact fractions so the
symbolic case stays tidy. Nothing is printed yet.
""")

d.code("Code 2/3 -- Example 13.3 with $K_c$ left as a symbol", [
    "Mirrors Derive 2/3-3/3: first column, then the boundary",
], """
col = routh([1, 6, 11, 6 * (1 + Kc)])
print("first column:", col)
Kcu = sp.solve(sp.Eq(col[2], 0), Kc)[0]
print("boundary Kc =", Kcu)
print(np.roots([1, 6, 11, float(6 * (1 + Kcu))]))
""", """
With K_c symbolic, the first column prints [1, 6, 10 - K_c, 6 K_c + 6]:
Derive 2/3. Setting the third entry to zero gives the boundary K_c = 10.
At that gain `np.roots` returns -6 and +/- 3.317j (printed with a tiny
or zero real part): the pair on the imaginary axis of Derive 3/3 and
the third root -6.
""")

d.code("Code 3/3 -- Examples 13.2 and 13.4: count sign changes", [
    "Theorem 13.2: sign changes in the first column = roots in the RHP",
], """
for name, c in [("13.2", [1, 3, 5, 4, 2]),
                ("13.4 (PI)", [1, 6, 11, 36, 120])]:
    col = routh(c)
    flips = sum(np.sign(float(col[i])) != np.sign(float(col[i+1]))
                for i in range(len(col) - 1))
    rhp = sum(np.roots(c).real > 0)
    print(f"Ex {name}: column {col}, changes {flips}, RHP roots {rhp}")
""", predict=True, walkthrough="""
For each characteristic polynomial the first column is computed and the
sign changes counted by comparing neighbours. The last count checks the
theorem with `np.roots`. Ex. 13.2: column [1, 3, 11/3, 26/11, 2], no
change, no RHP roots: stable. Ex. 13.4 (P control with K_c = 5 plus
integral action, tau_I = 0.25): column [1, 6, 5, -108, 120], two
changes, two RHP roots (0.795 +/- 2.70j): unstable, although K_c = 5
was stable with P alone. Predict before running.
""")

d.code("Build on it -- find the boundary by brute force", [
    "No Routh: roots for 1501 gains; the first with a RHP root wins",
], """
gains = np.linspace(0, 15, 1501)
worst = np.array([np.roots([1, 6, 11, 6 * (1 + k)]).real.max()
                  for k in gains])
print(f"first unstable gain: {gains[np.argmax(worst > 0)]:.2f}")
fig, ax = plt.subplots(figsize=(7, 5.25))
ax.plot(gains, worst); ax.axhline(0, c="k", lw=0.8)
ax.axvline(10, ls="--", c="gray")
ax.set(xlabel="Kc", ylabel="largest real part of the roots")
plt.show()
""", """
A list comprehension computes the roots for every gain on a fine grid
and keeps the largest real part. `np.argmax(worst > 0)` finds the first
gain where it turns positive: 10.01 (the grid step is 0.01). The plot
shows the largest real part rising through zero exactly where Routh put
the boundary. A computer finds the answer without any theory; Routh
explains *why* it is 10, and gives it as a formula.
""")

d.code("Build on it -- the responses of Fig. 13-2", [
    "Unit set-point step for gains either side of 10",
], """
tt = np.linspace(0, 12, 600)
G = ct.tf([1], [1, 1]) * ct.tf([1], [0.5, 1])     # process lags
H = ct.tf([1], [1/3, 1])                          # measurement
fig, ax = plt.subplots(figsize=(7, 5.25))
for kc in [1, 6, 9, 12]:
    y = ct.step_response(ct.feedback(kc * G, H), tt).outputs
    ax.plot(tt, y, label=f"Kc = {kc}")
ax.set(xlabel="t", ylabel="C(t)", ylim=(-1, 3))
ax.legend(loc="upper left"); plt.show()
""", """
The loop of Fig. 13-1: two lags forward, the third (measurement) in the
feedback path. K_c = 1 settles quickly with a large offset; 6 rings;
9 rings for a long time (stable but a poor response, as the book warns:
Routh says nothing about *how* stable); 12 grows without bound and
leaves the axis limits. The ylim keeps the stable curves readable.
""")

d.your_turn(10, """
**Prob. 13.11.** $s^4 + 4s^3 + 6s^2 + 4s + (1 + K) = 0$.

1. By hand: the Routh array; the $K$ above which it is unstable.
2. Read the code: what is printed?

```python
print(routh([1, 4, 6, 4, 1 + sp.Symbol("K")]))
```
""", """
(1) Rows: [1, 6, 1 + K], [4, 4], [5, 1 + K], [(20 - 4(1 + K))/5], [1 + K].
Fourth entry (16 - 4K)/5 > 0 requires K < 4. At K = 4 the imaginary
pair comes from 5 s^2 + 5 = 0: s = +/- j.
(2) [1, 4, 5, 16/5 - 4*K/5, K + 1].
""")

d.check("think-pair-share", """
Routh says $K_c = 9$ is stable. The $K_c = 9$ curve rings for a very
long time. What information does Routh *not* give, and which tool in
this lecture does?
""", """
How far the roots are from the imaginary axis (the decay rate) -- Routh
only counts roots in the RHP. The root locus (Part D) shows where the
roots actually are as K_c varies; frequency response (Lectures 7-8)
gives margins.
""")

# ===================================================================== D
d.part("D", "Root Locus",
       "Coughanowr & LeBlanc, Ch. 14", "coughanowr-ch14")

d.sub("""
### Introduce -- watch the roots move with the gain

- Open loop $G(s) = \\dfrac{K}{(s+1)(s+2)(s+3)}$, $K = 6K_c$
  (Eq. 14.4): **poles** at $-1, -2, -3$.
- The root locus plots the roots of $1 + G = 0$ as $K$ goes from 0 up.
- Branches start at the open-loop poles; complex roots come in pairs.
""")

d.derive("Derive 1/2 -- where the locus crosses the axis",
         "Routh with $K$: $b_1 = [66 - (K + 6)]/6 = 0$:",
         """
$K = 60$ ($K_c = 10$); substitute $s = ja$:
$(66 - 6a^2) + j(11a - a^3) = 0 \\Rightarrow a = \\pm\\sqrt{11} = 3.32$.
""")

d.derive("Derive 2/2 -- integral action moves the crossing",
         "PI with $\\tau_I = 1/4$ adds a pole at 0 and a zero at $-4$:",
         """
$$s(s+1)(s+2)(s+3) + K(s+4) = 0$$

Crossing at $K = 3.84$ instead of 60: integral action destabilizes
(Fig. 14-5).
""")

d.code("Code 1/2 -- Table 14.1 from `np.roots`", [
    "Mirrors Derive 1/2: roots of $(s+1)(s+2)(s+3) + K$ for the book's K",
], """
base = np.poly([-1, -2, -3])                 # (s+1)(s+2)(s+3)
for K in [0, 0.39, 1.58, 6.6, 26.5, 60, 100]:
    r = np.roots(base + np.array([0, 0, 0, K]))
    print(f"K = {K:5}: {np.round(np.sort_complex(r), 2)}")
""", """
`np.poly` builds the polynomial whose roots are given: [1, 6, 11, 6].
Adding K to the constant coefficient forms the characteristic equation.
`np.sort_complex` orders the roots. Read down the rows: at K = 0 the
roots are the open-loop poles; at 0.39 two roots have just met near
-1.42 (the breakaway; a tiny imaginary part shows we are just past it); then they become complex and move right; at 60 they sit on
the imaginary axis at +/- 3.32j; at 100 they have positive real parts.
This is the book's Table 14.1.
""")

d.code("Code 2/2 -- the locus drawn by python-control", [
    "`ct.root_locus_plot` traces all branches for $K$ from 0 up",
], """
G_ol = ct.tf([1], [1, 6, 11, 6])
G_pi = ct.tf([1, 4], [1, 6, 11, 6, 0])        # PI, tau_I = 1/4
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7, 5.25))
ct.root_locus_plot(G_ol, ax=a1)
ct.root_locus_plot(G_pi, ax=a2)
a1.set_title("P control (Fig. 14-2)", fontsize=11)
a2.set_title("PI control (Fig. 14-5)", fontsize=11)
plt.tight_layout(); plt.show()
""", """
`G_ol` is the open-loop transfer function with K = 1; `G_pi` adds the
PI pole at s = 0 and zero at s = -4 (numerator s + 4). `root_locus_plot`
computes the roots for a range of K and draws each branch; crosses mark
open-loop poles and circles mark zeros. Left: three branches from
-1, -2, -3; two curve into the right half-plane. Right: four branches;
one heads for the zero at -4, and the complex pair crosses the axis much
sooner -- the destabilizing effect of integral action.
""")

d.code("Build on it -- Example 14.1, two crossings", [
    "PID on a two-tank process with a measuring lag",
    "Scan $K_c$ on a log grid; report where the largest real part changes sign",
], """
num = np.array([2/3, 1, 1/3])                 # PID numerator / s
den = np.polymul(np.polymul([20, 1], [10, 1]),
                 np.polymul([0.5, 1], [1, 0]))
gains = np.logspace(-2, 3, 20000)
worst = np.array([np.roots(np.polyadd(den, k * num)).real.max()
                  for k in gains])
flip = gains[1:][np.diff(np.sign(worst)) != 0]
print("stability changes at Kc =", np.round(flip, 3))
""", """
G = K_c(1 + 2s/3 + 1/(3s))/((20s + 1)(10s + 1)(0.5s + 1)); multiplying
by s gives numerator 2s^2/3 + s + 1/3 and denominator
s(20s + 1)(10s + 1)(0.5s + 1), built with `np.polymul`. The
characteristic polynomial is den + K_c num (`np.polyadd` aligns the
lengths). On 20,000 log-spaced gains the sign of the largest real part
flips twice: at K_c = 0.728 and about 205 (the grid's 204.86; the
exact value is 204.83). The book quotes 0.6 and 360,
read from its sketched locus; an exact Routh calculation
(Derivations notebook) confirms 0.728 and 204.8. Stable below the
first, unstable between, stable again above the second.
""")

d.your_turn(8, """
1. By hand: from Table 14.1, between which two values of $K$ does the
   response change from non-oscillatory to oscillatory?
2. Read the code: what three roots does this print?

```python
print(np.round(np.roots([1, 6, 11, 66]), 3))
```
""", """
(1) Between K = 0.23 (three real roots) and K = 1.58 (a complex pair);
the breakaway is K = 0.39, where two real roots meet at -1.42.
(2) [-6, 3.317j, -3.317j] (displayed as -6.+0.j, 0.+3.317j,
-0.-3.317j): K = 60, the crossing point.
""")

d.check("cold-call", """
The book says root locus is "difficult to apply to systems containing
transportation lags". Why -- and what did we use in Lecture 4 that
would let us try anyway?
""", """
e^(-theta s) is not a polynomial, so the characteristic equation has
infinitely many roots. A Pade approximation (Lecture 4) turns it into a
rational function, so np.roots / root_locus can be used -- approximately.
Frequency response (Lecture 7) handles dead time exactly.
""")

d.slide("""
### Wrap-up

**Derived, then coded:** P control as a first-order closed loop and its
offset; PI as a second-order loop with no offset; the cost of
measurement lag; the characteristic equation, the Routh array and its
boundary; root locus for P and PI, and Example 14.1's two crossings.

**Tools:** `ct.feedback`, `ct.dcgain`, `sp.cancel`, a `routh()` function,
`np.roots` sweeps, `ct.root_locus_plot`

**Next:** Ch. 15 -- frequency response and Bode diagrams.
""")

d.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), NB))
