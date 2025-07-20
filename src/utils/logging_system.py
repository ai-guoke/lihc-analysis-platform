"""
Enhanced logging and error handling system for LIHC Platform
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
import json

class LIHCLogger:
    """Enhanced logging system for LIHC platform"""
    
    def __init__(self, name: str = "LIHC_Platform", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set up formatters
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        
        # Set up handlers
        self._setup_handlers(log_dir)
        
    def _setup_handlers(self, log_dir: Path):
        """Set up logging handlers"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_handler)
        
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.logger.info(message, extra=extra or {})
        
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra or {})
        
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra or {})
        
    def error(self, message: str, exception: Optional[Exception] = None, 
              extra: Optional[Dict[str, Any]] = None):
        """Log error message with optional exception"""
        if exception:
            self.logger.error(
                f"{message}: {str(exception)}", 
                exc_info=True, 
                extra=extra or {}
            )
        else:
            self.logger.error(message, extra=extra or {})
            
    def critical(self, message: str, exception: Optional[Exception] = None,
                 extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        if exception:
            self.logger.critical(
                f"{message}: {str(exception)}", 
                exc_info=True, 
                extra=extra or {}
            )
        else:
            self.logger.critical(message, extra=extra or {})

class ErrorHandler:
    """Enhanced error handling with recovery strategies"""
    
    def __init__(self, logger: Optional[LIHCLogger] = None):
        self.logger = logger or LIHCLogger("ErrorHandler")
        self.error_counts = {}
        
    def handle_analysis_error(self, 
                            error_type: str = "analysis",
                            fallback_return: Any = None,
                            max_retries: int = 0):
        """Decorator for handling analysis errors with retry logic"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__name__}"
                retry_count = 0
                
                while retry_count <= max_retries:
                    try:
                        result = func(*args, **kwargs)
                        if retry_count > 0:
                            self.logger.info(f"Function {func_name} succeeded after {retry_count} retries")
                        return result
                        
                    except Exception as e:
                        retry_count += 1
                        error_key = f"{func_name}_{error_type}"
                        
                        # Track error counts
                        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
                        
                        # Log error with context
                        error_context = {
                            "function": func_name,
                            "error_type": error_type,
                            "retry_count": retry_count,
                            "max_retries": max_retries,
                            "args": str(args)[:200],  # Truncate long args
                            "kwargs": str(kwargs)[:200]
                        }
                        
                        if retry_count <= max_retries:
                            self.logger.warning(
                                f"Error in {func_name} (attempt {retry_count}/{max_retries + 1}): {str(e)}", 
                                extra=error_context
                            )
                        else:
                            self.logger.error(
                                f"Final error in {func_name} after {max_retries} retries: {str(e)}", 
                                exception=e,
                                extra=error_context
                            )
                            
                            # Save error details for debugging
                            self._save_error_details(func_name, e, error_context)
                            
                            return fallback_return
                            
                return fallback_return
                
            return wrapper
        return decorator
    
    def _save_error_details(self, func_name: str, exception: Exception, context: Dict[str, Any]):
        """Save detailed error information for debugging"""
        error_dir = Path("logs") / "errors"
        error_dir.mkdir(exist_ok=True)
        
        error_details = {
            "timestamp": datetime.now().isoformat(),
            "function": func_name,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context
        }
        
        error_file = error_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w') as f:
            json.dump(error_details, f, indent=2)
            
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts.copy(),
            "most_common_errors": sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }

class PerformanceMonitor:
    """Monitor system performance and resource usage"""
    
    def __init__(self, logger: Optional[LIHCLogger] = None):
        self.logger = logger or LIHCLogger("PerformanceMonitor")
        self.metrics = {}
        
    def monitor_function(self, track_memory: bool = True, track_time: bool = True):
        """Decorator to monitor function performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                import psutil
                import os
                
                func_name = f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                if track_memory:
                    process = psutil.Process(os.getpid())
                    start_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    success = False
                    raise
                finally:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    metrics = {
                        "function": func_name,
                        "execution_time": execution_time,
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if track_memory:
                        end_memory = process.memory_info().rss / 1024 / 1024  # MB
                        metrics["memory_usage_mb"] = end_memory - start_memory
                        metrics["peak_memory_mb"] = end_memory
                    
                    # Store metrics
                    if func_name not in self.metrics:
                        self.metrics[func_name] = []
                    self.metrics[func_name].append(metrics)
                    
                    # Log performance info
                    if execution_time > 10:  # Log slow functions
                        self.logger.warning(
                            f"Slow function execution: {func_name} took {execution_time:.2f}s",
                            extra=metrics
                        )
                    else:
                        self.logger.debug(
                            f"Function {func_name} executed in {execution_time:.2f}s",
                            extra=metrics
                        )
                
                return result
                
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        for func_name, metrics_list in self.metrics.items():
            if not metrics_list:
                continue
                
            execution_times = [m["execution_time"] for m in metrics_list]
            success_rate = sum(1 for m in metrics_list if m["success"]) / len(metrics_list)
            
            summary[func_name] = {
                "total_calls": len(metrics_list),
                "success_rate": success_rate,
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "max_execution_time": max(execution_times),
                "min_execution_time": min(execution_times)
            }
            
            # Add memory info if available
            memory_usage = [m.get("memory_usage_mb", 0) for m in metrics_list]
            if any(memory_usage):
                summary[func_name]["avg_memory_usage_mb"] = sum(memory_usage) / len(memory_usage)
                summary[func_name]["max_memory_usage_mb"] = max(memory_usage)
                
        return summary

# Global instances
default_logger = LIHCLogger()
default_error_handler = ErrorHandler(default_logger)
default_performance_monitor = PerformanceMonitor(default_logger)

# Convenience functions
def log_info(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log info message using default logger"""
    default_logger.info(message, extra)

def log_error(message: str, exception: Optional[Exception] = None, 
              extra: Optional[Dict[str, Any]] = None):
    """Log error message using default logger"""
    default_logger.error(message, exception, extra)

def handle_errors(error_type: str = "analysis", fallback_return: Any = None, max_retries: int = 0):
    """Decorator for error handling using default handler"""
    return default_error_handler.handle_analysis_error(error_type, fallback_return, max_retries)

def monitor_performance(track_memory: bool = True, track_time: bool = True):
    """Decorator for performance monitoring using default monitor"""
    return default_performance_monitor.monitor_function(track_memory, track_time)