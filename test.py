from babel.dates import parse_date
from babel import Locale
from datetime import datetime

# The date string to test
date_string = "1 juillet 2026"

# Function to translate French month to English
def translate_french_month(date_str):
    months_in_french = {
        'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April', 'mai': 'May',
        'juin': 'June', 'juillet': 'July', 'août': 'August', 'septembre': 'September', 'octobre': 'October',
        'novembre': 'November', 'décembre': 'December'
    }

    for french_month, english_month in months_in_french.items():
        if french_month in date_str:
            return date_str.replace(french_month, english_month)
    return date_str