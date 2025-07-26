"""
Comprehensive i18n translations for LIHC Platform
完整的LIHC平台多语言翻译
"""

TRANSLATIONS = {
    'zh': {
        # Platform branding
        'platform_name': 'LIHC分析平台',
        'platform_full_name': 'LIHC多维度预后分析系统',
        
        # Navigation - Main
        'nav_overview': '平台概览',
        'nav_upload': '数据上传',
        'nav_dataset_management': '数据集管理',
        'nav_demo': '测试Demo',
        'nav_settings': '系统设置',
        'nav_help': '帮助文档',
        'nav_about': '关于我们',
        
        # Navigation - Analysis Functions
        'section_analysis': '分析功能',
        'nav_multidim': '多维度分析',
        'nav_network': '网络分析',
        'nav_linchpin': 'Linchpin靶点',
        'nav_survival': '生存分析',
        'nav_multiomics': '多组学整合',
        'nav_closedloop': 'ClosedLoop分析',
        
        # Navigation - Precision Medicine
        'section_precision': '精准医学',
        'nav_immune': '免疫微环境',
        'nav_drug': '药物响应预测',
        'nav_subtype': '分子分型',
        'nav_metabolism': '代谢分析',
        'nav_heterogeneity': '异质性分析',
        
        # Navigation - Advanced Analysis
        'section_advanced': '高级分析',
        'nav_charts': '交互式图表',
        'nav_batch': '批量分析',
        'nav_task_queue': '任务队列',
        
        # Common UI Elements
        'btn_submit': '提交',
        'btn_cancel': '取消',
        'btn_save': '保存',
        'btn_reset': '重置',
        'btn_download': '下载',
        'btn_upload': '上传',
        'btn_analyze': '分析',
        'btn_view': '查看',
        'btn_edit': '编辑',
        'btn_delete': '删除',
        'btn_export': '导出',
        'btn_import': '导入',
        'btn_refresh': '刷新',
        'btn_back': '返回',
        'btn_next': '下一步',
        'btn_previous': '上一步',
        'btn_finish': '完成',
        'btn_close': '关闭',
        
        # Status Messages
        'status_loading': '加载中...',
        'status_processing': '处理中...',
        'status_success': '成功',
        'status_error': '错误',
        'status_warning': '警告',
        'status_info': '信息',
        'status_completed': '已完成',
        'status_failed': '失败',
        'status_pending': '等待中',
        'status_running': '运行中',
        
        # Overview Page
        'overview_title': 'LIHC多维度预后分析系统',
        'overview_subtitle': '基于多维度网络分析的肝癌预后分析平台',
        'overview_description': '通过五维度肿瘤微环境分析发现关键治疗靶点',
        'overview_welcome': '欢迎使用LIHC分析平台',
        'overview_intro': '本平台提供全面的肝癌多组学数据分析功能',
        
        # Data Upload Page
        'upload_title': '数据上传',
        'upload_subtitle': '上传您的分析数据',
        'upload_clinical_data': '临床数据',
        'upload_expression_data': '表达数据',
        'upload_mutation_data': '突变数据',
        'upload_cnv_data': '拷贝数变异数据',
        'upload_methylation_data': '甲基化数据',
        'upload_requirements': '数据要求',
        'upload_format': '文件格式',
        'upload_size_limit': '文件大小限制',
        'upload_template': '下载模板',
        'upload_validation': '数据验证',
        'upload_preview': '数据预览',
        
        # Analysis Pages
        'analysis_parameters': '分析参数',
        'analysis_results': '分析结果',
        'analysis_visualization': '可视化',
        'analysis_export': '导出结果',
        'analysis_report': '分析报告',
        'analysis_summary': '分析摘要',
        'analysis_details': '详细信息',
        'analysis_statistics': '统计信息',
        
        # Multi-dimensional Analysis
        'multidim_title': '多维度分析',
        'multidim_subtitle': '五个生物学维度的综合分析',
        'multidim_tumor': '肿瘤细胞维度',
        'multidim_immune': '免疫细胞维度',
        'multidim_stromal': '基质细胞维度',
        'multidim_ecm': 'ECM维度',
        'multidim_cytokine': '细胞因子维度',
        'multidim_score': '维度评分',
        'multidim_heatmap': '维度热图',
        'multidim_comparison': '维度比较',
        
        # Network Analysis
        'network_title': '网络分析',
        'network_subtitle': '分子相互作用网络分析',
        'network_construction': '网络构建',
        'network_visualization': '网络可视化',
        'network_topology': '网络拓扑',
        'network_centrality': '中心性分析',
        'network_module': '模块识别',
        'network_hub_genes': '中心基因',
        'network_edge_weight': '边权重',
        'network_node_degree': '节点度',
        
        # Linchpin Analysis
        'linchpin_title': 'Linchpin靶点',
        'linchpin_subtitle': '关键治疗靶点识别',
        'linchpin_algorithm': 'Linchpin算法',
        'linchpin_score': 'Linchpin评分',
        'linchpin_ranking': '靶点排序',
        'linchpin_evidence': '证据支持',
        'linchpin_validation': '靶点验证',
        'linchpin_druggability': '可成药性',
        
        # Survival Analysis
        'survival_title': '生存分析',
        'survival_subtitle': '预后评估与风险分层',
        'survival_kaplan_meier': 'Kaplan-Meier曲线',
        'survival_cox_regression': 'Cox回归分析',
        'survival_risk_score': '风险评分',
        'survival_risk_groups': '风险分组',
        'survival_hazard_ratio': '风险比',
        'survival_pvalue': 'P值',
        'survival_confidence_interval': '置信区间',
        
        # Multi-omics Integration
        'multiomics_title': '多组学整合',
        'multiomics_subtitle': '多层次数据融合分析',
        'multiomics_data_types': '数据类型',
        'multiomics_integration_method': '整合方法',
        'multiomics_snf': '相似性网络融合',
        'multiomics_mofa': '多组学因子分析',
        'multiomics_clustering': '聚类分析',
        'multiomics_visualization': '整合可视化',
        
        # ClosedLoop Analysis
        'closedloop_title': 'ClosedLoop分析',
        'closedloop_subtitle': '因果推理与验证',
        'closedloop_evidence': '证据链',
        'closedloop_causal_score': '因果评分',
        'closedloop_validation': '循环验证',
        'closedloop_confidence': '置信度',
        'closedloop_pathway': '通路分析',
        
        # Immune Microenvironment
        'immune_title': '免疫微环境',
        'immune_subtitle': '肿瘤免疫浸润分析',
        'immune_infiltration': '免疫浸润',
        'immune_cell_types': '免疫细胞类型',
        'immune_checkpoint': '免疫检查点',
        'immune_score': '免疫评分',
        'immune_subtype': '免疫亚型',
        'immune_therapy_response': '免疫治疗响应',
        
        # Drug Response
        'drug_title': '药物响应预测',
        'drug_subtitle': '个体化用药指导',
        'drug_sensitivity': '药物敏感性',
        'drug_resistance': '药物耐药性',
        'drug_ic50': 'IC50预测',
        'drug_combination': '药物组合',
        'drug_pathway': '药物通路',
        'drug_target': '药物靶点',
        
        # Molecular Subtyping
        'subtype_title': '分子分型',
        'subtype_subtitle': '肿瘤分子亚型识别',
        'subtype_clustering': '聚类分析',
        'subtype_classification': '分型结果',
        'subtype_characteristics': '亚型特征',
        'subtype_survival': '亚型生存',
        'subtype_markers': '标志基因',
        
        # Metabolism Analysis
        'metabolism_title': '代谢分析',
        'metabolism_subtitle': '肿瘤代谢重编程分析',
        'metabolism_pathway': '代谢通路',
        'metabolism_activity': '代谢活性',
        'metabolism_dependency': '代谢依赖',
        'metabolism_target': '代谢靶点',
        'metabolism_immune_crosstalk': '代谢-免疫串扰',
        
        # Heterogeneity Analysis
        'heterogeneity_title': '异质性分析',
        'heterogeneity_subtitle': '肿瘤异质性与进化',
        'heterogeneity_clonal': '克隆结构',
        'heterogeneity_evolution': '进化轨迹',
        'heterogeneity_spatial': '空间异质性',
        'heterogeneity_temporal': '时间异质性',
        'heterogeneity_driver': '驱动事件',
        
        # Settings Page
        'settings_title': '系统设置',
        'settings_language': '语言设置',
        'settings_theme': '主题设置',
        'settings_analysis': '分析参数',
        'settings_visualization': '可视化设置',
        'settings_export': '导出设置',
        'settings_advanced': '高级设置',
        'settings_reset': '恢复默认',
        'settings_save_success': '设置保存成功',
        
        # Error Messages
        'error_file_format': '文件格式错误',
        'error_file_size': '文件大小超出限制',
        'error_data_missing': '缺少必要数据',
        'error_analysis_failed': '分析失败',
        'error_network': '网络连接错误',
        'error_permission': '权限不足',
        'error_unknown': '未知错误',
        
        # Success Messages
        'success_upload': '上传成功',
        'success_analysis': '分析完成',
        'success_export': '导出成功',
        'success_save': '保存成功',
        
        # Info Messages
        'info_processing': '正在处理，请稍候...',
        'info_no_data': '暂无数据',
        'info_select_file': '请选择文件',
        'info_analysis_time': '分析预计需要',
        
        # Table Headers
        'table_gene': '基因',
        'table_score': '评分',
        'table_pvalue': 'P值',
        'table_fdr': 'FDR',
        'table_fold_change': 'Fold Change',
        'table_expression': '表达量',
        'table_survival': '生存期',
        'table_sample': '样本',
        'table_group': '分组',
        'table_action': '操作',
        
        # Chart Labels
        'chart_distribution': '分布图',
        'chart_correlation': '相关性图',
        'chart_heatmap': '热图',
        'chart_volcano': '火山图',
        'chart_scatter': '散点图',
        'chart_bar': '柱状图',
        'chart_line': '折线图',
        'chart_box': '箱线图',
        'chart_network': '网络图',
        
        # Time
        'time_seconds': '秒',
        'time_minutes': '分钟',
        'time_hours': '小时',
        'time_days': '天',
        'time_today': '今天',
        'time_yesterday': '昨天',
        'time_this_week': '本周',
        'time_last_week': '上周',
        'time_this_month': '本月',
        'time_last_month': '上月',
        
        # Scientific Tips
        'scientific_principles': '科学原理',
        'scientific_basis': '科学基础',
        'design_philosophy': '设计理念',
        'mathematical_principle': '数学原理',
        'references': '参考文献',
    },
    
    'en': {
        # Platform branding
        'platform_name': 'LIHC Analysis Platform',
        'platform_full_name': 'LIHC Multi-dimensional Prognostic Analysis System',
        
        # Navigation - Main
        'nav_overview': 'Platform Overview',
        'nav_upload': 'Data Upload',
        'nav_dataset_management': 'Dataset Management',
        'nav_demo': 'Test Demo',
        'nav_settings': 'System Settings',
        'nav_help': 'Help Documentation',
        'nav_about': 'About Us',
        
        # Navigation - Analysis Functions
        'section_analysis': 'Analysis Functions',
        'nav_multidim': 'Multi-dimensional Analysis',
        'nav_network': 'Network Analysis',
        'nav_linchpin': 'Linchpin Targets',
        'nav_survival': 'Survival Analysis',
        'nav_multiomics': 'Multi-omics Integration',
        'nav_closedloop': 'ClosedLoop Analysis',
        
        # Navigation - Precision Medicine
        'section_precision': 'Precision Medicine',
        'nav_immune': 'Immune Microenvironment',
        'nav_drug': 'Drug Response Prediction',
        'nav_subtype': 'Molecular Subtyping',
        'nav_metabolism': 'Metabolism Analysis',
        'nav_heterogeneity': 'Heterogeneity Analysis',
        
        # Navigation - Advanced Analysis
        'section_advanced': 'Advanced Analysis',
        'nav_charts': 'Interactive Charts',
        'nav_batch': 'Batch Analysis',
        'nav_task_queue': 'Task Queue',
        
        # Common UI Elements
        'btn_submit': 'Submit',
        'btn_cancel': 'Cancel',
        'btn_save': 'Save',
        'btn_reset': 'Reset',
        'btn_download': 'Download',
        'btn_upload': 'Upload',
        'btn_analyze': 'Analyze',
        'btn_view': 'View',
        'btn_edit': 'Edit',
        'btn_delete': 'Delete',
        'btn_export': 'Export',
        'btn_import': 'Import',
        'btn_refresh': 'Refresh',
        'btn_back': 'Back',
        'btn_next': 'Next',
        'btn_previous': 'Previous',
        'btn_finish': 'Finish',
        'btn_close': 'Close',
        
        # Status Messages
        'status_loading': 'Loading...',
        'status_processing': 'Processing...',
        'status_success': 'Success',
        'status_error': 'Error',
        'status_warning': 'Warning',
        'status_info': 'Info',
        'status_completed': 'Completed',
        'status_failed': 'Failed',
        'status_pending': 'Pending',
        'status_running': 'Running',
        
        # Overview Page
        'overview_title': 'LIHC Multi-dimensional Prognostic Analysis System',
        'overview_subtitle': 'Liver Cancer Prognostic Analysis Platform Based on Multi-dimensional Network Analysis',
        'overview_description': 'Discover Key Therapeutic Targets Through Five-dimensional Tumor Microenvironment Analysis',
        'overview_welcome': 'Welcome to LIHC Analysis Platform',
        'overview_intro': 'This platform provides comprehensive liver cancer multi-omics data analysis functions',
        
        # Data Upload Page
        'upload_title': 'Data Upload',
        'upload_subtitle': 'Upload Your Analysis Data',
        'upload_clinical_data': 'Clinical Data',
        'upload_expression_data': 'Expression Data',
        'upload_mutation_data': 'Mutation Data',
        'upload_cnv_data': 'CNV Data',
        'upload_methylation_data': 'Methylation Data',
        'upload_requirements': 'Data Requirements',
        'upload_format': 'File Format',
        'upload_size_limit': 'File Size Limit',
        'upload_template': 'Download Template',
        'upload_validation': 'Data Validation',
        'upload_preview': 'Data Preview',
        
        # Analysis Pages
        'analysis_parameters': 'Analysis Parameters',
        'analysis_results': 'Analysis Results',
        'analysis_visualization': 'Visualization',
        'analysis_export': 'Export Results',
        'analysis_report': 'Analysis Report',
        'analysis_summary': 'Analysis Summary',
        'analysis_details': 'Detailed Information',
        'analysis_statistics': 'Statistics',
        
        # Multi-dimensional Analysis
        'multidim_title': 'Multi-dimensional Analysis',
        'multidim_subtitle': 'Comprehensive Analysis of Five Biological Dimensions',
        'multidim_tumor': 'Tumor Cell Dimension',
        'multidim_immune': 'Immune Cell Dimension',
        'multidim_stromal': 'Stromal Cell Dimension',
        'multidim_ecm': 'ECM Dimension',
        'multidim_cytokine': 'Cytokine Dimension',
        'multidim_score': 'Dimension Score',
        'multidim_heatmap': 'Dimension Heatmap',
        'multidim_comparison': 'Dimension Comparison',
        
        # Network Analysis
        'network_title': 'Network Analysis',
        'network_subtitle': 'Molecular Interaction Network Analysis',
        'network_construction': 'Network Construction',
        'network_visualization': 'Network Visualization',
        'network_topology': 'Network Topology',
        'network_centrality': 'Centrality Analysis',
        'network_module': 'Module Identification',
        'network_hub_genes': 'Hub Genes',
        'network_edge_weight': 'Edge Weight',
        'network_node_degree': 'Node Degree',
        
        # Linchpin Analysis
        'linchpin_title': 'Linchpin Targets',
        'linchpin_subtitle': 'Key Therapeutic Target Identification',
        'linchpin_algorithm': 'Linchpin Algorithm',
        'linchpin_score': 'Linchpin Score',
        'linchpin_ranking': 'Target Ranking',
        'linchpin_evidence': 'Evidence Support',
        'linchpin_validation': 'Target Validation',
        'linchpin_druggability': 'Druggability',
        
        # Survival Analysis
        'survival_title': 'Survival Analysis',
        'survival_subtitle': 'Prognostic Assessment and Risk Stratification',
        'survival_kaplan_meier': 'Kaplan-Meier Curve',
        'survival_cox_regression': 'Cox Regression Analysis',
        'survival_risk_score': 'Risk Score',
        'survival_risk_groups': 'Risk Groups',
        'survival_hazard_ratio': 'Hazard Ratio',
        'survival_pvalue': 'P-value',
        'survival_confidence_interval': 'Confidence Interval',
        
        # Multi-omics Integration
        'multiomics_title': 'Multi-omics Integration',
        'multiomics_subtitle': 'Multi-level Data Fusion Analysis',
        'multiomics_data_types': 'Data Types',
        'multiomics_integration_method': 'Integration Method',
        'multiomics_snf': 'Similarity Network Fusion',
        'multiomics_mofa': 'Multi-Omics Factor Analysis',
        'multiomics_clustering': 'Clustering Analysis',
        'multiomics_visualization': 'Integration Visualization',
        
        # ClosedLoop Analysis
        'closedloop_title': 'ClosedLoop Analysis',
        'closedloop_subtitle': 'Causal Inference and Validation',
        'closedloop_evidence': 'Evidence Chain',
        'closedloop_causal_score': 'Causal Score',
        'closedloop_validation': 'Circular Validation',
        'closedloop_confidence': 'Confidence',
        'closedloop_pathway': 'Pathway Analysis',
        
        # Immune Microenvironment
        'immune_title': 'Immune Microenvironment',
        'immune_subtitle': 'Tumor Immune Infiltration Analysis',
        'immune_infiltration': 'Immune Infiltration',
        'immune_cell_types': 'Immune Cell Types',
        'immune_checkpoint': 'Immune Checkpoint',
        'immune_score': 'Immune Score',
        'immune_subtype': 'Immune Subtype',
        'immune_therapy_response': 'Immunotherapy Response',
        
        # Drug Response
        'drug_title': 'Drug Response Prediction',
        'drug_subtitle': 'Personalized Medication Guidance',
        'drug_sensitivity': 'Drug Sensitivity',
        'drug_resistance': 'Drug Resistance',
        'drug_ic50': 'IC50 Prediction',
        'drug_combination': 'Drug Combination',
        'drug_pathway': 'Drug Pathway',
        'drug_target': 'Drug Target',
        
        # Molecular Subtyping
        'subtype_title': 'Molecular Subtyping',
        'subtype_subtitle': 'Tumor Molecular Subtype Identification',
        'subtype_clustering': 'Clustering Analysis',
        'subtype_classification': 'Classification Results',
        'subtype_characteristics': 'Subtype Characteristics',
        'subtype_survival': 'Subtype Survival',
        'subtype_markers': 'Marker Genes',
        
        # Metabolism Analysis
        'metabolism_title': 'Metabolism Analysis',
        'metabolism_subtitle': 'Tumor Metabolic Reprogramming Analysis',
        'metabolism_pathway': 'Metabolic Pathway',
        'metabolism_activity': 'Metabolic Activity',
        'metabolism_dependency': 'Metabolic Dependency',
        'metabolism_target': 'Metabolic Target',
        'metabolism_immune_crosstalk': 'Metabolism-Immune Crosstalk',
        
        # Heterogeneity Analysis
        'heterogeneity_title': 'Heterogeneity Analysis',
        'heterogeneity_subtitle': 'Tumor Heterogeneity and Evolution',
        'heterogeneity_clonal': 'Clonal Structure',
        'heterogeneity_evolution': 'Evolution Trajectory',
        'heterogeneity_spatial': 'Spatial Heterogeneity',
        'heterogeneity_temporal': 'Temporal Heterogeneity',
        'heterogeneity_driver': 'Driver Events',
        
        # Settings Page
        'settings_title': 'System Settings',
        'settings_language': 'Language Settings',
        'settings_theme': 'Theme Settings',
        'settings_analysis': 'Analysis Parameters',
        'settings_visualization': 'Visualization Settings',
        'settings_export': 'Export Settings',
        'settings_advanced': 'Advanced Settings',
        'settings_reset': 'Reset to Default',
        'settings_save_success': 'Settings Saved Successfully',
        
        # Error Messages
        'error_file_format': 'Invalid File Format',
        'error_file_size': 'File Size Exceeds Limit',
        'error_data_missing': 'Required Data Missing',
        'error_analysis_failed': 'Analysis Failed',
        'error_network': 'Network Connection Error',
        'error_permission': 'Insufficient Permission',
        'error_unknown': 'Unknown Error',
        
        # Success Messages
        'success_upload': 'Upload Successful',
        'success_analysis': 'Analysis Complete',
        'success_export': 'Export Successful',
        'success_save': 'Save Successful',
        
        # Info Messages
        'info_processing': 'Processing, please wait...',
        'info_no_data': 'No Data Available',
        'info_select_file': 'Please Select a File',
        'info_analysis_time': 'Analysis estimated time',
        
        # Table Headers
        'table_gene': 'Gene',
        'table_score': 'Score',
        'table_pvalue': 'P-value',
        'table_fdr': 'FDR',
        'table_fold_change': 'Fold Change',
        'table_expression': 'Expression',
        'table_survival': 'Survival',
        'table_sample': 'Sample',
        'table_group': 'Group',
        'table_action': 'Action',
        
        # Chart Labels
        'chart_distribution': 'Distribution Plot',
        'chart_correlation': 'Correlation Plot',
        'chart_heatmap': 'Heatmap',
        'chart_volcano': 'Volcano Plot',
        'chart_scatter': 'Scatter Plot',
        'chart_bar': 'Bar Chart',
        'chart_line': 'Line Chart',
        'chart_box': 'Box Plot',
        'chart_network': 'Network Graph',
        
        # Time
        'time_seconds': 'seconds',
        'time_minutes': 'minutes',
        'time_hours': 'hours',
        'time_days': 'days',
        'time_today': 'Today',
        'time_yesterday': 'Yesterday',
        'time_this_week': 'This Week',
        'time_last_week': 'Last Week',
        'time_this_month': 'This Month',
        'time_last_month': 'Last Month',
        
        # Scientific Tips
        'scientific_principles': 'Scientific Principles',
        'scientific_basis': 'Scientific Basis',
        'design_philosophy': 'Design Philosophy',
        'mathematical_principle': 'Mathematical Principle',
        'references': 'References',
    }
}