from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MenuViewSet, LoginView, CaptchaView, GetInfoView, LogoutView, GetRoutersView,
    DictTypeViewSet, DictDataViewSet,
)

router = DefaultRouter()
router.trailing_slash = '/?'
router.register(r'user', UserViewSet, basename='user')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'dict/type', DictTypeViewSet, basename='dict-type')
router.register(r'dict/data', DictDataViewSet, basename='dict-data')

urlpatterns = [
    path('system/', include(router.urls)),
    # path('system/menu/list', MenuViewSet.as_view({'get': 'list2'}), name='menu-list'),
    path('login', LoginView.as_view(), name='login'),
    path('captchaImage/', CaptchaView.as_view(), name='captcha-image'),
    path('getInfo', GetInfoView.as_view(), name='get-info'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('getRouters', GetRoutersView.as_view(), name='get-routers'),
]