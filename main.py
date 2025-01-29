from ICMmodels import *

def main(chip_stacks, payouts, model_type):
    """
    Main function to select the ICM model and run the calculations.
    """

    if model_type == ("1" or "chip-chop"):
        result = calculate_chip_chop_icm(chip_stacks, payouts)
    elif model_type == ("2" or "malmuth-harville-alternative"):
        result = calculate_malmuth_harville_alternative(chip_stacks, payouts)
    elif model_type == ("3" or "monte-carlo"):
        num_simulations = input("Enter number of simulations for Monte Carlo (enter to use default=100000): ")
        if not num_simulations:
            num_simulations = 100000
        else:
            num_simulations = int(num_simulations)
        result = calculate_icm_monte_carlo(chip_stacks, payouts, num_simulations)
    else:
        print("Invalid model type selected.")
        return

    print(f"Results for {model_type.capitalize()} ICM:")
    for key, value in result.items():
        print(f"{key}: {value}")

def run_test_case():
    """
    Function to test a specific ICM model.
    """
    chip_stacks = [5000, 3000, 2000]
    payouts = [50, 30, 20]

    # Test Chip-Chop ICM
    print("Testing Chip-Chop ICM...")
    print(calculate_chip_chop_icm(chip_stacks, payouts))

    # Test Malmuth-Harville ICM
    print("\nTesting Malmuth-Harville ICM...")
    print(calculate_malmuth_harville_alternative(chip_stacks, payouts))

    # Test Monte Carlo ICM
    print("\nTesting Monte Carlo ICM...")
    print(calculate_icm_monte_carlo(chip_stacks, payouts, num_simulations=100000))


# Uncomment below to run main or test case
if __name__ == "__main__":
    """
    Choose function to execute:
    """
    # Read environment variables
    run_test_case()

    # Define input
    chip_stacks = [5000, 3000, 2000, 1000, 500, 2000, 5000, 8000, 1500, 2500]
    # chip_stacks = [5000, 3000, 2000, 1000, 500]
    payouts = [50, 30, 20, 10, 0, 0, 0, 0, 0, 0]
    model_type = input("\nSelect ICM model (chip-chop=1, malmuth-harville=2, monte-carlo=3): ").strip().lower()

    main(chip_stacks, payouts, model_type)
