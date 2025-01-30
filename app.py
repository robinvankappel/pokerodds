import streamlit as st
from ICMmodels import *

def add_player(players):
    players.append({"name": f"Player {len(players) + 1}", "stack": ""})

def remove_player(players, index):
    if len(players) > 2:
        del players[index]

def update_stack(players, index, value):
    players[index]["stack"] = value

def update_payout(payouts, index, value):
    payouts[index] = value

def get_ordinal_suffix(number):
    if 10 <= number % 100 <= 20:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

def run_test():
    chip_stacks = [5000, 3000, 2000]
    payouts = [50, 30, 20]
    num_simulations = 100000
    expected_output = {
        "ICM EV": [38.4, 32.8, 28.8],
        "Probabilities": [[0.50, 0.30, 0.20], [0.34, 0.37, 0.29], [0.16, 0.32, 0.51]]
    }

    result = calculate_icm_monte_carlo(chip_stacks, payouts, num_simulations=num_simulations)

    st.write("### Test Input:")
    st.json({"chip_stacks": chip_stacks, "payouts": payouts, "num_simulations": num_simulations})

    st.write("### Expected Output:")
    st.json(expected_output)

    st.write("### Actual Output:")
    st.json(result)

    icm_ev_match = all(abs(result["ICM EV"][i] - expected_output["ICM EV"][i]) < 1.0 for i in range(len(result["ICM EV"])))
    probabilities_match = all(
        all(abs(result["Probabilities"][pos][player] - expected_output["Probabilities"][pos][player]) < 0.05
            for player in range(len(result["Probabilities"][pos])))
        for pos in range(len(result["Probabilities"]))
    )

    if icm_ev_match and probabilities_match:
        st.success("Test passed! The function is working correctly.")
    else:
        st.error("Test failed. The function is not producing expected results.")

# Streamlit UI
st.title("ICM Calculator")
st.subheader("Calculate Independent Chip Model (ICM) equity and probabilities")

# Define initial states
if "players" not in st.session_state:
    st.session_state.players = [
        {"name": "Player 1", "stack": ""},
        {"name": "Player 2", "stack": ""},
    ]

if "payouts" not in st.session_state:
    st.session_state.payouts = ["0"] * 9

if "results" not in st.session_state:
    st.session_state.results = {}

# UI Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Prize Pool Structure")
    for i in range(len(st.session_state.players)):
        payout = st.number_input(
            f"{i + 1}{get_ordinal_suffix(i + 1)} Place:",
            min_value=0.0,
            step=1.0,
            value=float(st.session_state.payouts[i]),
            key=f"payout_{i}",
            on_change=lambda i=i: update_payout(
                st.session_state.payouts, i, st.session_state[f"payout_{i}"]
            ),
        )

with col2:
    st.markdown("### Players")
    for i, player in enumerate(st.session_state.players):
        player_name, stack = st.columns([3, 2])
        with player_name:
            st.text_input(
                f"Player {i + 1} Name:",
                value=player["name"],
                key=f"player_name_{i}",
                on_change=lambda i=i: st.session_state.players[i].update(
                    {"name": st.session_state[f"player_name_{i}"]}
                ),
            )
        with stack:
            st.number_input(
                f"Stack size {i + 1}:",
                min_value=0.0,
                step=1.0,
                value=float(player["stack"] or 0),
                key=f"player_stack_{i}",
                on_change=lambda i=i: update_stack(
                    st.session_state.players, i, st.session_state[f"player_stack_{i}"]
                ),
            )

num_simulations = st.number_input(
    "Number of Simulations:",
    min_value=1000,
    max_value=500000,
    value=100000,
    step=1000,
    key="num_simulations"
)

st.button(
    label="Add Player",
    on_click=lambda: add_player(st.session_state.players),
    key="add_player",
)

st.button(
    label="Calculate ICM",
    key="calculate_icm",
    on_click=lambda: st.session_state.results.update(
        calculate_icm_monte_carlo(
            [float(player["stack"] or 0) for player in st.session_state.players],
            [float(payout or 0) for payout in st.session_state.payouts],
            num_simulations=st.session_state.num_simulations
        )
    ),
)

# Add Test Button
if st.button("Run Test"):
    run_test()

# Results
if "results" in st.session_state and st.session_state.results:
    st.subheader("Results")
    results = st.session_state.results

    st.markdown("### ICM EV")
    for i, ev in enumerate(results["ICM EV"]):
        st.write(f"Player {i + 1}: {ev:.2f}")

    st.markdown("### Probabilities")
    for pos, prob_list in enumerate(results["Probabilities"]):
        st.write(f"Position {pos + 1}:")
        for i, prob in enumerate(prob_list):
            st.write(f"  Player {i + 1}: {prob:.2%}")
