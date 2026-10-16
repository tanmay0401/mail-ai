import pandas as pd

def extract_first_name(full_name):
    """
    Extracts the first name from a full name string.
    Examples:
    'Rahul Sharma' -> 'Rahul'
    'Rahul K Sharma' -> 'Rahul'
    '' -> None
    """
    if not isinstance(full_name, str) or not full_name.strip():
        return None
        
    parts = full_name.strip().split()
    if parts:
        return parts[0]
    return None

def extract_name_from_email(email):
    """
    Attempts to extract a first name from an email address.
    john.doe@email.com -> John
    sarah_smith@email.com -> Sarah
    info@email.com -> None
    """
    if not isinstance(email, str) or not email.strip() or '@' not in email:
        return None
        
    local_part = email.split('@')[0]
    
    # Split by common separators (. or _ or -)
    import re
    parts = re.split(r'[._-]', local_part)
    if not parts:
        return None
        
    first_part = parts[0].strip()
    
    # Remove any numbers
    first_part = re.sub(r'\d+', '', first_part)
    
    # Ignore generic prefixes or extremely short parts
    generic_prefixes = {'info', 'contact', 'admin', 'support', 'sales', 'hello', 'team', 'hr', 'careers', 'mail'}
    if first_part.lower() in generic_prefixes or len(first_part) <= 1:
        return None
        
    return first_part.capitalize()

def get_first_name(row_data):
    """
    Extracts the first name from a row's full_name or falls back to extracting from the email address.
    Returns 'there' if neither is available.
    """
    full_name = row_data.get('full_name', '')
    first_name = extract_first_name(full_name)
    
    if not first_name:
        email = str(row_data.get('email', ''))
        first_name = extract_name_from_email(email)
        
    if not first_name:
        first_name = "there"
        
    return first_name

def personalize_template(template_str, row_data):
    """
    Replaces placeholders like {first_name}, {company} with actual values from row_data.
    row_data is expected to be a pandas Series or dict.
    """
    personalized_str = template_str
    
    first_name = get_first_name(row_data)
        
    # Dictionary of replacements
    replacements = {
        '{first_name}': first_name,
        '{company}': str(row_data.get('company', '')),
        '{role}': str(row_data.get('role', '')),
        '{linkedin}': str(row_data.get('linkedin', '')),
        '{notes}': str(row_data.get('notes', ''))
    }
    
    # Add any other custom columns dynamically
    for col_name, value in row_data.items():
        placeholder = f"{{{col_name}}}"
        if placeholder not in replacements:
            # Only stringify non-null values
            str_val = str(value) if not pd.isna(value) else ''
            replacements[placeholder] = str_val
            
    # Perform replacements
    for placeholder, actual_value in replacements.items():
        # Handle case where value might be pandas NaN
        if str(actual_value) == 'nan':
            actual_value = ''
        personalized_str = personalized_str.replace(placeholder, str(actual_value))
        
    return personalized_str
