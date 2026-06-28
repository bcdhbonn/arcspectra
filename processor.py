import os
import re
import traceback
import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Default formulas fallback for backward compatibility / display
FORMULAS = {
    "DVI": {
        "name": "Difference Vegetation Index",
        "formula": "NIR - Red"
    },
    "NDVI": {
        "name": "Normalized Difference Vegetation Index",
        "formula": "(NIR - Red) / (NIR + Red)"
    },
    "GNDVI": {
        "name": "Green Normalized Difference Vegetation Index",
        "formula": "(NIR - Green) / (NIR + Green)"
    },
    "WDVI": {
        "name": "Weighted Difference Vegetation Index",
        "formula": "NIR - (s * Red)"
    },
    "GEMI": {
        "name": "Global Environmental Monitoring Index",
        "formula": "eta * (1 - 0.25 * eta) - (Red - 0.125) / (1 - Red), where eta = [2*(NIR^2 - Red^2) + 1.5*NIR + 0.5*Red] / (NIR + Red + 0.5)"
    },
    "NDWI": {
        "name": "Normalized Difference Water Index (McFeeters)",
        "formula": "(Green - NIR) / (Green + NIR)"
    }
}

# Keep original PRESETS dictionary for legacy references
PRESETS = {
    "NRW": {
        "red": 1,
        "green": 2,
        "blue": 3,
        "nir": 4,
        "redEdge": None
    },
    "DJI": {
        "red": 3,
        "green": 2,
        "blue": 1,
        "nir": 5,
        "redEdge": None
    },
    "SEQ": {
        "red": 2,
        "green": 1,
        "blue": None,
        "nir": 4,
        "redEdge": 3
    }
}

def safe_divide(num, denom):
    """Safely divide two NumPy arrays, returning NaN where the denominator is zero."""
    with np.errstate(divide='ignore', invalid='ignore'):
        result = num / denom
        if isinstance(result, np.ndarray):
            result[denom == 0] = np.nan
            result[np.isinf(result)] = np.nan
        return result

def calculate_indices_dynamic(bands_data, selected_indices_formulas, parameters=None, log_callback=print):
    """
    Calculate spectral vegetation indices dynamically using Python eval and numpy.
    
    Parameters:
    - bands_data: Dict of {band_name: numpy_array}
    - selected_indices_formulas: Dict of {index_abbrev: formula_string}
    - parameters: Dict of extra parameters (e.g. {"s": 1.0, "gamma": 1.0, "L": 0.5})
    - log_callback: Logging function
    
    Returns:
    - Dict of {index_abbrev: index_array}
    """
    results = {}
    
    # Base context for eval
    # We provide numpy, common functions, and the band arrays
    context = {
        "np": np,
        "sqrt": np.sqrt,
        "arctan": np.arctan,
        "abs": np.abs,
        "log": np.log,
        "exp": np.exp,
        "safe_divide": safe_divide,
        "max": np.maximum,
        "min": np.minimum,
    }
    
    # Add band arrays to context (case-insensitive keys for safety)
    for band_name, band_arr in bands_data.items():
        arr_f32 = band_arr.astype(np.float32)
        context[band_name] = arr_f32
        # Also add uppercase/lowercase for safety
        context[band_name.upper()] = arr_f32
        context[band_name.lower()] = arr_f32
        
    # Add extra parameters
    if parameters:
        for k, v in parameters.items():
            context[k] = v
            # Add lowercase
            context[k.lower()] = v
            context[k.upper()] = v
            
    for idx_name, formula in selected_indices_formulas.items():
        # Make a copy of the context for this index so local variables don't leak
        idx_context = context.copy()
        try:
            # Pre-clean the formula: replace '^' with '**'
            clean_f = formula.replace('^', '**')
            
            # Split by semicolon to support assignments
            parts = [p.strip() for p in clean_f.split(';') if p.strip()]
            if not parts:
                continue
                
            # Execute all parts except the last one as statements
            for part in parts[:-1]:
                # This could be an assignment like 'eta = ...'
                # Executing in idx_context will add the variable to it
                exec(part, {}, idx_context)
                
            # Evaluate the final expression
            last_expression = parts[-1]
            
            with np.errstate(divide='ignore', invalid='ignore'):
                result = eval(last_expression, {}, idx_context)
                
                # If result is a single number instead of an array, expand it
                if not isinstance(result, np.ndarray):
                    for b_arr in bands_data.values():
                        result = np.full_like(b_arr, result)
                        break
                        
                # Clean up inf and NaN values
                if isinstance(result, np.ndarray):
                    result[np.isinf(result)] = np.nan
                    
            results[idx_name] = result
            log_callback(f"Successfully calculated: {idx_name}")
        except Exception as e:
            log_callback(f"Error calculating index {idx_name}: {str(e)}")
            print(traceback.format_exc())
            
    return results

def stretch_image(img, percentile_min=2, percentile_max=98):
    """Apply percentiles-based contrast stretch for visual plotting."""
    valid = img[~np.isnan(img) & ~np.isinf(img)]
    if len(valid) == 0:
        return img
    vmin, vmax = np.percentile(valid, [percentile_min, percentile_max])
    if vmin == vmax:
        return img
    return np.clip(img, vmin, vmax)

def generate_plot(ortho_name, results, output_dir):
    """
    Generate a dynamic grid plot of the computed indices.
    Saves the plot as a PNG file.
    """
    N = len(results)
    if N == 0:
        return None
        
    # Determine rows and cols dynamically
    if N == 1:
        rows, cols = 1, 1
    elif N == 2:
        rows, cols = 1, 2
    elif N <= 3:
        rows, cols = 1, 3
    elif N <= 4:
        rows, cols = 2, 2
    elif N <= 6:
        rows, cols = 2, 3
    elif N <= 8:
        rows, cols = 2, 4
    elif N <= 9:
        rows, cols = 3, 3
    else:
        cols = 4
        rows = (N + 3) // 4
        
    fig, axes = plt.subplots(rows, cols, figsize=(4.5 * cols, 4 * rows), dpi=200)
    fig.suptitle(f"Spectral Indices: {ortho_name}", fontsize=16, fontweight='bold', color='#1e293b')
    
    if N == 1:
        axes_flat = [axes]
    else:
        axes_flat = axes.flatten()
        
    # Sort indices alphabetically
    sorted_idx = sorted(list(results.keys()))
    
    for i, idx_name in enumerate(sorted_idx):
        ax = axes_flat[i]
        data = results[idx_name]
        stretched = stretch_image(data)
        
        im = ax.imshow(stretched, cmap='Spectral')
        ax.set_title(f"{idx_name}", fontsize=11, fontweight='semibold', color='#334155')
        
        # Colorbar
        cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.75, pad=0.04)
        cbar.ax.tick_params(labelsize=8)
        
        # Overlay stats
        valid_data = data[~np.isnan(data)]
        if len(valid_data) > 0:
            stats_str = f"Min: {np.nanmin(valid_data):.2f}\nMax: {np.nanmax(valid_data):.2f}\nMean: {np.nanmean(valid_data):.2f}"
            ax.text(0.02, 0.02, stats_str, transform=ax.transAxes, fontsize=8, 
                    bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
        ax.axis('off')
        
    # Hide unused grids
    for j in range(N, len(axes_flat)):
        axes_flat[j].axis('off')
        
    plt.tight_layout()
    plot_dir = os.path.join(output_dir, ortho_name)
    os.makedirs(plot_dir, exist_ok=True)
    plot_file = os.path.join(plot_dir, f"{ortho_name}_plot.png")
    plt.savefig(plot_file, bbox_inches='tight')
    plt.close()
    return plot_file

def process_raster_file(file_path, output_dir, bands_mapping, selected_indices_formulas, 
                        wdvi_s=1.0, scale_factor=1.0, log_callback=print):
    """
    Process a single GeoTIFF file: load bands, compute selected indices dynamically, save results, and save overview plot.
    """
    ortho_name = os.path.splitext(os.path.basename(file_path))[0]
    log_callback(f"Starting processing for {ortho_name}...")
    
    with rasterio.open(file_path) as src:
        num_bands = src.count
        log_callback(f"File loaded. Resolution: {src.width}x{src.height}, Bands: {num_bands}")
        
        # Read bands dynamically
        bands_data = {}
        for band_name, band_index in bands_mapping.items():
            if band_index is None or str(band_index).lower() == 'none':
                continue
            band_idx_int = int(band_index)
            if band_idx_int > num_bands:
                raise ValueError(f"Error: The {band_name} band was set to {band_idx_int}, but the image only has {num_bands} bands.")
            bands_data[band_name] = src.read(band_idx_int).astype(np.float32)
            log_callback(f"Loaded band '{band_name}' from band index {band_idx_int}")
            
        if not bands_data:
            raise ValueError("Error: No bands could be loaded. Check your sensor configuration.")
            
        # Mask nodata if present
        nodata = src.nodata
        if nodata is not None:
            # Build combined mask of valid pixels (valid in all loaded bands)
            first_arr = next(iter(bands_data.values()))
            valid_mask = np.ones(first_arr.shape, dtype=bool)
            for arr in bands_data.values():
                valid_mask &= (arr != nodata)
                
            # Set nodata values to NaN
            for band_name, arr in bands_data.items():
                arr[~valid_mask] = np.nan
                
        # Apply scale factor if specified
        if scale_factor != 1.0:
            log_callback(f"Scaling band reflectances by factor: {scale_factor}")
            for band_name, arr in bands_data.items():
                bands_data[band_name] = arr / scale_factor
                
        # Calculate indices
        log_callback(f"Calculating {len(selected_indices_formulas)} indices dynamically...")
        parameters = {"s": wdvi_s, "gamma": 1.0, "L": 0.5}
        results = calculate_indices_dynamic(bands_data, selected_indices_formulas, parameters, log_callback)
        
        if not results:
            log_callback("Warning: No spectral indices were calculated.")
            return ortho_name, {}, {}, None
            
        # Save indices to file
        log_callback("Saving GeoTIFF results...")
        out_dir = os.path.join(output_dir, ortho_name)
        os.makedirs(out_dir, exist_ok=True)
        
        out_profile = src.profile.copy()
        out_profile.update(
            dtype=rasterio.float32,
            count=1,
            nodata=np.nan
        )
        
        saved_files = {}
        for idx_name, idx_data in results.items():
            out_file = os.path.join(out_dir, f"{ortho_name}_{idx_name}.tif")
            with rasterio.open(out_file, 'w', **out_profile) as dst:
                dst.write(idx_data.astype(np.float32), 1)
            saved_files[idx_name] = out_file
            
        # Generate plot
        log_callback("Generating overview plots...")
        plot_file = generate_plot(ortho_name, results, output_dir)
        
        log_callback(f"Processing completed for {ortho_name}.\n")
        return ortho_name, results, saved_files, plot_file
