#!/usr/bin/env python3
"""
Celery Worker for LIHC Analysis Platform
用于启动Celery工作进程处理后台任务
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analysis.task_queue import app

if __name__ == '__main__':
    # Start celery worker
    # Usage:
    # python celery_worker.py worker --loglevel=info
    # python celery_worker.py worker --loglevel=info -Q quick,standard
    # python celery_worker.py worker --loglevel=info -Q heavy,batch -c 2
    
    app.start()