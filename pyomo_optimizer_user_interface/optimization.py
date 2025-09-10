# ============================================================================
# TENSOR-BASED OPTIMIZATION - MINIMAL CORE
# ============================================================================
# Pure innovation: "sum(x**2)" -> Pyomo objective
# Your core idea: find optimal tensor A by tuning parameters B

import re
from pyomo.environ import Objective, minimize, maximize

def add_optimization_objective(model, optimization_config):
    """Core function: Convert tensor expression to Pyomo objective"""
    
    if not optimization_config.get("enabled", False):
        model.obj = Objective(expr=0, sense=minimize)
        return
    
    # Extract user's tensor expression
    target_expr = optimization_config.get("target_expression")
    obj_type = optimization_config.get("objective_type", "minimize")
    
    if not target_expr:
        model.obj = Objective(expr=0, sense=minimize)
        return
    
    # THE CORE INNOVATION: Parse natural language to Pyomo
    obj_expr = parse_tensor_expression(target_expr, model)
    
    # Create Pyomo objective
    sense = minimize if obj_type == "minimize" else maximize
    model.obj = Objective(expr=obj_expr, sense=sense)

def parse_tensor_expression(expr_str, model):
    """THE CORE: Convert 'sum(x**2)' to Pyomo expression"""
    
    # Handle sum(x**2), sum(abs(x)), sum(x)
    if 'sum(' in expr_str:
        return parse_sum_expression(expr_str, model)
    
    # Handle x[0], x[-1] 
    if '[' in expr_str:
        return parse_point_expression(expr_str, model)
    
    # Default: quadratic sum for bare variable name
    var_name = expr_str.strip()
    if hasattr(model, var_name):
        return sum(getattr(model, var_name)[t]**2 for t in model.T)
    
    return 0

def parse_sum_expression(expr_str, model):
    """Parse sum(...) expressions"""
    
    # Extract content inside sum(...)
    match = re.search(r'sum\(([^)]+)\)', expr_str)
    if not match:
        return 0
    
    inner = match.group(1).strip()
    
    # sum(x**2) -> quadratic sum
    if '**2' in inner:
        var_name = inner.replace('**2', '').strip()
        if hasattr(model, var_name):
            return sum(getattr(model, var_name)[t]**2 for t in model.T)
    
    # sum(abs(x)) -> use x**2 (Pyomo-friendly approximation)
    elif 'abs(' in inner:
        abs_match = re.search(r'abs\(([^)]+)\)', inner)
        if abs_match:
            var_name = abs_match.group(1)
            if hasattr(model, var_name):
                return sum(getattr(model, var_name)[t]**2 for t in model.T)
    
    # sum(x) -> linear sum
    else:
        if hasattr(model, inner):
            return sum(getattr(model, inner)[t] for t in model.T)
    
    return 0

def parse_point_expression(expr_str, model):
    """Parse x[0], x[-1] expressions"""
    
    match = re.search(r'([a-zA-Z_]\w*)\[([^\]]+)\]', expr_str)
    if not match:
        return 0
    
    var_name = match.group(1)
    index_str = match.group(2)
    
    if hasattr(model, var_name):
        var_obj = getattr(model, var_name)
        T_list = list(model.T)
        
        # Handle -1 (final), 0 (initial), or specific index
        if index_str == '-1':
            return var_obj[T_list[-1]]
        elif index_str == '0':
            return var_obj[T_list[0]]
        else:
            try:
                idx = int(index_str)
                return var_obj[T_list[idx]] if idx < len(T_list) else var_obj[T_list[-1]]
            except:
                return var_obj[T_list[-1]]
    
    return 0

def analyze_optimization_results(model, optimization_config):
    """Simple results display"""
    
    if not optimization_config.get("enabled", False):
        return
    
    from pyomo.environ import value
    
    try:
        obj_value = value(model.obj)
        target_expr = optimization_config.get("target_expression", "objective")
        obj_type = optimization_config.get("objective_type", "minimize")
        
        print(f"\n🎯 OPTIMIZATION COMPLETE:")
        print(f"   {obj_type.capitalize()} {target_expr}: {obj_value:.6f}")
        
        # Show tuning variables
        tuning_vars = optimization_config.get("tuning_variables", [])
        if tuning_vars:
            print(f"   Tuning variables: {tuning_vars}")
            
    except Exception as e:
        print(f"   Could not display results: {e}")
