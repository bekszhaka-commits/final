# Technical Report: Mini Campus Delivery Robot
**Course:** ICT1103 - AI Fundamentals  
**Date:** November 25, 2026

---

## 1. Introduction and Problem Statement
Autonomous campus delivery robots operate in dynamic environments where static floor plans frequently diverge from real-time corridor conditions. A delivery agent must compute collision-free paths across building layouts, interpret noisy sensor readings when encountering unexpected obstructions, and weigh the reward of timely package delivery against the high cost of physical collisions.

**Core Problem Statement:**  
Campus delivery robots must find an optimal route across a structured campus grid, handle noisy sensor readings regarding blocked corridors, and decide whether to move or wait when collisions carry severe penalties.

### 1.1 Measurable Objectives
1. **Optimal Pathfinding:** Compute the shortest collision-free route from Start (Cell 21) to Goal (Cell 5) across a $5 \times 5$ campus map while avoiding static walls (Cells 7, 8, 14, 18) and high-penalty hazard zones (Cell 10).
2. **Probabilistic Belief Updating:** Update the prior probability of an obstacle in an uncertain corridor (Cell 16) using Bayesian inference given a binary sensor signal (Alarm vs. Clear) with known sensitivity and false-positive rates.
3. **Rational Decision-Making Under Uncertainty:** Select between `MOVE` and `WAIT` actions at the uncertain corridor by maximizing expected utility using a 2-state Markov Decision Process (MDP) calibrated with explicit step costs, delivery rewards, and collision penalties.

---

## 2. System Design and Architecture
The system is architected as a modular pipeline implemented in Python with an interactive Streamlit web interface (`app.py`). Each core AI paradigm operates as an independent functional module passing state representations forward, as summarized in Table 1.

### 2.1 Environment Representation
The campus floor is modeled as a $5 \times 5$ grid indexed sequentially from Cell 1 (top-left, row 0, col 0) to Cell 25 (bottom-right, row 4, col 4):
* **Start State (S):** Cell 21 (row 4, col 0).
* **Goal State (G):** Cell 5 (row 0, col 4), yielding reward $R_{goal} = +10.0$.
* **Impassable Walls:** Cells `{7, 8, 14, 18}`.
* **Hazard Zone (!):** Cell 10, carrying a penalty of `-10.0` (modeled in pathfinding with an elevated step cost of `20` so the planner actively routes around it).
* **Uncertain Corridor (?):** Cell 16, directly adjacent to the starting position along the optimal northern corridor.
* **Movement Cost:** Every discrete step incurs a time/energy cost of $c_{step} = 0.1$.

**Table 1: Modular Pipeline Architecture of the Mini Campus Delivery Robot**

| Pipeline Stage | Input | Output |
| :--- | :--- | :--- |
| **1. Campus Grid State** | $5 \times 5$ grid, walls `{7, 8, 14, 18}`, hazard `10` | Walkable graph representation |
| **2. $A^*$ Search Module** | Start (`21`), Goal (`5`), Manhattan heuristic | Shortest collision-free route |
| **3. Bayesian Inference** | Prior $P(B) = 0.20$, sensor signal $S \in \{\text{Alarm}, \text{Clear}\}$ | Posterior belief $P(B \mid S)$ |
| **4. 2-State MDP Module** | Posterior $P(B \mid S)$, rewards `{+10, -10, -0.1}` | Optimal action $\pi^* \in \{\text{MOVE}, \text{WAIT}\}$ |

---

## 3. Algorithms and Mathematical Formulations

### 3.1 $A^*$ Pathfinding Algorithm
To compute the shortest path from Start to Goal without diagonal movement, the robot employs $A^*$ search, evaluating each candidate node $n$ via the total estimated cost function:

$$f(n) = g(n) + h(n) \tag{1}$$

where $g(n)$ is the exact accumulated path cost from Cell 21 to node $n$ (`+1` per normal step, `+20` if entering Hazard Cell 10), and $h(n)$ is the Manhattan distance heuristic to Goal Cell 5:

$$h(n) = |r_n - r_{goal}| + |c_n - c_{goal}| \tag{2}$$

Because movement is restricted to four cardinal directions (Up, Down, Left, Right) with a minimum step cost of 1, $h(n)$ never overestimates the true remaining distance. Thus, $h(n)$ is admissible and consistent, guaranteeing that $A^*$ finds the globally optimal path.

### 3.2 Bayesian Inference for Obstacle Estimation
When approaching Cell 16, the robot receives a binary reading $S \in \{\text{Alarm}, \text{Clear}\}$ from an obstacle sensor. Let $B$ denote the event that Cell 16 is blocked and $\neg B$ denote that it is clear. Given a prior blockage probability $P(B) = 0.20$, the robot updates its belief using Bayes' Theorem:

$$P(B \mid S) = \frac{P(S \mid B)P(B)}{P(S)} \tag{3}$$

where the marginal probability of the sensor evidence $P(S)$ is computed via the Law of Total Probability:

$$P(S) = P(S \mid B)P(B) + P(S \mid \neg B)P(\neg B) \tag{4}$$

**Sensor Parameters:**
* **Sensitivity (True Positive Rate):** $P(\text{Alarm} \mid B) = 0.85$
* **False Negative Rate:** $P(\text{Clear} \mid B) = 1 - 0.85 = 0.15$
* **False Positive Rate:** $P(\text{Alarm} \mid \neg B) = 0.10$
* **Specificity (True Negative Rate):** $P(\text{Clear} \mid \neg B) = 1 - 0.10 = 0.90$

### 3.3 Markov Decision Process (MDP) Decision Module
Using the posterior blockage probability $p = P(B \mid S)$, the robot solves a 2-state decision problem (Clear vs. Blocked) to choose between executing `MOVE` or `WAIT`.

**Reward and Discount Parameters:**
* **Delivery Goal Reward:** $R_{goal} = +10.0$
* **Collision Penalty:** $R_{collision} = -10.0$
* **Step / Time Cost:** $c_{step} = 0.1$
* **Discount Factor:** $\gamma = 0.9$

**Expected Utility of MOVE:** If the corridor is clear (probability $1 - p$), the robot advances toward the goal and receives $R_{goal} - c_{step}$. If blocked (probability $p$), it collides and incurs $R_{collision} - c_{step}$:

$$EU(\text{MOVE}) = (1 - p)(10.0 - 0.1) + p(-10.0 - 0.1) = 9.9(1 - p) - 10.1p \tag{5}$$

**Expected Utility of WAIT:** Waiting avoids immediate collision risk at the expense of one step cost (`-0.1`), transitioning to a discounted future state ($\gamma = 0.9$) where the corridor has an equal chance (`0.5`) of clearing:

$$EU(\text{WAIT}) = -0.1 + 0.9 \times ((0.5 \times 10.0) - 0.1) = -0.1 + 0.9(4.9) = +4.31 \tag{6}$$

The optimal policy $\pi^*$ selects the action that maximizes expected utility:

$$\pi^* = \arg\max_{a \in \{\text{MOVE}, \text{WAIT}\}} EU(a) \tag{7}$$

---

## 4. Experimental Results

### 4.1 $A^*$ Route Execution
Under the default wall configuration (`{7, 8, 14, 18}`), $A^*$ bypasses the central wall cluster and avoids the high-cost hazard at Cell 10, generating an optimal 8-step route along the left and top perimeter:

$$\text{Route: } 21 \rightarrow 16 \rightarrow 11 \rightarrow 6 \rightarrow 1 \rightarrow 2 \rightarrow 3 \rightarrow 4 \rightarrow 5 \tag{8}$$

When interactive walls are toggled in the Streamlit interface (e.g., blocking Cell 3), $A^*$ dynamically recalculates an alternate valid path through the lower-right corridor ($21 \rightarrow 22 \rightarrow 23 \rightarrow 24 \rightarrow 25 \rightarrow 20 \rightarrow 15 \rightarrow 9 \rightarrow 4 \rightarrow 5$), cleanly bypassing Cell 10.

### 4.2 Bayesian Belief Updates and MDP Policy Comparison
Evaluating the system across both sensor states from a baseline prior of $P(B) = 0.20$ yields the quantitative results presented in Table 2.

**Table 2: Comparison of Bayesian Posterior Beliefs and MDP Expected Utilities**

| Metric / Output | Scenario A: No Alarm (Clear) | Scenario B: Alarm Triggered (Alarm) |
| :--- | :--- | :--- |
| **Prior Obstacle Probability $P(B)$** | `0.200` | `0.200` |
| **Evidence Likelihood $P(S)$** | $(0.15)(0.20) + (0.90)(0.80) = 0.750$ | $(0.85)(0.20) + (0.10)(0.80) = 0.250$ |
| **Posterior Probability $P(B \mid S)$** | $\frac{0.030}{0.750} = 0.040$ | $\frac{0.170}{0.250} = 0.680$ |
| **Expected Utility $EU(\text{MOVE})$** | $0.96(9.9) + 0.04(-10.1) = +9.10$ | $0.32(9.9) + 0.68(-10.1) = -3.70$ |
| **Expected Utility $EU(\text{WAIT})$** | `+4.31` | `+4.31` |
| **Recommended Action ($\pi^*$)** | **MOVE** | **WAIT** |

**Analysis:**
* **Scenario A (No Alarm):** Absence of an alarm reduces perceived blockage risk from `20.0%` to `4.0%`. Because $EU(\text{MOVE}) = +9.10 > EU(\text{WAIT}) = +4.31$, the robot confidently proceeds into Cell 16.
* **Scenario B (Alarm Triggered):** An alarm raises posterior blockage risk to `68.0%`. Because the `-10.0` collision penalty heavily outweighs the `+10.0` delivery reward at high risk, $EU(\text{MOVE})$ drops to `-3.70`, prompting the MDP to switch its recommendation to `WAIT` (`+4.31`).
* **Decision Boundary:** Setting $EU(\text{MOVE}) = EU(\text{WAIT})$ reveals that the critical risk threshold is $p^* = 0.2795$ (`27.95%`); any posterior probability exceeding `27.95%` causes the robot to wait.

---

## 5. Limitations
1. **Single-Step Static Belief Horizon:** The current Bayesian module processes a single sensor observation rather than accumulating sequential readings over multiple time steps while waiting.
2. **Simplified Wait Transition Model:** In the 2-state MDP, $EU(\text{WAIT})$ assumes a fixed 50% probability that the obstacle clears on the next turn rather than modeling a full multi-step state transition matrix $T(s' \mid s, a)$ solved via Value Iteration.
3. **Full Re-computation on Map Changes:** When a user modifies walls in the grid, $A^*$ recomputes the entire search tree from scratch rather than incrementally repairing the existing path.
4. **Single Uncertain Corridor:** Uncertainty is localized to Cell 16 rather than distributed across multiple dynamic corridors simultaneously.

---

## 6. Conclusion and Future Work
The Mini Campus Delivery Robot demonstrates how classical search, probabilistic reasoning, and utility-based decision theory combine to enable safe autonomous navigation. By integrating $A^*$ pathfinding, Bayesian sensor fusion, and MDP expected-utility evaluation into an interactive application, the agent successfully balances route efficiency against collision risk under noisy sensing.

### 6.1 Future Enhancements
* **Partially Observable Markov Decision Process (POMDP):** Upgrade the 2-state MDP into a full POMDP that maintains a continuous belief state across multiple `WAIT` cycles and updates beliefs iteratively with each new sensor poll.
* **Incremental Replanning ($D^*$ Lite):** Replace full $A^*$ re-execution with $D^*$ Lite so the robot can efficiently update shortest paths in real time when an obstacle persists and forces a detour.
* **Multi-Sensor Fusion:** Incorporate multiple heterogeneous sensors (e.g., LiDAR and ultrasonic readings) using conditional independence assumptions (Naive Bayes sensor model) to improve obstacle classification accuracy across all campus corridors.
```[cite: 3, 4, 5, 6, 7]

*(Note: The name only appeared once on the title header of page 1; the rest of the text and formulas have been kept intact and cleanly formatted[cite: 3, 4, 5, 6, 7].)*
