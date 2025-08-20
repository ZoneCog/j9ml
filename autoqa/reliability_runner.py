import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from test_runner import run_single_test_with_timeout
from utils import scan_test_files

logger = logging.getLogger(__name__)

async def run_reliability_test(computer, test_path, rp_client=None, launch_id=None, 
                              max_turns=30, jan_app_path=None, jan_process_name="Jan.exe", 
                              agent_config=None, enable_reportportal=False, 
                              phase="development", runs=5):
    """
    Run a single test case multiple times to verify reliability and stability
    
    Args:
        computer: Computer agent instance
        test_path: Path to the test file to run
        rp_client: ReportPortal client (optional)
        launch_id: ReportPortal launch ID (optional)
        max_turns: Maximum turns per test
        jan_app_path: Path to Jan application
        jan_process_name: Jan process name for monitoring
        agent_config: Agent configuration
        enable_reportportal: Whether to upload to ReportPortal
        phase: "development" (5 runs) or "deployment" (20 runs)
        runs: Number of runs to execute (overrides phase if specified)
    
    Returns:
        dict with reliability test results
    """
    # Determine number of runs based on phase
    if phase == "development":
        target_runs = 5
    elif phase == "deployment":
        target_runs = 20
    else:
        target_runs = runs
    
    logger.info("=" * 100)
    logger.info(f"RELIABILITY TESTING: {test_path.upper()}")
    logger.info("=" * 100)
    logger.info(f"Phase: {phase.upper()}")
    logger.info(f"Target runs: {target_runs}")
    logger.info(f"Test file: {test_path}")
    logger.info("")
    
    # Load test content
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test file not found: {test_path}")
    
    with open(test_path, "r", encoding="utf-8") as f:
        test_content = f.read()
    
    test_data = {
        "path": test_path,
        "prompt": test_content
    }
    
    # Initialize results tracking
    reliability_results = {
        "test_path": test_path,
        "phase": phase,
        "target_runs": target_runs,
        "completed_runs": 0,
        "successful_runs": 0,
        "failed_runs": 0,
        "run_details": [],
        "start_time": datetime.now(),
        "end_time": None,
        "success_rate": 0.0,
        "overall_success": False
    }
    
    logger.info(f"Starting reliability testing with {target_runs} runs...")
    logger.info("=" * 80)
    
    try:
        for run_number in range(1, target_runs + 1):
            logger.info(f"Run {run_number}/{target_runs}")
            logger.info("-" * 40)
            
            run_start_time = datetime.now()
            
            try:
                # Run the test
                test_result = await run_single_test_with_timeout(
                    computer=computer,
                    test_data=test_data,
                    rp_client=rp_client,
                    launch_id=launch_id,
                    max_turns=max_turns,
                    jan_app_path=jan_app_path,
                    jan_process_name=jan_process_name,
                    agent_config=agent_config,
                    enable_reportportal=enable_reportportal
                )
                
                # Extract success status
                success = False
                if test_result:
                    if isinstance(test_result, dict):
                        success = test_result.get('success', False)
                    elif isinstance(test_result, bool):
                        success = test_result
                    elif hasattr(test_result, 'success'):
                        success = getattr(test_result, 'success', False)
                    else:
                        success = bool(test_result)
                
                run_end_time = datetime.now()
                run_duration = (run_end_time - run_start_time).total_seconds()
                
                # Record run result
                run_result = {
                    "run_number": run_number,
                    "success": success,
                    "start_time": run_start_time,
                    "end_time": run_end_time,
                    "duration_seconds": run_duration,
                    "test_result": test_result
                }
                
                reliability_results["run_details"].append(run_result)
                reliability_results["completed_runs"] += 1
                
                if success:
                    reliability_results["successful_runs"] += 1
                    logger.info(f"✅ Run {run_number}: SUCCESS ({run_duration:.1f}s)")
                else:
                    reliability_results["failed_runs"] += 1
                    logger.error(f"❌ Run {run_number}: FAILED ({run_duration:.1f}s)")
                
                # Calculate current success rate
                current_success_rate = (reliability_results["successful_runs"] / reliability_results["completed_runs"]) * 100
                logger.info(f"Current success rate: {reliability_results['successful_runs']}/{reliability_results['completed_runs']} ({current_success_rate:.1f}%)")
                
            except Exception as e:
                run_end_time = datetime.now()
                run_duration = (run_end_time - run_start_time).total_seconds()
                
                # Record failed run
                run_result = {
                    "run_number": run_number,
                    "success": False,
                    "start_time": run_start_time,
                    "end_time": run_end_time,
                    "duration_seconds": run_duration,
                    "error": str(e)
                }
                
                reliability_results["run_details"].append(run_result)
                reliability_results["completed_runs"] += 1
                reliability_results["failed_runs"] += 1
                
                logger.error(f"❌ Run {run_number}: EXCEPTION ({run_duration:.1f}s) - {e}")
                
                # Calculate current success rate
                current_success_rate = (reliability_results["successful_runs"] / reliability_results["completed_runs"]) * 100
                logger.info(f"Current success rate: {reliability_results['successful_runs']}/{reliability_results['completed_runs']} ({current_success_rate:.1f}%)")
            
            # Add delay between runs (except for the last run)
            if run_number < target_runs:
                delay_seconds = 5
                logger.info(f"Waiting {delay_seconds} seconds before next run...")
                await asyncio.sleep(delay_seconds)
        
        # Final calculations
        reliability_results["end_time"] = datetime.now()
        total_duration = (reliability_results["end_time"] - reliability_results["start_time"]).total_seconds()
        reliability_results["total_duration_seconds"] = total_duration
        
        if reliability_results["completed_runs"] > 0:
            reliability_results["success_rate"] = (reliability_results["successful_runs"] / reliability_results["completed_runs"]) * 100
        
        # Determine overall success based on phase
        if phase == "development":
            # Development phase: 80% success rate required
            reliability_results["overall_success"] = reliability_results["success_rate"] >= 80.0
        else:
            # Deployment phase: 90% success rate required
            reliability_results["overall_success"] = reliability_results["success_rate"] >= 90.0
        
        # Print final summary
        logger.info("=" * 80)
        logger.info("RELIABILITY TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Test: {test_path}")
        logger.info(f"Phase: {phase.upper()}")
        logger.info(f"Completed runs: {reliability_results['completed_runs']}/{target_runs}")
        logger.info(f"Successful runs: {reliability_results['successful_runs']}")
        logger.info(f"Failed runs: {reliability_results['failed_runs']}")
        logger.info(f"Success rate: {reliability_results['success_rate']:.1f}%")
        logger.info(f"Total duration: {total_duration:.1f} seconds")
        logger.info(f"Average duration per run: {total_duration / reliability_results['completed_runs']:.1f} seconds")
        logger.info(f"Overall result: {'✅ PASSED' if reliability_results['overall_success'] else '❌ FAILED'}")
        
        # Phase-specific requirements
        if phase == "development":
            logger.info("Development phase requirement: ≥80% success rate")
        else:
            logger.info("Deployment phase requirement: ≥90% success rate")
        
        return reliability_results
        
    except Exception as e:
        logger.error(f"Reliability testing failed with exception: {e}")
        reliability_results["end_time"] = datetime.now()
        reliability_results["error_message"] = str(e)
        return reliability_results

async def run_reliability_tests(computer, test_paths, rp_client=None, launch_id=None, 
                               max_turns=30, jan_app_path=None, jan_process_name="Jan.exe", 
                               agent_config=None, enable_reportportal=False, 
                               phase="development", runs=None):
    """
    Run reliability tests for multiple test files
    
    Args:
        computer: Computer agent instance
        test_paths: List of test file paths or single path
        rp_client: ReportPortal client (optional)
        launch_id: ReportPortal launch ID (optional)
        max_turns: Maximum turns per test
        jan_app_path: Path to Jan application
        jan_process_name: Jan process name for monitoring
        agent_config: Agent configuration
        enable_reportportal: Whether to upload to ReportPortal
        phase: "development" (5 runs) or "deployment" (20 runs)
        runs: Number of runs to execute (overrides phase if specified)
    
    Returns:
        dict with overall reliability test results
    """
    # Convert single path to list
    if isinstance(test_paths, str):
        test_paths = [test_paths]
    
    logger.info("=" * 100)
    logger.info("RELIABILITY TESTING SUITE")
    logger.info("=" * 100)
    logger.info(f"Phase: {phase.upper()}")
    logger.info(f"Test files: {len(test_paths)}")
    logger.info(f"Test paths: {', '.join(test_paths)}")
    logger.info("")
    
    overall_results = {
        "phase": phase,
        "total_tests": len(test_paths),
        "completed_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_results": {},
        "start_time": datetime.now(),
        "end_time": None,
        "overall_success": False
    }
    
    try:
        for i, test_path in enumerate(test_paths, 1):
            logger.info(f"Starting reliability test {i}/{len(test_paths)}: {test_path}")
            
            test_result = await run_reliability_test(
                computer=computer,
                test_path=test_path,
                rp_client=rp_client,
                launch_id=launch_id,
                max_turns=max_turns,
                jan_app_path=jan_app_path,
                jan_process_name=jan_process_name,
                agent_config=agent_config,
                enable_reportportal=enable_reportportal,
                phase=phase,
                runs=runs
            )
            
            overall_results["test_results"][test_path] = test_result
            overall_results["completed_tests"] += 1
            
            if test_result and test_result.get("overall_success", False):
                overall_results["passed_tests"] += 1
                logger.info(f"✅ Test {i} PASSED: {test_path}")
            else:
                overall_results["failed_tests"] += 1
                logger.error(f"❌ Test {i} FAILED: {test_path}")
            
            # Add delay between tests (except for the last test)
            if i < len(test_paths):
                delay_seconds = 10
                logger.info(f"Waiting {delay_seconds} seconds before next test...")
                await asyncio.sleep(delay_seconds)
        
        # Final calculations
        overall_results["end_time"] = datetime.now()
        total_duration = (overall_results["end_time"] - overall_results["start_time"]).total_seconds()
        overall_results["total_duration_seconds"] = total_duration
        
        if overall_results["completed_tests"] > 0:
            overall_results["overall_success"] = overall_results["failed_tests"] == 0
        
        # Print overall summary
        logger.info("=" * 100)
        logger.info("RELIABILITY TESTING SUITE SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Phase: {phase.upper()}")
        logger.info(f"Total tests: {overall_results['total_tests']}")
        logger.info(f"Completed tests: {overall_results['completed_tests']}")
        logger.info(f"Passed tests: {overall_results['passed_tests']}")
        logger.info(f"Failed tests: {overall_results['failed_tests']}")
        logger.info(f"Total duration: {total_duration:.1f} seconds")
        logger.info(f"Overall result: {'✅ PASSED' if overall_results['overall_success'] else '❌ FAILED'}")
        
        # Individual test results
        logger.info("")
        logger.info("Individual Test Results:")
        for test_path, test_result in overall_results["test_results"].items():
            if test_result:
                status = "✅ PASSED" if test_result.get("overall_success", False) else "❌ FAILED"
                success_rate = test_result.get("success_rate", 0.0)
                logger.info(f"  {test_path}: {status} ({success_rate:.1f}% success rate)")
            else:
                logger.info(f"  {test_path}: ❌ ERROR (no result)")
        
        return overall_results
        
    except Exception as e:
        logger.error(f"Reliability testing suite failed with exception: {e}")
        overall_results["end_time"] = datetime.now()
        overall_results["error_message"] = str(e)
        return overall_results
