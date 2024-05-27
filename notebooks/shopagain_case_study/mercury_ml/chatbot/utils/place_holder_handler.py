import re

def detect_custom_placeholders(text):
    """
    Detect placeholders in various custom formats (square brackets, curly braces, double curly braces, parentheses)
    in the given text and return a boolean indicating if placeholders were found, 
    along with the list of placeholders.

    Parameters:
    text (str): The text to be searched for placeholders.

    Returns:
    bool: True if placeholders are found, False otherwise.
    list: List of strings that are placeholders.
    """
    # Regular expression to find placeholders in various formats
    pattern = r'\[([^\]]+)\]|\{([^\}]+)\}|\(\([^\)]+\)\)|\{\{([^\}]+)\}\}'
    matches = re.findall(pattern, text)

    # Flatten the list of tuples and remove empty strings
    matches = [item for sublist in matches for item in sublist if item]

    # Check if there are any matches
    found = len(matches) > 0

    return found, matches


def phone_detector(text):
    """
    Detects if the given text contains keywords related to phone numbers such as 'phone', 'contact', 'number', etc.

    Parameters:
    text (str): The text to be searched for keywords.

    Returns:
    bool: True if phone-related keywords are found, False otherwise.
    """
    # List of keywords related to phone numbers
    keywords = ['phone', 'contact', 'number', 'cell', 'mobile', 'telephone', 'hotline', 'call', 'dial']

    # Check if any of the keywords are in the text
    return any(keyword in text.lower() for keyword in keywords)


def email_detector(text):
    """
    Detects if the given text contains keywords or symbols related to email addresses such as 'email', '@', etc.

    Parameters:
    text (str): The text to be searched for email-related keywords and symbols.

    Returns:
    bool: True if email-related keywords or symbols are found, False otherwise.
    """
    # List of keywords and symbols related to email addresses
    keywords = ['email', '@', 'mail', 'inbox', 'address']

    # Check if any of the keywords or symbols are in the text
    return any(keyword in text.lower() for keyword in keywords)


def replace_placeholders_with_contact_info(input_text, phone_replacement, email_replacement):
    """
    Processes the input string to:
    1. Check for placeholders.
    2. If placeholders are found, check each placeholder for phone number and email.
    3. Replace placeholders with corresponding true values provided as input.

    Parameters:
    input_text (str): The text to be processed.
    phone_replacement (str): The replacement text for phone-related content.
    email_replacement (str): The replacement text for email-related content.

    Returns:
    str: The processed text with replacements if applicable.
    """
    # Detect placeholders
    placeholders_found, placeholders = detect_custom_placeholders(input_text)

    if placeholders_found:
        # Process each placeholder
        for placeholder in placeholders:
            if phone_detector(placeholder):
                # Replace phone-related placeholders
                input_text = input_text.replace('[' + placeholder + ']', phone_replacement)
                input_text = input_text.replace('{' + placeholder + '}', phone_replacement)
                input_text = input_text.replace('{{' + placeholder + '}}', phone_replacement)
                input_text = input_text.replace('(' + placeholder + ')', phone_replacement)
            elif email_detector(placeholder):
                # Replace email-related placeholders
                input_text = input_text.replace('[' + placeholder + ']', email_replacement)
                input_text = input_text.replace('{' + placeholder + '}', email_replacement)
                input_text = input_text.replace('{{' + placeholder + '}}', email_replacement)
                input_text = input_text.replace('(' + placeholder + ')', email_replacement)

    return input_text