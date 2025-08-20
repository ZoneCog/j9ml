# AutoQA Command Reference

📚 Complete reference for all AutoQA command line arguments and options.

## Command Line Arguments

### Basic Syntax

```bash
python main.py [OPTIONS]
```

### Argument Groups

Arguments are organized into logical groups for easier understanding and usage.

## Computer Server Configuration

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--skip-server-start` | `SKIP_SERVER_START` | `false` | Skip automatic computer server startup |

**Examples:**
```bash
# Auto-start computer server (default)
python main.py

# Use external computer server
python main.py --skip-server-start

# Using environment variable
SKIP_SERVER_START=true python main.py
```

## ReportPortal Configuration

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--enable-reportportal` | `ENABLE_REPORTPORTAL` | `false` | Enable ReportPortal integration |
| `--rp-endpoint` | `RP_ENDPOINT` | `https://reportportal.menlo.ai` | ReportPortal endpoint URL |
| `--rp-project` | `RP_PROJECT` | `default_personal` | ReportPortal project name |
| `--rp-token` | `RP_TOKEN` | - | ReportPortal API token (required when RP enabled) |
| `--launch-name` | `LAUNCH_NAME` | - | Custom launch name for ReportPortal |

**Examples:**
```bash
# Basic ReportPortal integration
python main.py --enable-reportportal --rp-token "YOUR_TOKEN"

# Full ReportPortal configuration
python main.py \
  --enable-reportportal \
  --rp-endpoint "https://reportportal.example.com" \
  --rp-project "my_project" \
  --rp-token "YOUR_TOKEN" \
  --launch-name "Custom Test Run"

# Using environment variables
ENABLE_REPORTPORTAL=true RP_TOKEN=secret python main.py
```

## Jan Application Configuration

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--jan-app-path` | `JAN_APP_PATH` | auto-detected | Path to Jan application executable |
| `--jan-process-name` | `JAN_PROCESS_NAME` | platform-specific | Jan process name for monitoring |

**Platform-specific defaults:**
- **Windows**: `Jan.exe`
- **macOS**: `Jan`
- **Linux**: `Jan-nightly`

**Examples:**
```bash
# Custom Jan app path
python main.py --jan-app-path "C:/Custom/Path/Jan.exe"

# Custom process name
python main.py --jan-process-name "Jan-nightly.exe"

# Using environment variable
JAN_APP_PATH="D:/Apps/Jan/Jan.exe" python main.py
```

## Model Configuration

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--model-loop` | `MODEL_LOOP` | `uitars` | Agent loop type |
| `--model-provider` | `MODEL_PROVIDER` | `oaicompat` | Model provider |
| `--model-name` | `MODEL_NAME` | `ByteDance-Seed/UI-TARS-1.5-7B` | AI model name |
| `--model-base-url` | `MODEL_BASE_URL` | `http://10.200.108.58:1234/v1` | Model API endpoint |

**Examples:**
```bash
# OpenAI GPT-4
python main.py \
  --model-provider "openai" \
  --model-name "gpt-4" \
  --model-base-url "https://api.openai.com/v1"

# Anthropic Claude
python main.py \
  --model-provider "anthropic" \
  --model-name "claude-3-sonnet-20240229" \
  --model-base-url "https://api.anthropic.com"

# Custom local model
python main.py \
  --model-name "my-custom-model" \
  --model-base-url "http://localhost:8000/v1"

# Using environment variables
MODEL_NAME=gpt-4 MODEL_BASE_URL=https://api.openai.com/v1 python main.py
```

## Test Execution Configuration

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--max-turns` | `MAX_TURNS` | `30` | Maximum number of turns per test |
| `--tests-dir` | `TESTS_DIR` | `tests` | Directory containing test files |
| `--delay-between-tests` | `DELAY_BETWEEN_TESTS` | `3` | Delay between tests (seconds) |

**Examples:**
```bash
# Increase turn limit
python main.py --max-turns 50

# Custom test directory
python main.py --tests-dir "my_tests"

# Longer delay between tests
python main.py --delay-between-tests 10

# Using environment variables
MAX_TURNS=50 DELAY_BETWEEN_TESTS=5 python main.py
```

## Migration Testing Arguments

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--enable-migration-test` | `ENABLE_MIGRATION_TEST` | `false` | Enable migration testing mode |
| `--migration-test-case` | `MIGRATION_TEST_CASE` | - | Specific migration test case to run |
| `--migration-batch-mode` | `MIGRATION_BATCH_MODE` | `false` | Use batch mode for migration tests |
| `--old-version` | `OLD_VERSION` | - | Path to old version installer |
| `--new-version` | `NEW_VERSION` | - | Path to new version installer |

## Reliability Testing Arguments

| Argument | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `--enable-reliability-test` | `ENABLE_RELIABILITY_TEST` | `false` | Enable reliability testing mode |
| `--reliability-phase` | `RELIABILITY_PHASE` | `development` | Testing phase: development (5 runs) or deployment (20 runs) |
| `--reliability-runs` | `RELIABILITY_RUNS` | `0` | Custom number of runs (overrides phase setting) |
| `--reliability-test-path` | `RELIABILITY_TEST_PATH` | - | Specific test file path for reliability testing |

**Examples:**
```bash
# Basic migration test
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "C:\path\to\old\installer.exe" \
  --new-version "C:\path\to\new\installer.exe"

# Batch mode migration test
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "C:\path\to\old\installer.exe" \
  --new-version "C:\path\to\new\installer.exe"

# Using environment variables
ENABLE_MIGRATION_TEST=true \
MIGRATION_TEST_CASE=assistants \
OLD_VERSION="C:\path\to\old.exe" \
NEW_VERSION="C:\path\to\new.exe" \
python main.py
```

## Complete Command Examples

### Basic Testing

```bash
# Run all tests with defaults
python main.py

# Run specific test category
python main.py --tests-dir "tests/base"

# Custom configuration
python main.py \
  --max-turns 50 \
  --model-name "gpt-4" \
  --model-base-url "https://api.openai.com/v1" \
  --tests-dir "tests/base"
```

### Migration Testing

```bash
# Simple migration test
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "Jan_0.6.6.exe" \
  --new-version "Jan_0.6.7.exe" \
  --max-turns 65

# Complete migration test with ReportPortal
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "Jan_0.6.6.exe" \
  --new-version "Jan_0.6.7.exe" \
  --max-turns 75 \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_migration_tests"

# Reliability testing - deployment phase with ReportPortal
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --reliability-test-path "tests/base/default-jan-assistant.txt" \
  --max-turns 50 \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_reliability_tests"

### Reliability Testing

```bash
# Development phase reliability test (5 runs)
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --max-turns 40

# Deployment phase reliability test (20 runs)
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --max-turns 40

# Custom number of runs
python main.py \
  --enable-reliability-test \
  --reliability-runs 10 \
  --max-turns 40

# Test specific file with reliability testing
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --reliability-test-path "tests/base/default-jan-assistant.txt" \
  --max-turns 40

# Reliability testing with ReportPortal
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --max-turns 40
```

### Advanced Configuration

```bash
# Full custom configuration
python main.py \
  --skip-server-start \
  --enable-reportportal \
  --rp-endpoint "https://custom.rp.com" \
  --rp-project "jan_tests" \
  --rp-token "YOUR_TOKEN" \
  --jan-app-path "C:/Custom/Jan/Jan.exe" \
  --jan-process-name "Jan-custom.exe" \
  --model-provider "openai" \
  --model-name "gpt-4-turbo" \
  --model-base-url "https://api.openai.com/v1" \
  --max-turns 100 \
  --tests-dir "custom_tests" \
  --delay-between-tests 5
```

## Environment Variables Summary

### Computer Server
- `SKIP_SERVER_START`: Skip auto computer server startup

### ReportPortal
- `ENABLE_REPORTPORTAL`: Enable ReportPortal integration
- `RP_ENDPOINT`: ReportPortal endpoint URL
- `RP_PROJECT`: ReportPortal project name
- `RP_TOKEN`: ReportPortal API token
- `LAUNCH_NAME`: Custom launch name

### Jan Application
- `JAN_APP_PATH`: Path to Jan executable
- `JAN_PROCESS_NAME`: Jan process name

### Model Configuration
- `MODEL_LOOP`: Agent loop type
- `MODEL_PROVIDER`: Model provider
- `MODEL_NAME`: AI model name
- `MODEL_BASE_URL`: Model API endpoint

### Test Execution
- `MAX_TURNS`: Maximum turns per test
- `TESTS_DIR`: Test files directory
- `DELAY_BETWEEN_TESTS`: Delay between tests

### Migration Testing
- `ENABLE_MIGRATION_TEST`: Enable migration mode
- `MIGRATION_TEST_CASE`: Migration test case
- `MIGRATION_BATCH_MODE`: Use batch mode
- `OLD_VERSION`: Old installer path
- `NEW_VERSION`: New installer path

### Reliability Testing
- `ENABLE_RELIABILITY_TEST`: Enable reliability testing mode
- `RELIABILITY_PHASE`: Testing phase (development/deployment)
- `RELIABILITY_RUNS`: Custom number of runs
- `RELIABILITY_TEST_PATH`: Specific test file path

## Help and Information

### Get Help
```bash
# Show all available options
python main.py --help

# Show help for specific section
python main.py --help | grep -A 10 "Migration"
```

### Version Information
```bash
# Check Python version
python --version

# Check AutoQA installation
python -c "import autoqa; print(autoqa.__version__)"
```

### Debug Information
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export PYTHONPATH=.

# Run with verbose output
python main.py --enable-migration-test ...
```

## Best Practices

### 1. Use Environment Variables
```bash
# Set common configuration
export MAX_TURNS=65
export MODEL_NAME="gpt-4"
export JAN_APP_PATH="C:\path\to\Jan.exe"

# Use in commands
python main.py --max-turns "$MAX_TURNS"
```

### 2. Combine Arguments Logically
```bash
# Group related arguments
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "old.exe" \
  --new-version "new.exe" \
  --max-turns 65 \
  --enable-reportportal \
  --rp-token "token"
```

### 3. Use Absolute Paths
```bash
# Windows
--old-version "C:\Users\username\Downloads\Jan_0.6.6.exe"

# Linux/macOS
--old-version "/home/user/downloads/Jan_0.6.6.deb"
```

### 4. Test Incrementally
```bash
# Start simple
python main.py

# Add migration
python main.py --enable-migration-test ...

# Add ReportPortal
python main.py --enable-migration-test ... --enable-reportportal ...
```

## Troubleshooting Commands

### Check Dependencies
```bash
# Verify Python packages
pip list | grep -E "(autoqa|computer|agent)"

# Check imports
python -c "import computer, agent, autoqa; print('All imports successful')"
```

### Check Configuration
```bash
# Validate arguments
python main.py --help

# Test specific configuration
python main.py --jan-app-path "nonexistent" 2>&1 | grep "not found"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export PYTHONPATH=.

# Run with debug output
python main.py --enable-migration-test ...
```

For more detailed information, see [MIGRATION_TESTING.md](MIGRATION_TESTING.md), [QUICK_START.md](QUICK_START.md), and [README.md](README.md).
