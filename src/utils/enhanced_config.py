"""
Enhanced configuration management system for LIHC Platform
"""

import json
import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class ConfigSource(Enum):
    """Configuration source types"""
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    USER = "user"

@dataclass
class AnalysisConfig:
    """Analysis configuration parameters"""
    # Statistical thresholds
    p_value_threshold: float = 0.05
    correlation_threshold: float = 0.4
    survival_threshold_years: float = 5.0
    hr_threshold: float = 0.2
    
    # Linchpin scoring weights
    prognostic_score_weight: float = 0.4
    network_hub_score_weight: float = 0.3
    cross_domain_score_weight: float = 0.2
    regulator_score_weight: float = 0.1
    
    # Performance settings
    n_jobs: int = -1
    memory_limit: str = "8GB"
    batch_size: int = 1000
    cache_enabled: bool = True
    
    # Output settings
    save_intermediate_results: bool = True
    result_formats: list = None
    
    def __post_init__(self):
        if self.result_formats is None:
            self.result_formats = ["csv", "json"]

@dataclass
class SystemConfig:
    """System configuration parameters"""
    # Logging settings
    log_level: str = "INFO"
    log_file_enabled: bool = True
    log_max_size: str = "10MB"
    log_backup_count: int = 5
    
    # Database settings
    database_url: str = "sqlite:///lihc_platform.db"
    database_pool_size: int = 10
    database_timeout: int = 30
    
    # Web server settings
    host: str = "localhost"
    port: int = 8050
    debug: bool = False
    secret_key: str = ""  # Must be set via environment variable
    
    # Security settings
    cors_enabled: bool = True
    cors_origins: list = None
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]

@dataclass
class DataConfig:
    """Data configuration parameters"""
    # Data paths
    data_root: str = "data"
    results_root: str = "results"
    cache_root: str = "cache"
    logs_root: str = "logs"
    
    # Data processing
    max_file_size: str = "500MB"
    allowed_extensions: list = None
    sample_size_limit: int = 10000
    gene_size_limit: int = 50000
    
    # TCGA settings
    tcga_endpoint: str = "https://api.gdc.cancer.gov"
    tcga_timeout: int = 300
    tcga_retry_count: int = 3
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = [".csv", ".tsv", ".xlsx", ".json"]

class ConfigurationManager:
    """Enhanced configuration management system"""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize configurations
        self.analysis_config = AnalysisConfig()
        self.system_config = SystemConfig()
        self.data_config = DataConfig()
        
        # Track configuration sources
        self.config_sources = {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load configurations from various sources"""
        # Load from files
        self._load_from_files()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Load user overrides
        self._load_user_overrides()
        
    def _load_from_files(self):
        """Load configuration from files"""
        config_files = {
            'analysis': self.config_dir / 'analysis.yaml',
            'system': self.config_dir / 'system.yaml',
            'data': self.config_dir / 'data.yaml'
        }
        
        for config_type, config_file in config_files.items():
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    
                    if config_type == 'analysis':
                        self._update_analysis_config(config_data, ConfigSource.FILE)
                    elif config_type == 'system':
                        self._update_system_config(config_data, ConfigSource.FILE)
                    elif config_type == 'data':
                        self._update_data_config(config_data, ConfigSource.FILE)
                        
                    self.logger.info(f"Loaded {config_type} configuration from {config_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load {config_type} configuration: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            # Analysis config
            'LIHC_P_VALUE_THRESHOLD': ('analysis_config', 'p_value_threshold', float),
            'LIHC_CORRELATION_THRESHOLD': ('analysis_config', 'correlation_threshold', float),
            'LIHC_N_JOBS': ('analysis_config', 'n_jobs', int),
            'LIHC_MEMORY_LIMIT': ('analysis_config', 'memory_limit', str),
            'LIHC_BATCH_SIZE': ('analysis_config', 'batch_size', int),
            
            # System config
            'LIHC_LOG_LEVEL': ('system_config', 'log_level', str),
            'LIHC_HOST': ('system_config', 'host', str),
            'LIHC_PORT': ('system_config', 'port', int),
            'LIHC_DEBUG': ('system_config', 'debug', bool),
            'LIHC_SECRET_KEY': ('system_config', 'secret_key', str),
            
            # Data config
            'LIHC_DATA_ROOT': ('data_config', 'data_root', str),
            'LIHC_RESULTS_ROOT': ('data_config', 'results_root', str),
            'LIHC_MAX_FILE_SIZE': ('data_config', 'max_file_size', str),
        }
        
        for env_var, (config_obj, attr_name, type_func) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    typed_value = type_func(env_value) if type_func != bool else env_value.lower() in ('true', '1', 'yes')
                    config_obj_instance = getattr(self, config_obj)
                    setattr(config_obj_instance, attr_name, typed_value)
                    
                    self.config_sources[f"{config_obj}.{attr_name}"] = ConfigSource.ENVIRONMENT
                    self.logger.debug(f"Set {config_obj}.{attr_name} from environment: {typed_value}")
                    
                except ValueError as e:
                    self.logger.error(f"Invalid environment value for {env_var}: {e}")
    
    def _load_user_overrides(self):
        """Load user-specific configuration overrides"""
        user_config_file = self.config_dir / 'user.yaml'
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                
                # Apply user overrides
                if 'analysis' in user_config:
                    self._update_analysis_config(user_config['analysis'], ConfigSource.USER)
                if 'system' in user_config:
                    self._update_system_config(user_config['system'], ConfigSource.USER)
                if 'data' in user_config:
                    self._update_data_config(user_config['data'], ConfigSource.USER)
                    
                self.logger.info(f"Loaded user configuration from {user_config_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to load user configuration: {e}")
    
    def _update_analysis_config(self, config_data: Dict[str, Any], source: ConfigSource):
        """Update analysis configuration"""
        for key, value in config_data.items():
            if hasattr(self.analysis_config, key):
                setattr(self.analysis_config, key, value)
                self.config_sources[f"analysis_config.{key}"] = source
    
    def _update_system_config(self, config_data: Dict[str, Any], source: ConfigSource):
        """Update system configuration"""
        for key, value in config_data.items():
            if hasattr(self.system_config, key):
                setattr(self.system_config, key, value)
                self.config_sources[f"system_config.{key}"] = source
    
    def _update_data_config(self, config_data: Dict[str, Any], source: ConfigSource):
        """Update data configuration"""
        for key, value in config_data.items():
            if hasattr(self.data_config, key):
                setattr(self.data_config, key, value)
                self.config_sources[f"data_config.{key}"] = source
    
    def get_config(self, config_type: str) -> Union[AnalysisConfig, SystemConfig, DataConfig]:
        """Get configuration by type"""
        config_map = {
            'analysis': self.analysis_config,
            'system': self.system_config,
            'data': self.data_config
        }
        return config_map.get(config_type)
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path (e.g., 'analysis.p_value_threshold')"""
        try:
            config_type, attr_name = path.split('.', 1)
            config_obj = self.get_config(config_type)
            if config_obj and hasattr(config_obj, attr_name):
                return getattr(config_obj, attr_name)
            return default
        except ValueError:
            return default
    
    def set_value(self, path: str, value: Any, source: ConfigSource = ConfigSource.USER):
        """Set configuration value by path"""
        try:
            config_type, attr_name = path.split('.', 1)
            config_obj = self.get_config(config_type)
            if config_obj and hasattr(config_obj, attr_name):
                setattr(config_obj, attr_name, value)
                self.config_sources[f"{config_type}_config.{attr_name}"] = source
                self.logger.info(f"Set {path} = {value} (source: {source.value})")
                return True
            return False
        except ValueError:
            return False
    
    def save_configuration(self, config_type: str, filename: Optional[str] = None):
        """Save configuration to file"""
        if filename is None:
            filename = f"{config_type}.yaml"
        
        config_file = self.config_dir / filename
        config_obj = self.get_config(config_type)
        
        if config_obj:
            try:
                config_dict = asdict(config_obj)
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                self.logger.info(f"Saved {config_type} configuration to {config_file}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to save {config_type} configuration: {e}")
                return False
        return False
    
    def validate_configuration(self) -> Dict[str, list]:
        """Validate configuration values"""
        errors = {}
        
        # Validate analysis config
        analysis_errors = []
        if not 0 < self.analysis_config.p_value_threshold < 1:
            analysis_errors.append("p_value_threshold must be between 0 and 1")
        if not 0 < self.analysis_config.correlation_threshold < 1:
            analysis_errors.append("correlation_threshold must be between 0 and 1")
        if self.analysis_config.n_jobs < -1 or self.analysis_config.n_jobs == 0:
            analysis_errors.append("n_jobs must be -1 or positive integer")
        
        if analysis_errors:
            errors['analysis'] = analysis_errors
        
        # Validate system config
        system_errors = []
        if not 1024 <= self.system_config.port <= 65535:
            system_errors.append("port must be between 1024 and 65535")
        if self.system_config.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            system_errors.append("log_level must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        if system_errors:
            errors['system'] = system_errors
        
        # Validate data config
        data_errors = []
        if not Path(self.data_config.data_root).exists():
            data_errors.append(f"data_root directory does not exist: {self.data_config.data_root}")
        
        if data_errors:
            errors['data'] = data_errors
        
        return errors
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'analysis': asdict(self.analysis_config),
            'system': asdict(self.system_config),
            'data': asdict(self.data_config),
            'sources': self.config_sources.copy()
        }
    
    def create_default_config_files(self):
        """Create default configuration files"""
        self.save_configuration('analysis')
        self.save_configuration('system')
        self.save_configuration('data')
        
        # Create user config template
        user_config_template = {
            'analysis': {
                'p_value_threshold': 0.05,
                'n_jobs': -1
            },
            'system': {
                'log_level': 'INFO',
                'debug': False
            },
            'data': {
                'data_root': 'data',
                'results_root': 'results'
            }
        }
        
        user_config_file = self.config_dir / 'user.yaml.template'
        with open(user_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(user_config_template, f, default_flow_style=False, indent=2)
        
        self.logger.info("Created default configuration files")

# Global configuration manager instance
config_manager = ConfigurationManager()

# Convenience functions
def get_analysis_config() -> AnalysisConfig:
    """Get analysis configuration"""
    return config_manager.analysis_config

def get_system_config() -> SystemConfig:
    """Get system configuration"""
    return config_manager.system_config

def get_data_config() -> DataConfig:
    """Get data configuration"""
    return config_manager.data_config

def get_config_value(path: str, default: Any = None) -> Any:
    """Get configuration value by path"""
    return config_manager.get_value(path, default)

def set_config_value(path: str, value: Any) -> bool:
    """Set configuration value by path"""
    return config_manager.set_value(path, value)