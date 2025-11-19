from rest_framework import serializers
from .models import User, Dept, Role, UserRole, Menu, DictType, DictData, Config
from .common import snake_to_camel

class CamelCaseModelSerializer(serializers.ModelSerializer):
    camelize = True
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not getattr(self, 'camelize', True):
            return data
        return { snake_to_camel(k): v for k, v in data.items() }

class PaginationQuerySerializer(serializers.Serializer):
    pageNum = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=10)

class BaseSerializer(serializers.ModelSerializer):
    """
    抽取各模型通用的审计/状态字段，统一命名为驼峰，以减少重复定义。
    字段在模型中不存在时，序列化为 None；写入时不强制要求。
    """
    createBy = serializers.CharField(source='create_by', required=False, read_only=True)
    updateBy = serializers.CharField(source='update_by', required=False, read_only=True)
    createTime = serializers.DateTimeField(source='create_time', read_only=True, format='%Y-%m-%d %H:%M:%S')
    updateTime = serializers.DateTimeField(source='update_time', read_only=True, format='%Y-%m-%d %H:%M:%S')
    remark = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)

    # 自动将公共字段并入子类 Meta.fields，避免每个子类重复声明
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        meta = getattr(cls, 'Meta', None)
        if not meta:
            return
        fields = getattr(meta, 'fields', None)
        default_public_fields = ['createBy', 'updateBy', 'createTime', 'updateTime', 'remark', 'status']
        if isinstance(fields, (list, tuple)):
            merged = list(fields)
            for f in default_public_fields:
                if f not in merged:
                    merged.append(f)
            meta.fields = merged

# User related
class UserQuerySerializer(PaginationQuerySerializer):
    userName = serializers.CharField(required=False, allow_blank=True)
    phonenumber = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])
    deptId = serializers.IntegerField(required=False)
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class ResetPwdSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    password = serializers.CharField(min_length=6, max_length=128)

class ChangeStatusSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['0','1'])

class UpdatePwdSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(min_length=6, max_length=128)
    newPassword = serializers.CharField(min_length=6, max_length=128)

class AvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()

class AuthRoleAssignSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    roleIds = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)

class AuthRoleQuerySerializer(serializers.Serializer):
    userId = serializers.IntegerField()

class UserSerializer(BaseSerializer):
    userId = serializers.IntegerField(source='id')
    userName = serializers.CharField(source='username', required=False)
    nickName = serializers.CharField(source='nick_name', required=False)
    # dept = serializers.SerializerMethodField()
    deptId = serializers.IntegerField(source='dept_id')
    
    class Meta:
        model = User
        fields = ['userId', 'userName', 'nickName', 'phonenumber', 'email', 'sex', 'avatar', 'status', 
                 'remark', 'deptId']
    
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

class UserProfileSerializer(BaseSerializer):
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
        return list(UserRole.objects.filter(user=obj).values_list('role_id', flat=True))
    
    def get_postIds(self, obj):
        return []

class UserInfoSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    userName = serializers.CharField()
    nickName = serializers.CharField()
    avatar = serializers.CharField()
    phonenumber = serializers.CharField()
    email = serializers.CharField()
    sex = serializers.CharField()
    class Meta:
        model = User
        fields = ['userId', 'userName', 'nickName', 'avatar', 'phonenumber', 'email', 'sex']

# Dept related
class DeptSerializer(BaseSerializer):
    deptId = serializers.IntegerField(source='dept_id')
    parentId = serializers.IntegerField(source='parent_id')
    deptName = serializers.CharField(source='dept_name')
    orderNum = serializers.IntegerField(source='order_num')
    
    class Meta:
        model = Dept
        fields = ['deptId', 'parentId', 'deptName', 'orderNum', 'leader', 'phone', 'email', 'status', 'remark']

class DeptQuerySerializer(serializers.Serializer):
    deptName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class DeptCreateSerializer(serializers.Serializer):
    parentId = serializers.IntegerField(required=False, default=0)
    deptName = serializers.CharField(max_length=30)
    orderNum = serializers.IntegerField(required=False, default=0)
    leader = serializers.CharField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.CharField(required=False, allow_blank=True, default='')
    status = serializers.ChoiceField(required=False, choices=['0','1'], default='0')

class DeptUpdateSerializer(DeptCreateSerializer):
    deptId = serializers.IntegerField()

# Role related
class RoleSerializer(BaseSerializer):
    roleId = serializers.IntegerField(source='role_id', read_only=True)
    roleName = serializers.CharField(source='role_name')
    roleKey = serializers.CharField(source='role_key')
    roleSort = serializers.IntegerField(source='role_sort')
    dataScope = serializers.CharField(source='data_scope', required=False)
    menuCheckStrictly = serializers.SerializerMethodField()
    deptCheckStrictly = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['roleId', 'roleName', 'roleKey', 'roleSort', 'dataScope', 'menuCheckStrictly', 'deptCheckStrictly']

    def get_menuCheckStrictly(self, obj):
        return True if getattr(obj, 'menu_check_strictly', 1) == 1 else False

    def get_deptCheckStrictly(self, obj):
        return True if getattr(obj, 'dept_check_strictly', 1) == 1 else False

class RoleQuerySerializer(PaginationQuerySerializer):
    roleName = serializers.CharField(required=False, allow_blank=True)
    roleKey = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class RoleCreateSerializer(serializers.Serializer):
    roleName = serializers.CharField(max_length=30)
    roleKey = serializers.CharField(max_length=100)
    roleSort = serializers.IntegerField(required=False, default=0)
    status = serializers.ChoiceField(choices=['0','1'], default='0')
    remark = serializers.CharField(required=False, allow_blank=True, default='')
    dataScope = serializers.ChoiceField(required=False, choices=['1','2','3','4','5'], default='1')
    menuCheckStrictly = serializers.BooleanField(required=False, default=True)
    deptCheckStrictly = serializers.BooleanField(required=False, default=True)
    menuIds = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)

class RoleUpdateSerializer(RoleCreateSerializer):
    roleId = serializers.IntegerField()

class RoleChangeStatusSerializer(serializers.Serializer):
    roleId = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['0','1'])

class RoleDataScopeSerializer(serializers.Serializer):
    roleId = serializers.IntegerField()
    dataScope = serializers.ChoiceField(choices=['1','2','3','4','5'])
    deptIds = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    deptCheckStrictly = serializers.BooleanField(required=False, default=True)

# Menu related
class MenuQuerySerializer(PaginationQuerySerializer):
    menuName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class MenuCreateSerializer(serializers.Serializer):
    parentId = serializers.IntegerField(required=False, default=0)
    menuName = serializers.CharField(max_length=50)
    orderNum = serializers.IntegerField(required=False, default=0)
    path = serializers.CharField(required=False, allow_blank=True, default='')
    component = serializers.CharField(required=False, allow_blank=True, default='')
    query = serializers.CharField(required=False, allow_blank=True, default='')
    isFrame = serializers.ChoiceField(choices=['0','1'], default='1')
    isCache = serializers.ChoiceField(choices=['0','1'], default='0')
    menuType = serializers.ChoiceField(choices=['M','C','F'], default='M')
    visible = serializers.ChoiceField(choices=['0','1'], default='0')
    status = serializers.ChoiceField(choices=['0','1'], default='0')
    perms = serializers.CharField(required=False, allow_blank=True, default='')
    icon = serializers.CharField(required=False, allow_blank=True, default='')
    remark = serializers.CharField(required=False, allow_blank=True, default='')

class MenuUpdateSerializer(MenuCreateSerializer):
    menuId = serializers.IntegerField()

class MenuSerializer(BaseSerializer):
    menuId = serializers.IntegerField(source='menu_id', read_only=True)
    parentId = serializers.IntegerField(source='parent_id')
    menuName = serializers.CharField(source='menu_name')
    orderNum = serializers.IntegerField(source='order_num')
    path = serializers.CharField()
    component = serializers.CharField(allow_blank=True)
    query = serializers.CharField(allow_blank=True)
    isFrame = serializers.CharField(source='is_frame')
    isCache = serializers.CharField(source='is_cache')
    menuType = serializers.CharField(source='menu_type')
    visible = serializers.CharField()
    perms = serializers.CharField(allow_blank=True)
    icon = serializers.CharField(allow_blank=True)

    class Meta:
        model = Menu
        fields = ['menuId', 'parentId', 'menuName', 'orderNum', 'path', 'component', 'query', 'isFrame',
                  'isCache', 'menuType', 'visible', 'perms', 'icon']

# DictType related
class DictTypeQuerySerializer(PaginationQuerySerializer):
    dictName = serializers.CharField(required=False, allow_blank=True)
    dictType = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class DictTypeSerializer(BaseSerializer):
    dictId = serializers.IntegerField(source='dict_id', read_only=True)
    dictName = serializers.CharField(source='dict_name')
    dictType = serializers.CharField(source='dict_type')

    class Meta:
        model = DictType
        fields = ['dictId', 'dictName', 'dictType']

# DictData related
class DictDataQuerySerializer(PaginationQuerySerializer):
    dictLabel = serializers.CharField(required=False, allow_blank=True)
    dictType = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class DictDataSerializer(BaseSerializer):
    dictCode = serializers.IntegerField(source='dict_code', read_only=True)
    dictSort = serializers.IntegerField(source='dict_sort')
    dictLabel = serializers.CharField(source='dict_label')
    dictValue = serializers.CharField(source='dict_value')
    dictType = serializers.CharField(source='dict_type')
    cssClass = serializers.CharField(source='css_class', allow_blank=True, required=False)
    listClass = serializers.CharField(source='list_class', allow_blank=True, required=False)

    class Meta:
        model = DictData
        fields = ['dictCode', 'dictSort', 'dictLabel', 'dictValue', 'dictType', 'cssClass', 'listClass']

# Config related
class ConfigQuerySerializer(PaginationQuerySerializer):
    configName = serializers.CharField(required=False, allow_blank=True)
    configKey = serializers.CharField(required=False, allow_blank=True)
    configType = serializers.ChoiceField(required=False, choices=['Y','N'])
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class ConfigSerializer(BaseSerializer):
    configId = serializers.IntegerField(source='config_id', read_only=True)
    configName = serializers.CharField(source='config_name')
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    configType = serializers.CharField(source='config_type')

    class Meta:
        model = Config
        fields = ['configId', 'configName', 'configKey', 'configValue', 'configType']

class ConfigCreateSerializer(serializers.Serializer):
    configName = serializers.CharField(max_length=100)
    configKey = serializers.CharField(max_length=100)
    configValue = serializers.CharField(max_length=500)
    configType = serializers.ChoiceField(choices=['Y','N'], default='Y')
    remark = serializers.CharField(required=False, allow_blank=True, default='')

class ConfigUpdateSerializer(ConfigCreateSerializer):
    configId = serializers.IntegerField()