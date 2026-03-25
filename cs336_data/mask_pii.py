import re

def mask_emails(text: str) -> tuple[str, int]:
    # Regex to match basic email addresses
    pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    masked_text, num_masked = pattern.subn('|||EMAIL_ADDRESS|||', text)
    return masked_text, num_masked

def mask_phone_numbers(text: str) -> tuple[str, int]:
    # Matches common US phone number formats:
    # 123-456-7890, (123) 456-7890, 123 456 7890, 123.456.7890, +1 123-456-7890
    pattern = re.compile(r'(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}')
    masked_text, num_masked = pattern.subn('|||PHONE_NUMBER|||', text)
    return masked_text, num_masked

def mask_ips(text: str) -> tuple[str, int]:
    # Matches IPv4 addresses
    pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    masked_text, num_masked = pattern.subn('|||IP_ADDRESS|||', text)
    return masked_text, num_masked
