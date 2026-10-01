#!/usr/bin/env python3
"""Build the Lecture 3 companion notebook (full derivations and answers)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from lecture_kit import Deck  # noqa: E402

OUT = os.path.join(HERE, "..", "derivations",
                   "PSE-823_Lecture-03_Derivations.ipynb")
d = Deck()
d.slide("""
# PSE-823: Advanced Process Dynamics and Control
## Lecture 3 -- Derivations and Worked Solutions
### (Coughanowr & LeBlanc, Ch. 4-6)

Companion to the main Lecture 3 notebook. Same Part order.
""")
d.setup(["Imports used below"], """
import numpy as np
import matplotlib.pyplot as plt
import control as ct
import sympy as sp
plt.rcParams.update({"font.size": 15})
""")
d.slide("""
## Part A
### First-Order Responses -- Derivations

(Coughanowr & LeBlanc, Ch. 4)
<!-- source: coughanowr-ch4 -->
""")
d.sub("""
### Step response (Eq. 4.15)

$$Y(s)=\\frac{A}{s(\\tau s+1)}=\\frac{A/\\tau}{s(s+1/\\tau)}
=\\frac{C_1}{s}+\\frac{C_2}{s+1/\\tau}$$

Cover-up: $C_1 = A$ (at $s=0$), $C_2=-A$ (at $s=-1/\\tau$), so

$$Y(t)=A\\left(1-e^{-t/\\tau}\\right)$$

Ex. 4.2: $8 = 10(1-e^{-t/0.1})\\Rightarrow t = -0.1\\ln(0.2) = 0.161$ min.
""")
d.sub("""
### Sinusoidal response (Eqs. 4.24-4.28)

$$Y(s)=\\frac{A\\omega}{(s^2+\\omega^2)(\\tau s+1)}$$

Partial fractions (one real pole, one complex pair) give

$$Y(t)=\\frac{A\\omega\\tau}{\\tau^2\\omega^2+1}e^{-t/\\tau}
+\\frac{A}{\\sqrt{\\tau^2\\omega^2+1}}\\sin(\\omega t+\\phi),
\\quad \\phi=-\\tan^{-1}(\\omega\\tau)$$

Ex. 4.3: $\\omega\\tau=2$: amplitude $2/\\sqrt5=0.894$ F,
$\\phi=-63.4^\\circ$, lag $=1.107/20=0.055$ min.
""")
d.code('Check -- sinusoidal response, symbolically', ['`apart` then invert; exact numbers via `sp.Rational`'], """
s, t = sp.symbols("s t", positive=True)
tau, w, A = sp.Rational(1, 10), 20, 2
Ys = A * w / ((s**2 + w**2) * (tau * s + 1))
print(sp.apart(Ys, s))
yt = sp.inverse_laplace_transform(Ys, s, t)
print(sp.simplify(yt))
""", """
The real pole at -10 gives the 4/(5(s + 10)) term; the complex pair
+/- 20j gives the other. The inverse is 4/5 e^(-10t) + 2/5 sin 20t -
4/5 cos 20t: the decaying term dies out and the sine and cosine combine
into one sine of amplitude 2/sqrt(5) = 0.894 x 2 lagging by 63.4 deg,
Eq. 4.28.
""")
d.sub("""
### Your Turn A -- worked (Probs. 4.9-4.10)

1. $y(1.2)=100-50e^{-1.2}=84.94$ C.
2. At $t=1.5$: $y=100-50e^{-1.5}=88.84$ C. After transfer the
   reading relaxes toward 75 C: $y=75+13.84\\,e^{-(t-1.5)}$.
   Maximum = **88.84 C** at $t = 1.5$ min; $y(20) = 75.00$ C.

By superposition the bath is a step of +50 at $t=0$ and a step of
$-25$ at $t=1.5$ -- `forced_response` handles it directly:
""")
d.code('Check -- the two-bath problem with `forced_response`', ['Piecewise bath temperature as an input array; python-control does the rest'], """
G = ct.tf([1], [1, 1])                  # tau = 1 min
t = np.linspace(0, 20, 4001)
x = np.where(t <= 1.5, 100.0, 75.0)     # bath temperature, C
Y = ct.forced_response(G, t, x - 50).outputs
y = 50 + Y
print(f"y(1.2) = {np.interp(1.2, t, y):.2f} C")
print(f"max    = {y.max():.2f} C at t = {t[y.argmax()]:.2f} min")
print(f"y(20)  = {y[-1]:.2f} C")
""", """
`np.where(t <= 1.5, 100.0, 75.0)` builds the bath temperature: 100 C
until 1.5 min, 75 C after. `forced_response` simulates the transfer
function for an arbitrary input (here the deviation from 50 C) and
returns the output on the same grid. Prints y(1.2) = 84.94 C, the
maximum 88.84 C at t = 1.50 min (the moment of transfer), and y(20) =
75.00 C, the hand answers to Probs. 4.9-4.10.
""")
d.slide("""
## Part B
### Estimating $\\tau$ from Data -- Worked

(Coughanowr & LeBlanc, Ch. 4, Prob. 4.6)
<!-- source: coughanowr-ch4 -->
""")
d.sub("""
### Two hand estimates

Step of $A=325$ F, so $Y/A=1-e^{-t/\\tau}$.

1. **63.2% crossing.** $Y/A=0.520$ at 8 s, $0.637$ at 10 s:
   $t = 8+2(0.632-0.520)/0.117 \\approx 9.9$ s.
2. **Log-linearization.** $\\ln(1-Y/A) = -t/\\tau$ is a straight line
   through the origin. From $t=5$ s ($-0.511$) and $t=15$ s ($-1.504$):
   slope $=-0.0993$ s$^{-1}$, so $\\tau\\approx 10.1$ s.
""")
d.sub("""
### Least squares on the log-linearized data (closed form)

Minimize $\\sum_i (z_i + t_i/\\tau)^2$ with $z_i=\\ln(1-f_i)$.
Setting the derivative in $k=1/\\tau$ to zero:

$$k=-\\frac{\\sum t_i z_i}{\\sum t_i^2}$$

This is ordinary linear regression through the origin -- the
simplest ML model. `curve_fit` instead fits the **untransformed**
data, which weights errors in F rather than in log units.
""")
d.code('Check -- least squares and pointwise tau', ['Same log-line formula, plus tau from each point separately'], """
t_d = np.array([1, 2.5, 5, 8, 10, 15, 30])
y_d = np.array([107, 140, 205, 244, 282, 328, 385])
z = np.log(1 - (y_d - 75) / 325)
k = -np.sum(t_d * z) / np.sum(t_d ** 2)
print(f"log-linear LS: tau = {1/k:.2f} s")
print("pointwise tau:", np.round(-t_d / z, 2))
""", """
The t = 0 point is dropped (log of 1 is 0 and adds nothing). The fit
gives tau = 9.85 s. `-t_d / z` computes the tau each single reading
implies: 9.65 to 11.2 s. That scatter is measurement noise; the fit
averages it out.
""")
d.sub("""
### Check question -- worked

$\\tau = mC/hA$. The heat-transfer coefficient in air is much lower
(Prob. 4.8 uses $h_{air}=h_{oil}/5$), so $\\tau_{air}\\approx 50$ s.

A model fitted to data inherits the conditions of that data.
Using it elsewhere is extrapolation -- the central risk with any
data-driven model, and the reason L10-L11 test models on
**unseen** operating conditions, not just held-out points.
""")
d.slide("""
## Part C
### Linearization -- Derivations

(Coughanowr & LeBlanc, Ch. 5)
<!-- source: coughanowr-ch5 -->
""")
d.sub("""
### Taylor linearization of $q_o = C\\sqrt h$ (Eqs. 5.30-5.38)

$$q_o \\approx q_{os} + \\frac{dq_o}{dh}\\Big|_{h_s}(h-h_s)
= q_{os} + \\frac{C}{2\\sqrt{h_s}}(h-h_s) = q_{os}+\\frac{h-h_s}{R_1}$$

Substitute into $A\\,dh/dt = q - q_o$, subtract the steady state
$q_s = q_{os}$, transform:

$$\\frac{H(s)}{Q(s)}=\\frac{R_1}{\\tau s+1},\\quad
R_1=\\frac{2\\sqrt{h_s}}{C},\\quad \\tau=R_1A$$

Book numbers: $C=16/\\sqrt4=8$, $R_1=2(2)/8=0.5$, $\\tau=1.5$ min.
""")
d.sub("""
### Validity window (closed form)

Steady states: $h_{true}=(q/C)^2$, $h_{tan}=h_s+R_1(q-q_s)$.
With $x=q/q_s$ and $h_s=(q_s/C)^2$:

$$h_{tan}=h_s(2x-1),\\quad h_{true}=h_s x^2
\\;\\Rightarrow\\; \\frac{h_{tan}-h_{true}}{h_{true}}=-\\frac{(x-1)^2}{x^2}$$

Always $\\le 0$ (tangent below a convex curve).
$|\\text{err}|<5\\%$ when $|x-1|/x<\\sqrt{0.05}$:
$x\\in[0.817,\\,1.288]$, i.e. $q\\in[13.1,\\,20.6]$ cfm.
""")
d.sub("""
### Your Turn C -- worked (Prob. 5.2)

$\\tau = R_1 A = 2A\\sqrt{h_s}/C$ with $A=3$, $C=8$:

- (a) $h_s=3$ ft: $\\tau = 2(3)(1.732)/8 = 1.30$ min
- (b) $h_s=9$ ft: $\\tau = 2(3)(3)/8 = 2.25$ min

The time constant grows as $\\sqrt{h_s}$: the same tank is a slower
process when run fuller.
""")
d.code('Check -- tau at two operating levels', ['Prob. 5.2: same tank, two levels, two time constants'], """
A, C = 3.0, 8.0
for hs in (3.0, 9.0):
    R1 = 2 * np.sqrt(hs) / C
    print(f"h_s = {hs} ft: R1 = {R1:.3f} ft/cfm, "
          f"tau = {A * R1:.2f} min")
""", """
For each operating level R1 = 2 sqrt(h_s)/C and tau = A R1. Prints
1.30 min at 3 ft and 2.25 min at 9 ft: the linearized dynamics depend on
where the tank is operated.
""")
d.slide("""
## Part D
### Tanks in Series -- Derivations

(Coughanowr & LeBlanc, Ch. 6)
<!-- source: coughanowr-ch6 -->
""")
d.sub("""
### Noninteracting, Example 6.1

$\\tau_1=0.5$, $\\tau_2=1$, $R_2=1$, unit step:

$$H_2(s)=\\frac{1}{s(0.5s+1)(s+1)}
\\;\\Rightarrow\\; H_2(t)=1-\\left(2e^{-t}-e^{-2t}\\right)\\quad(\\text{Eq. 6.11})$$

Slope at $t=0$ is zero: the S-shape (transfer lag).
""")
d.sub("""
### Interacting, Eq. 6.24 from Eqs. 6.20-6.23

Tank 1: $Q-Q_1=A_1sH_1$. Tank 2: $Q_1-Q_2=A_2sH_2$.
Valves: $R_1Q_1=H_1-H_2$, $\\;R_2Q_2=H_2$.

From tank 2 and valve 2: $Q_1=(A_2s+1/R_2)H_2$.
From valve 1: $H_1=H_2+R_1Q_1$. Substitute into tank 1:

$$Q = Q_1 + A_1s\\,[H_2+R_1Q_1] = (1+A_1R_1s)Q_1 + A_1sH_2$$

$$\\frac{H_2}{Q}=\\frac{R_2}{\\tau_1\\tau_2s^2+(\\tau_1+\\tau_2+A_1R_2)s+1}$$
""")
d.code('Check -- eliminating the intermediate variables by hand-style substitution', ['Express $Q_1$ and $Q$ in terms of $H_2$, then read off $H_2/Q$'], """
s, A1, A2, R1, R2 = sp.symbols("s A1 A2 R1 R2", positive=True)
H2 = sp.Symbol("H2")
Q1 = (A2 * s + 1 / R2) * H2
Q = Q1 + A1 * s * (H2 + R1 * Q1)
den = sp.expand(R2 * Q / H2)          # H2/Q = R2 / den
print(sp.collect(den, s))
# tau1 = A1 R1, tau2 = A2 R2 -> Eq. 6.24
""", """
Valve 2 and tank 2 give Q1 = (A2 s + 1/R2) H2. Tank 1 with valve 1
(H1 = H2 + R1 Q1) gives Q = Q1 + A1 s (H2 + R1 Q1). Then H2/Q = R2/den
with den = R2 Q/H2, expanded and collected in s:
A1 A2 R1 R2 s^2 + (A1 R1 + A1 R2 + A2 R2) s + 1, Eq. 6.24.
""")
d.sub("""
### Your Turn D -- worked

$\\tau_1=\\tau_2=\\tau$, $A_1=A_2$ $\\Rightarrow A_1R_2=\\tau$:

$$\\tau^2s^2+3\\tau s+1=0\\;\\Rightarrow\\;s=\\frac{-3\\pm\\sqrt5}{2\\tau}
=-\\frac{0.382}{\\tau},\\;-\\frac{2.618}{\\tau}$$

Effective time constants $2.618\\tau$ and $0.382\\tau$ (Eq. 6.28);
product $\\tau^2$, sum $3\\tau$. The slow one dominates, so the
interacting pair is more sluggish than two independent lags of $\\tau$.
""")
d.code('Check -- the roots for equal time constants', ['`np.roots` and the effective time constants'], """
print(np.roots([1, 3, 1]))          # tau = 1
print(-1 / np.roots([1, 3, 1]))     # effective time constants
""", """
The roots of s^2 + 3s + 1 are -2.618 and -0.382 (tau = 1); the
effective time constants -1/root are 0.382 and 2.618, Eq. 6.28.
""")

d.write(OUT)
