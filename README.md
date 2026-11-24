# Campus Delivery Robot
 
An interactive demo of a delivery robot that plans a route across a small campus, reasons about a noisy sensor, and decides whether to move or wait. It combines three topics from AI Fundamentals:
 
| Topic | Algorithm | Role in the project |
|---|---|---|
| Search | A* | Finds the cheapest route on a 5×5 grid with walls and hazards |
| Probabilistic reasoning | Bayesian inference | Updates the chance that the next cell is blocked after a sensor reading |
| Decision-making under uncertainty | Markov Decision Process (MDP) | Chooses **Move** or **Wait** by expected reward |
 
**Live demo:** _add your link here_  
**Demo video:** _add your link here_
 
## The problem
 
Delivery robots on a campus face three connected questions. Which route should they take? How much should they trust a noisy obstacle sensor? And if the corridor ahead might be blocked, is it better to push on or wait? Acting on a bad guess can cost time or cause a collision, so the project links the three questions into one pipeline.
 
## Objectives
 
1. Find the shortest route around walls and avoid hazards when possible.
2. Update the obstacle probability from one sensor signal.
3. Recommend Move or Wait using expected reward.
 
## Using the web app
 
1. **Edit the map.** Choose a tool (Wall, Start, Goal or Hazard) and click cells. Click a wall again to remove it. "Clear walls" empties the map and "Reset" restores the default.
2. **Set the sensor.** Use the sliders for the prior probability that the next cell is blocked and for sensor accuracy, then choose Alarm or No alarm.
3. **Read the results.** The grid shows the A* route, and a dashed outline marks the cell the sensor checks (the first cell after the start). Below it are the probability before and after the sensor reading, and the Move/Wait recommendation with its expected values.
## How it works
 
### 1. A* search
 
The robot moves up, down, left or right. Each step costs 1, and entering a hazard cell adds an extra penalty so the route avoids it when another route exists. The heuristic is the Manhattan distance to the goal, which never overestimates the true cost, so A* returns an optimal route.
 
```
f(n) = g(n) + h(n)
```
 
`g` is the cost so far and `h` is the estimated cost to the goal.
 
### 2. Bayesian inference
 
The sensor checks the next cell on the route. With sensor accuracy `a` and prior `P(O)` that the cell is blocked:
 
```
P(O | alarm) = a·P(O) / ( a·P(O) + (1 − a)·(1 − P(O)) )
```
 
The app uses the same value `a` for the detection rate and the true-negative rate. For example, with a 20% prior and 90% accuracy, an alarm raises the probability to 0.18 / 0.26 ≈ **69.2%**. If there is no alarm, the formula uses `(1 − a)` for the obstacle case and `a` for the free case, and the probability drops.
 
### 3. Markov Decision Process
 
The corridor ahead is in one of two states, **Clear** or **Blocked**, and the robot chooses **Move** or **Wait**.
 
| Parameter | Value |
|---|---|
| Move reward | +0.1 per move |
| Goal reward | +10 |
| Hazard reward | −10 |
| Discount factor γ | 0.9 |
| P(reach goal \| Move, Clear) | 0.9 |
| P(reach goal \| Move, Blocked) | 0.3 |
| Wait: Clear → Clear / Blocked | 0.7 / 0.3 |
| Wait: Blocked → Clear / Blocked | 0.4 / 0.6 |
 
Moving ends the episode: the robot either reaches the goal or slips onto the hazard. Waiting costs nothing but lets the corridor change state. Value iteration solves the Bellman equations:
 
```
Q(s, Move) = 0.1 + p·10 + (1 − p)·(−10)
Q(s, Wait) = γ · Σ P(s′ | s, Wait) · V(s′)
V(s)       = max( Q(s, Move), Q(s, Wait) )
```
 
The Bayesian posterior is used as the robot's belief about the state, so the final decision compares the belief-weighted values:
 
```
E[action] = (1 − b)·Q(Clear, action) + b·Q(Blocked, action)
```
 
With these parameters, Wait is better once the blocked probability `b` is above about 11%. After a 69.2% alarm belief, Move is worth about −0.2 and Wait about 6.5, so the robot waits.
 
## Repository structure
 
```
campus-delivery-robot/
├── campus_robot.html                 # interactive web app
├── delivery_robot_campus_clean.py    # command-line version of the same pipeline
├── README.md
└── docs/
    ├── technical_report.pdf
    ├── presentation.pdf
    ├── ai_usage_declaration.md
    └── team_contributions.md
```
 
Rename or move files as needed so this tree matches your repository.
 
## Assumptions and limitations
 
- The map is a static 5×5 grid and the robot sees the whole map.
- The sensor probabilities and MDP transition values are set by hand for illustration, not learned from data.
- The sensor checks one cell and gives one reading. The robot does not accumulate evidence over several readings.
- The MDP has only two abstract states, so it does not model the robot's position along the route.
## Future work
 
- Replan with A* when the robot finds a cell blocked (D* Lite).
- Combine several sensor readings, or model the problem as a POMDP.
- Estimate sensor and transition probabilities from real or simulated data.
- Support larger maps and moving obstacles such as people.
## AI usage
 
See `docs/ai_usage_declaration.md`. _Describe which tools were used (for example, Claude for code drafting and explanations) and what the team verified and changed itself._
 
## Team
 
See `docs/team_contributions.md`.
 
| Name | Contribution |
|---|---|
| _Name 1_ | _e.g. A* module and map editor_ |
| _Name 2_ | _e.g. Bayesian update and sensor controls_ |
| _Name 3_ | _e.g. MDP, report and slides_ |
 
## License
 
_Choose a license (for example MIT) or state that the project is for coursework only._
 
