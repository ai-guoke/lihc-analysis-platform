"""
Multi-omics Data Integration Module
整合RNA-seq、CNV、突变和甲基化数据
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)


class MultiOmicsIntegrator:
    """多组学数据整合器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.omics_data = {}
        self.integrated_features = None
        self.feature_weights = {}
        
    def load_expression_data(self, file_path: str) -> pd.DataFrame:
        """加载RNA-seq表达数据"""
        logger.info("Loading RNA-seq expression data...")
        expr_data = pd.read_csv(file_path, index_col=0)
        
        # 数据预处理
        # 1. Log2转换
        expr_data = np.log2(expr_data + 1)
        
        # 2. 过滤低表达基因
        mean_expr = expr_data.mean(axis=1)
        expr_data = expr_data[mean_expr > 1]
        
        # Check if data is empty after filtering
        if expr_data.empty:
            logger.warning("No genes passed expression threshold")
            self.omics_data['expression'] = expr_data
            return expr_data
        
        # 3. 标准化
        scaler = StandardScaler()
        expr_normalized = pd.DataFrame(
            scaler.fit_transform(expr_data.T).T,
            index=expr_data.index,
            columns=expr_data.columns
        )
        
        self.omics_data['expression'] = expr_normalized
        logger.info(f"Loaded {expr_normalized.shape[0]} genes x {expr_normalized.shape[1]} samples")
        return expr_normalized
    
    def load_cnv_data(self, file_path: str) -> pd.DataFrame:
        """加载拷贝数变异数据"""
        logger.info("Loading CNV data...")
        cnv_data = pd.read_csv(file_path, index_col=0)
        
        # CNV分类：-2(纯合缺失), -1(杂合缺失), 0(正常), 1(增益), 2(扩增)
        cnv_categories = pd.DataFrame(
            np.select(
                [cnv_data < -1, cnv_data < -0.3, cnv_data > 0.3, cnv_data > 1],
                [-2, -1, 1, 2],
                default=0
            ),
            index=cnv_data.index,
            columns=cnv_data.columns
        )
        
        self.omics_data['cnv'] = cnv_categories
        logger.info(f"Loaded CNV data for {cnv_categories.shape[0]} genes")
        return cnv_categories
    
    def load_mutation_data(self, file_path: str) -> pd.DataFrame:
        """加载突变数据"""
        logger.info("Loading mutation data...")
        mut_data = pd.read_csv(file_path)
        
        # 转换为二进制矩阵（0=无突变, 1=有突变）
        mutation_matrix = pd.crosstab(
            mut_data['gene_id'], 
            mut_data['sample_id']
        ).astype(int)
        
        # 计算突变频率
        mut_freq = mutation_matrix.sum(axis=1) / mutation_matrix.shape[1]
        
        # 过滤低频突变（<5%）
        mutation_matrix = mutation_matrix[mut_freq >= 0.05]
        
        self.omics_data['mutation'] = mutation_matrix
        logger.info(f"Loaded mutations for {mutation_matrix.shape[0]} genes")
        return mutation_matrix
    
    def load_methylation_data(self, file_path: str) -> pd.DataFrame:
        """加载甲基化数据"""
        logger.info("Loading methylation data...")
        meth_data = pd.read_csv(file_path, index_col=0)
        
        # Beta值应该在0-1之间
        meth_data = meth_data.clip(0, 1)
        
        # 过滤缺失值过多的探针
        missing_rate = meth_data.isna().sum(axis=1) / meth_data.shape[1]
        meth_data = meth_data[missing_rate < 0.2]
        
        # 填充缺失值
        imputer = SimpleImputer(strategy='mean')
        meth_imputed = pd.DataFrame(
            imputer.fit_transform(meth_data.T).T,
            index=meth_data.index,
            columns=meth_data.columns
        )
        
        self.omics_data['methylation'] = meth_imputed
        logger.info(f"Loaded methylation data for {meth_imputed.shape[0]} probes")
        return meth_imputed
    
    def integrate_omics(self, integration_method: str = "concatenate") -> pd.DataFrame:
        """整合多组学数据"""
        logger.info(f"Integrating multi-omics data using {integration_method} method...")
        
        if integration_method == "concatenate":
            return self._concatenate_integration()
        elif integration_method == "similarity_network":
            return self._similarity_network_fusion()
        elif integration_method == "mofa":
            return self._mofa_integration()
        else:
            raise ValueError(f"Unknown integration method: {integration_method}")
    
    def _concatenate_integration(self) -> pd.DataFrame:
        """简单拼接整合"""
        # 获取共同样本
        common_samples = None
        for omics_type, data in self.omics_data.items():
            if common_samples is None:
                common_samples = set(data.columns)
            else:
                common_samples = common_samples.intersection(set(data.columns))
        
        common_samples = sorted(list(common_samples))
        logger.info(f"Found {len(common_samples)} common samples across all omics")
        
        # 拼接特征
        integrated_list = []
        feature_info = []
        
        for omics_type, data in self.omics_data.items():
            # 选择共同样本
            data_subset = data[common_samples]
            
            # 添加前缀以区分来源
            data_subset.index = [f"{omics_type}_{idx}" for idx in data_subset.index]
            
            integrated_list.append(data_subset)
            feature_info.extend([(idx, omics_type) for idx in data_subset.index])
        
        # 合并所有特征
        integrated_data = pd.concat(integrated_list, axis=0)
        
        # 保存特征信息
        self.feature_info = pd.DataFrame(
            feature_info, 
            columns=['feature_id', 'omics_type']
        )
        
        self.integrated_features = integrated_data
        return integrated_data
    
    def _similarity_network_fusion(self) -> pd.DataFrame:
        """相似性网络融合（SNF）"""
        logger.info("Performing Similarity Network Fusion...")
        
        # 获取共同样本
        common_samples = None
        for omics_type, data in self.omics_data.items():
            if common_samples is None:
                common_samples = set(data.columns)
            else:
                common_samples = common_samples.intersection(set(data.columns))
        
        if not common_samples:
            logger.warning("No common samples found across omics data")
            return pd.DataFrame()
        
        common_samples = sorted(list(common_samples))
        
        # 为每种组学数据构建相似性网络
        similarity_networks = []
        
        for omics_type, data in self.omics_data.items():
            # 选择共同样本
            data_subset = data[common_samples]
            
            # 计算样本间相似性（使用相关系数）
            similarity = data_subset.T.corr()
            
            # 转换为相似性网络（高斯核）
            similarity_network = np.exp(-np.square(1 - similarity) / 0.5)
            similarity_networks.append(similarity_network.values)
        
        # SNF算法迭代融合
        n_iter = 20
        fused_network = self._snf_iterate(similarity_networks, n_iter)
        
        # 对融合网络进行谱聚类或降维
        # 这里使用PCA作为示例
        pca = PCA(n_components=100)
        integrated_features = pca.fit_transform(fused_network)
        
        # 转换为DataFrame
        feature_names = [f"SNF_PC{i+1}" for i in range(integrated_features.shape[1])]
        
        integrated_data = pd.DataFrame(
            integrated_features.T,
            index=feature_names,
            columns=common_samples
        )
        
        self.integrated_features = integrated_data
        return integrated_data
    
    def _snf_iterate(self, networks: List[np.ndarray], n_iter: int) -> np.ndarray:
        """SNF迭代算法"""
        n_networks = len(networks)
        n_samples = networks[0].shape[0]
        
        # 初始化 - 转换为numpy数组
        P = [net.values if hasattr(net, 'values') else net for net in networks]
        
        for _ in range(n_iter):
            P_next = []
            
            for i in range(n_networks):
                # 计算其他网络的平均
                P_avg = np.zeros((n_samples, n_samples))
                for j in range(n_networks):
                    if i != j:
                        P_avg += P[j]
                P_avg /= (n_networks - 1)
                
                # 更新网络
                P_next.append(P[i] @ P_avg @ P[i].T)
            
            P = P_next
        
        # 最终融合
        fused = np.mean(P, axis=0)
        return fused
    
    def _mofa_integration(self) -> pd.DataFrame:
        """MOFA (Multi-Omics Factor Analysis) 集成"""
        logger.info("Performing MOFA integration...")
        
        # 这里使用简化版的因子分析
        # 实际应用中应使用MOFA+ Python包
        
        from sklearn.decomposition import FactorAnalysis
        
        # 准备数据
        common_samples = None
        for data in self.omics_data.values():
            if common_samples is None:
                common_samples = set(data.columns)
            else:
                common_samples = common_samples.intersection(set(data.columns))
        
        common_samples = sorted(list(common_samples))
        
        # 对每种组学数据进行因子分析
        factors_list = []
        n_factors = 50
        
        for omics_type, data in self.omics_data.items():
            data_subset = data[common_samples].T
            
            # 因子分析
            fa = FactorAnalysis(n_components=n_factors, random_state=42)
            factors = fa.fit_transform(data_subset)
            
            factors_df = pd.DataFrame(
                factors,
                index=common_samples,
                columns=[f"{omics_type}_Factor{i+1}" for i in range(n_factors)]
            )
            
            factors_list.append(factors_df)
        
        # 合并所有因子
        all_factors = pd.concat(factors_list, axis=1)
        
        # 第二轮因子分析找到共同因子
        fa_final = FactorAnalysis(n_components=30, random_state=42)
        integrated_factors = fa_final.fit_transform(all_factors)
        
        integrated_data = pd.DataFrame(
            integrated_factors.T,
            index=[f"MOFA_Factor{i+1}" for i in range(30)],
            columns=common_samples
        )
        
        self.integrated_features = integrated_data
        return integrated_data
    
    def calculate_feature_importance(self, target: pd.Series) -> pd.DataFrame:
        """计算每个特征对目标变量的重要性"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.feature_selection import mutual_info_regression
        
        if self.integrated_features is None:
            raise ValueError("Please run integrate_omics() first")
        
        # 准备数据
        common_samples = list(set(self.integrated_features.columns) & set(target.index))
        X = self.integrated_features[common_samples].T
        y = target[common_samples]
        
        # 1. 随机森林特征重要性
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        rf_importance = pd.Series(rf.feature_importances_, index=X.columns)
        
        # 2. 互信息
        mi_importance = pd.Series(
            mutual_info_regression(X, y, random_state=42),
            index=X.columns
        )
        
        # 合并结果
        importance_df = pd.DataFrame({
            'rf_importance': rf_importance,
            'mi_importance': mi_importance,
            'combined_importance': (rf_importance + mi_importance) / 2
        })
        
        return importance_df.sort_values('combined_importance', ascending=False)
    
    def save_integrated_data(self, output_dir: str):
        """保存整合后的数据"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存整合数据
        self.integrated_features.to_csv(output_path / "integrated_features.csv")
        
        # 保存特征信息
        if hasattr(self, 'feature_info'):
            self.feature_info.to_csv(output_path / "feature_info.csv", index=False)
        
        # 保存各组学数据
        for omics_type, data in self.omics_data.items():
            data.to_csv(output_path / f"{omics_type}_processed.csv")
        
        logger.info(f"Integrated data saved to {output_path}")


def demo_multi_omics_integration():
    """演示多组学数据整合"""
    
    # 创建整合器
    integrator = MultiOmicsIntegrator()
    
    # 生成模拟数据
    n_samples = 100
    sample_names = [f"Sample_{i:03d}" for i in range(n_samples)]
    
    # 1. 表达数据
    expr_data = pd.DataFrame(
        np.random.randn(500, n_samples) * 2 + 8,
        index=[f"Gene_{i:04d}" for i in range(500)],
        columns=sample_names
    )
    expr_data.to_csv("data/raw/test_expression.csv")
    
    # 2. CNV数据
    cnv_data = pd.DataFrame(
        np.random.randn(300, n_samples) * 0.5,
        index=[f"Gene_{i:04d}" for i in range(300)],
        columns=sample_names
    )
    cnv_data.to_csv("data/raw/test_cnv.csv")
    
    # 3. 突变数据
    mut_records = []
    for i in range(200):
        gene = f"Gene_{i:04d}"
        # 随机选择10-30%的样本有突变
        mutated_samples = np.random.choice(sample_names, 
                                         size=np.random.randint(10, 30), 
                                         replace=False)
        for sample in mutated_samples:
            mut_records.append({
                'gene_id': gene,
                'sample_id': sample,
                'mutation_type': np.random.choice(['missense', 'nonsense', 'frameshift'])
            })
    
    mut_df = pd.DataFrame(mut_records)
    mut_df.to_csv("data/raw/test_mutations.csv", index=False)
    
    # 加载数据
    integrator.load_expression_data("data/raw/test_expression.csv")
    integrator.load_cnv_data("data/raw/test_cnv.csv")
    integrator.load_mutation_data("data/raw/test_mutations.csv")
    
    # 整合数据
    integrated = integrator.integrate_omics(integration_method="concatenate")
    
    print(f"Integrated data shape: {integrated.shape}")
    print(f"Integrated data preview:\n{integrated.iloc[:5, :5]}")
    
    # 保存结果
    integrator.save_integrated_data("results/multi_omics")
    
    return integrator


if __name__ == "__main__":
    # 运行演示
    demo_multi_omics_integration()