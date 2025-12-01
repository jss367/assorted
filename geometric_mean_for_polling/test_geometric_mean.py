"""Tests for geometric mean polling visualization"""
import pytest
import numpy as np
import os
from pathlib import Path
from geometric_mean_polling import generate_poll_responses, calculate_geometric_mean, create_visualizations


class TestDataGeneration:
    def test_generate_poll_responses_returns_correct_count(self):
        """Generate poll responses returns specified number of responses"""
        n_responses = 150
        true_value = 1.0

        responses = generate_poll_responses(n_responses, true_value)

        assert len(responses) == n_responses

    def test_generate_poll_responses_contains_outliers(self):
        """Generate poll responses includes some high outliers"""
        n_responses = 150
        true_value = 1.0

        responses = generate_poll_responses(n_responses, true_value)

        # Should have at least some responses > 15% (clear outliers)
        outliers = [r for r in responses if r > 15]
        assert len(outliers) > 0
        assert len(outliers) < n_responses * 0.2  # But not too many

    def test_generate_poll_responses_mostly_reasonable(self):
        """Generate poll responses has most values in reasonable range"""
        n_responses = 150
        true_value = 1.0

        responses = generate_poll_responses(n_responses, true_value)

        # Most responses should be between 0.5% and 10%
        reasonable = [r for r in responses if 0.5 <= r <= 10]
        assert len(reasonable) > n_responses * 0.7  # At least 70%


class TestGeometricMean:
    def test_calculate_geometric_mean_simple_values(self):
        """Geometric mean of simple values is correct"""
        data = np.array([1, 2, 4, 8])

        result = calculate_geometric_mean(data)

        # Geometric mean of 1,2,4,8 is (1*2*4*8)^(1/4) = 64^0.25 = 2.828...
        expected = (1 * 2 * 4 * 8) ** 0.25
        assert np.isclose(result, expected, rtol=1e-10)

    def test_calculate_geometric_mean_equals_exp_mean_log(self):
        """Geometric mean equals exp(mean(log(x))) - the key insight"""
        data = np.array([1.5, 2.3, 5.7, 12.4, 25.6])

        geometric_mean = calculate_geometric_mean(data)
        exp_mean_log = np.exp(np.mean(np.log(data)))

        assert np.isclose(geometric_mean, exp_mean_log, rtol=1e-10)

    def test_calculate_geometric_mean_less_sensitive_to_outliers(self):
        """Geometric mean is less sensitive to outliers than arithmetic mean"""
        data_without_outlier = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
        data_with_outlier = np.array([1.0, 1.5, 2.0, 2.5, 100.0])

        geo_mean_without = calculate_geometric_mean(data_without_outlier)
        geo_mean_with = calculate_geometric_mean(data_with_outlier)

        arith_mean_without = np.mean(data_without_outlier)
        arith_mean_with = np.mean(data_with_outlier)

        # Geometric mean should change proportionally less than arithmetic mean
        geo_change = (geo_mean_with - geo_mean_without) / geo_mean_without
        arith_change = (arith_mean_with - arith_mean_without) / arith_mean_without

        assert geo_change < arith_change


class TestVisualization:
    def test_create_visualizations_runs_without_error(self, tmp_path):
        """Visualization function runs without error"""
        responses = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 20.0, 30.0])
        true_value = 1.0
        output_dir = str(tmp_path)

        # Should not raise any exceptions
        create_visualizations(responses, true_value, output_dir)

    def test_create_visualizations_creates_files(self, tmp_path):
        """Visualization function creates expected output files"""
        responses = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 20.0, 30.0])
        true_value = 1.0
        output_dir = str(tmp_path)

        create_visualizations(responses, true_value, output_dir)

        # Check that files were created
        expected_files = [
            'distribution_histogram.png',
            'linear_scale_comparison.png',
            'log_scale_transformation.png',
            'outlier_sensitivity.png'
        ]

        for filename in expected_files:
            filepath = tmp_path / filename
            assert filepath.exists(), f"{filename} was not created"
