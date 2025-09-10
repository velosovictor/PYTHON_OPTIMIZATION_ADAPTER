#!/usr/bin/env python3
"""
PYOMO OPTIMIZER USER INTERFACE
Main entry point for running optimization problems.
"""

from pyomo_optimizer_user_interface.main import run
from pyomo_optimizer_user_interface.computational_resource_calculator import analyze_computational_requirements

if __name__ == "__main__":
    print("🚀 Starting Pyomo Optimizer User Interface...")
    
    # Perform computational resource analysis first
    print("\n🔬 Analyzing computational requirements...")
    resource_analysis = analyze_computational_requirements()
    
    # Check if problem is feasible
    if resource_analysis["assessment"]["feasible"]:
        print("\n✅ Proceeding with optimization...")
        run()
    else:
        print("\n❌ Problem may exceed available resources!")
        print("Consider the recommendations above before proceeding.")
        
        user_input = input("\nDo you want to proceed anyway? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            print("⚠️  Proceeding at user's discretion...")
            run()
        else:
            print("👋 Optimization cancelled. Please adjust your problem configuration.")
