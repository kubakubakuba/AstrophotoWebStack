import os
import shutil
import logging

class StackingDirectoryManager:
    """
    Manages copying files to a fast stacking directory (e.g., SSD) for faster stacking operations
    """
    
    def __init__(self, stacking_dir=None):
        self.stacking_dir = stacking_dir
        self.project_dir = None
        self.logger = logging.getLogger(__name__)
        
    def is_enabled(self):
        """Check if stacking directory is properly configured"""
        if self.stacking_dir is None or self.stacking_dir.strip() == "":
            self.logger.error("STACKING_DIRECTORY must be set - stacking directory is required for proper operation")
            return False
        return True
    
    def setup_project_directory(self, project_name):
        """Create project directory in the stacking location"""
        if not self.is_enabled():
            return None
            
        try:
            # Ensure stacking directory exists
            os.makedirs(self.stacking_dir, exist_ok=True)
            
            # Create project-specific directory
            self.project_dir = os.path.join(self.stacking_dir, project_name)
            os.makedirs(self.project_dir, exist_ok=True)
            
            self.logger.info(f"Created stacking directory: {self.project_dir}")
            return self.project_dir
            
        except Exception as e:
            self.logger.error(f"Failed to create stacking directory: {e}")
            return None
    
    def copy_folder_to_stacking_dir(self, source_folder, folder_name):
        """Copy a folder to stacking directory and return the new path"""
        if not self.is_enabled() or not self.project_dir:
            return source_folder
            
        if not os.path.exists(source_folder):
            self.logger.warning(f"Source folder does not exist: {source_folder}")
            return source_folder
            
        try:
            dest_folder = os.path.join(self.project_dir, folder_name)
            
            self.logger.info(f"Copying {source_folder} to stacking directory at {dest_folder}")
            shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
            
            self.logger.info(f"Successfully copied {folder_name} to stacking directory")
            return dest_folder
            
        except Exception as e:
            self.logger.error(f"Failed to copy {folder_name} to stacking directory: {e}")
            return source_folder
    
    def cleanup_intermediate_files(self, project_dir, folders_to_clean):
        """Clean up source files and processing folder, keep only final results and previews"""
        if not self.is_enabled() or not project_dir:
            return
            
        try:
            # Clean up source folders
            for folder_name in folders_to_clean:
                folder_path = os.path.join(project_dir, folder_name)
                if os.path.exists(folder_path):
                    self.logger.info(f"Cleaning up source files from {folder_path}")
                    shutil.rmtree(folder_path)
                    self.logger.info(f"Removed source folder: {folder_name}")
            
            # Also clean up the process folder (intermediate files)
            process_folder = os.path.join(project_dir, "process")
            if os.path.exists(process_folder):
                self.logger.info(f"Cleaning up processing files from {process_folder}")
                shutil.rmtree(process_folder)
                self.logger.info("Removed process folder")
            
            self.logger.info("Cleanup completed - only final results and previews preserved")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup files: {e}")
