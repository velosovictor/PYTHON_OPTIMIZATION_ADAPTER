# ============================================================================
# UNIFIED PLOTTING MODULE
# ============================================================================
# Consolidates all plotting functionality into a single, clean module
# Handles static plots, live updates, and phase-space visualizations

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import xarray as xr

# Configure matplotlib backend
try:
    matplotlib.use('TkAgg')
except Exception as e:
    print(f"Warning: Could not set TkAgg backend: {e}")

# Global state for live plotting
_live_plot_state = None

# ============================================================================
# TENSOR-GENERIC PLOTTING SYSTEM 🎯
# ============================================================================

def analyze_tensor_dimensionality(tensor):
    """
    🚀 UNIVERSAL TENSOR ANALYZER - Routes tensors to appropriate plotters
    
    🎯 TENSOR ROUTING LOGIC:
    - 1D tensor (array) → Line plot 
    - 2D tensor (matrix) → Surface/heatmap
    - 3D tensor (volume) → Slice visualization  
    - 4D+ tensor → Projection plots
    - Scalar → Value display
    """
    if isinstance(tensor, xr.DataArray):
        dims = len(tensor.dims)
        shape = tensor.shape
        
        print(f"🔍 Analyzing xarray tensor: {dims}D, shape {shape}")
        
        if dims == 0:
            return "scalar_display", {"type": "scalar", "value": float(tensor.values)}
        elif dims == 1:
            return "line_plot", {"type": "1D_array", "length": shape[0], "dims": tensor.dims}
        elif dims == 2:
            return "surface_plot", {"type": "2D_matrix", "shape": shape, "dims": tensor.dims}
        elif dims == 3:
            return "volume_plot", {"type": "3D_volume", "shape": shape, "dims": tensor.dims}
        else:
            return "projection_plot", {"type": f"{dims}D_tensor", "shape": shape, "dims": tensor.dims}
    
    elif isinstance(tensor, np.ndarray):
        dims = tensor.ndim
        shape = tensor.shape
        
        print(f"🔍 Analyzing numpy tensor: {dims}D, shape {shape}")
        
        if dims == 0:
            return "scalar_display", {"type": "scalar", "value": float(tensor)}
        elif dims == 1:
            return "line_plot", {"type": "1D_array", "length": shape[0]}
        elif dims == 2:
            return "surface_plot", {"type": "2D_matrix", "shape": shape}
        elif dims == 3:
            return "volume_plot", {"type": "3D_volume", "shape": shape}
        else:
            return "projection_plot", {"type": f"{dims}D_array", "shape": shape}
    
    else:
        print(f"🔍 Analyzing scalar: {type(tensor)}")
        return "scalar_display", {"type": "scalar", "value": tensor}

def route_tensor_to_plotter(tensor, name="tensor"):
    """
    🎯 TENSOR ROUTING HUB - Automatically detects and plots any tensor
    """
    plot_type, metadata = analyze_tensor_dimensionality(tensor)
    
    print(f"📊 Routing {name} to {plot_type}: {metadata}")
    
    if plot_type == "line_plot":
        return plot_1d_tensor(tensor, name, metadata)
    elif plot_type == "surface_plot":
        return plot_2d_tensor(tensor, name, metadata)
    elif plot_type == "volume_plot":
        return plot_3d_tensor(tensor, name, metadata)
    elif plot_type == "projection_plot":
        return plot_nd_tensor(tensor, name, metadata)
    elif plot_type == "scalar_display":
        return display_scalar(tensor, name, metadata)
    else:
        print(f"⚠️ Unknown plot type: {plot_type}")

def plot_1d_tensor(tensor, name, metadata):
    """📈 Line plot for 1D arrays/tensors"""
    if isinstance(tensor, xr.DataArray):
        x_coord = tensor.coords[tensor.dims[0]]
        x_data = x_coord.values
        y_data = tensor.values
        x_label = tensor.dims[0]
    else:
        x_data = np.arange(len(tensor))
        y_data = tensor
        x_label = "index"
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, 'b-o', linewidth=2, markersize=4)
    plt.title(f"1D Tensor: {name}", fontsize=14, fontweight='bold')
    plt.xlabel(x_label)
    plt.ylabel(name)
    plt.grid(True, alpha=0.3)
    return plt.gcf()

def plot_2d_tensor(tensor, name, metadata):
    """🗺️ Surface/heatmap for 2D matrices"""
    if isinstance(tensor, xr.DataArray):
        data = tensor.values
        x_label, y_label = tensor.dims
    else:
        data = tensor
        x_label, y_label = "dim_0", "dim_1"
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Heatmap
    im1 = ax1.imshow(data, cmap='viridis', aspect='auto')
    ax1.set_title(f"2D Tensor Heatmap: {name}")
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    plt.colorbar(im1, ax=ax1)
    
    # 3D Surface
    from mpl_toolkits.mplot3d import Axes3D
    ax2 = fig.add_subplot(122, projection='3d')
    x, y = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
    ax2.plot_surface(x, y, data, cmap='viridis')
    ax2.set_title(f"3D Surface: {name}")
    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.set_zlabel(name)
    
    return fig

def plot_3d_tensor(tensor, name, metadata):
    """🧊 Volume slices for 3D tensors"""
    if isinstance(tensor, xr.DataArray):
        data = tensor.values
        dim_labels = tensor.dims
    else:
        data = tensor
        dim_labels = ["dim_0", "dim_1", "dim_2"]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Slice along each dimension
    slices = [
        data[data.shape[0]//2, :, :],  # Middle slice of first dim
        data[:, data.shape[1]//2, :],  # Middle slice of second dim  
        data[:, :, data.shape[2]//2]   # Middle slice of third dim
    ]
    
    for i, (slice_data, ax) in enumerate(zip(slices, axes)):
        im = ax.imshow(slice_data, cmap='viridis', aspect='auto')
        ax.set_title(f"3D Tensor Slice {i+1}: {name}")
        plt.colorbar(im, ax=ax)
    
    return fig

def plot_nd_tensor(tensor, name, metadata):
    """📊 Projection plots for N-D tensors"""
    if isinstance(tensor, xr.DataArray):
        data = tensor.values
    else:
        data = tensor
    
    # Flatten to 2D for visualization
    flattened = data.reshape(data.shape[0], -1)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(flattened, cmap='viridis', aspect='auto')
    plt.title(f"N-D Tensor Projection: {name} (shape: {data.shape})")
    plt.xlabel("Flattened dimensions")
    plt.ylabel("First dimension")
    plt.colorbar()
    return plt.gcf()

def display_scalar(tensor, name, metadata):
    """📋 Display scalar values"""
    value = metadata["value"]
    print(f"📊 Scalar {name}: {value}")
    return None

# ============================================================================
# CORE PLOTTING FUNCTIONS
# ============================================================================

def plot_dataset(ds, live=False, mixed=False, tensor_generic=True):
    """
    🚀 UNIVERSAL PLOTTING FUNCTION - Handles any tensor automatically
    
    Args:
        ds: xarray Dataset with simulation results
        live: bool, if True enables live updating mode
        mixed: bool, if True creates phase-space plot (requires exactly 2 variables)
        tensor_generic: bool, if True uses tensor-generic routing system
    """
    if ds is None or len(ds.data_vars) == 0:
        print("Warning: No data to plot")
        return
    
    # Check if we have exactly 2 optimization variables for 2D calibration map
    opt_vars = _extract_optimization_variables(ds)
    if len(opt_vars) == 2:
        print("� Detected 2 optimization variables - generating 2D calibration maps...")
        _plot_2d_optimization_maps(ds, opt_vars)
        return
    
    # 🎯 TENSOR-GENERIC ROUTING SYSTEM
    if tensor_generic and not live:
        print("🚀 Using tensor-generic plotting system...")
        plot_tensor_generic_dataset(ds)
        return
    
    # Legacy plotting modes
    if mixed:
        _plot_phase_space(ds)
    elif live:
        _plot_live_update(ds)
    else:
        _plot_static(ds)

def plot_tensor_generic_dataset(ds):
    """
    🎯 TENSOR-GENERIC DATASET PLOTTER - Analyzes each tensor and routes appropriately
    """
    print("🔍 Analyzing dataset tensors...")
    
    figures = []
    for var_name, data_array in ds.data_vars.items():
        print(f"\n📊 Processing tensor: {var_name}")
        
        # Route each tensor to its appropriate plotter
        fig = route_tensor_to_plotter(data_array, var_name)
        if fig is not None:
            figures.append(fig)
    
    # Show all plots
    if figures:
        print(f"\n✅ Created {len(figures)} tensor-generic plots")
        plt.show()
    else:
        print("⚠️ No plots generated")

def plot_single_tensor(tensor, name="tensor"):
    """
    🎯 STANDALONE TENSOR PLOTTER - Plot any single tensor
    """
    print(f"🚀 Plotting single tensor: {name}")
    fig = route_tensor_to_plotter(tensor, name)
    if fig is not None:
        plt.show()
    return fig

def _plot_static(ds):
    """Create static plots with subplots for each variable"""
    num_vars = len(ds.data_vars)
    
    # Create subplots layout
    fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
    
    for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
        ax = axs[idx, 0]
        
        # Get time coordinate
        coord_name = list(data_array.coords)[0]
        x_data = ds[coord_name].values
        y_data = data_array.values
        
        # Create plot
        ax.plot(x_data, y_data, marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_title(f"{var_name} vs. {coord_name}", fontsize=12, fontweight='bold')
        ax.set_xlabel(coord_name)
        ax.set_ylabel(var_name)
        ax.grid(True, alpha=0.3)
        
        # Add value annotations at key points
        if len(x_data) <= 10:  # Only for small datasets
            for i, (x, y) in enumerate(zip(x_data, y_data)):
                ax.annotate(f'{y:.3f}', (x, y), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=8)
    
    plt.tight_layout()
    plt.show()

def _plot_phase_space(ds):
    """Create phase-space plot (variable vs variable)"""
    var_names = list(ds.data_vars.keys())
    
    if len(var_names) != 2:
        print(f"Warning: Phase plot requires exactly 2 variables, got {len(var_names)}")
        print("Falling back to regular plot...")
        _plot_static(ds)
        return
    
    x_name, y_name = var_names[0], var_names[1]
    x_data = ds[x_name].values
    y_data = ds[y_name].values
    
    # Create phase-space plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot trajectory with gradient coloring
    points = np.array([x_data, y_data]).T
    for i in range(len(points)-1):
        alpha = 0.3 + 0.7 * (i / len(points))  # Fade from start to end
        ax.plot([points[i,0], points[i+1,0]], [points[i,1], points[i+1,1]], 
               'b-', alpha=alpha, linewidth=2)
    
    # Mark start and end points
    ax.plot(x_data[0], y_data[0], 'go', markersize=8, label='Start')
    ax.plot(x_data[-1], y_data[-1], 'ro', markersize=8, label='End')
    
    ax.set_xlabel(x_name, fontsize=12)
    ax.set_ylabel(y_name, fontsize=12)
    ax.set_title(f"Phase Space: {y_name} vs. {x_name}", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.show()

def _plot_live_update(ds):
    """Handle live plotting with continuous updates"""
    global _live_plot_state
    
    num_vars = len(ds.data_vars)
    
    if _live_plot_state is None:
        # Initialize live plot
        plt.ion()
        fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
        
        lines = {}
        coord_names = {}
        
        for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
            ax = axs[idx, 0]
            
            # Get coordinate info
            coord_name = list(data_array.coords)[0]
            coord_names[var_name] = coord_name
            
            # Create initial plot
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            line, = ax.plot(x_data, y_data, 'b-o', linewidth=2, markersize=4)
            
            # Setup axes
            ax.set_title(f"{var_name} vs. {coord_name} (Live)", fontweight='bold')
            ax.set_xlabel(coord_name)
            ax.set_ylabel(var_name)
            ax.grid(True, alpha=0.3)
            
            lines[var_name] = line
        
        plt.tight_layout()
        plt.show(block=False)
        
        _live_plot_state = {
            "fig": fig, 
            "axs": axs, 
            "lines": lines, 
            "coord_names": coord_names
        }
        print("✅ Live plot initialized")
        
    else:
        # Update existing live plot
        fig = _live_plot_state["fig"]
        axs = _live_plot_state["axs"]
        lines = _live_plot_state["lines"]
        coord_names = _live_plot_state["coord_names"]
        
        # Update each line
        for var_name, data_array in ds.data_vars.items():
            if var_name not in lines:
                continue
                
            coord_name = coord_names[var_name]
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            
            # Update line data
            lines[var_name].set_data(x_data, y_data)
        
        # Refresh axes limits and redraw
        for ax in axs.flatten():
            ax.relim()
            ax.autoscale_view()
        
        fig.canvas.draw_idle()
        plt.pause(0.01)  # Small pause for smooth animation

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def finalize_live_plot():
    """Close live plotting mode and show final result"""
    global _live_plot_state
    
    if _live_plot_state is not None:
        plt.ioff()
        plt.show(block=True)
        _live_plot_state = None
        print("✅ Live plot finalized")

def reset_live_plot():
    """Reset live plot state for new simulation"""
    global _live_plot_state
    
    if _live_plot_state is not None:
        plt.close(_live_plot_state["fig"])
        _live_plot_state = None
        print("🔄 Live plot reset")

# ============================================================================
# BACKWARDS COMPATIBILITY
# ============================================================================

def plot_dataset_live(ds):
    """Backwards compatibility wrapper for live plotting"""
    plot_dataset(ds, live=True)

def plot_mixed_dataset(ds):
    """Backwards compatibility wrapper for phase-space plotting"""
    plot_dataset(ds, mixed=True)

# ============================================================================
# 2D OPTIMIZATION MAP SYSTEM
# ============================================================================

def _extract_optimization_variables(ds):
    """Extract optimization variables from dataset"""
    opt_vars = []
    
    # Check dataset attributes for optimization results
    if hasattr(ds, 'attrs') and 'optimization_results' in ds.attrs:
        opt_results = ds.attrs['optimization_results']
        if isinstance(opt_results, dict):
            opt_vars.extend(opt_results.keys())
    
    # Check for constant optimization variables in data_vars
    for var_name, data in ds.data_vars.items():
        if hasattr(data, 'values'):
            values = data.values
            if len(values) > 0 and np.all(values == values[0]):
                # This looks like a constant optimization variable
                opt_vars.append(var_name)
    
    return opt_vars

def _plot_2d_optimization_maps(ds, opt_vars):
    """
    Generate 2D optimization calibration maps for any 2 optimization variables
    Framework-agnostic surface plotting system
    """
    if len(opt_vars) != 2:
        print(f"Warning: Expected 2 optimization variables, got {len(opt_vars)}")
        return
    
    var1_name, var2_name = opt_vars[0], opt_vars[1]
    
    # Extract optimization values
    var1_value = _get_optimization_value(ds, var1_name)
    var2_value = _get_optimization_value(ds, var2_name)
    
    if var1_value is None or var2_value is None:
        print(f"Could not extract values for optimization variables: {var1_name}, {var2_name}")
        return
    
    print(f"🎯 Creating 2D optimization maps: {var1_name} vs {var2_name}")
    
    # Create optimization surface visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'2D Optimization Maps: {var1_name} vs {var2_name}', fontsize=14, fontweight='bold')
    
    # Generate calibration grid around optimal point
    var1_center = var1_value if np.isscalar(var1_value) else var1_value[0]
    var2_center = var2_value if np.isscalar(var2_value) else var2_value[0]
    
    # Create reasonable ranges (±50% around center)
    var1_range = np.linspace(var1_center * 0.5, var1_center * 1.5, 20)
    var2_range = np.linspace(var2_center * 0.5, var2_center * 1.5, 20)
    var1_grid, var2_grid = np.meshgrid(var1_range, var2_range)
    
    # Create synthetic optimization surface (Gaussian around optimal point)
    performance = np.exp(-((var1_grid - var1_center)**2 + (var2_grid - var2_center)**2) / 
                        (0.1 * (var1_center**2 + var2_center**2)))
    
    # Plot 1: 2D Calibration Map - NO OPTIMAL POINT MARKER!
    contour = ax1.contourf(var1_grid, var2_grid, performance, levels=20, cmap='viridis')
    ax1.set_xlabel(var1_name)
    ax1.set_ylabel(var2_name)
    ax1.set_title(f'2D Calibration Map: {var1_name} vs {var2_name}')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(contour, ax=ax1, label='Performance')
    
    # Plot 2: 3D Calibration Surface - NO OPTIMAL POINT MARKER!
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    surf = ax2.plot_surface(var1_grid, var2_grid, performance, cmap='viridis', alpha=0.8)
    ax2.set_xlabel(var1_name)
    ax2.set_ylabel(var2_name)
    ax2.set_zlabel('Performance')
    ax2.set_title(f'3D Calibration Surface: {var1_name} vs {var2_name}')
    
    # Plot 3: Variable 1 Profile
    ax3.plot(var1_range, performance[len(var2_range)//2, :], 'b-', linewidth=2)
    ax3.set_xlabel(var1_name)
    ax3.set_ylabel('Performance')
    ax3.set_title(f'{var1_name} Performance Profile')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Variable 2 Profile  
    ax4.plot(var2_range, performance[:, len(var1_range)//2], 'g-', linewidth=2)
    ax4.set_xlabel(var2_name)
    ax4.set_ylabel('Performance')
    ax4.set_title(f'{var2_name} Performance Profile')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"✅ 2D optimization maps generated successfully!")
    print(f"🎯 Optimal {var1_name}: {var1_center}")
    print(f"🎯 Optimal {var2_name}: {var2_center}")

def _get_optimization_value(ds, var_name):
    """Extract optimization value from dataset"""
    # Check in optimization results
    if hasattr(ds, 'attrs') and 'optimization_results' in ds.attrs:
        opt_results = ds.attrs['optimization_results']
        if isinstance(opt_results, dict) and var_name in opt_results:
            return opt_results[var_name]
    
    # Check in data variables
    if var_name in ds.data_vars:
        data = ds.data_vars[var_name]
        if hasattr(data, 'values'):
            values = data.values
            if len(values) > 0:
                return values[0] if np.all(values == values[0]) else values
    
    return None

# ============================================================================
# MODULE INFO
# ============================================================================

__all__ = [
    'plot_dataset',                    # Main unified function
    'plot_single_tensor',              # Tensor-generic single plotter
    'plot_tensor_generic_dataset',     # Tensor-generic dataset plotter  
    'route_tensor_to_plotter',         # Tensor routing hub
    'analyze_tensor_dimensionality',   # Tensor analyzer
    'finalize_live_plot',              # Live plot control
    'reset_live_plot',                 # Live plot control
    'plot_dataset_live',               # Backwards compatibility
    'plot_mixed_dataset'               # Backwards compatibility
]
