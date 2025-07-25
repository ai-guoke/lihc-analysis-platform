# Integration Tests for LIHC Platform

This directory contains integration tests for the new multi-omics data integration and ClosedLoop causal inference features.

## Test Files

### 1. test_multi_omics_integration.py
Tests for the MultiOmicsIntegrator class including:
- Data loading for different omics types (RNA-seq, CNV, mutations, methylation)
- Integration methods (concatenate, SNF, MOFA)
- Feature importance calculation
- Data saving and loading
- Error handling

### 2. test_closedloop_analyzer.py
Tests for the ClosedLoopAnalyzer class including:
- Evidence collection from multiple sources
- Causal score calculation
- Evidence network construction
- Pathway analysis
- Validation metrics
- Full analysis pipeline

### 3. test_integrated_analysis.py
Tests for the IntegratedAnalysisPipeline class including:
- Pipeline initialization
- Multi-omics data integration
- ClosedLoop analysis integration
- Results combination
- Report generation

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_multi_omics_integration.py

# Run specific test
python -m pytest tests/test_multi_omics_integration.py::TestMultiOmicsIntegration::test_data_loading

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run without coverage (faster)
python -m pytest tests/ --no-cov
```

## Test Status

- ✅ Multi-omics integration tests: 6/8 tests passing
- ✅ ClosedLoop analyzer tests: Core functionality tested
- ✅ Integrated analysis tests: Basic structure in place

## Known Issues

1. SNF integration test needs adjustment for sample size mismatches
2. Import paths need to be standardized across modules
3. Some tests require mock data generation

## Future Improvements

1. Add performance tests for large datasets
2. Add integration tests with real biological data
3. Add tests for visualization components
4. Add tests for API endpoints