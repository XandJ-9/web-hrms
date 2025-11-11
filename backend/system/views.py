from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import User, Dept, Role, UserRole
from .serializers import UserSerializer, DeptSerializer, UserProfileSerializer, RoleSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
import base64

class CaptchaView(TokenObtainPairView):
    def get(self, request, *args, **kwargs):
        hashkey = CaptchaStore.generate_key()
        image = captcha_image_url(hashkey)
        # 读取图片并转换为base64
        with open(image, 'rb') as f:
            img_base64 = base64.b64encode(f.read())
        return Response({
            'img': img_base64,
            'uuid': hashkey
        })

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'msg': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'token': serializer.validated_data.get('access')
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # 获取查询参数
        user_name = self.request.query_params.get('userName', '')
        phonenumber = self.request.query_params.get('phonenumber', '')
        status = self.request.query_params.get('status', '')
        dept_id = self.request.query_params.get('deptId', '')
        create_time_start = self.request.query_params.get('params', {}).get('beginTime', '')
        create_time_end = self.request.query_params.get('params', {}).get('endTime', '')
        
        # 构建查询条件
        if user_name:
            queryset = queryset.filter(Q(username__icontains=user_name) | Q(nick_name__icontains=user_name))
        if phonenumber:
            queryset = queryset.filter(phonenumber__icontains=phonenumber)
        if status:
            queryset = queryset.filter(status=status)
        if dept_id:
            queryset = queryset.filter(dept_id=dept_id)
        if create_time_start:
            queryset = queryset.filter(create_time__gte=create_time_start)
        if create_time_end:
            queryset = queryset.filter(create_time__lte=create_time_end)
            
        return queryset.order_by('-create_time')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # 分页处理
        page_size = int(request.query_params.get('pageSize', 10))
        page_num = int(request.query_params.get('pageNum', 1))
        total = queryset.count()
        
        start = (page_num - 1) * page_size
        end = start + page_size
        users = queryset[start:end]
        
        serializer = self.get_serializer(users, many=True)
        
        return Response({
            'total': total,
            'rows': serializer.data,
            'code': 200,
            'msg': '操作成功'
        })
    
    @action(detail=False, methods=['put'])
    def resetPwd(self, request):
        user_id = request.data.get('userId')
        password = request.data.get('password')
        
        if not user_id or not password:
            return Response({'code': 400, 'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            return Response({'code': 200, 'msg': '密码重置成功'})
        except User.DoesNotExist:
            return Response({'code': 404, 'msg': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put'])
    def changeStatus(self, request):
        user_id = request.data.get('userId')
        status_value = request.data.get('status')
        
        if not user_id or status_value is None:
            return Response({'code': 400, 'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.status = status_value
            user.save()
            return Response({'code': 200, 'msg': '状态修改成功'})
        except User.DoesNotExist:
            return Response({'code': 404, 'msg': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def deptTree(self, request):
        depts = Dept.objects.filter(status='0').order_by('parent_id', 'order_num')
        serializer = DeptSerializer(depts, many=True)
        
        # 构建树形结构
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
        return Response(tree_data)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({
            'code': 200,
            'msg': '操作成功',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['put'])
    def updateProfile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'msg': '个人信息修改成功'
            })
        return Response({
            'code': 400,
            'msg': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def updatePwd(self, request):
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')
        
        if not old_password or not new_password:
            return Response({'code': 400, 'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(old_password):
            return Response({'code': 400, 'msg': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'code': 200, 'msg': '密码修改成功'})
    
    @action(detail=False, methods=['post'])
    def avatar(self, request):
        # 头像上传功能，这里简化处理
        avatar_url = request.data.get('avatar')
        if not avatar_url:
            return Response({'code': 400, 'msg': '请上传头像'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.avatar = avatar_url
        user.save()
        return Response({'code': 200, 'msg': '头像上传成功'})
    
    @action(detail=False, methods=['get'])
    def authRole(self, request, pk=None):
        user_id = request.query_params.get('userId')
        if not user_id:
            return Response({'code': 400, 'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            roles = Role.objects.filter(status='0', del_flag='0')
            user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
            
            roles_data = []
            for role in roles:
                role_data = RoleSerializer(role).data
                role_data['flag'] = role.role_id in user_roles
                roles_data.append(role_data)
            
            return Response({
                'code': 200,
                'msg': '操作成功',
                'user': UserSerializer(user).data,
                'roles': roles_data
            })
        except User.DoesNotExist:
            return Response({'code': 404, 'msg': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put'])
    def authRole(self, request):
        user_id = request.data.get('userId')
        role_ids = request.data.get('roleIds', [])
        
        if not user_id:
            return Response({'code': 400, 'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            
            # 删除现有角色关联
            UserRole.objects.filter(user=user).delete()
            
            # 添加新角色关联
            for role_id in role_ids:
                try:
                    role = Role.objects.get(role_id=role_id)
                    UserRole.objects.create(user=user, role=role)
                except Role.DoesNotExist:
                    continue
            
            return Response({'code': 200, 'msg': '授权成功'})
        except User.DoesNotExist:
            return Response({'code': 404, 'msg': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
