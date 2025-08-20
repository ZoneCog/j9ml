# AutoQA Reliability Testing Guide

🚀 Comprehensive guide for running reliability tests with AutoQA to verify test case stability and reliability.

## Overview

Reliability testing is designed to verify that your test cases are stable and reliable by running them multiple times. This helps identify flaky tests and ensures consistent behavior before deploying to production.

## Two Testing Phases

### 1. Development Phase
- **Purpose**: Verify basic stability during development
- **Runs**: 5 times
- **Success Rate Requirement**: ≥80%
- **Use Case**: During development to catch obvious stability issues

### 2. Deployment Phase
- **Purpose**: Verify production readiness
- **Runs**: 20 times
- **Success Rate Requirement**: ≥90%
- **Use Case**: Before deploying to production to ensure reliability

## Command Line Usage

### Basic Reliability Testing

```bash
# Development phase (5 runs)
python main.py --enable-reliability-test --reliability-phase development

# Deployment phase (20 runs)
python main.py --enable-reliability-test --reliability-phase deployment
```

### Custom Configuration

```bash
# Custom number of runs
python main.py --enable-reliability-test --reliability-runs 10

# Specific test file
python main.py --enable-reliability-test --reliability-test-path "tests/base/default-jan-assistant.txt"

# Custom max turns
python main.py --enable-reliability-test --reliability-phase development --max-turns 50
```

### With ReportPortal Integration

```bash
# Development phase with ReportPortal
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_reliability_tests"

# Deployment phase with ReportPortal
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_reliability_tests"
```

## Environment Variables

```bash
# Enable reliability testing
export ENABLE_RELIABILITY_TEST=true

# Set phase
export RELIABILITY_PHASE=deployment

# Custom runs (overrides phase)
export RELIABILITY_RUNS=15

# Specific test path
export RELIABILITY_TEST_PATH="tests/base/my-test.txt"

# Run with environment variables
python main.py --enable-reliability-test
```

## Command Line Arguments

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--enable-reliability-test` | `ENABLE_RELIABILITY_TEST` | `false` | Enable reliability testing mode |
| `--reliability-phase` | `RELIABILITY_PHASE` | `development` | Testing phase: development or deployment |
| `--reliability-runs` | `RELIABILITY_RUNS` | `0` | Custom number of runs (overrides phase) |
| `--reliability-test-path` | `RELIABILITY_TEST_PATH` | - | Specific test file path |

## Test Execution Flow

### Single Test Reliability Testing

1. **Load Test File**: Read the specified test file
2. **Run Multiple Times**: Execute the test the specified number of times
3. **Track Results**: Monitor success/failure for each run
4. **Calculate Success Rate**: Determine overall reliability
5. **Generate Report**: Provide detailed results and statistics

### Multiple Tests Reliability Testing

1. **Scan Test Files**: Find all test files in the specified directory
2. **Run Reliability Tests**: Execute reliability testing on each test file
3. **Aggregate Results**: Combine results from all tests
4. **Overall Assessment**: Determine if the entire test suite is reliable

## Output and Results

### Success Rate Calculation

```
Success Rate = (Successful Runs / Total Runs) × 100
```

### Development Phase Requirements
- **Target**: 5 runs
- **Minimum Success Rate**: 80%
- **Result**: PASS if ≥80%, FAIL if <80%

### Deployment Phase Requirements
- **Target**: 20 runs
- **Minimum Success Rate**: 90%
- **Result**: PASS if ≥90%, FAIL if <90%

### Sample Output

```
==========================================
RELIABILITY TEST SUMMARY
==========================================
Test: tests/base/default-jan-assistant.txt
Phase: DEVELOPMENT
Completed runs: 5/5
Successful runs: 4
Failed runs: 1
Success rate: 80.0%
Total duration: 125.3 seconds
Average duration per run: 25.1 seconds
Overall result: ✅ PASSED
Development phase requirement: ≥80% success rate
```

## Use Cases

### 1. New Test Development
```bash
# Test a new test case for basic stability
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --reliability-test-path "tests/base/my-new-test.txt"
```

### 2. Pre-Production Validation
```bash
# Verify test suite is production-ready
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --tests-dir "tests/base"
```

### 3. Flaky Test Investigation
```bash
# Run a potentially flaky test multiple times
python main.py \
  --enable-reliability-test \
  --reliability-runs 25 \
  --reliability-test-path "tests/base/flaky-test.txt"
```

### 4. CI/CD Integration
```bash
# Automated reliability testing in CI/CD
ENABLE_RELIABILITY_TEST=true \
RELIABILITY_PHASE=deployment \
python main.py --max-turns 40
```

## Best Practices

### 1. Start with Development Phase
- Begin with 5 runs to catch obvious issues
- Use during active development
- Quick feedback on test stability

### 2. Use Deployment Phase for Production
- Run 20 times before production deployment
- Ensures high reliability standards
- Catches intermittent failures

### 3. Custom Runs for Specific Needs
- Use custom run counts for special testing scenarios
- Investigate flaky tests with higher run counts
- Balance between thoroughness and execution time

### 4. Monitor Execution Time
- Reliability testing takes longer than single runs
- Plan accordingly for CI/CD pipelines
- Consider parallel execution for multiple test files

## Troubleshooting

### Common Issues

#### 1. Test File Not Found
```bash
# Ensure test path is correct
python main.py \
  --enable-reliability-test \
  --reliability-test-path "tests/base/existing-test.txt"
```

#### 2. Low Success Rate
- Check test environment stability
- Verify test dependencies
- Review test logic for race conditions

#### 3. Long Execution Time
- Reduce max turns if appropriate
- Use development phase for quick feedback
- Consider running fewer test files

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export PYTHONPATH=.

# Run with verbose output
python main.py --enable-reliability-test --reliability-phase development
```

## Integration with Existing Workflows

### Migration Testing
```bash
# Run reliability tests on migration test cases
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --tests-dir "tests/migration"
```

### Base Testing
```bash
# Run reliability tests on base test cases
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --tests-dir "tests/base"
```

### Custom Test Directories
```bash
# Run reliability tests on custom test directory
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --tests-dir "my_custom_tests"
```

## Performance Considerations

### Execution Time
- **Development Phase**: ~5x single test execution time
- **Deployment Phase**: ~20x single test execution time
- **Multiple Tests**: Multiply by number of test files

### Resource Usage
- Screen recordings for each run
- Trajectory data for each run
- ReportPortal uploads (if enabled)

### Optimization Tips
- Use development phase for quick feedback
- Run deployment phase during off-peak hours
- Consider parallel execution for multiple test files
- Clean up old recordings and trajectories regularly

## Next Steps

1. **Start Simple**: Begin with development phase on single test files
2. **Scale Up**: Move to deployment phase for critical tests
3. **Automate**: Integrate into CI/CD pipelines
4. **Monitor**: Track reliability trends over time
5. **Improve**: Use results to identify and fix flaky tests

For more information, see the main [README.md](README.md), [QUICK_START.md](QUICK_START.md), and explore the test files in the `tests/` directory.
