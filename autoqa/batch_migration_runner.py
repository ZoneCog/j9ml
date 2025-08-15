import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
import threading

from utils import force_close_jan, is_jan_running, start_jan_app
from migration_utils import install_jan_version, prepare_migration_environment
from test_runner import run_single_test_with_timeout
from agent import ComputerAgent, LLM
from screen_recorder import ScreenRecorder
from reportportal_handler import upload_test_results_to_rp
from utils import get_latest_trajectory_folder
from reportportal_handler import extract_test_result_from_trajectory

logger = logging.getLogger(__name__)

async def run_single_test_with_timeout_no_restart(computer, test_data, rp_client, launch_id, max_turns=30, 
                                                 jan_app_path=None, jan_process_name="Jan.exe", agent_config=None, 
                                                 enable_reportportal=False):
    """
    Run a single test case WITHOUT restarting the Jan app - assumes app is already running
    Returns dict with test result: {"success": bool, "status": str, "message": str}
    """
    path = test_data['path']
    prompt = test_data['prompt']
    
    # Detect if using nightly version based on process name
    is_nightly = "nightly" in jan_process_name.lower() if jan_process_name else False
    
    # Default agent config if not provided
    if agent_config is None:
        agent_config = {
            "loop": "uitars",
            "model_provider": "oaicompat",
            "model_name": "ByteDance-Seed/UI-TARS-1.5-7B",
            "model_base_url": "http://10.200.108.58:1234/v1"
        }
    
    # Create trajectory_dir from path (remove .txt extension)
    trajectory_name = str(Path(path).with_suffix(''))
    trajectory_base_dir = os.path.abspath(f"trajectories/{trajectory_name.replace(os.sep, '/')}")
    
    # Ensure trajectories directory exists
    os.makedirs(os.path.dirname(trajectory_base_dir), exist_ok=True)
    
    # Create recordings directory
    recordings_dir = "recordings"
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Create video filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_test_name = trajectory_name.replace('/', '_').replace('\\', '_')
    video_filename = f"{safe_test_name}_{current_time}.mp4"
    video_path = os.path.abspath(os.path.join(recordings_dir, video_filename))
    
    # Initialize screen recorder
    recorder = ScreenRecorder(video_path, fps=10)
    
    try:
        # Check if Jan app is running (don't restart)
        from utils import is_jan_running
        if not is_jan_running(jan_process_name):
            logger.warning(f"Jan application ({jan_process_name}) is not running, but continuing anyway")
        else:
            # Ensure window is maximized for this test
            from utils import maximize_jan_window
            if maximize_jan_window():
                logger.info("Jan application window maximized for test")
            else:
                logger.warning("Could not maximize Jan application window for test")
        
        # Start screen recording
        recorder.start_recording()
        
        # Create agent for this test using config
        agent = ComputerAgent(
            computer=computer,
            loop=agent_config["loop"],
            model=LLM(
                provider=agent_config["model_provider"],
                name=agent_config["model_name"],
                provider_base_url=agent_config["model_base_url"]
            ),
            trajectory_dir=trajectory_base_dir
        )
        
        # Run the test with prompt
        logger.info(f"Running test case: {path}")
        
        async for result in agent.run(prompt):
            logger.info(f"Test result for {path}: {result}")
            print(result)
        
        # Stop screen recording
        recorder.stop_recording()
        
        # Extract test result
        trajectory_folder = get_latest_trajectory_folder(path)
        test_result = extract_test_result_from_trajectory(trajectory_folder)
        
        # Upload to ReportPortal if enabled
        if enable_reportportal and rp_client and launch_id:
            upload_test_results_to_rp(rp_client, launch_id, test_result, trajectory_folder)
        
        return test_result
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        recorder.stop_recording()
        return {"success": False, "status": "error", "message": str(e)}
    finally:
        # Stop screen recording
        recorder.stop_recording()
        
        # Don't close Jan app - let it keep running for the next test
        logger.info(f"Completed test: {path} (Jan app kept running)")

async def run_batch_migration_test(computer, old_version_path, new_version_path, 
                                 rp_client=None, launch_id=None, max_turns=30, agent_config=None, 
                                 enable_reportportal=False, test_cases=None):
    """
    Run migration test with batch approach: all setups first, then upgrade, then all verifies
    
    This approach is more realistic (like a real user) but less granular for debugging
    """
    from individual_migration_runner import MIGRATION_TEST_CASES
    
    if test_cases is None:
        test_cases = list(MIGRATION_TEST_CASES.keys())
    
    logger.info("=" * 100)
    logger.info("RUNNING BATCH MIGRATION TESTS")
    logger.info("=" * 100)
    logger.info(f"Test cases: {', '.join(test_cases)}")
    logger.info("Approach: Setup All → Upgrade → Verify All")
    logger.info("")
    
    batch_result = {
        "overall_success": False,
        "setup_phase_success": False,
        "upgrade_success": False,
        "verification_phase_success": False,
        "setup_results": {},
        "verify_results": {},
        "error_message": None
    }
    
    try:
        # Prepare migration environment
        env_setup = prepare_migration_environment()
        logger.info(f"Migration environment prepared: {env_setup}")
        
        # PHASE 1: Install old version and run ALL setup tests
        logger.info("=" * 80)
        logger.info("PHASE 1: BATCH SETUP ON OLD VERSION")
        logger.info("=" * 80)
        
        install_jan_version(old_version_path, "old")
        time.sleep(15)  # Extra wait time for stability
        
        # Force close any existing Jan processes before starting fresh
        logger.info("Force closing any existing Jan processes...")
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")
        time.sleep(5)  # Wait for processes to fully close
        
        # Start Jan app once for the entire setup phase
        logger.info("Starting Jan application for setup phase...")
        start_jan_app()
        time.sleep(10)  # Wait for app to be ready
        
        # Ensure window is maximized for testing
        from utils import maximize_jan_window
        if maximize_jan_window():
            logger.info("Jan application window maximized for setup phase")
        else:
            logger.warning("Could not maximize Jan application window for setup phase")
        
        setup_failures = 0
        
        for i, test_case_key in enumerate(test_cases, 1):
            test_case = MIGRATION_TEST_CASES[test_case_key]
            logger.info(f"[{i}/{len(test_cases)}] Running setup: {test_case['name']}")
            
            # Support both single setup_test and multiple setup_tests
            setup_files = []
            if 'setup_tests' in test_case:
                setup_files = test_case['setup_tests']
            elif 'setup_test' in test_case:
                setup_files = [test_case['setup_test']]
            else:
                logger.error(f"No setup tests defined for {test_case_key}")
                batch_result["setup_results"][test_case_key] = False
                setup_failures += 1
                continue
            
            # Run all setup files for this test case
            test_case_setup_success = True
            for j, setup_file in enumerate(setup_files, 1):
                logger.info(f"  [{j}/{len(setup_files)}] Running setup file: {setup_file}")
                
                # Load and run setup test
                setup_test_path = f"tests/migration/{setup_file}"
                if not os.path.exists(setup_test_path):
                    logger.error(f"Setup test file not found: {setup_test_path}")
                    test_case_setup_success = False
                    continue

                with open(setup_test_path, "r") as f:
                    setup_content = f.read()

                setup_test_data = {
                    "path": setup_file,
                    "prompt": setup_content
                }

                # Run test without restarting Jan app (assumes Jan is already running)
                setup_result = await run_single_test_with_timeout_no_restart(
                    computer=computer,
                    test_data=setup_test_data,
                    rp_client=rp_client,
                    launch_id=launch_id,
                    max_turns=max_turns,
                    jan_app_path=None,
                    jan_process_name="Jan.exe",
                    agent_config=agent_config,
                    enable_reportportal=enable_reportportal
                )

                success = setup_result.get("success", False) if setup_result else False
                if success:
                    logger.info(f"    ✅ Setup file {setup_file}: SUCCESS")
                else:
                    logger.error(f"    ❌ Setup file {setup_file}: FAILED")
                    test_case_setup_success = False

                # Small delay between setup files
                time.sleep(3)
            
            # Record overall result for this test case
            batch_result["setup_results"][test_case_key] = test_case_setup_success
            
            if test_case_setup_success:
                logger.info(f"✅ Setup {test_case_key}: SUCCESS (all {len(setup_files)} files completed)")
            else:
                logger.error(f"❌ Setup {test_case_key}: FAILED (one or more files failed)")
                setup_failures += 1
            
            # Small delay between setups
            time.sleep(3)
        
        batch_result["setup_phase_success"] = setup_failures == 0
        logger.info(f"Setup phase complete: {len(test_cases) - setup_failures}/{len(test_cases)} successful")
        
        if setup_failures > 0:
            logger.warning(f"{setup_failures} setup tests failed - continuing with upgrade anyway")
        
        # PHASE 2: Upgrade to new version
        logger.info("=" * 80)
        logger.info("PHASE 2: UPGRADING TO NEW VERSION")
        logger.info("=" * 80)
        
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")
        time.sleep(5)
        
        install_jan_version(new_version_path, "new")
        batch_result["upgrade_success"] = True
        time.sleep(15)  # Extra wait time after upgrade
        
        # Force close any existing Jan processes before starting fresh
        logger.info("Force closing any existing Jan processes...")
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")
        time.sleep(5)  # Wait for processes to fully close
        
        # Start Jan app once for the entire verification phase
        logger.info("Starting Jan application for verification phase...")
        start_jan_app()
        time.sleep(10)  # Wait for app to be ready
        
        # Ensure window is maximized for testing
        from utils import maximize_jan_window
        if maximize_jan_window():
            logger.info("Jan application window maximized for verification phase")
        else:
            logger.warning("Could not maximize Jan application window for verification phase")
        
        # PHASE 3: Run ALL verification tests on new version
        logger.info("=" * 80) 
        logger.info("PHASE 3: BATCH VERIFICATION ON NEW VERSION")
        logger.info("=" * 80)
        
        verify_failures = 0
        
        for i, test_case_key in enumerate(test_cases, 1):
            test_case = MIGRATION_TEST_CASES[test_case_key]
            logger.info(f"[{i}/{len(test_cases)}] Running verification: {test_case['name']}")
            
            # Skip verification if setup failed (optional - you could still try)
            if not batch_result["setup_results"].get(test_case_key, False):
                logger.warning(f"Skipping verification for {test_case_key} - setup failed")
                batch_result["verify_results"][test_case_key] = False
                verify_failures += 1
                continue
            
            # Support both single verify_test and multiple verify_tests
            verify_files = []
            if 'verify_tests' in test_case:
                verify_files = test_case['verify_tests']
            elif 'verify_test' in test_case:
                verify_files = [test_case['verify_test']]
            else:
                logger.error(f"No verify tests defined for {test_case_key}")
                batch_result["verify_results"][test_case_key] = False
                verify_failures += 1
                continue
            
            # Run all verify files for this test case
            test_case_verify_success = True
            for j, verify_file in enumerate(verify_files, 1):
                logger.info(f"  [{j}/{len(verify_files)}] Running verify file: {verify_file}")
                
                # Load and run verification test
                verify_test_path = f"tests/migration/{verify_file}"
                if not os.path.exists(verify_test_path):
                    logger.error(f"Verification test file not found: {verify_test_path}")
                    test_case_verify_success = False
                    continue

                with open(verify_test_path, "r") as f:
                    verify_content = f.read()

                verify_test_data = {
                    "path": verify_file,
                    "prompt": verify_content
                }

                # Run test without restarting Jan app (assumes Jan is already running)
                verify_result = await run_single_test_with_timeout_no_restart(
                    computer=computer,
                    test_data=verify_test_data,
                    rp_client=rp_client,
                    launch_id=launch_id,
                    max_turns=max_turns,
                    jan_app_path=None,
                    jan_process_name="Jan.exe",
                    agent_config=agent_config,
                    enable_reportportal=enable_reportportal
                )

                success = verify_result.get("success", False) if verify_result else False
                if success:
                    logger.info(f"    ✅ Verify file {verify_file}: SUCCESS")
                else:
                    logger.error(f"    ❌ Verify file {verify_file}: FAILED")
                    test_case_verify_success = False

                # Small delay between verify files
                time.sleep(3)
            
            # Record overall result for this test case
            batch_result["verify_results"][test_case_key] = test_case_verify_success
            
            if test_case_verify_success:
                logger.info(f"✅ Verify {test_case_key}: SUCCESS (all {len(verify_files)} files completed)")
            else:
                logger.error(f"❌ Verify {test_case_key}: FAILED (one or more files failed)")
                verify_failures += 1
            
            # Small delay between verifications
            time.sleep(3)
        
        batch_result["verification_phase_success"] = verify_failures == 0
        logger.info(f"Verification phase complete: {len(test_cases) - verify_failures}/{len(test_cases)} successful")
        
        # Overall success calculation
        batch_result["overall_success"] = (
            batch_result["setup_phase_success"] and
            batch_result["upgrade_success"] and
            batch_result["verification_phase_success"]
        )
        
        # Final summary
        logger.info("=" * 100)
        logger.info("BATCH MIGRATION TEST SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Overall Success: {batch_result['overall_success']}")
        logger.info(f"Setup Phase: {batch_result['setup_phase_success']} ({len(test_cases) - setup_failures}/{len(test_cases)})")
        logger.info(f"Upgrade Phase: {batch_result['upgrade_success']}")
        logger.info(f"Verification Phase: {batch_result['verification_phase_success']} ({len(test_cases) - verify_failures}/{len(test_cases)})")
        logger.info("")
        logger.info("Detailed Results:")
        for test_case_key in test_cases:
            setup_status = "✅" if batch_result["setup_results"].get(test_case_key, False) else "❌"
            verify_status = "✅" if batch_result["verify_results"].get(test_case_key, False) else "❌"
            logger.info(f"  {test_case_key.ljust(20)}: Setup {setup_status} | Verify {verify_status}")
            
        return batch_result
        
    except Exception as e:
        logger.error(f"Batch migration test failed with exception: {e}")
        batch_result["error_message"] = str(e)
        return batch_result
    finally:
        # Cleanup
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")


