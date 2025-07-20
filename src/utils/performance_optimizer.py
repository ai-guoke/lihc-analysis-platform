"""
Performance Optimization Configuration for LIHC Platform
Provides advanced performance tuning and optimization settings
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
import psutil
import multiprocessing


@dataclass
class DatabaseConfig:
    """Database performance configuration"""
    max_connections: int = 100
    shared_buffers: str = "256MB"
    effective_cache_size: str = "1GB"
    maintenance_work_mem: str = "64MB"
    checkpoint_completion_target: float = 0.9
    wal_buffers: str = "16MB"
    default_statistics_target: int = 100
    random_page_cost: float = 1.1
    effective_io_concurrency: int = 200
    work_mem: str = "4MB"
    min_wal_size: str = "1GB"
    max_wal_size: str = "4GB"
    
    # Connection pooling
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis performance configuration"""
    maxmemory: str = "2GB"
    maxmemory_policy: str = "allkeys-lru"
    tcp_keepalive: int = 60
    timeout: int = 0
    tcp_backlog: int = 511
    databases: int = 16
    save_intervals: list = None
    
    # Connection pooling
    connection_pool_size: int = 50
    connection_timeout: int = 20
    socket_timeout: int = 20
    
    def __post_init__(self):
        if self.save_intervals is None:
            self.save_intervals = ["900 1", "300 10", "60 10000"]


@dataclass
class APIConfig:
    """API server performance configuration"""
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 1000
    max_requests_jitter: int = 50
    timeout: int = 30
    keepalive: int = 5
    max_body_size: int = 500 * 1024 * 1024  # 500MB
    
    # FastAPI specific
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # Caching
    cache_ttl: int = 300
    cache_max_size: int = 1000


@dataclass
class CeleryConfig:
    """Celery task queue configuration"""
    workers: int = 4
    concurrency: int = 4
    prefetch_multiplier: int = 1
    max_tasks_per_child: int = 1000
    task_soft_time_limit: int = 1800
    task_time_limit: int = 3600
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 1
    
    # Result backend
    result_expires: int = 3600
    result_backend_transport_options: Dict[str, Any] = None
    
    # Broker settings
    broker_transport_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.result_backend_transport_options is None:
            self.result_backend_transport_options = {
                "master_name": "mymaster",
                "visibility_timeout": 3600,
                "retry_policy": {
                    "timeout": 5.0
                }
            }
        
        if self.broker_transport_options is None:
            self.broker_transport_options = {
                "master_name": "mymaster",
                "visibility_timeout": 3600,
                "retry_policy": {
                    "timeout": 5.0
                }
            }


@dataclass
class SystemConfig:
    """System-level performance configuration"""
    max_open_files: int = 65536
    tcp_max_syn_backlog: int = 4096
    tcp_rmem: str = "4096 87380 16777216"
    tcp_wmem: str = "4096 16384 16777216"
    tcp_congestion_control: str = "bbr"
    
    # Memory settings
    vm_swappiness: int = 10
    vm_dirty_ratio: int = 15
    vm_dirty_background_ratio: int = 5
    
    # File system
    fs_file_max: int = 2097152


class PerformanceOptimizer:
    """Performance optimization manager"""
    
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total // (1024**3)
        self.config = self._generate_optimized_config()
    
    def _generate_optimized_config(self) -> Dict[str, Any]:
        """Generate optimized configuration based on system resources"""
        
        # Database configuration
        db_config = DatabaseConfig()
        if self.memory_gb >= 16:
            db_config.shared_buffers = "512MB"
            db_config.effective_cache_size = "4GB"
            db_config.maintenance_work_mem = "128MB"
            db_config.work_mem = "8MB"
        elif self.memory_gb >= 8:
            db_config.shared_buffers = "256MB"
            db_config.effective_cache_size = "2GB"
            db_config.maintenance_work_mem = "64MB"
            db_config.work_mem = "4MB"
        
        # Redis configuration
        redis_config = RedisConfig()
        if self.memory_gb >= 16:
            redis_config.maxmemory = "4GB"
            redis_config.connection_pool_size = 100
        elif self.memory_gb >= 8:
            redis_config.maxmemory = "2GB"
            redis_config.connection_pool_size = 50
        
        # API configuration
        api_config = APIConfig()
        api_config.workers = min(self.cpu_count * 2, 8)
        
        # Celery configuration
        celery_config = CeleryConfig()
        celery_config.workers = min(self.cpu_count, 8)
        celery_config.concurrency = min(self.cpu_count, 8)
        
        return {
            "database": asdict(db_config),
            "redis": asdict(redis_config),
            "api": asdict(api_config),
            "celery": asdict(celery_config),
            "system": asdict(SystemConfig())
        }
    
    def generate_postgresql_conf(self) -> str:
        """Generate PostgreSQL configuration"""
        db_config = self.config["database"]
        
        conf = f"""
# PostgreSQL Configuration - Optimized for LIHC Platform
# Generated automatically based on system resources

# Connection Settings
max_connections = {db_config['max_connections']}
shared_buffers = {db_config['shared_buffers']}
effective_cache_size = {db_config['effective_cache_size']}

# Memory Settings
work_mem = {db_config['work_mem']}
maintenance_work_mem = {db_config['maintenance_work_mem']}

# Checkpoint Settings
checkpoint_completion_target = {db_config['checkpoint_completion_target']}
wal_buffers = {db_config['wal_buffers']}

# WAL Settings
min_wal_size = {db_config['min_wal_size']}
max_wal_size = {db_config['max_wal_size']}

# Query Planning
default_statistics_target = {db_config['default_statistics_target']}
random_page_cost = {db_config['random_page_cost']}
effective_io_concurrency = {db_config['effective_io_concurrency']}

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000

# Monitoring
track_activities = on
track_counts = on
track_io_timing = on
track_functions = all
"""
        return conf
    
    def generate_redis_conf(self) -> str:
        """Generate Redis configuration"""
        redis_config = self.config["redis"]
        
        conf = f"""
# Redis Configuration - Optimized for LIHC Platform
# Generated automatically based on system resources

# Memory Management
maxmemory {redis_config['maxmemory']}
maxmemory-policy {redis_config['maxmemory_policy']}

# Network
tcp-keepalive {redis_config['tcp_keepalive']}
timeout {redis_config['timeout']}
tcp-backlog {redis_config['tcp_backlog']}

# General
databases {redis_config['databases']}
daemonize yes
supervised systemd

# Persistence
"""
        
        for interval in redis_config['save_intervals']:
            conf += f"save {interval}\n"
        
        conf += """
# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Security
protected-mode yes
"""
        return conf
    
    def generate_nginx_conf(self) -> str:
        """Generate optimized NGINX configuration"""
        
        conf = f"""
# NGINX Configuration - Optimized for LIHC Platform
user nginx;
worker_processes {self.cpu_count};
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections 1024;
    use epoll;
    multi_accept on;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Buffer Settings
    client_body_buffer_size 128k;
    client_max_body_size 500m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=dashboard:10m rate=5r/s;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Upstream definitions
    upstream lihc_api {{
        server lihc-api:8050;
        keepalive 32;
    }}
    
    upstream lihc_dashboard {{
        server lihc-dashboard:8051;
        keepalive 32;
    }}
    
    include /etc/nginx/conf.d/*.conf;
}}
"""
        return conf
    
    def generate_docker_compose_override(self) -> str:
        """Generate Docker Compose override for performance optimization"""
        
        override = f"""
version: '3.8'

services:
  lihc-api:
    environment:
      - WORKERS={self.config['api']['workers']}
      - WORKER_CLASS={self.config['api']['worker_class']}
      - TIMEOUT={self.config['api']['timeout']}
      - KEEPALIVE={self.config['api']['keepalive']}
    deploy:
      resources:
        limits:
          cpus: '{min(self.cpu_count, 4)}'
          memory: {min(self.memory_gb//2, 8)}G
        reservations:
          cpus: '1'
          memory: 2G
  
  lihc-dashboard:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
  
  postgres:
    environment:
      - POSTGRES_SHARED_BUFFERS={self.config['database']['shared_buffers']}
      - POSTGRES_EFFECTIVE_CACHE_SIZE={self.config['database']['effective_cache_size']}
      - POSTGRES_WORK_MEM={self.config['database']['work_mem']}
    deploy:
      resources:
        limits:
          cpus: '{min(self.cpu_count//2, 4)}'
          memory: {min(self.memory_gb//2, 8)}G
        reservations:
          cpus: '1'
          memory: 2G
    volumes:
      - ./performance/postgresql.conf:/etc/postgresql/postgresql.conf
  
  redis:
    command: redis-server /etc/redis/redis.conf
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: {self.config['redis']['maxmemory']}
        reservations:
          cpus: '0.5'
          memory: 512M
    volumes:
      - ./performance/redis.conf:/etc/redis/redis.conf
  
  celery-worker:
    environment:
      - CELERY_WORKERS={self.config['celery']['workers']}
      - CELERY_CONCURRENCY={self.config['celery']['concurrency']}
      - CELERY_PREFETCH_MULTIPLIER={self.config['celery']['prefetch_multiplier']}
    deploy:
      resources:
        limits:
          cpus: '{self.cpu_count}'
          memory: {min(self.memory_gb//2, 8)}G
        reservations:
          cpus: '2'
          memory: 4G
  
  nginx:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    volumes:
      - ./performance/nginx.conf:/etc/nginx/nginx.conf
"""
        return override
    
    def generate_celery_config(self) -> str:
        """Generate Celery configuration"""
        celery_config = self.config["celery"]
        
        config = f"""
# Celery Configuration - Optimized for LIHC Platform
import os
from celery import Celery

# Broker settings
broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Performance settings
task_acks_late = {str(celery_config['task_acks_late']).lower()}
task_reject_on_worker_lost = True
task_soft_time_limit = {celery_config['task_soft_time_limit']}
task_time_limit = {celery_config['task_time_limit']}
worker_prefetch_multiplier = {celery_config['worker_prefetch_multiplier']}
worker_max_tasks_per_child = {celery_config['max_tasks_per_child']}

# Result backend settings
result_expires = {celery_config['result_expires']}
result_backend_transport_options = {celery_config['result_backend_transport_options']}

# Broker transport options
broker_transport_options = {celery_config['broker_transport_options']}

# Worker settings
worker_send_task_events = True
task_send_sent_event = True

# Monitoring
worker_hijack_root_logger = False
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
"""
        return config
    
    def save_configurations(self, output_dir: str = "performance"):
        """Save all performance configurations to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # PostgreSQL configuration
        with open(f"{output_dir}/postgresql.conf", "w") as f:
            f.write(self.generate_postgresql_conf())
        
        # Redis configuration
        with open(f"{output_dir}/redis.conf", "w") as f:
            f.write(self.generate_redis_conf())
        
        # NGINX configuration
        with open(f"{output_dir}/nginx.conf", "w") as f:
            f.write(self.generate_nginx_conf())
        
        # Docker Compose override
        with open(f"{output_dir}/docker-compose.override.yml", "w") as f:
            f.write(self.generate_docker_compose_override())
        
        # Celery configuration
        with open(f"{output_dir}/celery_config.py", "w") as f:
            f.write(self.generate_celery_config())
        
        # Save configuration summary
        with open(f"{output_dir}/config_summary.json", "w") as f:
            json.dump({
                "system_info": {
                    "cpu_count": self.cpu_count,
                    "memory_gb": self.memory_gb
                },
                "generated_config": self.config
            }, f, indent=2)
        
        print(f"Performance configurations saved to {output_dir}/")
        print(f"System detected: {self.cpu_count} CPUs, {self.memory_gb}GB RAM")
    
    def generate_monitoring_queries(self) -> Dict[str, str]:
        """Generate performance monitoring queries"""
        return {
            "database_performance": """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            ORDER BY total_time DESC 
            LIMIT 10;
            """,
            
            "slow_queries": """
            SELECT 
                query,
                calls,
                total_time,
                mean_time
            FROM pg_stat_statements 
            WHERE mean_time > 1000 
            ORDER BY mean_time DESC;
            """,
            
            "connection_stats": """
            SELECT 
                state,
                count(*) as connections
            FROM pg_stat_activity 
            GROUP BY state;
            """,
            
            "cache_hit_ratio": """
            SELECT 
                schemaname,
                tablename,
                heap_blks_read,
                heap_blks_hit,
                round(heap_blks_hit::numeric/(heap_blks_hit+heap_blks_read+1)*100,2) as cache_hit_ratio
            FROM pg_statio_user_tables 
            ORDER BY cache_hit_ratio DESC;
            """,
            
            "table_sizes": """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on system specs"""
        recommendations = []
        
        if self.memory_gb < 8:
            recommendations.append("Consider upgrading to at least 8GB RAM for better performance")
        
        if self.cpu_count < 4:
            recommendations.append("Consider upgrading to at least 4 CPU cores for optimal performance")
        
        if self.memory_gb >= 32:
            recommendations.append("Consider increasing PostgreSQL shared_buffers to 1GB or more")
            recommendations.append("Consider increasing Redis maxmemory to 8GB or more")
        
        recommendations.extend([
            "Enable PostgreSQL query logging for performance monitoring",
            "Set up regular VACUUM and ANALYZE operations",
            "Monitor slow queries and add indexes as needed",
            "Consider using connection pooling for high-concurrency scenarios",
            "Enable gzip compression for API responses",
            "Use CDN for static assets in production",
            "Set up proper monitoring and alerting",
            "Consider Redis clustering for high availability",
            "Use SSD storage for database files",
            "Enable kernel-level optimizations for network performance"
        ])
        
        return recommendations


if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    optimizer.save_configurations()
    
    print("\nOptimization Recommendations:")
    for i, rec in enumerate(optimizer.get_optimization_recommendations(), 1):
        print(f"{i}. {rec}")
    
    print("\nPerformance monitoring queries saved to config_summary.json")
    print("Apply configurations by copying files to appropriate locations and restarting services.")