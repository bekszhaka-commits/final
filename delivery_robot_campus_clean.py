import heapq
import streamlit as st

# ==========================================
# 1. CAMPUS MAP SETUP (5x5 Grid from Image)
# ==========================================
# Rows 0..4 correspond to cells 1..25
DEFAULT_WALLS = {7, 8, 14, 18}
START_CELL = 21
GOAL_CELL = 5
HAZARD_CELL = 10
UNCERTAIN_CELL = 16

def cell_to_pos(cell):
    return divmod(cell - 1, 5)

def pos_to_cell(row, col):
    return row * 5 + col + 1


# ==========================================
# 2. A* PATHFINDING MODULE
# ==========================================
def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def astar_search(start_cell, goal_cell, walls):
    start = cell_to_pos(start_cell)
    goal = cell_to_pos(goal_cell)
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {pos_to_cell(r, c): float("inf") for r in range(5) for c in range(5)}
    g_score[start_cell] = 0
    
    while open_set:
        _, current = heapq.heappop(open_set)
        current_cell = pos_to_cell(*current)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(pos_to_cell(*current))
                current = came_from[current]
            path.append(start_cell)
            return path[::-1]
            
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                neighbor_cell = pos_to_cell(nr, nc)
                if neighbor_cell in walls:
                    continue
                # Add extra cost if stepping on the hazard cell so A* prefers safe routes
                step_penalty = 20 if neighbor_cell == HAZARD_CELL else 1
                tentative_g = g_score[current_cell] + step_penalty
                if tentative_g < g_score[neighbor_cell]:
                    came_from[(nr, nc)] = current
                    g_score[neighbor_cell] = tentative_g
                    f_score = tentative_g + manhattan_distance((nr, nc), goal)
                    heapq.heappush(open_set, (f_score, (nr, nc)))
                    
    return None


# ==========================================
# 3. BAYESIAN INFERENCE MODULE
# ==========================================
def update_obstacle_probability(prior_blocked, alarm_triggered, sensitivity=0.85, false_positive=0.10):
    prior_clear = 1.0 - prior_blocked
    
    if alarm_triggered:
        p_signal_given_blocked = sensitivity
        p_signal_given_clear = false_positive
    else:
        p_signal_given_blocked = 1.0 - sensitivity
        p_signal_given_clear = 1.0 - false_positive
        
    evidence = (p_signal_given_blocked * prior_blocked) + (p_signal_given_clear * prior_clear)
    return (p_signal_given_blocked * prior_blocked) / evidence


# ==========================================
# 4. MDP DECISION MODULE (2-State Corridor)
# ==========================================
def mdp_decision(prob_blocked, step_cost=0.1, goal_reward=10.0, collision_penalty=-10.0, gamma=0.9):
    prob_clear = 1.0 - prob_blocked
    eu_move = (prob_clear * (goal_reward - step_cost)) + (prob_blocked * (collision_penalty - step_cost))
    eu_wait = -step_cost + gamma * ((0.5 * goal_reward) - step_cost)
    action = "MOVE" if eu_move >= eu_wait else "WAIT"
    return action, eu_move, eu_wait


# ==========================================
# 5. STREAMLIT INTERACTIVE UI
# ==========================================
st.set_page_config(page_title="Mini Campus Delivery Robot", layout="wide")
st.title("Mini Campus Delivery Robot")

if "walls" not in st.session_state:
    st.session_state.walls = set(DEFAULT_WALLS)

# Sidebar controls
st.sidebar.header("Sensor & MDP Controls")
prior_prob = st.sidebar.slider("Prior Obstacle Probability (Cell 16)", 0.05, 0.95, 0.20, 0.05)
alarm_state = st.sidebar.radio("Sensor Reading at Cell 16", ["No Alarm (Clear)", "Alarm Triggered"])
sensitivity = st.sidebar.slider("Sensor Sensitivity P(Alarm | Blocked)", 0.50, 0.99, 0.85, 0.01)
false_positive = st.sidebar.slider("False Positive Rate P(Alarm | Clear)", 0.01, 0.50, 0.10, 0.01)

if st.sidebar.button("Reset Default Walls"):
    st.session_state.walls = set(DEFAULT_WALLS)
    st.rerun()

# Compute A*, Bayes, and MDP
route = astar_search(START_CELL, GOAL_CELL, st.session_state.walls)
route_set = set(route) if route else set()
alarm_bool = (alarm_state == "Alarm Triggered")
posterior_prob = update_obstacle_probability(prior_prob, alarm_bool, sensitivity, false_positive)
action, eu_move, eu_wait = mdp_decision(posterior_prob)

col_grid, col_metrics = st.columns([1.3, 1])

with col_grid:
    st.subheader("5×5 Campus Map (Click cells to toggle walls)")
    for r in range(5):
        cols = st.columns(5)
        for c in range(5):
            cell = pos_to_cell(r, c)
            is_wall = cell in st.session_state.walls
            
            # Format cell label
            if is_wall:
                label = "⬛ WALL"
            elif cell == START_CELL:
                label = f"{cell} [S]"
            elif cell == GOAL_CELL:
                label = f"{cell} [G]"
            elif cell == HAZARD_CELL:
                label = f"{cell} [!]"
            elif cell == UNCERTAIN_CELL:
                label = f"{cell} (?)"
            elif cell in route_set:
                label = f"🔹 {cell}"
            else:
                label = str(cell)
                
            # Prevent placing walls on Start, Goal, or Hazard
            disabled = cell in {START_CELL, GOAL_CELL, HAZARD_CELL}
            if cols[c].button(label, key=f"cell_{cell}", use_container_width=True, disabled=disabled):
                if is_wall:
                    st.session_state.walls.remove(cell)
                else:
                    st.session_state.walls.add(cell)
                st.rerun()

with col_metrics:
    st.subheader("1. A* Search Route")
    if route:
        st.success(f"**Route ({len(route) - 1} steps):** {' → '.join(map(str, route))}")
    else:
        st.error("No valid path found! Remove a wall to open a route.")

    st.subheader("2. Bayesian Inference (Cell 16)")
    m1, m2 = st.columns(2)
    m1.metric("Prior Probability", f"{prior_prob:.3f}")
    m2.metric("Posterior Probability", f"{posterior_prob:.3f}", delta=f"{posterior_prob - prior_prob:+.3f}")

    st.subheader("3. MDP Action Recommendation")
    u1, u2 = st.columns(2)
    u1.metric("EU(Move)", f"{eu_move:.2f}")
    u2.metric("EU(Wait)", f"{eu_wait:.2f}")
    
    if action == "MOVE":
        st.success(f"Recommended Action: **{action}**")
    else:
        st.warning(f"Recommended Action: **{action}**")