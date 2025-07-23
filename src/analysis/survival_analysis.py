"""
Survival Analysis Module for LIHC Platform
Provides Kaplan-Meier survival curves and Log-rank test functionality
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SurvivalAnalyzer:
    """Survival analysis with Kaplan-Meier curves and Log-rank test"""
    
    def __init__(self):
        self.colors = {
            'high': '#E74C3C',  # Red for high expression
            'low': '#3498DB'    # Blue for low expression
        }
    
    def calculate_kaplan_meier(self, times: np.ndarray, events: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Kaplan-Meier survival probability
        
        Args:
            times: Array of survival times
            events: Array of event indicators (1=event, 0=censored)
            
        Returns:
            Tuple of (unique_times, survival_probabilities)
        """
        # Combine times and events, sort by time
        data = list(zip(times, events))
        data.sort(key=lambda x: x[0])
        
        unique_times = []
        survival_probs = []
        n_at_risk = len(data)
        survival_prob = 1.0
        
        i = 0
        while i < len(data):
            current_time = data[i][0]
            deaths = 0
            censored = 0
            
            # Count deaths and censored at current time
            while i < len(data) and data[i][0] == current_time:
                if data[i][1] == 1:  # Death event
                    deaths += 1
                else:  # Censored
                    censored += 1
                i += 1
            
            if deaths > 0:
                # Update survival probability only if there are deaths
                survival_prob *= (n_at_risk - deaths) / n_at_risk
                unique_times.append(current_time)
                survival_probs.append(survival_prob)
            
            # Update number at risk
            n_at_risk -= (deaths + censored)
        
        return np.array(unique_times), np.array(survival_probs)
    
    def logrank_test(self, group1_times: np.ndarray, group1_events: np.ndarray,
                     group2_times: np.ndarray, group2_events: np.ndarray) -> float:
        """
        Calculate Log-rank test p-value
        
        Args:
            group1_times: Survival times for group 1
            group1_events: Event indicators for group 1
            group2_times: Survival times for group 2  
            group2_events: Event indicators for group 2
            
        Returns:
            P-value from Log-rank test
        """
        try:
            # Combine all unique time points
            all_times = np.unique(np.concatenate([group1_times, group2_times]))
            
            observed_minus_expected = 0
            variance = 0
            
            for t in all_times:
                # Group 1 at risk and events at time t
                g1_at_risk = np.sum(group1_times >= t)
                g1_events_at_t = np.sum((group1_times == t) & (group1_events == 1))
                
                # Group 2 at risk and events at time t
                g2_at_risk = np.sum(group2_times >= t)
                g2_events_at_t = np.sum((group2_times == t) & (group2_events == 1))
                
                # Total at risk and events at time t
                total_at_risk = g1_at_risk + g2_at_risk
                total_events = g1_events_at_t + g2_events_at_t
                
                if total_at_risk > 0 and total_events > 0:
                    # Expected events in group 1
                    expected_g1 = (g1_at_risk / total_at_risk) * total_events
                    
                    # Add to test statistic
                    observed_minus_expected += (g1_events_at_t - expected_g1)
                    
                    # Add to variance
                    if total_at_risk > 1:
                        variance += (g1_at_risk * g2_at_risk * total_events * (total_at_risk - total_events)) / \
                                  (total_at_risk**2 * (total_at_risk - 1))
            
            # Calculate chi-square statistic
            if variance > 0:
                chi_square = (observed_minus_expected**2) / variance
                p_value = 1 - stats.chi2.cdf(chi_square, df=1)
            else:
                p_value = 1.0
                
            return p_value
            
        except Exception as e:
            print(f"Warning: Log-rank test failed: {e}")
            return 1.0
    
    def perform_survival_analysis(self, clinical_data: pd.DataFrame, 
                                expression_data: pd.DataFrame, 
                                gene_name: str,
                                dataset_name: str = "TCGA-LIHC") -> Dict:
        """
        Perform complete survival analysis for a gene
        
        Args:
            clinical_data: DataFrame with columns [sample_id, os_time, os_status, rfs_time, rfs_status]
            expression_data: DataFrame with genes as index and samples as columns
            gene_name: Target gene symbol
            dataset_name: Dataset name for display
            
        Returns:
            Dictionary containing analysis results and plot data
        """
        results = {
            'gene_name': gene_name,
            'dataset_name': dataset_name,
            'os_analysis': {},
            'rfs_analysis': {},
            'error': None
        }
        
        try:
            # Check if gene exists in expression data
            if gene_name not in expression_data.index:
                results['error'] = f"Gene '{gene_name}' not found in expression data"
                return results
            
            # Get gene expression values
            gene_expression = expression_data.loc[gene_name]
            
            # Merge clinical and expression data
            merged_data = clinical_data.copy()
            merged_data['expression'] = merged_data['sample_id'].map(gene_expression)
            
            # Remove samples without expression data
            merged_data = merged_data.dropna(subset=['expression'])
            
            if len(merged_data) < 10:
                results['error'] = f"Insufficient samples with both clinical and expression data (n={len(merged_data)})"
                return results
            
            # Split by median expression - 修正分组逻辑
            median_expr = merged_data['expression'].median()
            merged_data['expression_group'] = merged_data['expression'].apply(
                lambda x: 'High' if x >= median_expr else 'Low'  # 修正：≥中位数为高表达组
            )
            
            # Overall Survival Analysis
            if 'os_time' in merged_data.columns and 'os_status' in merged_data.columns:
                os_data = merged_data.dropna(subset=['os_time', 'os_status'])
                if len(os_data) >= 10:
                    # 重新计算每个分析终点的样本数量
                    os_high_count = sum(os_data['expression_group'] == 'High')
                    os_low_count = sum(os_data['expression_group'] == 'Low')
                    results['os_analysis'] = self._analyze_endpoint(
                        os_data, 'os_time', 'os_status', 
                        'Overall Survival', os_high_count, os_low_count
                    )
            
            # Recurrence-Free Survival Analysis
            if 'rfs_time' in merged_data.columns and 'rfs_status' in merged_data.columns:
                rfs_data = merged_data.dropna(subset=['rfs_time', 'rfs_status'])
                if len(rfs_data) >= 10:
                    # 重新计算每个分析终点的样本数量
                    rfs_high_count = sum(rfs_data['expression_group'] == 'High')
                    rfs_low_count = sum(rfs_data['expression_group'] == 'Low')
                    results['rfs_analysis'] = self._analyze_endpoint(
                        rfs_data, 'rfs_time', 'rfs_status',
                        'Recurrence-Free Survival', rfs_high_count, rfs_low_count
                    )
            
            return results
            
        except Exception as e:
            results['error'] = f"Analysis failed: {str(e)}"
            return results
    
    def _analyze_endpoint(self, data: pd.DataFrame, time_col: str, status_col: str,
                         endpoint_name: str, high_count: int, low_count: int) -> Dict:
        """Analyze a single survival endpoint"""
        
        # Separate high and low expression groups
        high_group = data[data['expression_group'] == 'High']
        low_group = data[data['expression_group'] == 'Low']
        
        # Calculate Kaplan-Meier curves
        high_times, high_survival = self.calculate_kaplan_meier(
            high_group[time_col].values, high_group[status_col].values
        )
        low_times, low_survival = self.calculate_kaplan_meier(
            low_group[time_col].values, low_group[status_col].values
        )
        
        # Log-rank test
        p_value = self.logrank_test(
            high_group[time_col].values, high_group[status_col].values,
            low_group[time_col].values, low_group[status_col].values
        )
        
        return {
            'endpoint_name': endpoint_name,
            'high_times': high_times,
            'high_survival': high_survival,
            'low_times': low_times,
            'low_survival': low_survival,
            'p_value': p_value,
            'high_count': high_count,
            'low_count': low_count,
            'total_samples': len(data)
        }
    
    def create_survival_plots(self, analysis_results: Dict) -> go.Figure:
        """
        Create Kaplan-Meier survival plots
        
        Args:
            analysis_results: Results from perform_survival_analysis
            
        Returns:
            Plotly figure with survival curves
        """
        if analysis_results.get('error'):
            # Return error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {analysis_results['error']}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="red")
            )
            fig.update_layout(
                title=f"Survival Analysis Error",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        # Determine subplot structure
        has_os = bool(analysis_results.get('os_analysis'))
        has_rfs = bool(analysis_results.get('rfs_analysis'))
        
        if has_os and has_rfs:
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=(
                    'Overall Survival (OS)',
                    'Recurrence-Free Survival (RFS)'
                ),
                x_title='Time (months)',
                y_title='Survival Probability'
            )
            plots = [
                (analysis_results['os_analysis'], 1, 1),
                (analysis_results['rfs_analysis'], 1, 2)
            ]
        elif has_os:
            fig = go.Figure()
            fig.update_layout(
                title='Overall Survival (OS)',
                xaxis_title='Time (months)',
                yaxis_title='Survival Probability'
            )
            plots = [(analysis_results['os_analysis'], None, None)]
        elif has_rfs:
            fig = go.Figure()
            fig.update_layout(
                title='Recurrence-Free Survival (RFS)',
                xaxis_title='Time (months)',
                yaxis_title='Survival Probability'
            )
            plots = [(analysis_results['rfs_analysis'], None, None)]
        else:
            # No valid analysis
            fig = go.Figure()
            fig.add_annotation(
                text="No survival data available for analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Add survival curves for each analysis
        for analysis, row, col in plots:
            if not analysis:
                continue
                
            # High expression group
            if len(analysis['high_times']) > 0:
                # Add step function for survival curve
                step_times = []
                step_survival = []
                
                # Start at (0, 1)
                step_times.extend([0, analysis['high_times'][0]])
                step_survival.extend([1, 1])
                
                # Add steps for each event
                for i in range(len(analysis['high_times'])):
                    if i < len(analysis['high_times']) - 1:
                        step_times.extend([analysis['high_times'][i], analysis['high_times'][i+1]])
                        step_survival.extend([analysis['high_survival'][i], analysis['high_survival'][i]])
                    else:
                        # Last point
                        step_times.append(analysis['high_times'][i])
                        step_survival.append(analysis['high_survival'][i])
                
                fig.add_trace(
                    go.Scatter(
                        x=step_times,
                        y=step_survival,
                        mode='lines',
                        name=f'High Expression (n={analysis["high_count"]})',
                        line=dict(color=self.colors['high'], width=3),
                        hovertemplate='Time: %{x:.1f} months<br>Survival: %{y:.3f}<extra></extra>'
                    ),
                    row=row, col=col
                )
            
            # Low expression group
            if len(analysis['low_times']) > 0:
                # Add step function for survival curve
                step_times = []
                step_survival = []
                
                # Start at (0, 1)
                step_times.extend([0, analysis['low_times'][0]])
                step_survival.extend([1, 1])
                
                # Add steps for each event
                for i in range(len(analysis['low_times'])):
                    if i < len(analysis['low_times']) - 1:
                        step_times.extend([analysis['low_times'][i], analysis['low_times'][i+1]])
                        step_survival.extend([analysis['low_survival'][i], analysis['low_survival'][i]])
                    else:
                        # Last point
                        step_times.append(analysis['low_times'][i])
                        step_survival.append(analysis['low_survival'][i])
                
                fig.add_trace(
                    go.Scatter(
                        x=step_times,
                        y=step_survival,
                        mode='lines',
                        name=f'Low Expression (n={analysis["low_count"]})',
                        line=dict(color=self.colors['low'], width=3),
                        hovertemplate='Time: %{x:.1f} months<br>Survival: %{y:.3f}<extra></extra>'
                    ),
                    row=row, col=col
                )
            
            # Add p-value annotation
            p_text = f"Log-rank p = {analysis['p_value']:.4f}"
            if analysis['p_value'] < 0.001:
                p_text = "Log-rank p < 0.001"
            
            # Position annotation based on subplot
            if row and col:  # Subplot
                x_pos = 0.98 if col == 2 else 0.48
                y_pos = 0.12  # 移到图表下方空白区域，避免与曲线重叠
                fig.add_annotation(
                    text=p_text,
                    xref="paper", yref="paper",
                    x=x_pos, y=y_pos, xanchor='right', yanchor='bottom',
                    showarrow=False,
                    font=dict(size=10, color="black"),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="gray",
                    borderwidth=1
                )
            else:  # Single plot
                # 对于单个图表，放在右下角
                fig.add_annotation(
                    text=p_text,
                    xref="paper", yref="paper", 
                    x=0.98, y=0.12, xanchor='right', yanchor='bottom',
                    showarrow=False,
                    font=dict(size=10, color="black"),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="gray",
                    borderwidth=1
                )
        
        # Update layout
        fig.update_layout(
            height=500 if (has_os and has_rfs) else 400,
            title=f"Survival Analysis: {analysis_results['gene_name']} in {analysis_results['dataset_name']}",
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=60, t=80, b=80),  # 增加左边距为Y轴标题留出更多空间
            legend=dict(
                yanchor="top",
                y=0.98,  # 提高图例位置
                xanchor="left", 
                x=0.02,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="gray",
                borderwidth=1
            )
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Time (months)",
            title_standoff=15,  # 增加标题与轴的距离
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='gray'
        )
        fig.update_yaxes(
            title_text="Survival Probability",
            title_standoff=20,  # 增加标题与轴的距离
            range=[0, 1.05],
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='gray'
        )
        
        return fig

def create_demo_survival_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create demo data for survival analysis testing"""
    
    # Create demo clinical data
    np.random.seed(42)  # For reproducible results
    n_samples = 200
    
    clinical_data = pd.DataFrame({
        'sample_id': [f'TCGA-{i:02d}' for i in range(n_samples)],
        'os_time': np.random.exponential(30, n_samples),  # OS time in months
        'os_status': np.random.binomial(1, 0.6, n_samples),  # 60% death rate
        'rfs_time': np.random.exponential(20, n_samples),  # RFS time in months  
        'rfs_status': np.random.binomial(1, 0.7, n_samples),  # 70% recurrence rate
    })
    
    # Create demo expression data
    genes = ['TP53', 'MYC', 'KRAS', 'EGFR', 'VEGFA', 'PIK3CA', 'PTEN', 'CTNNB1']
    expression_data = pd.DataFrame(
        np.random.lognormal(0, 1, (len(genes), n_samples)),
        index=genes,
        columns=clinical_data['sample_id']
    )
    
    return clinical_data, expression_data