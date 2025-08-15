import asyncio
import logging
import os
import argparse
import threading
import time
import platform
from datetime import datetime
from computer import Computer
from reportportal_client import RPClient
from reportportal_client.helpers import timestamp

from utils import scan_test_files
from test_runner import run_single_test_with_timeout
from individual_migration_runner import run_individual_migration_test, run_all_migration_tests, MIGRATION_TEST_CASES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

def get_computer_config():
    """Get computer configuration based on platform"""
    if IS_WINDOWS:
        return {
            "os_type": "windows"
        }
    elif IS_LINUX:
        return {
            "os_type": "linux"
        }
    elif IS_MACOS:
        return {
            "os_type": "macos"
        }
    else:
        # Default fallback
        logger.warning(f"Unknown platform {platform.system()}, using Linux config as fallback")
        return {
            "os_type": "linux"
        }

def get_default_jan_path():
    """Get default Jan app path based on OS"""
    if IS_WINDOWS:
        # Try multiple common locations on Windows
        possible_paths = [
            os.path.expanduser(r"~\AppData\Local\Programs\jan\Jan.exe"),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'jan', 'Jan.exe'),
            os.path.join(os.environ.get('APPDATA', ''), 'jan', 'Jan.exe'),
            r"C:\Program Files\jan\Jan.exe",
            r"C:\Program Files (x86)\jan\Jan.exe"
        ]
        
        # Return first existing path, or first option as default
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If none exist, return the most likely default
        return possible_paths[0]
    
    elif IS_LINUX:
        # Linux possible locations
        possible_paths = [
            "/usr/bin/Jan",
            "/usr/local/bin/Jan",
            os.path.expanduser("~/Applications/Jan/Jan"),
            "/opt/Jan/Jan"
        ]
        
        # Return first existing path, or first option as default
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to nightly build path
        return "/usr/bin/Jan"
    
    elif IS_MACOS:
        # macOS defaults
        possible_paths = [
            "/Applications/Jan.app/Contents/MacOS/Jan",
            os.path.expanduser("~/Applications/Jan.app/Contents/MacOS/Jan")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return possible_paths[0]
    
    else:
        # Unknown platform
        return "jan"

def start_computer_server():
    """Start computer server in background thread"""
    try:
        logger.info("Starting computer server in background...")
        
        # Import computer_server module
        import computer_server
        import sys
        
        # Start server in a separate thread
        def run_server():
            try:
                # Save original sys.argv to avoid argument conflicts
                original_argv = sys.argv.copy()
                
                # Override sys.argv for computer_server to use default args
                sys.argv = ['computer_server']  # Reset to minimal args
                
                # Use the proper entry point
                logger.info("Calling computer_server.run_cli()...")
                computer_server.run_cli()
                logger.info("Computer server.run_cli() completed")
            except KeyboardInterrupt:
                logger.info("Computer server interrupted")
            except Exception as e:
                logger.error(f"Computer server error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
            finally:
                # Restore original sys.argv
                try:
                    sys.argv = original_argv
                except:
                    pass
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        logger.info("Computer server thread started")
        
        # Give server more time to start up
        time.sleep(5)
        
        # Check if thread is still alive (server is running)
        if server_thread.is_alive():
            logger.info("Computer server is running successfully")
            return server_thread
        else:
            logger.error("Computer server thread died unexpectedly")
            return None
        
    except ImportError as e:
        logger.error(f"Cannot import computer_server module: {e}")
        logger.error("Please install computer_server package")
        return None
    except Exception as e:
        logger.error(f"Error starting computer server: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="E2E Test Runner with ReportPortal integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run locally without ReportPortal
  python main.py
  
  # Run with ReportPortal integration
  python main.py --enable-reportportal --rp-token YOUR_TOKEN
  
  # Run with custom Jan app path
  python main.py --jan-app-path "C:/Custom/Path/Jan.exe"
  
  # Run with different model
  python main.py --model-name "gpt-4" --model-base-url "https://api.openai.com/v1"
  
  # Using environment variables
  ENABLE_REPORTPORTAL=true RP_TOKEN=xxx MODEL_NAME=gpt-4 python main.py
        """
    )
    
    # Get default Jan path
    default_jan_path = get_default_jan_path()
    
    # Computer server arguments
    server_group = parser.add_argument_group('Computer Server Configuration')
    server_group.add_argument(
        '--skip-server-start',
        action='store_true',
        default=os.getenv('SKIP_SERVER_START', 'false').lower() == 'true',
        help='Skip automatic computer server startup (env: SKIP_SERVER_START, default: false)'
    )
    
    # ReportPortal arguments
    rp_group = parser.add_argument_group('ReportPortal Configuration')
    rp_group.add_argument(
        '--enable-reportportal',
        action='store_true',
        default=os.getenv('ENABLE_REPORTPORTAL', 'false').lower() == 'true',
        help='Enable ReportPortal integration (env: ENABLE_REPORTPORTAL, default: false)'
    )
    rp_group.add_argument(
        '--rp-endpoint',
        default=os.getenv('RP_ENDPOINT', 'https://reportportal.menlo.ai'),
        help='ReportPortal endpoint URL (env: RP_ENDPOINT, default: %(default)s)'
    )
    rp_group.add_argument(
        '--rp-project',
        default=os.getenv('RP_PROJECT', 'default_personal'),
        help='ReportPortal project name (env: RP_PROJECT, default: %(default)s)'
    )
    rp_group.add_argument(
        '--rp-token',
        default=os.getenv('RP_TOKEN'),
        help='ReportPortal API token (env: RP_TOKEN, required when --enable-reportportal is used)'
    )
    rp_group.add_argument(
        '--launch-name',
        default=os.getenv('LAUNCH_NAME'),
        help='Custom launch name for ReportPortal (env: LAUNCH_NAME, default: auto-generated with timestamp)'
    )
    
    # Jan app arguments
    jan_group = parser.add_argument_group('Jan Application Configuration')
    jan_group.add_argument(
        '--jan-app-path',
        default=os.getenv('JAN_APP_PATH', default_jan_path),
        help=f'Path to Jan application executable (env: JAN_APP_PATH, default: auto-detected or {default_jan_path})'
    )
    jan_group.add_argument(
        '--jan-process-name',
        default=os.getenv('JAN_PROCESS_NAME', 'Jan.exe' if IS_WINDOWS else ('Jan' if IS_MACOS else 'Jan-nightly')),
        help='Jan process name for monitoring (env: JAN_PROCESS_NAME, default: platform-specific)'
    )
    
    # Model/Agent arguments
    model_group = parser.add_argument_group('Model Configuration')
    model_group.add_argument(
        '--model-loop',
        default=os.getenv('MODEL_LOOP', 'uitars'),
        help='Agent loop type (env: MODEL_LOOP, default: %(default)s)'
    )
    model_group.add_argument(
        '--model-provider',
        default=os.getenv('MODEL_PROVIDER', 'oaicompat'),
        help='Model provider (env: MODEL_PROVIDER, default: %(default)s)'
    )
    model_group.add_argument(
        '--model-name',
        default=os.getenv('MODEL_NAME', 'ByteDance-Seed/UI-TARS-1.5-7B'),
        help='Model name (env: MODEL_NAME, default: %(default)s)'
    )
    model_group.add_argument(
        '--model-base-url',
        default=os.getenv('MODEL_BASE_URL', 'http://10.200.108.58:1234/v1'),
        help='Model base URL (env: MODEL_BASE_URL, default: %(default)s)'
    )
    
    # Test execution arguments
    test_group = parser.add_argument_group('Test Execution Configuration')
    test_group.add_argument(
        '--max-turns',
        type=int,
        default=int(os.getenv('MAX_TURNS', '30')),
        help='Maximum number of turns per test (env: MAX_TURNS, default: %(default)s)'
    )
    test_group.add_argument(
        '--tests-dir',
        default=os.getenv('TESTS_DIR', 'tests/base'),
        help='Directory containing test files for current version testing (env: TESTS_DIR, default: %(default)s for base tests, tests/migration for migration tests)'
    )
    test_group.add_argument(
        '--delay-between-tests',
        type=int,
        default=int(os.getenv('DELAY_BETWEEN_TESTS', '3')),
        help='Delay in seconds between tests (env: DELAY_BETWEEN_TESTS, default: %(default)s)'
    )
    
    # Migration testing arguments
    migration_group = parser.add_argument_group('Migration Testing Configuration')
    migration_group.add_argument(
        '--enable-migration-test',
        action='store_true',
        default=os.getenv('ENABLE_MIGRATION_TEST', 'false').lower() == 'true',
        help='Enable migration testing mode (env: ENABLE_MIGRATION_TEST, default: false)'
    )
    migration_group.add_argument(
        '--old-version',
        default=os.getenv('OLD_VERSION'),
        help='Path to old version installer for migration testing (env: OLD_VERSION)'
    )
    migration_group.add_argument(
        '--new-version',
        default=os.getenv('NEW_VERSION'),
        help='Path to new version installer for migration testing (env: NEW_VERSION)'
    )
    migration_group.add_argument(
        '--migration-test-case',
        default=os.getenv('MIGRATION_TEST_CASE'),
        help='Specific migration test case(s) to run. Can be a single case or comma-separated list (e.g., "assistants" or "models,threads"). Available cases: appearance, threads, models, assistants, assistant-chat, assistants-complete, mcp-servers, local-api, proxy-settings, thread-conversations. Note: "assistants-complete" is only supported in batch mode. If not specified, runs all test cases. Use --list-migration-tests to see all available cases. (env: MIGRATION_TEST_CASE)'
    )
    migration_group.add_argument(
        '--migration-batch-mode',
        action='store_true',
        default=os.getenv('MIGRATION_BATCH_MODE', 'false').lower() == 'true',
        help='Use batch migration mode: setup all → upgrade → verify all (env: MIGRATION_BATCH_MODE, default: false - uses individual mode)'
    )
    migration_group.add_argument(
        '--list-migration-tests',
        action='store_true',
        help='List available migration test cases and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list migration tests
    if args.list_migration_tests:
        print("Available migration test cases:")
        print("=" * 50)
        for key, test_case in MIGRATION_TEST_CASES.items():
            print(f"  {key}:")
            print(f"    Name: {test_case['name']}")
            print(f"    Description: {test_case['description']}")
            print()
        exit(0)
    
    # Validate ReportPortal token if ReportPortal is enabled
    if args.enable_reportportal and not args.rp_token:
        parser.error("--rp-token (or RP_TOKEN env var) is required when --enable-reportportal is used")
    
    # Validate migration test arguments
    if args.enable_migration_test:
        if not args.old_version:
            parser.error("--old-version (or OLD_VERSION env var) is required when --enable-migration-test is used")
        if not args.new_version:
            parser.error("--new-version (or NEW_VERSION env var) is required when --enable-migration-test is used")
        if not os.path.exists(args.old_version):
            parser.error(f"Old version installer not found: {args.old_version}")
        if not os.path.exists(args.new_version):
            parser.error(f"New version installer not found: {args.new_version}")
        
        # Validate specific test case if provided
        if args.migration_test_case and args.migration_test_case not in MIGRATION_TEST_CASES:
            parser.error(f"Unknown migration test case: {args.migration_test_case}. Use --list-migration-tests to see available test cases.")
    
    return args

async def main():
    """
    Main function to scan and run all test files with optional ReportPortal integration
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize final exit code
    final_exit_code = 0
    
    # Start computer server if not skipped
    server_thread = None
    if not args.skip_server_start:
        server_thread = start_computer_server()
        if server_thread is None:
            logger.error("Failed to start computer server. Exiting...")
            return
    else:
        logger.info("Skipping computer server startup (assuming it's already running)")
    
    try:
        # Build agent config from arguments
        agent_config = {
            "loop": args.model_loop,
            "model_provider": args.model_provider,
            "model_name": args.model_name,
            "model_base_url": args.model_base_url
        }
        
        # Log configuration
        logger.info("=== Configuration ===")
        logger.info(f"Testing Mode: {'MIGRATION (old → new version)' if args.enable_migration_test else 'BASE (current version)'}")
        logger.info(f"Computer server: {'STARTED' if server_thread else 'EXTERNAL'}")
        logger.info(f"Tests directory: {args.tests_dir}")
        logger.info(f"Max turns per test: {args.max_turns}")
        logger.info(f"Delay between tests: {args.delay_between_tests}s")
        logger.info(f"Jan app path: {args.jan_app_path}")
        logger.info(f"Jan app exists: {os.path.exists(args.jan_app_path)}")
        logger.info(f"Jan process name: {args.jan_process_name}")
        logger.info(f"Model: {args.model_name}")
        logger.info(f"Model URL: {args.model_base_url}")
        logger.info(f"Model provider: {args.model_provider}")
        logger.info(f"ReportPortal integration: {'ENABLED' if args.enable_reportportal else 'DISABLED'}")
        if args.enable_reportportal:
            logger.info(f"ReportPortal endpoint: {args.rp_endpoint}")
            logger.info(f"ReportPortal project: {args.rp_project}")
            logger.info(f"ReportPortal token: {'SET' if args.rp_token else 'NOT SET'}")
            logger.info(f"Launch name: {args.launch_name if args.launch_name else 'AUTO-GENERATED'}")
        logger.info(f"Migration testing: {'ENABLED' if args.enable_migration_test else 'DISABLED'}")
        if args.enable_migration_test:
            logger.info(f"Old version installer: {args.old_version}")
            logger.info(f"New version installer: {args.new_version}")
        logger.info("======================")
        
        # Initialize ReportPortal client only if enabled
        rp_client = None
        launch_id = None
        
        if args.enable_reportportal:
            try:
                rp_client = RPClient(
                    endpoint=args.rp_endpoint,
                    project=args.rp_project,
                    api_key=args.rp_token
                )
                
                # Start ReportPortal launch
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Use custom launch name if provided, otherwise generate default
                if args.launch_name:
                    launch_name = args.launch_name
                    logger.info(f"Using custom launch name: {launch_name}")
                else:
                    launch_name = f"E2E Test Run - {current_time}"
                    logger.info(f"Using auto-generated launch name: {launch_name}")
                
                launch_id = rp_client.start_launch(
                    name=launch_name,
                    start_time=timestamp(),
                    description=f"Automated E2E test run with {len(test_files)} test cases\n"
                               f"Model: {args.model_name}\n"
                               f"Max turns: {args.max_turns}"
                )
                
                logger.info(f"Started ReportPortal launch: {launch_name}")
            except Exception as e:
                logger.error(f"Failed to initialize ReportPortal: {e}")
                logger.warning("Continuing without ReportPortal integration...")
                rp_client = None
                launch_id = None
        else:
            logger.info("Running in local development mode - results will not be uploaded to ReportPortal")
        
        # Start computer environment
        logger.info("Initializing computer environment...")
        
        # Get platform-specific computer configuration
        computer_config = get_computer_config()
        logger.info(f"Using computer config: {computer_config}")
        
        computer = Computer(
            os_type=computer_config["os_type"], 
            use_host_computer_server=True
        )
        await computer.run()
        logger.info("Computer environment ready")
        
        # Check if migration testing is enabled
        if args.enable_migration_test:
            logger.info("=" * 60)
            logger.info("MIGRATION TESTING MODE ENABLED")
            logger.info("=" * 60)
            logger.info(f"Old version installer: {args.old_version}")
            logger.info(f"New version installer: {args.new_version}")
            logger.info(f"Migration mode: {'BATCH (all setups → upgrade → all verifies)' if args.migration_batch_mode else 'INDIVIDUAL (setup → upgrade → verify per test)'}")
            
            if args.migration_test_case:
                # Parse comma-separated test cases
                test_cases = [case.strip() for case in args.migration_test_case.split(',')]
                logger.info(f"Running specific test case(s): {', '.join(test_cases)}")
                
                # Validate all test cases exist
                for test_case in test_cases:
                    if test_case not in MIGRATION_TEST_CASES:
                        logger.error(f"Unknown test case: {test_case}")
                        logger.error(f"Available test cases: {', '.join(MIGRATION_TEST_CASES.keys())}")
                        final_exit_code = 1
                        return final_exit_code
                
                if args.migration_batch_mode:
                    # Import and run batch migration with specified test cases
                    from batch_migration_runner import run_batch_migration_test
                    
                    migration_results = await run_batch_migration_test(
                        computer=computer,
                        old_version_path=args.old_version,
                        new_version_path=args.new_version,
                        rp_client=rp_client,
                        launch_id=launch_id,
                        max_turns=args.max_turns,
                        agent_config=agent_config,
                        enable_reportportal=args.enable_reportportal,
                        test_cases=test_cases  # Multiple test cases in batch mode
                    )
                    
                    # Handle batch test result  
                    if migration_results and migration_results.get("overall_success", False):
                        logger.info(f"[SUCCESS] Batch migration test '{', '.join(test_cases)}' completed successfully!")
                        final_exit_code = 0
                    else:
                        logger.error(f"[FAILED] Batch migration test '{', '.join(test_cases)}' failed!")
                        if migration_results and migration_results.get("error_message"):
                            logger.error(f"Error: {migration_results['error_message']}")
                        final_exit_code = 1
                else:
                    # Run individual migration tests for each specified test case
                    all_individual_results = []
                    overall_individual_success = True
                    
                    for test_case in test_cases:
                        logger.info(f"Running individual migration test for: {test_case}")
                        migration_result = await run_individual_migration_test(
                            computer=computer,
                            test_case_key=test_case,
                            old_version_path=args.old_version,
                            new_version_path=args.new_version,
                            rp_client=rp_client,
                            launch_id=launch_id,
                            max_turns=args.max_turns,
                            agent_config=agent_config,
                            enable_reportportal=args.enable_reportportal
                        )
                        
                        all_individual_results.append(migration_result)
                        if not (migration_result and migration_result.get("overall_success", False)):
                            overall_individual_success = False
                    
                    # Handle individual test results
                    if overall_individual_success:
                        logger.info(f"[SUCCESS] All individual migration tests '{', '.join(test_cases)}' completed successfully!")
                        final_exit_code = 0
                    else:
                        logger.error(f"[FAILED] One or more individual migration tests '{', '.join(test_cases)}' failed!")
                        for i, result in enumerate(all_individual_results):
                            if result and result.get("error_message"):
                                logger.error(f"Error in {test_cases[i]}: {result['error_message']}")
                        final_exit_code = 1
            else:
                logger.info("Running all migration test cases")
                
                if args.migration_batch_mode:
                    # Import and run batch migration runner
                    from batch_migration_runner import run_batch_migration_test
                    
                    migration_results = await run_batch_migration_test(
                        computer=computer,
                        old_version_path=args.old_version,
                        new_version_path=args.new_version,
                        rp_client=rp_client,
                        launch_id=launch_id,
                        max_turns=args.max_turns,
                        agent_config=agent_config,
                        enable_reportportal=args.enable_reportportal
                    )
                else:
                    # Run all migration tests individually
                    migration_results = await run_all_migration_tests(
                        computer=computer,
                        old_version_path=args.old_version,
                        new_version_path=args.new_version,
                        rp_client=rp_client,
                        launch_id=launch_id,
                        max_turns=args.max_turns,
                        agent_config=agent_config,
                    enable_reportportal=args.enable_reportportal
                )
                
                # Handle overall results
                if migration_results and migration_results.get("overall_success", False):
                    logger.info("[SUCCESS] All migration tests completed successfully!")
                    final_exit_code = 0
                else:
                    logger.error("[FAILED] One or more migration tests failed!")
                    if migration_results:
                        logger.error(f"Failed {migration_results.get('failed', 0)} out of {migration_results.get('total_tests', 0)} tests")
                    final_exit_code = 1
            
            # Skip regular test execution in migration mode
            logger.info("Migration testing completed. Skipping regular test execution.")
            
        else:
            # Regular test execution mode (base/current version testing)
            logger.info("Running base test execution mode (current version testing)")
            
            # Use base tests directory if default tests_dir is being used
            base_tests_dir = args.tests_dir
            if args.tests_dir == 'tests/base' and not os.path.exists(args.tests_dir):
                # Fallback to old structure if base directory doesn't exist
                if os.path.exists('tests'):
                    base_tests_dir = 'tests'
                    logger.warning("tests/base directory not found, using 'tests' as fallback")
            
            logger.info(f"Using test directory: {base_tests_dir}")
            
            # Scan all test files
            test_files = scan_test_files(base_tests_dir)
            
            if not test_files:
                logger.warning(f"No test files found in directory: {base_tests_dir}")
                return
            
            logger.info(f"Found {len(test_files)} test files")
            
            # Track test results for final exit code
            test_results = {"passed": 0, "failed": 0, "total": len(test_files)}
            
            # Run each test sequentially with turn monitoring
            for i, test_data in enumerate(test_files, 1):
                logger.info(f"Running test {i}/{len(test_files)}: {test_data['path']}")
                
                try:
                    # Pass all configs to test runner
                    test_result = await run_single_test_with_timeout(
                        computer=computer, 
                        test_data=test_data, 
                        rp_client=rp_client,  # Can be None
                        launch_id=launch_id,  # Can be None
                        max_turns=args.max_turns,
                        jan_app_path=args.jan_app_path,
                        jan_process_name=args.jan_process_name,
                        agent_config=agent_config,
                        enable_reportportal=args.enable_reportportal
                    )
                    
                    # Track test result - properly handle different return formats
                    test_passed = False
                    
                    if test_result:
                        # Check different possible return formats
                        if isinstance(test_result, dict):
                            # Dictionary format: check 'success' key
                            test_passed = test_result.get('success', False)
                        elif isinstance(test_result, bool):
                            # Boolean format: direct boolean value
                            test_passed = test_result
                        elif hasattr(test_result, 'success'):
                            # Object format: check success attribute
                            test_passed = getattr(test_result, 'success', False)
                        else:
                            # Any truthy value is considered success
                            test_passed = bool(test_result)
                    else:
                        test_passed = False
                    
                    # Update counters and log result
                    if test_passed:
                        test_results["passed"] += 1
                        logger.info(f"[SUCCESS] Test {i} PASSED: {test_data['path']}")
                    else:
                        test_results["failed"] += 1
                        logger.error(f"[FAILED] Test {i} FAILED: {test_data['path']}")
                        
                    # Debug log for troubleshooting
                    logger.info(f"[INFO] Debug - Test result: type={type(test_result)}, value={test_result}, success_field={test_result.get('success', 'N/A') if isinstance(test_result, dict) else 'N/A'}, final_passed={test_passed}")
                        
                except Exception as e:
                    test_results["failed"] += 1
                    logger.error(f"[FAILED] Test {i} FAILED with exception: {test_data['path']} - {e}")
                
                # Add delay between tests
                if i < len(test_files):
                    logger.info(f"Waiting {args.delay_between_tests} seconds before next test...")
                    await asyncio.sleep(args.delay_between_tests)
            
            # Log final test results summary
            logger.info("=" * 50)
            logger.info("TEST EXECUTION SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Total tests: {test_results['total']}")
            logger.info(f"Passed: {test_results['passed']}")
            logger.info(f"Failed: {test_results['failed']}")
            logger.info(f"Success rate: {(test_results['passed']/test_results['total']*100):.1f}%")
            logger.info("=" * 50)
            
            if test_results["failed"] > 0:
                logger.error(f"[FAILED] Test execution completed with {test_results['failed']} failures!")
                final_exit_code = 1
            else:
                logger.info("[SUCCESS] All tests completed successfully!")
                final_exit_code = 0
        
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        final_exit_code = 1
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        final_exit_code = 1
    finally:
        # Finish ReportPortal launch only if it was started
        if args.enable_reportportal and rp_client and launch_id:
            try:
                rp_client.finish_launch(
                    launch_id=launch_id,
                    end_time=timestamp()
                )
                rp_client.session.close()
                logger.info("ReportPortal launch finished and session closed")
            except Exception as e:
                logger.error(f"Error finishing ReportPortal launch: {e}")
        
        # Note: daemon thread will automatically terminate when main program ends
        if server_thread:
            logger.info("Computer server will stop when main program exits (daemon thread)")
    
    # Exit with appropriate code based on test results
    logger.info(f"Exiting with code: {final_exit_code}")
    exit(final_exit_code)

if __name__ == "__main__":
    asyncio.run(main())