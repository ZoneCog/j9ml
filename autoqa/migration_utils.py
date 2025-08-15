import os
import logging
import subprocess
import time
from pathlib import Path
from utils import force_close_jan, is_jan_running, start_jan_app

logger = logging.getLogger(__name__)

def install_jan_version(installer_path, version_type="old"):
    """
    Install a specific version of Jan
    
    Args:
        installer_path: Path to the installer file
        version_type: "old" or "new" for logging purposes
    """
    logger.info(f"Installing Jan {version_type} version from: {installer_path}")
    
    # Force close any running Jan instances first
    force_close_jan("Jan.exe")
    force_close_jan("Jan-nightly.exe")
    
    try:
        if installer_path.endswith('.exe'):
            # Windows installer
            subprocess.run([installer_path, '/S'], check=True)
        elif installer_path.endswith('.deb'):
            # Ubuntu installer
            subprocess.run(['sudo', 'dpkg', '-i', installer_path], check=True)
        elif installer_path.endswith('.dmg'):
            # macOS installer - need to mount and copy
            subprocess.run(['hdiutil', 'attach', installer_path], check=True)
            # This is simplified - actual implementation would need to handle dmg mounting
            
        logger.info(f"Successfully installed Jan {version_type} version")
        
        # Wait for installation to complete
        time.sleep(30)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Jan {version_type} version: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error installing Jan {version_type} version: {e}")
        raise

# Backup functionality removed as it's redundant for direct persistence testing

def prepare_migration_environment():
    """
    Prepare environment for migration testing
    """
    logger.info("Preparing migration test environment...")
    
    # Create migration logs directory
    migration_logs_dir = "migration_logs"
    os.makedirs(migration_logs_dir, exist_ok=True)
    
    # Create migration artifacts directory  
    migration_artifacts_dir = "migration_artifacts"
    os.makedirs(migration_artifacts_dir, exist_ok=True)
    
    return {
        "logs_dir": migration_logs_dir,
        "artifacts_dir": migration_artifacts_dir
    }
