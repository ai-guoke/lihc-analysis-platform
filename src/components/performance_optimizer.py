"""
Performance Optimization System
性能优化系统 - 为大规模数据集提供高效处理能力
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Iterator, Generator
import json
import tempfile
import os
from pathlib import Path
import hashlib
import pickle
import gc
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
from functools import lru_cache, wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3

@dataclass
class PerformanceMetrics:
    """性能指标"""
    memory_usage_mb: float
    processing_time_s: float
    cpu_usage_percent: float
    cache_hit_rate: float
    data_size_mb: float
    optimization_applied: List[str]

@dataclass
class DataChunk:
    """数据分块"""
    chunk_id: str
    start_idx: int
    end_idx: int
    size: int
    data_hash: str
    cached: bool = False

class MemoryManager:
    """内存管理器"""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.current_usage = 0
        self.tracked_objects = {}
        
    def get_memory_usage(self) -> float:
        """获取当前内存使用情况（MB）"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def check_memory_pressure(self) -> bool:
        """检查内存压力"""
        current_mb = self.get_memory_usage()
        threshold_mb = (self.max_memory_bytes / 1024 / 1024) * 0.8  # 80% 阈值
        return current_mb > threshold_mb
    
    def suggest_chunk_size(self, data_size_mb: float, target_chunks: int = 4) -> int:
        """建议分块大小"""
        available_mb = (self.max_memory_bytes / 1024 / 1024) * 0.6  # 60% 可用
        chunk_size_mb = min(available_mb / target_chunks, data_size_mb / target_chunks)
        
        # 转换为行数估算（假设每行平均 1KB）
        estimated_rows = int(chunk_size_mb * 1024)
        return max(1000, estimated_rows)  # 最小 1000 行

class IntelligentCache:
    """智能缓存系统"""
    
    def __init__(self, cache_dir: str = "cache", max_size_gb: float = 10.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.metadata_db = self.cache_dir / "cache_metadata.db"
        self._init_database()
        
    def _init_database(self):
        """初始化缓存元数据数据库"""
        conn = sqlite3.connect(self.metadata_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                file_path TEXT,
                size_bytes INTEGER,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                data_type TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, data_hash: str, operation: str, params: Dict = None) -> str:
        """生成缓存键"""
        key_data = f"{data_hash}_{operation}"
        if params:
            key_data += "_" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.execute(
            "SELECT file_path FROM cache_entries WHERE key = ?", (key,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            file_path = Path(result[0])
            if file_path.exists():
                # 更新访问时间和计数
                self._update_access_stats(key)
                
                try:
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
                except:
                    # 缓存文件损坏，删除
                    self._remove_entry(key)
                    return None
        
        return None
    
    def set(self, key: str, data: Any, data_type: str = "general") -> bool:
        """设置缓存数据"""
        try:
            # 检查缓存空间
            if not self._ensure_cache_space():
                return False
            
            # 保存数据
            file_path = self.cache_dir / f"{key}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            # 记录元数据
            size_bytes = file_path.stat().st_size
            now = datetime.now()
            
            conn = sqlite3.connect(self.metadata_db)
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries 
                (key, file_path, size_bytes, created_at, last_accessed, data_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (key, str(file_path), size_bytes, now, now, data_type))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def _ensure_cache_space(self) -> bool:
        """确保缓存空间足够"""
        current_size = self._get_cache_size()
        
        if current_size > self.max_size_bytes * 0.9:  # 90% 阈值
            # 清理最少使用的缓存
            self._cleanup_lru_entries(0.3)  # 清理 30% 的空间
        
        return True
    
    def _get_cache_size(self) -> int:
        """获取当前缓存大小"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
        result = cursor.fetchone()
        conn.close()
        return result[0] or 0
    
    def _cleanup_lru_entries(self, cleanup_ratio: float = 0.3):
        """清理最少使用的条目"""
        conn = sqlite3.connect(self.metadata_db)
        
        # 按访问时间和频率排序，删除最少使用的
        cursor = conn.execute("""
            SELECT key, file_path FROM cache_entries 
            ORDER BY access_count ASC, last_accessed ASC
        """)
        
        all_entries = cursor.fetchall()
        cleanup_count = int(len(all_entries) * cleanup_ratio)
        
        for key, file_path in all_entries[:cleanup_count]:
            try:
                Path(file_path).unlink(missing_ok=True)
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            except:
                continue
        
        conn.commit()
        conn.close()
    
    def _update_access_stats(self, key: str):
        """更新访问统计"""
        conn = sqlite3.connect(self.metadata_db)
        conn.execute("""
            UPDATE cache_entries 
            SET last_accessed = ?, access_count = access_count + 1
            WHERE key = ?
        """, (datetime.now(), key))
        conn.commit()
        conn.close()
    
    def _remove_entry(self, key: str):
        """删除缓存条目"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.execute("SELECT file_path FROM cache_entries WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            Path(result[0]).unlink(missing_ok=True)
            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
        
        conn.commit()
        conn.close()

class DataChunker:
    """数据分块处理器"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        
    def create_chunks(self, data: pd.DataFrame, max_chunk_size: int = None) -> List[DataChunk]:
        """创建数据分块"""
        if max_chunk_size is None:
            data_size_mb = data.memory_usage(deep=True).sum() / 1024 / 1024
            max_chunk_size = self.memory_manager.suggest_chunk_size(data_size_mb)
        
        chunks = []
        total_rows = len(data)
        
        for start_idx in range(0, total_rows, max_chunk_size):
            end_idx = min(start_idx + max_chunk_size, total_rows)
            chunk_data = data.iloc[start_idx:end_idx]
            
            # 生成数据哈希
            data_hash = hashlib.md5(
                pd.util.hash_pandas_object(chunk_data).values
            ).hexdigest()
            
            chunk = DataChunk(
                chunk_id=f"chunk_{start_idx}_{end_idx}",
                start_idx=start_idx,
                end_idx=end_idx,
                size=end_idx - start_idx,
                data_hash=data_hash
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def process_chunks_parallel(self, chunks: List[DataChunk], data: pd.DataFrame,
                               processing_func: callable, max_workers: int = None) -> List[Any]:
        """并行处理数据分块"""
        if max_workers is None:
            max_workers = min(4, os.cpu_count() or 1)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = []
            for chunk in chunks:
                chunk_data = data.iloc[chunk.start_idx:chunk.end_idx]
                future = executor.submit(processing_func, chunk_data, chunk.chunk_id)
                futures.append((future, chunk))
            
            # 收集结果
            for future, chunk in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing chunk {chunk.chunk_id}: {e}")
                    results.append(None)
        
        return results

class StreamingProcessor:
    """流式数据处理器"""
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        
    def stream_process_large_matrix(self, file_path: str, 
                                   processing_func: callable,
                                   chunk_size: int = 10000) -> Iterator[Any]:
        """流式处理大型矩阵文件"""
        
        file_hash = self._get_file_hash(file_path)
        
        # 检查是否有缓存的处理结果
        cache_key = self._get_cache_key(file_hash, processing_func.__name__)
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            yield from cached_result
            return
        
        # 流式读取和处理
        results = []
        
        try:
            # 使用 pandas 的分块读取
            chunk_reader = pd.read_csv(file_path, chunksize=chunk_size)
            
            for chunk_idx, chunk in enumerate(chunk_reader):
                try:
                    # 处理当前分块
                    processed_chunk = processing_func(chunk)
                    results.append(processed_chunk)
                    
                    yield processed_chunk
                    
                    # 内存管理
                    if chunk_idx % 10 == 0:  # 每 10 个分块检查一次
                        if self.memory_manager.check_memory_pressure():
                            gc.collect()  # 强制垃圾回收
                            
                except Exception as e:
                    print(f"Error processing chunk {chunk_idx}: {e}")
                    continue
            
            # 缓存完整结果
            self.cache.set(cache_key, results, "stream_processing")
            
        except Exception as e:
            print(f"Error in stream processing: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """获取文件哈希（仅读取部分内容以提高速度）"""
        hash_obj = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            # 读取文件开头和结尾的部分内容
            hash_obj.update(f.read(8192))  # 前 8KB
            
            f.seek(-8192, 2)  # 从文件末尾开始
            hash_obj.update(f.read(8192))  # 后 8KB
            
        return hash_obj.hexdigest()
    
    def _get_cache_key(self, file_hash: str, operation: str) -> str:
        """生成缓存键"""
        return f"{file_hash}_{operation}"

class PerformanceOptimizer:
    """性能优化器主类"""
    
    def __init__(self, max_memory_gb: float = 8.0, cache_size_gb: float = 10.0):
        self.memory_manager = MemoryManager(max_memory_gb)
        self.cache = IntelligentCache(cache_size_gb=cache_size_gb)
        self.chunker = DataChunker(self.memory_manager)
        self.streaming_processor = StreamingProcessor(self.cache)
        self.performance_metrics = []
        
    def optimize_data_loading(self, file_path: str, **kwargs) -> pd.DataFrame:
        """优化数据加载"""
        start_time = datetime.now()
        start_memory = self.memory_manager.get_memory_usage()
        optimizations_applied = []
        
        # 检查文件大小
        file_size_mb = Path(file_path).stat().st_size / 1024 / 1024
        
        if file_size_mb > 500:  # 大于 500MB
            optimizations_applied.append("chunked_loading")
            
            # 分块加载
            chunks = []
            chunk_size = self.memory_manager.suggest_chunk_size(file_size_mb)
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, **kwargs):
                chunks.append(chunk)
                
                # 内存检查
                if self.memory_manager.check_memory_pressure():
                    gc.collect()
            
            data = pd.concat(chunks, ignore_index=True)
            del chunks  # 清理中间变量
            
        else:
            # 直接加载
            data = pd.read_csv(file_path, **kwargs)
        
        # 内存优化
        if file_size_mb > 100:  # 大于 100MB 才进行优化
            data = self._optimize_dataframe_memory(data)
            optimizations_applied.append("memory_optimization")
        
        # 记录性能指标
        end_time = datetime.now()
        end_memory = self.memory_manager.get_memory_usage()
        
        metrics = PerformanceMetrics(
            memory_usage_mb=end_memory - start_memory,
            processing_time_s=(end_time - start_time).total_seconds(),
            cpu_usage_percent=psutil.cpu_percent(),
            cache_hit_rate=0.0,  # 新加载的数据
            data_size_mb=file_size_mb,
            optimization_applied=optimizations_applied
        )
        
        self.performance_metrics.append(metrics)
        
        return data
    
    def optimize_computation(self, computation_func: callable, 
                           data: pd.DataFrame, *args, **kwargs) -> Any:
        """优化计算过程"""
        # 生成缓存键
        data_hash = hashlib.md5(pd.util.hash_pandas_object(data).values).hexdigest()
        cache_key = f"{data_hash}_{computation_func.__name__}_{hash(str(args) + str(kwargs))}"
        
        # 检查缓存
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = datetime.now()
        optimizations_applied = []
        
        # 检查数据大小决定优化策略
        data_size_mb = data.memory_usage(deep=True).sum() / 1024 / 1024
        
        if data_size_mb > 200:  # 大数据集使用分块处理
            optimizations_applied.append("chunked_computation")
            
            chunks = self.chunker.create_chunks(data)
            chunk_results = self.chunker.process_chunks_parallel(
                chunks, data, 
                lambda chunk_data, chunk_id: computation_func(chunk_data, *args, **kwargs)
            )
            
            # 合并结果（根据函数类型）
            if hasattr(chunk_results[0], 'shape'):  # DataFrame/Array
                result = pd.concat(chunk_results, ignore_index=True)
            elif isinstance(chunk_results[0], dict):  # 字典结果
                result = self._merge_dict_results(chunk_results)
            else:  # 其他类型
                result = chunk_results
                
        else:
            # 直接计算
            result = computation_func(data, *args, **kwargs)
        
        # 缓存结果
        self.cache.set(cache_key, result, "computation")
        
        # 记录性能
        end_time = datetime.now()
        metrics = PerformanceMetrics(
            memory_usage_mb=self.memory_manager.get_memory_usage(),
            processing_time_s=(end_time - start_time).total_seconds(),
            cpu_usage_percent=psutil.cpu_percent(),
            cache_hit_rate=0.0,
            data_size_mb=data_size_mb,
            optimization_applied=optimizations_applied
        )
        
        self.performance_metrics.append(metrics)
        
        return result
    
    def _optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """优化 DataFrame 内存使用"""
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            if col_type == 'object':
                # 尝试转换为分类数据
                if optimized_df[col].nunique() / len(optimized_df) < 0.5:  # 50% 阈值
                    optimized_df[col] = optimized_df[col].astype('category')
            
            elif col_type.name.startswith('int'):
                # 优化整数类型
                col_min = optimized_df[col].min()
                col_max = optimized_df[col].max()
                
                if col_min >= 0:
                    if col_max < 255:
                        optimized_df[col] = optimized_df[col].astype(np.uint8)
                    elif col_max < 65535:
                        optimized_df[col] = optimized_df[col].astype(np.uint16)
                    elif col_max < 4294967295:
                        optimized_df[col] = optimized_df[col].astype(np.uint32)
                else:
                    if col_min > -128 and col_max < 127:
                        optimized_df[col] = optimized_df[col].astype(np.int8)
                    elif col_min > -32768 and col_max < 32767:
                        optimized_df[col] = optimized_df[col].astype(np.int16)
                    elif col_min > -2147483648 and col_max < 2147483647:
                        optimized_df[col] = optimized_df[col].astype(np.int32)
            
            elif col_type.name.startswith('float'):
                # 优化浮点类型
                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        return optimized_df
    
    def _merge_dict_results(self, dict_results: List[Dict]) -> Dict:
        """合并字典类型的结果"""
        if not dict_results:
            return {}
        
        merged = {}
        
        for key in dict_results[0].keys():
            values = [result[key] for result in dict_results if key in result]
            
            if isinstance(values[0], (int, float)):
                merged[key] = sum(values) / len(values)  # 平均值
            elif isinstance(values[0], list):
                merged[key] = [item for sublist in values for item in sublist]  # 合并列表
            elif isinstance(values[0], pd.DataFrame):
                merged[key] = pd.concat(values, ignore_index=True)
            else:
                merged[key] = values  # 保持原始列表
        
        return merged
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        if not self.performance_metrics:
            return {'message': 'No performance data available'}
        
        recent_metrics = self.performance_metrics[-10:]  # 最近 10 次
        
        return {
            'total_operations': len(self.performance_metrics),
            'recent_operations': len(recent_metrics),
            'average_memory_usage_mb': sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics),
            'average_processing_time_s': sum(m.processing_time_s for m in recent_metrics) / len(recent_metrics),
            'cache_statistics': self._get_cache_statistics(),
            'optimization_frequency': self._get_optimization_frequency(),
            'recommendations': self._generate_performance_recommendations()
        }
    
    def _get_cache_statistics(self) -> Dict:
        """获取缓存统计"""
        conn = sqlite3.connect(self.cache.metadata_db)
        
        # 总条目数
        cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
        total_entries = cursor.fetchone()[0]
        
        # 总大小
        cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
        total_size = cursor.fetchone()[0] or 0
        
        # 平均访问次数
        cursor = conn.execute("SELECT AVG(access_count) FROM cache_entries")
        avg_access = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'total_size_mb': total_size / 1024 / 1024,
            'average_access_count': round(avg_access, 2),
            'cache_utilization': (total_size / self.cache.max_size_bytes) * 100
        }
    
    def _get_optimization_frequency(self) -> Dict:
        """获取优化频率统计"""
        optimization_counts = {}
        
        for metrics in self.performance_metrics:
            for opt in metrics.optimization_applied:
                optimization_counts[opt] = optimization_counts.get(opt, 0) + 1
        
        return optimization_counts
    
    def _generate_performance_recommendations(self) -> List[str]:
        """生成性能建议"""
        recommendations = []
        
        if not self.performance_metrics:
            return recommendations
        
        recent_metrics = self.performance_metrics[-5:]
        avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
        avg_time = sum(m.processing_time_s for m in recent_metrics) / len(recent_metrics)
        
        if avg_memory > 1000:  # 超过 1GB
            recommendations.append("💾 内存使用较高，建议启用更多数据分块处理")
        
        if avg_time > 60:  # 超过 1 分钟
            recommendations.append("⚡ 处理时间较长，建议使用并行处理或缓存")
        
        cache_stats = self._get_cache_statistics()
        if cache_stats['cache_utilization'] > 90:
            recommendations.append("🗄️ 缓存接近满载，建议清理或增加缓存空间")
        
        optimization_counts = self._get_optimization_frequency()
        if optimization_counts.get('chunked_processing', 0) < 2:
            recommendations.append("🔧 考虑为大数据集启用分块处理优化")
        
        return recommendations

# 全局实例
performance_optimizer = PerformanceOptimizer()