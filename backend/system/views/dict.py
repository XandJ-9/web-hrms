from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from ..models import DictType, DictData
from ..serializers import DictTypeSerializer, DictDataSerializer


class DictTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DictType.objects.filter(del_flag='0').order_by('-create_time')
    serializer_class = DictTypeSerializer

    def get_queryset(self):
        qs = DictType.objects.filter(del_flag='0')
        dict_name = self.request.query_params.get('dictName', '')
        dict_type = self.request.query_params.get('dictType', '')
        status_value = self.request.query_params.get('status', '')
        if dict_name:
            qs = qs.filter(dict_name__icontains=dict_name)
        if dict_type:
            qs = qs.filter(dict_type__icontains=dict_type)
        if status_value:
            qs = qs.filter(status=status_value)
        return qs.order_by('-create_time')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        page_size = int(request.query_params.get('pageSize', 10))
        page_num = int(request.query_params.get('pageNum', 1))
        total = qs.count()
        start = (page_num - 1) * page_size
        end = start + page_size
        serializer = self.get_serializer(qs[start:end], many=True)
        return Response({'code': 200, 'msg': '操作成功', 'total': total, 'rows': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({'code': 200, 'msg': '操作成功', 'data': data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['get'], url_path='list')
    def list_action(self, request):
        # 兼容前端 /system/dict/type/list
        return self.list(request)

    @action(detail=False, methods=['delete'], url_path='refreshCache')
    def refreshCache(self, request):
        cache.delete('dict_optionselect')
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['get'], url_path='optionselect')
    def optionselect(self, request):
        cached = cache.get('dict_optionselect')
        if cached is not None:
            return Response({'code': 200, 'msg': '操作成功', 'data': cached})
        qs = DictType.objects.filter(status='0', del_flag='0').order_by('dict_name')
        data = [{'dictId': d.dict_id, 'dictName': d.dict_name, 'dictType': d.dict_type} for d in qs]
        cache.set('dict_optionselect', data, timeout=300)
        return Response({'code': 200, 'msg': '操作成功', 'data': data})


class DictDataViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DictData.objects.filter(del_flag='0').order_by('-create_time')
    serializer_class = DictDataSerializer

    def get_queryset(self):
        qs = DictData.objects.filter(del_flag='0')
        dict_type = self.request.query_params.get('dictType', '')
        dict_label = self.request.query_params.get('dictLabel', '')
        status_value = self.request.query_params.get('status', '')
        if dict_type:
            qs = qs.filter(dict_type=dict_type)
        if dict_label:
            qs = qs.filter(dict_label__icontains=dict_label)
        if status_value:
            qs = qs.filter(status=status_value)
        return qs.order_by('-create_time')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        page_size = int(request.query_params.get('pageSize', 10))
        page_num = int(request.query_params.get('pageNum', 1))
        total = qs.count()
        start = (page_num - 1) * page_size
        end = start + page_size
        serializer = self.get_serializer(qs[start:end], many=True)
        return Response({'code': 200, 'msg': '操作成功', 'total': total, 'rows': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({'code': 200, 'msg': '操作成功', 'data': data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['get'], url_path='list')
    def list_action(self, request):
        # 兼容前端 /system/dict/data/list
        return self.list(request)

    @action(detail=False, methods=['get'], url_path=r'type/(?P<dict_type>[^/]+)')
    def by_type(self, request, dict_type=None):
        qs = DictData.objects.filter(dict_type=dict_type, status='0', del_flag='0').order_by('dict_sort', 'dict_label')
        serializer = self.get_serializer(qs, many=True)
        return Response({'code': 200, 'msg': '操作成功', 'data': serializer.data})