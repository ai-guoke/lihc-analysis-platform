"""
Integration tests for Integrated Analysis Pipeline
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import os

from src.analysis.integrated_analysis import IntegratedAnalysisPipeline
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer


class TestIntegratedAnalysis:
    """Test suite for integrated multi-omics and ClosedLoop analysis"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for data and results"""
        data_dir = tempfile.mkdtemp()
        results_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        (Path(data_dir) / "raw").mkdir()
        (Path(data_dir) / "processed").mkdir()
        
        yield data_dir, results_dir
        
        # Cleanup
        shutil.rmtree(data_dir)
        shutil.rmtree(results_dir)
    
    @pytest.fixture
    def sample_data_files(self, temp_dirs):
        """Generate sample data files"""
        data_dir, _ = temp_dirs
        raw_dir = Path(data_dir) / "raw"
        
        n_genes = 200
        n_samples = 100
        sample_names = [f"Sample_{i:03d}" for i in range(n_samples)]
        gene_names = [f"Gene_{i:04d}" for i in range(n_genes)]
        
        # Expression data
        expr_data = pd.DataFrame(
            np.random.lognormal(3, 1, (n_genes, n_samples)),
            index=gene_names,
            columns=sample_names
        )
        expr_file = raw_dir / "expression.csv"
        expr_data.to_csv(expr_file)
        
        # CNV data
        cnv_data = pd.DataFrame(
            np.random.normal(0, 0.5, (150, n_samples)),
            index=gene_names[:150],
            columns=sample_names
        )
        cnv_file = raw_dir / "cnv.csv"
        cnv_data.to_csv(cnv_file)
        
        # Mutation data
        mut_records = []
        for i in range(100):
            gene = gene_names[i]
            n_mutations = np.random.randint(5, 20)
            mutated_samples = np.random.choice(sample_names, n_mutations, replace=False)
            
            for sample in mutated_samples:
                mut_records.append({
                    'gene_id': gene,
                    'sample_id': sample,
                    'mutation_type': np.random.choice(['missense', 'nonsense'])
                })
        
        mut_data = pd.DataFrame(mut_records)
        mut_file = raw_dir / "mutations.csv"
        mut_data.to_csv(mut_file, index=False)
        
        # Methylation data
        meth_data = pd.DataFrame(
            np.random.beta(2, 5, (120, n_samples)),
            index=[f"cg{i:08d}" for i in range(120)],
            columns=sample_names
        )
        # Map probes to genes (simplified)
        meth_data.index = gene_names[:120]
        meth_file = raw_dir / "methylation.csv"
        meth_data.to_csv(meth_file)
        
        # Clinical data
        clinical_data = pd.DataFrame({
            'survival_time': np.random.exponential(1000, n_samples),
            'survival_status': np.random.binomial(1, 0.3, n_samples),
            'age': np.random.normal(60, 10, n_samples),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples)
        }, index=sample_names)
        clinical_file = raw_dir / "clinical.csv"
        clinical_data.to_csv(clinical_file)
        
        return {
            'expression': str(expr_file),
            'cnv': str(cnv_file),
            'mutation': str(mut_file),
            'methylation': str(meth_file),
            'clinical': str(clinical_file)
        }
    
    @pytest.fixture
    def pipeline(self, temp_dirs):
        """Create integrated analysis pipeline"""
        data_dir, results_dir = temp_dirs
        return IntegratedAnalysisPipeline(data_dir, results_dir)
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert hasattr(pipeline, 'multi_omics')
        assert hasattr(pipeline, 'closedloop')
        assert hasattr(pipeline, 'stage1')
        assert hasattr(pipeline, 'stage2')
        assert hasattr(pipeline, 'stage3')
        assert isinstance(pipeline.multi_omics, MultiOmicsIntegrator)
        assert isinstance(pipeline.closedloop, ClosedLoopAnalyzer)
    
    def test_multi_omics_data_loading(self, pipeline, sample_data_files):
        """Test loading and integrating multi-omics data"""
        integrated = pipeline._load_and_integrate_omics(
            sample_data_files['expression'],
            sample_data_files['cnv'],
            sample_data_files['mutation'],
            sample_data_files['methylation']
        )
        
        assert isinstance(integrated, pd.DataFrame)
        assert integrated.shape[1] == 100  # n_samples
        assert len(pipeline.multi_omics.omics_data) == 4  # All omics types loaded
    
    def test_closedloop_analysis(self, pipeline, sample_data_files):
        """Test ClosedLoop causal analysis integration"""
        # Load data first
        pipeline._load_and_integrate_omics(
            sample_data_files['expression'],
            sample_data_files['cnv'],
            sample_data_files['mutation'],
            sample_data_files['methylation']
        )
        
        # Run ClosedLoop analysis
        closedloop_results = pipeline._run_closedloop_analysis(
            sample_data_files['clinical']
        )
        
        assert isinstance(closedloop_results, dict)
        assert 'closedloop_scores' in closedloop_results
        assert 'evidence_report' in closedloop_results
        assert 'causal_network' in closedloop_results
    
    def test_classic_analysis_integration(self, pipeline, sample_data_files):
        """Test classic three-stage analysis with integrated data"""
        # Load data first
        pipeline._load_and_integrate_omics(
            sample_data_files['expression'],
            sample_data_files['cnv'],
            sample_data_files['mutation'],
            None  # Skip methylation
        )
        
        # Run classic analysis
        classic_results = pipeline._run_classic_analysis_integrated()
        
        assert isinstance(classic_results, dict)
        assert 'stage1' in classic_results
        assert 'stage2' in classic_results
        assert 'stage3' in classic_results
    
    def test_results_integration(self, pipeline):
        """Test integration of all analysis results"""
        # Create mock results
        closedloop_scores = pd.DataFrame({
            'closedloop_score': [0.9, 0.8, 0.7],
            'gene_id': ['Gene_001', 'Gene_002', 'Gene_003']
        }).set_index('gene_id')
        
        linchpin_scores = pd.DataFrame({
            'linchpin_score': [0.85, 0.75, 0.65],
            'gene_id': ['Gene_001', 'Gene_002', 'Gene_004']
        }).set_index('gene_id')
        
        closedloop_results = {
            'closedloop_scores': closedloop_scores
        }
        
        classic_results = {
            'stage3': {'linchpin_scores': linchpin_scores}
        }
        
        # Integrate results
        final_results = pipeline._integrate_all_results(
            closedloop_results, classic_results
        )
        
        assert 'integrated_scores' in final_results
        assert 'top_targets' in final_results
        
        # Check only common genes are included
        integrated = final_results['integrated_scores']
        assert len(integrated) == 2  # Gene_001 and Gene_002
        assert 'Gene_004' not in integrated.index
    
    def test_full_integrated_analysis(self, pipeline, sample_data_files):
        """Test complete integrated analysis pipeline"""
        results = pipeline.run_integrated_analysis(
            expression_file=sample_data_files['expression'],
            cnv_file=sample_data_files['cnv'],
            mutation_file=sample_data_files['mutation'],
            methylation_file=sample_data_files['methylation'],
            clinical_file=sample_data_files['clinical']
        )
        
        assert isinstance(results, dict)
        assert 'integrated_scores' in results
        assert 'top_targets' in results
        
        # Check report generation
        report_dir = pipeline.results_dir / "integrated_report"
        assert report_dir.exists()
        assert (report_dir / "integrated_target_scores.csv").exists()
        assert (report_dir / "integrated_analysis_report.html").exists()
    
    def test_evidence_chain_extraction(self, pipeline):
        """Test evidence chain extraction for genes"""
        # Create mock evidence chain
        from src.analysis.closedloop_analyzer import EvidenceScore, EvidenceType
        
        pipeline.closedloop.evidence_chains = {
            'Gene_001': [
                EvidenceScore(
                    gene_id='Gene_001',
                    evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                    score=0.8,
                    p_value=0.001,
                    effect_size=1.2,
                    confidence=0.9,
                    metadata={}
                )
            ]
        }
        
        evidence_chain = pipeline._get_evidence_chain('Gene_001', {})
        
        assert isinstance(evidence_chain, list)
        assert len(evidence_chain) == 1
        assert evidence_chain[0]['type'] == EvidenceType.DIFFERENTIAL_EXPRESSION
        assert evidence_chain[0]['score'] == 0.8
    
    def test_multiomics_profile_extraction(self, pipeline, sample_data_files):
        """Test multi-omics profile extraction for genes"""
        # Load data
        pipeline._load_and_integrate_omics(
            sample_data_files['expression'],
            sample_data_files['cnv'],
            None,
            None
        )
        
        # Get profile for first gene
        gene = 'Gene_0000'
        profile = pipeline._get_multiomics_profile(gene)
        
        assert isinstance(profile, dict)
        assert 'expression' in profile
        assert 'cnv' in profile
        
        for omics_type, stats in profile.items():
            assert 'mean' in stats
            assert 'std' in stats
            assert 'min' in stats
            assert 'max' in stats
    
    def test_html_report_generation(self, pipeline, temp_dirs):
        """Test HTML report generation"""
        _, results_dir = temp_dirs
        report_dir = Path(results_dir) / "test_report"
        report_dir.mkdir()
        
        # Create test results
        results = {
            'integrated_scores': pd.DataFrame({
                'integrated_score': [0.9, 0.8],
                'closedloop_score': [0.85, 0.75],
                'linchpin_score': [0.95, 0.85]
            }, index=['Gene_001', 'Gene_002']),
            'top_targets': [
                {
                    'gene': 'Gene_001',
                    'integrated_score': 0.9,
                    'closedloop_score': 0.85,
                    'linchpin_score': 0.95,
                    'evidence_chain': []
                }
            ]
        }
        
        pipeline._create_html_report(results, report_dir)
        
        html_file = report_dir / "integrated_analysis_report.html"
        assert html_file.exists()
        
        # Check HTML content
        content = html_file.read_text()
        assert "LIHC Integrated Multi-omics Analysis Report" in content
        assert "Gene_001" in content
        assert "0.900" in content  # integrated score
    
    def test_demo_clinical_data_generation(self, pipeline):
        """Test demo clinical data generation"""
        clinical_data = pipeline._generate_demo_clinical_data()
        
        assert isinstance(clinical_data, pd.DataFrame)
        assert len(clinical_data) == 100
        assert 'survival_time' in clinical_data.columns
        assert 'survival_status' in clinical_data.columns
        assert 'age' in clinical_data.columns
        assert 'stage' in clinical_data.columns
    
    def test_error_handling(self, pipeline):
        """Test error handling for missing files"""
        # Try with non-existent files
        results = pipeline.run_integrated_analysis(
            expression_file="non_existent.csv",
            cnv_file=None,
            mutation_file=None,
            methylation_file=None,
            clinical_file=None
        )
        
        # Should handle gracefully, possibly with empty results
        assert isinstance(results, dict)
    
    def test_partial_data_integration(self, pipeline, sample_data_files):
        """Test integration with partial data (missing some omics types)"""
        # Run with only expression and CNV data
        results = pipeline.run_integrated_analysis(
            expression_file=sample_data_files['expression'],
            cnv_file=sample_data_files['cnv'],
            mutation_file=None,
            methylation_file=None,
            clinical_file=sample_data_files['clinical']
        )
        
        assert isinstance(results, dict)
        assert len(pipeline.multi_omics.omics_data) == 2  # Only expression and CNV