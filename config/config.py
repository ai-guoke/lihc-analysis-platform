# LIHC Multi-dimensional Prognostic Analysis System
# Enhanced Configuration file for the integrated decision support system

# ==============================================================================
# DATA SOURCES CONFIGURATION
# ==============================================================================

# Primary data source
TCGA_PROJECT = "TCGA-LIHC"

# Validation datasets for cross-validation
VALIDATION_DATASETS = ["ICGC-LIRI-JP", "GSE14520", "GSE76427"]

# External database URLs (for future integration)
EXTERNAL_DATABASES = {
    "COSMIC": "https://cancer.sanger.ac.uk/cosmic",
    "OncoKB": "https://www.oncokb.org",
    "DrugBank": "https://go.drugbank.com",
    "ChEMBL": "https://www.ebi.ac.uk/chembl"
}

# ==============================================================================
# ANALYSIS PARAMETERS
# ==============================================================================

# Survival analysis thresholds
SURVIVAL_THRESHOLD_YEARS = 5
P_VALUE_THRESHOLD = 0.05
HR_THRESHOLD = 0.2  # Minimum hazard ratio for significance
FDR_THRESHOLD = 0.1  # False discovery rate threshold

# Multiple testing correction method
MULTIPLE_TESTING_METHOD = "benjamini-hochberg"  # or "bonferroni"

# Minimum sample size requirements
MIN_SAMPLE_SIZE = 10
MIN_EVENT_COUNT = 5

# ==============================================================================
# NETWORK ANALYSIS CONFIGURATION
# ==============================================================================

# Correlation and network thresholds
CORRELATION_THRESHOLD = 0.4
CORRELATION_METHOD = "spearman"  # or "pearson"

# WGCNA parameters
WGCNA_POWER = 6
WGCNA_MIN_MODULE_SIZE = 30
WGCNA_DEEP_SPLIT = 2
WGCNA_MERGE_CUT_HEIGHT = 0.25

# Network hub identification
NETWORK_HUB_THRESHOLD = 0.8
CENTRALITY_METHODS = ["degree", "betweenness", "closeness", "eigenvector"]

# Community detection parameters
COMMUNITY_RESOLUTION = 1.0
MIN_COMMUNITY_SIZE = 5

# ==============================================================================
# FIVE DIMENSIONS CONFIGURATION
# ==============================================================================

DIMENSIONS = {
    "tumor_cells": {
        "description": "Tumor intrinsic genes and mutations",
        "methods": ["cox_regression", "mutation_analysis", "cnv_analysis"],
        "gene_sets": [
            "HALLMARK_MYC_TARGETS_V1",
            "HALLMARK_P53_PATHWAY",
            "HALLMARK_PI3K_AKT_MTOR_SIGNALING"
        ],
        "key_genes": ["TP53", "KRAS", "MYC", "EGFR", "BRAF", "PIK3CA"],
        "weight": 0.25
    },
    "immune_cells": {
        "description": "Immune cell infiltration (TAMs, Tregs, CD8+ T cells, etc.)",
        "methods": ["cibersortx", "xcell", "quantiseq", "timer"],
        "cell_types": {
            "TAMs_M1": ["IL1B", "TNF", "IL6", "CXCL10", "CD86"],
            "TAMs_M2": ["ARG1", "IL10", "TGFB1", "MRC1", "CD163"],
            "Tregs": ["FOXP3", "IL10", "TGFB1", "CTLA4", "CD25"],
            "CD8_T": ["CD8A", "CD8B", "GZMB", "PRF1", "IFNG"],
            "CD4_T": ["CD4", "IL2", "IL4", "IL5", "CD40LG"],
            "NK": ["KLRK1", "NCR1", "GZMB", "PRF1", "FCGR3A"],
            "B_cells": ["CD19", "CD20", "IGH", "IGK", "MS4A1"],
            "Neutrophils": ["CXCR2", "FCGR3B", "CSF3R", "CEACAM1"]
        },
        "weight": 0.20
    },
    "stromal_cells": {
        "description": "Cancer-associated fibroblasts (CAFs)",
        "methods": ["xcell", "mcp_counter", "ssgsea"],
        "caf_subtypes": {
            "myCAF": ["ACTA2", "MYL9", "TPM1", "TPM2"],
            "iCAF": ["PDGFRA", "HAS2", "CD34", "LY6C1"],
            "apCAF": ["SLPI", "CFD", "CCL2", "CXCL12"]
        },
        "markers": ["FAP", "ACTA2", "PDPN", "COL1A1", "VIM", "S100A4"],
        "weight": 0.15
    },
    "ecm": {
        "description": "Extracellular matrix remodeling",
        "methods": ["ssgsea", "matrisome_analysis"],
        "gene_sets": {
            "MATRISOME_CORE": ["COL1A1", "COL3A1", "COL4A1", "FN1", "LAMB1"],
            "MATRISOME_ASSOCIATED": ["MMP2", "MMP9", "MMP14", "TIMP1", "TIMP2"],
            "ECM_REMODELING": ["SPARC", "THBS1", "POSTN", "COMP", "SPP1"]
        },
        "pathways": ["ECM_RECEPTOR_INTERACTION", "FOCAL_ADHESION"],
        "weight": 0.20
    },
    "cytokines": {
        "description": "Key cytokines and growth factors",
        "methods": ["gene_expression_analysis", "pathway_analysis"],
        "categories": {
            "pro_inflammatory": ["IL6", "TNF", "IL1B", "IFNG", "IL12A"],
            "anti_inflammatory": ["IL10", "TGFB1", "TGFB2", "IL4", "IL13"],
            "growth_factors": ["VEGFA", "PDGFA", "FGF2", "EGF", "IGF1"],
            "chemokines": ["CCL2", "CXCL8", "CXCL10", "CXCL12", "CCL5"]
        },
        "pathways": ["CYTOKINE_CYTOKINE_RECEPTOR_INTERACTION", "JAK_STAT_SIGNALING"],
        "weight": 0.20
    }
}

# ==============================================================================
# LINCHPIN SCORING CONFIGURATION
# ==============================================================================

# Linchpin scoring weights (must sum to 1.0)
LINCHPIN_WEIGHTS = {
    "prognostic_score": 0.4,      # Clinical prognostic importance
    "network_hub_score": 0.3,     # Network centrality importance
    "cross_domain_score": 0.2,    # Cross-dimensional connectivity
    "regulator_score": 0.1        # Master regulator potential
}

# Scoring normalization methods
SCORE_NORMALIZATION = {
    "prognostic": "log_transform",     # log, sqrt, minmax, zscore
    "network": "minmax",
    "cross_domain": "zscore",
    "regulator": "minmax"
}

# Master regulator identification
MASTER_REGULATOR_CRITERIA = {
    "min_targets": 10,               # Minimum number of target genes
    "target_enrichment_pvalue": 0.01, # P-value for target enrichment
    "tf_databases": ["TRANSFAC", "JASPAR", "ENCODE"]
}

# Druggability assessment
DRUGGABILITY_DATABASES = {
    "drugbank": {
        "weight": 0.4,
        "approved_only": False
    },
    "chembl": {
        "weight": 0.3,
        "activity_threshold": 1000  # nM
    },
    "dgidb": {
        "weight": 0.3,
        "interaction_types": ["inhibitor", "antagonist", "blocker"]
    }
}

# ==============================================================================
# VISUALIZATION CONFIGURATION
# ==============================================================================

# Plot styling
PLOT_STYLE = "seaborn-v0_8"
COLOR_PALETTE = "Set2"
FIGURE_DPI = 300
FIGURE_FORMAT = "png"  # or "pdf", "svg"

# Dashboard settings
DASHBOARD_CONFIG = {
    "theme": "modern",              # modern, classic, dark
    "default_port": 8050,
    "auto_refresh": True,
    "cache_timeout": 3600,          # seconds
    "max_upload_size": 100,         # MB
    "supported_formats": [".csv", ".tsv", ".xlsx", ".zip"]
}

# Network visualization
NETWORK_VIS_CONFIG = {
    "node_size_range": [10, 100],
    "edge_width_range": [1, 10],
    "layout_algorithm": "spring",    # spring, circular, kamada_kawai
    "physics_enabled": True,
    "max_nodes_display": 500
}

# ==============================================================================
# PERFORMANCE CONFIGURATION
# ==============================================================================

# Computational settings
COMPUTE_CONFIG = {
    "n_jobs": -1,                   # Number of parallel jobs (-1 = all cores)
    "random_state": 42,             # For reproducibility
    "batch_size": 1000,             # For large dataset processing
    "memory_limit": "8GB",          # Maximum memory usage
    "use_gpu": False                # GPU acceleration (if available)
}

# Caching settings
CACHE_CONFIG = {
    "enable_caching": True,
    "cache_dir": "cache",
    "max_cache_size": "2GB",
    "cache_expiry": 86400           # seconds (24 hours)
}

# ==============================================================================
# QUALITY CONTROL CONFIGURATION
# ==============================================================================

# Data quality thresholds
QUALITY_THRESHOLDS = {
    "max_missing_rate": 0.2,        # Maximum missing data rate
    "min_variance": 0.01,           # Minimum variance for features
    "max_correlation": 0.95,        # Maximum correlation for feature removal
    "outlier_threshold": 3.0,       # Z-score threshold for outliers
    "min_expression_level": 1.0     # Minimum log2 expression level
}

# Validation settings
VALIDATION_CONFIG = {
    "cross_validation_folds": 5,
    "test_size": 0.2,
    "stratify_by": "os_status",
    "bootstrap_iterations": 1000
}

# ==============================================================================
# OUTPUT CONFIGURATION
# ==============================================================================

# File naming conventions
OUTPUT_NAMING = {
    "timestamp_format": "%Y%m%d_%H%M%S",
    "include_timestamp": True,
    "prefix": "LIHC_analysis",
    "compression": "gzip"           # for large files
}

# Report generation
REPORT_CONFIG = {
    "include_methodology": True,
    "include_code": False,
    "language": "en",               # en, zh
    "format": "html",               # html, pdf, docx
    "template": "standard"          # standard, detailed, summary
}

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",                # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": True,
    "log_file": "logs/lihc_analysis.log",
    "max_log_size": "10MB",
    "backup_count": 5
}

# Progress tracking
PROGRESS_CONFIG = {
    "show_progress_bars": True,
    "update_frequency": 10,         # Update every N iterations
    "time_estimates": True
}

# ==============================================================================
# EXPERIMENTAL FEATURES
# ==============================================================================

# Beta features (use with caution)
EXPERIMENTAL_FEATURES = {
    "deep_learning_integration": False,
    "automated_hyperparameter_tuning": False,
    "real_time_analysis": False,
    "cloud_computation": False
}

# Advanced analytics
ADVANCED_ANALYTICS = {
    "pathway_analysis": True,
    "drug_repurposing": True,
    "biomarker_validation": True,
    "clinical_trials_matching": False
}

# ==============================================================================
# VERSION AND METADATA
# ==============================================================================

# System metadata
SYSTEM_INFO = {
    "version": "1.0.0",
    "build_date": "2024-01-15",
    "author": "LIHC Analysis Team",
    "contact": "support@lihc-analysis.org",
    "citation": "LIHC Multi-dimensional Analysis Platform v1.0 (2024)",
    "license": "MIT"
}