"""
Celery Configuration for LIHC Analysis Platform
"""

import os
from kombu import Exchange, Queue

# Broker settings
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Result backend settings
result_expires = 3600 * 24  # 24 hours
result_persistent = True

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 100
worker_disable_rate_limits = True

# Task execution settings
task_time_limit = 3600  # 1 hour hard limit
task_soft_time_limit = 3000  # 50 minutes soft limit
task_acks_late = True
task_reject_on_worker_lost = True

# Queue definitions
task_queues = (
    Queue('quick', Exchange('quick'), routing_key='quick', 
          queue_arguments={'x-max-priority': 10}),
    Queue('standard', Exchange('standard'), routing_key='standard',
          queue_arguments={'x-max-priority': 10}),
    Queue('heavy', Exchange('heavy'), routing_key='heavy',
          queue_arguments={'x-max-priority': 10}),
    Queue('batch', Exchange('batch'), routing_key='batch',
          queue_arguments={'x-max-priority': 10}),
)

# Task routing
task_routes = {
    'analysis.quick': {'queue': 'quick'},
    'analysis.standard': {'queue': 'standard'},
    'analysis.heavy': {'queue': 'heavy'},
    'analysis.batch': {'queue': 'batch'},
    'health.check': {'queue': 'quick'},
    'maintenance.cleanup': {'queue': 'standard'}
}

# Beat schedule for periodic tasks
beat_schedule = {
    'health-check': {
        'task': 'health.check',
        'schedule': 60.0,  # Every minute
    },
    'cleanup-old-tasks': {
        'task': 'maintenance.cleanup',
        'schedule': 3600.0 * 24,  # Daily
    },
}

# Monitoring
worker_send_task_events = True
task_send_sent_event = True