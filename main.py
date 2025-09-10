#!/usr/bin/env python3
"""
PYOMO OPTIMIZER USER INTERFACE
Main entry point for running optimization problems.

Usage:
    python main.py [data_folder]
    
Where data_folder contains object_data.json and lookup.py files.
If not specified, uses the user_data_example folder.
"""

import sys
import os
from pyomo_optimizer_user_interface.main import run
from pyomo_optimizer_user_interface.computational_resource_calculator import analyze_computational_requirements

if __name__ == "__main__":
    print("🚀 Starting Pyomo Optimizer User Interface...")
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
        print(f"📁 Using specified data folder: {data_folder}")
    else:
        # Default to the example folder in the repo
        data_folder = os.path.join(os.path.dirname(__file__), "user_data_example")
        print(f"📁 Using default example data folder: {data_folder}")
    
    # Verify data folder exists
    if not os.path.exists(data_folder):
        print(f"❌ Error: Data folder not found: {data_folder}")
        print("\n💡 Usage:")
        print("   python main.py [data_folder]")
        print(f"   python main.py \"{os.path.join(os.path.dirname(__file__), 'user_data_example')}\"")
        sys.exit(1)
    
    # Perform computational resource analysis first
    print("\n🔬 Analyzing computational requirements...")
    resource_analysis = analyze_computational_requirements()
    
    # Check if problem is feasible
    if resource_analysis["assessment"]["feasible"]:
        print("\n✅ Proceeding with optimization...")
        run(data_folder)
    else:
        print("\n❌ Problem may exceed available resources!")
        print("Consider the recommendations above before proceeding.")
        
        user_input = input("\nDo you want to proceed anyway? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            print("⚠️  Proceeding at user's discretion...")
            run(data_folder)
        else:
            print("👋 Optimization cancelled. Please adjust your problem configuration.")
