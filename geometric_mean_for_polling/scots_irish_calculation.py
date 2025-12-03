"""
Calculate how many people guessing 0% would balance out one person guessing 5%
to achieve a mean of 0.11% (the Wikipedia-reported percentage of Scots-Irish).
"""

import math
from typing import Dict, Tuple


def calculate_means(guesses: Dict[float, int]) -> Tuple[float, float]:
    """Calculate geometric and arithmetic means from a dictionary of guesses.

    Args:
        guesses: Dictionary where keys are guess values (percentages) and
                 values are the number of people who made that guess.
                 Example: {5.0: 1, 0.0: 44} means 1 person guessed 5%, 44 guessed 0%

    Returns:
        Tuple of (arithmetic_mean, geometric_mean)
        If any guess is 0 or negative, geometric_mean will be 0

    Example:
        >>> guesses = {5.0: 1, 0.0: 44}
        >>> arith, geo = calculate_means(guesses)
        >>> print(f"Arithmetic: {arith:.4f}%, Geometric: {geo:.4f}%")
    """
    if not guesses:
        return 0.0, 0.0

    total_people = sum(guesses.values())
    if total_people == 0:
        return 0.0, 0.0

    # Calculate arithmetic mean: sum(guess * count) / total_people
    weighted_sum = sum(guess * count for guess, count in guesses.items())
    arithmetic_mean = weighted_sum / total_people

    # Calculate geometric mean: exp(sum(count * log(guess)) / total_people)
    # Handle zeros and negatives - if any guess <= 0, geometric mean is 0
    has_non_positive = any(guess <= 0 for guess in guesses)
    if has_non_positive:
        geometric_mean = 0.0
    else:
        log_sum = sum(count * math.log(guess) for guess, count in guesses.items())
        geometric_mean = math.exp(log_sum / total_people)

    return arithmetic_mean, geometric_mean


def print_log_transformation() -> None:
    """Print corresponding values between common probability guesses and their natural log transformations.

    This helps visualize how geometric mean works by showing the log-space
    representation of common values people might guess when estimating probabilities.
    Uses natural logarithm (ln, base e).

    Example:
        >>> print_log_transformation()
    """
    # Common probability values people might guess
    values = [0.01, 0.1, 1.0, 5.0, 10.0, 25.0, 50.0]

    print("\n" + "=" * 60)
    print("Value and Natural Log Transformation Table")
    print("Common probability guesses and their natural log (ln) transformations")
    print("=" * 60)
    print(f"{'Value (%)':<15} {'ln(Value)':<20} {'exp(ln)':<15}")
    print("-" * 60)

    for value in values:
        ln_value = math.log(value)  # Natural logarithm
        exp_value = math.exp(ln_value)  # Should equal value
        print(f"{value:<15.2f} {ln_value:<20.6f} {exp_value:<15.6f}")

    print("-" * 60)
    print("Note: Geometric mean = exp(mean(ln(values)))")
    print("=" * 60)


def calculate_balance(target_mean: float, one_guess: float, zero_guess: float = 0.0) -> float:
    """Calculate the number of people guessing 0% to balance out one person guessing 5%
    to achieve a mean of 0.11% (the Wikipedia-reported percentage of Scots-Irish).
    """

    numerator = one_guess - target_mean
    denominator = target_mean - zero_guess

    if denominator == 0:
        print("Cannot balance: target mean equals zero guess")
        return None

    X = numerator / denominator

    print(f"Target mean: {target_mean}%")
    print(f"One person guesses: {one_guess}%")
    print(f"Other people guess: {zero_guess}%")
    print(f"\nTo balance this out, you need {X:.2f} people guessing {zero_guess}%")
    print("\nVerification:")
    print(f"  Total people: {1 + X:.2f}")
    print(f"  Sum of guesses: {one_guess + zero_guess * X:.2f}")
    print(f"  Mean: {(one_guess + zero_guess * X) / (1 + X):.4f}%")

    return X


if __name__ == "__main__":
    # Example: Scots-Irish calculation
    target_mean = 0.11  # Wikipedia percentage
    one_guess = 5.0  # One person's guess
    result = calculate_balance(target_mean, one_guess, 0.1)
    print(result)

    # Example: Calculate means from dictionary
    print("\n" + "=" * 50)
    print("Example: Calculating means from dictionary")
    print("=" * 50)
    guesses = {5.0: 1, 0.1: 50}  # 1 person guessed 5%,
    arith_mean, geo_mean = calculate_means(guesses)
    print(f"Guesses: {guesses}")
    print(f"Arithmetic mean: {arith_mean:.4f}%")
    print(f"Geometric mean: {geo_mean:.4f}%")

    # Print log transformation table
    print_log_transformation()

    # Another example with non-zero guesses
    print("\n" + "-" * 50)
    guesses2 = {1.0: 10, 2.0: 5, 3.0: 2}  # Various guesses
    arith_mean2, geo_mean2 = calculate_means(guesses2)
    print(f"Guesses: {guesses2}")
    print(f"Arithmetic mean: {arith_mean2:.4f}%")
    print(f"Geometric mean: {geo_mean2:.4f}%")
