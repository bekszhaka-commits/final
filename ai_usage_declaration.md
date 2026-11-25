# AI Usage Declaration

## Project Details
- **Project Title:** Mini Campus Delivery Robot (A*, Bayesian Inference & MDP Simulation)
- **Files Covered:** `delivery_robot_campus_clean.py` (Streamlit prototype), `campus_robot.html` (Standalone web application)[cite: 1, 2]

---

## Summary of AI Assistance
Generative AI was used as a development and learning aid during the design, implementation, and debugging of this project. All core algorithmic logic, mathematical parameters, and final code outputs were reviewed, tested, and verified by the author.

| Project Component | Level of AI Involvement | Description of Use |
| :--- | :--- | :--- |
| **Algorithm Design (A*, Bayes, MDP)** | Conceptual Review & Verification | Verified mathematical formulations for Manhattan distance heuristics, Bayes' theorem updates, and Value Iteration convergence (`solveMDP`).[cite: 1, 2] |
| **Python Prototype (`delivery_robot_campus_clean.py`)** | Code Scaffolding & Refactoring | Assisted with Streamlit layout structure (`st.sidebar`, `st.columns`, `st.session_state`) and clean modular separation.[cite: 1] |
| **Web Application (`campus_robot.html`)** | UI/UX & Front-End Implementation | Assisted with responsive CSS Grid styling, light/dark theme variables, SVG path overlay rendering, and DOM event handling.[cite: 2] |
| **Documentation & Explanations** | Drafting & Editing | Generated structural code explanations and helped format project documentation. |

---

## Detailed Breakdown of Prompts & Usage
1. **Architecture & Prototyping:**
   - Used AI to structure the 5×5 grid coordinate helpers (`cell_to_pos` / `pos_to_cell`) and integrate the three AI modules into an interactive Streamlit dashboard.[cite: 1]
2. **Transition to Standalone Web App (`final.html`):**
   - Used AI to port the Python logic into vanilla JavaScript, upgrade the single-step Expected Utility calculation into an infinite-horizon Value Iteration solver (`solveMDP()`), and add interactive map-editing tools (Wall, Start, Goal, Hazard).[cite: 1, 2]
3. **Debugging & Accessibility:**
   - Used AI to refine the SVG polyline coordinate alignment over the CSS grid and add ARIA labels (`aria-pressed`, `aria-label`) for keyboard and screen-reader accessibility.[cite: 2]

---

## Author Attestation
I confirm that:
- I understand how every function in `delivery_robot_campus_clean.py` and `campus_robot.html` operates and can explain the underlying AI algorithms independently.[cite: 1, 2]
- All AI-generated code snippets were critically evaluated, adapted to meet project requirements, and tested for edge cases (such as unreachable goals and boundary probabilities).
- This declaration accurately reflects the extent of AI tool usage in accordance with academic/organizational integrity guidelines.
