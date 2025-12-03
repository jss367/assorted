"""Visualization showing geometric mean advantage for polling data"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def generate_poll_responses(n_responses, true_value):
    """Generate synthetic poll responses with realistic distribution

    Args:
        n_responses: Number of poll responses to generate
        true_value: The actual correct percentage (e.g., 1.0 for 1%)

    Returns:
        Array of poll responses (percentages)
    """
    np.random.seed(42)  # For reproducibility

    # Add some clear outliers (15-50%)
    n_outliers = int(n_responses * 0.15)

    # Most responses centered around 2-3% with log-normal distribution
    n_main = n_responses - n_outliers
    main_responses = np.random.lognormal(mean=0.8, sigma=0.6, size=n_main)

    outliers = np.random.uniform(15, 50, size=n_outliers)

    # Combine and shuffle
    all_responses = np.concatenate([main_responses, outliers])
    np.random.shuffle(all_responses)

    return all_responses


def calculate_geometric_mean(data):
    """Calculate geometric mean using exp(mean(log(x)))

    Args:
        data: Array of positive numbers

    Returns:
        Geometric mean of the data
    """
    return np.exp(np.mean(np.log(data)))


def create_visualizations(responses, true_value, output_dir='.'):
    """Create visualizations showing geometric vs arithmetic mean

    Args:
        responses: Array of poll responses
        true_value: The actual correct value
        output_dir: Directory to save visualization files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    arithmetic_mean = np.mean(responses)
    geometric_mean = calculate_geometric_mean(responses)

    # 1. Distribution histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(responses, bins=30, alpha=0.7, edgecolor='black')
    # ax.axvline(true_value, color='green', linestyle='--', linewidth=2, label=f'True Value ({true_value}%)')
    ax.axvline(
        arithmetic_mean, color='red', linestyle='--', linewidth=2, label=f'Arithmetic Mean ({arithmetic_mean:.2f}%)'
    )
    # ax.axvline(
    #     geometric_mean, color='blue', linestyle='--', linewidth=2, label=f'Geometric Mean ({geometric_mean:.2f}%)'
    # )
    ax.set_xlabel('Poll Response (% of budget)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Poll Responses: Foreign Aid % of US Budget', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / 'distribution_histogram.png', dpi=150)
    plt.close()

    # 2. Histogram with geometric mean
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(responses, bins=30, alpha=0.7, edgecolor='black')
    # ax.axvline(true_value, color='green', linestyle='--', linewidth=2, label=f'True Value ({true_value}%)')
    ax.axvline(
        arithmetic_mean, color='red', linestyle='--', linewidth=2, label=f'Arithmetic Mean ({arithmetic_mean:.2f}%)'
    )
    ax.axvline(
        geometric_mean, color='blue', linestyle='--', linewidth=2, label=f'Geometric Mean ({geometric_mean:.2f}%)'
    )
    ax.set_xlabel('Poll Response (% of budget)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Poll Responses: Foreign Aid % of US Budget', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / 'distribution_histogram_geometric_mean.png', dpi=150)
    plt.close()

    # 3. Log-scale transformation
    log_responses = np.log(responses)
    log_mean = np.mean(log_responses)  # This is mean(log(x))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(log_responses, bins=30, alpha=0.7, edgecolor='black', color='lightcoral')
    ax.axvline(log_mean, color='purple', linestyle='--', linewidth=2, label=f'Mean in Log Space = log(Geometric Mean)')
    ax.set_xlabel('log(Response Value)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Log-Scale Transformation: Demonstrating exp(mean(log(x)))', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.text(
        0.05,
        0.95,
        f'exp(mean(log(x))) = {np.exp(log_mean):.2f}%\n= Geometric Mean',
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
    )
    plt.tight_layout()
    plt.savefig(output_path / 'log_scale_transformation.png', dpi=150)
    plt.close()

    # 4. Outlier sensitivity analysis
    # Remove the largest value and recalculate
    sorted_responses = np.sort(responses)
    responses_no_outlier = sorted_responses[:-1]

    arith_mean_with = arithmetic_mean
    geo_mean_with = geometric_mean
    arith_mean_without = np.mean(responses_no_outlier)
    geo_mean_without = calculate_geometric_mean(responses_no_outlier)

    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['With Highest\nOutlier', 'Without Highest\nOutlier']
    arith_means = [arith_mean_with, arith_mean_without]
    geo_means = [geo_mean_with, geo_mean_without]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax.bar(x - width / 2, arith_means, width, label='Arithmetic Mean', color='red', alpha=0.7)
    bars2 = ax.bar(x + width / 2, geo_means, width, label='Geometric Mean', color='blue', alpha=0.7)

    ax.axhline(true_value, color='green', linestyle='--', linewidth=2, label=f'True Value ({true_value}%)', alpha=0.7)
    ax.set_ylabel('Mean Value (%)', fontsize=12)
    ax.set_title('Sensitivity to Outliers: Arithmetic vs Geometric Mean', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}%', ha='center', va='bottom', fontsize=9)

    # Add change percentages
    arith_change = abs(arith_mean_with - arith_mean_without) / arith_mean_with * 100
    geo_change = abs(geo_mean_with - geo_mean_without) / geo_mean_with * 100
    ax.text(
        0.02,
        0.98,
        f'Arithmetic mean change: {arith_change:.1f}%\nGeometric mean change: {geo_change:.1f}%',
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
    )

    plt.tight_layout()
    plt.savefig(output_path / 'outlier_sensitivity.png', dpi=150)
    plt.close()
