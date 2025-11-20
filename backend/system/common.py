import functools
import logging


def audit_log(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            user = getattr(request, 'user', None)
            logging.getLogger().info(f"{getattr(user, 'username', 'anonymous')} {request.method} {request.path}")
        except Exception:
            pass
        return func(self, request, *args, **kwargs)
    return wrapper


def camel_to_snake(name: str) -> str:
    out = []
    for ch in name:
        if ch.isupper():
            out.append('_')
            out.append(ch.lower())
        else:
            out.append(ch)
    s = ''.join(out)
    return s.lstrip('_')


def snake_to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def decamelize_dict(d: dict) -> dict:
    return { camel_to_snake(k): v for k, v in d.items() }


def camelize_dict(d: dict) -> dict:
    return { snake_to_camel(k): v for k, v in d.items() }


def normalize_input(data):
    if isinstance(data, dict):
        return decamelize_dict(data)
    return data