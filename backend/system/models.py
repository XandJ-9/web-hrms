from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Dept(models.Model):
    dept_id = models.AutoField(primary_key=True, verbose_name='部门ID')
    parent_id = models.IntegerField(default=0, verbose_name='父部门ID')
    ancestors = models.CharField(max_length=50, default='', verbose_name='祖级列表')
    dept_name = models.CharField(max_length=30, verbose_name='部门名称')
    order_num = models.IntegerField(default=0, verbose_name='显示顺序')
    leader = models.CharField(max_length=20, blank=True, verbose_name='负责人')
    phone = models.CharField(max_length=11, blank=True, verbose_name='联系电话')
    email = models.CharField(max_length=50, blank=True, verbose_name='邮箱')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='部门状态')
    create_by = models.CharField(max_length=64, blank=True, verbose_name='创建者')
    update_by = models.CharField(max_length=64, blank=True, verbose_name='更新者')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_dept'
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return self.dept_name

class User(AbstractUser):
    nick_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Nick Name")
    phonenumber = models.CharField(max_length=11, blank=True, null=True, verbose_name="Phone Number")
    sex = models.CharField(max_length=1, choices=(('0', 'Male'), ('1', 'Female'), ('2', 'Unknown')), default='2', verbose_name="Sex")
    avatar = models.CharField(max_length=100, blank=True, null=True, verbose_name="Avatar")
    status = models.CharField(max_length=1, choices=(('0', 'Active'), ('1', 'Inactive')), default='0', verbose_name="Status")
    remark = models.CharField(max_length=500, blank=True, null=True, verbose_name="Remark")
    dept_id = models.IntegerField(null=True, blank=True, verbose_name="Department ID")
    create_by = models.CharField(max_length=64, blank=True, verbose_name="Created By")
    update_by = models.CharField(max_length=64, blank=True, verbose_name="Updated By")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="Created Time")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="Updated Time")

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class Role(models.Model):
    role_id = models.AutoField(primary_key=True, verbose_name='角色ID')
    role_name = models.CharField(max_length=30, verbose_name='角色名称')
    role_key = models.CharField(max_length=100, verbose_name='权限字符')
    role_sort = models.IntegerField(default=0, verbose_name='角色排序')
    data_scope = models.CharField(max_length=1, choices=[('1', '全部数据权限'), ('2', '自定数据权限'), ('3', '本部门数据权限'), ('4', '本部门及以下数据权限'), ('5', '仅本人数据权限')], default='1', verbose_name='数据范围')
    menu_check_strictly = models.IntegerField(default=1, verbose_name='菜单树选择项是否关联显示')
    dept_check_strictly = models.IntegerField(default=1, verbose_name='部门树选择项是否关联显示')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='角色状态')
    del_flag = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '删除')], default='0', verbose_name='删除标志')
    create_by = models.CharField(max_length=64, blank=True, verbose_name='创建者')
    update_by = models.CharField(max_length=64, blank=True, verbose_name='更新者')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def __str__(self):
        return self.role_name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    
    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色关联'
        verbose_name_plural = '用户角色关联'
        unique_together = ('user', 'role')
