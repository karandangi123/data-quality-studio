import importlib
import inspect
import pkgutil
from typing import List

from detectors.base import BaseDetector, Issue
import detectors

class DataProfiler:
    """
    The Profiler Engine orchestrates all detectors.
    It automatically discovers any detector inside the `detectors` folder that inherits from BaseDetector.
    """
    def __init__(self):
        self.detectors = self._load_detectors()
        
    def _load_detectors(self) -> List[BaseDetector]:
        """
        Dynamically loads all plugins (Detectors) from the detectors package.
        This allows new issue types to be added just by adding a new file.
        """
        loaded_detectors = []
        # Iterate over all modules in the detectors package
        for _, module_name, _ in pkgutil.iter_modules(detectors.__path__):
            # We skip base because it's just the abstract class
            if module_name == 'base':
                continue
            
            # Import the module dynamically
            module = importlib.import_module(f"detectors.{module_name}")
            
            # Find all classes in the module that inherit from BaseDetector
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseDetector) and obj is not BaseDetector:
                    loaded_detectors.append(obj())
                    
        return loaded_detectors

    def profile(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        """
        Runs all loaded detectors against the data.
        """
        all_issues = []
        for detector in self.detectors:
            # Each detector returns a list of Issue objects
            issues = detector.detect(conn, raw_table, ref_table)
            all_issues.extend(issues)
            
        return all_issues
