from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MenuViewSet, RoleViewSet, DeptViewSet, LoginView, CaptchaView, GetInfoView, LogoutView, GetRoutersView,
    DictTypeViewSet, DictDataViewSet, ConfigViewSet,
)

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'dept', DeptViewSet, basename='dept')
router.register(r'dict/type', DictTypeViewSet, basename='dict-type')
router.register(r'dict/data', DictDataViewSet, basename='dict-data')
router.register(r'config', ConfigViewSet, basename='config')

urlpatterns = [
    path('system/', include(router.urls)),
    # 兼容前端 PUT /system/menu（集合更新）
    path('system/menu', MenuViewSet.as_view({'put': 'update_by_body'}), name='menu-update-body'),
    path('system/user', UserViewSet.as_view({'put': 'update_by_body'}), name='user-update-body'),
    # 兼容前端 PUT /system/role（集合更新）
    path('system/role', RoleViewSet.as_view({'put': 'update_by_body'}), name='role-update-body'),
    # 兼容前端 PUT /system/dept（集合更新）
    path('system/dept', DeptViewSet.as_view({'put': 'update_by_body'}), name='dept-update-body'),
    # 兼容前端 PUT /system/config（集合更新）
    path('system/config', ConfigViewSet.as_view({'put': 'update_by_body'}), name='config-update-body'),
    path('login', LoginView.as_view(), name='login'),
    path('captchaImage/', CaptchaView.as_view(), name='captcha-image'),
    path('getInfo', GetInfoView.as_view(), name='get-info'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('getRouters', GetRoutersView.as_view(), name='get-routers'),
]