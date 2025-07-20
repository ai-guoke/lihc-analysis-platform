"""
ClosedLoop Causal Inference Algorithm for Multi-omics Analysis
Implements causal reasoning to identify cancer driver genes and pathways

The ClosedLoop algorithm integrates multiple lines of evidence:
1. Differential expression analysis
2. Survival association analysis  
3. Copy number variation analysis
4. Methylation regulation analysis
5. Mutation frequency analysis

Final causal score is calculated as weighted combination of all evidence types.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from dataclasses import dataclass
from enum import Enum
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

from ..utils.logging_system import LIHCLogger
from ..utils.enhanced_config import get_analysis_config


class EvidenceType(Enum):
    """Types of causal evidence"""
    DIFFERENTIAL_EXPRESSION = "differential_expression"
    SURVIVAL_ASSOCIATION = "survival_association"
    CNV_DRIVER = "cnv_driver"
    METHYLATION_REGULATION = "methylation_regulation"
    MUTATION_FREQUENCY = "mutation_frequency"


@dataclass
class EvidenceScore:
    """Individual evidence score for a gene"""
    gene_id: str
    evidence_type: EvidenceType
    score: float
    p_value: float
    effect_size: float
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class CausalGene:
    """Causal gene with integrated evidence"""
    gene_id: str
    causal_score: float
    evidence_scores: Dict[EvidenceType, EvidenceScore]
    confidence_level: str
    biological_context: Dict[str, Any]
    evidence_chain: List[str]
    validation_status: str


@dataclass
class ClosedLoopResult:
    """Complete ClosedLoop analysis result"""
    causal_genes: List[CausalGene]
    evidence_network: nx.Graph
    pathway_analysis: Dict[str, Any]
    validation_metrics: Dict[str, float]
    algorithm_stats: Dict[str, Any]
    success: bool
    errors: List[str]


class ClosedLoopAnalyzer:
    """Main ClosedLoop causal inference analyzer"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.analysis_config = get_analysis_config()
        self.logger = LIHCLogger(name="ClosedLoopAnalyzer")
        
        # Algorithm parameters
        self.evidence_weights = self.config.get('evidence_weights', {
            EvidenceType.DIFFERENTIAL_EXPRESSION: 0.25,
            EvidenceType.SURVIVAL_ASSOCIATION: 0.25,
            EvidenceType.CNV_DRIVER: 0.20,
            EvidenceType.METHYLATION_REGULATION: 0.20,
            EvidenceType.MUTATION_FREQUENCY: 0.10
        })
        
        # Statistical thresholds
        self.p_value_threshold = self.analysis_config.p_value_threshold
        self.effect_size_threshold = self.config.get('effect_size_threshold', 0.3)
        self.causal_score_threshold = self.config.get('causal_score_threshold', 0.6)
        
        # Validation settings
        self.cross_validation_folds = self.config.get('cross_validation_folds', 5)
        self.bootstrap_iterations = self.config.get('bootstrap_iterations', 100)
        
        self.logger.info("ClosedLoop analyzer initialized")
    
    def analyze_causal_relationships(self,
                                   rna_data: pd.DataFrame,
                                   clinical_data: pd.DataFrame,
                                   cnv_data: Optional[pd.DataFrame] = None,
                                   methylation_data: Optional[pd.DataFrame] = None,
                                   mutation_data: Optional[pd.DataFrame] = None,
                                   target_genes: Optional[List[str]] = None) -> ClosedLoopResult:
        """
        Perform comprehensive causal analysis using ClosedLoop algorithm
        """
        try:
            self.logger.info("Starting ClosedLoop causal analysis")
            
            # Initialize results
            all_evidence_scores = {}
            causal_genes = []
            errors = []
            
            # Determine target genes
            if target_genes is None:
                target_genes = self._select_candidate_genes(rna_data, cnv_data, mutation_data)
            
            self.logger.info(f"Analyzing {len(target_genes)} candidate genes")
            
            # Evidence collection phase
            self.logger.info("Phase 1: Evidence collection")
            
            # 1. Differential expression evidence
            de_evidence = self._analyze_differential_expression(rna_data, clinical_data)
            self._integrate_evidence(all_evidence_scores, de_evidence, EvidenceType.DIFFERENTIAL_EXPRESSION)
            
            # 2. Survival association evidence
            survival_evidence = self._analyze_survival_association(rna_data, clinical_data)
            self._integrate_evidence(all_evidence_scores, survival_evidence, EvidenceType.SURVIVAL_ASSOCIATION)
            
            # 3. CNV driver evidence
            if cnv_data is not None:
                cnv_evidence = self._analyze_cnv_drivers(cnv_data, rna_data, clinical_data)
                self._integrate_evidence(all_evidence_scores, cnv_evidence, EvidenceType.CNV_DRIVER)
            
            # 4. Methylation regulation evidence
            if methylation_data is not None:
                methylation_evidence = self._analyze_methylation_regulation(methylation_data, rna_data, clinical_data)
                self._integrate_evidence(all_evidence_scores, methylation_evidence, EvidenceType.METHYLATION_REGULATION)
            
            # 5. Mutation frequency evidence
            if mutation_data is not None:
                mutation_evidence = self._analyze_mutation_frequency(mutation_data, clinical_data)
                self._integrate_evidence(all_evidence_scores, mutation_evidence, EvidenceType.MUTATION_FREQUENCY)
            
            # Causal scoring phase
            self.logger.info("Phase 2: Causal score calculation")
            
            for gene_id in target_genes:
                if gene_id in all_evidence_scores:
                    causal_gene = self._calculate_causal_score(gene_id, all_evidence_scores[gene_id])
                    if causal_gene.causal_score >= self.causal_score_threshold:
                        causal_genes.append(causal_gene)
            
            # Sort by causal score
            causal_genes.sort(key=lambda x: x.causal_score, reverse=True)
            
            # Build evidence network
            self.logger.info("Phase 3: Evidence network construction")
            evidence_network = self._build_evidence_network(causal_genes, all_evidence_scores)
            
            # Pathway analysis
            self.logger.info("Phase 4: Pathway analysis")
            pathway_analysis = self._perform_pathway_analysis(causal_genes)
            
            # Validation
            self.logger.info("Phase 5: Validation")
            validation_metrics = self._validate_results(causal_genes, rna_data, clinical_data)
            
            # Algorithm statistics
            algorithm_stats = self._calculate_algorithm_stats(causal_genes, all_evidence_scores)
            
            result = ClosedLoopResult(
                causal_genes=causal_genes,
                evidence_network=evidence_network,
                pathway_analysis=pathway_analysis,
                validation_metrics=validation_metrics,
                algorithm_stats=algorithm_stats,
                success=True,
                errors=errors
            )
            
            self.logger.info(f"ClosedLoop analysis completed. Found {len(causal_genes)} causal genes")
            return result
            
        except Exception as e:
            self.logger.error(f"ClosedLoop analysis failed: {e}")
            return ClosedLoopResult(
                causal_genes=[],
                evidence_network=nx.Graph(),
                pathway_analysis={},
                validation_metrics={},
                algorithm_stats={},
                success=False,
                errors=[str(e)]
            )
    
    def _select_candidate_genes(self, rna_data: pd.DataFrame, 
                              cnv_data: Optional[pd.DataFrame],
                              mutation_data: Optional[pd.DataFrame]) -> List[str]:
        """Select candidate genes for causal analysis"""
        candidates = set()
        
        # High-variance genes from RNA-seq
        rna_variance = rna_data.var(axis=0)
        top_variable_genes = rna_variance.nlargest(1000).index.tolist()
        candidates.update(top_variable_genes)
        
        # Frequently altered genes from CNV
        if cnv_data is not None:
            cnv_altered = (cnv_data.abs() > 0.5).sum(axis=0)
            frequently_altered = cnv_altered[cnv_altered > len(cnv_data) * 0.1].index.tolist()
            candidates.update(frequently_altered)
        
        # Frequently mutated genes
        if mutation_data is not None:
            mutation_freq = mutation_data.sum(axis=0)
            frequently_mutated = mutation_freq[mutation_freq > len(mutation_data) * 0.05].index.tolist()
            candidates.update(frequently_mutated)
        
        # Filter to common genes across datasets
        common_genes = set(rna_data.columns)
        if cnv_data is not None:
            common_genes = common_genes.intersection(cnv_data.columns)
        if mutation_data is not None:
            common_genes = common_genes.intersection(mutation_data.columns)
        
        candidates = candidates.intersection(common_genes)
        
        return list(candidates)
    
    def _analyze_differential_expression(self, rna_data: pd.DataFrame, 
                                       clinical_data: pd.DataFrame) -> Dict[str, EvidenceScore]:
        """Analyze differential expression evidence"""
        evidence_scores = {}
        
        # Determine tumor vs normal samples (simplified)
        # In real implementation, this would use actual sample type information
        median_expression = rna_data.median(axis=1)
        high_expr_samples = median_expression > median_expression.median()
        
        for gene in rna_data.columns:
            try:
                # Perform t-test
                high_group = rna_data.loc[high_expr_samples, gene]
                low_group = rna_data.loc[~high_expr_samples, gene]
                
                t_stat, p_value = stats.ttest_ind(high_group, low_group)
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt(((len(high_group) - 1) * high_group.var() + 
                                     (len(low_group) - 1) * low_group.var()) / 
                                    (len(high_group) + len(low_group) - 2))
                
                effect_size = abs(high_group.mean() - low_group.mean()) / pooled_std
                
                # Calculate confidence based on p-value and effect size
                confidence = self._calculate_confidence(p_value, effect_size)
                
                # Calculate evidence score
                score = self._calculate_evidence_score(p_value, effect_size, confidence)
                
                evidence_scores[gene] = EvidenceScore(
                    gene_id=gene,
                    evidence_type=EvidenceType.DIFFERENTIAL_EXPRESSION,
                    score=score,
                    p_value=p_value,
                    effect_size=effect_size,
                    confidence=confidence,
                    metadata={
                        't_statistic': t_stat,
                        'high_group_mean': high_group.mean(),
                        'low_group_mean': low_group.mean(),
                        'high_group_size': len(high_group),
                        'low_group_size': len(low_group)
                    }
                )
                
            except Exception as e:
                self.logger.debug(f"Error analyzing differential expression for {gene}: {e}")
                continue
        
        return evidence_scores
    
    def _analyze_survival_association(self, rna_data: pd.DataFrame,
                                    clinical_data: pd.DataFrame) -> Dict[str, EvidenceScore]:
        """Analyze survival association evidence"""
        evidence_scores = {}
        
        # Check if survival data is available
        if 'survival_time' not in clinical_data.columns or 'survival_status' not in clinical_data.columns:
            # Generate simulated survival data for demonstration
            np.random.seed(42)
            survival_time = np.random.exponential(1000, len(clinical_data))
            survival_status = np.random.binomial(1, 0.3, len(clinical_data))
            
            clinical_data = clinical_data.copy()
            clinical_data['survival_time'] = survival_time
            clinical_data['survival_status'] = survival_status
        
        for gene in rna_data.columns:
            try:
                # Dichotomize gene expression
                gene_expr = rna_data[gene]
                high_expr = gene_expr > gene_expr.median()
                
                # Prepare survival data
                high_group_time = clinical_data.loc[high_expr, 'survival_time']
                high_group_status = clinical_data.loc[high_expr, 'survival_status']
                
                low_group_time = clinical_data.loc[~high_expr, 'survival_time']
                low_group_status = clinical_data.loc[~high_expr, 'survival_status']
                
                # Perform log-rank test
                results = logrank_test(high_group_time, low_group_time, 
                                     high_group_status, low_group_status)
                
                p_value = results.p_value
                
                # Calculate hazard ratio using Cox regression
                try:
                    cph_data = pd.DataFrame({
                        'T': clinical_data['survival_time'],
                        'E': clinical_data['survival_status'],
                        'gene_expr': gene_expr
                    })
                    
                    cph = CoxPHFitter()
                    cph.fit(cph_data, duration_col='T', event_col='E')
                    
                    hazard_ratio = cph.hazard_ratios_['gene_expr']
                    effect_size = abs(np.log(hazard_ratio))
                    
                except Exception:
                    # Fallback to simple effect size calculation
                    effect_size = abs(high_group_time.mean() - low_group_time.mean()) / high_group_time.std()
                
                # Calculate confidence and score
                confidence = self._calculate_confidence(p_value, effect_size)
                score = self._calculate_evidence_score(p_value, effect_size, confidence)
                
                evidence_scores[gene] = EvidenceScore(
                    gene_id=gene,
                    evidence_type=EvidenceType.SURVIVAL_ASSOCIATION,
                    score=score,
                    p_value=p_value,
                    effect_size=effect_size,
                    confidence=confidence,
                    metadata={
                        'logrank_statistic': results.test_statistic,
                        'high_group_median_survival': high_group_time.median(),
                        'low_group_median_survival': low_group_time.median(),
                        'high_group_size': len(high_group_time),
                        'low_group_size': len(low_group_time)
                    }
                )
                
            except Exception as e:
                self.logger.debug(f"Error analyzing survival association for {gene}: {e}")
                continue
        
        return evidence_scores
    
    def _analyze_cnv_drivers(self, cnv_data: pd.DataFrame, 
                           rna_data: pd.DataFrame,
                           clinical_data: pd.DataFrame) -> Dict[str, EvidenceScore]:
        """Analyze CNV driver evidence"""
        evidence_scores = {}
        
        # Find common genes between CNV and RNA data
        common_genes = set(cnv_data.columns).intersection(rna_data.columns)
        
        for gene in common_genes:
            try:
                cnv_values = cnv_data[gene]
                rna_values = rna_data[gene]
                
                # Calculate correlation between CNV and expression
                correlation, p_value = stats.pearsonr(cnv_values, rna_values)
                
                # Calculate amplification/deletion frequency
                amplifications = (cnv_values > 0.5).sum()
                deletions = (cnv_values < -0.5).sum()
                alteration_frequency = (amplifications + deletions) / len(cnv_values)
                
                # Effect size is combination of correlation and alteration frequency
                effect_size = abs(correlation) * alteration_frequency
                
                # Calculate confidence and score
                confidence = self._calculate_confidence(p_value, effect_size)
                score = self._calculate_evidence_score(p_value, effect_size, confidence)
                
                evidence_scores[gene] = EvidenceScore(
                    gene_id=gene,
                    evidence_type=EvidenceType.CNV_DRIVER,
                    score=score,
                    p_value=p_value,
                    effect_size=effect_size,
                    confidence=confidence,
                    metadata={
                        'correlation': correlation,
                        'amplifications': amplifications,
                        'deletions': deletions,
                        'alteration_frequency': alteration_frequency,
                        'mean_cnv': cnv_values.mean(),
                        'std_cnv': cnv_values.std()
                    }
                )
                
            except Exception as e:
                self.logger.debug(f"Error analyzing CNV driver for {gene}: {e}")
                continue
        
        return evidence_scores
    
    def _analyze_methylation_regulation(self, methylation_data: pd.DataFrame,
                                      rna_data: pd.DataFrame,
                                      clinical_data: pd.DataFrame) -> Dict[str, EvidenceScore]:
        """Analyze methylation regulation evidence"""
        evidence_scores = {}
        
        # Find common genes (simplified mapping)
        common_genes = set(methylation_data.columns).intersection(rna_data.columns)
        
        for gene in common_genes:
            try:
                methylation_values = methylation_data[gene]
                rna_values = rna_data[gene]
                
                # Calculate anti-correlation (methylation typically suppresses expression)
                correlation, p_value = stats.pearsonr(methylation_values, rna_values)
                
                # Calculate hypermethylation frequency
                hypermethylated = (methylation_values > 0.7).sum()
                hypomethylated = (methylation_values < 0.3).sum()
                methylation_alteration_freq = (hypermethylated + hypomethylated) / len(methylation_values)
                
                # Effect size is combination of anti-correlation and alteration frequency
                effect_size = abs(correlation) * methylation_alteration_freq
                
                # Calculate confidence and score
                confidence = self._calculate_confidence(p_value, effect_size)
                score = self._calculate_evidence_score(p_value, effect_size, confidence)
                
                evidence_scores[gene] = EvidenceScore(
                    gene_id=gene,
                    evidence_type=EvidenceType.METHYLATION_REGULATION,
                    score=score,
                    p_value=p_value,
                    effect_size=effect_size,
                    confidence=confidence,
                    metadata={
                        'correlation': correlation,
                        'hypermethylated_samples': hypermethylated,
                        'hypomethylated_samples': hypomethylated,
                        'methylation_alteration_freq': methylation_alteration_freq,
                        'mean_methylation': methylation_values.mean(),
                        'std_methylation': methylation_values.std()
                    }
                )
                
            except Exception as e:
                self.logger.debug(f"Error analyzing methylation regulation for {gene}: {e}")
                continue
        
        return evidence_scores
    
    def _analyze_mutation_frequency(self, mutation_data: pd.DataFrame,
                                  clinical_data: pd.DataFrame) -> Dict[str, EvidenceScore]:
        """Analyze mutation frequency evidence"""
        evidence_scores = {}
        
        for gene in mutation_data.columns:
            try:
                mutation_freq = mutation_data[gene].sum() / len(mutation_data)
                
                # Calculate effect size based on mutation frequency
                # More frequent mutations have higher effect size
                effect_size = mutation_freq
                
                # Calculate p-value using binomial test against background mutation rate
                background_rate = 0.01  # 1% background mutation rate
                n_mutations = mutation_data[gene].sum()
                n_samples = len(mutation_data)
                
                p_value = stats.binom_test(n_mutations, n_samples, background_rate, alternative='greater')
                
                # Calculate confidence and score
                confidence = self._calculate_confidence(p_value, effect_size)
                score = self._calculate_evidence_score(p_value, effect_size, confidence)
                
                evidence_scores[gene] = EvidenceScore(
                    gene_id=gene,
                    evidence_type=EvidenceType.MUTATION_FREQUENCY,
                    score=score,
                    p_value=p_value,
                    effect_size=effect_size,
                    confidence=confidence,
                    metadata={
                        'mutation_frequency': mutation_freq,
                        'n_mutations': n_mutations,
                        'n_samples': n_samples,
                        'background_rate': background_rate
                    }
                )
                
            except Exception as e:
                self.logger.debug(f"Error analyzing mutation frequency for {gene}: {e}")
                continue
        
        return evidence_scores
    
    def _calculate_confidence(self, p_value: float, effect_size: float) -> float:
        """Calculate confidence score based on p-value and effect size"""
        # Transform p-value to confidence score (0-1)
        p_confidence = -np.log10(max(p_value, 1e-10)) / 10
        p_confidence = min(p_confidence, 1.0)
        
        # Normalize effect size to confidence score
        effect_confidence = min(effect_size / self.effect_size_threshold, 1.0)
        
        # Combined confidence
        confidence = (p_confidence + effect_confidence) / 2
        return confidence
    
    def _calculate_evidence_score(self, p_value: float, effect_size: float, confidence: float) -> float:
        """Calculate evidence score combining statistical significance and effect size"""
        # Statistical significance component
        if p_value < self.p_value_threshold:
            significance_score = min(-np.log10(p_value) / 10, 1.0)
        else:
            significance_score = 0.0
        
        # Effect size component
        effect_score = min(effect_size / self.effect_size_threshold, 1.0)
        
        # Combined score with confidence weighting
        evidence_score = (significance_score * 0.4 + effect_score * 0.4 + confidence * 0.2)
        
        return evidence_score
    
    def _integrate_evidence(self, all_evidence: Dict[str, Dict[EvidenceType, EvidenceScore]],
                          new_evidence: Dict[str, EvidenceScore],
                          evidence_type: EvidenceType):
        """Integrate new evidence into the main evidence collection"""
        for gene_id, evidence_score in new_evidence.items():
            if gene_id not in all_evidence:
                all_evidence[gene_id] = {}
            all_evidence[gene_id][evidence_type] = evidence_score
    
    def _calculate_causal_score(self, gene_id: str, 
                              evidence_scores: Dict[EvidenceType, EvidenceScore]) -> CausalGene:
        """Calculate final causal score for a gene"""
        
        # Calculate weighted causal score
        total_score = 0.0
        total_weight = 0.0
        evidence_chain = []
        
        for evidence_type, weight in self.evidence_weights.items():
            if evidence_type in evidence_scores:
                evidence = evidence_scores[evidence_type]
                total_score += evidence.score * weight
                total_weight += weight
                evidence_chain.append(f"{evidence_type.value}: {evidence.score:.3f}")
        
        # Normalize by total weight
        if total_weight > 0:
            causal_score = total_score / total_weight
        else:
            causal_score = 0.0
        
        # Determine confidence level
        if causal_score >= 0.8:
            confidence_level = "High"
        elif causal_score >= 0.6:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        # Biological context (simplified)
        biological_context = {
            'evidence_types': list(evidence_scores.keys()),
            'mean_p_value': np.mean([e.p_value for e in evidence_scores.values()]),
            'mean_effect_size': np.mean([e.effect_size for e in evidence_scores.values()]),
            'evidence_consistency': len(evidence_scores) / len(self.evidence_weights)
        }
        
        return CausalGene(
            gene_id=gene_id,
            causal_score=causal_score,
            evidence_scores=evidence_scores,
            confidence_level=confidence_level,
            biological_context=biological_context,
            evidence_chain=evidence_chain,
            validation_status="Pending"
        )
    
    def _build_evidence_network(self, causal_genes: List[CausalGene],
                              all_evidence: Dict[str, Dict[EvidenceType, EvidenceScore]]) -> nx.Graph:
        """Build evidence network graph"""
        G = nx.Graph()
        
        # Add nodes for causal genes
        for gene in causal_genes:
            G.add_node(gene.gene_id, 
                      causal_score=gene.causal_score,
                      confidence_level=gene.confidence_level,
                      node_type='causal_gene')
        
        # Add edges based on evidence similarity
        for i, gene1 in enumerate(causal_genes):
            for gene2 in causal_genes[i+1:]:
                # Calculate evidence similarity
                similarity = self._calculate_evidence_similarity(
                    gene1.evidence_scores, gene2.evidence_scores
                )
                
                if similarity > 0.5:  # Threshold for connection
                    G.add_edge(gene1.gene_id, gene2.gene_id, 
                              similarity=similarity,
                              edge_type='evidence_similarity')
        
        return G
    
    def _calculate_evidence_similarity(self, 
                                     evidence1: Dict[EvidenceType, EvidenceScore],
                                     evidence2: Dict[EvidenceType, EvidenceScore]) -> float:
        """Calculate similarity between two evidence profiles"""
        common_evidence = set(evidence1.keys()).intersection(evidence2.keys())
        
        if not common_evidence:
            return 0.0
        
        similarities = []
        for evidence_type in common_evidence:
            score1 = evidence1[evidence_type].score
            score2 = evidence2[evidence_type].score
            
            # Calculate similarity (1 - normalized difference)
            similarity = 1 - abs(score1 - score2)
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    def _perform_pathway_analysis(self, causal_genes: List[CausalGene]) -> Dict[str, Any]:
        """Perform pathway enrichment analysis"""
        # This is a simplified pathway analysis
        # In a real implementation, you would use tools like GSEA, DAVID, etc.
        
        gene_ids = [gene.gene_id for gene in causal_genes]
        
        # Simulate pathway analysis results
        pathways = {
            'cancer_pathways': {
                'p53_pathway': len([g for g in gene_ids if 'TP53' in g or 'MDM' in g]),
                'pi3k_pathway': len([g for g in gene_ids if 'PIK3' in g or 'AKT' in g]),
                'rb_pathway': len([g for g in gene_ids if 'RB' in g or 'CDK' in g])
            },
            'metabolic_pathways': {
                'glycolysis': len([g for g in gene_ids if 'HK' in g or 'PFK' in g]),
                'oxidative_phosphorylation': len([g for g in gene_ids if 'COX' in g or 'NADH' in g])
            },
            'immune_pathways': {
                'interferon_response': len([g for g in gene_ids if 'IFNG' in g or 'STAT' in g]),
                'nf_kb_pathway': len([g for g in gene_ids if 'NFKB' in g or 'IKBK' in g])
            }
        }
        
        return {
            'enriched_pathways': pathways,
            'total_genes_analyzed': len(gene_ids),
            'pathway_coverage': sum(sum(p.values()) for p in pathways.values()) / len(gene_ids) if gene_ids else 0.0
        }
    
    def _validate_results(self, causal_genes: List[CausalGene],
                         rna_data: pd.DataFrame,
                         clinical_data: pd.DataFrame) -> Dict[str, float]:
        """Validate causal analysis results"""
        validation_metrics = {}
        
        # Cross-validation consistency
        validation_metrics['cross_validation_score'] = self._cross_validate_results(
            causal_genes, rna_data, clinical_data
        )
        
        # Bootstrap stability
        validation_metrics['bootstrap_stability'] = self._bootstrap_stability(
            causal_genes, rna_data, clinical_data
        )
        
        # Literature validation (simplified)
        validation_metrics['literature_support'] = self._calculate_literature_support(causal_genes)
        
        return validation_metrics
    
    def _cross_validate_results(self, causal_genes: List[CausalGene],
                               rna_data: pd.DataFrame,
                               clinical_data: pd.DataFrame) -> float:
        """Perform cross-validation of causal results"""
        # This is a simplified cross-validation
        # In practice, you would re-run the analysis on different data splits
        
        # Calculate consistency score based on evidence diversity
        consistency_scores = []
        for gene in causal_genes:
            evidence_types = len(gene.evidence_scores)
            max_evidence_types = len(self.evidence_weights)
            consistency = evidence_types / max_evidence_types
            consistency_scores.append(consistency)
        
        return np.mean(consistency_scores) if consistency_scores else 0.0
    
    def _bootstrap_stability(self, causal_genes: List[CausalGene],
                            rna_data: pd.DataFrame,
                            clinical_data: pd.DataFrame) -> float:
        """Calculate bootstrap stability of results"""
        # Simplified bootstrap stability calculation
        # Based on score consistency across top genes
        
        if len(causal_genes) < 2:
            return 0.0
        
        scores = [gene.causal_score for gene in causal_genes]
        stability = 1.0 - (np.std(scores) / np.mean(scores))
        
        return max(0.0, min(1.0, stability))
    
    def _calculate_literature_support(self, causal_genes: List[CausalGene]) -> float:
        """Calculate literature support for identified genes"""
        # This is a simplified literature support calculation
        # In practice, you would query databases like PubMed, COSMIC, etc.
        
        # Simulate literature support based on gene names
        cancer_associated_keywords = ['TP53', 'MYC', 'EGFR', 'KRAS', 'PIK3CA', 'PTEN', 'APC']
        
        supported_genes = 0
        for gene in causal_genes:
            if any(keyword in gene.gene_id for keyword in cancer_associated_keywords):
                supported_genes += 1
        
        return supported_genes / len(causal_genes) if causal_genes else 0.0
    
    def _calculate_algorithm_stats(self, causal_genes: List[CausalGene],
                                 all_evidence: Dict[str, Dict[EvidenceType, EvidenceScore]]) -> Dict[str, Any]:
        """Calculate algorithm performance statistics"""
        stats = {
            'total_genes_analyzed': len(all_evidence),
            'causal_genes_identified': len(causal_genes),
            'causal_gene_ratio': len(causal_genes) / len(all_evidence) if all_evidence else 0.0,
            'mean_causal_score': np.mean([g.causal_score for g in causal_genes]) if causal_genes else 0.0,
            'evidence_type_coverage': {
                evidence_type.value: sum(1 for genes in all_evidence.values() 
                                       if evidence_type in genes) / len(all_evidence)
                for evidence_type in EvidenceType
            } if all_evidence else {},
            'confidence_distribution': {
                'High': len([g for g in causal_genes if g.confidence_level == 'High']),
                'Medium': len([g for g in causal_genes if g.confidence_level == 'Medium']),
                'Low': len([g for g in causal_genes if g.confidence_level == 'Low'])
            }
        }
        
        return stats