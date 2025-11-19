from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Role, RoleMenu, Menu, User, UserRole
from ..serializers import (
    RoleSerializer,
    RoleQuerySerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    RoleChangeStatusSerializer,
    RoleDataScopeSerializer,
    UserQuerySerializer,
    UserSerializer,
)


class RoleViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Role.objects.filter(del_flag='0').order_by('create_time')
    serializer_class = RoleSerializer
    update_body_serializer_class = RoleUpdateSerializer
    update_body_id_field = 'roleId'

    def get_queryset(self):
        # 使用父类的 queryset 作为基础，避免递归调用自身
        qs = super().get_queryset()
        # 列表查询使用 query_params（GET 查询参数），而不是 request.data
        s = RoleQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        role_name = data.get('roleName')
        role_key = data.get('roleKey')
        status_value = data.get('status')
        begin_time = data.get('beginTime')
        end_time = data.get('endTime')

        if role_name:
            qs = qs.filter(role_name__icontains=role_name)
        if role_key:
            qs = qs.filter(role_key__icontains=role_key)
        if status_value:
            qs = qs.filter(status=status_value)
        if begin_time:
            qs = qs.filter(create_time__gte=begin_time)
        if end_time:
            qs = qs.filter(create_time__lte=end_time)
        return qs.order_by('create_time')

    def create(self, request, *args, **kwargs):
        v = RoleCreateSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        vd = v.validated_data

        # 创建角色
        role = Role(
            role_name=vd.get('roleName'),
            role_key=vd.get('roleKey'),
            role_sort=vd.get('roleSort', 0),
            status=vd.get('status', '0'),
            remark=vd.get('remark', ''),
            data_scope=vd.get('dataScope', '1'),
            menu_check_strictly=1 if vd.get('menuCheckStrictly', True) else 0,
            dept_check_strictly=1 if vd.get('deptCheckStrictly', True) else 0,
        )

        # 审计字段
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            role.create_by = user.username
            role.update_by = user.username
        role.save()

        # 处理菜单关联
        menu_ids = vd.get('menuIds') or []
        if menu_ids:
            menus = list(Menu.objects.filter(menu_id__in=menu_ids, del_flag='0').values_list('menu_id', flat=True))
            RoleMenu.objects.bulk_create([RoleMenu(role=role, menu_id=mid) for mid in menus])

        return self.ok()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        vd = RoleUpdateSerializer(instance, data=request.data, partial=partial)
        vd.is_valid(raise_exception=True)
        instance = vd.save()
        # 更新菜单关联（全量替换）
        if 'menuIds' in vd:
            new_ids = set(vd.get('menuIds') or [])
            RoleMenu.objects.filter(role=instance).delete()
            if new_ids:
                menus = list(Menu.objects.filter(menu_id__in=new_ids, del_flag='0').values_list('menu_id', flat=True))
                RoleMenu.objects.bulk_create([RoleMenu(role=instance, menu_id=mid) for mid in menus])

        return self.ok()

    @action(detail=False, methods=['put'], url_path='changeStatus')
    def change_status(self, request):
        s = RoleChangeStatusSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        role_id = s.validated_data.get('roleId')
        status_value = s.validated_data.get('status')
        try:
            role = Role.objects.get(role_id=role_id, del_flag='0')
        except Role.DoesNotExist:
            return Response({"code": 404, "msg": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)
        role.status = status_value
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            role.update_by = user.username
        role.save(update_fields=['status', 'update_by', 'update_time'])
        return Response({"code": 200, "msg": "操作成功"})

    @action(detail=False, methods=['put'], url_path='dataScope')
    def data_scope(self, request):
        s = RoleDataScopeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        vd = s.validated_data
        role_id = vd.get('roleId')
        try:
            role = Role.objects.get(role_id=role_id, del_flag='0')
        except Role.DoesNotExist:
            return Response({"code": 404, "msg": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)
        role.data_scope = vd.get('dataScope')
        role.dept_check_strictly = 1 if vd.get('deptCheckStrictly', True) else 0
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            role.update_by = user.username
        role.save(update_fields=['data_scope', 'dept_check_strictly', 'update_by', 'update_time'])
        # deptIds 可根据后续设计进行持久化，目前不存储，仅保持字段兼容
        return Response({"code": 200, "msg": "操作成功"})

    @action(detail=False, methods=['get'], url_path=r'deptTree/(?P<roleId>\d+)')
    def dept_tree_select(self, request, roleId=None):
        # 部门树与选中项（目前选中为空，保持兼容）
        from ..models import Dept
        depts = list(Dept.objects.filter(status='0', del_flag='0').order_by('parent_id', 'order_num'))

        def build_tree(items, pid=0):
            res = []
            for d in items:
                if d.parent_id == pid:
                    node = {"id": d.dept_id, "label": d.dept_name}
                    children = build_tree(items, d.dept_id)
                    if children:
                        node["children"] = children
                    res.append(node)
            return res

        data = build_tree(depts, 0)
        checked = []
        return Response({"code": 200, "msg": "操作成功", "depts": data, "checkedKeys": checked})

    # ----- 角色已/未授权用户及授权操作 -----
    @action(detail=False, methods=['get'], url_path='authUser/allocatedList')
    def allocated_user_list(self, request):
        s = UserQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        vd = s.validated_data
        role_id = request.query_params.get('roleId')
        try:
            role_id = int(role_id) if role_id is not None else None
        except Exception:
            role_id = None
        if not role_id:
            return Response({"code": 400, "msg": "缺少参数 roleId"}, status=status.HTTP_400_BAD_REQUEST)

        qs = User.objects.filter(del_flag='0', userrole__role_id=role_id)
        if vd.get('userName'):
            qs = qs.filter(username__icontains=vd['userName'])
        if vd.get('phonenumber'):
            qs = qs.filter(phonenumber__icontains=vd['phonenumber'])
        if vd.get('status'):
            qs = qs.filter(status=vd['status'])

        page = self.paginate_queryset(qs.order_by('-id'))
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='authUser/unallocatedList')
    def unallocated_user_list(self, request):
        s = UserQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        vd = s.validated_data
        role_id = request.query_params.get('roleId')
        try:
            role_id = int(role_id) if role_id is not None else None
        except Exception:
            role_id = None
        if not role_id:
            return Response({"code": 400, "msg": "缺少参数 roleId"}, status=status.HTTP_400_BAD_REQUEST)

        assigned_user_ids = list(UserRole.objects.filter(role_id=role_id).values_list('user_id', flat=True))
        qs = User.objects.filter(del_flag='0').exclude(id__in=assigned_user_ids)
        if vd.get('userName'):
            qs = qs.filter(username__icontains=vd['userName'])
        if vd.get('phonenumber'):
            qs = qs.filter(phonenumber__icontains=vd['phonenumber'])
        if vd.get('status'):
            qs = qs.filter(status=vd['status'])

        page = self.paginate_queryset(qs.order_by('-id'))
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['put'], url_path='authUser/cancel')
    def auth_user_cancel(self, request):
        role_id = request.data.get('roleId')
        user_id = request.data.get('userId')
        if not role_id or not user_id:
            return Response({"code": 400, "msg": "缺少参数 roleId 或 userId"}, status=status.HTTP_400_BAD_REQUEST)
        UserRole.objects.filter(role_id=role_id, user_id=user_id).delete()
        return Response({"code": 200, "msg": "操作成功"})

    @action(detail=False, methods=['put'], url_path='authUser/cancelAll')
    def auth_user_cancel_all(self, request):
        role_id = request.query_params.get('roleId')
        user_ids = request.query_params.get('userIds')
        if not role_id or not user_ids:
            return Response({"code": 400, "msg": "缺少参数 roleId 或 userIds"}, status=status.HTTP_400_BAD_REQUEST)
        ids = [int(i) for i in str(user_ids).split(',') if i]
        UserRole.objects.filter(role_id=role_id, user_id__in=ids).delete()
        return Response({"code": 200, "msg": "操作成功"})

    @action(detail=False, methods=['put'], url_path='authUser/selectAll')
    def auth_user_select_all(self, request):
        role_id = request.query_params.get('roleId')
        user_ids = request.query_params.get('userIds')
        if not role_id or not user_ids:
            return Response({"code": 400, "msg": "缺少参数 roleId 或 userIds"}, status=status.HTTP_400_BAD_REQUEST)
        ids = [int(i) for i in str(user_ids).split(',') if i]
        role = Role.objects.filter(role_id=role_id, del_flag='0').first()
        if not role:
            return Response({"code": 404, "msg": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)
        existing = set(UserRole.objects.filter(role_id=role_id).values_list('user_id', flat=True))
        creates = [UserRole(role=role, user_id=uid) for uid in ids if uid not in existing]
        if creates:
            UserRole.objects.bulk_create(creates, ignore_conflicts=True)
        return Response({"code": 200, "msg": "操作成功"})