"""
Dynamic Data Loader - Problem Agnostic

This module handles dynamic loading of user-specific data including:
- lookup.py (user's custom lookup tables)
- object_data.json (problem parameters)

The library remains completely problem-agnostic by loading everything dynamically.
"""

import os
import sys
import importlib.util
import json
from typing import Dict, Any, Optional

class DynamicDataLoader:
    """Dynamically loads user data from specified folder"""
    
    def __init__(self, data_folder: str = None):
        self.data_folder = data_folder
        self.lookup_tables = None
        self._user_module = None
    
    def load_lookup_tables(self) -> Dict[str, Any]:
        """Load lookup tables from user's lookup.py file"""
        if self.lookup_tables is not None:
            return self.lookup_tables
        
        if not self.data_folder:
            # Return empty lookup tables if no data folder specified
            self.lookup_tables = {}
            return self.lookup_tables
        
        lookup_file = os.path.join(self.data_folder, "lookup.py")
        
        if not os.path.exists(lookup_file):
            print(f"⚠️  Warning: No lookup.py found in {self.data_folder}")
            self.lookup_tables = {}
            return self.lookup_tables
        
        try:
            # Dynamic import of user's lookup.py
            spec = importlib.util.spec_from_file_location("user_lookup", lookup_file)
            user_lookup_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_lookup_module)
            
            # Get lookup_tables from the user's module
            if hasattr(user_lookup_module, 'lookup_tables'):
                self.lookup_tables = user_lookup_module.lookup_tables
                print(f"✅ Loaded lookup tables from {lookup_file}")
            else:
                print(f"⚠️  Warning: No 'lookup_tables' found in {lookup_file}")
                self.lookup_tables = {}
                
        except Exception as e:
            print(f"❌ Error loading lookup tables from {lookup_file}: {e}")
            self.lookup_tables = {}
        
        return self.lookup_tables
    
    def get_lookup_value(self, table_name: str, key: Any) -> Any:
        """Get value from a specific lookup table"""
        tables = self.load_lookup_tables()
        
        if table_name not in tables:
            raise KeyError(f"Lookup table '{table_name}' not found in user data")
        
        if key not in tables[table_name]:
            raise KeyError(f"Key '{key}' not found in lookup table '{table_name}'")
        
        return tables[table_name][key]

# Global loader instance (will be initialized when data folder is set)
_global_loader: Optional[DynamicDataLoader] = None

def initialize_dynamic_loader(data_folder: str = None):
    """Initialize the global dynamic loader with user's data folder"""
    global _global_loader
    _global_loader = DynamicDataLoader(data_folder)
    return _global_loader

def get_lookup_tables() -> Dict[str, Any]:
    """Get lookup tables from the global loader"""
    if _global_loader is None:
        raise RuntimeError("Dynamic loader not initialized. Call initialize_dynamic_loader() first.")
    return _global_loader.load_lookup_tables()

def get_lookup_value(table_name: str, key: Any) -> Any:
    """Get value from lookup table using global loader"""
    if _global_loader is None:
        raise RuntimeError("Dynamic loader not initialized. Call initialize_dynamic_loader() first.")
    return _global_loader.get_lookup_value(table_name, key)
