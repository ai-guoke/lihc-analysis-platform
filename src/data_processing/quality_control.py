"""
Data Quality Control System for Multi-omics Data
Implements comprehensive quality assessment and correction methods
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import warnings

from ..utils.logging_system import LIHCLogger
from ..utils.enhanced_config import get_analysis_config


class QualityIssue(Enum):
    """Types of quality issues"""
    HIGH_MISSING_RATE = "high_missing_rate"
    OUTLIER_SAMPLES = "outlier_samples"
    BATCH_EFFECTS = "batch_effects"
    LOW_VARIANCE = "low_variance"
    DUPLICATES = "duplicates"
    EXTREME_VALUES = "extreme_values"
    INCONSISTENT_NAMING = "inconsistent_naming"


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    dataset_name: str
    sample_count: int
    feature_count: int
    missing_rate: float
    outlier_samples: List[str]
    low_variance_features: List[str]
    duplicate_samples: List[str]
    extreme_values_count: int
    batch_effects_detected: bool
    overall_quality_score: float
    issues: List[QualityIssue]
    recommendations: List[str]
    plots_generated: List[str]


class DataQualityController:
    """Comprehensive data quality control system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.analysis_config = get_analysis_config()
        self.logger = LIHCLogger(name="DataQualityController")
        
        # Quality thresholds
        self.missing_rate_threshold = self.config.get('missing_rate_threshold', 0.2)
        self.outlier_threshold = self.config.get('outlier_threshold', 3.0)
        self.low_variance_percentile = self.config.get('low_variance_percentile', 5)
        self.extreme_value_threshold = self.config.get('extreme_value_threshold', 5.0)
        
        # Correction settings
        self.apply_corrections = self.config.get('apply_corrections', True)
        self.imputation_method = self.config.get('imputation_method', 'mean')
        self.outlier_method = self.config.get('outlier_method', 'clip')
        
        self.logger.info("Data Quality Controller initialized")
    
    def assess_data_quality(self, 
                           data: pd.DataFrame,
                           dataset_name: str = "Unknown",
                           generate_plots: bool = True,
                           output_dir: Optional[str] = None) -> QualityReport:
        """Comprehensive data quality assessment"""
        
        self.logger.info(f"Starting quality assessment for dataset: {dataset_name}")
        
        # Initialize report
        issues = []
        recommendations = []
        plots_generated = []
        
        # Basic statistics
        sample_count = data.shape[0]
        feature_count = data.shape[1]
        
        # Missing data analysis
        missing_rate = self._assess_missing_data(data)
        if missing_rate > self.missing_rate_threshold:
            issues.append(QualityIssue.HIGH_MISSING_RATE)
            recommendations.append(f"Consider imputation or removal of features with >20% missing values")
        
        # Outlier detection
        outlier_samples = self._detect_outlier_samples(data)
        if len(outlier_samples) > 0:
            issues.append(QualityIssue.OUTLIER_SAMPLES)
            recommendations.append(f"Investigate {len(outlier_samples)} outlier samples")
        
        # Variance analysis
        low_variance_features = self._detect_low_variance_features(data)
        if len(low_variance_features) > 0:
            issues.append(QualityIssue.LOW_VARIANCE)
            recommendations.append(f"Consider removing {len(low_variance_features)} low-variance features")
        
        # Duplicate detection
        duplicate_samples = self._detect_duplicate_samples(data)
        if len(duplicate_samples) > 0:
            issues.append(QualityIssue.DUPLICATES)
            recommendations.append(f"Remove {len(duplicate_samples)} duplicate samples")
        
        # Extreme values
        extreme_values_count = self._detect_extreme_values(data)
        if extreme_values_count > sample_count * feature_count * 0.01:
            issues.append(QualityIssue.EXTREME_VALUES)
            recommendations.append("Consider clipping or transforming extreme values")
        
        # Batch effects (simplified detection)
        batch_effects_detected = self._detect_batch_effects(data)
        if batch_effects_detected:
            issues.append(QualityIssue.BATCH_EFFECTS)
            recommendations.append("Consider batch correction methods")
        
        # Calculate overall quality score
        overall_quality_score = self._calculate_quality_score(
            missing_rate, len(outlier_samples), len(low_variance_features),
            len(duplicate_samples), extreme_values_count, sample_count, feature_count
        )
        
        # Generate plots if requested
        if generate_plots and output_dir:
            plots_generated = self._generate_quality_plots(data, dataset_name, output_dir)
        
        # Create report
        report = QualityReport(
            dataset_name=dataset_name,
            sample_count=sample_count,
            feature_count=feature_count,
            missing_rate=missing_rate,
            outlier_samples=outlier_samples,
            low_variance_features=low_variance_features,
            duplicate_samples=duplicate_samples,
            extreme_values_count=extreme_values_count,
            batch_effects_detected=batch_effects_detected,
            overall_quality_score=overall_quality_score,
            issues=issues,
            recommendations=recommendations,
            plots_generated=plots_generated
        )
        
        self.logger.info(f"Quality assessment completed. Overall score: {overall_quality_score:.2f}")
        return report
    
    def correct_data_quality(self, 
                            data: pd.DataFrame,
                            quality_report: QualityReport) -> pd.DataFrame:
        """Apply quality corrections based on assessment"""
        
        if not self.apply_corrections:
            self.logger.info("Quality corrections disabled")
            return data
        
        corrected_data = data.copy()
        corrections_applied = []
        
        # Remove duplicate samples
        if QualityIssue.DUPLICATES in quality_report.issues:
            corrected_data = corrected_data.drop_duplicates()
            corrections_applied.append("Removed duplicate samples")
        
        # Remove low-variance features
        if QualityIssue.LOW_VARIANCE in quality_report.issues:
            corrected_data = corrected_data.drop(columns=quality_report.low_variance_features)
            corrections_applied.append(f"Removed {len(quality_report.low_variance_features)} low-variance features")
        
        # Handle missing values
        if QualityIssue.HIGH_MISSING_RATE in quality_report.issues:
            corrected_data = self._impute_missing_values(corrected_data)
            corrections_applied.append(f"Imputed missing values using {self.imputation_method} method")
        
        # Handle extreme values
        if QualityIssue.EXTREME_VALUES in quality_report.issues:
            corrected_data = self._handle_extreme_values(corrected_data)
            corrections_applied.append("Clipped extreme values")
        
        # Handle outlier samples (optional - requires careful consideration)
        if QualityIssue.OUTLIER_SAMPLES in quality_report.issues and self.config.get('remove_outliers', False):
            corrected_data = corrected_data.drop(index=quality_report.outlier_samples, errors='ignore')
            corrections_applied.append(f"Removed {len(quality_report.outlier_samples)} outlier samples")
        
        self.logger.info(f"Applied corrections: {', '.join(corrections_applied)}")
        return corrected_data
    
    def _assess_missing_data(self, data: pd.DataFrame) -> float:
        """Assess missing data patterns"""
        total_values = data.shape[0] * data.shape[1]
        missing_values = data.isnull().sum().sum()
        missing_rate = missing_values / total_values
        
        self.logger.debug(f"Missing data rate: {missing_rate:.2%}")
        return missing_rate
    
    def _detect_outlier_samples(self, data: pd.DataFrame) -> List[str]:
        """Detect outlier samples using multiple methods"""
        outliers = set()
        
        # Method 1: Z-score based detection
        z_scores = np.abs(stats.zscore(data, axis=1, nan_policy='omit'))
        z_outliers = data.index[np.any(z_scores > self.outlier_threshold, axis=1)]
        outliers.update(z_outliers)
        
        # Method 2: IQR based detection
        Q1 = data.quantile(0.25, axis=1)
        Q3 = data.quantile(0.75, axis=1)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        for idx in data.index:
            sample_data = data.loc[idx]
            if np.any(sample_data < lower_bound[idx]) or np.any(sample_data > upper_bound[idx]):
                outliers.add(idx)
        
        # Method 3: PCA-based detection (if sufficient features)
        if data.shape[1] > 10:
            try:
                # Standardize data
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(data.fillna(data.mean()))
                
                # PCA
                pca = PCA(n_components=min(10, data.shape[1]))
                pca_scores = pca.fit_transform(scaled_data)
                
                # Detect outliers in PCA space
                distances = np.sqrt(np.sum(pca_scores**2, axis=1))
                distance_threshold = np.percentile(distances, 95)
                pca_outliers = data.index[distances > distance_threshold]
                outliers.update(pca_outliers)
                
            except Exception as e:
                self.logger.warning(f"PCA-based outlier detection failed: {e}")
        
        return list(outliers)
    
    def _detect_low_variance_features(self, data: pd.DataFrame) -> List[str]:
        """Detect features with low variance"""
        variances = data.var(axis=0, skipna=True)
        variance_threshold = np.percentile(variances.dropna(), self.low_variance_percentile)
        
        low_variance_features = variances[variances < variance_threshold].index.tolist()
        return low_variance_features
    
    def _detect_duplicate_samples(self, data: pd.DataFrame) -> List[str]:
        """Detect duplicate samples"""
        duplicates = data.duplicated(keep='first')
        duplicate_samples = data.index[duplicates].tolist()
        return duplicate_samples
    
    def _detect_extreme_values(self, data: pd.DataFrame) -> int:
        """Detect extreme values using modified z-score"""
        # Calculate modified z-score (more robust to outliers)
        median = data.median(axis=0)
        mad = np.median(np.abs(data - median), axis=0)
        
        # Avoid division by zero
        mad = pd.Series(mad, index=data.columns)
        mad = mad.replace(0, np.nan)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            modified_z_scores = 0.6745 * (data - median) / mad
        
        extreme_values = np.abs(modified_z_scores) > self.extreme_value_threshold
        return extreme_values.sum().sum()
    
    def _detect_batch_effects(self, data: pd.DataFrame) -> bool:
        """Simplified batch effect detection"""
        # This is a simplified approach - in practice, you'd need batch information
        # Here we look for systematic patterns that might indicate batch effects
        
        try:
            # Check for clustering patterns using PCA
            if data.shape[1] > 10:
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(data.fillna(data.mean()))
                
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(scaled_data)
                
                # Use DBSCAN to detect potential batch clusters
                clustering = DBSCAN(eps=0.5, min_samples=5)
                clusters = clustering.fit_predict(pca_result)
                
                # If we detect distinct clusters, it might indicate batch effects
                n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
                
                return n_clusters > 1
            
        except Exception as e:
            self.logger.warning(f"Batch effect detection failed: {e}")
        
        return False
    
    def _calculate_quality_score(self, missing_rate: float, outlier_count: int,
                                low_variance_count: int, duplicate_count: int,
                                extreme_values_count: int, sample_count: int,
                                feature_count: int) -> float:
        """Calculate overall quality score (0-1, higher is better)"""
        
        # Individual penalties
        missing_penalty = min(missing_rate * 2, 0.4)
        outlier_penalty = min(outlier_count / sample_count, 0.2)
        low_variance_penalty = min(low_variance_count / feature_count, 0.2)
        duplicate_penalty = min(duplicate_count / sample_count, 0.1)
        extreme_penalty = min(extreme_values_count / (sample_count * feature_count * 100), 0.1)
        
        # Calculate final score
        total_penalty = (missing_penalty + outlier_penalty + low_variance_penalty + 
                        duplicate_penalty + extreme_penalty)
        
        quality_score = max(0.0, 1.0 - total_penalty)
        return quality_score
    
    def _impute_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values using specified method"""
        if self.imputation_method == 'mean':
            return data.fillna(data.mean())
        elif self.imputation_method == 'median':
            return data.fillna(data.median())
        elif self.imputation_method == 'mode':
            return data.fillna(data.mode().iloc[0])
        elif self.imputation_method == 'forward':
            return data.fillna(method='ffill')
        elif self.imputation_method == 'backward':
            return data.fillna(method='bfill')
        else:
            self.logger.warning(f"Unknown imputation method: {self.imputation_method}. Using mean.")
            return data.fillna(data.mean())
    
    def _handle_extreme_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle extreme values using specified method"""
        if self.outlier_method == 'clip':
            # Clip to 99th percentile
            lower_bound = data.quantile(0.01)
            upper_bound = data.quantile(0.99)
            return data.clip(lower=lower_bound, upper=upper_bound, axis=1)
        elif self.outlier_method == 'winsorize':
            # Winsorize at 5% and 95% percentiles
            from scipy.stats import mstats
            return data.apply(lambda x: mstats.winsorize(x, limits=[0.05, 0.05]), axis=0)
        else:
            self.logger.warning(f"Unknown outlier method: {self.outlier_method}. Using clipping.")
            lower_bound = data.quantile(0.01)
            upper_bound = data.quantile(0.99)
            return data.clip(lower=lower_bound, upper=upper_bound, axis=1)
    
    def _generate_quality_plots(self, data: pd.DataFrame, dataset_name: str, output_dir: str) -> List[str]:
        """Generate quality assessment plots"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        plots_generated = []
        
        try:
            # 1. Missing data heatmap
            plt.figure(figsize=(12, 8))
            missing_data = data.isnull()
            
            if missing_data.any().any():
                sns.heatmap(missing_data.iloc[:, :50], cbar=True, cmap='viridis')
                plt.title(f'Missing Data Pattern - {dataset_name}')
                plt.xlabel('Features (first 50)')
                plt.ylabel('Samples')
                
                plot_path = output_path / f'{dataset_name}_missing_data.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plots_generated.append(str(plot_path))
                plt.close()
            
            # 2. Data distribution
            plt.figure(figsize=(12, 6))
            
            # Sample some features for visualization
            sample_features = data.columns[:min(5, len(data.columns))]
            for i, feature in enumerate(sample_features):
                plt.subplot(2, 3, i+1)
                data[feature].hist(bins=50, alpha=0.7)
                plt.title(f'{feature}')
                plt.xlabel('Value')
                plt.ylabel('Frequency')
            
            plt.tight_layout()
            plot_path = output_path / f'{dataset_name}_distributions.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plots_generated.append(str(plot_path))
            plt.close()
            
            # 3. PCA plot (if sufficient features)
            if data.shape[1] > 2:
                plt.figure(figsize=(10, 8))
                
                # Prepare data for PCA
                pca_data = data.fillna(data.mean())
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(pca_data)
                
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(scaled_data)
                
                plt.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.6)
                plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
                plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
                plt.title(f'PCA - {dataset_name}')
                
                plot_path = output_path / f'{dataset_name}_pca.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plots_generated.append(str(plot_path))
                plt.close()
            
            # 4. Correlation heatmap (for subset of features)
            if data.shape[1] > 1:
                plt.figure(figsize=(10, 8))
                
                # Sample features for correlation
                sample_size = min(20, data.shape[1])
                sampled_features = data.iloc[:, :sample_size]
                
                corr_matrix = sampled_features.corr()
                sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0)
                plt.title(f'Feature Correlation - {dataset_name}')
                
                plot_path = output_path / f'{dataset_name}_correlation.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plots_generated.append(str(plot_path))
                plt.close()
            
        except Exception as e:
            self.logger.error(f"Error generating plots: {e}")
        
        return plots_generated
    
    def generate_quality_report_html(self, reports: List[QualityReport], output_path: str):
        """Generate HTML quality report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Quality Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .report-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .quality-score {{ font-size: 24px; font-weight: bold; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
                .issue-list {{ margin: 10px 0; }}
                .recommendation {{ background: #f0f8ff; padding: 10px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Multi-omics Data Quality Report</h1>
            <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        for report in reports:
            # Determine quality level
            if report.overall_quality_score >= 0.8:
                quality_class = "good"
                quality_text = "Excellent"
            elif report.overall_quality_score >= 0.6:
                quality_class = "warning"
                quality_text = "Good"
            else:
                quality_class = "error"
                quality_text = "Needs Attention"
            
            html_content += f"""
            <div class="report-section">
                <h2>{report.dataset_name}</h2>
                <div class="quality-score {quality_class}">
                    Overall Quality: {report.overall_quality_score:.2f} ({quality_text})
                </div>
                
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Samples</td><td>{report.sample_count}</td></tr>
                    <tr><td>Features</td><td>{report.feature_count}</td></tr>
                    <tr><td>Missing Rate</td><td>{report.missing_rate:.2%}</td></tr>
                    <tr><td>Outlier Samples</td><td>{len(report.outlier_samples)}</td></tr>
                    <tr><td>Low Variance Features</td><td>{len(report.low_variance_features)}</td></tr>
                    <tr><td>Duplicate Samples</td><td>{len(report.duplicate_samples)}</td></tr>
                </table>
                
                <h3>Issues Detected</h3>
                <div class="issue-list">
            """
            
            for issue in report.issues:
                html_content += f"<li>{issue.value.replace('_', ' ').title()}</li>"
            
            html_content += """
                </div>
                
                <h3>Recommendations</h3>
            """
            
            for rec in report.recommendations:
                html_content += f'<div class="recommendation">{rec}</div>'
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"Quality report saved to {output_path}")