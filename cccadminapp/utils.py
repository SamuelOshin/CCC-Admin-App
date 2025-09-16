"""
Database utilities for handling cross-database compatibility
"""
from django.db import connection
from django.db.models import Func, TextField, F, Value


def get_month_format(field_name):
    """
    Returns month-year format for dashboard statistics
    SQLite: strftime('%Y-%m', field)
    PostgreSQL: to_char(field, 'YYYY-MM')

    Args:
        field_name: The name of the date field (string)

    Returns:
        Dictionary with 'month' key for use in .extra(select=...)
    """
    from django.db import connection

    if connection.vendor == 'postgresql':
        return {"month": f"to_char({field_name}, 'YYYY-MM')"}
    else:
        # Escape percent signs for SQLite strftime
        return {"month": f"strftime('%%Y-%%m', {field_name})"}
