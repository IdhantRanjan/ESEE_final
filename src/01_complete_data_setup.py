#!/usr/bin/env python3
"""
ESEE 2026 Degrowth ABM Project - Complete Data Setup & Validation Script

This script handles:
1. Extraction of ESS (European Social Survey) data from ZIP files
2. Download of Eurostat employment data via API (with synthetic fallback)
3. Extraction of Exiobase input-output tables from ZIP files
4. Comprehensive validation of all datasets
5. Generation of detailed validation reports

Author: ESEE 2026 Research Team
Date: 2025
"""

import os
import sys
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# PART 1: EXTRACT ESS DATA
# ============================================================================

def extract_ess_data() -> bool:
    """
    Extract ESS data from ZIP files in project root or data/raw/.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("PART 1: EXTRACTING ESS DATA")
    print("="*70)
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)
    
    # ESS10 extraction
    ess10_zip_paths = [
        project_root / "ESS10e03_3.zip",
        data_raw / "ESS10e03_3.zip",
    ]
    
    ess10_zip = None
    for path in ess10_zip_paths:
        if path.exists():
            ess10_zip = path
            print(f"✓ Found ESS10 ZIP: {path}")
            break
    
    if ess10_zip is None:
        print("✗ ERROR: ESS10e03_3.zip not found in project root or data/raw/")
        return False
    
    try:
        print(f"Extracting {ess10_zip.name}...")
        with zipfile.ZipFile(ess10_zip, 'r') as zip_ref:
            # List contents
            file_list = zip_ref.namelist()
            print(f"  Contents: {file_list}")
            
            # Extract all files to temporary location
            temp_dir = data_raw / "temp_ess10"
            temp_dir.mkdir(exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # Find CSV and HTML files
            csv_file = None
            html_file = None
            
            for file in file_list:
                if file.endswith('.csv'):
                    csv_file = temp_dir / file
                elif file.endswith('.html'):
                    html_file = temp_dir / file
            
            if csv_file and csv_file.exists():
                # Move CSV to final location
                target_csv = data_raw / "ESS10.csv"
                shutil.move(str(csv_file), str(target_csv))
                print(f"  ✓ Extracted CSV to: {target_csv}")
            else:
                print("  ✗ ERROR: No CSV file found in ZIP")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return False
            
            if html_file and html_file.exists():
                target_html = data_raw / "ESS10_codebook.html"
                shutil.move(str(html_file), str(target_html))
                print(f"  ✓ Extracted codebook to: {target_html}")
            
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        # Optional: Delete ZIP file after successful extraction
        # Uncomment next lines if you want to delete ZIP files
        # ess10_zip.unlink()
        # print(f"  ✓ Deleted ZIP file: {ess10_zip}")
        
        print("✓ ESS10 extraction completed successfully")
        
    except Exception as e:
        print(f"✗ ERROR extracting ESS10: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ESS9 extraction (optional, for robustness)
    ess9_zip_paths = [
        project_root / "ESS9MTMMe03.zip",
        data_raw / "ESS9MTMMe03.zip",
    ]
    
    ess9_zip = None
    for path in ess9_zip_paths:
        if path.exists():
            ess9_zip = path
            print(f"\n✓ Found ESS9 ZIP: {path}")
            break
    
    if ess9_zip:
        try:
            print(f"Extracting {ess9_zip.name}...")
            with zipfile.ZipFile(ess9_zip, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"  Contents: {file_list}")
                
                temp_dir = data_raw / "temp_ess9"
                temp_dir.mkdir(exist_ok=True)
                zip_ref.extractall(temp_dir)
                
                csv_file = None
                html_file = None
                for file in file_list:
                    if file.endswith('.csv'):
                        csv_file = temp_dir / file
                    elif file.endswith('.html'):
                        html_file = temp_dir / file
                
                if csv_file and csv_file.exists():
                    target_csv = data_raw / "ESS9.csv"
                    shutil.move(str(csv_file), str(target_csv))
                    print(f"  ✓ Extracted CSV to: {target_csv}")
                
                if html_file and html_file.exists():
                    target_html = data_raw / "ESS9_codebook.html"
                    shutil.move(str(html_file), str(target_html))
                    print(f"  ✓ Extracted codebook to: {target_html}")
                
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            print("✓ ESS9 extraction completed successfully")
        except Exception as e:
            print(f"⚠ WARNING: ESS9 extraction failed (non-critical): {e}")
    
    return True


# ============================================================================
# PART 2: DOWNLOAD EUROSTAT DATA
# ============================================================================

def install_eurostat() -> bool:
    """Install eurostat package if not available."""
    try:
        import eurostat
        return True
    except ImportError:
        print("  Installing eurostat package...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "eurostat", "--quiet"
            ])
            import eurostat
            print("  ✓ eurostat installed successfully")
            return True
        except Exception as e:
            print(f"  ✗ Failed to install eurostat: {e}")
            return False


def download_eurostat_data() -> str:
    """
    Download Eurostat employment data via API.
    
    Returns:
        'success' if real data downloaded, 'synthetic' if fallback used, 'failed' if total failure
    """
    print("\n" + "="*70)
    print("PART 2: DOWNLOADING EUROSTAT DATA")
    print("="*70)
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Install eurostat if needed
    if not install_eurostat():
        print("  ⚠ Falling back to synthetic data...")
        return create_synthetic_eurostat_data()
    
    try:
        import eurostat
        
        print("  Downloading dataset: 'lfsi_emp_a' (annual employment)...")
        
        # Download data
        dataset_code = 'lfsi_emp_a'
        filters = {
            'sex': 'T',  # Total
            'age': 'Y15-64',  # Working age
            'unit': 'THS',  # Thousands
        }
        
        try:
            df = eurostat.get_data_df(dataset_code, filters=filters)
            print(f"  ✓ Downloaded {len(df)} rows")
        except Exception as e:
            print(f"  ✗ API download failed: {e}")
            print("  ⚠ Falling back to synthetic data...")
            return create_synthetic_eurostat_data()
        
        if df is None or df.empty:
            print("  ✗ Downloaded data is empty")
            print("  ⚠ Falling back to synthetic data...")
            return create_synthetic_eurostat_data()
        
        # Clean the data
        print("  Cleaning downloaded data...")
        
        # Remove flag/note columns
        cols_to_drop = [col for col in df.columns if 'flag' in col.lower() or 'note' in col.lower()]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            print(f"    Dropped {len(cols_to_drop)} flag/note columns")
        
        # Ensure we have geo, time, values
        # Eurostat data structure varies, need to handle flexibly
        if 'geo\\time' in df.columns:
            df = df.rename(columns={'geo\\time': 'geo'})
            # Pivot if time is in columns
            time_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
            if time_cols:
                df = df.melt(id_vars=['geo'], value_vars=time_cols, 
                            var_name='time', value_name='values')
        elif 'geo' not in df.columns:
            # Try to find geo column
            geo_cols = [col for col in df.columns if 'geo' in col.lower()]
            if geo_cols:
                df = df.rename(columns={geo_cols[0]: 'geo'})
            else:
                print("  ✗ Cannot find geo column in downloaded data")
                print("  ⚠ Falling back to synthetic data...")
                return create_synthetic_eurostat_data()
        
        # Convert values to numeric
        if 'values' in df.columns:
            df['values'] = pd.to_numeric(df['values'], errors='coerce')
        
        # Filter to 2020-2023
        if 'time' in df.columns:
            df = df[df['time'].astype(str).isin(['2020', '2021', '2022', '2023'])]
        
        # Sort
        if 'geo' in df.columns and 'time' in df.columns:
            df = df.sort_values(['geo', 'time'])
        
        # Validate
        print("  Validating downloaded data...")
        validation_passed = True
        
        if 'geo' in df.columns:
            unique_countries = df['geo'].nunique()
            print(f"    Countries: {unique_countries}")
            if unique_countries < 20:
                print(f"    ⚠ WARNING: Only {unique_countries} countries found (expected >=20)")
                validation_passed = False
        else:
            validation_passed = False
        
        if 'time' in df.columns:
            unique_years = sorted(df['time'].unique())
            print(f"    Years: {unique_years}")
            required_years = ['2020', '2021', '2022', '2023']
            if not all(str(y) in [str(x) for x in unique_years] for y in required_years):
                print(f"    ⚠ WARNING: Missing some required years")
                validation_passed = False
        
        if not validation_passed:
            print("  ⚠ Validation failed, falling back to synthetic data...")
            return create_synthetic_eurostat_data()
        
        # Save
        output_path = data_raw / "eurostat_employment.csv"
        df.to_csv(output_path, index=False)
        print(f"  ✓ Saved to: {output_path}")
        
        # Create summary
        summary_lines = [
            "EUROSTAT DATA DOWNLOAD SUMMARY",
            "=" * 50,
            f"Download time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Dataset: {dataset_code}",
            f"Source: Eurostat API",
            f"",
            f"Number of countries: {df['geo'].nunique() if 'geo' in df.columns else 'N/A'}",
            f"Years covered: {sorted(df['time'].unique()) if 'time' in df.columns else 'N/A'}",
            f"Total observations: {len(df)}",
            f"",
        ]
        
        if 'geo' in df.columns and 'time' in df.columns:
            # Countries with complete data
            complete = df.groupby('geo')['time'].count()
            complete_countries = complete[complete >= 4].index.tolist()
            summary_lines.append(f"Countries with complete data (4 years): {len(complete_countries)}")
            summary_lines.append(f"  {', '.join(complete_countries[:10])}...")
            
            missing_countries = complete[complete < 4].index.tolist()
            if missing_countries:
                summary_lines.append(f"Countries with missing data: {len(missing_countries)}")
                summary_lines.append(f"  {', '.join(missing_countries)}")
        
        summary_text = "\n".join(summary_lines)
        log_path = logs_dir / "eurostat_download_log.txt"
        with open(log_path, 'w') as f:
            f.write(summary_text)
        print(f"  ✓ Summary saved to: {log_path}")
        
        return 'success'
        
    except Exception as e:
        print(f"  ✗ ERROR downloading Eurostat data: {e}")
        import traceback
        traceback.print_exc()
        print("  ⚠ Falling back to synthetic data...")
        return create_synthetic_eurostat_data()


def create_synthetic_eurostat_data() -> str:
    """Create synthetic Eurostat data as fallback."""
    print("  Creating synthetic Eurostat employment data...")
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    logs_dir = project_root / "results" / "logs"
    
    # EU27 countries with approximate employment (in thousands, 2020)
    eu_countries = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    ]
    
    # Base employment values (approximate, in thousands)
    base_employment = {
        'DE': 40000, 'FR': 27000, 'IT': 23000, 'ES': 20000, 'PL': 17000,
        'NL': 9000, 'RO': 9000, 'BE': 5000, 'SE': 5000, 'AT': 4500,
        'PT': 5000, 'CZ': 5000, 'GR': 4000, 'HU': 4500, 'FI': 2700,
        'DK': 3000, 'IE': 2300, 'SK': 2700, 'HR': 1700, 'BG': 3300,
        'LT': 1400, 'SI': 1000, 'LV': 950, 'EE': 700, 'LU': 300,
        'CY': 400, 'MT': 220
    }
    
    # Create data
    data = []
    years = ['2020', '2021', '2022', '2023']
    
    for country in eu_countries:
        base = base_employment.get(country, 2000)
        for i, year in enumerate(years):
            # Add small variation over years
            value = base * (1 + 0.01 * i + np.random.normal(0, 0.02))
            data.append({
                'geo': country,
                'time': year,
                'values': max(100, int(value)),  # Ensure positive
                'synthetic': True
            })
    
    df = pd.DataFrame(data)
    
    # Save
    output_path = data_raw / "eurostat_employment_SYNTHETIC.csv"
    df.to_csv(output_path, index=False)
    print(f"  ✓ Saved synthetic data to: {output_path}")
    
    # Log
    log_path = logs_dir / "eurostat_download_log.txt"
    with open(log_path, 'w') as f:
        f.write("EUROSTAT DATA - SYNTHETIC FALLBACK\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("WARNING: This is synthetic data, not real Eurostat data!\n")
        f.write("The Eurostat API download failed or was unavailable.\n\n")
        f.write(f"Countries: {len(eu_countries)}\n")
        f.write(f"Years: {years}\n")
        f.write(f"Total observations: {len(df)}\n")
    
    print("  ⚠ WARNING: Using synthetic data - not suitable for real analysis!")
    return 'synthetic'


# ============================================================================
# PART 3: EXTRACT EXIOBASE DATA
# ============================================================================

def extract_exiobase_data() -> bool:
    """
    Extract Exiobase input-output tables from ZIP files.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("PART 3: EXTRACTING EXIOBASE DATA")
    print("="*70)
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find Exiobase ZIP files (check both with and without (1) suffix)
    iot_zip_paths = [
        data_raw / "IOT_2020_pxp.zip",
        project_root / "IOT_2020_pxp.zip",
        data_raw / "IOT_2020_pxp (1).zip",
        project_root / "IOT_2020_pxp (1).zip",
    ]
    
    mrsut_zip_paths = [
        data_raw / "MRSUT_2020.zip",
        project_root / "MRSUT_2020.zip",
        data_raw / "MRSUT_2020 (1).zip",
        project_root / "MRSUT_2020 (1).zip",
    ]
    
    iot_zip = None
    mrsut_zip = None
    
    for path in iot_zip_paths:
        if path.exists():
            iot_zip = path
            print(f"✓ Found IOT ZIP: {path}")
            break
    
    for path in mrsut_zip_paths:
        if path.exists():
            mrsut_zip = path
            print(f"✓ Found MRSUT ZIP: {path}")
            break
    
    if iot_zip is None and mrsut_zip is None:
        print("✗ ERROR: No Exiobase ZIP files found")
        print("  Expected: IOT_2020_pxp.zip and/or MRSUT_2020.zip")
        return False
    
    # Create extraction directory
    exiobase_dir = data_raw / "exiobase3"
    exiobase_dir.mkdir(exist_ok=True)
    print(f"  Extraction directory: {exiobase_dir}")
    
    extracted_files = []
    
    # Extract IOT
    if iot_zip:
        try:
            print(f"\n  Extracting {iot_zip.name}...")
            with zipfile.ZipFile(iot_zip, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                zip_ref.extractall(exiobase_dir)
                extracted_files.extend(file_list)
                print(f"    ✓ Extracted {len(file_list)} files")
        except Exception as e:
            print(f"    ✗ ERROR extracting IOT: {e}")
            return False
    
    # Extract MRSUT
    if mrsut_zip:
        try:
            print(f"\n  Extracting {mrsut_zip.name}...")
            with zipfile.ZipFile(mrsut_zip, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                zip_ref.extractall(exiobase_dir)
                extracted_files.extend(file_list)
                print(f"    ✓ Extracted {len(file_list)} files")
        except Exception as e:
            print(f"    ✗ ERROR extracting MRSUT: {e}")
            return False
    
    # Look for key files
    print("\n  Looking for key Exiobase files...")
    key_patterns = ['A.txt', 'A.csv', 'Y.txt', 'Y.csv', 'F.txt', 'F.csv']
    found_files = []
    
    for pattern in key_patterns:
        matches = list(exiobase_dir.rglob(pattern))
        if matches:
            found_files.extend([str(f.relative_to(exiobase_dir)) for f in matches])
            print(f"    ✓ Found: {pattern}")
    
    # Try to validate a matrix file
    matrix_file = None
    for pattern in ['A.txt', 'A.csv']:
        matches = list(exiobase_dir.rglob(pattern))
        if matches:
            matrix_file = matches[0]
            break
    
    if matrix_file:
        try:
            print(f"\n  Validating matrix file: {matrix_file.name}...")
            # Try reading first few rows
            if matrix_file.suffix == '.txt':
                df_sample = pd.read_csv(matrix_file, sep='\t', nrows=10)
            else:
                df_sample = pd.read_csv(matrix_file, nrows=10)
            
            print(f"    ✓ File is readable")
            print(f"    Shape (first 10 rows): {df_sample.shape}")
            print(f"    Columns: {list(df_sample.columns)[:5]}...")
            
        except Exception as e:
            print(f"    ⚠ Could not validate matrix file: {e}")
    
    # Create inventory
    all_files = [str(f.relative_to(exiobase_dir)) for f in exiobase_dir.rglob('*') if f.is_file()]
    inventory = [
        "EXIOBASE EXTRACTION INVENTORY",
        "=" * 50,
        f"Extraction time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Extraction directory: {exiobase_dir}",
        f"",
        f"Total files extracted: {len(all_files)}",
        f"",
        "Key files found:",
    ]
    
    for pattern in key_patterns:
        matches = [f for f in all_files if f.endswith(pattern)]
        if matches:
            inventory.append(f"  {pattern}: {len(matches)} file(s)")
            for match in matches[:3]:  # Show first 3
                inventory.append(f"    - {match}")
            if len(matches) > 3:
                inventory.append(f"    ... and {len(matches) - 3} more")
    
    inventory.append("")
    inventory.append("All files:")
    for f in sorted(all_files)[:50]:  # First 50 files
        inventory.append(f"  {f}")
    if len(all_files) > 50:
        inventory.append(f"  ... and {len(all_files) - 50} more files")
    
    inventory_text = "\n".join(inventory)
    log_path = logs_dir / "exiobase_extraction_log.txt"
    with open(log_path, 'w') as f:
        f.write(inventory_text)
    print(f"\n  ✓ Inventory saved to: {log_path}")
    
    print("\n  NOTE: ZIP files are preserved. Delete manually if needed.")
    print("        Consider keeping them as backup.")
    
    return True


# ============================================================================
# PART 4: VALIDATE ALL DATA
# ============================================================================

def validate_ess10() -> Dict[str, Any]:
    """Validate ESS10 dataset."""
    print("\n  Validating ESS10 dataset...")
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    ess10_path = data_raw / "ESS10.csv"
    results = {
        'status': 'missing',
        'location': str(ess10_path),
        'rows': 0,
        'countries': [],
        'critical_columns': {},
        'policy_variables': [],
        'missing_data': {},
        'issues': []
    }
    
    if not ess10_path.exists():
        results['issues'].append("ESS10.csv not found")
        return results
    
    try:
        print(f"    Loading {ess10_path}...")
        df = pd.read_csv(ess10_path, low_memory=False)
        results['rows'] = len(df)
        results['status'] = 'valid'
        
        file_size_mb = ess10_path.stat().st_size / (1024 * 1024)
        print(f"    File size: {file_size_mb:.1f} MB")
        print(f"    Rows: {len(df)}")
        print(f"    Columns: {len(df.columns)}")
        
        # Check file size
        if file_size_mb < 30 or file_size_mb > 150:
            results['issues'].append(f"File size ({file_size_mb:.1f} MB) outside expected range (50-100 MB)")
        
        # Check row count
        if len(df) < 30000 or len(df) > 100000:
            results['issues'].append(f"Row count ({len(df)}) outside expected range (40,000-60,000)")
        
        # Critical columns
        critical_cols = {
            'idno': 'respondent ID',
            'cntry': 'country code',
            'agea': 'age',
            'gndr': 'gender',
            'eisced': 'education',
            'hinctnta': 'household income decile',
            'emplrel': 'employment relation',
            'isco08': 'occupation code (for sector)',
        }
        
        print("\n    Checking critical columns...")
        for col, desc in critical_cols.items():
            if col in df.columns:
                results['critical_columns'][col] = 'present'
                missing_pct = df[col].isna().sum() / len(df) * 100
                results['missing_data'][col] = f"{missing_pct:.1f}%"
                print(f"      ✓ {col} ({desc}): {missing_pct:.1f}% missing")
            else:
                results['critical_columns'][col] = 'missing'
                results['issues'].append(f"Missing critical column: {col} ({desc})")
                print(f"      ✗ {col} ({desc}): MISSING")
        
        # Policy/attitude variables
        print("\n    Searching for policy/attitude variables...")
        policy_keywords = {
            'work': ['wrk', 'work', 'job', 'employ'],
            'environment': ['env', 'climate', 'green', 'sustain'],
            'consumption': ['consum', 'buy', 'income'],
        }
        
        all_cols_lower = [c.lower() for c in df.columns]
        for category, keywords in policy_keywords.items():
            matches = [col for col in df.columns 
                      if any(kw in col.lower() for kw in keywords)]
            if matches:
                results['policy_variables'].extend(matches)
                print(f"      {category}: {len(matches)} variable(s) found")
                for match in matches[:5]:
                    print(f"        - {match}")
                if len(matches) > 5:
                    print(f"        ... and {len(matches) - 5} more")
        
        # Country distribution
        if 'cntry' in df.columns:
            countries = df['cntry'].value_counts()
            results['countries'] = countries.index.tolist()
            print(f"\n    Countries found: {len(countries)}")
            print(f"      Top 5: {', '.join(countries.head().index.tolist())}")
            if len(countries) < 10:
                results['issues'].append(f"Only {len(countries)} countries found (expected more)")
        
        # Save detailed report
        report_lines = [
            "ESS10 VALIDATION REPORT",
            "=" * 50,
            f"Validation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Location: {ess10_path}",
            f"",
            f"File size: {file_size_mb:.1f} MB",
            f"Rows: {len(df)}",
            f"Columns: {len(df.columns)}",
            f"",
            "CRITICAL COLUMNS:",
        ]
        
        for col, desc in critical_cols.items():
            status = results['critical_columns'].get(col, 'missing')
            missing_pct = results['missing_data'].get(col, 'N/A')
            report_lines.append(f"  {col} ({desc}): {status} - {missing_pct} missing")
        
        report_lines.extend([
            "",
            f"POLICY VARIABLES FOUND: {len(results['policy_variables'])}",
        ])
        for var in results['policy_variables'][:20]:
            report_lines.append(f"  - {var}")
        
        report_lines.extend([
            "",
            f"COUNTRIES: {len(results['countries'])}",
            f"  {', '.join(results['countries'][:20])}",
            "",
            "ISSUES:",
        ])
        if results['issues']:
            for issue in results['issues']:
                report_lines.append(f"  - {issue}")
        else:
            report_lines.append("  None")
        
        report_text = "\n".join(report_lines)
        report_path = logs_dir / "ess10_validation.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"\n    ✓ Detailed report saved to: {report_path}")
        
    except Exception as e:
        results['status'] = 'error'
        results['issues'].append(f"Error loading file: {e}")
        print(f"    ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return results


def validate_eurostat() -> Dict[str, Any]:
    """Validate Eurostat employment data."""
    print("\n  Validating Eurostat employment data...")
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for real or synthetic file
    real_path = data_raw / "eurostat_employment.csv"
    synthetic_path = data_raw / "eurostat_employment_SYNTHETIC.csv"
    
    data_path = None
    is_synthetic = False
    
    if real_path.exists():
        data_path = real_path
    elif synthetic_path.exists():
        data_path = synthetic_path
        is_synthetic = True
    else:
        return {
            'status': 'missing',
            'location': 'not found',
            'source': 'none',
            'issues': ['Eurostat file not found']
        }
    
    results = {
        'status': 'valid',
        'location': str(data_path),
        'source': 'synthetic' if is_synthetic else 'API',
        'years': [],
        'countries': 0,
        'complete_series': 0,
        'issues': []
    }
    
    try:
        print(f"    Loading {data_path.name}...")
        df = pd.read_csv(data_path)
        print(f"    Rows: {len(df)}")
        print(f"    Columns: {list(df.columns)}")
        
        if is_synthetic:
            results['issues'].append("WARNING: Using synthetic data, not real Eurostat data")
            print("    ⚠ WARNING: This is synthetic data!")
        
        # Check structure
        if 'geo' not in df.columns:
            results['issues'].append("Missing 'geo' column")
            results['status'] = 'invalid'
            return results
        
        if 'time' not in df.columns:
            results['issues'].append("Missing 'time' column")
            results['status'] = 'invalid'
            return results
        
        if 'values' not in df.columns:
            results['issues'].append("Missing 'values' column")
            results['status'] = 'invalid'
            return results
        
        # Years
        years = sorted(df['time'].astype(str).unique())
        results['years'] = years
        print(f"    Years: {years}")
        
        required_years = ['2020', '2021', '2022', '2023']
        missing_years = [y for y in required_years if y not in years]
        if missing_years:
            results['issues'].append(f"Missing years: {missing_years}")
        
        # Countries
        countries = df['geo'].unique()
        results['countries'] = len(countries)
        print(f"    Countries: {len(countries)}")
        
        if len(countries) < 20:
            results['issues'].append(f"Only {len(countries)} countries (expected >=20)")
        
        # Value ranges
        values = pd.to_numeric(df['values'], errors='coerce')
        if values.min() <= 0:
            results['issues'].append("Some values are <= 0")
        if values.max() > 100000:
            results['issues'].append("Some values are > 100,000 (suspiciously high)")
        
        print(f"    Value range: {values.min():.0f} - {values.max():.0f}")
        
        # Complete time series
        complete = df.groupby('geo')['time'].count()
        complete_countries = complete[complete >= 4].index.tolist()
        results['complete_series'] = len(complete_countries)
        print(f"    Complete series (4 years): {len(complete_countries)}/{len(countries)}")
        
        missing_countries = complete[complete < 4].index.tolist()
        if missing_countries:
            results['issues'].append(f"{len(missing_countries)} countries with incomplete data")
        
        # Save report
        report_lines = [
            "EUROSTAT EMPLOYMENT VALIDATION REPORT",
            "=" * 50,
            f"Validation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Location: {data_path}",
            f"Source: {results['source']}",
            f"",
            f"Rows: {len(df)}",
            f"Years: {', '.join(years)}",
            f"Countries: {len(countries)}",
            f"Complete time series: {len(complete_countries)}/{len(countries)}",
            f"Value range: {values.min():.0f} - {values.max():.0f}",
            f"",
            "ISSUES:",
        ]
        
        if results['issues']:
            for issue in results['issues']:
                report_lines.append(f"  - {issue}")
        else:
            report_lines.append("  None")
        
        if missing_countries:
            report_lines.append("")
            report_lines.append("Countries with incomplete data:")
            for country in missing_countries[:20]:
                count = complete[country]
                report_lines.append(f"  - {country}: {count} years")
        
        report_text = "\n".join(report_lines)
        report_path = logs_dir / "eurostat_validation.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"    ✓ Report saved to: {report_path}")
        
    except Exception as e:
        results['status'] = 'error'
        results['issues'].append(f"Error loading file: {e}")
        print(f"    ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return results


def validate_exiobase() -> Dict[str, Any]:
    """Validate Exiobase data."""
    print("\n  Validating Exiobase data...")
    
    project_root = Path(__file__).parent.parent.absolute()
    data_raw = project_root / "data" / "raw"
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    exiobase_dir = data_raw / "exiobase3"
    
    results = {
        'status': 'missing',
        'location': str(exiobase_dir),
        'files_found': [],
        'matrix_dimensions': None,
        'issues': []
    }
    
    if not exiobase_dir.exists():
        results['issues'].append("exiobase3 directory not found")
        return results
    
    try:
        all_files = [f.name for f in exiobase_dir.rglob('*') if f.is_file()]
        results['files_found'] = all_files
        results['status'] = 'valid'
        
        print(f"    Files found: {len(all_files)}")
        
        # Look for matrix file
        matrix_file = None
        for pattern in ['A.txt', 'A.csv']:
            matches = list(exiobase_dir.rglob(pattern))
            if matches:
                matrix_file = matches[0]
                break
        
        if matrix_file:
            print(f"    Found matrix file: {matrix_file.name}")
            try:
                if matrix_file.suffix == '.txt':
                    df = pd.read_csv(matrix_file, sep='\t', nrows=1000)
                else:
                    df = pd.read_csv(matrix_file, nrows=1000)
                
                print(f"    Matrix shape (sample): {df.shape}")
                print(f"    Columns (first 5): {list(df.columns[:5])}")
                
                # Check if numeric
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"    Numeric columns: {len(numeric_cols)}")
                    results['matrix_dimensions'] = f"{df.shape[0]}x{len(numeric_cols)} (sample)"
                else:
                    results['issues'].append("Matrix file appears non-numeric")
                
                # Check for NaN
                nan_count = df.isna().sum().sum()
                if nan_count > 0:
                    results['issues'].append(f"Found {nan_count} NaN values in first 1000 rows")
                else:
                    print(f"    No NaN values in sample")
                    
            except Exception as e:
                results['issues'].append(f"Could not read matrix file: {e}")
        else:
            results['issues'].append("No A.txt or A.csv matrix file found")
        
        # Save report
        report_lines = [
            "EXIOBASE VALIDATION REPORT",
            "=" * 50,
            f"Validation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Location: {exiobase_dir}",
            f"",
            f"Total files: {len(all_files)}",
            f"",
            "Key files:",
        ]
        
        key_patterns = ['A.txt', 'A.csv', 'Y.txt', 'Y.csv', 'F.txt', 'F.csv']
        for pattern in key_patterns:
            matches = [f for f in all_files if pattern in f]
            if matches:
                report_lines.append(f"  {pattern}: {len(matches)} file(s)")
                for match in matches[:3]:
                    report_lines.append(f"    - {match}")
        
        if results['matrix_dimensions']:
            report_lines.append("")
            report_lines.append(f"Matrix dimensions (sample): {results['matrix_dimensions']}")
        
        report_lines.append("")
        report_lines.append("ISSUES:")
        if results['issues']:
            for issue in results['issues']:
                report_lines.append(f"  - {issue}")
        else:
            report_lines.append("  None")
        
        report_text = "\n".join(report_lines)
        report_path = logs_dir / "exiobase_validation.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"    ✓ Report saved to: {report_path}")
        
    except Exception as e:
        results['status'] = 'error'
        results['issues'].append(f"Error validating: {e}")
        print(f"    ✗ ERROR: {e}")
    
    return results


def validate_all_data() -> None:
    """Run validation on all datasets and create master report."""
    print("\n" + "="*70)
    print("PART 4: VALIDATING ALL DATA")
    print("="*70)
    
    project_root = Path(__file__).parent.parent.absolute()
    logs_dir = project_root / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Run validations
    print("\n[4.1/3] Validating ESS10...")
    ess10_results = validate_ess10()
    
    print("\n[4.2/3] Validating Eurostat...")
    eurostat_results = validate_eurostat()
    
    print("\n[4.3/3] Validating Exiobase...")
    exiobase_results = validate_exiobase()
    
    # Create master report
    print("\n  Generating master validation report...")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report_lines = [
        "="*70,
        "ESEE 2026 DATA VALIDATION REPORT",
        f"Generated: {timestamp}",
        "="*70,
        "",
        "DATASET 1: EUROPEAN SOCIAL SURVEY (ESS10)",
        "-" * 70,
        f"Status: {get_status_symbol(ess10_results['status'])} {ess10_results['status'].upper()}",
        f"Location: {ess10_results['location']}",
        f"Rows: {ess10_results['rows']:,}" if ess10_results['rows'] > 0 else "Rows: N/A",
        f"Countries: {len(ess10_results['countries'])} - {', '.join(ess10_results['countries'][:10])}" if ess10_results['countries'] else "Countries: N/A",
        f"Critical columns: {sum(1 for v in ess10_results['critical_columns'].values() if v == 'present')}/{len(ess10_results['critical_columns'])} present",
        f"Policy variables found: {len(ess10_results['policy_variables'])}",
        f"Missing data: See detailed report",
        f"Issues: {len(ess10_results['issues'])}",
        "" if not ess10_results['issues'] else "\n".join([f"  - {issue}" for issue in ess10_results['issues']]),
        "",
        "DATASET 2: EUROSTAT EMPLOYMENT",
        "-" * 70,
        f"Status: {get_status_symbol(eurostat_results['status'])} {eurostat_results['status'].upper()}",
        f"Location: {eurostat_results['location']}",
        f"Source: {eurostat_results.get('source', 'N/A')}",
        f"Years: {', '.join(eurostat_results.get('years', []))}" if eurostat_results.get('years') else "Years: N/A",
        f"Countries: {eurostat_results.get('countries', 'N/A')}",
        f"Complete series: {eurostat_results.get('complete_series', 'N/A')}",
        f"Issues: {len(eurostat_results['issues'])}",
        "" if not eurostat_results['issues'] else "\n".join([f"  - {issue}" for issue in eurostat_results['issues']]),
        "",
        "DATASET 3: EXIOBASE INPUT-OUTPUT TABLES",
        "-" * 70,
        f"Status: {get_status_symbol(exiobase_results['status'])} {exiobase_results['status'].upper()}",
        f"Location: {exiobase_results['location']}",
        f"Version: 3.8.2 (assumed)",
        f"Files found: {len(exiobase_results['files_found'])}",
        f"Matrix dimensions: {exiobase_results.get('matrix_dimensions', 'N/A')}",
        f"Issues: {len(exiobase_results['issues'])}",
        "" if not exiobase_results['issues'] else "\n".join([f"  - {issue}" for issue in exiobase_results['issues']]),
        "",
        "="*70,
        "OVERALL STATUS",
        "="*70,
    ]
    
    # Determine overall status
    all_statuses = [
        ess10_results['status'],
        eurostat_results['status'],
        exiobase_results['status'],
    ]
    
    if all(s == 'valid' for s in all_statuses):
        overall_status = "✓ READY TO PROCEED"
        next_steps = [
            "All datasets validated successfully.",
            "You can proceed to data preprocessing (Step 4 in DEVELOPMENT_ROADMAP.md).",
            "",
            "Next steps:",
            "1. Review validation reports in results/logs/",
            "2. Run src/02_data_preprocessing_survey.py (when created)",
            "3. Run src/02b_data_preprocessing_structural.py (when created)",
        ]
    elif 'valid' in all_statuses:
        overall_status = "⚠ NEEDS ATTENTION"
        next_steps = [
            "Some datasets have issues. Review individual validation reports.",
            "",
            "Recommended actions:",
        ]
        if ess10_results['status'] != 'valid':
            next_steps.append("  - Fix ESS10 data issues")
        if eurostat_results['status'] != 'valid':
            next_steps.append("  - Check Eurostat data or download again")
        if exiobase_results['status'] != 'valid':
            next_steps.append("  - Verify Exiobase extraction")
    else:
        overall_status = "✗ CRITICAL ISSUES"
        next_steps = [
            "Multiple datasets are missing or invalid.",
            "Please re-run the data setup script or manually download missing data.",
        ]
    
    report_lines.append(overall_status)
    report_lines.append("")
    report_lines.append("Next steps:")
    report_lines.extend(next_steps)
    report_lines.append("")
    report_lines.append("="*70)
    
    report_text = "\n".join(report_lines)
    master_report_path = logs_dir / "master_data_report.txt"
    with open(master_report_path, 'w') as f:
        f.write(report_text)
    
    print(f"  ✓ Master report saved to: {master_report_path}")
    
    # Print summary to console
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"ESS10:      {get_status_symbol(ess10_results['status'])} {ess10_results['status']}")
    print(f"Eurostat:   {get_status_symbol(eurostat_results['status'])} {eurostat_results['status']} ({eurostat_results.get('source', 'N/A')})")
    print(f"Exiobase:   {get_status_symbol(exiobase_results['status'])} {exiobase_results['status']}")
    print("="*70)
    print(f"Overall: {overall_status}")
    print("="*70)


def get_status_symbol(status: str) -> str:
    """Get status symbol for report."""
    if status == 'valid':
        return '✓'
    elif status == 'missing':
        return '✗'
    else:
        return '⚠'


# ============================================================================
# PART 5: MAIN EXECUTION
# ============================================================================

def main():
    """Run complete data setup pipeline."""
    print("="*70)
    print("ESEE 2026 DATA SETUP & VALIDATION")
    print("="*70)
    
    # Create necessary directories
    project_root = Path(__file__).parent.parent.absolute()
    os.makedirs(project_root / 'data' / 'raw', exist_ok=True)
    os.makedirs(project_root / 'results' / 'logs', exist_ok=True)
    
    results = {}
    
    # Step 1: Extract ESS
    print("\n[1/4] Extracting ESS data...")
    try:
        ess_ok = extract_ess_data()
        results['ess'] = ess_ok
    except Exception as e:
        print(f"✗ ESS extraction failed: {e}")
        results['ess'] = False
    
    # Step 2: Download Eurostat
    print("\n[2/4] Downloading Eurostat data...")
    try:
        eurostat_result = download_eurostat_data()
        results['eurostat'] = eurostat_result in ['success', 'synthetic']
        results['eurostat_source'] = eurostat_result
    except Exception as e:
        print(f"✗ Eurostat download failed: {e}")
        results['eurostat'] = False
        results['eurostat_source'] = 'failed'
    
    # Step 3: Extract Exiobase
    print("\n[3/4] Extracting Exiobase data...")
    try:
        exiobase_ok = extract_exiobase_data()
        results['exiobase'] = exiobase_ok
    except Exception as e:
        print(f"✗ Exiobase extraction failed: {e}")
        results['exiobase'] = False
    
    # Step 4: Validate everything
    print("\n[4/4] Validating all datasets...")
    try:
        validate_all_data()
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    ess_symbol = '✓' if results.get('ess') else '✗'
    eurostat_symbol = '✓' if results.get('eurostat') else '✗'
    exiobase_symbol = '✓' if results.get('exiobase') else '✗'
    
    print(f"ESS:      {ess_symbol}")
    eurostat_msg = f"{eurostat_symbol}"
    if results.get('eurostat_source') == 'synthetic':
        eurostat_msg += " (SYNTHETIC - see warning above)"
    print(f"Eurostat: {eurostat_msg}")
    print(f"Exiobase: {exiobase_symbol}")
    print("\nSee results/logs/master_data_report.txt for details")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

