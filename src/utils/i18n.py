"""
Internationalization (i18n) module for LIHC Platform
Provides multi-language support with Chinese and English
"""

class I18nManager:
    """Multi-language support manager"""
    
    def __init__(self, default_language='zh'):
        self.current_language = default_language
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """Load translation dictionaries"""
        return {
            'zh': {
                # Navigation
                'nav_overview': '概览',
                'nav_demo': 'Demo结果', 
                'nav_upload': '数据上传',
                'nav_linchpins': 'Linchpin靶点',
                'nav_networks': '网络分析',
                'nav_multidim': '多维度分析',
                'nav_survival': '生存分析',
                'nav_templates': '数据模板',
                
                # Overview page
                'overview_title': 'LIHC多维度预后分析系统',
                'overview_subtitle': '基于多维度网络分析的肝癌预后分析平台',
                'overview_description': '通过五维度肿瘤微环境分析发现关键治疗靶点',
                'from_biomarker_to_targets': '从生物标志物列表到战略靶点',
                'platform_intro': '将传统的并行分析转化为整合的关键节点发现。我们的平台通过同时分析5个生物学维度来识别最关键的治疗靶点。',
                'explore_demo': '探索Demo',
                'upload_data': '上传数据',
                
                # Scoring indicators
                'scoring_guide': '评分指标快速指南',
                'scoring_intro': '平台使用三个核心指标评估基因作为治疗靶点的潜力：',
                'linchpin_score': 'Linchpin Score',
                'linchpin_desc': '综合评分 (0-1)',
                'linchpin_detail': '整合多维度分析结果的最终评分，分数越高表示作为治疗靶点的潜力越大',
                'prognostic_score': 'Prognostic Score', 
                'prognostic_desc': '预后评分 (0-1)',
                'prognostic_detail': '基于Cox回归分析，反映基因表达与患者生存期的关联强度',
                'network_hub_score': 'Network Hub Score',
                'network_desc': '网络中心性评分 (0-1)',
                'network_detail': '在分子相互作用网络中的重要程度，反映基因的连接和调控影响力',
                'usage_tip': '使用提示',
                'usage_detail': '在Demo页面查看详细的计算方法和数据来源说明',
                
                # Platform capabilities
                'platform_capabilities': '平台能力',
                'multidim_analysis': '多维度分析',
                'multidim_desc': '同时分析肿瘤、免疫、基质、ECM和细胞因子维度',
                'network_integration': '网络整合',
                'network_integration_desc': '跨维度网络分析用于中心节点识别',
                'linchpin_scoring': 'Linchpin评分',
                'linchpin_scoring_desc': '治疗优先级的复合评分系统',
                
                # Analysis workflow
                'analysis_workflow': '分析工作流程',
                'data_upload': '数据上传',
                'data_upload_desc': '临床、表达和突变数据',
                'multidim_analysis_step': '多维度分析',
                'multidim_desc_step': '5个维度的并行分析',
                'network_integration_step': '网络整合',
                'network_desc_step': '跨维度网络构建',
                'linchpin_discovery': 'Linchpin发现',
                'linchpin_desc_step': '复合评分和排序',
                
                # Demo page
                'demo_title': 'Demo分析结果',
                'demo_subtitle': '展示平台能力的综合TCGA-LIHC分析',
                'top_linchpin_molecules': 'Top Linchpin分子',
                'no_linchpin_results': '没有可用的linchpin分析结果。运行完整的流程来查看结果。',
                'scoring_explanation': '评分指标说明',
                'calculation_formula': '计算公式',
                'data_source': '数据来源',
                'interpretation_guide': '分数解读指南',
                'score_range': '分数范围: 0.0 - 1.0 (分数越高，作为治疗靶点的潜力越大)',
                'excellent_target': '优秀靶点 (≥0.8): 强烈推荐，具有强证据支持',
                'good_target': '良好靶点 (0.6-0.8): 值得关注，证据较强',
                'potential_target': '潜在靶点 (0.4-0.6): 需要进一步验证',
                'insufficient_evidence': '证据不足 (<0.4): 不推荐作为治疗靶点',
                
                # Multi-dimensional analysis
                'multidim_analysis_title': '多维度分析',
                'tumor_cells': '肿瘤细胞',
                'immune_cells': '免疫细胞', 
                'stromal_cells': '基质细胞',
                'ecm': 'ECM',
                'cytokines': '细胞因子',
                'genes': '基因',
                'factors': '因子',
                'signals': '信号',
                'oncogenes_suppressors': '癌基因和抑制基因',
                'immune_infiltration': '免疫浸润',
                'microenvironment': '微环境',
                'extracellular_matrix': '细胞外基质',
                'signaling_molecules': '信号分子',
                
                # Network analysis
                'network_analysis': '网络分析',
                'network_nodes': '网络节点',
                'connected_genes': '连接基因',
                'hub_genes': '中心基因', 
                'high_centrality': '高中心性',
                'modules': '模块',
                'functional_clusters': '功能簇',
                
                # Survival analysis
                'survival_analysis': '生存分析',
                'target_genes': '目标基因',
                'available_for_analysis': '可用于分析',
                'patient_cohort': '患者队列',
                'tcga_samples': 'TCGA-LIHC样本',
                'analysis_types': '分析类型',
                'os_rfs_endpoints': 'OS和RFS终点',
                'kaplan_meier': 'Kaplan-Meier',
                'with_logrank_test': '配合Log-rank检验',
                'functional_features': '功能特色',
                'survival_features_desc': '为目标基因生成Kaplan-Meier生存曲线，支持总生存期(OS)和无复发生存期(RFS)分析。',
                'analysis_method': '分析方法',
                'analysis_method_desc': '根据基因表达中位数分组，Log-rank检验比较组间差异，P<0.05为统计显著。',
                'try_survival_analysis': '试试生存分析',
                
                # Upload page
                'upload_title': '上传您的数据',
                'upload_subtitle': '上传您的LIHC数据集进行个性化分析',
                'data_requirements': '数据要求',
                'clinical_data': '临床数据',
                'clinical_desc': '患者生存和临床信息 (必需)',
                'expression_data': '表达数据',
                'expression_desc': '基因表达矩阵 (必需)',
                'mutation_data': '突变数据',
                'mutation_desc': '体细胞突变信息 (可选)',
                'drag_drop_files': '拖拽文件到此处或点击浏览',
                'supported_formats': '支持: CSV, TSV, Excel, ZIP',
                'run_analysis': '运行分析',
                
                # Templates page
                'templates_title': '数据模板',
                'templates_subtitle': '下载模板以正确格式化您的数据',
                'clinical_template': '临床数据模板',
                'clinical_template_desc': '患者生存和临床信息',
                'expression_template': '表达数据模板', 
                'expression_template_desc': '基因表达矩阵',
                'mutation_template': '突变数据模板',
                'mutation_template_desc': '体细胞突变信息',
                'download': '下载',
                'required_fields': '必需字段',
                'format_desc': '格式: 基因为行，样本为列',
                
                # Charts and visualization
                'score_comparison_analysis': '评分对比分析',
                'professional_chart_desc': '专业的图表对比分析，提供更直观的数据展示',
                'score_comparison_bar': '评分对比柱状图',
                'multidim_radar': '多维度雷达图',
                'score_correlation_scatter': '评分相关性散点图',
                'multidim_analysis_charts': '多维度分析图表',
                'comprehensive_viz': '五个生物学维度的综合可视化',
                'dimension_distribution': '维度分布',
                'dimension_comparison': '维度对比',
                'network_analysis_charts': '网络分析图表',
                'interactive_network_viz': '交互式网络可视化和中心性分析',
                'centrality_distribution': '中心性分布',
                
                # Gene selection (Survival Analysis)
                'gene_selection': '基因选择',
                'target_gene': '目标基因',
                'dataset': '数据集',
                'generate_survival_curves': '生成生存曲线',
                'grouping_strategy': '分组策略',
                'grouping_desc': '根据选定基因的中位表达水平将患者分为高表达组和低表达组。',
                'analysis_endpoints': '分析终点',
                'overall_survival': '总生存期 (OS)',
                'os_desc': '从诊断到死亡的时间',
                'recurrence_free_survival': '无复发生存期 (RFS)', 
                'rfs_desc': '疾病复发时间',
                'kaplan_meier_method': 'Kaplan-Meier方法',
                'km_desc': '考虑截尾观察的非参数生存概率估计。',
                'logrank_test': 'Log-rank检验',
                'logrank_desc': '表达组间生存曲线的统计比较 (p < 0.05认为显著)。',
                
                # Analysis results
                'analysis_results': '分析结果',
                'kaplan_meier_curves': 'Kaplan-Meier生存曲线',
                'interpretation_guide_title': '解读指南',
                'red_curve': '红色曲线',
                'high_expression_group': '高表达组',
                'blue_curve': '蓝色曲线', 
                'low_expression_group': '低表达组',
                'p_less_005': 'P < 0.05',
                'statistically_significant': '统计学显著差异',
                'higher_curve': '较高曲线',
                'better_survival': '更好的生存概率',
                'clinical_interpretation': '临床解读',
                'prognostic_value': '预后价值',
                'therapeutic_implications': '治疗意义',
                
                # Status indicators
                'total_samples': '总样本数',
                'high_expression': '高表达',
                'low_expression': '低表达',
                'logrank_pvalue': 'Log-rank p值',
                'result': '结果',
                'significant': '显著',
                'not_significant': '不显著',
                'analysis_error': '分析错误',
                'analysis_failed': '分析失败',
                
                # Common terms
                'gene': '基因',
                'score': '评分',
                'samples': '样本',
                'months': '月',
                'probability': '概率',
                'time': '时间',
                'frequency': '频率',
                'distribution': '分布',
                'comparison': '对比',
                'correlation': '相关性',
                'analysis': '分析',
                'visualization': '可视化',
                'interactive': '交互式',
                'professional': '专业',
                'comprehensive': '综合',
                'multiple_formats': '多种格式支持',
                'real_time_validation': '实时验证',
                'quick_navigation': '快速导航'
            },
            
            'en': {
                # Navigation  
                'nav_overview': 'Overview',
                'nav_demo': 'Demo Results',
                'nav_upload': 'Upload Data', 
                'nav_linchpins': 'Linchpins',
                'nav_networks': 'Networks',
                'nav_multidim': 'Multi-dimensional',
                'nav_survival': 'Survival Analysis',
                'nav_templates': 'Templates',
                
                # Overview page
                'overview_title': 'LIHC Multi-dimensional Prognostic Analysis Platform',
                'overview_subtitle': 'Advanced therapeutic target discovery through integrated omics analysis',
                'overview_description': 'Discover key therapeutic targets through five-dimensional tumor microenvironment analysis',
                'from_biomarker_to_targets': 'From Biomarker Lists to Strategic Targets',
                'platform_intro': 'Transform traditional parallel analysis into integrated linchpin discovery. Our platform identifies the most critical therapeutic targets by analyzing 5 biological dimensions simultaneously.',
                'explore_demo': 'Explore Demo',
                'upload_data': 'Upload Data',
                
                # Scoring indicators
                'scoring_guide': 'Quick Scoring Guide',
                'scoring_intro': 'The platform uses three core indicators to assess gene potential as therapeutic targets:',
                'linchpin_score': 'Linchpin Score',
                'linchpin_desc': 'Comprehensive Score (0-1)',
                'linchpin_detail': 'Final score integrating multi-dimensional analysis results, higher scores indicate greater potential as therapeutic targets',
                'prognostic_score': 'Prognostic Score',
                'prognostic_desc': 'Prognostic Score (0-1)', 
                'prognostic_detail': 'Based on Cox regression analysis, reflects the association strength between gene expression and patient survival',
                'network_hub_score': 'Network Hub Score',
                'network_desc': 'Network Centrality Score (0-1)',
                'network_detail': 'Importance in molecular interaction networks, reflecting gene connectivity and regulatory influence',
                'usage_tip': 'Usage Tip',
                'usage_detail': 'View detailed calculation methods and data source descriptions on the Demo page',
                
                # Platform capabilities
                'platform_capabilities': 'Platform Capabilities',
                'multidim_analysis': 'Multi-dimensional Analysis',
                'multidim_desc': 'Simultaneous analysis across tumor, immune, stromal, ECM, and cytokine dimensions',
                'network_integration': 'Network Integration',
                'network_integration_desc': 'Cross-dimensional network analysis for hub identification',
                'linchpin_scoring': 'Linchpin Scoring',
                'linchpin_scoring_desc': 'Composite scoring system for therapeutic prioritization',
                
                # Analysis workflow
                'analysis_workflow': 'Analysis Workflow',
                'data_upload': 'Data Upload',
                'data_upload_desc': 'Clinical, expression, and mutation data',
                'multidim_analysis_step': 'Multi-dimensional Analysis',
                'multidim_desc_step': 'Parallel analysis across 5 dimensions',
                'network_integration_step': 'Network Integration',
                'network_desc_step': 'Cross-dimensional network construction',
                'linchpin_discovery': 'Linchpin Discovery',
                'linchpin_desc_step': 'Composite scoring and ranking',
                
                # Demo page
                'demo_title': 'Demo Analysis Results',
                'demo_subtitle': 'Comprehensive TCGA-LIHC analysis demonstrating platform capabilities',
                'top_linchpin_molecules': 'Top Linchpin Molecules',
                'no_linchpin_results': 'No linchpin analysis results available. Run the complete pipeline to see results.',
                'scoring_explanation': 'Scoring Indicators Explanation',
                'calculation_formula': 'Calculation Formula',
                'data_source': 'Data Source',
                'interpretation_guide': 'Score Interpretation Guide',
                'score_range': 'Score Range: 0.0 - 1.0 (Higher scores indicate greater potential as therapeutic targets)',
                'excellent_target': 'Excellent Targets (≥0.8): Strongly recommended with strong evidence support',
                'good_target': 'Good Targets (0.6-0.8): Worth attention with strong evidence',
                'potential_target': 'Potential Targets (0.4-0.6): Require further validation',
                'insufficient_evidence': 'Insufficient Evidence (<0.4): Not recommended as therapeutic targets',
                
                # Multi-dimensional analysis
                'multidim_analysis_title': 'Multi-dimensional Analysis',
                'tumor_cells': 'Tumor Cells',
                'immune_cells': 'Immune Cells',
                'stromal_cells': 'Stromal Cells', 
                'ecm': 'ECM',
                'cytokines': 'Cytokines',
                'genes': 'genes',
                'factors': 'factors',
                'signals': 'signals',
                'oncogenes_suppressors': 'Oncogenes & suppressors',
                'immune_infiltration': 'Immune infiltration',
                'microenvironment': 'Microenvironment',
                'extracellular_matrix': 'Extracellular matrix',
                'signaling_molecules': 'Signaling molecules',
                
                # Network analysis
                'network_analysis': 'Network Analysis',
                'network_nodes': 'Network Nodes',
                'connected_genes': 'Connected genes',
                'hub_genes': 'Hub Genes',
                'high_centrality': 'High centrality',
                'modules': 'Modules',
                'functional_clusters': 'Functional clusters',
                
                # Survival analysis
                'survival_analysis': 'Survival Analysis',
                'target_genes': 'Target Genes',
                'available_for_analysis': 'Available for analysis',
                'patient_cohort': 'Patient Cohort',
                'tcga_samples': 'TCGA-LIHC samples',
                'analysis_types': 'Analysis Types',
                'os_rfs_endpoints': 'OS & RFS endpoints',
                'kaplan_meier': 'Kaplan-Meier',
                'with_logrank_test': 'With Log-rank test',
                'functional_features': 'Functional Features',
                'survival_features_desc': 'Generate Kaplan-Meier survival curves for target genes, supporting both Overall Survival (OS) and Recurrence-Free Survival (RFS) analysis.',
                'analysis_method': 'Analysis Method',
                'analysis_method_desc': 'Group patients by median gene expression, compare groups using Log-rank test, P<0.05 considered statistically significant.',
                'try_survival_analysis': 'Try Survival Analysis',
                
                # Upload page
                'upload_title': 'Upload Your Data',
                'upload_subtitle': 'Upload your LIHC dataset for personalized analysis',
                'data_requirements': 'Data Requirements',
                'clinical_data': 'Clinical Data',
                'clinical_desc': 'Patient survival and clinical information (required)',
                'expression_data': 'Expression Data',
                'expression_desc': 'Gene expression matrix (required)',
                'mutation_data': 'Mutation Data',
                'mutation_desc': 'Somatic mutation information (optional)',
                'drag_drop_files': 'Drag & drop files here or click to browse',
                'supported_formats': 'Supports: CSV, TSV, Excel, ZIP',
                'run_analysis': 'Run Analysis',
                
                # Templates page
                'templates_title': 'Data Templates',
                'templates_subtitle': 'Download templates to format your data correctly',
                'clinical_template': 'Clinical Data Template',
                'clinical_template_desc': 'Patient survival and clinical information',
                'expression_template': 'Expression Data Template',
                'expression_template_desc': 'Gene expression matrix',
                'mutation_template': 'Mutation Data Template',
                'mutation_template_desc': 'Somatic mutation information',
                'download': 'Download',
                'required_fields': 'Required fields',
                'format_desc': 'Format: Genes as rows, samples as columns',
                
                # Charts and visualization
                'score_comparison_analysis': 'Score Comparison Analysis',
                'professional_chart_desc': 'Professional chart-based comparative analysis for more intuitive data presentation',
                'score_comparison_bar': 'Score Comparison Bar Chart',
                'multidim_radar': 'Multi-dimensional Radar Chart',
                'score_correlation_scatter': 'Score Correlation Scatter Plot',
                'multidim_analysis_charts': 'Multi-dimensional Analysis Charts',
                'comprehensive_viz': 'Comprehensive visualization of five biological dimensions',
                'dimension_distribution': 'Dimension Distribution',
                'dimension_comparison': 'Dimension Comparison',
                'network_analysis_charts': 'Network Analysis Charts',
                'interactive_network_viz': 'Interactive network visualization and centrality analysis',
                'centrality_distribution': 'Centrality Distribution',
                
                # Gene selection (Survival Analysis)
                'gene_selection': 'Gene Selection',
                'target_gene': 'Target Gene',
                'dataset': 'Dataset',
                'generate_survival_curves': 'Generate Survival Curves',
                'grouping_strategy': 'Grouping Strategy',
                'grouping_desc': 'Patients are divided into High and Low expression groups based on the median expression level of the selected gene.',
                'analysis_endpoints': 'Analysis Endpoints',
                'overall_survival': 'Overall Survival (OS)',
                'os_desc': 'Time from diagnosis to death',
                'recurrence_free_survival': 'Recurrence-Free Survival (RFS)',
                'rfs_desc': 'Time to disease recurrence',
                'kaplan_meier_method': 'Kaplan-Meier Method',
                'km_desc': 'Non-parametric survival probability estimation accounting for censored observations.',
                'logrank_test': 'Log-rank Test',
                'logrank_desc': 'Statistical comparison of survival curves between expression groups (p < 0.05 considered significant).',
                
                # Analysis results
                'analysis_results': 'Analysis Results',
                'kaplan_meier_curves': 'Kaplan-Meier Survival Curves',
                'interpretation_guide_title': 'Interpretation Guide',
                'red_curve': 'Red curve',
                'high_expression_group': 'High expression group',
                'blue_curve': 'Blue curve',
                'low_expression_group': 'Low expression group',
                'p_less_005': 'P < 0.05',
                'statistically_significant': 'Statistically significant difference',
                'higher_curve': 'Higher curve',
                'better_survival': 'Better survival probability',
                'clinical_interpretation': 'Clinical Interpretation',
                'prognostic_value': 'Prognostic Value',
                'therapeutic_implications': 'Therapeutic Implications',
                
                # Status indicators
                'total_samples': 'Total Samples',
                'high_expression': 'High Expression',
                'low_expression': 'Low Expression',
                'logrank_pvalue': 'Log-rank p-value',
                'result': 'Result',
                'significant': 'Significant',
                'not_significant': 'Not Significant',
                'analysis_error': 'Analysis Error',
                'analysis_failed': 'Analysis Failed',
                
                # Common terms
                'gene': 'Gene',
                'score': 'Score',
                'samples': 'samples',
                'months': 'months',
                'probability': 'probability',
                'time': 'time',
                'frequency': 'frequency',
                'distribution': 'distribution',
                'comparison': 'comparison',
                'correlation': 'correlation',
                'analysis': 'analysis',
                'visualization': 'visualization',
                'interactive': 'interactive',
                'professional': 'professional',
                'comprehensive': 'comprehensive',
                'multiple_formats': 'Multiple format support',
                'real_time_validation': 'Real-time validation',
                'quick_navigation': 'Quick navigation'
            }
        }
    
    def set_language(self, language):
        """Set current language"""
        if language in self.translations:
            self.current_language = language
            return True
        return False
    
    def get_text(self, key, fallback=None):
        """Get translated text for current language"""
        if fallback is None:
            fallback = key
            
        return self.translations.get(self.current_language, {}).get(key, fallback)
    
    def get_current_language(self):
        """Get current language"""
        return self.current_language
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())

# Global instance
i18n = I18nManager()