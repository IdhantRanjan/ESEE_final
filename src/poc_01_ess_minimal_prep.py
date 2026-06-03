#!/usr/bin/env python3
"""
ESEE 2026 POC - Step 1: Minimal ESS Data Preparation

Extract and prepare ESS10 data for work-time reduction policy analysis.
Creates a minimal dataset with one policy outcome variable.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main data preparation function."""
    print("=" * 70)
    print("ESEE 2026 POC - Step 1: ESS Minimal Data Preparation")
    print("=" * 70)
    print()
    
    # Paths
    input_file = PROJECT_ROOT / "data" / "raw" / "ESS10.csv"
    output_file = PROJECT_ROOT / "data" / "processed" / "ess_minimal_poc.csv"
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # EU27 country codes
    EU27_COUNTRIES = {
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR',
        'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO',
        'SE', 'SI', 'SK'
    }
    
    print(f"Loading ESS10 data from: {input_file}")
    print("This may take a moment...")
    
    try:
        # Load data
        df = pd.read_csv(input_file, low_memory=False)
        print(f"  ✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"  ✗ ERROR loading data: {e}")
        sys.exit(1)
    
    print("\nSearching for work-time related variables...")
    
    # Look for work-time related columns
    work_cols = [col for col in df.columns if any(kw in col.lower() 
                                                   for kw in ['work', 'hour', 'job', 'employ', 'wrk'])]
    
    print(f"  Found {len(work_cols)} potential work-related columns")
    if len(work_cols) > 0:
        print(f"  Examples: {work_cols[:10]}")
    
    # Check for specific variables that might indicate work-time preferences
    # Common ESS variables: wrkctra, wrklong, wkdcorga, etc.
    
    # Create outcome variable: work_time_reduction_willingness
    print("\nCreating work-time reduction willingness variable...")
    
    # Strategy: Create synthetic proxy based on work-life balance, life satisfaction, and income
    # High satisfaction + long hours + low income → more likely to want work reduction
    
    # Check for relevant variables
    has_wrklong = 'wrklong' in df.columns  # Long working hours
    has_stflife = 'stflife' in df.columns  # Life satisfaction
    has_wrklong_hrs = 'wrklong_hrs' in df.columns  # Actual hours worked
    
    outcome_created = False
    
    if has_wrklong or has_stflife:
        # Try to create from existing variables
        # wrklong: 1=Very long, 2=Long, 3=About right, 4=Short, 5=Very short
        # Higher values = want to work less
        
        if 'wrklong' in df.columns:
            # People who say hours are too long are more willing to reduce
            df['work_time_reduction_willingness'] = (
                (df['wrklong'].isin([1, 2])) & (df['wrklong'].notna())
            ).astype(int)
            outcome_created = True
            print("  ✓ Created from 'wrklong' variable (working hours too long)")
    
    if not outcome_created:
        # Create synthetic proxy
        print("  Creating synthetic proxy variable...")
        
        # Combine multiple indicators if available
        score = 0
        
        # Long hours indicator
        if 'wrklong' in df.columns:
            score += (df['wrklong'].isin([1, 2]).astype(int) * 3)
        
        # Life satisfaction (lower = more willing to change)
        if 'stflife' in df.columns:
            # stflife: 0-10, lower = less satisfied
            score += (11 - pd.to_numeric(df['stflife'], errors='coerce').fillna(5.5)) * 0.5
        
        # Income (lower income more willing)
        if 'hinctnta' in df.columns:
            # hinctnta: 1-10 deciles, higher = more income
            score += (11 - pd.to_numeric(df['hinctnta'], errors='coerce').fillna(5.5)) * 0.5
        
        # Create binary outcome (top 40% of scores)
        threshold = score.quantile(0.6)
        df['work_time_reduction_willingness'] = (score >= threshold).astype(int)
        print(f"  ✓ Created synthetic variable (threshold: {threshold:.2f})")
    
    # Extract key features
    print("\nExtracting key features...")
    
    # Required columns
    required_cols = ['cntry', 'hinctnta']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"  ✗ ERROR: Missing required columns: {missing_cols}")
        sys.exit(1)
    
    # Create minimal dataset
    poc_df = pd.DataFrame()
    
    # Outcome
    poc_df['work_time_reduction_willingness'] = df['work_time_reduction_willingness']
    
    # Income: convert decile to quintile
    poc_df['income_decile'] = pd.to_numeric(df['hinctnta'], errors='coerce')
    poc_df['income_quintile'] = pd.cut(
        poc_df['income_decile'],
        bins=[0, 2, 4, 6, 8, 10],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True
    ).astype('Int64')
    
    # Country
    poc_df['country'] = df['cntry']
    
    # Demographics
    poc_df['age'] = pd.to_numeric(df['agea'], errors='coerce')
    poc_df['gender'] = pd.to_numeric(df['gndr'], errors='coerce') if 'gndr' in df.columns else np.nan
    poc_df['education'] = pd.to_numeric(df['eisced'], errors='coerce') if 'eisced' in df.columns else np.nan
    
    # Clean data
    print("\nCleaning data...")
    initial_n = len(poc_df)
    
    # Keep only EU27 countries
    poc_df = poc_df[poc_df['country'].isin(EU27_COUNTRIES)]
    print(f"  After filtering EU27 countries: {len(poc_df):,} rows")
    
    # Drop rows with missing income or country
    poc_df = poc_df.dropna(subset=['income_quintile', 'country'])
    print(f"  After dropping missing income/country: {len(poc_df):,} rows")
    
    # Handle missing values in other columns (median imputation)
    for col in ['age', 'gender', 'education']:
        if col in poc_df.columns:
            median_val = poc_df[col].median()
            poc_df[col] = poc_df[col].fillna(median_val)
            n_missing = poc_df[col].isna().sum()
            if n_missing > 0:
                print(f"  Filled {n_missing} missing values in {col} with median ({median_val})")
    
    final_n = len(poc_df)
    print(f"\nFinal dataset: {final_n:,} observations ({final_n/initial_n*100:.1f}% of original)")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    adoption_rate = poc_df['work_time_reduction_willingness'].mean() * 100
    print(f"\nWork-time reduction willingness: {adoption_rate:.1f}%")
    
    if adoption_rate < 30 or adoption_rate > 70:
        print(f"  ⚠ WARNING: Adoption rate ({adoption_rate:.1f}%) outside expected range (30-70%)")
        print("  This is okay for a POC - using synthetic proxy")
    
    # Distribution by income quintile
    print("\nDistribution by income quintile:")
    income_dist = poc_df.groupby('income_quintile')['work_time_reduction_willingness'].agg(['count', 'mean'])
    income_dist.columns = ['N', 'Adoption_Rate']
    income_dist['Adoption_Rate'] = income_dist['Adoption_Rate'] * 100
    print(income_dist)
    
    # Distribution by country
    print("\nDistribution by country (top 15):")
    country_dist = poc_df.groupby('country')['work_time_reduction_willingness'].agg(['count', 'mean'])
    country_dist.columns = ['N', 'Adoption_Rate']
    country_dist['Adoption_Rate'] = country_dist['Adoption_Rate'] * 100
    country_dist = country_dist.sort_values('N', ascending=False).head(15)
    print(country_dist)
    
    # Save
    print(f"\nSaving to: {output_file}")
    poc_df.to_csv(output_file, index=False)
    print("  ✓ Saved successfully")
    
    print("\n" + "=" * 70)
    print("STEP 1 COMPLETE")
    print("=" * 70)
    print(f"Output: {output_file}")
    print(f"Observations: {len(poc_df):,}")
    print(f"Adoption rate: {adoption_rate:.1f}%")
    print("=" * 70)
    
    return poc_df


if __name__ == "__main__":
    try:
        result = main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


