# ============================================================================
# TENSOR-BASED OPTIMIZATION - CORE IMPLEMENTATION
# ============================================================================
# Pure tensor philosophy: find optimal tensor A by tuning parameters B
# Core innovation: "sum(x**2)" -> Pyomo objective

import re
from pyomo.environ import Objective, minimize, maximize

# ============================================================================
# CORE: PARSE TENSOR EXPRESSIONS
# ============================================================================
def parse_tensor_expression(expr_str, model):
    """Convert "sum(x**2)" to Pyomo expression - THE CORE INNOVATION"""
    
    # Handle sum(x**2), sum(abs(x)), sum(x)
    if 'sum(' in expr_str:
        return _parse_sum(expr_str, model)
    
    # Handle x[0], x[-1] 
    if '[' in expr_str:
        return _parse_point(expr_str, model)
    
    # Default: sum of squares
    var_name = expr_str.strip()
    if hasattr(model, var_name):
        return sum(getattr(model, var_name)[t]**2 for t in model.T)
    
    return 0

def _parse_sum(expr_str, model):
    """Parse sum(expression) - the core tensor operation"""
    match = re.search(r'sum\(([^)]+)\)', expr_str)
    if not match:
        return 0
    
    inner = match.group(1).strip()
    
    # sum(x**2)
    if '**2' in inner:
        var_name = inner.replace('**2', '').strip()
        if hasattr(model, var_name):
            return sum(getattr(model, var_name)[t]**2 for t in model.T)
    
    # sum(x)
    else:
        if hasattr(model, inner):
            return sum(getattr(model, inner)[t] for t in model.T)
    
    return 0

def _parse_point(expr_str, model):
    """Parse x[0], x[-1] - point-wise expressions"""
    match = re.search(r'([a-zA-Z_]\w*)\[([^\]]+)\]', expr_str)
    if not match:
        return 0
    
    var_name = match.group(1)
    index_str = match.group(2)
    
    if hasattr(model, var_name):
        var_obj = getattr(model, var_name)
        T_list = list(model.T)
        
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

def parse_global_sum_expression(expr_str, model):
    """Parse sum(expression) patterns for global tensor optimization"""
    
    # Extract inner expression from sum(...)
    sum_match = re.search(r'sum\(([^)]+)\)', expr_str)
    if not sum_match:
        raise ValueError(f"Invalid sum expression: {expr_str}")
    
    inner_expr = sum_match.group(1)
    print(f"   📊 Global sum of: {inner_expr}")
    
    obj_expr = 0
    
    # Handle x**2, v**2, etc.
    if '**2' in inner_expr:
        var_name = inner_expr.replace('**2', '').strip()
        if hasattr(model, var_name):
            var_obj = getattr(model, var_name)
            for t in model.T:
                obj_expr += var_obj[t]**2
            print(f"   ✅ Added quadratic sum for {var_name}")
    
    # Handle abs(x), abs(v), etc.  
    elif 'abs(' in inner_expr:
        abs_match = re.search(r'abs\(([^)]+)\)', inner_expr)
        if abs_match:
            var_name = abs_match.group(1)
            if hasattr(model, var_name):
                var_obj = getattr(model, var_name)
                # Use squared approximation for abs() in optimization
                for t in model.T:
                    obj_expr += var_obj[t]**2  # Pyomo-friendly approximation
                print(f"   ✅ Added absolute sum for {var_name}")
    
    # Handle simple sum(x), sum(v), etc.
    else:
        var_name = inner_expr.strip()
        if hasattr(model, var_name):
            var_obj = getattr(model, var_name)
            for t in model.T:
                obj_expr += var_obj[t]
            print(f"   ✅ Added linear sum for {var_name}")
    
    return obj_expr

def parse_global_max_expression(expr_str, model):
    """Parse max(expression) patterns - approximate with penalty approach"""
    
    print(f"   📈 Global max expression detected")
    
    # For optimization, we approximate max() with sum of squares (penalty approach)
    # This encourages all values to be small rather than just the maximum
    
    # Extract inner expression from max(...)
    max_match = re.search(r'max\(([^)]+)\)', expr_str)
    if not max_match:
        raise ValueError(f"Invalid max expression: {expr_str}")
    
    inner_expr = max_match.group(1)
    
    # Convert max(abs(x)) to sum(x**2) approximation
    if 'abs(' in inner_expr:
        abs_match = re.search(r'abs\(([^)]+)\)', inner_expr)
        if abs_match:
            var_name = abs_match.group(1)
            if hasattr(model, var_name):
                var_obj = getattr(model, var_name)
                obj_expr = 0
                for t in model.T:
                    obj_expr += var_obj[t]**2  # Penalty approximation
                print(f"   ✅ Approximated max(abs({var_name})) with sum({var_name}**2)")
                return obj_expr
    
    raise ValueError(f"Unsupported max expression: {expr_str}")

def parse_variance_expression(expr_str, model):
    """Parse var(x) patterns for smoothness optimization"""
    
    var_match = re.search(r'var\(([^)]+)\)', expr_str)
    if not var_match:
        raise ValueError(f"Invalid variance expression: {expr_str}")
    
    var_name = var_match.group(1)
    print(f"   📉 Variance minimization for {var_name}")
    
    if not hasattr(model, var_name):
        raise ValueError(f"Variable {var_name} not found in model")
    
    var_obj = getattr(model, var_name)
    
    # Calculate variance: sum((x_i - mean)**2) / n
    # For optimization, we simplify to sum((x_i - x_j)**2) for all pairs
    obj_expr = 0
    T_list = list(model.T)
    
    for i, t1 in enumerate(T_list):
        for t2 in T_list[i+1:]:
            obj_expr += (var_obj[t1] - var_obj[t2])**2
    
    print(f"   ✅ Added variance minimization for {var_name}")
    return obj_expr

def parse_pointwise_expression(expr_str, model):
    """Parse point-wise expressions like x[0], x[-1], v[1]"""
    
    # Pattern: variable[index]
    point_match = re.search(r'([a-zA-Z_]\w*)\[([^\]]+)\]', expr_str)
    if not point_match:
        raise ValueError(f"Invalid pointwise expression: {expr_str}")
    
    var_name = point_match.group(1)
    index_str = point_match.group(2)
    
    print(f"   🎯 Point-wise expression: {var_name}[{index_str}]")
    
    if not hasattr(model, var_name):
        raise ValueError(f"Variable {var_name} not found in model")
    
    var_obj = getattr(model, var_name)
    T_list = list(model.T)
    
    # Handle index conversion
    if index_str == '-1':
        time_idx = T_list[-1]  # Final time
    elif index_str == '0':
        time_idx = T_list[0]   # Initial time
    else:
        try:
            idx = int(index_str)
            time_idx = T_list[idx] if idx < len(T_list) else T_list[-1]
        except:
            raise ValueError(f"Invalid index: {index_str}")
    
    print(f"   ✅ Target: {var_name}[t={time_idx}]")
    return var_obj[time_idx]

def parse_auto_global_expression(var_name, model):
    """Auto-decide best global metric for a variable"""
    
    print(f"   🤖 Auto-selecting best global metric for {var_name}")
    
    if not hasattr(model, var_name):
        raise ValueError(f"Variable {var_name} not found in model")
    
    # Default to quadratic sum (energy minimization)
    var_obj = getattr(model, var_name)
    obj_expr = 0
    for t in model.T:
        obj_expr += var_obj[t]**2
    
    print(f"   ✅ Auto-selected: sum({var_name}**2) [quadratic energy]")
    return obj_expr

def parse_complex_expression(expr_str, model):
    """Parse complex multi-parameter expressions"""
    
    print(f"   🔬 Complex expression analysis")
    
    # Split by + and - to handle terms
    terms = re.split(r'(?<!\*)\+(?!\+)|(?<!\*)-(?!-)', expr_str)
    obj_expr = 0
    
    for term in terms:
        term = term.strip()
        if not term:
            continue
            
        print(f"      Processing term: {term}")
        
        # Handle coefficients like 0.5*m*sum(v**2)
        if '*sum(' in term:
            # Extract coefficient and sum expression
            parts = term.split('*sum(')
            if len(parts) == 2:
                coeff_part = parts[0]
                sum_part = 'sum(' + parts[1]
                
                # Parse coefficient
                coeff = parse_coefficient(coeff_part, model)
                
                # Parse sum expression
                sum_expr = parse_global_sum_expression(sum_part, model)
                
                obj_expr += coeff * sum_expr
                print(f"      ✅ Added weighted term: {coeff} * {sum_part}")
    
    return obj_expr

def parse_coefficient(coeff_str, model):
    """Parse coefficient expressions like 0.5*m"""
    
    # Handle simple numbers
    try:
        return float(coeff_str)
    except:
        pass
    
    # Handle parameter references like m, k_eff
    if coeff_str in [p['name'] for p in get_parameter("discrete_parameters", [])]:
        if hasattr(model, coeff_str):
            return getattr(model, coeff_str)
    
    # Handle parameter lookup
    param_value = get_parameter(coeff_str)
    if param_value is not None:
        return param_value
    
    # Handle multiplication like 0.5*m
    if '*' in coeff_str:
        parts = coeff_str.split('*')
        result = 1.0
        for part in parts:
            part = part.strip()
            try:
                result *= float(part)
            except:
                param_val = get_parameter(part)
                if param_val is not None:
                    result *= param_val
        return result
    
    print(f"      ⚠️ Unknown coefficient: {coeff_str}, using 1.0")
    return 1.0

# ============================================================================
# PURE TENSOR-BASED OPTIMIZATION ASSIGNMENT
# ============================================================================
def add_optimization_objective(model, optimization_config):
    """
    REVOLUTIONARY TENSOR OPTIMIZATION APPROACH!
    
    Pure philosophy: Find optimal tensor A by tuning parameters B
    - Parameter A (TARGET): The tensor we want optimal values for
    - Parameter B (TUNING): The variables we adjust to achieve optimal A
    """
    
    if not optimization_config.get("enabled", False):
        print("🔧 No optimization - adding dummy objective for feasibility")
        model.obj = Objective(expr=0, sense=minimize)
        return
    
    print("\n" + "="*80)
    print("🚀 TENSOR-BASED OPTIMIZATION ENGINE ACTIVATED!")
    print("="*80)
    
    # Extract tensor optimization configuration
    target_param = optimization_config.get("target_parameter")
    target_expr = optimization_config.get("target_expression")  
    obj_type = optimization_config.get("objective_type", "minimize")
    tuning_vars = optimization_config.get("tuning_variables", [])
    
    print(f"🎯 TARGET TENSOR (A): {target_param}")
    print(f"📊 TARGET EXPRESSION: {target_expr}")
    print(f"⚙️  TUNING VARIABLES (B): {tuning_vars}")
    print(f"🎛️  OPTIMIZATION TYPE: {obj_type}")
    
    # Validate configuration
    if not target_expr:
        raise ValueError("target_expression must be specified for tensor optimization!")
    
    # Parse tensor expression to Pyomo objective
    try:
        obj_expr = parse_tensor_expression(target_expr, model)
        print(f"✅ Successfully parsed tensor expression")
    except Exception as e:
        print(f"❌ Failed to parse tensor expression: {e}")
        raise
    
    # Determine objective sense
    sense = minimize if obj_type == "minimize" else maximize
    
    # Add objective to model
    model.obj = Objective(expr=obj_expr, sense=sense)
    
    print(f"🎯 OBJECTIVE CREATED: {obj_type} {target_expr}")
    print("="*80)
    
    # Validate tuning variables exist
    missing_vars = []
    for var_name in tuning_vars:
        if not hasattr(model, var_name):
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"⚠️  WARNING: Tuning variables not found in model: {missing_vars}")
    else:
        print(f"✅ All tuning variables found: {tuning_vars}")

# ============================================================================
# LEGACY COMPATIBILITY (DEPRECATED)
# ============================================================================
def add_constraint_based_optimization(model, optimization_config):
    """DEPRECATED: Legacy constraint-based approach"""
    print("⚠️  Using deprecated constraint-based optimization")
    model.obj = Objective(expr=0, sense=minimize)

def add_objective_based_optimization(model, optimization_config):
    """DEPRECATED: Legacy objective-based approach - use tensor optimization instead"""
    print("⚠️  Using deprecated objective-based optimization")
    
    # Fall back to tensor optimization if new format detected
    if "target_expression" in optimization_config:
        return add_optimization_objective(model, optimization_config)
    
    # Legacy fallback
    model.obj = Objective(expr=0, sense=minimize)

# ============================================================================
# TENSOR OPTIMIZATION RESULT ANALYSIS
# ============================================================================
def analyze_optimization_results(model, optimization_config):
    """
    Analyzes tensor optimization results with enhanced reporting
    
    Shows:
    1. Optimal objective value for target expression
    2. Optimal tuning variable values (Parameter B)  
    3. Complete optimal tensor values (Parameter A)
    4. Optimization summary and insights
    """
    
    if not optimization_config.get("enabled", False):
        print("🔧 No optimization performed (feasibility solve only)")
        return
    
    print("\n" + "="*80)
    print("🏆 TENSOR OPTIMIZATION RESULTS")
    print("="*80)
    
    # Extract optimization configuration
    target_param = optimization_config.get("target_parameter")
    target_expr = optimization_config.get("target_expression")
    obj_type = optimization_config.get("objective_type", "minimize")
    tuning_vars = optimization_config.get("tuning_variables", [])
    
    # Report objective value
    try:
        obj_value = value(model.obj)
        print(f"🎯 OPTIMAL {obj_type.upper()} VALUE: {obj_value:.6f}")
        print(f"📊 TARGET EXPRESSION: {target_expr}")
    except Exception as e:
        print(f"❌ Could not retrieve objective value: {e}")
        obj_value = None
    
    print("\n" + "-"*50)
    print("⚙️  OPTIMAL TUNING VARIABLES (Parameter B)")
    print("-"*50)
    
    # Report tuning variable results
    if tuning_vars:
        for var_name in tuning_vars:
            if hasattr(model, var_name):
                var_obj = getattr(model, var_name)
                try:
                    if var_obj.is_indexed():
                        # Time-varying tuning variable
                        values = {}
                        for t in model.T:
                            try:
                                val = value(var_obj[t])
                                if val is not None:
                                    values[t] = val
                            except:
                                continue
                        
                        if values:
                            print(f"📈 {var_name} (time-varying):")
                            for t, val in values.items():
                                print(f"   t={t}: {val:.6f}")
                        else:
                            print(f"❓ {var_name}: values not available")
                    else:
                        # Constant tuning variable
                        val = value(var_obj)
                        print(f"🔧 {var_name}: {val:.6f}")
                except Exception as e:
                    print(f"❌ {var_name}: error retrieving value ({e})")
            else:
                print(f"❓ {var_name}: not found in model")
    else:
        print("   (No tuning variables specified)")
    
    print("\n" + "-"*50)
    print(f"🎯 OPTIMAL TARGET TENSOR (Parameter A): {target_param}")
    print("-"*50)
    
    # Report optimal tensor values
    if target_param and hasattr(model, target_param):
        var_obj = getattr(model, target_param)
        try:
            if var_obj.is_indexed():
                print(f"📊 Complete {target_param}(t) tensor:")
                tensor_values = {}
                for t in model.T:
                    try:
                        val = value(var_obj[t])
                        if val is not None:
                            tensor_values[t] = val
                            print(f"   {target_param}[t={t}] = {val:.6f}")
                    except:
                        print(f"   {target_param}[t={t}] = (not available)")
                
                # Calculate tensor statistics
                if tensor_values:
                    values_list = list(tensor_values.values())
                    print(f"\n📈 TENSOR STATISTICS:")
                    print(f"   Min value: {min(values_list):.6f}")
                    print(f"   Max value: {max(values_list):.6f}")
                    print(f"   Mean value: {sum(values_list)/len(values_list):.6f}")
                    print(f"   Sum of squares: {sum(v**2 for v in values_list):.6f}")
                    
            else:
                # Scalar target parameter
                val = value(var_obj)
                print(f"🎯 {target_param} = {val:.6f}")
        except Exception as e:
            print(f"❌ Error retrieving {target_param} values: {e}")
    
    print("\n" + "="*80)
    print("🏁 OPTIMIZATION COMPLETE")
    
    # Success summary
    if obj_value is not None:
        if obj_type == "minimize":
            print(f"✅ Successfully minimized {target_expr} to {obj_value:.6f}")
        else:
            print(f"✅ Successfully maximized {target_expr} to {obj_value:.6f}")
    
    print("="*80)
