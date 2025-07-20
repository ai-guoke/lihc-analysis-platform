"""
Unit tests for analysis modules
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys
import warnings
warnings.filterwarnings('ignore')

# Add src to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from analysis.stage1_multidimensional import MultidimensionalAnalyzer
from utils.common import DataGenerator

class TestMultidimensionalAnalyzer(unittest.TestCase):
    """Test MultidimensionalAnalyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = MultidimensionalAnalyzer()
        self.data_generator = DataGenerator()
        
        # Generate test data
        self.clinical_data = self.data_generator.generate_clinical_data(100)
        self.expression_data = self.data_generator.generate_expression_data(200, 100)
        self.mutation_data = self.data_generator.generate_mutation_data(100, 50)
        
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsInstance(self.analyzer, MultidimensionalAnalyzer)
        self.assertIsNotNone(self.analyzer.path_manager)
        self.assertIsNotNone(self.analyzer.config_manager)
        
    def test_data_loading(self):
        """Test data loading functionality"""
        # This would test the load_data method if it exists
        # For now, we'll test basic data validation
        self.assertIsInstance(self.clinical_data, pd.DataFrame)
        self.assertIsInstance(self.expression_data, pd.DataFrame)
        self.assertIsInstance(self.mutation_data, pd.DataFrame)
        
    def test_survival_analysis_input_validation(self):
        """Test survival analysis input validation"""
        # Test with valid data
        self.assertIn('os_time', self.clinical_data.columns)
        self.assertIn('os_status', self.clinical_data.columns)
        
        # Test data types
        self.assertTrue(self.clinical_data['os_time'].dtype in [np.int64, np.float64])
        self.assertTrue(self.clinical_data['os_status'].isin([0, 1]).all())
        
    def test_expression_data_format(self):
        """Test expression data format validation"""
        # Check basic format
        self.assertIn('gene_id', self.expression_data.columns)
        self.assertGreater(len(self.expression_data), 0)
        
        # Check expression values
        expr_cols = [col for col in self.expression_data.columns if col != 'gene_id']
        self.assertGreater(len(expr_cols), 0)
        
        # Check for reasonable expression values
        expr_values = self.expression_data[expr_cols].values
        self.assertTrue(np.all(expr_values >= 0))

class TestAnalysisWorkflow(unittest.TestCase):
    """Test complete analysis workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_generator = DataGenerator()
        
    def test_data_generation_pipeline(self):
        """Test complete data generation pipeline"""
        n_samples = 50
        n_genes = 100
        
        # Generate all data types
        clinical_data = self.data_generator.generate_clinical_data(n_samples)
        expression_data = self.data_generator.generate_expression_data(n_genes, n_samples)
        mutation_data = self.data_generator.generate_mutation_data(n_samples, 20)
        
        # Test data consistency
        self.assertEqual(len(clinical_data), n_samples)
        self.assertEqual(len(expression_data), n_genes)
        self.assertEqual(expression_data.shape[1], n_samples + 1)  # +1 for gene_id
        
        # Test sample ID consistency
        clinical_samples = set(clinical_data['sample_id'])
        expression_samples = set(expression_data.columns[1:])
        
        # Should have some overlap
        overlap = clinical_samples & expression_samples
        self.assertGreater(len(overlap), 0)

if __name__ == '__main__':
    unittest.main()