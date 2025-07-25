"""
Integration tests for Multi-omics Data Integration
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator


class TestMultiOmicsIntegration:
    """Test suite for multi-omics data integration"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_expression_data(self, temp_data_dir):
        """Generate sample expression data"""
        n_genes = 100
        n_samples = 50
        data = pd.DataFrame(
            np.random.lognormal(3, 1, (n_genes, n_samples)),
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
        file_path = Path(temp_data_dir) / "expression.csv"
        data.to_csv(file_path)
        return file_path
    
    @pytest.fixture
    def sample_cnv_data(self, temp_data_dir):
        """Generate sample CNV data"""
        n_genes = 80
        n_samples = 50
        data = pd.DataFrame(
            np.random.normal(0, 0.5, (n_genes, n_samples)),
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
        file_path = Path(temp_data_dir) / "cnv.csv"
        data.to_csv(file_path)
        return file_path
    
    @pytest.fixture
    def sample_mutation_data(self, temp_data_dir):
        """Generate sample mutation data"""
        records = []
        genes = [f"Gene_{i:03d}" for i in range(60)]
        samples = [f"Sample_{i:02d}" for i in range(50)]
        
        for gene in genes:
            # Each gene mutated in 5-20% of samples
            n_mutations = np.random.randint(3, 10)
            mutated_samples = np.random.choice(samples, n_mutations, replace=False)
            
            for sample in mutated_samples:
                records.append({
                    'gene_id': gene,
                    'sample_id': sample,
                    'mutation_type': np.random.choice(['missense', 'nonsense'])
                })
        
        data = pd.DataFrame(records)
        file_path = Path(temp_data_dir) / "mutations.csv"
        data.to_csv(file_path, index=False)
        return file_path
    
    @pytest.fixture
    def sample_methylation_data(self, temp_data_dir):
        """Generate sample methylation data"""
        n_probes = 120
        n_samples = 50
        data = pd.DataFrame(
            np.random.beta(2, 5, (n_probes, n_samples)),
            index=[f"cg{i:08d}" for i in range(n_probes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
        file_path = Path(temp_data_dir) / "methylation.csv"
        data.to_csv(file_path)
        return file_path
    
    def test_data_loading(self, temp_data_dir, sample_expression_data, 
                         sample_cnv_data, sample_mutation_data, sample_methylation_data):
        """Test loading different omics data types"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Test expression data loading
        expr_data = integrator.load_expression_data(sample_expression_data)
        assert isinstance(expr_data, pd.DataFrame)
        assert expr_data.shape[1] == 50  # n_samples
        assert 'expression' in integrator.omics_data
        
        # Test CNV data loading
        cnv_data = integrator.load_cnv_data(sample_cnv_data)
        assert isinstance(cnv_data, pd.DataFrame)
        assert cnv_data.shape[1] == 50
        assert 'cnv' in integrator.omics_data
        assert cnv_data.isin([-2, -1, 0, 1, 2]).all().all()  # Check categorization
        
        # Test mutation data loading
        mut_data = integrator.load_mutation_data(sample_mutation_data)
        assert isinstance(mut_data, pd.DataFrame)
        assert mut_data.shape[1] == 50
        assert 'mutation' in integrator.omics_data
        assert mut_data.isin([0, 1]).all().all()  # Binary matrix
        
        # Test methylation data loading
        meth_data = integrator.load_methylation_data(sample_methylation_data)
        assert isinstance(meth_data, pd.DataFrame)
        assert meth_data.shape[1] == 50
        assert 'methylation' in integrator.omics_data
        assert (meth_data >= 0).all().all() and (meth_data <= 1).all().all()
    
    def test_concatenate_integration(self, temp_data_dir, sample_expression_data, 
                                    sample_cnv_data, sample_mutation_data):
        """Test concatenate integration method"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Load data
        integrator.load_expression_data(sample_expression_data)
        integrator.load_cnv_data(sample_cnv_data)
        integrator.load_mutation_data(sample_mutation_data)
        
        # Integrate
        integrated = integrator.integrate_omics(integration_method="concatenate")
        
        assert isinstance(integrated, pd.DataFrame)
        assert integrated.shape[1] == 50  # All samples
        
        # Check feature prefixes
        assert any(idx.startswith("expression_") for idx in integrated.index)
        assert any(idx.startswith("cnv_") for idx in integrated.index)
        assert any(idx.startswith("mutation_") for idx in integrated.index)
        
        # Check feature info is created
        assert hasattr(integrator, 'feature_info')
        assert set(integrator.feature_info['omics_type']) == {'expression', 'cnv', 'mutation'}
    
    def test_similarity_network_fusion(self, temp_data_dir, sample_expression_data, 
                                     sample_cnv_data):
        """Test SNF integration method"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Load data
        integrator.load_expression_data(sample_expression_data)
        integrator.load_cnv_data(sample_cnv_data)
        
        # Integrate using SNF
        integrated = integrator.integrate_omics(integration_method="similarity_network")
        
        assert isinstance(integrated, pd.DataFrame)
        assert integrated.shape[1] == 50  # All samples
        assert all(idx.startswith("SNF_PC") for idx in integrated.index)
    
    def test_mofa_integration(self, temp_data_dir, sample_expression_data, 
                            sample_cnv_data, sample_mutation_data):
        """Test MOFA-style integration"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Load data
        integrator.load_expression_data(sample_expression_data)
        integrator.load_cnv_data(sample_cnv_data)
        integrator.load_mutation_data(sample_mutation_data)
        
        # Integrate using MOFA
        integrated = integrator.integrate_omics(integration_method="mofa")
        
        assert isinstance(integrated, pd.DataFrame)
        assert integrated.shape[1] == 50  # All samples
        assert all(idx.startswith("MOFA_Factor") for idx in integrated.index)
        assert integrated.shape[0] == 30  # Number of factors
    
    def test_feature_importance(self, temp_data_dir, sample_expression_data, 
                               sample_cnv_data):
        """Test feature importance calculation"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Load and integrate data
        integrator.load_expression_data(sample_expression_data)
        integrator.load_cnv_data(sample_cnv_data)
        integrated = integrator.integrate_omics()
        
        # Create target variable
        target = pd.Series(
            np.random.rand(50),
            index=[f"Sample_{i:02d}" for i in range(50)]
        )
        
        # Calculate importance
        importance = integrator.calculate_feature_importance(target)
        
        assert isinstance(importance, pd.DataFrame)
        assert 'rf_importance' in importance.columns
        assert 'mi_importance' in importance.columns
        assert 'combined_importance' in importance.columns
        assert len(importance) == len(integrated)
    
    def test_save_integrated_data(self, temp_data_dir, sample_expression_data, 
                                 sample_cnv_data):
        """Test saving integrated data"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Load and integrate
        integrator.load_expression_data(sample_expression_data)
        integrator.load_cnv_data(sample_cnv_data)
        integrated = integrator.integrate_omics()
        
        # Save
        output_dir = Path(temp_data_dir) / "output"
        integrator.save_integrated_data(str(output_dir))
        
        # Check files exist
        assert (output_dir / "integrated_features.csv").exists()
        assert (output_dir / "feature_info.csv").exists()
        assert (output_dir / "expression_processed.csv").exists()
        assert (output_dir / "cnv_processed.csv").exists()
    
    def test_empty_data_handling(self, temp_data_dir):
        """Test handling of empty or missing data"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Try to integrate without loading data
        with pytest.raises(Exception):
            integrator.integrate_omics()
    
    def test_mismatched_samples(self, temp_data_dir):
        """Test handling of mismatched sample names"""
        integrator = MultiOmicsIntegrator(temp_data_dir)
        
        # Create data with different samples
        expr_data = pd.DataFrame(
            np.random.rand(10, 5),
            columns=[f"Sample_A{i}" for i in range(5)]
        )
        cnv_data = pd.DataFrame(
            np.random.rand(10, 5),
            columns=[f"Sample_B{i}" for i in range(5)]
        )
        
        # Save to files
        expr_file = Path(temp_data_dir) / "expr_mismatch.csv"
        cnv_file = Path(temp_data_dir) / "cnv_mismatch.csv"
        expr_data.to_csv(expr_file)
        cnv_data.to_csv(cnv_file)
        
        # Load data
        integrator.load_expression_data(expr_file)
        integrator.load_cnv_data(cnv_file)
        
        # Should handle gracefully (no common samples)
        integrated = integrator.integrate_omics()
        assert integrated.shape[1] == 0  # No common samples