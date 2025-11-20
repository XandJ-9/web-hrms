from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    create_by = models.CharField(max_length=64, blank=True)
    update_by = models.CharField(max_length=64, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    del_flag = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '删除')], default='0')

    class Meta:
        abstract = True

class Dept(BaseModel):
    dept_id = models.AutoField(primary_key=True, verbose_name='部门ID')
    parent_id = models.IntegerField(default=0, verbose_name='父部门ID')
    ancestors = models.CharField(max_length=50, default='', verbose_name='祖级列表')
    dept_name = models.CharField(max_length=30, verbose_name='部门名称')
    order_num = models.IntegerField(default=0, verbose_name='显示顺序')
    leader = models.CharField(max_length=20, blank=True, verbose_name='负责人')
    phone = models.CharField(max_length=11, blank=True, verbose_name='联系电话')
    email = models.CharField(max_length=50, blank=True, verbose_name='邮箱')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='部门状态')
    

    class Meta:
        db_table = 'sys_dept'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['parent_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.dept_name

class User(AbstractUser, BaseModel):
    nick_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Nick Name")
    phonenumber = models.CharField(max_length=11, blank=True, null=True, verbose_name="Phone Number")
    sex = models.CharField(max_length=1, choices=(('0', 'Male'), ('1', 'Female'), ('2', 'Unknown')), default='2', verbose_name="Sex")
    avatar = models.CharField(max_length=100, blank=True, null=True, verbose_name="Avatar")
    status = models.CharField(max_length=1, choices=(('0', 'Active'), ('1', 'Inactive')), default='0', verbose_name="Status")
    remark = models.CharField(max_length=500, blank=True, null=True, verbose_name="Remark")
    dept_id = models.IntegerField(null=True, blank=True, verbose_name="Department ID")
    

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['dept_id']),
            models.Index(fields=['del_flag']),
        ]

    def __str__(self):
        return self.username


class Role(BaseModel):
    role_id = models.AutoField(primary_key=True, verbose_name='角色ID')
    role_name = models.CharField(max_length=30, verbose_name='角色名称')
    role_key = models.CharField(max_length=100, verbose_name='权限字符')
    role_sort = models.IntegerField(default=0, verbose_name='角色排序')
    data_scope = models.CharField(max_length=1, choices=[('1', '全部数据权限'), ('2', '自定数据权限'), ('3', '本部门数据权限'), ('4', '本部门及以下数据权限'), ('5', '仅本人数据权限')], default='1', verbose_name='数据范围')
    menu_check_strictly = models.IntegerField(default=1, verbose_name='菜单树选择项是否关联显示')
    dept_check_strictly = models.IntegerField(default=1, verbose_name='部门树选择项是否关联显示')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='角色状态')
    
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['del_flag']),
        ]

    def __str__(self):
        return self.role_name


class UserRole(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    
    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色关联'
        verbose_name_plural = '用户角色关联'
        unique_together = ('user', 'role')


class Menu(BaseModel):
    menu_id = models.AutoField(primary_key=True, verbose_name='菜单ID')
    parent_id = models.IntegerField(default=0, verbose_name='父菜单ID')
    menu_name = models.CharField(max_length=50, verbose_name='菜单名称')
    order_num = models.IntegerField(default=0, verbose_name='显示顺序')
    path = models.CharField(max_length=200, blank=True, default='', verbose_name='路由地址')
    component = models.CharField(max_length=200, blank=True, default='', verbose_name='组件路径')
    query = models.CharField(max_length=255, blank=True, default='', verbose_name='路由参数')
    is_frame = models.CharField(max_length=1, choices=[('0', '是'), ('1', '否')], default='1', verbose_name='是否外链')
    is_cache = models.CharField(max_length=1, choices=[('0', '缓存'), ('1', '不缓存')], default='0', verbose_name='是否缓存')
    menu_type = models.CharField(max_length=1, choices=[('M', '目录'), ('C', '菜单'), ('F', '按钮')], default='M', verbose_name='菜单类型')
    visible = models.CharField(max_length=1, choices=[('0', '显示'), ('1', '隐藏')], default='0', verbose_name='显示状态')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='菜单状态')
    perms = models.CharField(max_length=100, blank=True, default='', verbose_name='权限标识')
    icon = models.CharField(max_length=100, blank=True, default='', verbose_name='菜单图标')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    

    class Meta:
        db_table = 'sys_menu'
        verbose_name = '菜单'
        verbose_name_plural = '菜单'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['parent_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.menu_name


class RoleMenu(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name='菜单')

    class Meta:
        db_table = 'sys_role_menu'
        verbose_name = '角色菜单关联'
        verbose_name_plural = '角色菜单关联'
        unique_together = ('role', 'menu')


class DictType(BaseModel):
    dict_id = models.AutoField(primary_key=True, verbose_name='字典主键')
    dict_name = models.CharField(max_length=100, verbose_name='字典名称')
    dict_type = models.CharField(max_length=100, unique=True, verbose_name='字典类型')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='状态')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    

    class Meta:
        db_table = 'sys_dict_type'
        verbose_name = '字典类型'
        verbose_name_plural = '字典类型'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['dict_type']),
        ]

    def __str__(self):
        return self.dict_name


class DictData(BaseModel):
    dict_code = models.AutoField(primary_key=True, verbose_name='字典编码')
    dict_sort = models.IntegerField(default=0, verbose_name='字典排序')
    dict_label = models.CharField(max_length=100, verbose_name='字典标签')
    dict_value = models.CharField(max_length=100, verbose_name='字典键值')
    dict_type = models.CharField(max_length=100, verbose_name='字典类型')
    css_class = models.CharField(max_length=100, blank=True, default='', verbose_name='样式属性')
    list_class = models.CharField(max_length=20, blank=True, default='default', verbose_name='回显样式')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='状态')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    

    class Meta:
        db_table = 'sys_dict_data'
        verbose_name = '字典数据'
        verbose_name_plural = '字典数据'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['dict_type']),
        ]

    def __str__(self):
        return self.dict_label


class Config(BaseModel):
    config_id = models.AutoField(primary_key=True, verbose_name='参数主键')
    config_name = models.CharField(max_length=100, verbose_name='参数名称')
    config_key = models.CharField(max_length=100, unique=True, verbose_name='参数键名')
    config_value = models.CharField(max_length=500, verbose_name='参数键值')
    config_type = models.CharField(max_length=1, choices=[('Y', '是'), ('N', '否')], default='Y', verbose_name='系统内置')
    remark = models.TextField(blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'sys_config'
        verbose_name = '参数配置'
        verbose_name_plural = '参数配置'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['config_key']),
        ]

    def __str__(self):
        return f"{self.config_name}({self.config_key})"
