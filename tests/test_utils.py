"""
Unit tests for common utilities
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add src to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from utils.common import PathManager, ConfigManager, DataGenerator

class TestPathManager(unittest.TestCase):
    """Test PathManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.path_manager = PathManager()
        
    def test_get_data_path(self):
        """Test data path generation"""
        path = self.path_manager.get_data_path('raw', 'test.csv')
        self.assertTrue(str(path).endswith('data/raw/test.csv'))
        
    def test_get_results_path(self):
        """Test results path generation"""
        path = self.path_manager.get_results_path('tables', 'test.csv')
        self.assertTrue(str(path).endswith('results/tables/test.csv'))

class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_manager = ConfigManager()
        
    def test_get_default_values(self):
        """Test default configuration values"""
        p_value = self.config_manager.get('P_VALUE_THRESHOLD', 0.05)
        self.assertIsInstance(p_value, float)
        self.assertGreater(p_value, 0)
        self.assertLess(p_value, 1)

class TestDataGenerator(unittest.TestCase):
    """Test DataGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_generator = DataGenerator()
        
    def test_generate_clinical_data(self):
        """Test clinical data generation"""
        clinical_data = self.data_generator.generate_clinical_data(n_samples=100)
        
        # Check basic properties
        self.assertIsInstance(clinical_data, pd.DataFrame)
        self.assertEqual(len(clinical_data), 100)
        
        # Check required columns
        required_columns = ['sample_id', 'os_time', 'os_status', 'age', 'gender', 'stage']
        for col in required_columns:
            self.assertIn(col, clinical_data.columns)
            
        # Check data types and ranges
        self.assertTrue(clinical_data['os_time'].dtype in [np.int64, np.float64])
        self.assertTrue(clinical_data['os_status'].isin([0, 1]).all())
        self.assertTrue(clinical_data['age'].between(18, 90).all())
        self.assertTrue(clinical_data['gender'].isin(['Male', 'Female']).all())
        
    def test_generate_expression_data(self):
        """Test expression data generation"""
        expression_data = self.data_generator.generate_expression_data(
            n_genes=1000, n_samples=100
        )
        
        # Check basic properties
        self.assertIsInstance(expression_data, pd.DataFrame)
        self.assertEqual(expression_data.shape, (1000, 101))  # +1 for gene_id column
        
        # Check gene_id column exists
        self.assertIn('gene_id', expression_data.columns)
        
        # Check expression values are reasonable
        expr_values = expression_data.select_dtypes(include=[np.number])
        self.assertTrue((expr_values >= 0).all().all())
        
    def test_generate_mutation_data(self):
        """Test mutation data generation"""
        mutation_data = self.data_generator.generate_mutation_data(
            n_samples=100, n_genes=50
        )
        
        # Check basic properties
        self.assertIsInstance(mutation_data, pd.DataFrame)
        self.assertGreater(len(mutation_data), 0)
        
        # Check required columns
        required_columns = ['sample_id', 'gene_id', 'mutation_type', 'amino_acid_change']
        for col in required_columns:
            self.assertIn(col, mutation_data.columns)
            
        # Check mutation types are valid
        valid_types = ['missense', 'nonsense', 'silent', 'frameshift']
        self.assertTrue(mutation_data['mutation_type'].isin(valid_types).all())

class TestDataIntegration(unittest.TestCase):
    """Test data integration across components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_generator = DataGenerator()
        
    def test_sample_consistency(self):
        """Test sample ID consistency across datasets"""
        n_samples = 50
        
        # Generate datasets
        clinical_data = self.data_generator.generate_clinical_data(n_samples)
        expression_data = self.data_generator.generate_expression_data(100, n_samples)
        mutation_data = self.data_generator.generate_mutation_data(n_samples, 20)
        
        # Extract sample IDs
        clinical_samples = set(clinical_data['sample_id'])
        expression_samples = set(expression_data.columns[1:])  # Skip gene_id column
        mutation_samples = set(mutation_data['sample_id'].unique())
        
        # Check overlap
        self.assertGreater(len(clinical_samples & expression_samples), 0)
        self.assertGreater(len(clinical_samples & mutation_samples), 0)

if __name__ == '__main__':
    unittest.main()