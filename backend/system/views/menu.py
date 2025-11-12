from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Menu, RoleMenu
from ..serializers import MenuSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(del_flag='0').order_by('parent_id', 'order_num')
    serializer_class = MenuSerializer

    def list(self, request, *args, **kwargs):
        print(f'request.query_params: {request.query_params}')
        menu_name = request.query_params.get('menuName')
        status_value = request.query_params.get('status')
        qs = self.get_queryset()
        if menu_name:
            qs = qs.filter(menu_name__icontains=menu_name)
        if status_value:
            qs = qs.filter(status=status_value)
        data = self.get_serializer(qs, many=True).data
        return Response({"code": 200, "msg": "操作成功", "data": data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"code": 200, "msg": "操作成功", "data": data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "msg": "操作成功"})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "msg": "操作成功"})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        return Response({"code": 200, "msg": "操作成功"})

    def list2(self, request, *args, **kwargs):
        self.list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def treeselect(self, request):
        qs = self.get_queryset()
        items = list(qs)

        def build_tree(items, pid=0):
            res = []
            for m in items:
                if m.parent_id == pid:
                    node = {"id": m.menu_id, "label": m.menu_name}
                    children = build_tree(items, m.menu_id)
                    if children:
                        node["children"] = children
                    res.append(node)
            return res

        data = build_tree(items, 0)
        return Response({"code": 200, "msg": "操作成功", "data": data})

    @action(detail=False, methods=['get'], url_path=r'roleMenuTreeselect/(?P<roleId>\d+)')
    def roleMenuTreeselect(self, request, roleId=None):
        qs = self.get_queryset()
        items = list(qs)
        checked = list(RoleMenu.objects.filter(role_id=roleId).values_list('menu_id', flat=True))

        def build_tree(items, pid=0):
            res = []
            for m in items:
                if m.parent_id == pid:
                    node = {"id": m.menu_id, "label": m.menu_name}
                    children = build_tree(items, m.menu_id)
                    if children:
                        node["children"] = children
                    res.append(node)
            return res

        data = build_tree(items, 0)
        return Response({"code": 200, "msg": "操作成功", "menus": data, "checkedKeys": checked})