from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def _first_error_message(data):
    """
    Extract the first human-readable error message from DRF error dict/list.
    """
    if isinstance(data, dict):
        # Prefer 'detail' if present
        detail = data.get('detail')
        if detail:
            return str(detail)
        # Otherwise pick the first field error
        for value in data.values():
            if isinstance(value, (list, tuple)) and value:
                return str(value[0])
            if isinstance(value, dict):
                return _first_error_message(value)
        return ''
    if isinstance(data, (list, tuple)) and data:
        return str(data[0])
    return str(data) if data is not None else ''


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that wraps all errors with {code, message}.
    """
    response = exception_handler(exc, context)
    if response is not None:
        message = _first_error_message(response.data)
        # Fallback when message is empty
        if not message:
            message = '请求错误'
        response.data = {
            'code': response.status_code,
            'message': message,
        }
        # return response
        return Response(response.data, status=status.HTTP_200_OK)

    # Non-DRF or unhandled exceptions → 500
    return Response({'code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)