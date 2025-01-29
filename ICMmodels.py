import math
import random
from decimal import Decimal

def simulate_tournament(chip_stacks):
    """
    Simulates a single tournament outcome based on chip stacks.

    Args:
        chip_stacks (list): List of chip stacks for each player.

    Returns:
        list: Players in the order they finish (from first place to last place).
    """
    remaining_players = list(range(len(chip_stacks)))
    elimination_order = []

    while len(remaining_players) > 1:
        # Calculate probabilities of elimination
        total_chips = sum(chip_stacks[player] for player in remaining_players)
        elimination_probs = [chip_stacks[player] / total_chips for player in remaining_players]

        # Eliminate one player based on probabilities
        eliminated = random.choices(remaining_players, weights=elimination_probs, k=1)[0]
        elimination_order.append(eliminated)
        remaining_players.remove(eliminated)

    # Add the winner (last remaining player) to the elimination order
    elimination_order.append(remaining_players[0])

    # Finishing order matches the elimination order
    return elimination_order

def calculate_chip_chop_icm(chip_stacks, payouts):
    """
    Calculate ICM EVs using the Chip-Chop method.

    Args:
        chip_stacks (list): List of chip stacks for each player.
        payouts (list): List of payouts for finishing positions.

    Returns:
        dict: Contains ICM EVs for each player.
    """
    total_chips = sum(chip_stacks)
    icm_ev = [stack / total_chips * sum(payouts) for stack in chip_stacks]

    return {"ICM EV": icm_ev}

def calculate_malmuth_harville_alternative(stacks, payouts):
    class ICMAlternative:
        def __init__(self, stacks, payouts):
            self.stacks = stacks
            self.payouts = payouts
            self.equities = []
            self.probabilities = []
            self.num_players = len(stacks)
            self.prepare()

        def prepare(self):
            total = sum(self.stacks)
            for k, v in enumerate(self.stacks):
                equity = self.get_equities(Decimal(total), k, 0)
                self.equities.append(float(round(equity, 4)))
            self.calculate_probabilities()

        def get_equities(self, total, player, depth):
            eq = Decimal(self.stacks[player]) / total * Decimal(str(self.payouts[depth]))
            if depth + 1 < len(self.payouts):
                for i, stack in enumerate(self.stacks):
                    if i != player and stack > 0.0:
                        self.stacks[i] = 0.0  # Set stack to 0 temporarily
                        eq += self.get_equities(total - stack, player, depth + 1) * (Decimal(stack) / Decimal(total))
                        self.stacks[i] = stack  # Restore stack value
            return eq

        def calculate_probabilities(self):
            position_counts = [[0] * self.num_players for _ in range(self.num_players)]

            def simulate_tournament(remaining_stacks, remaining_indices):
                total_chips = sum(remaining_stacks)
                if len(remaining_stacks) == 1:
                    # Record the last player's position
                    last_player_index = remaining_indices[0]
                    position_counts[len(self.stacks) - len(remaining_indices)][last_player_index] += 1
                    return

                for i, stack in enumerate(remaining_stacks):
                    prob = stack / total_chips
                    reduced_stacks = remaining_stacks[:i] + remaining_stacks[i + 1:]
                    reduced_indices = remaining_indices[:i] + remaining_indices[i + 1:]
                    simulate_tournament(reduced_stacks, reduced_indices)

            simulate_tournament(self.stacks[:], list(range(self.num_players)))

            # Calculate probabilities from position counts
            num_simulations = sum(position_counts[0]) or 1  # Prevent division by zero
            self.probabilities = [
                [count / num_simulations for count in position_counts[pos]]
                for pos in range(self.num_players)
            ]

    model = ICMAlternative(stacks, payouts)
    return {"ICM EV": model.equities, "Probabilities": model.probabilities}


def calculate_icm_monte_carlo(chip_stacks, payouts, num_simulations=100000):
    """
    Calculate ICM EVs using Monte Carlo simulations.

    Args:
        chip_stacks (list): List of chip stacks for each player.
        payouts (list): List of payouts for finishing positions.
        num_simulations (int): Number of simulations to run.

    Returns:
        dict: Contains probabilities and ICM EVs for each player.
    """
    num_players = len(chip_stacks)
    position_counts = [[0] * num_players for _ in range(num_players)]

    for _ in range(num_simulations):
        finishing_order = simulate_tournament(chip_stacks)
        for pos, player in enumerate(finishing_order):
            position_counts[pos][player] += 1

    probabilities = [[count / num_simulations for count in position_counts[pos]] for pos in range(num_players)]
    icm_ev = [sum(probabilities[pos][player] * payouts[pos] for pos in range(num_players)) for player in range(num_players)]

    return {"ICM EV": icm_ev, "Probabilities": probabilities}

