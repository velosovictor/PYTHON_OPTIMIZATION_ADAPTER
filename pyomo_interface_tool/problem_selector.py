# ============================================================================
# PROBLEM SELECTOR MODULE
# ============================================================================
# Allows user to select between different example problems to demonstrate
# the constraint theory: fully constrained vs under-constrained systems

import os
import json
import shutil

# ============================================================================
# PROBLEM DEFINITIONS
# ============================================================================
PROBLEMS = {
    "1": {
        "name": "Fully Constrained System",
        "file": "problem1_fully_constrained.json",
        "description": "Logic constraints determine k_eff completely. Degrees of Freedom = 0.",
        "theory": "Parameters = Restrictions → Unique solution exists"
    },
    "2": {
        "name": "Under-Constrained Optimization Problem", 
        "file": "problem2_optimization.json",
        "description": "No logic constraints, endpoint targets, need optimization. Degrees of Freedom > 0.",
        "theory": "Parameters > Restrictions → Multiple solutions, need optimization to pick best"
    }
}

# ============================================================================
# PROBLEM SELECTION FUNCTIONS
# ============================================================================
def list_available_problems():
    # Display all available example problems
    print("=" * 80)
    print("AVAILABLE EXAMPLE PROBLEMS")
    print("=" * 80)
    
    for key, problem in PROBLEMS.items():
        print(f"\n{key}. {problem['name']}")
        print(f"   Description: {problem['description']}")
        print(f"   Theory: {problem['theory']}")
    print("\n" + "=" * 80)

def select_problem(problem_number=None):
    # Select and load a specific problem configuration
    
    if problem_number is None:
        list_available_problems()
        problem_number = input("Select problem number (1 or 2): ").strip()
    
    if problem_number not in PROBLEMS:
        print(f"Invalid problem number: {problem_number}")
        return False
    
    problem = PROBLEMS[problem_number]
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    problems_dir = os.path.join(current_dir, "user_data", "problems")
    source_file = os.path.join(problems_dir, problem["file"])
    target_file = os.path.join(current_dir, "user_data", "object_data.json")
    
    # Copy selected problem to main config
    try:
        shutil.copy2(source_file, target_file)
        print(f"\n✅ Loaded: {problem['name']}")
        print(f"📝 {problem['description']}")
        print(f"🎯 Theory: {problem['theory']}")
        return True
    except Exception as e:
        print(f"❌ Error loading problem: {e}")
        return False

def get_current_problem_info():
    # Analyze the currently loaded problem
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "user_data", "object_data.json")
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        minlp_enabled = config.get("minlp_enabled", False)
        has_optimization = config.get("optimization", {}).get("enabled", False)
        
        if minlp_enabled and not has_optimization:
            return "1", "Fully Constrained (Logic constraints active)"
        elif not minlp_enabled and has_optimization:
            return "2", "Under-Constrained Optimization"
        else:
            return "?", "Custom configuration"
    
    except Exception as e:
        return "?", f"Error reading config: {e}"

# ============================================================================
# INTERACTIVE PROBLEM SELECTION
# ============================================================================
def interactive_problem_selection():
    # Interactive problem selection with theory explanation
    
    print("\n" + "🎯" * 40)
    print("CONSTRAINT THEORY DEMONSTRATION")
    print("🎯" * 40)
    
    print("\nAccording to your theory:")
    print("• If Parameters = Restrictions → Fully Constrained (unique solution)")
    print("• If Parameters > Restrictions → Under-Constrained (need optimization)")
    print("• If Parameters < Restrictions → Over-Constrained (may be infeasible)")
    
    list_available_problems()
    
    while True:
        choice = input("\nSelect problem (1, 2, or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            return False
        elif choice in PROBLEMS:
            success = select_problem(choice)
            if success:
                return True
        else:
            print("Invalid choice. Please enter 1, 2, or 'q'.")

if __name__ == "__main__":
    interactive_problem_selection()
