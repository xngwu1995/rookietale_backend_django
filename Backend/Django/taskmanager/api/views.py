from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions
from taskmanager.models import TaskManager
from taskmanager.api.serializers import (
    TaskManagerSerializer,
    TaskManagerCompletedSerializer,
    TaskManagerSerializerForGet,
)
from django.contrib.auth.models import User


class TaskmanagerViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    @action(methods=['POST'], detail=False)
    def create_task(self, request):
        serializer = TaskManagerSerializer(data=request.data, mistress=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=True)
    def edit_task(self, request, pk=None):
        try:
            task = TaskManager.objects.get(pk=pk)
        except TaskManager.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskManagerSerializer(task, data=request.data, mistress=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=True)
    def completed_task(self, request, pk=None):
        try:
            task = TaskManager.objects.get(pk=pk)
        except TaskManager.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskManagerCompletedSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False)
    def get_sub_tasks(self, request):
        tasks = TaskManager.objects.filter(sub=request.user)
        serializer = TaskManagerSerializerForGet(tasks, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def get_mis_tasks(self, request):
        tasks = TaskManager.objects.filter(mistress=request.user)
        serializer = TaskManagerSerializerForGet(tasks, many=True)
        return Response(serializer.data)

    # Optional: If you want to retrieve a single task
    @action(methods=['GET'], detail=True)
    def get_task(self, request, pk=None):
        try:
            task = TaskManager.objects.get(pk=pk, mistress=request.user)
        except TaskManager.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskManagerSerializer(task)
        return Response(serializer.data)
