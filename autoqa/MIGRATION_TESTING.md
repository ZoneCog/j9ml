# AutoQA Migration Testing Guide

🚀 Comprehensive guide for running migration tests with AutoQA to verify data persistence across Jan application upgrades.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Basic Workflow (Base Test Cases)](#basic-workflow-base-test-cases)
4. [Migration Testing](#migration-testing)
5. [Migration Test Cases](#migration-test-cases)
6. [Running Migration Tests](#running-migration-tests)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

## Overview

AutoQA provides comprehensive testing capabilities for the Jan application, including:

- **Base Test Cases**: Standard functionality testing (assistants, models, extensions, etc.)
- **Migration Testing**: Verify data persistence and functionality across application upgrades
- **Batch Mode**: Run multiple test phases efficiently
- **Screen Recording**: Capture test execution for debugging
- **ReportPortal Integration**: Upload test results and artifacts

## Prerequisites

Before running migration tests, ensure you have:

1. **Python Environment**: Python 3.8+ with required packages
2. **Jan Installers**: Both old and new version installers
3. **Test Environment**: Clean system or virtual machine
4. **Dependencies**: All AutoQA requirements installed

```bash
# Install dependencies
pip install -r requirements.txt

```

## Basic Workflow (Base Test Cases)

### Running Standard Tests

Base test cases verify core Jan functionality without version upgrades:

```bash
# Run all base tests
python main.py

# Run specific test directory
python main.py --tests-dir "tests/base"

# Run with custom configuration
python main.py \
  --max-turns 50 
```

### Available Base Test Cases

| Test Case | File | Description |
|-----------|------|-------------|
| Default Assistant | `tests/base/default-jan-assistant.txt` | Verify Jan default assistant exists |
| Extensions | `tests/base/extensions.txt` | Check available extensions |
| Hardware Info | `tests/base/hardware-info.txt` | Verify hardware information display |
| Model Providers | `tests/base/providers-available.txt` | Check model provider availability |
| User Chat | `tests/base/user-start-chatting.txt` | Test basic chat functionality |
| MCP Server | `tests/base/enable-mcp-server.txt` | Test experimental features |

## Migration Testing

Migration testing verifies that user data and configurations persist correctly when upgrading Jan from one version to another.

### Migration Test Flow

```
1. Install OLD version → Run SETUP tests
2. Install NEW version → Run VERIFICATION tests
3. Compare results and verify persistence
```

### Migration Test Approaches

#### Individual Mode
- Runs one test case at a time
- More granular debugging
- Better for development and troubleshooting

#### Batch Mode
- Runs all setup tests first, then upgrades, then all verification tests
- More realistic user experience
- Faster execution for multiple test cases

## Migration Test Cases

### Available Migration Test Cases

| Test Case Key | Name | Description | Setup Tests | Verification Tests |
|---------------|------|-------------|-------------|-------------------|
| `models` | Model Downloads Migration | Tests downloaded models persist after upgrade | `models/setup-download-models.txt` | `models/verify-model-persistence.txt` |
| `assistants` | Custom Assistants Migration | Tests custom assistants persist after upgrade | `assistants/setup-create-assistants.txt` | `assistants/verify-create-assistant-persistence.txt` |
| `assistants-complete` | Complete Assistants Migration | Tests both creation and chat functionality | Multiple setup tests | Multiple verification tests |

### Test Case Details

#### Models Migration Test
- **Setup**: Downloads models, configures settings, tests functionality
- **Verification**: Confirms models persist, settings maintained, functionality intact

#### Assistants Migration Test
- **Setup**: Creates custom assistants with specific configurations
- **Verification**: Confirms assistants persist with correct metadata and settings

#### Assistants Complete Migration Test
- **Setup**: Creates assistants AND tests chat functionality
- **Verification**: Confirms both creation and chat data persist correctly

## Running Migration Tests

### Basic Migration Test Command

```bash
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old/installer.exe" \
  --new-version "path/to/new/installer.exe" \
  --max-turns 65
```

### Batch Mode Migration Test

```bash
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "path/to/old/installer.exe" \
  --new-version "path/to/new/installer.exe" \
  --max-turns 75
```

### Command Line Arguments

| Argument | Description | Required | Example |
|----------|-------------|----------|---------|
| `--enable-migration-test` | Enable migration testing mode | Yes | `--enable-migration-test` |
| `--migration-test-case` | Specific test case to run | Yes | `--migration-test-case "assistants"` |
| `--migration-batch-mode` | Use batch mode for multiple tests | No | `--migration-batch-mode` |
| `--old-version` | Path to old version installer | Yes | `--old-version "C:\path\to\old.exe"` |
| `--new-version` | Path to new version installer | Yes | `--new-version "C:\path\to\new.exe"` |
| `--max-turns` | Maximum turns per test phase | No | `--max-turns 75` |

### Environment Variables

You can also use environment variables for cleaner commands:

```bash
# Set environment variables
export OLD_VERSION="C:\path\to\old\installer.exe"
export NEW_VERSION="C:\path\to\new\installer.exe"
export MIGRATION_TEST_CASE="assistants"
export MAX_TURNS=65

# Run with environment variables
python main.py \
  --enable-migration-test \
  --migration-test-case "$MIGRATION_TEST_CASE" \
  --old-version "$OLD_VERSION" \
  --new-version "$NEW_VERSION" \
  --max-turns "$MAX_TURNS"
```

## Advanced Configuration

### Custom Model Configuration

```bash
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe" \
  --model-name "gpt-4" \
  --model-provider "openai" \
  --model-base-url "https://api.openai.com/v1" \
  --max-turns 80
```

### ReportPortal Integration

```bash
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe" \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_migration_tests" \
  --max-turns 65
```

### Custom Test Directory

```bash
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe" \
  --tests-dir "custom_tests" \
  --max-turns 65
```

## Examples

### Example 1: Basic Assistants Migration Test

```bash
# Test custom assistants persistence
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "C:\Users\ziczac computer\Downloads\Jan_0.6.6_x64-setup.exe" \
  --new-version "C:\Users\ziczac computer\Downloads\Jan_0.6.7_x64-setup.exe" \
  --max-turns 65
```

**What this does:**
1. Installs Jan 0.6.6
2. Creates custom assistants (Python Tutor, Creative Writer)
3. Upgrades to Jan 0.6.7
4. Verifies assistants persist with correct settings

### Example 2: Complete Assistants Migration (Batch Mode)

```bash
# Test both creation and chat functionality
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "C:\Users\ziczac computer\Downloads\Jan_0.6.6_x64-setup.exe" \
  --new-version "C:\Users\ziczac computer\Downloads\Jan_0.6.7_x64-setup.exe" \
  --max-turns 75
```

**What this does:**
1. Installs Jan 0.6.6
2. Creates custom assistants
3. Tests chat functionality with assistants
4. Upgrades to Jan 0.6.7
5. Verifies both creation and chat data persist

### Example 3: Models Migration Test

```bash
# Test model downloads and settings persistence
python main.py \
  --enable-migration-test \
  --migration-test-case "models" \
  --old-version "C:\Users\ziczac computer\Downloads\Jan_0.6.6_x64-setup.exe" \
  --new-version "C:\Users\ziczac computer\Downloads\Jan_0.6.7_x64-setup.exe" \
  --max-turns 60
```

**What this does:**
1. Installs Jan 0.6.6
2. Downloads models (jan-nano-gguf, gemma-2-2b-instruct-gguf)
3. Configures model settings
4. Upgrades to Jan 0.6.7
5. Verifies models persist and settings maintained

## Troubleshooting

### Common Issues

#### 1. Installer Path Issues
```bash
# Use absolute paths with proper escaping
--old-version "C:\Users\ziczac computer\Downloads\Jan_0.6.6_x64-setup.exe"
--new-version "C:\Users\ziczac computer\Downloads\Jan_0.6.7_x64-setup.exe"
```

#### 2. Turn Limit Too Low
```bash
# Increase max turns for complex tests
--max-turns 75  # Instead of default 30
```

#### 3. Test Case Not Found
```bash
# Verify test case key exists
--migration-test-case "assistants"  # Valid: models, assistants, assistants-complete
```

#### 4. Permission Issues
```bash
# Run as administrator on Windows
# Use sudo on Linux/macOS for system-wide installations
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set logging level
export PYTHONPATH=.
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe" \
  --max-turns 65
```

### Test Results

Migration tests generate detailed results:

- **Setup Phase Results**: Success/failure for each setup test
- **Upgrade Results**: Installation success status
- **Verification Phase Results**: Success/failure for each verification test
- **Overall Success**: Combined result from all phases

### Output Files

Tests generate several output files:

- **Trajectories**: `trajectories/` - Agent interaction logs
- **Recordings**: `recordings/` - Screen recordings (MP4)
- **Logs**: Console output with detailed execution information

## Best Practices

### 1. Test Environment
- Use clean virtual machines or fresh system installations
- Ensure sufficient disk space for installers and test data
- Close other applications during testing

### 2. Test Data
- Use realistic test data (assistant names, descriptions, instructions)
- Test with multiple models and configurations
- Verify edge cases and error conditions

### 3. Execution
- Start with individual mode for debugging
- Use batch mode for production testing
- Monitor system resources during execution

### 4. Validation
- Verify test results manually when possible
- Check generated artifacts (trajectories, recordings)
- Compare expected vs. actual behavior

## Next Steps

1. **Start Simple**: Begin with basic migration tests
2. **Add Complexity**: Gradually test more complex scenarios
3. **Automate**: Integrate into CI/CD pipelines
4. **Extend**: Add new test cases for specific features
5. **Optimize**: Refine test parameters and configurations

For more information, see the main [README.md](README.md) and explore the test files in the `tests/` directory.
