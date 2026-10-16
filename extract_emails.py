"""
Multi-Sheet Excel Lead Extractor Utility
Scans an Excel workbook (.xlsx / .xls), automatically detects header rows across
all worksheets, extracts contacts (email, full name, company), and exports a clean CSV.
"""
import sys
import os
import pandas as pd
from colorama import Fore, Style, init

init(autoreset=True)

def extract_leads_from_excel(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"{Fore.RED}[ERROR] Input file not found: {input_path}{Style.RESET_ALL}")
        return False

    print(f"{Fore.CYAN}Opening Excel workbook:{Style.RESET_ALL} {input_path}")
    try:
        xls = pd.ExcelFile(input_path)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to read Excel workbook: {e}{Style.RESET_ALL}")
        return False

    all_dfs = []

    for sheet in xls.sheet_names:
        print(f"Scanning sheet: {Fore.YELLOW}{sheet}{Style.RESET_ALL} ...")
        # Try to find header row if not the first row
        header_idx = 0
        for i in range(10):
            try:
                temp_df = pd.read_excel(xls, sheet_name=sheet, nrows=1, header=i)
                cols = [str(c).lower().strip() for c in temp_df.columns]
                target_cols = ['company', 'company name', 'email', 'email address', 'mail 1', 'mail', 'poc']
                if any(x in target_cols for x in cols):
                    header_idx = i
                    break
            except Exception:
                pass

        try:
            df = pd.read_excel(xls, sheet_name=sheet, header=header_idx)
        except Exception as e:
            print(f"Skipping sheet {sheet} due to error: {e}")
            continue

        # Normalize column names for extraction
        cols_lower = {c: str(c).lower().strip() for c in df.columns}
        df = df.rename(columns=cols_lower)

        # Check if this sheet has any email columns
        email_col = None
        for c in df.columns:
            if c in ['email', 'email address', 'mail 1', 'mail', 'contact email']:
                email_col = c
                break

        if email_col:
            # Find company and name if available
            company_col = None
            for c in df.columns:
                if c in ['company name', 'company', 'organization', 'firm']:
                    company_col = c
                    break

            name_col = None
            for c in df.columns:
                if c in ['hr / poc name', 'full_name', 'full name', 'first name', 'name', 'poc name', 'poc', 'contact name']:
                    name_col = c
                    break

            extracted = pd.DataFrame()
            extracted['email'] = df[email_col]
            extracted['company'] = df[company_col] if company_col else ''
            extracted['full_name'] = df[name_col] if name_col else ''
            extracted['source_sheet'] = sheet

            all_dfs.append(extracted)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        # Drop rows without valid email addresses
        final_df = final_df.dropna(subset=['email'])
        final_df = final_df[final_df['email'].astype(str).str.strip() != '']
        final_df = final_df[final_df['email'].astype(str).str.contains('@')]
        
        # Deduplicate
        initial_count = len(final_df)
        final_df = final_df.drop_duplicates(subset=['email'], keep='first')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        final_df.to_csv(output_path, index=False)
        print(f"\n{Fore.GREEN}[SUCCESS] Extracted {len(final_df)} unique leads (from {initial_count} records) into {output_path}{Style.RESET_ALL}\n")
        return True
    else:
        print(f"\n{Fore.YELLOW}[WARNING] No valid email addresses found across sheets in {input_path}{Style.RESET_ALL}\n")
        return False

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "data/extracted_leads.csv"
    else:
        # Default fallbacks
        candidates = ['Personal1_copy.xlsx', 'leads.xlsx', 'contacts.xlsx']
        input_file = next((f for f in candidates if os.path.exists(f)), None)
        output_file = "data/extracted_leads.csv"
        
        if not input_file:
            print(f"\n{Fore.CYAN}Usage:{Style.RESET_ALL} python extract_emails.py <path_to_excel_file.xlsx> [output_csv_file.csv]")
            print("Example: python extract_emails.py my_leads.xlsx data/my_leads.csv\n")
            sys.exit(1)

    extract_leads_from_excel(input_file, output_file)

if __name__ == "__main__":
    main()
