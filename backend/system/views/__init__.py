from .core import (
    CaptchaView, LoginView, GetInfoView, LogoutView, GetRoutersView
)
from .user import UserViewSet
from .menu import MenuViewSet
from .dict import DictTypeViewSet, DictDataViewSet
__all__ = [
    'CaptchaView', 'LoginView', 'GetInfoView', 'LogoutView', 'GetRoutersView',
    'DictTypeViewSet', 'DictDataViewSet',
    'UserViewSet', 'MenuViewSet'
]