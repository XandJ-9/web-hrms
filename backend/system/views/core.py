from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from captcha.models import CaptchaStore
from captcha.views import captcha_image
import base64

from ..models import UserRole, Menu, DictType, DictData
from ..serializers import DictTypeSerializer, DictDataSerializer
from django.db.models import Q
from django.core.cache import cache


class CaptchaView(TokenObtainPairView):
    def get(self, request, *args, **kwargs):
        hashkey = CaptchaStore.generate_key()
        img_response = captcha_image(request._request, hashkey)
        img_base64 = base64.b64encode(img_response.content).decode()
        resp = Response({
            'img': img_base64,
            'uuid': hashkey,
            'captchaEnabled': True
        })
        resp['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp['Pragma'] = 'no-cache'
        resp['Expires'] = '0'
        return resp


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'msg': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'token': serializer.validated_data.get('access')})


class GetInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            'userId': user.id,
            'userName': user.username,
            'nickName': getattr(user, 'nick_name', '') or user.username,
            'avatar': getattr(user, 'avatar', '') or '',
            'phonenumber': getattr(user, 'phonenumber', '') or '',
            'email': getattr(user, 'email', '') or '',
            'sex': getattr(user, 'sex', '2'),
        }

        try:
            user_roles = UserRole.objects.filter(user=user).select_related('role')
            roles = [ur.role.role_key for ur in user_roles]
        except Exception:
            roles = []
        if "admin" in roles:
            permissions = ["*:*:*"]
        else:
            permissions = []

        resp = {
            'code': 200,
            'msg': '操作成功',
            'user': user_data,
            'roles': roles,
            'permissions': permissions,
            'isDefaultModifyPwd': False,
            'isPasswordExpired': False,
        }
        return Response(resp)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'code': 200, 'msg': '操作成功'})


class GetRoutersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        menus = list(Menu.objects.filter(status='0', del_flag='0').order_by('parent_id', 'order_num'))

        def build_tree(items, pid=0):
            nodes = []
            for m in items:
                if m.parent_id == pid:
                    children = build_tree(items, m.menu_id)
                    nodes.append({"menu": m, "children": children})
            return nodes

        def to_router(node):
            m = node["menu"]
            children = node["children"]
            hidden = (m.visible == '1')
            is_outer = (m.is_frame == '0')

            meta = {
                "title": m.menu_name,
                "icon": m.icon or None,
                "noCache": (m.is_cache == '1')
            }
            if m.query:
                meta["query"] = m.query

            if m.menu_type == 'M':
                route = {
                    "path": m.path or ("/" + str(m.menu_id)),
                    "component": "Layout" if m.parent_id == 0 else "ParentView",
                    "hidden": hidden,
                    "alwaysShow": True,
                    "name": m.menu_name.replace('-', '').replace('_', ''),
                    "meta": meta
                }
                route["children"] = [r for r in [to_router(c) for c in children] if r is not None]
                return route
            elif m.menu_type == 'C':
                if is_outer and (m.path.startswith('http://') or m.path.startswith('https://')):
                    return {
                        "path": m.path,
                        "component": "InnerLink",
                        "hidden": hidden,
                        "name": m.menu_name.replace('-', '').replace('_', ''),
                        "meta": meta
                    }
                return {
                    "path": m.path or ("/" + str(m.menu_id)),
                    "component": m.component or "Layout",
                    "hidden": hidden,
                    "name": m.menu_name.replace('-', '').replace('_', ''),
                    "meta": meta
                }
            else:
                return None

        tree = build_tree(menus, 0)
        routers = [r for r in [to_router(n) for n in tree] if r is not None]
        return Response({"code": 200, "msg": "操作成功", "data": routers})

