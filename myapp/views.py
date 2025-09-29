from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Project, Task
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer
from .filters import *
from .pagination import *


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username, password=password)
        request.session['user_id'] = user.id
        return Response({"message": "logged in successfully"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "invalid data"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def logout(request):
    if request.session.get('user_id'):
        request.session.flush()
        return Response({"message": "Logged out"}, status=status.HTTP_202_ACCEPTED)
    return Response({"message": "Permission not allowed"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def projects(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    projects = Project.objects.filter(is_deleted=False, owner=user_id)
    projects = search_filter_project(projects, request.GET)
    paginator = ProjectPagination()
    paginated_projects = paginator.paginate_queryset(projects, request)
    serializer = ProjectSerializer(paginated_projects, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def project_add(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    user = get_object_or_404(User, id=user_id)
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def project_detail(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    project = get_object_or_404(Project, pk=pk, is_deleted=False)
    if project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProjectSerializer(project)
    return Response(serializer.data)


@api_view(["PUT"])
def project_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    project = get_object_or_404(Project, pk=pk, owner=user_id)
    serializer = ProjectSerializer(project, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def project_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    project = get_object_or_404(Project, pk=pk, owner=user_id)
    project.delete()
    return Response({"message": "project deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def project_restore(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    project.restore()
    return Response({"message": "restored project"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def tasks(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    tasks = Task.objects.filter(is_deleted=False, project__owner=user_id)
    tasks = priority_filter(tasks, request.GET)
    tasks = search_filter_task(tasks, request.GET)
    paginator = TaskPagination()
    paginated_tasks = paginator.paginate_queryset(tasks, request)
    serializer = TaskSerializer(paginated_tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def task_add(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    project_id = request.data.get('project')
    project = get_object_or_404(Project, id=project_id, owner=user_id)

    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def task_detail(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    task = get_object_or_404(Task, pk=pk)
    if task.project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = TaskSerializer(task)
    return Response(serializer.data)


@api_view(["PUT"])
def task_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    task = get_object_or_404(Task, pk=pk)
    if task.project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = TaskSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def task_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    task = get_object_or_404(Task, pk=pk)
    if task.project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    task.delete()
    return Response({"message": "task deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def task_restore(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    task = get_object_or_404(Task, pk=pk)
    if task.project.owner_id != user_id:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    task.restore()
    return Response({"message": "restored task"}, status=status.HTTP_200_OK)
