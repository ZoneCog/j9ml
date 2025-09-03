import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from utils import force_close_jan, is_jan_running
from migration_utils import install_jan_version, prepare_migration_environment
from test_runner import run_single_test_with_timeout

logger = logging.getLogger(__name__)

# Migration test case definitions - organized by QA checklist categories
MIGRATION_TEST_CASES = {
    "models": {
        "name": "Model Downloads Migration",
        "setup_test": "models/setup-download-model.txt",
        "verify_test": "models/verify-model-persistence.txt", 
        "description": "Tests that downloaded models persist after upgrade"
    },
    "assistants": {
        "name": "Custom Assistants Migration",
        "setup_test": "assistants/setup-create-assistants.txt",
        "verify_test": "assistants/verify-create-assistant-persistence.txt",
        "description": "Tests that custom assistants persist after upgrade"
    },
    # "assistants-complete": {
    #     "name": "Complete Assistants Migration (Create + Chat)",
    #     "setup_tests": [
    #         "assistants/setup-create-assistants.txt",
    #         "assistants/setup-chat-with-assistant.txt"
    #     ],
    #     "verify_tests": [
    #         "assistants/verify-create-assistant-persistence.txt", 
    #         "assistants/verify-chat-with-assistant-persistence.txt"
    #     ],
    #     "description": "Tests that custom assistants creation and chat functionality persist after upgrade (batch mode only)"
    # },
    "modify-local-api-server": {
        "name": "Modify Local API Server Settings Migration",
        "setup_test": "settings/setup-local-api-server.txt",
        "verify_test": "settings/verify-local-api-server-persistence.txt",
        "description": "Tests that local API server settings (port and API prefix) persist after upgrade"
    },
    "modify-https-proxy": {
        "name": "Modify HTTPS Proxy Settings Migration",
        "setup_test": "settings/setup-https-proxy.txt",
        "verify_test": "settings/verify-https-proxy-persistence.txt",
        "description": "Tests that HTTPS proxy settings persist after upgrade"
    }
}

async def run_individual_migration_test(computer, test_case_key, old_version_path, new_version_path, 
                                      rp_client=None, launch_id=None, max_turns=30, agent_config=None, 
                                      enable_reportportal=False):
    """
    Run a single migration test case
    
    Args:
        computer: Computer agent instance
        test_case_key: Key identifying the test case (e.g., "models", "chat-threads")
        old_version_path: Path to old version installer
        new_version_path: Path to new version installer  
        rp_client: ReportPortal client (optional)
        launch_id: ReportPortal launch ID (optional)
        max_turns: Maximum turns per test phase
        agent_config: Agent configuration
        enable_reportportal: Whether to upload to ReportPortal
    """
    if test_case_key not in MIGRATION_TEST_CASES:
        raise ValueError(f"Unknown test case: {test_case_key}")
    
    test_case = MIGRATION_TEST_CASES[test_case_key]
    
    logger.info("=" * 80)
    logger.info(f"RUNNING MIGRATION TEST: {test_case['name'].upper()}")
    logger.info("=" * 80)
    logger.info(f"Description: {test_case['description']}")
    logger.info(f"Setup Test: tests/migration/{test_case['setup_test']}")
    logger.info(f"Verify Test: tests/migration/{test_case['verify_test']}")
    logger.info("")
    logger.info("Test Flow:")
    logger.info("  1. Install OLD version → Run SETUP test")
    logger.info("  2. Install NEW version → Run VERIFY test") 
    logger.info("  3. Cleanup and prepare for next test")
    logger.info("")
    
    migration_result = {
        "test_case": test_case_key,
        "test_name": test_case["name"],
        "overall_success": False,
        "old_version_setup": False,
        "new_version_install": False,
        "upgrade_verification": False,
        "error_message": None
    }
    
    try:
        # Prepare migration environment
        env_setup = prepare_migration_environment()
        logger.info(f"Migration environment prepared: {env_setup}")
        
        # Phase 1: Install old version and run setup test
        logger.info("PHASE 1: Installing old version and running setup test")
        logger.info("-" * 60)
        
        install_jan_version(old_version_path, "old")
        time.sleep(10)  # Wait for Jan to be ready
        
        # Load and run setup test
        setup_test_path = f"tests/migration/{test_case['setup_test']}"
        if not os.path.exists(setup_test_path):
            raise FileNotFoundError(f"Setup test file not found: {setup_test_path}")
        
        with open(setup_test_path, "r", encoding="utf-8") as f:
            setup_content = f.read()
        
        setup_test_data = {
            "path": test_case['setup_test'],
            "prompt": setup_content
        }
        
        setup_result = await run_single_test_with_timeout(
            computer=computer,
            test_data=setup_test_data,
            rp_client=rp_client,
            launch_id=launch_id,
            max_turns=max_turns,
            jan_app_path=None,  # Auto-detect
            jan_process_name="Jan.exe",
            agent_config=agent_config,
            enable_reportportal=enable_reportportal
        )
        
        migration_result["old_version_setup"] = setup_result.get("success", False) if setup_result else False
        logger.info(f"Setup phase result: {migration_result['old_version_setup']}")
        
        if not migration_result["old_version_setup"]:
            migration_result["error_message"] = f"Failed to setup {test_case['name']} on old version"
            return migration_result
        
        # Phase 2: Install new version (upgrade)
        logger.info("PHASE 2: Installing new version (upgrade)")
        logger.info("-" * 60)
        
        # Force close Jan before installing new version
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe") 
        time.sleep(5)
        
        # Install new version
        install_jan_version(new_version_path, "new")
        migration_result["new_version_install"] = True
        time.sleep(10)  # Wait for new version to be ready
        
        # Phase 3: Run verification test on new version (includes data integrity check)
        logger.info("PHASE 3: Running verification test on new version")
        logger.info("-" * 60)
        
        # Load and run verification test
        verify_test_path = f"tests/migration/{test_case['verify_test']}"
        if not os.path.exists(verify_test_path):
            raise FileNotFoundError(f"Verification test file not found: {verify_test_path}")
        
        with open(verify_test_path, "r", encoding="utf-8") as f:
            verify_content = f.read()
        
        verify_test_data = {
            "path": test_case['verify_test'],
            "prompt": verify_content
        }
        
        verify_result = await run_single_test_with_timeout(
            computer=computer,
            test_data=verify_test_data,
            rp_client=rp_client,
            launch_id=launch_id,
            max_turns=max_turns,
            jan_app_path=None,  # Auto-detect
            jan_process_name="Jan.exe",
            agent_config=agent_config,
            enable_reportportal=enable_reportportal
        )
        
        migration_result["upgrade_verification"] = verify_result.get("success", False) if verify_result else False
        logger.info(f"Verification phase result: {migration_result['upgrade_verification']}")
        
        # Overall success check
        migration_result["overall_success"] = (
            migration_result["old_version_setup"] and
            migration_result["new_version_install"] and  
            migration_result["upgrade_verification"]
        )
        
        logger.info("=" * 80)
        logger.info(f"MIGRATION TEST COMPLETED: {test_case['name'].upper()}")
        logger.info("=" * 80)
        logger.info(f"Overall Success: {migration_result['overall_success']}")
        logger.info(f"Old Version Setup: {migration_result['old_version_setup']}")
        logger.info(f"New Version Install: {migration_result['new_version_install']}")
        logger.info(f"Upgrade Verification: {migration_result['upgrade_verification']}")
        
        return migration_result
        
    except Exception as e:
        logger.error(f"Migration test {test_case['name']} failed with exception: {e}")
        migration_result["error_message"] = str(e)
        return migration_result
    finally:
        # Cleanup: Force close any remaining Jan processes
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")

async def run_assistant_batch_migration_test(computer, old_version_path, new_version_path, 
                                           rp_client=None, launch_id=None, max_turns=30, agent_config=None, 
                                           enable_reportportal=False):
    """
    Run both assistant test cases in batch mode: 
    - Setup both assistant tests on old version
    - Upgrade to new version
    - Verify both assistant tests on new version
    """
    assistant_test_cases = ["assistants", "assistant-chat"]
    
    logger.info("=" * 100)
    logger.info("RUNNING ASSISTANT BATCH MIGRATION TESTS")
    logger.info("=" * 100)
    logger.info(f"Test cases: {', '.join(assistant_test_cases)}")
    logger.info("Approach: Setup Both → Upgrade → Verify Both")
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
        
        # PHASE 1: Install old version and run BOTH setup tests
        logger.info("=" * 80)
        logger.info("PHASE 1: BATCH SETUP ON OLD VERSION")
        logger.info("=" * 80)
        
        install_jan_version(old_version_path, "old")
        time.sleep(15)  # Extra wait time for stability
        
        setup_failures = 0
        
        for i, test_case_key in enumerate(assistant_test_cases, 1):
            test_case = MIGRATION_TEST_CASES[test_case_key]
            logger.info(f"[{i}/{len(assistant_test_cases)}] Running setup: {test_case['name']}")
            
            # Load and run setup test
            setup_test_path = f"tests/migration/{test_case['setup_test']}"
            if not os.path.exists(setup_test_path):
                logger.error(f"Setup test file not found: {setup_test_path}")
                batch_result["setup_results"][test_case_key] = False
                setup_failures += 1
                continue
            
            with open(setup_test_path, "r") as f:
                setup_content = f.read()
            
            setup_test_data = {
                "path": test_case['setup_test'],
                "prompt": setup_content
            }
            
            setup_result = await run_single_test_with_timeout(
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
            batch_result["setup_results"][test_case_key] = success
            
            if success:
                logger.info(f"✅ Setup {test_case_key}: SUCCESS")
            else:
                logger.error(f"❌ Setup {test_case_key}: FAILED")
                setup_failures += 1
            
            # Small delay between setups
            time.sleep(3)
        
        batch_result["setup_phase_success"] = setup_failures == 0
        logger.info(f"Setup phase complete: {len(assistant_test_cases) - setup_failures}/{len(assistant_test_cases)} successful")
        
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
        
        # PHASE 3: Run BOTH verification tests on new version
        logger.info("=" * 80) 
        logger.info("PHASE 3: BATCH VERIFICATION ON NEW VERSION")
        logger.info("=" * 80)
        
        verify_failures = 0
        
        for i, test_case_key in enumerate(assistant_test_cases, 1):
            test_case = MIGRATION_TEST_CASES[test_case_key]
            logger.info(f"[{i}/{len(assistant_test_cases)}] Running verification: {test_case['name']}")
            
            # Load and run verification test
            verify_test_path = f"tests/migration/{test_case['verify_test']}"
            if not os.path.exists(verify_test_path):
                logger.error(f"Verification test file not found: {verify_test_path}")
                batch_result["verify_results"][test_case_key] = False
                verify_failures += 1
                continue
            
            with open(verify_test_path, "r") as f:
                verify_content = f.read()
            
            verify_test_data = {
                "path": test_case['verify_test'],
                "prompt": verify_content
            }
            
            verify_result = await run_single_test_with_timeout(
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
            batch_result["verify_results"][test_case_key] = success
            
            if success:
                logger.info(f"✅ Verify {test_case_key}: SUCCESS")
            else:
                logger.error(f"❌ Verify {test_case_key}: FAILED")
                verify_failures += 1
            
            # Small delay between verifications
            time.sleep(3)
        
        batch_result["verification_phase_success"] = verify_failures == 0
        logger.info(f"Verification phase complete: {len(assistant_test_cases) - verify_failures}/{len(assistant_test_cases)} successful")
        
        # Overall success calculation
        batch_result["overall_success"] = (
            batch_result["setup_phase_success"] and
            batch_result["upgrade_success"] and
            batch_result["verification_phase_success"]
        )
        
        # Final summary
        logger.info("=" * 100)
        logger.info("ASSISTANT BATCH MIGRATION TEST SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Overall Success: {batch_result['overall_success']}")
        logger.info(f"Setup Phase: {batch_result['setup_phase_success']} ({len(assistant_test_cases) - setup_failures}/{len(assistant_test_cases)})")
        logger.info(f"Upgrade Phase: {batch_result['upgrade_success']}")
        logger.info(f"Verification Phase: {batch_result['verification_phase_success']} ({len(assistant_test_cases) - verify_failures}/{len(assistant_test_cases)})")
        logger.info("")
        logger.info("Detailed Results:")
        for test_case_key in assistant_test_cases:
            setup_status = "✅" if batch_result["setup_results"].get(test_case_key, False) else "❌"
            verify_status = "✅" if batch_result["verify_results"].get(test_case_key, False) else "❌"
            logger.info(f"  {test_case_key.ljust(20)}: Setup {setup_status} | Verify {verify_status}")
            
        return batch_result
        
    except Exception as e:
        logger.error(f"Assistant batch migration test failed with exception: {e}")
        batch_result["error_message"] = str(e)
        return batch_result
    finally:
        # Cleanup
        force_close_jan("Jan.exe")
        force_close_jan("Jan-nightly.exe")

async def run_all_migration_tests(computer, old_version_path, new_version_path, rp_client=None, 
                                launch_id=None, max_turns=30, agent_config=None, enable_reportportal=False,
                                test_cases=None):
    """
    Run multiple migration test cases
    
    Args:
        test_cases: List of test case keys to run. If None, runs all test cases.
    """
    if test_cases is None:
        test_cases = list(MIGRATION_TEST_CASES.keys())
    
    logger.info("=" * 100)
    logger.info("RUNNING ALL MIGRATION TESTS")
    logger.info("=" * 100)
    logger.info(f"Test cases to run: {', '.join(test_cases)}")
    
    results = {}
    overall_success = True
    
    for i, test_case_key in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{len(test_cases)}] Starting migration test: {test_case_key}")
        
        result = await run_individual_migration_test(
            computer=computer,
            test_case_key=test_case_key,
            old_version_path=old_version_path,
            new_version_path=new_version_path,
            rp_client=rp_client,
            launch_id=launch_id,
            max_turns=max_turns,
            agent_config=agent_config,
            enable_reportportal=enable_reportportal
        )
        
        results[test_case_key] = result
        if not result["overall_success"]:
            overall_success = False
        
        # Add delay between test cases
        if i < len(test_cases):
            logger.info("Waiting 30 seconds before next migration test...")
            time.sleep(30)
    
    # Final summary
    logger.info("=" * 100)
    logger.info("MIGRATION TESTS SUMMARY")
    logger.info("=" * 100)
    
    passed = sum(1 for r in results.values() if r["overall_success"])
    failed = len(results) - passed
    
    logger.info(f"Total tests: {len(results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Overall success: {overall_success}")
    
    for test_case_key, result in results.items():
        status = "PASS" if result["overall_success"] else "FAIL" 
        logger.info(f"  {test_case_key}: {status}")
        if result["error_message"]:
            logger.info(f"    Error: {result['error_message']}")
    
    return {
        "overall_success": overall_success,
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "results": results
    }
