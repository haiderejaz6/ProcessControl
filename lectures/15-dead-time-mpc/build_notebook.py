#!/usr/bin/env python3
"""Build Lecture 15 (Cecil, Sec. 8.2-8.3)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from lecture_kit import Deck, STANDARD_SETUP  # noqa: E402

NB = "PSE-823_Lecture-15_Dead-Time-MPC.ipynb"
d = Deck()

d.title("Lecture 15", "Dead-Time Compensation and Model Predictive Control",
        "Cecil, Ch. 8, Sec. 8.2-8.3")

d.slide("""
## Agenda

**Part A** -- Dead-time compensation: the paper machine (Sec. 8.2)

**Part B** -- Step-response models and the dynamic matrix (Sec. 8.3)

**Part C** -- MPC on the jacketed reactor: horizons, move suppression,
constraints

**Part D** -- The model inside MPC, identified from data
""")

d.setup(["The standard imports, plus tools for delays, matrices, "
         "optimization and regression"],
        STANDARD_SETUP + """from collections import deque
from scipy.optimize import brentq
from scipy.linalg import toeplitz
from gekko import GEKKO
from sklearn.linear_model import LinearRegression, RidgeCV
""")

# ===================================================================== A
d.part("A", "Dead-Time Compensation",
       "Cecil, Ch. 8, Sec. 8.2", "cecil-ch08")

d.sub("""
### Introduce -- a process dominated by dead time (Fig. 8.8)

- Paper machine: basis weight measured at the reel, about a minute
  after the stock valve acts.
- Model: dead time $\\theta = 1.2$ min, time constant $\\tau = 0.17$
  min, gain $K = 0.67$ %/%.
- Disturbance: actual consistency 2% -> 2.2% (+10% basis weight).
- PID must wait **two dead times** before seeing any correction.
- Minutes matter: at 1600 ft/min, 8 min is over 2 miles of paper.
""")

d.derive("Derive 1/2 -- PID limits (Fig. 8.9)",
         "Crossover: $\\tan^{-1}(0.17\\omega) + 1.2\\omega = \\pi$ "
         "(Lecture 8):",
         """
Cecil: $K_u = 1.6$ %/%, $P_u = 2.7$ min. Quarter decay:
$K_C = K_u/2 = 0.8$, $T_I = P_u = 2.7$ min. Lambda tuning with
$\\tau_{CL} = \\theta$: $K_C = \\frac{\\tau}{\\tau_{CL} + \\theta}\\frac1K
= 0.11$, $T_I = \\tau = 0.17$ min.
""")

d.derive("Derive 2/2 -- the Smith predictor (Figs. 8.14-8.15)",
         "Run a model beside the process; feed the controller a "
         "prediction:",
         """
$$\\tilde W(t + \\theta) = W(t) + [\\hat W(t + \\theta) - \\hat W(t)]$$

$\\hat W(t + \\theta)$: model output before its dead time;
$\\hat W(t)$: after it. The bracket is the effect of moves made in the
last dead time, not yet measured. With a perfect model the controller
sees only the lag: tune it hard.
""")

d.code("Code 1/3 -- ultimate gain and period", [
    "Mirrors Derive 1/2 with `brentq` (Lecture 8)",
], """
K, tau, theta = 0.67, 0.17, 1.2
w = brentq(lambda w: np.arctan(tau*w) + theta*w - np.pi, 0.1, 10)
Ku = np.sqrt(1 + (tau * w)**2) / K
print(f"w_co = {w:.3f} rad/min, Ku = {Ku:.2f} %/%, "
      f"Pu = {2*np.pi/w:.2f} min")
print(f"Lambda: Kc = {tau / (2*theta) / K:.3f}, TI = {tau} min")
""", """
The crossover equation is solved as in Lecture 8; Ku = 1/AR there,
with AR = K/sqrt(1 + (tau w)^2). Prints w_co = 2.307 rad/min,
Ku = 1.60 %/% and Pu = 2.72 min (Cecil: 1.6 and 2.7). Lambda tuning
gives Kc = 0.17/(2.4)/0.67 = 0.106 (Cecil rounds to 0.11) and
TI = 0.17 min.
""")

d.code("Code 2/3 -- the loop, with and without the predictor", [
    "Dead times as queues (Lecture 8); PI with set point 0",
    "`smith=True` adds the bracket of Derive 2/2 to the PV",
], """
def paper(Kc, TI, smith=False, th_m=1.2, dt=0.005, t_end=12):
    sheet = deque([0.0] * round(theta / dt))    # true dead time
    model = deque([0.0] * round(th_m / dt))     # model dead time
    x = xm = I = 0.0; W = []
    for _ in range(int(t_end / dt)):
        pv = sheet[0] + (xm - model[0] if smith else 0)   # Fig. 8.15
        I += -pv * dt; u = Kc * (-pv + I / TI)            # PI
        x += dt * (K * (u + 15) - x) / tau      # 15% load from t = 0
        xm += dt * (K * u - xm) / tau           # model, no load
        sheet.append(x); model.append(xm); model.popleft()
        W.append(sheet.popleft())
    return np.array(W)
""", """
`sheet` carries the true weight through the machine; `model` carries
the model's. Each step: the PV is the measurement `sheet[0]`, plus
(Smith) the model output before its delay minus after it. The PI
controller acts on -PV. The process lag gets the controller output
plus the load: 15% of valve equivalent, i.e. +10% weight (0.67 x 15)
if uncontrolled. The model gets the controller output only -- it
cannot know the consistency changed. `W` records the measured weight.
""")

d.code("Code 3/3 -- three controllers (Fig. 8.9 and beyond)", [
    "IAE over 12 min in the legend",
], """
t = np.arange(int(12 / 0.005)) * 0.005
fig, ax = plt.subplots(figsize=(7, 5.25))
for name, args in [("quarter decay", (0.8, 2.7)),
                   ("Lambda", (0.11, 0.17)),
                   ("Smith + PI", (1.0, 0.17, True))]:
    W = paper(*args)
    ax.plot(t, W, label=f"{name}: IAE {np.trapezoid(abs(W), t):.1f}")
ax.set(xlabel="t (min)", ylabel="basis weight change (%)"); ax.legend()
plt.show()
""", """
All three see nothing for one dead time, then the weight jumps toward
+10%. Quarter decay: IAE 40.7 and still off by 1.4% at 12 min (TI of
2.7 min is far too long, as Cecil says). Lambda: smooth, IAE 25.6,
lined out by about 7 min (Cecil: about 8). Smith predictor with an
aggressive PI (Kc = 1.0): IAE 14.6, within 0.5% after 3.4 min --
close to the two-dead-time limit of 2.4 min.
""")

d.code("Build on it -- the model's dead time is 20% too long", [
    "Machine speed changed; the predictor was not updated",
], """
W = paper(1.0, 0.17, smith=True, th_m=1.44)
print(f"IAE = {np.trapezoid(abs(W), t):.2f}, "
      f"last time |W| > 0.5: {t[abs(W) > 0.5].max():.2f} min")
""", predict=True, walkthrough="""
Same controller, model dead time 1.44 min against the true 1.2. IAE
rises from 14.6 to 18.75 and the response is outside +/-0.5% until
8.35 min, worse than Lambda tuning's line-out. The predictor's
benefit depends on an accurate dead time (Cecil: on a paper machine
it varies with machine speed, so it must be computed from the speed).
""")

d.your_turn(6, """
1. By hand: Lambda tuning with $\\tau_{CL} = 2\\theta$ instead of
   $\\theta$. New $K_C$?
2. Read the code: what does this print?

```python
q = deque([0.0, 0.0, 0.0]); out = []
for x in [1.0, 2.0, 3.0, 4.0]:
    q.append(x); out.append(q.popleft())
print(out)
```
""", """
(1) Kc = 0.17/(2.4 + 1.2)/0.67 = 0.070 %/%: slower still.
(2) [0.0, 0.0, 0.0, 1.0]: each value comes out three steps later -- a
dead time of three samples.
""")

d.check("cold-call", """
The operators beat the PID by: read the scan, turn the stock valve by
the "calibrated" amount, then **wait a dead time**. Which part of the
Smith predictor does the waiting correspond to?
""", """
The bracket W-hat(t + theta) - W-hat(t): the memory of moves already
made but not yet seen. It stops the controller from piling on more
correction while the first one is still travelling down the machine.
""")

# ===================================================================== B
d.part("B", "Step-Response Models and the Dynamic Matrix",
       "Cecil, Ch. 8, Sec. 8.3", "cecil-ch08")

d.sub("""
### Introduce -- a model as a list of numbers (Table 8.3)

- Reactor with a once-through jacket (Fig. 8.21): cooling water
  $108.8 \\to 88.8$ lb/min; temperature $150 \\to 154.5$ F.
- Step response per unit input: $s(k) = c(k)/(-20)$, every
  $\\Delta t = 15$ min; flat after $N = 13$ points.
- Impulse response $g(k) = s(k) - s(k-1)$.
- **Free-form**: no structure assumed. Linear, so superposition holds.
""")

d.derive("Derive 1/2 -- prediction by superposition",
         "Write any input as steps $\\Delta m(j)$; add their responses:",
         """
$$c(k) = \\sum_j s(k - j)\\,\\Delta m(j)$$

Pulse of +40 lb/min for 30 min: $\\Delta m(0) = +40$,
$\\Delta m(2) = -40$ (Table 8.4).
""")

d.derive("Derive 2/2 -- the dynamic matrix and QDMC",
         "Effect of $L$ future moves on $R$ future outputs:",
         """
$$\\mathbf x = A\\,\\Delta\\mathbf m,\\quad
A = \\begin{bmatrix} s(1) & 0\\\\ s(2) & s(1)\\\\ \\vdots & \\vdots\\\\
s(R) & s(R-1)\\end{bmatrix}$$

Choose $\\Delta\\mathbf m$ to cancel the predicted errors $\\hat{\\mathbf e}$
in least squares: $\\Delta\\mathbf m = (A^TA)^{-1}A^T\\hat{\\mathbf e}$.
Implement only the first move; repeat next sample.
""")

d.code("Code 1/3 -- Table 8.3", [
    "From the step test to $s(k)$ and $g(k)$",
], """
c_test = np.array([0, 1.0, 1.9, 2.5, 3.0, 3.4, 3.7, 3.9, 4.1, 4.2,
                   4.3, 4.4, 4.4, 4.5])           # F, every 15 min
s = c_test / -20                                  # F per (lb/min)
g = np.diff(s)
print("s:", s.round(3)); print("g:", g.round(3))
""", """
The test changed the flow by -20 lb/min, so dividing by -20 gives the
response to +1 lb/min. Prints s = 0, -0.05, -0.095, ..., -0.225 and
g = -0.05, -0.045, -0.03, ..., with s(11) = s(12) (g(12) = 0): the
0.1 F resolution of the thermometer shows up as "quantization noise"
in the model. `np.diff` gives the 13 differences g(k).
""")

d.code("Code 2/3 -- predict the pulse test (Table 8.4)", [
    "Mirrors Derive 1/2: two shifted, scaled copies of $s$",
], """
def s_at(k):                      # 0 before k = 0, flat after 13
    return np.where(k < 0, 0.0, s[np.clip(k, 0, 13)])
k = np.arange(19)
C = 150 + 40 * s_at(k) - 40 * s_at(k - 2)
print(C.round(1))
""", """
`s_at` extends the 14 stored values: zero for negative k (before the
step), the final value beyond k = 13 (the model is finite). The pulse
is +40 at k = 0 and -40 at k = 2 (30 min later). Prints 150.0, 148.0,
146.2, 147.0, 147.8, ... 150.0: Table 8.4's C(k) column. The real test
read 148.6 and 147.4 at the first two samples: the reactor is not
perfectly linear.
""")

d.code("Code 3/3 -- the dynamic matrix, $R = 4$, $L = 2$", [
    "Mirrors Derive 2/2; `toeplitz` builds the shifted columns",
], """
def dyn_matrix(s, R, L):
    return toeplitz(s[1:R + 1], np.zeros(L))
A = dyn_matrix(s, 4, 2)
G = np.linalg.solve(A.T @ A, A.T)                  # (A^T A)^-1 A^T
print(A); print(G.round(3))
print("moves:", (G @ np.full(4, 5.0)).round(1))
""", """
`toeplitz(col, row)` makes a matrix with constant diagonals: first
column s(1)..s(R), first row zeros -- exactly A. `np.linalg.solve`
computes (A^T A)^(-1) A^T without forming the inverse. G matches
Cecil: [[-14.05, -8.39, -0.343, 3.616], [18.31, 9.09, -3.052,
-9.316]]. For a +5 F set-point step every predicted error is 5: moves
-95.8 and +75.1 lb/min. Only -95.8 is implemented.
""")

d.your_turn(8, """
1. By hand: square DMC uses only the first row:
   $\\Delta m = \\hat e(1)/s(1)$. For the 5 F step with $\\Delta t = 15$
   min, what move? With $\\Delta t = 1$ min, $s(1) = 0$: what happens?
2. Read the code: what does it print?

```python
print(toeplitz([1, 2, 3], [1, 0]))
```
""", """
(1) 5/(-0.05) = -100 lb/min (flow 108.8 -> 8.8). With s(1) = 0 the
move is infinite: the dead time (1.35 min) hides the first sample.
QDMC needs R > int(theta/dt) + L.
(2) [[1 0] [2 1] [3 2]].
""")

d.check("think-pair-share", """
MPC computes $L$ future moves every sample but implements only the
first. Why throw the rest away?
""", """
Receding horizon: next sample brings a new measurement (and model
error); re-solving uses it. The later moves were based on older
information. It is feedback, implemented through repeated
optimization.
""")

# ===================================================================== C
d.part("C", "MPC on the Jacketed Reactor",
       "Cecil, Ch. 8, Sec. 8.3", "cecil-ch08")

d.sub("""
### Introduce -- making MPC behave

- A perfect-model controller is as aggressive as its math allows:
  the cooling flow would go negative.
- Knobs: horizon $R$, number of moves $L$, and **move suppression**:
  $\\Phi = \\|\\hat{\\mathbf e} - A\\Delta\\mathbf m\\|^2 +
  k^2\\|\\Delta\\mathbf m\\|^2$.
- **Constraints**: $0 \\le$ flow, i.e. $\\Delta M \\ge -108.8$ lb/min.
- Cecil's smoothed model: $K = -0.2312$, $\\tau = 55.49$ min,
  $\\theta = 1.353$ min; $\\Delta t = 1$ min, $R = 60$, $L = 2$.
""")

d.derive("Derive 1/1 -- move suppression",
         "Set $\\partial\\Phi/\\partial\\Delta\\mathbf m = 0$:",
         """
$$\\Delta\\mathbf m = (A^TA + k^2I)^{-1}A^T\\hat{\\mathbf e}$$

Ridge regression on the moves: $k$ trades tracking for smaller
moves. $k = 0$ is QDMC; large $k$ gives timid moves.
""")

d.code("Code 1/4 -- smooth the model by fitting (Table 8.7)", [
    "FOPDT least squares on the 14 points of $s(k)$ (Lecture 10)",
], """
def fopdt(t, K, T, th):
    return K * (1 - np.exp(-np.clip(t - th, 0, None) / T))
p, _ = curve_fit(fopdt, 15.0 * np.arange(14), s, p0=[-0.23, 50, 1])
print("K, tau, theta =", p.round(4))
s1 = fopdt(np.arange(400.0), *p)               # every 1 min
print("s(1), s(2) =", s1[1:3].round(4))
""", """
The same `curve_fit` as Lecture 10, on Table 8.3 at 15-min spacing.
Prints K = -0.2311, tau = 55.49 min, theta = 1.31 min (Cecil: -0.2312,
55.49, 1.353). The fitted curve, sampled every minute, is a smooth
step-response model with no quantization noise. s(1) = 0 because the
dead time exceeds one sample; s(2) = -0.003.
""")

d.code("Code 2/4 -- a QDMC controller in 12 lines", [
    "Model and plant both as step responses (superposition)",
    "Model error added to every prediction; flow constraint by "
    "clipping",
], """
def qdmc(sm, sp, R, L, k, n=120, r=5.0, lo=-108.8):
    A = dyn_matrix(sm, R, L)
    gain = np.linalg.solve(A.T @ A + k**2 * np.eye(L), A.T)[0]
    cm, cp = np.zeros(n + R + 1), np.zeros(n + R + 1)   # model, plant
    u, y, M = 0.0, [], []
    for i in range(n):
        e = r - (cm[i+1:i+R+1] + cp[i] - cm[i])   # predicted errors
        dm = max(gain @ e, lo - u); u += dm       # first move, clipped
        cm[i:] += dm * sm[:n+R+1-i]; cp[i:] += dm * sp[:n+R+1-i]
        y.append(cp[i]); M.append(u)
    return np.array(y), np.array(M)
""", """
`gain` is the first row of (A^T A + k^2 I)^(-1) A^T: only the first
move is ever used. `cm` and `cp` hold the future trajectories implied
by all moves so far, for the model and the plant. Each sample: model
error = measured cp[i] minus predicted cm[i] (Cecil's EM), added to
the R predictions; errors against the set point; first move, clipped
so the flow stays >= 0; both trajectories updated by superposition.
""")

d.code("Code 3/4 -- set point 150 -> 155 F", [
    "Perfect model; $k = 0$ against $k = 0.17$ (Figs. 8.31, 8.33)",
], """
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 5.6), sharex=True)
for k in [0.0, 0.17]:
    y, M = qdmc(s1, s1, 60, 2, k)
    a1.plot(150 + y, label=f"k = {k}: IAE {np.abs(5 - y).sum():.0f}")
    a2.plot(108.8 + M)
a1.set(ylabel="T (F)"); a1.legend()
a2.set(xlabel="t (min)", ylabel="flow (lb/min)"); plt.show()
""", """
k = 0: the flow drops straight to zero (the constraint) and stays
there until the temperature is nearly at 155; tracking is fast,
IAE 39. k = 0.17: the first move is only -26.5 lb/min, the flow never
goes below about 60, and the temperature approaches 155 more slowly
(IAE 122). With a perfect model, suppression only costs speed...
""")

d.code("Build on it -- ...but the model is never perfect", [
    "Plant gain 50% higher, dead time 5 min; same two controllers",
], """
sp_bad = fopdt(np.arange(400.0), 1.5 * p[0], p[1], 5.0)
for k in [0.0, 0.17]:
    y, M = qdmc(s1, sp_bad, 60, 2, k)
    print(f"k = {k}: peak {150 + y.max():.2f} F, "
          f"IAE {np.abs(5 - y).sum():.0f}")
""", predict=True, walkthrough="""
Same controllers; the plant is now more sensitive and slower to
respond than the model. k = 0: peak 157.58 F and a sustained
oscillation (IAE 322). k = 0.17: peak 155.0 F, IAE 82 -- better than
with the perfect model, because the extra plant gain speeds up the
cautious controller. Move suppression buys robustness to model error,
Cecil's reason for using it.
""")

d.code("Code 4/4 -- the same problem in GEKKO", [
    "Model as an ODE, flow bounds built in, moves penalized (`DCOST`)",
    "Dead time (1.35 min against $\\tau = 55$ min) neglected here",
], """
m = GEKKO(remote=False); m.time = np.linspace(0, 60, 61)
Mv = m.MV(value=0, lb=-108.8, ub=91.2); Mv.STATUS = 1; Mv.DCOST = 0.3
Cv = m.CV(value=0); Cv.STATUS = 1; Cv.SP = 5; Cv.TR_INIT = 0
m.Equation(p[1] * Cv.dt() == -Cv + p[0] * Mv)   # FOPDT, no dead time
m.options.IMODE = 6; m.options.CV_TYPE = 2       # MPC, squared error
m.solve(disp=False)
T = 150 + np.array(list(Cv.value))
print("planned:", np.round(Mv.value[1:5], 1), "T(10), T(60):",
      T[[10, 60]].round(2))
""", """
GEKKO builds and solves the optimization: `MV` is the manipulated
variable with bounds, `STATUS = 1` lets the optimizer move it,
`DCOST` penalizes each move (like k); `CV` is the controlled variable
with set point 5; the FOPDT is an ODE in `Cv.dt()`. IMODE 6 is MPC;
CV_TYPE 2 squares the error. `remote=False` solves on this machine.
Planned flow changes (from 108.8) -38.3, -64.7, -82.0, -92.7: a
gradual descent toward the lower bound; T reaches 153.25 F at 10 min,
154.96 at 60. Constraints are part of the problem, not clipped after.
""")

d.your_turn(6, """
1. By hand: at steady state, how much must the cooling flow change for
   +5 F? Compare with the sum of the two QDMC moves of Part B,
   $-95.8 + 75.1$.
2. Read the code: in `qdmc`, what would happen without the term
   `cp[i] - cm[i]`?
""", """
(1) 5/(-0.225) = -22.2 lb/min; the two moves sum to -20.7: close, and
closer as R grows (Cecil).
(2) No model-error feedback: the controller would act on the model
alone. With a mismatched plant (or a disturbance) it would settle
with an offset -- the term is MPC's integral action.
""")

d.check("poll", """
In GEKKO, raising `DCOST` from 0.3 to 30 would make the first planned
flow change:

**A)** larger  **B)** smaller  **C)** unchanged, only later moves
change
""", """
B: a much smaller first change than -38.3 lb/min. DCOST penalizes every move,
the first included; the controller spreads the change over time and
reaches the set point more slowly.
""")

# ===================================================================== D
d.part("D", "The Model Inside MPC, Identified from Data",
       "Cecil, Ch. 8, Sec. 8.3", "cecil-ch08")

d.sub("""
### Introduce -- a short, noisy plant test

- Cecil: the step-response coefficients can be fitted by **least
  squares** to any test data (finite impulse response, FIR).
- 60 impulse coefficients at $\\Delta t = 5$ min; only 150 samples of
  a random +/-10 lb/min test; 0.1 F noise and 0.1 F resolution.
- Plain least squares fits the noise. **Ridge regression** (Lecture 10's
  ML tools, plus a penalty) shrinks the coefficients.
- Question: which model makes the better controller?
""")

d.derive("Derive 1/1 -- FIR regression and its penalty",
         "$c_k = \\sum_{j=1}^{60} g_j\\,m_{k-j}$: linear in $g$:",
         """
Least squares: $\\min \\|c - Xg\\|^2$. Ridge:
$\\min \\|c - Xg\\|^2 + \\alpha\\|g\\|^2$ -- the same form as move
suppression, now on the model. `RidgeCV` picks $\\alpha$ by
cross-validation.
""")

d.code("Code 1/3 -- the test data and the regressors", [
    "Column $j$ of $X$ is the input delayed by $j$ samples",
], """
rng = np.random.default_rng(3)
n, N, dt5 = 150, 60, 5.0
m_test = np.repeat(rng.choice([-10.0, 10.0], n // 6 + 1), 6)[:n]
g_true = np.diff(fopdt(dt5 * np.arange(N + 1), *p))
c_meas = np.convolve(m_test, np.r_[0, g_true])[:n]
c_meas = np.round(c_meas + 0.1 * rng.standard_normal(n), 1)
X = np.column_stack([np.r_[np.zeros(j), m_test[:n - j]]
                     for j in range(1, N + 1)])
print(X.shape, c_meas[:5])
""", """
The input holds each random +/-10 for 6 samples (30 min). `g_true` is
the true impulse response (the fitted reactor at 5-min spacing);
`np.convolve` applies the FIR sum; noise is added and the result
rounded to 0.1 F like the real thermometer. `np.r_` concatenates;
column j of X is the input delayed j samples, so X g is the FIR
prediction. 150 rows, 60 unknowns.
""")

d.code("Code 2/3 -- least squares versus ridge", [
    "Two scikit-learn regressors; cumulative sum turns $g$ into $s$",
], """
fits = {"least squares": LinearRegression(fit_intercept=False),
        "ridge": RidgeCV(alphas=np.logspace(-2, 5, 30),
                         fit_intercept=False)}
s_id = {}
for name, mdl in fits.items():
    g_hat = mdl.fit(X, c_meas).coef_
    s_id[name] = np.r_[0, np.cumsum(g_hat)]
    print(f"{name}: gain {s_id[name][-1]:.3f}")
print("alpha chosen:", round(fits["ridge"].alpha_))
""", """
`fit_intercept=False`: deviation variables, no offset term. `coef_`
holds the 60 impulse coefficients; their running sum is the
step-response model s(k). Both give a gain near the true -0.231
(-0.230 and -0.227), but the least-squares s(k) is jagged and the
ridge one is smooth (the next plot). Cross-validation chose
alpha = 1172.
""")

d.code("Code 3/3 -- put each model in the controller", [
    "QDMC, $\\Delta t = 5$ min, $R = 12$, $L = 2$, $k = 0$; true plant",
], """
s_plant = fopdt(dt5 * np.arange(400), *p)
fig, ax = plt.subplots(figsize=(7, 5.25))
for name, sm in [("true", s_plant), *s_id.items()]:
    sm = np.r_[sm, np.full(400 - len(sm), sm[-1])][:400]
    y, M = qdmc(sm, s_plant, 12, 2, 0.0, n=40)
    tv = np.abs(np.diff(np.r_[0, M])).sum()
    ax.plot(dt5 * np.arange(40), 150 + y,
            label=f"{name}: IAE {np.abs(5-y).sum():.0f}, "
                  f"moves {tv:.0f}")
ax.set(xlabel="t (min)", ylabel="T (F)"); ax.legend(); plt.show()
""", """
Each identified s(k) is padded with its final value to the length
`qdmc` needs, then used as the controller's model against the true
plant. "moves" is the total variation, the sum of |change in flow|:
how hard the valve works. True model: IAE 10, moves 203. Least
squares: IAE 41, moves 2887, and the temperature swings grow -- the
noise in s(k) becomes valve thrashing. Ridge: IAE 15, moves 587. Regularizing the model did what
smoothing did for Cecil.
""")

d.your_turn(6, """
Read the code: what does each print?

```python
print(np.r_[0, np.cumsum([1.0, 2.0, 3.0])])
print(np.convolve([1.0, 0.0, 0.0], [0.0, 0.5, 0.3])[:3])
```

Which line turns an impulse response into a step response?
""", """
[0. 1. 3. 6.] and [0. 0.5 0.3]. The first: s(k) is the running sum of
g(k). The second shows a unit pulse at k = 0 producing the impulse
response itself.
""")

d.check("cold-call", """
Both identified models had nearly the right gain. Why did one make a
much worse controller?
""", """
MPC uses the whole s(k) shape, especially the early coefficients that
set the first moves; noise there is amplified by an aggressive
controller (Cecil's quantization-noise example). A good model for
control needs the right dynamics, not just the right gain: fit
quality and control quality are different tests (Lectures 10-11).
""")

d.slide("""
### Wrap-up

**Derived, then coded:** the dead-time limit on PID and the Smith
predictor; step and impulse response models and superposition; the
dynamic matrix and QDMC; move suppression and constraints; GEKKO MPC;
FIR identification by least squares and by ridge regression, judged
inside the controller.

**Tools:** `deque` as a dead time, `toeplitz`, `np.linalg.solve`,
receding-horizon loops, `GEKKO` (`MV`, `CV`, `IMODE = 6`),
`RidgeCV`

**Course end:** from first-order lags to model predictive control.
""")

d.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), NB))
