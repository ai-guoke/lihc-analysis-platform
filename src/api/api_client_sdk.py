"""
LIHC Platform API Client SDK
API客户端SDK
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class APIResponse:
    """API响应数据类"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    timestamp: Optional[str] = None
    error_code: Optional[int] = None

class LIHCAPIClient:
    """LIHC平台API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = None):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器地址
            api_token: API认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token or "ultrathink_api_token_2025"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            return APIResponse(
                success=data.get('success', False),
                message=data.get('message', ''),
                data=data.get('data'),
                task_id=data.get('task_id'),
                timestamp=data.get('timestamp')
            )
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                message=f"Request failed: {str(e)}",
                error_code=getattr(e.response, 'status_code', None)
            )
        except json.JSONDecodeError:
            return APIResponse(
                success=False,
                message="Invalid JSON response from server"
            )
    
    def health_check(self) -> APIResponse:
        """健康检查"""
        return self._make_request("GET", "/health")
    
    def get_api_info(self) -> APIResponse:
        """获取API信息"""
        return self._make_request("GET", "/")
    
    def analyze_single_cell(self, sample_data: Dict, analysis_params: Dict = None,
                           quality_control: bool = True, clustering_method: str = "leiden") -> APIResponse:
        """
        单细胞RNA-seq分析
        
        Args:
            sample_data: 样本数据
            analysis_params: 分析参数
            quality_control: 是否进行质量控制
            clustering_method: 聚类方法
        """
        payload = {
            "sample_data": sample_data,
            "analysis_params": analysis_params or {},
            "quality_control": quality_control,
            "clustering_method": clustering_method
        }
        
        return self._make_request("POST", "/analysis/single-cell", json=payload)
    
    def discover_biomarkers(self, omics_data: Dict, clinical_data: Dict = None,
                           algorithms: List[str] = None, validation_split: float = 0.2) -> APIResponse:
        """
        AI驱动的生物标志物发现
        
        Args:
            omics_data: 组学数据
            clinical_data: 临床数据
            algorithms: 使用的算法列表
            validation_split: 验证集比例
        """
        payload = {
            "omics_data": omics_data,
            "clinical_data": clinical_data,
            "algorithms": algorithms or ['random_forest', 'lasso', 'xgboost'],
            "validation_split": validation_split
        }
        
        return self._make_request("POST", "/analysis/biomarker", json=payload)
    
    def predict_drug_combinations(self, patient_profile: Dict, available_drugs: List[str],
                                 combination_size: int = 2, prediction_model: str = "bliss_independence") -> APIResponse:
        """
        药物组合疗法预测
        
        Args:
            patient_profile: 患者档案
            available_drugs: 可用药物列表
            combination_size: 组合药物数量
            prediction_model: 预测模型
        """
        payload = {
            "patient_profile": patient_profile,
            "available_drugs": available_drugs,
            "combination_size": combination_size,
            "prediction_model": prediction_model
        }
        
        return self._make_request("POST", "/analysis/drug-combination", json=payload)
    
    def integrate_multiomics(self, omics_data: Dict[str, Dict], integration_method: str = "SNF",
                            feature_selection: bool = True) -> APIResponse:
        """
        多组学数据整合
        
        Args:
            omics_data: 多组学数据字典
            integration_method: 整合方法
            feature_selection: 是否进行特征选择
        """
        payload = {
            "omics_data": omics_data,
            "integration_method": integration_method,
            "feature_selection": feature_selection
        }
        
        return self._make_request("POST", "/analysis/multiomics", json=payload)
    
    def stratify_patients(self, patient_data: Dict, stratification_method: str = "consensus_clustering",
                         n_clusters: int = None, risk_factors: List[str] = None) -> APIResponse:
        """
        患者分层分析
        
        Args:
            patient_data: 患者数据
            stratification_method: 分层方法
            n_clusters: 聚类数量
            risk_factors: 风险因子
        """
        payload = {
            "patient_data": patient_data,
            "stratification_method": stratification_method,
            "n_clusters": n_clusters,
            "risk_factors": risk_factors or []
        }
        
        return self._make_request("POST", "/analysis/stratification", json=payload)
    
    def generate_report(self, report_type: str, analysis_results: Dict, output_format: str = "HTML",
                       template_customization: Dict = None) -> APIResponse:
        """
        生成智能报告
        
        Args:
            report_type: 报告类型
            analysis_results: 分析结果
            output_format: 输出格式
            template_customization: 模板自定义
        """
        payload = {
            "report_type": report_type,
            "analysis_results": analysis_results,
            "output_format": output_format,
            "template_customization": template_customization
        }
        
        return self._make_request("POST", "/reports/generate", json=payload)
    
    def get_task_status(self, task_id: str) -> APIResponse:
        """查询任务状态"""
        return self._make_request("GET", f"/tasks/{task_id}")
    
    def wait_for_task_completion(self, task_id: str, max_wait_time: int = 1800,
                               check_interval: int = 5) -> APIResponse:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = self.get_task_status(task_id)
            
            if not response.success:
                return response
            
            status = response.data.get('status', 'unknown')
            
            if status == 'completed':
                return response
            elif status == 'failed':
                return APIResponse(
                    success=False,
                    message=f"Task failed: {response.data.get('message', 'Unknown error')}",
                    data=response.data
                )
            
            print(f"Task {task_id}: {status} ({response.data.get('progress', 0)*100:.1f}%)")
            time.sleep(check_interval)
        
        return APIResponse(
            success=False,
            message=f"Task timeout after {max_wait_time} seconds"
        )
    
    def run_analysis_and_wait(self, analysis_func, *args, **kwargs) -> APIResponse:
        """运行分析并等待完成"""
        # 启动分析
        response = analysis_func(*args, **kwargs)
        
        if not response.success or not response.task_id:
            return response
        
        print(f"Analysis started, task ID: {response.task_id}")
        
        # 等待完成
        return self.wait_for_task_completion(response.task_id)
    
    def batch_analysis(self, analyses: List[Dict]) -> APIResponse:
        """批量分析"""
        payload = analyses
        return self._make_request("POST", "/analysis/batch", json=payload)
    
    def upload_data(self, file_path: str, data_type: str) -> APIResponse:
        """上传数据文件"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'data_type': data_type}
            
            # 临时移除Content-Type头以支持文件上传
            headers = self.headers.copy()
            del headers['Content-Type']
            
            try:
                response = requests.post(
                    f"{self.base_url}/data/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                return APIResponse(
                    success=data.get('success', False),
                    message=data.get('message', ''),
                    data=data.get('data')
                )
                
            except Exception as e:
                return APIResponse(
                    success=False,
                    message=f"Upload failed: {str(e)}"
                )
    
    def get_api_stats(self) -> APIResponse:
        """获取API使用统计"""
        return self._make_request("GET", "/stats")

# 便捷函数
def create_sample_data(n_genes: int = 2000, n_cells: int = 500) -> Dict:
    """创建示例单细胞数据"""
    import numpy as np
    
    np.random.seed(42)
    expression_matrix = np.random.negative_binomial(5, 0.3, (n_genes, n_cells))
    
    return {
        "expression_matrix": expression_matrix.tolist(),
        "gene_names": [f"Gene_{i}" for i in range(n_genes)],
        "cell_barcodes": [f"Cell_{i}" for i in range(n_cells)],
        "metadata": {
            "n_genes": n_genes,
            "n_cells": n_cells,
            "sequencing_platform": "10X Genomics",
            "sample_type": "LIHC_tumor"
        }
    }

def create_omics_data(n_samples: int = 100, n_features: int = 1000) -> Dict:
    """创建示例组学数据"""
    import numpy as np
    
    np.random.seed(42)
    
    return {
        "genomics": {
            "mutation_data": np.random.randint(0, 2, (n_samples, n_features//2)).tolist(),
            "cnv_data": np.random.normal(0, 0.5, (n_samples, n_features//2)).tolist(),
            "feature_names": [f"Genomic_Feature_{i}" for i in range(n_features//2)],
            "sample_ids": [f"Sample_{i}" for i in range(n_samples)]
        },
        "transcriptomics": {
            "expression_data": np.random.lognormal(0, 1, (n_samples, n_features)).tolist(),
            "feature_names": [f"Gene_{i}" for i in range(n_features)],
            "sample_ids": [f"Sample_{i}" for i in range(n_samples)]
        },
        "proteomics": {
            "protein_abundance": np.random.normal(0, 1, (n_samples, n_features//4)).tolist(),
            "feature_names": [f"Protein_{i}" for i in range(n_features//4)],
            "sample_ids": [f"Sample_{i}" for i in range(n_samples)]
        }
    }

def create_patient_profile(patient_id: str = "P001") -> Dict:
    """创建示例患者档案"""
    import numpy as np
    
    np.random.seed(42)
    
    return {
        "patient_id": patient_id,
        "demographics": {
            "age": 65,
            "gender": "male",
            "ethnicity": "asian"
        },
        "clinical_features": {
            "stage": "III",
            "grade": "G2",
            "tumor_size": 5.2,
            "child_pugh_score": "A",
            "ecog_performance": 1,
            "hepatitis_status": "HBV+"
        },
        "biomarkers": {
            "AFP": 150.5,
            "AFP_L3": 25.8,
            "DCP": 85.2
        },
        "molecular_profile": {
            "mutations": ["TP53", "CTNNB1", "ARID1A"],
            "expression_signature": np.random.normal(0, 1, 50).tolist(),
            "copy_number_alterations": ["8q+", "17p-", "1q+"]
        },
        "treatment_history": {
            "previous_treatments": ["surgery", "TACE"],
            "response_to_previous": ["partial_response", "stable_disease"],
            "treatment_dates": ["2024-01-15", "2024-03-20"]
        }
    }

# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = LIHCAPIClient()
    
    print("🔍 Testing LIHC API Client...")
    
    # 健康检查
    health = client.health_check()
    print(f"Health Check: {health.success} - {health.message}")
    
    if health.success:
        # 创建示例数据
        sample_data = create_sample_data(n_genes=100, n_cells=50)
        
        # 单细胞分析
        print("\n🧬 Starting single cell analysis...")
        sc_response = client.analyze_single_cell(sample_data)
        
        if sc_response.success and sc_response.task_id:
            print(f"Task created: {sc_response.task_id}")
            
            # 等待完成
            result = client.wait_for_task_completion(sc_response.task_id, max_wait_time=300)
            
            if result.success:
                print("✅ Single cell analysis completed!")
                print(f"Results: {result.data}")
            else:
                print(f"❌ Analysis failed: {result.message}")
        
        # API统计
        stats = client.get_api_stats()
        if stats.success:
            print(f"\n📊 API Stats: {stats.data}")
    
    print("\n🎉 API Client testing completed!")