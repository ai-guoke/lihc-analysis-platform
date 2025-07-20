"""
Unit tests for ClosedLoop causal inference analyzer
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import networkx as nx

from src.analysis.closedloop_analyzer import (
    ClosedLoopAnalyzer, EvidenceType, EvidenceScore, CausalGene, ClosedLoopResult
)


class TestClosedLoopAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ClosedLoopAnalyzer()
        
        # Create test data
        np.random.seed(42)
        self.n_samples = 100
        self.n_genes = 50
        
        # Sample and gene names
        self.sample_names = [f"SAMPLE_{i:03d}" for i in range(self.n_samples)]
        self.gene_names = [f"GENE_{i:03d}" for i in range(self.n_genes)]
        
        # Test RNA-seq data
        self.test_rna_data = pd.DataFrame(
            np.random.normal(5, 2, size=(self.n_samples, self.n_genes)),
            index=self.sample_names,
            columns=self.gene_names
        )
        
        # Test clinical data
        self.test_clinical_data = pd.DataFrame({
            'survival_time': np.random.exponential(1000, self.n_samples),
            'survival_status': np.random.binomial(1, 0.3, self.n_samples),
            'age': np.random.normal(65, 10, self.n_samples),
            'gender': np.random.choice(['M', 'F'], self.n_samples)
        }, index=self.sample_names)
        
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
        """Test analyzer initialization"""
        analyzer = ClosedLoopAnalyzer()
        self.assertIsNotNone(analyzer.logger)
        self.assertIn(EvidenceType.DIFFERENTIAL_EXPRESSION, analyzer.evidence_weights)
        self.assertIn(EvidenceType.SURVIVAL_ASSOCIATION, analyzer.evidence_weights)
        self.assertEqual(analyzer.p_value_threshold, 0.05)
    
    def test_select_candidate_genes(self):
        """Test candidate gene selection"""
        candidates = self.analyzer._select_candidate_genes(
            self.test_rna_data, self.test_cnv_data, self.test_mutation_data
        )
        
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), self.n_genes)
        
        # All candidates should be in the common genes
        for candidate in candidates:
            self.assertIn(candidate, self.gene_names)
    
    def test_analyze_differential_expression(self):
        """Test differential expression analysis"""
        de_evidence = self.analyzer._analyze_differential_expression(
            self.test_rna_data, self.test_clinical_data
        )
        
        self.assertIsInstance(de_evidence, dict)
        self.assertGreater(len(de_evidence), 0)
        
        # Check evidence score structure
        for gene_id, evidence in de_evidence.items():
            self.assertIsInstance(evidence, EvidenceScore)
            self.assertEqual(evidence.gene_id, gene_id)
            self.assertEqual(evidence.evidence_type, EvidenceType.DIFFERENTIAL_EXPRESSION)
            self.assertIsInstance(evidence.score, float)
            self.assertIsInstance(evidence.p_value, float)
            self.assertIsInstance(evidence.effect_size, float)
            self.assertIsInstance(evidence.confidence, float)
            self.assertIsInstance(evidence.metadata, dict)
            
            # Check value ranges
            self.assertGreaterEqual(evidence.score, 0)
            self.assertLessEqual(evidence.score, 1)
            self.assertGreaterEqual(evidence.p_value, 0)
            self.assertLessEqual(evidence.p_value, 1)
            self.assertGreaterEqual(evidence.confidence, 0)
            self.assertLessEqual(evidence.confidence, 1)
    
    def test_analyze_survival_association(self):
        """Test survival association analysis"""
        survival_evidence = self.analyzer._analyze_survival_association(
            self.test_rna_data, self.test_clinical_data
        )
        
        self.assertIsInstance(survival_evidence, dict)
        self.assertGreater(len(survival_evidence), 0)
        
        # Check evidence score structure
        for gene_id, evidence in survival_evidence.items():
            self.assertIsInstance(evidence, EvidenceScore)
            self.assertEqual(evidence.evidence_type, EvidenceType.SURVIVAL_ASSOCIATION)
            self.assertGreaterEqual(evidence.score, 0)
            self.assertLessEqual(evidence.score, 1)
            
            # Check metadata
            self.assertIn('logrank_statistic', evidence.metadata)
            self.assertIn('high_group_median_survival', evidence.metadata)
            self.assertIn('low_group_median_survival', evidence.metadata)
    
    def test_analyze_cnv_drivers(self):
        """Test CNV driver analysis"""
        cnv_evidence = self.analyzer._analyze_cnv_drivers(
            self.test_cnv_data, self.test_rna_data, self.test_clinical_data
        )
        
        self.assertIsInstance(cnv_evidence, dict)
        self.assertGreater(len(cnv_evidence), 0)
        
        # Check evidence score structure
        for gene_id, evidence in cnv_evidence.items():
            self.assertIsInstance(evidence, EvidenceScore)
            self.assertEqual(evidence.evidence_type, EvidenceType.CNV_DRIVER)
            self.assertGreaterEqual(evidence.score, 0)
            self.assertLessEqual(evidence.score, 1)
            
            # Check metadata
            self.assertIn('correlation', evidence.metadata)
            self.assertIn('amplifications', evidence.metadata)
            self.assertIn('deletions', evidence.metadata)
            self.assertIn('alteration_frequency', evidence.metadata)
    
    def test_analyze_methylation_regulation(self):
        """Test methylation regulation analysis"""
        methylation_evidence = self.analyzer._analyze_methylation_regulation(
            self.test_methylation_data, self.test_rna_data, self.test_clinical_data
        )
        
        self.assertIsInstance(methylation_evidence, dict)
        self.assertGreater(len(methylation_evidence), 0)
        
        # Check evidence score structure
        for gene_id, evidence in methylation_evidence.items():
            self.assertIsInstance(evidence, EvidenceScore)
            self.assertEqual(evidence.evidence_type, EvidenceType.METHYLATION_REGULATION)
            self.assertGreaterEqual(evidence.score, 0)
            self.assertLessEqual(evidence.score, 1)
            
            # Check metadata
            self.assertIn('correlation', evidence.metadata)
            self.assertIn('hypermethylated_samples', evidence.metadata)
            self.assertIn('hypomethylated_samples', evidence.metadata)
    
    def test_analyze_mutation_frequency(self):
        """Test mutation frequency analysis"""
        mutation_evidence = self.analyzer._analyze_mutation_frequency(
            self.test_mutation_data, self.test_clinical_data
        )
        
        self.assertIsInstance(mutation_evidence, dict)
        self.assertGreater(len(mutation_evidence), 0)
        
        # Check evidence score structure
        for gene_id, evidence in mutation_evidence.items():
            self.assertIsInstance(evidence, EvidenceScore)
            self.assertEqual(evidence.evidence_type, EvidenceType.MUTATION_FREQUENCY)
            self.assertGreaterEqual(evidence.score, 0)
            self.assertLessEqual(evidence.score, 1)
            
            # Check metadata
            self.assertIn('mutation_frequency', evidence.metadata)
            self.assertIn('n_mutations', evidence.metadata)
            self.assertIn('n_samples', evidence.metadata)
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        # Test with significant p-value and large effect size
        confidence1 = self.analyzer._calculate_confidence(0.001, 0.8)
        self.assertGreater(confidence1, 0.5)
        
        # Test with non-significant p-value and small effect size
        confidence2 = self.analyzer._calculate_confidence(0.5, 0.1)
        self.assertLess(confidence2, 0.5)
        
        # Test with extreme values
        confidence3 = self.analyzer._calculate_confidence(1e-10, 2.0)
        self.assertLessEqual(confidence3, 1.0)
    
    def test_calculate_evidence_score(self):
        """Test evidence score calculation"""
        # Test with significant p-value and large effect size
        score1 = self.analyzer._calculate_evidence_score(0.001, 0.8, 0.9)
        self.assertGreater(score1, 0.5)
        
        # Test with non-significant p-value
        score2 = self.analyzer._calculate_evidence_score(0.5, 0.8, 0.9)
        self.assertLess(score2, score1)
        
        # Test with small effect size
        score3 = self.analyzer._calculate_evidence_score(0.001, 0.1, 0.9)
        self.assertLess(score3, score1)
        
        # Check score range
        self.assertGreaterEqual(score1, 0)
        self.assertLessEqual(score1, 1)
    
    def test_calculate_causal_score(self):
        """Test causal score calculation"""
        # Create mock evidence scores
        evidence_scores = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                gene_id="TEST_GENE",
                evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                score=0.8,
                p_value=0.001,
                effect_size=0.7,
                confidence=0.9,
                metadata={}
            ),
            EvidenceType.SURVIVAL_ASSOCIATION: EvidenceScore(
                gene_id="TEST_GENE",
                evidence_type=EvidenceType.SURVIVAL_ASSOCIATION,
                score=0.6,
                p_value=0.01,
                effect_size=0.5,
                confidence=0.7,
                metadata={}
            )
        }
        
        causal_gene = self.analyzer._calculate_causal_score("TEST_GENE", evidence_scores)
        
        # Check causal gene structure
        self.assertIsInstance(causal_gene, CausalGene)
        self.assertEqual(causal_gene.gene_id, "TEST_GENE")
        self.assertGreater(causal_gene.causal_score, 0)
        self.assertLessEqual(causal_gene.causal_score, 1)
        self.assertIn(causal_gene.confidence_level, ["High", "Medium", "Low"])
        self.assertIsInstance(causal_gene.evidence_scores, dict)
        self.assertIsInstance(causal_gene.biological_context, dict)
        self.assertIsInstance(causal_gene.evidence_chain, list)
    
    def test_build_evidence_network(self):
        """Test evidence network building"""
        # Create mock causal genes
        causal_genes = [
            CausalGene(
                gene_id="GENE_001",
                causal_score=0.8,
                evidence_scores={
                    EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                        "GENE_001", EvidenceType.DIFFERENTIAL_EXPRESSION, 0.8, 0.001, 0.7, 0.9, {}
                    )
                },
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            ),
            CausalGene(
                gene_id="GENE_002",
                causal_score=0.7,
                evidence_scores={
                    EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                        "GENE_002", EvidenceType.DIFFERENTIAL_EXPRESSION, 0.7, 0.01, 0.6, 0.8, {}
                    )
                },
                confidence_level="High",
                biological_context={},
                evidence_chain=[],
                validation_status="Pending"
            )
        ]
        
        network = self.analyzer._build_evidence_network(causal_genes, {})
        
        # Check network structure
        self.assertIsInstance(network, nx.Graph)
        self.assertEqual(len(network.nodes), 2)
        
        # Check node attributes
        for node in network.nodes:
            self.assertIn(node, ["GENE_001", "GENE_002"])
            self.assertIn('causal_score', network.nodes[node])
            self.assertIn('confidence_level', network.nodes[node])
            self.assertIn('node_type', network.nodes[node])
    
    def test_calculate_evidence_similarity(self):
        """Test evidence similarity calculation"""
        evidence1 = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                "GENE_001", EvidenceType.DIFFERENTIAL_EXPRESSION, 0.8, 0.001, 0.7, 0.9, {}
            ),
            EvidenceType.SURVIVAL_ASSOCIATION: EvidenceScore(
                "GENE_001", EvidenceType.SURVIVAL_ASSOCIATION, 0.6, 0.01, 0.5, 0.7, {}
            )
        }
        
        evidence2 = {
            EvidenceType.DIFFERENTIAL_EXPRESSION: EvidenceScore(
                "GENE_002", EvidenceType.DIFFERENTIAL_EXPRESSION, 0.7, 0.01, 0.6, 0.8, {}
            ),
            EvidenceType.SURVIVAL_ASSOCIATION: EvidenceScore(
                "GENE_002", EvidenceType.SURVIVAL_ASSOCIATION, 0.5, 0.05, 0.4, 0.6, {}
            )
        }
        
        similarity = self.analyzer._calculate_evidence_similarity(evidence1, evidence2)
        
        # Check similarity properties
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 1)
        
        # Test with no common evidence
        evidence3 = {
            EvidenceType.CNV_DRIVER: EvidenceScore(
                "GENE_003", EvidenceType.CNV_DRIVER, 0.5, 0.1, 0.3, 0.5, {}
            )
        }
        
        similarity_no_common = self.analyzer._calculate_evidence_similarity(evidence1, evidence3)
        self.assertEqual(similarity_no_common, 0.0)
    
    def test_perform_pathway_analysis(self):
        """Test pathway analysis"""
        # Create mock causal genes
        causal_genes = [
            CausalGene("TP53", 0.9, {}, "High", {}, [], "Pending"),
            CausalGene("PIK3CA", 0.8, {}, "High", {}, [], "Pending"),
            CausalGene("KRAS", 0.7, {}, "Medium", {}, [], "Pending")
        ]
        
        pathway_analysis = self.analyzer._perform_pathway_analysis(causal_genes)
        
        # Check pathway analysis structure
        self.assertIsInstance(pathway_analysis, dict)
        self.assertIn('enriched_pathways', pathway_analysis)
        self.assertIn('total_genes_analyzed', pathway_analysis)
        self.assertIn('pathway_coverage', pathway_analysis)
        
        self.assertEqual(pathway_analysis['total_genes_analyzed'], 3)
        self.assertIsInstance(pathway_analysis['pathway_coverage'], float)
    
    def test_validate_results(self):
        """Test result validation"""
        # Create mock causal genes
        causal_genes = [
            CausalGene("TP53", 0.9, {}, "High", {}, [], "Pending"),
            CausalGene("MYC", 0.8, {}, "High", {}, [], "Pending")
        ]
        
        validation_metrics = self.analyzer._validate_results(
            causal_genes, self.test_rna_data, self.test_clinical_data
        )
        
        # Check validation metrics structure
        self.assertIsInstance(validation_metrics, dict)
        self.assertIn('cross_validation_score', validation_metrics)
        self.assertIn('bootstrap_stability', validation_metrics)
        self.assertIn('literature_support', validation_metrics)
        
        # Check metric ranges
        for metric_name, metric_value in validation_metrics.items():
            self.assertIsInstance(metric_value, float)
            self.assertGreaterEqual(metric_value, 0)
            self.assertLessEqual(metric_value, 1)
    
    def test_full_analysis_workflow(self):
        """Test complete ClosedLoop analysis workflow"""
        # Run full analysis
        result = self.analyzer.analyze_causal_relationships(
            rna_data=self.test_rna_data,
            clinical_data=self.test_clinical_data,
            cnv_data=self.test_cnv_data,
            methylation_data=self.test_methylation_data,
            mutation_data=self.test_mutation_data
        )
        
        # Check result structure
        self.assertIsInstance(result, ClosedLoopResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        
        # Check causal genes
        self.assertIsInstance(result.causal_genes, list)
        if result.causal_genes:  # If any causal genes were found
            for gene in result.causal_genes:
                self.assertIsInstance(gene, CausalGene)
                self.assertGreaterEqual(gene.causal_score, 0.6)  # Above threshold
        
        # Check evidence network
        self.assertIsInstance(result.evidence_network, nx.Graph)
        
        # Check pathway analysis
        self.assertIsInstance(result.pathway_analysis, dict)
        
        # Check validation metrics
        self.assertIsInstance(result.validation_metrics, dict)
        
        # Check algorithm stats
        self.assertIsInstance(result.algorithm_stats, dict)
        self.assertIn('total_genes_analyzed', result.algorithm_stats)
        self.assertIn('causal_genes_identified', result.algorithm_stats)
    
    def test_error_handling(self):
        """Test error handling in analysis"""
        # Test with empty data
        empty_data = pd.DataFrame()
        
        result = self.analyzer.analyze_causal_relationships(
            rna_data=empty_data,
            clinical_data=self.test_clinical_data
        )
        
        # Should handle error gracefully
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_custom_configuration(self):
        """Test analyzer with custom configuration"""
        custom_config = {
            'evidence_weights': {
                EvidenceType.DIFFERENTIAL_EXPRESSION: 0.5,
                EvidenceType.SURVIVAL_ASSOCIATION: 0.3,
                EvidenceType.CNV_DRIVER: 0.2,
                EvidenceType.METHYLATION_REGULATION: 0.0,
                EvidenceType.MUTATION_FREQUENCY: 0.0
            },
            'causal_score_threshold': 0.7,
            'effect_size_threshold': 0.5
        }
        
        analyzer = ClosedLoopAnalyzer(config=custom_config)
        
        # Check if custom configuration is applied
        self.assertEqual(
            analyzer.evidence_weights[EvidenceType.DIFFERENTIAL_EXPRESSION], 0.5
        )
        self.assertEqual(analyzer.causal_score_threshold, 0.7)
        self.assertEqual(analyzer.effect_size_threshold, 0.5)
    
    def test_target_genes_specification(self):
        """Test analysis with specified target genes"""
        target_genes = ["GENE_001", "GENE_002", "GENE_003"]
        
        result = self.analyzer.analyze_causal_relationships(
            rna_data=self.test_rna_data,
            clinical_data=self.test_clinical_data,
            target_genes=target_genes
        )
        
        # Check that only target genes are analyzed
        self.assertTrue(result.success)
        
        # All identified causal genes should be in the target list
        for gene in result.causal_genes:
            self.assertIn(gene.gene_id, target_genes)


if __name__ == '__main__':
    unittest.main()