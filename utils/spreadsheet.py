import pandas as pd
from utils.logger import log_info, log_error
import config

def load_data(file_path):
    """Loads spreadsheet data into a pandas DataFrame. Supports CSV and Excel."""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            # Scan the first 10 rows to detect the correct header row
            header_idx = 0
            for i in range(10):
                try:
                    temp_df = pd.read_excel(file_path, nrows=1, header=i)
                    cols = [str(c).lower().strip() for c in temp_df.columns]
                    target_cols = ['company', 'company name', 'email', 'email address', 'contact name', 'recipient name', 'name']
                    if any(x in target_cols for x in cols):
                        header_idx = i
                        log_info(f"Auto-detected header row at index {header_idx}")
                        break
                except Exception:
                    pass
            df = pd.read_excel(file_path, header=header_idx)
        else:
            log_error("Unsupported file format. Please use .csv or .xlsx")
            return None
        
        # Auto-map custom columns so the user doesn't have to rename them
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['company name', 'company name for emails', 'company', 'organization', 'firm'] and 'company' not in df.columns:
                df['company'] = df[col]
            if col_lower in ['email', 'email address', 'mail 1', 'mail'] and 'email' not in df.columns:
                df['email'] = df[col]
            if col_lower in ['hr / poc name', 'full_name', 'full name', 'first name', 'name', 'poc name', 'recipient name', 'contact name'] and 'full_name' not in df.columns:
                df['full_name'] = df[col]
            
        # Ensure required columns exist, create them if they don't
        required_columns = ['sent_status', 'sent_time', 'error_message', 'full_name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
                
        # Fill NaN with empty string for tracking columns
        df['sent_status'] = df['sent_status'].fillna('')
        df['error_message'] = df['error_message'].fillna('')

        # Convert 'status (fill in)' to object type if it exists to prevent pandas LossySetitemError
        for col in df.columns:
            if str(col).lower().strip() == 'status (fill in)':
                df[col] = df[col].astype(object).fillna('')
        
        log_info(f"Successfully loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        log_error(f"Failed to load data from {file_path}: {e}")
        return None

def save_data(df, file_path):
    """Saves the DataFrame back to the file."""
    try:
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith(('.xls', '.xlsx')):
            df.to_excel(file_path, index=False)
    except Exception as e:
        log_error(f"Failed to save data to {file_path}: {e}")

def get_pending_leads(df):
    """Filters the DataFrame to return only rows that haven't been successfully sent."""
    # We ignore rows where 'email' is empty or NaN
    valid_emails = df[df['email'].notna() & (df['email'] != '')]
    # Keep only those that don't have 'SUCCESS' status
    pending = valid_emails[valid_emails['sent_status'] != 'SUCCESS']
    
    # Remove exact duplicates based on email first to avoid multiple sends to same email
    pending = pending.drop_duplicates(subset=['email'], keep='first')
    
    if config.LIMIT_BY_UNIQUE_COMPANIES:
        # Get the first MAX_COMPANIES_LIMIT unique companies in order of appearance
        unique_companies = []
        for c in pending['company']:
            if pd.notna(c) and str(c).strip() != '':
                if c not in unique_companies:
                    unique_companies.append(c)
                if len(unique_companies) >= config.MAX_COMPANIES_LIMIT:
                    break
        
        # Filter to only keep rows for these companies
        pending = pending[pending['company'].isin(unique_companies)]
        
        # If config.EMAIL_ONLY_FIRST_CONTACT is True, we keep only the first contact per company
        if config.EMAIL_ONLY_FIRST_CONTACT:
            pending = pending.drop_duplicates(subset=['company'], keep='first')
    else:
        # Option B: Limit to first MAX_COMPANIES_LIMIT rows directly
        pending = pending.head(config.MAX_COMPANIES_LIMIT)
        
    return pending


def update_row_status(df, index, status, timestamp, error_msg=""):
    """Updates the status of a specific row in the DataFrame."""
    df.at[index, 'sent_status'] = status
    df.at[index, 'sent_time'] = timestamp
    df.at[index, 'error_message'] = error_msg
    # Also sync with 'Status (fill in)' if it exists
    for col in df.columns:
        if str(col).lower().strip() == 'status (fill in)':
            df.at[index, col] = status
