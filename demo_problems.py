#!/usr/bin/env python3
# ============================================================================
# PROBLEM DEMO SCRIPT
# ============================================================================
# Interactive script to demonstrate the constraint theory with two examples

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyomo_interface_tool.problem_selector import interactive_problem_selection, select_problem
from pyomo_interface_tool.main import run

def main():
    print("🚀 CONSTRAINT THEORY DEMONSTRATION")
    print("=" * 50)
    
    # Let user select a problem
    if interactive_problem_selection():
        print("\n🏃 Running the selected problem...")
        print("=" * 50)
        
        # Run the main simulation
        try:
            run()
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            print("\nThis might be expected if the problem is infeasible or needs different solver settings.")
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
