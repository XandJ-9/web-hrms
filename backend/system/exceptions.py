from rest_framework.views import exception_handler,set_rollback
from rest_framework.response import Response
from rest_framework import status
from django.db.models import ProtectedError, RestrictedError
from django.db.utils import DatabaseError

import traceback



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
        for key,value in data.items():
            if isinstance(value, (list, tuple)) and value:
                return str(key)+':'+str(value[0])
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
    traceback.print_exc()
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
    elif isinstance(exc, (ProtectedError, RestrictedError)):
        set_rollback()
        msg = "无法删除:该条数据与其他数据有相关绑定"
    elif isinstance(exc, DatabaseError):
        set_rollback()
        msg = "接口服务器异常,请联系管理员" + str(exc)
    elif isinstance(exc, Exception):
        msg = str(exc)
    # Non-DRF or unhandled exceptions → 500
    return Response({'code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
