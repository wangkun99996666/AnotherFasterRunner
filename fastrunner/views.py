from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from fastrunner import models, serializers
from FasterRunner import pagination
from rest_framework.response import Response
from fastrunner.utils import response
from fastrunner.utils.counter import get_project_detail
from fastrunner.utils.parser import Format
from fastrunner.utils.tree import get_tree_max_id
from django.db import DataError

# Create your views here.


class ProjectView(GenericViewSet):
    """
    项目增删改查
    """

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    pagination_class = pagination.MyCursorPagination
    authentication_classes = ()

    def list(self, request):
        """
        查询项目信息
        """

        projects = self.get_queryset()
        page_projects = self.paginate_queryset(projects)
        serializer = self.get_serializer(page_projects, many=True)
        return self.get_paginated_response(serializer.data)

    def add(self, request):
        """
        添加项目
        """

        name = request.data["name"]

        if models.Project.objects.filter(name=name).first():
            response.PROJECT_EXISTS["name"] = name
            return Response(response.PROJECT_EXISTS)
        """
        反序列化
        """
        serializer = serializers.ProjectSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            project = models.Project.objects.get(name=name)
            # 自动生成默认debugtalk.py
            models.Debugtalk.objects.create(project=project)

            return Response(response.PROJECT_ADD_SUCCESS)

        else:
            return Response(response.SYSTEM_ERROR)

    def update(self, request):
        """
        编辑项目
        """

        try:
            obj = models.Project.objects.get(id=request.data['id'])
        except (KeyError, ObjectDoesNotExist):
            return Response(response.SYSTEM_ERROR)

        if request.data['name'] != obj.name:
            if models.Project.objects.filter(name=request.data['name']).first():
                return Response(response.PROJECT_EXISTS)

        # 调用save方法update_time字段才会自动更新
        obj.name = request.data['name']
        obj.desc = request.data['desc']
        obj.save()

        return Response(response.PROJECT_UPDATE_SUCCESS)

    def delete(self, request):
        """
        删除项目
        """
        try:
            models.Project.objects.get(id=request.data['id']).delete()
            # 此处应该删除project表其他数据
            pass
            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    def get_single(self, request, **kwargs):
        """
        得到单个项目相关统计信息
        """
        pk = kwargs.pop('pk')
        try:
            queryset = models.Project.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        project_info = get_project_detail(pk)
        project_info.update(serializer.data)

        return Response(project_info)


class DataBaseView(ModelViewSet):
    """
    DataBase 增删改查
    """
    queryset = models.DataBase.objects.all()
    authentication_classes = ()
    pagination_class = pagination.MyCursorPagination
    serializer_class = serializers.DataBaseSerializer


class DebugTalkView(GenericViewSet):
    """
    DebugTalk update
    """
    authentication_classes = ()
    serializer_class = serializers.DebugTalkSerializer

    def debugtalk(self, request, **kwargs):
        """
        得到debugtalk code
        """
        pk = kwargs.pop('pk')
        try:
            queryset = models.Debugtalk.objects.get(project__id=pk)
        except ObjectDoesNotExist:
            return Response(response.DEBUGTALK_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        return Response(serializer.data)

    def update(self, request):
        """
        编辑debugtalk.py 代码并保存
        """
        try:
            models.Debugtalk.objects.update_or_create(defaults=request.data)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        return Response(response.DEBUGTALK_UPDATE_SUCCESS)


class TreeView(APIView):
    """
    树形结构操作
    """
    authentication_classes = ()

    def get(self, request, **kwargs):
        """
        返回树形结构
        当前最带节点ID
        """
        try:
            tree = models.Relation.objects.get(project__id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        body = eval(tree.tree)  # list
        tree = {
            "tree": body,
            "id": tree.id,
            "success": True
        }
        return Response(tree)

    def patch(self, request, **kwargs):
        """
        修改树形结构，ID不能重复
        """
        try:
            models.Relation.objects.filter(id=kwargs['pk']).update(tree=request.data)

        except KeyError:
            return Response(response.KEY_MISS)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        response.TREE_UPDATE_SUCCESS['tree'] = request.data
        response.TREE_UPDATE_SUCCESS['max'] = get_tree_max_id(request.data)

        return Response(response.TREE_UPDATE_SUCCESS)


class FileView(APIView):
    authentication_classes = ()

    def post(self, request):
        """
        接收文件并保存
        """
        file = request.FILES['file']

        # 此处应该插入数据库
        pass

        return Response(response.FILE_UPLOAD_SUCCESS)


class APITemplateView(GenericViewSet):
    """
    API操作视图
    """
    authentication_classes = ()
    queryset = models.API.objects.all()
    serializer_class = serializers.APISerializer
    """使用默认分页器"""

    def list(self, request):
        pagination_querset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(pagination_querset, many=True)
        return self.get_paginated_response(serializer.data)

    def add(self, request):
        """
        新增一个接口
        """

        api = Format(request.data)
        api.parse_test()

        api_body = {
            'name': api.name,
            'body': api.testcase,
            'url': api.url,
            'method': api.method,
            'project': models.Project.objects.get(id=api.project),
            'relation': api.relation
        }

        try:
            models.API.objects.create(**api_body)
        except DataError:
            return Response(response.DATA_TO_LONG)

        return Response(response.API_ADD_SUCCESS)
