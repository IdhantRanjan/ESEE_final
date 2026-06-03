#!/usr/bin/env python3
"""
Eurostat Employment Data Validation Script

Validates the real Eurostat employment data file with comprehensive checks.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# EU27 country codes
EU27_COUNTRIES = {
    'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR',
    'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO',
    'SE', 'SI', 'SK'
}

# Expected years
EXPECTED_YEARS = ['2020', '2021', '2022', '2023']


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """Main validation function."""
    print("=" * 70)
    print("EUROSTAT EMPLOYMENT DATA VALIDATION")
    print("=" * 70)
    print()
    
    # File path
    data_file = PROJECT_ROOT / "data" / "raw" / "eurostat_employment.csv"
    
    if not data_file.exists():
        print(f"✗ ERROR: File not found: {data_file}")
        print("Please ensure the file exists and try again.")
        sys.exit(1)
    
    # File info
    file_size = data_file.stat().st_size
    print(f"FILE INFO:")
    print(f"  Path: {data_file}")
    print(f"  Size: {format_size(file_size)}")
    print()
    
    # Load data
    print("Loading data...")
    try:
        # Try different separators and encodings
        df = None
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(data_file, sep=sep, low_memory=False)
                if len(df.columns) > 1:
                    print(f"  ✓ Successfully loaded with separator: '{sep}'")
                    break
            except:
                continue
        
        if df is None:
            print("  ✗ ERROR: Could not parse CSV file")
            sys.exit(1)
        
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print()
    except Exception as e:
        print(f"  ✗ ERROR loading file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Column information
    print("=" * 70)
    print("DATA STRUCTURE")
    print("=" * 70)
    print("\nCOLUMN NAMES:")
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        print(f"  {i:2d}. {col:30s} | Type: {dtype:15s} | Non-null: {non_null:6,} | Null: {null_count:6,}")
    
    # Find value column
    value_column = None
    possible_value_cols = ['OBS_VALUE', 'values', 'obs_value', 'value', 'VALUES', 'obsValue']
    for col in df.columns:
        if col in possible_value_cols:
            value_column = col
            break
    
    # If not found, try to identify numeric column
    if value_column is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            # Use the numeric column with most non-null values
            value_column = numeric_cols[df[numeric_cols].notna().sum().idxmax()]
            print(f"\n  ⚠ Value column not found with expected name, using: {value_column}")
        else:
            print("\n  ✗ ERROR: Could not identify value column")
            value_column = None
    
    if value_column:
        print(f"\nKEY COLUMN (values): {value_column}")
    print()
    
    # First and last rows
    print("=" * 70)
    print("DATA PREVIEW")
    print("=" * 70)
    print("\nFIRST 20 ROWS:")
    print(df.head(20).to_string(max_rows=20))
    print("\nLAST 5 ROWS:")
    print(df.tail(5).to_string(max_rows=5))
    print()
    
    # Geography analysis
    print("=" * 70)
    print("GEOGRAPHY ANALYSIS")
    print("=" * 70)
    
    # Find geography column
    geo_column = None
    possible_geo_cols = ['geo', 'GEO', 'GEOGRAPHY', 'country', 'COUNTRY', 'GEO\\TIME']
    for col in df.columns:
        if col in possible_geo_cols or 'geo' in col.lower():
            geo_column = col
            break
    
    if geo_column is None:
        print("  ✗ ERROR: Could not identify geography column")
    else:
        print(f"\nGeography column: {geo_column}")
        unique_geos = sorted(df[geo_column].unique())
        print(f"Total entities: {len(unique_geos)}")
        print(f"\nALL COUNTRIES/REGIONS FOUND ({len(unique_geos)}):")
        for i, geo in enumerate(unique_geos, 1):
            count = (df[geo_column] == geo).sum()
            print(f"  {i:2d}. {geo:10s} ({count:4,} observations)")
        
        # Check EU27 countries
        eu27_found = set(unique_geos) & EU27_COUNTRIES
        eu27_missing = EU27_COUNTRIES - set(unique_geos)
        
        print(f"\nEU27 COUNTRIES:")
        print(f"  Found: {len(eu27_found)}/27")
        if eu27_found:
            print(f"  Countries: {', '.join(sorted(eu27_found))}")
        if eu27_missing:
            print(f"  ✗ Missing: {', '.join(sorted(eu27_missing))}")
        else:
            print(f"  ✓ All EU27 countries present")
        
        # Aggregates
        aggregates = [g for g in unique_geos if g not in EU27_COUNTRIES]
        if aggregates:
            print(f"\nAGGREGATES FOUND ({len(aggregates)}):")
            for agg in sorted(aggregates):
                print(f"  - {agg}")
    
    # Time analysis
    print("\n" + "=" * 70)
    print("TIME COVERAGE")
    print("=" * 70)
    
    # Find time column - prioritize TIME_PERIOD
    time_column = None
    # First check for exact match to TIME_PERIOD
    if 'TIME_PERIOD' in df.columns:
        time_column = 'TIME_PERIOD'
    else:
        possible_time_cols = ['time', 'TIME', 'year', 'YEAR', 'date', 'DATE']
        for col in df.columns:
            if col in possible_time_cols:
                time_column = col
                break
        # Last resort: look for time/period in name
        if time_column is None:
            for col in df.columns:
                if ('time' in col.lower() or 'period' in col.lower()) and 'frequency' not in col.lower():
                    time_column = col
                    break
    
    if time_column is None:
        print("  ✗ ERROR: Could not identify time column")
    else:
        print(f"\nTime column: {time_column}")
        unique_times = sorted([str(t) for t in df[time_column].unique()])
        print(f"Unique time periods: {len(unique_times)}")
        print(f"Values: {', '.join(unique_times[:20])}")
        if len(unique_times) > 20:
            print(f"  ... and {len(unique_times) - 20} more")
        
        # Check for expected years
        years_found = [y for y in EXPECTED_YEARS if y in unique_times]
        years_missing = [y for y in EXPECTED_YEARS if y not in unique_times]
        
        print(f"\nEXPECTED YEARS (2020-2023):")
        if years_found:
            print(f"  ✓ Found: {', '.join(years_found)}")
        if years_missing:
            print(f"  ✗ Missing: {', '.join(years_missing)}")
        
        # Check completeness by country
        if geo_column and time_column:
            print(f"\nDATA COMPLETENESS BY COUNTRY:")
            complete_countries = []
            incomplete_countries = []
            
            for geo in unique_geos:
                geo_data = df[df[geo_column] == geo]
                years_for_geo = [str(t) for t in geo_data[time_column].unique()]
                if all(y in years_for_geo for y in EXPECTED_YEARS):
                    complete_countries.append(geo)
                else:
                    missing_years = [y for y in EXPECTED_YEARS if y not in years_for_geo]
                    incomplete_countries.append((geo, missing_years))
            
            print(f"  Countries with complete data (all 4 years): {len(complete_countries)}")
            if len(complete_countries) <= 30:
                print(f"    {', '.join(sorted(complete_countries))}")
            
            if incomplete_countries:
                print(f"\n  Countries with missing data: {len(incomplete_countries)}")
                for geo, missing in sorted(incomplete_countries)[:20]:
                    print(f"    - {geo}: missing {', '.join(missing)}")
                if len(incomplete_countries) > 20:
                    print(f"    ... and {len(incomplete_countries) - 20} more")
    
    # Value analysis
    print("\n" + "=" * 70)
    print("DATA QUALITY - EMPLOYMENT VALUES")
    print("=" * 70)
    
    if value_column:
        values = df[value_column]
        
        # Convert to numeric
        numeric_values = pd.to_numeric(values, errors='coerce')
        
        print(f"\nColumn: {value_column}")
        print(f"Data type: {df[value_column].dtype}")
        print(f"Total non-null values: {numeric_values.notna().sum():,}")
        print(f"Missing values: {numeric_values.isna().sum():,} ({numeric_values.isna().sum() / len(numeric_values) * 100:.1f}%)")
        
        if numeric_values.notna().sum() > 0:
            print(f"\nSTATISTICS:")
            print(f"  Min: {numeric_values.min():,.0f} thousand persons")
            print(f"  Max: {numeric_values.max():,.0f} thousand persons")
            print(f"  Mean: {numeric_values.mean():,.0f} thousand persons")
            print(f"  Median: {numeric_values.median():,.0f} thousand persons")
            print(f"  Std Dev: {numeric_values.std():,.0f} thousand persons")
            
            # Value range checks (exclude aggregates from high-value check)
            print(f"\nVALUE RANGE CHECKS:")
            issues = []
            if (numeric_values < 0).any():
                issues.append(f"Found {(numeric_values < 0).sum()} negative values")
            
            # Check high values only for individual countries (not aggregates)
            if geo_column:
                # Known aggregate codes (non-EU27 countries)
                aggregates_list = aggregates if 'aggregates' in locals() else []
                individual_countries_mask = df[geo_column].isin(EU27_COUNTRIES)
                individual_values = numeric_values[individual_countries_mask]
                
                if (individual_values > 100000).any():
                    issues.append(f"Found {(individual_values > 100000).sum()} individual country values > 100,000 (suspiciously high)")
                elif (numeric_values > 100000).any():
                    high_count = (numeric_values > 100000).sum()
                    print(f"  ℹ {high_count} values > 100,000 are from aggregates (EA20, EU27_2020) - this is expected")
            else:
                if (numeric_values > 100000).any():
                    issues.append(f"Found {(numeric_values > 100000).sum()} values > 100,000 (suspiciously high)")
            
            if numeric_values.isna().sum() > len(numeric_values) * 0.1:
                issues.append(f"High missing value rate: {numeric_values.isna().sum() / len(numeric_values) * 100:.1f}%")
            
            if issues:
                print(f"  ✗ ISSUES FOUND:")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print(f"  ✓ All checks passed")
    else:
        print("\n  ✗ Cannot analyze values - value column not identified")
    
    # Generate report
    print("\n" + "=" * 70)
    print("GENERATING REPORT")
    print("=" * 70)
    
    report_lines = [
        "=" * 70,
        "EUROSTAT EMPLOYMENT DATA VALIDATION",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "FILE INFO:",
        f"Path: {data_file}",
        f"Size: {format_size(file_size)}",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns)}",
        "",
        "DATA STRUCTURE:",
        "Columns:",
    ]
    
    for col in df.columns:
        report_lines.append(f"  - {col} ({df[col].dtype})")
    
    if value_column:
        report_lines.append(f"Key column (values): {value_column}")
    
    report_lines.extend([
        "",
        "GEOGRAPHY:",
        f"Total entities: {len(unique_geos) if geo_column else 'N/A'}",
        f"EU27 countries: {len(eu27_found) if geo_column else 'N/A'}/27 {'✓' if geo_column and len(eu27_found) == 27 else '✗'}",
    ])
    
    if geo_column:
        if eu27_missing:
            report_lines.append(f"Missing countries: {', '.join(sorted(eu27_missing))}")
        else:
            report_lines.append("Missing countries: None")
        if aggregates:
            report_lines.append(f"Aggregates found: {', '.join(sorted(aggregates))}")
    
    report_lines.extend([
        "",
        "TIME COVERAGE:",
        f"Years: {', '.join(years_found if time_column else [])} {'✓' if time_column and len(years_found) == len(EXPECTED_YEARS) else '✗'}",
    ])
    
    if geo_column and time_column:
        report_lines.append(f"Countries with complete data (all 4 years): {len(complete_countries)}")
        if incomplete_countries:
            report_lines.append(f"Countries with missing data: {len(incomplete_countries)}")
            for geo, missing in sorted(incomplete_countries)[:10]:
                report_lines.append(f"  - {geo}: missing {', '.join(missing)}")
    
    report_lines.extend([
        "",
        "DATA QUALITY:",
        "Employment values:",
    ])
    
    if value_column:
        numeric_values = pd.to_numeric(df[value_column], errors='coerce')
        report_lines.extend([
            f"  Min: {numeric_values.min():,.0f} thousand persons",
            f"  Max: {numeric_values.max():,.0f} thousand persons",
            f"  Mean: {numeric_values.mean():,.0f} thousand persons",
            f"  Missing values: {numeric_values.isna().sum():,} ({numeric_values.isna().sum() / len(numeric_values) * 100:.1f}%)",
            f"  Data type: {df[value_column].dtype}",
        ])
        
        # Determine status (check individual countries only for high values)
        value_status = "VALID ✓"
        if (numeric_values < 0).any():
            value_status = "ISSUES ✗"
        elif geo_column:
            individual_countries_mask = df[geo_column].isin(EU27_COUNTRIES)
            individual_values = pd.to_numeric(df.loc[individual_countries_mask, value_column], errors='coerce')
            if (individual_values > 100000).any():
                value_status = "ISSUES ✗"
        elif (numeric_values > 100000).any():
            value_status = "ISSUES ✗"
        report_lines.append(f"  Value range: {value_status}")
    
    # Overall status
    all_issues = []
    if geo_column and len(eu27_found) < 27:
        all_issues.append(f"Missing {27 - len(eu27_found)} EU27 countries")
    if time_column and len(years_found) < len(EXPECTED_YEARS):
        all_issues.append(f"Missing years: {', '.join(years_missing)}")
    if value_column:
        numeric_values = pd.to_numeric(df[value_column], errors='coerce')
        if (numeric_values < 0).any():
            all_issues.append("Negative values found")
        # Check high values only for individual countries
        if geo_column:
            individual_countries_mask = df[geo_column].isin(EU27_COUNTRIES)
            individual_values = numeric_values[individual_countries_mask]
            if (individual_values > 100000).any():
                all_issues.append("Suspiciously high values in individual countries")
        else:
            if (numeric_values > 100000).any():
                all_issues.append("Suspiciously high values found")
    
    if not all_issues:
        overall_status = "✓ VALID"
    elif len(all_issues) <= 2:
        overall_status = "⚠ WARNINGS"
    else:
        overall_status = "✗ CRITICAL ISSUES"
    
    report_lines.extend([
        "",
        "OVERALL STATUS:",
        overall_status,
        "Issues found:",
    ])
    
    if all_issues:
        for issue in all_issues:
            report_lines.append(f"  - {issue}")
    else:
        report_lines.append("  None")
    
    report_lines.extend([
        "",
        f"READY FOR PREPROCESSING: {'YES' if overall_status.startswith('✓') else 'NO'}",
        "=" * 70,
    ])
    
    report_text = "\n".join(report_lines)
    
    # Save report
    logs_dir = PROJECT_ROOT / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_file = logs_dir / "eurostat_real_validation.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"  ✓ Report saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Overall Status: {overall_status}")
    if all_issues:
        print("\nIssues:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("\n✓ No issues detected")
    print(f"\nReady for preprocessing: {'YES' if overall_status.startswith('✓') else 'NO'}")
    print("=" * 70)
    
    return {
        'status': overall_status,
        'issues': all_issues,
        'geo_column': geo_column,
        'time_column': time_column,
        'value_column': value_column,
    }


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

