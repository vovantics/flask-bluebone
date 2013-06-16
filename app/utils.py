# -*- coding: utf-8 -*-
"""
Utils has nothing to do with models and views.
"""

from datetime import datetime
from flask import current_app


def get_current_time():
    return datetime.utcnow()


def format_date(value, format='%Y-%m-%d %H:%M:%S'):
        return value.strftime(format)


def get_resource_as_string(name, charset='utf-8'):
    with current_app.open_resource(name) as f:
        return f.read().decode(charset)
