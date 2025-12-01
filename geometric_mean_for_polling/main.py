#!/usr/bin/env python3
"""
Main script to generate visualizations demonstrating the advantage of geometric mean
over arithmetic mean for polling data with outliers.

Example: Polling question "What percentage of the US budget is foreign aid?"
"""
import numpy as np
from geometric_mean_polling import calculate_geometric_mean, create_visualizations, generate_poll_responses


def main():
    """Generate synthetic poll data and create visualizations"""
    # Configuration
    n_responses = 150  # Number of poll responses
    true_value = 1.0  # Actual percentage (~1% of US budget is foreign aid)
    output_dir = './output'

    print("Generating Geometric Mean Polling Visualizations")
    print("=" * 50)
    print(f"Simulating {n_responses} poll responses")
    print(f"True value: {true_value}% of budget")
    print()

    # Generate synthetic poll responses
    print("Generating synthetic poll data...")
    responses = generate_poll_responses(n_responses, true_value)

    # Calculate statistics
    arithmetic_mean = np.mean(responses)
    geometric_mean = calculate_geometric_mean(responses)

    # Display statistics
    print("\nStatistics:")
    print(f"  True value:        {true_value:.2f}%")
    print(f"  Arithmetic mean:   {arithmetic_mean:.2f}%")
    print(f"  Geometric mean:    {geometric_mean:.2f}%")
    print()
    print(
        f"  Arithmetic error:  {abs(arithmetic_mean - true_value):.2f}% ({abs(arithmetic_mean - true_value) / true_value * 100:.1f}% relative)"
    )
    print(
        f"  Geometric error:   {abs(geometric_mean - true_value):.2f}% ({abs(geometric_mean - true_value) / true_value * 100:.1f}% relative)"
    )
    print()

    # Show key insight
    print("Key insight:")
    print("  Geometric mean = exp(mean(log(x)))")
    print("  This is equivalent to taking the arithmetic mean in log space,")
    print("  then transforming back - but without confusing poll respondents!")
    print()

    # Create visualizations
    print(f"Creating visualizations in '{output_dir}/'...")
    create_visualizations(responses, true_value, output_dir)

    print("\nVisualizations created successfully:")
    print(f"  1. {output_dir}/distribution_histogram.png")
    print(f"  2. {output_dir}/linear_scale_comparison.png")
    print(f"  3. {output_dir}/log_scale_transformation.png")
    print(f"  4. {output_dir}/outlier_sensitivity.png")
    print("\nDone!")


if __name__ == '__main__':
    main()
