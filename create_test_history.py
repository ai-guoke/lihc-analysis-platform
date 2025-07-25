#!/usr/bin/env python3
"""Create test history records for demonstration"""

import sys
sys.path.insert(0, '.')

from src.data_processing.history_manager import HistoryManager
import uuid

# Initialize history manager
history_manager = HistoryManager()

# Create some test upload records
for i in range(3):
    session_id = str(uuid.uuid4())
    upload_info = {
        'success': True if i != 1 else False,
        'files_processed': {
            'clinical_data.csv': {'data_type': 'clinical', 'validation': {'valid': True}},
            'expression_data.csv': {'data_type': 'expression', 'validation': {'valid': True}},
            'mutation_data.csv': {'data_type': 'mutation', 'validation': {'valid': i != 1}}
        },
        'errors': [] if i != 1 else ['Missing required columns in mutation data'],
        'warnings': ['High percentage of missing values'] if i == 2 else []
    }
    
    record = history_manager.add_upload_record(session_id, upload_info)
    print(f"✅ Created upload record {i+1}: {session_id[:8]}...")
    
    # Add analysis record for successful uploads
    if upload_info['success']:
        analysis_info = {
            'modules': ['stage1', 'stage2', 'stage3'] if i == 0 else ['stage1', 'precision'],
            'status': 'completed',
            'duration': f'{15 + i*5} minutes'
        }
        history_manager.add_analysis_record(session_id, analysis_info)
        print(f"✅ Created analysis record for session {session_id[:8]}...")

# Show statistics
stats = history_manager.get_statistics()
print("\n📊 History Statistics:")
print(f"Total uploads: {stats['total_uploads']}")
print(f"Successful uploads: {stats['successful_uploads']}")
print(f"Failed uploads: {stats['failed_uploads']}")
print(f"Total analyses: {stats['total_analyses']}")

print("\n✨ Test history records created successfully!")
print("Visit http://localhost:8050 → 历史记录 to view them.")