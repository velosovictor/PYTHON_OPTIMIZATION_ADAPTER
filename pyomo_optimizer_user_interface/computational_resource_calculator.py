# ============================================================================
# COMPUTATIONAL RESOURCE CALCULATOR MODULE
# ============================================================================
# Estimates problem complexity and computational requirements before execution
# Provides early warning for resource-intensive problems

import math
import os
import psutil
from .parameters import get_parameter, get_all_parameters
from .equations import unknown_funcs, all_equations

# ============================================================================
# COMPLEXITY ESTIMATION FUNCTIONS
# ============================================================================

def estimate_problem_size():
    # Estimate the size and complexity of the optimization problem
    
    # Get parameters dynamically
    final_time = get_parameter("final_time")
    dt_value = get_parameter("dt_value")
    discrete_parameters = get_parameter("discrete_parameters") or []
    params_data = get_all_parameters()
    
    # Calculate time discretization
    time_steps = int(final_time / dt_value) + 1
    
    # Count variables
    state_variables = len(unknown_funcs) * time_steps
    optimization_variables = len(discrete_parameters) * time_steps if discrete_parameters else 0
    total_variables = state_variables + optimization_variables
    
    # Count constraints
    ode_constraints = len(all_equations) * (time_steps - 1)  # ODE discretization
    initial_constraints = len(unknown_funcs)  # Initial conditions
    
    # Estimate discrete logic constraints
    logic_constraints = 0
    discrete_logic = params_data.get("discrete_logic", {})
    if discrete_logic and discrete_logic.get("logic_constraints"):
        logic_count = len(discrete_logic["logic_constraints"])
        logic_constraints = logic_count * time_steps
    
    total_constraints = ode_constraints + initial_constraints + logic_constraints
    
    return {
        "time_steps": time_steps,
        "state_variables": state_variables,
        "optimization_variables": optimization_variables,
        "total_variables": total_variables,
        "total_constraints": total_constraints,
        "problem_density": total_constraints / max(total_variables, 1)
    }

def estimate_memory_requirements(problem_size):
    """Estimate memory requirements in MB"""
    
    # Base memory estimation (empirical formulas)
    variables = problem_size["total_variables"]
    constraints = problem_size["total_constraints"]
    
    # Pyomo model overhead
    pyomo_overhead = 50  # MB base overhead
    
    # Variable storage (each variable ~1KB in Pyomo)
    variable_memory = variables * 1e-3  # MB
    
    # Constraint storage (each constraint ~2KB)
    constraint_memory = constraints * 2e-3  # MB
    
    # Jacobian matrix (sparse, estimated 10% density)
    jacobian_memory = variables * constraints * 0.1 * 8e-9 * 1024  # MB (8 bytes per float)
    
    # SCIP solver overhead (depends on problem type)
    from pyomo_optimizer_user_interface.parameters import get_parameter
    minlp_enabled = get_parameter("minlp_enabled", False)
    solver_overhead = 100 if minlp_enabled else 50  # MB
    
    total_memory = pyomo_overhead + variable_memory + constraint_memory + jacobian_memory + solver_overhead
    
    return {
        "pyomo_overhead_mb": round(pyomo_overhead, 2),
        "variables_mb": round(variable_memory, 2),
        "constraints_mb": round(constraint_memory, 2),
        "jacobian_mb": round(jacobian_memory, 2),
        "solver_overhead_mb": round(solver_overhead, 2),
        "total_estimated_mb": round(total_memory, 2)
    }

def estimate_solve_time(problem_size):
    """Estimate solving time based on problem complexity"""
    
    variables = problem_size["total_variables"]
    constraints = problem_size["total_constraints"]
    params_data = get_all_parameters()
    discrete_parameters = get_parameter("discrete_parameters") or []
    minlp_enabled = params_data.get("minlp_enabled", False)
    
    # Base complexity factors (empirical)
    if minlp_enabled:
        # MINLP is exponential in discrete variables but polynomial in continuous
        discrete_vars = len(discrete_parameters) if discrete_parameters else 0
        base_complexity = variables**1.5 + 2**min(discrete_vars, 20)  # Cap exponential growth
    else:
        # NLP is roughly cubic in variables
        base_complexity = variables**2.5
    
    # Time estimation (very rough, depends on hardware)
    # Normalized to a reference problem: 100 vars, 100 constraints = ~1 second
    reference_complexity = 100**2.5
    estimated_seconds = (base_complexity / reference_complexity) * 1.0
    
    # Add constraint density penalty
    if problem_size["problem_density"] > 2.0:
        estimated_seconds *= 2.0  # Dense problems are harder
    
    return {
        "estimated_seconds": max(0.1, round(estimated_seconds, 2)),
        "complexity_class": get_complexity_class(variables, constraints, minlp_enabled)
    }

def get_complexity_class(variables, constraints, minlp_enabled):
    """Classify problem complexity for user guidance"""
    
    if minlp_enabled:
        if variables < 100:
            return "Small MINLP (< 1 minute)"
        elif variables < 500:
            return "Medium MINLP (1-10 minutes)"
        elif variables < 2000:
            return "Large MINLP (10-60 minutes)"
        else:
            return "Very Large MINLP (> 1 hour, consider problem reduction)"
    else:
        if variables < 1000:
            return "Small NLP (< 30 seconds)"
        elif variables < 5000:
            return "Medium NLP (30 seconds - 5 minutes)"
        elif variables < 20000:
            return "Large NLP (5-30 minutes)"
        else:
            return "Very Large NLP (> 30 minutes)"

def check_system_resources():
    """Check available system resources"""
    
    # Memory info
    memory = psutil.virtual_memory()
    available_memory_gb = memory.available / (1024**3)
    
    # CPU info
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    
    # Disk space (for temporary files)
    disk_usage = psutil.disk_usage('/')
    available_disk_gb = disk_usage.free / (1024**3)
    
    return {
        "available_memory_gb": round(available_memory_gb, 2),
        "total_memory_gb": round(memory.total / (1024**3), 2),
        "cpu_cores": cpu_count,
        "cpu_freq_ghz": round(cpu_freq.current / 1000, 2) if cpu_freq else "Unknown",
        "available_disk_gb": round(available_disk_gb, 2)
    }

def assess_feasibility(problem_size, memory_req, system_resources):
    """Assess if the problem is feasible given current resources"""
    
    params_data = get_all_parameters()
    discrete_parameters = get_parameter("discrete_parameters") or []
    
    warnings = []
    recommendations = []
    feasible = True
    
    # Memory check
    required_memory_gb = memory_req["total_estimated_mb"] / 1024
    if required_memory_gb > system_resources["available_memory_gb"] * 0.8:  # 80% safety margin
        warnings.append(f"⚠️  High memory usage: {required_memory_gb:.1f}GB required, {system_resources['available_memory_gb']:.1f}GB available")
        recommendations.append("Consider reducing time_steps or final_time")
        if required_memory_gb > system_resources["available_memory_gb"]:
            feasible = False
    
    # Variable count check
    if problem_size["total_variables"] > 50000:
        warnings.append("⚠️  Very large problem size (>50k variables)")
        recommendations.append("Consider problem decomposition or coarser discretization")
    
    # MINLP complexity check
    if params_data.get("minlp_enabled") and len(discrete_parameters or []) > 15:
        warnings.append("⚠️  High discrete variable count may cause exponential solve times")
        recommendations.append("Consider continuous relaxation or reformulation")
    
    # Dense problem check
    if problem_size["problem_density"] > 5.0:
        warnings.append("⚠️  Very dense constraint matrix detected")
        recommendations.append("Problem may benefit from sparse reformulation")
    
    return {
        "feasible": feasible,
        "warnings": warnings,
        "recommendations": recommendations
    }

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_computational_requirements():
    """Complete computational resource analysis"""
    
    print("\n" + "🔬" * 60)
    print("COMPUTATIONAL RESOURCE ANALYSIS")
    print("🔬" * 60)
    
    # Problem size estimation
    problem_size = estimate_problem_size()
    print(f"\n📊 PROBLEM SIZE ESTIMATION:")
    print(f"   Time steps: {problem_size['time_steps']}")
    print(f"   State variables: {problem_size['state_variables']}")
    print(f"   Optimization variables: {problem_size['optimization_variables']}")
    print(f"   Total variables: {problem_size['total_variables']}")
    print(f"   Total constraints: {problem_size['total_constraints']}")
    print(f"   Problem density: {problem_size['problem_density']:.2f}")
    
    # Memory estimation
    memory_req = estimate_memory_requirements(problem_size)
    print(f"\n💾 MEMORY REQUIREMENTS:")
    print(f"   Pyomo overhead: {memory_req['pyomo_overhead_mb']} MB")
    print(f"   Variables: {memory_req['variables_mb']} MB")
    print(f"   Constraints: {memory_req['constraints_mb']} MB")
    print(f"   Jacobian matrix: {memory_req['jacobian_mb']} MB")
    print(f"   Solver overhead: {memory_req['solver_overhead_mb']} MB")
    print(f"   📈 TOTAL ESTIMATED: {memory_req['total_estimated_mb']} MB ({memory_req['total_estimated_mb']/1024:.2f} GB)")
    
    # Time estimation
    solve_time = estimate_solve_time(problem_size)
    print(f"\n⏱️  SOLVE TIME ESTIMATION:")
    print(f"   Estimated time: {solve_time['estimated_seconds']} seconds")
    print(f"   Complexity class: {solve_time['complexity_class']}")
    
    # System resources
    system_resources = check_system_resources()
    print(f"\n🖥️  SYSTEM RESOURCES:")
    print(f"   Available memory: {system_resources['available_memory_gb']:.2f} GB / {system_resources['total_memory_gb']:.2f} GB")
    print(f"   CPU cores: {system_resources['cpu_cores']}")
    print(f"   CPU frequency: {system_resources['cpu_freq_ghz']} GHz")
    print(f"   Available disk: {system_resources['available_disk_gb']:.1f} GB")
    
    # Feasibility assessment
    assessment = assess_feasibility(problem_size, memory_req, system_resources)
    
    print(f"\n🎯 FEASIBILITY ASSESSMENT:")
    if assessment["feasible"]:
        print("   ✅ Problem appears computationally feasible")
    else:
        print("   ❌ Problem may exceed available resources")
    
    if assessment["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        for warning in assessment["warnings"]:
            print(f"   {warning}")
    
    if assessment["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in assessment["recommendations"]:
            print(f"   • {rec}")
    
    print("\n" + "🔬" * 60)
    
    return {
        "problem_size": problem_size,
        "memory_requirements": memory_req,
        "solve_time": solve_time,
        "system_resources": system_resources,
        "assessment": assessment
    }

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_feasibility_check():
    """Quick yes/no feasibility check"""
    analysis = analyze_computational_requirements()
    return analysis["assessment"]["feasible"]

def get_resource_summary():
    """Get a brief resource summary"""
    problem_size = estimate_problem_size()
    memory_req = estimate_memory_requirements(problem_size)
    
    return {
        "variables": problem_size["total_variables"],
        "constraints": problem_size["total_constraints"],
        "memory_mb": memory_req["total_estimated_mb"],
        "feasible": quick_feasibility_check()
    }
