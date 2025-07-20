"""
Unit tests for multi-omics data loader
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.data_processing.multi_omics_loader import (
    MultiOmicsDataLoader, DataType, IntegrationResult, DataQualityMetrics
)


class TestMultiOmicsDataLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.loader = MultiOmicsDataLoader()
        
        # Create test data
        np.random.seed(42)
        self.n_samples = 50
        self.n_genes = 100
        
        # Sample names
        self.sample_names = [f"SAMPLE_{i:03d}" for i in range(self.n_samples)]
        self.gene_names = [f"GENE_{i:03d}" for i in range(self.n_genes)]
        
        # Test RNA-seq data
        self.test_rna_data = pd.DataFrame(
            np.random.lognormal(mean=2, sigma=1, size=(self.n_samples, self.n_genes)),
            index=self.sample_names,
            columns=self.gene_names
        )
        
        # Test CNV data
        self.test_cnv_data = pd.DataFrame(
            np.random.normal(0, 0.5, size=(self.n_samples, self.n_genes)),
            index=self.sample_names,
            columns=self.gene_names
        )
        
        # Test mutation data
        self.test_mutation_data = pd.DataFrame(
            np.random.binomial(1, 0.1, size=(self.n_samples, self.n_genes)),
            index=self.sample_names,
            columns=self.gene_names
        )
        
        # Test methylation data
        self.test_methylation_data = pd.DataFrame(
            np.random.beta(2, 2, size=(self.n_samples, self.n_genes)),
            index=self.sample_names,
            columns=self.gene_names
        )
    
    def test_initialization(self):
        """Test loader initialization"""
        loader = MultiOmicsDataLoader()
        self.assertIsNotNone(loader.logger)
        self.assertEqual(loader.tcga_endpoint, "https://api.gdc.cancer.gov")
        self.assertEqual(loader.max_missing_rate, 0.3)
    
    def test_load_rna_seq_data_from_file(self):
        """Test loading RNA-seq data from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            self.test_rna_data.to_csv(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.loader.load_rna_seq_data(file_path=tmp_path)
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape[0], self.n_samples)
            self.assertGreater(result.shape[1], 0)  # Some genes might be filtered
            
            # Check if data is in datasets
            self.assertIn(DataType.RNA_SEQ.value, self.loader.datasets)
            
        finally:
            os.unlink(tmp_path)
    
    def test_load_cnv_data_from_file(self):
        """Test loading CNV data from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            self.test_cnv_data.to_csv(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.loader.load_cnv_data(file_path=tmp_path)
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape[0], self.n_samples)
            self.assertGreater(result.shape[1], 0)
            
            # Check if data is in datasets
            self.assertIn(DataType.CNV.value, self.loader.datasets)
            
        finally:
            os.unlink(tmp_path)
    
    def test_load_mutation_data_from_file(self):
        """Test loading mutation data from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            self.test_mutation_data.to_csv(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.loader.load_mutation_data(file_path=tmp_path)
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape[0], self.n_samples)
            self.assertGreater(result.shape[1], 0)
            
            # Check if data is in datasets
            self.assertIn(DataType.MUTATION.value, self.loader.datasets)
            
        finally:
            os.unlink(tmp_path)
    
    def test_load_methylation_data_from_file(self):
        """Test loading methylation data from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            self.test_methylation_data.to_csv(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.loader.load_methylation_data(file_path=tmp_path)
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape[0], self.n_samples)
            self.assertGreater(result.shape[1], 0)
            
            # Check if data is in datasets
            self.assertIn(DataType.METHYLATION.value, self.loader.datasets)
            
        finally:
            os.unlink(tmp_path)
    
    def test_load_tcga_simulated_data(self):
        """Test loading simulated TCGA data"""
        # Test RNA-seq
        rna_data = self.loader.load_rna_seq_data()
        self.assertIsInstance(rna_data, pd.DataFrame)
        self.assertEqual(rna_data.shape[0], 200)  # Default simulated sample count
        
        # Test CNV
        cnv_data = self.loader.load_cnv_data()
        self.assertIsInstance(cnv_data, pd.DataFrame)
        self.assertEqual(cnv_data.shape[0], 200)
        
        # Test mutation
        mutation_data = self.loader.load_mutation_data()
        self.assertIsInstance(mutation_data, pd.DataFrame)
        self.assertEqual(mutation_data.shape[0], 200)
        
        # Test methylation
        methylation_data = self.loader.load_methylation_data()
        self.assertIsInstance(methylation_data, pd.DataFrame)
        self.assertEqual(methylation_data.shape[0], 200)
    
    def test_preprocess_rna_seq(self):
        """Test RNA-seq preprocessing"""
        # Test with raw counts (should be log-transformed)
        raw_counts = pd.DataFrame(
            np.random.poisson(100, size=(50, 100)),
            index=[f"S{i}" for i in range(50)],
            columns=[f"G{i}" for i in range(100)]
        )
        
        processed = self.loader._preprocess_rna_seq(raw_counts)
        
        # Check if data is log-transformed
        self.assertLess(processed.max().max(), 20)  # Log2 values should be < 20
        
        # Check if low-variance genes are filtered
        self.assertLessEqual(processed.shape[1], raw_counts.shape[1])
    
    def test_preprocess_cnv(self):
        """Test CNV preprocessing"""
        processed = self.loader._preprocess_cnv(self.test_cnv_data)
        
        # Check if extreme values are clipped
        self.assertGreaterEqual(processed.min().min(), -3)
        self.assertLessEqual(processed.max().max(), 3)
    
    def test_preprocess_mutation(self):
        """Test mutation preprocessing"""
        processed = self.loader._preprocess_mutation(self.test_mutation_data)
        
        # Check if data is binary
        unique_values = set(processed.values.flatten())
        self.assertTrue(unique_values.issubset({0, 1}))
    
    def test_preprocess_methylation(self):
        """Test methylation preprocessing"""
        processed = self.loader._preprocess_methylation(self.test_methylation_data)
        
        # Check if values are between 0 and 1
        self.assertGreaterEqual(processed.min().min(), 0)
        self.assertLessEqual(processed.max().max(), 1)
    
    def test_find_common_samples(self):
        """Test finding common samples across datasets"""
        # Load test datasets
        self.loader.datasets = {
            DataType.RNA_SEQ.value: self.test_rna_data,
            DataType.CNV.value: self.test_cnv_data,
            DataType.MUTATION.value: self.test_mutation_data
        }
        
        common_samples = self.loader._find_common_samples(required_overlap=0.5)
        
        # All samples should be common since we used the same sample names
        self.assertEqual(len(common_samples), self.n_samples)
        self.assertEqual(set(common_samples), set(self.sample_names))
    
    def test_perform_quality_checks(self):
        """Test quality checks on integrated datasets"""
        datasets = {
            DataType.RNA_SEQ.value: self.test_rna_data,
            DataType.CNV.value: self.test_cnv_data
        }
        
        self.loader._perform_quality_checks(datasets)
        
        # Check if quality metrics are calculated
        self.assertIn(DataType.RNA_SEQ.value, self.loader.quality_metrics)
        self.assertIn(DataType.CNV.value, self.loader.quality_metrics)
        
        # Check quality metrics structure
        rna_metrics = self.loader.quality_metrics[DataType.RNA_SEQ.value]
        self.assertIsInstance(rna_metrics, DataQualityMetrics)
        self.assertEqual(rna_metrics.sample_count, self.n_samples)
        self.assertEqual(rna_metrics.feature_count, self.n_genes)
        self.assertIsInstance(rna_metrics.quality_score, float)
        self.assertGreaterEqual(rna_metrics.quality_score, 0)
        self.assertLessEqual(rna_metrics.quality_score, 1)
    
    def test_integrate_datasets(self):
        """Test dataset integration"""
        # Load test datasets
        self.loader.datasets = {
            DataType.RNA_SEQ.value: self.test_rna_data,
            DataType.CNV.value: self.test_cnv_data,
            DataType.MUTATION.value: self.test_mutation_data
        }
        
        result = self.loader.integrate_datasets()
        
        # Check integration result
        self.assertIsInstance(result, IntegrationResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        
        # Check integrated datasets
        self.assertEqual(len(result.datasets), 3)
        self.assertIn(DataType.RNA_SEQ.value, result.datasets)
        self.assertIn(DataType.CNV.value, result.datasets)
        self.assertIn(DataType.MUTATION.value, result.datasets)
        
        # Check that all datasets have the same samples
        sample_counts = [df.shape[0] for df in result.datasets.values()]
        self.assertEqual(len(set(sample_counts)), 1)  # All should be equal
    
    def test_calculate_integration_stats(self):
        """Test integration statistics calculation"""
        datasets = {
            DataType.RNA_SEQ.value: self.test_rna_data,
            DataType.CNV.value: self.test_cnv_data
        }
        
        stats = self.loader._calculate_integration_stats(datasets)
        
        # Check statistics structure
        self.assertIn('total_samples', stats)
        self.assertIn('data_types', stats)
        self.assertIn('feature_counts', stats)
        self.assertIn('total_features', stats)
        self.assertIn('integration_timestamp', stats)
        
        self.assertEqual(stats['total_samples'], self.n_samples)
        self.assertEqual(len(stats['data_types']), 2)
        self.assertEqual(stats['total_features'], self.n_genes * 2)
    
    def test_save_integration_result(self):
        """Test saving integration result"""
        # Create a minimal integration result
        result = IntegrationResult(
            datasets={DataType.RNA_SEQ.value: self.test_rna_data},
            sample_mapping={},
            feature_mapping={},
            quality_metrics={},
            integration_stats={'test': 'data'},
            success=True,
            errors=[]
        )
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.loader.save_integration_result(result, tmp_dir)
            
            # Check if files are created
            output_path = Path(tmp_dir)
            self.assertTrue((output_path / f"{DataType.RNA_SEQ.value}_integrated.csv").exists())
            self.assertTrue((output_path / "integration_metadata.json").exists())
    
    def test_get_integration_summary(self):
        """Test integration summary generation"""
        # Load test datasets
        self.loader.datasets = {
            DataType.RNA_SEQ.value: self.test_rna_data,
            DataType.CNV.value: self.test_cnv_data
        }
        
        # Add some quality metrics
        self.loader.quality_metrics = {
            DataType.RNA_SEQ.value: DataQualityMetrics(
                sample_count=self.n_samples,
                feature_count=self.n_genes,
                missing_rate=0.1,
                duplicates_count=0,
                outliers_count=5,
                data_range=(0.0, 10.0),
                quality_score=0.8,
                issues=[]
            )
        }
        
        summary = self.loader.get_integration_summary()
        
        # Check summary structure
        self.assertIn('loaded_datasets', summary)
        self.assertIn('dataset_shapes', summary)
        self.assertIn('quality_metrics', summary)
        
        self.assertEqual(len(summary['loaded_datasets']), 2)
        self.assertEqual(len(summary['dataset_shapes']), 2)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test with non-existent file
        with self.assertRaises(Exception):
            self.loader.load_rna_seq_data(file_path="/non/existent/path.csv")
        
        # Test integration with no datasets
        result = self.loader.integrate_datasets()
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_unsupported_file_format(self):
        """Test handling of unsupported file formats"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("unsupported format")
            tmp_path = tmp.name
        
        try:
            result = self.loader._load_local_file(tmp_path)
            self.assertIsNone(result)
        finally:
            os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()