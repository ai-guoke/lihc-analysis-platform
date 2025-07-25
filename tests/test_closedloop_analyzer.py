"""
Integration tests for ClosedLoop Causal Inference Analyzer
"""

import pytest
import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
import tempfile

from src.analysis.closedloop_analyzer import (
    ClosedLoopAnalyzer, EvidenceType, EvidenceScore, 
    CausalGene, ClosedLoopResult
)


class TestClosedLoopAnalyzer:
    """Test suite for ClosedLoop causal inference"""
    
    @pytest.fixture
    def sample_rna_data(self):
        """Generate sample RNA expression data"""
        n_genes = 100
        n_samples = 80
        np.random.seed(42)
        
        # Create data with some structure
        data = np.random.randn(n_genes, n_samples)
        # Add some genes with high variance
        data[:20, :] *= 3
        
        return pd.DataFrame(
            data,
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
    
    @pytest.fixture
    def sample_clinical_data(self):
        """Generate sample clinical data"""
        n_samples = 80
        np.random.seed(42)
        
        survival_times = np.random.exponential(1000, n_samples)
        survival_status = np.random.binomial(1, 0.3, n_samples)
        
        return pd.DataFrame({
            'survival_time': survival_times,
            'survival_status': survival_status,
            'age': np.random.normal(60, 10, n_samples),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples)
        }, index=[f"Sample_{i:02d}" for i in range(n_samples)])
    
    @pytest.fixture
    def sample_cnv_data(self):
        """Generate sample CNV data"""
        n_genes = 100
        n_samples = 80
        np.random.seed(42)
        
        # CNV values between -2 and 2
        data = np.random.normal(0, 0.5, (n_genes, n_samples))
        data = np.clip(data, -2, 2)
        
        return pd.DataFrame(
            data,
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
    
    @pytest.fixture
    def sample_mutation_data(self):
        """Generate sample mutation data"""
        n_genes = 100
        n_samples = 80
        np.random.seed(42)
        
        # Binary mutation matrix
        data = np.random.binomial(1, 0.1, (n_genes, n_samples))
        
        return pd.DataFrame(
            data,
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
    
    @pytest.fixture
    def sample_methylation_data(self):
        """Generate sample methylation data"""
        n_genes = 100
        n_samples = 80
        np.random.seed(42)
        
        # Beta values between 0 and 1
        data = np.random.beta(2, 5, (n_genes, n_samples))
        
        return pd.DataFrame(
            data,
            index=[f"Gene_{i:03d}" for i in range(n_genes)],
            columns=[f"Sample_{i:02d}" for i in range(n_samples)]
        )
    
    @pytest.fixture
    def analyzer(self):
        """Create ClosedLoop analyzer instance"""
        config = {
            'p_value_threshold': 0.05,
            'effect_size_threshold': 0.3,
            'causal_score_threshold': 0.6
        }
        return ClosedLoopAnalyzer(config)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = ClosedLoopAnalyzer()
        
        assert analyzer.p_value_threshold == 0.05
        assert analyzer.causal_score_threshold == 0.6
        assert len(analyzer.evidence_weights) == 5
        assert sum(analyzer.evidence_weights.values()) == 1.0
    
    def test_differential_expression_analysis(self, analyzer, sample_rna_data, 
                                            sample_clinical_data):
        """Test differential expression evidence calculation"""
        evidence = analyzer._analyze_differential_expression(
            sample_rna_data, sample_clinical_data
        )
        
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
        
        # Check evidence structure
        for gene_id, score in evidence.items():
            assert isinstance(score, EvidenceScore)
            assert score.evidence_type == EvidenceType.DIFFERENTIAL_EXPRESSION
            assert 0 <= score.p_value <= 1
            assert score.effect_size >= 0
            assert 0 <= score.confidence <= 1
            assert 't_statistic' in score.metadata
    
    def test_survival_association_analysis(self, analyzer, sample_rna_data, 
                                         sample_clinical_data):
        """Test survival association evidence calculation"""
        evidence = analyzer._analyze_survival_association(
            sample_rna_data, sample_clinical_data
        )
        
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
        
        for gene_id, score in evidence.items():
            assert isinstance(score, EvidenceScore)
            assert score.evidence_type == EvidenceType.SURVIVAL_ASSOCIATION
            assert 'logrank_statistic' in score.metadata
            assert 'high_group_median_survival' in score.metadata
    
    def test_cnv_driver_analysis(self, analyzer, sample_cnv_data, 
                                sample_rna_data, sample_clinical_data):
        """Test CNV driver evidence calculation"""
        evidence = analyzer._analyze_cnv_drivers(
            sample_cnv_data, sample_rna_data, sample_clinical_data
        )
        
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
        
        for gene_id, score in evidence.items():
            assert isinstance(score, EvidenceScore)
            assert score.evidence_type == EvidenceType.CNV_DRIVER
            assert 'correlation' in score.metadata
            assert 'amplifications' in score.metadata
            assert 'deletions' in score.metadata
    
    def test_methylation_regulation_analysis(self, analyzer, sample_methylation_data,
                                           sample_rna_data, sample_clinical_data):
        """Test methylation regulation evidence calculation"""
        evidence = analyzer._analyze_methylation_regulation(
            sample_methylation_data, sample_rna_data, sample_clinical_data
        )
        
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
        
        for gene_id, score in evidence.items():
            assert isinstance(score, EvidenceScore)
            assert score.evidence_type == EvidenceType.METHYLATION_REGULATION
            assert 'hypermethylated_samples' in score.metadata
            assert 'hypomethylated_samples' in score.metadata
    
    def test_mutation_frequency_analysis(self, analyzer, sample_mutation_data,
                                       sample_clinical_data):
        """Test mutation frequency evidence calculation"""
        evidence = analyzer._analyze_mutation_frequency(
            sample_mutation_data, sample_clinical_data
        )
        
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
        
        for gene_id, score in evidence.items():
            assert isinstance(score, EvidenceScore)
            assert score.evidence_type == EvidenceType.MUTATION_FREQUENCY
            assert 'mutation_frequency' in score.metadata
            assert 'n_mutations' in score.metadata
    
    def test_causal_score_calculation(self, analyzer):
        """Test causal score calculation"""
        # Create mock evidence scores
        evidence_scores = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                gene_id="Gene_001",
                evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                score=0.8,
                p_value=0.001,
                effect_size=1.2,
                confidence=0.9,
                metadata={}
            ),
            EvidenceType.SURVIVAL_ASSOCIATION: EvidenceScore(
                gene_id="Gene_001",
                evidence_type=EvidenceType.SURVIVAL_ASSOCIATION,
                score=0.7,
                p_value=0.01,
                effect_size=0.8,
                confidence=0.8,
                metadata={}
            )
        }
        
        causal_gene = analyzer._calculate_causal_score("Gene_001", evidence_scores)
        
        assert isinstance(causal_gene, CausalGene)
        assert causal_gene.gene_id == "Gene_001"
        assert 0 <= causal_gene.causal_score <= 1
        assert causal_gene.confidence_level in ["High", "Medium", "Low"]
        assert len(causal_gene.evidence_chain) == 2
    
    def test_full_causal_analysis(self, analyzer, sample_rna_data, 
                                 sample_clinical_data, sample_cnv_data,
                                 sample_mutation_data, sample_methylation_data):
        """Test complete causal analysis pipeline"""
        result = analyzer.analyze_causal_relationships(
            rna_data=sample_rna_data,
            clinical_data=sample_clinical_data,
            cnv_data=sample_cnv_data,
            methylation_data=sample_methylation_data,
            mutation_data=sample_mutation_data
        )
        
        assert isinstance(result, ClosedLoopResult)
        assert result.success
        assert isinstance(result.causal_genes, list)
        assert isinstance(result.evidence_network, nx.Graph)
        assert isinstance(result.pathway_analysis, dict)
        assert isinstance(result.validation_metrics, dict)
        assert isinstance(result.algorithm_stats, dict)
        
        # Check causal genes are sorted by score
        if len(result.causal_genes) > 1:
            scores = [g.causal_score for g in result.causal_genes]
            assert scores == sorted(scores, reverse=True)
    
    def test_evidence_network_construction(self, analyzer):
        """Test evidence network graph construction"""
        # Create mock causal genes
        causal_genes = [
            CausalGene(
                gene_id=f"Gene_{i:03d}",
                causal_score=0.8 - i*0.1,
                evidence_scores={},
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            )
            for i in range(5)
        ]
        
        network = analyzer._build_evidence_network(causal_genes, {})
        
        assert isinstance(network, nx.Graph)
        assert network.number_of_nodes() == 5
        assert all(node in network for node in [f"Gene_{i:03d}" for i in range(5)])
    
    def test_pathway_analysis(self, analyzer):
        """Test pathway enrichment analysis"""
        causal_genes = [
            CausalGene(
                gene_id="TP53_related",
                causal_score=0.9,
                evidence_scores={},
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            ),
            CausalGene(
                gene_id="PIK3CA",
                causal_score=0.85,
                evidence_scores={},
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            )
        ]
        
        pathway_results = analyzer._perform_pathway_analysis(causal_genes)
        
        assert isinstance(pathway_results, dict)
        assert 'enriched_pathways' in pathway_results
        assert 'total_genes_analyzed' in pathway_results
        assert pathway_results['total_genes_analyzed'] == 2
    
    def test_validation_metrics(self, analyzer, sample_rna_data, 
                               sample_clinical_data):
        """Test result validation metrics"""
        causal_genes = [
            CausalGene(
                gene_id=f"Gene_{i:03d}",
                causal_score=0.8 - i*0.05,
                evidence_scores={
                    EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                        gene_id=f"Gene_{i:03d}",
                        evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                        score=0.7,
                        p_value=0.01,
                        effect_size=0.5,
                        confidence=0.8,
                        metadata={}
                    )
                },
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            )
            for i in range(3)
        ]
        
        validation = analyzer._validate_results(
            causal_genes, sample_rna_data, sample_clinical_data
        )
        
        assert isinstance(validation, dict)
        assert 'cross_validation_score' in validation
        assert 'bootstrap_stability' in validation
        assert 'literature_support' in validation
        assert all(0 <= v <= 1 for v in validation.values() if isinstance(v, float))
    
    def test_candidate_gene_selection(self, analyzer, sample_rna_data, 
                                    sample_cnv_data, sample_mutation_data):
        """Test candidate gene selection"""
        candidates = analyzer._select_candidate_genes(
            sample_rna_data, sample_cnv_data, sample_mutation_data
        )
        
        assert isinstance(candidates, list)
        assert len(candidates) > 0
        assert all(isinstance(g, str) for g in candidates)
        # Should include high-variance genes
        assert len(candidates) <= len(sample_rna_data.columns)
    
    def test_error_handling(self, analyzer):
        """Test error handling in analysis"""
        # Empty data
        empty_data = pd.DataFrame()
        result = analyzer.analyze_causal_relationships(
            rna_data=empty_data,
            clinical_data=empty_data
        )
        
        assert isinstance(result, ClosedLoopResult)
        assert not result.success
        assert len(result.errors) > 0
        assert len(result.causal_genes) == 0
    
    def test_confidence_calculation(self, analyzer):
        """Test confidence score calculation"""
        # Test with different p-values and effect sizes
        conf1 = analyzer._calculate_confidence(0.001, 1.0)
        conf2 = analyzer._calculate_confidence(0.05, 0.5)
        conf3 = analyzer._calculate_confidence(0.5, 0.1)
        
        assert conf1 > conf2 > conf3
        assert all(0 <= c <= 1 for c in [conf1, conf2, conf3])
    
    def test_evidence_similarity(self, analyzer):
        """Test evidence similarity calculation"""
        evidence1 = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                gene_id="Gene1",
                evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                score=0.8,
                p_value=0.01,
                effect_size=1.0,
                confidence=0.9,
                metadata={}
            )
        }
        
        evidence2 = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                gene_id="Gene2",
                evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                score=0.7,
                p_value=0.02,
                effect_size=0.9,
                confidence=0.85,
                metadata={}
            )
        }
        
        similarity = analyzer._calculate_evidence_similarity(evidence1, evidence2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be relatively similar