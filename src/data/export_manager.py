"""
Data Export Manager for LIHC Platform
Handles export of analysis results in various formats
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
import zipfile
import io
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from src.analysis.closedloop_analyzer import ClosedLoopResult, CausalGene
from src.data_processing.multi_omics_loader import IntegrationResult
from src.utils.logging_system import LIHCLogger


class ExportFormat(Enum):
    """Export format enumeration"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"
    TSV = "tsv"
    BIOM = "biom"
    GCT = "gct"


class ReportType(Enum):
    """Report type enumeration"""
    SUMMARY = "summary"
    DETAILED = "detailed"
    PUBLICATION = "publication"
    DASHBOARD = "dashboard"


@dataclass
class ExportOptions:
    """Export configuration options"""
    format: ExportFormat
    include_metadata: bool = True
    include_plots: bool = True
    include_quality_metrics: bool = True
    include_raw_data: bool = False
    compress: bool = True
    report_type: ReportType = ReportType.SUMMARY
    custom_filters: Optional[Dict[str, Any]] = None


class DataExportManager:
    """Manages data export functionality"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = LIHCLogger(name="DataExport")
        
        # Configure matplotlib for non-GUI backend
        plt.switch_backend('Agg')
        
        self.logger.info(f"Data export manager initialized with output directory: {self.output_dir}")
    
    def export_analysis_results(self, 
                               results: Union[ClosedLoopResult, IntegrationResult, Dict[str, Any]],
                               analysis_id: str,
                               options: ExportOptions) -> str:
        """Export analysis results in specified format"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_name = f"analysis_{analysis_id}_{timestamp}"
        
        self.logger.info(f"Exporting analysis results: {analysis_id} in {options.format.value} format")
        
        if isinstance(results, ClosedLoopResult):
            return self._export_closedloop_results(results, export_name, options)
        elif isinstance(results, IntegrationResult):
            return self._export_integration_results(results, export_name, options)
        else:
            return self._export_generic_results(results, export_name, options)
    
    def _export_closedloop_results(self, 
                                  results: ClosedLoopResult, 
                                  export_name: str, 
                                  options: ExportOptions) -> str:
        """Export ClosedLoop analysis results"""
        
        export_dir = self.output_dir / export_name
        export_dir.mkdir(exist_ok=True)
        
        # Export causal genes
        causal_genes_df = self._create_causal_genes_dataframe(results.causal_genes)
        
        if options.format == ExportFormat.CSV:
            output_path = export_dir / "causal_genes.csv"
            causal_genes_df.to_csv(output_path, index=False)
        elif options.format == ExportFormat.EXCEL:
            output_path = export_dir / "analysis_results.xlsx"
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                causal_genes_df.to_excel(writer, sheet_name='Causal_Genes', index=False)
                
                # Add validation metrics
                if options.include_quality_metrics:
                    metrics_df = pd.DataFrame([results.validation_metrics])
                    metrics_df.to_excel(writer, sheet_name='Validation_Metrics', index=False)
                
                # Add algorithm statistics
                stats_df = pd.DataFrame([results.algorithm_stats])
                stats_df.to_excel(writer, sheet_name='Algorithm_Stats', index=False)
        
        elif options.format == ExportFormat.JSON:
            output_path = export_dir / "results.json"
            export_data = {
                "analysis_type": "closedloop",
                "causal_genes": [asdict(gene) for gene in results.causal_genes],
                "validation_metrics": results.validation_metrics,
                "algorithm_stats": results.algorithm_stats,
                "export_timestamp": datetime.now().isoformat()
            }
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        # Generate plots if requested
        if options.include_plots:
            self._generate_closedloop_plots(results, export_dir)
        
        # Generate PDF report if requested
        if options.format == ExportFormat.PDF:
            output_path = self._generate_closedloop_pdf_report(results, export_dir, options.report_type)
        
        # Create compressed archive if requested
        if options.compress:
            return self._create_archive(export_dir, export_name)
        
        return str(export_dir)
    
    def _export_integration_results(self, 
                                   results: IntegrationResult, 
                                   export_name: str, 
                                   options: ExportOptions) -> str:
        """Export multi-omics integration results"""
        
        export_dir = self.output_dir / export_name
        export_dir.mkdir(exist_ok=True)
        
        # Export integrated expression matrix
        if options.format == ExportFormat.CSV:
            output_path = export_dir / "integrated_expression.csv"
            results.integrated_expression.to_csv(output_path)
        elif options.format == ExportFormat.EXCEL:
            output_path = export_dir / "integration_results.xlsx"
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                results.integrated_expression.to_excel(writer, sheet_name='Integrated_Expression')
                
                if hasattr(results, 'sample_metadata'):
                    results.sample_metadata.to_excel(writer, sheet_name='Sample_Metadata', index=False)
                
                if options.include_quality_metrics and hasattr(results, 'quality_metrics'):
                    quality_df = pd.DataFrame([results.quality_metrics])
                    quality_df.to_excel(writer, sheet_name='Quality_Metrics', index=False)
        
        elif options.format == ExportFormat.GCT:
            # Export in GCT format for compatibility with analysis tools
            output_path = export_dir / "integrated_expression.gct"
            self._write_gct_format(results.integrated_expression, output_path)
        
        # Generate integration plots
        if options.include_plots:
            self._generate_integration_plots(results, export_dir)
        
        if options.compress:
            return self._create_archive(export_dir, export_name)
        
        return str(export_dir)
    
    def _export_generic_results(self, 
                               results: Dict[str, Any], 
                               export_name: str, 
                               options: ExportOptions) -> str:
        """Export generic analysis results"""
        
        export_dir = self.output_dir / export_name
        export_dir.mkdir(exist_ok=True)
        
        if options.format == ExportFormat.JSON:
            output_path = export_dir / "results.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        elif options.format == ExportFormat.CSV:
            # Convert to DataFrame if possible
            if isinstance(results, dict) and len(results) > 0:
                try:
                    df = pd.DataFrame(results)
                    output_path = export_dir / "results.csv"
                    df.to_csv(output_path, index=False)
                except ValueError:
                    # Fallback to JSON if conversion fails
                    output_path = export_dir / "results.json"
                    with open(output_path, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
        
        return str(export_dir)
    
    def _create_causal_genes_dataframe(self, causal_genes: List[CausalGene]) -> pd.DataFrame:
        """Create DataFrame from causal genes"""
        data = []
        for gene in causal_genes:
            row = {
                "gene_id": gene.gene_id,
                "gene_symbol": gene.gene_symbol,
                "causal_score": gene.causal_score,
                "confidence_level": gene.confidence_level,
                "evidence_types": "; ".join(gene.evidence_types) if gene.evidence_types else "",
                "differential_expression_score": gene.differential_expression_score,
                "survival_association_score": gene.survival_association_score,
                "cnv_driver_score": gene.cnv_driver_score,
                "methylation_regulation_score": gene.methylation_regulation_score,
                "mutation_frequency_score": gene.mutation_frequency_score,
                "biological_context": json.dumps(gene.biological_context) if gene.biological_context else "",
                "validation_status": gene.validation_status,
                "literature_support": gene.literature_support
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _generate_closedloop_plots(self, results: ClosedLoopResult, output_dir: Path):
        """Generate plots for ClosedLoop results"""
        plots_dir = output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Causal score distribution
        causal_scores = [gene.causal_score for gene in results.causal_genes]
        
        plt.figure(figsize=(10, 6))
        plt.hist(causal_scores, bins=30, alpha=0.7, edgecolor='black')
        plt.xlabel('Causal Score')
        plt.ylabel('Frequency')
        plt.title('Distribution of Causal Scores')
        plt.grid(True, alpha=0.3)
        plt.savefig(plots_dir / "causal_score_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Top genes bar plot
        top_genes = sorted(results.causal_genes, key=lambda x: x.causal_score, reverse=True)[:20]
        gene_names = [gene.gene_symbol or gene.gene_id for gene in top_genes]
        scores = [gene.causal_score for gene in top_genes]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(range(len(gene_names)), scores)
        plt.yticks(range(len(gene_names)), gene_names)
        plt.xlabel('Causal Score')
        plt.title('Top 20 Causal Genes')
        plt.grid(True, alpha=0.3, axis='x')
        
        # Color bars by confidence level
        colors_map = {'High': 'red', 'Medium': 'orange', 'Low': 'yellow'}
        for i, (bar, gene) in enumerate(zip(bars, top_genes)):
            bar.set_color(colors_map.get(gene.confidence_level, 'gray'))
        
        plt.tight_layout()
        plt.savefig(plots_dir / "top_causal_genes.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Evidence types analysis
        evidence_counts = {}
        for gene in results.causal_genes:
            if gene.evidence_types:
                for evidence in gene.evidence_types:
                    evidence_counts[evidence] = evidence_counts.get(evidence, 0) + 1
        
        if evidence_counts:
            plt.figure(figsize=(10, 6))
            evidence_types = list(evidence_counts.keys())
            counts = list(evidence_counts.values())
            plt.bar(evidence_types, counts)
            plt.xlabel('Evidence Type')
            plt.ylabel('Gene Count')
            plt.title('Distribution of Evidence Types')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(plots_dir / "evidence_types_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        self.logger.info(f"Generated ClosedLoop plots in {plots_dir}")
    
    def _generate_integration_plots(self, results: IntegrationResult, output_dir: Path):
        """Generate plots for integration results"""
        plots_dir = output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Sample correlation heatmap
        if results.integrated_expression.shape[1] > 1:
            correlation_matrix = results.integrated_expression.T.corr()
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', center=0,
                       square=True, cbar_kws={"shrink": 0.8})
            plt.title('Sample Correlation Heatmap')
            plt.tight_layout()
            plt.savefig(plots_dir / "sample_correlation_heatmap.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # Feature variance distribution
        feature_variances = results.integrated_expression.var(axis=1)
        
        plt.figure(figsize=(10, 6))
        plt.hist(feature_variances, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Variance')
        plt.ylabel('Frequency')
        plt.title('Feature Variance Distribution')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.savefig(plots_dir / "feature_variance_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Generated integration plots in {plots_dir}")
    
    def _generate_closedloop_pdf_report(self, 
                                       results: ClosedLoopResult, 
                                       output_dir: Path, 
                                       report_type: ReportType) -> str:
        """Generate PDF report for ClosedLoop results"""
        
        output_path = output_dir / "analysis_report.pdf"
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("LIHC Platform ClosedLoop Analysis Report", title_style))
        story.append(Spacer(1, 12))
        
        # Summary section
        summary_text = f"""
        <b>Analysis Summary</b><br/>
        Total Causal Genes Identified: {len(results.causal_genes)}<br/>
        High Confidence Genes: {len([g for g in results.causal_genes if g.confidence_level == 'High'])}<br/>
        Medium Confidence Genes: {len([g for g in results.causal_genes if g.confidence_level == 'Medium'])}<br/>
        Low Confidence Genes: {len([g for g in results.causal_genes if g.confidence_level == 'Low'])}<br/>
        Average Causal Score: {np.mean([g.causal_score for g in results.causal_genes]):.4f}<br/>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Validation metrics
        if results.validation_metrics:
            story.append(Paragraph("<b>Validation Metrics</b>", styles['Heading2']))
            metrics_data = [['Metric', 'Value']]
            for key, value in results.validation_metrics.items():
                metrics_data.append([key, str(value)])
            
            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 12))
        
        # Top causal genes table
        if report_type == ReportType.DETAILED:
            story.append(Paragraph("<b>Top 20 Causal Genes</b>", styles['Heading2']))
            top_genes = sorted(results.causal_genes, key=lambda x: x.causal_score, reverse=True)[:20]
            
            genes_data = [['Gene Symbol', 'Gene ID', 'Causal Score', 'Confidence', 'Evidence Types']]
            for gene in top_genes:
                evidence_str = '; '.join(gene.evidence_types[:3]) if gene.evidence_types else 'N/A'
                genes_data.append([
                    gene.gene_symbol or 'N/A',
                    gene.gene_id,
                    f"{gene.causal_score:.4f}",
                    gene.confidence_level,
                    evidence_str
                ])
            
            genes_table = Table(genes_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 2*inch])
            genes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(genes_table)
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"Generated PDF report: {output_path}")
        return str(output_path)
    
    def _write_gct_format(self, expression_data: pd.DataFrame, output_path: Path):
        """Write expression data in GCT format"""
        with open(output_path, 'w') as f:
            f.write("#1.2\n")
            f.write(f"{expression_data.shape[0]}\t{expression_data.shape[1]}\n")
            f.write("NAME\tDESCRIPTION")
            for sample in expression_data.columns:
                f.write(f"\t{sample}")
            f.write("\n")
            
            for gene in expression_data.index:
                f.write(f"{gene}\t{gene}")  # Use gene ID as description too
                for sample in expression_data.columns:
                    f.write(f"\t{expression_data.loc[gene, sample]}")
                f.write("\n")
    
    def _create_archive(self, export_dir: Path, export_name: str) -> str:
        """Create compressed archive of export directory"""
        archive_path = self.output_dir / f"{export_name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in export_dir.rglob('*'):
                if root.is_file():
                    arcname = root.relative_to(export_dir)
                    zipf.write(root, arcname)
        
        self.logger.info(f"Created archive: {archive_path}")
        return str(archive_path)
    
    def export_dataset_metadata(self, 
                               datasets: List[Dict[str, Any]], 
                               output_format: ExportFormat = ExportFormat.CSV) -> str:
        """Export dataset metadata"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == ExportFormat.CSV:
            output_path = self.output_dir / f"dataset_metadata_{timestamp}.csv"
            df = pd.DataFrame(datasets)
            df.to_csv(output_path, index=False)
        
        elif output_format == ExportFormat.JSON:
            output_path = self.output_dir / f"dataset_metadata_{timestamp}.json"
            with open(output_path, 'w') as f:
                json.dump(datasets, f, indent=2, default=str)
        
        elif output_format == ExportFormat.EXCEL:
            output_path = self.output_dir / f"dataset_metadata_{timestamp}.xlsx"
            df = pd.DataFrame(datasets)
            df.to_excel(output_path, index=False)
        
        self.logger.info(f"Exported dataset metadata: {output_path}")
        return str(output_path)
    
    def export_system_logs(self, 
                          logs: List[Dict[str, Any]], 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          log_levels: Optional[List[str]] = None) -> str:
        """Export system logs with filtering"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter logs
        filtered_logs = logs
        if start_date:
            filtered_logs = [log for log in filtered_logs 
                           if log.get('created_at', datetime.min) >= start_date]
        if end_date:
            filtered_logs = [log for log in filtered_logs 
                           if log.get('created_at', datetime.max) <= end_date]
        if log_levels:
            filtered_logs = [log for log in filtered_logs 
                           if log.get('level') in log_levels]
        
        output_path = self.output_dir / f"system_logs_{timestamp}.csv"
        df = pd.DataFrame(filtered_logs)
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"Exported {len(filtered_logs)} system logs: {output_path}")
        return str(output_path)
    
    def create_analysis_summary_report(self, 
                                     analyses: List[Dict[str, Any]]) -> str:
        """Create comprehensive analysis summary report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"analysis_summary_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("LIHC Platform Analysis Summary Report", title_style))
        story.append(Spacer(1, 12))
        
        # Overall statistics
        total_analyses = len(analyses)
        completed = len([a for a in analyses if a.get('status') == 'completed'])
        failed = len([a for a in analyses if a.get('status') == 'failed'])
        running = len([a for a in analyses if a.get('status') == 'running'])
        
        summary_text = f"""
        <b>Overall Statistics</b><br/>
        Total Analyses: {total_analyses}<br/>
        Completed: {completed} ({completed/total_analyses*100:.1f}%)<br/>
        Failed: {failed} ({failed/total_analyses*100:.1f}%)<br/>
        Currently Running: {running}<br/>
        Success Rate: {completed/(completed+failed)*100:.1f}% (of completed analyses)<br/>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Analysis breakdown by type
        analysis_types = {}
        for analysis in analyses:
            analysis_type = analysis.get('analysis_type', 'Unknown')
            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
        
        story.append(Paragraph("<b>Analysis Types Distribution</b>", styles['Heading2']))
        type_data = [['Analysis Type', 'Count', 'Percentage']]
        for analysis_type, count in analysis_types.items():
            percentage = count / total_analyses * 100
            type_data.append([analysis_type, str(count), f"{percentage:.1f}%"])
        
        type_table = Table(type_data)
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(type_table)
        
        doc.build(story)
        
        self.logger.info(f"Created analysis summary report: {output_path}")
        return str(output_path)
    
    def get_export_formats(self) -> List[str]:
        """Get list of available export formats"""
        return [format_type.value for format_type in ExportFormat]
    
    def cleanup_old_exports(self, days: int = 30):
        """Clean up old export files"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        cleaned_count = 0
        for file_path in self.output_dir.rglob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                file_path.unlink()
                cleaned_count += 1
        
        self.logger.info(f"Cleaned up {cleaned_count} old export files")
        return cleaned_count


# Utility functions for specific export needs
def export_to_biom_format(expression_data: pd.DataFrame, 
                         sample_metadata: Optional[pd.DataFrame] = None,
                         output_path: str = "output.biom") -> str:
    """Export expression data to BIOM format"""
    import biom
    
    # Create BIOM table
    table = biom.Table(expression_data.values, 
                      observation_ids=expression_data.index,
                      sample_ids=expression_data.columns)
    
    # Add sample metadata if provided
    if sample_metadata is not None:
        sample_metadata_dict = sample_metadata.to_dict('index')
        table.add_metadata(sample_metadata_dict, axis='sample')
    
    # Write BIOM file
    with biom.util.biom_open(output_path, 'w') as f:
        table.to_hdf5(f, "LIHC Analysis")
    
    return output_path


def create_publication_ready_tables(causal_genes: List[CausalGene], 
                                  output_dir: str = "publication_tables") -> Dict[str, str]:
    """Create publication-ready supplementary tables"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Main causal genes table
    main_table_data = []
    for gene in sorted(causal_genes, key=lambda x: x.causal_score, reverse=True):
        main_table_data.append({
            "Gene Symbol": gene.gene_symbol or gene.gene_id,
            "Gene ID": gene.gene_id,
            "Causal Score": f"{gene.causal_score:.6f}",
            "Confidence Level": gene.confidence_level,
            "Differential Expression Score": f"{gene.differential_expression_score:.6f}" if gene.differential_expression_score else "N/A",
            "Survival Association Score": f"{gene.survival_association_score:.6f}" if gene.survival_association_score else "N/A",
            "CNV Driver Score": f"{gene.cnv_driver_score:.6f}" if gene.cnv_driver_score else "N/A",
            "Methylation Regulation Score": f"{gene.methylation_regulation_score:.6f}" if gene.methylation_regulation_score else "N/A",
            "Mutation Frequency Score": f"{gene.mutation_frequency_score:.6f}" if gene.mutation_frequency_score else "N/A",
            "Literature Support": "Yes" if gene.literature_support else "No"
        })
    
    main_df = pd.DataFrame(main_table_data)
    main_table_path = output_path / "supplementary_table_1_causal_genes.csv"
    main_df.to_csv(main_table_path, index=False)
    
    # Evidence summary table
    evidence_summary = {}
    for gene in causal_genes:
        if gene.evidence_types:
            for evidence in gene.evidence_types:
                if evidence not in evidence_summary:
                    evidence_summary[evidence] = {"high": 0, "medium": 0, "low": 0, "total": 0}
                evidence_summary[evidence][gene.confidence_level.lower()] += 1
                evidence_summary[evidence]["total"] += 1
    
    evidence_data = []
    for evidence_type, counts in evidence_summary.items():
        evidence_data.append({
            "Evidence Type": evidence_type,
            "High Confidence Genes": counts["high"],
            "Medium Confidence Genes": counts["medium"], 
            "Low Confidence Genes": counts["low"],
            "Total Genes": counts["total"]
        })
    
    evidence_df = pd.DataFrame(evidence_data)
    evidence_table_path = output_path / "supplementary_table_2_evidence_summary.csv"
    evidence_df.to_csv(evidence_table_path, index=False)
    
    return {
        "main_table": str(main_table_path),
        "evidence_summary": str(evidence_table_path)
    }


if __name__ == "__main__":
    # Example usage
    export_manager = DataExportManager("test_exports")
    
    # Test export options
    options = ExportOptions(
        format=ExportFormat.EXCEL,
        include_plots=True,
        include_quality_metrics=True,
        report_type=ReportType.DETAILED
    )
    
    print("Data Export Manager initialized successfully!")
    print(f"Available formats: {export_manager.get_export_formats()}")