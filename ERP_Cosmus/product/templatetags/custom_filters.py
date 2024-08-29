from django import template
from datetime import datetime

register = template.Library()

@register.filter
def subtract_dates(date1, date2):
    if date1 and date2:
        return (date1 - date2).days  # Returns the difference in days
    return None