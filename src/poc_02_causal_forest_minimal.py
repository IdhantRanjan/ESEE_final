#!/usr/bin/env python3
"""
ESEE 2026 POC - Step 2: Simple Causal Forest

Train simple heterogeneous effect model using RandomForest.
Estimates adoption probabilities by income quintile × country.
"""

import sys
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def main():
    """Main causal forest function."""
    print("=" * 70)
    print("ESEE 2026 POC - Step 2: Simple Causal Forest")
    print("=" * 70)
    print()
    
    # Paths
    input_file = PROJECT_ROOT / "data" / "processed" / "ess_minimal_poc.csv"
    output_table = PROJECT_ROOT / "results" / "tables" / "poc_adoption_probabilities.csv"
    output_model = PROJECT_ROOT / "results" / "model_outputs" / "poc_forest_model.pkl"
    output_figure = PROJECT_ROOT / "results" / "figures" / "poc_heterogeneity_heatmap.png"
    
    # Create output directories
    output_table.parent.mkdir(parents=True, exist_ok=True)
    output_model.parent.mkdir(parents=True, exist_ok=True)
    output_figure.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading data from: {input_file}")
    try:
        df = pd.read_csv(input_file)
        print(f"  ✓ Loaded {len(df):,} observations")
    except Exception as e:
        print(f"  ✗ ERROR loading data: {e}")
        sys.exit(1)
    
    # Define variables
    print("\nDefining variables...")
    
    # Y: Outcome (work_time_reduction_willingness)
    Y = df['work_time_reduction_willingness'].values
    
    # T: Treatment (synthetic - use income > median as proxy)
    income_median = df['income_decile'].median()
    T = (df['income_decile'] > income_median).astype(int)
    print(f"  Treatment: income > median (decile {income_median:.1f})")
    print(f"  Treated: {T.sum():,} ({T.mean()*100:.1f}%)")
    
    # X: Features
    feature_cols = ['income_quintile', 'age', 'gender', 'education']
    
    # Encode country as dummy variables
    country_dummies = pd.get_dummies(df['country'], prefix='country')
    X_base = df[feature_cols].fillna(df[feature_cols].median())
    X = pd.concat([X_base, country_dummies], axis=1)
    
    print(f"  Features: {len(X.columns)} columns")
    print(f"    - {len(feature_cols)} numeric features")
    print(f"    - {len(country_dummies.columns)} country dummies")
    
    # Split data
    X_train, X_test, y_train, y_test, t_train, t_test = train_test_split(
        X, Y, T, test_size=0.2, random_state=42, stratify=Y
    )
    print(f"\nTrain set: {len(X_train):,} observations")
    print(f"Test set: {len(X_test):,} observations")
    
    # Train models
    print("\nTraining Random Forest models...")
    
    # Model for treated group (T=1)
    mask_treated = t_train == 1
    if mask_treated.sum() > 0:
        rf_treated = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=50,
            random_state=42,
            n_jobs=-1
        )
        rf_treated.fit(X_train[mask_treated], y_train[mask_treated])
        print(f"  ✓ Trained treated model ({mask_treated.sum():,} observations)")
    else:
        rf_treated = None
        print("  ⚠ No treated observations, using null model")
    
    # Model for control group (T=0)
    mask_control = t_train == 0
    if mask_control.sum() > 0:
        rf_control = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=50,
            random_state=42,
            n_jobs=-1
        )
        rf_control.fit(X_train[mask_control], y_train[mask_control])
        print(f"  ✓ Trained control model ({mask_control.sum():,} observations)")
    else:
        rf_control = None
        print("  ⚠ No control observations, using null model")
    
    # Predict probabilities on full dataset
    print("\nPredicting adoption probabilities...")
    
    if rf_treated is not None:
        prob_treated = rf_treated.predict_proba(X)[:, 1]
    else:
        prob_treated = np.full(len(X), y_train.mean())
    
    if rf_control is not None:
        prob_control = rf_control.predict_proba(X)[:, 1]
    else:
        prob_control = np.full(len(X), y_train.mean())
    
    # Treatment effect (simplified: just use treated probability)
    # In real causal inference, this would be τ(X) = E[Y|T=1,X] - E[Y|T=0,X]
    # For simplicity, we'll use prob_treated as adoption probability
    df['adoption_probability'] = prob_treated
    
    # Aggregate by income_quintile × country
    print("\nAggregating by income quintile × country...")
    
    # Get top 10 countries by sample size
    top_countries = df['country'].value_counts().head(10).index.tolist()
    print(f"  Top 10 countries: {', '.join(top_countries)}")
    
    # Create aggregation
    agg_data = df[df['country'].isin(top_countries)].groupby(['income_quintile', 'country']).agg({
        'adoption_probability': ['mean', 'std', 'count'],
        'work_time_reduction_willingness': 'mean'
    }).reset_index()
    
    agg_data.columns = ['income_quintile', 'country', 'adoption_prob_mean', 'adoption_prob_std', 'n', 'actual_rate']
    agg_data = agg_data.sort_values(['country', 'income_quintile'])
    
    # Create matrix for heatmap
    pivot_matrix = agg_data.pivot(index='income_quintile', columns='country', values='adoption_prob_mean')
    
    print(f"\nCreated matrix: {pivot_matrix.shape[0]} income quintiles × {pivot_matrix.shape[1]} countries")
    print(f"  Min probability: {pivot_matrix.min().min():.3f}")
    print(f"  Max probability: {pivot_matrix.max().max():.3f}")
    print(f"  Mean probability: {pivot_matrix.mean().mean():.3f}")
    
    # Save table
    print(f"\nSaving results...")
    agg_data.to_csv(output_table, index=False)
    print(f"  ✓ Saved adoption probabilities: {output_table}")
    
    # Save model
    model_data = {
        'rf_treated': rf_treated,
        'rf_control': rf_control,
        'feature_names': X.columns.tolist(),
        'top_countries': top_countries
    }
    with open(output_model, 'wb') as f:
        pickle.dump(model_data, f)
    print(f"  ✓ Saved model: {output_model}")
    
    # Generate heatmap
    print(f"\nGenerating heatmap...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sns.heatmap(
        pivot_matrix,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        center=pivot_matrix.mean().mean(),
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Adoption Probability'},
        ax=ax
    )
    
    ax.set_title('Predicted Work-Time Reduction Adoption by Income & Country', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Income Quintile (1=Lowest, 5=Highest)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_figure, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved heatmap: {output_figure}")
    plt.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nAdoption probability range: {pivot_matrix.min().min():.3f} to {pivot_matrix.max().max():.3f}")
    
    max_idx = pivot_matrix.stack().idxmax()
    print(f"Highest adoption: Quintile {max_idx[0]} in {max_idx[1]} ({pivot_matrix.loc[max_idx[0], max_idx[1]]:.3f})")
    
    min_idx = pivot_matrix.stack().idxmin()
    print(f"Lowest adoption: Quintile {min_idx[0]} in {min_idx[1]} ({pivot_matrix.loc[min_idx[0], min_idx[1]]:.3f})")
    
    # Income effect
    income_effect = pivot_matrix.mean(axis=1)
    print(f"\nIncome effect (average across countries):")
    for quintile, prob in income_effect.items():
        print(f"  Quintile {quintile}: {prob:.3f}")
    
    print("\n" + "=" * 70)
    print("STEP 2 COMPLETE")
    print("=" * 70)
    print(f"Heatmap: {output_figure}")
    print(f"Table: {output_table}")
    print("=" * 70)
    
    return agg_data, pivot_matrix


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


