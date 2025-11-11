from rest_framework import serializers
from .models import User, Dept, Role, UserRole

class DeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dept
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    dept = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'nick_name', 'phonenumber', 'email', 'sex', 'avatar', 'status', 
                 'remark', 'dept_id', 'dept', 'create_by', 'update_by', 'create_time', 'update_time']
    
    def get_dept(self, obj):
        if obj.dept_id:
            try:
                dept = Dept.objects.get(dept_id=obj.dept_id)
                return {
                    'deptId': dept.dept_id,
                    'deptName': dept.dept_name
                }
            except Dept.DoesNotExist:
                return None
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    dept = serializers.SerializerMethodField()
    roleIds = serializers.SerializerMethodField()
    postIds = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'nick_name', 'phonenumber', 'email', 'sex', 'avatar', 
                 'dept_id', 'dept', 'roleIds', 'postIds']
    
    def get_dept(self, obj):
        if obj.dept_id:
            try:
                dept = Dept.objects.get(dept_id=obj.dept_id)
                return {
                    'deptId': dept.dept_id,
                    'deptName': dept.dept_name
                }
            except Dept.DoesNotExist:
                return None
        return None
    
    def get_roleIds(self, obj):
        # 获取用户关联的角色ID列表
        return list(UserRole.objects.filter(user=obj).values_list('role_id', flat=True))
    
    def get_postIds(self, obj):
        # 这里需要实现岗位关联，暂时返回空列表
        return []