from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from .core import BaseViewSet
from ..permission import HasRolePermission
from ..common import audit_log
from ..serializers import (
    UserSerializer, DeptSerializer, UserProfileSerializer, RoleSerializer,
    UserQuerySerializer, ResetPwdSerializer, ChangeStatusSerializer,
    UpdatePwdSerializer, AvatarSerializer, AuthRoleAssignSerializer, AuthRoleQuerySerializer
)
from ..models import User, Dept, Role, UserRole
from ..serializers import UserSerializer, DeptSerializer, UserProfileSerializer, RoleSerializer

from drf_spectacular.utils import extend_schema

class UserViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    update_body_serializer_class = UserSerializer
    def get_queryset(self):
        queryset = User.objects.all()
        s = UserQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        user_name = data.get('userName') or ''
        phonenumber = data.get('phonenumber') or ''
        status_value = data.get('status') or ''
        dept_id = data.get('deptId')
        begin_time = data.get('beginTime')
        end_time = data.get('endTime')
        if user_name:
            queryset = queryset.filter(Q(username__icontains=user_name) | Q(nick_name__icontains=user_name))
        if phonenumber:
            queryset = queryset.filter(phonenumber__icontains=phonenumber)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if dept_id:
            queryset = queryset.filter(dept_id=dept_id)
        if begin_time:
            queryset = queryset.filter(create_time__gte=begin_time)
        if end_time:
            queryset = queryset.filter(create_time__lte=end_time)
        return queryset.order_by('-create_time')
    
    @action(detail=False, methods=['put'])
    @audit_log
    def resetPwd(self, request):
        v = ResetPwdSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        password = v.validated_data['password']
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            return self.ok('密码重置成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['put'])
    @audit_log
    def changeStatus(self, request):
        v = ChangeStatusSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        status_value = v.validated_data['status']
        try:
            user = User.objects.get(id=user_id)
            user.status = status_value
            user.save()
            return self.ok('状态修改成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['get'])
    def deptTree(self, request):
        depts = Dept.objects.filter(status='0').order_by('parent_id', 'order_num')
        serializer = DeptSerializer(depts, many=True)
        
        def build_tree(data, parent_id=0):
            tree = []
            for item in data:
                if item['parent_id'] == parent_id:
                    children = build_tree(data, item['dept_id'])
                    if children:
                        item['children'] = children
                    tree.append(item)
            return tree
        
        tree_data = build_tree(serializer.data)
        return self.raw_response(tree_data)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return self.data(serializer.data)
    
    @action(detail=False, methods=['put'])
    @audit_log
    def updateProfile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.ok('个人信息修改成功')
    
    @action(detail=False, methods=['put'])
    @audit_log
    def updatePwd(self, request):
        v = UpdatePwdSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        old_password = v.validated_data['oldPassword']
        new_password = v.validated_data['newPassword']
        user = request.user
        if not user.check_password(old_password):
            return self.error('旧密码错误')
        
        user.set_password(new_password)
        user.save()
        return self.ok('密码修改成功')
    
    @action(detail=False, methods=['post'])
    @audit_log
    def avatar(self, request):
        v = AvatarSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        avatar_url = v.validated_data['avatar']
        user = request.user
        user.avatar = avatar_url
        user.save()
        # return Response({'code': 200, 'msg': '头像上传成功'})
        return self.ok('头像上传成功')
    
    @action(detail=False, methods=['get'], url_path=r'authRole/(?P<userId>[^/]+)')
    def getAuthRole(self, request, userId = None):
        v = AuthRoleQuerySerializer(data={'userId': userId})
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        try:
            user = User.objects.get(id=user_id)
            roles = Role.objects.filter(status='0', del_flag='0')
            user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
            
            roles_data = []
            for role in roles:
                role_data = RoleSerializer(role).data
                role_data['flag'] = role.role_id in user_roles
                roles_data.append(role_data)
            
            return self.data({'user': UserSerializer(user).data, 'roles': roles_data})
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['put'], url_path=r'authRole')
    @audit_log
    @extend_schema(request=AuthRoleAssignSerializer)
    def updateAuthRole(self, request):
        v = AuthRoleAssignSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        role_ids = v.validated_data.get('roleIds', [])
        try:
            user = User.objects.get(id=user_id)
            UserRole.objects.filter(user=user).delete()
            for role_id in role_ids:
                try:
                    role = Role.objects.get(role_id=role_id)
                    UserRole.objects.create(user=user, role=role)
                except Role.DoesNotExist:
                    continue
            return self.ok('授权成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
