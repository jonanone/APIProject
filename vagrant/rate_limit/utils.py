from flask import g


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)
