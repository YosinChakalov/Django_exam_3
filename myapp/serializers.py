from rest_framework import serializers
from .models import User, Project, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'desc', 'owner', 'updated_at']

    def validate_title(self, value):
        owner = self.initial_data.get('owner')
        if not owner:
            raise serializers.ValidationError("Owner is required.")

        exists = Project.objects.filter(owner=owner, title=value)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise serializers.ValidationError("Project title must be unique for this owner.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'desc', 'priority', 'created_at', 'is_deleted']

    def validate_title(self, value):
        project = self.initial_data.get('project')
        if not project:
            raise serializers.ValidationError("Project is required.")

        exists = Task.objects.filter(project=project, title=value)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise serializers.ValidationError("Task title must be unique within the project.")
        return value

    def validate_priority(self, value):
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Priority must be between 1 and 5.")
        return value