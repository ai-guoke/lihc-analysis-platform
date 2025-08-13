# 🛠 LIHC Platform 开发者文档

本文档为开发者提供详细的开发指南、架构说明、API文档和最佳实践。

## 📋 目录

- [开发环境设置](#开发环境设置)
- [项目架构](#项目架构)
- [核心模块](#核心模块)
- [API参考](#api参考)
- [添加新功能](#添加新功能)
- [测试指南](#测试指南)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [发布流程](#发布流程)

---

## 开发环境设置

### 1. 克隆项目

```bash
# 克隆主仓库
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 添加上游仓库（用于同步更新）
git remote add upstream https://github.com/ai-guoke/lihc-analysis-platform.git
```

### 2. Python环境配置

```bash
# 创建虚拟环境（推荐使用Python 3.9）
python3.9 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 升级pip
pip install --upgrade pip setuptools wheel

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 开发工具配置

#### VS Code配置

创建 `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    "*.egg-info": true
  }
}
```

#### PyCharm配置

1. 设置Python解释器：`Settings → Project → Python Interpreter`
2. 配置代码风格：`Settings → Editor → Code Style → Python`
3. 启用格式化工具：`Settings → Tools → External Tools → Add Black`

### 4. Pre-commit Hooks

```bash
# 安装pre-commit
pip install pre-commit

# 安装git hooks
pre-commit install

# 手动运行所有hooks
pre-commit run --all-files
```

`.pre-commit-config.yaml` 配置:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--ignore=E203,W503']

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ['--profile', 'black']
```

---

## 项目架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户界面层                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dash Web   │  │   REST API   │  │   CLI界面    │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                      业务逻辑层                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  分析模块   │  │   可视化模块  │  │   报告模块   │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                      数据访问层                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  数据处理   │  │   缓存管理   │  │  数据库访问  │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 目录结构详解

```
lihc-analysis-platform/
├── src/                          # 源代码主目录
│   ├── analysis/                # 分析模块
│   │   ├── __init__.py
│   │   ├── base_analyzer.py    # 基础分析器类
│   │   ├── survival_analysis.py # 生存分析
│   │   ├── network_analysis.py  # 网络分析
│   │   ├── five_dimension_prognostic.py # 五维度分析
│   │   ├── ai_biomarker.py     # AI生物标志物
│   │   └── linchpin_target.py  # Linchpin靶点识别
│   │
│   ├── visualization/           # 可视化模块
│   │   ├── __init__.py
│   │   ├── professional_dashboard.py # 主仪表板
│   │   ├── plotly_helper.py    # Plotly辅助函数
│   │   └── chart_factory.py    # 图表工厂类
│   │
│   ├── data_processing/         # 数据处理模块
│   │   ├── __init__.py
│   │   ├── data_upload_manager.py # 数据上传管理
│   │   ├── data_preprocessor.py   # 数据预处理
│   │   ├── data_validator.py      # 数据验证
│   │   └── data_transformer.py    # 数据转换
│   │
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── gene.py             # 基因模型
│   │   ├── sample.py           # 样本模型
│   │   ├── analysis_result.py  # 分析结果模型
│   │   └── dataset.py          # 数据集模型
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── logger.py           # 日志管理
│   │   ├── cache.py            # 缓存管理
│   │   └── helpers.py          # 辅助函数
│   │
│   └── api/                     # API接口
│       ├── __init__.py
│       ├── routes.py           # 路由定义
│       ├── handlers.py         # 请求处理
│       └── serializers.py      # 数据序列化
│
├── tests/                       # 测试代码
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── scripts/                     # 脚本工具
│   ├── init_db.py              # 初始化数据库
│   ├── migrate.py              # 数据库迁移
│   └── deploy.sh               # 部署脚本
│
└── config/                      # 配置文件
    ├── config.yaml             # 主配置文件
    ├── logging.yaml            # 日志配置
    └── database.yaml           # 数据库配置
```

---

## 核心模块

### 1. 分析模块 (analysis/)

#### 基础分析器类

```python
# src/analysis/base_analyzer.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional

class BaseAnalyzer(ABC):
    """所有分析器的基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.results = {}
        
    @abstractmethod
    def validate_input(self, data: pd.DataFrame) -> bool:
        """验证输入数据"""
        pass
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """执行分析"""
        pass
    
    @abstractmethod
    def visualize(self, results: Dict[str, Any]) -> Any:
        """可视化结果"""
        pass
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """运行完整分析流程"""
        if not self.validate_input(data):
            raise ValueError("Invalid input data")
        
        self.results = self.analyze(data, **kwargs)
        self.results['visualization'] = self.visualize(self.results)
        
        return self.results
```

#### 五维度分析实现

```python
# src/analysis/five_dimension_prognostic.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple

class FiveDimensionPrognosticAnalyzer(BaseAnalyzer):
    """五维度预后分析器"""
    
    DIMENSIONS = ['tumor', 'immune', 'stromal', 'ecm', 'cytokine']
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.gene_sets = self._load_gene_sets()
        self.weights = self.config.get('weights', {
            'tumor': 0.3,
            'immune': 0.25,
            'stromal': 0.2,
            'ecm': 0.15,
            'cytokine': 0.1
        })
    
    def _load_gene_sets(self) -> Dict[str, List[str]]:
        """加载各维度基因集"""
        return {
            'tumor': ['TP53', 'EGFR', 'MYC', ...],
            'immune': ['CD8A', 'CD4', 'FOXP3', ...],
            'stromal': ['VIM', 'FAP', 'ACTA2', ...],
            'ecm': ['COL1A1', 'FN1', 'LAMB1', ...],
            'cytokine': ['IL6', 'TNF', 'IFNG', ...]
        }
    
    def calculate_dimension_score(
        self, 
        expression: pd.DataFrame, 
        dimension: str
    ) -> pd.Series:
        """计算单个维度得分"""
        genes = self.gene_sets[dimension]
        available_genes = list(set(genes) & set(expression.index))
        
        if not available_genes:
            return pd.Series(0, index=expression.columns)
        
        # 使用GSVA算法计算富集分数
        dimension_expr = expression.loc[available_genes]
        scores = self._gsva(dimension_expr)
        
        return scores
    
    def _gsva(self, expression: pd.DataFrame) -> pd.Series:
        """GSVA算法实现"""
        # 简化的GSVA实现
        z_scores = StandardScaler().fit_transform(expression.T)
        scores = np.mean(z_scores, axis=1)
        return pd.Series(scores, index=expression.columns)
    
    def analyze(
        self, 
        expression: pd.DataFrame,
        clinical: pd.DataFrame,
        **kwargs
    ) -> Dict[str, Any]:
        """执行五维度分析"""
        results = {
            'dimension_scores': {},
            'integrated_score': None,
            'risk_groups': None,
            'survival_analysis': None
        }
        
        # 计算各维度得分
        for dim in self.DIMENSIONS:
            scores = self.calculate_dimension_score(expression, dim)
            results['dimension_scores'][dim] = scores
        
        # 计算综合得分
        integrated = self._integrate_scores(results['dimension_scores'])
        results['integrated_score'] = integrated
        
        # 风险分组
        results['risk_groups'] = self._stratify_risk(integrated)
        
        # 生存分析
        if clinical is not None:
            results['survival_analysis'] = self._survival_analysis(
                results['risk_groups'], 
                clinical
            )
        
        return results
```

### 2. 可视化模块 (visualization/)

#### Dashboard组件

```python
# src/visualization/professional_dashboard.py
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px

class ProfessionalDashboard:
    """专业仪表板类"""
    
    def __init__(self, app: dash.Dash):
        self.app = app
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """设置布局"""
        self.app.layout = html.Div([
            # Header
            self._create_header(),
            
            # Main content
            html.Div([
                # Sidebar
                self._create_sidebar(),
                
                # Content area
                html.Div(id='content-area', children=[
                    self._create_default_content()
                ])
            ], className='main-container')
        ])
    
    def _create_header(self) -> html.Div:
        """创建页头"""
        return html.Div([
            html.H1("LIHC Analysis Platform"),
            html.P("Multi-dimensional Analysis System")
        ], className='header')
    
    def _create_sidebar(self) -> html.Div:
        """创建侧边栏"""
        return html.Div([
            self._create_nav_item("Dashboard", "dashboard", "📊"),
            self._create_nav_item("Data Upload", "upload", "📁"),
            self._create_nav_item("Analysis", "analysis", "🔬"),
            self._create_nav_item("Results", "results", "📈"),
        ], className='sidebar')
    
    def setup_callbacks(self):
        """设置回调函数"""
        @self.app.callback(
            Output('content-area', 'children'),
            Input('nav-item-dashboard', 'n_clicks'),
            Input('nav-item-upload', 'n_clicks'),
            Input('nav-item-analysis', 'n_clicks'),
            Input('nav-item-results', 'n_clicks'),
        )
        def update_content(*args):
            """更新内容区域"""
            ctx = dash.callback_context
            if not ctx.triggered:
                return self._create_default_content()
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if 'dashboard' in button_id:
                return self._create_dashboard_content()
            elif 'upload' in button_id:
                return self._create_upload_content()
            elif 'analysis' in button_id:
                return self._create_analysis_content()
            elif 'results' in button_id:
                return self._create_results_content()
            
            return self._create_default_content()
```

### 3. 数据处理模块 (data_processing/)

#### 数据验证器

```python
# src/data_processing/data_validator.py
import pandas as pd
from typing import List, Tuple, Optional

class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_expression_matrix(
        data: pd.DataFrame
    ) -> Tuple[bool, Optional[str]]:
        """验证表达矩阵"""
        # 检查数据类型
        if not isinstance(data, pd.DataFrame):
            return False, "Data must be a pandas DataFrame"
        
        # 检查是否为空
        if data.empty:
            return False, "Data is empty"
        
        # 检查数值类型
        if not all(data.dtypes.apply(lambda x: np.issubdtype(x, np.number))):
            return False, "All values must be numeric"
        
        # 检查缺失值
        if data.isnull().any().any():
            return False, "Data contains missing values"
        
        return True, None
    
    @staticmethod
    def validate_clinical_data(
        data: pd.DataFrame
    ) -> Tuple[bool, Optional[str]]:
        """验证临床数据"""
        required_columns = ['OS_time', 'OS_status']
        
        # 检查必需列
        missing_cols = set(required_columns) - set(data.columns)
        if missing_cols:
            return False, f"Missing required columns: {missing_cols}"
        
        # 检查生存时间
        if not pd.api.types.is_numeric_dtype(data['OS_time']):
            return False, "OS_time must be numeric"
        
        if (data['OS_time'] < 0).any():
            return False, "OS_time cannot be negative"
        
        # 检查生存状态
        if not set(data['OS_status'].unique()).issubset({0, 1}):
            return False, "OS_status must be 0 or 1"
        
        return True, None
```

---

## API参考

### RESTful API

#### 基础端点

```python
# src/api/routes.py
from flask import Flask, request, jsonify
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class HealthCheck(Resource):
    """健康检查端点"""
    def get(self):
        return {'status': 'healthy', 'version': '2.6'}

class DataUpload(Resource):
    """数据上传端点"""
    def post(self):
        file = request.files.get('file')
        if not file:
            return {'error': 'No file provided'}, 400
        
        # 处理文件上传
        result = upload_manager.upload(file)
        return {'dataset_id': result['id']}, 201

class Analysis(Resource):
    """分析端点"""
    def post(self):
        data = request.json
        dataset_id = data.get('dataset_id')
        analysis_type = data.get('type')
        
        # 执行分析
        job_id = analysis_manager.start(dataset_id, analysis_type)
        return {'job_id': job_id}, 202
    
    def get(self, job_id):
        """获取分析结果"""
        result = analysis_manager.get_result(job_id)
        if not result:
            return {'error': 'Job not found'}, 404
        return result

# 注册路由
api.add_resource(HealthCheck, '/api/health')
api.add_resource(DataUpload, '/api/upload')
api.add_resource(Analysis, '/api/analysis', '/api/analysis/<string:job_id>')
```

#### API文档（OpenAPI）

```yaml
openapi: 3.0.0
info:
  title: LIHC Platform API
  version: 2.6.0
  description: API for LIHC Analysis Platform

paths:
  /api/health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  version:
                    type: string

  /api/upload:
    post:
      summary: Upload dataset
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '201':
          description: File uploaded successfully

  /api/analysis:
    post:
      summary: Start analysis
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                dataset_id:
                  type: string
                type:
                  type: string
                  enum: [survival, network, five_dimension, linchpin, ai_biomarker]
      responses:
        '202':
          description: Analysis started
```

### Python SDK

```python
# sdk/lihc_client.py
import requests
from typing import Dict, Any, Optional

class LIHCClient:
    """LIHC Platform Python客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8050"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def upload_data(
        self, 
        expression_file: str,
        clinical_file: Optional[str] = None
    ) -> str:
        """上传数据"""
        files = {'expression': open(expression_file, 'rb')}
        if clinical_file:
            files['clinical'] = open(clinical_file, 'rb')
        
        response = self.session.post(
            f"{self.base_url}/api/upload",
            files=files
        )
        response.raise_for_status()
        return response.json()['dataset_id']
    
    def run_analysis(
        self,
        dataset_id: str,
        analysis_type: str,
        params: Optional[Dict] = None
    ) -> str:
        """运行分析"""
        data = {
            'dataset_id': dataset_id,
            'type': analysis_type,
            'params': params or {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/analysis",
            json=data
        )
        response.raise_for_status()
        return response.json()['job_id']
    
    def get_results(self, job_id: str) -> Dict[str, Any]:
        """获取结果"""
        response = self.session.get(
            f"{self.base_url}/api/analysis/{job_id}"
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = LIHCClient()
dataset_id = client.upload_data("expression.csv", "clinical.csv")
job_id = client.run_analysis(dataset_id, "five_dimension")
results = client.get_results(job_id)
```

---

## 添加新功能

### 1. 添加新的分析模块

创建新的分析器类:

```python
# src/analysis/my_new_analyzer.py
from .base_analyzer import BaseAnalyzer

class MyNewAnalyzer(BaseAnalyzer):
    """新的分析器"""
    
    def validate_input(self, data: pd.DataFrame) -> bool:
        # 实现输入验证
        return True
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        # 实现分析逻辑
        results = {}
        # ... 分析代码 ...
        return results
    
    def visualize(self, results: Dict[str, Any]) -> Any:
        # 实现可视化
        fig = go.Figure()
        # ... 可视化代码 ...
        return fig
```

注册到分析管理器:

```python
# src/analysis/__init__.py
from .my_new_analyzer import MyNewAnalyzer

ANALYZERS = {
    'survival': SurvivalAnalyzer,
    'network': NetworkAnalyzer,
    'my_new': MyNewAnalyzer,  # 添加新分析器
}
```

### 2. 添加新的可视化组件

```python
# src/visualization/components/my_component.py
import dash_core_components as dcc
import dash_html_components as html

def create_my_component(data):
    """创建新组件"""
    return html.Div([
        html.H3("My New Component"),
        dcc.Graph(
            figure=create_figure(data)
        )
    ])

def create_figure(data):
    """创建图表"""
    # 实现图表创建逻辑
    pass
```

### 3. 添加新的API端点

```python
# src/api/routes.py
@app.route('/api/my_endpoint', methods=['POST'])
def my_endpoint():
    """新的API端点"""
    data = request.json
    
    # 处理请求
    result = process_request(data)
    
    return jsonify(result)
```

---

## 测试指南

### 单元测试

```python
# tests/unit/test_five_dimension.py
import pytest
import pandas as pd
from src.analysis.five_dimension_prognostic import FiveDimensionPrognosticAnalyzer

class TestFiveDimensionAnalyzer:
    """五维度分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return FiveDimensionPrognosticAnalyzer()
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        expression = pd.DataFrame({
            'Sample1': [10.5, 8.3, 12.1],
            'Sample2': [9.2, 7.8, 11.5],
            'Sample3': [11.1, 8.9, 13.2]
        }, index=['TP53', 'EGFR', 'MYC'])
        
        clinical = pd.DataFrame({
            'OS_time': [365, 730, 500],
            'OS_status': [1, 0, 1]
        }, index=['Sample1', 'Sample2', 'Sample3'])
        
        return expression, clinical
    
    def test_dimension_score_calculation(self, analyzer, sample_data):
        """测试维度得分计算"""
        expression, _ = sample_data
        score = analyzer.calculate_dimension_score(expression, 'tumor')
        
        assert isinstance(score, pd.Series)
        assert len(score) == expression.shape[1]
        assert not score.isnull().any()
    
    def test_full_analysis(self, analyzer, sample_data):
        """测试完整分析流程"""
        expression, clinical = sample_data
        results = analyzer.analyze(expression, clinical)
        
        assert 'dimension_scores' in results
        assert 'integrated_score' in results
        assert len(results['dimension_scores']) == 5
```

### 集成测试

```python
# tests/integration/test_api.py
import pytest
from src.app import app

class TestAPI:
    """API集成测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    def test_data_upload(self, client):
        """测试数据上传"""
        data = {'file': (io.BytesIO(b"test data"), 'test.csv')}
        response = client.post('/api/upload', data=data)
        assert response.status_code == 201
        assert 'dataset_id' in response.json
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_five_dimension.py

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html

# 运行并生成报告
pytest --html=report.html --self-contained-html
```

---

## 代码规范

### Python代码风格

遵循 PEP 8 和 Google Python Style Guide:

```python
# 良好的代码示例
class DataProcessor:
    """数据处理器类
    
    Attributes:
        config: 配置字典
        logger: 日志记录器
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化数据处理器
        
        Args:
            config: 配置字典，包含处理参数
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理数据
        
        Args:
            data: 输入数据框
            
        Returns:
            处理后的数据框
            
        Raises:
            ValueError: 当数据无效时
        """
        if data.empty:
            raise ValueError("Input data is empty")
        
        # 数据处理逻辑
        processed = self._normalize(data)
        processed = self._filter_outliers(processed)
        
        return processed
```

### 文档字符串

使用 Google 风格的文档字符串:

```python
def calculate_score(
    expression: pd.DataFrame,
    gene_set: List[str],
    method: str = "ssgsea"
) -> pd.Series:
    """计算基因集富集分数
    
    使用指定方法计算给定基因集在表达矩阵中的富集分数。
    
    Args:
        expression: 基因表达矩阵，行为基因，列为样本
        gene_set: 基因集列表
        method: 富集方法，可选 'ssgsea', 'gsva', 'zscore'
        
    Returns:
        pd.Series: 每个样本的富集分数
        
    Raises:
        ValueError: 当方法不支持或基因集为空时
        
    Example:
        >>> expr = pd.DataFrame(...)
        >>> genes = ['TP53', 'EGFR', 'MYC']
        >>> scores = calculate_score(expr, genes, method='gsva')
    """
    pass
```

### 类型注解

使用类型注解提高代码可读性:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
import pandas as pd
import numpy as np

def analyze_survival(
    time: np.ndarray,
    event: np.ndarray,
    groups: Optional[np.ndarray] = None,
    method: str = "kaplan-meier"
) -> Dict[str, Union[float, np.ndarray]]:
    """分析生存数据"""
    pass
```

---

## 调试技巧

### 1. 使用调试器

```python
# 使用 pdb 调试
import pdb

def complex_function(data):
    pdb.set_trace()  # 设置断点
    result = process_data(data)
    return result

# 使用 ipdb (更友好的界面)
import ipdb

def analyze_data(data):
    ipdb.set_trace()
    # 调试命令：
    # n - 下一行
    # s - 步入函数
    # c - 继续执行
    # l - 显示当前代码
    # p variable - 打印变量
    pass
```

### 2. 日志调试

```python
# src/utils/logger.py
import logging
import sys

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 文件处理器
    file_handler = logging.FileHandler('debug.log')
    file_handler.setLevel(logging.DEBUG)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 使用日志
logger = setup_logger(__name__)

def process_data(data):
    logger.debug(f"Processing data with shape: {data.shape}")
    try:
        result = complex_operation(data)
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        raise
```

### 3. 性能分析

```python
# 使用 cProfile
import cProfile
import pstats

def profile_function():
    """性能分析示例"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 运行要分析的代码
    result = expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 打印前10个最耗时的函数

# 使用装饰器
from functools import wraps
import time

def timeit(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timeit
def slow_function():
    time.sleep(1)
    return "done"
```

---

## 性能优化

### 1. 数据处理优化

```python
# 使用向量化操作
import numpy as np
import pandas as pd

# 慢速循环
def slow_calculation(df):
    results = []
    for _, row in df.iterrows():
        results.append(row['A'] * row['B'] + row['C'])
    return results

# 快速向量化
def fast_calculation(df):
    return df['A'] * df['B'] + df['C']

# 使用 numba 加速
from numba import jit

@jit(nopython=True)
def fast_loop(arr):
    result = 0
    for i in range(len(arr)):
        result += arr[i] ** 2
    return result
```

### 2. 缓存优化

```python
# 使用 functools.lru_cache
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    """缓存计算结果"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

# 使用 Redis 缓存
import redis
import pickle

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def get(self, key):
        value = self.redis_client.get(key)
        if value:
            return pickle.loads(value)
        return None
    
    def set(self, key, value, expire=3600):
        self.redis_client.setex(
            key, 
            expire, 
            pickle.dumps(value)
        )
```

### 3. 并行处理

```python
# 使用 multiprocessing
from multiprocessing import Pool
import pandas as pd

def process_chunk(chunk):
    """处理数据块"""
    return chunk.apply(complex_function)

def parallel_processing(df, n_workers=4):
    """并行处理数据框"""
    chunks = np.array_split(df, n_workers)
    
    with Pool(processes=n_workers) as pool:
        results = pool.map(process_chunk, chunks)
    
    return pd.concat(results)

# 使用 joblib
from joblib import Parallel, delayed

def parallel_analysis(datasets):
    """并行分析多个数据集"""
    results = Parallel(n_jobs=-1)(
        delayed(analyze_dataset)(data) for data in datasets
    )
    return results
```

---

## 发布流程

### 1. 版本管理

遵循语义化版本控制 (Semantic Versioning):

```bash
# 版本格式: MAJOR.MINOR.PATCH
# MAJOR: 不兼容的API更改
# MINOR: 向后兼容的功能添加
# PATCH: 向后兼容的错误修复

# 更新版本
bumpversion patch  # 2.6.0 -> 2.6.1
bumpversion minor  # 2.6.0 -> 2.7.0
bumpversion major  # 2.6.0 -> 3.0.0
```

### 2. 发布检查清单

```markdown
## 发布前检查清单

- [ ] 所有测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] 依赖已锁定
- [ ] 安全扫描通过
- [ ] 性能测试通过
```

### 3. CI/CD配置

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=src

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t lihc-platform:${{ github.ref_name }} .
      - name: Push to registry
        run: |
          docker tag lihc-platform:${{ github.ref_name }} \
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          docker push ghcr.io/${{ github.repository }}:${{ github.ref_name }}

  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Create Release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
          draft: false
          prerelease: false
```

### 4. 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# 配置
VERSION=$1
ENVIRONMENT=$2  # dev, staging, production

if [ -z "$VERSION" ] || [ -z "$ENVIRONMENT" ]; then
    echo "Usage: ./deploy.sh <version> <environment>"
    exit 1
fi

echo "Deploying version $VERSION to $ENVIRONMENT..."

# 拉取最新镜像
docker pull ghcr.io/ai-guoke/lihc-platform:$VERSION

# 停止旧容器
docker stop lihc-platform || true
docker rm lihc-platform || true

# 启动新容器
docker run -d \
    --name lihc-platform \
    --restart unless-stopped \
    -p 8050:8050 \
    -v /data:/app/data \
    -e ENVIRONMENT=$ENVIRONMENT \
    ghcr.io/ai-guoke/lihc-platform:$VERSION

# 健康检查
sleep 10
curl -f http://localhost:8050/api/health || exit 1

echo "Deployment completed successfully!"
```

---

## 故障排除

### 常见问题

#### 1. ImportError

```python
# 问题: ImportError: No module named 'xxx'
# 解决方案:
pip install -r requirements.txt
# 或
pip install xxx
```

#### 2. 内存错误

```python
# 问题: MemoryError
# 解决方案:
# 1. 使用数据分块处理
def process_large_data(file_path, chunk_size=10000):
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        process_chunk(chunk)

# 2. 释放内存
import gc
del large_object
gc.collect()
```

#### 3. 并发问题

```python
# 问题: 多线程/多进程错误
# 解决方案:
# 使用进程池管理
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(task, arg) for arg in args]
    results = [f.result() for f in futures]
```

### 调试工具

```bash
# 内存分析
pip install memory_profiler
python -m memory_profiler script.py

# CPU分析
pip install line_profiler
kernprof -l -v script.py

# 查找内存泄漏
pip install objgraph
python -c "import objgraph; objgraph.show_most_common_types()"
```

---

## 贡献指南

### 提交规范

使用 Conventional Commits:

```bash
# 格式: <type>(<scope>): <subject>

feat(analysis): add new clustering algorithm
fix(ui): resolve dashboard rendering issue
docs(api): update API documentation
style(code): format with black
refactor(data): optimize data processing pipeline
test(unit): add tests for survival analysis
chore(deps): update dependencies
```

### Pull Request流程

1. Fork 仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交代码
5. 创建 Pull Request
6. 代码审查
7. 合并

### 代码审查清单

- [ ] 代码符合规范
- [ ] 有适当的测试
- [ ] 文档已更新
- [ ] 没有安全问题
- [ ] 性能影响可接受

---

## 资源链接

### 文档

- [Python官方文档](https://docs.python.org/3/)
- [Pandas文档](https://pandas.pydata.org/docs/)
- [Plotly文档](https://plotly.com/python/)
- [Dash文档](https://dash.plotly.com/)

### 工具

- [Black](https://github.com/psf/black) - Python代码格式化
- [Pytest](https://docs.pytest.org/) - 测试框架
- [Poetry](https://python-poetry.org/) - 依赖管理
- [Pre-commit](https://pre-commit.com/) - Git hooks

### 学习资源

- [生物信息学算法](https://www.bioinformatics.org/)
- [机器学习教程](https://scikit-learn.org/stable/tutorial/)
- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)

---

<div align="center">

[返回主页](../README.md) | [部署指南](DEPLOYMENT.md) | [快速开始](QUICKSTART.md)

</div>