import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_severity_color(severity):
    colors = {
        'Low': '#10b981',
        'Medium': '#f59e0b',
        'High': '#ef4444'
    }
    return colors.get(severity, '#6b7280')