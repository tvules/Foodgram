from django.core.validators import RegexValidator


class HEXColorValidator(RegexValidator):
    """HEX color validation. Match: #abc or #abcdef"""

    regex = r'^#(?:[0-9a-f]{3}){1,2}$'
