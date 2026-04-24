import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

def load_data():
    """Load the timeseries and metadata files with correct separators."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    ts_path = os.path.join(base_path, "timeseries", "timeseries.csv")
    meta_path = os.path.join(base_path, "timeseries", "metadata.txt")

    print(f"Loading data from {ts_path}...")
    
    # Load timeseries: semicolon separator
    # We load as strings first because decimals are inconsistent between columns
    ts_df = pd.read_csv(ts_path, sep=';', dtype=str)
    
    # Clean and convert to numeric:
    # 1. trait_mean uses '.' as decimal
    ts_df['trait_mean'] = pd.to_numeric(ts_df['trait_mean'].str.replace(',', '.'), errors='coerce')
    
    # 2. age_MY uses ',' as decimal (we convert it to '.' for Python/Pandas)
    ts_df['age_MY'] = pd.to_numeric(ts_df['age_MY'].str.replace(',', '.'), errors='coerce')
    
    # 3. trait_var and others should also be numeric
    ts_df['trait_var'] = pd.to_numeric(ts_df['trait_var'].str.replace(',', '.'), errors='coerce')
    ts_df['tsID'] = pd.to_numeric(ts_df['tsID'], errors='coerce')
    
    # Drop rows that couldn't be converted
    ts_df = ts_df.dropna(subset=['trait_mean', 'age_MY', 'tsID'])

    # Load metadata: tab separator
    meta_df = pd.read_csv(meta_path, sep='\t')
    
    return ts_df, meta_df

def calculate_evolutionary_rate(df, ts_id, species_name):
    """
    Calculate the rate of evolution for a specific timeseries ID.
    The rate is calculated as the change in trait_mean over age_MY.
    """
    # Filter data for the specific time series
    subset = df[df['tsID'] == ts_id].copy()
    
    # We need at least 2 points to calculate a rate
    if len(subset) < 2:
        return None

    # Sort by age (from oldest to youngest)
    subset = subset.sort_values('age_MY', ascending=False)

    # Linear Regression: Trait = slope * Age + intercept
    # Note: Age is in Millions of Years. 
    # Slope represents: Change in Trait Units per Million Years.
    slope, intercept, r_value, p_value, std_err = stats.linregress(subset['age_MY'], subset['trait_mean'])

    # Calculation of Darwins (d)
    # 1 Darwin = change by a factor of e per million years.
    # Formula: [ln(Trait2) - ln(Trait1)] / (Time1 - Time2)
    # We use the log of the mean if the values are positive.
    if (subset['trait_mean'] > 0).all():
        log_trait = np.log(subset['trait_mean'])
        d_slope, _, _, _, _ = stats.linregress(subset['age_MY'], log_trait)
        darwins = abs(d_slope)
    else:
        darwins = None

    return {
        'tsID': ts_id,
        'species': species_name,
        'slope': slope,
        'r_squared': r_value**2,
        'p_value': p_value,
        'darwins': darwins,
        'data': subset
    }

def plot_evolution(result):
    """Visualize the trait change over time."""
    data = result['data']
    
    plt.figure(figsize=(10, 6))
    plt.scatter(data['age_MY'], data['trait_mean'], color='blue', label='Data Points')
    
    # Plot regression line
    x = np.array([data['age_MY'].min(), data['age_MY'].max()])
    y = result['slope'] * x + (data['trait_mean'].mean() - result['slope'] * data['age_MY'].mean())
    plt.plot(x, y, color='red', linestyle='--', label=f"Trend (Slope: {result['slope']:.4f})")

    plt.gca().invert_xaxis()  # Time usually goes from Old (right) to Present (left)
    plt.xlabel("Age (Millions of Years ago)")
    plt.ylabel("Trait Mean Value")
    plt.title(f"Evolutionary Trend: {result['species']} (ID: {result['tsID']})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    filename = f"evolution_rate_{result['tsID']}.png"
    plt.savefig(filename)
    print(f"\nGraph saved as {filename}")
    plt.close()

def compare_evolution_types(summary_df):
    """
    Compare 'Scaling' traits (Size) vs 'Complexity' traits (Structure).
    """
    scaling_types = ['linear', 'volume', 'mass', 'area']
    complexity_types = ['ratio', 'angle', 'complex']
    
    # We need the trait_type in the summary_df
    # (Assuming we pass it through from the metadata)
    
    scaling_df = summary_df[summary_df['Trait_Type'].isin(scaling_types)]
    complexity_df = summary_df[summary_df['Trait_Type'].isin(complexity_types)]
    
    print("\n--- Scaling vs. Complexity Analysis ---")
    print(f"Scaling Traits (Size): {len(scaling_df)} series")
    print(f"Complexity Traits (Shape/Structure): {len(complexity_df)} series")
    
    if not scaling_df.empty and not complexity_df.empty:
        avg_scaling = scaling_df['Darwins'].mean()
        avg_complexity = complexity_df['Darwins'].mean()
        
        print(f"\nAverage Rate (Scaling): {avg_scaling:.6f} Darwins")
        print(f"Average Rate (Complexity): {avg_complexity:.6f} Darwins")
        
        ratio = avg_scaling / avg_complexity
        print(f"\nRESULT: Scaling evolution is {ratio:.2f}x faster on average than Structural innovation.")
        
        print("\nSUPPORT FOR 'A THOUSAND BRAINS' THEORY:")
        if ratio > 1.2:
            print("The data supports Jeff Hawkins' claim: Evolution finds it much easier to 'scale up' existing structures")
            print("than to invent new complex capabilities. This explains why the neocortex could triple in size")
            print("so rapidly—it was simply duplicating existing neural columns.")
        else:
            print("The data suggests Scaling and Complexity evolve at similar rates in this dataset.")

def main():
    print("Evolutionary Rate Analyzer: Complexity vs. Scaling")
    print("===============================================")
    
    try:
        ts_df, meta_df = load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    all_results = []
    unique_ids = ts_df['tsID'].unique()
    
    print(f"Scanning {len(unique_ids)} time-series datasets...")

    for ts_id in unique_ids:
        species_info = meta_df[meta_df['tsID'] == ts_id]
        if species_info.empty: continue
        
        species_name = species_info['species'].values[0]
        trait_type = species_info['trait_type'].values[0]
        
        result = calculate_evolutionary_rate(ts_df, ts_id, species_name)
        if result and result['darwins'] is not None:
            result['trait_type'] = trait_type
            all_results.append(result)

    if not all_results:
        print("No valid data.")
        return

    summary_df = pd.DataFrame([
        {
            'tsID': r['tsID'],
            'Species': r['species'],
            'Darwins': r['darwins'],
            'Trait_Type': r['trait_type'],
            'Significant': r['p_value'] < 0.05
        } for r in all_results
    ])

    # Perform the comparison
    compare_evolution_types(summary_df)

    # Find the top significant evolvers
    sig_df = summary_df[summary_df['Significant'] == True].sort_values('Darwins', ascending=False)
    print("\n--- Fastest SIGNIFICANT Evolvers ---")
    print(sig_df.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
