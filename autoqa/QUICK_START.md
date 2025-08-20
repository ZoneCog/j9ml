# AutoQA Quick Start Guide

🚀 Get started with AutoQA in minutes - from basic testing to migration verification.

## Quick Start

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Basic Testing (No Migration)

```bash
# Run all base tests
python main.py

# Run specific test category
python main.py --tests-dir "tests/base"

# Custom configuration
python main.py \
  --max-turns 50
```

### 3. Migration Testing

```bash
# Basic migration test
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "C:\path\to\old\installer.exe" \
  --new-version "C:\path\to\new\installer.exe" \
  --max-turns 65

# Batch mode migration test
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "C:\path\to\old\installer.exe" \
  --new-version "C:\path\to\new\installer.exe" \
  --max-turns 75
```

### 4. Reliability Testing

```bash
# Development phase (5 runs)
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --max-turns 40

# Deployment phase (20 runs)
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --max-turns 40

# Custom number of runs
python main.py \
  --enable-reliability-test \
  --reliability-runs 10 \
  --max-turns 40
```

## Test Types

### Base Test Cases
- **Default Assistant**: Verify Jan default assistant exists
- **Extensions**: Check available extensions
- **Hardware Info**: Verify hardware information display
- **Model Providers**: Check model provider availability
- **User Chat**: Test basic chat functionality
- **MCP Server**: Test experimental features

### Migration Test Cases
- **`models`**: Test downloaded models persist after upgrade
- **`assistants`**: Test custom assistants persist after upgrade
- **`assistants-complete`**: Test both creation and chat functionality

### Reliability Testing
- **Development Phase**: Run test 5 times to verify basic stability (≥80% success rate)
- **Deployment Phase**: Run test 20 times to verify production readiness (≥90% success rate)
- **Custom Runs**: Specify custom number of runs for specific testing needs

## Common Commands

### Basic Workflow
```bash
# Run all tests
python main.py

# Run with ReportPortal
python main.py --enable-reportportal --rp-token "YOUR_TOKEN"

# Custom test directory
python main.py --tests-dir "my_tests"

# Skip computer server auto-start
python main.py --skip-server-start
```

### Migration Workflow
```bash
# Test assistants migration
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe"

# Test models migration
python main.py \
  --enable-migration-test \
  --migration-test-case "models" \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe"

# Test complete assistants migration (batch mode)
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants-complete" \
  --migration-batch-mode \
  --old-version "path/to/old.exe" \
  --new-version "path/to/new.exe"

# Test reliability - development phase
python main.py \
  --enable-reliability-test \
  --reliability-phase development \
  --max-turns 40

# Test reliability - deployment phase
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --max-turns 40

## Configuration Options

### Essential Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--max-turns` | Maximum turns per test | 30 |
| `--tests-dir` | Test files directory | `tests` |
| `--jan-app-path` | Jan executable path | auto-detected |
| `--model-name` | AI model name | UI-TARS-1.5-7B |

### Migration Arguments
| Argument | Description | Required |
|----------|-------------|----------|
| `--enable-migration-test` | Enable migration mode | Yes |
| `--migration-test-case` | Test case to run | Yes |
| `--migration-batch-mode` | Use batch mode | No |
| `--old-version` | Old installer path | Yes |
| `--new-version` | New installer path | Yes |

### ReportPortal Arguments
| Argument | Description | Required |
|----------|-------------|----------|
| `--enable-reportportal` | Enable RP integration | No |
| `--rp-token` | ReportPortal token | Yes (if RP enabled) |
| `--rp-endpoint` | RP endpoint URL | No |
| `--rp-project` | RP project name | No |

### Reliability Testing Arguments
| Argument | Description | Required |
|----------|-------------|----------|
| `--enable-reliability-test` | Enable reliability mode | Yes |
| `--reliability-phase` | Testing phase (development/deployment) | No |
| `--reliability-runs` | Custom number of runs | No |
| `--reliability-test-path` | Specific test file path | No |

## Environment Variables

```bash
# Set common variables
export MAX_TURNS=65
export MODEL_NAME="gpt-4"
export MODEL_BASE_URL="https://api.openai.com/v1"
export JAN_APP_PATH="C:\path\to\Jan.exe"

# Use in commands
python main.py --max-turns "$MAX_TURNS"
```

## Examples

### Example 1: Basic Testing
```bash
# Test core functionality
python main.py \
  --max-turns 40 \
  --tests-dir "tests/base"
```

### Example 2: Simple Migration
```bash
# Test assistants persistence
python main.py \
  --enable-migration-test \
  --migration-test-case "assistants" \
  --old-version "Jan_0.6.6.exe" \
  --new-version "Jan_0.6.7.exe" \
  --max-turns 65
```

### Example 3: Advanced Migration
```bash
# Test complete functionality with ReportPortal
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
```

### Example 4: Reliability Testing
```bash
# Test reliability with deployment phase
python main.py \
  --enable-reliability-test \
  --reliability-phase deployment \
  --reliability-test-path "tests/base/default-jan-assistant.txt" \
  --max-turns 50 \
  --enable-reportportal \
  --rp-token "YOUR_TOKEN" \
  --rp-project "jan_reliability_tests"
```

## Troubleshooting

### Common Issues
1. **Path Issues**: Use absolute paths with proper escaping
2. **Turn Limits**: Increase `--max-turns` for complex tests
3. **Permissions**: Run as administrator on Windows
4. **Dependencies**: Ensure all packages are installed

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
export PYTHONPATH=.

# Run with debug output
python main.py --enable-migration-test ...
```

## Output Files

- **Trajectories**: `trajectories/` - Agent interaction logs
- **Recordings**: `recordings/` - Screen recordings (MP4)
- **Console**: Detailed execution logs

## Next Steps

1. **Start Simple**: Run basic tests first
2. **Add Migration**: Test data persistence
3. **Customize**: Adjust parameters for your needs
4. **Integrate**: Add to CI/CD pipelines

For detailed documentation, see [MIGRATION_TESTING.md](MIGRATION_TESTING.md) and [README.md](README.md).
