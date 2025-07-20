#!/usr/bin/env python3
"""
LIHC Multi-dimensional Analysis Platform
Main entry point for the complete analysis system
"""

import sys
import os
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import with proper error handling
try:
    from utils.common import PathManager, ConfigManager, DataGenerator
    from run_pipeline import LIHCAnalysisPipeline
    from visualization.unified_dashboard import UnifiedLIHCDashboard
except ImportError as e:
    print(f"❌ Error: Could not import required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

class LIHCPlatform:
    """Main platform orchestrator"""
    
    def __init__(self):
        self.path_manager = PathManager()
        self.config_manager = ConfigManager()
        
    def setup_demo_data(self, force: bool = False) -> bool:
        """Setup demo data for the platform"""
        print("🔧 Setting up demo data...")
        
        # Check if demo data already exists
        clinical_path = self.path_manager.get_data_path('raw', 'clinical_data.csv')
        expression_path = self.path_manager.get_data_path('raw', 'expression_data.csv')
        mutation_path = self.path_manager.get_data_path('raw', 'mutation_data.csv')
        
        if not force and all(p.exists() for p in [clinical_path, expression_path, mutation_path]):
            print("✅ Demo data already exists. Use --force-demo to regenerate.")
            return True
        
        try:
            # Generate synthetic demo data
            generator = DataGenerator()
            
            # Generate clinical data
            print("  📊 Generating clinical data...")
            clinical_data = generator.generate_clinical_data(n_samples=100)
            clinical_data.to_csv(clinical_path, index=False)
            
            # Generate expression data
            print("  🧬 Generating expression data...")
            expression_data = generator.generate_expression_data(n_genes=1000, n_samples=100)
            expression_data.to_csv(expression_path)
            
            # Generate mutation data
            print("  🔬 Generating mutation data...")
            mutation_data = generator.generate_mutation_data(n_samples=100, n_mutations=150)
            mutation_data.to_csv(mutation_path, index=False)
            
            print("✅ Demo data generated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate demo data: {e}")
            return False
    
    def run_analysis(self, args) -> bool:
        """Run the complete analysis pipeline"""
        print("🚀 Starting LIHC Multi-dimensional Analysis...")
        
        pipeline = LIHCAnalysisPipeline(
            data_dir=args.data_dir,
            results_dir=args.results_dir
        )
        
        # Run pipeline based on stage selection
        if args.stage == 'all':
            success = pipeline.run_complete_pipeline(args.force_download)
        elif args.stage == '0':
            success = pipeline.run_data_preparation(args.force_download)
        elif args.stage == '1':
            pipeline.run_data_preparation(args.force_download)
            success = pipeline.run_stage1_analysis()
        elif args.stage == '2':
            pipeline.run_data_preparation(args.force_download)
            pipeline.run_stage1_analysis()
            success = pipeline.run_stage2_analysis()
        elif args.stage == '3':
            pipeline.run_data_preparation(args.force_download)
            pipeline.run_stage1_analysis()
            pipeline.run_stage2_analysis()
            success = pipeline.run_stage3_analysis()
        else:
            print(f"❌ Invalid stage: {args.stage}")
            return False
        
        if success:
            print("🎉 Analysis completed successfully!")
            return True
        else:
            print("❌ Analysis failed. Check error messages above.")
            return False
    
    def launch_dashboard(self, args) -> None:
        """Launch the unified dashboard"""
        print("🌐 Launching LIHC Analysis Dashboard...")
        
        try:
            dashboard = UnifiedLIHCDashboard(results_dir=args.results_dir)
            dashboard.run(debug=args.debug, port=args.port)
        except KeyboardInterrupt:
            print("\\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
    
    def show_status(self, args) -> None:
        """Show platform status and available data"""
        print("📊 LIHC Platform Status")
        print("=" * 50)
        
        # Check data availability
        print("\\n📁 Data Status:")
        data_files = {
            'Clinical Data': 'raw/clinical_data.csv',
            'Expression Data': 'raw/expression_data.csv',
            'Mutation Data': 'raw/mutation_data.csv'
        }
        
        for name, path in data_files.items():
            file_path = self.path_manager.get_data_path('raw', path.split('/')[-1])
            status = "✅ Available" if file_path.exists() else "❌ Missing"
            size = f" ({file_path.stat().st_size // 1024} KB)" if file_path.exists() else ""
            print(f"  {name}: {status}{size}")
        
        # Check results availability
        print("\\n📈 Results Status:")
        result_files = {
            'Stage 1 Results': 'tables/',
            'Stage 2 Results': 'networks/',
            'Stage 3 Results': 'linchpins/'
        }
        
        for name, path in result_files.items():
            dir_path = self.path_manager.get_results_path(path.rstrip('/'))
            if dir_path.exists():
                file_count = len(list(dir_path.glob('*.csv')))
                status = f"✅ Available ({file_count} files)" if file_count > 0 else "⚠️  Empty"
            else:
                status = "❌ Missing"
            print(f"  {name}: {status}")
        
        # Configuration info
        print("\\n⚙️  Configuration:")
        print(f"  Data Directory: {args.data_dir}")
        print(f"  Results Directory: {args.results_dir}")
        print(f"  Dashboard Port: {args.port}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="LIHC Multi-dimensional Prognostic Analysis Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup demo data and run complete analysis
  python main.py --setup-demo --run-analysis
  
  # Run only Stage 1 analysis
  python main.py --run-analysis --stage 1
  
  # Launch dashboard only
  python main.py --dashboard
  
  # Check platform status
  python main.py --status
        """
    )
    
    # Action arguments
    parser.add_argument(
        "--setup-demo", 
        action="store_true", 
        help="Generate synthetic demo data for testing"
    )
    parser.add_argument(
        "--run-analysis", 
        action="store_true", 
        help="Run the analysis pipeline"
    )
    parser.add_argument(
        "--dashboard", 
        action="store_true", 
        help="Launch the interactive dashboard"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Show platform status"
    )
    
    # Analysis options
    parser.add_argument(
        "--stage", 
        choices=['0', '1', '2', '3', 'all'], 
        default='all',
        help="Analysis stage to run (0=data, 1=multidim, 2=network, 3=linchpin, all=complete)"
    )
    parser.add_argument(
        "--force-download", 
        action="store_true", 
        help="Force re-download of data"
    )
    parser.add_argument(
        "--force-demo", 
        action="store_true", 
        help="Force regeneration of demo data"
    )
    
    # Directory options
    parser.add_argument(
        "--data-dir", 
        default="data", 
        help="Directory for data storage"
    )
    parser.add_argument(
        "--results-dir", 
        default="results", 
        help="Directory for results storage"
    )
    
    # Dashboard options
    parser.add_argument(
        "--port", 
        type=int, 
        default=8050, 
        help="Port for dashboard"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run dashboard in debug mode"
    )
    
    args = parser.parse_args()
    
    # If no actions specified, show help
    if not any([args.setup_demo, args.run_analysis, args.dashboard, args.status]):
        print("🧬 LIHC Multi-dimensional Analysis Platform")
        print("=" * 50)
        print("Please specify an action. Use --help for available options.")
        print("\\nQuick start:")
        print("  python main.py --setup-demo --run-analysis --dashboard")
        return 1
    
    platform = LIHCPlatform()
    
    try:
        # Execute requested actions in logical order
        if args.setup_demo:
            if not platform.setup_demo_data(force=args.force_demo):
                return 1
        
        if args.run_analysis:
            if not platform.run_analysis(args):
                return 1
        
        if args.status:
            platform.show_status(args)
        
        if args.dashboard:
            platform.launch_dashboard(args)
            
        return 0
        
    except KeyboardInterrupt:
        print("\\n👋 Interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())