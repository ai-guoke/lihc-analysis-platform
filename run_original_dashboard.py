#!/usr/bin/env python3
"""
Run the original professional dashboard on port 8051
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from visualization.professional_dashboard import ProfessionalDashboard

if __name__ == "__main__":
    dashboard = ProfessionalDashboard()
    print("🚀 Starting Original Professional Dashboard...")
    print("📊 Running on port 8051 (avoiding Docker's 8050)")
    dashboard.run(debug=False, port=8051)