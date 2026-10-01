"""
Single source of truth for the site's lecture cards and chapter list.

tools/build_site.py renders index.html, derivations.html and chapters.html
from this file. A lecture with `status="slot"` gets an empty placeholder
card: those are the lectures whose textbook chapter files are not yet
available (REVISION_PLAN.md, Section 9).
"""

LECTURES = [
    dict(n=1, folder="01-intro-fundamentals",
         base="PSE-823_Lecture-01_Intro-Fundamentals",
         title="Introduction: Control Fundamentals and the DCS Layer",
         meta="Coughanowr &amp; LeBlanc, Ch. 1 &middot; Cecil Smith, Ch. 1 (Sec. 1.1&ndash;1.2)",
         chapters=["coughanowr-ch01", "cecil-ch01"],
         deriv="Hot-water tank on/off, P and PI; offset formula; DCS block arithmetic"),
    dict(n=2, folder="02-modeling-laplace",
         base="PSE-823_Lecture-02_Modeling-Laplace",
         title="Modeling and Laplace Transforms, Derived then Coded",
         meta="Coughanowr &amp; LeBlanc, Ch. 2&ndash;3",
         chapters=["coughanowr-ch02", "coughanowr-ch03"],
         deriv="Mixing and heated tanks; Problem 2.9; Examples 3.1&ndash;3.5 inverted"),
    dict(n=3, folder="03-first-order-systems",
         base="PSE-823_Lecture-03_First-Order-Systems",
         title="First-Order Systems: Derive, then Code",
         meta="Coughanowr &amp; LeBlanc, Ch. 4&ndash;6",
         chapters=["coughanowr-ch04", "coughanowr-ch05", "coughanowr-ch06"],
         deriv="Thermometer responses; fitting tau; linearization window; tanks in series"),
    dict(n=4, folder="04-second-order-control-system",
         base="PSE-823_Lecture-04_Second-Order-Control-System",
         title="Second-Order Systems, Transportation Lag and the Control System",
         meta="Coughanowr &amp; LeBlanc, Ch. 7&ndash;8",
         chapters=["coughanowr-ch07", "coughanowr-ch08"],
         deriv="Underdamped step response; overshoot and decay ratio; Pade; block diagram reduction"),
    dict(n=5, status="slot",
         title="Controllers, the Reactor Block Diagram and Digital PID",
         meta="Coughanowr &amp; LeBlanc, Ch. 9&ndash;11 and Ch. 26",
         chapters=["coughanowr-ch09", "coughanowr-ch10", "coughanowr-ch11",
                   "coughanowr-ch26"],
         why="Waiting for the Ch. 26 chapter file"),
    dict(n=6, folder="06-closed-loop-stability",
         base="PSE-823_Lecture-06_Closed-Loop-Stability",
         title="Closed-Loop Response, Stability and Root Locus",
         meta="Coughanowr &amp; LeBlanc, Ch. 12&ndash;14",
         chapters=["coughanowr-ch12", "coughanowr-ch13", "coughanowr-ch14"],
         deriv="P and PI offset; measurement lag; Routh array; root locus"),
    dict(n=7, folder="07-frequency-response",
         base="PSE-823_Lecture-07_Frequency-Response",
         title="Frequency Response and Bode Diagrams",
         meta="Coughanowr &amp; LeBlanc, Ch. 15",
         chapters=["coughanowr-ch15"],
         deriv="Substitution rule; AR and phase of each block; Bode asymptotes"),
    dict(n=8, folder="08-frequency-design",
         base="PSE-823_Lecture-08_Frequency-Design",
         title="Control System Design by Frequency Response",
         meta="Coughanowr &amp; LeBlanc, Ch. 16",
         chapters=["coughanowr-ch16"],
         deriv="Crossover frequency; Bode criterion; gain and phase margins; Ziegler&ndash;Nichols"),
    dict(n=9, status="slot",
         title="Advanced Strategies: Cascade, Feedforward, Override",
         meta="Coughanowr &amp; LeBlanc, Ch. 17 &middot; Cecil Smith, Ch. 2&ndash;6",
         chapters=["coughanowr-ch17", "cecil-ch02", "cecil-ch03", "cecil-ch04",
                   "cecil-ch05", "cecil-ch06"],
         why="Waiting for the Cecil Smith Ch. 2 chapter file"),
    dict(n=10, folder="10-tuning-identification",
         base="PSE-823_Lecture-10_Tuning-Identification",
         title="Controller Tuning and Process Identification",
         meta="Coughanowr &amp; LeBlanc, Ch. 18",
         chapters=["coughanowr-ch18"],
         deriv="Reaction-curve inflection point; normal equations; tank gain linearized"),
    dict(n=11, folder="11-complex-processes",
         base="PSE-823_Lecture-11_Complex-Processes",
         title="Theoretical Analysis of Complex Processes",
         meta="Coughanowr &amp; LeBlanc, Ch. 20",
         chapters=["coughanowr-ch20"],
         deriv="Kettle linearization; absorber damping bound; slab and exchanger transforms"),
    dict(n=12, status="slot",
         title="State-Space Representation and the Transition Matrix",
         meta="Coughanowr &amp; LeBlanc, Ch. 21&ndash;22",
         chapters=["coughanowr-ch21", "coughanowr-ch22"],
         why="Waiting for the Ch. 22 chapter file"),
    dict(n=13, folder="13-multivariable-control",
         base="PSE-823_Lecture-13_Multivariable-Control",
         title="Multivariable Control: Interaction, RGA and Decoupling",
         meta="Coughanowr &amp; LeBlanc, Ch. 23 &middot; Cecil Smith, Ch. 7, Sec. 8.1",
         chapters=["coughanowr-ch23", "cecil-ch07", "cecil-ch08"],
         deriv="Ex. 23.1 by hand; RGA row sums; PI cross-controllers; the reduced quartic"),
    dict(n=14, status="slot",
         title="Nonlinear Systems and Phase-Plane Analysis",
         meta="Coughanowr &amp; LeBlanc, Ch. 24&ndash;25",
         chapters=["coughanowr-ch24", "coughanowr-ch25"],
         why="Waiting for the Ch. 25 chapter file"),
    dict(n=15, folder="15-dead-time-mpc",
         base="PSE-823_Lecture-15_Dead-Time-MPC",
         title="Dead-Time Compensation and Model Predictive Control",
         meta="Cecil Smith, Sec. 8.2&ndash;8.3",
         chapters=["cecil-ch08"],
         deriv="Smith predictor closed loop; QDMC least-squares moves; square DMC limits"),
]

# Chapter list. `src` is the file name in the Drive Books/ folder; None means
# the chapter file is not available yet.
COUGHANOWR = [
    (1, "Introductory Concepts", "1.1 Why process control? 1.2 Control systems"),
    (2, "Modeling Tools for Process Dynamics", "2.1 A chemical mixing scenario; 2.2 Mathematical tools; 2.3 Solution of ODEs"),
    (3, "Inversion by Partial Fractions", "3.1 Partial fractions; 3.2 Qualitative nature of solutions"),
    (4, "Response of First-Order Systems", "4.1 Transfer function; 4.2-4.7 step, impulse, ramp, sinusoidal responses"),
    (5, "Physical Examples of First-Order Systems", "5.1 Examples; 5.2 Linearization"),
    (6, "Response of First-Order Systems in Series", "6.2 Noninteracting system; 6.3 Interacting system"),
    (7, "Higher-Order Systems: Second-Order and Transportation Lag", "7.1 Second-order system; 7.2 Transportation lag"),
    (8, "The Control System", "8.2 Components; 8.3 Block diagram; 8.4 Development of block diagram"),
    (9, "Controllers and Final Control Elements", "9.1 Mechanisms; 9.2 Ideal transfer functions"),
    (10, "Block Diagram of a Chemical-Reactor Control System", "10.1-10.8 Reactor, valve, measuring element, controller, lag, block diagram"),
    (11, "Closed-Loop Transfer Functions", "11.1 Symbols; 11.2 Single-loop systems; 11.3 Multiloop systems"),
    (12, "Transient Response of Simple Control Systems", "12.1-12.4 P and PI for set point and load; 12.5 Measurement lag"),
    (13, "Stability", "13.1-13.3 Concept, definition, criterion; 13.4 Routh test"),
    (14, "Root Locus", "14.1 Concept of root locus"),
    (15, "Introduction to Frequency Response", "15.1 Substitution rule; 15.2 Bode diagrams"),
    (16, "Control System Design by Frequency Response", "16.1 Tank temperature control; 16.2 Bode criterion; 16.3 Margins; 16.4 Ziegler-Nichols"),
    (17, "Advanced Control Strategies", "17.1 Cascade; 17.2 Feedforward; 17.3 Ratio; 17.4 Smith predictor; 17.5 IMC"),
    (18, "Controller Tuning and Process Identification", "18.1 Tuning; 18.2 Tuning rules; 18.3 Process identification"),
    (19, "Control Valves", "19.1 Construction; 19.2 Sizing; 19.3 Characteristics; 19.4 Positioner"),
    (20, "Theoretical Analysis of Complex Processes", "20.1 Steam-jacketed kettle; 20.2 Gas absorber; 20.3 Distributed-parameter systems"),
    (21, "State-Space Representation of Physical Systems", "21.2 State variables"),
    (22, "Transfer Function Matrix", "22.1 Transition matrix; 22.2 Transfer function matrix"),
    (23, "Multivariable Control", "23.1 Interacting systems; 23.2 Stability of multivariable systems"),
    (24, "Examples of Nonlinear Systems", "24.2 Phase plane; 24.3 Damped oscillator; 24.4 Pendulum; 24.5 Chemical reactor"),
    (25, "Examples of Phase-Plane Analysis", "25.1 Phase space; 25.2 Examples"),
    (26, "Microprocessor-Based Controllers and Distributed Control", "26.1-26.5 Hardware, tasks, special features, distributed control"),
]
COUGHANOWR_MISSING = {19, 22, 25, 26}

CECIL = [
    (1, "Introduction", "1.1 Implementing control logic; 1.2 Control blocks; 1.3-1.9 PID, integrator, lead-lag, dead time, selector, cutoff, hand station"),
    (2, "Cascade Control", "2.1 Jacketed reactor; 2.11 Tuning cascades; 2.12-2.15 Windup protection"),
    (3, "Split-Range Control", "3.1 Storage tank pressure; 3.2 Split range; 3.3-3.4 Temperature control"),
    (4, "Override Control", "4.1 Limit on cooling water return; 4.2-4.6 Windup protection, limits"),
    (5, "Valve Position Control", "5.1-5.4 Polymer pumping, reheat, equilibrium reaction, once-through jacket"),
    (6, "Ratio and Feedforward Control", "6.1-6.8 Ratios, trim, compensation; 6.9-6.10 Feedforward"),
    (7, "Loop Interaction", "7.1 Multivariable processes; 7.3 Gains; 7.4 Measures of interaction; 7.5 Pairing"),
    (8, "Multivariable Control", "8.1 Decoupler; 8.2 Dead-time compensation; 8.3 Model predictive control"),
]
CECIL_MISSING = {2}


def chapters():
    """Every chapter as a dict, in display order."""
    out = []
    for n, title, secs in COUGHANOWR:
        out.append(dict(slug=f"coughanowr-ch{n:02d}", book="Coughanowr & LeBlanc",
                        num=n, title=title, sections=secs,
                        available=n not in COUGHANOWR_MISSING))
    for n, title, secs in CECIL:
        out.append(dict(slug=f"cecil-ch{n:02d}", book="Cecil Smith",
                        num=n, title=title, sections=secs,
                        available=n not in CECIL_MISSING))
    return out


def lectures_using(slug):
    return [L["n"] for L in LECTURES if slug in L.get("chapters", [])]
