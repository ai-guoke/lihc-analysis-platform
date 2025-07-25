# LIHC平台测试套件

本目录包含LIHC多维度预后分析平台的核心功能测试。

## 核心测试模块

### 1. test_multi_omics_integration.py
多组学数据整合测试：
- 🧬 RNA-seq、CNV、突变、甲基化数据加载
- 🔗 多种整合方法（连接、SNF、MOFA）
- 📊 特征重要性计算
- 💾 数据保存和加载
- ⚠️ 错误处理机制

### 2. test_closedloop_analyzer.py  
ClosedLoop因果推理分析测试：
- 🔍 多源证据收集
- 📈 因果评分计算
- 🕸️ 证据网络构建
- 🛤️ 通路分析
- ✅ 验证指标
- 🔄 完整分析流程

### 3. test_integrated_analysis.py
集成分析流程测试：
- 🚀 流程初始化
- 🧬 多组学数据整合
- 🔄 ClosedLoop分析集成
- 📋 结果合并
- 📄 报告生成

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件  
python -m pytest tests/test_multi_omics_integration.py

# 运行特定测试
python -m pytest tests/test_multi_omics_integration.py::TestMultiOmicsIntegration::test_data_loading

# 带覆盖率运行
python -m pytest tests/ --cov=src --cov-report=html

# 快速运行（无覆盖率）
python -m pytest tests/ --no-cov
```

## 测试状态

- ✅ **多组学整合测试**: 核心功能完整测试
- ✅ **ClosedLoop分析测试**: 因果推理算法测试
- ✅ **集成分析测试**: 端到端流程测试
- 📊 **测试覆盖率**: >75%

## 质量保证

### 测试原则
- **功能完整性**: 确保所有核心算法正确运行
- **数据安全性**: 验证数据处理的完整性和安全性  
- **性能稳定性**: 测试大数据集处理能力
- **错误处理**: 验证异常情况的处理机制

### 持续集成
- 自动化测试执行
- 代码质量检查
- 覆盖率监控
- 性能基准测试